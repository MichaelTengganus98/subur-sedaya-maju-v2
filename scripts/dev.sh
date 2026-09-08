# PT Subur Sedaya Maju - developer shell helpers (bash).
#
#   source scripts/dev.sh
#
# then use:
#   ssm_install   create the virtualenv (once) and install requirements.txt
#   ssm_sync      run migrations + collectstatic
#   ssm_admin     create/refresh the Django admin login (idempotent)
#   ssm_run [addr]        run the dev server (default 127.0.0.1:8000)
#   ssm_check     manage.py check + full test suite
#   ssm_shell     Django shell
#
# Config via env vars (all optional):
#   SSM_PYTHON     interpreter used to build the venv        (default: python3.8)
#   SSM_VENV       venv location                             (default: <repo>/.venv)
#   SSM_ADMIN_USER / SSM_ADMIN_PASS / SSM_ADMIN_EMAIL        (ssm_admin defaults:
#                  adminssm / ssmadmin / admin@subursedayamaju.co.id)
#
# NOTE: 'ssmadmin' is a throwaway LOCAL password. On the server, export a strong
#       SSM_ADMIN_PASS before running ssm_admin - ensure_admin refuses the
#       default when DEBUG is off.

SSM_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." 2>/dev/null && pwd)"
: "${SSM_PYTHON:=python3.8}"
: "${SSM_VENV:=$SSM_ROOT/.venv}"

_ssm_py() {
  if   [ -x "$SSM_VENV/Scripts/python.exe" ]; then echo "$SSM_VENV/Scripts/python.exe"
  elif [ -x "$SSM_VENV/bin/python" ];         then echo "$SSM_VENV/bin/python"
  else return 1; fi
}

ssm_install() ( set -e
  cd "$SSM_ROOT"
  if ! _ssm_py >/dev/null 2>&1; then
    echo "-> creating virtualenv ($SSM_PYTHON) at $SSM_VENV"
    "$SSM_PYTHON" -m venv "$SSM_VENV"
  fi
  py="$(_ssm_py)"
  "$py" -m pip install --upgrade pip wheel
  "$py" -m pip install -r requirements.txt
  echo "OK: python environment ready ($("$py" --version 2>&1))"
)

ssm_sync() ( set -e
  cd "$SSM_ROOT"
  py="$(_ssm_py)" || { echo "run ssm_install first"; exit 1; }
  "$py" manage.py migrate --noinput
  "$py" manage.py collectstatic --noinput
  echo "OK: database migrated, static files collected"
)

ssm_admin() ( set -e
  cd "$SSM_ROOT"
  py="$(_ssm_py)" || { echo "run ssm_install first"; exit 1; }
  u="${SSM_ADMIN_USER:-adminssm}"
  p="${SSM_ADMIN_PASS:-ssmadmin}"
  e="${SSM_ADMIN_EMAIL:-admin@subursedayamaju.co.id}"
  DJANGO_SUPERUSER_USERNAME="$u" DJANGO_SUPERUSER_PASSWORD="$p" DJANGO_SUPERUSER_EMAIL="$e" \
    "$py" manage.py ensure_admin
  echo "OK: sign in at /admin/  (then /message/ is reachable) as '$u'"
  [ "$p" = "ssmadmin" ] && echo "WARN: default dev password in use - set SSM_ADMIN_PASS on the server"
  true
)

ssm_run()   { cd "$SSM_ROOT" && "$(_ssm_py)" manage.py runserver "${1:-127.0.0.1:8000}"; }
ssm_shell() { cd "$SSM_ROOT" && "$(_ssm_py)" manage.py shell; }
ssm_check() ( set -e
  cd "$SSM_ROOT"
  py="$(_ssm_py)" || { echo "run ssm_install first"; exit 1; }
  "$py" manage.py check
  "$py" manage.py test
)

# One-shot: full local bring-up.
ssm_bootstrap() ( set -e; ssm_install && ssm_sync && ssm_admin
  echo; echo "Done. Start the server with:  ssm_run" )
