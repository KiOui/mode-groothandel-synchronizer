import logging

from django.core.management import BaseCommand

from mode_groothandel.clients.api import ApiException
from snelstart.clients.snelstart import Snelstart

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Retrieve Uphance organisations."""

    def handle(self, *args, **options):
        """Execute the command."""
        snelstart_client = Snelstart.get_client()

        try:
            grootboeken = snelstart_client.get_grootboeken()
        except ApiException as err:
            logger.error(f"An API Exception occurred: {err}")
            return

        grootboeken.sort(key=lambda x: x.nummer)

        for grootboek in grootboeken:
            print(f"{grootboek.omschrijving} - {grootboek.rekening_code} ({grootboek.nummer}): {grootboek.id}")
