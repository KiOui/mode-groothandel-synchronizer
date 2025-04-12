import logging

from django.core.management import BaseCommand

from sendcloud.services import refresh_shipping_methods

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Retrieve Sendcloud shipping methods."""

    def handle(self, *args, **options):
        """Execute the command."""
        (created, updated, deleted) = refresh_shipping_methods()

        print(f"Cached shipping methods refreshed\nCreated: {created}\nUpdated: {updated}\nDeleted: {deleted}")
