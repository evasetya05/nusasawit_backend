from django import forms
import calendar
from .models import PayrollPeriod, Allowance, Deduction, BPJSConfig, Attendance, LeaveRequest
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        fields = ['employee', 'date', 'clock_in', 'clock_out', 'status', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'clock_in': forms.TimeInput(attrs={'type': 'time'}),
            'clock_out': forms.TimeInput(attrs={'type': 'time'}),
        }


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'leave_type', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }
