---
name: travel-os
description: Maintain a versioned travel plan from a user-provided workbook or itinerary, including change proposals, collaboration decisions, and recovery of the active version. Use when planning or revising a trip that needs a durable source of truth.
---

# Travel OS

Treat the user's travel archive as the source of truth. Read it before planning, identify the Active Version, and state which version you used.

## Workflow

1. Read the trip overview, active itinerary, confirmed bookings, constraints, open decisions and version history.
2. Flag missing or conflicting facts. Never invent reservation, visa, health, price, opening-hour or safety facts.
3. For a requested change, present a concise proposal with affected days, dependencies, trade-offs and facts that require current verification.
4. Apply the change only after the user accepts it. Create a new version, update Active Version, preserve the previous version record and note why the change occurred.
5. Record collaborator suggestions as Pending, Accepted, Rejected or Needs clarification. The trip owner resolves conflicts.
6. Return an execution view for the next relevant day and a short list of unresolved actions.

Use [references/archive-schema.md](references/archive-schema.md) when reading or writing the workbook. Use [references/versioning.md](references/versioning.md) for changes and collaboration.

## Boundaries

- Confirm time-sensitive transport, entry, weather, safety, availability and pricing from current reliable sources when tools allow; label anything unverified.
- Do not purchase, book, cancel or disclose private itinerary data without the user's explicit authorization.
- Minimize personal data and never place credentials or identity documents in the archive.
- If the archive is unavailable, build a draft and label it as a draft without an Active Version.
