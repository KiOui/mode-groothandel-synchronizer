from typing import List

from mode_groothandel.clients.utils import get_value_or_error, apply_from_data_to_list_or_error
from uphance.clients.models.customer_address import CustomerAddress
from uphance.clients.models.person import Person


class Customer:

    def __init__(
        self,
        customer_id: int,
        name: str,
        country: str,
        city: str,
        vat_number: str,
        channel_id: int,
        notes: str,
        people: List[Person],
        addresses: List[CustomerAddress],
    ):
        self.id = customer_id
        self.name = name
        self.country = country
        self.city = city
        self.vat_number = vat_number
        self.channel_id = channel_id
        self.notes = notes
        self.people = people
        self.addresses = addresses

    @staticmethod
    def from_data(data: dict) -> "Customer":
        return Customer(
            customer_id=int(get_value_or_error(data, "id")),
            name=str(get_value_or_error(data, "name")),
            country=str(get_value_or_error(data, "country")),
            city=str(get_value_or_error(data, "city")),
            vat_number=str(get_value_or_error(data, "vat_number")),
            channel_id=int(get_value_or_error(data, "channel_id")),
            notes=str(get_value_or_error(data, "notes")),
            people=apply_from_data_to_list_or_error(Person.from_data, data, "people"),
            addresses=apply_from_data_to_list_or_error(CustomerAddress.from_data, data, "addresses"),
        )

    def __str__(self):
        """Convert this object to string."""
        return f"Customer {self.name} ({self.id})"
