"""ISO 8601 datetime parsing."""

from __future__ import annotations

import datetime

from isochron._errors import ParseError
from isochron._parse_date import parse_date
from isochron._parse_time import parse_time


def parse_datetime(s: str) -> datetime.datetime:
    """Parse a combined ISO 8601 datetime string.

    Expected format: ``<date>T<time>`` where ``T`` is the separator.

    Raises
    ------
    ParseError
        If *s* is not a valid ISO 8601 datetime.
    """
    # Find the T separator — it must separate date from time
    t_pos = s.find("T")
    if t_pos == -1:
        t_pos = s.find("t")
    if t_pos == -1:
        raise ParseError("Missing T separator in datetime", string=s)

    date_str = s[:t_pos]
    time_str = s[t_pos + 1:]  # strip the T prefix, parse_time handles T-prefixed too

    if not date_str:
        raise ParseError("Empty date component", string=s)
    if not time_str:
        raise ParseError("Empty time component", string=s)

    try:
        d = parse_date(date_str)
    except ParseError:
        raise ParseError("Invalid date in datetime", string=s) from None

    try:
        t = parse_time(time_str)
    except ParseError:
        raise ParseError("Invalid time in datetime", string=s) from None

    return datetime.datetime.combine(d, t)
