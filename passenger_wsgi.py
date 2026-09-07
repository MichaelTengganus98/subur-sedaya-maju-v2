"""
Passenger entrypoint for cPanel's "Setup Python App".

cPanel points the app's "startup file" at this module and its "entry point" at
`application`. Keep DJANGO_SETTINGS_MODULE on the production settings here; set
SECRET_KEY, ALLOWED_HOSTS, DEBUG, email creds, etc. as environment variables in
the Python App UI (or a .env file in the app root).
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

from config.wsgi import application  # noqa: E402,F401
