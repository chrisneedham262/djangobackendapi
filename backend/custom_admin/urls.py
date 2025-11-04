from django.urls import path
from .admin import custom_admin_site

# Explicit URL patterns for custom admin
urlpatterns = [
    path('', custom_admin_site.urls),
]

