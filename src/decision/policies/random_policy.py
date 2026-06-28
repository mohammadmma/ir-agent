from __future__ import annotations

import random
from typing import Optional

from config import default_config
from src.decision.interfaces import InterfaceSelectionPolicy
from src.domain.page import Page


class RandomPolicy:
    """Selection policy that reproduces the legacy agent's behaviour.

    Strategy: shuffle candidates and accept any page with enough content.
    No diversity optimization, no state — the simplest possible policy.

    This is the baseline. A `GreedyDiversityPolicy` (Step 9) would
    replace this to actively maximize diversity — but the agent itself
    wouldn't change. That's the Strategy pattern payoff.
    """

    def __init__(self, min_char: int = default_config.page_config.min_char) -> None:
        self._min_char = min_char

    def select_next(self, candidates: list[str]) -> Optional[str]:
        """Return a random candidate (shuffles in place, picks first).

        The legacy code shuffled the entire candidate list once, then
        iterated sequentially. This preserves that exact behaviour.
        """
        if not candidates:
            return None
        random.shuffle(candidates)
        return candidates[0]

    def observe(self, page: Page) -> None:
        """No-op: the random policy has no state to update."""
        pass

    def should_keep(self, page: Page) -> bool:
        """Accept any page with content above the minimum character threshold."""
        return page.has_min_content(self._min_char)
