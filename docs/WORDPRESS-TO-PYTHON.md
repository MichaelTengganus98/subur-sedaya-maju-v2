# Moving from WordPress to this Python (Django) site

How to retire the current WordPress site and put this Django project in its place
on the same cPanel account, without losing search rankings or breaking links.

> If the live site is actually the old static `index.html` and not WordPress, the
> steps are the same minus the WP export/redirect parts — jump to §5.

---

## 1. Inventory what WordPress is doing

Before touching anything, write down:

- **Every public URL.** Crawl the live site (Screaming Frog free tier, or
  `wget --spider -r -np https://subursedayamaju.co.id`), export the list. Note
  the URL shape: pretty permalinks (`/layanan/pengangkutan-alat-berat/`),
  dated posts (`/2023/07/slug/`), `?p=123`, `/category/...`, `/tag/...`,
  `/wp-content/uploads/...`, feeds (`/feed/`), `/sitemap_index.xml`.
- **Content types in use:** just Pages? Pages + Posts (a blog)? Custom post
  types? A form plugin (Contact Form 7 / WPForms / Fluent Forms)?
- **Plugins that produce front-end behaviour** (SEO plugin sitemaps, redirects,
  caching, galleries, multilingual).
- **Media:** size of `wp-content/uploads`.
- **Analytics / tag manager / Search Console** property type (URL-prefix vs
  Domain) and how it's verified.

## 2. Decide the mapping

| WordPress | This project |
|---|---|
| Home page | `templates/pages/home.html` (already built) |
| "Static" pages (About, Services, Contact) | sections of the one-page site, or new `apps/pages` views + templates + a sitemap entry each |
| Contact Form 7 / WPForms | `apps/contact` — `ContactMessage` model, `/kirim-pesan/` POST, `/message/` + Django admin (already built) |
| Blog / news (Posts) | only if wanted: a small `apps/blog` (`Post` model, list + detail, RSS, sitemap). Export posts to a data migration or fixtures from the WP REST API (`/wp-json/wp/v2/posts?per_page=100`). |
| Yoast/RankMath meta | already handled in `base.html` + `_seo_jsonld.html` |
| WP media library | copy files into `static/images/` (site assets) or `media/` (if they'll be managed in the admin); rewrite `<img>` paths |
| SEO-plugin sitemap | `/sitemap.xml` (django.contrib.sitemaps, already wired) |

Anything with no mapping and no traffic (old tag pages, empty categories, author
archives) → let it 404/410, don't recreate it.

## 3. Preserve URLs and set redirects

For every old URL that won't exist at the same path on the new site, add a
**301 redirect** to the closest new URL (or to `/` as a last resort). Options,
in order of preference:

1. **`django.contrib.redirects`** — add `django.contrib.sites` +
   `django.contrib.redirects` to `INSTALLED_APPS`, the redirects middleware,
   run migrations, then load a CSV of `old_path,new_path` via a data migration or
   the admin. Central, editable, no server config.
2. **Passenger/`.htaccess`** `Redirect 301` lines in `public_html` — fine for a
   handful; don't hand-edit the Passenger-managed block.

Keep these redirects **forever** (or years). Losing them is how ranking is lost.

Special cases:
- `/feed/`, `/comments/feed/` → 301 to `/` or 410 if there was never a real feed.
- `/wp-login.php`, `/wp-admin/` → let them 404 once WP is gone (or redirect to
  `/admin/`). Do **not** proxy them.
- `/wp-content/uploads/x.jpg` → 301 to the new asset path, or copy the file to
  the same path under the new docroot so the URL still resolves.

## 4. SEO carry-over checklist

- Keep the **same domain** — no Change-of-Address needed.
- `title` / meta description / canonical / Open Graph / JSON-LD: already in
  `base.html` + `_seo_jsonld.html`. Re-check they match the old important pages.
- **Search Console:** a **Domain property** (DNS TXT) keeps working across the
  swap — nothing to redo. A URL-prefix property verified by a Yoast meta tag or
  an uploaded HTML file will break; move to the Domain property (DNS TXT is
  already added at Dewaweb — see `SEO.md`).
- Submit the new `/sitemap.xml`; remove the old `sitemap_index.xml` submission.
- After cutover, watch Search Console **Coverage / Pages** for a spike in 404s —
  each one is a missing redirect from §3.
- Re-add the analytics tag: set `GA4_MEASUREMENT_ID` or `PLAUSIBLE_DOMAIN` env
  vars (`base.html` renders the snippet). Don't carry over the WP plugin.
- `robots.txt`: the Django one (`/robots.txt`) replaces the WP/Yoast one.

## 5. Build & verify on staging

1. Deploy this project to a **staging subdomain** (`staging.subursedayamaju.co.id`)
   as its own cPanel "Setup Python App" — full steps in
   `REVAMP-DJANGO-CPANEL.md` §6. WordPress stays untouched on the apex.
2. `ssm_sync` (migrate + collectstatic), `ssm_admin` with a **strong**
   `SSM_ADMIN_PASS`.
3. Smoke test on staging: every nav link, the contact form (submit a real test
   message, confirm it lands in `/message/` and the notification email arrives),
   `/sitemap.xml`, `/robots.txt`, `/seo/` (should be all-green), mobile layout.
4. Run the old→new redirect list against staging (a quick script that curls each
   old path and asserts a 301 to the expected target).

## 6. Cutover

Low-traffic window (e.g. Sunday night WIB):

1. Lower the domain's DNS TTL a day ahead if a DNS change is involved (usually
   it isn't — same account).
2. Final content sync (any WP edits since the staging copy).
3. **Repoint the apex** to the Django app:
   - cPanel → *Setup Python App* → change the staging app's **Application URL**
     from the subdomain to `subursedayamaju.co.id` (and `www`), **or** create the
     production app fresh and move the domain's document root / Passenger config
     to it.
   - Move the WordPress files out of the way: rename `public_html` contents
     (`wp-*`, `wp-content`, …) into `public_html/_wp_old/` so they stop being
     served but are recoverable.
4. `touch tmp/restart.txt`, then smoke-test the apex exactly as in §5.3.
5. Put the redirect rules live (they were staged in §3).
6. In Search Console: submit the new sitemap, use **URL Inspection → Request
   indexing** on the home page and top 5 pages.

## 7. After cutover

- Watch for 2–4 weeks: Search Console Coverage, `/message/` for real leads,
  server logs for 404s and for hits on `/wp-*` (bots probing — fine, just 404).
- Keep `public_html/_wp_old/` and a full WordPress DB dump for at least a month
  as the rollback path. Rollback = restore the files and point the docroot back.
- Once stable: delete the WP database and `_wp_old/`, cancel paid plugin
  licences, remove the staging app (or keep it for future staging).

## 8. Security note for the admin

The Django admin lives at `/admin/` and `/message/` sits behind it.

- Use a **strong** admin password in production (`ssmadmin` is dev-only;
  `ensure_admin` refuses it when `DEBUG` is off).
- Consider restricting `/admin/` by IP (cPanel *Directory Privacy* / `.htaccess`
  on the Passenger static dir won't cover app routes — do it in a small Django
  middleware or via Cloudflare/host firewall) or moving it to a non-obvious path.
- `production.py` already sets secure cookies, HSTS, and
  `SECURE_SSL_REDIRECT`.
