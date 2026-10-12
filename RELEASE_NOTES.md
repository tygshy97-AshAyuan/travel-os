# Travel OS v0.4.28

This release prevents empty versions from creating gaps in itinerary history.

Every Change Log version must now retain a corresponding Daily Plan snapshot. Travel OS rejects an archive when a historical version number exists but its itinerary rows are missing, instead of pretending that the version can be recovered.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 55 contract tests.
