# Changelog

## Unreleased

- Auto-format staged Python with a pinned Ruff pre-commit hook. For trusted
  same-repository PRs, commit CI formatting corrections back and dispatch checks
  for the new head; keep other CI paths read-only.
- Test formatting commits, no-op runs, concurrent pushes, and dispatch failures
  with temporary local Git remotes and a stubbed GitHub CLI.

- Establish the Python package skeleton, pinned development tools, documentation,
  and GitHub Actions quality checks.
- Add typed filing references, date-aware original-form selection, and nine
  synthetic behavioral tests. Include tests in the required quality job and
  strict type checking.
- Require `/simplify-review-rebase` before future PR merges.

No release has been published. The first planned version is `v0.1.0`, after the
filing discovery and archive increments are implemented and reviewed.
