from __future__ import annotations

from typing import Optional

from wikipediaapi import Wikipedia

from config import default_config
from src.domain.page import Page
from src.retrieval.interfaces import InterfacePageRepository


class WikiPediaAPIRepository:
    """Adapter that exposes the third-party `wikipediaapi` library through our
    `InterfacePageRepository` port.

    Single responsibility: **translate** between the external Wikipedia client
    and our domain. This is the Adapter pattern — `wikipediaapi` is a
    third-party API whose shape we don't control, so we wrap it behind our own
    stable interface rather than letting its types leak into the codebase.

    Deliberately THIN: it contains NONE of the concerns that used to bloat the
    old `WikipediaAPI` God Object:
      * budget / legality / discovery  -> handled by RetrievalGuardDecorator
      * embeddings                     -> the processing layer (IEmbedder)
      * scoring                        -> the evaluation layer (IScorer)
      * the final dataset ledger       -> the collection agent

    So this class has exactly one job: fetch raw page data from Wikipedia and
    return it as a `Page` value object. Anything else belongs elsewhere.

    Notably this class does NOT know about `legal_pages` or `known_pages` —
    those are constraint concerns owned by the guard decorator. A pure adapter
    has no opinions about which pages are "allowed".
    """


    # The Wikipedia client is *injected* (DIP). A default factory keeps normal
    # usage one-line (`WikiPediaAPIRepository()`) while still allowing a fake
    # client to be passed for tests — that is what makes this class testable in
    # isolation, with no network access.
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
    # The port's two methods. The adapter maps each to the underlying client.

    def search_pages(self, query: str) -> list[str]:
        """Return up to `max_results` page titles reachable from `query`.

        The external `wikipediaapi` client has no search-by-query endpoint; it
        resolves a page by title. We approximate "search" the way the legacy
        code did: resolve the query as a page, then take its outgoing links.

        Legality filtering (the en.tsv set) is intentionally NOT done here —
        that is the RetrievalGuardDecorator's responsibility, not the adapter's.
        Returning too many candidates is harmless: the guard filters them and
        records only the legal ones.
        """
        try:
            page = self._wiki_api.page(query)
        except Exception:
            # A network/protocol error is not the adapter's concern to handle
            # beyond "this search produced nothing". Let the guard's accounting
            # decide what to do with the spent request.
            return []
        if not page.exists():
            return []

        # The page itself plus its top links are the candidate titles. Slice to
        # max_results to mirror the legacy ~10 candidates/query behaviour.
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
