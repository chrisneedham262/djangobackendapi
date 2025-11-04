from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.staticfiles.storage import staticfiles_storage
from accounts.models import User, UserProfile, Contact  # Import your models
from support_agent.models import FAQ, ChatHistory


class CustomAdminSite(admin.AdminSite):
    site_header = "My Custom Admin"
    site_title = "Admin Panel"
    index_title = "Welcome to My Admin Panel"

    def each_context(self, request):
        # Add the custom CSS to the context
        context = super().each_context(request)
        context["custom_admin_css"] = staticfiles_storage.url("admin/custom_admin.css")
        return context


custom_admin_site = CustomAdminSite(name="custom_admin")

# Register User with default UserAdmin
User = get_user_model()
custom_admin_site.register(User, UserAdmin)


# Custom UserProfile Admin
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "email", "about", "phone_number", "countries", "created_at")
    search_fields = ("user__username", "user__email", "phone_number", "countries")
    list_filter = ("countries", "created_at")

    def email(self, obj):
        """Display email from related User model."""
        return obj.user.email


custom_admin_site.register(UserProfile, UserProfileAdmin)


# Custom Contact Admin
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "formatted_created_at")
    search_fields = ("name", "email")
    list_filter = ("created_at",)

    def formatted_created_at(self, obj):
        """Display formatted created_at date and time."""
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    formatted_created_at.admin_order_field = "created_at"
    formatted_created_at.short_description = "Created At"


custom_admin_site.register(Contact, ContactAdmin)


# Custom FAQ Admin
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "answer")
    search_fields = ("question", "answer")
    list_filter = ("question",)
    ordering = ("question",)
    list_per_page = 20
    actions = ["bulk_delete"]

    def bulk_delete(self, request, queryset):
        queryset.delete()

    bulk_delete.short_description = "Delete selected FAQs"


custom_admin_site.register(FAQ, FAQAdmin)


# Custom ChatHistory Admin
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "question",
        "response",
        "timestamp",
    )
    search_fields = ("user_id", "question", "response")
    list_filter = ("timestamp",)
    ordering = ("-timestamp",)
    list_per_page = 20
    readonly_fields = ("user_id", "question", "response", "timestamp")


custom_admin_site.register(ChatHistory, ChatHistoryAdmin)
