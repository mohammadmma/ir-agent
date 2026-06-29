from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Iterable
from config import default_config


@dataclass(frozen=True)
class Page:
    """A Wikipedia page — the shared value object passed across every layer."""

    title: str
    content: str
    url: str
    links: tuple[str, ...] = field(default_factory=tuple)
    categories: tuple[str, ...] = field(default_factory=tuple)
    embedding: Any = None

    # ── domain predicates ──────────────────────────────────────────────
    def has_min_content(self, min_chars: int = default_config.page_config.min_char) -> bool:
        """True if the page body is long enough to be worth keeping."""
        return len(self.content) >= min_chars

    # ── enriching ──────────────────────────────────────────────────────
    def with_embedding(self, embedding: Any) -> "Page":
        """Return a copy of this page with the embedding attached."""
        return replace(self, embedding=embedding)

    # # ── interop ────────────────────────────────────────────────────────
    # # Bridge from the legacy dict shape that today's WikipediaAPI produces,
    # # so layers can migrate to `Page` one at a time without a big-bang.

    # @classmethod
    # def from_raw(cls, raw: dict) -> "Page":
    #     """Build a `Page` from a legacy `page_info` dict.

    #     Accepts both the v2 shape (links/categories as lists of strings) and
    #     tolerates missing keys by falling back to safe defaults.
    #     """
    #     return cls(
    #         title=raw["title"],
    #         content=raw.get("content", ""),
    #         url=raw.get("url", ""),
    #         links=tuple(raw.get("links", ()) or ()),
    #         categories=tuple(raw.get("categories", ()) or ()),
    #         embedding=raw.get("embeddings", None),
    #     )

    # @classmethod
    # def from_raw_iter(cls, raws: Iterable[dict]) -> list["Page"]:
    #     """Convenience: build a list of `Page` from an iterable of legacy dicts."""
    #     return [cls.from_raw(r) for r in raws]
