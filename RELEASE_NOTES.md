# Travel OS v0.4.14

Execution-history integrity update.

Every Daily Plan row now requires an item ID, version, date, time zone, activity and execution status. Partially written itinerary rows can no longer pass validation and disappear from recovery.

When a new version succeeds another, Done and Skipped items must remain present with the same stable ID and status. The release includes a directly installable `Travel-OS-Skill-v0.4.14.zip`, the full repository archive and checksums for both. The package passes 39 contract tests.
