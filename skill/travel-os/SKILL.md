---
name: travel-os
description: Plan, execute and maintain a trip from a workbook or itinerary with durable state, versioned changes, verified facts and collaboration decisions. Use for new trip planning, itinerary changes, daily execution, or cross-session recovery.
---

# Travel OS

Travel OS follows `Planning → Execution → Memory → Collaboration`. The travel archive is the durable source of truth; chat history is context only.

For a new trip, copy [assets/TravelOS-Template.xlsx](assets/TravelOS-Template.xlsx). One workbook represents one trip.

## Start every session with recovery

1. Read all archive sheets and validate the archive using [references/archive-schema.md](references/archive-schema.md).
   When Python execution is available, run `python scripts/validate_archive.py <workbook.xlsx>` before reading and after every write.
2. Resolve Active Version from `Travel Overview`; use only matching `Daily Plan` rows as the current plan.
3. Reconcile hard constraints, confirmed bookings, open decisions and execution events. A confirmed booking or hard constraint wins over an unconfirmed itinerary row.
4. State the Trip ID, Active Version, archive status, unresolved conflicts, stale facts and the next action before planning or editing.
5. If recovery fails, stop writes and explain the smallest repair needed. Do not guess which version is current.

## Choose the workflow

- **New trip:** collect only decision-driving facts, distinguish hard constraints from preferences, create a Draft, expose assumptions and request confirmation before activating it.
- **Plan or optimize:** preserve confirmed bookings and hard constraints; compare alternatives by time, cost, fatigue, risk and user priorities. Verify time-sensitive facts before relying on them.
- **Change:** follow the proposal and atomic version update in [references/versioning.md](references/versioning.md).
- **Execute:** return the next actionable block, local time, transport buffer, booking reference location, current verification state and fallback. Record actual progress in the active `Daily Plan` row's execution status and notes; version only changes that affect the remaining plan.
- **Collaborate:** record each suggestion and its owner-visible status. Never treat silence or a vote as authority unless the trip owner defined that rule.
- **Resume:** run recovery again even if the chat claims to remember the trip.
- **Review:** after the trip, compare planned and actual outcomes, close tasks, record reusable lessons, and update Preferences only from explicit feedback or repeated observed choices. Never infer sensitive traits.

Read [references/operating-rules.md](references/operating-rules.md) for planning, verification and execution rules.
Read [references/planning-rules.md](references/planning-rules.md) before researching destinations or building a route.

## Output contract

Keep answers operational. Identify the version used, separate confirmed facts from assumptions, show conflicts before recommendations, and finish with unresolved decisions and the next action. When proposing a write, list every sheet and row type that will change.

## Boundaries

- Confirm time-sensitive transport, entry, weather, safety, availability and pricing from current reliable sources when tools allow; record source and checked time, and label anything unverified or stale.
- Do not purchase, book, cancel or disclose private itinerary data without the user's explicit authorization.
- Minimize personal data and never place credentials or identity documents in the archive.
- Do not overwrite history, silently resolve conflicts, or update Active Version before all new-version rows and the version record are written successfully.
- If the archive is unavailable, build a Draft without claiming an Active Version or cross-session memory.
