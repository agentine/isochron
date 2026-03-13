"""Tests for the isodate compatibility shim."""

from __future__ import annotations

import datetime

from isochron.compat import (
    Duration,
    ISO8601Error,
    ParseError,
    UTC,
    date_isoformat,
    datetime_isoformat,
    duration_isoformat,
    parse_date,
    parse_datetime,
    parse_duration,
    parse_time,
    time_isoformat,
)


class TestCompat:
    def test_iso8601_error_is_parse_error_base(self) -> None:
        assert issubclass(ParseError, ISO8601Error)

    def test_parse_date(self) -> None:
        assert parse_date("2026-03-13") == datetime.date(2026, 3, 13)

    def test_parse_time(self) -> None:
        assert parse_time("14:30:00") == datetime.time(14, 30, 0)

    def test_parse_datetime(self) -> None:
        dt = parse_datetime("2026-03-13T14:30:00Z")
        assert isinstance(dt, datetime.datetime)

    def test_parse_duration(self) -> None:
        d = parse_duration("P1Y2M")
        assert isinstance(d, Duration)

    def test_date_isoformat(self) -> None:
        assert date_isoformat(datetime.date(2026, 1, 1)) == "2026-01-01"

    def test_datetime_isoformat(self) -> None:
        dt = datetime.datetime(2026, 3, 13, 14, 30, 0, tzinfo=datetime.timezone.utc)
        assert datetime_isoformat(dt) == "2026-03-13T14:30:00Z"

    def test_duration_isoformat(self) -> None:
        assert duration_isoformat(datetime.timedelta(days=7)) == "P1W"

    def test_time_isoformat(self) -> None:
        assert time_isoformat(datetime.time(14, 30, 0)) == "14:30:00"

    def test_utc(self) -> None:
        assert UTC is datetime.timezone.utc
