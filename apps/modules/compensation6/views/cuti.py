from collections import defaultdict
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



def pengajuan_cuti(request):
    """Pengajuan cuti hirarki: submit form, list requests."""
    person = getattr(request.user, 'person', None)
    is_owner = request.user.is_owner

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

    team_leaves = {}

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
        if person.subordinates.exists():
            team_requests = (
                LeaveRequest.objects.filter(employee__manager=person)
                .select_related('employee')
                .order_by('employee__name', '-created_at')
            )
            grouped = defaultdict(list)
            for leave in team_requests:
                emp_name = leave.employee.name if leave.employee else 'Unknown'
                grouped[emp_name].append(leave)
            # Convert to regular dict to avoid exposing defaultdict to template
            team_leaves = dict(grouped)
    else:
        leaves = []

    return render(request, 'compensation6/pengajuan_cuti.html', {
        'form': form,
        'leaves': leaves,
        'is_owner': is_owner,
        'can_submit': person is not None,
        'team_leaves': team_leaves,
    })
def leave_approvals(request):
    """List pending leave requests for approval."""
    person = getattr(request.user, 'person', None)
    if not person and not request.user.is_owner:
        messages.error(request, 'Akses ditolak.')
        return redirect('compensation6:komponen_gaji')

    if request.user.is_owner:
        # Owner sees leaves approved by supervisor
        leaves = LeaveRequest.objects.filter(status='approved_supervisor')
        role = 'owner'
    elif person and person.subordinates.exists():  # Check if has subordinates
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
    if request.method != 'POST':
        messages.error(request, 'Gunakan tombol aksi untuk memproses cuti.')
        return redirect('compensation6:leave_approvals')

    person = getattr(request.user, 'person', None)
    if not person and not request.user.is_owner:
        messages.error(request, 'Akses ditolak.')
        return redirect('compensation6:leave_approvals')

    if action not in ['approve', 'reject']:
        messages.error(request, 'Aksi tidak valid.')
        return redirect('compensation6:leave_approvals')

    if request.user.is_owner and leave.status == 'approved_supervisor':
        # Owner final approval
        if action == 'approve':
            leave.status = 'approved_hr'
            leave.approved_by_hr = request.user
            leave.approval_date = timezone.now()
            messages.success(request, 'Cuti disetujui oleh owner.')
        else:
            leave.status = 'rejected'
            messages.success(request, 'Cuti ditolak oleh owner.')
    elif person and person.subordinates.exists() and leave.employee.manager == person and leave.status == 'pending':
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
