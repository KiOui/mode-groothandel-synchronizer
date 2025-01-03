from typing import List

from mode_groothandel.clients.utils import get_value_or_error, apply_from_data_to_list_or_error
from sendcloud.client.models.country import Country


class ShippingMethod:

    def __init__(
        self,
        _id: int,
        name: str,
        carrier: str,
        min_weight: float,
        max_weight: float,
        service_point_input: str,
        price: float,
        countries: List[Country],
    ):
        self.id = _id
        self.name = name
        self.carrier = carrier
        self.min_weight = min_weight
        self.max_weight = max_weight
        self.service_point_input = service_point_input
        self.price = price
        self.countries = countries

    @staticmethod
    def from_data(data: dict) -> "ShippingMethod":
        return ShippingMethod(
            _id=int(get_value_or_error(data, "id")),
            name=str(get_value_or_error(data, "name")),
            carrier=str(get_value_or_error(data, "carrier")),
            min_weight=float(get_value_or_error(data, "min_weight")),
            max_weight=float(get_value_or_error(data, "max_weight")),
            service_point_input=str(get_value_or_error(data, "service_point_input")),
            price=float(get_value_or_error(data, "price")),
            countries=apply_from_data_to_list_or_error(Country.from_data, data, "countries"),
        )
