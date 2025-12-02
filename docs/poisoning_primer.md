# Poisoning Techniques (Simulated)

- **Label flipping**: Detects patterns where labels are intentionally inverted.
- **Gradient poisoning**: Simulated via clustering anomalies to mimic corrupted gradients.
- **Backdoor triggers**: Rare pattern scanner flags unusual tokens like `trigger_*`.
- **Synthetic malicious samples**: Minority clusters identified as suspicious.
- **Targeted bias injection**: Sensitive group labelled `rare_group` increases scrutiny.

All detections are heuristic and non-invasive to keep the environment safe and educational.
