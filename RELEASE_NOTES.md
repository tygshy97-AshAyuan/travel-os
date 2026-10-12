# Travel OS v0.4.31

This release gives durable preferences a verifiable lifecycle.

Every preference or constraint now requires a valid effective date. Optional expiry dates must also be valid and cannot precede the effective date, so recovery can distinguish current memory from expired trip context.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 58 contract tests.
