from django.contrib import admin

from snelstart.models import CachedLand


@admin.register(CachedLand)
class CachedLandAdmin(admin.ModelAdmin):
    search_fields = ("naam", "landcode", "landcode_iso")
    list_display = ("naam", "landcode")
