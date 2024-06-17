from typing import Optional

from customers.models import Customer
from mode_groothandel.clients.api import ApiException
from mode_groothandel.exceptions import SynchronizationError
from mutations.models import Mutation

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


def match_or_create_snelstart_relatie_with_name(
    snelstart_client: Snelstart, customer: UphanceCustomer, trigger
) -> SnelstartRelatie:
    """Get or create a Snelstart relation with a name."""
    customer_in_database, _ = Customer.objects.get_or_create(uphance_id=customer.id)
    customer_in_database.uphance_name = customer.name
    customer_in_database.save()

    address = retrieve_address_info_from_uphance_customer(customer)
    if address is not None:
        address = convert_address_information(address)

    name = customer.name
    # Snelstart relatie names can be a maximum of 50 characters long
    if len(name) > 50:
        name = name[:50]

    if customer_in_database.snelstart_id is not None:
        # We have already matched this customer once.
        try:
            relatie = snelstart_client.update_relatie(
                customer_in_database.snelstart_id, {"relatieSoort": ["Klant"], "naam": name, "address": address}
            )
        except ApiException as e:
            Mutation.objects.create(
                method=Mutation.METHOD_UPDATE,
                trigger=trigger,
                on=customer_in_database,
                success=False,
                message=f"An error occurred while updating relation {customer_in_database.snelstart_id} in Snelstart: {e}",
            )
            raise SynchronizationError(
                f"An error occurred while updating relation {customer_in_database.snelstart_id} in Snelstart: {e}"
            )

        customer_in_database.snelstart_name = name
        customer_in_database.save()

        Mutation.objects.create(
            method=Mutation.METHOD_UPDATE,
            trigger=trigger,
            on=customer_in_database,
            success=True,
            message=None,
        )

        return relatie

    # We have not matched this customer, we should first search for a match in Snelstart.
    name_escaped = name.replace("'", "''")
    try:
        relaties = snelstart_client.get_relaties(_filter=f"Naam eq '{name_escaped}'")
    except ApiException as e:
        raise SynchronizationError(f"An error occurred while retrieving relations for name {name} from Snelstart: {e}")

    if len(relaties) > 1:
        Mutation.objects.create(
            method=Mutation.METHOD_CREATE,
            trigger=trigger,
            on=customer_in_database,
            success=False,
            message=f"Multiple relaties found in Snelstart for {name} (Uphance ID: {customer.id})",
        )
        raise SynchronizationError(f"Multiple relaties found in snelstart for relatie {name}")
    elif len(relaties) == 1:
        relatie = relaties[0]
        customer_in_database.snelstart_id = relatie.id
        customer_in_database.snelstart_name = relatie.naam
        customer_in_database.save()

        Mutation.objects.create(
            method=Mutation.METHOD_CREATE,
            trigger=trigger,
            on=customer_in_database,
            success=True,
            message=None,
        )

        return relatie
    else:
        try:
            relatie = snelstart_client.add_relatie({"relatieSoort": ["Klant"], "naam": name, "address": address})
        except ApiException as e:
            Mutation.objects.create(
                method=Mutation.METHOD_CREATE,
                trigger=trigger,
                on=customer_in_database,
                success=False,
                message=f"An error occurred while adding a relation with name {name} to Snelstart: {e}",
            )

            raise SynchronizationError(f"An error occurred while adding a relation with name {name} to Snelstart: {e}")

        customer_in_database.snelstart_id = relatie.id
        customer_in_database.snelstart_name = relatie.naam
        customer_in_database.save()

        Mutation.objects.create(
            method=Mutation.METHOD_CREATE,
            trigger=trigger,
            on=customer_in_database,
            success=True,
            message=None,
        )

        return relatie
