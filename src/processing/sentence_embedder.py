from __future__ import annotations

import logging
from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

from src.domain.page import Page
from src.processing.interfaces import InterfaceEmbedder

logger = logging.getLogger(__name__)


class SentenceEmbedder:
    """Concrete `InterfaceEmbedder` backed by a sentence-transformers model."""

    def __init__(self, model: SentenceTransformer | None = None) -> None:
        self._model = model or SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, page: Page) -> Page:
        """Return a new `Page` with its embedding attached."""
        return self.embed_batch([page])[0]

    def embed_batch(self, pages: Iterable[Page]) -> list[Page]:
        """Embed many pages, returning new `Page` objects with embeddings set.

        Input order IS preserved — this is important because downstream code
        (scorers, persistence) expects the embedding-to-page correspondence
        to match.
        """
        pages_list = list(pages)
        if not pages_list:
            return []

        # Extract content for batch encoding
        contents = [p.content for p in pages_list]
        embeddings = self._model.encode(contents, show_progress_bar=False)

        # Produce new enriched Pages (input pages are NOT mutated)
        enriched = []
        for page, vec in zip(pages_list, embeddings):
            enriched.append(page.with_embedding(vec))

        logger.info("Embedded %d pages", len(enriched))
        return enriched


# class DummyEmbedder:
#     """Fake `InterfaceEmbedder` that returns deterministic embeddings.

#     Returns a zero-filled numpy array of the given `dim` for every page.
#     Useful for:
#       * unit-testing the agent / scorers without downloading the real model
#       * CI pipelines where GPU / model weights are unavailable
#       * fast iteration during development

#     Also satisfies `InterfaceEmbedder` structurally (no base class needed).
#     """

#     def __init__(self, dim: int = 384) -> None:
#         self._dim = dim

#     def embed(self, page: Page) -> Page:
#         return self.embed_batch([page])[0]

#     def embed_batch(self, pages: Iterable[Page]) -> list[Page]:
#         pages_list = list(pages)
#         dummy_vec = np.zeros(self._dim, dtype=np.float32)
#         return [p.with_embedding(dummy_vec) for p in pages_list]
