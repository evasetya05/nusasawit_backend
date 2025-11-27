from django import template

register = template.Library()


@register.filter
def lcr_badge_class(lcr_percentage):
    """
    Return the appropriate Bootstrap badge class based on LCR percentage.

    Args:
        lcr_percentage: The LCR percentage value

    Returns:
        String: Bootstrap badge class name
    """
    try:
        lcr = float(lcr_percentage)
        if lcr < 20:
            return 'bg-warning'
        elif lcr <= 60:
            return 'bg-success'
        elif lcr <= 80:
            return 'bg-warning'
        else:
            return 'bg-danger'
    except (ValueError, TypeError):
        return 'bg-secondary'


@register.filter
def lcr_row_class(lcr_percentage):
    """
    Return the appropriate Bootstrap table row class based on LCR percentage.

    Args:
        lcr_percentage: The LCR percentage value

    Returns:
        String: Bootstrap table row class name
    """
    try:
        lcr = float(lcr_percentage)
        if lcr < 20:
            return 'table-warning'
        elif lcr <= 60:
            return 'table-success'
        elif lcr <= 80:
            return 'table-warning'
        else:
            return 'table-danger'
    except (ValueError, TypeError):
        return 'table-light'
