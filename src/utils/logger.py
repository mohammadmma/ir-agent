import logging
import sys
from pathlib import Path


def setup_logging(
    level:    str        = "INFO",
    log_file: Path | None = None,
) -> None:
    """
    Configure root logger with console + optional file output.
    Call this ONCE before anything else runs.

    Args:
        level:    minimum level to show: DEBUG / INFO / WARNING / ERROR
        log_file: if provided, also write logs to this file
    """

    log_level = getattr(logging, level.upper(), logging.INFO)

    # format: timestamp | level | module name | message
    formatter = logging.Formatter(
        fmt   = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt = "%H:%M:%S",
    )

    # root logger — all module loggers propagate to this
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # avoid duplicate handlers if called twice (common in notebooks)
    if root_logger.handlers:
        root_logger.handlers.clear()

    # ── console handler ───────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # ── file handler (optional) ───────────────────────────────────
    if log_file is not None:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level) 
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    logging.getLogger(__name__).info(
        f"Logging configured | level: {level}"
        + (f" | file: {log_file}" if log_file else "")
    )