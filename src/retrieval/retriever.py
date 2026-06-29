from __future__ import annotations

from typing import Optional

from wikipediaapi import Wikipedia

from config import default_config
from src.domain.page import Page
from src.retrieval.interfaces import InterfacePageRepository


class WikiPediaAPIRepository:
    def __init__(
        self,
        user_agent: str = "MyAgent/1.0",
        language: str = "en",
        client: Wikipedia | None = None,
        max_results: int = default_config.wiki_api_conf.max_search_result,
    ) -> None:
        self._wiki_api = client or Wikipedia(user_agent, language)
        self._max_results = max_results

    # ── InterfacePageRepository ───────────────────────────────────────
    def search_pages(self, query: str) -> list[str]:
        """Return up to `max_results` page titles reachable from `query`.

        The external `wikipediaapi` client has no search-by-query endpoint; it
        resolves a page by title.
        """
        try:
            page = self._wiki_api.page(query)
        except Exception:
            return []
        if not page.exists():
            return []

        titles = [page.title]
        titles.extend(list(page.links.keys())[: self._max_results - 1])
        return titles[: self._max_results]

    def fetch_page(self, page_name: str) -> Optional[Page]:
        """Load a single page as a `Page` value object.

        Returns `None` if the page does not exist (ordinary control flow, not
        an exception) so the guard and the agent can treat "missing" simply.
        Links/categories are stored as tuples to match the immutable `Page`.
        """
        page = self._wiki_api.page(page_name)
        if not page.exists():
            return None

        return Page(
            title=page.title,
            content=page.text,
            url=page.fullurl,
            links=tuple(page.links.keys()),
            categories=tuple(page.categories.keys()),
        )
