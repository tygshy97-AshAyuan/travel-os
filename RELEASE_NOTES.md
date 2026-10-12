# Travel OS v0.4.36

This release protects version recovery from malformed historical itinerary times.

Daily Plan start and end times are now checked in every version. Historical rows can no longer pass with only one endpoint, an invalid clock value or a reversed range without an overnight marker.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 63 contract tests.
