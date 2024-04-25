from typing import Optional

from mode_groothandel.clients.utils import get_value_or_error, get_value_or_none


class PageMeta:
    """Meta data returned for pages."""

    def __init__(
        self, current_page: int, next_page: Optional[str], prev_page: Optional[str], total_pages: int, total_count: int
    ):
        """Initialize a PageMeta object."""
        self.current_page = current_page
        self.next_page = next_page
        self.prev_page = prev_page
        self.total_pages = total_pages
        self.total_count = total_count

    @staticmethod
    def from_data(data: dict) -> "PageMeta":
        """Initialize a PageMeta object from a dictionary."""
        return PageMeta(
            current_page=int(get_value_or_error(data, "current_page")),
            next_page=get_value_or_none(data, "next_page"),
            prev_page=get_value_or_none(data, "prev_page"),
            total_pages=int(get_value_or_error(data, "total_pages")),
            total_count=int(get_value_or_error(data, "total_count")),
        )
