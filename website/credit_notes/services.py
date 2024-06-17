import logging
from typing import List, Dict, Any, Tuple

from credit_notes.models import CreditNote
from mode_groothandel.clients.api import ApiException
from mode_groothandel.exceptions import SynchronizationError
from customers.services import match_or_create_snelstart_relatie_with_name
from mutations.models import Mutation
from snelstart.clients.snelstart import Snelstart
from snelstart.models import TaxMapping
from uphance.clients.models.credit_note import CreditNote as UphanceCreditNote
from uphance.clients.uphance import Uphance


logger = logging.getLogger(__name__)


def construct_order_and_tax_line_items(
    credit_note: UphanceCreditNote,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    to_order = list()
    tax_lines = dict()

    for item in credit_note.line_items:
        amount = sum([x.quantity for x in item.line_quantities])

        try:
            tax_mapping = TaxMapping.objects.get(tax_amount=item.tax_level)
        except TaxMapping.DoesNotExist:
            raise SynchronizationError(f"Tax mapping for tax amount {item.tax_level} does not exist")

        to_order.append(
            {
                "omschrijving": f"{amount} x {item.product_id} {item.product_name}",
                "grootboek": {
                    "id": str(tax_mapping.grootboekcode),
                },
                "bedrag": "{:.2f}".format((item.unit_price * -1) * amount),
                "btwSoort": tax_mapping.name,
            }
        )

        tax = (item.unit_price * -1) * amount * item.tax_level / 100
        if tax != 0:
            if tax_mapping.name in tax_lines.keys():
                tax_lines[tax_mapping.name] = tax_lines[tax_mapping.name] + tax
            else:
                tax_lines[tax_mapping.name] = tax

    if credit_note.freeform_amount is not None and credit_note.freeform_amount != 0:
        # Add a fake line item for the freeform amount.
        computed_tax_level = credit_note.freeform_tax / (credit_note.freeform_amount / 100)
        computed_tax_level_2_decimals = "{:.1f}".format(computed_tax_level)

        try:
            tax_mapping = TaxMapping.objects.get(tax_amount=float(computed_tax_level_2_decimals))
        except TaxMapping.DoesNotExist:
            raise SynchronizationError(
                f"Error finding tax mapping for freeform amount: Tax mapping for computed tax amount {computed_tax_level_2_decimals} does not exist"
            )

        to_order.append(
            {
                "omschrijving": f"Freeform ({credit_note.freeform_description})",
                "grootboek": {
                    "id": str(tax_mapping.grootboekcode),
                },
                "bedrag": "{:.2f}".format(credit_note.freeform_amount * -1),
                "btwSoort": tax_mapping.name,
            }
        )

        if credit_note.freeform_tax != 0:
            if tax_mapping.name in tax_lines.keys():
                tax_lines[tax_mapping.name] = tax_lines[tax_mapping.name] + (credit_note.freeform_tax * -1)
            else:
                tax_lines[tax_mapping.name] = credit_note.freeform_tax * -1

    tax_lines = [
        {"btwSoort": tax_name, "btwBedrag": "{:.2f}".format(tax_amount)}
        for (tax_name, tax_amount) in tax_lines.items()
        if tax_amount > 0
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

    grootboek_regels, tax_lines = construct_order_and_tax_line_items(credit_note)
    snelstart_relatie_for_order = match_or_create_snelstart_relatie_with_name(snelstart_client, customer, trigger)

    if snelstart_relatie_for_order is None:
        raise SynchronizationError(
            f"Failed to synchronize credit note {credit_note.credit_note_number} because customer {customer.name} could not be found or created in Snelstart."
        )

    credit_note_grand_total = credit_note.grand_total * -1

    return {
        "factuurnummer": credit_note.credit_note_number,
        "klant": {"id": str(snelstart_relatie_for_order.id)},
        "boekingsregels": grootboek_regels,
        "factuurbedrag": "{:.2f}".format(credit_note_grand_total),
        "betalingstermijn": 0,
        "factuurdatum": credit_note.created_at.strftime("%Y-%m-%d %H:%I:%S"),
        "btw": tax_lines,
    }


def get_or_create_credit_note_in_database(credit_note: UphanceCreditNote) -> CreditNote:
    try:
        return CreditNote.objects.get(uphance_id=credit_note.id)
    except CreditNote.DoesNotExist:
        return CreditNote.objects.create(
            uphance_id=credit_note.id,
            credit_note_number=credit_note.credit_note_number,
            credit_note_total=credit_note.items_total + credit_note.items_tax,
        )


def try_delete_credit_note(snelstart_client: Snelstart, credit_note: UphanceCreditNote, trigger: int) -> None:
    credit_note_in_database = get_or_create_credit_note_in_database(credit_note)
    if credit_note_in_database.snelstart_id is None:
        Mutation.objects.create(
            method=Mutation.METHOD_DELETE,
            trigger=trigger,
            on=credit_note_in_database,
            success=False,
            message=f"Unable to delete credit note {credit_note.id} because no Snelstart ID was found in the database",
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
            message=f"An API error occurred for credit note {credit_note.id}: {e}",
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
                f"An error occurred while updating verkoopboeking {credit_note_in_database.snelstart_id} for credit note {credit_note.id} in Snelstart: {e}"
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
                f"An error occurred while adding a verkoopboeking for credit note {credit_note.credit_note_number} to Snelstart: {e}"
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
