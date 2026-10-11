# Weather-driven re-planning

Use this workflow only with a current forecast for the itinerary's location and local date. Record the provider or URL, forecast issuance time when available, checked time, location granularity and forecast window. If the trip date is beyond the source's useful forecast window, label the weather Unverified and add a dated recheck task instead of changing the plan.

## Assess impact before proposing changes

1. Recover the Active Version and freeze completed or skipped history.
2. Match forecast conditions and timing to future itinerary rows. Identify the specific outdoor activity, transfer, accessibility need, reservation or safety margin at risk.
3. Preserve hard constraints and confirmed bookings. Show cancellation terms, transfer dependencies and extra cost before proposing a move.
4. Mark conflicting forecasts as Conflicting; do not choose one silently. A newer forecast does not erase the earlier source or checked time.

## Offer bounded alternatives

Offer no more than three workable choices, including keeping the plan when reasonable. Prefer shifting time, swapping days or using an indoor fallback before deleting a high-priority activity. Compare each choice by time, cost, fatigue, booking impact and the user's stated priorities.

Keep unaffected days and stable item IDs unchanged. Never move a completed item. Do not describe forecast confidence as certainty.

## Commit an accepted change

Record the selected option as an Owner-resolved proposal. Apply the atomic version workflow: copy the active itinerary, edit only affected future rows, preserve execution history, add the Change Log row, validate, then update Active Version last. Store the weather source and checked time on affected `Daily Plan` rows.

Finish with the next recheck time when conditions remain uncertain and a fallback that can be executed without another plan rewrite.
