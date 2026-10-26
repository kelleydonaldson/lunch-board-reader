#!/usr/bin/env python3
"""Score a Lunch Board Reader extraction against the sample-kit answer key.

Schema (revised build brief s5): one object per post —
  {"truck": ..., "post_date": "YYYY-MM-DD",
   "stops": [{"date": ..., "start": ..., "end": ..., "place": ..., "address": ...}],
   "flags": [{"code": ..., "stop": <0-based index or null>,
              "field": <field name or null>, "note": ...}]}
Extraction files wrap the per-post objects:
  {"cases": [{"case": 1, "file": ..., "truck": ..., "post_date": ...,
              "stops": [...], "flags": [...]}]}

Comparison is field-by-field: truck, post_date, stop count, and every
stop's date/start/end/place/address. Flags are matched as multisets on
(code, stop, field) — the note's wording is ignored. A missing flag
fails, and an extra flag the key does not expect also fails.

Usage:
  python3 score.py <extraction.json>              # all 8 cases
  python3 score.py <extraction.json> --case 1    # one case (repeatable)
  python3 score.py <extraction.json> --cases 1,2 # Day-1 subset
Exit 0 = PASS (every compared field matches), 1 = FAIL, 2 = bad input.
"""
import argparse, json, sys
from collections import Counter
from pathlib import Path

KEY = Path(__file__).resolve().parent.parent / "sample-cases-2026-10-23" / "answer-key.json"
FIELDS = ["date", "start", "end", "place", "address"]

def norm(v):
    return None if v is None else " ".join(str(v).split()).strip()

def flag_key(f):
    if not isinstance(f, dict):
        return ("<not-an-object>", repr(f), None)
    stop = f.get("stop")
    if isinstance(stop, bool) or (stop is not None and not isinstance(stop, int)):
        stop = ("<bad-stop>", repr(stop))
    return (norm(f.get("code")), stop, norm(f.get("field")))

def main():
    ap = argparse.ArgumentParser(description="Score a Reader extraction against the answer key")
    ap.add_argument("extraction")
    ap.add_argument("--case", type=int, action="append", dest="case_list",
                    help="score only this case (repeatable)")
    ap.add_argument("--cases", type=str, dest="cases_csv",
                    help="score only these cases, comma-separated (e.g. 1,2)")
    a = ap.parse_args()
    only = None
    if a.cases_csv:
        try:
            only = {int(x) for x in a.cases_csv.split(",") if x.strip()}
        except ValueError:
            print("BAD INPUT: --cases must be comma-separated integers"); return 2
    if a.case_list:
        only = (only or set()) | set(a.case_list)
    try:
        got = json.loads(Path(a.extraction).read_text())
        key = json.loads(KEY.read_text())
    except Exception as e:
        print(f"BAD INPUT: {e}"); return 2
    want = {c["case"]: c for c in key["cases"] if only is None or c["case"] in only}
    have = {c.get("case"): c for c in got.get("cases", [])
            if only is None or c.get("case") in only}
    diffs, checked = [], 0
    for n in sorted(want):
        w = want[n]
        h = have.get(n)
        if h is None:
            diffs.append(f"case {n}: MISSING from extraction"); continue
        for f in ("truck", "post_date"):
            checked += 1
            if norm(h.get(f)) != norm(w.get(f)):
                diffs.append(f"case {n} {f}: got {h.get(f)!r}, want {w.get(f)!r}")
        wf = Counter(flag_key(f) for f in w.get("flags", []))
        hf = Counter(flag_key(f) for f in h.get("flags", []))
        checked += sum(wf.values()) + sum(hf.values())
        for fk in sorted(set(wf) | set(hf), key=repr):
            if wf[fk] != hf[fk]:
                diffs.append(f"case {n} flag {fk}: got x{hf[fk]}, want x{wf[fk]} "
                             f"(flags match on code+stop+field; note ignored)")
        ws, hs = w.get("stops", []), h.get("stops", [])
        checked += 1
        if len(hs) != len(ws):
            diffs.append(f"case {n} stop count: got {len(hs)}, want {len(ws)}")
        for i, (b, a2) in enumerate(zip(ws, hs)):
            for f in FIELDS:
                checked += 1
                if norm(a2.get(f)) != norm(b.get(f)):
                    diffs.append(f"case {n} stop {i+1} {f}: got {a2.get(f)!r}, want {b.get(f)!r}")
    label = "all cases" if only is None else "case(s) " + ",".join(str(n) for n in sorted(want))
    if diffs:
        print(f"FAIL — {len(diffs)} difference(s) across {checked} compared fields ({label}):")
        for d in diffs: print(" -", d)
        return 1
    print(f"PASS — {label} match the answer key on all {checked} compared fields.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
