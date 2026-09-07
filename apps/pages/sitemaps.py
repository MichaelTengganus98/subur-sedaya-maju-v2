from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for the hard-coded, non-model pages (currently just the home page)."""

    protocol = "https"
    changefreq = "monthly"
    priority = 1.0

    def items(self):
        return ["pages:home"]

    def location(self, item):
        return reverse(item)
