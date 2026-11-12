# Test policy

`test_filings.py` contains nine behavioral cases for selecting original filings
at a historical cutoff. They use synthetic typed references with example.com
source URLs, not downloaded SEC metadata or facts about TKO/APH.

The cases cover look-ahead exclusion, stability after future filings are added,
an inclusive cutoff, company identity, excluded forms and amendments, missing
results, same-day ties, input order, and preservation of original source metadata.
Pytest runs in the required CI quality job; strict mypy checks the tests too.

When the SEC client is added, use recorded public-source response fixtures and
mocked HTTP calls. Ordinary CI must not contact SEC or paid model APIs.

Keep tests focused on observable behavior. Explain the failure or requirement a
test protects; avoid tests that merely repeat constants or implementation details.
