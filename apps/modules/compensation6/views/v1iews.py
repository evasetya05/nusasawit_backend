from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from apps.core.models import Employee
from .models import Payroll, PayrollPeriod, Allowance, Deduction, BPJSConfig, Attendance, LeaveRequest
from .forms import (
    AllowanceForm, DeductionForm, PayrollPeriodForm,
    BPJSTKForm, BPJSTKJPForm, BPJSKesehatanForm, PajakForm,
    BPJSTKJKKCompanyForm, BPJSTKJKMCompanyForm, BPJSTKJHTCompanyForm, BPJSTKJPCompanyForm, BPJSKesehatanCompanyForm,
    BPJSConfigKaryawanForm, BPJSConfigPerusahaanForm,
    PayslipSelectionForm,
    AttendanceForm, LeaveRequestForm
)
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string


def compensation_dashboard(request):
    return render(request, 'compensation6/compensation_dashboard.html')

# Tambah Allowance
def add_allowance(request):
    form = AllowanceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Allowance berhasil ditambahkan.')
        return redirect('compensation6:add_allowance')
    return render(request, 'compensation6/add_allowance.html', {'form': form})


# 💸 Tambah Deduction
def add_deduction(request):
    form = DeductionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Deduction berhasil ditambahkan.')
        return redirect('compensation6:add_deduction')
    return render(request, 'compensation6/add_deduction.html', {'form': form})


def payroll_period_list(request):
    periods = PayrollPeriod.objects.all().order_by('-year', '-month')
    form = PayrollPeriodForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Periode payroll berhasil dibuat.')
            return redirect('compensation6:payroll_period_list')

    return render(request, 'compensation6/payroll_period_list.html', {
        'periods': periods,
        'form': form,
    })


def generate_payroll(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)
    employees = Employee.objects.all()
    cfg = BPJSConfig.objects.first()

    for emp in employees:
        payroll, created = Payroll.objects.get_or_create(employee=emp, period=period)

        # Set basic salary from employee
        payroll.basic_salary = getattr(emp, 'basic_salary', 0)

        # Create default allowance from employee's default_allowance if it exists
        default_allowance = getattr(emp, 'default_allowance', 0)
        if default_allowance and default_allowance > 0:
            # Check if default allowance already exists for this period
            if not Allowance.objects.filter(
                employee=emp,
                period=period,
                name='Tunjangan Tetap'
            ).exists():
                Allowance.objects.create(
                    employee=emp,
                    period=period,
                    name='Tunjangan Tetap',
                    amount=default_allowance
                )

        # Calculate daily salary
        daily_salary = Decimal(payroll.basic_salary or 0) / Decimal(cfg.working_days_per_month if cfg else 30)
        hourly_rate = daily_salary / 8  # Assume 8 hours per day

        # Attendance calculations
        attendances = Attendance.objects.filter(employee=emp, date__year=period.year, date__month=period.month)
        total_alfa_days = sum(1 for a in attendances if a.status in ['absent'])
        half_day_alfa = sum(0.5 for a in attendances if a.status == 'half_day')
        total_alfa_days += half_day_alfa

        # Deduction for alfa
        if total_alfa_days > 0:
            deduction_amount = total_alfa_days * daily_salary
            Deduction.objects.update_or_create(
                employee=emp, period=period, name='Potongan Alfa',
                defaults={'amount': deduction_amount.quantize(Decimal('1.'), rounding='ROUND_HALF_UP')}
            )

        # Overtime allowance
        total_overtime_hours = Decimal('0')
        for att in attendances:
            if att.clock_in and att.clock_out:
                # Calculate hours from time objects
                in_minutes = att.clock_in.hour * 60 + att.clock_in.minute
                out_minutes = att.clock_out.hour * 60 + att.clock_out.minute
                if out_minutes > in_minutes:
                    worked_hours = (out_minutes - in_minutes) / 60
                    if worked_hours > 8:
                        total_overtime_hours += Decimal(worked_hours - 8)
        if total_overtime_hours > 0:
            overtime_amount = total_overtime_hours * hourly_rate * (cfg.overtime_rate if cfg else Decimal('1.5'))
            Allowance.objects.update_or_create(
                employee=emp, period=period, name='Lembur',
                defaults={'amount': overtime_amount.quantize(Decimal('1.'), rounding='ROUND_HALF_UP')}
            )

        # Leave deductions (unpaid leave)
        from datetime import date
        period_start = date(period.year, period.month, 1)
        period_end = date(period.year, period.month + 1, 1) if period.month < 12 else date(period.year + 1, 1, 1)
        period_end = period_end.replace(day=1) - timedelta(days=1)  # Last day of month
        leaves = LeaveRequest.objects.filter(
            employee=emp,
            start_date__lte=period_end, end_date__gte=period_start,
            status='approved_hr'
        ).exclude(leave_type='annual')
        total_leave_days = Decimal('0')
        for leave in leaves:
            # Calculate overlapping days
            start = max(leave.start_date, period_start)
            end = min(leave.end_date, period_end)
            days = (end - start).days + 1 if end >= start else 0
            total_leave_days += Decimal(days)
        if total_leave_days > 0:
            leave_deduction = total_leave_days * daily_salary
            Deduction.objects.update_or_create(
                employee=emp, period=period, name='Potongan Cuti Tanpa Bayar',
                defaults={'amount': leave_deduction.quantize(Decimal('1.'), rounding='ROUND_HALF_UP')}
            )

        # Generate BPJS Karyawan deductions based on config percentages
        if cfg and payroll.basic_salary and Decimal(payroll.basic_salary) > 0:
            base = Decimal(payroll.basic_salary)
            # JKK Karyawan
            if hasattr(cfg, 'emp_jkk_pct') and cfg.emp_jkk_pct and cfg.emp_jkk_pct > 0:
                amount = (base * Decimal(cfg.emp_jkk_pct) / Decimal('100')).quantize(Decimal('1.'), rounding='ROUND_HALF_UP')
                Deduction.objects.update_or_create(
                    employee=emp, period=period, name='BPJS TK - JKK Karyawan',
                    defaults={'amount': amount}
                )
            # JKM Karyawan
            if hasattr(cfg, 'emp_jkm_pct') and cfg.emp_jkm_pct and cfg.emp_jkm_pct > 0:
                amount = (base * Decimal(cfg.emp_jkm_pct) / Decimal('100')).quantize(Decimal('1.'), rounding='ROUND_HALF_UP')
                Deduction.objects.update_or_create(
                    employee=emp, period=period, name='BPJS TK - JKM Karyawan',
                    defaults={'amount': amount}
                )
            # JHT Karyawan
            if cfg.emp_jht_pct and cfg.emp_jht_pct > 0:
                amount = (base * Decimal(cfg.emp_jht_pct) / Decimal('100')).quantize(Decimal('1.'), rounding='ROUND_HALF_UP')
                Deduction.objects.update_or_create(
                    employee=emp, period=period, name='BPJS TK - JHT Karyawan',
                    defaults={'amount': amount}
                )
            # JP Karyawan
            if cfg.emp_jp_pct and cfg.emp_jp_pct > 0:
                amount = (base * Decimal(cfg.emp_jp_pct) / Decimal('100')).quantize(Decimal('1.'), rounding='ROUND_HALF_UP')
                Deduction.objects.update_or_create(
                    employee=emp, period=period, name='BPJS TK - JP Karyawan',
                    defaults={'amount': amount}
                )
            # JKN/BPJS Kesehatan Karyawan
            if cfg.emp_jkn_pct and cfg.emp_jkn_pct > 0:
                amount = (base * Decimal(cfg.emp_jkn_pct) / Decimal('100')).quantize(Decimal('1.'), rounding='ROUND_HALF_UP')
                Deduction.objects.update_or_create(
                    employee=emp, period=period, name='BPJS Kesehatan Karyawan',
                    defaults={'amount': amount}
                )

        payroll.calculate_totals()

        # Set employer contributions based on BPJSConfig
        if cfg and payroll.basic_salary and Decimal(payroll.basic_salary) > 0:
            base = Decimal(payroll.basic_salary)
            payroll.tk_jkk_company = (base * Decimal(cfg.com_jkk_pct or 0) / Decimal('100')).quantize(Decimal('1.'), rounding='ROUND_HALF_UP')
            payroll.tk_jkm_company = (base * Decimal(cfg.com_jkm_pct or 0) / Decimal('100')).quantize(Decimal('1.'), rounding='ROUND_HALF_UP')
            payroll.tk_jht_company = (base * Decimal(cfg.com_jht_pct or 0) / Decimal('100')).quantize(Decimal('1.'), rounding='ROUND_HALF_UP')
            payroll.tk_jp_company = (base * Decimal(cfg.com_jp_pct or 0) / Decimal('100')).quantize(Decimal('1.'), rounding='ROUND_HALF_UP')
            payroll.jkn_company = (base * Decimal(cfg.com_jkn_pct or 0) / Decimal('100')).quantize(Decimal('1.'), rounding='ROUND_HALF_UP')
            payroll.save()

        payroll.save()

    messages.success(request, f"Payroll untuk periode {period} berhasil digenerate.")
    return redirect('compensation6:payroll_list')


def payroll_list(request):
    payrolls = Payroll.objects.all().order_by('-period__year', '-period__month')
    return render(request, 'compensation6/payroll_list.html', {'payrolls': payrolls})


def payroll_detail(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    allowances = Allowance.objects.filter(employee=payroll.employee, period=payroll.period)
    deductions = Deduction.objects.filter(employee=payroll.employee, period=payroll.period)
    cfg = BPJSConfig.objects.first()
    # employer contributions from model
    tk_jkk_company = payroll.tk_jkk_company
    tk_jkm_company = payroll.tk_jkm_company
    tk_jht_company = payroll.tk_jht_company
    tk_jp_company = payroll.tk_jp_company
    jkn_company = payroll.jkn_company
    total_employer_contrib = tk_jkk_company + tk_jkm_company + tk_jht_company + tk_jp_company + jkn_company

    # Attendance summary
    attendances = Attendance.objects.filter(employee=payroll.employee, date__year=payroll.period.year, date__month=payroll.period.month)
    present_days = attendances.filter(status='present').count()
    late_days = attendances.filter(status='late').count()
    absent_days = attendances.filter(status='absent').count()
    half_days = attendances.filter(status='half_day').count()
    total_overtime_hours = Decimal('0')
    for att in attendances:
        if att.clock_in and att.clock_out:
            in_minutes = att.clock_in.hour * 60 + att.clock_in.minute
            out_minutes = att.clock_out.hour * 60 + att.clock_out.minute
            if out_minutes > in_minutes:
                worked_hours = (out_minutes - in_minutes) / 60
                if worked_hours > 8:
                    total_overtime_hours += Decimal(worked_hours - 8)

    # Leave summary
    leaves = LeaveRequest.objects.filter(employee=payroll.employee, status='approved_hr')
    annual_leave_taken = leaves.filter(leave_type='annual').count()  # Approximate
    sick_leave_taken = leaves.filter(leave_type='sick').count()

    return render(request, 'compensation6/payroll_detail.html', {
        'payroll': payroll,
        'allowances': allowances,
        'deductions': deductions,
        'tk_jkk_company': tk_jkk_company,
        'tk_jkm_company': tk_jkm_company,
        'tk_jht_company': tk_jht_company,
        'tk_jp_company': tk_jp_company,
        'jkn_company': jkn_company,
        'total_employer_contrib': total_employer_contrib,
        'present_days': present_days,
        'late_days': late_days,
        'absent_days': absent_days,
        'half_days': half_days,
        'total_overtime_hours': total_overtime_hours,
        'annual_leave_taken': annual_leave_taken,
        'sick_leave_taken': sick_leave_taken,
    })


def close_period(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)
    period.is_closed = True
    period.save()
    messages.info(request, f"Periode {period} telah ditutup.")
    return redirect('compensation6:payroll_period_list')


def komponen_gaji_view(request):
    return render(request, "compensation6/komponen_gaji.html")


def add_bpjs_tk_jht(request):
    form = BPJSTKForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS TK - JHT Karyawan'
        deduction.save()
        messages.success(request, 'BPJS TK - JHT Karyawan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_tk_jht.html', {'form': form})


def add_bpjs_tk_jp(request):
    form = BPJSTKJPForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS TK - JP Karyawan'
        deduction.save()
        messages.success(request, 'BPJS TK - JP Karyawan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_tk_jp.html', {'form': form})


def add_bpjs_kesehatan(request):
    form = BPJSKesehatanForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS Kesehatan Karyawan'
        deduction.save()
        messages.success(request, 'BPJS Kesehatan Karyawan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_kesehatan.html', {'form': form})


def add_pajak(request):
    form = PajakForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'Pajak Penghasilan'
        deduction.save()
        messages.success(request, 'Pajak Penghasilan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_pajak.html', {'form': form})


def add_bpjs_tk_jkk_company(request):
    form = BPJSTKJKKCompanyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS TK - JKK Perusahaan'
        deduction.save()
        messages.success(request, 'BPJS TK - JKK Perusahaan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_tk_jkk_company.html', {'form': form})


def add_bpjs_tk_jkm_company(request):
    form = BPJSTKJKMCompanyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS TK - JKM Perusahaan'
        deduction.save()
        messages.success(request, 'BPJS TK - JKM Perusahaan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_tk_jkm_company.html', {'form': form})


def add_bpjs_tk_jht_company(request):
    form = BPJSTKJHTCompanyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS TK - JHT Perusahaan'
        deduction.save()
        messages.success(request, 'BPJS TK - JHT Perusahaan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_tk_jht_company.html', {'form': form})


def add_bpjs_tk_jp_company(request):
    form = BPJSTKJPCompanyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS TK - JP Perusahaan'
        deduction.save()
        messages.success(request, 'BPJS TK - JP Perusahaan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_tk_jp_company.html', {'form': form})


def add_bpjs_kesehatan_company(request):
    form = BPJSKesehatanCompanyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS Kesehatan Perusahaan'
        deduction.save()
        messages.success(request, 'BPJS Kesehatan Perusahaan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_kesehatan_company.html', {'form': form})


def bpjs_karyawan(request):
    cfg, _ = BPJSConfig.objects.get_or_create(id=1)
    form = BPJSConfigKaryawanForm(request.POST or None, instance=cfg)
    if request.method == 'POST':
        # Hanya owner yang boleh update
        if not getattr(request.user, 'is_owner', False):
            messages.error(request, 'Hanya owner yang dapat mengubah persentase BPJS karyawan.')
            return redirect('compensation6:bpjs_karyawan')
        if form.is_valid():
            form.save()
            messages.success(request, 'Persentase BPJS karyawan berhasil disimpan.')
            return redirect('compensation6:bpjs_karyawan')
    return render(request, "compensation6/bpjs_karyawan.html", {'form': form, 'cfg': cfg})


def bpjs_perusahaan(request):
    cfg, _ = BPJSConfig.objects.get_or_create(id=1)
    form = BPJSConfigPerusahaanForm(request.POST or None, instance=cfg)
    if request.method == 'POST':
        # Hanya owner yang boleh update
        if not getattr(request.user, 'is_owner', False):
            messages.error(request, 'Hanya owner yang dapat mengubah persentase BPJS perusahaan.')
            return redirect('compensation6:bpjs_perusahaan')
        if form.is_valid():
            form.save()
            messages.success(request, 'Persentase BPJS perusahaan berhasil disimpan.')
            return redirect('compensation6:bpjs_perusahaan')
    return render(request, "compensation6/bpjs_perusahaan.html", {'form': form, 'cfg': cfg})


# Payslip: select and preview
def payslip_select(request):
    if request.user.is_owner():
        form = PayslipSelectionForm(request.POST or None)
    else:
        # For non-owners, limit to their own employee
        person = getattr(request.user, 'person', None)
        if person:
            form = PayslipSelectionForm(request.POST or None)
            form.fields['employee'].queryset = Employee.objects.filter(id=person.id)
        else:
            # No person, can't access
            messages.error(request, 'Profil karyawan tidak ditemukan.')
            return redirect('compensation6:compensation_dashboard')
    
    if request.method == 'POST' and form.is_valid():
        emp_id = form.cleaned_data['employee'].id
        month = form.cleaned_data['month']
        year = form.cleaned_data['year']
        return redirect('compensation6:payslip_preview', employee_id=emp_id, month=month, year=year)
    return render(request, 'compensation6/payslip_form.html', {'form': form})


def _get_payroll_bundle(employee_id, month, year):
    period = get_object_or_404(PayrollPeriod, month=month, year=year)
    employee = get_object_or_404(Employee, id=employee_id)
    payroll = get_object_or_404(Payroll, employee=employee, period=period)
    allowances = Allowance.objects.filter(employee=employee, period=period)
    deductions = Deduction.objects.filter(employee=employee, period=period)
    cfg = BPJSConfig.objects.first()
    # employer contributions
    base = Decimal(payroll.basic_salary or 0)
    tk_jkk_company = tk_jkm_company = tk_jht_company = tk_jp_company = jkn_company = Decimal('0.00')
    if cfg and base > 0:
        tk_jkk_company = (base * Decimal(cfg.com_jkk_pct or 0) / Decimal('100'))
        tk_jkm_company = (base * Decimal(cfg.com_jkm_pct or 0) / Decimal('100'))
        tk_jht_company = (base * Decimal(cfg.com_jht_pct or 0) / Decimal('100'))
        tk_jp_company = (base * Decimal(cfg.com_jp_pct or 0) / Decimal('100'))
        jkn_company = (base * Decimal(cfg.com_jkn_pct or 0) / Decimal('100'))
    total_employer_contrib = tk_jkk_company + tk_jkm_company + tk_jht_company + tk_jp_company + jkn_company
    ctx = {
        'payroll': payroll,
        'allowances': allowances,
        'deductions': deductions,
        'period': period,
        'employee': employee,
        'tk_jkk_company': tk_jkk_company,
        'tk_jkm_company': tk_jkm_company,
        'tk_jht_company': tk_jht_company,
        'tk_jp_company': tk_jp_company,
        'jkn_company': jkn_company,
        'total_employer_contrib': total_employer_contrib,
    }
    return ctx


def payslip_preview(request, employee_id, month, year):
    try:
        ctx = _get_payroll_bundle(employee_id, month, year)
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    return render(request, 'compensation6/payslip_pdf.html', {**ctx, 'preview': True})


def payslip_pdf(request, employee_id, month, year):
    try:
        ctx = _get_payroll_bundle(employee_id, month, year)
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    html = render_to_string('compensation6/payslip_pdf.html', {**ctx, 'preview': False})
    try:
        from weasyprint import HTML
        pdf = HTML(string=html).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"slip_gaji_{ctx['employee'].id}_{int(month):02d}-{year}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception:
        # Fallback: provide HTML with a note
        messages.warning(request, 'WeasyPrint tidak tersedia. Tampilkan versi HTML. Install weasyprint untuk PDF.')
        return HttpResponse(html)


def absensi_harian(request):
    """Absensi harian: form clock in/out, list attendance."""
    form = AttendanceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        attendance = form.save()
        messages.success(request, f'Absensi untuk {attendance.employee} pada {attendance.date} berhasil disimpan.')
        return redirect('compensation6:absensi_harian')

    # Get current user's employee if applicable
    person = getattr(request.user, 'person', None)
    if person:
        attendances = Attendance.objects.filter(employee=person).order_by('-date')
    else:
        attendances = Attendance.objects.all().order_by('-date')[:50]  # Limit for admin

    return render(request, 'compensation6/absensi_harian.html', {
        'form': form,
        'attendances': attendances,
    })


def pengajuan_cuti(request):
    """Pengajuan cuti hirarki: submit form, list requests."""
    person = getattr(request.user, 'person', None)
    is_owner = request.user.is_owner()

    # Allow owners to view even without person profile
    if not person and not is_owner:
        messages.error(request, 'Hanya karyawan yang dapat mengajukan cuti.')
        return redirect('compensation6:komponen_gaji')

    # Only allow submission if has person
    if request.method == 'POST' and person:
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = person
            leave.save()
            messages.success(request, 'Pengajuan cuti berhasil dikirim. Menunggu approval.')
            return redirect('compensation6:pengajuan_cuti')
    else:
        form = LeaveRequestForm() if person else None

    # Show leave requests: all for owners, own for others (if have person)
    if is_owner:
        # Group leaves by employee
        all_leaves = LeaveRequest.objects.select_related('employee').all().order_by('employee__name', '-created_at')
        leaves_by_employee = {}
        for leave in all_leaves:
            emp_name = leave.employee.name if leave.employee else 'Unknown'
            if emp_name not in leaves_by_employee:
                leaves_by_employee[emp_name] = []
            leaves_by_employee[emp_name].append(leave)
        leaves = leaves_by_employee  # dict of lists
    elif person:
        leaves = list(LeaveRequest.objects.filter(employee=person).order_by('-created_at'))
    else:
        leaves = []

    return render(request, 'compensation6/pengajuan_cuti.html', {
        'form': form,
        'leaves': leaves,
        'is_owner': is_owner,
        'can_submit': person is not None,
    })
def leave_approvals(request):
    """List pending leave requests for approval."""
    person = getattr(request.user, 'person', None)
    if not person:
        messages.error(request, 'Akses ditolak.')
        return redirect('compensation6:komponen_gaji')

    if getattr(request.user, 'is_owner', False):
        # Owner sees leaves approved by supervisor
        leaves = LeaveRequest.objects.filter(status='approved_supervisor')
        role = 'owner'
    elif person.subordinates.exists():  # Check if has subordinates
        # Supervisor sees pending leaves from their team
        leaves = LeaveRequest.objects.filter(employee__manager=person, status='pending')
        role = 'supervisor'
    else:
        messages.error(request, 'Akses ditolak.')
        return redirect('compensation6:komponen_gaji')

    return render(request, 'compensation6/leave_approvals.html', {
        'leaves': leaves,
        'role': role,
    })


def approve_leave(request, leave_id, action):
    """Approve or reject leave request."""
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    person = getattr(request.user, 'person', None)
    if not person:
        messages.error(request, 'Akses ditolak.')
        return redirect('compensation6:leave_approvals')

    if action not in ['approve', 'reject']:
        messages.error(request, 'Aksi tidak valid.')
        return redirect('compensation6:leave_approvals')

    if getattr(request.user, 'is_owner', False) and leave.status == 'approved_supervisor':
        # Owner final approval
        if action == 'approve':
            leave.status = 'approved_hr'
            leave.approved_by_hr = request.user
            leave.approval_date = timezone.now()
            messages.success(request, 'Cuti disetujui oleh owner.')
        else:
            leave.status = 'rejected'
            messages.success(request, 'Cuti ditolak oleh owner.')
    elif person.subordinates.exists() and leave.employee.manager == person and leave.status == 'pending':
        # Supervisor approval
        if action == 'approve':
            leave.status = 'approved_supervisor'
            leave.approved_by_supervisor = request.user
            messages.success(request, 'Cuti disetujui oleh supervisor.')
        else:
            leave.status = 'rejected'
            messages.success(request, 'Cuti ditolak oleh supervisor.')
    else:
        messages.error(request, 'Akses ditolak.')
        return redirect('compensation6:leave_approvals')

    leave.save()
    return redirect('compensation6:leave_approvals')
