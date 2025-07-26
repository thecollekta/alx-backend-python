# chats/middleware.py

import logging
from datetime import datetime, time

from django.http import HttpResponseForbidden
from django.utils import timezone

# Configure the logger
logger = logging.getLogger("request_logger")
logger.setLevel(logging.INFO)

# Create file handler which logs even debug messages
file_handler = logging.FileHandler("requests.log")
file_handler.setLevel(logging.INFO)

# Create formatter and add it to the handlers
formatter = logging.Formatter("%(message)s")
file_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)


class RequestLoggingMiddleware:
    """Middleware for logging user requests"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Process request and log request information"""
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # Get the user (or 'Anonymous' if not authenticated)
        user = (
            request.user.username
            if hasattr(request, "user") and request.user.is_authenticated
            else "Anonymous"
        )

        # Log the request
        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        # Call the next middleware/view
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access to chat views outside the allowed hours
    between the hours of 6PM (18:00) and 9PM (21:00)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define restricted hours (9 PM to 6 AM)
        start_time = time(21, 0)  # 9:00 PM
        end_time = time(6, 0)  # 6:00 AM
        current_time = timezone.now().time()

        # Check if current time is within restricted hours
        if start_time <= current_time or current_time <= end_time:
            return HttpResponseForbidden(
                "Access to the chat is restricted between 9:00 PM and 6:00 AM. "
                "Please try again during working hours."
            )

        return self.get_response(request)
