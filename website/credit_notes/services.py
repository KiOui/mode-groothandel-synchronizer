import logging
from typing import List, Dict, Any, Tuple

from credit_notes.models import CreditNote
from invoices.services import round_half_up
from mode_groothandel.clients.api import ApiException
from mode_groothandel.exceptions import SynchronizationError
from customers.services import match_or_create_snelstart_relatie_with_name
from mutations.models import Mutation
from snelstart.clients.snelstart import Snelstart
from snelstart.constants import BTW_VERKOPEN_PREFIX
from uphance.clients.models.credit_note import CreditNote as UphanceCreditNote
from uphance.clients.uphance import Uphance
from uphance.models import TaxMapping
from django.conf import settings

logger = logging.getLogger(__name__)


def construct_order_and_tax_line_items(
    credit_note: UphanceCreditNote,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """Construct order and tax line items for a credit note from Uphance."""
    # TODO: The credit notes do not communicate the channel IDs yet. This should be resolved by Uphance after which
    #  this method needs to get adjusted.
    channel_id = settings.HARDCODED_CREDIT_NOTES_CHANNEL_ID

    to_order = list()
    # Dictionary mapping tax percentages to the total amount to compute the tax over.
    compute_tax_over_amount = dict()
    # The tax mappings belonging to the channel of the credit note.
    filtered_tax_mappings = TaxMapping.objects.filter(channel_mapping__channel__channel_id=channel_id)
    for item in credit_note.line_items:
        amount = sum([x.quantity for x in item.line_quantities])

        total_price_line = item.unit_price * amount

        if total_price_line != 0:
            try:
                tax_mapping = filtered_tax_mappings.get(tax_amount__btw_percentage=item.tax_level)
            except TaxMapping.DoesNotExist:
                raise SynchronizationError(
                    f"Tax mapping for tax amount {item.tax_level} in channel {channel_id} does not exist"
                )
            except TaxMapping.MultipleObjectsReturned:
                raise SynchronizationError(
                    f"Multiple tax mappings for tax amount {item.tax_level} in channel {channel_id} exist"
                )

            to_order.append(
                {
                    "omschrijving": f"{amount} x {item.product_id} {item.product_name}",
                    "grootboek": {
                        "id": str(tax_mapping.grootboekcode),
                    },
                    "bedrag": "{:.2f}".format(total_price_line),
                    "btwSoort": tax_mapping.tax_amount.btw_soort,
                }
            )

            if tax_mapping in compute_tax_over_amount.keys():
                compute_tax_over_amount[tax_mapping] = compute_tax_over_amount[tax_mapping] + total_price_line
            else:
                compute_tax_over_amount[tax_mapping] = total_price_line

    if credit_note.freeform_amount is not None and credit_note.freeform_amount != 0:
        # Add a fake line item for the freeform amount.
        computed_tax_level = credit_note.freeform_tax / (credit_note.freeform_amount / 100)
        computed_tax_level_2_decimals = "{:.1f}".format(computed_tax_level)

        try:
            tax_mapping = filtered_tax_mappings.get(tax_amount=float(computed_tax_level_2_decimals))
        except TaxMapping.DoesNotExist:
            raise SynchronizationError(
                f"Error finding tax mapping for freeform amount: Tax mapping for computed tax amount "
                f"{computed_tax_level_2_decimals} and channel {channel_id} does not exist"
            )

        total_price_line = credit_note.freeform_amount * -1

        to_order.append(
            {
                "omschrijving": f"Freeform ({credit_note.freeform_description})",
                "grootboek": {
                    "id": str(tax_mapping.grootboekcode),
                },
                "bedrag": "{:.2f}".format(credit_note.freeform_amount * -1),
                "btwSoort": tax_mapping.tax_amount.btw_soort,
            }
        )

        if tax_mapping in compute_tax_over_amount.keys():
            compute_tax_over_amount[tax_mapping] = compute_tax_over_amount[tax_mapping] + total_price_line
        else:
            compute_tax_over_amount[tax_mapping] = total_price_line

    # Calculate the tax.
    tax_lines = dict()

    for tax_mapping, total_amount_to_compute_tax_over in compute_tax_over_amount.items():
        tax_lines[tax_mapping.tax_amount.btw_soort] = (
            total_amount_to_compute_tax_over * tax_mapping.tax_amount.btw_percentage / 100
        )

    tax_lines = [
        # Round tax amount by 2 digits.
        {"btwSoort": BTW_VERKOPEN_PREFIX + tax_name, "btwBedrag": "{:.2f}".format(round_half_up(tax_amount, 2))}
        for (tax_name, tax_amount) in tax_lines.items()
        if tax_amount != 0
    ]

    return to_order, tax_lines


def setup_credit_note_for_synchronisation(
    uphance_client: Uphance, snelstart_client: Snelstart, credit_note: UphanceCreditNote, trigger
) -> dict:
    """Setup a credit note from Uphance for synchronisation to Snelstart."""
    try:
        orders = uphance_client.orders(credit_note.order_number)
    except ApiException as e:
        raise SynchronizationError(f"An error occurred while requesting order number {credit_note.order_number}: {e}")

    if len(orders.objects) > 0:
        order = orders.objects[0]
    else:
        raise SynchronizationError(
            f"Retrieved {len(orders.objects)} orders for credit note {credit_note.id} where one was expected"
        )
    try:
        customer = uphance_client.customer_by_id(order.company_id)
    except ApiException as e:
        raise SynchronizationError(
            f"An error occurred while requesting customer with company id {order.company_id}: {e}"
        )

    # Make line item prices negative because we are computing a credit note.
    credit_note.grand_total = credit_note.grand_total * -1

    for line_item in credit_note.line_items:
        line_item.unit_tax = line_item.unit_tax * -1
        line_item.unit_price = line_item.unit_price * -1
        line_item.original_price = line_item.original_price * -1

    grootboek_regels, tax_lines = construct_order_and_tax_line_items(credit_note)
    snelstart_relatie_for_order = match_or_create_snelstart_relatie_with_name(snelstart_client, customer, trigger)

    if snelstart_relatie_for_order is None:
        raise SynchronizationError(
            f"Failed to synchronize credit note {credit_note.credit_note_number} because customer {customer.name} "
            f"could not be found or created in Snelstart."
        )

    result = {
        "factuurnummer": credit_note.credit_note_number,
        "klant": {"id": str(snelstart_relatie_for_order.id)},
        "boekingsregels": grootboek_regels,
        "factuurbedrag": "{:.2f}".format(credit_note.grand_total),
        "betalingstermijn": 0,
        "factuurdatum": credit_note.created_at.strftime("%Y-%m-%d %H:%I:%S"),
        "btw": tax_lines,
    }
    return result


def get_or_create_credit_note_in_database(credit_note: UphanceCreditNote) -> CreditNote:
    try:
        return CreditNote.objects.get(uphance_id=credit_note.id)
    except CreditNote.DoesNotExist:
        return CreditNote.objects.create(
            uphance_id=credit_note.id,
            credit_note_number=credit_note.credit_note_number,
            credit_note_total=credit_note.items_total + credit_note.items_tax,
        )


def try_delete_credit_note(snelstart_client: Snelstart, credit_note_id: int, trigger: int) -> None:
    try:
        credit_note_in_database = CreditNote.objects.get(uphance_id=credit_note_id)
    except CreditNote.DoesNotExist:
        credit_note_in_database = CreditNote.objects.create(
            uphance_id=credit_note_id,
        )
    if credit_note_in_database.snelstart_id is None:
        Mutation.objects.create(
            method=Mutation.METHOD_DELETE,
            trigger=trigger,
            on=credit_note_in_database,
            success=False,
            message=f"Unable to delete credit note {credit_note_id} because no Snelstart ID was found in the database",
        )

    try:
        snelstart_client.delete_verkoopboeking(credit_note_in_database.snelstart_id)
        Mutation.objects.create(
            method=Mutation.METHOD_DELETE,
            trigger=trigger,
            on=credit_note_in_database,
            success=True,
            message=None,
        )
    except ApiException as e:
        Mutation.objects.create(
            method=Mutation.METHOD_DELETE,
            trigger=trigger,
            on=credit_note_in_database,
            success=False,
            message=f"An API error occurred for credit note {credit_note_id}: {e}",
        )


def try_update_credit_note(
    uphance_client: Uphance, snelstart_client: Snelstart, credit_note: UphanceCreditNote, trigger: int
) -> None:
    credit_note_in_database = get_or_create_credit_note_in_database(credit_note)

    credit_note_in_database.credit_note_number = credit_note.credit_note_number
    credit_note_in_database.credit_note_total = credit_note.items_total + credit_note.items_tax
    credit_note_in_database.save()

    if credit_note_in_database.snelstart_id is None:
        Mutation.objects.create(
            method=Mutation.METHOD_UPDATE,
            trigger=trigger,
            on=credit_note_in_database,
            success=False,
            message=f"Unable to update credit note {credit_note.id} because no Snelstart ID was found in the database",
        )
        return

    try:
        credit_note_converted = setup_credit_note_for_synchronisation(
            uphance_client, snelstart_client, credit_note, trigger
        )
        try:
            snelstart_client.update_verkoopboeking(credit_note_in_database.snelstart_id, credit_note_converted)
        except ApiException as e:
            raise SynchronizationError(
                f"An error occurred while updating verkoopboeking {credit_note_in_database.snelstart_id} for credit "
                f"note {credit_note.id} in Snelstart: {e}"
            )
        logger.info(f"Successfully updated credit note {credit_note.id}")
        Mutation.objects.create(
            method=Mutation.METHOD_UPDATE,
            trigger=trigger,
            on=credit_note_in_database,
            success=True,
            message=None,
        )
    except SynchronizationError as e:
        logger.error(f"A Synchronization error occurred while updating credit note {credit_note.id}: {e}")
        Mutation.objects.create(
            method=Mutation.METHOD_UPDATE,
            trigger=trigger,
            on=credit_note_in_database,
            success=False,
            message=f"A Synchronization error occurred while updating credit note {credit_note.id}: {e}",
        )


def try_create_credit_note(
    uphance_client: Uphance, snelstart_client: Snelstart, credit_note: UphanceCreditNote, trigger: int
) -> None:
    credit_note_in_database = get_or_create_credit_note_in_database(credit_note)

    try:
        credit_note_converted = setup_credit_note_for_synchronisation(
            uphance_client, snelstart_client, credit_note, trigger
        )
        try:
            verkoopboeking = snelstart_client.add_verkoopboeking(credit_note_converted)
        except ApiException as e:
            raise SynchronizationError(
                f"An error occurred while adding a verkoopboeking for credit note {credit_note.credit_note_number} to "
                f"Snelstart: {e}"
            )

        logger.info(f"Successfully synchronized credit note {credit_note.id}")

        credit_note_in_database.snelstart_id = verkoopboeking["id"]
        credit_note_in_database.save()
        Mutation.objects.create(
            method=Mutation.METHOD_CREATE,
            trigger=trigger,
            on=credit_note_in_database,
            success=True,
            message=None,
        )
    except SynchronizationError as e:
        logger.error(f"A Synchronization error occurred for credit note {credit_note.id}: {e}")
        Mutation.objects.create(
            method=Mutation.METHOD_CREATE,
            trigger=trigger,
            on=credit_note_in_database,
            success=False,
            message=f"A Synchronization error occurred for credit note {credit_note.id}: {e}",
        )
