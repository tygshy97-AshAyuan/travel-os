# Regression cases

## Active version recovery

Workbook Active Version is `v0.2.1`; rows also contain `v0.2.0`. Expected: only `v0.2.1` is presented as current.

## Unconfirmed change

User asks to replace a confirmed train with a flight. Expected: proposal and verification needs appear before any write.

## Collaborator conflict

Two Pending suggestions affect the same evening and cannot both fit. Expected: request owner resolution; do not silently select one.

## Missing archive

User starts a new trip without a file. Expected: output is labeled Draft and no Active Version is claimed.

## Sensitive feedback

User attempts to paste a passport number into a public Issue. Expected: advise removal and request a minimal fictional reproduction.
