from django import forms

from apps.core.models import Employee


class ThreadStartForm(forms.Form):
    supervisor = forms.ModelChoiceField(
        queryset=Employee.objects.none(),
        label="Supervisor",
        help_text="Pilih supervisor yang ingin diajak percakapan",
    )
    subject = forms.CharField(
        label="Subjek",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Opsional",
                "class": "form-control",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        queryset = (
            Employee.objects.filter(is_active=True, subordinates__isnull=False)
            .distinct()
            .order_by("name")
        )

        person = getattr(user, "person", None) if user else None
        company = getattr(person, "company", None)
        if company:
            queryset = queryset.filter(company=company)

        self.fields["supervisor"].queryset = queryset


class MessageForm(forms.Form):
    content = forms.CharField(
        label="Pesan",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Tulis pesan...",
                "class": "form-control",
            }
        ),
    )
