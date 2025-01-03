import logging
from functools import cmp_to_key

from django.core.management import BaseCommand

from mode_groothandel.clients.api import ApiException
from snelstart.clients.models.btw_tarief import BtwTarief
from snelstart.clients.snelstart import Snelstart

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Retrieve Uphance organisations."""

    def handle(self, *args, **options):
        """Execute the command."""
        snelstart_client = Snelstart.get_client()

        try:
            btw_types = snelstart_client.get_btwtarieven()
        except ApiException as err:
            logger.error(f"An API Exception occurred: {err}")
            return

        def compare(btw_type_1: BtwTarief, btw_type_2: BtwTarief) -> int:
            if btw_type_1.btw_soort == btw_type_2.btw_soort:
                return btw_type_1.datum_vanaf < btw_type_2.datum_vanaf
            else:
                return btw_type_1.btw_soort < btw_type_2.btw_soort

        btw_types = sorted(btw_types, key=cmp_to_key(compare))

        for btw_type in btw_types:
            print(f'"{btw_type.btw_soort}" ({btw_type.btw_percentage}%) from {btw_type.datum_vanaf}')
