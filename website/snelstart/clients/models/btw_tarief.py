from mode_groothandel.clients.utils import get_value_or_error


class BtwTarief:

    def __init__(self, btw_soort: str, btw_percentage: float, datum_vanaf: str, datum_tot_en_met: str):
        self.btw_soort = btw_soort
        self.btw_percentage = btw_percentage
        self.datum_vanaf = datum_vanaf
        self.datum_tot_en_met = datum_tot_en_met

    @staticmethod
    def from_data(data: dict) -> "BtwTarief":
        return BtwTarief(
            btw_soort=str(get_value_or_error(data, "btwSoort")),
            btw_percentage=get_value_or_error(data, "btwPercentage"),
            datum_vanaf=str(get_value_or_error(data, "datumVanaf")),
            datum_tot_en_met=str(get_value_or_error(data, "datumTotEnMet")),
        )

    def __str__(self):
        """Convert this object to string."""
        return f"BTW tarief {self.btw_soort} ({self.btw_percentage}%)"
