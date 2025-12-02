# Security Policy

TDIE is intentionally synthetic-safe and designed to avoid processing real personal data. Please help us keep it secure and educational.

## Supported Versions
The `main` branch is supported. Report issues against the latest commit or tagged release.

## Reporting a Vulnerability
- Email the maintainers or open a private security issue with reproduction steps and impact.
- Do not include sensitive data in reports; provide synthetic examples instead.
- We aim to acknowledge reports within 2 business days and provide an action plan within 7 days.

## Security Best Practices for Contributors
- Never introduce PII or outbound network calls.
- Validate and sanitize all inputs; prefer Pydantic models for request validation.
- Avoid logging secrets or full payloads; rely on structured, minimal logs.
- Keep dependencies minimal and up to date.

## Responsible Disclosure
If you discover a vulnerability, please give us a reasonable opportunity to investigate and remediate before public disclosure.
