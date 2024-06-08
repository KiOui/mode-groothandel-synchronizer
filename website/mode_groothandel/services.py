from typing import Optional

from mode_groothandel.clients.api import ApiException
from mode_groothandel.exceptions import SynchronizationError

from snelstart.clients.models.relatie import Relatie as SnelstartRelatie
from snelstart.models import CachedLand
from uphance.clients.models.customer import Customer as UphanceCustomer
from snelstart.clients.snelstart import Snelstart
from uphance.clients.models.customer_address import CustomerAddress as UphanceCustomerAddress


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


def retrieve_address_info_from_uphance_customer(customer: UphanceCustomer) -> Optional[UphanceCustomerAddress]:
    """Retrieve the address information from an Uphance customer."""
    if customer.addresses is None:
        return None

    for address in customer.addresses:
        if address.default_for_shipping:
            return address

    return None


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
