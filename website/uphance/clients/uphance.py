import logging
from typing import Optional

from django.conf import settings

from mode_groothandel.clients.api import ApiClient
from mode_groothandel.clients.cache.cache import CacheFileHandler
from mode_groothandel.clients.utils import get_value_or_error, get_value_or_none, apply_from_data_or_error
from uphance.clients.authentication import UphanceAuthClient
from uphance.clients.models.api_page import ApiPage
from uphance.clients.models.customer import Customer
from uphance.clients.models.invoice import Invoice

logger = logging.getLogger(__name__)


class UphancePaginatedResponse:

    def __init__(
        self,
        current_page: int,
        next_page: Optional[int],
        previous_page: Optional[int],
        total_pages: int,
        total_count: int,
        data,
    ):
        self.current_page = current_page
        self.next_page = next_page
        self.previous_page = previous_page
        self.total_pages = total_pages
        self.total_count = total_count
        self.data = data

    @staticmethod
    def from_data(data: dict) -> "UphancePaginatedResponse":
        metadata = get_value_or_error(data, "meta")
        del data["meta"]

        return UphancePaginatedResponse(
            get_value_or_error(metadata, "current_page"),
            get_value_or_none(metadata, "next_page"),
            get_value_or_none(metadata, "prev_page"),
            get_value_or_error(metadata, "total_pages"),
            get_value_or_error(metadata, "total_count"),
            data,
        )


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

    def order(self, order_id: int) -> dict:
        url = f"sales_orders/{order_id}"
        return self._get(url)

    def orders(self, order_number: Optional[int]) -> UphancePaginatedResponse:
        url = "sales_orders/" + self._create_querystring_safe([("by_order_number", str(order_number))])
        response = self._get(url)
        return UphancePaginatedResponse.from_data(response)

    def credit_note(self, credit_note_id: int) -> dict:
        url = f"credit_notes/{credit_note_id}"
        data = self._get(url)
        return get_value_or_error(data, "credit_notes")

    def credit_notes(self, since_id: Optional[int] = None, page: int = 1) -> UphancePaginatedResponse:
        queries = [("since_id", str(since_id) if since_id is not None else None), ("page", str(page))]
        url = "credit_notes/" + self._create_querystring_safe(queries)
        response = self._get(url)
        return UphancePaginatedResponse.from_data(response)

    def pick_ticket(self, pick_ticket_id: int) -> dict:
        url = f"pick_tickets/{pick_ticket_id}"
        data = self._get(url)
        return get_value_or_error(data, "pick_ticket")

    def pick_tickets(self, since_id: Optional[int] = None, page: int = 1) -> UphancePaginatedResponse:
        queries = [("since_id", str(since_id) if since_id is not None else None), ("page", str(page))]
        url = "pick_tickets/" + self._create_querystring_safe(queries)
        response = self._get(url)
        return UphancePaginatedResponse.from_data(response)

    def customer_by_id(self, customer_id: int) -> Customer:
        response = self._get("customers/" + str(customer_id))
        return apply_from_data_or_error(Customer.from_data, response, "customer")
