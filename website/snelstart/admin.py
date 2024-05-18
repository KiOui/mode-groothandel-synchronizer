from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.html import format_html

from mode_groothandel.clients.api import ApiException
from snelstart.forms import TaxMappingAdminForm
from snelstart.models import TaxMapping
from snelstart.services import refresh_cached_tax_types, refresh_cached_grootboeken


@admin.register(TaxMapping)
class TaxMappingAdmin(admin.ModelAdmin):

    list_display = ("name", "tax_amount", "grootboekcode", "grootboekcode_shipping")

    form = TaxMappingAdminForm
    exclude = ("tax_amount",)

    def _should_refresh_tax_types(self, request):
        """Whether a tax type refresh should happen."""
        return "_refresh_tax_types" in request.POST

    def _should_refresh_grootboekcodes(self, request):
        """Whether a grootboekcode refresh should happen."""
        return "_refresh_grootboekcodes" in request.POST

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
        else:
            return super(TaxMappingAdmin, self).changeform_view(
                request, object_id=object_id, form_url=form_url, extra_context=extra_context
            )
