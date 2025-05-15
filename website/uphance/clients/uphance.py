import logging
from typing import Optional

from django.conf import settings

from mode_groothandel.clients.api import ApiClient
from mode_groothandel.clients.cache.cache import CacheFileHandler
from mode_groothandel.clients.utils import (
    get_value_or_error,
    apply_from_data_or_error,
    apply_from_data_to_list_or_error,
)
from uphance.clients.authentication import UphanceAuthClient
from uphance.clients.models.api_page import ApiPage
from uphance.clients.models.channel import Channel
from uphance.clients.models.credit_note import CreditNote
from uphance.clients.models.customer import Customer
from uphance.clients.models.invoice import Invoice
from uphance.clients.models.pick_ticket import PickTicket
from uphance.clients.models.sales_order import SalesOrder

logger = logging.getLogger(__name__)


class Uphance(ApiClient):
    """Uphance API client class."""

    @staticmethod
    def get_client() -> "Uphance":
        uphance_username = settings.UPHANCE_USERNAME
        uphance_password = settings.UPHANCE_PASSWORD

        cache_path = settings.UPHANCE_CACHE_PATH

        uphance_auth_client = UphanceAuthClient(
            uphance_username, uphance_password, cache=CacheFileHandler(cache_path=cache_path)
        )

        return Uphance("https://api.uphance.com/", auth_manager=uphance_auth_client)

    @property
    def api_url(self) -> str:
        return self.prefix

    def organisations(self):
        return self._get("organisations")

    def set_current_organisation(self, organisation_id: int) -> bool:
        response = self._post("organisations/set_current_org", payload={"organizationId": organisation_id})
        return "Status" in response.keys() and response["Status"] == "Updated"

    def invoice(self, invoice_id: int) -> Optional[Invoice]:
        url = f"invoices/?invoice_id={invoice_id}"
        response = self._get(url)
        if not isinstance(response, dict):
            return None

        if "invoices" not in response.keys():
            return None

        invoices = get_value_or_error(response, "invoices")

        if len(invoices) > 0:
            return Invoice.from_data(invoices[0])
        else:
            return None

    def invoices(self, since_id: Optional[int] = None, page: int = 1) -> ApiPage[Invoice]:
        queries = [("since_id", str(since_id) if since_id is not None else None), ("page", str(page))]
        url = "invoices/" + self._create_querystring_safe(queries)
        response = self._get(url)
        return ApiPage.from_response(response, "invoices", Invoice.from_data)

    def channels(self) -> list[Channel]:
        """Retrieve the channels from Uphance."""
        data = self._get("channels")
        return apply_from_data_to_list_or_error(Channel.from_data, data, "channels")

    def order(self, order_id: int) -> SalesOrder:
        url = f"sales_orders/{order_id}"
        response = self._get(url)
        return SalesOrder.from_data(response)

    def orders(self, order_number: Optional[int]) -> ApiPage[SalesOrder]:
        url = "sales_orders/" + self._create_querystring_safe([("by_order_number", str(order_number))])
        response = self._get(url)
        return ApiPage.from_response(response, "sales_orders", SalesOrder.from_data)

    def credit_note(self, credit_note_id: int) -> CreditNote:
        url = f"credit_notes/{credit_note_id}"
        data = self._get(url)
        return apply_from_data_or_error(CreditNote.from_data, data, "credit_notes")

    def credit_notes(self, since_id: Optional[int] = None, page: int = 1) -> ApiPage[CreditNote]:
        queries = [("since_id", str(since_id) if since_id is not None else None), ("page", str(page))]
        url = "credit_notes/" + self._create_querystring_safe(queries)
        response = self._get(url)
        return ApiPage.from_response(response, "credit_notes", CreditNote.from_data)

    def pick_ticket(self, pick_ticket_id: int) -> PickTicket:
        url = f"pick_tickets/{pick_ticket_id}"
        data = self._get(url)
        return apply_from_data_or_error(PickTicket.from_data, data, "pick_ticket")

    def pick_tickets(self, since_id: Optional[int] = None, page: int = 1) -> ApiPage[PickTicket]:
        queries = [("since_id", str(since_id) if since_id is not None else None), ("page", str(page))]
        url = "pick_tickets/" + self._create_querystring_safe(queries)
        response = self._get(url)
        return ApiPage.from_response(response, "pick_tickets", PickTicket.from_data)

    def customer_by_id(self, customer_id: int) -> Customer:
        response = self._get("customers/" + str(customer_id))
        return apply_from_data_or_error(Customer.from_data, response, "customer")

    def customers(self, page: int = 1) -> ApiPage[Customer]:
        queries = [("page", str(page))]
        url = "customers/" + self._create_querystring_safe(queries)
        response = self._get(url)
        return ApiPage.from_response(response, "customers", Customer.from_data)
