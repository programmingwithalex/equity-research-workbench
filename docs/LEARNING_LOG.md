# Learning log

## Working agreement

Learn one concept and implement one small increment at a time. Explain concepts,
alternatives, dependencies, commands, and runtime flow before changes. Use the
authorization already given for the agreed increment; do not repeatedly ask for
the same permission. Stop at meaningful comprehension and review checkpoints.

Prioritize architecture, evidence coverage, evaluation, and failure modes over
elementary syntax quizzes. Include informative docstrings and decision comments.
Assume well-formed project-owned inputs where appropriate; do not hide the main
logic under generic defensive handling.

## 2026-11-12: Repository and CI foundation

### Concepts covered

- A feature branch isolates an increment; a pull request presents its diff for
  review. Required checks prevent merging when configured checks fail.
- CI repeats quality commands against a clean checkout. Local success alone does
  not establish that the same dependency installation works on Linux CI.
- Ruff linting and formatting, mypy static typing, and behavioral tests answer
  different questions. None proves the financial validity of future model output.
- A virtual environment isolates dependencies. Exact tool versions and a
  committed dependency snapshot keep local and CI installations aligned.
- A `src/` package layout and editable installation make imports explicit.
- Public repository visibility does not require publishing personal portfolio
  data, generated downloads, or credentials.

### Decisions Alex made

- Build a personal financial-research application, starting with TKO and APH.
- Create the public `programmingwithalex/equity-research-workbench` repository;
  preserve the existing policy lab as a separate project.
- Track code changes rather than add an API-cost ledger in this increment.
- Prioritize feature PRs, CI, tests, strict typing, formatting, documentation, and
  versioned releases. Introduce deployment scripts later.
- Approve the first three planned increments, beginning with this foundation.

### Implementation and verification

- Bootstrap `main` with the README; present the foundation changes on a feature PR.
- Pin Ruff, mypy, pytest, and the setuptools build backend. No application runtime
  dependencies or application functions are introduced.
- Configure pytest now and enable its CI gate with the first actual behavior and
  tests. No placeholder tests are added.
- Local editable installation and dependency consistency checks passed. Ruff lint,
  Ruff formatting, and strict mypy passed; mypy checked the single package module.
- The first GitHub Actions Linux run passed clean dependency installation,
  editable installation, lint, formatting, and typing. No application tests ran.
- Verified main-branch protection through the GitHub API: require PRs and the
  up-to-date `quality` check, apply protections to administrators, and disallow
  force pushes and deletion. No separate approving reviewer is required.
- Opened PR #1 for the foundation increment. It remains unmerged for review.

### Debugging lessons

- The GitHub connector returned HTTP 403 when creating the PR. The already
  authenticated GitHub CLI could create it. Connector permissions and CLI
  credentials are separate access paths; no new token was created.

### Remaining learning checkpoints

- Review the small diff and distinguish what each CI check establishes.
- Before SEC discovery, understand filing identity, publication date versus
  reporting period, and how a research-date cutoff prevents future-data leakage.
- No retrieval, generated-answer, trading-signal, cost, or performance result has
  been measured by this repository.

## 2026-11-12: Historical filing selection

### Concepts and decisions

- A reporting period describes the business interval; the filing date determines
  eligibility for a historical research date. Filtering only on report-period end
  can admit evidence that was not yet public.
- SEC company identity uses CIK, while an accession identifies a submission. A
  display ticker alone is not used as the selector's company identity.
- Separate pure selection from future network fetching and SEC JSON parsing.
  Supplied typed records make the date policy explicit and testable offline.
- Return the latest original 10-K and 10-Q independently. This does not establish
  that the selected reporting periods are suitable for numerical comparisons.
- Use an inclusive day-level cutoff. Break same-day ties by accession solely for
  deterministic results; intraday ordering is outside this slice.
- Omit missing forms and exclude amendments. Preserve the supplied source and
  date fields rather than inventing evidence or borrowing another company.

### Implementation and verification

- PR #1 was approved and merged. Work continues on `codex/sec-filing-discovery`.
- Added the immutable `Filing` record and `select_latest_filings`; no HTTP client,
  live metadata parser, CLI, or new dependency is introduced.
- Nine synthetic pytest cases passed locally. Ruff lint and strict mypy passed;
  mypy now includes tests. Ruff formatting initially requested line wrapping in
  the test file; the formatter corrected it without changing behavior.
- Added pytest to the existing required CI job. The latest remote result is
  available on [PR #2](https://github.com/programmingwithalex/equity-research-workbench/pull/2).
  Local lint, formatting, strict typing, and whitespace checks passed after the
  formatting correction.
- Alex requested that every future PR merge run `/simplify-review-rebase`. Its
  exact definition was initially unavailable. The combined skill was subsequently
  created as `$simplify-review-rebase` and run on PR #2. The first review found no
  blocking or should-fix defects; M1 identified stale workflow-availability text.
- Resolve M1 during merge preparation by updating the current README/status
  statements. Preserve the historical account of the missing workflow here.
- Alex authorizes automatic merges in this repository after the combined workflow
  has no outstanding findings and required CI passes for the exact reviewed head.
  A green check alone is insufficient, and unresolved minor findings also block
  automatic merging unless Alex explicitly accepts them.

### Remaining learning gaps and next slice

- Date-selection behavior has automated tests; independent explanation by Alex
  has not been checked through a completed comprehension answer.
- Next: parse SEC metadata, handle historical submission files, fetch through an
  explicit HTTP client, and provide the discovery CLI. These are not built yet.
- Source snapshots and archive checksums are a later increment. This selector
  cannot prove that a future live data source will never revise past metadata.
