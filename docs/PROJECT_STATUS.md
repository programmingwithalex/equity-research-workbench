# Project status

## Current increment

Repository and CI foundation for `programmingwithalex/equity-research-workbench`.
The bootstrap README is on `main`; foundation changes are being prepared on
`codex/bootstrap-quality` for Alex's review.

## Implemented scope

- Python 3.14 package skeleton using the `src/` layout.
- Pinned development dependencies, Ruff lint/format configuration, strict mypy,
  and pytest configuration.
- GitHub Actions `quality` job for lint, formatting, and typing on PRs and `main`.
- README, contribution instructions, changelog, and separate learning log.

No application functions or tests exist yet. Pytest is configured but intentionally
not run by CI until the first functional feature adds behavioral tests. Filing
discovery, downloads, parsing, storage, embeddings, retrieval, model integration,
UI, MCP, financial analysis, technical indicators, and deployment are not built.

## Verification and repository controls

- Local installation, dependency consistency, Ruff lint/format, strict mypy, and
  package import checks passed. The first remote CI run is pending.
- Main-branch protection will require the registered `quality` check and PRs,
  including administrators, with no force pushes or deletion.
- No application behavior, retrieval quality, financial accuracy, or performance
  claim has been verified.
- No version tag, release workflow, release, or deployment exists yet.

## Next increments after review

1. Discover latest eligible 10-K/10-Q filings for TKO/APH at a research-date cutoff;
   add deterministic SEC-response tests and enable pytest in CI.
2. Archive selected source documents and provenance/checksums; test repeat runs and
   prepare the `v0.1.0` release workflow.

Keep the old company-policy repository untouched. Do not merge this feature PR
before Alex's review and learning checkpoint. Do not commit generated downloads,
personal financial information, credentials, or local environments.
