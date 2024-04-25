from typing import List, Optional

from mode_groothandel.clients.utils import get_value_or_error, apply_from_data_to_list_or_none, get_value_or_none
from snelstart.clients.models.rgs_code import RgsCode


class Grootboek:

    def __init__(
        self,
        modified_on: str,
        omschrijving: str,
        kostenplaats_verplicht: bool,
        rekening_code: str,
        nonactief: bool,
        nummer: int,
        grootboekfunctie: str,
        grootboek_rubriek: str,
        rgs_code: Optional[List[RgsCode]],
        btw_soort: List[str],
        vat_rate_code: Optional[str],
        _id: str,
        uri: str,
    ):
        self.modified_on = modified_on
        self.omschrijving = omschrijving
        self.kostenplaats_verplicht = kostenplaats_verplicht
        self.rekening_code = rekening_code
        self.nonactief = nonactief
        self.nummer = nummer
        self.grootboekfunctie = grootboekfunctie
        self.grootboek_rubriek = grootboek_rubriek
        self.rgs_code = rgs_code
        self.btw_soort = btw_soort
        self.vat_rate_code = vat_rate_code
        self.id = _id
        self.uri = uri

    @staticmethod
    def from_data(data: dict) -> "Grootboek":
        return Grootboek(
            modified_on=str(get_value_or_error(data, "modifiedOn")),
            omschrijving=str(get_value_or_error(data, "omschrijving")),
            kostenplaats_verplicht=bool(get_value_or_error(data, "kostenplaatsVerplicht")),
            rekening_code=str(get_value_or_error(data, "rekeningCode")),
            nonactief=bool(get_value_or_error(data, "nonactief")),
            nummer=int(get_value_or_error(data, "nummer")),
            grootboekfunctie=str(get_value_or_error(data, "grootboekfunctie")),
            grootboek_rubriek=str(get_value_or_error(data, "grootboekRubriek")),
            rgs_code=apply_from_data_to_list_or_none(RgsCode.from_data, data, "rgsCode"),
            btw_soort=[str(x) for x in get_value_or_error(data, "btwSoort")],
            vat_rate_code=get_value_or_none(data, "vatRateCode"),
            _id=str(get_value_or_error(data, "id")),
            uri=str(get_value_or_error(data, "uri")),
        )

    def __str__(self):
        """Convert this object to string."""
        return f"Grootboek {self.omschrijving} ({self.id}%)"
