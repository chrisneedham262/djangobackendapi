from django.db import models
from datetime import *
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class DifferentCountries(models.TextChoices):
    AUSTRALIA = "AU", "Australia"
    AUSTRIA = "AT", "Austria"
    BELGIUM = "BE", "Belgium"
    BRAZIL = "BR", "Brazil"
    BULGARIA = "BG", "Bulgaria"
    CANADA = "CA", "Canada"
    CROATIA = "HR", "Croatia"
    CYPRUS = "CY", "Cyprus"
    CZECH_REPUBLIC = "CZ", "Czech Republic"
    DENMARK = "DK", "Denmark"
    ESTONIA = "EE", "Estonia"
    FINLAND = "FI", "Finland"
    FRANCE = "FR", "France"
    GERMANY = "DE", "Germany"
    GIBRALTAR = "GI", "Gibraltar"
    GREECE = "GR", "Greece"
    HONG_KONG = "HK", "Hong Kong"
    HUNGARY = "HU", "Hungary"
    INDIA = "IN", "India"
    INDONESIA = "ID", "Indonesia"
    IRELAND = "IE", "Ireland"
    ITALY = "IT", "Italy"
    JAPAN = "JP", "Japan"
    LATVIA = "LV", "Latvia"
    LIECHTENSTEIN = "LI", "Liechtenstein"
    LITHUANIA = "LT", "Lithuania"
    LUXEMBOURG = "LU", "Luxembourg"
    MALAYSIA = "MY", "Malaysia"
    MALTA = "MT", "Malta"
    MEXICO = "MX", "Mexico"
    NETHERLANDS = "NL", "Netherlands"
    NEW_ZEALAND = "NZ", "New Zealand"
    NORWAY = "NO", "Norway"
    POLAND = "PL", "Poland"
    PORTUGAL = "PT", "Portugal"
    ROMANIA = "RO", "Romania"
    SINGAPORE = "SG", "Singapore"
    SLOVAKIA = "SK", "Slovakia"
    SLOVENIA = "SI", "Slovenia"
    SPAIN = "ES", "Spain"
    SWEDEN = "SE", "Sweden"
    SWITZERLAND = "CH", "Switzerland"
    THAILAND = "TH", "Thailand"
    UNITED_ARAB_EMIRATES = "AE", "United Arab Emirates"
    UNITED_KINGDOM = "GB", "United Kingdom"
    UNITED_STATES = "US", "United States"


class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True, null=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(
        upload_to="profile_imgs/",
        default="profile_imgs/default-profile.png",
        null=True,
        blank=True,
    )
    about = models.TextField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=17, blank=True, null=True
    )  # Moved from User model
    countries = models.CharField(
        max_length=2,
        choices=[(None, "Not Specified")] + DifferentCountries.choices,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True, blank=True, null=True
    )  # Correct usage
    updated_at = models.DateTimeField(auto_now=True)  # Correct usage

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.email} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Password reset token for {self.user.email}"
