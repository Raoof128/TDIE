# TDIE Lab Manual

1. Start API: `uvicorn backend.main:app --reload`.
2. POST example payload (see README) to `/tdie_score` to generate scores and provenance.
3. Review `logs/tdie.log`, `provenance/*.json`, and `logs/evidence_bundle.pdf`.
4. Use `/train_if_clean` with the TDIE score to test guardrail behavior at STRICT, MODERATE, and PERMISSIVE levels.
5. Open `frontend/index.html` in a browser to view dashboard data.
