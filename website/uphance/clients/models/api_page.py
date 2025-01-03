from typing import List, Callable, Any

from mode_groothandel.clients.utils import apply_from_data_to_list_or_error, apply_from_data_or_error
from uphance.clients.models.page_meta import PageMeta


class ApiPage[T]:
    """Api Page model."""

    def __init__(self, objects: List[T], meta: PageMeta):
        """Initialise ApiPage model."""
        self.objects = objects
        self.meta = meta

    @staticmethod
    def from_response(response_data: dict, objects_key: str, from_data: Callable[[Any], T]) -> "ApiPage":
        """Initialise ApiPage model."""
        return ApiPage(
            objects=apply_from_data_to_list_or_error(from_data, response_data, objects_key),
            meta=apply_from_data_or_error(PageMeta.from_data, response_data, "meta"),
        )
