import logging
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Tuple, Dict, Any

from invoices.models import Invoice
from mode_groothandel.clients.api import ApiException
from mode_groothandel.exceptions import SynchronizationError
from customers.services import match_or_create_snelstart_relatie_with_name
from mutations.models import Mutation
from snelstart.clients.snelstart import Snelstart
from snelstart.constants import BTW_VERKOPEN_PREFIX
from snelstart.models import TaxMapping
from uphance.clients.models.invoice import Invoice as UphanceInvoice
from uphance.clients.uphance import Uphance


logger = logging.getLogger(__name__)


def round_half_up(n, decimals=0):
    """Round x.5 up instead of half."""
    base = Decimal(10) ** -decimals
    return float(Decimal(str(n)).quantize(base, rounding=ROUND_HALF_UP))


def construct_order_and_tax_line_items(
    invoice: UphanceInvoice,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """Construct order and tax line items for an invoice from Uphance."""
    to_order = list()
    # Dictionary mapping tax percentages to the total amount to compute the tax over.
    compute_tax_over_amount = dict()
    for item in invoice.line_items:
        amount = sum([x.quantity for x in item.line_quantities])

        total_price_line = item.unit_price * amount

        if total_price_line != 0:
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
                    "bedrag": "{:.2f}".format(total_price_line),
                    "btwSoort": tax_mapping.name,
                }
            )

            if tax_mapping in compute_tax_over_amount.keys():
                compute_tax_over_amount[tax_mapping] = compute_tax_over_amount[tax_mapping] + total_price_line
            else:
                compute_tax_over_amount[tax_mapping] = total_price_line

    # Calculate the tax.
    tax_lines = dict()

    for tax_mapping, total_amount_to_compute_tax_over in compute_tax_over_amount.items():
        tax_lines[tax_mapping.name] = total_amount_to_compute_tax_over * tax_mapping.tax_amount / 100

    if invoice.shipping_cost != 0:
        tax_level = int(invoice.shipping_tax / invoice.shipping_cost * 100)
        try:
            tax_mapping = TaxMapping.objects.get(tax_amount=tax_level)
        except TaxMapping.DoesNotExist:
            raise SynchronizationError(f"Tax mapping for tax amount {tax_level} does not exist")
        to_order.append(
            {
                "omschrijving": "Shipping costs",
                "grootboek": {
                    "id": str(tax_mapping.grootboekcode),
                },
                "bedrag": "{:.2f}".format(invoice.shipping_cost),
                "btwSoort": tax_mapping.name,
            }
        )

        if tax_mapping.name in tax_lines.keys():
            tax_lines[tax_mapping.name] = tax_lines[tax_mapping.name] + invoice.shipping_tax
        else:
            tax_lines[tax_mapping.name] = invoice.shipping_tax

    tax_lines = [
        # Round tax amount by 2 digits.
        {"btwSoort": BTW_VERKOPEN_PREFIX + tax_name, "btwBedrag": "{:.2f}".format(round_half_up(tax_amount, 2))}
        for (tax_name, tax_amount) in tax_lines.items()
        if tax_amount > 0
    ]

    return to_order, tax_lines


def convert_date_to_amount_of_days_until(date: datetime) -> int:
    """Convert a datetime to the amount of days until that datetime."""
    now = datetime.now()
    delta = date - now
    return max(0, delta.days)


def setup_invoice_for_synchronisation(
    uphance_client: Uphance, snelstart_client: Snelstart, invoice: UphanceInvoice, trigger: int
) -> dict:
    """Setup an invoice from Uphance for synchronisation to Snelstart."""
    customer = uphance_client.customer_by_id(invoice.company_id)
    grootboek_regels, tax_lines = construct_order_and_tax_line_items(invoice)
    snelstart_relatie_for_order = match_or_create_snelstart_relatie_with_name(snelstart_client, customer, trigger)
    betalingstermijn = convert_date_to_amount_of_days_until(invoice.due_date)

    if snelstart_relatie_for_order is None:
        raise SynchronizationError(
            f"Failed to synchronize invoice {invoice.invoice_number} because customer {customer.name} could not be "
            f"found or created in Snelstart."
        )

    invoice_date = invoice.created_at if invoice.created_at is not None else datetime.now()

    return {
        "factuurnummer": invoice.invoice_number,
        "Klant": {"id": str(snelstart_relatie_for_order.id)},
        "boekingsregels": grootboek_regels,
        "factuurbedrag": "{:.2f}".format(
            invoice.items_total + invoice.items_tax + invoice.shipping_cost + invoice.shipping_tax
        ),
        "betalingstermijn": betalingstermijn,
        "factuurdatum": invoice_date.strftime("%Y-%m-%d %H:%I:%S"),
        "btw": tax_lines,
    }


def get_or_create_invoice_in_database(invoice: UphanceInvoice) -> Invoice:
    try:
        return Invoice.objects.get(uphance_id=invoice.id)
    except Invoice.DoesNotExist:
        return Invoice.objects.create(
            uphance_id=invoice.id,
            invoice_number=invoice.invoice_number,
            invoice_total=invoice.items_total + invoice.items_tax + invoice.shipping_cost + invoice.shipping_tax,
        )


def try_delete_invoice(snelstart_client: Snelstart, invoice_id: int, trigger: int) -> None:
    try:
        invoice_in_database = Invoice.objects.get(uphance_id=invoice_id)
    except Invoice.DoesNotExist:
        invoice_in_database = Invoice.objects.create(
            uphance_id=invoice_id,
        )
    if invoice_in_database.snelstart_id is None:
        Mutation.objects.create(
            method=Mutation.METHOD_DELETE,
            trigger=trigger,
            on=invoice_in_database,
            success=False,
            message=f"Unable to delete invoice {invoice_id} because no Snelstart ID was found in the database",
        )

    try:
        snelstart_client.delete_verkoopboeking(invoice_in_database.snelstart_id)
        Mutation.objects.create(
            method=Mutation.METHOD_DELETE,
            trigger=trigger,
            on=invoice_in_database,
            success=True,
            message=None,
        )
    except ApiException as e:
        Mutation.objects.create(
            method=Mutation.METHOD_DELETE,
            trigger=trigger,
            on=invoice_in_database,
            success=False,
            message=f"An API error occurred for invoice {invoice_id}: {e}",
        )


def try_update_invoice(
    uphance_client: Uphance, snelstart_client: Snelstart, invoice: UphanceInvoice, trigger: int
) -> None:
    invoice_in_database = get_or_create_invoice_in_database(invoice)

    invoice_in_database.invoice_number = invoice.invoice_number
    invoice_in_database.invoice_total = (
        invoice.items_total + invoice.items_tax + invoice.shipping_cost + invoice.shipping_tax
    )
    invoice_in_database.save()

    if invoice_in_database.snelstart_id is None:
        Mutation.objects.create(
            method=Mutation.METHOD_UPDATE,
            trigger=trigger,
            on=invoice_in_database,
            success=False,
            message=f"Unable to update invoice {invoice.id} because no Snelstart ID was found in the database",
        )
        return

    try:
        invoice_converted = setup_invoice_for_synchronisation(uphance_client, snelstart_client, invoice, trigger)
        invoice_converted["id"] = invoice_in_database.snelstart_id
        try:
            snelstart_client.update_verkoopboeking(invoice_in_database.snelstart_id, invoice_converted)
        except ApiException as e:
            raise SynchronizationError(
                f"An error occurred while updating verkoopboeking {invoice_in_database.snelstart_id} in Snelstart: {e}"
            )
        logger.info(f"Successfully updated invoice {invoice.id}")
        Mutation.objects.create(
            method=Mutation.METHOD_UPDATE,
            trigger=trigger,
            on=invoice_in_database,
            success=True,
            message=None,
        )
    except SynchronizationError as e:
        logger.error(f"A Synchronization error occurred while updating invoice {invoice.id}: {e}")
        Mutation.objects.create(
            method=Mutation.METHOD_UPDATE,
            trigger=trigger,
            on=invoice_in_database,
            success=False,
            message=f"A Synchronization error occurred while updating invoice {invoice.id}: {e}",
        )


def try_create_invoice(
    uphance_client: Uphance, snelstart_client: Snelstart, invoice: UphanceInvoice, trigger: int
) -> None:
    invoice_in_database = get_or_create_invoice_in_database(invoice)

    try:
        invoice_converted = setup_invoice_for_synchronisation(uphance_client, snelstart_client, invoice, trigger)
        try:
            verkoopboeking = snelstart_client.add_verkoopboeking(invoice_converted)
        except ApiException as e:
            raise SynchronizationError(
                f"An error occurred while adding a verkoopboeking for invoice {invoice.invoice_number} to Snelstart: "
                f"{e}"
            )
        logger.info(f"Successfully synchronized invoice {invoice.id}")
        invoice_in_database.snelstart_id = verkoopboeking["id"]
        invoice_in_database.save()
        Mutation.objects.create(
            method=Mutation.METHOD_CREATE,
            trigger=trigger,
            on=invoice_in_database,
            success=True,
            message=None,
        )
    except SynchronizationError as e:
        logger.error(f"A Synchronization error occurred for invoice {invoice.id}: {e}")
        Mutation.objects.create(
            method=Mutation.METHOD_CREATE,
            trigger=trigger,
            on=invoice_in_database,
            success=False,
            message=f"A Synchronization error occurred for invoice {invoice.id}: {e}",
        )
