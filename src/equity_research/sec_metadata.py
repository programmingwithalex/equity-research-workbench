"""Convert SEC submissions metadata into filing references without network I/O."""

from collections.abc import Mapping, Sequence
from datetime import date
from urllib.parse import quote

from equity_research.filings import Filing


def parse_filings(
    columns: Mapping[str, Sequence[str]], *, cik: str, ticker: str
) -> list[Filing]:
    """Assemble SEC column arrays into records for the existing filing selector.

    Args:
        columns: The ``filings.recent`` object from a submissions response, or
            the equivalent top-level columns from an older-history response.
            Required columns are accessionNumber, form, filingDate, reportDate,
            and primaryDocument. Dates use ISO format; an empty reportDate means
            the reporting period is unavailable. Unused columns are ignored.
        cik: Canonical ten-digit company identifier supplied by the caller.
        ticker: Display ticker supplied by the caller, including for history
            responses that do not contain company identity.

    Returns:
        Filing references in input order, retaining all forms and dates. The
        input is unchanged. This function neither fetches documents nor proves
        that the supplied metadata covers the company's complete history.

    Raises:
        KeyError: A required column is missing.
        ValueError: Required columns differ in length, a date cannot be parsed,
            or the supplied CIK is not numeric.
    """
    # SEC arrays are parallel: the same position in every column is one filing.
    # Strict pairing prevents a shorter column from silently dropping records.
    rows = zip(
        columns["accessionNumber"],
        columns["form"],
        columns["filingDate"],
        columns["reportDate"],
        columns["primaryDocument"],
        strict=True,
    )
    filings: list[Filing] = []
    for accession, form, filed, reported, primary_document in rows:
        # SEC archive directories omit CIK padding and accession-number dashes.
        # Escape the document name so URL punctuation remains part of the name.
        source_url = (
            f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
            f"{accession.replace('-', '')}/{quote(primary_document, safe='')}"
        )
        filings.append(
            Filing(
                ticker=ticker,
                cik=cik,
                form=form,
                accession_number=accession,
                filing_date=date.fromisoformat(filed),
                # Unknown reporting periods stay unknown; do not invent a date.
                report_date=date.fromisoformat(reported) if reported else None,
                source_url=source_url,
            )
        )
    return filings
