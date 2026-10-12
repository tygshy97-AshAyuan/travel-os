# Travel archive schema and invariants

One workbook represents one trip and uses eight stable sheets. Preserve their names so the same archive works across sessions.

Treat every uploaded workbook as untrusted. The bundled validator rejects oversized archives, excessive ZIP entries, oversized XML parts and XML `DOCTYPE` declarations before reading the travel data.

A canonical workbook with the exact eight-sheet schema and no data rows is an uninitialized template. The command-line validator reports it as `READY` so the New trip workflow can initialize it; it is not yet a valid or recovered trip archive.

## Travel Overview

Exactly one trip data row: Trip ID, title, destination, start/end dates, travelers, owner, Active Version, phase, status, home time zone and notes. Every field except Active Version and notes is required; Draft leaves Active Version empty.

Active Version is required for Active or Completed trips. It must exist in both `Daily Plan` and `Change Log`. A Draft has no Active Version until the Owner confirms the first plan.

## Preferences

One row per durable preference or trip-specific constraint: ID, scope, category, priority, traveler, statement, evidence, confidence, valid from/to and notes. Scope is Long term or This trip. Priority distinguishes hard constraints from preferences. Explicit user statements outrank inferred patterns; MBTI and astrology may be recorded only as optional entertainment context, never as factual decision rules.

Every preference row requires its ID, scope, category, priority, subject, statement, evidence and confidence. Evidence must say whether the preference came from an explicit statement or a repeated observed choice; a guess from one event is not a durable preference.

## Bookings

One row per booking: ID, category, provider, start/end, city, status, refundable, amount, currency, reference location, source, checked time and notes. ID, category, provider and status are required. Store where a booking reference can be found, not the credential or full sensitive document.

When both booking times are present, use consistent time-zone notation and ensure the end does not precede the start. A current itinerary row cannot rely on a cancelled booking unless the row is Skipped or Blocked. A `Ready` itinerary row may reference only a confirmed or completed booking.

## Daily Plan

One row per itinerary item: item ID, version, date, start/end time, time zone, city, activity, location, transport, booking ID, execution status, cost, currency, source, checked time and notes. Rows whose version does not match Active Version are historical.

Item IDs remain stable when an item is copied into a new version. The unique key is Version plus Item ID, so the same Item ID may appear once in every version. Every Daily Plan version must exist in Change Log. Execution status is Planned, Ready, In progress, Done, Skipped or Blocked.

Every Daily Plan row requires its item ID, version, date, time zone, activity and execution status. When a new version succeeds another, items already marked Done or Skipped remain present with the same stable ID and execution status.

When either local start or end is present, both are required and must use a valid Excel time or `HH:MM[:SS]`. End must follow start; add `[overnight]`, `跨夜` or `过夜` to Notes when the end falls on the next day. Executable items in the Active Version cannot overlap when they share a time zone.

Execution status and notes may be updated in place because they record what happened rather than changing the plan. If reality changes any remaining itinerary item, use the version workflow.

## Checklist

One row per action: ID, category, task, owner, due date, status, dependency, related booking or plan item and notes. ID, category, task, owner, valid due date and status are required. Typical categories include visa, transport, accommodation, packing, payment, insurance and confirmation.

Dependencies must form an acyclic chain: a task cannot depend on itself, directly or through other tasks. Resolve a dependency cycle before using the checklist for execution.

## Members

One row per traveler: member ID, display name, role, relationship, trip-specific needs, permissions and notes. Roles are Owner, Editor, Member and Viewer. Owner and Editor may author versions; Owner, Editor and Member may submit proposals or own tasks; Viewer is read-only. Only Owner gives final approval unless the archive explicitly names another rule.

Exactly one member has the Owner role, that member matches Travel Overview's owner, and the overview traveler count matches the number of member rows. A preference applies to `所有人` or an existing member ID.

## Proposals

One row per suggestion or decision: ID, submitted by, date, affected item/day, proposal, reason, status, decision owner, resolution and resulting version. ID, submitter, valid date, affected scope, proposal, reason and status are required.

A proposal marked Accepted or Rejected must name the trip Owner as decision owner and record the resolution. An accepted proposal must also name the resulting valid version, whose Change Log reason or summary includes the Proposal ID. Other statuses never name a result version. Pending or Needs clarification proposals never change the itinerary and must be resolved before the trip is Completed.

## Change Log

One row per version: version, created time, author, reason, summary, predecessor and archive hash when available. Never reuse or silently overwrite a version number.

## Required integrity checks

- Exactly one trip overview data row exists in a workbook.
- Workbook cells contain literal values only; formulas are rejected because the archive does not need executable spreadsheet content.
- Every filled row in the other seven sheets has its sheet-specific ID.
- Travel Overview, Bookings and Checklist retain the minimum fields needed for recovery and execution.
- Active and Completed trips have a non-empty Active Version.
- Draft trips have no Active Version, so recovery cannot mistake an unapproved plan for the current itinerary.
- A Completed trip is in the `旅行后` phase, every active plan item is `Done` or `Skipped`, and every checklist task is `已完成` or `已取消`.
- Active Version has Daily Plan rows and exactly one Change Log row.
- Change Log has one root and a linear predecessor chain; Active Version is the final version in that chain.
- The Owner authors the root version, and every successor version is backed by an accepted Proposal resolved by the Owner.
- Daily Plan rows use a unique Version plus Item ID pair, and every referenced version exists in Change Log.
- Daily Plan rows contain the minimum executable fields, and successor versions never drop or regress Done or Skipped items.
- Timed current items have valid ranges, explicit overnight intent and no same-time-zone overlaps.
- Booking IDs referenced by current Daily Plan rows exist in `Bookings`.
- Booking time ranges are valid, cancelled bookings do not support executable current items, and `Ready` items use confirmed or completed bookings.
- Accepted decisions that changed the plan name the resulting version.
- Accepted and rejected proposals are resolved by the trip Owner and include the resolution.
- Proposal rows retain decision-driving context; only Accepted proposals name a result version, and Completed trips have no unresolved proposals.
- Current Daily Plan dates fall within the trip range unless Notes contains `[pre-trip]`, `[post-trip]`, `行前` or `行后`.
- Change Log predecessors name an existing earlier version and never point to themselves.
- Checklist dependencies name an existing task; related IDs name an existing booking or plan item.
- Checklist dependencies contain no direct or indirect cycles.
- Travel Overview traveler count, owner and preference subjects reconcile with Members.
- Change Log authors, Proposal submitters and Checklist assignees obey their member roles; Viewer remains read-only.
- Preference rows include the decision-driving statement, evidence and confidence instead of an unsupported profile label.
- Confirmed facts include a source and checked time when time-sensitive.
- A booking marked `已确认` and a Daily Plan item marked `Ready` both require Source and Checked Time.
- Status, role, scope and priority values must use the dropdown vocabulary in the canonical template.
