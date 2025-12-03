"""Provenance capture and lineage management."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.utils.logger import get_logger

logger = get_logger(__name__)

PROVENANCE_LOG = Path("provenance/provenance_log.json")


def record_provenance(
    source: str,
    user: str,
    transformation_steps: list[str],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    entry = {
        "source": source,
        "user": user,
        "transformation_steps": transformation_steps,
        "timestamp": datetime.now(UTC).isoformat(),
        "metadata": metadata,
    }
    _append_entry(entry)
    logger.info("Provenance captured for source %s", source)
    return entry


def _append_entry(entry: dict[str, Any]) -> None:
    PROVENANCE_LOG.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(PROVENANCE_LOG.read_text()) if PROVENANCE_LOG.exists() else []
    existing.append(entry)
    PROVENANCE_LOG.write_text(json.dumps(existing, indent=2))


def provenance_completeness(metadata: dict[str, Any]) -> float:
    expected_keys = {"source", "user", "transformation_steps", "schema_version"}
    present = sum(1 for key in expected_keys if key in metadata and metadata[key])
    completeness = (present / len(expected_keys)) * 100
    return round(completeness, 2)
