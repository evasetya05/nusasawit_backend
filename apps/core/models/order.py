from django.conf import settings
from django.db import models

class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    )
    BILLING_CYCLE_CHOICES = (
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    company = models.ForeignKey('Company', on_delete=models.CASCADE)

    base_price = models.PositiveIntegerField(default=0)
    user_pack_price = models.PositiveIntegerField(default=0)
    modules = models.JSONField()
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLE_CHOICES, default="monthly")
    total_price = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk or 'N/A'} - {self.company.name} - {self.status}"


class PaymentReceipt(models.Model):
    """Stores user-submitted payment receipts for manual verification."""
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='receipts')
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_receipts')
    receipt_file = models.FileField(upload_to='receipts/%Y/%m/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt #{self.pk or 'N/A'} - {self.company.name}"
