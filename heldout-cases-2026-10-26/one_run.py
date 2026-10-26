#!/usr/bin/env python3
"""Make ONE live held-out read through the proven reader seam.

Usage: python3 one_run.py H1 1     (case id, run number)

Loads the case's post_date from heldout-key.json, fills the UNMODIFIED
recipe via reader.load_recipe, calls reader.call_model_api (the real
seam: connector helper -> Meta Model API, model muse-spark-1.3),
archives the seam's raw response + extraction into out/run-<r>/, and
appends one HELD-OUT line to the shared spend log. Prints a JSON
summary. This script never scores - scoring is a separate step run
after every call, before the next call is made.
"""
import json, shutil, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
GOAL = HERE.parents[1]
DEMO = GOAL / "files" / "day1-slice" / "demo-intake"
SPEND = GOAL / "hidden_files" / "spend-log.md"
sys.path.insert(0, str(DEMO))
import reader  # noqa: E402  (the Day-1 harness; its seam is the read path)

def main():
    case_id, run_no = sys.argv[1].upper(), int(sys.argv[2])
    key = json.loads((HERE / "heldout-key.json").read_text())
    case = next(c for c in key["cases"] if c["case"] == case_id)
    image = HERE / case["file"]
    prompt = reader.load_recipe(case["post_date"])
    extraction = reader.call_model_api(image, prompt)  # THE live call
    stem = image.stem
    raw_src = DEMO / "out" / f"{stem}-raw-response.json"
    raw = json.loads(raw_src.read_text())
    outdir = HERE / "out" / f"run-{run_no}"
    outdir.mkdir(parents=True, exist_ok=True)
    raw_dst = outdir / f"{case_id.lower()}-run{run_no}-raw-response.json"
    ext_dst = outdir / f"{case_id.lower()}-run{run_no}-extraction.json"
    shutil.copyfile(raw_src, raw_dst)
    shutil.copyfile(DEMO / "out" / f"{stem}-extraction.json", ext_dst)
    u = raw.get("usage") or {}
    det = u.get("completion_tokens_details") or {}
    pdet = u.get("prompt_tokens_details") or {}
    toks = {"prompt": u.get("prompt_tokens"), "completion": u.get("completion_tokens"),
            "reasoning": det.get("reasoning_tokens"), "total": u.get("total_tokens"),
            "cached": pdet.get("cached_tokens")}
    now = datetime.now(ZoneInfo("America/Chicago"))
    line = (f"- **{now:%Y-%m-%d %-I:%M %p} CT — HELD-OUT {case_id} run {run_no} "
            f"vision read** — model `muse-spark-1.3`, image `{case['file']}` "
            f"(held-out kit). Tokens: **prompt {toks['prompt']}, completion "
            f"{toks['completion']} (including {toks['reasoning']} reasoning), "
            f"total {toks['total']}**, cached {toks['cached']}. Cost: **no "
            "dollar figure in the response** — free-credit pool; console "
            "Usage page is the dollar source.\n")
    with open(SPEND, "a") as fh:
        fh.write(line)
    print(json.dumps({"case": case_id, "run": run_no, "tokens": toks,
                      "extraction_file": str(ext_dst),
                      "extraction": extraction}, ensure_ascii=False, indent=1))
    return 0

if __name__ == "__main__":
    sys.exit(main())
