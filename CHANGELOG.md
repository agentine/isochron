# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-03-13

### Added

- Full ISO 8601:2004 parsing and formatting
- `parse_date()` — calendar, ordinal, and week date formats
- `parse_time()` — with fractional seconds and timezone offsets
- `parse_datetime()` — combined date and time
- `parse_duration()` — standard, week, and alternate formats
- `parse_interval()` — start/end, start/duration, duration/end
- `parse_recurring()` — recurring intervals with iteration support
- `parse_timezone()` — Z, +HH:MM, +HHMM, +HH offset parsing
- `Duration` class — immutable, hashable, supports year/month components
- `Interval` and `RecurringInterval` data classes
- `format_date()`, `format_time()`, `format_datetime()`, `format_duration()`
- `strftime()` with ISO 8601 extras: `%G`, `%V`, `%u`, `%:z`
- `UTC` and `FixedOffset` timezone utilities
- `isochron.compat` — drop-in replacement for `isodate` imports
- PEP 561 py.typed marker for type checker support

### Fixed (vs isodate)

- #85, #86: Accept `T24:00:00` as valid midnight representation
- #87: Handle `59.99999` rounding to 60 seconds
- #89: `format_datetime()` outputs `Z` for UTC (not `+00:00`)
- #90: Second-out-of-range errors handled gracefully
- #95: `Duration.total_seconds()` raises `ValueError` instead of silent `0`
- #96: Alternate duration format no longer produces spurious `months=1`
- #97: Ordinal date format no longer adds extra days
- #98: Negative year support in date parsing
