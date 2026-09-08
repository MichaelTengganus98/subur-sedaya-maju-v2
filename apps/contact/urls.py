from django.urls import path

from .views import ContactSubmitView, MessageListView

app_name = "contact"

urlpatterns = [
    path("kirim-pesan/", ContactSubmitView.as_view(), name="submit"),
    path("message/", MessageListView.as_view(), name="message_list"),
]
