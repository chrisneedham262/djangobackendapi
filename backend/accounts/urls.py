from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView, TokenBlacklistView
from . import views

urlpatterns = [
    path("userlist/", views.UserList.as_view(), name="user-list"),
    path("register/", views.customerRegister, name="customer-register"),
    path("me/", views.currentUser, name="current_user"),
    path("me/update/", views.updateUser, name="update_user"),
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "token/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"
    ),
    path(
        "user-profile/",
        views.UserProfileDetailView.as_view(),
        name="user-profile-detail",
    ),
    # New separate endpoints for profile updates
    path(
        "user-profile/text/",
        views.UserProfileTextUpdateView.as_view(),
        name="user-profile-text-update",
    ),
    path(
        "user-profile/avatar/",
        views.UserProfileAvatarUpdateView.as_view(),
        name="user-profile-avatar-update",
    ),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("contact/", views.ContactCreateView.as_view(), name="contact-create"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("password-reset/", views.passwordResetRequest, name="password-reset-request"),
    path("password-reset-confirm/", views.passwordResetConfirm, name="password-reset-confirm"),
]
