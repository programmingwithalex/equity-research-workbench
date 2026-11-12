# Contributing

## Increment and review workflow

1. Explain the concept, alternatives, dependencies, and runtime flow for one small
   increment. Review the proposed files and behavior before editing.
2. Create a feature branch from `main`; keep unrelated changes out of the PR.
3. Add behavioral tests alongside application logic. Use focused fixtures for SEC
   metadata and mock HTTP responses; ordinary CI must not use live SEC or model
   APIs.
4. Run the README quality commands and, once tests exist, `python -m pytest` using
   the project virtual environment. Inspect the diff and update documentation.
5. Open a PR describing behavior, verification, and limitations. Alex reviews the
   implementation and learning checkpoint before merge. Passing checks are
   required; a separate approving reviewer is not required for this solo project.

The only direct-to-main exception is the initial README bootstrap commit. After
the first `quality` check is registered, protect `main` against direct changes,
force pushes, and deletion, including administrator bypass.

## Code and documentation

- Annotate function parameters and returns; keep mypy strict mode enabled.
- Use Google-style docstrings. Explain inputs, outputs, side effects, and
  exceptions when they are relevant to the function.
- Comments explain non-obvious decisions and assumptions, rather than repeat
  individual Python statements.
- Prefer direct, readable code. Assume project-owned inputs are well-formed;
  enforce meaningful source provenance, external-data, and correctness boundaries
  without surrounding every operation with generic exception handling.
- Keep the README current. Record learning in `docs/LEARNING_LOG.md` and technical
  handoff state in `docs/PROJECT_STATUS.md`; keep both distinct from the changelog.
- Ruff enforces docstring conventions but cannot establish that an explanation is
  informative. Human review must check that.

## Versions and public content

Use semantic release tags such as `v0.1.0` and describe changes in `CHANGELOG.md`.
Release automation starts with the first complete filing-library release;
deployment automation follows later.

Only public-source fixtures and synthetic portfolio examples may be committed.
Keep downloads, personal financial data, credentials, and environment files local.
Check the exact staged file list before every commit.
