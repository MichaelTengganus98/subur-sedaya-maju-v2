# Content TODO

Status of content on the `revamp/django-cpanel` home page. The visible
"this is placeholder" disclaimers have been removed; the items below are where
**real client-supplied material would still improve** what's shown.

## Fleet / Armada (`#armada`) — filled, photos pending
- 6 cards now name real unit types with specs sourced from public company
  info: Self-Loader Truck, Lowboy (Lowbed Trailer), Trailer & Dolly,
  Crawler Crane 25–260 T, Dump Truck, Alat Berat Pendukung.
- All 6 cards now show a photo. 3 are the company's own yard photos
  (`hero-truck`, `partner-photo`, `mitra-photo`); 3 are client-supplied stock
  images (`fleet-lowboy`, `fleet-trailer-dolly`, `fleet-dump-truck`).
- **Provenance flag:** `fleet-trailer-dolly` and `fleet-dump-truck` are US
  stock/AI photos with another company's name on the truck door
  ("ROADMASTER FREIGHT", "BUILD-MOR CONSTRUCTION") and non-Indonesian scenery.
  The grayscale/contrast filter softens this but they do not match SSM's real
  fleet. Replace with SSM's own unit photos before this goes to production, or
  at minimum crop out the visible third-party branding.
- **Still ideal:** a real photo + exact spec sheet per unit from the client
  (tonnage, dimensions, plate/asset count).

## Testimonials / Testimoni (`#testimoni`) — replaced with Google reviews CTA
- No public client testimonials exist, so the fake quote cards were removed.
- Section now points to the company's Google Business reviews.
- **Still ideal:** 2–3 real, attributed client quotes (name, role, company,
  with permission) to show inline instead of / alongside the CTA.

## Certifications / Legalitas (`#legalitas`) — reframed to verifiable facts
- Fake "Nama Sertifikasi" badges removed. Now 4 real attributes:
  Badan Hukum PT · Beroperasi Sejak 2006 · Komitmen K3/SMK3 ·
  Bengkel Pemeliharaan Sendiri.
- **Still ideal:** if the company holds NIB/SIUP, SMK3, ISO 9001/45001, or
  association membership, add the real certificate names + logos.

## Coverage / Wilayah (`#wilayah`) — filled
- Chips: Sumatera Selatan (basis operasional) + Prabumulih, Palembang,
  Muara Enim, Lahat + "Jangkauan Nasional — sesuai kebutuhan proyek".
- **Verify with client:** that these regencies are actually served, and
  whether the footer's "seluruh Indonesia" claim is accurate.

## FAQ (`#faq`) — filled
- All four answers written (wilayah, proses pemesanan, asuransi, estimasi
  waktu). The asuransi and estimasi answers are deliberately non-committal —
  **replace with the company's actual policy** once confirmed.

## Other content fixes
- ~~Contact form labels English → Indonesian~~ — done.
- Confirm the "20+ tahun" figure (2006 → 2026 ≈ 20 years).
- Decide whether the contact form should send email server-side (see
  `REVAMP-DJANGO-CPANEL.md` §4).
- Replace the reused hero/partner/mitra photos in the Fleet section once
  dedicated unit photos exist, so no image appears twice on the page.
