from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.utils import quote
from django.http import HttpResponseRedirect
from django.urls import reverse

from customers.models import Customer
from customers.services import match_or_create_snelstart_relatie_with_name
from mode_groothandel.clients.api import ApiException
from mode_groothandel.exceptions import SynchronizationError
from mutations.admin import MutationInline
from mutations.models import Mutation
from snelstart.clients.snelstart import Snelstart
from uphance.clients.uphance import Uphance


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Customer Admin."""

    search_fields = ["uphance_name", "uphance_id", "snelstart_name", "snelstart_id"]

    list_display = [
        "uphance_name",
        "uphance_id",
        "snelstart_id",
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
