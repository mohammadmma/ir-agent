from __future__ import annotations

from typing import Iterable, Protocol, runtime_checkable

from src.domain.page import Page


@runtime_checkable
class InterfaceEmbedder(Protocol):
    """Port: turn page text into vector embeddings.

    This is the processing layer's only contract. Keeping it separate means
    the retrieval layer never imports an embedding model (clean-architecture
    rule: "no embedding logic inside the crawler"), and the evaluation /
    decision layers depend on this abstraction rather than on
    `sentence-transformers` directly.

    Implementations are free to be model-backed (`SentenceEmbedder`) or
    deterministic fakes (`DummyEmbedder`) for fast, offline tests.
    """

    def embed(self, page: Page) -> Page:
        """Return a new `Page` with its embedding attached.

        The input page is not mutated — enrichment produces a new value
        (see `Page.with_embedding`).
        """
        ...

    def embed_batch(self, pages: Iterable[Page]) -> list[Page]:
        """Embed many pages, returning new `Page` objects with embeddings set.

        Implementations may vectorise this; callers should not assume the
        input order is preserved unless documented by the implementation.
        """
        ...
