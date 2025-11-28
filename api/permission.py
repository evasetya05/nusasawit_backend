from django.conf import settings
from rest_framework.permissions import BasePermission
from .user_flutter.models import FlutterUser


class HasValidAppKey(BasePermission):
    """Require requests to include the configured APP secret key."""

    message = "Invalid or missing application key."

    def has_permission(self, request, view):
        expected_key = getattr(settings, "APP_SECRET_KEY", None)
        if not expected_key:
            return False

        # Store user identifier from headers if available
        email = request.headers.get("X-EMAIL")
        phone = request.headers.get("X-PHONE")
        
        # Create user identifier from email and/or phone
        if email and phone:
            request.user_identifier = f"{email}|{phone}"
        elif email:
            request.user_identifier = email
        elif phone:
            request.user_identifier = phone
        else:
            request.user_identifier = "unknown"

        # Resolve and save FlutterUser from headers
        FlutterUser.resolve_from_request(request)

        provided_key = request.headers.get("X-APP-KEY")
        if provided_key is None:
            provided_key = request.query_params.get("app_key")

        return provided_key == expected_key
