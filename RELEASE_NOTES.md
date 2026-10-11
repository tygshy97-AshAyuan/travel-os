# Travel OS v0.4.4

GitHub Early Access workflow update.

This release adds a review-first workflow for pasted or exported booking confirmations. Message content is treated as untrusted, sensitive fields stay out of the archive, and every extracted booking requires user review before writing.

It also adds an API-key-free Google Maps directions URL builder with ordered waypoints and travel modes. Release tags now run the full test suite and automatically publish a ZIP plus SHA-256 file from the exact tagged commit. The package passes 22 contract tests. Direct mailbox synchronization and supported-client behavior evaluation remain pending.
