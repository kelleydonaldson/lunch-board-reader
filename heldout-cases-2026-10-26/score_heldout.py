#!/usr/bin/env python3
"""Score ONE held-out extraction against heldout-key.json (+ invention check).

Semantics mirror the main scorer (files/day1-slice/score.py): truck,
post_date, stop count, every stop field compared exactly after
whitespace-collapsing; flags matched as multisets on (code, stop,
field) - the note's wording is ignored. Case H6 uses the owner's
2026-10-26 widened key (see heldout-key.md).

On top of scoring, an INVENTED-VALUE check runs against what the
graphic actually prints (the printed-value sets below are transcribed
from the verified graphics): any returned non-null value that appears
nowhere on its graphic is an invention. Two owner-ruled hard stops
are detected explicitly:
  - H4: the canceled stop returned as a stop (ruling, 2026-10-26).
  - H6: the end time returned COMPLETED - anything other than the
    printed token '2' or null (ruling, 2026-10-26).

Usage: python3 score_heldout.py <extraction.json> <H1..H6>
Prints one JSON verdict line. Exit 0 = scored (pass or fail),
3 = HARD STOP condition present, 2 = bad input.
"""
import json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEY = HERE / "heldout-key.json"
FIELDS = ["date", "start", "end", "place", "address"]

# Everything printed on each graphic (verified by reading the PNGs).
PRINTED = {
    "H1": {"truck": ["Sample Grill Wagon"],
           "date": ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06"],
           "start": ["11 AM", "4 PM"], "end": ["2 PM", "8 PM", "3 PM"],
           "place": ["Lakeside Sample Park", "Sampleton Post Office", "Sample Bowling Alley",
                     "Westside Sample Market", "Sampleton Fire Station"],
           "address": ["88 Shore Dr", "12 Postal Way", "300 Strike Ln",
                       "415 Sunset Blvd", "7 Engine Ct"]},
    "H2": {"truck": ["Sample Dumpling Cart"],
           "date": ["2026-11-04"], "start": ["11 AM", "5 PM"], "end": ["1 PM", "9 PM"],
           "place": ["Sampleton Bookstore", "Sample Vineyard"],
           "address": ["64 Novel St", "900 Grapevine Rd"]},
    "H3": {"truck": ["Sample Slice Truck"],
           "date": ["2026-11-05"], "start": ["11 AM", "4 PM"], "end": ["2 PM", "7 PM"],
           "place": ["Northgate Sample Mall", "Sampleton Skate Park"],
           "address": ["1200 Retail Row", "33 Wheel Way"]},
    "H4": {"truck": ["Sample Curry Cart"],
           "date": ["2026-11-06"], "start": ["11 AM", "2 PM", "5 PM"],
           "end": ["1 PM", "4 PM", "8 PM"],
           "place": ["Sampleton City Hall", "Sample Farmers Market", "Sample Community Theater"],
           "address": ["1 Civic Plaza", "250 Harvest Ave", "77 Stage Door Ln"]},
    "H5": {"truck": ["Sample Smoke Co. × Sample Taco Cart", "Sample Smoke Co.", "Sample Taco Cart"],
           "date": ["2026-11-07"], "start": ["11 AM", "4 PM"], "end": ["2 PM", "7 PM"],
           "place": ["Riverside Sample Lot", "Sample Fairgrounds"],
           "address": ["100 River Bend Rd", "900 Fairgrounds Rd"]},
    "H6": {"truck": ["Sample Waffle Wagon"],
           "date": ["2026-11-03"], "start": ["11 AM"], "end": ["2"],
           "place": ["Sampleton Depot"], "address": ["19 Rail Spur"]},
}

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
    if len(sys.argv) != 3:
        print("usage: score_heldout.py <extraction.json> <Hn>"); return 2
    ext_path, case_id = Path(sys.argv[1]), sys.argv[2].upper()
    key = json.loads(KEY.read_text())
    want = next((c for c in key["cases"] if c["case"] == case_id), None)
    if want is None:
        print(f"BAD INPUT: no key case {case_id}"); return 2
    got = json.loads(ext_path.read_text())
    diffs, checked = [], 0
    hard_stop = None

    # --- invented-value check against the printed graphic ---------------
    printed = PRINTED[case_id]
    inventions = []
    gt = norm(got.get("truck"))
    if gt is not None and gt not in [norm(t) for t in printed["truck"]]:
        inventions.append(f"truck {got.get('truck')!r} is not printed on the graphic")
    for i, s in enumerate(got.get("stops") or []):
        if not isinstance(s, dict):
            continue
        for f in FIELDS:
            v = norm(s.get(f))
            if v is not None and v not in [norm(x) for x in printed[f]]:
                inventions.append(
                    f"stop {i} {f} {s.get(f)!r} is not printed on the graphic")
    # H4 owner-ruled hard stop: canceled stop returned as a stop.
    if case_id == "H4":
        for s in got.get("stops") or []:
            if isinstance(s, dict) and norm(s.get("place")) == "Sample Farmers Market":
                hard_stop = ("H4: the CANCELED stop (Sample Farmers Market) was "
                             "returned as a stop - owner-ruled HARD STOP")
    # H6 owner-ruled hard stop: end completed instead of '2' / null.
    if case_id == "H6" and got.get("stops"):
        e = norm((got["stops"][0] or {}).get("end"))
        if e is not None and e != "2":
            hard_stop = (f"H6: end returned COMPLETED as {e!r} - the graphic prints "
                         "'11 AM - 2'; completing it is an invented value (HARD STOP)")
    if inventions and hard_stop is None:
        hard_stop = "invented value(s): " + "; ".join(inventions)

    # --- field-by-field scoring ------------------------------------------
    for f in ("truck", "post_date"):
        checked += 1
        if norm(got.get(f)) != norm(want.get(f)):
            diffs.append(f"{f}: got {got.get(f)!r}, want {want.get(f)!r}")
    ws, hs = want.get("stops", []), got.get("stops", [])
    checked += 1
    if len(hs) != len(ws):
        diffs.append(f"stop count: got {len(hs)}, want {len(ws)}")
    if case_id == "H6":
        # widened key (owner, 2026-10-26): compare all fields except end,
        # then accept end per end_acceptance.
        pairs = list(zip(ws, hs))
        for i, (b, a) in enumerate(pairs):
            for f in ("date", "start", "place", "address"):
                checked += 1
                if norm(a.get(f)) != norm(b.get(f)):
                    diffs.append(f"stop {i} {f}: got {a.get(f)!r}, want {b.get(f)!r}")
        if hs:
            e = norm(hs[0].get("end"))
            hf = Counter(flag_key(fl) for fl in got.get("flags", []))
            unread = Counter({("UNREADABLE", 0, "end"): 1})
            if e == "2":
                if hf not in (Counter(), unread):
                    diffs.append(f"H6 read (a): end '2' ok, but flags {dict(hf)} "
                                 "are not [] or a single UNREADABLE(0,end)")
                checked += 1
            elif e is None:
                if hf != unread:
                    diffs.append(f"H6 read (b): end null requires exactly one "
                                 f"UNREADABLE(0,end) flag; got {dict(hf)}")
                checked += 1
            else:
                checked += 1
                diffs.append(f"stop 0 end: got {hs[0].get('end')!r} - completed "
                             "time (see hard_stop)")
    else:
        for i, (b, a) in enumerate(zip(ws, hs)):
            for f in FIELDS:
                checked += 1
                if norm(a.get(f)) != norm(b.get(f)):
                    diffs.append(f"stop {i} {f}: got {a.get(f)!r}, want {b.get(f)!r}")
        wf = Counter(flag_key(f) for f in want.get("flags", []))
        hf = Counter(flag_key(f) for f in got.get("flags", []))
        checked += sum(wf.values()) + sum(hf.values())
        for fk in sorted(set(wf) | set(hf), key=repr):
            if wf[fk] != hf[fk]:
                diffs.append(f"flag {fk}: got x{hf[fk]}, want x{wf[fk]} "
                             "(flags match on code+stop+field; note ignored)")

    verdict = {
        "case": case_id,
        "verdict": "PASS" if not diffs else "FAIL",
        "fields_compared": checked,
        "diffs": diffs,
        "invented_values": inventions,
        "hard_stop": hard_stop,
    }
    print(json.dumps(verdict, ensure_ascii=False, indent=1))
    return 3 if hard_stop else 0

if __name__ == "__main__":
    sys.exit(main())
