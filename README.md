# Lunch Board Reader

**An approval system for food-truck schedule posts — not an image
analyzer.** A vision model is one component inside it: the input
stage. Around that read sit the parts that make its output safe to
publish — a never-guess rule enforced as structured flags,
programmatic guardrails that check every read before it is filed,
an approval queue where a human compares the read against the
original post, and provenance that records what the machine read,
what it refused to read, and what a person supplied. Nothing the
system produces reaches the board on its own.

Built for **Owensboro Market**, a local marketplace in Owensboro,
Kentucky, launching in pilot with founding local businesses — food
trucks among them. Its lunch board shows where each truck will be,
day by day. Truck schedules mostly arrive as pictures on Facebook:
a weekly schedule graphic, an event flyer, the dates, times and
addresses inside the image. The Reader turns each picture post into
structured stops a human can approve — and flags what it can't
read, instead of guessing.

*Every truck, post, and result in this repo is invented sample
data. No real merchant information appears anywhere in the project.*

## The system

- **Never-guess flags.** Each read is one JSON object per post
  (truck, post date, stops, flags). Anything unclear — a smudged
  time, a place with no street address, a week that could mean two
  Mondays — comes back `null`, explained by a flag with one of five
  fixed codes: `UNREADABLE`, `NO_STREET_ADDRESS`,
  `FLYER_NOT_CONFIRMED`, `PRIVATE_STOP`, `WEEK_UNCLEAR`. An
  employees-only stop is never returned as a stop at all; it exists
  only as a flag.
- **Guardrails.** Plain code — not the model — checks every read
  before filing: exact schema match, every date a real calendar
  date, printed times normalized to 24-hour to prove end is after
  start, and every `null` explained by a flag. Clean reads file as
  drafts; flagged reads go to a flag pile.
- **Approval gate.** The queue shows post and read side by side.
  Filing never approves anything; every approval is a person's
  explicit action. A flagged post isn't all-or-nothing — a reviewer
  can approve a single good stop out of it (per-stop approval),
  while the rest stays in the pile.
- **Provenance.** When a reviewer supplies a value the machine
  honestly left blank (a date, a place), it is recorded in its own
  `human_supplied` field on the board entry. The machine's read is
  never rewritten — you can always tell what the program read and
  what a person added.

The read itself: each picture goes to Meta's Model API vision
model (`muse-spark-1.3`) with a fixed written recipe
(`day1-slice/recipe.md`) — the same instructions every time,
weekdays anchored to the post date inside a Monday–Sunday week.

## Evidence

Tested against eight invented sample cases built to probe the
rules — including four traps where a plausible-but-invented end
time, address, private stop, or date would each be a failure. The
result, across five full runs of the suite: **40 of 40 reads
correct across 5 runs, zero invented values.** The only thing that
varied between runs was flag-note wording — the one field the
scorer sets aside by design.

Held-out: six graphics the recipe was not designed against (skewed
phone photo, decorative font, low-res screenshot, a canceled stop,
a two-truck post, a typo'd time "11 AM–2"), keys written before
any run — 18 of 18 reads correct, zero invented values. One
reliability issue was found and fixed: on the two-truck post, the
model twice spent its entire answer budget reasoning and returned
empty; the budget was raised (4,096 → 8,192) and the case re-ran
clean three times.

## Run the scorer (offline — no API key needed)

The archived real reads score against the keys with no network:

```bash
# All eight run-1 reads against the answer key (97 fields):
python3 day1-slice/score.py day1-slice/demo-intake/out/extractions.json

# A single case:
python3 day1-slice/score.py day1-slice/demo-intake/out/extraction-case1.json --case 1

# Held-out (adds an invented-value check against the graphic's printed values):
python3 heldout-cases-2026-10-26/score_heldout.py \
  heldout-cases-2026-10-26/out/run-1/h5-run1-extraction.json H5
```

(Both commands verified from this tree: `PASS — all cases match the
answer key on all 97 compared fields`, and H5 `PASS`.) The per-case
`out/caseN-extraction.json` files are the same reads in bare
single-case form; the scorer's native input is the wrapped
`extractions.json` / `extraction-caseN.json` shape used during the
runs.

`day1-slice/demo-intake/queue.html` and `board.html` are static
pages — open them in a browser to see the approval queue (post
beside read) and the demo board exactly as filed from the real
reads. To make new live reads you would implement the one seam,
`call_model_api()` in `day1-slice/demo-intake/reader.py`, against
your own Meta Model API key; no key is included in this repo, and
none is needed to verify the evidence.

## Layout

- `day1-slice/` — the harness: `recipe.md` (the fixed instructions
  sent with every image), `score.py` (field-by-field scorer; flags
  matched on code + stop + field), `extraction.template.json`, and
  `demo-intake/` (the demo approval queue: `reader.py`, the flat
  JSON store, inputs, the queue/board pages, and `out/` — the real
  run extractions, including reliability runs 2–5 under `runs/`).
- `sample-cases-2026-10-23/` — the eight sample graphics + answer
  key + the generator script that made them.
- `heldout-cases-2026-10-26/` — the six held-out graphics, their
  key (written before any run, owner rulings recorded in it),
  scorer, results, and run extractions (incl. the budget-fix
  re-runs under `out/refix-run-*`).
- `submission-writeup-draft-2026-10-26.md` — the hackathon
  submission write-up.
- `new-vs-reference-inventory-2026-10-26.md` — the full dated
  inventory behind the two sections below.
- `day1-score-sheet-cases1-2.md` — the human-readable Day-1 key.

## Built during the hackathon

Clearly identified, per the rules (all dates from the files' own
creation/modification records; the full inventory is in
`new-vs-reference-inventory-2026-10-26.md`):

**Reference state, staged the morning of Oct 26** — the harness
named in the build brief (§10): the recipe, extraction template,
scorer, and a demo intake whose model call was stubbed to refuse.
Staged before the first live call and treated as reference, not
new build work. It was *revised* that same day, on the record: the
recipe's content was replaced with the brief's §4 text verbatim,
the scorer was rewritten for the 8-case §5 shape, the template was
created in the §5 shape, and the answer key (created Oct 23) was
rewritten to the §5 shape with cases 7–8 added and one expected
value corrected on the owner's ruling.

**Built new on Oct 26, inside the window:** sample cases 7–8
(graphics); the Meta Model API connector; the live seam wiring the
stubbed intake to that API, and the first real reads; per-stop
approval and human-supplied provenance, added to the staged
intake; the demo queue and board re-filed on the real reads; the
five-run reliability suite; the held-out test kit and its 18 runs;
the answer-budget fix and its re-test; the submission write-up,
the demo video script, and this repo.

## Reference implementation (pre-existing)

What predates the hackathon and is **not** claimed as hackathon
work: the live Owensboro Market site and lunch board, its merchant
intake approval queue, and the scheduled checks that update the
board (the platform's working tree was first assembled Oct 9,
2026, and is in daily operation — the demo queue in this repo
copies its record shapes); the build plan (dated Oct 22, 2026);
the original six sample graphics and their answer key (created
Oct 23, 2026); the process graphic and Day-1 checklist (Oct 24);
and the Day-1 score sheet (Oct 25).

## Keys and data

Sample data only, throughout. The API key used for the live reads
lives in a secure vault and is swapped in by a connector at call
time; it appears in no code, file, or log in this repo. Raw API
response envelopes were kept out of the repo; the parsed
extractions are the evidence of record.
