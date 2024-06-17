import logging

from django.conf import settings
from django.core.management import BaseCommand

from customers.services import match_or_create_snelstart_relatie_with_name
from mode_groothandel.exceptions import SynchronizationError
from mutations.models import Mutation
from snelstart.clients.snelstart import Snelstart
from uphance.clients.uphance import Uphance

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Synchronize customers to Snelstart."""

    def handle(self, *args, **options):
        """Execute the command."""
        uphance_client = Uphance.get_client()
        if not uphance_client.set_current_organisation(settings.UPHANCE_ORGANISATION):
            logger.error("Unable to set the Uphance Organisation")
            return

        snelstart_client = Snelstart.get_client()

        next_page = 1

        while next_page is not None:
            customers = uphance_client.customers(page=next_page)
            for customer in customers.objects:
                try:
                    match_or_create_snelstart_relatie_with_name(snelstart_client, customer, Mutation.TRIGGER_MANUAL)
                except SynchronizationError as e:
                    print(e)

            next_page = customers.meta.next_page
