from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


EMAIL_HEADER = "X-USER-EMAIL"


def _normalize_email(raw_email: str) -> str:
    email = raw_email.strip().lower()
    try:
        validate_email(email)
    except DjangoValidationError:
        raise ValidationError({"detail": "Email tidak valid."})
    return email


def _generate_unique_username(email: str) -> str:
    base_slug = slugify(email.split("@")[0])
    if not base_slug:
        base_slug = slugify(email.replace("@", "-")) or "user"
    candidate = base_slug
    User = get_user_model()
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        candidate = f"{base_slug}{suffix}"
        suffix += 1
    return candidate


def get_or_create_user_by_email(raw_email: str):
    email = _normalize_email(raw_email)
    User = get_user_model()
    user = User.objects.filter(email__iexact=email).first()
    if user:
        return user
    username = _generate_unique_username(email)
    password = get_random_string(12)
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )


def get_request_email(request) -> str:
    header_email = request.headers.get(EMAIL_HEADER)
    query_email = request.query_params.get("email") if hasattr(request, "query_params") else None
    body_email = request.data.get("email") if hasattr(request, "data") else None

    email = header_email or query_email or body_email
    if not email:
        raise ValidationError({"detail": "Parameter email wajib dikirimkan."})
    return _normalize_email(email)


def resolve_user_from_request(request):
    email = get_request_email(request)
    user = get_or_create_user_by_email(email)
    if hasattr(request, "_request"):
        request._user = user
    else:
        setattr(request, "user", user)
    setattr(request, "email_user", user)
    return user


class EmailIdentityMixin:
    """Mixin untuk APIView/GenericView agar mengenali user berdasarkan email."""

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self._email_user = resolve_user_from_request(request)

    def get_request_user(self):
        if not hasattr(self, "_email_user"):
            self._email_user = resolve_user_from_request(self.request)
        return self._email_user
