"""Regression tests for fixed bugs."""

from __future__ import annotations

import datetime

import pytest

from isochron import (
    Duration,
    FormatError,
    ParseError,
    parse_date,
    strftime,
)
from isochron._format import format_timezone
from isochron.compat import tz_isoformat


# ---- #340: Duration.__str__ roundtrip with month→year normalization ---------


class TestDurationRoundtripRegression:
    """Bug #340 issue 1: Duration(years=1, months=-2) formatted incorrectly."""

    def test_mixed_sign_raises_format_error(self) -> None:
        d = Duration(years=1, days=-1)
        with pytest.raises(FormatError, match="mixed-sign"):
            str(d)

    def test_month_year_normalization_formats_correctly(self) -> None:
        # Duration(years=1, months=-2) has total_months=10, no mixed sign
        d = Duration(years=1, months=-2)
        assert str(d) == "P10M"

    def test_negative_duration_roundtrip(self) -> None:
        d = Duration(years=-1, months=-2)
        assert str(d) == "-P1Y2M"

    def test_positive_duration_roundtrip(self) -> None:
        d = Duration(years=1, months=2)
        assert str(d) == "P1Y2M"

    def test_month_normalization_to_year(self) -> None:
        d = Duration(months=14)
        assert str(d) == "P1Y2M"


# ---- #340: compat tz_isoformat returns tz portion only ----------------------


class TestTzIsoformatRegression:
    """Bug #340 issue 2: tz_isoformat returned full time, not just tz."""

    def test_tz_isoformat_utc(self) -> None:
        t = datetime.time(14, 30, 0, tzinfo=datetime.timezone.utc)
        assert tz_isoformat(t) == "Z"

    def test_tz_isoformat_offset(self) -> None:
        tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        t = datetime.time(14, 30, 0, tzinfo=tz)
        assert tz_isoformat(t) == "+05:30"

    def test_tz_isoformat_naive(self) -> None:
        t = datetime.time(14, 30, 0)
        assert tz_isoformat(t) == ""

    def test_format_timezone_matches(self) -> None:
        t = datetime.time(14, 30, 0, tzinfo=datetime.timezone.utc)
        assert format_timezone(t) == "Z"


# ---- #340: strftime %% escape -----------------------------------------------


class TestStrftimeEscapeRegression:
    """Bug #340 issue 3: strftime(dt, '%%G') produced ISO year instead of literal %G."""

    def test_double_percent_g(self) -> None:
        dt = datetime.date(2026, 3, 13)
        result = strftime(dt, "%%G")
        assert result == "%G"

    def test_double_percent_v(self) -> None:
        dt = datetime.date(2026, 3, 13)
        result = strftime(dt, "%%V")
        assert result == "%V"

    def test_double_percent_u(self) -> None:
        dt = datetime.date(2026, 3, 13)
        result = strftime(dt, "%%u")
        assert result == "%u"

    def test_mixed_escaped_and_real(self) -> None:
        dt = datetime.date(2026, 3, 13)
        result = strftime(dt, "%G-%%G")
        assert result == "2026-%G"


# ---- #340: date - Duration --------------------------------------------------


class TestDateSubDurationRegression:
    """Bug #340 issue 4: date - Duration raised TypeError."""

    def test_date_minus_duration(self) -> None:
        d = datetime.date(2026, 3, 13)
        dur = Duration(months=1)
        result = d - dur
        assert result == datetime.date(2026, 2, 13)

    def test_datetime_minus_duration(self) -> None:
        dt = datetime.datetime(2026, 3, 13, 12, 0, 0)
        dur = Duration(months=1)
        result = dt - dur
        assert result == datetime.datetime(2026, 2, 13, 12, 0, 0)


# ---- #367: Ordinal date validation -------------------------------------------


class TestOrdinalDateValidation:
    """Bug #367 issue 1: parse_date accepted out-of-range ordinal days."""

    def test_ordinal_day_zero_raises(self) -> None:
        with pytest.raises(ParseError, match="Ordinal day 0 out of range"):
            parse_date("2026-000")

    def test_ordinal_day_366_non_leap_raises(self) -> None:
        # 2026 is not a leap year, max ordinal is 365
        with pytest.raises(ParseError, match="Ordinal day 366 out of range"):
            parse_date("2026-366")

    def test_ordinal_day_366_leap_ok(self) -> None:
        # 2024 is a leap year
        result = parse_date("2024-366")
        assert result == datetime.date(2024, 12, 31)

    def test_ordinal_day_367_leap_raises(self) -> None:
        with pytest.raises(ParseError, match="Ordinal day 367 out of range"):
            parse_date("2024-367")

    def test_ordinal_day_365_non_leap_ok(self) -> None:
        result = parse_date("2026-365")
        assert result == datetime.date(2026, 12, 31)

    def test_ordinal_day_1_ok(self) -> None:
        result = parse_date("2026-001")
        assert result == datetime.date(2026, 1, 1)
