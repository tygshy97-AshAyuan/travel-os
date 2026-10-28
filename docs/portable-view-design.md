# Portable itinerary design notes

Direction: Taste **Achromatic ledger**, seed **327246617**, light, no sidebar; no redraw. Type retained as a deliberate system-font stack with PingFang SC / Microsoft YaHei fallbacks: no font download, Chinese coverage and offline readability take precedence over Geist. Ground #f2f4f7; white next-action block; #1d5fbf only on the current-action edge; black print action.

The product-specific content is the archive's active version, local schedule, stable activity identities, predecessor changes, recorded verification timestamps, unresolved proposals, preparation checklist, per-item currency, original place names and readonly save boundary. A timetable, not a destination advertisement, is the visual reference.

The screen answers: “What is my current plan, what comes next, and what changed?” The next action uses the largest activity text; the day timeline supplies context; side content becomes a lower section on phones. All itinerary days remain in the HTML for no-script reading and print output.

## Screenshot critique

Reviewed desktop/tablet/mobile fold and full-page images from `artifacts/qa-domestic/`.

- Hierarchy: title identifies the trip; next activity is prominent with its local date/time. No itinerary fields masquerade as live verification.
- Alignment: header and content share a centered 1120px box; desktop timeline and checklist share the top edge. Tablet stacks preparation content below the schedule. Mobile has 16px gutters and no horizontal clipping in the reviewed screenshots.
- Color and type: neutral chrome, one blue current-action marker, system CJK text renders. No image or chart is needed for this schedule task.
- Data consistency: v0.1.1 is used in header and export data; comparison is with v0.1.0. The shown walk is 15:00–17:00 and its old time is 14:00–16:00. No total combines currencies. Zero is explicitly 0.00; unknown amounts are “待核实”. All demo values are fictional.
- Phone: time column remains distinct; change fields stack as before/current pairs; controls meet 44px minimums. The next action remains on the first screen. Preparation and history require scrolling by design.
- Static lint eyebrow warning is accepted only for the actual destination above the trip title. Inspector reported no FAIL/WARN; no visual-rule suppression flags used.

Unverified: English screenshots, true mobile file opening, clipboard/print browser behavior, no-script print details and complete updated model behavior. These are recorded in the validation document rather than inferred from screenshots or JS tests.

## 2026-10-27 refinement after user feedback

The user rejected the first version as too AI-styled. The new direction is a personal trip sheet: one reading column, white paper (#ffffff), dark text (#202522), muted text (#636d67), quiet separators (#e5e9e6), a restrained green (#25634b) for place links and the next stop, and a pale next-stop background (#f1f6f3). System CJK fonts remain offline. The 840px content box intentionally limits reading width instead of filling the desktop with widgets.

The reading order is trip → date → next stop → daily schedule → actual open tasks. Empty task sections are hidden. Costs, evidence and changes remain available through disclosures; version/export information moves to the footer. Ordinary Planned/Ready badges are omitted; blocking/completion states remain. Print events open disclosures and restore them afterward.

The first revised screenshots at 1440/768/390px were reviewed: the mobile fold now includes the first timeline row, visual hierarchy is clearer, and no clipping appeared. Static lint has no findings. The inspector reports a desktop whitespace warning: accepted because the centered reading column intentionally leaves a margin on a wide display; no artificial widget is added just to occupy it. This replaces the earlier sidebar/ledger treatment. Final screenshot check uses artifacts/qa-natural/. Phone file access and print behavior remain unverified on real devices.

## 2026-10-28 English inbound check

The approved single-column design is unchanged. English inbound-China screenshots at 1440/768/390px were reviewed, including page-length images. Original Chinese place names remain legible; map links now name Amap in the English UI. The next-action caption and footer were shortened to match the Chinese version's tone. No clipping was observed; the desktop whitespace warning is accepted for the same bounded-reading-width reason. Latest images: `artifacts/qa-inbound/`. This supersedes the earlier note that English screenshots were unverified; device file opening and print interactions still require separate evidence.
