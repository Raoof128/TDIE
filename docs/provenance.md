# Provenance Model

Each dataset submission records:
- Source, user, and transformation steps
- Timestamp and schema metadata
- Dataset hash and per-feature hashes

Artifacts:
- `provenance/provenance_log.json` stores lineage entries
- `provenance/checksum_history.json` tracks fingerprint history

Completeness score evaluates presence of source, user, transformation steps, and schema version.
