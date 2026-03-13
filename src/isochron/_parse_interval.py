"""ISO 8601 interval and recurring interval parsing."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Iterator

from isochron._duration import Duration
from isochron._errors import ParseError
from isochron._parse_date import parse_date
from isochron._parse_datetime import parse_datetime
from isochron._parse_duration import parse_duration


@dataclass(frozen=True, slots=True)
class Interval:
    """An ISO 8601 time interval."""

    start: datetime.datetime | datetime.date | None
    end: datetime.datetime | datetime.date | None
    duration: Duration | datetime.timedelta | None


@dataclass(frozen=True, slots=True)
class RecurringInterval:
    """An ISO 8601 recurring time interval."""

    recurrences: int | None  # None = infinite
    interval: Interval

    def __iter__(self) -> Iterator[datetime.datetime | datetime.date]:
        start = self.interval.start
        dur = self.interval.duration

        if start is None or dur is None:
            raise ValueError("Cannot iterate: need start and duration")

        count = 0
        current = start
        while self.recurrences is None or count < self.recurrences:
            yield current
            if isinstance(dur, Duration):
                current = dur + current
            elif isinstance(current, datetime.datetime):
                current = current + dur
            else:
                current = current + dur
            count += 1


def _parse_endpoint(s: str) -> datetime.datetime | datetime.date:
    """Parse an interval endpoint as datetime or date."""
    if "T" in s or "t" in s:
        return parse_datetime(s)
    return parse_date(s)


def parse_interval(s: str) -> Interval:
    """Parse an ISO 8601 interval string.

    Supported forms:
    - ``start/end``
    - ``start/duration``
    - ``duration/end``

    Raises
    ------
    ParseError
        If *s* is not a valid ISO 8601 interval.
    """
    parts = s.split("/")
    if len(parts) != 2:
        raise ParseError("Interval must have exactly one '/' separator", string=s)

    left, right = parts

    if not left or not right:
        raise ParseError("Empty interval component", string=s)

    left_is_dur = left.lstrip("-").startswith("P")
    right_is_dur = right.lstrip("-").startswith("P")

    if left_is_dur and right_is_dur:
        raise ParseError("Both components cannot be durations", string=s)

    if left_is_dur:
        # duration/end
        dur = parse_duration(left)
        end = _parse_endpoint(right)
        return Interval(start=None, end=end, duration=dur)

    if right_is_dur:
        # start/duration
        start = _parse_endpoint(left)
        dur = parse_duration(right)
        return Interval(start=start, end=None, duration=dur)

    # start/end
    start = _parse_endpoint(left)
    end = _parse_endpoint(right)
    return Interval(start=start, end=end, duration=None)


def parse_recurring(s: str) -> RecurringInterval:
    """Parse an ISO 8601 recurring interval.

    Format: ``Rn/<interval>`` or ``R/<interval>`` (infinite).

    Raises
    ------
    ParseError
        If *s* is not a valid recurring interval.
    """
    if not s.startswith("R"):
        raise ParseError("Recurring interval must start with 'R'", string=s)

    # Find first '/' after R
    slash_pos = s.find("/")
    if slash_pos == -1:
        raise ParseError("Missing '/' in recurring interval", string=s)

    r_part = s[1:slash_pos]
    interval_str = s[slash_pos + 1:]

    if r_part == "":
        recurrences: int | None = None
    else:
        try:
            recurrences = int(r_part)
        except ValueError:
            raise ParseError("Invalid recurrence count", string=s) from None

    interval = parse_interval(interval_str)
    return RecurringInterval(recurrences=recurrences, interval=interval)
