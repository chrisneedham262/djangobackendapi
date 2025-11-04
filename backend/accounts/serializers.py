from django.db.models import Q
from rest_framework import serializers
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    User,
    UserProfile,
    DifferentCountries,
    Contact,
)


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password")

        extra_kwargs = {
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
            "email": {"required": True, "allow_blank": False},
            "password": {"required": True, "allow_blank": False, "min_length": 6},
        }


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        read_only_fields = ("username",)
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "username",
            "is_customer",
            "is_staff",
        )
        extra_kwargs = {
            "is_customer": {
                "required": False,
            },
            "is_staff": {
                "required": False,
            },
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "username",
            # add custom fields here
            # "is_customer",
            # "is_expert",
        )


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", required=False
    )  # ✅ Now optional
    last_name = serializers.CharField(
        source="user.last_name", required=False
    )  # ✅ Now optional
    email = serializers.EmailField(source="user.email", read_only=True)
    countries = serializers.ChoiceField(
        choices=[("", "Not Specified")] + UserProfile.countries.field.choices,
        allow_blank=True,
        allow_null=True,
    )
    country_choices = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()  # ✅ Converts avatar to full URL

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "first_name",  # ✅ Now included
            "last_name",
            "email",
            "about",
            "avatar",  # ✅ Ensures full URL
            "phone_number",
            "countries",
            "created_at",
            "updated_at",
            "country_choices",
        ]

    def get_avatar(self, obj):
        """Ensure avatar returns a full absolute URL instead of a relative path."""
        request = self.context.get("request")
        if request and obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)  # ✅ Converts to full URL
        elif obj.avatar:
            return f"{settings.MEDIA_URL}{obj.avatar.url}"  # ✅ Fallback
        return None

    def get_country_choices(self, obj):
        """Returns list of available country choices."""
        return [
            {"code": code, "name": name}
            for code, name in UserProfile.countries.field.choices
            if code
        ]

    def update(self, instance, validated_data):
        """Override update method to handle nested user fields."""

        user_data = validated_data.pop("user", {})  # Extract nested user fields
        user = instance.user  # Get the related user

        # ✅ Update User fields (first_name & last_name if provided)
        user.first_name = user_data.get("first_name", user.first_name)
        user.last_name = user_data.get("last_name", user.last_name)
        user.save()

        # ✅ Update UserProfile fields (about, phone_number, countries, avatar)
        instance.about = validated_data.get("about", instance.about)
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.countries = validated_data.get("countries", instance.countries)

        # ✅ Handle avatar upload (check if avatar is provided)
        if "avatar" in validated_data and validated_data["avatar"]:
            instance.avatar = validated_data["avatar"]

        instance.save()
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom serializer to accept both username and email"""

    def validate(self, attrs):
        username_or_email = attrs.get("username")
        password = attrs.get("password")
        user = None
        # Check if user exists by username or email
        user = User.objects.filter(
            Q(email=username_or_email) | Q(username=username_or_email)
        ).first()
        # If no user is found, raise validation error
        if user is None:
            raise serializers.ValidationError(
                "No active account found with the given credentials"
            )
        # Check if the password is correct
        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password")
        # Replace the 'username' with the actual user's username
        attrs["username"] = user.username
        return super().validate(attrs)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class UserProfileTextSerializer(serializers.ModelSerializer):
    """Serializer for profile text fields only (no file upload)"""
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    email = serializers.EmailField(source="user.email", read_only=True)
    countries = serializers.ChoiceField(
        choices=[("", "Not Specified")] + UserProfile.countries.field.choices,
        allow_blank=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "about",
            "phone_number",
            "countries",
        ]

    def update(self, instance, validated_data):
        """Update text fields only"""
        user_data = validated_data.pop("user", {})
        user = instance.user

        # Update User fields
        if "first_name" in user_data:
            user.first_name = user_data["first_name"]
        if "last_name" in user_data:
            user.last_name = user_data["last_name"]
        user.save()

        # Update UserProfile text fields
        if "about" in validated_data:
            instance.about = validated_data["about"]
        if "phone_number" in validated_data:
            instance.phone_number = validated_data["phone_number"]
        if "countries" in validated_data:
            instance.countries = validated_data["countries"]

        instance.save()
        return instance


class UserProfileAvatarSerializer(serializers.ModelSerializer):
    """Serializer for avatar upload only"""
    avatar = serializers.ImageField(required=True)

    class Meta:
        model = UserProfile
        fields = ["avatar"]

    def update(self, instance, validated_data):
        """Update avatar only"""
        if "avatar" in validated_data:
            instance.avatar = validated_data["avatar"]
            instance.save()
        return instance
