# Travel OS v0.4.13

Booking and itinerary consistency update.

Travel OS now validates booking time ranges and rejects mixed zoned and unzoned timestamps. A booking cannot end before it starts.

Current executable itinerary rows cannot rely on cancelled bookings, and a `Ready` row can reference only a confirmed or completed booking. The release includes a directly installable `Travel-OS-Skill-v0.4.13.zip`, the full repository archive and checksums for both. The package passes 36 contract tests.
