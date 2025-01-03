from typing import Optional

from mode_groothandel.clients.utils import get_value_or_error, get_value_or_none


class Land:

    def __init__(self, naam: str, landcode_iso: Optional[str], landcode: str, _id: str, uri: str):
        self.naam = naam
        self.landcode_iso = landcode_iso
        self.landcode = landcode
        self.id = _id
        self.uri = uri

    @staticmethod
    def from_data(data: dict) -> "Land":
        return Land(
            naam=str(get_value_or_error(data, "naam")),
            landcode_iso=get_value_or_none(data, "landcodeISO"),
            landcode=str(get_value_or_error(data, "landcode")),
            _id=str(get_value_or_error(data, "id")),
            uri=str(get_value_or_error(data, "uri")),
        )

    def __str__(self):
        """Convert this object to string."""
        return f"Land {self.naam} ({self.id})"
