from __future__ import annotations

from typing import Iterable, Optional
from pathlib import Path
import pandas as pd

from src.domain.page import Page
from src.retrieval.interfaces import InterfacePageRepository
from src.utils.exceptions import BudgetExceededError, IllegalRequestError
from config import default_config


class RetrievalGuardDecorator:
    """Decorator over `InterfacePageRepository` enforcing the project's three
    retrieval constraints:

      1. **Budget**    — at most `limit` requests may be issued.
      2. **Discovery** — a page may be fetched only after it was seen in a
                         `search_pages` result or as a link of a fetched page.
      3. **Legality**  — only pages in `legal_pages` (the en.tsv page-name set)
                         are accepted as results / fetchable.

    The guard is a *concrete* class that *implements* `InterfacePageRepository`,
    so it is a drop-in stand-in for a bare repository: any client expecting
    `InterfacePageRepository` (the collection agent) works unchanged with a
    guarded or an unguarded repository.
    """

    def __init__(
        self,
        inner: InterfacePageRepository,
        wikirank_dataset_path: Path = default_config.paths.en_tsv_file_path,
        request_limit: int = default_config.wiki_api_conf.page_request_limit,
    ) -> None:
        self._inner = inner
        self._request_limit = request_limit
        self._legal_pages: set[str] = set(pd.read_csv(wikirank_dataset_path, sep='\t')['page_name'].to_list())
        self._known_pages: set[str] = set()
        self._requests_used = 0

    # ── read-only state (consumed by the orchestrator) ────────────────
    @property
    def requests_used(self) -> int:
        return self._requests_used

    @property
    def remaining_budget(self) -> int:
        return max(self._request_limit - self._requests_used, 0)

    @property
    def known_pages(self) -> frozenset[str]:
        """Pages discovered so far (a subset of legal pages)."""
        return frozenset(self._known_pages)

    # ── internal helpers ──────────────────────────────────────────────
    def _charge(self) -> None:
        """Account for one request, refusing to exceed the budget."""
        if self._requests_used >= self._request_limit:
            raise BudgetExceededError(
                f"API budget exhausted: {self._requests_used}/{self._request_limit} requests used."
            )
        self._requests_used += 1

    def _enforce_fetchable(self, page_name: str) -> None:
        """Validate a fetch BEFORE charging. A rejected request makes no API
        call, so it must not consume budget.
        """
        if page_name not in self._known_pages:
            raise IllegalRequestError(
                f"'{page_name}' has not been discovered yet "
                f"(pages may be fetched only after search or via links)."
            )
        if page_name not in self._legal_pages:
            raise IllegalRequestError(f"'{page_name}' is not in the legal page set.")

    def _record_discovered(self, titles: Iterable[str]) -> None:
        """Remember the legal titles we have now seen (search results or
        fetched-page links), so they become fetchable later."""
        self._known_pages.update(t for t in titles if t in self._legal_pages)

    # ── InterfacePageRepository ───────────────────────────────────────
    def search_pages(self, query: str) -> list[str]:
        self._charge()
        titles = self._inner.search_pages(query)
        legal_titles = [t for t in titles if t in self._legal_pages]
        self._record_discovered(legal_titles)
        return legal_titles

    def fetch_page(self, page_name: str) -> Optional[Page]:
        self._enforce_fetchable(page_name)

        self._charge()

        try:
            page = self._inner.fetch_page(page_name)
        except Exception:
            self._requests_used -= 1
            raise
        if page is None:
            self._requests_used -= 1
            return None

        self._record_discovered(page.links)
        return page
