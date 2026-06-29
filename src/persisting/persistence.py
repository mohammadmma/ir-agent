from __future__ import annotations

import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from src.domain.page import Page
from src.evaluation.interfaces import (
    DiversityReport,
    InterfaceDiversityEvaluator,
    InterfaceScorer,
    InterfaceFinalScorer,
)
from src.processing.interfaces import InterfaceEmbedder
from config import default_config

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SubmissionScore:
    dataset_size: int
    diversity: float
    wikirank: float
    final: float


def enrich_pages(
    pages: Iterable[Page],
    embedder: InterfaceEmbedder,
) -> list[Page]:
    """Attach embeddings to pages using the embedder."""
    logger.info("Enriching %d pages with embeddings...", len(list(pages)) if isinstance(pages, list) else "N")
    enriched = embedder.embed_batch(pages)
    logger.info("Embeddings complete.")
    return enriched


def compute_scores(
    pages: Iterable[Page],
    diversity_eval: InterfaceDiversityEvaluator,
    wikirank_eval: InterfaceScorer,
    final_eval: InterfaceFinalScorer
) -> tuple[SubmissionScore, DiversityReport]:
    """Score the collected pages and return both the submission score and
    the detailed diversity report.
    """
    pages_list = list(pages)

    diversity_report = diversity_eval.evaluate(pages_list)
    diversity_score = diversity_report.overall_score()

    wikirank_score = wikirank_eval.score(pages_list)

    final_score = final_eval.score(wikirank_score, diversity_score)

    scores = SubmissionScore(
        dataset_size=len(pages_list),
        diversity=diversity_score,
        wikirank=wikirank_score,
        final=final_score,
    )
    return scores, diversity_report


def save_dataset_pkl(pages: Iterable[Page], path: Path = default_config.paths.pkl_file_path) -> None:
    """Save the dataset as a pickle file.

    Pages are saved as a list of dicts (the format expected by the Moodle
    / Kaggle evaluation pipeline).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "title": p.title,
            "content": p.content,
            "url": p.url,
            "links": list(p.links),
            "categories": list(p.categories),
            "embeddings": p.embedding,
        }
        for p in pages
    ]
    with open(path, "wb") as f:
        pickle.dump(data, f)
    logger.info("Dataset saved: %s", path)


def save_submission_csv(scores: SubmissionScore, path: Path) -> None:
    """Save the competition scores as a CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    import pandas as pd

    df = pd.DataFrame([{
        "id": 0,
        "Dataset Size": scores.dataset_size,
        "WikiRank Score": scores.wikirank,
        "Diversity Score": scores.diversity,
        "Final Score": scores.final,
    }])
    df.to_csv(path, index=False)
    logger.info("Scores saved: %s", path)
