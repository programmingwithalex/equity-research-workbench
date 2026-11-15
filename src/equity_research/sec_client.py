"""Fetch SEC filing metadata through one pooled HTTPX client and request policy."""

import re
from math import isfinite
from threading import Lock
from time import monotonic, sleep
from typing import cast

import httpx

from equity_research.filings import Filing
from equity_research.sec_metadata import REQUIRED_COLUMNS, parse_filings


def _object(value: object) -> dict[str, object]:
    """Require a JSON object before reading SEC metadata fields.

    Args:
        value: Decoded JSON value at an object boundary.

    Returns:
        The object, without inventing defaults for missing metadata.

    Raises:
        ValueError: The value is not a JSON object.
    """
    if not isinstance(value, dict):
        raise ValueError("Expected a SEC metadata JSON object")
    return value


def _parse_batch(value: object, *, cik: str, ticker: str) -> list[Filing]:
    """Check wire column types, then reuse the existing record parser.

    Args:
        value: Recent or historical column object decoded from SEC JSON.
        cik: Canonical company identifier established by the caller.
        ticker: Display label to preserve in the resulting records.

    Returns:
        Typed references; date conversion and length checks belong to parse_filings.

    Raises:
        ValueError: Required columns are not string arrays, or parsing fails.
        KeyError: A required column is absent.
    """
    raw = _object(value)
    columns: dict[str, list[str]] = {}
    for name in REQUIRED_COLUMNS:
        values = raw[name]
        if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
            raise ValueError(f"SEC column {name} must be an array of strings")
        # The runtime checks above establish what the type checker cannot infer.
        columns[name] = cast(list[str], values)
    return parse_filings(columns, cik=cik, ticker=ticker)


class SecClient:
    """Coordinate metadata requests; the caller owns the HTTPX client's lifetime.

    Reuse one instance in an ingestion worker. Pacing is local to this instance;
    multiple workers need shared rate coordination before parallel SEC ingestion.
    """

    def __init__(
        self,
        http: httpx.Client,
        *,
        user_agent: str,
        timeout_seconds: float = 10.0,
        request_interval_seconds: float = 0.2,
    ) -> None:
        """Configure shared request identity, timeout, and pacing.

        Args:
            http: Pooled synchronous HTTPX client, closed by its owner.
            user_agent: Application name and contact required by SEC fair access.
            timeout_seconds: Network inactivity timeout, not a whole-fetch deadline.
            request_interval_seconds: Minimum gap between request starts; at least
                0.1 seconds. The default limits this instance to five starts/second.

        Raises:
            ValueError: Identity is blank, pacing is invalid, or timeout is not
                positive and finite.
        """
        if (
            not user_agent.strip()
            or not isfinite(request_interval_seconds)
            or request_interval_seconds < 0.1
        ):
            raise ValueError(
                "Provide a User-Agent and request spacing of at least 0.1s"
            )
        if not isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("Timeout must be positive and finite")
        self._http = http
        self._user_agent = user_agent
        self._timeout = httpx.Timeout(timeout_seconds)
        self._interval = request_interval_seconds
        self._next_request = 0.0
        self._lock = Lock()

    def _get_json(self, filename: str) -> dict[str, object]:
        """Fetch one SEC submissions file through the shared request policy.

        Args:
            filename: Company submissions or validated historical JSON filename.

        Returns:
            A decoded JSON object. HTTP, timeout, and JSON errors propagate.
        """
        # Keep pacing and the request together so a shared instance cannot burst.
        with self._lock:
            delay = self._next_request - monotonic()
            if delay > 0:
                sleep(delay)
            self._next_request = monotonic() + self._interval
            response = self._http.get(
                f"https://data.sec.gov/submissions/{filename}",
                headers={"User-Agent": self._user_agent, "Accept": "application/json"},
                timeout=self._timeout,
                follow_redirects=False,
            )
            response.raise_for_status()
            return _object(response.json())

    def fetch_filings(self, *, cik: str, ticker: str) -> list[Filing]:
        """Fetch recent filings and every historical batch listed by the SEC.

        Args:
            cik: Ten ASCII digits identifying the company, including leading zeros.
            ticker: Display label; company identity is verified using CIK.

        Returns:
            Combined references, without form/date filtering. Nothing is returned
            if any required request or parse fails. Completeness covers the files
            listed by the retrieved index, not an atomic historical SEC snapshot.

        Raises:
            ValueError: Identity, history filenames, or column shapes are invalid.
            KeyError: Required SEC metadata is missing.
            httpx.HTTPError: A request fails, times out, or receives a non-2xx status.
        """
        if re.fullmatch(r"[0-9]{10}", cik) is None:
            raise ValueError("CIK must contain ten ASCII digits")
        index = self._get_json(f"CIK{cik}.json")
        if str(index["cik"]).zfill(10) != cik:
            raise ValueError("SEC response CIK does not match the requested company")
        filings = _object(index["filings"])
        records = _parse_batch(filings["recent"], cik=cik, ticker=ticker)
        history = filings["files"]
        if not isinstance(history, list):
            raise ValueError("SEC historical-file index must be an array")
        for entry in history:
            filename = _object(entry)["name"]
            # Restrict metadata-controlled requests to this company's SEC files.
            if (
                not isinstance(filename, str)
                or re.fullmatch(rf"CIK{cik}-submissions-[0-9]+\.json", filename) is None
            ):
                raise ValueError(
                    "Invalid historical filename for the requested company"
                )
            records.extend(
                _parse_batch(self._get_json(filename), cik=cik, ticker=ticker)
            )
        return records
