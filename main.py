"""Composition root — the ONLY file that knows concrete implementations.

Every other module depends on abstractions (interfaces / Protocols).
This file wires concretes together and injects them into the agent.

To swap a component, change ONE line here:
  - RandomPolicy → GreedyDiversityPolicy
  - SentenceEmbedder → DummyEmbedder
  - WikiPediaAPIRepository → FakeRepository (for tests)
"""

import logging
import pandas as pd

from config import default_config
from src.utils.logger import setup_logging

from src.retrieval.retriever import WikiPediaAPIRepository
from src.retrieval.decorators import RetrievalGuardDecorator

from src.processing.sentence_embedder import SentenceEmbedder

from src.evaluation.diversity_score import DiversityEvaluator
from src.evaluation.wikirank_score import WikiRankScorer
from src.evaluation.final_score import FinalMeanScorer

from src.decision.policies.random_policy import MinLengthPolicy
from src.decision.collection_agent import make_agent

from src.persisting.persistence import (
    enrich_pages,
    compute_scores,
    save_dataset_pkl,
    save_submission_csv,
)

logger = logging.getLogger(__name__)


def main() -> None:
    # ── logging ────────────────────────────────────────────────────────
    setup_logging(
        level="INFO",
        log_file=default_config.paths.root / "logs" / "run.log",
    )

    logger.info("=" * 70)
    logger.info("STARTING COLLECTION")
    logger.info("=" * 70 + "\n")

    # ── 1. Build the retrieval layer ─────────────────────────────────
    # Adapter: translates wikipediaapi → our InterfacePageRepository
    repo = WikiPediaAPIRepository()
    # Decorator: wraps the adapter with budget + legality enforcement
    guarded_repo = RetrievalGuardDecorator(
        inner=repo,
        wikirank_dataset_path=default_config.paths.en_tsv_file_path,
        request_limit=default_config.wiki_api_conf.page_request_limit,
    )
    logger.info("Repository ready (guarded).\n")

    # ── 2. Build the processing layer ──────────────────────────────────
    embedder = SentenceEmbedder()
    logger.info("Embedder ready.\n")

    # ── 3. Build the decision layer ───────────────────────────────────
    policy = MinLengthPolicy(min_char=default_config.page_config.min_char)
    agent = make_agent(
        repo=guarded_repo,
        policy=policy,
        dev_mode=default_config.agent_conf.dev_mode,
    )
    logger.info("Agent ready (dev_mode=%s).\n", default_config.agent_conf.dev_mode)

    # ── 4. Collect pages ────────────────────────────────────────────
    result = agent.collect_dataset()
    logger.info("Collected %d pages in %.1f minutes.\n",
                len(result.pages), result.elapsed_seconds / 60)

    if not result.pages:
        logger.warning("No pages collected. Nothing to score or save.")
        return

    # ── 5. Enrich pages with embeddings ───────────────────────────────
    enriched_pages = enrich_pages(result.pages, embedder)

    # ── 6. Score the dataset ────────────────────────────────────────
    ground_truth = pd.read_csv(default_config.paths.en_tsv_file_path, sep="\t")

    diversity_eval = DiversityEvaluator()
    wikirank_eval = WikiRankScorer(ground_truth)
    final_eval = FinalMeanScorer()

    scores, report = compute_scores(enriched_pages, diversity_eval, wikirank_eval, final_eval)

    logger.info("SCORES:")
    logger.info("  Dataset size:    %d", scores.dataset_size)
    logger.info("  WikiRank:        %.4f", scores.wikirank)
    logger.info("  Diversity:       %.4f", scores.diversity)
    logger.info("    Lexical:       %.4f", report.lexical)
    logger.info("    Semantic:      %.4f", report.semantic)
    logger.info("    Category:      %.4f", report.category)
    logger.info("  Final:           %.4f", scores.final)

    # ── 7. Persist ────────────────────────────────────────────────────
    save_dataset_pkl(enriched_pages, default_config.paths.pkl_file_path)
    save_submission_csv(scores, default_config.paths.scores_csv_file_path)

    logger.info("\n" + "=" * 70)
    logger.info("SUCCESS!")
    logger.info("=" * 70)
    logger.info("Output files:")
    logger.info("  1. %s  <- Kaggle", default_config.paths.scores_csv_file_path)
    logger.info("  2. %s  <- Moodle", default_config.paths.pkl_file_path)
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
