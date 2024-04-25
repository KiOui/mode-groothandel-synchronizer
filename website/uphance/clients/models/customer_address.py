from typing import Optional

from mode_groothandel.clients.utils import get_value_or_error, get_value_or_none


class CustomerAddress:

    def __init__(
        self,
        customer_address_id: int,
        customer_id: int,
        line_1: Optional[str],
        line_2: Optional[str],
        line_3: Optional[str],
        city: Optional[str],
        state: Optional[str],
        country: Optional[str],
        postcode: Optional[str],
        default_for_shipping: bool,
        default_for_billing: bool,
    ):
        self.customer_address_id = customer_address_id
        self.customer_id = customer_id
        self.line_1 = line_1
        self.line_2 = line_2
        self.line_3 = line_3
        self.city = city
        self.state = state
        self.country = country
        self.postcode = postcode
        self.default_for_shipping = default_for_shipping
        self.default_for_billing = default_for_billing

    @staticmethod
    def from_data(data: dict) -> "CustomerAddress":
        return CustomerAddress(
            customer_address_id=int(get_value_or_error(data, "id")),
            customer_id=int(get_value_or_error(data, "customer_id")),
            line_1=get_value_or_none(data, "line_1"),
            line_2=get_value_or_none(data, "line_2"),
            line_3=get_value_or_none(data, "line_3"),
            city=get_value_or_none(data, "city"),
            state=get_value_or_none(data, "state"),
            country=get_value_or_none(data, "country"),
            postcode=get_value_or_none(data, "postcode"),
            default_for_shipping=bool(get_value_or_error(data, "default_for_shipping")),
            default_for_billing=bool(get_value_or_error(data, "default_for_billing")),
        )
