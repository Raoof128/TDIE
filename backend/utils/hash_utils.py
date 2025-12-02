"""Hash utilities for dataset fingerprinting."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def _stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, default=str)


def hash_record(record: dict[str, Any]) -> str:
    """Return SHA-256 hash for a single record."""
    stable = _stable_json(record).encode("utf-8")
    return hashlib.sha256(stable).hexdigest()


def hash_dataset(records: Iterable[dict[str, Any]]) -> str:
    """Return SHA-256 hash for an entire dataset."""
    aggregate = _stable_json(list(records)).encode("utf-8")
    return hashlib.sha256(aggregate).hexdigest()


def hash_features(records: Iterable[dict[str, Any]]) -> dict[str, str]:
    """Compute per-feature hashes based on column-wise values."""
    feature_values: dict[str, list[Any]] = {}
    for record in records:
        for key, value in record.items():
            feature_values.setdefault(key, []).append(value)

    return {
        key: hashlib.sha256(_stable_json(values).encode("utf-8")).hexdigest()
        for key, values in feature_values.items()
    }


def persist_hash(path: Path, data: dict[str, Any]) -> None:
    """Persist hash metadata to disk, appending to a JSON log."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(path.read_text()) if path.exists() else []
    existing.append(data)
    path.write_text(json.dumps(existing, indent=2))
