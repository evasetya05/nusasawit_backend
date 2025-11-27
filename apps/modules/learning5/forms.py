from django import forms
from apps.core.models import Employee
from .models import TrainingNeed, Competency


class CompetencyForm(forms.ModelForm):
    class Meta:
        model = Competency
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap form-control class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class TrainingNeedForm(forms.ModelForm):
    class Meta:
        model = TrainingNeed
        fields = [
            'employee', 'competency', 'detail_competency', 'current_score',
            'desired_score', 'when_to_traine', 'jenis_pelatihan',
            'done_at', 'cost', 'notes'
        ]
        widgets = {
            'current_score': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'desired_score': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'when_to_traine': forms.DateInput(attrs={'type': 'date'}),
            'done_at': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

        # Filter employee choices based on current user role
        employee_qs = Employee.objects.none()
        if current_user:
            person = getattr(current_user, 'person', None)
            if current_user.is_owner():
                if current_user.company:
                    employee_qs = Employee.objects.filter(company=current_user.company)
                else:
                    employee_qs = Employee.objects.all()
            elif person and person.subordinates.exists():
                employee_qs = person.subordinates.all()

        instance = kwargs.get('instance')
        if instance and instance.employee_id:
            employee_qs = Employee.objects.filter(pk=instance.employee_id) | employee_qs

        self.fields['employee'].queryset = employee_qs.order_by('name').distinct()

        # ✅ Competency berdasarkan name
        self.fields['competency'].queryset = Competency.objects.all().order_by('name')
        self.fields['competency'].label_from_instance = lambda obj: obj.name

        # ✅ Detail competency berdasarkan description
        qs = Competency.objects.exclude(description__exact="").order_by('description')
        self.fields['detail_competency'].queryset = qs
        self.fields['detail_competency'].label_from_instance = lambda obj: obj.description or obj.name

        # Add Bootstrap form-control class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
