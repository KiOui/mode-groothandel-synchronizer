from datetime import datetime
from typing import Optional, List
from dateutil import parser

from mode_groothandel.clients.utils import (
    get_value_or_error,
    get_value_or_none,
    apply_from_data_or_error,
    apply_from_data_to_list_or_error,
    apply_from_data_or_none,
)
from uphance.clients.models.address import Address
from uphance.clients.models.contact import Contact
from uphance.clients.models.line_item import LineItem


class Invoice:
    """Invoice."""

    def __init__(
        self,
        invoice_id: int,
        created_at: Optional[datetime],
        updated_at: Optional[datetime],
        items_total: float,
        items_tax: float,
        subtotal: float,
        total_tax: float,
        grand_total: float,
        total_quantity: int,
        shipping_cost: float,
        shipping_tax: float,
        settlement_discount_percentage: float,
        invoice_number: int,
        due_date: datetime,
        invoice_type: str,
        total_paid: float,
        total_credited: float,
        total_discounted: Optional[float],
        amount_outstanding: float,
        channel_id: int,
        channel_name: str,
        currency: str,
        tax_rate_name: Optional[str],
        payment_terms: str,
        order_number: str,
        customer_name: str,
        billing_address: Address,
        shipping_address: Address,
        billing_contact: Optional[Contact],
        shipping_contact: Optional[Contact],
        organisation_id: int,
        company_id: int,
        payments_count: int,
        sale_id: int,
        line_items: List[LineItem],
    ):
        """Initialize an Invoice object."""
        self.id = invoice_id
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
        self.settlement_discount_percentage = settlement_discount_percentage
        self.invoice_number = invoice_number
        self.due_date = due_date
        self.invoice_type = invoice_type
        self.total_paid = total_paid
        self.total_credited = total_credited
        self.total_discounted = total_discounted
        self.amount_outstanding = amount_outstanding
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.currency = currency
        self.tax_rate_name = tax_rate_name
        self.payment_terms = payment_terms
        self.order_number = order_number
        self.customer_name = customer_name
        self.billing_address = billing_address
        self.shipping_address = shipping_address
        self.billing_contact = billing_contact
        self.shipping_contact = shipping_contact
        self.organisation_id = organisation_id
        self.company_id = company_id
        self.payments_count = payments_count
        self.sale_id = sale_id
        self.line_items = line_items

    @staticmethod
    def from_data(data: dict) -> "Invoice":
        """Initialize an Invoice object from a dictionary."""
        return Invoice(
            invoice_id=int(get_value_or_error(data, "id")),
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
            items_total=float(get_value_or_error(data, "items_total")),
            items_tax=float(get_value_or_error(data, "items_tax")),
            subtotal=float(get_value_or_error(data, "subtotal")),
            total_tax=float(get_value_or_error(data, "total_tax")),
            grand_total=float(get_value_or_error(data, "grand_total")),
            total_quantity=int(get_value_or_error(data, "total_quantity")),
            shipping_cost=float(get_value_or_error(data, "shipping_cost")),
            shipping_tax=float(get_value_or_error(data, "shipping_tax")),
            settlement_discount_percentage=float(get_value_or_error(data, "settlement_discount_percentage")),
            invoice_number=int(get_value_or_error(data, "invoice_number")),
            due_date=parser.parse(str(get_value_or_error(data, "due_date"))),
            invoice_type=get_value_or_error(data, "invoice_type"),
            total_paid=float(get_value_or_error(data, "total_paid")),
            total_credited=float(get_value_or_error(data, "total_credited")),
            total_discounted=get_value_or_none(data, "total_discounted"),
            amount_outstanding=float(get_value_or_error(data, "amount_outstanding")),
            channel_id=int(get_value_or_error(data, "channel_id")),
            channel_name=str(get_value_or_error(data, "channel_name")),
            currency=str(get_value_or_error(data, "currency")),
            tax_rate_name=get_value_or_none(data, "tax_rate_name", str),
            payment_terms=str(get_value_or_error(data, "payment_terms")),
            order_number=str(get_value_or_error(data, "order_number")),
            customer_name=str(get_value_or_error(data, "customer_name")),
            billing_address=apply_from_data_or_error(Address.from_data, data, "billing_address"),
            shipping_address=apply_from_data_or_error(Address.from_data, data, "shipping_address"),
            billing_contact=apply_from_data_or_none(Contact.from_data, data, "billing_contact"),
            shipping_contact=apply_from_data_or_none(Contact.from_data, data, "shipping_contact"),
            organisation_id=int(get_value_or_error(data, "organisation_id")),
            company_id=int(get_value_or_error(data, "company_id")),
            payments_count=int(get_value_or_error(data, "payments_count")),
            sale_id=int(get_value_or_error(data, "sale_id")),
            line_items=apply_from_data_to_list_or_error(LineItem.from_data, data, "line_items"),
        )

    def __str__(self):
        """Convert this object to string."""
        return f"Invoice #{self.invoice_number} ({self.id})"
