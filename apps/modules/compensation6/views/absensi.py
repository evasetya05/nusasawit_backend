from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from apps.core.models import Employee, Borongan
from ..models import Payroll, PayrollPeriod, Allowance, Deduction, BPJSConfig, Attendance, LeaveRequest, WorkRequest
from ..forms import (
    AllowanceForm, DeductionForm, PayrollPeriodForm,
    BPJSTKForm, BPJSTKJPForm, BPJSKesehatanForm, PajakForm,
    BPJSTKJKKCompanyForm, BPJSTKJKMCompanyForm, BPJSTKJHTCompanyForm, BPJSTKJPCompanyForm, BPJSKesehatanCompanyForm,
    BPJSConfigKaryawanForm, BPJSConfigPerusahaanForm,
    PayslipSelectionForm,
    AttendanceForm, LeaveRequestForm, WorkRequestForm
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


from django.views.generic import TemplateView


class WorkCalendarView(TemplateView):
    template_name = 'compensation6/work_calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        initial = {}
        employee_param = self.request.GET.get('employee')
        start_date_param = self.request.GET.get('start_date')
        end_date_param = self.request.GET.get('end_date')
        due_date_param = self.request.GET.get('due_date')

        if employee_param:
            initial['employee'] = employee_param
        if start_date_param:
            initial['start_date'] = start_date_param
            if not end_date_param:
                initial['end_date'] = start_date_param
        if end_date_param:
            initial['end_date'] = end_date_param
        if due_date_param:
            initial['due_date'] = due_date_param

        form = kwargs.get('form') or WorkRequestForm(user=self.request.user, initial=initial)
        context['form'] = form

        # Ambil periode aktif pertama untuk ditampilkan
        active_period = PayrollPeriod.objects.filter(is_closed=False).order_by('start_date').first()
        context['active_period'] = active_period

        if not active_period:
            messages.info(self.request, "Tidak ada periode penggajian yang aktif.")
            context['date_range'] = []
            context['calendar_data'] = []
            context['work_requests'] = []
            return context

        date_range = [
            active_period.start_date + timedelta(days=offset)
            for offset in range((active_period.end_date - active_period.start_date).days + 1)
        ]

        employees = Employee.objects.filter(is_active=True).order_by('name')
        work_requests = (
            WorkRequest.objects.filter(
                employee__in=employees,
                start_date__lte=active_period.end_date,
                end_date__gte=active_period.start_date
            )
            .select_related('employee', 'flutter_user')
            .order_by('employee__name', 'start_date')
        )

        request_map = {}
        for wr in work_requests:
            for date in date_range:
                if wr.covers_date(date):
                    request_map[(wr.employee_id, date)] = wr

        calendar_data = []
        for employee in employees:
            days = {}
            for current_date in date_range:
                work_request = request_map.get((employee.id, current_date))
                days[current_date] = work_request
            calendar_data.append({
                'employee': employee,
                'days': days,
            })

        context['date_range'] = date_range
        context['calendar_data'] = calendar_data
        context['work_requests'] = work_requests

        edit_instance = kwargs.get('edit_instance')
        edit_form = kwargs.get('edit_form')

        if not edit_instance:
            edit_id = self.request.GET.get('edit')
            if edit_id:
                try:
                    edit_instance = WorkRequest.objects.select_related('employee').get(pk=edit_id)
                except WorkRequest.DoesNotExist:
                    messages.error(self.request, 'Work request tidak ditemukan.')
                    edit_instance = None

        if edit_instance:
            context['edit_instance'] = edit_instance
            if edit_form is None:
                edit_form = WorkRequestForm(instance=edit_instance, user=self.request.user)
            context['edit_form'] = edit_form
            context['edit_allowed'] = edit_instance.is_editable

        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', 'create')

        if action == 'update':
            work_request_id = request.POST.get('work_request_id')
            work_request = get_object_or_404(WorkRequest, pk=work_request_id)

            if not work_request.is_editable:
                messages.error(request, 'Work request sudah melewati tanggal akhir dan tidak dapat diedit.')
                return redirect('compensation6:work_calendar')

            form = WorkRequestForm(request.POST, instance=work_request, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Work request berhasil diperbarui.')
                return redirect('compensation6:work_calendar')

            context = self.get_context_data(form=WorkRequestForm(user=request.user), edit_instance=work_request, edit_form=form)
            return self.render_to_response(context)

        form = WorkRequestForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Work request berhasil ditambahkan.')
            return redirect('compensation6:work_calendar')

        context = self.get_context_data(form=form)
        return self.render_to_response(context)
