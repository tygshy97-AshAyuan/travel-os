# Travel archive schema

## 旅行概览

One row per trip: Trip ID, title, destination, start/end dates, travelers, owner, Active Version, status and notes.

## 当前行程

One row per itinerary item: version, date, start/end time, city, activity, location, transport, booking status, cost, currency, source and notes. Rows whose version does not match Active Version are not current.

## 决策与协作

One row per suggestion or decision: ID, submitted by, date, affected day, proposal, reason, status, decision owner and resolution.

## 版本记录

One row per version: version, created time, author, reason, summary and predecessor. Never reuse or silently overwrite a version number.
