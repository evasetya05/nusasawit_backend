from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, QueryDict, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from django.views.generic import TemplateView
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.db import transaction

import logging
from .forms import KPICycleForm, KPIForm, MonthlyActualTargetForm
from .models import KPI, KPICycle, KPIEvaluation, KPIPeriodTarget
from .services.dashboard_service import get_dashboard_data
from .services.kpi_service import (
    get_kpi_list_data,
    create_kpi_period_targets,
)
from .services.period_input_service import (
    compute_roles,
    check_access,
    prefill_form_initial,
    handle_table_submit,
    process_form_submission,
    build_summary,
    process_evaluation_action,
)
from .services.period_service import generate_periods
import json

logger = logging.getLogger(__name__)


@login_required
def kinerja4(request):
    try:
        company = getattr(request.user, 'company', None)

        if not company:
            messages.error(request, 'Perusahaan tidak ditemukan pada akun Anda.')
            return redirect('dashboard:index') if hasattr(messages, 'index') else render(request, 'kinerja4/kinerja_dashboard.html')

        context = get_dashboard_data(request.user)
        context['title'] = 'Dashboard Kinerja'
        return render(request, 'kinerja4/kinerja_dashboard.html', context)
    except Exception as e:
        logger.error(f"Error in kinerja4 dashboard: {str(e)}", exc_info=True)
        messages.error(request, f'Terjadi kesalahan saat memuat dashboard: {str(e)}')
        return render(request, 'kinerja4/kinerja_dashboard.html')


class KPIListView(LoginRequiredMixin, TemplateView):
    template_name = 'kinerja4/kpi_list.html'

    def get(self, request, *args, **kwargs):
        try:
            context = get_kpi_list_data(request.user)
            context['title'] = 'Daftar KPI'
            return render(request, self.template_name, context)
        except (PermissionError, ValueError) as e:
            messages.error(request, str(e))
            return redirect('kinerja4:dashboard')
        except Exception as e:
            logger.error(f"Error in KPIListView: {str(e)}", exc_info=True)
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            return redirect('kinerja4:dashboard')


class KPICreateView(LoginRequiredMixin, CreateView):
    model = KPI
    form_class = KPIForm
    template_name = 'kinerja4/kpi_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = getattr(self.request.user, 'person', None)
        manager = getattr(person, 'manager', None)
        context['supervisor_display'] = getattr(manager, 'name', '-')
        context['title'] = 'Tambah KPI'
        return context

    def form_valid(self, form):
        try:
            user = self.request.user
            form.instance.company = user.company
            form.instance.employee = user.person
            if hasattr(user, "person") and getattr(user.person, "manager", None):
                form.instance.supervisor = user.person.manager
            form.instance.created_by = user
            response = super().form_valid(form)
            create_kpi_period_targets(self.object, self.request.POST)
            messages.success(self.request, 'KPI dibuat beserta target per-periode.')
            return response
        except Exception as e:
            logger.error(f"Error in KPICreateView: {str(e)}", exc_info=True)
            messages.error(self.request, f'Terjadi kesalahan: {str(e)}')
            return redirect('kinerja4:dashboard')

    def form_invalid(self, form):
        messages.error(self.request, 'Terjadi kesalahan saat membuat KPI.')
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('kinerja4:kpi_detail', kwargs={'kpi_id': self.object.id})


class KPIEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = KPI
    form_class = KPIForm
    template_name = 'kinerja4/kpi_form.html'
    pk_url_kwarg = 'kpi_id'

    def get_queryset(self):
        return KPI.objects.filter(company=self.request.user.company)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        kpi = self.get_object()
        employee = getattr(self.request.user, 'person', None)
        return kpi.employee == employee and kpi.status == KPI.Status.DRAFT

    def handle_no_permission(self):
        try:
            kpi = self.get_object()
            messages.error(self.request, 'Anda tidak memiliki izin untuk mengedit KPI ini atau KPI sudah diajukan.')
            return redirect('kinerja4:kpi_detail', kpi_id=kpi.id)
        except Exception:
            messages.error(self.request, 'Anda tidak memiliki izin untuk mengedit KPI ini.')
            return redirect('kinerja4:kpi_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit KPI'
        context['kpi'] = self.object
        employee = getattr(self.object, "employee", None)
        supervisor = getattr(employee, "manager", None)
        context["supervisor_display"] = getattr(supervisor, "name", "-")

        cycle = self.object.cycle
        periods = generate_periods(
            period_type=cycle.period,
            start_date=cycle.start_date,
            end_date=cycle.end_date,
            kpi_id=self.object.id,
        )
        context['periods'] = periods
        context['is_editable'] = self.object.status == KPI.Status.DRAFT
        return context

    def form_valid(self, form):
        # Check if cycle is being changed
        old_cycle = None
        if self.object.pk:
            old_cycle = KPI.objects.get(pk=self.object.pk).cycle
        new_cycle = form.cleaned_data.get('cycle')
        cycle_changed = old_cycle and new_cycle and (old_cycle != new_cycle)

        try:
            with transaction.atomic():
                response = super().form_valid(form)

                if cycle_changed:
                    self.object.period_targets.all().delete()

                create_kpi_period_targets(self.object, self.request.POST)
                messages.success(self.request, 'Perubahan KPI dan target per-periode berhasil disimpan.')
                return response

        except Exception as e:
            logger.error(f"Error in KPIEditView: {str(e)}", exc_info=True)
            messages.error(self.request, f'Terjadi kesalahan: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Terjadi kesalahan saat menyimpan perubahan KPI.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('kinerja4:kpi_detail', kwargs={'kpi_id': self.object.id})


@login_required
def get_period_grid(request):
    cycle_id = request.GET.get('cycle')
    if not cycle_id:
        return JsonResponse({'error': 'No cycle selected'}, status=400)
    cycle = get_object_or_404(KPICycle, id=cycle_id)

    kpi_id = request.GET.get('kpi_id') or None

    periods = generate_periods(
        period_type=cycle.period,
        start_date=cycle.start_date,
        end_date=cycle.end_date,
        kpi_id=kpi_id,
    )

    context = {
        'periods': periods,
        'cycle': cycle,
        'is_editable': not kpi_id or KPI.objects.filter(id=kpi_id, status=KPI.Status.DRAFT).exists()
    }

    if request.htmx:
        return render(request, 'kinerja4/partials/period_grid.html', context)
    return JsonResponse({'error': 'HTMX request required'}, status=400)


class KPIDetailView(LoginRequiredMixin, DetailView):
    model = KPI
    template_name = 'kinerja4/kpi_detail.html'
    context_object_name = 'kpi'
    pk_url_kwarg = 'kpi_id'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kpi = self.object
        person = getattr(self.request.user, 'person', None)

        if not person:
            messages.error(self.request, 'Profil Anda belum lengkap.')
            return redirect('kinerja4:kpi_list')

        is_employee = kpi.employee == person
        is_supervisor = kpi.supervisor == person

        # Check if user has permission to view this KPI
        if not (self.request.user.is_owner or
               is_employee or
               is_supervisor):
            messages.error(self.request, 'Anda tidak memiliki izin untuk melihat KPI ini')
            return redirect('kinerja4:kpi_list')

        # Get evaluations if they exist
        evaluations = getattr(kpi, 'evaluations', None)
        is_can_approve = (is_supervisor or self.request.user.is_owner) and kpi.status == 'SUBMITTED'
        # Check if person is in the management chain of the KPI's employee
        is_manager = False
        if hasattr(kpi.employee, 'manager'):
            current = kpi.employee
            while current and hasattr(current, 'manager') and current.manager:
                if current.manager == person:
                    is_manager = True
                    break
                current = current.manager
            # Also check if person is the company owner
            is_manager = is_manager or getattr(self.request.user, 'is_owner', False)

        context.update({
            'evaluations': evaluations,
            'can_edit': is_employee and kpi.status == 'DRAFT',
            'can_approve': is_can_approve,
            'is_manager': is_manager,
            'title': f'Detail KPI: {kpi.title}'
        })

        try:
            rows, total_target, total_actual = build_summary(kpi)
            # Build chart data in chronological order
            pts = KPIPeriodTarget.objects.filter(kpi=kpi).order_by('period_start')
            eval_map = {e.period_target_id: e for e in KPIEvaluation.objects.filter(period_target__kpi=kpi)}
            labels = []
            targets = []
            actuals = []
            for pt in pts:
                labels.append(pt.label)
                targets.append(float(pt.target_value or 0))
                ev = eval_map.get(pt.id)
                actuals.append(float(getattr(ev, 'score', 0) or 0))

            achievement_pct = round((total_actual / total_target * 100), 2) if total_target else None

            context.update({
                'rows': rows,
                'total_target': total_target,
                'total_actual': total_actual,
                'achievement_pct': achievement_pct,
                'chart_labels_json': json.dumps(labels),
                'chart_targets_json': json.dumps(targets, default=float),
                'chart_actuals_json': json.dumps(actuals, default=float),
            })
        except Exception:
            pass

        return context

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Exception as e:
            logger.error(f"Error in KPIDetailView: {str(e)}", exc_info=True)
            messages.error(request, f'Terjadi kesalahan saat memuat detail KPI: {str(e)}')
            return redirect('kinerja4:kpi_list')

        context = self.get_context_data(object=self.object)
        if isinstance(context, HttpResponse):
            return context
        return self.render_to_response(context)


@login_required
def kpi_submit(request, kpi_id: int):
    kpi = get_object_or_404(KPI, id=kpi_id, company=request.user.company)
    employee = getattr(request.user, 'person', None)
    if kpi.employee != employee or kpi.status != KPI.Status.DRAFT:
        return HttpResponseForbidden()
    kpi.status = KPI.Status.SUBMITTED
    kpi.save(update_fields=['status'])
    messages.success(request, 'KPI diajukan untuk persetujuan.')
    return render(request, 'kinerja4/partials/kpi_approval.html', {'kpi': kpi})


class KPICycleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = KPICycle
    form_class = KPICycleForm
    template_name = 'kinerja4/cycle_create.html'
    success_url = reverse_lazy('kinerja4:cycle_create')
    permission_denied_message = "Anda tidak memiliki izin untuk menambahkan siklus KPI."

    def test_func(self):
        return self.request.user.has_perm("kinerja4.add_kpiperiodtarget")

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, self.permission_denied_message)
        return redirect(reverse("dashboard"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cycles'] = KPICycle.objects.filter(company=self.request.user.company).order_by('-start_date')
        context['title'] = 'Buat Siklus KPI Baru'
        return context

    def form_valid(self, form):
        try:
            form.instance.company = self.request.user.company
            response = super().form_valid(form)
            messages.success(self.request, 'Siklus KPI berhasil disimpan!')
            return response
        except Exception as e:
            logger.error(f"Error saving KPICycle: {str(e)}", exc_info=True)
            messages.error(self.request, f'Terjadi kesalahan: {str(e)}')
            return self.form_invalid(form)


class KPICycleTemplateView(LoginRequiredMixin, TemplateView):
    model = KPICycle
    template_name = "kinerja4/cycle_create.html"

    def get_object(self):
        return get_object_or_404(
            self.model, id=self.kwargs.get("id"), company=self.request.user.company
        )

    def patch(self, request, *args, **kwargs):
        if request.user.has_perm("kinerja4.change_kpiperiodtarget"):
            cycle = self.get_object()
            data = QueryDict(request.body.decode("utf-8"))
            action = data.get("action")
            cycle.active = True if action == "activate" else False
            cycle.save()
            messages.success(
                request,
                f'Siklus "{cycle.name}" berhasil di{"aktifkan" if cycle.active else "nonaktifkan"}.',
            )
            return render(
                request,
                "kinerja4/partials/cycle_activate.html",
                {
                    "cycle": cycle,
                },
            )
        else:
            messages.error(
                request, "Anda tidak memiliki izin untuk mengubah siklus KPI ini."
            )
            return HttpResponse(status=403)


class KPIApprovalView(LoginRequiredMixin, View):
    template_name = 'kinerja4/partials/kpi_approval.html'

    def get_kpi(self):
        return get_object_or_404(KPI, id=self.kwargs.get('kpi_id'), company=self.request.user.company)

    def post(self, request, *args, **kwargs):
        kpi = self.get_kpi()
        employee = getattr(request.user, 'person', None)
        action = request.POST.get('action')

        is_authorized = (kpi.supervisor == employee or request.user.is_owner)
        if not is_authorized or kpi.status != KPI.Status.SUBMITTED or action not in ['approve', 'reject']:
            return HttpResponseForbidden("Anda tidak memiliki izin untuk menyetujui/menolak KPI ini.")

        kpi.status = KPI.Status.APPROVED if action == 'approve' else KPI.Status.REJECTED
        kpi.save(update_fields=['status'])

        action_text = 'disetujui' if action == 'approve' else 'ditolak'
        messages.success(request, f'KPI {action_text}.')
        return render(request, self.template_name, {'kpi': kpi})


class KPIPeriodInputView(LoginRequiredMixin, View):
    template_name = 'kinerja4/kpi_period_input.html'

    def get_kpi(self, request, kpi_id):
        return get_object_or_404(KPI, id=kpi_id, company=request.user.company)

    def get(self, request, kpi_id: int):
        kpi = self.get_kpi(request, kpi_id)
        person, is_employee, is_supervisor, is_manager = compute_roles(request.user, kpi)
        if not check_access(request, kpi, person):
            return redirect('kinerja4:kpi_detail', kpi_id=kpi.id)

        form = MonthlyActualTargetForm()
        today = timezone.now().date()
        prefill_form_initial(kpi, form, today)

        rows, total_target, total_actual = build_summary(kpi)
        return render(request, self.template_name, {
            'kpi': kpi,
            'form': form,
            'rows': rows,
            'total_target': total_target,
            'total_actual': total_actual,
            'title': 'Input Target & Nilai Per Periode',
            'can_edit_period': True,
            'is_supervisor': is_supervisor,
            'is_manager': is_manager,
        })

    def post(self, request, kpi_id: int):
        kpi = self.get_kpi(request, kpi_id)
        person, is_employee, is_supervisor, is_manager = compute_roles(request.user, kpi)
        if not check_access(request, kpi, person):
            return redirect('kinerja4:kpi_detail', kpi_id=kpi.id)

        today = timezone.now().date()
        form = MonthlyActualTargetForm(request.POST)

        if 'submit_table' in request.POST:
            handle_table_submit(request, kpi, is_supervisor)
            return redirect('kinerja4:kpi_period_input', kpi_id=kpi.id)

        if form.is_valid():
            process_form_submission(request, form, kpi, can_edit_actual=True, is_employee=is_employee, is_supervisor=is_supervisor, today=today)
            return redirect('kinerja4:kpi_period_input', kpi_id=kpi.id)

        # If invalid, re-render with errors and current summary
        rows, total_target, total_actual = build_summary(kpi)
        return render(request, self.template_name, {
            'kpi': kpi,
            'form': form,
            'rows': rows,
            'total_target': total_target,
            'total_actual': total_actual,
            'title': 'Input Target & Nilai Per Periode',
            'can_edit_period': True,
            'is_supervisor': is_supervisor,
            'is_manager': is_manager,
        })


class KPIEvaluationApprovalView(LoginRequiredMixin, View):
    def get_object(self):
        return get_object_or_404(KPIEvaluation, id=self.kwargs.get("eval_id"))

    def patch(self, request, *args, **kwargs):
        evaluation = self.get_object()
        person = getattr(request.user, 'person', None)
        if evaluation.period_target.kpi.supervisor != person:
            messages.error(request, 'Anda tidak memiliki izin untuk menyetujui evaluasi ini.')
            return HttpResponseForbidden()
        if evaluation.status != KPIEvaluation.Status.PENDING:
            messages.error(request, 'Evaluasi sudah diproses.')
            return HttpResponseForbidden()

        data = QueryDict(request.body.decode("utf-8"))
        action = data.get("action")
        if action not in ["approve", "reject"]:
            return HttpResponseForbidden()
        evaluation_ctx = process_evaluation_action(evaluation, action)
        messages.success(
            request,
            f'Evaluasi periode "{evaluation_ctx.get("label")}" berhasil di{"setujui" if action == "approve" else "tolak dan data direset"}.',
        )
        return render(
            request,
            "kinerja4/partials/evaluation_approval.html",
            {
                "evaluation": evaluation_ctx,
            },
        )
