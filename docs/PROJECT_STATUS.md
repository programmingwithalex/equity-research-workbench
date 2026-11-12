# Project status

## Current increment

Historical filing-selection slice for `programmingwithalex/equity-research-workbench`.
[PR #1](https://github.com/programmingwithalex/equity-research-workbench/pull/1)
was approved and merged. The current increment is tracked in
[PR #2](https://github.com/programmingwithalex/equity-research-workbench/pull/2)
on `codex/sec-filing-discovery`; the PR is the source of truth for merge status.

## Implemented scope

- Python 3.14 package skeleton using the `src/` layout.
- Pinned development dependencies, Ruff lint/format configuration, strict mypy,
  and pytest configuration.
- Immutable `Filing` references and a pure `select_latest_filings` function.
- Latest original 10-K/10-Q selection by company CIK and inclusive public filing
  date, with deterministic same-day ties and preserved source metadata.
- Nine synthetic behavioral tests; no external network calls or live SEC facts.
- GitHub Actions `quality` job for lint, formatting, typing, and pytest on PRs and
  `main`. Strict mypy now includes tests.
- README, contribution instructions, changelog, and separate learning log.

SEC metadata fetching/parsing, historical-file handling, the discovery CLI,
downloads, storage, embeddings, retrieval, model integration, UI, MCP, financial
analysis, technical indicators, and deployment are not built. The selector alone
does not complete the planned SEC-discovery feature.

## Verification and repository controls

- Local installation, dependency consistency, Ruff lint/format, strict mypy, and
  package import checks passed.
- The first [Linux CI run](https://github.com/programmingwithalex/equity-research-workbench/actions/runs/43299339708)
  passed dependency installation, editable installation, lint, formatting, and
  typing. No application tests ran.
- Main-branch protection requires PRs and the up-to-date `quality` check,
  including for administrators, with no force pushes or deletion. The GitHub API
  confirmed these settings. No separate approving reviewer is required.
- No application behavior, retrieval quality, financial accuracy, or performance
  claim was established by the foundation. The current selector's nine synthetic
  cases passed locally; PR #2 shows remote CI for the final revision. No live filing,
  retrieval-quality, financial-accuracy, or performance claim is established.
- No version tag, release workflow, release, or deployment exists yet.

## Next increments after review

1. Parse/fetch SEC metadata and add the TKO/APH discovery CLI, reusing the tested
   selector and adding mocked HTTP/metadata cases.
2. Archive selected source documents and provenance/checksums; test repeat runs and
   prepare the `v0.1.0` release workflow.

Keep the old company-policy repository untouched. The combined skill is installed
as `$simplify-review-rebase`. Before every future PR merge, complete that workflow
and verify required CI on the exact resulting head. Alex authorizes automatic
merging when no findings remain outstanding and checks pass; otherwise keep the
PR open and report the blocker. Do not commit generated downloads, personal
financial information, credentials, or local environments.
