from django.contrib import admin
from import_export.admin import ExportMixin

from invoices.models import Invoice
from invoices.resources import InvoiceResource
from mutations.admin import MutationInline


@admin.register(Invoice)
class InvoiceAdmin(ExportMixin, admin.ModelAdmin):
    """Invoice Admin."""

    resource_class = InvoiceResource

    search_fields = ["uphance_id", "snelstart_id", "invoice_number"]

    list_display = [
        "uphance_id",
        "snelstart_id",
        "invoice_number",
        "invoice_total",
        "created",
        "updated",
    ]

    inlines = (MutationInline,)

    def has_change_permission(self, request, obj=None):
        """No change permission for this admin view."""
        return False
