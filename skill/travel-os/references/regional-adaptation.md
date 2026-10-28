# Regional travel adaptation

Use this for route planning, travel preparation and portable itinerary delivery. Prioritize Chinese-language domestic and outbound journeys while supporting English inbound and overseas journeys through the same archive.

## Route the situation, not the person

Reuse the user's origin, destinations, dates, preferred language, companions and fixed bookings. Ask only for what changes the next result. Language, citizenship, residence and destination are separate facts: Chinese text does not establish a Chinese passport; English does not establish a foreign traveler. Do not require citizenship to sketch a domestic city walk.

When entry or transit eligibility matters, ask for the issuing jurisdiction and type of travel document, residency/visa conditions where relevant, purpose, dates and transit route. Do not request document numbers or copies. Verify current official rules for the actual route before giving eligibility advice; do not embed visa-free day counts or nationality lists in this skill. Treat mainland China, Hong Kong, Macao and Taiwan as separate travel-entry/service regions for this operational check. This classification is not a statement about sovereignty.

| Journey | Route and preparation focus | Portable view |
| --- | --- | --- |
| Chinese-language domestic travel | City/station disambiguation, real-name booking requirements, holiday reservation pressure, walking/rest constraints, intercity transfers and last-mile transport | Chinese UI; mainland destinations use Amap keyword search; preserve original Chinese addresses |
| Chinese-language outbound travel | Local names alongside Chinese explanation, destination/transit entry verification when needed, time differences, actual payment options, connectivity, booking access and transport buffers | Chinese UI; each stop retains local time zone; destination map provider; costs retain original currency |
| Foreign traveler visiting China | Document-compatible booking channel, original Chinese station/place name for driver/staff, payment setup and backup, connectivity and access to bookings; clarify entry route only when relevant | User's preferred UI language; mainland destinations still use Amap; copyable original Chinese names/address |
| Foreign traveler traveling elsewhere | Same route/constraint planning; verify destination and transit conditions for the stated documents instead of assuming US/EU eligibility | English or Chinese UI by preference; map provider by destination; local time zones and original names |

Do not promise that a platform, card, foreign phone number or identity document is supported without checking the relevant service. For holidays and rail/attraction reservations, verify actual sale windows for the trip dates instead of assuming fixed lead times. Do not infer lodging acceptance or cancellation terms from a search result.

## Keep the archive usable

- Use the existing fields; do not add sheets or columns. Keep original local place names/address in `地点` and localized explanation in `活动` or `备注`. Transliteration alone is not sufficient for finding a station or showing an address to a driver.
- `时区` belongs to each activity, not the traveler's phone. Verify airport/station local dates across overnight travel and date-line crossings. Ambiguous DST times need clarification.
- Keep costs and currency per row. Unknown is blank, not zero. Do not sum different currencies; any conversion in conversation needs a stated rate, time and source and must not replace original amounts.
- Store trip-specific needs in Preferences/Checklist with explicit evidence. Avoid permanent nationality/personality profiles and unnecessary sensitive facts.
- Region selection for exports is explicit. Use per-city overrides for multi-region trips; never guess region from language or `Asia/Shanghai` alone. Search links locate candidates, not verified coordinates or guaranteed working navigation.
- If live sources or destination services cannot be reached, deliver the checked portions and clearly identify unresolved transport/booking/entry facts. The static file cannot verify live conditions or guarantee that external services work from a user's network.

## Official starting points

These are discovery links, not evidence that an individual traveler is eligible. Reopen and verify the relevant policy at use time. Link formats checked 2026-10-27:

- [China National Immigration Administration services](https://en.nia.gov.cn/n147423/n147478/index.html)
- [China Railway 12306 English FAQ](https://www.12306.cn/en/faq.html?item=2)
- [Amap URI keyword search](https://developer.amap.com/api/uri-api/guide/search/search)
- [Google Maps URLs](https://developers.google.com/maps/documentation/urls/get-started)

For other destinations use their official immigration/consular sources, then the actual carrier/operator for operational requirements. Do not substitute a travel marketplace's general article for an entry decision.
