from typing import List, Optional

from mode_groothandel.clients.utils import (
    get_value_or_error,
    apply_from_data_to_list_or_error,
    apply_from_data_to_list_or_none,
    get_value_or_none,
)
from uphance.clients.models.customer_address import CustomerAddress
from uphance.clients.models.person import Person


class Customer:

    def __init__(
        self,
        customer_id: int,
        name: str,
        country: Optional[str],
        city: Optional[str],
        vat_number: str,
        channel_id: int,
        notes: Optional[str],
        people: List[Person],
        addresses: Optional[List[CustomerAddress]],
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
            country=get_value_or_none(data, "country", str),
            city=get_value_or_none(data, "city", str),
            vat_number=str(get_value_or_error(data, "vat_number")),
            channel_id=get_value_or_none(data, "channel_id", int),
            notes=get_value_or_none(data, "notes"),
            people=apply_from_data_to_list_or_error(Person.from_data, data, "people"),
            addresses=apply_from_data_to_list_or_none(CustomerAddress.from_data, data, "addresses"),
        )

    def __str__(self):
        """Convert this object to string."""
        return f"Customer {self.name} ({self.id})"
