# Travel OS v0.4.40

This release makes fact and version timestamps precise enough for audit and staleness checks.

Confirmed booking and `Ready` itinerary checked times, plus Change Log creation times, must now include both a date and a time. Date-only text no longer passes as a timestamp; native Excel date-time values remain supported.

This release also includes the current-download guard, safer public feedback forms, pinned workflow Actions and weekly Dependabot checks merged since v0.4.39. Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 71 contract tests.
