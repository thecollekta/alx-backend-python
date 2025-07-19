# messaging_app/chats/serializers.py

"""
Serializers for User, Conversation, and Message models
"""

from rest_framework import serializers

from .models import Conversation, Message, User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = [
            "user_id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "created_at",
        ]
        read_only_fields = ["user_id", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""

    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["message_id", "sender", "message_body", "sent_at", "conversation"]
        read_only_fields = ["message_id", "sent_at", "sender"]
        extra_kwargs = {"conversation": {"write_only": True}}


class ConversationListSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "participants", "created_at", "last_message"]
        read_only_fields = ["id", "created_at"]


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested participants and messages"""

    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    # Field for writing participants (using IDs)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True, source="participants"
    )

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "participant_ids",
            "created_at",
            "messages",
        ]
        read_only_fields = ["conversation_id", "created_at", "messages"]

    def validate_participant_ids(self, value):
        """Ensure at least 2 participants in a conversation"""
        if len(value) < 2:
            raise serializers.ValidationError(
                "A conversation must have at least 2 participants."
            )
        return value
