from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from invoices.services import try_create_invoice, try_delete_invoice, try_update_invoice
from mutations.models import Mutation
from snelstart.clients.snelstart import Snelstart
from uphance.clients.models.invoice import Invoice as UphanceInvoice
from uphance.clients.uphance import Uphance


class InvoiceCreateUpdateDeleteApiView(APIView):
    """Invoice Create Update Delete API View."""

    def check_permissions(self, request):
        """Check if requester has permissions."""
        expected_secret = settings.UPHANCE_SECRET
        if expected_secret is None:
            return True

        request_secret = request.GET.get("secret", None)
        if request_secret is None or request_secret != expected_secret:
            return False

        return True

    def _create_invoice(self, invoice: dict) -> None:
        """Create an invoice in Snelstart."""
        invoice = UphanceInvoice.from_data(invoice)
        uphance_client = Uphance.get_client()
        snelstart_client = Snelstart.get_client()
        try_create_invoice(uphance_client, snelstart_client, invoice, Mutation.TRIGGER_WEBHOOK)

    def _delete_invoice(self, invoice: dict):
        """Delete an invoice from Snelstart."""
        invoice = UphanceInvoice.from_data(invoice)
        snelstart_client = Snelstart.get_client()
        try_delete_invoice(snelstart_client, invoice, Mutation.TRIGGER_WEBHOOK)

    def _update_invoice(self, invoice: dict):
        """Update an invoice in Snelstart."""
        invoice = UphanceInvoice.from_data(invoice)
        uphance_client = Uphance.get_client()
        snelstart_client = Snelstart.get_client()
        try_update_invoice(uphance_client, snelstart_client, invoice, Mutation.TRIGGER_WEBHOOK)

    def post(self, request):
        """Handle a request from Uphance."""
        event = request.data.get("event", None)
        if event is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        invoice = request.data.get("invoice", None)
        if invoice is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event == "invoice_create":
            self._create_invoice(invoice)
        elif event == "invoice_update":
            self._update_invoice(invoice)
        elif event == "invoice_delete":
            self._delete_invoice(invoice)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
