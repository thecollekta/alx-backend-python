# chats/middleware.py

import logging
from collections import defaultdict
from datetime import datetime, time, timedelta

from django.http import HttpResponseForbidden, JsonResponse
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


class OffensiveLanguageMiddleware:
    """
    Middleware to limit the number of chat messages per IP address.
    Implements a rate limit of 5 messages per minute per IP.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to store IP addresses and their request timestamps
        self.requests = defaultdict(list)
        # Rate limit configuration
        self.RATE_LIMIT = 5  # Max 5 requests
        self.TIME_WINDOW = 60  # 1 minute in seconds

    def __call__(self, request):
        # Only apply rate limiting to POST requests to message endpoints
        if request.method == "POST" and "messages" in request.path:
            # Get client IP address
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]
            else:
                ip = request.META.get("REMOTE_ADDR")

            current_time = datetime.now()

            # Clean up old requests outside the time window
            self.requests[ip] = [
                t
                for t in self.requests[ip]
                if current_time - t < timedelta(seconds=self.TIME_WINDOW)
            ]

            # Check if rate limit exceeded
            if len(self.requests[ip]) >= self.RATE_LIMIT:
                return JsonResponse(
                    {
                        "error": "Rate limit exceeded. Please try again later.",
                        "status": "error",
                        "code": 429,
                    },
                    status=429,
                )

            # Add current request timestamp
            self.requests[ip].append(current_time)

            # Log the rate limit status (optional)
            remaining = self.RATE_LIMIT - len(self.requests[ip])
            print(f"IP {ip}: {remaining} requests remaining in current window")

        return self.get_response(request)


class RolePermissionMiddleware:
    """
    Middleware to enforce role-based access control.
    Only allows admin or moderator roles to perform certain actions.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Define protected paths and their required roles
        self.protected_paths = {
            "/api/v1/users/": ["admin"],  # User management
            "/api/v1/conversations/": ["admin", "moderator"],  # Conversation management
        }

    def __call__(self, request):
        # Only check for protected paths
        if any(path in request.path for path in self.protected_paths):
            # Skip for safe methods (GET, HEAD, OPTIONS)
            if request.method not in ["GET", "HEAD", "OPTIONS"]:
                # Check if user is authenticated
                if not hasattr(request, "user") or not request.user.is_authenticated:
                    return JsonResponse(
                        {
                            "error": "Authentication required",
                            "status": "error",
                            "code": 401,
                        },
                        status=401,
                    )

                # Get user's role
                user_role = getattr(request.user, "role", None)

                # Get required roles for the current path
                required_roles = next(
                    (
                        roles
                        for path, roles in self.protected_paths.items()
                        if path in request.path
                    ),
                    [],
                )

                # Check if user has required role
                if user_role not in required_roles:
                    return JsonResponse(
                        {
                            "error": "Insufficient permissions. Admin or moderator role required.",
                            "status": "error",
                            "code": 403,
                        },
                        status=403,
                    )

        return self.get_response(request)
