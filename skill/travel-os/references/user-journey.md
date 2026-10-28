# User journey and result presentation

Read this when starting or resuming a trip and when deciding what to present after planning, execution or review. Archive and version invariants remain in their existing references.

## Start from the user's situation

| Situation | First useful result | Next step |
| --- | --- | --- |
| New trip, no workbook | A route outline using the destination, duration, interests and fixed commitments already provided | Resolve only the missing choice that changes the route |
| Destination or dates still open | Meaningfully different directions, or a Day 1 / Day 2 outline with explicit assumptions | Narrow the direction; collect dates when they affect feasibility or saving |
| Existing itinerary or confirmations | Extract fixed arrangements and show gaps or conflicts | Review facts before importing; distinguish suggestions from confirmed bookings |
| Continue a trip | Recover the supplied archive, then show what is settled and the next action | Resolve a relevant conflict or continue the requested work |
| Already traveling | Today's next actionable block and fallback | Record progress, or propose a change to the affected remainder |
| Finished traveling | Compare what worked and what changed | Confirm reusable preferences and close outstanding items before completion |

This is routing guidance, not a menu to make every user choose from. Reuse answers already given. Ask only when the answer changes the next result; do not require completion of a questionnaire. A narrow route request does not need a flight or hotel search first. Query those services only when relevant to the user's request and available in the host.

## First value before archive setup

For a new trip, provide a concrete provisional route as soon as there is enough information. Highlight the experience, approximate pace, major transfers and fixed arrangements. Compare alternatives only for a meaningful decision, not for an already specific request.

Use Day 1 / Day 2 for undated ideas in chat. Date-dependent opening, seasonal events and prices remain conditional until checked against actual dates. Follow planning rules for sources; an outline is not a verified booking or confirmed executable itinerary.

When the host can access bundled assets, create a new copy of the template itself. The user should not have to find, fill or upload it. Before initializing a workbook, obtain required dates, owner, traveler count and time zones; use approved member display labels, not invented identities. Keep Active Version empty while the archive is Draft. Schema-required dates must be real calendar dates, never Day 1 placeholders or fabricated defaults.

If file access or writing is unavailable, continue with a clearly labeled unsaved draft and say what is needed to save it. Missing required fields do not block exploration, but do block claiming a valid archive. For an existing trip, a missing file blocks reliable recovery and writes: request that file rather than starting over.

## Present the useful view for this moment

- **Plan:** show a compact overview and day-by-day route with travel and rest time, fixed bookings, outstanding decisions and relevant map links. Explain tradeoffs in travel terms. Do not lead with sheet names, Trip IDs or validation logs.
- **Ready to save:** summarize what will become the current plan and important unknowns. Explicit acceptance of this plan is sufficient; do not ask for a special command or another generic confirmation. Save and validate before reporting success. Provide the actual latest workbook and explain that it is needed when switching clients or conversations without persistent file access.
- **Today:** lead with where to go next, when to leave in local time, transfer buffer and fallback. Do not repeat the whole archive after every progress update.
- **Change:** show the affected original arrangement, proposed replacement and consequences for time, cost and bookings. Preserve fixed commitments and completed history. Obtain the required Owner decision, then use atomic versioning and return the new file. A collaborator's suggestion alone is not approval.
- **Share:** provide a reviewable summary with private references and lodging details removed. Existing directions links are not a hosted interactive journal. Do not claim a public link exists, publish a file or send it to companions without the requested sharing scope and appropriate authorization.
- **Review:** record concrete feedback and name what should carry into another trip. One workbook remains one trip; cross-trip reuse requires access to previous preferences and user intent to reuse them. Do not promise automatic memory across disconnected clients.

Use plain labels such as provisional plan, current plan and saved file in the user's language. Retain a short version/save-status line for traceability. Surface conflicts and unavailable capabilities when they affect a decision. Finish with the next useful action; if the request is fulfilled, a new question is unnecessary.
