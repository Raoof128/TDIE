"""TDIE score endpoint orchestrating checks."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from backend.engines.bias_engine import run_bias_checks
from backend.engines.poison_detector import compute_poisoning_risk
from backend.engines.provenance import provenance_completeness, record_provenance
from backend.engines.quality_checker import generate_quality_report
from backend.engines.schema_validator import SchemaValidator
from backend.engines.tdie_scorer import compute_tdie_score
from backend.utils.data_loader import load_dataset

router = APIRouter()


@router.post("/tdie_score")
def tdie_score(payload: dict[str, Any]) -> dict[str, Any]:
    """Run the full TDIE stack and return a consolidated integrity report."""

    try:
        schema, records = load_dataset(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not records:
        raise HTTPException(status_code=400, detail="No records supplied for scoring")

    validator = SchemaValidator(schema)
    schema_violations = validator.validate(records)
    quality_report = generate_quality_report(records, records)
    bias_report = run_bias_checks(records)
    poison_report = compute_poisoning_risk(records)
    provenance_entry = record_provenance(
        source=payload.get("source", "synthetic"),
        user=payload.get("user", "system"),
        transformation_steps=payload.get("transformation_steps", []),
        metadata={"schema_version": schema.version, "schema_name": schema.name},
    )
    provenance_score = provenance_completeness(
        {
            "schema_version": schema.version,
            "schema_name": schema.name,
            "source": payload.get("source"),
            "user": payload.get("user"),
            "transformation_steps": payload.get("transformation_steps", []),
        }
    )

    combined = compute_tdie_score(
        quality_score=quality_report.score,
        poisoning_risk=poison_report["poisoning_risk_score"],
        bias_score=bias_report["bias_integrity_score"],
        schema_violations=schema_violations,
        provenance_completeness=provenance_score,
    )

    return {
        **quality_report.to_dict(),
        "schema_violations": [v.dict() for v in schema_violations],
        **poison_report,
        **bias_report,
        "provenance": provenance_entry,
        "provenance_completeness": provenance_score,
        **combined,
    }
