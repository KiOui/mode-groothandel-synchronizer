from django.urls import path

from uphance.api.v1.views import (
    InvoiceCreateUpdateDeleteApiView,
    CreditNoteCreateUpdateDeleteApiView,
    PickTicketCreateUpdateDeleteApiView,
)

urlpatterns = [
    path("invoices/", InvoiceCreateUpdateDeleteApiView.as_view(), name="uphance_invoice_create_update_destroy_view"),
    path(
        "credit_notes/",
        CreditNoteCreateUpdateDeleteApiView.as_view(),
        name="uphance_credit_note_create_update_destroy_view",
    ),
    path(
        "pick_tickets/",
        PickTicketCreateUpdateDeleteApiView.as_view(),
        name="uphance_pick_ticket_create_update_destroy_view",
    ),
]
