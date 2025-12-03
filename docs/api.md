# API Reference (FastAPI)

- `POST /validate_dataset` — Validate against schema + quality checks. Returns `quality_score`, `violations`, `schema_violations`.
- `POST /fingerprint` — Compute dataset + per-feature hashes and tamper status.
- `POST /poison_detect` — Run simulated poisoning heuristics and return `poisoning_risk_score`.
- `POST /bias_check` — Compute fairness metrics and `bias_integrity_score`.
- `POST /tdie_score` — Full orchestration returning TDIE score, severity, decision, and provenance.
- `POST /train_if_clean` — Guardrail-enforced training decision; blocks when TDIE score is low.
- `GET /logs` — Retrieve recent log lines.
- `GET /health` — Health probe.
