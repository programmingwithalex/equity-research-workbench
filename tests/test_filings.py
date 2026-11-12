"""Test historical selection using synthetic metadata without network access."""

from dataclasses import replace
from datetime import date

import pytest

from equity_research.filings import Filing, select_latest_filings


def _filing(
    form: str,
    filed: str,
    period: str | None,
    accession: str,
    *,
    cik: str = "0000000001",
    ticker: str = "EXAMPLE_A",
) -> Filing:
    """Build one synthetic reference with explicitly supplied filing dates.

    Args:
        form: SEC form name for the scenario.
        filed: ISO public filing date.
        period: ISO reporting-period end, or None when absent.
        accession: Synthetic submission identifier.
        cik: Synthetic company identity, separate from the display ticker.
        ticker: Synthetic display ticker.

    Returns:
        A typed reference with parsed dates and a non-SEC example source URL.
    """
    return Filing(
        ticker=ticker,
        cik=cik,
        form=form,
        accession_number=accession,
        filing_date=date.fromisoformat(filed),
        report_date=date.fromisoformat(period) if period is not None else None,
        source_url=f"https://example.com/filings/{accession}.html",
    )


@pytest.fixture
def filings() -> list[Filing]:
    """Supply synthetic companies, periods, and excluded forms for selection.

    Returns:
        References whose identities, dates, and URLs are test data rather than
        downloaded SEC records. The August report covers a period before July's
        cutoff, creating the look-ahead trap the selector must prevent.
    """
    return [
        _filing("10-K", "2025-02-14", "2024-12-31", "0000000001-25-000001"),
        _filing("10-K", "2026-02-14", "2025-12-31", "0000000001-26-000001"),
        _filing("10-Q", "2026-05-05", "2026-03-31", "0000000001-26-000002"),
        _filing("10-Q", "2026-08-05", "2026-06-30", "0000000001-26-000003"),
        _filing("10-Q/A", "2026-09-05", "2026-06-30", "0000000001-26-000004"),
        _filing("8-K", "2026-09-15", None, "0000000001-26-000005"),
        _filing(
            "10-Q",
            "2026-09-20",
            "2026-06-30",
            "0000000002-26-000001",
            cik="0000000002",
            ticker="EXAMPLE_A",
        ),
    ]


def test_historical_cutoff_uses_publication_not_period_end(
    filings: list[Filing],
) -> None:
    """Exclude an August publication even though its period ends before July."""
    selected = select_latest_filings(filings, cik="0000000001", as_of=date(2026, 7, 31))

    assert [filing.accession_number for filing in selected] == [
        "0000000001-26-000001",
        "0000000001-26-000002",
    ]


def test_adding_future_filings_does_not_change_historical_result(
    filings: list[Filing],
) -> None:
    """Keep a historical selection stable as later publications are added."""
    cutoff = date(2026, 7, 31)
    original_history = filings[:3]

    assert select_latest_filings(filings, cik="0000000001", as_of=cutoff) == (
        select_latest_filings(original_history, cik="0000000001", as_of=cutoff)
    )


def test_publication_on_cutoff_date_is_eligible(filings: list[Filing]) -> None:
    """Include the exact cutoff date instead of dropping that day's filing."""
    selected = select_latest_filings(filings, cik="0000000001", as_of=date(2026, 8, 5))

    assert selected[1].accession_number == "0000000001-26-000003"


def test_amendments_other_forms_and_other_companies_are_excluded(
    filings: list[Filing],
) -> None:
    """Keep original forms and company identity despite newer distractors."""
    selected = select_latest_filings(
        filings, cik="0000000001", as_of=date(2026, 12, 31)
    )

    assert [(filing.form, filing.accession_number) for filing in selected] == [
        ("10-K", "0000000001-26-000001"),
        ("10-Q", "0000000001-26-000003"),
    ]


def test_missing_form_is_omitted_without_fallback(filings: list[Filing]) -> None:
    """Return the available annual report without inventing a quarterly match."""
    selected = select_latest_filings(
        filings, cik="0000000001", as_of=date(2025, 12, 31)
    )

    assert [filing.accession_number for filing in selected] == ["0000000001-25-000001"]


@pytest.mark.parametrize(
    ("cik", "cutoff"),
    [
        ("0000000001", date(2020, 1, 1)),
        ("0000000003", date(2026, 12, 31)),
    ],
)
def test_no_eligible_filing_returns_empty(
    filings: list[Filing], cik: str, cutoff: date
) -> None:
    """Return no result for absent companies or dates before all publications."""
    assert select_latest_filings(filings, cik=cik, as_of=cutoff) == []


def test_order_and_same_day_ties_are_deterministic(filings: list[Filing]) -> None:
    """Resolve date ties consistently without relying on upstream result order."""
    tied = replace(
        filings[3],
        accession_number="0000000001-26-000099",
        source_url="https://example.com/filings/same-day.html",
    )
    records = [*filings, tied]
    selected = select_latest_filings(records, cik="0000000001", as_of=date(2026, 8, 5))

    assert selected[1] is tied
    assert selected == select_latest_filings(
        reversed(records), cik="0000000001", as_of=date(2026, 8, 5)
    )


def test_original_source_metadata_and_input_are_preserved(
    filings: list[Filing],
) -> None:
    """Retain citation provenance while leaving supplied history untouched."""
    before = list(filings)
    selected = select_latest_filings(filings, cik="0000000001", as_of=date(2026, 7, 31))

    assert filings == before
    assert selected[0] is filings[1]
    assert selected[1] is filings[2]
    assert selected[1].source_url == (
        "https://example.com/filings/0000000001-26-000002.html"
    )
    assert selected[1].report_date == date(2026, 3, 31)
