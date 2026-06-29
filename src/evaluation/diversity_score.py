from __future__ import annotations

import logging
from itertools import combinations
from typing import Iterable

import nltk
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.domain.page import Page
from src.evaluation.interfaces import DiversityReport
from config import default_config

logger = logging.getLogger(__name__)

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)


# ── private sub-metrics ────────────────────────────────────────────────
def _lexical_diversity(pages: list[Page]) -> float:
    """Ratio of unique words to total words across all page contents.

    A high ratio means the dataset uses many distinct terms (good).
    A low ratio means heavy repetition (bad).
    """
    total_words = 0
    unique_words: set[str] = set()
    for page in pages:
        if not page.content.strip():
            continue
        tokens = nltk.word_tokenize(page.content)
        total_words += len(tokens)
        unique_words.update(word.lower() for word in tokens)
    return len(unique_words) / total_words if total_words > 0 else 0.0


def _semantic_diversity(pages: list[Page]) -> float:
    """Average pairwise cosine distance between page embeddings.

    Requires pages to have embeddings attached (via InterfaceEmbedder).
    Returns 0 if fewer than 2 pages have embeddings.
    A high value means pages are semantically dissimilar (good).
    """
    embeddings = [p.embedding for p in pages if p.embedding is not None]
    if len(embeddings) < 2:
        return 0.0
    matrix = np.vstack(embeddings)
    cosine_sim = cosine_similarity(matrix)
    # Upper triangle (excluding diagonal) = all unique pairs
    avg_sim = np.mean(cosine_sim[np.triu_indices_from(cosine_sim, k=1)])
    return float(1.0 - avg_sim)


def _category_diversity(pages: list[Page]) -> float:
    """1 minus the average Jaccard overlap of categories across all page pairs.

    A high value means pages cover different categories (good).
    A low value means categories heavily overlap (bad).
    """
    category_sets = [set(p.categories) for p in pages if p.categories]
    n = len(category_sets)
    if n < 2:
        return 0.0

    overlap_sum = 0.0
    pair_count = 0
    for cat1, cat2 in combinations(category_sets, 2):
        union = len(cat1 | cat2)
        if union:
            overlap_sum += len(cat1 & cat2) / union
        pair_count += 1

    return 1.0 - (overlap_sum / pair_count) if pair_count > 0 else 0.0


# ── composite evaluator ──────────────────────────────────────────────
class DiversityEvaluator:
    """Composite diversity scorer combining lexical, semantic, and category."""

    # def __init__(
    #     self,
    #     lexical_weight: float = default_config.scoring_conf.lexical_weight,
    #     semantic_weight: float = default_config.scoring_conf.semantic_weight,
    #     category_weight: float = default_config.scoring_conf.category_weight,
    # ) -> None:
    #     self._lexical_weight = lexical_weight
    #     self._semantic_weight = semantic_weight
    #     self._category_weight = category_weight

    def evaluate(self, pages: Iterable[Page]) -> DiversityReport:
        """Score all three diversity dimensions, return the structured report."""
        pages_list = list(pages)
        if not pages_list:
            return DiversityReport(lexical=0.0, semantic=0.0, category=0.0)

        try:
            lex = _lexical_diversity(pages_list)
        except Exception:
            logger.exception("Lexical diversity calculation failed")
            lex = 0.0

        try:
            sem = _semantic_diversity(pages_list)
        except Exception:
            logger.exception("Semantic diversity calculation failed")
            sem = 0.0

        try:
            cat = _category_diversity(pages_list)
        except Exception:
            logger.exception("Category diversity calculation failed")
            cat = 0.0

        return DiversityReport(lexical=lex, semantic=sem, category=cat)

    # def score(self, pages: Iterable[Page]) -> float:
    #     """Single-float convenience — satisfies `InterfaceScorer`."""
    #     report = self.evaluate(pages)
    #     return report.overall_score(
    #         lexical_weight=self._lexical_weight,
    #         semantic_weight=self._semantic_weight,
    #         category_weight=self._category_weight,
    #     )
