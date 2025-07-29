from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Conversation, Message, Notification

User = get_user_model()


class NotificationSignalTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.sender = User.objects.create_user(
            username="sender",
            email="sender@example.com",
            first_name="Sender",
            last_name="User",
            password="testpass123",
            role="host",
        )

        self.recipient1 = User.objects.create_user(
            username="recipient1",
            email="recipient1@example.com",
            first_name="Recipient",
            last_name="One",
            password="testpass123",
            role="guest",
        )

        self.recipient2 = User.objects.create_user(
            username="recipient2",
            email="recipient2@example.com",
            first_name="Recipient",
            last_name="Two",
            password="testpass123",
            role="guest",
        )

        # Create a conversation
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(
            self.sender, self.recipient1, self.recipient2
        )

    def test_notification_created_on_message_save(self):
        """Test that a notification is created for each recipient when a message is sent"""
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            conversation=self.conversation,
            message_body="Hello, this is a test message",
        )

        # Verify notifications were created for both recipients
        notifications = Notification.objects.filter(message=message)
        self.assertEqual(notifications.count(), 2)  # Should be one for each recipient

        # Verify the correct users received notifications
        recipient_emails = {n.user.email for n in notifications}
        self.assertIn(self.recipient1.email, recipient_emails)
        self.assertIn(self.recipient2.email, recipient_emails)

        # Verify notification details
        for notification in notifications:
            self.assertEqual(notification.notification_type, "message")
            self.assertFalse(notification.is_read)
            self.assertIsNotNone(notification.created_at)

    def test_no_notification_for_sender(self):
        """Test that the sender doesn't receive a notification for their own message"""
        message = Message.objects.create(
            sender=self.sender,
            conversation=self.conversation,
            message_body="This message should not notify me",
        )

        # Verify no notification was created for the sender
        self.assertFalse(
            Notification.objects.filter(message=message, user=self.sender).exists()
        )

    def test_notification_on_message_update(self):
        """Test that notifications aren't created when updating an existing message"""
        # Create initial message
        message = Message.objects.create(
            sender=self.sender,
            conversation=self.conversation,
            message_body="Initial message",
        )

        # Clear any notifications from creation
        Notification.objects.all().delete()

        # Update the message
        message.message_body = "Updated message"
        message.save()

        # Verify no new notifications were created
        self.assertEqual(Notification.objects.count(), 0)


class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
            role="guest",
        )

        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user)

        self.message = Message.objects.create(
            sender=self.user,
            conversation=self.conversation,
            message_body="Test message",
        )

    def test_mark_as_read(self):
        """Test the mark_as_read method"""
        notification = Notification.objects.create(
            user=self.user,
            message=self.message,
            notification_type="message",
            is_read=False,
        )

        self.assertFalse(notification.is_read)
        notification.mark_as_read()
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_notification_str_representation(self):
        """Test the string representation of a notification"""
        notification = Notification.objects.create(
            user=self.user,
            message=self.message,
            notification_type='message'
        )
        
        self.assertIn("message for", str(notification).lower())
        self.assertIn(self.user.email, str(notification))
