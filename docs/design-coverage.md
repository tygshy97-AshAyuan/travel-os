# Product design coverage

This file maps the v0.1 product design to the GitHub implementation so maintenance does not silently drift from the agreed scope.

| Design area | Implementation | Verification | Status |
|---|---|---|---|
| AI-native conversation entry | `SKILL.md` workflow and output contract | Skill reference-link test | Implemented |
| Excel-first Trip Master | Eight-sheet `TravelOS-Template.xlsx` | Workbook schema, relationship and dependency-cycle tests; visual review | Implemented |
| Pre-trip planning | `planning-rules.md` and New trip workflow | Manual regression scenarios | Implemented in Skill |
| In-trip calibration | Execute workflow, execution status, booking consistency and version rules | Automated archive and booking integrity tests; manual behavior scenario | Implemented in Skill |
| User profiling | `Preferences` with scope, evidence and confidence | Automated preference integrity tests | Implemented |
| Source hierarchy | Official, traveler experience and AI reasoning roles | Manual behavior scenario | Implemented in Skill |
| Route, flight and hotel logic | `planning-rules.md` | Manual behavior scenario | Implemented in Skill |
| Active Version recovery | Recovery protocol, `Daily Plan`, `Change Log` | Automated Active Version test | Implemented |
| Collaboration roles | `Members`, `Proposals`, owner approval | Automated member-reference and Owner-decision tests | Implemented |
| Post-trip learning | Review workflow and durable preference rules | Automated preference integrity tests; manual behavior scenario | Implemented in Skill |
| Weather re-planning | `weather-replanning.md`, fact states and atomic change workflow | Automated workflow contract; manual behavior scenarios | Implemented when a current weather source is available at runtime |
| Email booking parsing | Review-first import rules for pasted or exported confirmations | Skill reference-link test; manual behavior scenario | Partial: direct mailbox sync is deferred |
| Map output | API-key-free directions URL builder | Automated URL test | Implemented for shareable route links |
| Automatic booking | Permission boundary only | None | Deferred P2 |
| Content generation and community learning | Outside MVP | None | Deferred P2 |

Automated tests validate deterministic package and archive rules. They do not claim that every AI client follows the Skill instructions; supported-client evaluations must be recorded separately when a stable test runner and model are selected.
