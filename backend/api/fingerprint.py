"""Fingerprint endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from backend.engines.fingerprint_engine import detect_tampering, fingerprint_dataset
from backend.utils.data_loader import load_dataset
from backend.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/fingerprint")
def fingerprint(payload: dict[str, Any]) -> dict[str, Any]:
    """Return dataset and per-feature hashes with tamper detection."""

    try:
        schema, records = load_dataset(payload)
    except Exception as exc:  # broad for validation errors
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    metadata = {
        "schema_name": schema.name,
        "schema_version": schema.version,
        "record_count": len(records),
    }
    fingerprint_result = fingerprint_dataset(records, metadata)
    fingerprint_result["tamper_detected"] = detect_tampering(fingerprint_result["dataset_hash"])
    return fingerprint_result
