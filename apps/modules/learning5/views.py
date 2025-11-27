# apps/learning5/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from apps.core.models import Employee
from .models import TrainingNeed, Competency
from .forms import TrainingNeedForm, CompetencyForm


# === DASHBOARD ===
@login_required
def learning_dashboard(request):
    return render(request, 'learning5/learning_dashboard.html')


# === COMPETENCY ADD / EDIT ===
@login_required
def competency_add(request, pk=None):
    """
    Tambah atau edit Competency.
    Kalau pk diberikan → mode edit.
    """
    company = request.user.person.company
    competency = get_object_or_404(
        Competency, pk=pk, company=company) if pk else None

    if request.method == 'POST':
        form = CompetencyForm(request.POST, instance=competency)
        if form.is_valid():
            rec = form.save(commit=False)
            rec.company = company
            rec.save()
            messages.success(
                request,
                "Competency berhasil diperbarui." if competency else "Competency berhasil ditambahkan."
            )
            return redirect('learning5:competency_add')
    else:
        form = CompetencyForm(instance=competency)

    competencies = Competency.objects.filter(company=company).order_by('name')
    return render(request, 'learning5/competency_form.html', {
        'form': form,
        'competencies': competencies,
        'edit_mode': bool(pk),
        'competency': competency,
    })


@login_required
def load_detail_competencies(request):
    competency_name = request.GET.get('competency_name')
    company = request.user.person.company
    details = Competency.objects.filter(
        name=competency_name, company=company).values('id', 'description')
    return JsonResponse(list(details), safe=False)


# === TRAINING NEED: LIST ===
@login_required
def trainingneed_list(request):
    person = getattr(request.user, 'person', None)
    base_qs = TrainingNeed.objects.select_related(
        'employee', 'competency', 'detail_competency', 'assessed_by'
    )

    if request.user.is_owner:
        needs = base_qs
    elif person and person.subordinates.exists():
        needs = base_qs.filter(employee__in=person.subordinates.all() | Employee.objects.filter(pk=person.pk))
    elif person:
        needs = base_qs.filter(employee=person)
    else:
        needs = base_qs.none()

    grouped_needs = {}
    for need in needs:
        emp_name = need.employee.name if need.employee else 'Tidak Diketahui'
        grouped_needs.setdefault(emp_name, []).append(need)

    return render(request, 'learning5/trainingneed_list.html', {
        'grouped_needs': grouped_needs,
        'is_owner': request.user.is_owner,
    })


# === TAMBAH TRAINING NEED ===
@login_required
def trainingneed_add(request):
    company = request.user.person.company
    if request.method == 'POST':
        form = TrainingNeedForm(request.POST, current_user=request.user)
        if form.is_valid():
            training_need = form.save(commit=False)
            training_need.company = company
            training_need.assessed_by = request.user
            training_need.save()
            messages.success(
                request, "Kebutuhan pelatihan berhasil ditambahkan.")
            return redirect('learning5:trainingneed_list')
    else:
        form = TrainingNeedForm(current_user=request.user)

    needs = TrainingNeed.objects.filter(company=company).select_related(
        'employee', 'competency', 'detail_competency')
    return render(request, 'learning5/trainingneed_form.html', {
        'form': form,
        'needs': needs,
    })


# === EDIT TRAINING NEED ===
@login_required
def trainingneed_edit(request, pk):
    need = get_object_or_404(TrainingNeed, pk=pk, company=request.user.person.company)

    if request.method == 'POST':
        form = TrainingNeedForm(request.POST, instance=need, current_user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Training Need berhasil diperbarui.")
            return redirect('learning5:trainingneed_list')
    else:
        form = TrainingNeedForm(instance=need, current_user=request.user)

    return render(request, 'learning5/trainingneed_form.html', {
        'form': form,
        'object': need,
        'edit_mode': True,
    })


# === DELETE TRAINING NEED ===
@login_required
def trainingneed_delete(request, pk):
    if not request.user.is_owner:
        messages.error(request, 'Hanya owner yang dapat menghapus AKP.')
        return redirect('learning5:trainingneed_list')

    need = get_object_or_404(TrainingNeed, pk=pk)

    if request.method == 'POST':
        need.delete()
        messages.success(request, 'AKP berhasil dihapus.')
    else:
        messages.error(request, 'Gunakan tombol hapus untuk menghapus AKP.')

    return redirect('learning5:trainingneed_list')
