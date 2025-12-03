"""Poison detection endpoint."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from backend.engines.poison_detector import compute_poisoning_risk
from backend.utils.data_loader import load_dataset

router = APIRouter()


@router.post("/poison_detect")
def poison_detect(payload: dict[str, Any]) -> dict[str, Any]:
    """Simulate poisoning detection heuristics for the provided dataset."""

    try:
        _, records = load_dataset(payload)
    except Exception as exc:  # broad for validation errors
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return compute_poisoning_risk(records)
