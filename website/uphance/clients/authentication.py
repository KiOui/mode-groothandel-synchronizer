import json
import logging
import time
from typing import Optional

import requests

from mode_groothandel.clients.authentication import AuthClient
from mode_groothandel.clients.cache.cache import CacheFileHandler


logger = logging.getLogger(__name__)


class UphanceAuthClient(AuthClient):

    TOKEN_URL = "https://api.uphance.com/oauth/token"

    def __init__(self, email: str, password: str, cache: Optional[CacheFileHandler] = None):
        self.email = email
        self.password = password

        if cache is not None:
            self.cache = cache
        else:
            self.cache = CacheFileHandler()

        self._session = requests.Session()

    def request_access_token(self):
        headers = {
            "Content-Type": "application/json",
        }

        body = json.dumps(
            {
                "email": self.email,
                "password": self.password,
                "grant_type": "password",
            }
        )

        try:
            response = self._session.post(self.TOKEN_URL, headers=headers, data=body)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            response = http_error.response
            try:
                json_response = response.json()
                error = json_response.get("error", {})
            except ValueError:
                error = response.text

            logger.error(
                "HTTP Error for POST to %s with Params: %s returned %s due to %s",
                self.TOKEN_URL,
                response.status_code,
                error,
            )

            return None
        except requests.exceptions.RetryError:
            logger.error("Max Retries reached for POST to %s", self.TOKEN_URL)
            return None

        try:
            result = response.json()
            return result
        except ValueError:
            logger.error(
                "Failed to extract JSON token for POST to %s with Params: %s returned %s due to %s",
                self.TOKEN_URL,
                response.status_code,
                response.text,
            )
            return None

    @staticmethod
    def token_is_valid(token: dict) -> bool:
        if "expires_at" not in token.keys():
            return False

        now = int(time.time())
        return token["expires_at"] - now > 60

    @staticmethod
    def _add_custom_values_to_token(token: dict) -> dict:
        token["expires_at"] = int(time.time()) + token["expires_in"]
        return token

    def get_access_token(self) -> Optional[dict]:
        cached_token = self.cache.get_cached_token()
        if cached_token is not None and self.token_is_valid(cached_token):
            return cached_token["access_token"]
        else:
            new_token = self.request_access_token()
            if new_token is not None:
                new_token = self._add_custom_values_to_token(new_token)
                self.cache.save_token_to_cache(new_token)
                return new_token["access_token"]
            else:
                return None
