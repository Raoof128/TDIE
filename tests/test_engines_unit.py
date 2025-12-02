from __future__ import annotations

import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from backend.engines.schema_validator import DatasetSchema, FieldSchema, SchemaValidator
from backend.engines.tdie_scorer import compute_tdie_score
from backend.engines.training_gate import GuardrailLevel, training_gate


def test_schema_validator_detects_missing_required_field() -> None:
    schema = DatasetSchema(
        name="demo", version="1.0", fields=[FieldSchema(name="id", dtype="int", required=True)]
    )
    records = [{"value": 1}]

    violations = SchemaValidator(schema).validate(records)

    assert len(violations) == 1
    assert violations[0].field == "id"


def test_tdie_score_returns_expected_severity_and_decision() -> None:
    score = compute_tdie_score(
        quality_score=90,
        poisoning_risk=5,
        bias_score=85,
        schema_violations=[],
        provenance_completeness=95,
    )

    assert score["severity"] == "Low"
    assert score["decision"] == "PASS"
    assert 0 <= score["tdie_score"] <= 100


def test_training_gate_respects_guardrail_levels() -> None:
    strict = training_gate(tdie_score=50, level=GuardrailLevel.STRICT)
    moderate = training_gate(tdie_score=50, level=GuardrailLevel.MODERATE)
    permissive = training_gate(tdie_score=10, level=GuardrailLevel.PERMISSIVE)

    assert strict["training_decision"] == "BLOCK"
    assert moderate["training_decision"] == "REVIEW"
    assert permissive["training_decision"] == "PASS"
