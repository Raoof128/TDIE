"""Data quality checks covering nulls, outliers, duplicates, and drift."""

from __future__ import annotations

import math
import statistics
from collections import Counter
from datetime import datetime
from typing import Any

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class QualityReport:
    """Represents quality metrics and derived score."""

    def __init__(self, score: float, violations: list[str], recommendations: list[str]):
        self.score = score
        self.violations = violations
        self.recommendations = recommendations

    def to_dict(self) -> dict[str, Any]:
        return {
            "quality_score": round(self.score, 2),
            "violations": self.violations,
            "recommended_fixes": self.recommendations,
        }


def detect_missing(records: list[dict[str, Any]]) -> tuple[int, list[str]]:
    missing = 0
    violations: list[str] = []
    for idx, record in enumerate(records):
        for key, value in record.items():
            if value in (None, "", [], {}):
                missing += 1
                violations.append(f"Record {idx} missing value in {key}")
    return missing, violations


def detect_duplicates(records: list[dict[str, Any]]) -> tuple[int, list[str]]:
    serialised = [tuple(sorted(item.items())) for item in records]
    counts = Counter(serialised)
    duplicates = [rec for rec, count in counts.items() if count > 1]
    if not duplicates:
        return 0, []
    return len(duplicates), ["Duplicate records detected"]


def detect_outliers(records: list[dict[str, Any]], numeric_fields: list[str]) -> list[str]:
    issues: list[str] = []
    for field in numeric_fields:
        values = [
            float(r[field]) for r in records if field in r and isinstance(r[field], (int | float))
        ]
        if len(values) < 4:
            continue
        q1, q3 = percentile(values, 25), percentile(values, 75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        for idx, val in enumerate(values):
            if val < lower or val > upper:
                issues.append(f"Outlier in {field} value {val} at position {idx}")
    return issues


def percentile(data: list[float], percentile_value: float) -> float:
    if not data:
        return 0.0
    k = (len(data) - 1) * (percentile_value / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted(data)[int(k)]
    d0 = sorted(data)[int(f)] * (c - k)
    d1 = sorted(data)[int(c)] * (k - f)
    return d0 + d1


def detect_timestamp_anomalies(
    records: list[dict[str, Any]], timestamp_fields: list[str]
) -> list[str]:
    anomalies: list[str] = []
    for field in timestamp_fields:
        timestamps: list[datetime] = []
        for record in records:
            if field not in record:
                continue
            try:
                timestamps.append(datetime.fromisoformat(str(record[field])))
            except ValueError:
                anomalies.append(f"Invalid timestamp format in field {field}")
        if timestamps:
            sorted_ts = sorted(timestamps)
            for i in range(1, len(sorted_ts)):
                if (sorted_ts[i] - sorted_ts[i - 1]).total_seconds() < 0:
                    anomalies.append(f"Timestamp order anomaly in field {field}")
    return anomalies


def detect_distribution_drift(
    records: list[dict[str, Any]], baseline: list[dict[str, Any]], fields: list[str]
) -> list[str]:
    drift_messages: list[str] = []
    for field in fields:
        current_values = [r.get(field) for r in records if field in r]
        base_values = [r.get(field) for r in baseline if field in r]
        if not current_values or not base_values:
            continue
        current_mean = statistics.mean(
            [float(v) for v in current_values if isinstance(v, (int | float))]
        )
        base_mean = statistics.mean([float(v) for v in base_values if isinstance(v, (int | float))])
        if base_mean == 0:
            continue
        shift = abs(current_mean - base_mean) / abs(base_mean)
        if shift > 0.3:
            drift_messages.append(
                f"Distribution drift detected in {field}: {shift:.2f} relative change"
            )
    return drift_messages


def generate_quality_report(
    records: list[dict[str, Any]], baseline: list[dict[str, Any]]
) -> QualityReport:
    if not records:
        logger.warning("Quality report requested for empty record set")
        return QualityReport(
            score=0.0,
            violations=["No records supplied"],
            recommendations=["Provide at least one record to assess quality"],
        )

    violations: list[str] = []
    recommendations: list[str] = []
    missing, missing_messages = detect_missing(records)
    violations.extend(missing_messages)

    duplicate_count, duplicate_messages = detect_duplicates(records)
    violations.extend(duplicate_messages)

    numeric_fields = [key for key, value in records[0].items() if isinstance(value, (int | float))]
    outlier_messages = detect_outliers(records, numeric_fields)
    violations.extend(outlier_messages)

    timestamp_fields = [key for key in records[0] if "time" in key or "date" in key]
    timestamp_messages = detect_timestamp_anomalies(records, timestamp_fields)
    violations.extend(timestamp_messages)

    drift_messages = detect_distribution_drift(records, baseline, numeric_fields)
    violations.extend(drift_messages)

    if missing:
        recommendations.append("Fill missing values or remove affected records")
    if duplicate_count:
        recommendations.append("Deduplicate dataset before training")
    if outlier_messages:
        recommendations.append("Winsorize or investigate outliers")
    if drift_messages:
        recommendations.append("Recompute baseline or retrain model with new distribution")

    penalty = min(len(violations) * 2 + missing + duplicate_count * 5, 100)
    score = max(100 - penalty, 0)
    logger.info("Quality score computed at %.2f", score)
    return QualityReport(score=score, violations=violations, recommendations=recommendations)
