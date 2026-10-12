# Travel OS v0.4.42

This release makes damaged workbooks safer and easier to repair.

Shortened Travel Overview rows now report each missing field, and changed or missing headers return a schema error. The command-line validator catches other malformed structures and returns a normal validation failure instead of exposing a traceback.

The README quickstart also starts from a blank template and lets the AI initialize the workbook from a natural-language trip request. Both canonical workbooks remain unchanged and pass the validator. The package passes 74 contract tests.
