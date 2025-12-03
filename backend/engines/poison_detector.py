"""Simulated poisoning detection heuristics."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.cluster import KMeans

from backend.utils.logger import get_logger

logger = get_logger(__name__)


def _vectorise(records: list[dict[str, Any]], numeric_fields: list[str]) -> np.ndarray:
    if not numeric_fields:
        return np.zeros((len(records), 1))
    matrix = []
    for record in records:
        row = [float(record.get(field, 0.0)) for field in numeric_fields]
        matrix.append(row)
    return np.array(matrix)


def detect_label_flips(records: list[dict[str, Any]], label_field: str = "label") -> list[int]:
    flips: list[int] = []
    for idx, record in enumerate(records):
        if (
            label_field in record
            and isinstance(record[label_field], str)
            and record[label_field].startswith("flipped")
        ):
            flips.append(idx)
    return flips


def detect_cluster_anomalies(records: list[dict[str, Any]], numeric_fields: list[str]) -> list[int]:
    matrix = _vectorise(records, numeric_fields)
    if len(records) < 3 or matrix.shape[1] == 0:
        return []
    n_clusters = min(3, len(records))
    kmeans = KMeans(n_clusters=n_clusters, n_init=5, random_state=42)
    labels = kmeans.fit_predict(matrix)
    counts = {label: list(labels).count(label) for label in set(labels)}
    minority = [idx for idx, lbl in enumerate(labels) if counts[lbl] == min(counts.values())]
    return minority


def detect_embedding_drift(
    records: list[dict[str, Any]], baseline_embeddings: np.ndarray, numeric_fields: list[str]
) -> float:
    if not len(records):
        return 0.0
    current = _vectorise(records, numeric_fields)
    if current.size == 0:
        return 0.0
    baseline_mean = baseline_embeddings.mean(axis=0)
    current_mean = current.mean(axis=0)
    drift = float(np.linalg.norm(current_mean - baseline_mean[: current_mean.shape[0]]))
    return drift


def detect_bias_injection(
    records: list[dict[str, Any]], sensitive_field: str = "group"
) -> list[int]:
    pattern_indices: list[int] = []
    for idx, record in enumerate(records):
        if sensitive_field in record and str(record[sensitive_field]).lower() == "rare_group":
            pattern_indices.append(idx)
    return pattern_indices


def compute_poisoning_risk(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        logger.warning("Poison detection requested on empty record set")
        return {
            "poisoning_risk_score": 0.0,
            "suspected_poison_samples": [],
            "signals": {
                "label_flips": [],
                "cluster_outliers": [],
                "embedding_drift": 0.0,
                "bias_injection": [],
                "rare_pattern": [],
            },
            "anomaly_visualization": "simulated",
        }

    numeric_fields = [k for k, v in records[0].items() if isinstance(v, (int | float))]
    label_flips = detect_label_flips(records)
    cluster_outliers = detect_cluster_anomalies(records, numeric_fields)
    baseline_embeddings = np.random.normal(0, 0.5, size=(10, max(len(numeric_fields), 1)))
    drift = detect_embedding_drift(records, baseline_embeddings, numeric_fields)
    bias_injection = detect_bias_injection(records)

    rare_pattern_scanner = [
        idx
        for idx, r in enumerate(records)
        if any(str(v).startswith("trigger") for v in r.values())
    ]
    poison_hits = set(label_flips + cluster_outliers + bias_injection + rare_pattern_scanner)

    risk_score = min(100, 10 * len(poison_hits) + drift)
    logger.info("Poisoning risk computed at %.2f", risk_score)
    return {
        "poisoning_risk_score": round(risk_score, 2),
        "suspected_poison_samples": sorted(poison_hits),
        "signals": {
            "label_flips": label_flips,
            "cluster_outliers": cluster_outliers,
            "embedding_drift": drift,
            "bias_injection": bias_injection,
            "rare_pattern": rare_pattern_scanner,
        },
        "anomaly_visualization": "simulated",
    }
