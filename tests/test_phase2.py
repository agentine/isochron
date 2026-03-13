"""Phase 2 unit tests — formatting and intervals."""

from __future__ import annotations

import datetime

import pytest

from isochron import (
    Duration,
    FixedOffset,
    Interval,
    ParseError,
    RecurringInterval,
    UTC,
    format_date,
    format_datetime,
    format_duration,
    format_time,
    parse_interval,
    parse_recurring,
    strftime,
)


# ---- format_date ------------------------------------------------------------


class TestFormatDate:
    def test_basic(self) -> None:
        assert format_date(datetime.date(2026, 3, 13)) == "2026-03-13"

    def test_new_year(self) -> None:
        assert format_date(datetime.date(2026, 1, 1)) == "2026-01-01"


# ---- format_time ------------------------------------------------------------


class TestFormatTime:
    def test_basic(self) -> None:
        assert format_time(datetime.time(14, 30, 0)) == "14:30:00"

    def test_utc_outputs_z(self) -> None:
        t = datetime.time(14, 30, 0, tzinfo=datetime.timezone.utc)
        assert format_time(t) == "14:30:00Z"

    def test_fixed_offset(self) -> None:
        tz = FixedOffset(hours=5, minutes=30)
        t = datetime.time(14, 30, 0, tzinfo=tz)
        assert format_time(t) == "14:30:00+05:30"

    def test_negative_offset(self) -> None:
        tz = FixedOffset(hours=-8)
        t = datetime.time(14, 30, 0, tzinfo=tz)
        assert format_time(t) == "14:30:00-08:00"

    def test_microseconds(self) -> None:
        t = datetime.time(14, 30, 0, 123000)
        assert format_time(t) == "14:30:00.123"

    def test_naive(self) -> None:
        assert format_time(datetime.time(0, 0, 0)) == "00:00:00"


# ---- format_datetime --------------------------------------------------------


class TestFormatDatetime:
    def test_basic(self) -> None:
        dt = datetime.datetime(2026, 3, 13, 14, 30, 0)
        assert format_datetime(dt) == "2026-03-13T14:30:00"

    def test_utc_z(self) -> None:
        dt = datetime.datetime(2026, 3, 13, 14, 30, 0, tzinfo=datetime.timezone.utc)
        assert format_datetime(dt) == "2026-03-13T14:30:00Z"

    def test_offset(self) -> None:
        tz = FixedOffset(hours=1)
        dt = datetime.datetime(2026, 3, 13, 14, 30, 0, tzinfo=tz)
        assert format_datetime(dt) == "2026-03-13T14:30:00+01:00"


# ---- format_duration --------------------------------------------------------


class TestFormatDuration:
    def test_duration(self) -> None:
        d = Duration(years=1, months=2, days=3, seconds=14706)
        assert format_duration(d) == "P1Y2M3DT4H5M6S"

    def test_timedelta_days(self) -> None:
        assert format_duration(datetime.timedelta(days=30)) == "P30D"

    def test_timedelta_weeks(self) -> None:
        assert format_duration(datetime.timedelta(weeks=3)) == "P3W"

    def test_timedelta_time(self) -> None:
        assert format_duration(datetime.timedelta(hours=1, minutes=30)) == "PT1H30M"

    def test_zero(self) -> None:
        assert format_duration(datetime.timedelta(0)) == "P0D"

    def test_negative_timedelta(self) -> None:
        result = format_duration(datetime.timedelta(days=-1))
        assert result.startswith("-P")

    def test_timedelta_with_microseconds(self) -> None:
        td = datetime.timedelta(seconds=1, microseconds=500000)
        result = format_duration(td)
        assert "1.5S" in result


# ---- strftime ---------------------------------------------------------------


class TestStrftime:
    def test_basic(self) -> None:
        dt = datetime.date(2026, 3, 13)
        assert strftime(dt, "%Y-%m-%d") == "2026-03-13"

    def test_iso_year(self) -> None:
        dt = datetime.date(2026, 3, 13)
        result = strftime(dt, "%G")
        assert result == "2026"

    def test_iso_week(self) -> None:
        dt = datetime.date(2026, 3, 13)
        result = strftime(dt, "%V")
        # 2026-03-13 is in ISO week 11
        assert result == "11"

    def test_iso_weekday(self) -> None:
        dt = datetime.date(2026, 3, 13)  # Friday
        result = strftime(dt, "%u")
        assert result == "5"

    def test_colon_z(self) -> None:
        tz = FixedOffset(hours=5, minutes=30)
        dt = datetime.datetime(2026, 3, 13, 14, 30, 0, tzinfo=tz)
        result = strftime(dt, "%:z")
        assert result == "+05:30"

    def test_colon_z_naive(self) -> None:
        dt = datetime.date(2026, 3, 13)
        result = strftime(dt, "%:z")
        assert result == ""

    def test_combined(self) -> None:
        dt = datetime.date(2026, 3, 13)
        result = strftime(dt, "%G-W%V-%u")
        assert result == "2026-W11-5"


# ---- Interval parsing ------------------------------------------------------


class TestParseInterval:
    def test_start_end(self) -> None:
        iv = parse_interval("2026-01-01/2026-12-31")
        assert iv.start == datetime.date(2026, 1, 1)
        assert iv.end == datetime.date(2026, 12, 31)
        assert iv.duration is None

    def test_start_duration(self) -> None:
        iv = parse_interval("2026-01-01/P1Y")
        assert iv.start == datetime.date(2026, 1, 1)
        assert iv.end is None
        assert isinstance(iv.duration, Duration)

    def test_duration_end(self) -> None:
        iv = parse_interval("P1M/2026-03-13")
        assert iv.start is None
        assert iv.end == datetime.date(2026, 3, 13)

    def test_datetime_start_end(self) -> None:
        iv = parse_interval("2026-01-01T00:00:00Z/2026-12-31T23:59:59Z")
        assert isinstance(iv.start, datetime.datetime)
        assert isinstance(iv.end, datetime.datetime)

    def test_invalid_no_slash(self) -> None:
        with pytest.raises(ParseError):
            parse_interval("2026-01-01")

    def test_invalid_both_durations(self) -> None:
        with pytest.raises(ParseError):
            parse_interval("P1Y/P2M")


# ---- Recurring interval parsing --------------------------------------------


class TestParseRecurring:
    def test_finite(self) -> None:
        r = parse_recurring("R3/2026-01-01/P1M")
        assert r.recurrences == 3
        assert r.interval.start == datetime.date(2026, 1, 1)

    def test_infinite(self) -> None:
        r = parse_recurring("R/2026-01-01/P1M")
        assert r.recurrences is None

    def test_iteration_finite(self) -> None:
        r = parse_recurring("R3/2026-01-01/P7D")
        dates = list(r)
        assert len(dates) == 3
        assert dates[0] == datetime.date(2026, 1, 1)
        assert dates[1] == datetime.date(2026, 1, 8)
        assert dates[2] == datetime.date(2026, 1, 15)

    def test_invalid_no_r(self) -> None:
        with pytest.raises(ParseError):
            parse_recurring("3/2026-01-01/P1M")

    def test_invalid_no_slash(self) -> None:
        with pytest.raises(ParseError):
            parse_recurring("R3")


# ---- Interval class --------------------------------------------------------


class TestInterval:
    def test_frozen(self) -> None:
        iv = Interval(start=datetime.date(2026, 1, 1), end=None, duration=None)
        with pytest.raises(AttributeError):
            iv.start = datetime.date(2026, 2, 1)  # type: ignore[misc]


class TestRecurringInterval:
    def test_iteration_with_duration(self) -> None:
        iv = Interval(
            start=datetime.date(2026, 1, 1),
            end=None,
            duration=Duration(months=1),
        )
        r = RecurringInterval(recurrences=3, interval=iv)
        dates = list(r)
        assert len(dates) == 3
        assert dates[0] == datetime.date(2026, 1, 1)
        assert dates[1] == datetime.date(2026, 2, 1)
        assert dates[2] == datetime.date(2026, 3, 1)

    def test_iteration_no_start_raises(self) -> None:
        iv = Interval(start=None, end=datetime.date(2026, 12, 31), duration=Duration(months=1))
        r = RecurringInterval(recurrences=3, interval=iv)
        with pytest.raises(ValueError):
            list(r)
