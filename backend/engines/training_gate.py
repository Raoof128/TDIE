"""Training guardrail logic to block or allow training runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.utils.logger import get_logger

logger = get_logger(__name__)
AUDIT_LOG = Path("logs/training_audit.log")


class GuardrailLevel:
    STRICT = "STRICT"
    MODERATE = "MODERATE"
    PERMISSIVE = "PERMISSIVE"


def training_gate(
    tdie_score: float, level: str = GuardrailLevel.STRICT, threshold: float = 60.0
) -> dict[str, Any]:
    """Decide whether to pass, review, or block training based on guardrail level."""

    safe_score = max(0.0, tdie_score)
    safe_threshold = max(0.0, threshold)
    decision = "BLOCK"
    reason = ""
    if level == GuardrailLevel.PERMISSIVE:
        decision = "PASS"
        reason = "Permissive mode logs only"
    elif level == GuardrailLevel.MODERATE:
        decision = "REVIEW" if safe_score < safe_threshold else "PASS"
        reason = "Moderate guardrail requires approval on low scores"
    else:
        decision = "BLOCK" if safe_score < safe_threshold else "PASS"
        reason = "Strict mode blocks scores below threshold"

    _audit({"tdie_score": safe_score, "level": level, "decision": decision, "reason": reason})
    return {"training_decision": decision, "guardrail_level": level, "reason": reason}


def _audit(entry: dict[str, Any]) -> None:
    """Persist a minimal audit log for training decisions."""

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        with AUDIT_LOG.open("a", encoding="utf-8") as f:
            f.write(str(entry) + "\n")
    except OSError as exc:
        logger.error("Failed to write training audit entry: %s", exc)
        return
    logger.info("Training audit entry: %s", entry)
