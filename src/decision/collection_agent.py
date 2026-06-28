from __future__ import annotations

import logging
import time
from typing import Optional

from config import default_config
from src.decision.interfaces import (
    CollectionResult,
    InterfaceAgent,
    InterfaceSelectionPolicy,
)
from src.decision.seed_queries import SEED_QUERIES
from src.domain.page import Page
from src.retrieval.interfaces import InterfacePageRepository
from src.utils.exceptions import BudgetExceededError

logger = logging.getLogger(__name__)


class CollectionAgent:
    """Orchestrator: search → fetch → decide → collect → done.

    Single responsibility: run the collection loop and own the resulting
    pages. It delegates every *quality decision* to the selection policy and
    every *retrieval operation* to the repository.

    This class does NOT know about:
      * embeddings          → evaluation layer's concern
      * wikirank / scoring  → evaluation layer's concern
      * persistence          → `main.py`'s concern (composition root)

    It depends only on abstractions (DIP):
      * `InterfacePageRepository`  — search and fetch pages
      * `InterfaceSelectionPolicy` — what to fetch next, what to keep

    The 3-phase loop preserves the legacy agent's exact behaviour:
      Phase 1: Broad search — discover candidates via diverse seed queries
      Phase 2: Fetch — iterate candidates, fetch and keep via policy
      Phase 3: Fill — use remaining known pages to reach the target
    """

    def __init__(
        self,
        repo: InterfacePageRepository,
        policy: InterfaceSelectionPolicy,
        target_pages: int = default_config.agent_conf.target_pages,
        budget_phase1: int = default_config.agent_conf.budget_phase1,
        budget_limit: int = default_config.agent_conf.budget_limit,
        min_char: int = default_config.page_config.min_char,
        max_candidate_pool: int = default_config.agent_conf.max_candidate_pool,
        log_interval: int = default_config.agent_conf.log_interval,
        seed_queries: list[str] | None = None,
    ) -> None:
        self._repo = repo
        self._policy = policy
        self._target_pages = target_pages
        self._budget_phase1 = budget_phase1
        self._budget_limit = budget_limit
        self._min_char = min_char
        self._max_candidate_pool = max_candidate_pool
        self._log_interval = log_interval
        self._seed_queries = seed_queries or SEED_QUERIES

    # ── InterfaceAgent ───────────────────────────────────────────────

    def collect_dataset(self) -> CollectionResult:
        """Run the full 3-phase collection loop. Returns the result."""
        start_time = time.time()
        collected: list[Page] = []
        collected_titles: set[str] = set()
        candidate_pool: set[str] = set()

        logger.info("=" * 70)
        logger.info("WIKIPEDIA DATASET COLLECTION")
        logger.info("=" * 70)
        logger.info(
            "Target: %d pages | Phase-1 budget: %d | Hard limit: %d",
            self._target_pages, self._budget_phase1, self._budget_limit,
        )

        # ── Phase 1: Broad search ─────────────────────────────────────
        self._phase1_search(candidate_pool)
        logger.info("Phase 1 done: %d candidates\n", len(candidate_pool))

        # ── Phase 2: Fetch candidates ─────────────────────────────────
        self._phase2_fetch(
            candidate_pool, collected, collected_titles, start_time,
        )
        logger.info("Phase 2 done: %d pages\n", len(collected))

        # ── Phase 3: Fill from remaining known pages ──────────────────
        if len(collected) < self._target_pages:
            self._phase3_fill(collected, collected_titles, start_time)

        elapsed = time.time() - start_time

        # ── Summary ────────────────────────────────────────────────────
        logger.info("=" * 70)
        logger.info("COLLECTION COMPLETE!")
        logger.info("=" * 70)
        logger.info("Pages collected: %d/%d", len(collected), self._target_pages)
        logger.info("Time: %.1f minutes", elapsed / 60)
        logger.info("=" * 70 + "\n")

        return CollectionResult(
            pages=tuple(collected),
            requests_used=self._repo.requests_used,
            elapsed_seconds=elapsed,
        )

    # ── Phase implementations ─────────────────────────────────────────
    # Each phase is a private method with a clear single purpose.
    # Extracted from the legacy monolithic `collect_dataset()`.

    def _phase1_search(self, candidate_pool: set[str]) -> None:
        """Discover candidates via diverse seed queries."""
        logger.info("Phase 1: Searching diverse topics...")
        queries = self._seed_queries

        for i, query in enumerate(queries):
            # Stop if budget spent or pool is large enough
            if self._repo.requests_used >= self._budget_phase1:
                break
            if len(candidate_pool) >= self._max_candidate_pool:
                break

            try:
                titles = self._repo.search_pages(query)
                candidate_pool.update(titles)
                if (i + 1) % self._log_interval == 0:
                    logger.info(
                        "  %d searches | %d candidates | %d requests",
                        i + 1, len(candidate_pool), self._repo.requests_used,
                    )
            except BudgetExceededError:
                logger.warning("Phase 1: budget exhausted during search")
                break
            except Exception:
                continue

    def _phase2_fetch(
        self,
        candidate_pool: set[str],
        collected: list[Page],
        collected_titles: set[str],
        start_time: float,
    ) -> None:
        """Fetch candidates, keep pages that pass the policy's quality gate."""
        logger.info("Phase 2: Fetching pages...")
        candidates = list(candidate_pool - collected_titles)

        for page_name in candidates:
            if len(collected) >= self._target_pages:
                break
            if self._repo.requests_used >= self._budget_limit:
                break

            try:
                page = self._repo.fetch_page(page_name)
                if page is None:
                    continue
                if not self._policy.should_keep(page):
                    continue

                collected.append(page)
                collected_titles.add(page.title)
                self._policy.observe(page)

                if len(collected) % self._log_interval == 0:
                    self._log_progress(collected, start_time)
            except BudgetExceededError:
                logger.warning("Phase 2: budget exhausted")
                break
            except Exception:
                continue

    def _phase3_fill(
        self,
        collected: list[Page],
        collected_titles: set[str],
        start_time: float,
    ) -> None:
        """Try remaining known pages to reach the target count."""
        logger.info("Phase 3: Filling remaining from known pages...")
        # The guard's `known_pages` contains everything discovered via search
        # or links during phases 1–2. Try any we haven't fetched yet.
        remaining = list(self._repo.known_pages - collected_titles)

        for page_name in remaining:
            if len(collected) >= self._target_pages:
                break
            if self._repo.requests_used >= self._budget_limit:
                break

            try:
                page = self._repo.fetch_page(page_name)
                if page is None:
                    continue
                if not self._policy.should_keep(page):
                    continue

                collected.append(page)
                collected_titles.add(page.title)
                self._policy.observe(page)

                if len(collected) % 100 == 0:
                    self._log_progress(collected, start_time)
            except BudgetExceededError:
                logger.warning("Phase 3: budget exhausted")
                break
            except Exception:
                continue

    # ── helpers ───────────────────────────────────────────────────────

    def _log_progress(self, collected: list[Page], start_time: float) -> None:
        elapsed = time.time() - start_time
        rate = len(collected) / max(elapsed, 1)
        eta = (self._target_pages - len(collected)) / rate / 60
        logger.info(
            "  %d/%d | %d requests | ETA: %.1f min",
            len(collected), self._target_pages, self._repo.requests_used, eta,
        )


# ── factory for dev mode ────────────────────────────────────────────
# A convenience function that builds the agent with dev-mode overrides
# from config. Keeps `main.py` clean — it just calls `make_dev_agent()`.

def make_agent(
    repo: InterfacePageRepository,
    policy: InterfaceSelectionPolicy,
    dev_mode: bool = default_config.agent_conf.dev_mode,
) -> CollectionAgent:
    """Build a CollectionAgent with production or dev-mode config overrides."""
    conf = default_config.agent_conf

    if dev_mode:
        return CollectionAgent(
            repo=repo,
            policy=policy,
            target_pages=conf.dev_target_pages,
            budget_phase1=conf.dev_budget_phase1,
            budget_limit=conf.dev_budget_limit,
            min_char=conf.dev_min_char,
            log_interval=10,
        )

    return CollectionAgent(
        repo=repo,
        policy=policy,
        target_pages=conf.target_pages,
        budget_phase1=conf.budget_phase1,
        budget_limit=conf.budget_limit,
    )
