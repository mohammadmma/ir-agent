from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable
from dataclasses import dataclass
from src.domain.page import Page
from src.retrieval.interfaces import InterfacePageRepository


@dataclass(frozen=True)
class CollectionResult:
    pages: tuple[Page, ...]
    requests_used: int
    elapsed_seconds: float

@runtime_checkable
class InterfaceSelectionPolicy(Protocol):
    """Port: decide which candidate to fetch next and whether to keep it.

    This is the "brain" seam of the agent. The orchestrator (collection
    agent) owns the mechanical loop — search, fetch, embed, budget — and
    delegates every *quality decision* here. That separation is what lets
    us swap `RandomPolicy` (today's behaviour) for `GreedyDiversityPolicy`
    (Step 9) without touching the crawler.

    Statefulness is left to the implementation: a greedy policy must track
    what's already in the dataset to score marginal gains, while a random
    policy needs none. The orchestrator therefore always informs the policy
    of the current selected set via `observe`.
    """

    def select_next(self, candidates: list[str]) -> Optional[str]:
        """Pick the next page title to fetch from `candidates`.

        Returns `None` when the policy has no further recommendation (e.g.
        all candidates exhausted). The orchestrator owns budget/ordering
        concerns; the policy only expresses preference.
        """
        ...

    def observe(self, page: Page) -> None:
        """Inform the policy that `page` has been added to the dataset.

        Stateful policies update their internal model (e.g. embedding
        centroid) here. Stateless policies may no-op.
        """
        ...

    def should_keep(self, page: Page) -> bool:
        """Decide whether a fetched page is worth keeping.

        Encodes quality gates such as minimum content length. Returning
        `False` lets the orchestrator discard the page without saving.
        """
        ...

@runtime_checkable
class InterfaceAgent(Protocol):
    def collect_dataset(self) -> CollectionResult:
        ...
