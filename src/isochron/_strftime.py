"""strftime-style formatting with ISO 8601 extras."""

from __future__ import annotations

import datetime
import re

from isochron._errors import FormatError

# Custom directives we handle ourselves
_CUSTOM_RE = re.compile(r"%(:z|G|V|u)")


def strftime(dt: datetime.date | datetime.datetime, fmt: str) -> str:
    """Format a date or datetime using strftime with ISO 8601 extensions.

    Extra directives beyond standard strftime:
    - ``%G``: ISO year (week-based year)
    - ``%V``: ISO week number (01-53)
    - ``%u``: ISO weekday (1=Monday, 7=Sunday)
    - ``%:z``: timezone offset as ``+HH:MM`` (vs ``%z`` which is ``+HHMM``)

    Raises
    ------
    FormatError
        On formatting failures.
    """

    def _replace(m: re.Match[str]) -> str:
        directive = m.group(1)
        if directive == ":z":
            if not isinstance(dt, datetime.datetime) or dt.tzinfo is None:
                return ""
            offset = dt.utcoffset()
            if offset is None:
                return ""
            total = int(offset.total_seconds())
            sign = "+" if total >= 0 else "-"
            total = abs(total)
            h, mins = divmod(total // 60, 60)
            return f"{sign}{h:02d}:{mins:02d}"
        if directive == "G":
            iso_year, _, _ = dt.isocalendar()
            return str(iso_year)
        if directive == "V":
            _, iso_week, _ = dt.isocalendar()
            return f"{iso_week:02d}"
        if directive == "u":
            _, _, iso_day = dt.isocalendar()
            return str(iso_day)
        return m.group(0)

    # Protect escaped %% from custom directive matching
    _placeholder = "\x00PERCENT\x00"
    protected = fmt.replace("%%", _placeholder)

    # Replace custom directives
    processed = _CUSTOM_RE.sub(_replace, protected)

    # Restore escaped %%
    processed = processed.replace(_placeholder, "%%")

    try:
        return dt.strftime(processed)
    except (ValueError, TypeError) as e:
        raise FormatError(str(e)) from e
