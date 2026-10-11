# Travel OS v0.4.2

GitHub Early Access archive-safety update.

This release adds a zero-dependency validator that an Agent can run before reading and after writing a Travel OS workbook. It checks the eight-sheet schema, exact headers, trip ownership, Active Version, version history, booking and member references, duplicate IDs, and accepted proposal results.

The repository now also publishes a roadmap, contribution guide and security policy. Private vulnerability reporting is enabled, and main requires a pull request plus a passing validation check. AI behavior still requires supported-client evaluation because the repository does not call a paid model during CI.
