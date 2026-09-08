from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "full_name", "email", "phone", "subject", "is_handled")
    list_display_links = ("created_at", "full_name")
    list_filter = ("is_handled", "created_at")
    list_editable = ("is_handled",)
    search_fields = ("first_name", "last_name", "email", "phone", "subject", "message")
    date_hierarchy = "created_at"
    readonly_fields = (
        "first_name", "last_name", "email", "phone", "subject", "message",
        "created_at", "ip_address", "user_agent",
    )

    @admin.display(description="Nama")
    def full_name(self, obj):
        return obj.full_name or "—"

    def has_add_permission(self, request):
        return False
