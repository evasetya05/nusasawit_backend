from django.conf import settings
from rest_framework.permissions import BasePermission


class HasValidAppKey(BasePermission):
    """Require requests to include the configured APP secret key."""

    message = "Invalid or missing application key."

    def has_permission(self, request, view):
        expected_key = getattr(settings, "APP_SECRET_KEY", None)
        if not expected_key:
            return False

        provided_key = request.headers.get("X-APP-KEY")
        if provided_key is None:
            provided_key = request.query_params.get("app_key")

        return provided_key == expected_key
