# PT. Subur Sedaya Maju — Company Website

Marketing website for **PT. Subur Sedaya Maju**, a heavy‑equipment transportation
company operating in Indonesia since 2006.

- **Live domain:** https://www.subursedayamaju.co.id/
- **Language:** Indonesian (`lang="id"`)
- **Current stack:** Static HTML + CSS + vanilla JavaScript (no build step, no backend)
- **Hosting:** cPanel shared hosting

## Repository layout

```
website/
├── index.html              # Single-page site (all sections)
├── assets/
│   ├── css/style.css       # All styles (custom, no framework)
│   ├── js/main.js          # All behaviour (vanilla JS, IIFE)
│   └── images/             # Logos, icons, hero + section photos
├── invoice/                # Vendor invoices & price-adjustment letters (admin records)
└── docs/                   # Project documentation (see below)
```

## Documentation

| Document | Purpose |
|---|---|
| [`docs/SITE-OVERVIEW.md`](docs/SITE-OVERVIEW.md) | Full inventory of the existing static site: sections, content, assets, behaviour |
| [`docs/BUSINESS-INFO.md`](docs/BUSINESS-INFO.md) | Company facts as they currently appear on the site (contact, services, stats) |
| [`docs/CONTENT-TODO.md`](docs/CONTENT-TODO.md) | Placeholder content on the live site that still needs real data |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | How the current static site is deployed on cPanel |

## Branches

| Branch | Purpose |
|---|---|
| `main` | The current, live static site + documentation |
| `revamp/django-cpanel` | Rebuild of the site on Django, deployable via cPanel's "Setup Python App" (Passenger/WSGI). See `docs/REVAMP-DJANGO-CPANEL.md` on that branch. |

## Running locally

No build step. Serve the folder with any static server:

```bash
python -m http.server 8000
# then open http://localhost:8000
```
