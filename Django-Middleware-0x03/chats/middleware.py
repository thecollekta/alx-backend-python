# chats/middleware.py
import logging
from datetime import datetime

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
