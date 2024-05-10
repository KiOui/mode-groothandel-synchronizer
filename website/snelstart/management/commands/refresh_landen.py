import logging

from django.core.management import BaseCommand

from snelstart.services import refresh_landen

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Refresh Cached Tax Types."""

    def handle(self, *args, **options):
        """Execute the command."""
        (created, updated, deleted) = refresh_landen()

        print(f"Cached BTW Tarieven refreshed\nCreated: {created}\nUpdated: {updated}\nDeleted: {deleted}")
