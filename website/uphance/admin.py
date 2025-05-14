from django.contrib import admin, messages
from autocompletefilter.admin import AutocompleteFilterMixin
from django.http import HttpResponseRedirect
from django.utils.html import format_html

from mode_groothandel.clients.api import ApiException
from snelstart.services import refresh_cached_tax_types, refresh_cached_grootboeken
from uphance.forms import TaxMappingAdminForm
from uphance.models import Country, TaxMapping, ChannelMapping
from uphance.services import refresh_cached_channels


@admin.register(Country)
class CountryAdmin(AutocompleteFilterMixin, admin.ModelAdmin):
    search_fields = ("country_code",)
    list_display = (
        "country_code",
        "mapped_shipping_method_for_pick_tickets",
        "mapped_country_code_in_snelstart",
    )
    autocomplete_fields = (
        "mapped_country_code_in_snelstart",
        "mapped_shipping_method_for_pick_tickets",
    )


class TaxMappingInline(admin.StackedInline):
    model = TaxMapping
    form = TaxMappingAdminForm
    extra = 0


@admin.register(ChannelMapping)
class ChannelMappingAdmin(admin.ModelAdmin):
    list_display = ("channel",)
    inlines = (TaxMappingInline,)

    def _should_refresh_tax_types(self, request):
        """Whether a tax type refresh should happen."""
        return "_refresh_tax_types" in request.POST

    def _should_refresh_grootboekcodes(self, request):
        """Whether a grootboekcode refresh should happen."""
        return "_refresh_grootboekcodes" in request.POST

    def _should_refresh_channels(self, request):
        """Whether a channel refresh should happen."""
        return "_refresh_channels" in request.POST

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Add extra action to admin post request."""
        if self._should_refresh_tax_types(request):
            try:
                refresh_cached_tax_types()
                pass
            except ApiException as e:
                self.message_user(
                    request,
                    format_html(f"Failed to refresh tax types from Snelstart: {e}"),
                    level=messages.ERROR,
                )
            redirect_url = request.path
            return HttpResponseRedirect(redirect_url)
        elif self._should_refresh_grootboekcodes(request):
            try:
                refresh_cached_grootboeken()
                pass
            except ApiException as e:
                self.message_user(
                    request,
                    format_html(f"Failed to refresh grootboekcodes from Snelstart: {e}"),
                    level=messages.ERROR,
                )
            redirect_url = request.path
            return HttpResponseRedirect(redirect_url)
        elif self._should_refresh_channels(request):
            try:
                refresh_cached_channels()
                pass
            except ApiException as e:
                self.message_user(
                    request,
                    format_html(f"Failed to refresh channels from Uphance: {e}"),
                    level=messages.ERROR,
                )
            redirect_url = request.path
            return HttpResponseRedirect(redirect_url)
        else:
            return super(ChannelMappingAdmin, self).changeform_view(
                request, object_id=object_id, form_url=form_url, extra_context=extra_context
            )
