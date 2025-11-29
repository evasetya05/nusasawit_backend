from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from PIL import Image

from api.user_flutter.models import FlutterUser


def validate_image_dimension(image_field) -> None:
    """Ensure image largest dimension does not exceed 200px."""
    if not image_field:
        return

    try:
        file_obj = getattr(image_field, "file", image_field)
        position = file_obj.tell() if hasattr(file_obj, "tell") else None
        image = Image.open(file_obj)
        width, height = image.size
        if position is not None and hasattr(file_obj, "seek"):
            file_obj.seek(position)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValidationError("Gagal memproses gambar.") from exc

    max_size = 200
    if width > max_size or height > max_size:
        raise ValidationError(
            f"Ukuran gambar maksimal {max_size}px untuk lebar dan tinggi."
        )


class MarketplaceItem(models.Model):
    seller = models.ForeignKey(
        FlutterUser,
        on_delete=models.SET_NULL,
        related_name="marketplace_items",
        null=True,
        blank=True,
    )
    seller_identifier = models.CharField(max_length=255, blank=True)

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    photo_1 = models.ImageField(
        upload_to="pasar/items/",
        validators=[validate_image_dimension],
        blank=True,
        null=True,
    )
    photo_2 = models.ImageField(
        upload_to="pasar/items/",
        validators=[validate_image_dimension],
        blank=True,
        null=True,
    )

    is_sold = models.BooleanField(default=False)
    sold_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - representasional
        return self.title

    def clean(self) -> None:
        super().clean()
        if not self.photo_1 and not self.photo_2:
            raise ValidationError("Minimal satu foto diperlukan.")

        for image_field in (self.photo_1, self.photo_2):
            validate_image_dimension(image_field)

    def set_sold(self, is_sold: bool = True) -> None:
        self.is_sold = is_sold
        self.sold_at = timezone.now() if is_sold else None
        self.save(update_fields=["is_sold", "sold_at", "updated_at"])


class MarketplaceComment(models.Model):
    item = models.ForeignKey(
        MarketplaceItem,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    flutter_user = models.ForeignKey(
        FlutterUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marketplace_comments",
    )
    buyer_identifier = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    is_purchase_intent = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:  # pragma: no cover - representasional
        identifier = self.buyer_identifier or "anonim"
        return f"Komentar {identifier}"

