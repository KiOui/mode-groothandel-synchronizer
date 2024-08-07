from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from import_export.admin import ExportMixin
from rangefilter.filters import DateRangeFilter

from mutations.models import Mutation
from mutations.resources import MutationResource


class MutationInline(GenericTabularInline):
    """Display Mutation inline."""

    model = Mutation
    readonly_fields = (
        "created",
        "method",
        "trigger",
        "on",
        "success",
    )
    fields = (
        "created",
        "method",
        "trigger",
        "on",
        "success",
    )
    extra = 0
    show_change_link = True

    def has_change_permission(self, request, obj=None):
        """No change permission for this inline."""
        return False

    def has_add_permission(self, request, obj):
        """No add permission for this inline."""
        return False

    def has_delete_permission(self, request, obj=None):
        """No delete permission for this inline."""
        return False


@admin.register(Mutation)
class MutationsAdmin(ExportMixin, admin.ModelAdmin):
    """Mutations Admin."""

    resource_class = MutationResource

    search_fields = ["on"]

    list_filter = [
        "success",
        "method",
        "content_type",
        ("created", DateRangeFilter),
    ]

    list_display = [
        "on",
        "method",
        "content_type",
        "success",
    ]

    def has_change_permission(self, request, obj=None):
        """No change permission for this admin view."""
        return False
