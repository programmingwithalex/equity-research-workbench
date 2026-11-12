"""Select filing references that were public by a research-date cutoff."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import Final

SUPPORTED_FORMS: Final = ("10-K", "10-Q")


@dataclass(frozen=True)
class Filing:
    """Keep a filing's identity, dates, and source together during selection.

    Attributes:
        ticker: Display ticker supplied with the filing metadata.
        cik: Canonical ten-digit SEC company identifier. Selection uses this
            identity rather than assuming a ticker permanently identifies a firm.
        form: SEC form name; this can include forms the selector will exclude.
        accession_number: Identifier of this particular SEC submission.
        filing_date: Public filing date used for historical eligibility.
        report_date: End of the financial period covered, or None if unavailable.
            This date does not establish when the filing became public.
        source_url: Original filing URL, retained for later downloads and citations.
    """

    ticker: str
    cik: str
    form: str
    accession_number: str
    filing_date: date
    report_date: date | None
    source_url: str


def select_latest_filings(
    filings: Iterable[Filing], *, cik: str, as_of: date
) -> list[Filing]:
    """Select the latest eligible original 10-K and 10-Q for one company.

    Args:
        filings: Already parsed filing references, in any order. The selector
            assumes their company identifiers and dates are valid.
        cik: Canonical ten-digit SEC identifier of the company to select.
        as_of: Inclusive public filing-date cutoff, at day precision.

    Returns:
        Original references ordered 10-K then 10-Q, omitting either missing form.
        Other companies, filings after the cutoff, amendments, and other forms
        are excluded. Reporting periods are preserved but do not drive selection.
        Same-day ties use the accession number as a reproducible tie-breaker;
        this does not establish intraday publication order. Input is not mutated.
    """
    latest: dict[str, Filing] = {}
    for filing in filings:
        if (
            filing.cik != cik
            or filing.form not in SUPPORTED_FORMS
            or filing.filing_date > as_of
        ):
            continue

        previous = latest.get(filing.form)
        # Publication eligibility and recency are independent of report-period end.
        if previous is None or (filing.filing_date, filing.accession_number) > (
            previous.filing_date,
            previous.accession_number,
        ):
            latest[filing.form] = filing

    return [latest[form] for form in SUPPORTED_FORMS if form in latest]
