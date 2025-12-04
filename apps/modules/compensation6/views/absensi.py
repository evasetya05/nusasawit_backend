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
    
    # Debug: Print user information
    print(f"=== USER DEBUG INFO ===")
    print(f"User: {request.user}")
    print(f"User ID: {request.user.id}")
    print(f"Username: {request.user.username}")
    print(f"Email: {request.user.email}")
    print(f"Is Owner: {getattr(request.user, 'is_owner', False)()}")
    person = getattr(request.user, 'person', None)
    is_supervisor = bool(person and person.subordinates.exists())
    print(f"Is Supervisor: {is_supervisor}")
    print(f"Is Staff: {request.user.is_staff}")
    print(f"Is Superuser: {request.user.is_superuser}")
    
    # Check if user has person
    try:
        person = request.user.person
        print(f"Has Person: YES")
        print(f"Person: {person}")
        print(f"Person Name: {person.name if hasattr(person, 'name') else 'N/A'}")
        print(f"Person Company: {person.company if hasattr(person, 'company') else 'N/A'}")
    except AttributeError:
        print(f"Has Person: NO")
        person = None
    
    # Check if person is employee
    if person and hasattr(person, 'employee'):
        print(f"Is Employee: YES")
        print(f"Employee: {person.employee}")
        print(f"Employee Position: {person.employee.position if person.employee.position else 'N/A'}")
    else:
        print(f"Is Employee: NO")
    
    print(f"========================")
    
    # Temukan periode penggajian yang aktif untuk membatasi input tanggal
    open_periods = PayrollPeriod.objects.filter(is_closed=False)
    min_date, max_date = None, None

    if open_periods:
        # Tentukan rentang tanggal valid dari semua periode yang terbuka
        min_date = min(p.start_date for p in open_periods)
        max_date = max(p.end_date for p in open_periods)
    else:
        messages.warning(request, 'Tidak ada periode penggajian yang aktif. Silakan buka periode baru untuk mencatat absensi.')

    form = AttendanceForm(request.POST or None, user=request.user)

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

    # Debug information
    debug_info = {
        'user': request.user,
        'is_owner': getattr(request.user, 'is_owner', False),
        'has_person': person is not None,
        'person': person,
    }
    
    if person and hasattr(person, 'employee'):
        employee = person.employee
        debug_info['is_employee'] = True
        debug_info['employee'] = employee
        debug_info['manager'] = employee.manager
        debug_info['subordinates'] = list(employee.subordinates.all())
    else:
        debug_info['is_employee'] = False
        debug_info['employee'] = None
        debug_info['manager'] = None
        debug_info['subordinates'] = []
    
    if person:
        debug_info['person_subordinates'] = list(person.subordinates.all())
        debug_info['is_supervisor'] = person.subordinates.exists()
    else:
        debug_info['person_subordinates'] = []
        debug_info['is_supervisor'] = False

    # Ambil semua opsi borongan untuk dropdown
    borongan_options = Borongan.objects.all().select_related('employee')

    return render(request, 'compensation6/absensi_harian.html', {
        'form': form,
        'attendances': attendances,
        'borongan_options': borongan_options,
        'debug_info': debug_info,
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import json


@require_GET
@csrf_exempt
def get_borongan_by_employee(request):
    """API endpoint to get borongan options for a specific employee"""
    employee_id = request.GET.get('employee_id')
    
    if not employee_id:
        return JsonResponse({'borongan_options': []})
    
    try:
        employee = Employee.objects.get(id=employee_id)
        borongans = Borongan.objects.filter(employee=employee).order_by('pekerjaan')
        
        options = []
        for borongan in borongans:
            options.append({
                'id': borongan.id,
                'pekerjaan': borongan.pekerjaan,
                'satuan': borongan.satuan,
                'harga_borongan': float(borongan.harga_borongan)
            })
        
        return JsonResponse({'borongan_options': options})
    
    except Employee.DoesNotExist:
        return JsonResponse({'borongan_options': []})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def riwayat_absensi(request):
    """View for displaying attendance history."""
    
    print(f"\n=== RIWAYAT ABSENSI DEBUG ===")
    print(f"User: {request.user}")
    
    # Get filter parameters
    selected_employee_id = request.GET.get('employee')
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    
    print(f"Filters - Employee: {selected_employee_id}, Month: {selected_month}, Year: {selected_year}")
    
    # Get current user's person
    person = getattr(request.user, 'person', None)
    is_owner = getattr(request.user, 'is_owner', False)
    is_owner = is_owner() if callable(is_owner) else is_owner
    
    print(f"Person: {person}")
    print(f"Is Owner: {is_owner}")
    
    if person:
        print(f"Person has subordinates: {person.subordinates.exists()}")
        if person.subordinates.exists():
            print(f"Direct subordinates: {list(person.subordinates.all())}")
    
    # Owner tidak boleh akses riwayat absensi (hanya supervisor dan employee)
    if is_owner:
        print("Branch: OWNER - NO ACCESS")
        attendances = Attendance.objects.none()
        messages.info(request, 'Owner tidak dapat mengakses riwayat absensi. Hanya supervisor dan karyawan yang dapat mengakses.')
    elif person:
        print("Branch: HAS PERSON")
        # Check if person is an employee (supervisor or regular employee)
        has_employee = hasattr(person, 'employee')
        print(f"Has employee attribute: {has_employee}")
        
        if has_employee:
            print("Sub-branch: PERSON IS EMPLOYEE")
            # Person is an employee - can be supervisor or regular employee
            employee = person.employee
            
            # Get all subordinates recursively
            def get_descendants(emp):
                descendants = set()
                direct_subs = emp.subordinates.all()
                print(f"Direct subordinates of {emp.name}: {list(direct_subs)}")
                for sub in direct_subs:
                    descendants.add(sub.id)
                    descendants.update(get_descendants(sub))
                return descendants
            
            subordinate_ids = get_descendants(employee)
            # Include self for supervisor and regular employee
            allowed_ids = subordinate_ids | {employee.id}
            
            print(f"Allowed employee IDs: {allowed_ids}")
            
            # Build attendance query with filters
            attendances = Attendance.objects.filter(
                employee__id__in=allowed_ids
            ).select_related('employee', 'borongan').order_by('-date')
            
            # Apply filters if provided
            if selected_employee_id:
                attendances = attendances.filter(employee__id=selected_employee_id)
                print(f"Filtered by employee: {selected_employee_id}")
            
            if selected_month and selected_year:
                attendances = attendances.filter(date__month=selected_month, date__year=selected_year)
                print(f"Filtered by month/year: {selected_month}/{selected_year}")
                
        else:
            print("Sub-branch: PERSON WITHOUT EMPLOYEE RECORD")
            # Person without employee record - supervisor yang hanya Person
            # Include self if exists as Employee
            allowed_ids = set()
            
            # Check if person exists as employee (by same ID)
            try:
                self_employee = Employee.objects.get(id=person.id)
                allowed_ids.add(self_employee.id)
                print(f"Found self as employee: {self_employee.id} - {self_employee.name}")
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
                        print(f"    Found as employee by ID: {emp.id} - {emp.name}")
                    except Employee.DoesNotExist:
                        print(f"    Not found as employee")
            
            print(f"Final allowed employee IDs: {allowed_ids}")
            
            if allowed_ids:
                attendances = Attendance.objects.filter(
                    employee__id__in=allowed_ids
                ).select_related('employee', 'borongan').order_by('-date')
                
                # Apply filters if provided
                if selected_employee_id:
                    attendances = attendances.filter(employee__id=selected_employee_id)
                    print(f"Filtered by employee: {selected_employee_id}")
                
                if selected_month and selected_year:
                    attendances = attendances.filter(date__month=selected_month, date__year=selected_year)
                    print(f"Filtered by month/year: {selected_month}/{selected_year}")
                    
                print(f"Attendances count: {attendances.count()}")
            else:
                attendances = Attendance.objects.none()
                print("No allowed IDs - empty queryset")
    else:
        print("Branch: NO PERSON - NO ACCESS")
        # No person record - no access
        attendances = Attendance.objects.none()
        messages.error(request, 'Profil karyawan tidak ditemukan. Tidak dapat mengakses riwayat absensi.')

    print(f"Final attendances count: {attendances.count()}")
    print(f"===========================\n")

    # Get available employees for filter dropdown
    if person and hasattr(person, 'employee'):
        employee = person.employee
        subordinate_ids = set()
        direct_subs = employee.subordinates.all()
        for sub in direct_subs:
            subordinate_ids.add(sub.id)
            # Get recursive subordinates
            def get_recursive_descendants(emp):
                descendants = set()
                for sub_emp in emp.subordinates.all():
                    descendants.add(sub_emp.id)
                    descendants.update(get_recursive_descendants(sub_emp))
                return descendants
            subordinate_ids.update(get_recursive_descendants(sub))
        
        allowed_ids = subordinate_ids | {employee.id}
        available_employees = Employee.objects.filter(id__in=allowed_ids).order_by('name')
    elif person:
        # Person without employee record
        allowed_ids = set()
        try:
            self_employee = Employee.objects.get(id=person.id)
            allowed_ids.add(self_employee.id)
        except Employee.DoesNotExist:
            pass
        
        for subordinate in person.subordinates.all():
            if hasattr(subordinate, 'employee'):
                allowed_ids.add(subordinate.employee.id)
            else:
                try:
                    emp = Employee.objects.get(id=subordinate.id)
                    allowed_ids.add(emp.id)
                except Employee.DoesNotExist:
                    pass
        
        available_employees = Employee.objects.filter(id__in=allowed_ids).order_by('name')
    else:
        available_employees = Employee.objects.none()

    # Get available months and years for filter dropdowns
    attendance_dates = attendances.values_list('date', flat=True)
    available_months = sorted(set(date.month for date in attendance_dates))
    available_years = sorted(set(date.year for date in attendance_dates), reverse=True)

    return render(request, 'compensation6/riwayat_abensi.html', {
        'attendances': attendances,
        'available_employees': available_employees,
        'available_months': available_months,
        'available_years': available_years,
        'selected_employee_id': selected_employee_id,
        'selected_month': selected_month,
        'selected_year': selected_year,
    })


from django.views.generic import TemplateView


class WorkCalendarView(TemplateView):
    template_name = 'compensation6/work_calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Debug: Print user information
        print(f"=== WORK CALENDAR VIEW USER DEBUG ===")
        print(f"User: {self.request.user}")
        print(f"User ID: {self.request.user.id}")
        print(f"Username: {self.request.user.username}")
        print(f"Email: {self.request.user.email}")
        print(f"Is Owner: {getattr(self.request.user, 'is_owner', False)}")
        print(f"Is Supervisor: {getattr(self.request.user, 'is_supervisor', False)}")
        print(f"Is Staff: {self.request.user.is_staff}")
        print(f"Is Superuser: {self.request.user.is_superuser}")
        
        # Check if user has person
        try:
            person = self.request.user.person
            print(f"Has Person: YES")
            print(f"Person: {person}")
            print(f"Person Name: {person.name if hasattr(person, 'name') else 'N/A'}")
            print(f"Person Company: {person.company if hasattr(person, 'company') else 'N/A'}")
        except AttributeError:
            print(f"Has Person: NO")
            person = None
        
        # Check if person is employee
        if person and hasattr(person, 'employee'):
            print(f"Is Employee: YES")
            print(f"Employee: {person.employee}")
            print(f"Employee Position: {person.employee.position if person.employee.position else 'N/A'}")
        else:
            print(f"Is Employee: NO")
        
        print(f"=======================================")

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
