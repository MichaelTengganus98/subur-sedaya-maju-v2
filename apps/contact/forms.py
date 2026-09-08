from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot: hidden from real users via CSS (.hp-field). Bots fill it in.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["first_name", "last_name", "email", "phone", "subject", "message"]

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("bot detected")
        return ""

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        digits = sum(c.isdigit() for c in phone)
        if digits < 7:
            raise forms.ValidationError("Nomor telepon tidak valid.")
        return phone
