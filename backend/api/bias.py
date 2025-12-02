"""Bias detection endpoint."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from backend.engines.bias_engine import run_bias_checks
from backend.utils.data_loader import load_dataset

router = APIRouter()


@router.post("/bias_check")
def bias_check(payload: dict[str, Any]) -> dict[str, Any]:
    """Run fairness integrity checks on the dataset."""

    try:
        _, records = load_dataset(payload)
    except Exception as exc:  # broad for validation errors
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return run_bias_checks(records)
