import logging
from typing import List, Any

from django.conf import settings

from mode_groothandel.clients.api import ApiClient
from sendcloud.client.authentication import SendcloudAuthClient
from sendcloud.client.models.shipping_method import ShippingMethod

logger = logging.getLogger(__name__)


class Sendcloud(ApiClient):
    """Sendcloud API client class."""

    @staticmethod
    def get_client() -> "Sendcloud":
        """Create a Sendcloud client from Django settings."""
        sendcloud_public_key = settings.SENDCLOUD_PUBLIC_KEY
        sendcloud_private_key = settings.SENDCLOUD_PRIVATE_KEY

        sendcloud_auth_client = SendcloudAuthClient(sendcloud_public_key, sendcloud_private_key)

        return Sendcloud("https://panel.sendcloud.sc/api/v2/", auth_manager=sendcloud_auth_client)

    def _auth_headers(self):
        """Retrieve the authentication headers."""
        if self._auth:
            return {"Authorization": "Basic {}".format(self._auth)}
        elif self.auth_manager:
            return {"Authorization": "Basic {}".format(self.auth_manager.get_access_token())}
        else:
            return {}

    @property
    def api_url(self) -> str:
        """Retrieve the API prefix."""
        return self.prefix

    def create_parcel(self, parcel) -> Any:
        """Create a parcel in Sendcloud."""
        return self._post(
            "parcels",
            payload=parcel,
        )

    def update_parcel(self, parcel) -> Any:
        """Update a parcel in Sendcloud."""
        return self._put("parcels", payload=parcel)

    def cancel_parcel(self, parcel_id: str) -> Any:
        """Cancel (remove) a parcel from Sendcloud."""
        return self._post(f"parcels/{parcel_id}/cancel")

    def get_shipping_methods(self) -> List[ShippingMethod]:
        """Retrieve shipping methods."""
        response = self._get("shipping_methods")
        return [ShippingMethod.from_data(x) for x in response["shipping_methods"]]
