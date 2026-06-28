from dataclasses import dataclass, field
from pathlib import Path


# ── paths ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PathConfig:
    root: Path = field(default_factory=lambda: Path(__file__).parent)

    @property
    def en_tsv_file_path(self) -> Path:
        return self.root / "dataset" / "en.tsv"

    @property
    def pkl_file_path(self) -> Path:
        return self.root / "result" / "wikipedia_dataset.pkl"

    @property
    def scores_csv_file_path(self) -> Path:
        return self.root / "result" / "submission.csv"


# ── page quality ─────────────────────────────────────────────────────

@dataclass(frozen=True)
class PageConfig:
    min_char: int = 1000


# ── agent budgets & targets ──────────────────────────────────────────
# All the numbers that were hardcoded in the old `FastWikipediaAgent`.
# Dev-mode values are proportional to ~1% of production.

@dataclass(frozen=True)
class AgentConfig:
    target_pages: int = 5000
    dev_mode: bool = False

    # Phase 1: how many search requests to spend discovering candidates
    budget_phase1: int = 2500
    # Phase 2/3: hard ceiling on total requests before stopping fetches
    budget_limit: int = 6400

    # Dev-mode overrides
    dev_target_pages: int = 50
    dev_budget_phase1: int = 30
    dev_budget_limit: int = 150
    dev_min_char: int = 100

    # Max candidates to collect in phase 1 before moving on
    max_candidate_pool: int = 10_000

    # Logging interval for phase 2 progress
    log_interval: int = 250


# ── retrieval ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class WikiAPIConfig:
    page_request_limit: int = 6500
    max_search_result: int = 10


# ── scoring weights ──────────────────────────────────────────────────

@dataclass(frozen=True)
class ScoringConfig:
    lexical_weight: float = 0.3
    semantic_weight: float = 0.4
    category_weight: float = 0.3


# ── project root ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class ProjectConfig:
    paths: PathConfig = field(default_factory=PathConfig)
    page_config: PageConfig = field(default_factory=PageConfig)
    agent_conf: AgentConfig = field(default_factory=AgentConfig)
    wiki_api_conf: WikiAPIConfig = field(default_factory=WikiAPIConfig)
    scoring_conf: ScoringConfig = field(default_factory=ScoringConfig)


default_config = ProjectConfig()
