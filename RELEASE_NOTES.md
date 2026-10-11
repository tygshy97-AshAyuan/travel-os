# Travel OS v0.4.15

Itinerary time-conflict update.

Travel OS now validates paired local start and end times on the Active Version. An end before its start requires an explicit overnight marker, so night trains and flights remain supported without accepting accidental reversed times.

Executable activities in the same time zone cannot overlap. Skipped and Blocked rows are excluded from collision checks. The release includes a directly installable `Travel-OS-Skill-v0.4.15.zip`, the full repository archive and checksums for both. The package passes 42 contract tests.
