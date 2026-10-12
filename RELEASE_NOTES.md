# Travel OS v0.4.20

This release closes a spreadsheet-formula injection path in imported or pasted travel data.

Travel OS archives now accept literal cell values only and reject workbook formulas. Import guidance also requires formula-like external text to remain text, preventing booking messages or pasted content from becoming executable spreadsheet formulas when a user opens the workbook.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 46 contract tests, including a malicious `WEBSERVICE` formula case.
