from typing import Optional, Dict, Any

from customers.models import Customer
from mode_groothandel.clients.api import ApiException
from mode_groothandel.exceptions import SynchronizationError
from mutations.models import Mutation

from snelstart.clients.models.relatie import Relatie as SnelstartRelatie
from snelstart.models import CachedLand
from uphance.clients.models.customer import Customer as UphanceCustomer
from uphance.clients.models.person import Person as UphancePerson
from snelstart.clients.snelstart import Snelstart
from uphance.clients.models.customer_address import CustomerAddress as UphanceCustomerAddress


def convert_address_information(address: UphanceCustomerAddress) -> Optional[dict]:
    """Convert address information of an Uphance customer to address information for Snelstart."""
    try:
        snelstart_country = CachedLand.objects.get(landcode=address.country)
    except CachedLand.DoesNotExist:
        # As a backup, try to match the custom country code.
        try:
            snelstart_country = CachedLand.objects.get(uphance_country_code=address.country)
        except CachedLand.DoesNotExist:
            return None
        except CachedLand.MultipleObjectsReturned:
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

    # Return the first shipping address.
    for address in customer.addresses:
        if address.default_for_shipping:
            return address

    # If no shipping address, return the first address.
    if len(customer.addresses) > 0:
        return customer.addresses[0]

    return None


def retrieve_contact_from_uphance_customer(customer: UphanceCustomer) -> Optional[UphancePerson]:
    """Retrieve the first billing contact from an Uphance customer."""
    for person in customer.people:
        if person.billing:
            return person

    return None


def convert_uphance_customer_to_relatie(customer: UphanceCustomer) -> Dict[str, Any]:
    """Convert an Uphance Customer to a Snelstart Relatie."""
    address = retrieve_address_info_from_uphance_customer(customer)
    if address is not None:
        address = convert_address_information(address)

    name = customer.name
    # Snelstart relatie names can be a maximum of 50 characters long
    if len(name) > 50:
        name = name[:50]

    btw_nummer = customer.vat_number.replace(" ", "")

    email = None
    phone = None

    billing_person = retrieve_contact_from_uphance_customer(customer)

    if billing_person is not None:
        email = billing_person.email
        phone = billing_person.phone_2 if billing_person.phone_1 is None else billing_person.phone_1

    return {
        "relatieSoort": ["Klant"],
        "naam": name,
        "vestigingsAdres": address,
        "email": email,
        "telefoon": phone,
        "btwNummer": btw_nummer,
    }


def match_or_create_snelstart_relatie_with_name(
    snelstart_client: Snelstart, customer: UphanceCustomer, trigger
) -> SnelstartRelatie:
    """Get or create a Snelstart relation with a name."""
    customer_in_database, _ = Customer.objects.get_or_create(uphance_id=customer.id)
    customer_in_database.uphance_name = customer.name
    customer_in_database.save()

    customer_converted_to_snelstart_relatie = convert_uphance_customer_to_relatie(customer)
    converted_name = customer_converted_to_snelstart_relatie["naam"]

    if customer_in_database.snelstart_id is not None:
        # We have already matched this customer once.
        try:
            # We need to provide the same ID.
            customer_converted_to_snelstart_relatie["id"] = customer_in_database.snelstart_id
            relatie = snelstart_client.update_relatie(
                customer_in_database.snelstart_id,
                customer_converted_to_snelstart_relatie,
            )
        except ApiException as e:
            Mutation.objects.create(
                method=Mutation.METHOD_UPDATE,
                trigger=trigger,
                on=customer_in_database,
                success=False,
                message=f"An error occurred while updating relation {customer_in_database.snelstart_id} ({customer_in_database.uphance_name}) in Snelstart: {e}",
            )
            raise SynchronizationError(
                f"An error occurred while updating relation {customer_in_database.snelstart_id} ({customer_in_database.uphance_name}) in Snelstart: {e}"
            )

        customer_in_database.snelstart_name = converted_name
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
    name_escaped = converted_name.replace("'", "''")
    try:
        relaties = snelstart_client.get_relaties(_filter=f"Naam eq '{name_escaped}'")
    except ApiException as e:
        raise SynchronizationError(
            f"An error occurred while retrieving relations for name {converted_name} from Snelstart: {e}"
        )

    if len(relaties) > 1:
        Mutation.objects.create(
            method=Mutation.METHOD_CREATE,
            trigger=trigger,
            on=customer_in_database,
            success=False,
            message=f"Multiple relaties found in Snelstart for {converted_name} (Uphance ID: {customer.id})",
        )
        raise SynchronizationError(f"Multiple relaties found in snelstart for relatie {converted_name}")
    elif len(relaties) == 1:
        relatie = relaties[0]

        if Customer.objects.filter(snelstart_id=relatie.id).exists():
            Mutation.objects.create(
                method=Mutation.METHOD_CREATE,
                trigger=trigger,
                on=customer_in_database,
                success=False,
                message=f"Matched customer in Uphance {customer.id} ({customer.name}) with already matched customer in database {relatie.id} ({relatie.naam}).",
            )
            raise SynchronizationError(
                f"Matched customer in Uphance {customer.id} ({customer.name}) with already matched customer in database {relatie.id} ({relatie.naam})."
            )

        customer_in_database.snelstart_id = relatie.id
        customer_in_database.snelstart_name = relatie.naam
        customer_in_database.save()

        Mutation.objects.create(
            method=Mutation.METHOD_CREATE,
            trigger=trigger,
            on=customer_in_database,
            success=True,
            message=f"Matched customer in Uphance with already existing customer in Snelstart.",
        )

        return relatie
    else:
        try:
            relatie = snelstart_client.add_relatie(customer_converted_to_snelstart_relatie)
        except ApiException as e:
            Mutation.objects.create(
                method=Mutation.METHOD_CREATE,
                trigger=trigger,
                on=customer_in_database,
                success=False,
                message=f"An error occurred while adding a relation with name {converted_name} to Snelstart: {e}",
            )

            raise SynchronizationError(
                f"An error occurred while adding a relation with name {converted_name} to Snelstart: {e}"
            )

        customer_in_database.snelstart_id = relatie.id
        customer_in_database.snelstart_name = relatie.naam
        customer_in_database.save()

        Mutation.objects.create(
            method=Mutation.METHOD_CREATE,
            trigger=trigger,
            on=customer_in_database,
            success=True,
            message=f"Created a new customer ({customer_in_database.snelstart_name}) in Snelstart.",
        )

        return relatie
