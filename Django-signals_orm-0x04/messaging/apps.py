# messaging/apps.py

from django.apps import AppConfig


class MessagingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "messaging"

    def ready(self):
        # Import signals to register them
        import messaging.signals  # noqa
