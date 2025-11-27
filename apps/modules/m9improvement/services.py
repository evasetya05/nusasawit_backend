from django.db.models import Avg
from .models import OcaiAnswer, OcaiQuestion


def get_continues_improvement_data(company, period_year=None, period_half=None):
    """
    Process and return data for the continues improvement dashboard.

    Args:
        company: The company to get data for
        period_year (int|None): filter by year if provided
        period_half (int|None): filter by half (1=H1, 2=H2) if provided

    Returns:
        tuple: (grouped_data, overall_averages)
            - grouped_data: Data grouped by department
            - overall_averages: Aggregated data across all departments
    """
    qs = OcaiAnswer.objects.filter(employee__company=company)
    if period_year is not None:
        qs = qs.filter(period_year=period_year)
    if period_half is not None:
        qs = qs.filter(period_half=period_half)

    avg_data = qs.values(
        'employee__department', 'question__category'
    ).annotate(
        avg_current=Avg('current'),
        avg_expected=Avg('expected')
    )

    grouped_data = {}
    overall_averages = {'categories': {},
                       'sum_avg_current': 0, 'sum_avg_expected': 0}

    for entry in avg_data:
        # Handle None values
        departemen = entry['employee__department'] or "Unknown"
        category = entry['question__category']
        avg_current = int(
            round(entry['avg_current'] if entry['avg_current'] is not None else 0))
        avg_expected = int(
            round(entry['avg_expected'] if entry['avg_expected'] is not None else 0))

        # Group by department
        if departemen not in grouped_data:
            grouped_data[departemen] = {
                'categories': {}, 'sum_avg_current': 0, 'sum_avg_expected': 0}

        grouped_data[departemen]['categories'][category] = {
            'avg_current': avg_current,
            'avg_expected': avg_expected,
        }

        grouped_data[departemen]['sum_avg_current'] += avg_current
        grouped_data[departemen]['sum_avg_expected'] += avg_expected

        # Calculate overall averages
        if category not in overall_averages['categories']:
            overall_averages['categories'][category] = {
                'total_current': 0, 'total_expected': 0, 'count': 0}

        overall_averages['categories'][category]['total_current'] += avg_current
        overall_averages['categories'][category]['total_expected'] += avg_expected
        overall_averages['categories'][category]['count'] += 1

    # Calculate final averages for all departments
    for category, values in overall_averages['categories'].items():
        if values['count'] > 0:
            avg_current = int(round(values['total_current'] / values['count']))
            avg_expected = int(
                round(values['total_expected'] / values['count']))
        else:
            avg_current = 0
            avg_expected = 0

        overall_averages['categories'][category] = {
            'avg_current': avg_current,
            'avg_expected': avg_expected,
        }

        overall_averages['sum_avg_current'] += avg_current
        overall_averages['sum_avg_expected'] += avg_expected

    return grouped_data, overall_averages


def save_ocai_answers(form_data, employee, period_year, period_half):
    questions = OcaiQuestion.objects.all()
    for question in questions:
        current_score = form_data.get(f'current_score_{question.id}')
        expected_score = form_data.get(f'expected_score_{question.id}')

        if current_score is not None and expected_score is not None:
            # ensure one record per period per question
            OcaiAnswer.objects.update_or_create(
                employee=employee,
                question=question,
                period_year=period_year,
                period_half=period_half,
                defaults={
                    'current': current_score,
                    'expected': expected_score,
                }
            )
