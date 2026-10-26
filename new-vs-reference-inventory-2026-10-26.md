# New vs. reference — Lunch Board Reader

*Inventory prepared Mon Oct 26, 2026, for the hackathon submission's
"new work only, clearly identified" requirement. **Every date below
comes from the filesystem** (`stat` birth time = when the file was
created in its current tree; mtime = last modification), in
America/Chicago time, cited per item. Where birth and mtime straddle
the Oct 26 line, both are reported. Nothing here is dated from
memory or summaries.*

## (i) Pre-hackathon — created before Oct 26, 2026

- **Owensboro Market — the live site, lunch board, and merchant
  intake approval queue (the platform the Reader serves).**
  Working tree `owensboro-market-good-20261009` (directory name dates
  the tree's first assembly to 2026-10-09); the tree's current copy
  was created **birth 2026-10-23 15:50** (site/index.html,
  worker/_worker.js, shared-data files all share that birth time).
  In daily operation through the hackathon: mtimes 2026-10-26 —
  site/index.html 13:49, worker 08:38, lunch.json 13:49,
  sports.json 16:08, deploy ledger (last_deploy_v2.json) 16:10.
  The intake queue's record shapes (`evt:`/`draft:` in KV) are what
  the demo queue copies. Still in pilot, behind a password.
- **The scheduled board checks** (morning + afternoon jobs that scan
  the trucks' Facebook pages and update the live board directly).
  The jobs were in daily operation before the event — their outputs
  are the live files above. Their definition files in this tree
  (crons/daily/monday-lunch-board-check, afternoon-truck-check) were
  **regenerated 2026-10-26 10:02–10:03 (birth = mtime)** when an
  append-only section was added that day under the owner's
  dated-backup rule — a revision of pre-existing jobs, annotated
  here rather than re-dated.
- **GOAL.md** (this goal's charter) — **mtime 2026-10-22 17:14**;
  in-tree birth 2026-10-23 15:50 (copied in with the tree setup).
- **Build plan** — `lunch-board-reader-build-plan-2026-10-22.md`,
  dated **2026-10-22** (filename; matches GOAL.md's mtime);
  in-tree birth 2026-10-23 15:50; **mtime 2026-10-26 14:31** —
  annotation: the Oct 26 edit removed one real business name from a
  planning parenthetical under the owner's separation rule; the
  plan's substance is unchanged.
- **Sample-case kit, original six cases** — graphics
  case1–case6 **birth 2026-10-23 18:22** each; `answer-key.json`
  birth 2026-10-23 18:23; `answer-key.md` birth 2026-10-23 18:23;
  generator `make_sample_cases.py` birth 2026-10-23 18:22.
  Annotations (all Oct 26 revisions of pre-existing files):
  graphics re-rendered byte-identical **mtime 2026-10-26 12:02**;
  generator modified **mtime 2026-10-26 12:02** (cases 7–8 added);
  answer key **rewritten mtime 2026-10-26 14:48** — moved to the
  §5 shape, cases 7–8 entries added, and case 3's expected place
  corrected on the owner's ruling (the model had read the printed
  venue correctly; the correction is logged in the key's own
  `key_changes` record).
- **Process graphic** — `lunch-board-reader-process-graphic-2026-10-24`
  (.html + .png): **birth = mtime 2026-10-24 10:38**.
- **Day-1 checklist** — `day1-checklist-2026-10-26.md`:
  **birth = mtime 2026-10-24 14:21** (prepared Oct 24 for Oct 26).
- **Day-1 score sheet (cases 1–2)** — `day1-score-sheet-cases1-2.md`:
  **birth 2026-10-25 14:22**; mtime 2026-10-26 12:03 (touched
  during the Oct 26 midday spec update).
- **Hackathon application** — *no artifact exists in the local
  filesystem* (it was submitted through Meta's portal; the
  submission record lives there, outside filesystem evidence).
  The local pointer is GOAL.md, mtime 2026-10-22. Dated here as
  pre-hackathon on that basis, and flagged as the one item whose
  date the filesystem cannot itself prove.

## (ii) Reference state staged the morning of Oct 26 — the brief §10 harness

The build brief (§10) designates this harness as the reference
implementation the live build started from. The filesystem shows it
was created the **morning of Oct 26, before the first live call**
(credits landed 14:34; first extraction born 14:37) — so it is
listed separately, with both dates, rather than folded into either
list. Itemized per §10:

- **The build brief itself** — `build-brief-for-claude-2026-10-26.md`:
  **birth 2026-10-26 11:52, mtime 2026-10-26 15:53**. The owner's
  revised spec (§4 recipe, §5 schema, §6 cases, §10 this reference
  state). Same-day mtime annotations: Step 6 redefinition and §1
  alignment edits during the afternoon.
- **Recipe** — `day1-slice/recipe.md`: **birth 2026-10-26 11:21,
  mtime 2026-10-26 12:01** — annotation: at the midday spec update
  its content was replaced with the brief's §4 text verbatim.
- **Scorer** — `day1-slice/score.py`: **birth 2026-10-26 11:21,
  mtime 2026-10-26 12:04** — annotation: rewritten at midday for
  the 8-case §5 shape (flags matched on code + stop + field) with
  doctored-key self-checks.
- **Extraction template** — `day1-slice/extraction.template.json`:
  **birth = mtime 2026-10-26 12:01** — created directly in the §5
  shape at the midday update; no earlier version exists in this
  tree.
- **Stubbed demo intake** — `day1-slice/demo-intake/`:
  store files + inputs **birth 2026-10-26 11:43**; `reader.py`
  **birth 2026-10-26 11:44, mtime 2026-10-26 15:35**;
  `demo-intake/README.md` birth 11:44, mtime 12:30; `queue.html`
  birth 11:44, **mtime 15:00**; `board.html` **birth 12:17**,
  mtime 15:00. At creation, `call_model_api()` was a stub that
  refused to run (no key/credits path yet); guardrails + filing
  were exercised on stand-in reads, and the Step 5 queue/board were
  rendered from those stand-ins (~12:17). Same-day revisions to
  `reader.py` (its 15:35 mtime is the trail): per-stop approval +
  human-supplied provenance added midday; the seam wired to the
  live API at 14:37; the answer budget raised 4,096 → 8,192 at
  15:35. Store files were reset and re-filed with the real reads
  at ~15:00 (their mtimes); the stand-in state was preserved
  byte-identical in `baseline-standin-2026-10-26/` (kept out of
  the public repo by the owner's exclusion list).
- **Day-1 slice README** — `day1-slice/README.md`:
  birth 2026-10-26 11:21, mtime 12:30.

## (iii) Built during the hackathon — created Oct 26, 2026, from the live build onward

- **Sample cases 7–8 graphics** (private stop; Sunday post) —
  **birth = mtime 2026-10-26 12:02**, added to the pre-existing
  kit (see the kit's annotations in part (i)).
- **Meta Model API connector** — `custom.meta-model-api`:
  CONNECTOR.md **birth 2026-10-26 12:02**, helper
  `bin/meta_model_api.py` **birth 2026-10-26 12:03**. New tooling
  built for this event; the owner's dedicated API key was stored
  in Muse's Secure Vault the same day — the key exists in no
  file (verifiable: the repo scan covers every staged file).
- **Per-stop approval + human-supplied provenance** — added to the
  staged harness's `reader.py` on Oct 26 (see its mtime trail in
  part (ii)): one stop out of a flagged post can be approved while
  the rest stays in the flag pile; a stop that exists only as a
  flag (`PRIVATE_STOP`) has no approval path; reviewer-supplied
  values are recorded in their own `human_supplied` field and the
  machine's read is never rewritten. 66 checks incl. refusal tests.
- **Live seam + first real reads** — `call_model_api()` implemented
  against the connector (model `muse-spark-1.3`); first real
  extraction **born 2026-10-26 14:37** (case 1, shown to the owner
  alone before anything else ran), then case 2, then cases 3–8
  one at a time under a stop-on-any-failure rule.
- **Five-run reliability suite** — runs 2–5 extractions under
  `demo-intake/out/runs/` (last file **born 2026-10-26 15:04**):
  40 of 40 reads correct across 5 runs, zero invented values;
  104,410 tokens total. Only flag-note wording varied — the field
  the scorer ignores by design.
- **Held-out test kit** — `heldout-cases-2026-10-26/`:
  key **birth 2026-10-26 15:11** (written before any run, with
  the owner's two rulings recorded in it), graphics **birth
  15:12**, scorer **birth 15:13**, results **birth 15:19** —
  six graphics the recipe was not designed against, 18 of 18
  reads correct, zero invented values.
- **Answer-budget fix** — the held-out two-truck post twice
  returned empty after burning the 4,096-token completion budget
  on reasoning; budget raised to 8,192 in `reader.py`
  (**mtime 2026-10-26 15:35**, dated code comment); three clean
  re-runs followed (last refix extraction **born 15:36**), one
  using 5,178 completion tokens — over the old cap.
- **Spend log** — `hidden_files/spend-log.md`: birth 2026-10-26
  14:38, mtime 15:36. Per-call token record for every live read.
  *Private — excluded from the public repo.*
- **Submission materials** — write-up draft **birth 2026-10-26
  15:09**; video script draft **birth 2026-10-26 15:09** (owner's
  own paragraph and Beat 1 lines inserted verbatim the same day);
  Oct 31 dry-run sheet **birth = mtime 2026-10-26 16:21**; this
  inventory; and the staged public repo (assembled Oct 26).
