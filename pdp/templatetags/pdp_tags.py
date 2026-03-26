from decimal import Decimal

from django import template


register = template.Library()


@register.filter
def get_item(mapping, key):
    if isinstance(mapping, dict):
        return mapping.get(key)
    return ""


@register.filter
def split_lines(value):
    return [line.strip() for line in (value or "").splitlines() if line.strip()]


@register.filter
def trend_class(value):
    if value in (None, "", Decimal("0"), 0):
        return "flat"
    return "up" if value > 0 else "down"


@register.filter
def format_delta(value):
    if value in (None, ""):
        return "No prior value"
    prefix = "+" if value > 0 else ""
    return f"{prefix}{value}"
