# Travel OS v0.4.23

This release prevents recovery from selecting a stale or ambiguous plan history.

Change Log must now contain exactly one root followed by a linear predecessor chain. For Active and Completed trips, Active Version must point to the final version in that chain. Branched histories, multiple roots and stale active pointers are rejected before planning or edits continue.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 50 contract tests.
