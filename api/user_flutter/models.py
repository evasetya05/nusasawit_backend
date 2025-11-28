from __future__ import annotations

from typing import Optional, Tuple

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.db import models


EMAIL_HEADER = "X-EMAIL"
PHONE_HEADER = "X-PHONE"


class FlutterUser(models.Model):
    """Simpan identitas user yang melakukan request dari aplikasi Flutter."""

    identifier = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - representasional
        return self.identifier

    @staticmethod
    def build_identifier(email: str | None, phone: str | None) -> str | None:
        email_part = (email or "").strip().lower()
        phone_part = (phone or "").strip()
        if email_part and phone_part:
            return f"email:{email_part}|phone:{phone_part}"
        if email_part:
            return f"email:{email_part}"
        if phone_part:
            return f"phone:{phone_part}"
        return None

    @classmethod
    def resolve_from_request(cls, request) -> Tuple[Optional["FlutterUser"], Optional[str]]:
        """Ambil atau buat FlutterUser berdasarkan header request."""
        raw_email = request.headers.get(EMAIL_HEADER)
        raw_phone = request.headers.get(PHONE_HEADER)

        email = cls._normalize_email(raw_email)
        phone = cls._normalize_phone(raw_phone)
        identifier = cls.build_identifier(email, phone)

        if not identifier:
            return None, None

        defaults = {}
        if email:
            defaults["email"] = email
        if phone:
            defaults["phone_number"] = phone

        flutter_user, created = cls.objects.get_or_create(
            identifier=identifier,
            defaults=defaults,
        )

        update_fields = []
        if email and flutter_user.email != email:
            flutter_user.email = email
            update_fields.append("email")
        if phone and flutter_user.phone_number != phone:
            flutter_user.phone_number = phone
            update_fields.append("phone_number")
        if update_fields:
            flutter_user.save(update_fields=update_fields + ["updated_at"])

        setattr(request, "flutter_user", flutter_user)
        setattr(request, "flutter_user_identifier", identifier)
        return flutter_user, identifier

    @staticmethod
    def _normalize_email(raw_email: Optional[str]) -> Optional[str]:
        if not raw_email:
            return None
        email = raw_email.strip().lower()
        try:
            validate_email(email)
        except DjangoValidationError:
            return None
        return email

    @staticmethod
    def _normalize_phone(raw_phone: Optional[str]) -> Optional[str]:
        if not raw_phone:
            return None
        phone = raw_phone.strip()
        return phone or None
