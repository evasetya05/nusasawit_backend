from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from api.user_flutter.models import FlutterUser


def validate_image_size(image_field) -> None:
    """Ensure image file size does not exceed 150KB."""
    if not image_field:
        return

    max_size_kb = 150
    if image_field.size > max_size_kb * 1024:
        raise ValidationError(f"Ukuran file gambar tidak boleh melebihi {max_size_kb} KB.")


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
        validators=[validate_image_size],
        blank=True,
        null=True,
    )
    photo_2 = models.ImageField(
        upload_to="pasar/items/",
        validators=[validate_image_size],
        blank=True,
        null=True,
    )

    provinsi = models.ForeignKey(
        'area.Provinsi', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='marketplace_items'
    )
    kabupaten_kota = models.ForeignKey(
        'area.KabupatenKota', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='marketplace_items'
    )
    kecamatan = models.ForeignKey(
        'area.Kecamatan', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='marketplace_items'
    )
    desa = models.ForeignKey(
        'area.Desa', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='marketplace_items'
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

    

    # ... rest of the model ...
    is_purchase_intent = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:  # pragma: no cover - representasional
        identifier = self.buyer_identifier or "anonim"
        return f"Komentar {identifier}"
