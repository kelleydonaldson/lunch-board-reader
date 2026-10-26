# Lunch Board Reader — sample case kit (answer key)

Cases 1–6 built 2026-10-23 from the six cases named in the 2026-10-22
build plan; cases 7–8 added 2026-10-26 from the revised build brief (§6).
ALL data is invented — no merchant names, addresses, or real posts.
Graphics are code-rendered test fixtures (make_sample_cases.py), not
public-facing material. Post date = the date the truck supposedly posted
the graphic; weekday anchoring is tested against it.

Schema (revised brief §5): one object per post — `truck` once per post,
`post_date`, `stops` (each `date`/`start`/`end`/`place`/`address`, a
string or null), and `flags` — objects `{code, stop, field, note}`.
Times are written exactly as printed on the graphics. Flags are scored
on code + stop + field (the note's wording is ignored); a missing flag
fails its case, and so does an extra one. Flag codes: `UNREADABLE`,
`NO_STREET_ADDRESS`, `FLYER_NOT_CONFIRMED`, `PRIVATE_STOP`, `WEEK_UNCLEAR`.

## Case 1 — case1-weekly-schedule.png
- Tests: weekday → date anchoring from the post date; clean extraction.
- Posted: Mon Oct 26, 2026. Truck: Sample Smoke Co.
- Expected stops (flags: []):
  - Mon Oct 26, 11 AM–2 PM, Riverside Sample Lot, 100 River Bend Rd
  - Tue Oct 27, 11 AM–2 PM, Sampleton Hardware, 220 Main St
  - Wed Oct 28, 4 PM–7 PM, Sample Community Center, 35 Center Ave
  - Thu Oct 29, 11 AM–2 PM, Northgate Sample Plaza, 780 Northgate Dr
  - Fri Oct 30, 11 AM–3 PM, Sampleton High School lot, 15 Schoolhouse Ln

## Case 2 — case2-two-stop-day.png
- Tests: two stops on one day, each time paired to its own stop.
- Posted: Wed Oct 28, 2026. Truck: Sample Taco Cart.
- Expected stops (flags: []):
  - Wed Oct 28, 11 AM–1 PM, Downtown Sample Square, 10 Court Sq
  - Wed Oct 28, 5 PM–8 PM, Sample Brewing Co., 410 Ale House Way

## Case 3 — case3-event-flyer.png
- Tests: a flyer counts as a stop only because it clearly says the truck
  will be there; the address exists only inside the image.
- Posted: Fri Oct 30, 2026. Truck: Sample Noodle Wagon.
- Expected stop (flags: []):
  - Sat Oct 31, 5 PM–9 PM, Sample Fairgrounds, 900 Fairgrounds Rd
- KEY CHANGE (2026-10-26, owner's ruling): the expected place was
  "Sample Fairgrounds (Sampleton Fall Fest)"; it is now
  "Sample Fairgrounds". The recipe copies the place exactly as printed,
  and the flyer prints "Sample Fairgrounds" — the key had combined the
  venue with the event name from the flyer header ("Sampleton Fall
  Fest"), and the model read the place correctly. Key fixed; recipe
  untouched. (Showing the event name on the board is a possible future
  optional `event` field — a post-hackathon idea, never a combined
  string.)

## Case 4 — case4-smudged-time.png
- Tests: flag, never guess. The end time is under a coffee-stain smudge
  and is NOT recoverable from the image.
- Posted: Thu Oct 29, 2026. Truck: Sample Burger Bus.
- Expected stop: Fri Oct 30, start 11 AM, end null, Sample Auto Parts,
  640 Mechanic St.
- Expected flag: `UNREADABLE`, stop 0, field `end` — "The end time is
  smudged and cannot be read." Any specific end time in the output is a
  FAIL, however plausible it looks.

## Case 5 — case5-no-address.png
- Tests: place name with no street address → plain text, no guessed
  Maps link.
- Posted: Mon Oct 26, 2026. Truck: Sample Coffee Cart.
- Expected stop: Tue Oct 27, 7 AM–10 AM, "the old mill pavilion",
  address null.
- Expected flag: `NO_STREET_ADDRESS`, stop 0, field `address` — "No
  street address in the post; the place stays plain text." Any street
  address in the output is a FAIL.

## Case 6 — case6-out-of-town.png
- Tests: out-of-town stop stays on the board, town + state named.
- Posted: Fri Oct 30, 2026. Truck: Sample Smoke Co.
- Expected stop (flags: []):
  - Sat Oct 31, 11 AM–3 PM, Henderson Sample Market, 55 Market St,
    Henderson, KY — output line must name "Henderson, KY".

## Case 7 — case7-private-stop.png
- Tests: a private / employees-only stop is omitted, never published,
  and flagged; the public stop beside it is read normally.
- Posted: Tue Oct 27, 2026. Truck: Sample Burger Bus.
- The graphic lists two stops: Wed 11 AM–1 PM "Sample Manufacturing —
  employees only", and Thu 11 AM–2 PM Sample Public Library, 5 Book Ln.
- Expected stop: Thu Oct 29, 11 AM–2 PM, Sample Public Library,
  5 Book Ln.
- Expected flag: `PRIVATE_STOP`, stop null, field null — "The Sample
  Manufacturing stop is employees only, so it is not a public stop."
  Any stop for Sample Manufacturing in the output is a FAIL.

## Case 8 — case8-sunday-post.png
- Tests: the Monday–Sunday week rule. A Sunday post naming "Monday":
  that Monday (Oct 26) falls before the post date, so the week is
  ambiguous and a human picks it.
- Posted: Sun Nov 1, 2026. Truck: Sample Taco Cart.
- The graphic says only: "Monday — 11 AM–2 PM — Downtown Sample
  Square, 10 Court Sq."
- Expected stop: date null, 11 AM–2 PM, Downtown Sample Square,
  10 Court Sq.
- Expected flag: `WEEK_UNCLEAR`, stop 0, field `date` — "Monday of the
  week containing the post date falls before the post date, so the
  week is ambiguous." Any specific date in the output (Oct 26 or
  Nov 2) is a FAIL.

## How the kit is used
The build plan runs cases 1–2 first (Day 1), then 3–4, then 5–8.
Scoring a run = compare the Reader's structured output field-by-field
against this key (score.py); flags count as fields — a missing flag on
cases 4, 5, 7, or 8 fails the case even if every other field matches,
and an extra flag the key doesn't expect also fails.
