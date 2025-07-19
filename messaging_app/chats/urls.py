# messaging_app/chats/urls.py

"""
URL configuration for chats app
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import ConversationViewSet, MessageViewSet

# Create a router and register viewsets
router = DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")

# Create nested router for messages within conversations
conversations_router = routers.NestedDefaultRouter(
    router, r"conversations", lookup="conversation"
)
conversations_router.register(
    r"messages", MessageViewSet, basename="conversation-messages"
)

app_name = "chats"

# Custom URL patterns for nested routes
urlpatterns = [
    # Main router URLs (includes conversations CRUD)
    path("", include(router.urls)),
    # Nested router URLs (includes messages within conversations)
    path("", include(conversations_router.urls)),
    # Alternative explicit routes if nested router isn't available
    path(
        "api/v1/conversations/<uuid:conversation_id>/messages/",
        MessageViewSet.as_view({"get": "list", "post": "create"}),
        name="conversation-messages-list",
    ),
    path(
        "api/v1/conversations/<uuid:conversation_id>/messages/<uuid:pk>/",
        MessageViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="conversation-messages-detail",
    ),
]
