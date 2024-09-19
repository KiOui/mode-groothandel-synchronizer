import logging
from time import sleep
from typing import Optional

from django.conf import settings
from django.core.management import BaseCommand

from customers.services import match_or_create_snelstart_relatie_with_name, convert_uphance_customer_to_relatie
from mode_groothandel.clients.api import ApiException
from mode_groothandel.exceptions import SynchronizationError
from mutations.models import Mutation
from snelstart.clients.snelstart import Snelstart
from uphance.clients.uphance import Uphance

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Synchronize customers to Snelstart."""

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument("--customer", type=int, required=False)
        parser.add_argument("--timeout", type=int, required=False)

    def handle(self, *args, **options):
        """Execute the command."""
        uphance_client = Uphance.get_client()
        if not uphance_client.set_current_organisation(settings.UPHANCE_ORGANISATION):
            logger.error("Unable to set the Uphance Organisation")
            return

        snelstart_client = Snelstart.get_client()

        if options["customer"] is not None:
            try:
                customer = uphance_client.customer_by_id(options["customer"])
            except ApiException as err:
                print(f"Failed to retrieve customer: {err}")
                return
            match_or_create_snelstart_relatie_with_name(snelstart_client, customer, Mutation.TRIGGER_MANUAL)
            return
        else:
            next_page = 1

            counter_processed = 0
            counter_errors = 0

            while next_page is not None:
                customers = uphance_client.customers(page=next_page)
                for customer in customers.objects:
                    try:
                        match_or_create_snelstart_relatie_with_name(
                            snelstart_client, customer, Mutation.TRIGGER_MANUAL
                        )
                    except SynchronizationError as e:
                        counter_errors += 1
                        print(e)
                    counter_processed += 1

                next_page = customers.meta.next_page
                if next_page is not None and options["timeout"] is not None:
                    print("Sleeping {} seconds.".format(options["timeout"]))
                    sleep(options["timeout"])

            counter_success = counter_processed - counter_errors

            print(f"Synchronized {counter_success} out of {counter_processed} customers ({counter_errors} errors)")
