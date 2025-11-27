from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from apps.core.models import Employee, Borongan
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


def absensi_harian(request):
    """Absensi harian: form clock in/out, list attendance."""
    # Temukan periode penggajian yang aktif untuk membatasi input tanggal
    open_periods = PayrollPeriod.objects.filter(is_closed=False)
    min_date, max_date = None, None

    if open_periods:
        # Tentukan rentang tanggal valid dari semua periode yang terbuka
        min_date = min(p.start_date for p in open_periods)
        max_date = max(p.end_date for p in open_periods)
    else:
        messages.warning(request, 'Tidak ada periode penggajian yang aktif. Silakan buka periode baru untuk mencatat absensi.')

    form = AttendanceForm(request.POST or None)

    # Terapkan batasan tanggal ke widget form
    if min_date and max_date:
        form.fields['date'].widget.attrs['min'] = min_date.strftime('%Y-%m-%d')
        form.fields['date'].widget.attrs['max'] = max_date.strftime('%Y-%m-%d')
    else:
        # Jika tidak ada periode aktif, nonaktifkan form
        for field in form.fields.values():
            field.widget.attrs['disabled'] = True

    if request.method == 'POST' and open_periods: # Hanya proses jika ada periode aktif
        if form.is_valid():
            attendance = form.save()
            messages.success(request, f'Absensi untuk {attendance.employee} pada {attendance.date} berhasil disimpan.')
            return redirect('compensation6:absensi_harian')
        else:
            messages.error(request, 'Gagal menyimpan. Periksa kembali input Anda.')

    # Get current user's employee if applicable
    person = getattr(request.user, 'person', None)
    if person:
        attendances = Attendance.objects.filter(employee=person).order_by('-date')
    else:
        attendances = Attendance.objects.all().order_by('-date')[:50]  # Limit for admin

    # Ambil semua opsi borongan untuk dropdown
    borongan_options = Borongan.objects.all().select_related('employee')

    return render(request, 'compensation6/absensi_harian.html', {
        'form': form,
        'attendances': attendances,
        'borongan_options': borongan_options,
    })
