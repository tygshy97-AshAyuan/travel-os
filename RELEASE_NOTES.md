# Travel OS v0.4.33

This release protects local-time execution from missing or misspelled time zones.

Travel Overview and every Daily Plan row now use IANA names such as `Asia/Shanghai` or `America/New_York`. The validator checks the installed time-zone database when available and retains a portable syntax check when it is not.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 60 contract tests.
