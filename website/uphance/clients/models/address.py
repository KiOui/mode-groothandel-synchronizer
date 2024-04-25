from mode_groothandel.clients.utils import get_value_or_error


class Address:

    def __init__(self, line_1: str, line_2: str, line_3: str, city: str, state: str, country: str, postcode: str):
        self.line_1 = line_1
        self.line_2 = line_2
        self.line_3 = line_3
        self.city = city
        self.state = state
        self.country = country
        self.postcode = postcode

    @staticmethod
    def from_data(data: dict) -> "Address":
        return Address(
            line_1=str(get_value_or_error(data, "line_1")),
            line_2=str(get_value_or_error(data, "line_2")),
            line_3=str(get_value_or_error(data, "line_3")),
            city=str(get_value_or_error(data, "city")),
            state=str(get_value_or_error(data, "state")),
            country=str(get_value_or_error(data, "country")),
            postcode=str(get_value_or_error(data, "postcode")),
        )
