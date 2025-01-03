from mode_groothandel.clients.utils import get_value_or_error


class LineQuantity:
    """Invoice Line quantity item."""

    def __init__(self, line_quantity_id: int, size: str, quantity: int, sku_id: int):
        """Initialize a LineQuantity object."""
        self.id = line_quantity_id
        self.size = size
        self.quantity = quantity
        self.sku_id = sku_id

    @staticmethod
    def from_data(data: dict) -> "LineQuantity":
        """Initialize a LineQuantity object from a dictionary."""
        return LineQuantity(
            line_quantity_id=int(get_value_or_error(data, "id")),
            size=str(get_value_or_error(data, "size")),
            quantity=int(get_value_or_error(data, "quantity")),
            sku_id=int(get_value_or_error(data, "sku_id")),
        )
