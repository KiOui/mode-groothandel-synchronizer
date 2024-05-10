import abc
import json
import logging
from typing import Optional, List, Tuple
from urllib.parse import quote_plus

import requests
import urllib3
from requests.adapters import HTTPAdapter

from mode_groothandel.clients.authentication import AuthClient

logger = logging.getLogger(__name__)


class ApiException(Exception):

    def __init__(self, http_status, code, msg, reason=None, headers=None):
        """Initialize API Exception."""
        self.http_status = http_status
        self.code = code
        self.msg = msg
        self.reason = reason
        if headers is None:
            headers = {}
        self.headers = headers

    def __str__(self):
        """Conver this object to string."""
        return "http status: {0}, code:{1} - {2}, reason: {3}".format(
            self.http_status, self.code, self.msg, self.reason
        )


class ApiClient(abc.ABC):
    """API client class."""

    default_retry_codes = (429, 500, 502, 503, 504)

    def __init__(
        self,
        base_url: str,
        auth: Optional[str] = None,
        requests_session=True,
        auth_manager: Optional[AuthClient] = None,
        requests_timeout: int = 5,
        status_forcelist=None,
        retries: int = 3,
        status_retries: int = 3,
        backoff_factor: float = 0.3,
    ):
        """Initialize API Client."""
        if not base_url.endswith("/"):
            base_url = base_url + "/"
        self.prefix = base_url
        self._auth = auth
        self._auth_manager = auth_manager
        self.requests_timeout = requests_timeout
        self.status_forcelist = status_forcelist or self.default_retry_codes
        self.backoff_factor = backoff_factor
        self.retries = retries
        self.status_retries = status_retries

        if isinstance(requests_session, requests.Session):
            self._session = requests_session
        else:
            if requests_session:  # Build a new session.
                self._build_session()
            else:  # Use the Requests API module as a "session".
                self._session = requests.api

    @property
    def api_url(self):
        """Get API URL."""
        raise NotImplemented

    @property
    def auth_manager(self):
        """Get the auth manager."""
        return self._auth_manager

    def _build_session(self):
        """Build a request session."""
        self._session = requests.Session()
        retry = urllib3.Retry(
            total=self.retries,
            connect=None,
            read=False,
            allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE"]),
            status=self.status_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist,
        )

        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def __del__(self):
        """Make sure the connection (pool) gets closed."""
        if isinstance(self._session, requests.Session):
            self._session.close()

    def _auth_headers(self):
        """Get authentication headers via the auth manager or a fixed Bearer token."""
        if self._auth:
            return {"Authorization": "Bearer {0}".format(self._auth)}
        elif self.auth_manager:
            token = self.auth_manager.get_access_token()
            return {"Authorization": "Bearer {0}".format(token)}
        else:
            return {}

    def _internal_call(self, method, url, payload, params):
        """Do an internal request."""
        args = dict(params=params)
        if not url.startswith("http"):
            url = self.api_url + url
        headers = self._auth_headers()

        if "content_type" in args["params"]:
            headers["Content-Type"] = args["params"]["content_type"]
            del args["params"]["content_type"]
            if payload:
                args["data"] = payload
        else:
            headers["Content-Type"] = "application/json"
            if payload:
                args["data"] = json.dumps(payload)

        logger.debug(
            "Sending %s to %s with Params: %s Headers: %s and Body: %r ",
            method,
            url,
            args.get("params"),
            headers,
            args.get("data"),
        )

        try:
            response = self._session.request(method, url, headers=headers, timeout=self.requests_timeout, **args)

            response.raise_for_status()
            results = response.json()
        except requests.exceptions.HTTPError as http_error:
            response = http_error.response
            print(response.text)
            try:
                json_response = response.json()
                error = json_response.get("error", {})
                msg = error.get("message")
                reason = error.get("reason")
            except ValueError:
                msg = response.text or None
                reason = None
            except AttributeError:
                msg = response.text or None
                reason = None

            logger.error(
                "HTTP Error for %s to %s with Params: %s returned %s due to %s",
                method,
                url,
                args.get("params"),
                response.status_code,
                msg,
            )

            raise ApiException(
                response.status_code,
                -1,
                "%s:\n %s" % (response.url, msg),
                reason=reason,
                headers=response.headers,
            )
        except requests.exceptions.RetryError as retry_error:
            request = retry_error.request
            logger.error("Max Retries reached")
            try:
                reason = retry_error.args[0].reason
            except (IndexError, AttributeError):
                reason = None
            raise ApiException(429, -1, "%s:\n %s" % (request.path_url, "Max Retries"), reason=reason)
        except ValueError:
            results = None

        logger.debug("RESULTS: %s", results)
        return results

    @staticmethod
    def _create_querystring_safe(query: List[Tuple[str, str | None]]) -> str:
        safe_filtered_query: List[(str, str)] = list()
        for query_key, query_value in query:
            if query_value is not None:
                safe_filtered_query.append((quote_plus(query_key), quote_plus(query_value)))
                # safe_filtered_query.append((quote_plus(query_key), quote_plus(query_value)))
        return ApiClient._create_querystring(safe_filtered_query)

    @staticmethod
    def _create_querystring(query: List[Tuple[str, str]]) -> str:
        if len(query) == 0:
            return ""
        else:
            query_string = ""
            prepend = "?"
            for query_key, query_value in query:
                query_string += "{}{}={}".format(prepend, query_key, query_value)
                if prepend == "?":
                    prepend = "&"
            return query_string

    def _get(self, url, args=None, payload=None, **kwargs):
        """GET request."""
        if args:
            kwargs.update(args)

        return self._internal_call("GET", url, payload, kwargs)

    def _post(self, url, args=None, payload=None, **kwargs):
        """POST request."""
        if args:
            kwargs.update(args)
        return self._internal_call("POST", url, payload, kwargs)

    def _delete(self, url, args=None, payload=None, **kwargs):
        """DELETE request."""
        if args:
            kwargs.update(args)
        return self._internal_call("DELETE", url, payload, kwargs)

    def _put(self, url, args=None, payload=None, **kwargs):
        """PUT request."""
        if args:
            kwargs.update(args)
        return self._internal_call("PUT", url, payload, kwargs)
