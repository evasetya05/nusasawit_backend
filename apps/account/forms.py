from django import forms
from django_registration.forms import RegistrationFormTermsOfService
from django.utils.translation import gettext as _
from .models import SystemUser


class UserRegistrationForm(RegistrationFormTermsOfService):
    tos = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={
            'required': _('You must accept the terms of service'),
        }
    )


class AcceptInvitationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label=_("Password"))
    password2 = forms.CharField(
        widget=forms.PasswordInput, label=_("Password confirmation"))

    class Meta:
        model = SystemUser
        fields = ['username', 'password']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError(_('Passwords don\'t match.'))
        return cd['password2']
