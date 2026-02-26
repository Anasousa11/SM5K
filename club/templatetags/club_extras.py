from django import template

register = template.Library()

@register.filter
def has_attr(obj, attr_name):
    """Return True if *obj* has attribute *attr_name* without raising.

    This can be used in templates to safely test for related objects
    (e.g. ``user|has_attr:'client_profile'``) without triggering a
    RelatedObjectDoesNotExist exception.
    """
    try:
        return hasattr(obj, attr_name)
    except Exception:
        return False
