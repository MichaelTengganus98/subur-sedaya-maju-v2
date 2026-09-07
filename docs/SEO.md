# SEO

State of search-engine optimisation on `revamp/django-cpanel`, what was added,
and what still needs client input or a later phase.

## 1. Done in this branch

### Crawlability
- **`/robots.txt`** — `templates/robots.txt`, served as `text/plain` from
  `config/urls.py`. Allows everything, disallows `/admin/`, points to the sitemap.
- **`/sitemap.xml`** — `apps/pages/sitemaps.py` (`StaticViewSitemap`) wired through
  `django.contrib.sitemaps`. Currently lists the home page only; add entries as
  real pages are built. Emits `https://` + the request host, so production must
  serve it under the canonical domain (see `ALLOWED_HOSTS`).

### `<head>` metadata (`templates/base.html`)
- `<title>` is keyword- + location-first:
  *"Transportasi & Sewa Alat Berat Prabumulih | PT Subur Sedaya Maju"*.
- Meta description rewritten (~1 line, names the location + main equipment).
- `robots` = `index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1`.
- `canonical` → `https://www.subursedayamaju.co.id/`.
- Open Graph: added `og:locale=id_ID`, `og:image:alt`; `og:image` now the hero
  photo (`hero-truck.jpeg`) instead of the logo.
- Twitter Card: `summary_large_image` set (title / description / image).
- Geo meta: `geo.region=ID-SS`, `geo.placename`, `geo.position`, `ICBM`.
- `<link rel="sitemap">`.

### Structured data (JSON-LD)
- **`templates/partials/_seo_jsonld.html`** (included site-wide from `base.html`,
  URLs built from `settings.CANONICAL_HOST`): `@graph` with
  - `WebSite`
  - `WebPage` (`isPartOf` website, `about` the org, `primaryImageOfPage`)
  - `MovingCompany` + `LocalBusiness` — name, legal name, founding date 2006,
    phone (E.164), email, `PostalAddress`, `GeoCoordinates`, `hasMap`,
    `contactPoint`, `ImageObject` logo, `openingHoursSpecification`
    (Mon–Sat 08:00–17:00), `areaServed` (Sumatera Selatan + Indonesia),
    `knowsAbout`, `makesOffer` → 3 full `Service` nodes with
    `provider` / `areaServed`.
- **`FAQPage`** — in `pages/home.html` `{% block extra_head %}`, mirroring the 4
  visible FAQ entries verbatim (Google requires the answer text to be on-page).
  Note: FAQ *rich results* are now limited to authoritative gov/health sites; the
  markup is still valid and used by other engines.

### On-page structure
- Heading hierarchy fixed: fleet cards, process steps, certification badges and
  contact-info blocks were `<h4>` directly under a section `<h2>` (skipped a
  level) → now `<h3>`. CSS selectors updated 1:1, so rendering is unchanged.
- Hero image (LCP) gets `fetchpriority="high"` + `decoding="async"`; all
  below-the-fold images already use `loading="lazy"` with `width`/`height`.
- Branded **`404.html`** (extends `base.html`, `noindex`) and standalone
  **`500.html`**.

### Performance / Core Web Vitals
- **WebP pipeline.** `python manage.py optimize_images` (Pillow) writes a
  downscaled WebP sibling for each big photo; `templates/partials/_picture.html`
  + the `to_webp` filter (`apps/pages/templatetags/seo_extras.py`) serve it via
  `<picture><source>` with the original as `<img>` fallback. First run took the 4
  photos from **2.4 MB → 337 KB** (the two 1 MB PNGs → ~80 KB each). Re-run after
  changing any source image; the `.webp` files are committed.
- `picture{ display:contents }` keeps the wrapper transparent to the existing
  `.hero-media img` / `.fleet-media img` / `.media img` layout.

### Analytics (wired, inert until configured)
- `GA4_MEASUREMENT_ID` and `PLAUSIBLE_DOMAIN` env vars (see `.env.example`).
  `base.html` emits the GA4 `gtag` snippet and/or the Plausible script **only**
  when the matching value is set — nothing loads until the client provides one.
- `CANONICAL_HOST` env var (default `https://www.subursedayamaju.co.id`) drives
  every absolute URL (canonical, OG, JSON-LD) so staging can override it.

## 2. Client answers already applied

- **Geo coordinates** — decoded from the Google listing's Plus Code
  (`G6X8+XWJ Prabumulih`, CID `5137559904468020167`): `-3.45004, 104.21727`.
  Used in `_seo_jsonld.html` `geo` and the `geo.position` / `ICBM` meta.
  ~14 m precision; if the map pin is elsewhere, send the exact `lat, long` from
  the pin's right-click menu and it's a one-line change.
- **`sameAs`** — Facebook page added
  (`facebook.com/pages/Yard-Pt.-Subur-Sedaya-Maju/180378142812477`). Add more as
  they exist (Instagram, LinkedIn, TikTok, directory listings).
- **`hasMap`** — now the real listing link (`google.com/maps?cid=...`).
- **Service area** — Sumatra, Kalimantan, Jawa. Applied to JSON-LD `areaServed`
  (org + each Service), the coverage section chips, the wilayah FAQ (visible +
  JSON-LD), and the footer blurb (was "seluruh Indonesia").

## 2b. Still needs the client / real data

- **Google Business Profile — BLOCKED.** The client has said they cannot create
  one. Consequences: no Google Maps pack listing, no local knowledge panel, and
  Google has no first-party confirmation of NAP/hours. Partial mitigations that
  do **not** need GBP: the `LocalBusiness` JSON-LD (done), the Facebook page,
  **Bing Places for Business** and **Apple Business Connect** (both free,
  independent of Google), and consistent NAP on Indonesian B2B directories. Revisit
  GBP later — it remains the single highest-value local lever.
- **Real certificates** (NIB, SIUP, SMK3, ISO, association membership) — client
  said **skip for now**. When supplied: `hasCredential` nodes + a logo wall.
- **Company logo file** for JSON-LD `logo` / `og:image` — client said skip for
  now; currently points at `logo-horizontal.png` / the hero photo.
- **Aggregate rating / reviews** — do **not** hard-code `aggregateRating` /
  `review` unless it reflects genuine, on-page, verifiable reviews. Fake rating
  markup is a manual-action risk. The Google-reviews CTA stays until real
  testimonials are collected.
- **Dedicated 1200×630 social share image** — current hero JPEG is 1200×900
  (works, not ideal ratio).

## 3. Off-page / operational (not code)

- **Google Search Console** — verification token
  `google-site-verification=5rAifQ57E0D1t9sLSYTmmFViQS3BRacMBBMxoLgwFHU`.
  Two ways, either works:
  1. **DNS TXT** (Domain property, covers all subdomains) — add a TXT record at
     Dewaweb (host `@`, value = the whole `google-site-verification=...` string).
  2. **HTML tag** (URL-prefix property) — set `GOOGLE_SITE_VERIFICATION` env var
     to just the token (`5rAif…FHU`); `base.html` renders the meta tag. Deploy,
     then click Verify.
  After verifying, submit `https://www.subursedayamaju.co.id/sitemap.xml` and
  watch Coverage + Core Web Vitals. **Do not remove** the record/tag afterwards.
- **Bing Webmaster Tools** — import from GSC once GSC is verified.
- **Bing Places + Apple Business Connect** — free business listings that do not
  depend on Google Business Profile (which is blocked, see §2b).
- **Analytics** — the wiring is done (§1). Client picks GA4 or Plausible and
  provides the id/domain; set `GA4_MEASUREMENT_ID` / `PLAUSIBLE_DOMAIN` in the
  cPanel Python-App env and restart. GA4 also needs a cookie-consent banner under
  Indonesian PDP law before it should load.
- **Business directories & NAP consistency** — list the company on Indonesian
  B2B directories (Indotrading, Indonetwork, etc.) with the *exact* same Name,
  Address, Phone. Inconsistent NAP dilutes local ranking.
- **Backlinks** — client/partner sites, association pages, local news, equipment
  marketplaces.

## 4. Next-phase code work

- **Split into real pages** (`/layanan/pengangkutan-alat-berat/`,
  `/armada/lowboy/`, `/wilayah/palembang/`, …). A single page can only rank for
  so many terms; per-service and per-equipment pages let each target its own
  query and get its own `Service` / `Product` schema and sitemap entry. This
  lines up with `REVAMP-DJANGO-CPANEL.md` step 5.
- **Blog / artikel** section for informational queries
  ("biaya sewa lowboy", "cara mobilisasi excavator") — top-of-funnel traffic.
- **AVIF** — add a second `<source type="image/avif">` for another ~20-30% off
  the photos (WebP already done, §1).
- **Breadcrumbs** + `BreadcrumbList` schema once there is more than one page.
- **`hreflang`** only if an English version is ever added (currently `id` only).
- **Performance budget** — inline critical CSS or `media`-split the stylesheet;
  self-host fonts to drop the `fonts.gstatic.com` round-trip; run Lighthouse in
  CI. Core Web Vitals are a ranking factor.
- **XML sitemap** — extend `StaticViewSitemap` / add model sitemaps (`FleetUnit`,
  articles) with real `lastmod` when the `content` app lands.
