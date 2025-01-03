from typing import Optional

from mode_groothandel.clients.utils import get_value_or_error, get_value_or_none


class Relatie:

    def __init__(self, _id: str, naam: str, email: Optional[str], telefoon: Optional[str], btw_nummer: Optional[str]):
        self.id = _id
        self.naam = naam
        self.email = email
        self.telefoon = telefoon
        self.btw_nummer = btw_nummer

    @staticmethod
    def from_data(data: dict) -> "Relatie":
        return Relatie(
            _id=str(get_value_or_error(data, "id")),
            naam=str(get_value_or_error(data, "naam")),
            email=get_value_or_none(data, "email", str),
            telefoon=get_value_or_none(data, "telefoon", str),
            btw_nummer=get_value_or_none(data, "btwNummer", str),
        )
