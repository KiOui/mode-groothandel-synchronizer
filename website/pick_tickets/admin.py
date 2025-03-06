from django.contrib import admin
from import_export.admin import ExportMixin
from rangefilter.filters import DateRangeFilter

from mutations.admin import MutationInline, SucceededMutationFilter
from pick_tickets.models import PickTicket
from pick_tickets.resources import PickTicketResource


@admin.register(PickTicket)
class PickTicketAdmin(ExportMixin, admin.ModelAdmin):
    """Pick Ticket Admin."""

    resource_class = PickTicketResource

    search_fields = ["uphance_id", "sendcloud_id", "shipment_number", "order_id", "sale_id"]

    list_display = [
        "uphance_id",
        "sendcloud_id",
        "created",
        "updated",
    ]

    list_filter = [
        SucceededMutationFilter,
        ("created", DateRangeFilter),
        ("updated", DateRangeFilter),
    ]

    inlines = (MutationInline,)

    def has_change_permission(self, request, obj=None):
        """No change permission for this admin view."""
        return False
