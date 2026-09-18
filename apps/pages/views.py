from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import TemplateView

from apps.contact.forms import make_form_token

from .seo_audit import audit


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contact_form_token"] = make_form_token()
        return context


class SeoAuditView(View):
    """On-page SEO health check for the home page.

    Renders the real home template in-process and runs `seo_audit.audit` over the
    HTML. Available with DEBUG on, or to logged-in staff in production. Add
    `?format=json` for the raw result.
    """

    def get(self, request, *args, **kwargs):
        if not (settings.DEBUG or request.user.is_staff):
            raise Http404()
        html = render_to_string("pages/home.html", request=request)
        # Search Console for this domain is verified via a DNS TXT record, so a
        # missing HTML-tag meta is expected rather than a problem.
        result = audit(
            html,
            base_url=request.build_absolute_uri("/"),
            dns_verification=True,
        )
        if request.GET.get("format") == "json":
            return JsonResponse(result)
        return render(request, "pages/seo_audit.html", {"result": result})
