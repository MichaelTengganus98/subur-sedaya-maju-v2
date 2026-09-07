# Revamp Plan — Django on cPanel

Branch: `revamp/django-cpanel`

Goal: rebuild the current single-file static site as a small Django project that
can be deployed on the existing cPanel shared hosting using cPanel's
**Setup Python App** (Passenger / WSGI), while keeping the same look, content, and
Indonesian copy.

This document is the plan. Code lands in later commits on this branch.

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

## 5. Dependencies (`requirements.txt`, first pass)

```
Django>=5.0,<5.3
gunicorn            # local prod-like runs only; cPanel uses Passenger
python-dotenv       # load .env
whitenoise          # serve static files from the WSGI app
Pillow              # ImageField
dj-database-url     # optional, if we move off sqlite
```

Database: **SQLite** is fine for this traffic level and simplest on shared
hosting. If cPanel offers MySQL and the client prefers it, switch via
`dj-database-url` + `mysqlclient`.

Static files: **WhiteNoise** so we don't fight Passenger over static routing.
Run `collectstatic` on deploy; WhiteNoise serves `/static/` from `STATIC_ROOT`.

## 6. cPanel deployment (Setup Python App / Passenger)

Assumes cPanel with "Setup Python App" available (Python 3.8+; check the version).

### One-time setup
1. **cPanel → Setup Python App → Create Application**
   - Python version: newest available (3.10+ preferred).
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
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

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
STORAGES = {  # Django 5 style
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
```

Add structured data (JSON-LD `LocalBusiness` / `MovingCompany`), `sitemap.xml`
(`django.contrib.sitemaps`), and `robots.txt` while we're rebuilding — all listed
as gaps in `SITE-OVERVIEW.md` §8.

## 8. Migration steps (suggested commit order on this branch)

1. Scaffold Django project + `config/settings/{base,development,production}.py`.
2. Port `assets/` → `static/`; build `base.html` + section partials; home view
   renders the page **pixel-identical** to `index.html`.
3. Add `passenger_wsgi.py`, `requirements.txt`, `.env.example`, WhiteNoise.
4. `contact` app: model + form + email send + tests. Wire `static/js/main.js` to POST.
5. `content` app: models + admin + template loops; migrate existing hard-coded
   copy into fixtures/data migration.
6. SEO: JSON-LD, sitemap, robots, meta review.
7. Deploy to a **staging subdomain** on cPanel, verify, then cut over the main domain.
8. Keep `main` (static site) as the rollback target until the Django site is verified live.

## 9. Open questions for the client

- Do they want admin-editable content, or is a clean static rebuild enough?
- Preferred DB: SQLite (simplest) or MySQL (already in cPanel)?
- Which mailbox should the contact form send from / to?
- Python version available in their cPanel? (decides Django version)
- Is there SSH access, or File-Manager/Git-only? (decides deploy workflow)
- Staging subdomain available (e.g. `staging.subursedayamaju.co.id`)?
