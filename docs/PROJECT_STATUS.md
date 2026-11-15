# Project status

## Current increment

SEC metadata fetching for `programmingwithalex/equity-research-workbench`.
[PR #1](https://github.com/programmingwithalex/equity-research-workbench/pull/1)
was approved and merged. Filing selection was merged in
[PR #2](https://github.com/programmingwithalex/equity-research-workbench/pull/2)
with nine passing tests. Ruff automation was merged in
[PR #3](https://github.com/programmingwithalex/equity-research-workbench/pull/3).
The parser was merged into `main` in
[PR #4](https://github.com/programmingwithalex/equity-research-workbench/pull/4).

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
- Pinned Ruff formatting in a local pre-commit hook, installed separately per clone.
- A same-repository PR formatter job that commits corrections with a normal push
  and dispatches fresh CI. Fork, Dependabot, main, and manual runs are read-only.
- Four local Git integration tests for no-op, commit/push/dispatch, concurrent
  push rejection, and dispatch failure. GitHub calls are stubbed; Bash is required.
- Pure `parse_filings` conversion for supplied recent or historical SEC columns.
  It preserves input order, all forms, dates, and citation references, with unknown
  report periods represented as `None`. No new dependency is introduced.
- Synthetic parser tests and a parser-to-selector historical-coverage case.
- HTTPX-backed `SecClient`: fetch the company index and every listed history file,
  check company identity and wire column types, then reuse `parse_filings`.
- One shared request policy for declared identity, inactivity timeouts, local
  pacing, fixed SEC destinations, and redirect refusal. HTTPX client ownership
  and cleanup belong to the caller. Required-batch failures return no partial list.
- Shared SEC column names and test fixtures, plus separate runtime/development
  lockfiles included together in CI cache keys. HTTPX is the direct runtime dependency.

The discovery CLI, report downloads, archival storage, embeddings, retrieval,
model integration, UI, MCP, financial analysis, technical indicators, and deployment
are not built. Metadata fetching alone does not complete the planned CLI or archive.

## Verification and repository controls

- Eighteen offline HTTPX client cases passed, covering history completeness,
  HTTP/timeout failures, identity/destination/redirect checks, pacing, and wire types.
  Ruff lint and strict mypy passed after the client and shared-fixture changes.
- A manual November 15, 2026 APH check used the real client to fetch its company
  index and one listed historical file, producing 2,017 references. This establishes
  one successful live integration check, not ongoing availability or completeness
  of all possible SEC history. No reports or personal data were written to Git.
- Pacing is per shared client instance; multi-worker ingestion needs a shared SEC
  rate budget. Retries, caching, ingestion jobs, and whole-job deadlines remain
  separate operational work. No user-capacity or performance benchmark is claimed.

- Seven parser cases and the full 20-test suite passed locally, including shorter
  and longer-column whole-batch rejection, as Alex requested. Ruff lint/format,
  strict mypy (six files), and whitespace checks passed. The feature PR and its
  exact-head required CI are the source of truth for publication state.

- The formatter helper's four local cases and nine filing cases passed together.
  Live GitHub token permissions and dispatch delivery require remote verification;
  local helper tests do not establish those platform behaviors.

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

1. Add the TKO/APH discovery CLI using the client, parser, and selector. Keep
   completeness/failure behavior explicit and add command-level tests.
2. Archive selected source documents and provenance/checksums; test repeat runs and
   prepare the `v0.1.0` release workflow.

Keep the old company-policy repository untouched. The combined skill is installed
as `$simplify-review-rebase`. Before every future PR merge, complete that workflow
and verify required CI on the exact resulting head. Alex authorizes automatic
merging when no findings remain outstanding and checks pass; otherwise keep the
PR open and report the blocker. Do not commit generated downloads, personal
financial information, credentials, or local environments.
