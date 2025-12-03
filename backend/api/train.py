"""Training gate endpoint."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.engines.training_gate import GuardrailLevel, training_gate
from backend.utils.pdf_export import export_evidence

router = APIRouter()


@router.post("/train_if_clean")
def train_if_clean(payload: dict[str, Any]) -> dict[str, Any]:
    """Apply training guardrails and emit an evidence bundle."""

    tdie_score = float(payload.get("tdie_score", 0))
    guardrail = payload.get("guardrail_level", GuardrailLevel.STRICT)
    threshold = float(payload.get("threshold", 60))

    decision_payload = training_gate(tdie_score, level=guardrail, threshold=threshold)
    evidence_path = export_evidence(
        {"tdie_score": tdie_score, **decision_payload}, Path("logs/evidence_bundle.pdf")
    )
    decision_payload["evidence_path"] = str(evidence_path)
    if decision_payload["training_decision"] == "BLOCK":
        raise HTTPException(status_code=403, detail=decision_payload)
    return decision_payload
