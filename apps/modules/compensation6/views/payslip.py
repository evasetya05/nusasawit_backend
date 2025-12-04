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
    print(f"PDF Request - Employee: {employee_id}, Month: {month}, Year: {year}")
    
    try:
        ctx = _get_payroll_bundle(employee_id, month, year)
        print(f"Context loaded for employee: {ctx['employee'].name}")
    except Exception as e:
        print(f"Context error: {e}")
        return HttpResponseBadRequest(str(e))
    
    # Use clean template for PDF (no layout, no navigation)
    html = render_to_string('compensation6/payslip_pdf_clean.html', {**ctx, 'preview': False}, request=request)
    print(f"HTML rendered, length: {len(html)}")
    
    try:
        from weasyprint import HTML
        pdf = HTML(string=html).write_pdf()
        print(f"PDF generated, size: {len(pdf)} bytes")
        
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"slip_borongan_{ctx['employee'].name}_{int(month):02d}-{year}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        print(f"Returning PDF with filename: {filename}")
        return response
    except Exception as e:
        print(f"WeasyPrint error: {e}")
        import traceback
        traceback.print_exc()
        messages.warning(request, f'PDF generation failed: {str(e)}')
        return HttpResponse(html)


# Payslip: select and preview
def payslip_select(request):
    print(f"\n=== PAYSLIP VIEW DEBUG ===")
    print(f"Request user: {request.user}")
    person = getattr(request.user, 'person', None)
    print(f"Person: {person}")
    
    if person:
        print(f"Person has subordinates: {person.subordinates.exists()}")
        if person.subordinates.exists():
            print(f"Direct subordinates: {list(person.subordinates.all())}")
    
    print(f"===========================\n")
    
    form = PayslipSelectionForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        emp_id = form.cleaned_data['employee'].id
        month = form.cleaned_data['month']
        year = form.cleaned_data['year']
        return redirect('compensation6:payslip_preview', employee_id=emp_id, month=month, year=year)
    return render(request, 'compensation6/payslip_form.html', {'form': form})
