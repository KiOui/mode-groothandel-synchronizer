from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Subquery, Max, Min, OuterRef, Exists, Window
from import_export.admin import ExportMixin
from rangefilter.filters import DateRangeFilter

from invoices.models import Invoice
from invoices.resources import InvoiceResource
from mutations.admin import MutationInline
from mutations.models import Mutation


class SucceededMutationFilter(admin.SimpleListFilter):
    title = "succeeded mutation"

    parameter_name = "succeeded_mutation"

    def __init__(self, *args, **kwargs):
        super(SucceededMutationFilter, self).__init__(*args, **kwargs)
        self.content_type = ContentType.objects.get_for_model(Invoice)

    def lookups(self, request, model_admin):
        return [
            ("exists", "At least one succeeded mutation"),
            ("not_exists", "No succeeded mutations"),
            ("latest", "Latest mutation must be succeeded"),
            ("not_latest", "Latest mutation must be failed"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "exists":
            return queryset.filter(
                Exists(
                    Mutation.objects.filter(content_type=self.content_type, object_id=OuterRef("pk")).exclude(
                        success=False
                    )
                )
            )
        elif self.value() == "not_exists":
            return queryset.exclude(
                id__in=Subquery(
                    Mutation.objects.filter(content_type=self.content_type)
                    .exclude(success=False)
                    .values("object_id")
                    .distinct()
                    .all()
                )
            )
        elif self.value() == "latest":
            return queryset.annotate(
                latest_success=Subquery(
                    Mutation.objects.filter(content_type=self.content_type, object_id=OuterRef("pk"))
                    .order_by("-created")
                    .values("success")[:1]
                )
            ).filter(latest_success=True)
        elif self.value() == "not_latest":
            return queryset.annotate(
                latest_success=Subquery(
                    Mutation.objects.filter(content_type=self.content_type, object_id=OuterRef("pk"))
                    .order_by("-created")
                    .values("success")[:1]
                )
            ).filter(latest_success=False)

        return queryset


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

    list_filter = [
        SucceededMutationFilter,
        ("created", DateRangeFilter),
        ("updated", DateRangeFilter),
    ]

    inlines = (MutationInline,)

    def has_change_permission(self, request, obj=None):
        """No change permission for this admin view."""
        return False
