import logging

from django.conf import settings
from django.core.management import BaseCommand

from invoices.services import setup_invoice_for_synchronisation
from snelstart.clients.snelstart import Snelstart
from uphance.clients.uphance import Uphance

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Retrieve Uphance organisations."""

    def handle(self, *args, **options):
        """Execute the command."""
        uphance_client = Uphance.get_client()
        if not uphance_client.set_current_organisation(settings.UPHANCE_ORGANISATION):
            logger.error("Unable to set the Uphance Organisation")
            return

        invoice_id = 798000

        snelstart_client = Snelstart.get_client()

        invoice = uphance_client.invoice(invoice_id)
        invoice_converted = setup_invoice_for_synchronisation(uphance_client, snelstart_client, invoice)
        print(invoice_converted)
        snelstart_client.add_verkoopboeking(invoice_converted)
