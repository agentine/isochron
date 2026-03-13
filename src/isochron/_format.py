"""ISO 8601 formatting functions."""

from __future__ import annotations

import datetime

from isochron._duration import Duration
from isochron._errors import FormatError


def format_date(d: datetime.date) -> str:
    """Format a date as ``YYYY-MM-DD``."""
    return d.isoformat()


def format_time(t: datetime.time) -> str:
    """Format a time as ``HH:MM:SS`` with optional timezone suffix.

    Fix for isodate #89: ``datetime.timezone.utc`` outputs ``Z`` instead
    of ``+00:00``.
    """
    base = t.strftime("%H:%M:%S")
    if t.microsecond:
        base += f".{t.microsecond:06d}".rstrip("0")

    if t.tzinfo is not None:
        offset = t.utcoffset()
        if offset is None:
            return base
        if offset == datetime.timedelta(0):
            return base + "Z"
        total = int(offset.total_seconds())
        sign = "+" if total >= 0 else "-"
        total = abs(total)
        h, m = divmod(total // 60, 60)
        return f"{base}{sign}{h:02d}:{m:02d}"

    return base


def format_datetime(dt: datetime.datetime) -> str:
    """Format a datetime as ``YYYY-MM-DDTHH:MM:SS`` with timezone suffix.

    UTC-aware datetimes output ``Z`` suffix (isodate #89 fix).
    """
    return format_date(dt.date()) + "T" + format_time(dt.timetz())


def format_duration(d: Duration | datetime.timedelta) -> str:
    """Format a duration as an ISO 8601 duration string.

    Uses ``PnW`` form when the duration is an exact number of weeks.
    """
    if isinstance(d, datetime.timedelta):
        if d.days < 0:
            return _format_negative_td(d)
        return _format_timedelta(d)
    if isinstance(d, Duration):  # pyright: ignore[reportUnnecessaryIsInstance]
        return str(d)
    raise FormatError(f"Cannot format {type(d).__name__} as duration")


def _format_timedelta(td: datetime.timedelta) -> str:
    """Format a non-negative timedelta as ISO 8601."""
    total_seconds = int(td.total_seconds())
    if total_seconds == 0 and td.microseconds == 0:
        return "P0D"

    days = td.days
    remainder = td.seconds

    # Check if pure weeks
    if remainder == 0 and td.microseconds == 0 and days % 7 == 0:
        return f"P{days // 7}W"

    parts: list[str] = ["P"]
    if days:
        parts.append(f"{days}D")

    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    time_parts: list[str] = []
    if hours:
        time_parts.append(f"{hours}H")
    if minutes:
        time_parts.append(f"{minutes}M")
    if secs or td.microseconds:
        if td.microseconds:
            frac = f"{secs}.{td.microseconds:06d}".rstrip("0")
            time_parts.append(f"{frac}S")
        else:
            time_parts.append(f"{secs}S")

    if time_parts:
        parts.append("T")
        parts.extend(time_parts)

    result = "".join(parts)
    return result if result != "P" else "P0D"


def _format_negative_td(td: datetime.timedelta) -> str:
    """Format a negative timedelta."""
    pos = -td
    return "-" + _format_timedelta(pos)


def format_timezone(t: datetime.time | datetime.datetime) -> str:
    """Format only the timezone portion of a time or datetime.

    Returns ``Z`` for UTC, ``+HH:MM`` / ``-HH:MM`` for other offsets,
    or an empty string for naive values.  This matches isodate's
    ``tz_isoformat`` behaviour.
    """
    if t.tzinfo is None:
        return ""
    offset = t.utcoffset()
    if offset is None:
        return ""
    if offset == datetime.timedelta(0):
        return "Z"
    total = int(offset.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    h, m = divmod(total // 60, 60)
    return f"{sign}{h:02d}:{m:02d}"
