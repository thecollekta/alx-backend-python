# messaging_app/chats/serializers.py

"""
Serializers for User, Conversation, and Message models
"""

from rest_framework import serializers

from .models import Conversation, Message, User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    user_id = serializers.UUIDField(source="id", read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    phone_number = serializers.CharField(allow_blank=True, required=False)
    role = serializers.CharField()

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

    message_id = serializers.UUIDField(source="id", read_only=True)
    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = ["message_id", "sender", "message_body", "sent_at"]
        read_only_fields = ["message_id", "sent_at", "sender"]


class ConversationListSerializer(serializers.ModelSerializer):
    conversation_id = serializers.UUIDField(source="id", read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["conversation_id", "participants", "created_at", "last_message"]
        read_only_fields = ["conversation_id", "created_at"]

    def get_last_message(self, obj):
        last_message = obj.messages.order_by("-sent_at").first()
        if last_message:
            return MessageSerializer(last_message).data
        return None


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested participants and messages"""

    conversation_id = serializers.UUIDField(source="id", read_only=True)
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
