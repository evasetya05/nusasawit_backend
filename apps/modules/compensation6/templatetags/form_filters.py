from django import template, forms

register = template.Library()


@register.filter(name="get_item")
def get_item(obj, key):
    if isinstance(obj, dict):
        return obj.get(key)
    elif isinstance(obj, forms.Form):
        return obj[key]
    return None
