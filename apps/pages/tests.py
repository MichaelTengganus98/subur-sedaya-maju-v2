from django.test import SimpleTestCase

from .seo_audit import audit


def _status(result, check_id):
    return next(c["status"] for c in result["checks"] if c["id"] == check_id)


class SeoAuditTests(SimpleTestCase):
    GOOD = """
    <!DOCTYPE html><html lang="id"><head>
    <title>Transportasi &amp; Sewa Alat Berat Prabumulih | PT Subur Sedaya Maju</title>
    <meta name="description" content="Jasa transportasi dan sewa alat berat sejak 2006 di Prabumulih, Sumatera Selatan; melayani proyek di Sumatera, Kalimantan, dan Jawa dengan armada modern.">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="canonical" href="https://www.subursedayamaju.co.id/">
    <link rel="icon" href="/static/favicon.png">
    <link rel="sitemap" href="/sitemap.xml">
    <meta property="og:title" content="x"><meta property="og:description" content="x">
    <meta property="og:image" content="x"><meta property="og:url" content="x">
    <meta name="twitter:card" content="summary_large_image">
    <script type="application/ld+json">{"@context":"https://schema.org","@type":["MovingCompany","LocalBusiness"],"name":"PT Subur Sedaya Maju","address":{},"telephone":"+62","geo":{}}</script>
    </head><body>
    <h1>PT Subur Sedaya Maju</h1><h2>Layanan</h2><h3>Detail</h3>
    <img src="a.jpg" alt="truk" width="800" height="600">
    <a href="https://wa.me/x" target="_blank" rel="noopener">wa</a>
    <p>%s</p>
    </body></html>
    """ % ("kata " * 400)

    def test_healthy_page_passes_core_checks(self):
        r = audit(self.GOOD, check_routes=False)
        for cid in ("title", "description", "h1", "hierarchy", "lang",
                    "canonical", "viewport", "open-graph", "twitter-card",
                    "jsonld", "localbusiness", "img-alt", "img-dimensions",
                    "blank-rel", "favicon", "content-volume"):
            self.assertEqual(_status(r, cid), "pass", f"{cid} should pass")
        self.assertEqual(r["summary"]["fail"], 0)

    def test_missing_title_and_description_fail(self):
        r = audit("<html lang='id'><head></head><body><h1>x</h1></body></html>",
                  check_routes=False)
        self.assertEqual(_status(r, "title"), "fail")
        self.assertEqual(_status(r, "description"), "fail")

    def test_noindex_fails(self):
        html = self.GOOD.replace(
            '<meta name="viewport"',
            '<meta name="robots" content="noindex, follow"><meta name="viewport"')
        self.assertEqual(_status(audit(html, check_routes=False), "robots-meta"), "fail")

    def test_missing_alt_and_broken_jsonld(self):
        html = self.GOOD.replace('alt="truk" ', "").replace('"geo":{}}', '"geo":{}')
        r = audit(html, check_routes=False)
        self.assertEqual(_status(r, "img-alt"), "fail")
        self.assertEqual(_status(r, "jsonld"), "fail")

    def test_multiple_h1_warns(self):
        html = self.GOOD.replace("<h2>Layanan</h2>", "<h1>Second</h1>")
        self.assertEqual(_status(audit(html, check_routes=False), "h1"), "warn")
