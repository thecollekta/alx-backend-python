from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Message, Notification


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal handler to create notifications for all participants in a conversation
    when a new message is created, excluding the sender.
    """
    if not created:
        return

    # Get all participants in the conversation except the sender
    participants = instance.conversation.participants.exclude(
        user_id=instance.sender.user_id
    )

    # Create notifications in bulk for better performance
    notifications = [
        Notification(user=participant, message=instance, notification_type="message")
        for participant in participants
    ]

    # Use bulk_create for better performance with multiple recipients
    if notifications:
        Notification.objects.bulk_create(notifications)


def setup_signals():
    """
    Explicitly connect signals. This function is called in apps.py.
    """
    # The @receiver decorator already connects the signal,
    # but we are keeping this for explicit handling if needed
    pass
