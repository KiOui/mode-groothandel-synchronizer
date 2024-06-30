from typing import Optional

from mode_groothandel.clients.utils import get_value_or_error, get_value_or_none


class Contact:

    def __init__(
        self, first_name: str, last_name: str, position: str, phone_1: str, phone_2: str, email: str, notes: Optional[str]
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.phone_1 = phone_1
        self.phone_2 = phone_2
        self.email = email
        self.notes = notes

    @staticmethod
    def from_data(data: dict) -> "Contact":
        return Contact(
            first_name=str(get_value_or_error(data, "first_name")),
            last_name=str(get_value_or_error(data, "last_name")),
            position=str(get_value_or_error(data, "position")),
            phone_1=str(get_value_or_error(data, "phone_1")),
            phone_2=str(get_value_or_error(data, "phone_2")),
            email=str(get_value_or_error(data, "email")),
            notes=get_value_or_none(data, "notes", str),
        )
