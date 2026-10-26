#!/usr/bin/env python3
"""Lunch Board Reader — Day-1 harness skeleton (DEMO ONLY, sample data only).

Pipeline (Oct 22 build plan):
  1. Recipe  — fixed instruction (../recipe.md) sent with every image.
  2. Plumbing — image + post date -> Meta Model API vision read -> structured stops.
  3. Guardrails — real date? times sane? anything flagged?
       pass  -> approval-ready draft filed in the DEMO intake queue copy
       fail  -> flag pile in the DEMO store, for a human. Nothing auto-publishes.

The demo store in ./store mirrors the live intake queue's shapes exactly
(events / drafts / indexes as flat JSON files standing in for the live KV
entries). This script NEVER touches the live Owensboro Market tree.

Modes:
  python3 reader.py --case 1            stub run (credits not live yet -> flag pile)
  python3 reader.py --all               stub run for every staged input case
  python3 reader.py --all --simulate extraction.json
                                        dry run: skip the model call, feed a
                                        hand-filled extraction (brief s5 schema)
                                        through guardrails + filing instead.
                                        The Step 5 early build used this in
                                        stand-in mode with the answer key.
  python3 reader.py --approve <event_id>
                                        demo approval: mark that event's draft
                                        approved (repeatable), then re-render
  python3 reader.py --approve-stop <event_id> <stop_index>
                    [--resolve-date YYYY-MM-DD] [--resolve-place PLACE]
                                        per-stop reviewer approval from the
                                        flag pile (owner addition, brief s3.3):
                                        put ONE returned stop of a flagged post
                                        on the board. A stop with null date or
                                        place refuses unless the reviewer
                                        supplies the value (recorded as
                                        human_supplied). stop=null flags are
                                        not stops and can never be approved.
  python3 reader.py --render-only       rebuild queue.html + board.html

Exit codes: 0 = ran and filed output (stub output included), 2 = bad input.
"""
import argparse, datetime, html, json, random, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLICE = HERE.parent
RECIPE_FILE = SLICE / "recipe.md"
STORE = HERE / "store"
INPUTS = HERE / "inputs"
OUT = HERE / "out"
QUEUE_HTML = HERE / "queue.html"
BOARD_HTML = HERE / "board.html"
COMBINED_OUT = OUT / "extractions.json"


class AwaitingAccessError(RuntimeError):
    """Raised by the model-call stub until the free credits land."""


# --------------------------------------------------------------------------
# Piece 2 (plumbing): the Meta Model API call — REAL (seam implemented
# 2026-10-26, the Day-1 first real run).
# --------------------------------------------------------------------------
MODEL_ID = "muse-spark-1.3"
CONNECTOR_HELPER = (Path.home() / "workspace" / "custom-connectors"
                    / "custom.meta-model-api" / "bin" / "meta_model_api.py")


def call_model_api(image_path, prompt):
    """THE READ SEAM — the single place a model read happens.

    Send one image + the recipe prompt to the Meta Model API vision model
    (via the connector helper, see CONNECTOR.md for custom.meta-model-api)
    and return the parsed structured extraction: one post object in the
    revised brief s5 schema — {truck, post_date, stops[], flags[]} (the
    harness adds its case/file bookkeeping around it).

    Stand-in mode (the Step 5 early build) never reaches this function:
    --simulate feeds extractions (the answer key's) through the same
    guardrails + filing instead. Real mode changed ONLY this function —
    the recipe, guardrails, filing, queue and board are untouched.

    Billing gate: OPEN. The owner (Kelley) confirmed the $150 hackathon
    free credits are live on 2026-10-26 ($150.00 showing under Billing ->
    Free credits in use, dev.meta.ai console), so real calls are allowed
    and draw on the free credit pool. Before that confirmation this seam
    refused to call (uncredited calls charge the card on file).

    The API key is NOT read here, is never in this project, and is never
    in an environment variable on this machine: it is held in Muse's
    Secure Vault under connector custom.meta-model-api, and the
    connector helper attaches it at call time.

    Side effects (for the record + cost tracking): the FULL raw API
    response is saved to out/<caseN>-raw-response.json and the parsed
    extraction to out/<caseN>-extraction.json, next to the harness's own
    out/extraction-caseN.json that run_case writes.
    """
    image_path = Path(image_path)
    if not image_path.exists():
        # run_case resolves the manifest's demo_image against HERE, but the
        # manifest paths are written relative to inputs/ — so the resolved
        # path misses the demo store's own copy by one directory. Fall back
        # to the store copy by file name (byte-identical to the kit image;
        # sha256-verified 2026-10-26).
        store_copy = HERE / "store" / "images" / image_path.name
        if store_copy.exists():
            image_path = store_copy
    cmd = [sys.executable, str(CONNECTOR_HELPER), "vision",
           "--image", str(image_path),
           "--prompt", prompt,
           "--model", MODEL_ID,
           # 2026-10-26: raised 4096 → 8192 — H5 collab reads twice burned
           # the full budget on reasoning and returned empty (owner-ordered fix).
           "--max-tokens", "8192"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise RuntimeError(
            "connector helper vision call failed "
            f"(exit {proc.returncode}): {proc.stderr.strip()[:800]}")
    try:
        raw = json.loads(proc.stdout)
    except ValueError:
        raise RuntimeError("connector helper returned non-JSON stdout: "
                           + proc.stdout[:400])
    m = re.match(r"(case\d+)", Path(image_path).name)
    stem = m.group(1) if m else Path(image_path).stem
    OUT.mkdir(exist_ok=True)
    save_json(OUT / f"{stem}-raw-response.json", raw)
    choices = raw.get("choices") or []
    if not choices:
        raise RuntimeError("API response carried no choices: "
                           + json.dumps(raw)[:400])
    content = (choices[0].get("message") or {}).get("content")
    if isinstance(content, list):  # content-parts shape: join the text parts
        text = "".join(p.get("text", "") for p in content
                       if isinstance(p, dict))
    else:
        text = content
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("API response first choice carried no text "
                           "content: " + json.dumps(raw)[:400])
    text = text.strip()
    if text.startswith("```"):  # recipe says no fences; tolerate them anyway
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    extraction = json.loads(text)
    save_json(OUT / f"{stem}-extraction.json", extraction)
    return extraction


# --------------------------------------------------------------------------
# Piece 1 (recipe): load the fixed instruction with the post date filled in.
# --------------------------------------------------------------------------
def load_recipe(posted_iso):
    d = datetime.date.fromisoformat(posted_iso)
    return (
        RECIPE_FILE.read_text()
        .replace("<POST_DATE as YYYY-MM-DD>", posted_iso)
        .replace("<WEEKDAY>", d.strftime("%A"))
    )


# --------------------------------------------------------------------------
# Piece 3 (guardrails): program checks before anything is filed as a draft.
# Implements revised brief s3.3 against the s5 schema:
#   exact schema check (keys, types, flag codes) - real calendar dates -
#   times normalized to 24-hour internally to verify end > start (the draft
#   keeps the printed times; an unparseable time is itself a failure) -
#   required fields (date, place) not null - every null explained by a flag.
# --------------------------------------------------------------------------
FLAG_CODES = {"UNREADABLE", "NO_STREET_ADDRESS", "FLYER_NOT_CONFIRMED",
              "PRIVATE_STOP", "WEEK_UNCLEAR"}
STOP_FIELDS = ["date", "start", "end", "place", "address"]
CORE_KEYS = {"truck", "post_date", "stops", "flags"}
HARNESS_KEYS = {"case", "file"}  # bookkeeping the harness adds around a post object

TIME_RE = re.compile(r"^(\d{1,2})(?::(\d{2}))?\s*([AP]M)$", re.I)


def parse_time(s):
    """Normalize a printed time ("11 AM", "11:00 AM", "2:30 PM") to minutes
    after midnight; None if unparseable. Internal check only — filed drafts
    keep the times exactly as printed."""
    if not s:
        return None
    m = TIME_RE.match(str(s).strip())
    if not m:
        return None
    h = int(m.group(1))
    mi = int(m.group(2)) if m.group(2) is not None else 0
    ap = m.group(3).upper()
    if not (1 <= h <= 12 and 0 <= mi <= 59):
        return None
    if ap == "PM" and h != 12:
        h += 12
    if ap == "AM" and h == 12:
        h = 0
    return h * 60 + mi


def _real_date(v):
    if not isinstance(v, str):
        return False
    try:
        datetime.datetime.strptime(v, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_schema(case):
    """Exact s5 schema check. Returns a list of problem strings (empty = ok)."""
    problems = []
    if not isinstance(case, dict):
        return ["extraction is not a JSON object"]
    keys = set(case)
    missing = CORE_KEYS - keys
    extra = keys - CORE_KEYS - HARNESS_KEYS
    if missing:
        problems.append(f"schema: missing key(s) {sorted(missing)}")
    if extra:
        problems.append(f"schema: unexpected key(s) {sorted(extra)}")
    if "truck" in case and case["truck"] is not None \
            and not isinstance(case["truck"], str):
        problems.append("schema: truck is not a string or null")
    if "post_date" in case and not _real_date(case.get("post_date")):
        problems.append(f"schema: post_date {case.get('post_date')!r} "
                        "is not a real YYYY-MM-DD date")
    stops = case.get("stops")
    if not isinstance(stops, list):
        problems.append("schema: stops is not an array")
        stops = []
    for i, s in enumerate(stops):
        if not isinstance(s, dict):
            problems.append(f"schema: stop {i} is not an object")
            continue
        if set(s) != set(STOP_FIELDS):
            problems.append(f"schema: stop {i} keys are {sorted(s)}, "
                            f"want exactly {STOP_FIELDS}")
        for f in STOP_FIELDS:
            if f in s and s[f] is not None and not isinstance(s[f], str):
                problems.append(f"schema: stop {i} {f} is not a string or null")
    flags = case.get("flags")
    if not isinstance(flags, list):
        problems.append("schema: flags is not an array")
        flags = []
    for j, fl in enumerate(flags):
        if not isinstance(fl, dict):
            problems.append(f"schema: flag {j} is not an object")
            continue
        if set(fl) != {"code", "stop", "field", "note"}:
            problems.append(f"schema: flag {j} keys are {sorted(fl)}, "
                            "want exactly code/field/note/stop")
        if fl.get("code") not in FLAG_CODES:
            problems.append(f"schema: flag {j} code {fl.get('code')!r} "
                            "is not a valid flag code")
        st = fl.get("stop")
        if st is not None and (isinstance(st, bool) or not isinstance(st, int)
                               or not 0 <= st < len(stops)):
            problems.append(f"schema: flag {j} stop {st!r} is not a valid "
                            "stop index or null")
        if fl.get("field") is not None and fl.get("field") not in STOP_FIELDS:
            problems.append(f"schema: flag {j} field {fl.get('field')!r} "
                            "is not a stop field or null")
        if not isinstance(fl.get("note"), str):
            problems.append(f"schema: flag {j} note is not a string")
    return problems


def format_flag(fl):
    """Render a model flag object as one human line for the flag pile."""
    where = ""
    if fl.get("stop") is not None:
        where = f"stop {fl['stop'] + 1}"
        if fl.get("field"):
            where += f", {fl['field']}"
    elif fl.get("field"):
        where = fl["field"]
    return f"{fl.get('code')}" + (f" ({where})" if where else "") \
        + f": {fl.get('note')}"


def guardrails(case, expected_post_date=None):
    """Return (route, problems, model_flags) where route is 'draft' or 'flag'.
    A case routes to the flag pile if the model flagged anything OR any
    program check fails. Flagged/unclear is a valid outcome; guessed is not."""
    problems = validate_schema(case)
    model_flags = case.get("flags") if isinstance(case.get("flags"), list) else []
    stops = case.get("stops") if isinstance(case.get("stops"), list) else []

    if expected_post_date and case.get("post_date") not in (None, expected_post_date):
        problems.append(f"post_date {case.get('post_date')!r} does not match "
                        f"the post's date {expected_post_date!r}")
    if not stops and not model_flags and not problems:
        problems.append("no stops extracted and nothing flagged - needs a human look")

    def explained(i, field):
        return any(fl.get("stop") == i and fl.get("field") == field
                   for fl in model_flags if isinstance(fl, dict))

    for i, s in enumerate(stops):
        if not isinstance(s, dict):
            continue
        n = i + 1
        # real calendar date? (null date is a required-field failure below)
        if s.get("date") is not None and not _real_date(s["date"]):
            problems.append(f"stop {n}: date {s['date']!r} is not a real YYYY-MM-DD date")
        # required fields: date and place must not be null.
        if s.get("date") is None:
            problems.append(f"stop {n}: date is null (required field)")
        if s.get("place") is None:
            problems.append(f"stop {n}: place is null (required field)")
        # every other null must be explained by a flag on that stop+field.
        for f in ("start", "end", "address"):
            if s.get(f) is None and not explained(i, f):
                problems.append(f"stop {n}: {f} is null with no flag explaining it")
        # times sane? normalize to 24-hour; unparseable is itself a failure.
        st, en = parse_time(s.get("start")), parse_time(s.get("end"))
        if s.get("start") is not None and st is None:
            problems.append(f"stop {n}: start time {s.get('start')!r} cannot be parsed")
        if s.get("end") is not None and en is None:
            problems.append(f"stop {n}: end time {s.get('end')!r} cannot be parsed")
        if st is not None and en is not None and en <= st:
            problems.append(f"stop {n}: end time is not after start time")
    route = "flag" if (problems or model_flags) else "draft"
    return route, problems, model_flags


# --------------------------------------------------------------------------
# Filing into the DEMO store (mirrors the live intake draft/event shapes).
# --------------------------------------------------------------------------
def load_json(path, fallback):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return fallback


def save_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def draft_id():
    # Mirrors the live draft id style: base36 timestamp + base36 random.
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"

    def b36(n):
        out = ""
        while n:
            n, r = divmod(n, 36)
            out = digits[r] + out
        return out or "0"

    return "d" + b36(time.time_ns() // 1_000_000) + b36(random.randint(0, 46655))


def summarize_stops(stops):
    parts = []
    for s in stops:
        t = f"{s.get('start') or '?'}-{s.get('end') or '?'}"
        addr = f" ({s['address']})" if s.get("address") else " (no street address)"
        parts.append(f"{s.get('date')} {t} {s.get('place')}{addr}")
    return ("Lunch Board Reader draft: " + "; ".join(parts))[:600]


def file_result(case_input, case, extra_problems=None):
    """File one read case into the demo store: draft (pass) or flag pile."""
    route, problems, model_flags = guardrails(case, case_input.get("posted"))
    problems = list(extra_problems or []) + problems
    if problems:
        route = "flag"
    # Flag-pile entries keep the live-mirrored shape: flags as human lines —
    # the model's coded flags first, then any guardrail problems.
    flag_lines = [format_flag(f) for f in model_flags if isinstance(f, dict)]
    flag_lines += [p for p in problems if p not in flag_lines]
    events = load_json(STORE / "events.json", [])
    ev = next((e for e in events if e["id"] == case_input["event_id"]), None)
    if ev is None:
        raise SystemExit(f"event {case_input['event_id']} not in demo store")
    if route == "draft":
        drafts = load_json(STORE / "drafts.json", [])
        idx = load_json(STORE / "draft_index.json", [])
        draft = {
            "id": draft_id(),
            "event_id": ev["id"],
            "kind": "Other update",
            "note": summarize_stops(case.get("stops") or []),
            "ts": now_iso(),
            "status": "awaiting merchant text approval",
            # Demo-only extension: the Reader's structured read, shown beside
            # the post in queue.html. The live draft shape above is unchanged.
            "reader": {"truck": case.get("truck"),
                       "stops": case.get("stops") or [], "flags": []},
        }
        # (drafts are only filed when guardrails pass with no flags)
        drafts.insert(0, draft)
        idx.insert(0, draft["id"])
        save_json(STORE / "drafts.json", drafts)
        save_json(STORE / "draft_index.json", idx)
        return route, draft
    pile = load_json(STORE / "flag_pile.json", [])
    entry = {
        "id": "f" + draft_id()[1:],
        "event_id": ev["id"],
        "ts": now_iso(),
        "flags": flag_lines,
        "stops": case.get("stops") or [],
        "truck": case.get("truck"),
    }
    pile.insert(0, entry)
    save_json(STORE / "flag_pile.json", pile)
    return route, entry


def approve_draft(event_id):
    """Demo approval step, mirroring the production flow: a filed draft
    waits at status 'awaiting merchant text approval' until the human
    approves it; only then does it reach the (demo) board. Returns the
    approved draft, or None if the event has no draft.
    Demo-only extension: approved_ts records when the approval landed."""
    drafts = load_json(STORE / "drafts.json", [])
    for d in drafts:
        if d.get("event_id") == event_id:
            d["status"] = "approved"
            d["approved_ts"] = now_iso()
            save_json(STORE / "drafts.json", drafts)
            return d
    return None


def approve_stop(event_id, stop_index_raw, resolve_date=None, resolve_place=None):
    """Per-stop reviewer approval from the flag pile (owner addition,
    2026-10-26; brief s3.3). Approving ONE returned stop of a flagged post
    creates a board-eligible single-stop entry in store/board_entries.json;
    the parent item STAYS in the flag pile with its flags intact, recording
    the approved index on the item itself (approved_stop_indexes).

    Safety rails (enforced here — this is the only per-stop approval path):
      - Only stops actually returned in the read have indexes. A flag with
        stop=null (PRIVATE_STOP, FLYER_NOT_CONFIRMED) is not a stop and can
        never be approved: it has no index to approve.
      - A stop with null date or null place cannot be approved bare: the
        reviewer must supply the missing value (--resolve-date /
        --resolve-place), recorded under provenance.human_supplied.
        Without the resolution the approval REFUSES and changes nothing.
      - Filing never calls this. Approvals happen only through the explicit
        --approve / --approve-stop actions; nothing approves automatically.
    Returns (entry, None) on success, (None, refusal_message) otherwise.
    """
    pile = load_json(STORE / "flag_pile.json", [])
    item = next((p for p in pile if p.get("event_id") == event_id), None)
    if item is None:
        return None, (f"event {event_id} is not in the flag pile (per-stop "
                      "approval applies to flag-pile items; whole reads are "
                      "approved with --approve)")
    if str(stop_index_raw).strip().lower() == "null":
        return None, ("stop=null flags (PRIVATE_STOP, FLYER_NOT_CONFIRMED) "
                      "are not returned stops and can never be approved "
                      "onto the board")
    try:
        idx = int(stop_index_raw)
    except (TypeError, ValueError):
        return None, f"stop index {stop_index_raw!r} is not a stop index"
    stops = item.get("stops") or []
    if idx < 0 or idx >= len(stops):
        return None, (f"stop index {idx} is out of range: the read returned "
                      f"{len(stops)} stop(s), indexes 0..{len(stops) - 1}")
    approved = item.get("approved_stop_indexes") or []
    if idx in approved:
        return None, (f"stop {idx + 1} of event {event_id} is already "
                      "approved; refusing to approve it twice")
    stop = dict(stops[idx])
    human_supplied = {}
    if stop.get("date") is None:
        if not resolve_date:
            return None, (f"stop {idx + 1} has a null date: supply "
                          "--resolve-date YYYY-MM-DD (the reviewer's pick, "
                          "recorded as human_supplied) to approve it")
        if not _real_date(resolve_date):
            return None, (f"--resolve-date {resolve_date!r} is not a real "
                          "YYYY-MM-DD date")
        stop["date"] = resolve_date
        human_supplied["date"] = resolve_date
    if stop.get("place") is None:
        if not resolve_place:
            return None, (f"stop {idx + 1} has a null place: supply "
                          "--resolve-place \"<place>\" (recorded as "
                          "human_supplied) to approve it")
        stop["place"] = resolve_place
        human_supplied["place"] = resolve_place
    entry = {
        "id": "b" + draft_id()[1:],
        "event_id": event_id,
        "kind": "Reader stop approval (demo)",
        "truck": item.get("truck"),
        "stop": stop,
        # Provenance: where this board entry came from and how it got
        # approved. approval states plainly it was a reviewer action.
        "provenance": {
            "source": "flag_pile",
            "source_event_id": event_id,
            "source_flag_entry_id": item.get("id"),
            "stop_index": idx,
            "approved_ts": now_iso(),
            "approval": "reviewer action - explicit per-stop approval "
                        "(--approve-stop); nothing approves automatically",
            "human_supplied": human_supplied,
        },
    }
    entries = load_json(STORE / "board_entries.json", [])
    entries.insert(0, entry)
    item["approved_stop_indexes"] = sorted(approved + [idx])
    save_json(STORE / "board_entries.json", entries)
    save_json(STORE / "flag_pile.json", pile)
    return entry, None


def write_extraction(case):
    OUT.mkdir(exist_ok=True)
    save_json(OUT / f"extraction-case{case['case']}.json", {"cases": [case]})
    combined = load_json(COMBINED_OUT, {"kit": "Lunch Board Reader extraction (brief s5 schema)", "cases": []})
    by_case = {c["case"]: c for c in combined.get("cases", [])}
    by_case[case["case"]] = case
    combined["cases"] = [by_case[k] for k in sorted(by_case)]
    save_json(COMBINED_OUT, combined)


# --------------------------------------------------------------------------
# Side-by-side demo queue page: post (picture + text) beside the Reader read.
# --------------------------------------------------------------------------
def render_queue():
    events = load_json(STORE / "events.json", [])
    idx = load_json(STORE / "evt_index.json", [e["id"] for e in events])
    by_id = {e["id"]: e for e in events}
    drafts = {d["event_id"]: d for d in load_json(STORE / "drafts.json", [])}
    pile = {p["event_id"]: p for p in load_json(STORE / "flag_pile.json", [])}
    extractions = {}
    combined = load_json(COMBINED_OUT, {"cases": []})
    ev_case = {}
    for ci in INPUTS.glob("case*.json"):
        inp = load_json(ci, {})
        if inp.get("event_id"):
            ev_case[inp["event_id"]] = inp.get("case")
    for c in combined.get("cases", []):
        for eid, n in ev_case.items():
            if n == c.get("case"):
                extractions[eid] = c

    def esc(s):
        return html.escape(str(s if s is not None else ""))

    cards = []
    for eid in idx:
        e = by_id.get(eid)
        if not e:
            continue
        left = (
            f"<div class='post'><div class='meta'>{esc(e.get('ts'))} &middot; "
            f"{esc(e.get('verb') or e.get('item') or e.get('field') or 'post')} "
            f"&middot; page {esc(e.get('page_id'))} (DEMO)</div>"
            f"<img src='store/{esc(e.get('image'))}' alt='sample schedule graphic'>"
            f"<div class='excerpt'>{esc(e.get('excerpt') or '(no text)')}</div>"
            f"<div class='meta'>Post date (weekday anchor): {esc(e.get('posted'))}</div></div>"
        )
        if eid in drafts:
            d = drafts[eid]
            rows = "".join(
                f"<tr><td>{esc(s.get('date'))}</td><td>{esc(s.get('start'))}&ndash;{esc(s.get('end'))}</td>"
                f"<td>{esc(s.get('place'))}</td><td>{esc(s.get('address') or '(none)')}</td></tr>"
                for s in d["reader"]["stops"]
            )
            right = (
                f"<div class='reader'><h3>Reader draft — ready for approval</h3>"
                f"<table><tr><th>Date</th><th>Time</th><th>Place</th><th>Address</th></tr>{rows}</table>"
                f"<div class='note'>{esc(d.get('note'))}</div>"
                f"<span class='pill{' approved' if d.get('status') == 'approved' else ''}'>"
                f"{esc(d.get('status'))}</span></div>"
            )
        elif eid in pile:
            p = pile[eid]
            fl = "".join(f"<li>{esc(f)}</li>" for f in p["flags"])
            approved_idx = set(p.get("approved_stop_indexes") or [])
            rows = "".join(
                f"<tr><td>{esc(s.get('date') or '(unresolved)')}</td>"
                f"<td>{esc(s.get('start') or '(unknown)')}&ndash;{esc(s.get('end') or '(unknown)')}</td>"
                f"<td>{esc(s.get('place') or '(unknown)')}</td>"
                f"<td>{esc(s.get('address') or '(none)')}</td>"
                f"<td>{'approved &rarr; on board' if i in approved_idx else 'awaiting reviewer'}</td></tr>"
                for i, s in enumerate(p.get("stops") or [])
            )
            stop_tbl = (
                f"<table><tr><th>Date</th><th>Time</th><th>Place</th><th>Address</th>"
                f"<th>Stop review</th></tr>{rows}</table>"
                if rows else "<p>No stops were returned.</p>"
            )
            # Flags whose line carries no "(stop N...)" marker are stop=null
            # flags: they are about stops that were NOT returned, so they are
            # visibly not stops and have no approval path onto the board.
            null_codes = []
            for line in p["flags"]:
                m = re.match(r"^([A-Z_]+):", str(line))
                if m:
                    null_codes.append(m.group(1))
            not_stop = (
                f"<p class='note'>Flag(s) {esc(', '.join(null_codes))} are about "
                "stops that were not returned — they are not stops and can never "
                "be approved onto the board.</p>"
                if null_codes else ""
            )
            right = (
                f"<div class='reader flag'><h3>Flagged — needs a human</h3>"
                f"<ul>{fl}</ul>{stop_tbl}{not_stop}"
                f"<span class='pill warn'>flag pile</span></div>"
            )
        else:
            right = ("<div class='reader'><h3>Not yet read</h3>"
                     "<p>No extraction has been filed for this post yet.</p></div>")
        cards.append(f"<div class='row'>{left}{right}</div>")

    n_approved = sum(1 for d in drafts.values() if d.get("status") == "approved")
    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Merchant intake — DEMO copy (Lunch Board Reader)</title>
<style>
body{{font-family:Georgia,serif;background:#f7f3ea;color:#2b2b2b;margin:0;}}
.wrap{{max-width:1060px;margin:0 auto;padding:28px 18px 80px;}}
h1{{font-size:24px;color:#1b2a4a;margin:6px 0 4px;}}
.sub{{color:#6b6257;font-size:14px;margin:0 0 18px;}}
.row{{display:flex;gap:16px;background:#fff;border:1px solid #e4dccb;border-radius:10px;padding:14px 16px;margin:0 0 14px;}}
.post,.reader{{flex:1;min-width:0;}}
.post img{{max-width:100%;border:1px solid #e4dccb;border-radius:6px;}}
.meta{{color:#6b6257;font-size:12.5px;margin:4px 0;}}
.excerpt{{font-size:15px;line-height:1.55;margin:6px 0;}}
.reader h3{{margin:2px 0 10px;font-size:16px;color:#1b2a4a;}}
.reader.flag{{background:#fdf3e0;border-radius:6px;padding:8px 12px;}}
.reader table{{border-collapse:collapse;font-size:13.5px;}}
.reader th,.reader td{{border:1px solid #e4dccb;padding:4px 7px;text-align:left;}}
.note{{font-size:13px;color:#6b6257;margin:8px 0;}}
.pill{{display:inline-block;background:#e8f3e4;border:1px solid #b9d6ae;border-radius:20px;padding:2px 10px;font-size:12.5px;}}
.pill.warn{{background:#fbe9c8;border-color:#e0b96a;}}
.pill.approved{{background:#cfe8c4;border-color:#7aa964;font-weight:bold;}}
</style></head><body><div class="wrap">
<h1>Merchant intake — DEMO copy</h1>
<p class="sub">Lunch Board Reader Day-1 slice. Sample data only (invented trucks).
Left: the post as it lands in the queue. Right: the Reader's structured read —
an approval-ready draft, or the flag pile. Nothing here touches the live site.</p>
<p class="sub">{len(idx)} posts &middot; {len(drafts)} drafts ({n_approved} approved) &middot; {len(pile)} in the flag pile</p>
{''.join(cards) if cards else '<p>No events in the demo queue.</p>'}
</div></body></html>
"""
    QUEUE_HTML.write_text(doc)
    return QUEUE_HTML


# --------------------------------------------------------------------------
# Demo lunch board: APPROVED drafts plus stops a reviewer individually
# approved out of the flag pile (store/board_entries.json), grouped by date.
# A flagged read as a whole never reaches the board — only an explicit
# per-stop reviewer approval moves one of its stops here (brief s3.3).
# --------------------------------------------------------------------------
def render_board():
    drafts = load_json(STORE / "drafts.json", [])
    by_date = {}
    for d in drafts:
        if d.get("status") != "approved":
            continue
        reader = d.get("reader") or {}
        for s in reader.get("stops") or []:
            if s.get("date"):
                by_date.setdefault(s["date"], []).append((reader.get("truck"), s))
    for en in load_json(STORE / "board_entries.json", []):
        s = en.get("stop") or {}
        if s.get("date"):
            by_date.setdefault(s["date"], []).append((en.get("truck"), s))

    def esc(v):
        return html.escape(str(v if v is not None else ""))

    sections = []
    for date in sorted(by_date):
        d0 = datetime.date.fromisoformat(date)
        rows = "".join(
            f"<tr><td>{esc(truck)}</td>"
            f"<td>{esc(s.get('start'))}&ndash;{esc(s.get('end'))}</td>"
            f"<td>{esc(s.get('place'))}</td>"
            f"<td>{esc(s.get('address') or '(none)')}</td></tr>"
            for truck, s in by_date[date]
        )
        sections.append(
            f"<h2>{esc(d0.strftime('%A, %B ') + str(d0.day) + d0.strftime(', %Y'))} "
            f"<span class='meta'>({esc(date)})</span></h2>"
            f"<table><tr><th>Truck</th><th>Time</th><th>Place</th><th>Address</th></tr>{rows}</table>"
        )

    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Lunch board — DEMO copy (Lunch Board Reader)</title>
<style>
body{{font-family:Georgia,serif;background:#f7f3ea;color:#2b2b2b;margin:0;}}
.wrap{{max-width:860px;margin:0 auto;padding:28px 18px 80px;}}
h1{{font-size:24px;color:#1b2a4a;margin:6px 0 4px;}}
h2{{font-size:18px;color:#1b2a4a;margin:22px 0 8px;}}
.sub{{color:#6b6257;font-size:14px;margin:0 0 18px;}}
.meta{{color:#6b6257;font-size:12.5px;}}
table{{border-collapse:collapse;font-size:14px;background:#fff;}}
th,td{{border:1px solid #e4dccb;padding:5px 9px;text-align:left;}}
</style></head><body><div class="wrap">
<h1>Lunch board — DEMO copy</h1>
<p class="sub">Built from approved Reader drafts, plus any single stop a
reviewer individually approved out of the flag pile. Sample data only
(invented trucks). Flagged reads as a whole never appear here — they wait
in the queue's flag pile for a human, and nothing is approved
automatically. Nothing here touches the live site.</p>
{''.join(sections) if sections else '<p>No approved drafts yet.</p>'}
</div></body></html>
"""
    BOARD_HTML.write_text(doc)
    return BOARD_HTML


# --------------------------------------------------------------------------
def run_case(n, simulate_cases=None):
    inp = load_json(INPUTS / f"case{n}.json", None)
    if inp is None:
        print(f"case {n}: no input manifest at inputs/case{n}.json")
        return 2
    extra_problems = None
    if simulate_cases is not None:
        case = simulate_cases.get(n)
        if case is None:
            print(f"case {n}: not present in the simulate file")
            return 2
        source = "simulate (no model call)"
    else:
        prompt = load_recipe(inp["posted"])
        image_path = (HERE / inp["demo_image"]).resolve()
        try:
            case = call_model_api(image_path, prompt)
            source = "model"
        except AwaitingAccessError:
            case = {
                "case": n,
                "file": inp["kit_file"],
                "truck": None,
                "post_date": inp["posted"],
                "stops": [],
                "flags": [],
            }
            extra_problems = ["awaiting free credits - extraction not run"]
            source = "stub"
    case.setdefault("case", n)
    case.setdefault("file", inp["kit_file"])
    case.setdefault("post_date", inp["posted"])
    write_extraction(case)
    route, filed = file_result(inp, case, extra_problems)
    if source == "stub":
        print(f"case {n}: STUB MODE - {filed['flags'][0]}")
    print(f"case {n}: extraction written to out/extraction-case{n}.json; "
          f"filed in demo store as {route.upper()} ({filed['id']}) via {source}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Lunch Board Reader Day-1 harness (demo)")
    ap.add_argument("--case", type=int, choices=range(1, 9),
                    help="case number (inputs are staged for all 8 cases)")
    ap.add_argument("--all", action="store_true",
                    help="run every staged input case")
    ap.add_argument("--simulate", metavar="FILE",
                    help="extraction JSON (brief s5 schema) to run through "
                         "guardrails instead of calling the model")
    ap.add_argument("--approve", action="append", metavar="EVENT_ID",
                    help="demo approval: mark the draft for this event "
                         "approved (repeatable)")
    ap.add_argument("--approve-stop", action="append", nargs=2,
                    metavar=("EVENT_ID", "STOP_INDEX"),
                    help="per-stop reviewer approval from the flag pile: "
                         "put one returned stop of a flagged post on the "
                         "board (repeatable). stop=null flags are not "
                         "stops and refuse. Pairs with --resolve-date / "
                         "--resolve-place when the stop's date/place is null")
    ap.add_argument("--resolve-date", metavar="YYYY-MM-DD",
                    help="human-supplied date for a stop whose date is "
                         "null; recorded as provenance.human_supplied.date")
    ap.add_argument("--resolve-place", metavar="PLACE",
                    help="human-supplied place for a stop whose place is "
                         "null; recorded as provenance.human_supplied.place")
    ap.add_argument("--render-only", action="store_true")
    a = ap.parse_args()
    if a.render_only:
        print(f"demo queue rendered: {render_queue()}")
        print(f"demo board rendered: {render_board()}")
        return 0
    sim = None
    if a.simulate:
        data = load_json(a.simulate, None)
        if data is None:
            print(f"BAD INPUT: cannot read {a.simulate}")
            return 2
        sim = {c["case"]: c for c in data.get("cases", [])}
    staged = sorted(int(p.stem[4:]) for p in INPUTS.glob("case*.json")
                    if p.stem[4:].isdigit())
    cases = staged if a.all else ([a.case] if a.case else [])
    if not cases and not a.approve and not a.approve_stop:
        ap.print_help()
        return 2
    rc = 0
    for n in cases:
        rc = run_case(n, sim) or rc
    touched = bool(cases)
    for eid in a.approve or []:
        d = approve_draft(eid)
        if d is None:
            print(f"approve: no draft found for event {eid}")
            rc = rc or 2
        else:
            touched = True
            print(f"approved draft {d['id']} for event {eid}")
    for pair in a.approve_stop or []:
        entry, refusal = approve_stop(pair[0], pair[1],
                                      a.resolve_date, a.resolve_place)
        if entry is None:
            print(f"approve-stop REFUSED: {refusal}")
            rc = rc or 2
        else:
            touched = True
            prov = entry["provenance"]
            print(f"approved stop {prov['stop_index'] + 1} of event {pair[0]} "
                  f"-> board entry {entry['id']} "
                  f"({entry['stop'].get('date')} "
                  f"{entry['stop'].get('place')})")
    if touched:
        render_queue()
        render_board()
        print(f"demo queue rendered: {QUEUE_HTML}")
        print(f"demo board rendered: {BOARD_HTML}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
