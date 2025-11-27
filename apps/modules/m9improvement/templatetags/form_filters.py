from django import template, forms

register = template.Library()


@register.filter(name="get_item")
def get_item(obj, key):
    if isinstance(obj, dict):
        return obj.get(key)
    elif isinstance(obj, forms.Form):
        return obj[key]
    else:
        return None


@register.filter
def concat(value, arg):
    return f"{value}{arg}"
