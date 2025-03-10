from datetime import datetime
from typing import Optional, List

from dateutil import parser

from mode_groothandel.clients.utils import (
    get_value_or_error,
    get_value_or_none,
    apply_from_data_or_error,
    apply_from_data_to_list_or_error,
    get_value_or_default,
)
from uphance.clients.models.address import Address
from uphance.clients.models.line_item import LineItem


class PickTicket:
    """Pick Ticket class."""

    def __init__(
        self,
        _id: int,
        created_at: Optional[datetime],
        updated_at: Optional[datetime],
        stock_adjusted_at: Optional[datetime],
        tracking_number: Optional[str],
        carrier: Optional[str],
        service: Optional[str],
        notes: Optional[str],
        items_total: float,
        items_tax: float,
        subtotal: float,
        total_tax: float,
        grand_total: float,
        total_quantity: int,
        currency: Optional[str],
        order_number: int,
        # This is not set when a pick ticket is deleted.
        order_id: Optional[int],
        order_source: str,
        warehouse: str,
        channel: str,
        shipment_number: int,
        commercial_invoice_number: int,
        organisation_id: int,
        sale_id: int,
        customer_id: int,
        customer_name: str,
        customer_note: Optional[str],
        date: datetime,
        shipping_cost: float,
        shipping_tax: float,
        shipping_method: Optional[str],
        address: Address,
        contact_name: Optional[str],
        contact_email: Optional[str],
        contact_phone: str,
        dimensions: Optional[str],
        gross_weight: Optional[float],
        net_weight: Optional[float],
        gross_weight_unit: str,
        weight_unit: str,
        status: str,
        shipper_email_address: Optional[str],
        shipping_instructions: Optional[str],
        payment_terms: str,
        invoice_numbers: str,
        estimated_shipping_cost: float,
        line_items: List[LineItem],
    ):
        """Initialise Pick Ticket object."""
        self.id = _id
        self.created_at = created_at
        self.updated_at = updated_at
        self.stock_adjusted_at = stock_adjusted_at
        self.tracking_number = tracking_number
        self.carrier = carrier
        self.service = service
        self.notes = notes
        self.items_total = items_total
        self.items_tax = items_tax
        self.subtotal = subtotal
        self.total_tax = total_tax
        self.grand_total = grand_total
        self.total_quantity = total_quantity
        self.currency = currency
        self.order_number = order_number
        self.order_id = order_id
        self.order_source = order_source
        self.warehouse = warehouse
        self.channel = channel
        self.shipment_number = shipment_number
        self.commercial_invoice_number = commercial_invoice_number
        self.organisation_id = organisation_id
        self.sale_id = sale_id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_note = customer_note
        self.date = date
        self.shipping_cost = shipping_cost
        self.shipping_tax = shipping_tax
        self.shipping_method = shipping_method
        self.address = address
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.dimensions = dimensions
        self.gross_weight = gross_weight
        self.net_weight = net_weight
        self.gross_weight_unit = gross_weight_unit
        self.weight_unit = weight_unit
        self.status = status
        self.shipper_email_address = shipper_email_address
        self.shipping_instructions = shipping_instructions
        self.payment_terms = payment_terms
        self.invoice_numbers = invoice_numbers
        self.estimated_shipping_cost = estimated_shipping_cost
        self.line_items = line_items

    @staticmethod
    def from_data(data: dict) -> "PickTicket":
        """Initialise Pick Ticket object from data."""
        return PickTicket(
            _id=int(get_value_or_none(data, "id")),
            created_at=(
                parser.parse(get_value_or_none(data, "created_at", str))
                if get_value_or_none(data, "created_at", str) is not None
                else None
            ),
            updated_at=(
                parser.parse(get_value_or_none(data, "updated_at", str))
                if get_value_or_none(data, "created_at", str) is not None
                else None
            ),
            stock_adjusted_at=(
                None
                if get_value_or_none(data, "stock_adjusted_at") is None
                else parser.parse(get_value_or_error(data, "stock_adjusted_at"))
            ),
            tracking_number=get_value_or_none(data, "tracking_number"),
            carrier=get_value_or_none(data, "carrier"),
            service=get_value_or_none(data, "service"),
            notes=get_value_or_none(data, "notes"),
            items_total=float(get_value_or_default(data, "items_total", 0)),
            items_tax=float(get_value_or_default(data, "items_tax", 0)),
            subtotal=float(get_value_or_default(data, "subtotal", 0)),
            total_tax=float(get_value_or_default(data, "total_tax", 0)),
            grand_total=float(get_value_or_default(data, "grand_total", 0)),
            total_quantity=int(get_value_or_default(data, "total_quantity", 0)),
            currency=get_value_or_none(data, "currency", str),
            order_number=get_value_or_none(data, "order_number", int),
            order_id=get_value_or_none(data, "order_id", int),
            order_source=str(get_value_or_error(data, "order_source")),
            warehouse=str(get_value_or_error(data, "warehouse")),
            channel=str(get_value_or_error(data, "channel")),
            shipment_number=int(get_value_or_error(data, "shipment_number")),
            commercial_invoice_number=int(get_value_or_error(data, "commercial_invoice_number")),
            organisation_id=int(get_value_or_error(data, "organisation_id")),
            sale_id=int(get_value_or_error(data, "sale_id")),
            customer_id=int(get_value_or_error(data, "customer_id")),
            customer_name=str(get_value_or_error(data, "customer_name")),
            customer_note=get_value_or_none(data, "customer_note"),
            date=parser.parse(get_value_or_error(data, "date")),
            shipping_cost=float(get_value_or_error(data, "shipping_cost")),
            shipping_tax=float(get_value_or_error(data, "shipping_tax")),
            shipping_method=get_value_or_none(data, "shipping_method"),
            address=apply_from_data_or_error(Address.from_data, data, "address"),
            contact_name=get_value_or_none(data, "contact_name"),
            contact_email=get_value_or_none(data, "contact_email", str),
            contact_phone=get_value_or_none(data, "contact_phone", str),
            dimensions=get_value_or_none(data, "dimensions"),
            gross_weight=get_value_or_none(data, "gross_weight", float),
            net_weight=get_value_or_none(data, "net_weight", float),
            gross_weight_unit=get_value_or_error(data, "gross_weight_unit"),
            weight_unit=get_value_or_error(data, "weight_unit"),
            status=get_value_or_error(data, "status"),
            shipper_email_address=get_value_or_none(data, "shipper_email_address"),
            shipping_instructions=get_value_or_none(data, "shipping_instructions"),
            payment_terms=get_value_or_error(data, "payment_terms"),
            invoice_numbers=get_value_or_error(data, "invoice_numbers"),
            estimated_shipping_cost=float(get_value_or_error(data, "estimated_shipping_cost")),
            line_items=apply_from_data_to_list_or_error(LineItem.from_data, data, "line_items"),
        )
