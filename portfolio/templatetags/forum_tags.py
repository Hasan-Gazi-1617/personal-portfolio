from django import template

register = template.Library()


@register.filter
def first_word(value):
    """Return the first word of a student's display name."""
    return str(value or "").strip().split(maxsplit=1)[0] if str(value or "").strip() else ""
