# Roadmap

Travel OS is currently in Early Access. Work is ordered by whether it makes a real trip safer and easier to maintain.

## Now

- Validate the v0.5.0 first-run flow: route before archive mechanics, automatic template preparation when supported, honest unsaved outlines and recovery for existing trips.
- Validate the implemented portable HTML exporter in ChatGPT / Codex and phone browsers: daily routes, next action, predecessor comparison, local time zones, destination-specific maps and printing all days.
- Test Chinese domestic/outbound journeys first, plus English inbound-China and international examples. UI language must not imply citizenship or destination.
- Test companion allowlist exports and manual content review. Local export is implemented; hosted sharing remains separate.
- Repeat the complete planning, change, execution and review regression after workflow or spreadsheet-write changes in supported Agent clients.
- Improve first-run instructions from real user reports.
- Validate weather-driven changes in supported Agent clients.

## Next

- Consider hosted companion links only after the account-free file flow is accepted; do not introduce a second editable source of truth.
- Evaluate activation with consenting testers: first useful outline, validated saved plan, successful next-session recovery and accepted change. Downloads and clones are distribution signals, not active users. No telemetry endpoint is implemented yet.
- Add optional direct mailbox import with explicit account permission.
- Validate route links in supported Agent clients.

## Later

- Optional Todoist and Notion integrations.
- Booking actions with explicit confirmation and rollback guidance.
- Privacy-safe reusable trip patterns from opted-in examples.

Feature priority follows reproducible user problems. Submit the problem and desired outcome through the repository's Feature Request form; do not include private itinerary data.
