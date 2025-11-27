from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from .models import OcaiQuestion, OcaiAnswer

from .forms import OcaiForm
from .services import save_ocai_answers, get_continues_improvement_data


@login_required
def continues_improvement_dashboard(request):
    company = request.user.company
    grouped_data, overall_averages = get_continues_improvement_data(company)

    return render(request, 'm9improvement/continues_improvement_dashboard.html', {
        'grouped_data': grouped_data,
        'overall_averages': overall_averages
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
            save_ocai_answers(form.cleaned_data, request.user.person)
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

    result_ocai = OcaiAnswer.objects.filter(employee__company=company)

    # Group by department, then by employee (nama_karyawan)
    grouped_by_departemen = {}
    for item in result_ocai:
        departemen = item.employee.department or "Unknown"
        nama_karyawan = item.employee.name or "Anonymous"

        if departemen not in grouped_by_departemen:
            grouped_by_departemen[departemen] = {}

        if nama_karyawan not in grouped_by_departemen[departemen]:
            grouped_by_departemen[departemen][nama_karyawan] = []

        grouped_by_departemen[departemen][nama_karyawan].append(item)

    return render(request, 'm9improvement/result_ocai.html', {
        'grouped_by_departemen': grouped_by_departemen,
    })



def thankyou(request):
    return render(request, 'm9improvement/thank_you.html')
