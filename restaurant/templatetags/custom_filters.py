from django import template

register = template.Library()


@register.filter
def vnd_format(value):
    """
    Format number with thousand separators for VND currency
    Example: 350000 -> 350.000
    """
    try:
        # Convert to integer (remove decimals)
        value = int(float(value))
        # Format with dots as thousand separators
        return "{:,}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value
