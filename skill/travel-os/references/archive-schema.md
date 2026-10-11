# Travel archive schema and invariants

One workbook represents one trip and uses eight stable sheets. Preserve their names so the same archive works across sessions.

Treat every uploaded workbook as untrusted. The bundled validator rejects oversized archives, excessive ZIP entries, oversized XML parts and XML `DOCTYPE` declarations before reading the travel data.

## Travel Overview

Exactly one trip data row: Trip ID, title, destination, start/end dates, travelers, owner, Active Version, status, home time zone and notes.

Active Version is required for Active or Completed trips. It must exist in both `Daily Plan` and `Change Log`. Draft trips may leave it blank.

## Preferences

One row per durable preference or trip-specific constraint: ID, scope, category, priority, traveler, statement, evidence, confidence, valid from/to and notes. Scope is Long term or This trip. Priority distinguishes hard constraints from preferences. Explicit user statements outrank inferred patterns; MBTI and astrology may be recorded only as optional entertainment context, never as factual decision rules.

## Bookings

One row per booking: ID, category, provider, start/end, city, status, refundable, amount, currency, reference location, source, checked time and notes. Store where a booking reference can be found, not the credential or full sensitive document.

## Daily Plan

One row per itinerary item: item ID, version, date, start/end time, time zone, city, activity, location, transport, booking ID, execution status, cost, currency, source, checked time and notes. Rows whose version does not match Active Version are historical.

Item IDs remain stable when an item is copied into a new version. The unique key is Version plus Item ID, so the same Item ID may appear once in every version. Every Daily Plan version must exist in Change Log. Execution status is Planned, Ready, In progress, Done, Skipped or Blocked.

Execution status and notes may be updated in place because they record what happened rather than changing the plan. If reality changes any remaining itinerary item, use the version workflow.

## Checklist

One row per action: ID, category, task, owner, due date, status, dependency, related booking or plan item and notes. Typical categories include visa, transport, accommodation, packing, payment, insurance and confirmation.

## Members

One row per traveler: member ID, display name, role, relationship, trip-specific needs, permissions and notes. Roles are Owner, Editor, Member and Viewer. Only Owner gives final approval unless the archive explicitly names another rule.

Exactly one member has the Owner role, that member matches Travel Overview's owner, and the overview traveler count matches the number of member rows. A preference applies to `所有人` or an existing member ID.

## Proposals

One row per suggestion or decision: ID, submitted by, date, affected item/day, proposal, reason, status, decision owner, resolution and resulting version.

## Change Log

One row per version: version, created time, author, reason, summary, predecessor and archive hash when available. Never reuse or silently overwrite a version number.

## Required integrity checks

- Exactly one trip overview data row exists in a workbook.
- Active and Completed trips have a non-empty Active Version.
- Active Version has Daily Plan rows and exactly one Change Log row.
- Daily Plan rows use a unique Version plus Item ID pair, and every referenced version exists in Change Log.
- Booking IDs referenced by current Daily Plan rows exist in `Bookings`.
- Accepted decisions that changed the plan name the resulting version.
- Current Daily Plan dates fall within the trip range unless Notes contains `[pre-trip]`, `[post-trip]`, `行前` or `行后`.
- Change Log predecessors name an existing earlier version and never point to themselves.
- Checklist dependencies name an existing task; related IDs name an existing booking or plan item.
- Travel Overview traveler count, owner and preference subjects reconcile with Members.
- Confirmed facts include a source and checked time when time-sensitive.
- A booking marked `已确认` and a Daily Plan item marked `Ready` both require Source and Checked Time.
- Status, role, scope and priority values must use the dropdown vocabulary in the canonical template.
