from django.db import models


class ContactMessage(models.Model):
    """One submission of the home-page contact form."""

    first_name = models.CharField("Nama depan", max_length=80, blank=True)
    last_name = models.CharField("Nama belakang", max_length=80, blank=True)
    email = models.EmailField("Email")
    phone = models.CharField("Telepon", max_length=40)
    subject = models.CharField("Subjek", max_length=160, blank=True)
    message = models.TextField("Pesan")

    created_at = models.DateTimeField("Diterima", auto_now_add=True)
    is_handled = models.BooleanField("Sudah ditangani", default=False)
    ip_address = models.GenericIPAddressField("Alamat IP", null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pesan kontak"
        verbose_name_plural = "Pesan kontak"

    def __str__(self):
        return f"{self.full_name or self.email} — {self.created_at:%Y-%m-%d %H:%M}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
