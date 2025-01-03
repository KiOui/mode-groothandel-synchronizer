from typing import List

from mode_groothandel.clients.utils import get_value_or_error, apply_from_data_to_list_or_error
from uphance.clients.models.line_quantity import LineQuantity


class LineItem:
    """Invoice Line Item."""

    def __init__(
        self,
        line_item_id: int,
        product_id: int,
        product_name: str,
        variation_id: int,
        color: str,
        unit_tax: float,
        tax_level: float,
        unit_price: float,
        original_price: float,
        percentage_discount: float,
        line_quantities: List[LineQuantity],
    ):
        """Initialize the LineItem object."""
        self.id = line_item_id
        self.product_id = product_id
        self.product_name = product_name
        self.variation_id = variation_id
        self.color = color
        self.unit_tax = unit_tax
        self.tax_level = tax_level
        self.unit_price = unit_price
        self.original_price = original_price
        self.percentage_discount = percentage_discount
        self.line_quantities = line_quantities

    @staticmethod
    def from_data(data: dict) -> "LineItem":
        """Initialize the LineItem object from a dictionary."""
        return LineItem(
            line_item_id=int(get_value_or_error(data, "id")),
            product_id=int(get_value_or_error(data, "product_id")),
            product_name=str(get_value_or_error(data, "product_name")),
            variation_id=int(get_value_or_error(data, "variation_id")),
            color=str(get_value_or_error(data, "color")),
            unit_tax=float(get_value_or_error(data, "unit_tax")),
            tax_level=float(get_value_or_error(data, "tax_level")),
            unit_price=float(get_value_or_error(data, "unit_price")),
            original_price=float(get_value_or_error(data, "original_price")),
            percentage_discount=float(get_value_or_error(data, "percentage_discount")),
            line_quantities=apply_from_data_to_list_or_error(LineQuantity.from_data, data, "line_quantities"),
        )
