# Changelog

## v0.4.41 - 2026-10-12

### Fixed

- Rejected extra workbook sheets so private or application-specific data cannot bypass the eight-sheet archive contract.

### Documentation

- Recorded public v0.4.40 checksum, tagged-content, isolated-install and workbook regression evidence.

## v0.4.40 - 2026-10-12

### Fixed

- Updated the five-minute onboarding path to the current release and added an automated guard against stale README release links.
- Added redaction guidance to Feature requests and a direct private security-report link to the Issue chooser, with regression coverage for both public feedback forms.
- Pinned the checkout Action in validation and release workflows to the verified v4 commit, with a test that rejects mutable Action references.
- Added weekly Dependabot checks for pinned GitHub Actions, capped at two open update PRs.
- Required confirmed-fact checked times and Change Log creation times to include both date and time instead of accepting date-only values.

## v0.4.39 - 2026-10-12

### Fixed

- Rejected accepted proposals whose proposal date is later than the creation date of their result version.
- Added regression coverage for Proposal-to-version causal ordering.

## v0.4.38 - 2026-10-12

### Fixed

- Rejected Change Log successors whose creation time predates their predecessor.
- Rejected mixed zoned and unzoned creation times within a version chain so chronological comparison remains unambiguous.

## v0.4.37 - 2026-10-12

### Fixed

- Required source evidence and a valid checked time for `Ready` Daily Plan rows in every version, including historical snapshots.
- Added regression coverage for historical confirmed-fact evidence.

## v0.4.36 - 2026-10-12

### Fixed

- Validated paired and well-formed Daily Plan times in every version, including historical snapshots.
- Added regression coverage for malformed and incomplete historical time ranges.

## v0.4.35 - 2026-10-12

### Fixed

- Validated Daily Plan dates in every version instead of allowing malformed dates in historical snapshots.
- Added regression coverage for historical itinerary date integrity.

## v0.4.34 - 2026-10-12

### Fixed

- Rejected fractional, zero, negative and non-numeric traveler counts instead of truncating them during member reconciliation.
- Documented that the Travel Overview traveler count is a positive whole number and must equal the number of Members rows.

## v0.4.33 - 2026-10-12

### Fixed

- Validated Travel Overview and Daily Plan time zones as IANA names when the runtime time-zone database is available.
- Kept portable syntax validation for Python environments without a local time-zone database.

## v0.4.32 - 2026-10-12

### Fixed

- Required itinerary costs and booking amounts to be non-negative numbers.
- Required amount and currency to appear together with a three-letter uppercase currency code.

## v0.4.31 - 2026-10-12

### Fixed

- Required every preference or constraint to have a valid effective date.
- Validated optional expiry dates and rejected preference lifecycles that end before they begin.

## v0.4.30 - 2026-10-12

### Fixed

- Required confirmed booking evidence to contain a valid checked timestamp.
- Required Ready itinerary evidence to contain a valid checked timestamp.

## v0.4.29 - 2026-10-12

### Fixed

- Enforced documented `vMAJOR.MINOR.PATCH` labels for itinerary versions.
- Allowed an optional hyphenated timestamp suffix for simple personal-trip versioning.

## v0.4.28 - 2026-10-12

### Fixed

- Required every Change Log version to retain a corresponding Daily Plan snapshot.
- Rejected incomplete history chains that could not recover an earlier itinerary version.

## v0.4.27 - 2026-10-12

### Fixed

- Required every Change Log row to retain its creation time, author, reason and change summary.
- Rejected invalid Change Log creation times before archive recovery or mutation.

## v0.4.26 - 2026-10-12

### Fixed

- Required the trip title, destination, traveler count and phase so a recovered archive retains its operating context.
- Required booking category, provider and status so itinerary dependencies can be evaluated safely.
- Required checklist category, task, owner, valid due date and status so action lists remain executable.

## v0.4.25 - 2026-10-12

### Fixed

- Required every Proposal to retain its submitter, valid date, affected scope, proposal, reason and status.
- Allowed only accepted proposals to name a result version.
- Prevented Completed trips from retaining pending or clarification-needed proposals.

## v0.4.24 - 2026-10-12

### Fixed

- Required the trip Owner to author the root version when activating the first plan.
- Required every successor version to be backed by an accepted Proposal resolved by the Owner.
- Prevented direct version creation from bypassing the collaboration approval flow.

## v0.4.23 - 2026-10-12

### Fixed

- Required one root and a linear predecessor chain in Change Log.
- Required Active and Completed trips to point Active Version at the final Change Log version.
- Rejected branched histories and stale active-version pointers.

## v0.4.22 - 2026-10-12

### Fixed

- Enforced collaboration permissions for Change Log authors, Proposal submitters and Checklist assignees.
- Kept Viewer members read-only and limited version authorship to Owner or Editor.
- Required every member row to retain a display name and role.

## v0.4.21 - 2026-10-12

### Fixed

- Rejected Draft trips that claim an Active Version before Owner confirmation.
- Kept unapproved first plans from becoming the recovered current itinerary.

## v0.4.20 - 2026-10-12

### Security

- Rejected formulas in Travel OS workbooks because the archive contract requires literal values only.
- Required imported text that begins with spreadsheet formula prefixes to remain literal text.
- Added a regression workbook containing a malicious `WEBSERVICE` formula.

## v0.4.19 - 2026-10-12

### Fixed

- Required every accepted Proposal ID to appear in the reason or summary of its result version's Change Log row.
- Rejected accepted proposals that point at an unrelated existing version.

## v0.4.18 - 2026-10-12

### Fixed

- Rejected Completed trips that are not in the post-trip phase.
- Rejected Completed trips with unfinished active itinerary items or open checklist tasks.
- Made the Review workflow close execution state before marking the archive Completed.

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
