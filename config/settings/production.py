"""Production settings (cPanel / Passenger)."""
from .base import *  # noqa: F401,F403
from .base import env, env_bool, env_list

DEBUG = env_bool("DEBUG", False)

ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    ["subursedayamaju.co.id", "www.subursedayamaju.co.id"],
)
CSRF_TRUSTED_ORIGINS = [
    "https://subursedayamaju.co.id",
    "https://www.subursedayamaju.co.id",
]

# Behind cPanel's Apache/Passenger proxy terminating TLS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", "3600"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"

if not env("SECRET_KEY"):
    raise RuntimeError("SECRET_KEY environment variable must be set in production.")

# Real SMTP by default in production; override via env for a mailbox on cPanel.
EMAIL_BACKEND = env("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
