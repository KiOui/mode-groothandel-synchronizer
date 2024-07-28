from dataclasses import dataclass
from typing import Optional

from mode_groothandel.clients.utils import get_value_or_error, get_value_or_none


@dataclass
class Person:
    """Person class."""

    person_id: int
    customer_id: int
    first_name: str
    last_name: str
    position: str
    phone_1: Optional[str]
    phone_2: Optional[str]
    email: str
    notes: Optional[str]
    buyer: bool
    shipping: bool
    billing: bool

    @staticmethod
    def from_data(data: dict) -> "Person":
        """Initialise Person object from data."""
        return Person(
            person_id=int(get_value_or_error(data, "id")),
            customer_id=int(get_value_or_error(data, "customer_id")),
            first_name=str(get_value_or_error(data, "first_name")),
            last_name=str(get_value_or_error(data, "last_name")),
            position=str(get_value_or_error(data, "position")),
            phone_1=get_value_or_none(data, "phone_1", str),
            phone_2=get_value_or_none(data, "phone_2", str),
            email=str(get_value_or_error(data, "email")),
            notes=get_value_or_none(data, "notes"),
            buyer=bool(get_value_or_error(data, "buyer")),
            shipping=bool(get_value_or_error(data, "shipping")),
            billing=bool(get_value_or_error(data, "billing")),
        )
