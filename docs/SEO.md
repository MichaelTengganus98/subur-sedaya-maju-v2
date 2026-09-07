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

## 2. Needs the client / real data before it ships

- **Exact geo coordinates.** `_seo_jsonld.html` and the geo meta tags use an
  approximate Prabumulih city point (`-3.4325, 104.2356`). Replace with the exact
  lat/long from the company's Google Business Profile ("Business Profile → Edit →
  location pin"), and keep the address string identical to the profile.
- **`sameAs`** is intentionally omitted — add verified profile URLs once known
  (Google Business Profile, Instagram, LinkedIn, Facebook, YouTube, industry
  directories). This is one of the strongest entity signals.
- **Real certificates** (NIB, SIUP, SMK3, ISO 9001/45001, association
  membership): when supplied, add `hasCredential` / `Certification` nodes and a
  logo wall — see `CONTENT-TODO.md`.
- **Aggregate rating / reviews.** Do **not** hard-code `aggregateRating` or
  `review` in JSON-LD unless it reflects genuine, on-page, verifiable reviews —
  fake rating markup is a manual-action risk. The Google reviews CTA stays as-is
  until real testimonials are collected.
- **Dedicated 1200×630 social share image** (`og:image`) with the logo + a strong
  photo; the current hero JPEG is 1200×900 (works, not ideal ratio).
- Confirm the **service-area list** (Prabumulih, Palembang, Muara Enim, Lahat +
  "nasional") and the footer's "seluruh Indonesia" claim.

## 3. Off-page / operational (not code)

- **Google Search Console** — verify the domain (DNS TXT), submit
  `https://www.subursedayamaju.co.id/sitemap.xml`, watch Coverage + Core Web
  Vitals.
- **Google Business Profile** — claim/complete it: category
  "Perusahaan transportasi" / "Jasa penyewaan alat berat", service area, hours,
  photos of real units, and start collecting reviews. This is the highest-impact
  lever for a local B2B operator and feeds the Map Pack.
- **Bing Webmaster Tools** — import from GSC.
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
