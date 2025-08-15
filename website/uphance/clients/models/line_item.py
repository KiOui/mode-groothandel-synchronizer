from dataclasses import dataclass
from typing import List

from mode_groothandel.clients.utils import get_value_or_error, apply_from_data_to_list_or_error
from uphance.clients.models.line_quantity import LineQuantity


@dataclass
class LineItem:
    """Invoice Line Item."""

    id: int
    product_id: int
    product_name: str
    variation_id: int
    color: str
    unit_tax: float
    tax_level: float
    unit_price: float
    original_price: float
    weight: float
    weight_unit: str
    percentage_discount: float
    country_of_origin: str
    intrastat_code: str
    line_quantities: List[LineQuantity]

    @staticmethod
    def from_data(data: dict) -> "LineItem":
        """Initialize the LineItem object from a dictionary."""
        return LineItem(
            id=int(get_value_or_error(data, "id")),
            product_id=int(get_value_or_error(data, "product_id")),
            product_name=str(get_value_or_error(data, "product_name")),
            variation_id=int(get_value_or_error(data, "variation_id")),
            color=str(get_value_or_error(data, "color")),
            unit_tax=float(get_value_or_error(data, "unit_tax")),
            tax_level=float(get_value_or_error(data, "tax_level")),
            unit_price=float(get_value_or_error(data, "unit_price")),
            original_price=float(get_value_or_error(data, "original_price")),
            weight=float(get_value_or_error(data, "weight")),
            weight_unit=str(get_value_or_error(data, "weight_unit")),
            percentage_discount=float(get_value_or_error(data, "percentage_discount")),
            country_of_origin=str(get_value_or_error(data, "country_of_origin")),
            intrastat_code=str(get_value_or_error(data, "intrastat_code")),
            line_quantities=apply_from_data_to_list_or_error(LineQuantity.from_data, data, "line_quantities"),
        )
