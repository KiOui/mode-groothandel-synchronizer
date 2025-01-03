import abc
import errno
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CacheHandler(abc.ABC):
    """
    An abstraction layer for handling the caching and retrieval of
    authorization tokens.

    Custom extensions of this class must implement get_cached_token
    and save_token_to_cache methods with the same input and output
    structure as the CacheHandler class.
    """

    @abc.abstractmethod
    def get_cached_token(self) -> Optional[dict]:
        """Get and return a token_info dictionary object."""
        pass

    @abc.abstractmethod
    def save_token_to_cache(self, token_info) -> bool:
        """Save a token_info dictionary object to the cache and return whether the operation succeeded."""
        pass


class CacheFileHandler(CacheHandler):
    """Handles reading and writing cached authorization tokens as json files on disk."""

    def __init__(self, cache_path: Optional[str] = None):
        """Initialize a Cache File Handler."""
        if cache_path:
            self.cache_path = cache_path
        else:
            self.cache_path = ".cache"

    def get_cached_token(self) -> Optional[dict]:
        """Retrieve a cached token from a cache file."""
        token_info = None

        try:
            f = open(self.cache_path)
            token_info_string = f.read()
            f.close()
            token_info = json.loads(token_info_string)
        except IOError as error:
            if error.errno == errno.ENOENT:
                logger.debug("Cache does not exist at: %s", self.cache_path)
            else:
                logger.warning("Couldn't read cache at: %s", self.cache_path)

        return token_info

    def save_token_to_cache(self, token_info) -> bool:
        """Save a token to a cache file."""
        try:
            f = open(self.cache_path, "w")
            f.write(json.dumps(token_info))
            f.close()
            return True
        except IOError:
            logger.warning("Couldn't write token to cache at: %s", self.cache_path)
            return False
