from typing import Optional

from mode_groothandel.clients.utils import get_value_or_error, get_value_or_none


class Relatie:

    def __init__(self, _id: str, naam: str, email: Optional[str]):
        self.id = _id
        self.naam = naam
        self.email = email

    @staticmethod
    def from_data(data: dict) -> "Relatie":
        return Relatie(
            _id=str(get_value_or_error(data, 'id')),
            naam=str(get_value_or_error(data, 'naam')),
            email=str(get_value_or_none(data, 'email')),
        )
