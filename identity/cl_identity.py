"""RD-03's own identity, refusing (`prereg/RD-03_contract_levers.md` 9.1 items 1 and 2; the runner's label `cl_identity`;
its build Q-119): the reference -- every lever option a constant at its off value -- run through this reading's path
(14.1 A-1, by A-2 and A-3) reproduces P-14's and P-16's registered gate paths and U1's start rows.

    python identity/cl_identity.py --paths 4 --u1-starts 4 --row E-NNN        # T-8, slow: the lead's, under the lock
    python identity/cl_identity.py --paths 500 --u1-starts all --row E-NNN    # step 1: heavy, the lead's, under the lock

**The reference only (9.1; T-11).** The reader's `identity` purpose is allowed in any tree, as often as it runs, so this
script can never read a cell: the levers are the constant `LEVERS` (every option off, the counters on so item 4's
zeros are read), no argument names a lever, a cell, a price or an option, and `guard` -- called first in each
comparison, before any input is built, any start runs or any path -- refuses unless every option is off.

**What it compares** (each refusing; E-010's tolerances), every input through RD-02's real inputs at their reference
(`extended/pp_inputs.RealInputs`, the code `identity/pp_identity.py` certifies):

1. **P-14's registered gate paths** -- `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`, the `gate` run at 0 %,
   point and bound -- through `extended/gate.py` with A-3 (the keyword `levers` given, every option off), every
   `zero_edge_decomposition.PATH_COLS` column to 1e-6, at P-14's seed (20261131); **and P-16's** --
   `vendor/stage2/results/rc_s150_all_gate_paths.csv` at its seed (20261206), after its trades' hash (the builder's);
2. **U1's start rows for P-14 and P-16** -- `vendor/stage2/results/user_journey.csv` section `start`, configs `p14` and
   `p16`, both arms, every start, every column as E-010 compared them (`RealInputs.identity_problems`), with U1's own
   checks of every run's payouts and fees against the engine's totals -- through `extended.user_beside.run_starts`
   with A-2 (the keyword `levers` given) and the response `off`; and on the starts, every lever count zero.

**The read.** Stage 2's engine reads the bars and the atlas itself, so `main` authorises them first
(`extended.reader.authorise_engine_read`, purpose `identity`, declaration `--row`, the lead's row registering this
identity). **Its cover** (9.1, Q-111's rule): `BASE`, this script and its import closure (`extended/cl_reading.py`'s
`OWN_WAITS`, held by T-0 and the build's tests).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
for _p in (str(ROOT), str(ROOT / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import reader, use_vendored_stage2  # noqa: E402

use_vendored_stage2()

from extended import levers_path as LP  # noqa: E402

#: the reference -- a constant, never an argument (9.1, T-11): every option off, the counters on (item 4's zeros)
CELL = "ref"
LEVERS = LP.Levers(counters=True)
VENDOR = ROOT / "vendor" / "stage2"
DESIGNS = ("p14", "p16")


def guard(levers: Any = None) -> None:
    """Refuse (`RuntimeError`) unless this script runs the reference: the cell `ref`, every option of the levers off
    (no reactivation, no expiry, no house money, no counted reading, no seat or price keyword)."""
    lv = LEVERS if levers is None else levers
    bad = []
    if CELL != "ref":
        bad.append(f"the cell is {CELL!r}")
    if not isinstance(lv, LP.Levers) or not lv.off:
        bad.append(f"the levers are {lv!r}")
    if bad:
        raise RuntimeError("REFUSED (RD-03 9.1, T-11): identity/cl_identity.py runs the reference only -- "
                           + "; ".join(bad))


COUNTS: dict[tuple[str, str, str], dict[str, float]] = {}
_INPUTS: dict[tuple, Any] = {}


def _inputs(n_paths: int | None = None, starts: int | None = None) -> Any:
    from extended import pp_inputs as PI

    key = (n_paths, starts)
    if key not in _INPUTS:
        _INPUTS[key] = PI.RealInputs(starts=starts, n_paths=int(n_paths) if n_paths else 500)
    return _INPUTS[key]


def gate_problems(design: str, n: int, workers: int) -> list[str]:
    """Item 1: the registered gate paths -- the `gate` run, point and bound -- through `extended/gate.py` with A-3."""
    guard()
    from extended import gate as XG
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    ri = _inputs(n_paths=n)
    g = ri.gate_call(design, "ref", False)
    kw = dict(g["kw"])
    guard(LEVERS)
    counts: dict[str, float] = {}

    def hook(shift: str, p: float, paths: Any, inner: Any = kw.get("path_hook")) -> dict[str, Any]:
        for x in paths:
            for k, v in (getattr(x, "lever_counts", None) or {}).items():
                if k in LP.LEVER_KEYS:
                    counts[k] = counts.get(k, 0.0) + float(v or 0)
        return inner(shift, p, paths) if inner is not None else {}

    kw["path_hook"] = hook
    XG.run_gate(kw.pop("blocks"), workers=int(workers), levers=LEVERS, **kw)
    ref = read_result(RESULTS_DIR / ri.registered_paths_file(design))
    probs = zd.path_problems(g["sink"], ref, [(g["label"], s, "gate", s) for s in ("point", "lower_bound")], int(n))
    COUNTS[(design, "gate paths", "gate")] = counts
    if any(counts.values()):
        probs.append(f"the levers are not off on the gate's paths ({counts})")
    return probs


def u1_problems(design: str, starts: int | None, workers: int) -> list[str]:
    """Item 2: U1's start rows through `run_starts` with A-2 (the levers given, every option off), both arms."""
    guard()
    import user_journey as UJ

    from extended import pp_inputs as PI
    from extended import user_beside as B

    ri = _inputs(starts=starts)
    try:
        jobs = ri.jobs(design)
    except PI.Refused as exc:
        return [str(exc)]
    probs: list[str] = []
    for arm in UJ.ARMS:
        job = jobs[arm]
        guard(LEVERS)
        chosen = UJ.start_choice(len(job["blocks"]), starts)
        sink = LP.LeverSink()
        outs = B.run_starts(design, arm, B.BY_NAME["off"], job, chosen, int(workers), levers=LEVERS, lever_sink=sink)
        probs += ri.identity_problems(design, arm, outs)
        tot = {k: float(sum(float(c.get(k, 0) or 0) for c in sink.starts(design, arm, "off").values()))
               for k in LP.LEVER_KEYS}
        COUNTS[(design, "U1 start rows", arm)] = tot
        if any(tot.values()):
            probs.append(f"{design} {arm}: the levers are not off on the starts ({tot})")
    return probs


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--paths", type=int, default=None, help="the registered gate paths at N paths (slow or heavy)")
    ap.add_argument("--u1-starts", default=None, help="U1's start rows at N starts a configuration and arm, or 'all'")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--only", choices=DESIGNS, default=None)
    ap.add_argument("--row", required=True, help="the decision row that registers this identity (E-NNN; the lead's)")
    return ap


def main(argv: list[str] | None = None) -> int:
    a = parser().parse_args(argv)
    guard()
    if a.paths is None and a.u1_starts is None:
        print("give --paths N and/or --u1-starts N|all")
        return 2
    starts = None if a.u1_starts in (None, "all") else int(a.u1_starts)
    designs = [d for d in DESIGNS if a.only is None or d == a.only]
    import stage2_identity as SI

    try:
        reader.authorise_engine_read(reader.CHOICE_START, reader.JUDGED_END, purpose=reader.IDENTITY,
                                     declaration=a.row, files=SI.engine_files(VENDOR, bars="p16" in designs),
                                     what=f"{a.row}'s identity (identity/cl_identity.py): RD-03's reference, "
                                          f"{', '.join(designs)}, gate paths {a.paths}, U1 starts {a.u1_starts}")
    except (reader.ReadRefused, FileNotFoundError) as exc:
        print(SI.refusal(exc))
        print("EXIT 3", flush=True)
        return 3
    bad = False
    for d in designs:
        for what, run in (("gate paths", (lambda: gate_problems(d, a.paths, a.workers)) if a.paths else None),
                          ("U1 start rows", (lambda: u1_problems(d, starts, a.workers)) if a.u1_starts else None)):
            if run is None:
                continue
            t0 = time.time()
            probs = run()
            if probs:
                bad = True
                print(f"identity FAILS: RD-03 ref {d} {what} -- {len(probs)} problem(s): " + "; ".join(probs[:6]),
                      flush=True)
            else:
                print(f"identity HOLDS: RD-03 ref {d} {what} ({time.time() - t0:.0f} s); the levers' counts zero",
                      flush=True)
        _INPUTS.clear()
    pm = SI.peak_memory()
    if pm:
        print(pm)
    print(f"EXIT {3 if bad else 0}", flush=True)
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
