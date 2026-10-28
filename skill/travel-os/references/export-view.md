# Portable itinerary export

Use after a validated plan is activated or updated, or when the user requests a phone-readable copy. The workbook remains the editable source of truth; the HTML is a read-only snapshot. No account, remote API, telemetry or hosted link is created.

## Generate and hand over

From this skill's directory, with Python 3.9+ and an IANA time-zone database:

```sh
python scripts/export_trip.py /path/to/latest.xlsx --output /path/to/trip-v0.1.0.html --locale zh-CN --region mainland-cn
```

Use a new output path on every export; existing files are not overwritten. Validation failures, drafts, uninitialized templates and cancelled trips cannot be exported as the current plan. The exporter reads all sheets for validation but presents only Active Version. It compares the current plan with the direct predecessor by stable item ID; execution status updates alone are not route changes. Added/removed items and changed fields are shown separately.

Map selection does not follow UI language. `--locale` supports `zh-CN` and `en`; it translates controls only. Preserve or translate itinerary content separately when requested, retaining local place names. `--region` supports `mainland-cn`, `hong-kong`, `macao`, `taiwan`, `other`, `unknown`. Mainland uses Amap; known other regions use Google; unknown produces copyable names without a map link. Multi-city example:

```sh
python scripts/export_trip.py /path/to/latest.xlsx --output /path/to/trip-en.html --locale en --region unknown --city-region '上海=mainland-cn' --city-region 'Tokyo=other'
```

City keys must exactly match `Daily Plan` city values. A keyword search is not a verified POI, multi-stop route, travel-time estimate or coordinate conversion. Confirm the selected result before navigation.

Deliver both the actual latest XLSX and generated HTML with accessible file links. Explain in one sentence: download/open the HTML in a browser, choose a date, and use Print / save PDF to export a paper copy. All days print, regardless of the date filter. Sources/check timestamps are recorded evidence, not fresh verification.

## ChatGPT / Codex capability handling

- In a host that provides file execution, run the bundled exporter; do not merely paste a command and claim delivery. Verify that it returned success and the file exists.
- If a host does not load installed skills automatically, use the accessible skill files and supplied archive explicitly. Do not claim every ChatGPT interface supports ZIP installation or local skill discovery.
- Some chat previews or mobile file viewers disable scripts. All day sections remain readable without JavaScript; open the downloaded HTML in a full browser for filtering/copying/printing. Printing to PDF depends on the browser/OS, not an embedded PDF engine.
- If execution is unavailable, provide a clearly labeled text itinerary and explain that a file was not generated. Do not invent a download link.
- The next-action card uses each item's local date/time and the device clock. Completed/skipped rows are excluded; overdue unfinished rows remain visible rather than being marked done. DST-ambiguous or missing times are labeled for confirmation. It does not provide live traffic, departure alerts or automatic progress synchronization.
- An ongoing overnight activity stays visible after midnight, with its end labeled as next day. The automatic today view follows local date changes; choosing a date manually keeps that date until the user chooses Today again. When today has no activity, keep the selected day and explain it. Future activities across time zones are ordered by their actual instants.
- Printing opens collapsed details, includes all itinerary dates, and restores the previous expanded/collapsed state afterward. This is browser behavior; verify it in the actual browser before claiming device compatibility.
- An old HTML file cannot detect a newer workbook. The visible version and export timestamp let the user identify it; after changes, regenerate from the latest validated file.

## Optional companion copy

For a user-requested shareable summary, select explicit current item IDs. The exporter excludes private fields, source notes, booking data, members, todos, proposals and revision history. Lodging-linked selected items are rejected. Example:

```sh
python scripts/export_trip.py /path/to/latest.xlsx --output /path/to/companion.html --region mainland-cn --audience companion --share-item I-002
```

This is data minimization, not automatic anonymization. Activities, dates, places and transport can still identify someone or reveal lodging in free text; review the generated content against the requested sharing scope before handing it over for sharing. Do not send or publish it without authorization. A local file is not a collaboration backend or a public URL.
