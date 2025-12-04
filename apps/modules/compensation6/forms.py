from django import forms
import calendar
from .models import PayrollPeriod, Allowance, Deduction, BPJSConfig, Attendance, LeaveRequest, WorkRequest
from apps.core.models import Employee

class PayrollPeriodForm(forms.ModelForm):
    class Meta:
        model = PayrollPeriod
        fields = ['month', 'year', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('Tanggal akhir tidak boleh lebih awal dari tanggal awal.')

        return cleaned_data


class AllowanceForm(forms.ModelForm):
    class Meta:
        model = Allowance
        fields = ['employee', 'period', 'name', 'amount']


class DeductionForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['employee', 'period', 'name', 'amount']


class BPJSTKForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['employee', 'period', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].label = "JHT Karyawan"
        self.fields['amount'].widget.attrs['placeholder'] = "JHT Karyawan (40,000)"
        self.fields['amount'].widget.attrs['step'] = "1000"


class BPJSTKJPForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['employee', 'period', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].label = "JP Karyawan"
        self.fields['amount'].widget.attrs['placeholder'] = "JP Karyawan (20,000)"
        self.fields['amount'].widget.attrs['step'] = "1000"


class BPJSKesehatanForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['employee', 'period', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].label = "BPJS Kesehatan Karyawan"
        self.fields['amount'].widget.attrs['placeholder'] = "BPJS Kesehatan Karyawan"
        self.fields['amount'].widget.attrs['step'] = "1000"


class PajakForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['employee', 'period', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].label = "Pajak Penghasilan"
        self.fields['amount'].widget.attrs['placeholder'] = "Pajak Penghasilan"
        self.fields['amount'].widget.attrs['step'] = "1000"


class BPJSTKJKKCompanyForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['employee', 'period', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].label = "JKK Perusahaan"
        self.fields['amount'].widget.attrs['placeholder'] = "JKK Perusahaan"
        self.fields['amount'].widget.attrs['step'] = "1000"


class BPJSTKJKMCompanyForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['employee', 'period', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].label = "JKM Perusahaan"
        self.fields['amount'].widget.attrs['placeholder'] = "JKM Perusahaan"
        self.fields['amount'].widget.attrs['step'] = "1000"


class BPJSTKJHTCompanyForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['employee', 'period', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].label = "JHT Perusahaan"
        self.fields['amount'].widget.attrs['placeholder'] = "JHT Perusahaan"
        self.fields['amount'].widget.attrs['step'] = "1000"


class BPJSTKJPCompanyForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['employee', 'period', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].label = "JP Perusahaan"
        self.fields['amount'].widget.attrs['placeholder'] = "JP Perusahaan"
        self.fields['amount'].widget.attrs['step'] = "1000"


class BPJSKesehatanCompanyForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['employee', 'period', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].label = "BPJS Kesehatan Perusahaan"
        self.fields['amount'].widget.attrs['placeholder'] = "BPJS Kesehatan Perusahaan"
        self.fields['amount'].widget.attrs['step'] = "1000"


class BPJSConfigForm(forms.ModelForm):
    class Meta:
        model = BPJSConfig
        fields = [
            'emp_jkk_pct', 'emp_jkm_pct', 'emp_jht_pct', 'emp_jp_pct', 'emp_jkn_pct',
            'com_jkk_pct', 'com_jkm_pct', 'com_jht_pct', 'com_jp_pct', 'com_jkn_pct',
            'working_days_per_month', 'overtime_rate'
        ]
        widgets = {f: forms.NumberInput(attrs={'step': '0.01'}) for f in [
            'emp_jkk_pct','emp_jkm_pct','emp_jht_pct','emp_jp_pct','emp_jkn_pct','com_jkk_pct','com_jkm_pct','com_jht_pct','com_jp_pct','com_jkn_pct']}

class BPJSConfigKaryawanForm(forms.ModelForm):
    class Meta:
        model = BPJSConfig
        fields = ['emp_jkk_pct', 'emp_jkm_pct', 'emp_jht_pct', 'emp_jp_pct', 'emp_jkn_pct']
        widgets = {f: forms.NumberInput(attrs={'step': '0.01'}) for f in ['emp_jkk_pct','emp_jkm_pct','emp_jht_pct','emp_jp_pct','emp_jkn_pct']}

class BPJSConfigPerusahaanForm(forms.ModelForm):
    class Meta:
        model = BPJSConfig
        fields = ['com_jkk_pct', 'com_jkm_pct', 'com_jht_pct', 'com_jp_pct', 'com_jkn_pct']
        widgets = {f: forms.NumberInput(attrs={'step': '0.01'}) for f in ['com_jkk_pct','com_jkm_pct','com_jht_pct','com_jp_pct','com_jkn_pct']}


class PayslipSelectionForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())
    month = forms.ChoiceField()
    year = forms.ChoiceField()

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter employees based on user role
        if user:
            person = getattr(user, 'person', None)
            is_owner_attr = getattr(user, 'is_owner', False)
            is_owner = is_owner_attr() if callable(is_owner_attr) else is_owner_attr
            
            if is_owner:
                # Owner sees all employees in their company
                self.fields['employee'].queryset = Employee.objects.filter(
                    company=user.company, 
                    is_active=True
                ).order_by('name')
            elif person:
                # Check if person is an employee (supervisor or regular employee)
                has_employee = hasattr(person, 'employee')
                
                if has_employee:
                    # Person is an employee - can be supervisor or regular employee
                    employee = person.employee
                    
                    # Get all subordinates recursively
                    def get_descendants(emp):
                        descendants = set()
                        direct_subs = emp.subordinates.all()
                        for sub in direct_subs:
                            descendants.add(sub.id)
                            descendants.update(get_descendants(sub))
                        return descendants
                    
                    subordinate_ids = get_descendants(employee)
                    # Include self for supervisor and regular employee
                    allowed_ids = subordinate_ids | {employee.id}
                    
                    self.fields['employee'].queryset = Employee.objects.filter(
                        id__in=allowed_ids,
                        is_active=True
                    ).order_by('name')
                else:
                    # Person without employee record - fallback to self only
                    try:
                        self_employee = Employee.objects.get(id=person.id)
                        self.fields['employee'].queryset = Employee.objects.filter(
                            id=self_employee.id,
                            is_active=True
                        )
                    except Employee.DoesNotExist:
                        self.fields['employee'].queryset = Employee.objects.none()
            else:
                # No person record - no access
                self.fields['employee'].queryset = Employee.objects.none()
        else:
            # No user - no access
            self.fields['employee'].queryset = Employee.objects.none()
        
        closed_periods = PayrollPeriod.objects.filter(is_closed=True).order_by('-year', '-month')

        month_choices = []
        seen_months = set()
        for period in closed_periods:
            if period.month not in seen_months:
                label = f"{period.month:02d} - {calendar.month_name[period.month]}"
                month_choices.append((str(period.month), label))
                seen_months.add(period.month)
        month_choices.sort(key=lambda item: int(item[0]))

        year_choices = []
        seen_years = set()
        for period in closed_periods:
            if period.year not in seen_years:
                year_choices.append((str(period.year), str(period.year)))
                seen_years.add(period.year)
        year_choices.sort(key=lambda item: int(item[0]), reverse=True)

        if not month_choices:
            month_choices = [('', 'Tidak ada periode yang ditutup')]
        if not year_choices:
            year_choices = [('', 'Tidak ada periode yang ditutup')]

        self.fields['month'].choices = month_choices
        self.fields['year'].choices = year_choices

    def clean(self):
        cleaned_data = super().clean()
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')

        if month and year:
            try:
                month_int = int(month)
                year_int = int(year)
            except (TypeError, ValueError):
                raise forms.ValidationError('Pilih bulan dan tahun yang valid.')

            exists = PayrollPeriod.objects.filter(
                month=month_int,
                year=year_int,
                is_closed=True
            ).exists()
            if not exists:
                raise forms.ValidationError('Periode tersebut belum ditutup. Silakan pilih periode yang sudah ditutup.')

        return cleaned_data


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'clock_in', 'clock_out', 'status', 'borongan', 'realisasi', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'clock_in': forms.TimeInput(attrs={'type': 'time'}),
            'clock_out': forms.TimeInput(attrs={'type': 'time'}),
            'borongan': forms.Select(attrs={'class': 'form-control'}),
            'realisasi': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        print(f"\n=== ATTENDANCE FORM DEBUG ===")
        print(f"User: {user}")
        
        if user:
            person = getattr(user, 'person', None)
            is_owner_attr = getattr(user, 'is_owner', False)
            # is_owner might be a method, so call it if callable
            is_owner = is_owner_attr() if callable(is_owner_attr) else is_owner_attr
            
            print(f"Person: {person}")
            print(f"Is Owner: {is_owner}")
            print(f"Is Owner Callable: {callable(is_owner_attr)}")
            
            if is_owner:
                print("Branch: OWNER")
                # Owner sees all active employees in their company
                self.fields['employee'].queryset = Employee.objects.filter(
                    company=user.company, 
                    is_active=True
                ).order_by('name')
            elif person:
                print("Branch: HAS PERSON")
                # Check if person is an employee
                has_employee = hasattr(person, 'employee')
                print(f"Has employee attribute: {has_employee}")
                
                if has_employee:
                    print("Sub-branch: PERSON IS EMPLOYEE")
                    # Regular employee or Supervisor (with Employee record)
                    employee = person.employee
                    
                    # Get all subordinates recursively
                    def get_descendants(emp):
                        descendants = set()
                        direct_subs = emp.subordinates.all()
                        for sub in direct_subs:
                            descendants.add(sub.id)
                            descendants.update(get_descendants(sub))
                        return descendants
                    
                    subordinate_ids = get_descendants(employee)
                    # Include self
                    allowed_ids = subordinate_ids | {employee.id}
                    
                    print(f"Allowed employee IDs: {allowed_ids}")
                    
                    self.fields['employee'].queryset = Employee.objects.filter(
                        id__in=allowed_ids,
                        is_active=True
                    ).order_by('name')
                else:
                    print("Sub-branch: PERSON WITHOUT EMPLOYEE RECORD")
                    # Person without Employee record (e.g., supervisor that's just a Person)
                    # Get their person subordinates
                    allowed_ids = set()
                    
                    # Include themselves if they exist as an Employee
                    try:
                        self_employee = Employee.objects.get(id=person.id)
                        allowed_ids.add(self_employee.id)
                        print(f"Found self as employee: {self_employee.id}")
                    except Employee.DoesNotExist:
                        print("Self not found as employee")
                    
                    # Get all person subordinates and check if they're employees
                    person_subordinates = person.subordinates.all()
                    print(f"Person subordinates: {list(person_subordinates)}")
                    
                    for subordinate in person_subordinates:
                        print(f"  Checking subordinate: {subordinate}")
                        # Check if this person is also an employee
                        if hasattr(subordinate, 'employee'):
                            allowed_ids.add(subordinate.employee.id)
                            print(f"    Found as employee via attribute: {subordinate.employee.id}")
                        else:
                            # Person subordinate might have the same ID as Employee
                            try:
                                emp = Employee.objects.get(id=subordinate.id)
                                allowed_ids.add(emp.id)
                                print(f"    Found as employee by ID: {emp.id}")
                            except Employee.DoesNotExist:
                                print(f"    Not found as employee")
                    
                    print(f"Final allowed employee IDs: {allowed_ids}")
                    
                    if allowed_ids:
                        self.fields['employee'].queryset = Employee.objects.filter(
                            id__in=allowed_ids,
                            is_active=True
                        ).order_by('name')
                        print(f"Queryset count: {self.fields['employee'].queryset.count()}")
                    else:
                        self.fields['employee'].queryset = Employee.objects.none()
                        print("No allowed IDs - empty queryset")
            else:
                print("Branch: NO PERSON - FALLBACK")
                # Fallback for users without person record
                self.fields['employee'].queryset = Employee.objects.none()
        else:
            print("No user provided to form")
            
        print(f"Final employee queryset: {list(self.fields['employee'].queryset.values_list('id', 'name'))}")
        print(f"===========================\n")




class WorkRequestForm(forms.ModelForm):
    class Meta:
        model = WorkRequest
        fields = ['employee', 'start_date', 'end_date', 'due_date', 'title', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        employee_field = self.fields.get('employee')

        if employee_field:
            employee_field.label = 'Karyawan'

        if user:
            person = getattr(user, 'person', None)
            is_owner = getattr(user, 'is_owner', False)

            if person and not is_owner:
                employee_field.queryset = Employee.objects.filter(pk=person.pk)
                employee_field.initial = person
                employee_field.widget = forms.HiddenInput()
            else:
                employee_field.queryset = Employee.objects.filter(is_active=True).order_by('name')
        elif employee_field:
            employee_field.queryset = Employee.objects.filter(is_active=True).order_by('name')

        for field in ['start_date', 'end_date', 'due_date', 'title']:
            if field in self.fields:
                self.fields[field].required = True

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        due_date = cleaned_data.get('due_date')

        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', 'Tanggal akhir tidak boleh sebelum tanggal mulai.')

        if start_date and due_date and due_date < start_date:
            self.add_error('due_date', 'Due date tidak boleh sebelum tanggal mulai kerja.')

        if employee and start_date and end_date:
            # Check for overlapping work requests
            qs = WorkRequest.objects.filter(
                employee=employee,
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('start_date', 'Ada work request yang tumpang tindih dengan tanggal yang dipilih.')

        if self.instance.pk and not self.instance.is_editable:
            raise forms.ValidationError('Work request sudah melewati tanggal akhir dan tidak dapat diedit.')

        return cleaned_data


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'leave_type', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }
