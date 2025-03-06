from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef, Subquery
from import_export.admin import ExportMixin
from rangefilter.filters import DateRangeFilter

from mutations.models import Mutation
from mutations.resources import MutationResource


class SucceededMutationFilter(admin.SimpleListFilter):
    title = "succeeded mutation"

    parameter_name = "succeeded_mutation"

    def __init__(self, request, params, model, model_admin):
        super(SucceededMutationFilter, self).__init__(request, params, model, model_admin)
        self.content_type = ContentType.objects.get_for_model(model)

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
        "created",
        "on",
        "method",
        "content_type",
        "success",
    ]

    def has_change_permission(self, request, obj=None):
        """No change permission for this admin view."""
        return False
