"""Mock evidence bundle exporter. Writes plain text with .pdf extension for portability."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.utils.logger import get_logger

logger = get_logger(__name__)


def export_evidence(report: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = ["Training Data Integrity Engine Evidence Bundle", ""]
    for key, value in report.items():
        content.append(f"{key}: {value}")
    path.write_text("\n".join(content))
    logger.info("Evidence bundle written to %s", path)
    return path
