from dataclasses import dataclass
from typing import Optional

from mode_groothandel.clients.utils import get_value_or_error, get_value_or_none


@dataclass
class Address:
    """Address class."""

    line_1: str
    country: str
    postcode: Optional[str] = None
    line_2: Optional[str] = None
    line_3: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

    @staticmethod
    def from_data(data: dict) -> "Address":
        """Convert data to an Address instance."""
        return Address(
            line_1=str(get_value_or_error(data, "line_1")),
            line_2=get_value_or_none(data, "line_2", str),
            line_3=get_value_or_none(data, "line_3", str),
            city=get_value_or_none(data, "city", str),
            state=get_value_or_none(data, "state", str),
            country=str(get_value_or_error(data, "country")),
            postcode=get_value_or_none(data, "postcode", str),
        )
