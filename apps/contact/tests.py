import time

from django.contrib.auth import get_user_model
from django.core import mail, signing
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import MIN_SUBMIT_SECONDS, TOKEN_SALT
from .models import ContactMessage


def _token(age_seconds=MIN_SUBMIT_SECONDS + 1):
    """A form_token as if the page had been open for `age_seconds` already."""
    return signing.dumps(time.time() - age_seconds, salt=TOKEN_SALT)


VALID = {
    "first_name": "Budi",
    "last_name": "Santoso",
    "email": "budi@contoh.co.id",
    "phone": "0812 3456 7890",
    "subject": "Sewa lowbed",
    "message": "Butuh lowbed 3 unit untuk mobilisasi excavator ke Muara Enim.",
}


class ContactSubmitTests(TestCase):
    def test_valid_post_saves_and_redirects(self):
        resp = self.client.post(reverse("contact:submit"), {**VALID, "form_token": _token()})
        self.assertRedirects(resp, reverse("pages:home") + "?terkirim=1#contact-us",
                             fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.count(), 1)
        row = ContactMessage.objects.get()
        self.assertEqual(row.email, "budi@contoh.co.id")
        self.assertEqual(row.full_name, "Budi Santoso")
        self.assertFalse(row.is_handled)

    @override_settings(CONTACT_EMAIL="ops@subursedayamaju.co.id")
    def test_valid_post_sends_notification_to_configured_and_admin(self):
        self.client.post(reverse("contact:submit"), {**VALID, "form_token": _token()})
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertIn("budi@contoh.co.id", sent.body)
        self.assertIn("ops@subursedayamaju.co.id", sent.to)
        self.assertIn("admin@subursedayamaju.co.id", sent.to)

    @override_settings(CONTACT_EMAIL="")
    def test_notification_still_reaches_admin_when_contact_email_unset(self):
        self.client.post(reverse("contact:submit"), {**VALID, "form_token": _token()})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["admin@subursedayamaju.co.id"])

    def test_honeypot_blocks_save(self):
        resp = self.client.post(reverse("contact:submit"),
                                 {**VALID, "form_token": _token(), "website": "http://spam"})
        self.assertRedirects(resp, reverse("pages:home") + "?galat=1#contact-us",
                             fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_missing_token_blocks_save(self):
        resp = self.client.post(reverse("contact:submit"), VALID)
        self.assertRedirects(resp, reverse("pages:home") + "?galat=1#contact-us",
                             fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_too_fast_submit_blocks_save(self):
        resp = self.client.post(reverse("contact:submit"), {**VALID, "form_token": _token(0)})
        self.assertRedirects(resp, reverse("pages:home") + "?galat=1#contact-us",
                             fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_stale_token_blocks_save(self):
        resp = self.client.post(reverse("contact:submit"), {**VALID, "form_token": _token(7 * 3600)})
        self.assertRedirects(resp, reverse("pages:home") + "?galat=1#contact-us",
                             fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_missing_required_is_rejected(self):
        resp = self.client.post(reverse("contact:submit"), {"email": "x@y.z", "form_token": _token()})
        self.assertRedirects(resp, reverse("pages:home") + "?galat=1#contact-us",
                             fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_get_redirects_home(self):
        resp = self.client.get(reverse("contact:submit"))
        self.assertEqual(resp.status_code, 302)

    def test_rate_limit_blocks_after_max_within_window(self):
        for _ in range(3):
            resp = self.client.post(reverse("contact:submit"), {**VALID, "form_token": _token()})
            self.assertRedirects(resp, reverse("pages:home") + "?terkirim=1#contact-us",
                                 fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.count(), 3)

        resp = self.client.post(reverse("contact:submit"), {**VALID, "form_token": _token()})
        self.assertRedirects(resp, reverse("pages:home") + "?galat=1#contact-us",
                             fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.count(), 3)


class MessageListAccessTests(TestCase):
    def setUp(self):
        ContactMessage.objects.create(email="a@b.co", phone="0812345678", message="halo")

    def test_anonymous_redirected_to_login(self):
        resp = self.client.get(reverse("contact:message_list"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/admin/login/", resp["Location"])

    def test_staff_sees_messages(self):
        get_user_model().objects.create_user("adminssm", password="ssmadmin", is_staff=True)
        self.client.login(username="adminssm", password="ssmadmin")
        resp = self.client.get(reverse("contact:message_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "a@b.co")

    def test_non_staff_denied(self):
        get_user_model().objects.create_user("joe", password="x")
        self.client.login(username="joe", password="x")
        resp = self.client.get(reverse("contact:message_list"))
        self.assertIn(resp.status_code, (302, 403))
