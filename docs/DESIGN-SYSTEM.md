# Design System — Industrial Redesign

Applied on `revamp/django-cpanel`. Reference mock: `design/subursedayamaju-redesign.html`
(git-ignored). All of it lives in `static/css/style.css`; templates use the
class names below.

## Direction

Rugged / industrial — "asphalt, weathered concrete, hazard amber, rust".
Sharp corners everywhere, heavy 1px rules instead of shadows, mono micro-labels,
alternating light / tint / dark section bands. Real photos kept, framed with a
1px border and a small amber corner tab.

## Tokens (`:root`)

| Token | Value | Use |
|---|---|---|
| `--asphalt` | `#1B1E20` | dark sections, header, footer |
| `--asphalt-2` | `#24282B` | dark card fill |
| `--steel` | `#3E4750` | secondary dark |
| `--concrete` / `--concrete-2` | `#EDE9E1` / `#E1DCD1` | tint sections, placeholder grid |
| `--paper` | `#F7F5F1` | page + light-section background |
| `--amber` / `--amber-hi` / `--amber-dim` | `#E8A020` / `#F4B13A` / `#B87D18` | primary accent, hover, on-light text |
| `--rust` | `#B4432B` | placeholder / warning accents |
| `--ink` / `--ink-soft` / `--muted` / `--muted-2` | `#1B1E20` / `#565C5F` / `#9AA0A3` / `#6B7173` | text scale |
| `--line` / `--line-dark` | `#C9C2B4` / `#454C50` | hairlines on light / dark |

Fonts (Google Fonts, loaded in `base.html`):
`--display` / `--head` = **Archivo** (display uses `font-stretch:expanded` + tight tracking),
`--body` = **IBM Plex Sans**, `--mono` = **IBM Plex Mono** (all uppercase micro-labels).

## Building blocks

| Class | What it is |
|---|---|
| `.section` + `.section-light` / `.section-tint` / `.section-dark` | 96px band, one of three grounds. Alternate down the page. |
| `.wrap` / `.container` | max-width 1180px, 32px gutters (20px on mobile) |
| `.stripe-line` | 10px diagonal hazard divider (amber/asphalt). Used once, under the hero. |
| `.stripe-band` | dark section with a faint 45° amber pinstripe overlay (partner CTA, final CTA) |
| `.kicker` | mono uppercase eyebrow, amber-dim on light / amber on dark |
| `.section-title` | Archivo expanded, `clamp(28px,3.4vw,38px)` |
| `.head-row` | title left + supporting `<p>` right, hairline under |
| `.btn` + `.btn-primary` / `.btn-outline` / `.btn-outline-light` | sharp 2px-border buttons |
| `.col-list` / `.col-item` | equal columns divided by vertical hairlines (services, why-us) |
| `.col-icon` | 52px bordered icon box |
| `.stats-grid` / `.stat-card` | bordered 4-up band; `.stat-number[data-count]` animates (main.js) |
| `.process-grid` / `.process-step` + `.process-number` | 4 mono-numbered steps |
| `.safety-card` + `.check-list` | dark-headed checklist panel ("PROTOKOL KESELAMATAN KERJA") |
| `.vision` | dark band, quote as `<h2>`, photo with amber corner |
| `.fleet-grid` / `.fleet-card` + `.placeholder-media` | placeholder photo grid (blueprint-grid fill) |
| `.placeholder-note` | rust dashed banner flagging placeholder content |
| `.placeholder-copy` | muted italic for dummy text |
| `.testimonial-grid` / `.cert-grid` / `.coverage-chips` / `.chip` | matching bordered treatments |
| `.faq-list` / `.faq-item` | `<details>` rows with `+` / `−` marker |
| `.contact-grid` | info (concrete) + form (paper) split, 1px border |
| `.form-field` | mono uppercase label + sharp bordered input |
| `.map-embed` | real Google Maps iframe, bordered, amber corner, `grayscale(.3)` |
| `.whatsapp-fab` | green rectangular pill, label hides < 520px |

## Behaviour

`static/js/main.js` is unchanged from the plain port: mobile nav (`.nav-toggle` /
`.site-nav.is-open` / `#nav-overlay`), sticky-header `.is-scrolled`, `.reveal`
→ `.is-visible` on scroll, `.stat-number` count-up, footer `#year`, and the
contact form → `mailto:` fallback. The mobile nav breakpoint is 1080px.

## Still to do

- Section content flagged in `CONTENT-TODO.md` is unchanged — fleet, testimonials,
  certifications, most coverage/FAQ still ship placeholders (with visible notes).
- Split `home.html` into `templates/partials/_*.html` (REVAMP plan step 3).
- Wire the contact form to the `contact` app once built (step 4).
