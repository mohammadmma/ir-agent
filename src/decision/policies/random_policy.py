from __future__ import annotations

from config import default_config
from src.domain.page import Page


class MinLengthPolicy:
    def __init__(self, min_char: int = default_config.page_config.min_char) -> None:
        self._min_char = min_char

    def should_keep(self, page: Page) -> bool:
        """Accept any page with content above the minimum character threshold."""
        return page.has_min_content(self._min_char)
