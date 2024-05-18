import logging

from django.conf import settings
from django.core.management import BaseCommand

from mode_groothandel.clients.api import ApiException
from sendcloud.client.sendcloud import Sendcloud
from snelstart.clients.snelstart import Snelstart
from uphance.clients.uphance import Uphance

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Retrieve Sendcloud shipping methods."""

    def handle(self, *args, **options):
        """Execute the command."""
        sendcloud_client = Sendcloud.get_client()

        try:
            shipping_methods = sendcloud_client.get_shipping_methods()
        except ApiException as err:
            logger.error(f"An API Exception occurred: {err}")
            return

        for shipping_method in shipping_methods:
            print(f"{shipping_method.name} ({shipping_method.carrier}) - {shipping_method.id}")
