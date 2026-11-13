# Test policy

`test_filings.py` contains nine behavioral cases for selecting original filings
at a historical cutoff. They use synthetic typed references with example.com
source URLs, not downloaded SEC metadata or facts about TKO/APH.

The cases cover look-ahead exclusion, stability after future filings are added,
an inclusive cutoff, company identity, excluded forms and amendments, missing
results, same-day ties, input order, and preservation of original source metadata.
Pytest runs in the required CI quality job; strict mypy checks the tests too.

`test_ci_format.py` adds four integration cases for the actual CI Bash helper:
already-formatted code creates no commit or workflow dispatch; malformed spacing
produces a formatting commit, normal push, and fresh-check request; a concurrent
push is preserved; and a dispatch failure after a successful push stays failed.
Temporary working copies and bare Git origins are local. A stub `gh` records the
dispatch request, and a path check refuses to run against the real GitHub CLI.
These tests validate helper behavior, not live GitHub permissions or event delivery.
They require Bash (Git for Windows provides it) and the installed project Ruff.

When the SEC client is added, use recorded public-source response fixtures and
mocked HTTP calls. Ordinary CI must not contact SEC or paid model APIs.

Keep tests focused on observable behavior. Explain the failure or requirement a
test protects; avoid tests that merely repeat constants or implementation details.
