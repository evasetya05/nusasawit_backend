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

