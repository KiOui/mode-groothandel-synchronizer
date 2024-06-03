from datetime import datetime
from typing import Optional, Any, List

from dateutil import parser

from mode_groothandel.clients.utils import get_value_or_error, get_value_or_none, apply_from_data_to_list_or_error
from uphance.clients.models.line_item import LineItem


class CreditNote:

    def __init__(self, _id: int, created_at: datetime, updated_at: datetime, items_total: float, items_tax: float, subtotal: float, total_tax: float, grand_total: float, total_quantity: int, overpayment: Optional[Any], reference: Optional[Any], total_credited: float, total_refunded: float, amount_outstanding: float, settlement_discount_percentage: float, freeform_amount: Optional[float], freeform_description: str, freeform_tax: Optional[Any], organisation_id: int, credit_note_number: int, order_number: int, warehouse_name: str, line_items: List[LineItem]):
        self.id = _id
        self.created_at = created_at
        self.updated_at = updated_at
        self.items_total = items_total
        self.items_tax = items_tax
        self.subtotal = subtotal
        self.total_tax = total_tax
        self.grand_total = grand_total
        self.total_quantity = total_quantity
        self.overpayment = overpayment
        self.reference = reference
        self.total_credited = total_credited
        self.total_refunded = total_refunded
        self.amount_outstanding = amount_outstanding
        self.settlement_discount_percentage = settlement_discount_percentage
        self.freeform_amount = freeform_amount
        self.freeform_description = freeform_description
        self.freeform_tax = freeform_tax
        self.organisation_id = organisation_id
        self.credit_note_number = credit_note_number
        self.order_number = order_number
        self.warehouse_name = warehouse_name
        self.line_items = line_items

    @staticmethod
    def from_data(data: dict) -> "CreditNote":
        return CreditNote(
            _id=get_value_or_error(data, "id"),
            created_at=parser.parse(str(get_value_or_error(data, "created_at"))),
            updated_at=parser.parse(str(get_value_or_error(data, "updated_at"))),
            items_total=float(get_value_or_error(data, "items_total")),
            items_tax=float(get_value_or_error(data, "items_tax")),
            subtotal=float(get_value_or_error(data, "subtotal")),
            total_tax=float(get_value_or_error(data, "total_tax")),
            grand_total=float(get_value_or_error(data, "grand_total")),
            total_quantity=int(get_value_or_error(data, "total_quantity")),
            overpayment=get_value_or_none(data, "overpayment"),
            reference=get_value_or_none(data, "reference"),
            total_credited=float(get_value_or_error(data, "total_credited")),
            total_refunded=float(get_value_or_error(data, "total_refunded")),
            amount_outstanding=float(get_value_or_error(data, "amount_outstanding")),
            settlement_discount_percentage=float(get_value_or_error(data, "settlement_discount_percentage")),
            freeform_amount=get_value_or_none(data, "freeform_amount"),
            freeform_description=str(get_value_or_error(data, "freeform_description")),
            freeform_tax=get_value_or_none(data, "freeform_tax"),
            organisation_id=int(get_value_or_error(data, "organisation_id")),
            credit_note_number=int(get_value_or_error(data, "credit_note_number")),
            order_number=int(get_value_or_error(data, "order_number")),
            warehouse_name=str(get_value_or_error(data, "warehouse_name")),
            line_items=apply_from_data_to_list_or_error(LineItem.from_data, data, "line_items"),
        )