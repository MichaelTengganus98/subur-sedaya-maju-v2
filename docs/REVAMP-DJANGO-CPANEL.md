# Revamp Plan — Django on cPanel

Branch: `revamp/django-cpanel`

Goal: rebuild the current single-file static site as a small Django project that
can be deployed on the existing cPanel shared hosting using cPanel's
**Setup Python App** (Passenger / WSGI), while keeping the same look, content, and
Indonesian copy.

This document is the plan. The Django scaffold (project skeleton + home page
ported from `index.html`) is now committed on this branch — see §10 for how to
run it locally.

**Python target: 3.8** (the version available in the client's cPanel), which
pins the stack to **Django 4.2 LTS** — the last Django series that supports
Python 3.8 (security support until April 2026). Move to Django 5.x only after
cPanel's Python is upgraded to 3.10+.

---

## 1. Why Django (and when it's overkill)

The current site is one static page. Django is worth it here only if we want at
least one of:

- **A working contact form** that emails the company (server-side send + spam
  protection) instead of relying on the visitor's `mailto:` client.
- **Editable content** (fleet list, testimonials, certifications, FAQ, coverage
  areas) via the Django admin, so the client updates them without touching HTML.
- **Templating** — shared header/footer/partials, and room to grow to multiple
  pages (per-service pages, blog/news, careers).

If none of those are wanted, a static-site generator or just cleaning up the
existing HTML is the lighter option. The rest of this plan assumes we want the
contact form + admin-editable content.

## 2. Target architecture

```
config/                 # Django project (settings, urls, wsgi)
  settings/
    base.py
    production.py        # reads from environment / .env
    development.py
  urls.py
  wsgi.py
apps/
  pages/                 # home page view + static-ish sections
  content/               # models: FleetUnit, Testimonial, Certification,
                         #         FaqItem, CoverageArea, ServiceItem
  contact/               # ContactMessage model + form + email send
templates/
  base.html              # <head>, header, footer, WhatsApp FAB
  pages/home.html        # the long single page, built from section partials
  partials/_*.html       # hero, services, stats, why-us, process, about,
                         # vision, fleet, partners, testimonials, certs,
                         # coverage, faq, cta, contact, location, footer
static/
  css/style.css          # ported from assets/css/style.css (unchanged)
  js/main.js             # ported from assets/js/main.js (form posts to Django)
  images/                # ported from assets/images/
manage.py
requirements.txt
passenger_wsgi.py        # cPanel Passenger entrypoint
.env.example
```

Keep the existing `assets/` files as the styling/JS source — port them verbatim
into `static/` first, get the page pixel-identical, then change things.

## 3. Data models (initial)

| Model | Fields (first pass) |
|---|---|
| `ServiceItem` | title, slug, short_description, icon (choice or svg name), order |
| `FleetUnit` | name, type, capacity, specs (text), photo (ImageField), order, is_published |
| `Testimonial` | quote, client_name, client_role, company, photo (optional), order, is_published |
| `Certification` | name, issuer, logo (ImageField), document (FileField, optional), order |
| `FaqItem` | question, answer (rich text or plain), order, is_published |
| `CoverageArea` | name, order |
| `ContactMessage` | first_name, last_name, email, phone, subject, message, created_at, is_handled, ip (optional) |

`Meta.ordering = ["order"]` everywhere; expose all in the Django admin.
Media (`photo`, `logo`, `document`) → `MEDIA_ROOT` under the app root (see §6).

## 4. Contact form

- Django `Form` / `ModelForm` for `ContactMessage`.
- On POST: validate → save row → send email to `admin@subursedayamaju.co.id`
  (and optional autoreply) → redirect with a success flash (PRG pattern).
- Progressive enhancement: keep it working without JS; `static/js/main.js` can
  still `fetch()`-submit for a nicer UX.
- Spam protection: honeypot field + timestamp check first; add reCAPTCHA/hCaptcha
  only if spam actually shows up.
- Translate the field labels to Indonesian (see `CONTENT-TODO.md`).

### Email on cPanel
- Create a mailbox / use an existing one in cPanel (e.g. `no-reply@subursedayamaju.co.id`).
- SMTP settings in `production.py` from env:
  ```
  EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
  EMAIL_HOST = "mail.subursedayamaju.co.id"   # or the server hostname cPanel gives
  EMAIL_PORT = 465
  EMAIL_USE_SSL = True
  EMAIL_HOST_USER = "<from env>"
  EMAIL_HOST_PASSWORD = "<from env>"
  DEFAULT_FROM_EMAIL = "PT Subur Sedaya Maju <no-reply@subursedayamaju.co.id>"
  ```

## 5. Dependencies (`requirements.txt`)

Current, as committed (Python 3.8 → Django 4.2 LTS):

```
Django>=4.2,<4.3
python-dotenv>=1.0,<2.0
whitenoise>=6.6,<7.0
Pillow>=10.0,<10.5      # last Pillow series with cp38 wheels
```

Not included yet, add when the matching feature lands:
`dj-database-url` + `mysqlclient` (only if we move off SQLite).

Database: **SQLite** is fine for this traffic level and simplest on shared
hosting. If cPanel offers MySQL and the client prefers it, switch via
`dj-database-url` + `mysqlclient`.

Static files: **WhiteNoise** so we don't fight Passenger over static routing.
Run `collectstatic` on deploy; WhiteNoise serves `/static/` from `STATIC_ROOT`.

## 6. cPanel deployment (Setup Python App / Passenger)

Assumes cPanel with "Setup Python App" available. This project is built for
**Python 3.8**; if cPanel offers a newer 3.x it will still run (bump Django
afterwards).

### One-time setup
1. **cPanel → Setup Python App → Create Application**
   - Python version: 3.8 (or newer if offered).
   - Application root: e.g. `subursedayamaju_app` (NOT inside `public_html`).
   - Application URL: the domain (or a subdomain for staging first).
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`
2. cPanel creates a virtualenv and shows the exact
   `source /home/<user>/virtualenv/.../bin/activate` command — note it.
3. Upload the project into the application root (Git deploy, SFTP, or File
   Manager). Keep `.git/`, `docs/`, `invoice/` out of the server copy.
4. In the app's UI, add the `requirements.txt` file and click **Run Pip Install**
   (or run `pip install -r requirements.txt` in the venv over SSH).
5. Set **Environment variables** in the Python App UI:
   ```
   DJANGO_SETTINGS_MODULE = config.settings.production
   SECRET_KEY = <generate>
   DEBUG = 0
   ALLOWED_HOSTS = subursedayamaju.co.id,www.subursedayamaju.co.id
   DATABASE_URL = sqlite:////home/<user>/subursedayamaju_app/db.sqlite3
   EMAIL_HOST_USER = ...
   EMAIL_HOST_PASSWORD = ...
   ```
6. Over SSH (venv activated), from the app root:
   ```
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```
7. **Restart** the app from the Python App UI (or `touch tmp/restart.txt`).

### `passenger_wsgi.py`
```python
import os
from config.wsgi import application  # noqa

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
```
(If Passenger's Python differs from the venv, cPanel's generated stub also
`exec`s the correct interpreter — keep whatever cPanel scaffolds and just point
it at `config.wsgi`.)

### Static & media
- `STATIC_ROOT = BASE_DIR / "staticfiles"`, served by WhiteNoise.
- `MEDIA_ROOT = BASE_DIR / "media"`; either serve via a lightweight Django view
  behind auth-free URLs, or symlink `public_html/media -> ../subursedayamaju_app/media`
  so Apache serves uploads directly (preferred for performance).
- `.htaccess` in `public_html` is managed by Passenger — don't hand-edit the
  Passenger block.

### Deploy updates
```
git pull            # or re-upload changed files
pip install -r requirements.txt   # if changed
python manage.py migrate          # if migrations
python manage.py optimize_images  # only if a source photo changed (webp is committed)
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

SEO-related env vars to set in the Python App UI (all optional, see `SEO.md`):
`CANONICAL_HOST`, and `GA4_MEASUREMENT_ID` / `PLAUSIBLE_DOMAIN` when analytics
is approved.

## 7. Settings essentials for shared hosting

```python
DEBUG = env.bool("DEBUG", False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = ["https://subursedayamaju.co.id", "https://www.subursedayamaju.co.id"]
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600  # raise after verifying
STORAGES = {  # Django 4.2+ dict-style storages
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
```

(All of the above is already implemented in `config/settings/production.py`.)

Add structured data (JSON-LD `LocalBusiness` / `MovingCompany`), `sitemap.xml`
(`django.contrib.sitemaps`), and `robots.txt` while we're rebuilding — all listed
as gaps in `SITE-OVERVIEW.md` §8.

## 8. Migration steps (commit order on this branch)

1. ✅ Scaffold Django project + `config/settings/{base,development,production}.py`,
   `passenger_wsgi.py`, `requirements.txt`, `.env.example`, WhiteNoise.
2. ✅ Port `assets/` → `static/`; `base.html` + `pages/home.html` render the page.
   Then re-skinned to the industrial redesign — new `static/css/style.css`, Archivo
   / IBM Plex fonts, all sections kept, real photos in restyled frames. Design
   system documented in `DESIGN-SYSTEM.md`. Reference: `design/subursedayamaju-redesign.html`.
3. ⬜ Split `home.html` into `partials/_*.html` section includes.
4. ✅ `contact` app: `ContactMessage` model, `ContactForm` (honeypot + phone
   check), `/kirim-pesan/` POST (PRG, saves + emails `CONTACT_EMAIL`),
   `/message/` staff list, Django admin registration, tests. `main.js` no longer
   does the `mailto:` hijack — the form is a native POST with `{% csrf_token %}`.
   Admin login is created by `manage.py ensure_admin` /
   `scripts/dev.sh ssm_admin` (dev default `adminssm` / `ssmadmin`; set a strong
   `SSM_ADMIN_PASS` on the server — `ensure_admin` refuses the default when
   `DEBUG` is off).
5. ⬜ `content` app: models + admin + template loops; migrate existing hard-coded
   copy into fixtures/data migration.
6. 🔶 SEO: JSON-LD (`WebSite` + `MovingCompany`/`LocalBusiness` + `FAQPage`),
   `sitemap.xml`, `robots.txt`, OG/Twitter/geo meta, heading hierarchy — done.
   Remaining: exact geo coords, `sameAs`, GSC/GBP, analytics, per-service pages.
   See `SEO.md`.
7. ⬜ Deploy to a **staging subdomain** on cPanel, verify, then cut over the main domain.
8. ⬜ Keep `main` (static site) as the rollback target until the Django site is verified live.

## 9. Open questions for the client

- Do they want admin-editable content, or is a clean static rebuild enough?
- Preferred DB: SQLite (simplest) or MySQL (already in cPanel)?
- Which mailbox should the contact form send from / to?
- Confirm cPanel's Python version. Built for 3.8 / Django 4.2; newer is fine.
- Is there SSH access, or File-Manager/Git-only? (decides deploy workflow)
- Staging subdomain available (e.g. `staging.subursedayamaju.co.id`)?

## 10. Run locally

Requires Python 3.8 on PATH as `python3.8` (or set `SSM_PYTHON`). From the branch
checkout, the `scripts/dev.sh` helpers do everything:

```bash
source scripts/dev.sh

ssm_install     # create .venv (once) + pip install -r requirements.txt
ssm_sync        # manage.py migrate + collectstatic
ssm_admin       # create the admin login (dev: adminssm / ssmadmin)
ssm_run         # runserver on 127.0.0.1:8000
# ssm_bootstrap  == install + sync + admin in one go
# ssm_check      == manage.py check + test
```

- `http://127.0.0.1:8000/`         home page
- `http://127.0.0.1:8000/admin/`   Django admin (contact messages, users)
- `http://127.0.0.1:8000/message/` staff-only list of contact-form submissions
- `http://127.0.0.1:8000/seo/`     on-page SEO health check (DEBUG/staff only)

Doing it by hand instead:

```bash
python3.8 -m venv .venv && source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
DJANGO_SUPERUSER_USERNAME=adminssm DJANGO_SUPERUSER_PASSWORD=ssmadmin \
  python manage.py ensure_admin        # or: python manage.py createsuperuser
python manage.py runserver
```

`.venv/`, `db.sqlite3`, and `staticfiles/` are git-ignored.

**Admin password:** `ssmadmin` is a local-only convenience. On the server export a
strong `SSM_ADMIN_PASS` (or `DJANGO_SUPERUSER_PASSWORD`) before running
`ensure_admin` — it refuses the dev default when `DEBUG` is off.

Production dry-run (uses `config.settings.production`, needs a `SECRET_KEY`):

```bash
SECRET_KEY=xxx ALLOWED_HOSTS=localhost DJANGO_SETTINGS_MODULE=config.settings.production \
  python manage.py collectstatic --noinput
SECRET_KEY=xxx ALLOWED_HOSTS=localhost DJANGO_SETTINGS_MODULE=config.settings.production \
  python manage.py check --deploy
```
