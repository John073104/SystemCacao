from django import template

register = template.Library()

@register.filter
def replace(value, args):
    """Replaces all instances of `old` with `new` in the string."""
    old, new = args.split(':')
    return value.replace(old, new)
