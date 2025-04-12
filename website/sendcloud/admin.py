from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from sendcloud.models import CachedCountry, CachedShippingMethod


@admin.register(CachedCountry)
class CachedCountryAdmin(admin.ModelAdmin):
    search_fields = ("sendcloud_id", "name", "iso_2", "iso_3")
    list_display = ("sendcloud_id", "name", "iso_2", "iso_3")


@admin.register(CachedShippingMethod)
class CachedShippingMethodAdmin(AutocompleteFilterMixin, admin.ModelAdmin):
    list_filter = (
        ("countries", AutocompleteListFilter),
        "carrier",
    )
    search_fields = ("sendcloud_id", "name", "carrier")
    list_display = ("sendcloud_id", "name", "carrier")

    class Meta:
        """Necessary for AutocompleteListFilter."""
