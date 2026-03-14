# isochron

[![CI](https://github.com/agentine/isochron/actions/workflows/ci.yml/badge.svg)](https://github.com/agentine/isochron/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/isochron)](https://pypi.org/project/isochron/)
[![Python](https://img.shields.io/pypi/pyversions/isochron)](https://pypi.org/project/isochron/)

A modern, fully-typed ISO 8601 date/time/duration/interval parser and formatter for Python. Drop-in replacement for [isodate](https://github.com/gweis/isodate).

## Why isochron?

`isodate` has 129M+ downloads/month but suffers from single-maintainer risk, sporadic maintenance, and [28 open bugs](https://github.com/gweis/isodate/issues). isochron fixes all known isodate bugs, adds interval/recurring interval support, and provides strict type annotations.

## Installation

```bash
pip install isochron
```

## Quick Start

```python
import datetime
from isochron import (
    parse_date, parse_time, parse_datetime, parse_duration,
    format_datetime, Duration, UTC
)

# Parse dates (calendar, ordinal, week formats)
parse_date("2026-03-13")        # datetime.date(2026, 3, 13)
parse_date("2026-072")          # ordinal -> datetime.date(2026, 3, 13)
parse_date("2026-W11-5")        # week date -> datetime.date(2026, 3, 13)

# Parse times (with timezone support)
parse_time("14:30:00Z")         # datetime.time(14, 30, tzinfo=UTC)
parse_time("24:00:00")          # midnight -> datetime.time(0, 0)  (isodate #85 fix)

# Parse datetimes
parse_datetime("2026-03-13T14:30:00+01:00")

# Parse durations
dur = parse_duration("P1Y2M3DT4H5M6S")  # -> Duration(years=1, months=2, ...)
dur.total_seconds(reference=datetime.date(2026, 1, 1))  # requires ref (isodate #95 fix)

# Format with UTC -> Z suffix (isodate #89 fix)
format_datetime(datetime.datetime(2026, 3, 13, 14, 30, tzinfo=UTC))
# -> "2026-03-13T14:30:00Z"

# Duration arithmetic
Duration(months=1) + datetime.date(2026, 1, 31)  # -> datetime.date(2026, 2, 28)
```

## Intervals and Recurring Intervals

```python
from isochron import parse_interval, parse_recurring

# Start/end, start/duration, duration/end
iv = parse_interval("2026-01-01/P1M")

# Recurring intervals with iteration
for dt in parse_recurring("R3/2026-01-01/P1M"):
    print(dt)  # 2026-01-01, 2026-02-01, 2026-03-01
```

## Migrating from isodate

```python
# Before:
from isodate import parse_date, parse_datetime, ISO8601Error, Duration

# After (option 1 - direct):
from isochron import parse_date, parse_datetime, ParseError, Duration

# After (option 2 - compat shim):
from isochron.compat import parse_date, parse_datetime, ISO8601Error, Duration
```

The `isochron.compat` module maps all isodate public names to their isochron equivalents.

## API Reference

### Parsing

| Function | Input | Output |
|----------|-------|--------|
| `parse_date(s)` | `"2026-03-13"` | `datetime.date` |
| `parse_time(s)` | `"14:30:00Z"` | `datetime.time` |
| `parse_datetime(s)` | `"2026-03-13T14:30:00+01:00"` | `datetime.datetime` |
| `parse_duration(s)` | `"P1Y2M3DT4H5M6S"` | `Duration` or `timedelta` |
| `parse_interval(s)` | `"2026-01-01/2026-12-31"` | `Interval` |
| `parse_recurring(s)` | `"R3/2026-01-01/P1M"` | `RecurringInterval` |
| `parse_timezone(s)` | `"Z"`, `"+05:30"` | `tzinfo` |

### Formatting

| Function | Input | Output |
|----------|-------|--------|
| `format_date(d)` | `datetime.date` | `"2026-03-13"` |
| `format_time(t)` | `datetime.time` | `"14:30:00Z"` |
| `format_datetime(dt)` | `datetime.datetime` | `"2026-03-13T14:30:00Z"` |
| `format_duration(d)` | `Duration` or `timedelta` | `"P1Y2M3DT4H5M6S"` |
| `strftime(dt, fmt)` | date/datetime + format | custom string |

### Types

- **`Duration`** -- Immutable, hashable dataclass with `years`, `months`, `days`, `seconds`, `microseconds`. Supports arithmetic with dates, datetimes, and timedeltas.
- **`Interval`** -- Frozen dataclass with `start`, `end`, `duration`.
- **`RecurringInterval`** -- Iterable frozen dataclass with `recurrences` and `interval`.
- **`UTC`** -- Alias for `datetime.timezone.utc`.
- **`FixedOffset(offset_minutes)`** -- Fixed UTC-offset `tzinfo` subclass.

### Exceptions

- **`ISO8601Error`** -- Base exception for all isochron errors.
- **`ParseError`** -- Raised when input cannot be parsed. Has optional `string` and `position` attributes.
- **`FormatError`** -- Raised when a value cannot be formatted to ISO 8601.

### `strftime` Format Codes

`strftime(dt, fmt)` supports all standard Python `%` directives plus these ISO 8601 extras:

| Code | Description | Example |
|------|-------------|---------|
| `%G` | ISO week-based year | `2026` |
| `%V` | ISO week number (01–53) | `11` |
| `%u` | ISO weekday (1=Monday, 7=Sunday) | `5` |
| `%:z` | UTC offset as `+HH:MM` (vs `%z` → `+HHMM`) | `+05:30` |

## isodate Bugs Fixed

| Bug | Description |
|-----|-------------|
| #85, #86 | `T24:00:00` midnight accepted |
| #87 | 59.99999 to 60 second rounding handled |
| #89 | UTC formatted as `Z`, not `+00:00` |
| #90 | Second out-of-range handled gracefully |
| #95 | `total_seconds()` raises on non-fixed durations |
| #96 | Alternate format spurious `months=1` fixed |
| #97 | Ordinal date format extra days fixed |
| #98 | Negative year support |

## License

BSD-3-Clause
