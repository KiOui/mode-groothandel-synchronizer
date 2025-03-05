import logging
import re
import time
from typing import Optional

from django.conf import settings
from django.core.management import BaseCommand

from invoices.services import try_create_invoice
from mode_groothandel.clients.api import ApiException
from mutations.models import Mutation
from snelstart.clients.snelstart import Snelstart
from uphance.clients.uphance import Uphance

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Retrieve Uphance organisations."""

    def parse_invoices_argument(self, invoices_raw: str) -> Optional[range]:
        """Parse the 'invoices' command line argument."""
        regex = r"^(?P<invoice_start>\d+)(?:-(?P<invoice_end>\d+))?$"
        match = re.fullmatch(regex, invoices_raw)

        if match is None:
            logger.error("'invoices' command line argument could not be parsed successfully.")
            return None

        groups = match.groups()
        start = groups[0]
        end = groups[1]
        if end is None:
            return range(int(start), int(start) + 1)
        else:
            return range(int(start), int(end))

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument("invoices", type=str)
        parser.add_argument("--sleep", type=int, default=None)
        parser.add_argument("--sleep-every", type=int, default=None)

    def handle(self, *args, **options):
        """Execute the command."""
        invoices = self.parse_invoices_argument(options["invoices"])
        sleep_seconds = options["sleep"]
        sleep_every = options["sleep_every"]
        if invoices is None:
            return

        uphance_client = Uphance.get_client()
        if not uphance_client.set_current_organisation(settings.UPHANCE_ORGANISATION):
            logger.error("Unable to set the Uphance Organisation")
            return

        snelstart_client = Snelstart.get_client()
        for index, invoice_id in enumerate(invoices):
            try:
                invoice = uphance_client.invoice(invoice_id)
                if invoice is not None:
                    try_create_invoice(uphance_client, snelstart_client, invoice, Mutation.TRIGGER_MANUAL)
                else:
                    logger.warning(f"Invoice {invoice_id} was not found in Uphance!")
            except ApiException as e:
                logger.error(f"An API exception occurred while synchronizing invoice {invoice_id}: {e}")
            if sleep_seconds is not None:
                if sleep_every is None:
                    print(f"Sleeping for {sleep_seconds} seconds")
                    time.sleep(sleep_seconds)
                elif index != 0 and index % sleep_every == 0:
                    print(f"Sleeping for {sleep_seconds} seconds")
                    time.sleep(sleep_seconds)
