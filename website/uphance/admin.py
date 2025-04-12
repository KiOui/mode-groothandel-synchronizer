from django.contrib import admin
from autocompletefilter.admin import AutocompleteFilterMixin

from uphance.models import Country


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
