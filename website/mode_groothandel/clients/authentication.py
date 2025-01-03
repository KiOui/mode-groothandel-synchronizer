import abc
from typing import Optional


class AuthClient(abc.ABC):

    @abc.abstractmethod
    def get_access_token(self) -> Optional[dict]:
        pass
