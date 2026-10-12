# Changelog

## v0.4.17 - 2026-10-12

### Verified

- Completed an installed-Skill end-to-end run on the fictional workbook: recovery, Owner-approved version change, execution update, unavailable-weather fallback and post-trip preference writeback.
- Revalidated the generated workbook with the repository validator, a formula-error scan and rendered-sheet inspection.

## v0.4.16 - 2026-10-12

### Fixed

- Replaced non-ASCII arrows that broke a legacy Windows Skill validator using the GBK locale.
- Added an automated ASCII compatibility check for `SKILL.md`.

### Added

- Recorded Codex GitHub installation and official Skill validation evidence.

## v0.4.15 - 2026-10-12

### Fixed

- Validated paired local start/end times on current itinerary rows.
- Required an explicit overnight marker for cross-midnight activities.
- Rejected overlapping executable activities in the same time zone.

## v0.4.14 - 2026-10-12

### Fixed

- Required the minimum executable fields on every Daily Plan row.
- Prevented successor versions from dropping Done or Skipped items.
- Prevented successor versions from regressing completed execution states.

## v0.4.13 - 2026-10-12

### Fixed

- Validated booking start/end order and consistent time-zone notation.
- Rejected current executable itinerary rows that reference cancelled bookings.
- Required `Ready` itinerary rows to use confirmed or completed bookings.

## v0.4.12 - 2026-10-12

### Fixed

- Rejected direct and indirect dependency cycles in Checklist tasks.
- Added a regression test for two tasks waiting on each other.

## v0.4.11 - 2026-10-12

### Added

- Added a bounded weather re-planning workflow with forecast-window checks.
- Preserved completed history, hard constraints and confirmed bookings during weather changes.
- Added regression scenarios for unavailable and localized forecasts.

## v0.4.10 - 2026-10-12

### Fixed

- Required the trip Owner to decide every accepted or rejected proposal.
- Required resolved proposals to retain a written resolution.
- Kept accepted proposals linked to a valid resulting version.

## v0.4.9 - 2026-10-12

### Fixed

- Rejected filled workbook rows that omit their sheet-specific ID.
- Required every preference to name its scope, category, priority, subject, statement, evidence and confidence.
- Added explicit post-trip rules for evidence-backed durable preferences.

## v0.4.8 - 2026-10-12

### Fixed

- Recognized an untouched canonical workbook as a safe, uninitialized template.
- Let the command-line validator return `READY` so first-time users can enter the New trip workflow.
- Kept populated archives on the strict recovery and integrity-validation path.

## v0.4.7 - 2026-10-12

### Fixed

- Allowed a stable Daily Plan item ID to be carried across plan versions.
- Enforced uniqueness by Version plus Item ID within Daily Plan.
- Rejected Daily Plan rows whose version is missing from Change Log.

## v0.4.6 - 2026-10-11

### Added

- Added client-facing Skill metadata, icon and default recovery prompt.
- Added a direct-install Skill ZIP with `SKILL.md` at the archive root.
- Included both the source and Skill archives in the release checksum file.
- Verified the Skill ZIP structure during automated release creation.

## v0.4.5 - 2026-10-11

### Added

- Added README previews rendered from the fictional example workbook.
- Added XLSX limits for ZIP entries, uncompressed bytes and individual XML parts.
- Rejected XML DOCTYPE declarations before archive parsing.
- Reported workbook file-access failures as validation errors.

## v0.4.4 - 2026-10-11

### Added

- Added a review-first booking import workflow for pasted or exported confirmations.
- Treated imported message content as untrusted and excluded sensitive raw fields.
- Added an API-key-free Google Maps directions URL builder.
- Added regression cases for malicious booking messages and route links.
- Automated tag-based test, ZIP, SHA-256 and prerelease creation.

## v0.4.3 - 2026-10-11

### Fixed

- Enforced required overview fields and valid trip date ranges.
- Checked current-plan dates, version predecessors, checklist links and accepted proposal results.
- Validated dropdown vocabularies after pasted or programmatic edits.
- Required source and checked time for confirmed bookings and Ready itinerary items.
- Required exactly one Owner and reconciled traveler count and preference subjects with Members.

## v0.4.2 - 2026-10-11

### Added

- Added a standard-library archive validator inside the installable Skill.
- Validated sheet names, headers, trip ownership, Active Version, version history, references, duplicate IDs and accepted proposal results.
- Added a public roadmap, contribution guide, pull-request checklist and security policy.
- Enabled private vulnerability reporting.
- Protected main with required pull requests, passing validation and resolved conversations.

## v0.4.1 - 2026-10-11

### Fixed

- Bundled the canonical blank Excel template inside the installable Skill.
- Separated the blank template from the fictional completed example.
- Defined where execution-only updates are stored without creating a new version.
- Preserved empty Excel columns when validating archive relationships.
- Added native table filters to all eight workbook sheets.
- Extended credential scanning into XLSX contents and prevented blank public issues.
- Removed duplicate branch and pull-request CI runs.

## v0.4.0 - 2026-10-11

### Changed

- Completed the Planning, Execution, Memory and Collaboration operating model.
- Added recovery, fact-state, constraint-priority and atomic version-write rules.
- Expanded the workbook schema for constraints, bookings and execution state.
- Replaced file-presence CI with executable archive contract tests.
- Removed creator-platform-specific packaging and documentation.

## v0.3.1 - 2026-10-11

### Added

- Single-file Markdown package for creator-platform submission.
- Standard Agent Skill directory and references.
- Excel travel archive with overview, active itinerary, decisions and version history.
- Five-minute user guide, feedback form and regression scenarios.
- GitHub Issue templates and basic validation workflow.

### Safety

- Public feedback templates warn users not to disclose travel or identity data.
- The template contains fictional examples only and no external connections.

### Known limitations

- Third-party creator-platform upload and review were not validated.
- Travel OS does not provide live booking, price or safety guarantees.
