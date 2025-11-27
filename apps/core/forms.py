from django import forms
from django.contrib.auth import get_user_model
from .models import Employee
User = get_user_model()


class UserUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="New Password", widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(
        label="Confirm Password", widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User  # Ensure this is the correct model you're working with
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class EmployeeForm(forms.ModelForm):
    name = forms.CharField(max_length=225, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Employee
        fields = ['name', 'email', 'position', 'department', 'phone', 'address',
                  'manager', 'hire_date']
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
        }


class EmployeeEditForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'name', 'email', 'position', 'department', 'phone', 'address', 'manager',
            'hire_date', 'is_active', 'photo', 'kk', 'ktp', 'npwp'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        # Customize manager queryset to only show employees from the same company
        if company:
            self.fields['manager'].queryset = Employee.objects.filter(
                company=company
            ).exclude(id=self.instance.id if self.instance else None)

        # Add Bootstrap classes to all fields
        for field in self.fields.values():
            if getattr(field.widget, 'input_type', None) != 'checkbox':
                field.widget.attrs.update({'class': 'form-control'})
            if field.required:
                field.widget.attrs['required'] = ''
                field.label = f"{field.label} *"
