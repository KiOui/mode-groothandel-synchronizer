from mode_groothandel.clients.utils import get_value_or_error


class RgsCode:

    def __init__(self, versie: str, rgs_code: str):
        self.versie = versie
        self.rgs_code = rgs_code

    @staticmethod
    def from_data(data: dict) -> "RgsCode":
        return RgsCode(
            versie=str(get_value_or_error(data, "versie")),
            rgs_code=str(get_value_or_error(data, "rgsCode")),
        )

    def __str__(self):
        """Convert this object to string."""
        return f"RGS Code {self.rgs_code}"
