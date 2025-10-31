"""
Deprecated placeholder for template tags.

Historically, this file accidentally contained application view functions which
caused duplication and conflicts with mainapp.views, resulting in errors and
"red dots" in editors.

All application views must live in `mainapp.views`.

This module intentionally exposes an empty template tag library to preserve
compatibility in case `{% load views %}` is referenced in templates.
"""
from django import template

register = template.Library()

@register.filter(name="noop")
def noop(value):
    """No-op filter for compatibility."""
    return value
