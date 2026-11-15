"""Test real HTTPX request construction with synthetic, in-process SEC responses."""

from collections.abc import Iterator
from datetime import date

import httpx
import pytest

from equity_research import sec_client
from equity_research.filings import select_latest_filings
from equity_research.sec_client import SecClient

CIK = "0000000001"
MAIN = f"/submissions/CIK{CIK}.json"
HISTORY = [f"/submissions/CIK{CIK}-submissions-{number:03}.json" for number in (1, 2)]
AGENT = "equity-research-test contact@example.com"


def _index(columns: object, names: list[str]) -> dict[str, object]:
    """Build the company envelope independently from historical batch payloads.

    Args:
        columns: Recent wire columns, including malformed values in negative tests.
        names: Historical filenames advertised by the synthetic index.

    Returns:
        SEC-shaped company metadata with a numeric CIK to exercise normalization.
    """
    return {
        "cik": 1,
        "filings": {"recent": columns, "files": [{"name": n} for n in names]},
    }


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Replace only the SEC module's clock/sleep bindings with virtual time.

    Args:
        monkeypatch: Pytest fixture that restores module bindings after each test.

    Returns:
        Successive virtual times after requested waits; no test actually sleeps.
    """
    times = [100.0]
    monkeypatch.setattr(sec_client, "monotonic", lambda: times[-1])
    monkeypatch.setattr(
        sec_client, "sleep", lambda delay: times.append(times[-1] + delay)
    )
    return times


@pytest.fixture
def responses(
    columns: dict[str, list[str]],
) -> dict[str, httpx.Response | httpx.HTTPError]:
    """Provide recent metadata and two distinct older filing batches.

    Args:
        columns: Shared synthetic recent columns from conftest.py.

    Returns:
        In-memory responses that tests can replace with status or transport errors.
    """
    older = {
        "accessionNumber": ["0000000001-25-000001"],
        "form": ["10-K"],
        "filingDate": ["2025-02-14"],
        "reportDate": ["2024-12-31"],
        "primaryDocument": ["older-annual.htm"],
    }
    oldest = {
        "accessionNumber": ["0000000001-24-000001"],
        "form": ["10-Q"],
        "filingDate": ["2024-11-01"],
        "reportDate": ["2024-09-30"],
        "primaryDocument": ["oldest-quarterly.htm"],
    }
    return {
        MAIN: httpx.Response(
            200, json=_index(columns, [p.rsplit("/", 1)[1] for p in HISTORY])
        ),
        HISTORY[0]: httpx.Response(200, json=older),
        HISTORY[1]: httpx.Response(200, json=oldest),
    }


@pytest.fixture
def requests() -> list[httpx.Request]:
    """Collect actual HTTPX requests for policy and coverage assertions."""
    return []


@pytest.fixture
def http(
    responses: dict[str, httpx.Response | httpx.HTTPError],
    requests: list[httpx.Request],
    clock: list[float],
) -> Iterator[httpx.Client]:
    """Own a real HTTPX client whose transport cannot access the network.

    Args:
        responses: Synthetic responses or exceptions indexed by request path.
        requests: Request log populated by the mock transport.
        clock: Activate virtual pacing for every test using this fixture.

    Yields:
        A pooled HTTPX client, closed automatically when the test finishes.
    """

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        result = responses[request.url.path]
        if isinstance(result, httpx.HTTPError):
            raise result
        return result

    with httpx.Client(transport=httpx.MockTransport(handle), trust_env=False) as client:
        yield client


def test_complete_history_reuses_policy_and_existing_selector(
    http: httpx.Client, requests: list[httpx.Request], clock: list[float]
) -> None:
    """Fetch every advertised batch and preserve older evidence and request policy."""
    records = SecClient(http, user_agent=AGENT).fetch_filings(cik=CIK, ticker="EXAMPLE")

    assert len(records) == 4
    assert [request.url.path for request in requests] == [MAIN, *HISTORY]
    assert all(request.url.host == "data.sec.gov" for request in requests)
    assert all(request.headers["user-agent"] == AGENT for request in requests)
    assert all(request.extensions["timeout"]["read"] == 10.0 for request in requests)
    assert clock == pytest.approx([100.0, 100.2, 100.4])
    selected = select_latest_filings(records, cik=CIK, as_of=date(2025, 12, 31))
    assert [record.accession_number for record in selected] == [
        "0000000001-25-000001",
        "0000000001-24-000001",
    ]


def test_empty_history_index_uses_only_recent_records(
    http: httpx.Client,
    responses: dict[str, httpx.Response | httpx.HTTPError],
    requests: list[httpx.Request],
    columns: dict[str, list[str]],
) -> None:
    """Respect an explicitly empty index without guessing older filenames."""
    responses[MAIN] = httpx.Response(200, json=_index(columns, []))
    assert (
        len(SecClient(http, user_agent=AGENT).fetch_filings(cik=CIK, ticker="EXAMPLE"))
        == 2
    )
    assert len(requests) == 1


@pytest.mark.parametrize("status", [429, 503])
def test_history_http_error_aborts_without_partial_result_or_hidden_retry(
    http: httpx.Client,
    responses: dict[str, httpx.Response | httpx.HTTPError],
    requests: list[httpx.Request],
    status: int,
) -> None:
    """Never present recent plus one successful history batch as complete evidence."""
    responses[HISTORY[1]] = httpx.Response(status)
    with pytest.raises(httpx.HTTPStatusError):
        SecClient(http, user_agent=AGENT).fetch_filings(cik=CIK, ticker="EXAMPLE")
    assert len(requests) == 3


def test_timeout_stops_history_traversal(
    http: httpx.Client,
    responses: dict[str, httpx.Response | httpx.HTTPError],
    requests: list[httpx.Request],
) -> None:
    """Propagate transport failure and stop requesting later files."""
    responses[HISTORY[0]] = httpx.ReadTimeout("Synthetic SEC timeout")
    with pytest.raises(httpx.ReadTimeout):
        SecClient(http, user_agent=AGENT).fetch_filings(cik=CIK, ticker="EXAMPLE")
    assert len(requests) == 2


@pytest.mark.parametrize(
    "filename",
    [
        "https://example.com/history.json",
        "../history.json",
        "CIK0000000002-submissions-001.json",
    ],
)
def test_untrusted_history_names_cannot_change_host_or_company(
    http: httpx.Client,
    responses: dict[str, httpx.Response | httpx.HTTPError],
    requests: list[httpx.Request],
    columns: dict[str, list[str]],
    filename: str,
) -> None:
    """Reject metadata-controlled destinations before issuing a history request."""
    responses[MAIN] = httpx.Response(200, json=_index(columns, [filename]))
    with pytest.raises(ValueError, match="historical filename"):
        SecClient(http, user_agent=AGENT).fetch_filings(cik=CIK, ticker="EXAMPLE")
    assert len(requests) == 1


def test_company_identity_mismatch_is_rejected(
    http: httpx.Client,
    responses: dict[str, httpx.Response | httpx.HTTPError],
    requests: list[httpx.Request],
    columns: dict[str, list[str]],
) -> None:
    """Keep a successful HTTP response from attaching another company's evidence."""
    wrong_company = _index(columns, [])
    wrong_company["cik"] = 2
    responses[MAIN] = httpx.Response(200, json=wrong_company)
    with pytest.raises(ValueError, match="CIK does not match"):
        SecClient(http, user_agent=AGENT).fetch_filings(cik=CIK, ticker="EXAMPLE")
    assert len(requests) == 1


def test_redirect_does_not_escape_the_sec_origin(
    http: httpx.Client,
    responses: dict[str, httpx.Response | httpx.HTTPError],
    requests: list[httpx.Request],
) -> None:
    """Enforce SEC policy even if the supplied HTTPX client normally follows redirects."""
    http.follow_redirects = True
    responses[MAIN] = httpx.Response(
        302, headers={"Location": "https://example.com/outside"}
    )
    with pytest.raises(httpx.HTTPStatusError) as error:
        SecClient(http, user_agent=AGENT).fetch_filings(cik=CIK, ticker="EXAMPLE")
    assert error.value.response.status_code == 302
    assert len(requests) == 1


@pytest.mark.parametrize("interval", [0.0, float("nan"), float("inf")])
def test_invalid_pacing_is_rejected(http: httpx.Client, interval: float) -> None:
    """Prevent configuration from silently disabling the SEC request ceiling."""
    with pytest.raises(ValueError, match="spacing"):
        SecClient(http, user_agent=AGENT, request_interval_seconds=interval)


@pytest.mark.parametrize("timeout", [0.0, float("nan"), float("inf")])
def test_timeout_cannot_be_disabled_by_invalid_configuration(
    http: httpx.Client, timeout: float
) -> None:
    """Keep network waits bounded by a valid inactivity timeout."""
    with pytest.raises(ValueError, match="Timeout"):
        SecClient(http, user_agent=AGENT, timeout_seconds=timeout)


@pytest.mark.parametrize("bad_column", ["not-an-array", [17]])
def test_wire_column_types_are_checked_before_parsing(
    http: httpx.Client,
    responses: dict[str, httpx.Response | httpx.HTTPError],
    columns: dict[str, list[str]],
    bad_column: object,
) -> None:
    """Runtime JSON checks prevent type hints from becoming a false validation claim."""
    malformed: dict[str, object] = dict(columns)
    malformed["form"] = bad_column
    responses[MAIN] = httpx.Response(200, json=_index(malformed, []))
    with pytest.raises(ValueError, match="array of strings"):
        SecClient(http, user_agent=AGENT).fetch_filings(cik=CIK, ticker="EXAMPLE")
