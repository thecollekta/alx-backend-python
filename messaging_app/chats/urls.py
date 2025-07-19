# messaging_app/chats/urls.py

"""
URL configuration for chats app
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ConversationViewSet, MessageViewSet

# Create a router and register viewsets
router = DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")

# Custom URL patterns for nested routes
urlpatterns = [
    # Include router URLs
    path("", include(router.urls)),
    # Nested route for messages within a conversation
    path(
        "conversations/<uuid:conversation_id>/messages/",
        MessageViewSet.as_view({"get": "list", "post": "create"}),
        name="conversation-messages",
    ),
]
