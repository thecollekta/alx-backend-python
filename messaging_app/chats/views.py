# messaging_app/chats/views.py

"""Viewsets for Conversation and Message models"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Conversation, Message, User
from .permissions import IsParticipant
from .serializers import (
    ConversationDetailSerializer,
    ConversationListSerializer,
    CustomTokenObtainPairSerializer,
    MessageSerializer,
    UserSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view that includes user data in the response
    """

    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing user accounts.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "head", "options"]  # Remove delete

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == "create":
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter to only show the current user's profile in list view
        Non-staff users can only see their own profile
        """
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(pk=user.pk)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Retrieve the current user's profile
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and creating conversations
    """

    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    http_method_names = ["get", "post", "head", "options"]  # Disable PUT/PATCH/DELETE
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    search_fields = [
        "participants__first_name",
        "participants__last_name",
        "participants__email",
    ]

    def get_queryset(self):
        # Get conversations where current user is a participant
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related("participants", "messages")

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return ConversationListSerializer
        return ConversationDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Add current user to participants if not included
        participants = serializer.validated_data.get("participants", [])
        if request.user not in participants:
            participants.append(request.user)

        conversation = serializer.save(participants=participants)
        return Response(
            ConversationDetailSerializer(conversation).data,
            status=status.HTTP_201_CREATED,
        )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and creating messages within a conversation
    """

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    http_method_names = ["get", "post", "head", "options"]  # Disable PUT/PATCH/DELETE
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["sender__role"]
    ordering_fields = ["sent_at"]
    ordering = ["-sent_at"]
    search_fields = ["message_body", "sender__first_name", "sender__last_name"]

    def get_queryset(self):
        # Get conversation ID from URL
        conversation_id = self.kwargs.get("conversation_id")

        # Verify conversation exists and user is participant
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise NotFound("Conversation not found")

        if self.request.user not in conversation.participants.all():
            raise PermissionDenied("You are not a participant in this conversation")

        # Return messages for this conversation with optimized queries
        return (
            Message.objects.filter(conversation=conversation)
            .select_related("sender", "conversation")
            .order_by("-sent_at")
        )

    def create(self, request, *args, **kwargs):
        # Get conversation ID from URL
        conversation_id = self.kwargs.get("conversation_id")

        # Verify conversation exists and user is participant
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise NotFound("Conversation not found")

        if request.user not in conversation.participants.all():
            raise PermissionDenied("You are not a participant in this conversation")

        # Create message with current user as sender
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(sender=request.user, conversation=conversation)

        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
