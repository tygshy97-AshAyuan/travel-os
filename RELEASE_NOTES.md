# Travel OS v0.4.41

This release enforces the documented eight-sheet archive boundary.

The validator now rejects extra workbook sheets. This keeps every stored field inside the validated Travel OS contract and prevents private notes, formulas or application-specific state from silently bypassing archive checks.

Both canonical workbooks remain unchanged and pass the stricter validator. The package passes 72 contract tests.
