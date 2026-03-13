"""Timezone offset parsing."""

from __future__ import annotations

import datetime
import re

from isochron._errors import ParseError
from isochron._tz import UTC, FixedOffset

_TZ_RE = re.compile(
    r"^(?P<z>Z)|(?P<sign>[+-])(?P<hours>\d{2})(?::?(?P<minutes>\d{2}))?$"
)


def parse_timezone(s: str) -> datetime.tzinfo:
    """Parse an ISO 8601 timezone offset string.

    Accepted formats: ``Z``, ``+HH``, ``+HH:MM``, ``+HHMM``,
    ``-HH``, ``-HH:MM``, ``-HHMM``.

    Raises
    ------
    ParseError
        If *s* is not a valid timezone string.
    """
    m = _TZ_RE.match(s)
    if m is None:
        raise ParseError("Invalid timezone", string=s)

    if m.group("z"):
        return UTC

    sign = 1 if m.group("sign") == "+" else -1
    hours = int(m.group("hours"))
    minutes = int(m.group("minutes") or "0")
    return FixedOffset(hours=sign * hours, minutes=sign * minutes)
