# Equity Research Workbench

A personal financial-research application for comparing company filings and
building evidence-backed research reports, starting with TKO and APH.

## Current implementation

The project contains a typed filing reference and a pure selector for the latest
eligible original 10-K and 10-Q at a research-date cutoff. A pure SEC metadata
parser converts supplied column arrays into those references. SEC HTTP requests,
historical-file discovery, and a command-line interface are not implemented yet.

Filing downloads, retrieval, answer generation, technical analysis, and portfolio
scenarios are not implemented. No investment recommendations are generated.

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
.venv\Scripts\python.exe -m pre_commit install --install-hooks
```

The first command creates an isolated environment. The second installs the pinned
development dependencies. The third installs this package from `src/` in editable
mode, reusing the installed build backend; source changes are then importable
without reinstalling. Runtime application dependencies have not been added yet.
The fourth command installs the local Git hook and its isolated Ruff environment.
Before each commit, it formats staged Python files. If it changes a file, inspect
the changes, stage them again, and retry the commit. Hook installation is needed
in each clone; it is not enabled merely by cloning the repository.

On macOS/Linux, use `.venv/bin/python` instead of `.venv\Scripts\python.exe`.

## Quality checks

```powershell
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m ruff format --check .
.venv\Scripts\python.exe -m mypy
.venv\Scripts\python.exe -m pytest
```

Ruff checks lint, imports, docstring conventions, and formatting. Mypy checks
annotated source and tests using strict settings from `pyproject.toml`. Pytest
checks selection behavior and CI formatting using local Git remotes and a stubbed
GitHub CLI. The formatting tests require Bash, provided by Git for Windows on
Windows and by the CI runner on Linux. The tests make no external requests.
CI runs the formatter itself and requires a clean diff, plus lint, typing, and
tests. These tests do not evaluate
live SEC data, retrieval relevance, generated answers, or financial accuracy.

### Automatic formatting in CI

For same-repository PRs, except Dependabot, a separate job runs Ruff and commits
formatting corrections back to the source branch using the workflow token. It
uses a normal push, so it cannot overwrite a concurrent contributor push. Local
pre-commit and CI use the same pinned Ruff version. Fork PRs, Dependabot PRs,
`main` pushes, and manual runs only validate formatting without pushing changes.

After a formatting push, CI explicitly dispatches a new run for the updated branch.
The old revision's quality gate fails intentionally; only checks on the new head
count. A new formatting commit also requires review of that head before merging.
If dispatch fails after a successful push, inspect the branch and request checks
with `gh workflow run ci.yml --ref <branch>`; the failed run does not become green.
The write-enabled job is restricted to trusted same-repository PR code. It uses
the short-lived GitHub Actions token, with no personal access token required.

## Filing-selection behavior

`equity_research.filings.select_latest_filings(records, cik=..., as_of=...)` returns
the latest eligible original 10-K and 10-Q, in that order, omitting missing forms.
Company identity uses the supplied canonical CIK rather than the display ticker.
Eligibility uses public filing date, not the reporting-period end. For example,
a June-period report published in August cannot be used for July research.

The cutoff is inclusive and has day precision. Same-day ties use the accession
number for reproducibility, not as evidence of intraday publication order.
Amended forms such as 10-Q/A are excluded from this first selector. The function
returns original records with source URLs and reporting periods intact and does
not modify the input collection.

To inspect the look-ahead case manually, read the synthetic fixture and expected
accessions in `tests/test_filings.py`, then run:

```powershell
.venv\Scripts\python.exe -m pytest -v tests/test_filings.py
```

Dates, identities, and URLs in these fixtures are synthetic and are not current
facts about TKO or APH.

## SEC metadata parsing

`equity_research.sec_metadata.parse_filings(columns, cik=..., ticker=...)` accepts
the `filings.recent` columns from a submissions response or equivalent top-level
columns from a historical response. Company identity is supplied explicitly so
the same function can parse either batch. It pairs fields by array position,
converts ISO dates, preserves blank report dates as `None`, and constructs SEC
archive source URLs. It preserves every form; the selector handles eligibility.
Required columns are `accessionNumber`, `form`, `filingDate`, `reportDate`, and
`primaryDocument`. The parser expects SEC-shaped string arrays; it does not perform
general JSON schema validation. Required columns must have equal lengths.

Fetching is separate from parsing. An empty batch does not prove that no eligible
filing exists across a company's history. Discovery must inspect relevant older
files before making that claim. See the [SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces).

To inspect the historical-coverage example, run:

```powershell
.venv\Scripts\python.exe -m pytest -v tests/test_sec_metadata.py -k recent_and_historical
```

The recent-only synthetic input has no eligible annual report at the cutoff;
adding the supplied historical batch finds it. This verifies parsing and selection
together, without implementing or exercising HTTP fetching.

## Development and releases

Changes use feature-branch pull requests with required CI checks before merging
into `main`. See [CONTRIBUTING.md](CONTRIBUTING.md) for the review workflow.
The only direct-to-main exception is the initial README bootstrap commit.
Every future PR merge must first complete the installed `$simplify-review-rebase`
skill and pass CI on the resulting revision. Alex authorizes automatic merging
in this repository when the workflow has no outstanding findings and required
checks pass for that exact revision. Otherwise, keep the PR open and report what
remains. See the contribution guide for the fix and merge policy.

The first tagged release, `v0.1.0`, is planned after filing discovery and archival
are implemented and reviewed. See [CHANGELOG.md](CHANGELOG.md). Release automation
and deployment scripts have not been implemented yet.

## Public-data boundary

Only source code, public-source test fixtures, and synthetic portfolio examples
belong in Git. Generated downloads, personal holdings, credentials, and local
configuration belong in ignored directories or environment files. The existing
company-policy learning repository remains a separate project.
