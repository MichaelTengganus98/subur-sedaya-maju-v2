from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for the hard-coded, non-model pages (currently just the home page).

    Domain is pinned to settings.CANONICAL_HOST rather than the requesting host.
    The site is reachable on more than one host (apex + www, see ALLOWED_HOSTS in
    config/settings/production.py) with no canonicalizing redirect between them,
    so without this override the sitemap's <loc> would follow whichever host was
    used to fetch /sitemap.xml and could disagree with the <link rel=canonical>,
    og:url and JSON-LD urls, which always use CANONICAL_HOST.
    """

    protocol = "https"
    changefreq = "monthly"
    priority = 1.0

    def items(self):
        return ["pages:home"]

    def location(self, item):
        return reverse(item)

    def get_domain(self, site=None):
        return urlparse(settings.CANONICAL_HOST).netloc
