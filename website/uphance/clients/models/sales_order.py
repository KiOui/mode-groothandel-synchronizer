from datetime import datetime
from typing import Optional, List

from dateutil import parser

from mode_groothandel.clients.utils import get_value_or_error, get_value_or_none, apply_from_data_to_list_or_error
from uphance.clients.models.line_item import LineItem


class SalesOrder:

    def __init__(
        self,
        _id: int,
        created_at: datetime,
        updated_at: datetime,
        items_total: float,
        items_tax: float,
        subtotal: float,
        total_tax: float,
        grand_total: float,
        total_quantity: int,
        shipping_cost: float,
        shipping_tax: float,
        settlement_discount: float,
        deposit_percentage: float,
        start_ship_date: Optional[datetime],
        cancel_ship_date: Optional[datetime],
        submitted_at: Optional[datetime],
        confirmed_at: Optional[datetime],
        notes: Optional[str],
        internal_notes: Optional[str],
        currency: str,
        proforma_number: Optional[int],
        order_number: int,
        purchase_order_ref: str,
        invoice_numbers: str,
        shipment_numbers: str,
        next_due_date: Optional[datetime],
        company_name: str,
        season_id: int,
        organisation_id: int,
        channel_id: int,
        company_id: int,
        invoice_method: str,
        warehouse_name: str,
        fulfillment_status: str,
        financial_status: str,
        payment_term_name: str,
        shipping_instructions: Optional[str],
        line_items: List[LineItem],
    ):
        self.id = _id
        self.created_at = created_at
        self.updated_at = updated_at
        self.items_total = items_total
        self.items_tax = items_tax
        self.subtotal = subtotal
        self.total_tax = total_tax
        self.grand_total = grand_total
        self.total_quantity = total_quantity
        self.shipping_cost = shipping_cost
        self.shipping_tax = shipping_tax
        self.settlement_discount = settlement_discount
        self.deposit_percentage = deposit_percentage
        self.start_ship_date = start_ship_date
        self.cancel_ship_date = cancel_ship_date
        self.submitted_at = submitted_at
        self.confirmed_at = confirmed_at
        self.notes = notes
        self.internal_notes = internal_notes
        self.currency = currency
        self.proforma_number = proforma_number
        self.order_number = order_number
        self.purchase_order_ref = purchase_order_ref
        self.invoice_numbers = invoice_numbers
        self.shipment_numbers = shipment_numbers
        self.next_due_date = next_due_date
        self.company_name = company_name
        self.season_id = season_id
        self.organisation_id = organisation_id
        self.channel_id = channel_id
        self.company_id = company_id
        self.invoice_method = invoice_method
        self.warehouse_name = warehouse_name
        self.fulfillment_status = fulfillment_status
        self.financial_status = financial_status
        self.payment_term_name = payment_term_name
        self.shipping_instructions = shipping_instructions
        self.line_items = line_items

    @staticmethod
    def from_data(data: dict) -> "SalesOrder":
        return SalesOrder(
            _id=int(get_value_or_error(data, "id")),
            created_at=parser.parse(str(get_value_or_error(data, "created_at"))),
            updated_at=parser.parse(str(get_value_or_error(data, "updated_at"))),
            items_total=float(get_value_or_error(data, "items_total")),
            items_tax=float(get_value_or_error(data, "items_tax")),
            subtotal=float(get_value_or_error(data, "subtotal")),
            total_tax=float(get_value_or_error(data, "total_tax")),
            grand_total=float(get_value_or_error(data, "grand_total")),
            total_quantity=int(get_value_or_error(data, "total_quantity")),
            shipping_cost=float(get_value_or_error(data, "shipping_cost")),
            shipping_tax=float(get_value_or_error(data, "shipping_tax")),
            settlement_discount=float(get_value_or_error(data, "settlement_discount")),
            deposit_percentage=float(get_value_or_error(data, "deposit_percentage")),
            start_ship_date=(
                None
                if get_value_or_none(data, "start_ship_date") is None
                else parser.parse(get_value_or_error(data, "start_ship_date"))
            ),
            cancel_ship_date=(
                None
                if get_value_or_none(data, "cancel_ship_date") is None
                else parser.parse(get_value_or_error(data, "cancel_ship_date"))
            ),
            submitted_at=(
                None
                if get_value_or_none(data, "submitted_at") is None
                else parser.parse(get_value_or_error(data, "submitted_at"))
            ),
            confirmed_at=(
                None
                if get_value_or_none(data, "confirmed_at") is None
                else parser.parse(get_value_or_error(data, "confirmed_at"))
            ),
            notes=get_value_or_none(data, "notes"),
            internal_notes=get_value_or_none(data, "internal_notes"),
            currency=str(get_value_or_error(data, "currency")),
            proforma_number=get_value_or_none(data, "proforma_number"),
            order_number=int(get_value_or_error(data, "order_number")),
            purchase_order_ref=get_value_or_error(data, "purchase_order_ref"),
            invoice_numbers=get_value_or_error(data, "invoice_numbers"),
            shipment_numbers=get_value_or_error(data, "shipment_numbers"),
            next_due_date=(
                None
                if get_value_or_none(data, "next_due_date") is None
                else parser.parse(get_value_or_error(data, "next_due_date"))
            ),
            company_name=get_value_or_error(data, "company_name"),
            season_id=int(get_value_or_error(data, "season_id")),
            organisation_id=int(get_value_or_error(data, "organisation_id")),
            channel_id=int(get_value_or_error(data, "channel_id")),
            company_id=int(get_value_or_error(data, "company_id")),
            invoice_method=get_value_or_error(data, "invoice_method"),
            warehouse_name=get_value_or_error(data, "warehouse_name"),
            fulfillment_status=get_value_or_error(data, "fulfillment_status"),
            financial_status=get_value_or_error(data, "financial_status"),
            payment_term_name=get_value_or_error(data, "payment_term_name"),
            shipping_instructions=get_value_or_none(data, "shipping_instructions"),
            line_items=apply_from_data_to_list_or_error(LineItem.from_data, data, "line_items"),
        )
