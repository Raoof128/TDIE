"""Centralized logging utilities for TDIE."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "tdie.log"


class LoggerFactory:
    """Factory for application-wide loggers with sane defaults."""

    @staticmethod
    def create_logger(name: str = "tdie", level: int = logging.INFO) -> logging.Logger:
        """Return a configured logger that writes to file and console."""
        logger = logging.getLogger(name)
        logger.setLevel(level)

        if not logger.handlers:
            formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")

            file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
            file_handler.setFormatter(formatter)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            logger.addHandler(stream_handler)
        return logger


def get_logger(name: str = "tdie") -> logging.Logger:
    """Expose a helper to retrieve the shared logger."""
    return LoggerFactory.create_logger(name)
