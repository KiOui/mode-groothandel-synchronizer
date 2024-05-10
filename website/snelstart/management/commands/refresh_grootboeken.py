import logging

from django.core.management import BaseCommand

from snelstart.services import refresh_cached_grootboeken

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Refresh Cached Grootboeken."""

    def handle(self, *args, **options):
        """Execute the command."""
        (created, updated, deleted) = refresh_cached_grootboeken()

        print(f"Cached Grootboeken refreshed\nCreated: {created}\nUpdated: {updated}\nDeleted: {deleted}")
