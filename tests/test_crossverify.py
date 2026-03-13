"""Cross-verification tests: isochron vs isodate.

Parse with isodate, verify with isochron and vice versa.
"""

from __future__ import annotations

import datetime

import isodate  # type: ignore[import-untyped]
import pytest

from isochron import (
    Duration,
    format_date,
    format_datetime,
    format_duration,
    format_time,
    parse_date,
    parse_datetime,
    parse_duration,
    parse_time,
)


class TestParseDateCross:
    """Parse dates with both libraries and compare."""

    @pytest.mark.parametrize(
        "s",
        [
            "2026-03-13",
            "2000-01-01",
            "1999-12-31",
            "2026-02-28",
            "2024-02-29",  # leap year
            "20260313",    # compact form
        ],
    )
    def test_parse_date_equivalence(self, s: str) -> None:
        iso_result = isodate.parse_date(s)
        our_result = parse_date(s)
        assert iso_result == our_result, f"Mismatch for {s!r}: isodate={iso_result} isochron={our_result}"


class TestParseTimeCross:
    """Parse times with both libraries and compare."""

    @pytest.mark.parametrize(
        "s",
        [
            "14:30:00",
            "00:00:00",
            "23:59:59",
            "14:30:00Z",
            "14:30:00+05:30",
            "14:30:00-08:00",
        ],
    )
    def test_parse_time_equivalence(self, s: str) -> None:
        iso_result = isodate.parse_time(s)
        our_result = parse_time(s)
        assert iso_result == our_result, f"Mismatch for {s!r}: isodate={iso_result} isochron={our_result}"


class TestParseDatetimeCross:
    """Parse datetimes with both libraries and compare."""

    @pytest.mark.parametrize(
        "s",
        [
            "2026-03-13T14:30:00",
            "2026-03-13T14:30:00Z",
            "2026-03-13T14:30:00+01:00",
            "2026-03-13T14:30:00-05:00",
            "2000-01-01T00:00:00Z",
        ],
    )
    def test_parse_datetime_equivalence(self, s: str) -> None:
        iso_result = isodate.parse_datetime(s)
        our_result = parse_datetime(s)
        assert iso_result == our_result, f"Mismatch for {s!r}: isodate={iso_result} isochron={our_result}"


class TestParseDurationCross:
    """Parse durations with both libraries and compare."""

    @pytest.mark.parametrize(
        "s",
        [
            "P1Y",
            "P1M",
            "P1D",
            "PT1H",
            "PT1M",
            "PT1S",
            "P1Y2M3DT4H5M6S",
            "P1W",
            "PT0S",
            "-P1Y",
        ],
    )
    def test_parse_duration_equivalence(self, s: str) -> None:
        iso_result = isodate.parse_duration(s)
        our_result = parse_duration(s)

        # isodate returns either timedelta or isodate.Duration
        if isinstance(iso_result, datetime.timedelta) and isinstance(our_result, datetime.timedelta):
            assert iso_result == our_result, f"Mismatch for {s!r}"
        elif isinstance(our_result, Duration):
            # Compare component-wise with isodate Duration
            assert our_result.years == iso_result.years, f"years mismatch for {s!r}"  # type: ignore[union-attr]
            assert our_result.months == iso_result.months, f"months mismatch for {s!r}"  # type: ignore[union-attr]
            assert our_result.days == iso_result.tdelta.days, f"days mismatch for {s!r}"  # type: ignore[union-attr]
            assert our_result.seconds == iso_result.tdelta.seconds, f"seconds mismatch for {s!r}"  # type: ignore[union-attr]


class TestFormatCross:
    """Format with isochron, parse back with isodate."""

    def test_format_date_roundtrip(self) -> None:
        d = datetime.date(2026, 3, 13)
        formatted = format_date(d)
        parsed = isodate.parse_date(formatted)
        assert d == parsed

    def test_format_time_roundtrip(self) -> None:
        t = datetime.time(14, 30, 0, tzinfo=datetime.timezone.utc)
        formatted = format_time(t)
        parsed = isodate.parse_time(formatted)
        assert t == parsed

    def test_format_datetime_roundtrip(self) -> None:
        dt = datetime.datetime(2026, 3, 13, 14, 30, 0, tzinfo=datetime.timezone.utc)
        formatted = format_datetime(dt)
        parsed = isodate.parse_datetime(formatted)
        assert dt == parsed

    def test_format_duration_roundtrip_timedelta(self) -> None:
        td = datetime.timedelta(days=365, hours=5, minutes=30)
        formatted = format_duration(td)
        parsed = isodate.parse_duration(formatted)
        assert isinstance(parsed, datetime.timedelta)
        assert td == parsed

    def test_format_duration_roundtrip_weeks(self) -> None:
        td = datetime.timedelta(weeks=3)
        formatted = format_duration(td)
        assert formatted == "P3W"
        parsed = isodate.parse_duration(formatted)
        assert isinstance(parsed, datetime.timedelta)
        assert td == parsed


class TestIsodateFormatIschronParse:
    """Format with isodate, parse with isochron."""

    def test_date(self) -> None:
        d = datetime.date(2026, 6, 15)
        formatted = isodate.date_isoformat(d)
        parsed = parse_date(formatted)
        assert d == parsed

    def test_datetime(self) -> None:
        dt = datetime.datetime(2026, 6, 15, 10, 0, 0, tzinfo=datetime.timezone.utc)
        formatted = isodate.datetime_isoformat(dt)
        parsed = parse_datetime(formatted)
        assert dt == parsed

    def test_duration(self) -> None:
        td = datetime.timedelta(days=30, seconds=3600)
        formatted = isodate.duration_isoformat(td)
        parsed = parse_duration(formatted)
        assert isinstance(parsed, datetime.timedelta)
        assert td == parsed
