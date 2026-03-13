"""Phase 1 unit tests — core types and parsing."""

from __future__ import annotations

import datetime

import pytest

from isochron import (
    Duration,
    FixedOffset,
    ISO8601Error,
    ParseError,
    FormatError,
    UTC,
    parse_date,
    parse_datetime,
    parse_duration,
    parse_time,
    parse_timezone,
)


# ---- Error hierarchy -------------------------------------------------------


class TestErrors:
    def test_parse_error_is_iso8601_error(self) -> None:
        assert issubclass(ParseError, ISO8601Error)

    def test_format_error_is_iso8601_error(self) -> None:
        assert issubclass(FormatError, ISO8601Error)

    def test_iso8601_error_is_value_error(self) -> None:
        assert issubclass(ISO8601Error, ValueError)

    def test_parse_error_with_string(self) -> None:
        e = ParseError("bad input", string="xyz")
        assert "xyz" in str(e)
        assert e.string == "xyz"

    def test_parse_error_with_position(self) -> None:
        e = ParseError("bad", string="abc", position=2)
        assert e.position == 2
        assert "position 2" in str(e)


# ---- Timezone classes -------------------------------------------------------


class TestTimezones:
    def test_utc_is_stdlib(self) -> None:
        assert UTC is datetime.timezone.utc

    def test_fixed_offset_positive(self) -> None:
        tz = FixedOffset(hours=5, minutes=30)
        assert tz.utcoffset(None) == datetime.timedelta(hours=5, minutes=30)
        assert tz.dst(None) == datetime.timedelta(0)
        assert "UTC+05:30" in tz.tzname(None)

    def test_fixed_offset_negative(self) -> None:
        tz = FixedOffset(hours=-8)
        assert tz.utcoffset(None) == datetime.timedelta(hours=-8)

    def test_fixed_offset_zero(self) -> None:
        tz = FixedOffset()
        assert tz.total_minutes == 0

    def test_fixed_offset_equality(self) -> None:
        a = FixedOffset(hours=1)
        b = FixedOffset(hours=1)
        assert a == b
        assert hash(a) == hash(b)

    def test_fixed_offset_neq(self) -> None:
        assert FixedOffset(hours=1) != FixedOffset(hours=2)

    def test_fixed_offset_repr(self) -> None:
        tz = FixedOffset(hours=3, minutes=30)
        assert "FixedOffset" in repr(tz)

    def test_fixed_offset_eq_stdlib_timezone(self) -> None:
        tz = FixedOffset(hours=5)
        stdlib = datetime.timezone(datetime.timedelta(hours=5))
        assert tz == stdlib


# ---- Timezone parsing -------------------------------------------------------


class TestParseTz:
    def test_z(self) -> None:
        assert parse_timezone("Z") is UTC

    def test_positive_hhmm(self) -> None:
        tz = parse_timezone("+05:30")
        assert tz.utcoffset(None) == datetime.timedelta(hours=5, minutes=30)

    def test_positive_compact(self) -> None:
        tz = parse_timezone("+0530")
        assert tz.utcoffset(None) == datetime.timedelta(hours=5, minutes=30)

    def test_positive_hh_only(self) -> None:
        tz = parse_timezone("+05")
        assert tz.utcoffset(None) == datetime.timedelta(hours=5)

    def test_negative(self) -> None:
        tz = parse_timezone("-08:00")
        assert tz.utcoffset(None) == datetime.timedelta(hours=-8)

    def test_invalid(self) -> None:
        with pytest.raises(ParseError):
            parse_timezone("ABC")


# ---- Duration ---------------------------------------------------------------


class TestDuration:
    def test_construction(self) -> None:
        d = Duration(years=1, months=2, days=3, seconds=4, microseconds=5)
        assert d.years == 1
        assert d.months == 2
        assert d.days == 3
        assert d.seconds == 4
        assert d.microseconds == 5

    def test_is_fixed_true(self) -> None:
        assert Duration(days=30).is_fixed is True

    def test_is_fixed_false(self) -> None:
        assert Duration(years=1).is_fixed is False

    def test_to_timedelta_fixed(self) -> None:
        d = Duration(days=10, seconds=3600)
        td = d.to_timedelta()
        assert td == datetime.timedelta(days=10, seconds=3600)

    def test_to_timedelta_needs_reference(self) -> None:
        d = Duration(years=1)
        with pytest.raises(ValueError, match="reference"):
            d.to_timedelta()

    def test_to_timedelta_with_reference(self) -> None:
        d = Duration(months=1)
        td = d.to_timedelta(reference=datetime.date(2026, 1, 31))
        # Jan 31 + 1 month = Feb 28 (2026 is not a leap year) = 28 days
        assert td == datetime.timedelta(days=28)

    def test_total_seconds_fixed(self) -> None:
        d = Duration(days=1)
        assert d.total_seconds() == 86400.0

    def test_total_seconds_non_fixed_raises(self) -> None:
        d = Duration(years=1)
        with pytest.raises(ValueError):
            d.total_seconds()

    def test_add_durations(self) -> None:
        a = Duration(years=1, days=10)
        b = Duration(months=2, days=5)
        c = a + b
        assert c.years == 1
        assert c.months == 2
        assert c.days == 15

    def test_add_timedelta(self) -> None:
        d = Duration(years=1)
        result = d + datetime.timedelta(days=5)
        assert result.years == 1
        assert result.days == 5

    def test_neg(self) -> None:
        d = Duration(years=1, months=2)
        neg = -d
        assert neg.years == -1
        assert neg.months == -2

    def test_mul(self) -> None:
        d = Duration(months=3)
        assert (d * 4).months == 12

    def test_rmul(self) -> None:
        d = Duration(days=7)
        assert (2 * d).days == 14

    def test_bool_empty(self) -> None:
        assert not Duration()

    def test_bool_nonempty(self) -> None:
        assert Duration(days=1)

    def test_repr(self) -> None:
        d = Duration(years=1, days=5)
        assert "years=1" in repr(d)
        assert "days=5" in repr(d)

    def test_str_format(self) -> None:
        d = Duration(years=1, months=2, days=3, seconds=14706)
        assert str(d) == "P1Y2M3DT4H5M6S"

    def test_hashable(self) -> None:
        d = Duration(years=1)
        {d}  # should not raise

    def test_add_to_date(self) -> None:
        d = Duration(months=1)
        result = d + datetime.date(2026, 1, 31)
        assert result == datetime.date(2026, 2, 28)

    def test_add_to_datetime(self) -> None:
        d = Duration(months=1)
        dt = datetime.datetime(2026, 1, 31, 12, 0)
        result = d + dt
        assert result == datetime.datetime(2026, 2, 28, 12, 0)


# ---- Date parsing -----------------------------------------------------------


class TestParseDate:
    def test_calendar(self) -> None:
        assert parse_date("2026-03-13") == datetime.date(2026, 3, 13)

    def test_calendar_compact(self) -> None:
        assert parse_date("20260313") == datetime.date(2026, 3, 13)

    def test_ordinal(self) -> None:
        assert parse_date("2026-072") == datetime.date(2026, 3, 13)

    def test_ordinal_compact(self) -> None:
        assert parse_date("2026072") == datetime.date(2026, 3, 13)

    def test_week_date(self) -> None:
        d = parse_date("2026-W11-5")
        assert d == datetime.date(2026, 3, 13)

    def test_week_date_compact(self) -> None:
        d = parse_date("2026W115")
        assert d == datetime.date(2026, 3, 13)

    def test_week_date_no_day(self) -> None:
        d = parse_date("2026-W11")
        assert d.isocalendar()[1] == 11

    def test_invalid(self) -> None:
        with pytest.raises(ParseError):
            parse_date("not-a-date")

    def test_invalid_month(self) -> None:
        with pytest.raises(ParseError):
            parse_date("2026-13-01")

    def test_invalid_day(self) -> None:
        with pytest.raises(ParseError):
            parse_date("2026-02-30")


# ---- Time parsing -----------------------------------------------------------


class TestParseTime:
    def test_basic(self) -> None:
        assert parse_time("14:30:00") == datetime.time(14, 30, 0)

    def test_compact(self) -> None:
        assert parse_time("143000") == datetime.time(14, 30, 0)

    def test_fractional(self) -> None:
        t = parse_time("14:30:00.123456")
        assert t.microsecond == 123456

    def test_fractional_short(self) -> None:
        t = parse_time("14:30:00.5")
        assert t.microsecond == 500000

    def test_t_prefix(self) -> None:
        assert parse_time("T14:30:00") == datetime.time(14, 30, 0)

    def test_midnight_24(self) -> None:
        assert parse_time("24:00:00") == datetime.time(0, 0, 0)

    def test_midnight_24_invalid(self) -> None:
        with pytest.raises(ParseError):
            parse_time("24:01:00")

    def test_with_utc(self) -> None:
        t = parse_time("14:30:00Z")
        assert t.tzinfo is not None
        assert t.utcoffset() == datetime.timedelta(0)

    def test_with_offset(self) -> None:
        t = parse_time("14:30:00+05:30")
        assert t.utcoffset() == datetime.timedelta(hours=5, minutes=30)

    def test_second_60_clamped(self) -> None:
        # isodate #87 fix: 59.99999 rounding to 60
        t = parse_time("14:30:60")
        assert t.second == 59
        assert t.microsecond == 999999

    def test_invalid(self) -> None:
        with pytest.raises(ParseError):
            parse_time("invalid")

    def test_hhmm_only(self) -> None:
        assert parse_time("14:30") == datetime.time(14, 30, 0)

    def test_hh_only(self) -> None:
        assert parse_time("14") == datetime.time(14, 0, 0)


# ---- Datetime parsing -------------------------------------------------------


class TestParseDatetime:
    def test_basic(self) -> None:
        dt = parse_datetime("2026-03-13T14:30:00")
        assert dt == datetime.datetime(2026, 3, 13, 14, 30, 0)

    def test_with_tz(self) -> None:
        dt = parse_datetime("2026-03-13T14:30:00+01:00")
        assert dt.tzinfo is not None
        assert dt.utcoffset() == datetime.timedelta(hours=1)

    def test_with_utc(self) -> None:
        dt = parse_datetime("2026-03-13T14:30:00Z")
        assert dt.utcoffset() == datetime.timedelta(0)

    def test_with_fractional(self) -> None:
        dt = parse_datetime("2026-03-13T14:30:00.123456")
        assert dt.microsecond == 123456

    def test_no_separator(self) -> None:
        with pytest.raises(ParseError):
            parse_datetime("20260313143000")

    def test_missing_time(self) -> None:
        with pytest.raises(ParseError):
            parse_datetime("2026-03-13T")


# ---- Duration parsing -------------------------------------------------------


class TestParseDuration:
    def test_full(self) -> None:
        d = parse_duration("P1Y2M3DT4H5M6S")
        assert isinstance(d, Duration)
        assert d.years == 1
        assert d.months == 2
        assert d.days == 3

    def test_weeks(self) -> None:
        td = parse_duration("P3W")
        assert isinstance(td, datetime.timedelta)
        assert td.days == 21

    def test_days_only(self) -> None:
        td = parse_duration("P30D")
        assert isinstance(td, datetime.timedelta)
        assert td.days == 30

    def test_time_only(self) -> None:
        td = parse_duration("PT1H30M")
        assert isinstance(td, datetime.timedelta)
        assert td.seconds == 5400

    def test_fractional_seconds(self) -> None:
        td = parse_duration("PT1.5S")
        assert isinstance(td, datetime.timedelta)
        assert td.seconds == 1
        assert td.microseconds == 500000

    def test_negative(self) -> None:
        d = parse_duration("-P1Y")
        assert isinstance(d, Duration)
        assert d.years == -1

    def test_alternate_format(self) -> None:
        d = parse_duration("P0001-02-03T04:05:06")
        assert isinstance(d, Duration)
        assert d.years == 1
        assert d.months == 2
        assert d.days == 3

    def test_empty_raises(self) -> None:
        with pytest.raises(ParseError):
            parse_duration("P")

    def test_invalid(self) -> None:
        with pytest.raises(ParseError):
            parse_duration("not-a-duration")

    def test_returns_timedelta_for_fixed(self) -> None:
        td = parse_duration("P5D")
        assert isinstance(td, datetime.timedelta)

    def test_returns_duration_for_non_fixed(self) -> None:
        d = parse_duration("P1M")
        assert isinstance(d, Duration)
