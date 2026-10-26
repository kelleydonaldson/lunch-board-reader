# Lunch Board Reader — held-out case kit (answer key, H1–H6)

Written 2026-10-26, **before** any held-out graphic was generated or
read. The recipe (build brief §4) was designed against the main kit
(cases 1–8); it was NOT designed against these six. ALL data is
invented — no merchant names, addresses, or real posts. Graphics are
code-rendered fixtures (`make_heldout_cases.py` in this folder).

Schema and scoring mirror the main kit: one object per post —
`truck`, `post_date`, `stops` (`date`/`start`/`end`/`place`/`address`,
string or null), `flags` (`code`/`stop`/`field`/`note`). Times exactly
as printed. Flags are scored on code + stop + field (note wording
ignored); a missing or extra flag fails its run. Each case runs 3
times through the real reader path. **Hard stop rule for the whole
set: the moment any run returns an invented value — a date, time,
place, or address that is not printed on its graphic — all remaining
runs stop and the invention is the lead finding.**

## Owner rulings applied to this key (Kelley, 2026-10-26 — in force before the first call)

- **H4 severity raised:** the expected read stays "no stop, no flag"
  for the canceled stop, but a run that returns the canceled stop as
  a stop is now a **HARD STOP**, same severity as an invented value —
  it sends people to a place the truck won't be.
- **H6 key widened:** both reads of the typo'd end are acceptable —
  (a) end `"2"` copied exactly as printed (the guardrail is then
  expected to route the item to the flag pile as unparseable), or
  (b) end `null` + `UNREADABLE` (stop 0, field end). **Hard stop**
  only if the end comes back *completed* ("2 PM" or any other
  filled-in time value). **Pre-run gate:** before H6 runs live, a
  synthetic extraction shaped like the H6 expectation but with end
  `"2"` must be shown to route to the flag pile as unparseable
  through the reader's guardrails (simulate / no-API path). If it
  drafts instead, H6 does not run and the guardrail gap is reported
  as a lead finding; the other cases proceed.

## H1 — h1-skewed-photo.png
- Tests: geometry robustness. A normal weekly schedule photographed,
  not screenshotted: perspective skew, rotation, a soft shadow and a
  vignette. The test is geometry, not ambiguity — every fact is
  printed completely and legibly.
- Posted: Mon Nov 2, 2026. Truck: Sample Grill Wagon.
- Expected stops (flags: []):
  - Mon Nov 2, 11 AM–2 PM, Lakeside Sample Park, 88 Shore Dr
  - Tue Nov 3, 11 AM–2 PM, Sampleton Post Office, 12 Postal Way
  - Wed Nov 4, 4 PM–8 PM, Sample Bowling Alley, 300 Strike Ln
  - Thu Nov 5, 11 AM–2 PM, Westside Sample Market, 415 Sunset Blvd
  - Fri Nov 6, 11 AM–3 PM, Sampleton Fire Station, 7 Engine Ct

## H2 — h2-decorative-font.png
- Tests: typography and background robustness. A one-day, two-stop
  schedule set entirely in a decorative display font on a busy
  patterned background (two-tone polka dots, checkerboard border).
  Facts printed completely.
- Font: **Noto Serif Display Black** (subtitle in Black Italic),
  `/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf` — the
  most decorative Latin TTF installed on this system (no script or
  chancery face exists here; DejaVu/Liberation are plainer).
- Posted: Wed Nov 4, 2026. Truck: Sample Dumpling Cart.
- Expected stops (flags: []):
  - Wed Nov 4, 11 AM–1 PM, Sampleton Bookstore, 64 Novel St
  - Wed Nov 4, 5 PM–9 PM, Sample Vineyard, 900 Grapevine Rd

## H3 — h3-low-res.png
- Tests: resolution robustness. A two-stop day rendered small
  (460 px wide) and passed through JPEG compression (quality 42) so
  the artifacts are visible, then saved as PNG. Every fact is still
  legible by design at 100% zoom — this is NOT an unreadability trap,
  so no `UNREADABLE` flag belongs here either.
- Posted: Thu Nov 5, 2026. Truck: Sample Slice Truck.
- Expected stops (flags: []):
  - Thu Nov 5, 11 AM–2 PM, Northgate Sample Mall, 1200 Retail Row
  - Thu Nov 5, 4 PM–7 PM, Sampleton Skate Park, 33 Wheel Way

## H4 — h4-canceled-stop.png
- Tests: cancellation semantics. A three-stop day whose middle stop
  is struck through AND stamped "CANCELED".
- Posted: Fri Nov 6, 2026. Truck: Sample Curry Cart.
- Printed stops: 11 AM–1 PM Sampleton City Hall, 1 Civic Plaza ·
  **2 PM–4 PM Sample Farmers Market, 250 Harvest Ave (CANCELED)** ·
  5 PM–8 PM Sample Community Theater, 77 Stage Door Ln.
- **Ruling (owner, 2026-10-26): a canceled stop is NOT a stop.** The
  flag-code set has no canceled code and the graphic is unambiguous,
  so the expected extraction is exactly the 2 live stops below and
  NO flag for the canceled one.
- **Severity (owner, 2026-10-26):** if a run includes the canceled
  stop as a normal stop, that is a **HARD STOP** — stop everything
  and report it as the lead finding. (Publishing a canceled stop is
  the exact harm the product exists to prevent.)
- Expected stops (flags: []):
  - Fri Nov 6, 11 AM–1 PM, Sampleton City Hall, 1 Civic Plaza
  - Fri Nov 6, 5 PM–8 PM, Sample Community Theater, 77 Stage Door Ln

## H5 — h5-two-truck-collab.png
- Tests: joint-post semantics. One graphic, a joint header naming
  both trucks together, and per-stop lines that each name their
  truck — 2 stops, one per truck, different times and places.
- Posted: Sat Nov 7, 2026. Header as printed: **"Sample Smoke Co. ×
  Sample Taco Cart"**.
- Expected: `truck` = the joint header copied exactly as printed;
  both stops below; flags: [].
  - Sat Nov 7, 11 AM–2 PM — Sample Smoke Co. — Riverside Sample Lot,
    100 River Bend Rd
  - Sat Nov 7, 4 PM–7 PM — Sample Taco Cart — Sample Fairgrounds,
    900 Fairgrounds Rd
- **Schema limit, stated in the key:** the §5 schema has one
  post-level `truck` field and no per-stop truck field, so which
  truck owns which stop cannot be represented in the output. That
  limit is accepted here, not worked around. A run that silently
  drops one truck's stop, or merges the two stops into one, is a
  FAIL.

## H6 — h6-typo-time.png
- Tests: the never-guess rule against an incomplete-as-printed time.
  A one-stop day prints **"11 AM - 2"** — the end has no AM/PM. The
  print is perfectly legible; it is a typo, not a smudge.
- Posted: Tue Nov 3, 2026. Truck: Sample Waffle Wagon.
- **Ruling (owner, 2026-10-26) — key widened.** Acceptable reads:
  - (a) `end` = `"2"`, copied exactly as printed (flags empty, or a
    single `UNREADABLE` on stop 0 / field `end`). The guardrail is
    then expected to route the item to the flag pile as
    unparseable — proven by the pre-run gate below.
  - (b) `end` = `null` + one `UNREADABLE` flag, stop 0, field `end`
    (the case-4 precedent; this is the canonical object in
    heldout-key.json).
- **Hard stop (owner, 2026-10-26):** `end` coming back *completed* —
  "2 PM" or any other filled-in time value — is an invented value.
- **Pre-run gate (owner, 2026-10-26):** before H6 runs, feed a
  synthetic extraction identical in shape to the expectation but
  with `end` `"2"` through the reader's guardrails via the
  simulate/no-API path and verify it routes to the **flag pile as
  unparseable**, NOT to draft. If it drafts, H6 does not run and
  the gap is the lead finding; the other cases are unaffected.
- Expected stop: Tue Nov 3, start 11 AM, end per the ruling above,
  Sampleton Depot, 19 Rail Spur.

## How this kit is used
Keys first (this file), then graphics, each graphic read back against
this key before any model run — if a graphic and the key disagree,
the graphic gets fixed, never the key. Then each case runs 3 times
through the real reader path (`files/day1-slice/demo-intake/reader.py`
seam, model `muse-spark-1.3`). After every single call, the
extraction is checked against its graphic for invented values before
the next call is made. Raw responses and extractions are saved under
`out/run-<r>/` in this folder; tokens go to the shared spend log,
marked as held-out runs.
