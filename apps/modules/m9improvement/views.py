from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from .models import OcaiQuestion, OcaiAnswer

from .forms import OcaiForm
from .services import save_ocai_answers, get_continues_improvement_data


@login_required
def continues_improvement_dashboard(request):
    company = request.user.company
    # Optional period filters via query params
    period_year = request.GET.get('year')
    period_half = request.GET.get('half')
    try:
        period_year = int(period_year) if period_year else None
    except (TypeError, ValueError):
        period_year = None
    try:
        period_half = int(period_half) if period_half else None
    except (TypeError, ValueError):
        period_half = None

    grouped_data, overall_averages = get_continues_improvement_data(company, period_year, period_half)

    return render(request, 'm9improvement/continues_improvement_dashboard.html', {
        'grouped_data': grouped_data,
        'overall_averages': overall_averages,
        'period_year': period_year,
        'period_half': period_half,
    })


@login_required
def ocai_form(request):
    if not hasattr(request.user, 'person'):
        return render(request, 'm9improvement/ocai_not_allowed.html')

    company = request.user.company
    pertanyaan_list = OcaiQuestion.objects.all().order_by('dimension')
    grouped_pertanyaan = defaultdict(list)
    for pertanyaan in pertanyaan_list:
        grouped_pertanyaan[pertanyaan.dimension].append(pertanyaan)

    if request.method == 'POST':
        form = OcaiForm(request.POST)
        if form.is_valid():
            period_year = int(form.cleaned_data['period_year'])
            period_half = int(form.cleaned_data['period_half'])
            save_ocai_answers(form.cleaned_data, request.user.person, period_year, period_half)
            return redirect('m9improvement:thank_you')
    else:
        form = OcaiForm()

    return render(request, 'm9improvement/ocai_form.html', {
        'form': form,
        'grouped_pertanyaan': dict(grouped_pertanyaan),
        'company': company,
    })


@login_required
def result_ocai(request):
    company = request.user.company

    # Optional period filters via query params
    period_year = request.GET.get('year')
    period_half = request.GET.get('half')
    try:
        period_year = int(period_year) if period_year else None
    except (TypeError, ValueError):
        period_year = None
    try:
        period_half = int(period_half) if period_half else None
    except (TypeError, ValueError):
        period_half = None

    qs = OcaiAnswer.objects.filter(employee__company=company)
    if period_year is not None:
        qs = qs.filter(period_year=period_year)
    if period_half is not None:
        qs = qs.filter(period_half=period_half)

    # Group by department, then by employee (nama_karyawan)
    grouped_by_departemen = {}
    for item in qs:
        departemen = item.employee.department or "Unknown"
        nama_karyawan = item.employee.name or "Anonymous"

        if departemen not in grouped_by_departemen:
            grouped_by_departemen[departemen] = {}

        if nama_karyawan not in grouped_by_departemen[departemen]:
            grouped_by_departemen[departemen][nama_karyawan] = []

        grouped_by_departemen[departemen][nama_karyawan].append(item)

    return render(request, 'm9improvement/result_ocai.html', {
        'grouped_by_departemen': grouped_by_departemen,
        'period_year': period_year,
        'period_half': period_half,
    })



def thankyou(request):
    return render(request, 'm9improvement/thank_you.html')
