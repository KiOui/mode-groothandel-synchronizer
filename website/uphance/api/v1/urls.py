from django.urls import path

from uphance.api.v1.views import InvoiceCreateUpdateDeleteApiView

urlpatterns = [
    path("invoices/", InvoiceCreateUpdateDeleteApiView.as_view(), name="uphance_invoice_create_update_destroy_view"),
]
