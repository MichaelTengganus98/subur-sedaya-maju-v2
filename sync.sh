#!/usr/bin/env bash
#
# One-shot: bring this checkout up to date and ready to serve.
# Safe to run for the first-time setup AND after every `git pull`.
#
#   bash sync.sh
#
# Steps:
#   1. create/reuse a virtualenv, install/upgrade requirements.txt
#   2. run database migrations
#   3. collect static files
#   4. create/refresh the admin login (see "Admin login" below)
#   5. on a Passenger/cPanel deploy, touch tmp/restart.txt
#
# Optional env vars:
#   SSM_PYTHON        interpreter to build the venv   (default: python3.8 -> python3 -> python)
#   SSM_VENV          virtualenv path                 (default: ./.venv, or $VIRTUAL_ENV if active)
#   SSM_PIP_UPGRADE=0 install only what's missing instead of upgrading
#   DJANGO_SUPERUSER_PASSWORD / DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_EMAIL
#   SSM_ADMIN_PASS    alias for DJANGO_SUPERUSER_PASSWORD
#
# On the SERVER, first `source` the app's virtualenv activate script and make sure
# DJANGO_SETTINGS_MODULE=config.settings.production (and SECRET_KEY, DB, EMAIL_*,
# CANONICAL_HOST ...) are exported - cPanel's "Setup Python App" does this from the
# app's Environment Variables. Then run `bash sync.sh`.
#
# Admin login: on a DEBUG (local) checkout it is created as adminssm / ssmadmin
# automatically. On a production box nothing is created unless you pass a
# password, and `ensure_admin` refuses the weak default there.

set -euo pipefail
cd "$(dirname "$0")"

say() { printf '\n\033[1m== %s ==\033[0m\n' "$*"; }

# --- locate / build the virtualenv ---------------------------------------
if [ -n "${VIRTUAL_ENV:-}" ] && [ -z "${SSM_VENV:-}" ]; then
  SSM_VENV="$VIRTUAL_ENV"
fi
SSM_VENV="${SSM_VENV:-$PWD/.venv}"

venv_py() {
  if   [ -x "$SSM_VENV/bin/python" ];         then echo "$SSM_VENV/bin/python"
  elif [ -x "$SSM_VENV/Scripts/python.exe" ]; then echo "$SSM_VENV/Scripts/python.exe"
  else return 1; fi
}

say "1/5  virtualenv + dependencies"
if ! venv_py >/dev/null 2>&1; then
  bootstrap=""
  for cand in "${SSM_PYTHON:-}" python3.8 python3 python; do
    [ -n "$cand" ] || continue
    command -v "$cand" >/dev/null 2>&1 && { bootstrap="$cand"; break; }
  done
  [ -n "$bootstrap" ] || { echo "no python interpreter found - set SSM_PYTHON"; exit 1; }
  echo "creating venv at $SSM_VENV using $bootstrap"
  "$bootstrap" -m venv "$SSM_VENV"
fi
PY="$(venv_py)"
echo "python: $("$PY" --version 2>&1)  ($PY)"

"$PY" -m pip install --upgrade pip wheel
if [ "${SSM_PIP_UPGRADE:-1}" = "1" ]; then
  "$PY" -m pip install --upgrade -r requirements.txt
else
  "$PY" -m pip install -r requirements.txt
fi

# --- is this a DEBUG (dev) checkout? -----------------------------------
if "$PY" - <<'PYEOF' >/dev/null 2>&1
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()
from django.conf import settings
raise SystemExit(0 if settings.DEBUG else 1)
PYEOF
then IS_DEBUG=1; else IS_DEBUG=0; fi

say "2/5  database migrations"
"$PY" manage.py migrate --noinput

say "3/5  static files"
"$PY" manage.py collectstatic --noinput

say "4/5  admin login"
: "${DJANGO_SUPERUSER_PASSWORD:=${SSM_ADMIN_PASS:-}}"
export DJANGO_SUPERUSER_PASSWORD
export DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-adminssm}"
export DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@subursedayamaju.co.id}"
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  "$PY" manage.py ensure_admin
elif [ "$IS_DEBUG" = "1" ]; then
  DJANGO_SUPERUSER_PASSWORD=ssmadmin "$PY" manage.py ensure_admin
  echo "  dev default: adminssm / ssmadmin  (set DJANGO_SUPERUSER_PASSWORD to override)"
else
  echo "  skipped - set DJANGO_SUPERUSER_PASSWORD (or SSM_ADMIN_PASS) to (re)create the admin"
fi

say "5/5  restart"
if [ "$IS_DEBUG" = "1" ]; then
  echo "  dev checkout - start the server with:  \"$PY\" manage.py runserver"
elif [ -f passenger_wsgi.py ]; then
  mkdir -p tmp && touch tmp/restart.txt
  echo "  touched tmp/restart.txt - Passenger will reload the app"
else
  echo "  no passenger_wsgi.py here; restart your app server manually"
fi

echo
echo "OK: sync complete"
