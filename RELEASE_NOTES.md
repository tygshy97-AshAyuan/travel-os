# Travel OS v0.4.21

This release enforces the first-plan approval boundary.

A trip in `Draft` status can no longer claim an Active Version. The Owner must confirm the first plan before it becomes the current itinerary, preventing recovery from treating an unapproved draft as established trip state.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 47 contract tests.
