"""isodate drop-in compatibility shim.

Provides all public names from ``isodate`` mapped to isochron equivalents::

    # Before:
    from isodate import parse_date, parse_datetime, parse_duration
    from isodate import ISO8601Error, Duration

    # After:
    from isochron.compat import parse_date, parse_datetime, parse_duration
    from isochron.compat import ISO8601Error, Duration
"""

from __future__ import annotations

from isochron._duration import Duration
from isochron._errors import ISO8601Error, ParseError
from isochron._format import format_date, format_datetime, format_duration, format_time, format_timezone
from isochron._parse_date import parse_date
from isochron._parse_datetime import parse_datetime
from isochron._parse_duration import parse_duration
from isochron._parse_time import parse_time
from isochron._parse_tz import parse_timezone
from isochron._tz import UTC, FixedOffset

# isodate name aliases
duration_isoformat = format_duration
datetime_isoformat = format_datetime
date_isoformat = format_date
time_isoformat = format_time
tz_isoformat = format_timezone  # isodate uses tz_isoformat for tz portion only

__all__ = [
    "Duration",
    "FixedOffset",
    "ISO8601Error",
    "ParseError",
    "UTC",
    "date_isoformat",
    "datetime_isoformat",
    "duration_isoformat",
    "format_date",
    "format_datetime",
    "format_duration",
    "format_time",
    "parse_date",
    "parse_datetime",
    "parse_duration",
    "parse_time",
    "parse_timezone",
    "time_isoformat",
    "tz_isoformat",
]
