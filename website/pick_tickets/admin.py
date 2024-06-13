from django.contrib import admin

from mutations.admin import MutationInline
from pick_tickets.models import PickTicket


@admin.register(PickTicket)
class PickTicketAdmin(admin.ModelAdmin):
    """Pick Ticket Admin."""

    search_fields = ["uphance_id", "snelstart_id"]

    list_display = [
        "uphance_id",
        "sendcloud_id",
        "created",
        "updated",
    ]

    inlines = (MutationInline,)

    def has_change_permission(self, request, obj=None):
        """No change permission for this admin view."""
        return False
