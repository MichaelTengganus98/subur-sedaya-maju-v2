"""Dependency-free on-page SEO checks for a rendered HTML page.

Used by the ``/seo/`` view (:class:`apps.pages.views.SeoAuditView`). Kept as pure
functions so the logic can be unit-tested without a request/response cycle.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from urllib.parse import urlparse

# fail floats to the top of the report, info sinks to the bottom
_STATUS_ORDER = {"fail": 0, "warn": 1, "pass": 2, "info": 3}


@dataclass
class Check:
    id: str
    label: str
    status: str  # "pass" | "warn" | "fail" | "info"
    detail: str = ""


class _DOM(HTMLParser):
    """Minimal DOM scrape: just what the checks below need."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self._in_title = False
        self.metas: list[dict] = []
        self.links: list[dict] = []
        self.imgs: list[dict] = []
        self.anchors: list[dict] = []
        self.headings: list[tuple] = []  # (level:int, text:str)
        self._heading = None
        self.jsonld: list[str] = []
        self._in_ld = False
        self._ld_buf: list[str] = []
        self.script_srcs: list[str] = []
        self.html_lang = None
        self._notext_depth = 0
        self.word_count = 0

    def handle_starttag(self, tag, attrs):
        d = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.html_lang = d.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            self.metas.append(d)
        elif tag == "link":
            self.links.append(d)
        elif tag == "img":
            self.imgs.append(d)
        elif tag == "a":
            self.anchors.append(d)
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._heading = [int(tag[1]), ""]
        elif tag == "script":
            if d.get("src"):
                self.script_srcs.append(d["src"])
            if d.get("type", "").lower() == "application/ld+json":
                self._in_ld = True
                self._ld_buf = []
            self._notext_depth += 1
        elif tag == "style":
            self._notext_depth += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._heading:
            self.headings.append((self._heading[0], " ".join(self._heading[1].split())))
            self._heading = None
        elif tag == "script":
            if self._in_ld:
                self.jsonld.append("".join(self._ld_buf).strip())
                self._in_ld = False
            self._notext_depth = max(0, self._notext_depth - 1)
        elif tag == "style":
            self._notext_depth = max(0, self._notext_depth - 1)

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)
        if self._heading is not None:
            self._heading[1] += data
        if self._in_ld:
            self._ld_buf.append(data)
        elif self._notext_depth == 0:
            self.word_count += len(data.split())

    # -- helpers ----------------------------------------------------------
    @property
    def title(self):
        return "".join(self.title_parts).strip()

    def meta_name(self, name):
        for m in self.metas:
            if m.get("name", "").lower() == name.lower():
                return m.get("content", "")
        return None

    def meta_prop(self, prop):
        for m in self.metas:
            if m.get("property", "").lower() == prop.lower():
                return m.get("content", "")
        return None

    def link_rel(self, rel):
        for link in self.links:
            if rel in link.get("rel", "").lower().split():
                return link
        return None


_BUSINESS_TYPES = {"LocalBusiness", "MovingCompany", "Organization"}


def _iter_nodes(blocks):
    for raw in blocks:
        try:
            data = json.loads(raw)
        except ValueError:
            yield None  # signals a parse failure
            continue
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
        if isinstance(nodes, list):
            for node in nodes:
                if isinstance(node, dict):
                    yield node


def _node_types(node):
    tp = node.get("@type")
    return set(tp) if isinstance(tp, list) else ({tp} if tp else set())


def _route_ok(path):
    from django.urls import Resolver404, resolve

    try:
        resolve(path)
        return True
    except Resolver404:
        return False


def audit(html, *, base_url="", check_routes=True):
    """Run the checks against ``html`` and return a JSON-serialisable dict."""
    dom = _DOM()
    dom.feed(html)
    checks: list[Check] = []
    add = checks.append

    # --- <title> -------------------------------------------------------
    t = dom.title
    if not t:
        add(Check("title", "Title tag", "fail", "No <title> element."))
    else:
        n = len(t)
        status = "pass" if 15 <= n <= 65 else "warn"
        hint = "" if status == "pass" else ("too short" if n < 15 else "long — Google truncates around 60–65 chars")
        add(Check("title", "Title tag", status, f"{n} chars — “{t}”. {hint}".strip()))

    # --- meta description --------------------------------------------------
    desc = dom.meta_name("description")
    if not desc:
        add(Check("description", "Meta description", "fail", "Missing."))
    else:
        n = len(desc)
        status = "pass" if 70 <= n <= 160 else ("warn" if n <= 200 else "fail")
        add(Check("description", "Meta description", status,
                  f"{n} chars." + ("" if status == "pass" else " Aim for 70–160.")))

    # --- single H1 ------------------------------------------------------
    h1s = [txt for lvl, txt in dom.headings if lvl == 1]
    if len(h1s) == 1:
        add(Check("h1", "Single H1", "pass", h1s[0][:90]))
    elif not h1s:
        add(Check("h1", "Single H1", "fail", "No <h1> on the page."))
    else:
        add(Check("h1", "Single H1", "warn", f"{len(h1s)} H1s: " + " | ".join(x[:40] for x in h1s)))

    # --- heading hierarchy -------------------------------------------------
    skips, prev = [], 0
    for lvl, _ in dom.headings:
        if prev and lvl > prev + 1:
            skips.append(f"h{prev}→h{lvl}")
        prev = lvl
    add(Check("hierarchy", "Heading hierarchy", "pass" if not skips else "warn",
              "No skipped levels." if not skips else "Skipped: " + ", ".join(sorted(set(skips)))))

    # --- html[lang] --------------------------------------------------------
    add(Check("lang", "html[lang]", "pass" if dom.html_lang else "fail",
              dom.html_lang or "No lang attribute on <html>."))

    # --- canonical ------------------------------------------------------
    canon = dom.link_rel("canonical")
    if not canon:
        add(Check("canonical", "Canonical URL", "fail", "No <link rel=canonical>."))
    else:
        href = canon.get("href", "")
        ok = urlparse(href).scheme in ("http", "https")
        add(Check("canonical", "Canonical URL", "pass" if ok else "warn",
                  href or "empty href"))

    # --- robots meta -----------------------------------------------------
    robots = (dom.meta_name("robots") or "").lower()
    if "noindex" in robots:
        add(Check("robots-meta", "Robots meta", "fail", f"Page is noindex: “{robots}”."))
    else:
        add(Check("robots-meta", "Robots meta", "pass", robots or "(default: index, follow)"))

    # --- viewport ------------------------------------------------------
    add(Check("viewport", "Viewport meta", "pass" if dom.meta_name("viewport") else "fail",
              dom.meta_name("viewport") or "Missing — not mobile-friendly."))

    # --- Open Graph -----------------------------------------------------
    og_missing = [p for p in ("og:title", "og:description", "og:image", "og:url")
                  if not dom.meta_prop(p)]
    add(Check("open-graph", "Open Graph tags", "pass" if not og_missing else "warn",
              "og:title/description/image/url all present."
              if not og_missing else "Missing: " + ", ".join(og_missing)))

    # --- Twitter card --------------------------------------------------
    tw = dom.meta_name("twitter:card")
    add(Check("twitter-card", "Twitter Card", "pass" if tw else "warn",
              tw or "No twitter:card meta."))

    # --- JSON-LD -----------------------------------------------------------
    parsed_types, parse_fail = [], False
    for node in _iter_nodes(dom.jsonld):
        if node is None:
            parse_fail = True
        else:
            parsed_types.extend(_node_types(node))
    if not dom.jsonld:
        add(Check("jsonld", "Structured data (JSON-LD)", "warn", "No JSON-LD blocks found."))
    elif parse_fail:
        add(Check("jsonld", "Structured data (JSON-LD)", "fail",
                  "A JSON-LD block failed to parse."))
    else:
        add(Check("jsonld", "Structured data (JSON-LD)", "pass",
                  f"{len(dom.jsonld)} block(s): " + ", ".join(sorted(set(parsed_types)))))

    # --- LocalBusiness completeness --------------------------------------
    biz = next((n for n in _iter_nodes(dom.jsonld)
                if n and _node_types(n) & _BUSINESS_TYPES), None)
    if biz is None:
        add(Check("localbusiness", "LocalBusiness schema", "info", "No LocalBusiness/Organization node."))
    else:
        miss = [f for f in ("name", "address", "telephone", "geo") if f not in biz]
        add(Check("localbusiness", "LocalBusiness schema", "pass" if not miss else "warn",
                  "name, address, telephone, geo all set."
                  if not miss else "Missing field(s): " + ", ".join(miss)))

    # --- image alt text ----------------------------------------------------
    no_alt = [i for i in dom.imgs if "alt" not in i]
    add(Check("img-alt", "Image alt text", "pass" if not no_alt else "fail",
              f"All {len(dom.imgs)} <img> carry alt (alt=\"\" = decorative, OK)."
              if not no_alt else f"{len(no_alt)} of {len(dom.imgs)} <img> have no alt attribute."))

    # --- image dimensions (CLS) -----------------------------------------
    no_dim = [i for i in dom.imgs if not (i.get("width") and i.get("height"))]
    add(Check("img-dimensions", "Image width/height (CLS)", "pass" if not no_dim else "warn",
              "Every <img> sets width & height."
              if not no_dim else
              f"{len(no_dim)} of {len(dom.imgs)} <img> lack explicit width/height "
              "(fine if they sit in an aspect-ratio box)."))

    # --- target=_blank safety ----------------------------------------------
    risky = [a for a in dom.anchors
             if a.get("target") == "_blank" and "noopener" not in a.get("rel", "").lower()]
    add(Check("blank-rel", "Blank-target links", "pass" if not risky else "warn",
              "All target=_blank links use rel=noopener."
              if not risky else f"{len(risky)} target=_blank link(s) missing rel=noopener."))

    # --- favicon ------------------------------------------------------
    add(Check("favicon", "Favicon", "pass" if dom.link_rel("icon") else "warn",
              "Declared." if dom.link_rel("icon") else "No <link rel=icon>."))

    # --- sitemap ------------------------------------------------------
    sm_link = dom.link_rel("sitemap") is not None
    sm_route = _route_ok("/sitemap.xml") if check_routes else None
    parts = [f"<link rel=sitemap>: {'yes' if sm_link else 'no'}"]
    if sm_route is not None:
        parts.append(f"/sitemap.xml route: {'yes' if sm_route else 'no'}")
    ok = sm_link and (sm_route is not False)
    add(Check("sitemap", "Sitemap", "pass" if ok else "warn", "; ".join(parts) + "."))

    # --- robots.txt route --------------------------------------------------
    if check_routes:
        rt = _route_ok("/robots.txt")
        add(Check("robots-txt", "robots.txt", "pass" if rt else "warn",
                  "/robots.txt route configured." if rt else "No /robots.txt route."))

    # --- content volume --------------------------------------------------
    wc = dom.word_count
    add(Check("content-volume", "Visible word count", "pass" if wc >= 300 else "warn",
              f"~{wc} words." + ("" if wc >= 300 else " Thin content — aim for 300+.")))

    # --- analytics (informational) ---------------------------------------
    srcs = " ".join(dom.script_srcs)
    found = [name for token, name in (("googletagmanager.com/gtag", "GA4"),
                                     ("plausible", "Plausible")) if token in srcs]
    add(Check("analytics", "Analytics", "info", ", ".join(found) if found else "None loaded."))

    # --- Search Console meta (informational) ----------------------------
    add(Check("gsc", "Search Console meta", "info",
              dom.meta_name("google-site-verification") or "Not set (DNS TXT method may be in use)."))

    summary = {s: sum(c.status == s for c in checks) for s in ("pass", "warn", "fail", "info")}
    summary["total"] = len(checks)
    checks.sort(key=lambda c: (_STATUS_ORDER[c.status], c.id))
    return {"url": base_url or "/", "summary": summary, "checks": [asdict(c) for c in checks]}
