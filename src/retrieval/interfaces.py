from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from src.domain.page import Page


@runtime_checkable
class InterfacePageRepository(Protocol):
    """Port: read access to Wikipedia pages.

    A repository knows how to *discover* pages (search) and *load* a known
    page (fetch). It deliberately does **not** own scoring, embeddings,
    persistence, or the final dataset — those are separate concerns living
    in their own layers.

    Contract / invariants for any implementation:
      * `fetch_page` may be called only for titles returned (now or earlier)
        by `search_pages` or discovered as links in a fetched page.
      * An implementation MAY enforce a request budget and page legality,
        raising when violated — but that enforcement is itself a separate,
        decoratable concern (see `utils/constraints.py`). A bare repository
        is not required to enforce it.
      * `fetch_page` returns `None` when the page does not exist, rather
        than raising, so callers can treat "missing" as ordinary control flow.
    """

    def search_pages(self, query: str) -> list[str]:
        """Search Wikipedia for `query`; return discovered page titles.

        Implementations typically return up to ~10 titles. The call counts
        against any enforced request budget.
        """
        ...

    def fetch_page(self, page_name: str) -> Optional[Page]:
        """Load a previously-discovered page as a `Page` value object.

        Returns `None` if the page does not exist. Raises if `page_name` was
        never discovered or is illegal (when the implementation enforces it).
        """
        ...
