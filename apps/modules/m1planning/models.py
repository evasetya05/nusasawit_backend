"""Models for the M1 Planning module."""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from apps.core.models import Company


class LCRRecord(models.Model):
    """Record for storing company input and LCR calculation results."""

    class Meta:
        verbose_name = _("LCR Record")
        verbose_name_plural = _("LCR Records")
        ordering = ['-created_at']

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='lcr_records',
        verbose_name=_("Company")
    )

    # Store as DateField with first day of the month
    period = models.DateField(
        _("Period"),
        help_text=_("Format: YYYY-MM (e.g., 2025-10)")
    )

    total_income = models.BigIntegerField(
        _("Total Income"),
        validators=[MinValueValidator(0)],
        help_text=_("Total income (in IDR, without decimals)")
    )

    total_labor_cost = models.BigIntegerField(
        _("Total Labor Cost"),
        validators=[MinValueValidator(0)],
        help_text=_("Total labor cost (in IDR, without decimals)")
    )

    created_at = models.DateTimeField(
        _("Created At"),
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        _("Updated At"),
        auto_now=True
    )

    def __str__(self):
        return _("LCR {id} - {company} ({period})").format(
            id=self.id,
            company=self.company.name,
            period=self.period.strftime('%Y-%m')
        )

    def clean(self):
        """Validate the model before saving."""
        super().clean()

        # Ensure labor cost doesn't exceed income
        if self.total_labor_cost > self.total_income:
            raise ValidationError({
                'total_labor_cost': _(
                    "Labor cost cannot be greater than total income"
                )
            })

    @property
    def lcr_percentage(self):
        """Calculate Labor Cost Ratio percentage."""
        if not self.total_income:
            return None
        return (self.total_labor_cost / self.total_income) * 100

    @property
    def formatted_income(self):
        """Format total income as IDR currency."""
        return f"Rp {self.total_income:,.0f}".replace(",", ".")

    @property
    def formatted_labor_cost(self):
        """Format total labor cost as IDR currency."""
        return f"Rp {self.total_labor_cost:,.0f}".replace(",", ".")

    @property
    def formatted_lcr(self):
        """Format LCR as a percentage string."""
        if self.lcr_percentage is None:
            return "-"
        return f"{self.lcr_percentage:.2f}%"
