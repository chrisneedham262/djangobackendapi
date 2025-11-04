from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", include("custom_admin.urls")),  # Points to custom_admin/urls.py
    path("api/", include("accounts.urls")),
    path("api/", include("support_agent.urls")),
]

# ✅ Serve media files only in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = "utils.error_views.handler404"
handler500 = "utils.error_views.handler500"
