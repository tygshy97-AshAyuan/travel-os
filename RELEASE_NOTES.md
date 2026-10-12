# Travel OS v0.4.29

This release makes itinerary version labels predictable across sessions and clients.

Change Log versions must now use `vMAJOR.MINOR.PATCH`. A hyphenated timestamp suffix such as `v0.1.1-20300401T020000Z` remains supported for simple personal trips. Ambiguous labels such as `latest` or `final-final` are rejected before recovery.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 56 contract tests.
