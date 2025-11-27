import logging
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from typing import Dict, Iterable, List

from django.db.models import Case, When, Sum, Q

from apps.core.models import Employee

from ..models import KPI, KPIPeriodTarget, KPIEvaluation

logger = logging.getLogger(__name__)


TWO_PLACES = Decimal("0.01")


def _decimal(value: object) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if value in (None, ""):
        return Decimal("0")
    return Decimal(str(value))


def _build_subordinate_map(company) -> Dict[int, List[int]]:
    """Build an adjacency list of employees keyed by manager id within a company."""
    relations = Employee.objects.filter(company=company).values_list("manager_id", "id")
    tree: Dict[int, List[int]] = defaultdict(list)
    for manager_id, employee_id in relations:
        if manager_id is None:
            continue
        tree[manager_id].append(employee_id)
    return tree


def _collect_subordinate_ids(tree: Dict[int, List[int]], manager_id: int) -> List[int]:
    """Collect ids for all nested subordinates of a manager using the provided tree."""
    if manager_id is None:
        return []

    seen: set[int] = set()
    stack: List[int] = list(tree.get(manager_id, []))

    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(tree.get(current, []))

    return list(seen)


def _annotate_kpis_with_totals(queryset):
    return queryset.annotate(
        total_target=Sum("period_targets__target_value"),
        approved_score=Sum(
            "period_targets__evaluations__score",
            filter=Q(period_targets__evaluations__status=KPIEvaluation.Status.APPROVED),
        ),
    )


def _compute_percentage(score, target) -> float | None:
    if target is None:
        return None

    target_dec = _decimal(target)
    if target_dec == 0:
        return None

    if score is None:
        return None

    pct = (_decimal(score) / target_dec) * Decimal("100")
    return float(pct.quantize(TWO_PLACES))


def _compute_weighted_percentage(pct: float | None, weight, total_weight: Decimal) -> float | None:
    if pct is None:
        return None

    weight_dec = _decimal(weight)
    if weight_dec <= 0 or total_weight <= 0:
        return None

    weighted = Decimal(str(pct)) * weight_dec / total_weight
    return float(weighted.quantize(TWO_PLACES))


def _build_kpi_data(kpi_queryset) -> List[Dict[str, object]]:
    kpis = list(_annotate_kpis_with_totals(kpi_queryset))
    total_weight = sum((_decimal(kpi.weight) for kpi in kpis), Decimal("0"))

    result: List[Dict[str, object]] = []
    for kpi in kpis:
        target = getattr(kpi, "total_target", None)
        score = getattr(kpi, "approved_score", None)
        pct = _compute_percentage(score, target)
        weighted_pct = _compute_weighted_percentage(pct, kpi.weight, total_weight)

        result.append({
            "kpi": kpi,
            "target": target,
            "score": score,
            "pct": pct,
            "weighted_pct": weighted_pct,
        })

    return result


def get_visible_kpis(user, company):
    """Get KPIs visible to the user based on their role."""
    base_qs = KPI.objects.filter(company=company).select_related("employee", "supervisor", "cycle")

    if user.is_owner:
        return base_qs

    person = getattr(user, 'person', None)
    if not person:
        return KPI.objects.none()

    # Check if user is a supervisor (has supervised KPIs)
    is_supervisor = KPI.objects.filter(company=company, supervisor=person).exists()
    if is_supervisor:
        tree = _build_subordinate_map(company)
        subordinate_ids = _collect_subordinate_ids(tree, person.id)
        subordinate_filter = Q(employee__id__in=subordinate_ids) if subordinate_ids else Q()
        # Supervisor can see their own KPIs and KPIs supervised by them, and KPIs of subordinates recursive
        return base_qs.filter(
            Q(employee=person) | Q(supervisor=person) | subordinate_filter
        )
    else:
        # Regular employee can only see their own KPIs
        return base_qs.filter(employee=person)


def get_kpi_list_data(user) -> Dict[str, object]:
    """
    Build context data for KPI list page for the current user.
    Raises ValueError or PermissionError for known validation failures.
    """
    logger.info(f"User: {user}, is_authenticated: {getattr(user, 'is_authenticated', False)}")

    person = getattr(user, 'person', None)
    if not person:
        logger.error("User has no person attribute")
        raise ValueError("Profil Anda belum lengkap. Silakan hubungi administrator.")

    user_company = getattr(user, 'company', None)
    person_company = getattr(person, 'company', None)
    logger.info(f"Person found: {person}, Company: {person_company if person_company else 'No company'}")

    if not person_company or person_company != user_company:
        logger.error(
            f"Company mismatch - Person company: {person_company}, User company: {user_company}"
        )
        raise PermissionError("Akses ditolak. Perusahaan tidak sesuai.")

    visible_kpis = get_visible_kpis(user, user_company)

    my_kpis = visible_kpis.filter(employee=person).order_by(
        Case(
            When(status=KPI.Status.APPROVED, then=1),
            When(status=KPI.Status.SUBMITTED, then=2),
            When(status=KPI.Status.DRAFT, then=3),
            default=4
        ),
        '-created_at'
    )
    logger.info(f"Found {my_kpis.count()} KPIs for employee")

    supervised_kpis = visible_kpis.exclude(employee=person).order_by(
        Case(
            When(status=KPI.Status.APPROVED, then=1),
            When(status=KPI.Status.SUBMITTED, then=2),
            When(status=KPI.Status.DRAFT, then=3),
            default=4
        ),
        Case(
            When(cycle__period='weekly', then=1),
            When(cycle__period='monthly', then=2),
            When(cycle__period='quarterly', then=3),
            When(cycle__period='semiannual', then=4),
            When(cycle__period='annual', then=5),
            default=6
        ),
        '-created_at'
    )
    logger.info(f"Found {supervised_kpis.count()} supervised KPIs")

    supervised_kpis_with_data = _build_kpi_data(supervised_kpis)

    # Split supervised KPIs for template rendering needs
    supervised_kpis_submitted = [k for k in supervised_kpis_with_data if getattr(k['kpi'], 'status', None) == KPI.Status.SUBMITTED]
    supervised_kpis_others = [k for k in supervised_kpis_with_data if getattr(k['kpi'], 'status', None) != KPI.Status.SUBMITTED]

    my_kpis_with_data = _build_kpi_data(my_kpis)
    # Calculate average % for my_kpis
    my_pcts = [k['pct'] for k in my_kpis_with_data if k['pct'] is not None]
    my_total_pct = sum(my_pcts)
    my_total_pct = round(my_total_pct, 2)
    my_total_weight = sum(k['kpi'].weight for k in my_kpis_with_data)
    my_total_weighted_pct = sum(k['weighted_pct'] for k in my_kpis_with_data if k['weighted_pct'] is not None)
    my_total_weighted_pct = round(my_total_weighted_pct, 2)

    return {
        'my_kpis': my_kpis_with_data,
        'my_total_pct': my_total_pct,
        'my_total_weight': my_total_weight,
        'my_total_weighted_pct': my_total_weighted_pct,
        'supervised_kpis_submitted': supervised_kpis_submitted,
        'supervised_kpis_others': supervised_kpis_others,
    }


def create_kpi_period_targets(kpi, post_data):
    labels = post_data.getlist('pt_label[]')
    starts = post_data.getlist('pt_start[]')
    targets = post_data.getlist('pt_target[]')
    try:
        for lbl, st, tv in zip(labels, starts, targets):
            if not st:
                continue
            from datetime import datetime
            period_start = datetime.strptime(st, '%Y-%m-%d').date()
            tv_val = None
            if tv not in (None, '',):
                try:
                    tv_val = Decimal(str(tv))
                except (InvalidOperation, ValueError, TypeError):
                    tv_val = None
            KPIPeriodTarget.objects.update_or_create(
                kpi=kpi, period_start=period_start,
                defaults={'label': lbl, 'target_value': tv_val}
            )
    except Exception as e:
        logger.warning(f"Error saving period grid for KPI {kpi.id}: {e}")
        raise
