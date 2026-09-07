# Deployment — Current Static Site

The live site is plain static files on cPanel shared hosting.

## What's deployed

- `index.html`, `assets/css/style.css`, `assets/js/main.js`, `assets/images/*`
- Nothing else — no `invoice/`, no `docs/`, no `.git/`.

## How it's served

- Files live under the cPanel account's `public_html/` (document root for `subursedayamaju.co.id`).
- Apache serves `index.html` as the directory index.
- HTTPS via cPanel's AutoSSL (Let's Encrypt).
- No `.htaccess` currently in the repo. If one exists on the server it is not tracked here.

## Updating the current site

1. Edit files locally on `main`.
2. Upload the changed files via cPanel **File Manager** or SFTP into `public_html/`.
3. Hard-refresh to bypass browser cache (there is no cache-busting on the CSS/JS `<link>`/`<script>` tags).

## Notes for the revamp

The Django revamp will **not** be served from `public_html` as static files. cPanel
runs Python apps through Passenger with a separate application root and a
`public_html` (or subdomain docroot) that only holds static assets and the
Passenger entrypoint. See `REVAMP-DJANGO-CPANEL.md` on the `revamp/django-cpanel`
branch.
