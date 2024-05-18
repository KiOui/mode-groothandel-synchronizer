from typing import List

from mode_groothandel.clients.utils import get_value_or_error


class Country:

    def __init__(self, _id: int, name: str, price: float, iso_2: str, iso_3: str):
        self.id = _id
        self.name = name
        self.price = price
        self.iso_2 = iso_2
        self.iso_3 = iso_3

    @staticmethod
    def from_data(data: dict) -> "Country":
        return Country(
            _id=int(get_value_or_error(data, "id")),
            name=str(get_value_or_error(data, "name")),
            price=float(get_value_or_error(data, "price")),
            iso_2=str(get_value_or_error(data, "iso_2")),
            iso_3=str(get_value_or_error(data, "iso_3")),
        )
