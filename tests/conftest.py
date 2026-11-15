"""Share synthetic SEC wire data across parser and network-boundary tests."""

import pytest


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
