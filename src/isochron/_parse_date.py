"""ISO 8601 date parsing."""

from __future__ import annotations

import calendar
import datetime
import re

from isochron._errors import ParseError

# Calendar date: YYYY-MM-DD or YYYYMMDD (with optional negative year)
_CALENDAR_RE = re.compile(
    r"^(?P<neg>-)?(?P<year>\d{4})-?(?P<month>\d{2})-?(?P<day>\d{2})$"
)

# Ordinal date: YYYY-DDD
_ORDINAL_RE = re.compile(
    r"^(?P<neg>-)?(?P<year>\d{4})-?(?P<ordinal>\d{3})$"
)

# Week date: YYYY-Www-D or YYYYWwwD
_WEEK_RE = re.compile(
    r"^(?P<neg>-)?(?P<year>\d{4})-?W(?P<week>\d{2})(?:-?(?P<day>\d))?$"
)


def parse_date(s: str) -> datetime.date:
    """Parse an ISO 8601 date string.

    Supported formats:
    - Calendar: ``YYYY-MM-DD``, ``YYYYMMDD``
    - Ordinal: ``YYYY-DDD``
    - Week: ``YYYY-Www-D``, ``YYYYWwwD``
    - Negative years: ``-YYYY-MM-DD``

    Raises
    ------
    ParseError
        If *s* is not a valid ISO 8601 date.
    """
    # Try calendar date
    m = _CALENDAR_RE.match(s)
    if m:
        year = int(m.group("year"))
        if m.group("neg"):
            year = -year
        month = int(m.group("month"))
        day = int(m.group("day"))
        try:
            return datetime.date(year, month, day)
        except ValueError as e:
            raise ParseError(str(e), string=s) from e

    # Try ordinal date
    m = _ORDINAL_RE.match(s)
    if m:
        year = int(m.group("year"))
        if m.group("neg"):
            year = -year
        ordinal = int(m.group("ordinal"))
        max_ordinal = 366 if calendar.isleap(year) else 365
        if ordinal < 1 or ordinal > max_ordinal:
            raise ParseError(
                f"Ordinal day {ordinal} out of range for year {year} (1-{max_ordinal})",
                string=s,
            )
        try:
            return datetime.date(year, 1, 1) + datetime.timedelta(days=ordinal - 1)
        except ValueError as e:
            raise ParseError(str(e), string=s) from e

    # Try week date
    m = _WEEK_RE.match(s)
    if m:
        year = int(m.group("year"))
        if m.group("neg"):
            year = -year
        week = int(m.group("week"))
        day = int(m.group("day") or "1")
        try:
            return datetime.date.fromisocalendar(year, week, day)
        except ValueError as e:
            raise ParseError(str(e), string=s) from e

    raise ParseError("Invalid ISO 8601 date", string=s)
