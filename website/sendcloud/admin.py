from django.contrib import admin
from sendcloud.models import CachedCountry, CachedShippingMethod


@admin.register(CachedCountry)
class CachedCountryAdmin(admin.ModelAdmin):
    search_fields = ("sendcloud_id", "name", "iso_2", "iso_3")
    list_display = ("sendcloud_id", "name", "iso_2", "iso_3")


@admin.register(CachedShippingMethod)
class CachedShippingMethodAdmin(admin.ModelAdmin):
    list_filter = ("carrier",)
    search_fields = ("sendcloud_id", "name", "carrier")
    list_display = ("sendcloud_id", "name", "carrier")
