"""Benchmarks for isochron vs isodate (and aniso8601 if available)."""

from __future__ import annotations

import datetime
import timeit


def bench(label: str, stmt: str, setup: str, number: int = 1000) -> float:
    """Run a benchmark and print results."""
    try:
        t = timeit.timeit(stmt, setup=setup, number=number)
        us = t / number * 1_000_000
        print(f"  {label}: {us:.1f} \u00b5s/op ({number} iterations)")
        return us
    except Exception as e:
        print(f"  {label}: SKIPPED ({e})")
        return 0.0


def main() -> None:
    print("=" * 60)
    print("isochron benchmarks")
    print("=" * 60)

    print("\n--- parse_date ---")
    bench(
        "isochron",
        'parse_date("2026-03-13")',
        "from isochron import parse_date",
    )
    bench(
        "isodate",
        'parse_date("2026-03-13")',
        "from isodate import parse_date",
    )
    bench(
        "aniso8601",
        'parse_date("2026-03-13")',
        "from aniso8601 import parse_date",
    )

    print("\n--- parse_time ---")
    bench(
        "isochron",
        'parse_time("14:30:00Z")',
        "from isochron import parse_time",
    )
    bench(
        "isodate",
        'parse_time("14:30:00Z")',
        "from isodate import parse_time",
    )

    print("\n--- parse_datetime ---")
    bench(
        "isochron",
        'parse_datetime("2026-03-13T14:30:00+01:00")',
        "from isochron import parse_datetime",
    )
    bench(
        "isodate",
        'parse_datetime("2026-03-13T14:30:00+01:00")',
        "from isodate import parse_datetime",
    )

    print("\n--- parse_duration ---")
    bench(
        "isochron",
        'parse_duration("P1Y2M3DT4H5M6S")',
        "from isochron import parse_duration",
    )
    bench(
        "isodate",
        'parse_duration("P1Y2M3DT4H5M6S")',
        "from isodate import parse_duration",
    )

    print("\n--- format_datetime ---")
    setup_isochron = (
        "import datetime; from isochron import format_datetime; "
        "dt = datetime.datetime(2026, 3, 13, 14, 30, 0, tzinfo=datetime.timezone.utc)"
    )
    setup_isodate = (
        "import datetime; from isodate import datetime_isoformat; "
        "dt = datetime.datetime(2026, 3, 13, 14, 30, 0, tzinfo=datetime.timezone.utc)"
    )
    bench("isochron", "format_datetime(dt)", setup_isochron)
    bench("isodate", "datetime_isoformat(dt)", setup_isodate)

    print()


if __name__ == "__main__":
    main()
