from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from src.domain.page import Page


@runtime_checkable
class InterfacePageRepository(Protocol):
    """Port: read access to Wikipedia pages."""

    def search_pages(self, query: str) -> list[str]:
        """Search Wikipedia for `query`; return discovered page titles."""
        ...

    def fetch_page(self, page_name: str) -> Optional[Page]:
        """Load a previously-discovered page as a `Page` value object."""
        ...
