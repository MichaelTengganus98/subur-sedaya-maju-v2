# Site Overview — Existing Static Website

A snapshot of the current site as pulled from production, so the revamp has a
clear baseline of what exists today.

## 1. Technology

| Area | Detail |
|---|---|
| Markup | Single file `index.html` (~600 lines), semantic HTML5, one long scrolling page |
| Styling | `assets/css/style.css` (~1,370 lines). Hand-written, no CSS framework. Uses CSS custom properties for the design tokens. |
| Scripting | `assets/js/main.js` (~145 lines). Vanilla JS wrapped in an IIFE. No dependencies. |
| Fonts | Google Fonts — `Poppins` (headings) and `Inter` (body), loaded via `<link>` with `preconnect`. |
| Icons | Inline SVG (Feather-style stroke icons) plus a few PNG icons in `assets/images/`. |
| Maps | Google Maps `<iframe>` embed (no API key). |
| Backend | **None.** The contact form is handled entirely client-side (see §4). |
| Build | **None.** Files are served as-is. |

## 2. Design tokens (`:root` in `style.css`)

```
--brand-900: #0f2c47   --brand-700: #1c4e78   --brand-500: #2f7dc4
--amber-500: #f2994a   --amber-600: #dd8225
--gray-50:  #f7f9fb    --gray-100: #eef2f6    --gray-200: #dfe6ed
--gray-500: #6b7785    --gray-700: #3a4552    --text: #202b36
--font-heading: "Poppins", "Segoe UI", Arial, sans-serif
--font-body:    "Inter", "Segoe UI", Arial, sans-serif
--container-width: 1180px
--radius: 12px
--shadow-sm / --shadow-md / --shadow-lg
```

Palette in words: deep navy blue as the primary brand colour, an amber/orange
accent, neutral grays for text and surfaces.

## 3. Page structure (in DOM order)

| # | Section | `id` | Notes |
|---|---|---|---|
| 1 | Skip link + Header | `site-header` | Logo, desktop nav, WhatsApp number, "Hubungi Kami" CTA, mobile hamburger + overlay |
| 2 | Hero | `main-content` | Background truck photo, headline "PT Subur Sedaya Maju — Sejak 2006", two CTAs, 3 trust badges |
| 3 | Services / Layanan | `layanan` | 3 cards: Pengangkutan Alat Berat, Pengangkutan Muatan Besar, Peralatan Industri & Konstruksi |
| 4 | Stats | — | Animated counters: 20+ years, 50+ partners, "Berdiri Sejak 2006", K3 priority |
| 5 | Why Us / Kenapa Kami | — | 3 info boxes: Teknisi Berpengalaman, Kualitas Produk Baik, Kondisi Terawat |
| 6 | Process / Proses Kerja | `proses` | 4 numbered steps: Konsultasi → Survei & Rute → Pengiriman → Dukungan Purna |
| 7 | About / Tentang Kami (Misi) | `about-us` | Mission copy + safety commitment checklist (5 items) |
| 8 | Vision / Visi | — | `visi-photo.png` + vision statement |
| 9 | Fleet / Armada | `armada` | 6 cards — **placeholder** photos & specs |
| 10 | Partners / Partner Kami | `our-partner` | `partner-photo.png` + "50+ perusahaan" copy + CTA |
| 11 | Lifetime Partner / Komitmen | — | `mitra-photo.jpeg` + long-term partnership copy + CTA |
| 12 | Testimonials / Testimoni | `testimoni` | 3 cards — **placeholder** quotes |
| 13 | Certifications / Legalitas | `legalitas` | 4 badges — **placeholder** (SIUP, SMK3, ISO, …) |
| 14 | Coverage / Wilayah Layanan | `wilayah` | Chips: "Sumatera Selatan" + 3 placeholder chips |
| 15 | FAQ | `faq` | 4 `<details>` items — 3 answers are **placeholder** |
| 16 | CTA banner | — | "Siap Bekerja Sama?" — WhatsApp + "Kirim Pesan" |
| 17 | Contact / Hubungi Kami | `contact-us` | Contact details + contact form |
| 18 | Location / Lokasi | — | Google Maps iframe |
| 19 | WhatsApp FAB | — | Floating chat button, fixed bottom-right |
| 20 | Footer | `site-footer` | Brand blurb, link columns, contact column, dynamic `© <year>` |

### Navigation targets
Desktop nav links to: `#about-us`, `#layanan`, `#our-partner`, `#contact-us`.
Footer links additionally reference `#armada` and `#faq`.

## 4. JavaScript behaviour (`assets/js/main.js`)

All in one IIFE. `CONTACT_EMAIL = "admin@subursedayamaju.co.id"`.

1. **Mobile nav** — hamburger toggles `.is-open` on `.site-nav`, `.is-active` on the toggle and overlay; `aria-expanded` kept in sync; any nav link click or overlay click closes it.
2. **Sticky header** — toggles `.is-scrolled` on `#site-header` when `scrollY > 8` (passive scroll listener).
3. **Scroll reveal** — `IntersectionObserver` adds `.is-visible` to `.reveal` elements (threshold 0.15, `rootMargin: 0px 0px -40px 0px`), then unobserves. Falls back to showing all if no `IntersectionObserver`.
4. **Stat counters** — `IntersectionObserver` (threshold 0.4) animates `.stat-number` from 0 to `data-count` over ~1200 ms with `requestAnimationFrame`.
5. **Footer year** — sets `#year` to the current year.
6. **Contact form → mailto** — on submit, `preventDefault()`, builds a `mailto:admin@subursedayamaju.co.id` URL with subject + body (Nama / Email / Telepon / message) and sets `window.location.href`. No network request, no validation beyond the browser's `required` attributes.

## 5. Contact form fields (`#contact-form`)

| Field | `name` | Required |
|---|---|---|
| First Name | `first_name` | no |
| Last Name | `last_name` | no |
| Email | `email` | yes |
| Subject | `subject` | no |
| Phone Number | `phone` | yes |
| Your Message | `message` | yes |

Submit button label: "Kirim Pesan". Labels are in English; the rest of the site is Indonesian.

## 6. Assets (`assets/images/`)

| File | Used for |
|---|---|
| `logo.png` | Footer logo |
| `logo-horizontal.png` | Header brand (declared 826×154) |
| `favicon.png`, `favicon-32.png` | Favicons / apple-touch-icon |
| `hero-truck.jpeg` | Hero background |
| `icon-teknisi.png`, `icon-kualitas.png`, `icon-kondisi.png` | "Why Us" icons |
| `visi-photo.png` | Vision section |
| `partner-photo.png` | Partners section |
| `mitra-photo.jpeg` | Lifetime-partner section |

## 7. SEO / metadata (in `<head>`)

- `<title>`: "PT. Subur Sedaya Maju — Transportasi Alat Berat Terpercaya"
- Meta description + `robots: index, follow`
- `canonical`: `https://www.subursedayamaju.co.id/`
- Open Graph: `og:type/title/description/url/site_name/image` (image = `assets/images/logo-horizontal.png`)
- No Twitter Card, no JSON-LD structured data, no `sitemap.xml` / `robots.txt` in the repo.

## 8. Known gaps / observations

- Contact form has no server side — messages depend on the visitor having a mail client.
- Placeholder content in Fleet, Testimonials, Certifications, Coverage, and 3 FAQ answers (see `CONTENT-TODO.md`).
- Form labels are English while the site is Indonesian.
- No structured data / `sitemap.xml` / `robots.txt`.
- Single HTML file — no templating, so shared markup (header/footer) is duplicated only once today but will not scale to multiple pages.
