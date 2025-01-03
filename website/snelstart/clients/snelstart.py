import logging
from typing import Optional, Any, List

from django.conf import settings

from mode_groothandel.clients.api import ApiClient
from mode_groothandel.clients.cache.cache import CacheFileHandler
from snelstart.clients.authentication import SnelstartAuthClient
from snelstart.clients.models.btw_tarief import BtwTarief
from snelstart.clients.models.grootboek import Grootboek
from snelstart.clients.models.land import Land
from snelstart.clients.models.relatie import Relatie

logger = logging.getLogger(__name__)


class Snelstart(ApiClient):
    """Snelstart API client class."""

    def __init__(self, subscription_key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscription_key = subscription_key

    @staticmethod
    def get_client() -> "Snelstart":
        snelstart_client_key = settings.SNELSTART_CLIENT_KEY
        snelstart_subscription_key = settings.SNELSTART_SUBSCRIPTION_KEY

        cache_path = settings.SNELSTART_CACHE_PATH

        snelstart_auth_client = SnelstartAuthClient(
            snelstart_client_key, cache=CacheFileHandler(cache_path=cache_path)
        )

        return Snelstart(
            snelstart_subscription_key, "https://b2bapi.snelstart.nl/v2/", auth_manager=snelstart_auth_client
        )

    @property
    def api_url(self) -> str:
        return self.prefix

    def _auth_headers(self):
        if self.auth_manager is None:
            return {
                "Ocp-Apim-Subscription-Key": self.subscription_key,
            }
        else:
            access_token = self.auth_manager.get_access_token()
            return {
                "Authorization": f"Bearer {access_token}",
                "Ocp-Apim-Subscription-Key": self.subscription_key,
            }

    def add_verkoopboeking(self, data: Any) -> Any:
        return self._post("verkoopboekingen", payload=data)

    def update_verkoopboeking(self, _id: str, data: Any) -> Any:
        return self._put(f"verkoopboekingen/{_id}", payload=data)

    def delete_verkoopboeking(self, _id: str):
        return self._delete(f"verkoopboekingen/{_id}")

    def get_grootboeken(self) -> List[Grootboek]:
        response = self._get("grootboeken")
        return [Grootboek.from_data(x) for x in response]

    def get_relaties(
        self,
        skip: Optional[int] = None,
        top: Optional[int] = None,
        _filter: Optional[str] = None,
        expand: Optional[str] = None,
    ) -> List[Relatie]:
        queries = [
            ("$skip", str(skip) if skip is not None else None),
            ("$top", str(top) if top is not None else None),
            ("$filter", _filter),
            ("$expand", expand),
        ]
        url = "relaties" + self._create_querystring_safe(queries)
        response = self._get(url)
        return [Relatie.from_data(x) for x in response]

    def get_relatie(self, snelstart_id: str) -> Relatie:
        response = self._get(f"relaties/{snelstart_id}")
        return Relatie.from_data(response)

    def update_relatie(self, snelstart_id: str, relatie: Any) -> Relatie:
        response = self._put(f"relaties/{snelstart_id}", payload=relatie)
        return Relatie.from_data(response)

    def add_relatie(self, relatie: Any) -> Relatie:
        response = self._post("relaties", payload=relatie)
        return Relatie.from_data(response)

    def get_btwtarieven(self) -> [BtwTarief]:
        response = self._get("btwtarieven")
        return [BtwTarief.from_data(x) for x in response]

    def get_landen(self) -> List[Land]:
        response = self._get("landen")
        return [Land.from_data(x) for x in response]
