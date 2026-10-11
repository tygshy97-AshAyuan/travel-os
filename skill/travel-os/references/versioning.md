# Versioning and collaboration

Use `vMAJOR.MINOR.PATCH` labels. Increment PATCH for ordinary itinerary edits, MINOR for structural changes across several days, and MAJOR when the trip scope changes. For a simple personal trip, a timestamped suffix is acceptable if it remains unique.

Before a write, summarize the proposed change, affected items, dependencies, confirmed bookings, constraints and facts requiring verification.

Apply an accepted change atomically:

1. Choose a unique next version and record its predecessor.
2. Copy every active itinerary row to the new version, retaining stable item IDs.
3. Apply accepted edits to the copied rows.
4. Add or update related bookings, decisions and execution events.
5. Validate the new version against archive invariants.
6. Append one version-history row.
7. Update Active Version last.

If any step fails, leave Active Version unchanged and report the partial write. Never delete the prior version.

Suggestions remain Pending until the trip owner resolves them. Accepted suggestions must name the resulting version. Rejected suggestions retain a short reason. Conflicting accepted suggestions require clarification before the itinerary changes.

Execution events do not create a new version when they only record what happened. Create a new version when a deviation changes any remaining itinerary item, booking dependency, cost commitment or hard constraint.
