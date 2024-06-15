from django.contrib import admin

from mutations.admin import MutationInline


class CustomerAdmin(admin.ModelAdmin):
    """Customer Admin."""

    search_fields = ["uphance_name", "uphance_id", "snelstart_name", "snelstart_id"]

    list_display = [
        "uphance_name",
        "uphance_id",
        "snelstart_id",
    ]

    inlines = (MutationInline,)
