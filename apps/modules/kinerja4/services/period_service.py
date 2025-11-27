import datetime
from typing import List, Dict, Any
from ..models import KPIPeriodTarget

def monday(d: datetime.date) -> datetime.date:
    """Get the Monday of the week containing the given date."""
    dt = datetime.date(d.year, d.month, d.day)
    day = dt.weekday()  # Monday is 0, Sunday is 6
    return dt - datetime.timedelta(days=day)


def iso_week(d: datetime.date) -> Dict[str, int]:
    """Get ISO week number and year for the given date."""
    # Thursday in the target week (ISO weeks start on Monday)
    d = d - datetime.timedelta(days=d.weekday() - 3)
    # January 4th is always in week 1 (ISO 8601)
    week1 = datetime.date(d.year, 1, 4)
    week1_monday = week1 - datetime.timedelta(days=week1.weekday())

    if d < week1_monday:
        week1 = datetime.date(d.year - 1, 1, 4)
        week1_monday = week1 - datetime.timedelta(days=week1.weekday())

    week_num = (d - week1_monday).days // 7 + 1
    return {'year': week1.year + (1 if week_num > 0 and d.month == 1 else 0), 'week': week_num}


def generate_periods(
    period_type: str,
    start_date: datetime.date,
    end_date: datetime.date,
    kpi_id: int = None,
    period_targets: Dict[str, str] = None
) -> List[Dict[str, Any]]:
    """
    Generate periods based on the period type and date range.

    Args:
        period_type: Type of period ('weekly', 'monthly', 'quarterly', 'semiannual', 'annual')
        start_date: Start date of the period range
        end_date: End date of the period range
        kpi_id: ID of the KPI (optional)
        period_targets: Optional dictionary of existing period targets (alternative to kpi_id)

    Returns:
        List of period dictionaries with label, start_date, end_date, and target_value
    """
    if kpi_id is not None and period_targets is None:
        period_targets = {
            str(target.period_start): str(target.target_value) if target.target_value else ''
            for target in KPIPeriodTarget.objects.filter(kpi_id=kpi_id)
        }
    elif period_targets is None:
        period_targets = {}

    periods = []
    current = start_date

    if period_type.lower() == 'monthly':
        current = start_date.replace(day=1)
        while current <= end_date:
            # Calculate last day of current month
            if current.month == 12:
                next_month = current.replace(
                    year=current.year + 1, month=1, day=1)
            else:
                next_month = current.replace(month=current.month + 1, day=1)
            period_end = next_month - datetime.timedelta(days=1)

            if period_end > end_date:
                period_end = end_date

            period_key = current.strftime('%Y-%m-%d')
            periods.append({
                'label': current.strftime('%b %Y'),
                'start_date': current,
                'end_date': period_end,
                'target_value': period_targets.get(period_key, '')
            })

            current = next_month

    elif period_type.lower() == 'weekly':
        current = monday(start_date)
        while current <= end_date:
            period_end = current + datetime.timedelta(days=6)
            if period_end > end_date:
                period_end = end_date

            iw = iso_week(current)
            period_key = current.strftime('%Y-%m-%d')
            periods.append({
                'label': f"W{iw['week']:02d} {iw['year']}",
                'start_date': current,
                'end_date': period_end,
                'target_value': period_targets.get(period_key, '')
            })

            current += datetime.timedelta(weeks=1)

    elif period_type.lower() == 'quarterly':
        current = start_date.replace(day=1)
        while current <= end_date:
            quarter = (current.month - 1) // 3 + 1
            quarter_start = datetime.date(
                current.year, 3 * (quarter - 1) + 1, 1)

            if quarter == 4:
                quarter_end = datetime.date(current.year, 12, 31)
            else:
                quarter_end = datetime.date(
                    current.year, 3 * quarter + 1, 1) - datetime.timedelta(days=1)

            if quarter_end > end_date:
                quarter_end = end_date

            period_key = quarter_start.strftime('%Y-%m-%d')
            periods.append({
                'label': f"Q{quarter} {quarter_start.year}",
                'start_date': quarter_start,
                'end_date': quarter_end,
                'target_value': period_targets.get(period_key, '')
            })

            current = quarter_end + datetime.timedelta(days=1)

    elif period_type.lower() == 'semiannual':
        current = start_date.replace(day=1)
        while current <= end_date:
            semester = 1 if current.month <= 6 else 2
            semester_start = datetime.date(
                current.year, 6 * (semester - 1) + 1, 1)

            if semester == 1:
                semester_end = datetime.date(current.year, 6, 30)
            else:
                semester_end = datetime.date(current.year, 12, 31)

            if semester_end > end_date:
                semester_end = end_date

            period_key = semester_start.strftime('%Y-%m-%d')
            periods.append({
                'label': f"Semester {semester} {semester_start.year}",
                'start_date': semester_start,
                'end_date': semester_end,
                'target_value': period_targets.get(period_key, '')
            })

            current = semester_end + datetime.timedelta(days=1)

    elif period_type.lower() == 'annual':
        current = start_date.replace(month=1, day=1)
        while current <= end_date:
            year_end = datetime.date(current.year, 12, 31)
            if year_end > end_date:
                year_end = end_date

            period_key = current.strftime('%Y-%m-%d')
            periods.append({
                'label': f"Tahun {current.year}",
                'start_date': current,
                'end_date': year_end,
                'target_value': period_targets.get(period_key, '')
            })

            current = datetime.date(current.year + 1, 1, 1)

    return periods
