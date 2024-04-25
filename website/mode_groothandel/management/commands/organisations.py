import logging

from django.core.management import BaseCommand

from mode_groothandel.clients.uphance import Uphance

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Retrieve Uphance organisations."""

    def handle(self, *args, **options):
        """Execute the command."""
        uphance_client = Uphance.get_client()
        print(uphance_client.organisations())
