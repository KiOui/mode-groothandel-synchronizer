from django.urls import path, include

app_name = "mode_groothandel"

urlpatterns = [
    path("uphance/", include("uphance.api.v1.urls")),
]
