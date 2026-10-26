# Lunch Board Reader

**Reads the picture. Flags what it can't. A human decides.**

*Submission write-up draft — Meta Global AI Developer Hackathon, Startup
track. Drafted Mon Oct 26, 2026. The demo and every number in this
write-up run on invented sample trucks — no real merchant data appears
anywhere in the build, the demo, or this submission.*

## What this is

The Lunch Board Reader is an approval system, not an image analyzer.
A vision model is one component inside it — the input stage. Around
that read sit the parts that make its output safe to publish: a
never-guess rule enforced as structured flags, programmatic
guardrails that check every read before it is filed, an approval
queue where a human compares the read against the original post, and
provenance that records what the machine read, what it refused to
read, and what a person supplied. Nothing the system produces
reaches the board on its own. That system is the product; the
picture is just how the work arrives.

## The problem

Owensboro Market is a local marketplace for Owensboro, Kentucky, launching in pilot with founding local businesses — food trucks among them. One of its pages is the lunch board: where each truck will be, day by day.

The board isn't kept by hand. Scheduled automated checks already scan the trucks' Facebook pages and update it directly. That's fast, but nothing structured is recorded about what was read, and nothing waits for a person: a misread time goes straight to the board. And truck schedules mostly arrive as pictures, with the dates, times and addresses inside the image, which is where misreads happen.

The Lunch Board Reader closes that gap. A truck's post — the picture, plus the date it was posted — goes in. The Reader turns the picture into structured stops, checks its own work, and files the result as a draft a human approves before anything reaches the board. Anything it can't read clearly is flagged for that human. Never guessed.

## What the Reader does

The Lunch Board Reader does the reading. A truck's post — the picture
plus the date it was posted — goes in. Out comes structured stops:
truck, date, start time, end time, place, address. Plain code then
checks the read, and the result is filed into an approval queue as a
draft. A human compares the draft to the post and approves it before
anything reaches the board.

The core feature is what the Reader refuses to do. Anything it can't
read clearly — a smudged time, a place with no street address, a week
that could mean two different Mondays — comes back empty, with a flag
saying exactly what's unclear. **It flags; it doesn't guess.** The
board's whole value is that people can trust it. One invented address
or time would destroy that, so the Reader is built to know what it
doesn't know.

## Who it helps

- **Truck owners**, whose stops get listed right — and whose private
  stops (an employees-only booking) never get listed at all.
- **Lunch-goers**, who at launch will check one board instead of a
  dozen Facebook pages, and can trust what it says.
- **The operator** — Owensboro Market is a one-person operation.
  The Reader turns picture-reading into review-and-approve — nothing
  it reads reaches the board until he says yes.

## How it works

- **The read.** Each picture goes to Meta's Model API vision model
  (`muse-spark-1.3`) with a fixed written recipe: the same instructions
  every time, including the output shape and the never-guess rule.
  Weekdays are anchored to the post date inside a Monday–Sunday week,
  and times stay paired with their own stop.
- **The schema.** One JSON object per post: truck, post date, stops,
  flags. Every unclear field is `null`, and every `null` is explained
  by a flag with one of five fixed codes: `UNREADABLE`,
  `NO_STREET_ADDRESS`, `FLYER_NOT_CONFIRMED`, `PRIVATE_STOP`,
  `WEEK_UNCLEAR`.
- **The guardrails.** Plain code — not the model — checks every read
  before filing: the JSON matches the schema exactly, every date is a
  real calendar date, printed times normalize to 24-hour to confirm
  end is after start, and required fields aren't silently empty. Clean
  reads file as drafts. Flagged reads go to a flag pile.
- **The human gate.** The queue shows the post and the read side by
  side. Nothing publishes itself — every approval is a person's
  explicit action. A flagged post isn't all-or-nothing: the reviewer
  can approve a single good stop out of it (per-stop approval), while
  the rest stays in the pile. When a reviewer supplies a missing value
  themselves — a date the machine honestly left blank — it's recorded
  in its own `human_supplied` field. The machine's read is never
  rewritten, so you can always tell what the program read and what a
  person added.
- **Key handling.** The API key lives only in a secure vault, swapped
  in by a connector on outgoing requests. It appears in no code, file,
  or log.

**Built with an AI coding agent.** This project was built during the
hackathon with Muse — Meta's personal AI agent — working as the coding
agent in the owner's workspace. The owner set the rules, reviewed
every result, and made the judgment calls (including overruling the
answer key once, on the record); the agent wrote and tested the code
under that direction. The Reader itself runs on Meta's Model API.

## Built during the hackathon

Clearly identified, per the rules. **What predates the hackathon:**
the live Owensboro Market site and lunch board, its merchant intake
approval queue, and the scheduled checks that update the board (the
platform's working tree was first assembled Oct 9, 2026, and is in
daily operation); the build plan (dated Oct 22); the original six
sample graphics and their answer key (created Oct 23); and the
process graphic and Day-1 checklist (Oct 24) and score sheet
(Oct 25). None of that is claimed as hackathon work.

**The reference harness (brief §10)** — the recipe, extraction
template, scorer, and a demo intake with its model call stubbed to
refuse — was staged the morning of Oct 26, before the first live
call, and is treated as reference state, not new build work. It was
*revised* that same day, on the record: the recipe's content was
replaced with the brief's §4 text verbatim, the scorer was
rewritten for the 8-case §5 shape, the template was created in the
§5 shape, and the answer key (created Oct 23) was rewritten to the
§5 shape with cases 7–8 added.

**Built new on Oct 26, inside the window:** sample cases 7–8
(graphics); the Meta Model API connector; the live seam wiring the
stubbed intake to that API, and the first real reads (case 1 shown
to the owner alone before anything else ran); per-stop approval
from the flag pile and human-supplied provenance, added to the
staged intake; the demo queue and board re-filed on the real
reads; the five-run reliability suite; the held-out test kit and
its 18 runs; the answer-budget fix and its re-test; and this
write-up, the demo video script, and the repo itself. Every date
above comes from the files' own creation/modification records; a
full dated inventory ships in the repo.

## The evidence

The Reader was tested against eight invented sample cases, each one
built to probe a rule: a clean weekly schedule, a two-stop day, an
event flyer, a smudged end time, a place with no street address, an
out-of-town stop, a post mixing a public stop with an employees-only
one, and a Sunday post with an ambiguous Monday. Four of them are
traps — a plausible-but-invented end time, address, private stop, or
date would each be a failure, however reasonable it looked.

The result, across five full runs of the suite: **40 of 40 reads
correct across 5 runs, zero invented values.** The whole five-run
suite used 104,410 tokens. The only thing that varied between runs
was the wording of the human-readable flag notes — the one field the
scorer sets aside by design, because notes are explanations for the
reviewer, not data.

Held-out results: six graphics the recipe was not designed against — a skewed phone photo, a decorative-font design, a low-res screenshot, a schedule with a canceled stop, a two-truck post, and a typo'd time ('11 AM–2') — three runs each: 18 of 18 reads correct, zero invented values. The canceled stop was excluded every time; the typo'd time was copied as printed, never completed. One reliability issue found and fixed: on the two-truck post, the model twice spent its entire answer budget reasoning and returned empty; the budget was raised and the case re-ran clean three times.

## What's next

After the hackathon: an optional `event` field, stored as its own
field, so a flyer stop can carry its event's name without ever being
merged into the place name. And the path from this demo queue to the
live board's existing intake — same record shapes, same guardrails,
and the human approval gate exactly where it is now. That gate isn't
a placeholder for fuller automation. It's the product.
