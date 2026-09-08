from django.urls import path

from .views import HomeView, SeoAuditView

app_name = "pages"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("seo/", SeoAuditView.as_view(), name="seo_audit"),
]
