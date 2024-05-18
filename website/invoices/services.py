import logging
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

from invoices.models import Invoice
from mode_groothandel.clients.api import ApiException
from mode_groothandel.exceptions import SynchronizationError
from mutations.models import Mutation
from snelstart.clients.models.relatie import Relatie as SnelstartRelatie
from snelstart.clients.snelstart import Snelstart
from snelstart.models import TaxMapping, CachedLand
from uphance.clients.models.invoice import Invoice as UphanceInvoice
from uphance.clients.models.customer import Customer as UphanceCustomer
from uphance.clients.models.customer_address import CustomerAddress as UphanceCustomerAddress
from uphance.clients.uphance import Uphance


logger = logging.getLogger(__name__)


def construct_order_and_tax_line_items(
    invoice: UphanceInvoice,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """Construct order and tax line items for an invoice from Uphance."""
    to_order = list()
    tax_lines = dict()
    for item in invoice.line_items:
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
                "bedrag": "{:.2f}".format(item.unit_price * amount),
                "btwSoort": tax_mapping.name,
            }
        )

        tax = item.unit_price * amount * item.tax_level / 100
        if tax > 0:
            if tax_mapping.name in tax_lines.keys():
                tax_lines[tax_mapping.name]["btwBedrag"] = tax_lines[tax_mapping.name]["btwBedrag"] + tax
            else:
                tax_lines[tax_mapping.name] = {
                    "btwSoort": tax_mapping.name,
                    "btwBedrag": tax,
                }

    if invoice.shipping_cost > 0:
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
            tax_lines[tax_mapping.name]["btwBedrag"] = tax_lines[tax_mapping.name]["btwBedrag"] + invoice.shipping_tax
        else:
            tax_lines[tax_mapping.name] = {"btwSoort": tax_mapping.name, "btwBedrag": invoice.shipping_tax}

    for tax_name in tax_lines.keys():
        tax_lines[tax_name]["btwBedrag"] = "{:.2f}".format(tax_lines[tax_name]["btwBedrag"])

    return to_order, [x for x in tax_lines.values() if x["btwBedrag"] > 0]


def retrieve_address_info_from_uphance_customer(customer: UphanceCustomer) -> Optional[UphanceCustomerAddress]:
    """Retrieve the address information from an Uphance customer."""
    if customer.addresses is None:
        return None

    for address in customer.addresses:
        if address.default_for_shipping:
            return address

    return None


def convert_address_information(address: UphanceCustomerAddress) -> Optional[dict]:
    """Convert address information of an Uphance customer to address information for Snelstart."""
    try:
        snelstart_country = CachedLand.objects.get(landcode=address.country)
    except CachedLand.DoesNotExist:
        return None
    except CachedLand.MultipleObjectsReturned:
        return None

    return {
        "contactpersoon": "",
        "straat": address.line_1,
        "postcode": address.postcode,
        "plaats": address.city,
        "land": {"id": str(snelstart_country.snelstart_id)},
    }


def get_or_create_snelstart_relatie_with_name(
    snelstart_client: Snelstart, customer: UphanceCustomer
) -> SnelstartRelatie:
    """Get or create a Snelstart relation with a name."""
    name = customer.name
    # Snelstart relatie names can be a maximum of 50 characters long
    if len(name) > 50:
        name = name[:50]

    name_escaped = name.replace("'", "''")
    try:
        relaties = snelstart_client.get_relaties(_filter=f"Naam eq '{name_escaped}'")
    except ApiException as e:
        raise SynchronizationError(f"An error occurred while retrieving relations for name {name} from Snelstart: {e}")

    if len(relaties) == 1:
        return relaties[0]
    elif len(relaties) > 1:
        raise SynchronizationError(f"Multiple relaties found in snelstart for relatie {name}")

    address = retrieve_address_info_from_uphance_customer(customer)
    if address is not None:
        address = convert_address_information(address)

    try:
        return snelstart_client.add_relatie({"relatieSoort": ["Klant"], "naam": name, "address": address})
    except ApiException as e:
        raise SynchronizationError(f"An error occurred while adding a relation with name {name} to Snelstart: {e}")


def convert_date_to_amount_of_days_until(date: datetime) -> int:
    """Convert a datetime to the amount of days until that datetime."""
    now = datetime.now()
    delta = date - now
    return max(0, delta.days)


def setup_invoice_for_synchronisation(
    uphance_client: Uphance, snelstart_client: Snelstart, invoice: UphanceInvoice
) -> dict:
    """Setup an invoice from Uphance for synchronisation to Snelstart."""
    customer = uphance_client.customer_by_id(invoice.company_id)
    grootboek_regels, tax_lines = construct_order_and_tax_line_items(invoice)
    snelstart_relatie_for_order = get_or_create_snelstart_relatie_with_name(snelstart_client, customer)
    betalingstermijn = convert_date_to_amount_of_days_until(invoice.due_date)

    if snelstart_relatie_for_order is None:
        raise SynchronizationError(
            f"Failed to synchronize {invoice.invoice_number} because customer {customer.name} could not be found or created in Snelstart."
        )

    invoice_date = invoice.created_at

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


def try_delete_invoice(snelstart_client: Snelstart, invoice: UphanceInvoice, trigger: int) -> None:
    invoice_in_database = get_or_create_invoice_in_database(invoice)
    if invoice_in_database.snelstart_id is None:
        Mutation.objects.create(
            method=Mutation.METHOD_DELETE,
            trigger=trigger,
            on=invoice_in_database,
            success=False,
            message=f"Unable to delete invoice {invoice.id} because no Snelstart ID was found in the database",
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
            message=f"An API error occurred for invoice {invoice.id}: {e}",
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

    try:
        invoice_converted = setup_invoice_for_synchronisation(uphance_client, snelstart_client, invoice)
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
        invoice_converted = setup_invoice_for_synchronisation(uphance_client, snelstart_client, invoice)
        try:
            verkoopboeking = snelstart_client.add_verkoopboeking(invoice_converted)
        except ApiException as e:
            raise SynchronizationError(f"An error occurred while adding a verkoopboeking to Snelstart: {e}")
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
