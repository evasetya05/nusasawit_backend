from django import forms
from .models import KPI, KPICycle
from django.forms import DateInput, NumberInput, Textarea, TextInput, Select


class KPIForm(forms.ModelForm):
    """Form untuk pembuatan atau edit KPI."""

    class Meta:
        model = KPI
        fields = ['title', 'description', 'unit', 'weight', 'cycle']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit': TextInput(attrs={'class': 'form-control'}),
            'weight': NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cycle': Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        qs = KPICycle.objects.filter(active=True)
        company = getattr(self.user, 'company', None)
        if company:
            qs = qs.filter(company=company)
        self.fields['cycle'].queryset = qs


class KPICycleForm(forms.ModelForm):
    class Meta:
        model = KPICycle
        fields = ['name', 'period', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
            'end_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
        }


class MonthlyActualTargetForm(forms.Form):
    """Form untuk input target dan nilai aktual per periode (mingguan/bulanan/kuartalan/dll)."""

    month = forms.DateField(
        required=False,
        input_formats=['%Y-%m'],
        widget=DateInput(attrs={'type': 'month', 'class': 'form-control'})
    )

    week = forms.CharField(
        required=False,
        widget=DateInput(attrs={'type': 'week', 'class': 'form-control'})
    )

    target_value = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        widget=NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    actual_value = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        widget=NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    notes = forms.CharField(
        required=False,
        widget=Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    notes_supervisor = forms.CharField(
        required=False,
        widget=Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
