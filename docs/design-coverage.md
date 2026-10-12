# Product design coverage

This file maps the v0.1 product design to the GitHub implementation so maintenance does not silently drift from the agreed scope.

| Design area | Implementation | Verification | Status |
|---|---|---|---|
| AI-native conversation entry | `SKILL.md` workflow and output contract | Current-tag Codex install, official Skill validator, reference-link test and full supported-client scenario | Installation and one complete client path verified; repeatability across models remains |
| Excel-first Trip Master | Eight-sheet `TravelOS-Template.xlsx` with minimum operational fields | Workbook schema, completeness, traveler-count, relationship and dependency-cycle tests; visual review | Implemented |
| Pre-trip planning | `planning-rules.md` and New trip workflow | Automated itinerary time-conflict tests; manual regression scenarios | Implemented in Skill |
| In-trip calibration | Execute workflow, local time zones, execution status, booking consistency and version rules | Automated archive, time-zone, booking and execution-history integrity tests; manual behavior scenario | Implemented in Skill |
| User profiling | `Preferences` with scope, evidence, confidence and validity dates | Automated preference integrity and lifecycle tests | Implemented |
| Source hierarchy | Official, traveler experience and AI reasoning roles | Automated current and historical confirmed-fact source and timestamp checks; manual behavior scenario | Implemented in Skill |
| Route, flight and hotel logic | `planning-rules.md` | Automated amount/currency integrity; manual behavior scenario | Implemented in Skill |
| Active Version recovery | Recovery protocol, Draft activation gate, stable version labels, valid historical snapshots, complete snapshots, chronological and auditable linear `Change Log`, and latest-version rule | Automated Active Version, label-format, historical-date/time, snapshot-completeness, audit-field, version-time, version-chain and unapproved-Draft tests | Implemented |
| Collaboration roles | `Members`, role permissions, complete Proposal lifecycle, bidirectional Owner approval and version traceability | Automated member-reference, Viewer boundary, proposal completeness, closure and proposal/version tests | Implemented |
| Post-trip learning | Review workflow, closed execution state and durable preference rules | Automated completion-state and preference integrity tests; supported-client behavior scenario | Implemented and client-validated |
| Weather re-planning | `weather-replanning.md`, fact states and atomic change workflow | Automated workflow contract; manual behavior scenarios | Implemented when a current weather source is available at runtime |
| Email booking parsing | Review-first import rules for pasted or exported confirmations; literal-value writes | Formula-injection test; Skill reference-link test; manual behavior scenario | Partial: direct mailbox sync is deferred |
| Map output | API-key-free directions URL builder | Automated URL test | Implemented for shareable route links |
| Automatic booking | Permission boundary only | None | Deferred P2 |
| Content generation and community learning | Outside MVP | None | Deferred P2 |

Automated tests validate deterministic package and archive rules. They do not claim that every AI client follows the Skill instructions; supported-client evaluations must be recorded separately when a stable test runner and model are selected.
