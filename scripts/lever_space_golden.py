"""Q-151b (the per-firm lever tables): write or check the golden snapshot of Topstep's lever-space loader output.

The snapshot (`tests/data/lever_space_topstep_golden.json`) is every Topstep lever's metadata and its `bounds` outcome --
the loaded `Range`'s repr, or the refusal's class and message -- with S1's search-year reading pointed at an absent file
(so the snapshot does not depend on whether a tree holds `results/s1_range.csv`). It was written from master 1b29e07,
before the per-firm loader was added, so `tests/test_lever_space_firms.py` proves the Topstep output unchanged bit for
bit. Rewrite it only under the lead's decision row (a changed Topstep record changes the snapshot by design).

    python scripts/lever_space_golden.py --check     # exit 1 on any difference
    python scripts/lever_space_golden.py --write     # only under a decision row

Reads rules and configuration only; writes nothing under `results/`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

GOLDEN = ROOT / "tests" / "data" / "lever_space_topstep_golden.json"


def snapshot() -> dict:
    from extended import lever_space as LS
    from extended.firm_terms import UnverifiedTerm

    saved = LS.S1_PATH
    LS.S1_PATH = ROOT / "__absent__" / "s1_range.csv"
    try:
        out = {}
        for i, lv in LS.LEVERS.items():
            meta = [lv.id, lv.layer, lv.name, lv.cls, lv.source, list(lv.keys), list(lv.depends)]
            try:
                got = repr(LS.bounds(i))
            except (LS.LeverRefused, UnverifiedTerm) as e:
                got = f"{type(e).__name__}: {e}"
            out[i] = {"meta": meta, "bounds": got}
        out["__space__"] = sorted(LS.space())
        out["__refusals__"] = LS.refusals()
        out["__counts__"] = LS.counts()
        return out
    finally:
        LS.S1_PATH = saved


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    a = ap.parse_args()
    snap = snapshot()
    if a.write:
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(json.dumps(snap, indent=1, sort_keys=False) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {GOLDEN.relative_to(ROOT)}")
        return 0
    old = json.loads(GOLDEN.read_text(encoding="utf-8"))
    if old != snap:
        diff = [k for k in set(old) | set(snap) if old.get(k) != snap.get(k)]
        print(f"DIFFERS at {sorted(diff)}")
        return 1
    print("unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
