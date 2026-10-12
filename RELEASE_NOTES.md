# Travel OS v0.4.34

This release protects trip recovery from malformed traveler counts.

Travel Overview now rejects fractional, zero, negative and non-numeric traveler counts. A valid count remains required to match the number of Members rows, so values such as `2.5` can no longer be silently truncated to `2`.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 61 contract tests.
