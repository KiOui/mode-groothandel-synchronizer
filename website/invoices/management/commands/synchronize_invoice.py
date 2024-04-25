import logging

from django.conf import settings
from django.core.management import BaseCommand

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

        print(snelstart_client.get_grootboeken())

        """

        for i in range(invoice_id, invoice_id + 100):
            invoice = uphance_client.invoice(i)

            if invoice is None:
                logger.error(f"Invoice with ID {invoice_id} could not be found")
                # return
            else:
                print(uphance_client.customer_by_id(invoice.company_id))
        
        """
