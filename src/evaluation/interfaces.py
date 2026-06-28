from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol, runtime_checkable
from pandas import DataFrame

from src.domain.page import Page



@dataclass(frozen=True)
class DiversityReport:
    """Structured result of a multi-component diversity evaluation.

    Individual sub-scores (lexical / semantic / category) are exposed so
    callers can inspect them, while `overall` gives the single weighted
    number. Frozen so the report is a safe-to-share value object.
    """

    lexical: float
    semantic: float
    category: float
    
    def overall_score(self, lexical_weight: float = 0.3, semantic_weight: float = 0.4, category_weight: float = 0.3) -> float:
        return (self.lexical * lexical_weight) + (self.semantic * semantic_weight) + (self.category * category_weight)


@runtime_checkable
class InterfaceScorer(Protocol):
    """Port: score a collection of pages with a single scalar in [0, 1].

    The lowest-common-denominator contract: any one-dimensional quality
    signal (a sub-diversity metric, the composite diversity, etc.) can
    satisfy it. This is what the decision layer asks for when it only needs
    a number to compare candidates.
    """

    def score(self, pages: Iterable[Page]) -> float:
        ...

@runtime_checkable
class InterfaceWikiRankScorer(Protocol):
    def score(self, dataset: Iterable[Page], ground_truth: DataFrame) -> float:
        ...


@runtime_checkable
class InterfaceDiversityEvaluator(InterfaceScorer, Protocol):
    """Port: the composite diversity scorer with a structured breakdown.

    Refines `IScorer` by also returning the per-component report. The
    concrete `DiversityEvaluator` (Composite of lexical/semantic/category)
    will satisfy this. Splitting it out keeps the single-float contract
    minimal for callers that don't care about the breakdown.
    """

    def evaluate(self, pages: Iterable[Page]) -> DiversityReport:
        ...

@runtime_checkable
class InterfaceFinalScorer(Protocol):
    def score(self, wikirank_score: float, diversity_score: float) -> float:
        ...
