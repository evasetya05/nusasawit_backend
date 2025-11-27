from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import json
from collections import defaultdict
from ..models import KPI
from .kpi_service import get_visible_kpis


def get_dashboard_data(user):
    """
    Get all data needed for the KPI dashboard.
    Returns a dictionary with all the dashboard data.
    """
    company = getattr(user, 'company', None)
    person = getattr(user, 'person', None)

    if not company:
        return None

    visible_kpis = get_visible_kpis(user, company)

    # Get supervised KPIs - for owners and supervisors
    if user.is_owner:
        supervised_kpis = visible_kpis.exclude(employee=person)
    else:
        # For non-owners, get KPIs where the user is the supervisor
        supervised_kpis = visible_kpis.filter(supervisor=person, status=KPI.Status.APPROVED)

    # Apply common ordering and limit
    supervised_kpis = supervised_kpis.order_by('-created_at')[:10] if person else KPI.objects.none()

    # Group supervised KPIs by employee
    grouped_supervised = defaultdict(list)
    for kpi in supervised_kpis:
        grouped_supervised[kpi.employee].append(kpi)
    grouped_supervised = dict(grouped_supervised)

    today = timezone.now().date()

    # Monthly trend data
    months = []
    y, m = today.year, today.month
    for _ in range(12):
        months.append((y, m))
        if m == 1:
            y, m = y - 1, 12
        else:
            m -= 1
    months.reverse()

    # sum target and actual per month
    kpi_monthly_data = visible_kpis.annotate(
        month=TruncMonth('period_targets__period_start')
    ).values('month').annotate(
        target=Sum('period_targets__target_value'),
        actual=Sum('period_targets__evaluations__score')
    )
    grouped_kpi_monthly_data = {}
    for group in kpi_monthly_data:
        if not group['month']:
            continue
        key = group['month'].strftime('%Y-%m')
        target = group['target'] or 0
        actual = group['actual'] or 0
        grouped_kpi_monthly_data[key] = {'target': target, 'actual': actual}

    # Prepare monthly chart data
    recent_labels = []
    sum_targets = []
    sum_actuals = []
    for (yy, mm) in months:
        key = f"{yy}-{mm:02d}"
        from datetime import date as _d
        lbl = _d(yy, mm, 1).strftime('%b %Y')
        recent_labels.append(lbl)
        sum_targets.append(grouped_kpi_monthly_data.get(key, {}).get('target', 0))
        sum_actuals.append(grouped_kpi_monthly_data.get(key, {}).get('actual', 0))



    return {
        'grouped_supervised': grouped_supervised,
        'recent_labels_json': json.dumps(recent_labels, default=float),
        'sum_targets_json': json.dumps(sum_targets, default=float),
        'sum_actuals_json': json.dumps(sum_actuals, default=float),
    }
