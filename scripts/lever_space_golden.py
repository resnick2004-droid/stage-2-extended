"""Q-151b (the per-firm lever tables): write or check the golden snapshot of Topstep's lever-space loader output.

The snapshot (`tests/data/lever_space_topstep_golden.json`) is every Topstep lever's metadata and its `bounds` outcome --
the loaded `Range`'s repr, or the refusal's class and message -- with every result reading pointed at an absent file
(`PINNED_RESULTS`: S1's and T7's), so the snapshot does not depend on which result files a tree holds. It was first
written from master 1b29e07, before the per-firm loader was added, so `tests/test_lever_space_firms.py` proves the Topstep output unchanged bit for
bit. Rewrite it only under the lead's decision row (a changed Topstep record changes the snapshot by design).

    python scripts/lever_space_golden.py --check     # exit 1 on any difference
    python scripts/lever_space_golden.py --write     # only under a decision row

Reads rules and configuration only; writes nothing under `results/`.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

GOLDEN = ROOT / "tests" / "data" / "lever_space_topstep_golden.json"


#: the result-file state every snapshot (and every test of the lever spaces) is taken under: each reading the loader can
#: load, pointed at an absent file -- so the outcome never depends on which git-ignored result files a tree holds
#: (S1's `results/s1_range.csv`, a licensed derivative; T7's `results/t7_forecast.csv`, where the loader has one)
PINNED_RESULTS = {"S1_PATH": "s1_range.csv", "T7_PATH": "t7_forecast.csv"}
ABSENT = ROOT / "__absent__"


@contextlib.contextmanager
def pinned(LS=None):
    """Point every result path of `extended.lever_space` at `ABSENT` for the block; restore it afterwards (an attribute
    the loader does not have yet, T7_PATH before T7's merge, is set and then removed)."""
    if LS is None:
        from extended import lever_space as LS
    missing = object()
    saved = {name: getattr(LS, name, missing) for name in PINNED_RESULTS}
    try:
        for name, fname in PINNED_RESULTS.items():
            setattr(LS, name, ABSENT / fname)
        yield
    finally:
        for name, v in saved.items():
            if v is missing:
                delattr(LS, name)
            else:
                setattr(LS, name, v)


def snapshot() -> dict:
    from extended import lever_space as LS
    from extended.firm_terms import UnverifiedTerm

    with pinned(LS):
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
