# Travel OS v0.4.30

This release prevents invalid timestamps from masquerading as verified travel facts.

Confirmed bookings and Ready itinerary items must now pair their source with a valid checked timestamp. Values such as `unknown` or `not-a-time` no longer satisfy the evidence requirement used for recovery and stale-fact review.

Both canonical workbooks and the prior end-to-end fictional workbook pass the stricter validator. The package passes 57 contract tests.
