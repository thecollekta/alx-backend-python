# messaging/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Message, MessageHistory, Notification


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a notification when a new message is sent.
    """
    if created:  # Only create notification for new messages
        Notification.objects.create(user=instance.receiver, message=instance)


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:  # Only for existing messages
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:  # Content has changed
                MessageHistory.objects.create(
                    message=instance,
                    content=old_message.content,
                    edited_by=instance.sender,
                )
        except Message.DoesNotExist:
            pass  # New message, no history to log
