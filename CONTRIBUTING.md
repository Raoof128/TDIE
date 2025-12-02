# Contributing Guide

Thank you for investing time in improving TDIE. We welcome issues, feature ideas, and pull requests.

## Development Setup
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run tests:
   ```bash
   pytest
   ```
3. Start the API:
   ```bash
   uvicorn backend.main:app --reload
   ```

## Coding Standards
- Use type hints and docstrings for all public functions/classes.
- Prefer small, composable modules and keep business logic in `backend/engines`.
- Write clear logs; avoid logging sensitive content.
- Keep changes synthetic-safe; never introduce PII or outbound network calls.

## Pull Request Checklist
- Add tests for new features or bug fixes.
- Update documentation and diagrams as needed.
- Run linters/formatters and ensure `pytest` passes.
- Ensure no secrets or personal data are committed.
- Provide a short summary of the change and any operational considerations.

## Branching & Releases
- Use feature branches (`feature/<topic>`). Keep main stable and passing CI.
- Rebase or merge main frequently to reduce drift.

## Reporting Security Issues
Please avoid public disclosure. Email the maintainers or open a private issue with details so we can respond responsibly.
