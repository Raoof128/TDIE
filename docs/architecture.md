# TDIE Architecture Overview

TDIE follows a clean separation between API routers, engines, utilities, and artifacts.

- **API layer** (`backend/api`): FastAPI routes for validation, fingerprinting, poisoning, bias, scoring, and training.
- **Engines** (`backend/engines`): Pure logic for schema validation, quality checks, poisoning detection, bias checks, scoring, provenance, and guardrails.
- **Utilities** (`backend/utils`): Logging, hashing, evidence export, and payload parsing.
- **Artifacts** (`provenance`, `logs`, `data`): Persisted state for checksums, lineage, and baselines.

## Data Flow
1. Client posts dataset payload to `/tdie_score`.
2. Schema + quality checks run, producing violations and quality score.
3. Poisoning and bias heuristics execute on numeric and sensitive features.
4. Provenance entry recorded and completeness measured.
5. TDIE score combines signals into severity + decision.
6. Fingerprints and logs are written for auditability.

## Security & Privacy
- Only synthetic/anonymised data accepted by design; payload validation enforces expected schema.
- No outbound network access; threat intel checks are simulated.
- Logs avoid sensitive content and are rotated.
