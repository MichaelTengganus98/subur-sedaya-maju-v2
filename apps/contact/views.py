import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from .forms import ContactForm
from .models import ContactMessage

log = logging.getLogger(__name__)

# Always notified in addition to settings.CONTACT_EMAIL, so a blank/misconfigured
# CONTACT_EMAIL env var can never fully silence contact notifications.
ADMIN_FALLBACK_EMAIL = "admin@subursedayamaju.co.id"

# Per-IP flood guard, on top of the honeypot + timing checks in ContactForm.
RATE_LIMIT_WINDOW = timedelta(minutes=10)
RATE_LIMIT_MAX = 3


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

        ip = _client_ip(request)
        if ip and self._rate_limited(ip):
            log.info("contact form rate-limited: %s", ip)
            return redirect(reverse(self.home) + "?galat=1#contact-us")

        msg = form.save(commit=False)
        msg.ip_address = ip
        msg.user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]
        msg.save()
        self._notify(msg)
        messages.success(request, "Pesan Anda sudah kami terima.")
        return redirect(reverse(self.home) + "?terkirim=1#contact-us")

    def _rate_limited(self, ip):
        window_start = timezone.now() - RATE_LIMIT_WINDOW
        recent = ContactMessage.objects.filter(ip_address=ip, created_at__gte=window_start)
        return recent.count() >= RATE_LIMIT_MAX

    def _notify(self, msg):
        recipients = []
        for addr in (getattr(settings, "CONTACT_EMAIL", ""), ADMIN_FALLBACK_EMAIL):
            addr = (addr or "").strip()
            if addr and addr.lower() not in (seen.lower() for seen in recipients):
                recipients.append(addr)
        if not recipients:
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
                recipients,
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
