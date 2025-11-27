from django import forms
from apps.core.models import Employee


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

        self.fields['photo'].widget = forms.FileInput()
        self.fields['kk'].widget = forms.FileInput()
        self.fields['ktp'].widget = forms.FileInput()
        self.fields['npwp'].widget = forms.FileInput()

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
