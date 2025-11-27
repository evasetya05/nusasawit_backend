from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from apps.core.models import Employee
from ..models import Payroll, PayrollPeriod, Allowance, Deduction, BPJSConfig, Attendance, LeaveRequest
from ..forms import (
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

        # Create borongan allowances from attendance records (not from employee.borongan)
        attendances = Attendance.objects.filter(employee=emp, date__year=period.year, date__month=period.month)
        
        # Group borongan by borongan record to consolidate same borongan
        borongan_dict = {}
        for att in attendances:
            if att.borongan:
                borongan = att.borongan
                key = borongan.id
                if key not in borongan_dict:
                    borongan_dict[key] = {
                        'borongan': borongan,
                        'total_harga': Decimal('0'),
                        'dates': []
                    }
                borongan_dict[key]['total_harga'] += Decimal(borongan.harga_borongan)
                borongan_dict[key]['dates'].append(str(att.date))
        
        # Create allowances for each borongan
        for borongan_id, borongan_data in borongan_dict.items():
            borongan = borongan_data['borongan']
            allowance_name = f"Borongan: {borongan.pekerjaan} ({borongan.satuan})"
            if not Allowance.objects.filter(
                employee=emp,
                period=period,
                name=allowance_name
            ).exists():
                # Create allowance with dates info stored
                allowance = Allowance.objects.create(
                    employee=emp,
                    period=period,
                    name=allowance_name,
                    amount=borongan_data['total_harga'],
                    borongan_dates=borongan_data['dates']
                )

        # Calculate daily salary
        daily_salary = Decimal(payroll.basic_salary or 0) / Decimal(cfg.working_days_per_month if cfg else 30)
        hourly_rate = daily_salary / 8  # Assume 8 hours per day

        # Attendance calculations
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
    payrolls = Payroll.objects.select_related('employee', 'period').order_by('-period__year', '-period__month')
    selected_period = None

    period_id = request.GET.get('period')
    if period_id:
        selected_period = get_object_or_404(PayrollPeriod, pk=period_id)
        payrolls = payrolls.filter(period=selected_period)

    context = {
        'payrolls': payrolls,
        'selected_period': selected_period,
    }
    return render(request, 'compensation6/payroll_list.html', context)


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

