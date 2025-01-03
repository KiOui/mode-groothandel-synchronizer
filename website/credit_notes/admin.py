from django.contrib import admin

from credit_notes.models import CreditNote
from mutations.admin import MutationInline


@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    """Credit Note Admin."""

    search_fields = ["uphance_id", "snelstart_id", "credit_note_number"]

    list_display = [
        "uphance_id",
        "snelstart_id",
        "credit_note_number",
        "credit_note_total",
        "created",
        "updated",
    ]

    inlines = (MutationInline,)

    def has_change_permission(self, request, obj=None):
        """No change permission for this admin view."""
        return False
