"""Forms for the M1 Planning module."""
import re
from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import LCRRecord


class LCRRecordForm(forms.ModelForm):
    """Form for creating and updating LCR records."""

    class Meta:
        model = LCRRecord
        fields = ['period', 'total_income', 'total_labor_cost']
        widgets = {
            'period': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'month',
                    'placeholder': 'YYYY-MM'
                },
                format='%Y-%m'
            ),
            'total_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1',
                'min': '0',
                'data-thousands-separator': '.',
            }),
            'total_labor_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1',
                'min': '0',
                'data-thousands-separator': '.',
            }),
        }
        help_texts = {
            'period': _('Select a month and year (YYYY-MM)'),
            'total_income': _('Enter total income in IDR (without decimals)'),
            'total_labor_cost': _('Enter total labor cost in IDR (without decimals)'),
        }

    def __init__(self, *args, **kwargs):
        """Initialize the form with additional attributes."""
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        # Set date format for the period field
        self.fields['period'].input_formats = ['%Y-%m']

        # Set initial period to current month if creating new record
        if not self.instance.pk:
            self.initial['period'] = date.today().strftime('%Y-%m')


    def clean_period(self):
        """Validate the period format."""
        period = self.cleaned_data.get('period')

        if not period:
            raise ValidationError(_('Period is required (select Month-Year)'))

        # Ensure the period is the first day of the month
        if period.day != 1:
            period = period.replace(day=1)

        return period

    def clean(self):
        """Validate the form data."""
        cleaned_data = super().clean()

        # Skip further validation if we already have errors
        if any(self.errors):
            return cleaned_data

        total_income = cleaned_data.get('total_income')
        total_labor_cost = cleaned_data.get('total_labor_cost')
        period = cleaned_data.get('period')

        # Validate that labor cost doesn't exceed income
        if total_income is not None and total_labor_cost is not None:
            if total_labor_cost > total_income:
                self.add_error(
                    'total_labor_cost',
                    _('Labor cost cannot be greater than total income')
                )

        # Check for duplicate period for the same company
        if period and self.company and 'period' not in self.errors:
            qs = LCRRecord.objects.filter(
                company=self.company,
                period=period
            )

            # Exclude current instance when updating
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                self.add_error(
                    'period',
                    _('An LCR record already exists for this period')
                )

        return cleaned_data
