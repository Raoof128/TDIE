"""TDIE scoring logic that combines quality, poisoning, schema, bias, and provenance signals."""

from __future__ import annotations

from typing import Any

from backend.engines.schema_validator import SchemaViolation
from backend.utils.logger import get_logger

logger = get_logger(__name__)


SEVERITY_MAP = {"ERROR": 30, "WARN": 10, "INFO": 0}


def compute_tdie_score(
    quality_score: float,
    poisoning_risk: float,
    bias_score: float,
    schema_violations: list[SchemaViolation],
    provenance_completeness: float,
) -> dict[str, Any]:
    """Aggregate integrity signals and return TDIE score metadata."""

    schema_penalty = sum(SEVERITY_MAP.get(v.severity, 5) for v in schema_violations)
    base = quality_score + bias_score + provenance_completeness
    risk_penalty = poisoning_risk
    raw_score = max(0.0, (base / 3) - risk_penalty - schema_penalty)
    capped_score = min(100.0, raw_score)
    severity = severity_tier(capped_score)
    decision = decision_gate(capped_score, len(schema_violations))
    logger.info("TDIE score %.2f with severity %s", capped_score, severity)
    return {
        "tdie_score": round(capped_score, 2),
        "severity": severity,
        "decision": decision,
    }


def severity_tier(score: float) -> str:
    """Map TDIE score to a severity tier."""

    if score >= 80:
        return "Low"
    if score >= 60:
        return "Medium"
    if score >= 40:
        return "High"
    return "Critical"


def decision_gate(score: float, schema_violations: int) -> str:
    """Return recommended action based on TDIE score and contract violations."""

    if score < 40 or schema_violations > 5:
        return "BLOCK"
    if score < 60:
        return "REVIEW"
    return "PASS"
