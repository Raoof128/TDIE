"""Dataset validation endpoint."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.engines.quality_checker import generate_quality_report
from backend.engines.schema_validator import SchemaValidator
from backend.utils.data_loader import load_dataset
from backend.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
BASELINE_PATH = Path("data/baseline.json")


def _load_baseline() -> list[dict[str, Any]]:
    """Load the baseline dataset for drift comparisons if available."""

    if not BASELINE_PATH.exists():
        return []

    try:
        return json.loads(BASELINE_PATH.read_text())
    except json.JSONDecodeError as exc:
        logger.warning("Failed to parse baseline file: %s", exc)
        return []


@router.post("/validate_dataset")
def validate_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate schema compliance and generate data quality report."""

    try:
        schema, records = load_dataset(payload)
    except Exception as exc:  # broad for validation errors
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    validator = SchemaValidator(schema)
    violations = validator.validate(records)
    baseline = _load_baseline()
    quality_report = generate_quality_report(records, baseline)

    return {
        "schema_violations": [v.dict() for v in violations],
        **quality_report.to_dict(),
    }
