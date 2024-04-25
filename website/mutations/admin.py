from django.contrib import admin


class MutationsAdmin(admin.ModelAdmin):

    search_fields = ["on"]

    list_filter = [
        "success",
        "method",
        "content_type",
    ]
