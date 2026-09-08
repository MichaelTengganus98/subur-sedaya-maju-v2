import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from .forms import ContactForm
from .models import ContactMessage

log = logging.getLogger(__name__)


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or None


class ContactSubmitView(View):
    """Handles POST from the home-page contact form (PRG pattern)."""

    home = "pages:home"

    def get(self, request):
        return redirect(reverse(self.home) + "#contact-us")

    def post(self, request):
        form = ContactForm(request.POST)
        if not form.is_valid():
            log.info("contact form rejected: %s", form.errors.as_json())
            return redirect(reverse(self.home) + "?galat=1#contact-us")

        msg = form.save(commit=False)
        msg.ip_address = _client_ip(request)
        msg.user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]
        msg.save()
        self._notify(msg)
        messages.success(request, "Pesan Anda sudah kami terima.")
        return redirect(reverse(self.home) + "?terkirim=1#contact-us")

    def _notify(self, msg):
        recipient = getattr(settings, "CONTACT_EMAIL", "")
        if not recipient:
            return
        body = (
            f"Nama    : {msg.full_name or '-'}\n"
            f"Email   : {msg.email}\n"
            f"Telepon : {msg.phone}\n"
            f"Subjek  : {msg.subject or '-'}\n"
            f"Diterima: {msg.created_at:%Y-%m-%d %H:%M}\n\n"
            f"{msg.message}\n"
        )
        try:
            send_mail(
                f"[Website] Pesan baru dari {msg.full_name or msg.email}",
                body,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=True,
            )
        except Exception:  # pragma: no cover - never break the save on mail issues
            log.exception("contact notification email failed")


class MessageListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Read-only list of contact messages for staff, at /message/."""

    model = ContactMessage
    template_name = "contact/message_list.html"
    context_object_name = "rows"
    paginate_by = 50
    login_url = "/admin/login/"
    raise_exception = False

    def test_func(self):
        return self.request.user.is_staff
