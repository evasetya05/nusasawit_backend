from datetime import date, timedelta
from django.utils import timezone
from django.db import transaction
from django.contrib import messages

from ..models import KPI, KPICycle, KPIEvaluation, KPIPeriodTarget
from ..forms import MonthlyActualTargetForm


def compute_roles(user, kpi):
    person = getattr(user, 'person', None)
    is_employee = kpi.employee == person
    is_supervisor = kpi.supervisor == person
    is_manager = person.subordinates.exists() if person else False
    return person, is_employee, is_supervisor, is_manager


def check_access(request, kpi, person):
    if not (request.user.is_staff or kpi.employee == person or kpi.supervisor == person):
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return False
    if kpi.status != KPI.Status.APPROVED:
        messages.error(request, 'Hanya KPI yang sudah disetujui yang dapat diisi target/nilai per periode.')
        return False
    return True


def build_labels_from_date(kpi, d: date):
    if not kpi.cycle:
        return d.strftime('%b %Y'), d.replace(day=1)

    period = kpi.cycle.period

    if period == KPICycle.Period.WEEKLY:
        iso_year, iso_week, _ = d.isocalendar()
        label = f"W{iso_week:02d} {iso_year}"
        period_start = d - timedelta(days=d.weekday())

    elif period == KPICycle.Period.MONTHLY:
        label = d.strftime('%b %Y')
        period_start = d.replace(day=1)

    elif period == KPICycle.Period.QUARTERLY:
        q = ((d.month - 1) // 3) + 1
        label = f"Q{q} {d.year}"
        period_start = d.replace(month=(q - 1) * 3 + 1, day=1)

    elif period == KPICycle.Period.SEMIANNUAL:
        h = 1 if d.month <= 6 else 2
        label = f"H{h} {d.year}"
        period_start = d.replace(month=(1 if h == 1 else 7), day=1)

    elif period == KPICycle.Period.ANNUAL:
        label = str(d.year)
        period_start = d.replace(month=1, day=1)

    else:
        label = d.strftime('%b %Y')
        period_start = d.replace(day=1)

    return label, period_start


def prefill_form_initial(kpi, form: MonthlyActualTargetForm, today):
    if kpi.cycle and kpi.cycle.period == KPICycle.Period.WEEKLY:
        iso_year, iso_week, _ = today.isocalendar()
        form.initial['week'] = f"{iso_year}-W{iso_week:02d}"
    else:
        form.initial['month'] = today.strftime('%Y-%m')


@transaction.atomic
def handle_table_submit(request, kpi, is_supervisor):
    period_labels = [pt.label for pt in KPIPeriodTarget.objects.filter(kpi=kpi)]
    for period_label in period_labels:
        actual_val = request.POST.get(f'actual_{period_label}')
        notes = request.POST.get(f'notes_{period_label}', '')
        target_val = request.POST.get(f'target_{period_label}')
        notes_supervisor = request.POST.get(f'notes_supervisor_{period_label}', '')

        if actual_val:
            try:
                actual_val = float(actual_val)
            except ValueError:
                actual_val = None

        if target_val:
            try:
                target_val = float(target_val)
            except ValueError:
                target_val = None

        if target_val is not None:
            try:
                pt = KPIPeriodTarget.objects.get(kpi=kpi, label=period_label)
                pt.target_value = target_val
                pt.save()
            except KPIPeriodTarget.DoesNotExist:
                pass

        if actual_val is not None or notes or notes_supervisor:
            try:
                pt = KPIPeriodTarget.objects.get(kpi=kpi, label=period_label)
                ev, _ = KPIEvaluation.objects.get_or_create(period_target=pt)
                if actual_val is not None:
                    ev.score = actual_val
                if notes:
                    ev.notes = notes
                if notes_supervisor:
                    ev.notes_supervisor = notes_supervisor
                ev.evaluated_by = request.user
                ev.status = KPIEvaluation.Status.APPROVED if is_supervisor else KPIEvaluation.Status.PENDING
                ev.save()
            except KPIPeriodTarget.DoesNotExist:
                pass
    messages.success(request, 'Data berhasil disimpan.')


@transaction.atomic
def process_form_submission(request, form, kpi, can_edit_actual, is_employee, is_supervisor, today):
    period = kpi.cycle.period if kpi.cycle else KPICycle.Period.MONTHLY

    if period == KPICycle.Period.WEEKLY:
        week_str = (form.cleaned_data.get('week') or '').strip()
        try:
            iso_year, iso_week = map(int, week_str.replace('W', '').split('-'))
            anchor = date.fromisocalendar(iso_year, iso_week, 1)
        except Exception:
            messages.error(request, 'Format minggu tidak valid (gunakan YYYY-Www).')
            return None, None

    elif period == KPICycle.Period.MONTHLY:
        anchor = form.cleaned_data.get('month') or today.replace(day=1)

    else:
        anchor = today

    label, period_start = build_labels_from_date(kpi, anchor)

    target_value = form.cleaned_data.get('target_value')
    if target_value is not None:
        KPIPeriodTarget.objects.update_or_create(
            kpi=kpi,
            period_start=period_start,
            defaults={'label': label, 'target_value': target_value}
        )

    actual_val = form.cleaned_data.get('actual_value') if can_edit_actual else None
    notes = form.cleaned_data.get('notes', '') if is_employee or request.user.is_staff else ''
    notes_supervisor = form.cleaned_data.get('notes_supervisor', '') if is_supervisor else ''

    if actual_val is not None:
        status = KPIEvaluation.Status.APPROVED if is_supervisor else KPIEvaluation.Status.PENDING
        pt, _ = KPIPeriodTarget.objects.get_or_create(
            kpi=kpi,
            period_start=period_start,
            defaults={'label': label, 'target_value': target_value}
        )
        KPIEvaluation.objects.update_or_create(
            period_target=pt,
            defaults={'score': actual_val, 'notes': notes, 'notes_supervisor': notes_supervisor, 'evaluated_by': request.user, 'status': status}
        )
    elif notes or notes_supervisor:
        pt, _ = KPIPeriodTarget.objects.get_or_create(
            kpi=kpi,
            period_start=period_start,
            defaults={'label': label, 'target_value': target_value}
        )
        ev, created = KPIEvaluation.objects.get_or_create(
            period_target=pt,
            defaults={'score': None, 'notes': notes, 'notes_supervisor': notes_supervisor, 'evaluated_by': request.user}
        )
        if not created:
            changed = False
            if notes and ev.notes != notes:
                ev.notes = notes
                changed = True
            if notes_supervisor and ev.notes_supervisor != notes_supervisor:
                ev.notes_supervisor = notes_supervisor
                changed = True
            if changed:
                ev.evaluated_by = request.user
                ev.save()

    messages.success(request, f'Data periode {label} berhasil disimpan.')
    return label, period_start


def build_summary(kpi):
    period_targets = KPIPeriodTarget.objects.filter(kpi=kpi).order_by('-period_start')
    eval_map = {e.period_target.label: e for e in KPIEvaluation.objects.filter(period_target__kpi=kpi)}
    rows = []
    total_target = 0
    total_actual = 0

    for pt in period_targets:
        e = eval_map.get(pt.label)
        row = make_row(pt, e)
        rows.append(row)
        total_target += (pt.target_value or 0)
        total_actual += (row.get('score') or 0)

    return rows, total_target, total_actual


def make_row(pt: KPIPeriodTarget, e: KPIEvaluation | None):
    target = pt.target_value or 0
    actual = getattr(e, 'score', None) or 0
    variance = actual - target if (pt.target_value is not None and getattr(e, 'score', None) is not None) else None
    return {
        'label': pt.label,
        'period_start': pt.period_start,
        'target_value': pt.target_value,
        'score': getattr(e, 'score', None),
        'notes': getattr(e, 'notes', ''),
        'notes_supervisor': getattr(e, 'notes_supervisor', ''),
        'evaluated_at': getattr(e, 'evaluated_at', None),
        'variance': variance,
        'status': getattr(e, 'status', None),
        'eval_id': getattr(e, 'id', None),
        'period_label': pt.label,
    }


def process_evaluation_action(evaluation: KPIEvaluation, action: str):
    if action == "reject":
        evaluation.score = 0
        evaluation.notes = ''
        evaluation.notes_supervisor = ''
        evaluation.status = KPIEvaluation.Status.REJECTED
    else:
        evaluation.status = KPIEvaluation.Status.APPROVED
    evaluation.save()
    pt = evaluation.period_target
    return make_row(pt, evaluation)
