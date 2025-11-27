from django import forms
from apps.core.models import Employee
from .models import DocumentStandar


class EmployeeForm(forms.ModelForm):
    name = forms.CharField(max_length=225, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Employee
        fields = ['name', 'email', 'position', 'department', 'phone', 'address',
                  'emergency_contact', 'manager', 'hire_date', 'birth_date', 'pph21_status']
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'pph21_status': forms.Select(attrs={'class': 'form-select'}),
        }


class EmployeeEditForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'name', 'email', 'position', 'department', 'phone', 'address', 'emergency_contact', 'manager',
            'hire_date', 'birth_date', 'is_active', 'photo', 'kk', 'ktp', 'npwp',
            'basic_salary', 'default_allowance', 'pph21_status'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'basic_salary': forms.NumberInput(attrs={'min': '0'}),
            'default_allowance': forms.NumberInput(attrs={'min': '0'}),
            'pph21_status': forms.Select(attrs={'class': 'form-select'}),
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


class SOPSuggestionForm(forms.ModelForm):
    MAX_SIZE = 2 * 1024 * 1024  # 2 MB

    class Meta:
        model = DocumentStandar
        fields = ['name', 'file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama dokumen'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if not f:
            return f
        if f.size > self.MAX_SIZE:
            raise forms.ValidationError('Ukuran file maksimal 2 MB.')
        return f
