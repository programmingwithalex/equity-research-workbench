"""Test SEC-shaped synthetic metadata and selector integration without HTTP."""

from copy import deepcopy
from datetime import date

import pytest

from equity_research.filings import Filing, select_latest_filings
from equity_research.sec_metadata import parse_filings


@pytest.fixture
def columns() -> dict[str, list[str]]:
    """Supply aligned SEC-style columns using entirely synthetic filing values.

    Returns:
        Annual and quarterly metadata with distinct identities and dates so
        accidental mixing of columns would produce an observable wrong record.
    """
    return {
        "accessionNumber": ["0000000001-26-000001", "0000000001-26-000002"],
        "form": ["10-K", "10-Q"],
        "filingDate": ["2026-02-14", "2026-05-05"],
        "reportDate": ["2025-12-31", "2026-03-31"],
        "primaryDocument": ["annual.htm", "quarterly.htm"],
    }


def test_columns_become_aligned_filing_records_without_mutation(
    columns: dict[str, list[str]],
) -> None:
    """Preserve identity, row alignment, dates, order, and input metadata."""
    before = deepcopy(columns)

    records = parse_filings(columns, cik="0000000001", ticker="EXAMPLE")

    assert records == [
        Filing(
            ticker="EXAMPLE",
            cik="0000000001",
            form="10-K",
            accession_number="0000000001-26-000001",
            filing_date=date(2026, 2, 14),
            report_date=date(2025, 12, 31),
            source_url=(
                "https://www.sec.gov/Archives/edgar/data/1/"
                "000000000126000001/annual.htm"
            ),
        ),
        Filing(
            ticker="EXAMPLE",
            cik="0000000001",
            form="10-Q",
            accession_number="0000000001-26-000002",
            filing_date=date(2026, 5, 5),
            report_date=date(2026, 3, 31),
            source_url=(
                "https://www.sec.gov/Archives/edgar/data/1/"
                "000000000126000002/quarterly.htm"
            ),
        ),
    ]
    assert columns == before


def test_missing_report_period_and_other_forms_are_preserved(
    columns: dict[str, list[str]],
) -> None:
    """Keep missing evidence explicit and leave form eligibility to the selector."""
    columns["reportDate"][0] = ""
    columns["form"] = ["8-K", "10-Q/A"]
    columns["unusedColumn"] = ["ignored"]

    records = parse_filings(columns, cik="0000000001", ticker="EXAMPLE")

    assert [record.form for record in records] == ["8-K", "10-Q/A"]
    assert records[0].report_date is None
    assert records[0].filing_date == date(2026, 2, 14)


def test_document_name_is_encoded_as_one_url_component(
    columns: dict[str, list[str]],
) -> None:
    """Prevent filename punctuation from becoming a query string or fragment."""
    columns["primaryDocument"][0] = "annual report#1?.htm"

    records = parse_filings(columns, cik="0000000001", ticker="EXAMPLE")

    assert records[0].source_url == (
        "https://www.sec.gov/Archives/edgar/data/1/"
        "000000000126000001/annual%20report%231%3F.htm"
    )


def test_empty_columns_return_no_records(columns: dict[str, list[str]]) -> None:
    """Represent an empty supplied batch without inventing filing references."""
    empty_columns: dict[str, list[str]] = {name: [] for name in columns}

    assert parse_filings(empty_columns, cik="0000000001", ticker="EXAMPLE") == []


@pytest.mark.parametrize(
    "documents",
    [
        ["annual.htm"],
        ["annual.htm", "quarterly.htm", "extra.htm"],
    ],
    ids=["shorter-column", "longer-column"],
)
def test_unequal_columns_reject_the_batch(
    columns: dict[str, list[str]], documents: list[str]
) -> None:
    """Reject incomplete evidence even when the first row can be assembled."""
    columns["primaryDocument"] = documents

    with pytest.raises(ValueError):
        parse_filings(columns, cik="0000000001", ticker="EXAMPLE")


def test_recent_and_historical_batches_feed_the_same_selector(
    columns: dict[str, list[str]],
) -> None:
    """Show why parsing recent data alone cannot establish historical absence."""
    history = {
        "accessionNumber": ["0000000001-25-000001"],
        "form": ["10-K"],
        "filingDate": ["2025-02-14"],
        "reportDate": ["2024-12-31"],
        "primaryDocument": ["older-annual.htm"],
    }
    recent_records = parse_filings(columns, cik="0000000001", ticker="EXAMPLE")
    historical_records = parse_filings(history, cik="0000000001", ticker="EXAMPLE")
    cutoff = date(2025, 12, 31)

    assert select_latest_filings(recent_records, cik="0000000001", as_of=cutoff) == []
    selected = select_latest_filings(
        [*recent_records, *historical_records], cik="0000000001", as_of=cutoff
    )

    assert [record.accession_number for record in selected] == ["0000000001-25-000001"]
    assert selected[0].source_url.endswith("/000000000125000001/older-annual.htm")
