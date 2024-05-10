from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

from mode_groothandel.exceptions import SynchronizationError
from snelstart.clients.models.relatie import Relatie as SnelstartRelatie
from snelstart.clients.snelstart import Snelstart
from snelstart.models import TaxMapping, CachedLand
from uphance.clients.models.invoice import Invoice as UphanceInvoice
from uphance.clients.models.customer import Customer as UphanceCustomer
from uphance.clients.models.customer_address import CustomerAddress as UphanceCustomerAddress
from uphance.clients.uphance import Uphance


def construct_order_and_tax_line_items(invoice: UphanceInvoice) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, str]]]:
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
                tax_lines[tax_mapping.name]['btwBedrag'] = tax_lines[tax_mapping.name]['btwBedrag'] + tax
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
            tax_lines[tax_mapping.name]['btwBedrag'] = tax_lines[tax_mapping.name]['btwBedrag'] + invoice.shipping_tax
        else:
            tax_lines[tax_mapping.name] = {
                "btwSoort": tax_mapping.name,
                "btwBedrag": invoice.shipping_tax
            }

    for tax_name in tax_lines.keys():
        tax_lines[tax_name]["btwBedrag"] = "{:.2f}".format(tax_lines[tax_name]["btwBedrag"])

    return to_order, [x for x in tax_lines.values() if x["btwBedrag"] > 0]


def retrieve_address_info_from_uphance_customer(customer: UphanceCustomer) -> Optional[UphanceCustomerAddress]:
    if customer.addresses is None:
        return None

    for address in customer.addresses:
        if address.default_for_shipping:
            return address

    return None


def convert_address_information(address: UphanceCustomerAddress) -> Optional[dict]:
    try:
        snelstart_country = CachedLand.objects.get(landcode=address.country)
    except CachedLand.DoesNotExist:
        return None
    except CachedLand.MultipleObjectsReturned:
        return None

    return {
        'contactpersoon': '',
        'straat': address.line_1,
        'postcode': address.postcode,
        'plaats': address.city,
        'land': {
            'id': str(snelstart_country.snelstart_id)
        }
    }


def get_or_create_snelstart_relatie_with_name(snelstart_client: Snelstart, customer: UphanceCustomer) -> SnelstartRelatie:
    name = customer.name
    # Snelstart relatie names can be a maximum of 50 characters long
    if len(name) > 50:
        name = name[:50]

    name_escaped = name.replace("'", "''")
    relaties = snelstart_client.get_relaties(_filter=f"Naam eq '{name_escaped}'")

    if len(relaties) == 1:
        return relaties[0]
    elif len(relaties) > 1:
        raise SynchronizationError(f"Multiple relaties found in snelstart for relatie {name}")

    address = retrieve_address_info_from_uphance_customer(customer)
    if address is not None:
        address = convert_address_information(address)

    tax_number = customer.vat_number.replace(' ', '')

    print(tax_number)

    return snelstart_client.add_relatie({
        'relatieSoort': ["Klant"],
        'naam': name,
        'address': address
    })


def convert_date_to_amount_of_days_until(date: datetime) -> int:
    now = datetime.now()
    delta = date - now
    return max(0, delta.days)


def setup_invoice_for_synchronisation(uphance_client: Uphance, snelstart_client: Snelstart, invoice: UphanceInvoice) -> dict:
    customer = uphance_client.customer_by_id(invoice.company_id)
    grootboek_regels, tax_lines = construct_order_and_tax_line_items(invoice)
    snelstart_relatie_for_order = get_or_create_snelstart_relatie_with_name(snelstart_client, customer)
    betalingstermijn = convert_date_to_amount_of_days_until(invoice.due_date)

    if snelstart_relatie_for_order is None:
        raise SynchronizationError(f"Failed to synchronize {invoice.invoice_number} because customer {customer.name} could not be found or created in Snelstart.")

    invoice_date = invoice.created_at

    return {
        "factuurnummer": invoice.invoice_number,
        "Klant": {"id": str(snelstart_relatie_for_order.id)},
        "boekingsregels": grootboek_regels,
        "factuurbedrag": "{:.2f}".format(invoice.items_total + invoice.items_tax + invoice.shipping_cost + invoice.shipping_tax),
        "betalingstermijn": betalingstermijn,
        "factuurdatum": invoice_date.strftime("%Y-%m-%d %H:%I:%S"),
        "btw": tax_lines,
    }
