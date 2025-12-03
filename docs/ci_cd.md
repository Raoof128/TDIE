# CI/CD Pipeline

The repository ships with a GitHub Actions workflow (`.github/workflows/ci.yml`) that enforces quality gates on every push and pull request.

## What the pipeline runs
- **Lint**: `make lint` executes Ruff and Black in check mode to enforce formatting and static analysis.
- **Tests**: `make test` runs the full pytest suite, including async API checks.
- **Python matrix**: Jobs execute on Python 3.11 and 3.12 to guard against version regressions.
- **Pip cache**: Dependencies are cached between runs for faster feedback.

## Local equivalence
To reproduce the CI checks locally:

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
make ci
```

## Status badges
You can embed the following badge in documentation to surface pipeline health:

```markdown
![CI](https://github.com/<org>/TDIE/actions/workflows/ci.yml/badge.svg)
```
Replace `<org>` with your GitHub organization or username.
