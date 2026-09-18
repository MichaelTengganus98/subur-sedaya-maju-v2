import time

from django import forms
from django.core import signing

from .models import ContactMessage

# Salt for the timing token below - just namespaces the signature, not a secret.
TOKEN_SALT = "contact-form-timing"
# A real visitor takes at least this long to read the form and type into it;
# a bot that fetches the page and immediately POSTs does not.
MIN_SUBMIT_SECONDS = 3
# Beyond this the token is treated as stale (e.g. a page left open overnight)
# and the visitor is asked to resubmit rather than silently accepted.
MAX_TOKEN_AGE_SECONDS = 6 * 3600


def make_form_token():
    """Signed render-time timestamp, embedded as a hidden field by the home page.

    Paired with clean_form_token() below for lightweight, dependency-free
    spam protection: it catches bots that skip loading the page (no valid
    token at all) and bots that submit faster than a human could (token
    younger than MIN_SUBMIT_SECONDS).
    """
    return signing.dumps(time.time(), salt=TOKEN_SALT)


class ContactForm(forms.ModelForm):
    # Honeypot: hidden from real users via CSS (.hp-field). Bots fill it in.
    website = forms.CharField(required=False, widget=forms.HiddenInput)
    # Timing check: see make_form_token()/clean_form_token().
    form_token = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["first_name", "last_name", "email", "phone", "subject", "message"]

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("bot detected")
        return ""

    def clean_form_token(self):
        token = self.cleaned_data.get("form_token")
        try:
            # Age is judged against the rendered_at payload, not signing's own
            # signature timestamp, so it reflects exactly when the page that
            # produced this token was rendered.
            rendered_at = signing.loads(token, salt=TOKEN_SALT)
        except (signing.BadSignature, TypeError, ValueError):
            raise forms.ValidationError("bot detected")
        age = time.time() - rendered_at
        if age < MIN_SUBMIT_SECONDS or age > MAX_TOKEN_AGE_SECONDS:
            raise forms.ValidationError("bot detected")
        return token

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        digits = sum(c.isdigit() for c in phone)
        if digits < 7:
            raise forms.ValidationError("Nomor telepon tidak valid.")
        return phone
