"""Local development settings."""
from .base import *  # noqa: F401,F403
from .base import env_list

DEBUG = True
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["localhost", "127.0.0.1", "0.0.0.0"])

# Print emails to the console instead of sending them.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Serve static files straight from STATICFILES_DIRS without a manifest,
# so `runserver` works without running collectstatic first.
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}
