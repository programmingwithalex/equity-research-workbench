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
