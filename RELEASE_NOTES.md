# Travel OS v0.4.37

This release protects the evidence trail in historical itinerary snapshots.

Every `Ready` Daily Plan row now requires a source and valid checked time, including rows from historical versions. Confirmed travel facts therefore retain their evidence when plans are versioned and recovered later.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 64 contract tests.
