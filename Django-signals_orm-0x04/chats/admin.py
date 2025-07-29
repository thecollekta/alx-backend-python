# messaging_app/chats/admin.py

"""
Admin registration for chats app models: User, Conversation, Message, Notification
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework.permissions import IsAdminUser

from .models import Conversation, Message, Notification, User


# Custom User Admin configuration
class CustomUserAdmin(UserAdmin):
    """Custom User model display in admin"""

    model = User
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = ("is_staff", "is_superuser", "role")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "phone_number", "role")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "role"),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    def has_module_permission(self, request):
        return IsAdminUser().has_permission(request, self)


# Custom Conversation configuration
class ConversationAdmin(admin.ModelAdmin):
    """Admin view for Conversation model"""

    list_display = ("conversation_id", "created_at", "participants_list")
    filter_horizontal = ("participants",)

    def participants_list(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])

    def has_module_permission(self, request):
        return IsAdminUser().has_permission(request, self)


# Custom Message configuration
class MessageAdmin(admin.ModelAdmin):
    """Admin view for Message model"""

    list_display = (
        "message_id",
        "sender",
        "conversation",
        "sent_at",
        "short_message_body",
    )
    list_filter = ("sender", "conversation")
    search_fields = ("message_body", "sender__username")
    date_hierarchy = "sent_at"

    @admin.display(description="Message")
    def short_message_body(self, obj):
        return (
            obj.message_body[:50] + "..."
            if len(obj.message_body) > 50
            else obj.message_body
        )

    def has_module_permission(self, request):
        return IsAdminUser().has_permission(request, self)


# Custom Notification configuration
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model"""

    list_display = (
        "user",
        "get_message_snippet",
        "notification_type",
        "is_read",
        "created_at",
    )
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "message__message_body",
    )
    readonly_fields = ("created_at", "notification_id")
    date_hierarchy = "created_at"
    list_select_related = ("user", "message")

    @admin.display(description="Message Snippet")
    def get_message_snippet(self, obj):
        """Return a snippet of the message content"""
        if obj.message and obj.message.message_body:
            return f"{obj.message.message_body[:50]}..."
        return "No message"


# Register models with admin site
admin.site.register(User, CustomUserAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
