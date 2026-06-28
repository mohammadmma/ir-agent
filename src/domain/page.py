from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Iterable
from config import default_config


@dataclass(frozen=True)
class Page:
    """A Wikipedia page — the shared value object passed across every layer.

    Single responsibility: *represent* a fetched Wikipedia page. It knows
    nothing about HTTP, budgets, embeddings computation, or scoring. Those
    concerns live in the retrieval / processing / evaluation layers, which
    produce, enrich, and consume `Page` instances.

    `frozen=True` gives value-object semantics: a `Page` is safe to share
    across layers without defensive copies. The embedding is modelled as an
    optional, separately-set field because a freshly fetched page has no
    embedding — that enrichment is the processing layer's job.
    """

    title: str
    content: str
    url: str
    links: tuple[str, ...] = field(default_factory=tuple)
    categories: tuple[str, ...] = field(default_factory=tuple)
    embedding: Any = None

    # ── domain predicates ──────────────────────────────────────────────
    # Quality rules that belong to the *page itself* (not to the crawler or
    # the agent). Keeping them here means callers express intent rather than
    # reimplementing string-length checks ("len(content) > min_content").

    def has_min_content(self, min_chars: int = default_config.page_config.min_char) -> bool:
        """True if the page body is long enough to be worth keeping."""
        return len(self.content) >= min_chars

    def link_set(self) -> frozenset[str]:
        """A hashable view of the outgoing links (useful for set ops / scoring)."""
        return frozenset(self.links)

    def category_set(self) -> frozenset[str]:
        """A hashable view of the categories (used by category-diversity scoring)."""
        return frozenset(self.categories)

    # ── enriching ──────────────────────────────────────────────────────
    # Producing a page *with* an embedding is a transformation that yields a
    # new immutable value, rather than mutating in place. This keeps the
    # fetched page and its enriched counterpart cleanly separable.

    def with_embedding(self, embedding: Any) -> "Page":
        """Return a copy of this page with the embedding attached."""
        return replace(self, embedding=embedding)

    # ── interop ────────────────────────────────────────────────────────
    # Bridge from the legacy dict shape that today's WikipediaAPI produces,
    # so layers can migrate to `Page` one at a time without a big-bang.

    @classmethod
    def from_raw(cls, raw: dict) -> "Page":
        """Build a `Page` from a legacy `page_info` dict.

        Accepts both the v2 shape (links/categories as lists of strings) and
        tolerates missing keys by falling back to safe defaults.
        """
        return cls(
            title=raw["title"],
            content=raw.get("content", ""),
            url=raw.get("url", ""),
            links=tuple(raw.get("links", ()) or ()),
            categories=tuple(raw.get("categories", ()) or ()),
            embedding=raw.get("embeddings", raw.get("embedding")),
        )

    @classmethod
    def from_raw_iter(cls, raws: Iterable[dict]) -> list["Page"]:
        """Convenience: build a list of `Page` from an iterable of legacy dicts."""
        return [cls.from_raw(r) for r in raws]
