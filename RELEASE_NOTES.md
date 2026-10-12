# Travel OS v0.4.32

This release makes itinerary and booking costs safe to compare.

Costs remain optional when unknown. Once entered, itinerary costs and booking amounts must be non-negative numbers, and each must be paired with a three-letter uppercase currency code such as `CNY` or `USD`.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 59 contract tests.
