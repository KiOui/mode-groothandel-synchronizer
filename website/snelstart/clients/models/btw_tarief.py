from datetime import datetime

from dateutil import parser

from mode_groothandel.clients.utils import get_value_or_error


class BtwTarief:
    """Snelstart Tax type."""

    def __init__(self, btw_soort: str, btw_percentage: float, datum_vanaf: datetime, datum_tot_en_met: datetime):
        """Initialize Snelstart Tax Type."""
        self.btw_soort = btw_soort
        self.btw_percentage = btw_percentage
        self.datum_vanaf = datum_vanaf
        self.datum_tot_en_met = datum_tot_en_met

    @staticmethod
    def from_data(data: dict) -> "BtwTarief":
        """Convert a dictionary to a BtwTarief."""
        return BtwTarief(
            btw_soort=str(get_value_or_error(data, "btwSoort")),
            btw_percentage=get_value_or_error(data, "btwPercentage"),
            datum_vanaf=parser.parse(str(get_value_or_error(data, "datumVanaf"))),
            datum_tot_en_met=parser.parse(str(get_value_or_error(data, "datumTotEnMet"))),
        )

    def __str__(self):
        """Convert this object to string."""
        return f"BTW tarief {self.btw_soort} ({self.btw_percentage}%)"
