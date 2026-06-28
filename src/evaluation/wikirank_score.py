from __future__ import annotations

import logging
from typing import Iterable

import pandas as pd

from src.domain.page import Page
from src.evaluation.interfaces import InterfaceWikiRankScorer

logger = logging.getLogger(__name__)


class WikiRankScorer:
    """Score a dataset by its mean WikiRank quality from an external ground truth.

    The ground truth (en.tsv) maps page names to a quality score. This scorer
    looks up each collected page and returns the mean quality — a proxy for
    "how important/complete are the pages we collected."

    Satisfies `InterfaceWikiRankScorer`. The ground truth is injected via the
    constructor (DIP) so the scorer doesn't depend on a hardcoded file path,
    and tests can inject a tiny fixture DataFrame.
    """

    def __init__(self, ground_truth: pd.DataFrame) -> None:
        # Pre-index for fast lookup — avoids re-merging on every call.
        self._quality = dict(zip(
            ground_truth["page_name"],
            ground_truth["wikirank_quality"],
        ))

    def score(self, pages: Iterable[Page], ground_truth: pd.DataFrame = None) -> float:
        """Mean WikiRank quality for the given pages.

        Parameters
        ----------
        pages : Iterable[Page]
            The collected pages to score.
        ground_truth : pd.DataFrame
            Accepted to satisfy the `InterfaceWikiRankScorer` protocol, but
            IGNORED — the scorer uses the ground truth from its constructor.
            This avoids passing a large DataFrame on every call while still
            matching the interface signature.
        """
        titles = [p.title for p in pages]
        scores = [self._quality[t] for t in titles if t in self._quality]

        if not scores:
            logger.warning("No collected pages matched the ground truth.")
            return 0.0

        return float(sum(scores) / len(scores))
