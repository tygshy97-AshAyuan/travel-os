# Travel OS v0.4.38

This release makes version-history time order auditable.

Change Log successors can no longer predate their predecessors or mix zoned and unzoned creation times within the chain. Recovery now rejects histories whose row order and timestamps disagree.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 65 contract tests.
