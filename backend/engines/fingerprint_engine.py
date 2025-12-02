"""Fingerprinting utilities for datasets."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.utils.hash_utils import hash_dataset, hash_features, persist_hash
from backend.utils.logger import get_logger

logger = get_logger(__name__)

CHECKSUM_HISTORY = Path("provenance/checksum_history.json")


def fingerprint_dataset(records: list[dict[str, Any]], metadata: dict[str, Any]) -> dict[str, Any]:
    """Compute dataset-level and feature-level fingerprints."""
    dataset_hash = hash_dataset(records)
    feature_hashes = hash_features(records)
    fingerprint = {
        "dataset_hash": dataset_hash,
        "feature_hashes": feature_hashes,
        "generated_at": datetime.now(UTC).isoformat(),
        "metadata": metadata,
    }
    persist_hash(CHECKSUM_HISTORY, fingerprint)
    logger.info("Fingerprint stored with hash %s", dataset_hash)
    return fingerprint


def detect_tampering(new_hash: str) -> bool:
    """Simple tamper detection by comparing latest stored hash."""
    if not CHECKSUM_HISTORY.exists():
        return False
    history_raw = CHECKSUM_HISTORY.read_text()
    if not history_raw.strip():
        return False
    entries = json.loads(history_raw)
    if not entries:
        return False
    last_hash = entries[-1]["dataset_hash"]
    return last_hash != new_hash
