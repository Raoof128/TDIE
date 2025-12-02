"""Bias and fairness integrity checks using synthetic-safe heuristics."""

from __future__ import annotations

from typing import Any

import numpy as np

from backend.utils.logger import get_logger

logger = get_logger(__name__)


def _group_metrics(
    records: list[dict[str, Any]], label_field: str, sensitive_field: str
) -> dict[str, dict[str, float]]:
    """Aggregate per-group label counts and rates for fairness calculations."""

    group_counts: dict[str, dict[str, float]] = {}
    for record in records:
        group = str(record.get(sensitive_field, "unknown"))
        label = record.get(label_field)
        counts = group_counts.setdefault(group, {"positives": 0, "total": 0})
        counts["total"] += 1
        if label == 1:
            counts["positives"] += 1
    for _group, counts in group_counts.items():
        counts["rate"] = counts["positives"] / counts["total"] if counts["total"] else 0
    return group_counts


def demographic_parity(
    records: list[dict[str, Any]], label_field: str, sensitive_field: str
) -> float:
    """Compute demographic parity gap as max-min positive prediction rate across groups."""

    metrics = _group_metrics(records, label_field, sensitive_field)
    rates = [group_data["rate"] for group_data in metrics.values() if group_data["total"] > 0]
    if not rates:
        return 0.0
    return float(max(rates) - min(rates))


def equal_opportunity(
    records: list[dict[str, Any]], label_field: str, sensitive_field: str
) -> float:
    """Calculate equal opportunity gap across groups using observed positive rates."""

    metrics = _group_metrics(records, label_field, sensitive_field)
    rates = [
        group_data["positives"] / group_data["total"]
        for group_data in metrics.values()
        if group_data["total"] > 0
    ]
    if not rates:
        return 0.0
    return float(max(rates) - min(rates))


def pooled_fairness_index(
    records: list[dict[str, Any]], label_field: str, sensitive_field: str
) -> float:
    """Return pooled fairness index (standard deviation of group positive rates)."""

    metrics = _group_metrics(records, label_field, sensitive_field)
    rates = [group_data["rate"] for group_data in metrics.values() if group_data["total"] > 0]
    if not rates:
        return 0.0
    return float(np.std(rates))


def run_bias_checks(
    records: list[dict[str, Any]],
    sensitive_field: str = "group",
    label_field: str = "label",
) -> dict[str, Any]:
    """Compute fairness metrics and aggregate into a bias integrity score."""

    if not records:
        logger.warning("Bias checks requested on empty record set")
        return {
            "demographic_parity_gap": 0.0,
            "equal_opportunity_gap": 0.0,
            "pooled_fairness_index": 0.0,
            "sensitive_feature_imbalance": 0.0,
            "bias_integrity_score": 0.0,
        }

    dp_gap = demographic_parity(records, label_field, sensitive_field)
    eo_gap = equal_opportunity(records, label_field, sensitive_field)
    pfi = pooled_fairness_index(records, label_field, sensitive_field)
    imbalance = _imbalance(records, sensitive_field)

    bias_score = max(0.0, 100 - (dp_gap + eo_gap + pfi) * 50 - imbalance)
    logger.info("Bias integrity score at %.2f", bias_score)
    return {
        "demographic_parity_gap": round(dp_gap, 4),
        "equal_opportunity_gap": round(eo_gap, 4),
        "pooled_fairness_index": round(pfi, 4),
        "sensitive_feature_imbalance": imbalance,
        "bias_integrity_score": round(bias_score, 2),
    }


def _imbalance(records: list[dict[str, Any]], sensitive_field: str) -> float:
    """Measure sensitive feature imbalance as relative majority/minority difference."""

    counts: dict[str, int] = {}
    for record in records:
        group = str(record.get(sensitive_field, "unknown"))
        counts[group] = counts.get(group, 0) + 1
    if not counts:
        return 0.0
    majority = max(counts.values())
    minority = min(counts.values())
    if majority == 0:
        return 0.0
    return round((majority - minority) / majority * 100, 2)
