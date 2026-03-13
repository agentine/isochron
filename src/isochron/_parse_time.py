"""ISO 8601 time parsing."""

from __future__ import annotations

import datetime
import re

from isochron._errors import ParseError
from isochron._parse_tz import parse_timezone

# Time pattern: optional T prefix, HH:MM:SS or HHMMSS, optional fraction, optional tz
_TIME_RE = re.compile(
    r"^T?"
    r"(?P<hour>\d{2})"
    r"(?::?(?P<minute>\d{2})"
    r"(?::?(?P<second>\d{2})"
    r"(?:[.,](?P<frac>\d+))?)?)?"
    r"(?P<tz>Z|[+-]\d{2}(?::?\d{2})?)?$"
)


def parse_time(s: str) -> datetime.time:
    """Parse an ISO 8601 time string.

    Supports ``HH:MM:SS``, ``HHMMSS``, fractional seconds,
    ``T``-prefixed forms, ``T24:00:00`` midnight, and timezone suffixes.

    Fixes over isodate:
    - Accepts ``T24:00:00`` (#85, #86)
    - Handles 59.99999->60 rounding (#87)
    - Second out of range (#90)

    Raises
    ------
    ParseError
        If *s* is not a valid ISO 8601 time.
    """
    m = _TIME_RE.match(s)
    if m is None:
        raise ParseError("Invalid ISO 8601 time", string=s)

    hour = int(m.group("hour"))
    minute = int(m.group("minute") or "0")
    second = int(m.group("second") or "0")
    microsecond = 0

    if m.group("frac"):
        frac_str = m.group("frac")
        # Pad or truncate to 6 digits for microseconds
        frac_str = frac_str[:6].ljust(6, "0")
        microsecond = int(frac_str)

    # Handle T24:00:00 — ISO 8601 midnight representation
    if hour == 24:
        if minute != 0 or second != 0 or microsecond != 0:
            raise ParseError("T24 only valid as T24:00:00", string=s)
        hour = 0

    # Handle 59.99999 -> 60 rounding (isodate #87) and second out of range (#90)
    if second >= 60:
        second = 59
        microsecond = 999999

    if minute >= 60:
        raise ParseError("Minute out of range", string=s)

    # Parse timezone
    tzinfo: datetime.tzinfo | None = None
    if m.group("tz"):
        tzinfo = parse_timezone(m.group("tz"))

    try:
        return datetime.time(hour, minute, second, microsecond, tzinfo=tzinfo)
    except ValueError as e:
        raise ParseError(str(e), string=s) from e
