# Travel OS v0.4.35

This release protects version recovery from malformed historical itinerary dates.

Daily Plan dates are now validated in every version, not only the active version. A damaged historical snapshot can no longer pass validation and later undermine audit or recovery.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 62 contract tests.
