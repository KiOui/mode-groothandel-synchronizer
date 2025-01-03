import logging

from django.core.management import BaseCommand

from snelstart.services import refresh_cached_tax_types

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Refresh Cached Tax Types."""

    def handle(self, *args, **options):
        """Execute the command."""
        (created, updated, deleted) = refresh_cached_tax_types()

        print(f"Cached BTW Tarieven refreshed\nCreated: {created}\nUpdated: {updated}\nDeleted: {deleted}")
