from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol, runtime_checkable

from src.domain.page import Page



@dataclass(frozen=True)
class DiversityReport:
    """Structured result of a multi-component diversity evaluation."""

    lexical: float
    semantic: float
    category: float
    
    def overall_score(self, lexical_weight: float = 0.3, semantic_weight: float = 0.4, category_weight: float = 0.3) -> float:
        return (self.lexical * lexical_weight) + (self.semantic * semantic_weight) + (self.category * category_weight)


@runtime_checkable
class InterfaceScorer(Protocol):
    def score(self, pages: Iterable[Page]) -> float:
        ...

@runtime_checkable
class InterfaceDiversityEvaluator(Protocol):
    def evaluate(self, pages: Iterable[Page]) -> DiversityReport:
        ...

@runtime_checkable
class InterfaceFinalScorer(Protocol):
    def score(self, wikirank_score: float, diversity_score: float) -> float:
        ...
