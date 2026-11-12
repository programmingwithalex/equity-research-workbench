# Equity Research Workbench

A personal financial-research application for comparing company filings and
building evidence-backed research reports, starting with TKO and APH.

## Current implementation

The project currently contains a Python package skeleton and development checks.
Filing ingestion, retrieval, answer generation, technical analysis, and portfolio
scenarios are not implemented yet. No investment recommendations are generated.

The first three increments are:

1. Establish the repository, documentation, and CI quality gates.
2. Discover eligible TKO and APH annual and quarterly filings from SEC metadata.
3. Archive selected filings with source metadata and content checksums.

Each increment is taught, reviewed, and verified before moving to the next.
See the [learning log](docs/LEARNING_LOG.md) for concepts and decisions and the
[project status](docs/PROJECT_STATUS.md) for technical handoff state.

## Local setup

Use Python 3.14. The same minor version is used in GitHub Actions.
Run the following from the repository root in PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation --editable .
```

The first command creates an isolated environment. The second installs the pinned
development dependencies. The third installs this package from `src/` in editable
mode, reusing the installed build backend; source changes are then importable
without reinstalling. Runtime application dependencies have not been added yet.

On macOS/Linux, use `.venv/bin/python` instead of `.venv\Scripts\python.exe`.

## Quality checks

```powershell
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m ruff format --check .
.venv\Scripts\python.exe -m mypy
```

Ruff checks lint, imports, docstring conventions, and formatting. Mypy checks
annotated Python code using strict settings from `pyproject.toml`.

Pytest is installed and configured, but there are no application tests yet.
The first functional feature must add behavioral tests and make pytest a required
part of CI. Until then, CI reports lint, formatting, and type-check results only.
These checks do not establish application correctness or financial accuracy.

## Development and releases

Changes use feature-branch pull requests with required CI checks before merging
into `main`. See [CONTRIBUTING.md](CONTRIBUTING.md) for the review workflow.
The only direct-to-main exception is the initial README bootstrap commit.

The first tagged release, `v0.1.0`, is planned after filing discovery and archival
are implemented and reviewed. See [CHANGELOG.md](CHANGELOG.md). Release automation
and deployment scripts have not been implemented yet.

## Public-data boundary

Only source code, public-source test fixtures, and synthetic portfolio examples
belong in Git. Generated downloads, personal holdings, credentials, and local
configuration belong in ignored directories or environment files. The existing
company-policy learning repository remains a separate project.
