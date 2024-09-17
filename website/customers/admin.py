from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.utils import quote
from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, Subquery, OuterRef
from django.http import HttpResponseRedirect
from django.urls import reverse
from import_export.admin import ExportMixin

from customers.models import Customer
from customers.resources import CustomerResource
from customers.services import match_or_create_snelstart_relatie_with_name
from mode_groothandel.clients.api import ApiException
from mode_groothandel.exceptions import SynchronizationError
from mutations.admin import MutationInline
from mutations.models import Mutation
from snelstart.clients.snelstart import Snelstart
from uphance.clients.uphance import Uphance


class SucceededMutationFilter(admin.SimpleListFilter):
    title = "succeeded mutation"

    parameter_name = "succeeded_mutation"

    def __init__(self, *args, **kwargs):
        super(SucceededMutationFilter, self).__init__(*args, **kwargs)
        self.content_type = ContentType.objects.get_for_model(Customer)

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


@admin.register(Customer)
class CustomerAdmin(ExportMixin, admin.ModelAdmin):
    """Customer Admin."""

    resource_class = CustomerResource

    search_fields = ["uphance_name", "uphance_id", "snelstart_name", "snelstart_id"]

    list_display = [
        "uphance_name",
        "uphance_id",
        "snelstart_id",
    ]

    list_filter = [
        SucceededMutationFilter,
    ]

    inlines = (MutationInline,)

    def _should_create_or_update_customer(self, request):
        """Whether a customer create or update should happen."""
        return "_create_or_update" in request.POST

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Add extra action to admin post request."""
        if self._should_create_or_update_customer(request):
            obj = self.get_object(request, object_id)
            if obj is None:
                self.message_user(
                    request,
                    "Object could not be found.",
                    level=messages.WARNING,
                )
                return super(CustomerAdmin, self).changeform_view(
                    request, object_id=object_id, form_url=form_url, extra_context=extra_context
                )

            uphance_client = Uphance.get_client()
            snelstart_client = Snelstart.get_client()
            try:
                customer = uphance_client.customer_by_id(obj.uphance_id)
            except ApiException as err:
                self.message_user(
                    request,
                    f"An error occurred while retrieving the customer from Uphance: {err}.",
                    level=messages.WARNING,
                )
                return super(CustomerAdmin, self).changeform_view(
                    request, object_id=object_id, form_url=form_url, extra_context=extra_context
                )

            try:
                match_or_create_snelstart_relatie_with_name(snelstart_client, customer, Mutation.TRIGGER_MANUAL)
                self.message_user(
                    request,
                    f"Successfully synchronized customer to Snelstart!",
                    level=messages.SUCCESS,
                )
            except SynchronizationError as e:
                self.message_user(
                    request,
                    f"Failed to synchronize customer to Snelstart: {e}.",
                    level=messages.WARNING,
                )

            opts = obj._meta
            obj_url = reverse(
                "admin:%s_%s_change" % (opts.app_label, opts.model_name),
                args=(quote(obj.pk),),
                current_app=self.admin_site.name,
            )
            return HttpResponseRedirect(obj_url)

        return super(CustomerAdmin, self).changeform_view(
            request, object_id=object_id, form_url=form_url, extra_context=extra_context
        )
