# Training-Time Threat Models (Educational)

- **Data tampering**: Mitigated via SHA-256 fingerprints and tamper diff detection.
- **Poisoning**: Simulated via clustering anomalies, label flip detection, and rare pattern scans.
- **Bias amplification**: Mitigated through fairness metrics and imbalance checks.
- **Drift**: Detected via baseline comparisons and TDIE scoring.
- **Unauthorized training**: Guardrails block or flag low scores and produce evidence bundles.

These are simulations to teach integrity practices without real-world attack data.
