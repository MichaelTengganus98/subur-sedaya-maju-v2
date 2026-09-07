from django import template

register = template.Library()


@register.filter
def to_webp(path):
    """'images/foo.png' -> 'images/foo.webp' (used to point <source> at the
    WebP sibling produced by `manage.py optimize_images`)."""
    base, sep, _ext = path.rpartition(".")
    return (base + ".webp") if sep else (path + ".webp")
