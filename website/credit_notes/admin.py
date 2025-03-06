from django.contrib import admin
from import_export.admin import ExportMixin
from rangefilter.filters import DateRangeFilter

from credit_notes.models import CreditNote
from credit_notes.resources import CreditNoteResource
from mutations.admin import MutationInline, SucceededMutationFilter


@admin.register(CreditNote)
class CreditNoteAdmin(ExportMixin, admin.ModelAdmin):
    """Credit Note Admin."""

    resource_class = CreditNoteResource

    search_fields = ["uphance_id", "snelstart_id", "credit_note_number"]

    list_display = [
        "uphance_id",
        "snelstart_id",
        "credit_note_number",
        "credit_note_total",
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
