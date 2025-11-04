from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError
import os
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView,
    ListAPIView,
)
from .models import User, UserProfile, Contact, PasswordResetToken
from .serializers import (
    SignUpSerializer,
    UserListSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    ContactSerializer,
    UserProfileTextSerializer,
    UserProfileAvatarSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import secrets
from .models import PasswordResetToken


@api_view(["POST"])
def passwordResetRequest(request):
    """Request a password reset - sends email with reset token"""
    email = request.data.get("email")
    
    if not email:
        return Response(
            {"error": "Email is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Don't reveal if user exists or not for security
        return Response(
            {"message": "If an account exists with this email, you will receive a password reset link."},
            status=status.HTTP_200_OK
        )
    
    # Generate secure random token
    token = secrets.token_urlsafe(32)
    
    # Delete any existing unused tokens for this user
    PasswordResetToken.objects.filter(user=user, used=False).delete()
    
    # Create new token (expires in 1 hour)
    expires_at = timezone.now() + timezone.timedelta(hours=1)
    PasswordResetToken.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )
    
    # Send email with reset link
    reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={token}"
    
    try:
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link below to reset your password:\n\n{reset_url}\n\nThis link will expire in 1 hour.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email: {e}")
        return Response(
            {"error": "Failed to send reset email. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response(
        {"message": "If an account exists with this email, you will receive a password reset link."},
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
def passwordResetConfirm(request):
    """Confirm password reset with token and new password"""
    token = request.data.get("token")
    new_password = request.data.get("password")
    
    if not token or not new_password:
        return Response(
            {"error": "Token and new password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        return Response(
            {"error": "Invalid or expired reset token"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if token is valid
    if not reset_token.is_valid():
        return Response(
            {"error": "Invalid or expired reset token"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update user password
    user = reset_token.user
    user.password = make_password(new_password)
    user.save()
    
    # Mark token as used
    reset_token.used = True
    reset_token.save()
    
    return Response(
        {"message": "Password has been reset successfully. You can now log in with your new password."},
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
def customerRegister(request):
    data = request.data
    user = SignUpSerializer(data=data)

    if user.is_valid():
        if not User.objects.filter(email=data["email"]).exists():
            password = make_password(data["password"])
            user = User.objects.create(
                first_name=data["first_name"],
                last_name=data["last_name"],
                username=data["email"],
                email=data["email"],
                password=password,
            )
            # add custom fields here
            # user.is_customer = True
            user.save()

            return Response({"message": "User registered."}, status=status.HTTP_200_OK)
    else:
        return Response(user.errors)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateUser(request):
    user = request.user
    data = request.data

    user.first_name = data["first_name"]
    user.last_name = data["last_name"]
    user.username = data["email"]
    user.email = data["email"]

    if data["password"] != "":
        user.password = make_password(data["password"])

    user.save()

    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# Create your views here.
class UserList(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]


class UserProfileDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # ✅ Required for file uploads

    def get(self, request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(user_profile, context={"request": request})
        return Response(serializer.data)

    def put(self, request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Pass request.data directly to serializer - DRF handles files properly
        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def currentUser(request):
    user = UserSerializer(request.user)
    return Response(user.data)


class ContactCreateView(ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Thank you for reaching out! We'll get back to you soon."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileTextUpdateView(APIView):
    """
    API endpoint for updating profile text fields only (no file upload).
    Accepts JSON data: first_name, last_name, about, phone_number, countries
    """
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileTextSerializer(
            user_profile, 
            data=request.data, 
            partial=True,
            context={"request": request}
        )
        
        if serializer.is_valid():
            serializer.save()
            # Return full profile data after update
            full_serializer = UserProfileSerializer(user_profile, context={"request": request})
            return Response(full_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAvatarUpdateView(APIView):
    """
    API endpoint for uploading/updating avatar only.
    Accepts multipart/form-data with avatar file
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if 'avatar' not in request.FILES:
            return Response(
                {"error": "No avatar file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserProfileAvatarSerializer(
            user_profile,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            # Return full profile data after update
            full_serializer = UserProfileSerializer(user_profile, context={"request": request})
            return Response(full_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
