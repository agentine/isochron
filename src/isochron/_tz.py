"""Timezone utilities: UTC singleton and FixedOffset tzinfo."""

from __future__ import annotations

import datetime


UTC: datetime.timezone = datetime.timezone.utc
"""UTC timezone singleton, alias for ``datetime.timezone.utc``."""


class FixedOffset(datetime.tzinfo):
    """A fixed UTC-offset timezone.

    Parameters
    ----------
    hours:
        Offset hours (may be negative).
    minutes:
        Offset minutes (same sign as *hours*).
    """

    __slots__ = ("_offset", "_name")

    def __init__(self, hours: int = 0, minutes: int = 0) -> None:
        self._offset: datetime.timedelta = datetime.timedelta(hours=hours, minutes=minutes)
        total = int(self._offset.total_seconds())
        sign = "+" if total >= 0 else "-"
        total = abs(total)
        h, m = divmod(total // 60, 60)
        self._name: str = f"UTC{sign}{h:02d}:{m:02d}"

    # -- tzinfo interface --------------------------------------------------

    def utcoffset(self, dt: datetime.datetime | None = None) -> datetime.timedelta:
        return self._offset

    def tzname(self, dt: datetime.datetime | None = None) -> str:
        return self._name

    def dst(self, dt: datetime.datetime | None = None) -> datetime.timedelta:
        return datetime.timedelta(0)

    # -- extras ------------------------------------------------------------

    @property
    def total_minutes(self) -> int:
        """Total offset in minutes."""
        return int(self._offset.total_seconds()) // 60

    # -- identity ----------------------------------------------------------

    def __repr__(self) -> str:
        return f"FixedOffset({self._name!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FixedOffset):
            return self._offset == other._offset
        if isinstance(other, datetime.timezone):
            return self._offset == other.utcoffset(None)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._offset)
