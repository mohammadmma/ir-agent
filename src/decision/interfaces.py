from __future__ import annotations

from typing import Protocol, runtime_checkable
from dataclasses import dataclass
from src.domain.page import Page


@dataclass(frozen=True)
class CollectionResult:
    pages: tuple[Page, ...]
    requests_used: int
    elapsed_seconds: float

@runtime_checkable
class InterfaceSelectionPolicy(Protocol):
    def should_keep(self, page: Page) -> bool:
        """Decide whether a fetched page is worth keeping."""
        ...

@runtime_checkable
class InterfaceAgent(Protocol):
    def collect_dataset(self) -> CollectionResult:
        ...
