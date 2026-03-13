"""ISO 8601 duration parsing."""

from __future__ import annotations

import datetime
import re

from isochron._duration import Duration
from isochron._errors import ParseError

# Standard duration: PnYnMnDTnHnMnS
_DURATION_RE = re.compile(
    r"^(?P<sign>-)?P"
    r"(?:(?P<years>\d+)Y)?"
    r"(?:(?P<months>\d+)M)?"
    r"(?:(?P<weeks>\d+)W)?"
    r"(?:(?P<days>\d+)D)?"
    r"(?:T"
    r"(?:(?P<hours>\d+)H)?"
    r"(?:(?P<minutes>\d+)M)?"
    r"(?:(?P<seconds>\d+)(?:[.,](?P<frac>\d+))?S)?"
    r")?$"
)

# Alternate format: PYYYY-MM-DDThh:mm:ss or PYYYYMMDDThhmmss
_ALT_RE = re.compile(
    r"^(?P<sign>-)?P"
    r"(?P<years>\d{4})-(?P<months>\d{2})-(?P<days>\d{2})"
    r"T(?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})$"
)

_ALT_COMPACT_RE = re.compile(
    r"^(?P<sign>-)?P"
    r"(?P<years>\d{4})(?P<months>\d{2})(?P<days>\d{2})"
    r"T(?P<hours>\d{2})(?P<minutes>\d{2})(?P<seconds>\d{2})$"
)


def parse_duration(s: str) -> Duration | datetime.timedelta:
    """Parse an ISO 8601 duration string.

    Returns a ``Duration`` when the result has year or month components,
    otherwise a ``datetime.timedelta``.

    Fixes over isodate:
    - #95: non-fixed durations return ``Duration``, not broken ``timedelta``
    - #96: alternate format spurious months=1
    - #97: ordinal date format extra days

    Raises
    ------
    ParseError
        If *s* is not a valid ISO 8601 duration.
    """
    # Try alternate format first (more specific)
    for alt_re in (_ALT_RE, _ALT_COMPACT_RE):
        m = alt_re.match(s)
        if m:
            return _build_duration(m)

    # Standard format
    m = _DURATION_RE.match(s)
    if m is None:
        raise ParseError("Invalid ISO 8601 duration", string=s)

    # Validate not empty (just "P" with nothing)
    if not any(m.group(g) for g in ("years", "months", "weeks", "days", "hours", "minutes", "seconds")):
        raise ParseError("Empty duration", string=s)

    return _build_duration(m)


def _build_duration(m: re.Match[str]) -> Duration | datetime.timedelta:
    """Build a Duration or timedelta from regex match groups."""
    sign = -1 if m.group("sign") else 1

    years = int(m.group("years") or 0)
    months = int(m.group("months") or 0)
    weeks = int(m.group("weeks") or 0) if "weeks" in m.groupdict() else 0
    days = int(m.group("days") or 0)
    hours = int(m.group("hours") or 0)
    minutes = int(m.group("minutes") or 0)
    seconds = int(m.group("seconds") or 0)

    microseconds = 0
    if "frac" in m.groupdict() and m.group("frac"):
        frac_str = m.group("frac")[:6].ljust(6, "0")
        microseconds = int(frac_str)

    total_days = days + weeks * 7
    total_seconds = hours * 3600 + minutes * 60 + seconds

    if years or months:
        return Duration(
            years=sign * years,
            months=sign * months,
            days=sign * total_days,
            seconds=sign * total_seconds,
            microseconds=sign * microseconds,
        )

    return datetime.timedelta(
        days=sign * total_days,
        seconds=sign * total_seconds,
        microseconds=sign * microseconds,
    )
