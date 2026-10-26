# Lunch Board Reader — Day 1 score sheet: sample cases 1–2
For Monday Oct 26, 2026, noon first build slice. Extracted 2026-10-25 from the kit's answer key
(files/sample-cases-2026-10-23/answer-key.md); revised 2026-10-26 to the revised build brief's
§5 schema (kit now 8 cases + answer-key.json/.md in the same shape).
Score = compare the Reader's structured output field-by-field against this sheet with score.py.
Flags count as fields: matched on code + stop + field (note wording ignored); a missing OR
extra flag fails. Times are scored exactly as printed on the graphics ("11 AM", not "11:00 AM").
Sample data only — invented trucks, no real merchant info.

## Case 1 — case1-weekly-schedule.png (Sample Smoke Co.)
Posted: Mon Oct 26, 2026 (post_date 2026-10-26). Tests weekday → date anchoring from the post date; clean extraction.
Expected stops, flags []:
- Mon Oct 26, 11 AM–2 PM, Riverside Sample Lot, 100 River Bend Rd
- Tue Oct 27, 11 AM–2 PM, Sampleton Hardware, 220 Main St
- Wed Oct 28, 4 PM–7 PM, Sample Community Center, 35 Center Ave
- Thu Oct 29, 11 AM–2 PM, Northgate Sample Plaza, 780 Northgate Dr
- Fri Oct 30, 11 AM–3 PM, Sampleton High School lot, 15 Schoolhouse Ln

## Case 2 — case2-two-stop-day.png (Sample Taco Cart)
Posted: Wed Oct 28, 2026 (post_date 2026-10-28). Tests two stops on one day, each time paired to its own stop.
Expected stops, flags []:
- Wed Oct 28, 11 AM–1 PM, Downtown Sample Square, 10 Court Sq
- Wed Oct 28, 5 PM–8 PM, Sample Brewing Co., 410 Ale House Way

Score just these two with: `python3 score.py <extraction.json> --cases 1,2`
(run with no --cases flag, score.py checks all 8 cases in the kit).

## Day-1 done test (from the Day-1 checklist)
Rules accepted, API access verified with a real call returning, case 1 read correctly
against this sheet with any unclear item flagged — not guessed.
Cases 4, 5, 7 and 8 are the flag tests (UNREADABLE smudged end time; NO_STREET_ADDRESS;
PRIVATE_STOP; WEEK_UNCLEAR) — not part of Day 1; they are scored from the full answer key.
