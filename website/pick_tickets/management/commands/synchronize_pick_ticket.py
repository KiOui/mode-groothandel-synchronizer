import logging
import re
import time
from typing import Optional

from django.conf import settings
from django.core.management import BaseCommand

from mode_groothandel.clients.api import ApiException
from mode_groothandel.exceptions import SynchronizationError
from mutations.models import Mutation
from pick_tickets.services import try_create_pick_ticket
from sendcloud.client.sendcloud import Sendcloud
from uphance.clients.uphance import Uphance

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Synchronize pick tickets."""

    def parse_pick_tickets_argument(self, invoices_raw: str) -> Optional[range]:
        """Parse the 'pick-tickets' command line argument."""
        regex = r"^(?P<pick_ticket_start>\d+)(?:-(?P<pick_ticket_end>\d+))?$"
        match = re.fullmatch(regex, invoices_raw)

        if match is None:
            logger.error("'pick-tickets' command line argument could not be parsed successfully.")
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
        parser.add_argument("pick-tickets", type=str)
        parser.add_argument("--sleep", type=int, default=None)
        parser.add_argument("--sleep-every", type=int, default=None)

    def handle(self, *args, **options):
        """Execute the command."""
        pick_tickets = self.parse_pick_tickets_argument(options["pick-tickets"])
        sleep_seconds = options["sleep"]
        sleep_every = options["sleep_every"]
        if pick_tickets is None:
            return

        uphance_client = Uphance.get_client()
        if not uphance_client.set_current_organisation(settings.UPHANCE_ORGANISATION):
            logger.error("Unable to set the Uphance Organisation")
            return

        sendlcloud_client = Sendcloud.get_client()
        for index, pick_ticket_id in enumerate(pick_tickets):
            try:
                pick_ticket = uphance_client.pick_ticket(pick_ticket_id)
                try:
                    try_create_pick_ticket(sendlcloud_client, pick_ticket, Mutation.TRIGGER_MANUAL)
                    print(f"Successfully synchronized pick ticket {pick_ticket}")
                except SynchronizationError as e:
                    logger.error(e)
            except ApiException as e:
                logger.error(f"An API exception occurred while synchronizing pick ticket {pick_ticket_id}: {e}")
            if sleep_seconds is not None:
                if sleep_every is None:
                    print(f"Sleeping for {sleep_seconds} seconds")
                    time.sleep(sleep_seconds)
                elif index != 0 and index % sleep_every == 0:
                    print(f"Sleeping for {sleep_seconds} seconds")
                    time.sleep(sleep_seconds)
