"""Idempotently create/refresh the admin (staff superuser) from env vars.

    DJANGO_SUPERUSER_USERNAME   (default: adminssm)
    DJANGO_SUPERUSER_PASSWORD   (required)
    DJANGO_SUPERUSER_EMAIL      (optional)

Safe to run repeatedly (used by scripts/dev.sh `ssm_admin`). On a non-DEBUG
site it refuses the well-known dev password so a live box never ends up with it.
"""
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

DEV_DEFAULT_PASSWORD = "ssmadmin"


class Command(BaseCommand):
    help = "Create or update the admin superuser from DJANGO_SUPERUSER_* env vars."

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "adminssm")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

        if not password:
            raise CommandError("DJANGO_SUPERUSER_PASSWORD is not set.")
        if not settings.DEBUG and password == DEV_DEFAULT_PASSWORD:
            raise CommandError(
                "Refusing to set the well-known dev password on a non-DEBUG site. "
                "Set DJANGO_SUPERUSER_PASSWORD to a strong value."
            )

        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email}
        )
        if email:
            user.email = email
        user.is_staff = user.is_superuser = user.is_active = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(
            f"{'Created' if created else 'Updated'} superuser '{username}'."
        ))
