"""Duration class supporting years/months and timedelta components."""

from __future__ import annotations

import calendar
import datetime
from dataclasses import dataclass
from typing import overload


@dataclass(frozen=True, slots=True)
class Duration:
    """An ISO 8601 duration with year/month and day/time components.

    Unlike ``datetime.timedelta``, a Duration can represent periods with
    variable-length units (years and months).
    """

    years: int = 0
    months: int = 0
    days: int = 0
    seconds: int = 0
    microseconds: int = 0

    # -- properties --------------------------------------------------------

    @property
    def is_fixed(self) -> bool:
        """True when the duration contains no year/month components."""
        return self.years == 0 and self.months == 0

    # -- conversion --------------------------------------------------------

    def to_timedelta(self, reference: datetime.date | None = None) -> datetime.timedelta:
        """Convert to a ``datetime.timedelta``.

        If the duration has year or month components a *reference* date is
        required to resolve their variable lengths.

        Raises
        ------
        ValueError
            If *reference* is ``None`` and the duration has year/month parts.
        """
        if not self.is_fixed and reference is None:
            raise ValueError(
                "Duration with year/month components requires a reference date "
                "to convert to timedelta"
            )

        extra_days = 0
        if reference is not None and not self.is_fixed:
            y = reference.year + self.years
            m = reference.month + self.months
            # normalise month overflow / underflow
            y += (m - 1) // 12
            m = (m - 1) % 12 + 1
            day = min(reference.day, calendar.monthrange(y, m)[1])
            target = reference.replace(year=y, month=m, day=day)
            extra_days = (target - reference).days

        return datetime.timedelta(
            days=self.days + extra_days,
            seconds=self.seconds,
            microseconds=self.microseconds,
        )

    def total_seconds(self, reference: datetime.date | None = None) -> float:
        """Return total duration in seconds.

        Raises ``ValueError`` when years/months are present and *reference*
        is ``None`` — unlike isodate which silently returns 0 (bug #95).
        """
        return self.to_timedelta(reference).total_seconds()

    # -- arithmetic --------------------------------------------------------

    @overload
    def __add__(self, other: Duration) -> Duration: ...
    @overload
    def __add__(self, other: datetime.timedelta) -> Duration: ...
    @overload
    def __add__(self, other: datetime.datetime) -> datetime.datetime: ...
    @overload
    def __add__(self, other: datetime.date) -> datetime.date: ...

    def __add__(
        self, other: Duration | datetime.timedelta | datetime.date | datetime.datetime
    ) -> Duration | datetime.date | datetime.datetime:
        if isinstance(other, Duration):
            return Duration(
                years=self.years + other.years,
                months=self.months + other.months,
                days=self.days + other.days,
                seconds=self.seconds + other.seconds,
                microseconds=self.microseconds + other.microseconds,
            )
        if isinstance(other, datetime.timedelta):
            return Duration(
                years=self.years,
                months=self.months,
                days=self.days + other.days,
                seconds=self.seconds + other.seconds,
                microseconds=self.microseconds + other.microseconds,
            )
        if isinstance(other, datetime.datetime):
            return _add_to_datetime(other, self)
        if isinstance(other, datetime.date):
            return _add_to_date(other, self)
        return NotImplemented

    def __radd__(
        self, other: datetime.timedelta | datetime.date | datetime.datetime
    ) -> Duration | datetime.date | datetime.datetime:
        return self.__add__(other)

    def __sub__(self, other: Duration | datetime.timedelta) -> Duration:
        if isinstance(other, Duration):
            return Duration(
                years=self.years - other.years,
                months=self.months - other.months,
                days=self.days - other.days,
                seconds=self.seconds - other.seconds,
                microseconds=self.microseconds - other.microseconds,
            )
        if isinstance(other, datetime.timedelta):
            return Duration(
                years=self.years,
                months=self.months,
                days=self.days - other.days,
                seconds=self.seconds - other.seconds,
                microseconds=self.microseconds - other.microseconds,
            )
        return NotImplemented

    def __rsub__(
        self, other: datetime.timedelta | datetime.date | datetime.datetime
    ) -> Duration | datetime.date | datetime.datetime:
        if isinstance(other, datetime.timedelta):
            return Duration(
                years=-self.years,
                months=-self.months,
                days=other.days - self.days,
                seconds=other.seconds - self.seconds,
                microseconds=other.microseconds - self.microseconds,
            )
        if isinstance(other, datetime.datetime):
            return _add_to_datetime(other, -self)
        if isinstance(other, datetime.date):
            return _add_to_date(other, -self)
        return NotImplemented

    def __neg__(self) -> Duration:
        return Duration(
            years=-self.years,
            months=-self.months,
            days=-self.days,
            seconds=-self.seconds,
            microseconds=-self.microseconds,
        )

    def __mul__(self, other: int) -> Duration:
        if isinstance(other, int):
            return Duration(
                years=self.years * other,
                months=self.months * other,
                days=self.days * other,
                seconds=self.seconds * other,
                microseconds=self.microseconds * other,
            )
        return NotImplemented

    def __rmul__(self, other: int) -> Duration:
        return self.__mul__(other)

    def __bool__(self) -> bool:
        return bool(self.years or self.months or self.days or self.seconds or self.microseconds)

    def __repr__(self) -> str:
        parts: list[str] = []
        for field in ("years", "months", "days", "seconds", "microseconds"):
            val = getattr(self, field)
            if val:
                parts.append(f"{field}={val}")
        if not parts:
            return "Duration()"
        return f"Duration({', '.join(parts)})"

    def __str__(self) -> str:
        return _format_duration(self)


# -- helpers ---------------------------------------------------------------


def _add_to_date(d: datetime.date, dur: Duration) -> datetime.date:
    """Add a Duration to a date, resolving year/month components."""
    y = d.year + dur.years
    m = d.month + dur.months
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    day = min(d.day, calendar.monthrange(y, m)[1])
    result = d.replace(year=y, month=m, day=day)
    td = datetime.timedelta(days=dur.days, seconds=dur.seconds, microseconds=dur.microseconds)
    return result + td


def _add_to_datetime(dt: datetime.datetime, dur: Duration) -> datetime.datetime:
    """Add a Duration to a datetime, resolving year/month components."""
    y = dt.year + dur.years
    m = dt.month + dur.months
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    day = min(dt.day, calendar.monthrange(y, m)[1])
    result = dt.replace(year=y, month=m, day=day)
    td = datetime.timedelta(days=dur.days, seconds=dur.seconds, microseconds=dur.microseconds)
    return result + td


def _format_duration(d: Duration) -> str:
    """Format a Duration as an ISO 8601 duration string."""
    from isochron._errors import FormatError

    if not d:
        return "P0D"

    # Normalize months into years
    total_months = d.years * 12 + d.months
    norm_years, norm_months = divmod(abs(total_months), 12)

    # Normalize time
    total_us = d.seconds * 1_000_000 + d.microseconds
    abs_total_us = abs(total_us)
    total_s, norm_us = divmod(abs_total_us, 1_000_000)
    hours, remainder = divmod(total_s, 3600)
    minutes, secs = divmod(remainder, 60)

    norm_days = abs(d.days)

    # Check for mixed signs (unrepresentable in ISO 8601)
    signs: set[bool] = set()
    if total_months != 0:
        signs.add(total_months > 0)
    if d.days != 0:
        signs.add(d.days > 0)
    if total_us != 0:
        signs.add(total_us > 0)

    if len(signs) > 1:
        raise FormatError(
            f"Cannot format duration with mixed-sign components: {d!r}"
        )

    is_negative = False in signs  # False means a negative value was present

    parts: list[str] = ["P"]
    if norm_years:
        parts.append(f"{norm_years}Y")
    if norm_months:
        parts.append(f"{norm_months}M")
    if norm_days:
        parts.append(f"{norm_days}D")

    time_parts: list[str] = []
    if hours:
        time_parts.append(f"{hours}H")
    if minutes:
        time_parts.append(f"{minutes}M")
    if secs or norm_us:
        if norm_us:
            frac = f"{secs}.{norm_us:06d}".rstrip("0")
            time_parts.append(f"{frac}S")
        else:
            time_parts.append(f"{secs}S")

    if time_parts:
        parts.append("T")
        parts.extend(time_parts)

    result = "".join(parts)
    if result == "P":
        return "P0D"

    if is_negative:
        return "-" + result
    return result
