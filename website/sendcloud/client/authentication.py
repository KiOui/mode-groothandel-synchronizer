import base64
import logging
from typing import Optional

from mode_groothandel.clients.authentication import AuthClient


logger = logging.getLogger(__name__)


class SendcloudAuthClient(AuthClient):
    """Authentication client for communicating with Sendcloud."""

    def __init__(self, public_key: str, private_key: str):
        """Initialize Authentication Client."""
        self.public_key = public_key
        self.private_key = private_key

    def get_access_token(self) -> str:
        """Retrieve the access token as header information."""
        b = base64.b64encode(bytes(f"{self.public_key}:{self.private_key}", "utf-8"))  # bytes
        return b.decode("utf-8")
