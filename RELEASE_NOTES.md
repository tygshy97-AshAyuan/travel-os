# Travel OS v0.4.18

This release prevents a trip from being closed while its operational state is still unfinished.

An archive marked `Completed` must now be in the post-trip phase, every active itinerary item must be `Done` or `Skipped`, and every checklist task must be completed or cancelled. This keeps recovery and post-trip learning from treating unresolved plans as finished history.

The stricter validator accepts the previously generated end-to-end fictional workbook. The package passes 44 contract tests.
