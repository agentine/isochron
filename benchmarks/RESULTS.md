# Benchmark Results

**Environment:** Python 3.14, macOS Darwin 25.3.0
**Date:** 2026-03-13
**Method:** timeit, 1000 iterations per operation

## isochron vs isodate

| Operation        | isochron (µs/op) | isodate (µs/op) | Speedup |
|-----------------|----------------:|----------------:|--------:|
| parse_date      |             0.7 |             1.5 |   2.1×  |
| parse_time      |             1.3 |             2.9 |   2.2×  |
| parse_datetime  |             4.2 |             4.7 |   1.1×  |
| parse_duration  |             3.5 |             6.4 |   1.8×  |
| format_datetime |             2.4 |             4.4 |   1.8×  |

isochron is **1.1×–2.2× faster** than isodate across all operations.
