from django.conf import settings


def site(request):
    """Expose a few settings to every template (SEO identity + analytics ids)."""
    return {
        "SITE_NAME": settings.SITE_NAME,
        "CONTACT_EMAIL": settings.CONTACT_EMAIL,
        "CONTACT_PHONE": settings.CONTACT_PHONE,
        "CONTACT_WHATSAPP": settings.CONTACT_WHATSAPP,
        "CANONICAL_HOST": settings.CANONICAL_HOST,
        "GA4_MEASUREMENT_ID": settings.GA4_MEASUREMENT_ID,
        "PLAUSIBLE_DOMAIN": settings.PLAUSIBLE_DOMAIN,
    }
