from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from credit_notes.services import try_create_credit_note, try_delete_credit_note, try_update_credit_note
from invoices.services import try_create_invoice, try_delete_invoice, try_update_invoice
from mode_groothandel.clients.utils import get_value_or_error
from mutations.models import Mutation
from pick_tickets.services import (
    try_create_pick_ticket,
    try_delete_pick_ticket,
    try_update_pick_ticket,
    try_create_or_update_pick_ticket,
)
from sendcloud.client.sendcloud import Sendcloud
from snelstart.clients.snelstart import Snelstart
from uphance.clients.models.invoice import Invoice as UphanceInvoice
from uphance.clients.models.credit_note import CreditNote as UphanceCreditNote
from uphance.clients.models.pick_ticket import PickTicket as UphancePickTicket
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
        invoice_id = get_value_or_error(invoice, "id")
        snelstart_client = Snelstart.get_client()
        try_delete_invoice(snelstart_client, invoice_id, Mutation.TRIGGER_WEBHOOK)

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


class CreditNoteCreateUpdateDeleteApiView(APIView):
    """Credit Note Create Update Delete API View."""

    def check_permissions(self, request):
        """Check if requester has permissions."""
        expected_secret = settings.UPHANCE_SECRET
        if expected_secret is None:
            return True

        request_secret = request.GET.get("secret", None)
        if request_secret is None or request_secret != expected_secret:
            return False

        return True

    def _create_credit_note(self, credit_note: dict) -> None:
        """Create a credit note in Snelstart."""
        credit_note = UphanceCreditNote.from_data(credit_note)
        uphance_client = Uphance.get_client()
        snelstart_client = Snelstart.get_client()
        try_create_credit_note(uphance_client, snelstart_client, credit_note, Mutation.TRIGGER_WEBHOOK)

    def _delete_credit_note(self, credit_note: dict):
        """Delete a credit note from Snelstart."""
        credit_note_id = get_value_or_error(credit_note, "id")
        snelstart_client = Snelstart.get_client()
        try_delete_credit_note(snelstart_client, credit_note_id, Mutation.TRIGGER_WEBHOOK)

    def _update_credit_note(self, credit_note: dict):
        """Update a credit note in Snelstart."""
        credit_note = UphanceCreditNote.from_data(credit_note)
        uphance_client = Uphance.get_client()
        snelstart_client = Snelstart.get_client()
        try_update_credit_note(uphance_client, snelstart_client, credit_note, Mutation.TRIGGER_WEBHOOK)

    def post(self, request):
        """Handle a request from Uphance."""
        event = request.data.get("event", None)
        if event is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        credit_note = request.data.get("credit_note", None)
        if credit_note is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event == "credit_note_create":
            self._create_credit_note(credit_note)
        elif event == "credit_note_update":
            self._update_credit_note(credit_note)
        elif event == "credit_note_delete":
            self._delete_credit_note(credit_note)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


class PickTicketCreateUpdateDeleteApiView(APIView):
    """Pick Ticket Create Update Delete API View."""

    def check_permissions(self, request):
        """Check if requester has permissions."""
        expected_secret = settings.UPHANCE_SECRET
        if expected_secret is None:
            return True

        request_secret = request.GET.get("secret", None)
        if request_secret is None or request_secret != expected_secret:
            return False

        return True

    def _create_pick_ticket(self, pick_ticket: dict) -> None:
        """Create a pick ticket in Sendcloud."""
        pick_ticket = UphancePickTicket.from_data(pick_ticket)
        sendcloud_client = Sendcloud.get_client()
        try_create_pick_ticket(sendcloud_client, pick_ticket, Mutation.TRIGGER_WEBHOOK)

    def _delete_pick_ticket(self, pick_ticket: dict):
        """Delete a pick ticket from Sendcloud."""
        pick_ticket_id = get_value_or_error(pick_ticket, "id")
        sendcloud_client = Sendcloud.get_client()
        try_delete_pick_ticket(sendcloud_client, pick_ticket_id, Mutation.TRIGGER_WEBHOOK)

    def _create_or_update_pick_ticket(self, pick_ticket: dict):
        """Create or update a pick ticket in Sendcloud."""
        pick_ticket = UphancePickTicket.from_data(pick_ticket)
        sendcloud_client = Sendcloud.get_client()
        try_create_or_update_pick_ticket(sendcloud_client, pick_ticket, Mutation.TRIGGER_WEBHOOK)

    def post(self, request):
        """Handle a request from Uphance."""
        event = request.data.get("event", None)
        if event is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        pick_ticket = request.data.get("pick_ticket", None)
        if pick_ticket is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event == "pick_ticket_create":
            self._create_pick_ticket(pick_ticket)
        elif event == "pick_ticket_update":
            self._create_or_update_pick_ticket(pick_ticket)
        elif event == "pick_ticket_delete":
            self._delete_pick_ticket(pick_ticket)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
