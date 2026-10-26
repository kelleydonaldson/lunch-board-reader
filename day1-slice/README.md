# Lunch Board Reader — Day 1 slice workspace (prepared Mon Oct 26, 2026, ~11:20 AM CT;
updated later Oct 26 to the revised build brief's §5 schema, flag codes, and 8-case kit)

Purpose: everything for the noon first slice EXCEPT the Meta Model API call itself,
so the slice starts the minute Kelley's login / team_id / credits land.
Sample data only — invented trucks. Nothing here touches the live site or live intake.

## Files in this folder
- `recipe.md` — the fixed instruction sent with every image: brief §4 verbatim
  (reader.py fills in `<POST_DATE as YYYY-MM-DD>` and `<WEEKDAY>` per post).
- `extraction.template.json` — blank extraction in the §5 schema for all 8 cases:
  one object per post `{truck, post_date, stops[], flags[{code, stop, field, note}]}`;
  fill it from the model's return (or by hand for a dry run), then score it.
- `score.py` — field-by-field scorer over all 8 cases against the kit's answer key.
  Compares truck, post_date, every stop's date/start/end/place/address, and flags
  matched on code + stop + field (note ignored; missing OR extra flags fail).
  `--cases 1,2` scores just the Day-1 pair; `--case N` a single case.
- `../day1-score-sheet-cases1-2.md` — the human-readable Day-1 key (cases 1–2).

## Run order once access lands
1. Kelley signs in at dev.meta.ai (menu → Login, or Products → Meta Model API → API Login),
   lands with `team_id=` in the address, submits the $150 credits form and agrees to terms — his clicks.
2. Confirm one real API call returns (Day-1 done test, part 1).
3. Send `../sample-cases-2026-10-23/case1-weekly-schedule.png` + `recipe.md` to the model;
   save the structured return as `extraction-case1.json` in the template's schema.
4. Score it: `python3 score.py extraction-case1.json --case 1` — or fill the full
   template and run `python3 score.py extraction.json --cases 1,2` for the Day-1 pair
   (no filter = all 8 cases).
5. Repeat for case 2. Day-1 done = case 1 (ideally both) reads correctly, no invented fields,
   anything unclear flagged rather than guessed.

## Scorer self-check (run Oct 26, before any model call; re-run after the
§5/8-case update — all on scratch copies)
- Feeding the full answer key as the extraction: PASS (all 8 cases).
- Doctored keys FAIL, as required: case 2 with the two stops' times swapped;
  case 4 with an invented "2 PM" end time and its UNREADABLE flag removed;
  case 7 with the private stop included as a stop; any case carrying an
  extra flag the key doesn't expect.
So a PASS later means the extraction matches, not that the scorer waves everything through.

## Demo intake workspace (added Oct 26, ~11:45 AM CT)
- `demo-intake/` — a demo COPY of the intake queue structures (events/drafts/
  indexes mirrored from the live worker's shapes as flat JSON in
  `demo-intake/store/`), seeded with all 8 sample cases as queue events, plus
  `demo-intake/reader.py`: the harness — recipe -> read (the seam:
  `--simulate` stand-in extractions, or `call_model_api`, STUBBED until the
  free credits land; the API key is already stored in Muse's Secure Vault
  and reached via connector custom.meta-model-api, never in a file or env
  var) -> guardrails (exact §5 schema check incl. flag codes; real-date
  check; printed times normalized to 24-hour to verify end > start, draft
  keeps printed times; required date/place not null; every null explained
  by a flag) -> filing as an approval-ready draft (clean reads only) or
  into the flag pile (flagged/failed) -> demo approval step -> side-by-side
  queue at `demo-intake/queue.html` + approved-only demo board at
  `demo-intake/board.html`. Step 5 was built early on Oct 26 in stand-in
  mode: the answer key was fed through guardrails + filing, the 4 clean
  drafts were approved, and the board rendered; the staged store now HOLDS
  those stand-in results (8 events, 4 drafts, 4 flag-pile entries).
  Verified end to end on a scratch copy first (58 checks). See
  `demo-intake/README.md` ("Stand-in mode vs real mode").
  Per-stop approval from the flag pile (owner addition, brief §3.3) was
  added later Oct 26: `reader.py --approve-stop <event_id> <stop_index>`
  (with `--resolve-date` / `--resolve-place` for null date/place, recorded
  as human-supplied) writes single-stop entries to
  `demo-intake/store/board_entries.json` with full provenance; the parent
  item stays in the flag pile. Applied to the staged state for case 7's
  library stop only — the demo board now shows 10 stops. See
  `demo-intake/README.md` ("Per-stop approval from the flag pile").
