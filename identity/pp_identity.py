"""RD-02's identities, refusing (`prereg/RD-02_payout_policy.md` 8.1 items 1 to 3, with item 4 on the paths and starts,
and item 6 at `ref`; Q-105, Q-105e): the reference policy (`elig`, `max`) run through this reading's whole adapter -- its
funded-account class, the held-state rule, the payout fields -- **and through the reading's own inputs**
(`extended/pp_inputs.RealInputs`, the third read's D2) reproduces P-14's and P-16's registered gate paths with their
zero-edge twins, U1's start rows, and Q-44's per-start rows beside.

    python identity/pp_identity.py --paths 4 --u1-starts 4 --row E-NNN        # T-8, slow: the lead's, under the lock
    python identity/pp_identity.py --paths 500 --u1-starts all --row E-NNN    # heavy: the lead's, under the lock

**The reference policy only (8.1; Q-102's m1; T-11).** The reader's `identity` purpose is allowed in any tree, as often
as it runs, and is ledgered only inside a clean run, so this script can never read a policy cell: its cell, class and
payout fields are the constants below, equal to `ref`'s; no argument selects a policy, a lever or a payout field; and
`guard` -- called first in each comparison, before any input is built, any start runs or any path -- refuses unless both
levers are off and the class is the reference's under the declared rule. The inputs are the reading's `RealInputs` at the
constant cell `ref` (`payout_policy.cell_protocol(base, "ref")` is the base itself), so no policy cell can be built here.

**What it compares** (each refusing; E-010's tolerances), every input through `RealInputs` -- so the identity certifies
the code the reading runs (D2; the duplicate gate builder this script carried is gone):

1. **P-14's registered gate paths** -- `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`, the `gate` run at 0 %,
   point and bound, and its `zero_edge_twin` run, point and bound -- through `extended/gate.py` with the class given,
   the calls built by `RealInputs.gate_call("p14", "ref", twin)`, every `zero_edge_decomposition.PATH_COLS` column to
   1e-6, at P-14's seed;
2. **U1's start rows for P-14** -- `vendor/stage2/results/user_journey.csv` section `start`, config `p14`, both arms --
   through `extended.user_beside.run_starts` with the class given and the response `off`, the jobs and the comparison
   `RealInputs.jobs` and `identity_problems` (`identity/user_beside_identity.py`'s build and comparison);
3. **the same for P-16** (its trades' hash first; `rc_s150_all_gate_paths.csv`; U1's `p16` rows);
4. **on the paths and the starts, the levers off**: through the counters' channel (`GateCounters`, `ReplayCounters`),
   every lever count zero -- no held read, no first request held, no request cut, no close where the policy's
   eligibility differs from the firm's;
6. **the readings beside at `ref`** (8.1 item 6, with `--u1-starts`): `ref` under `denial_10`, `denial_25`,
   `denial_50` and `rtp` on the verdict arm, at the identity's starts, against Q-44's `results/user_beside_starts.csv`
   through `RealInputs.ladder_problems` (the file read as text; E-010's comparator; money to the cent). Q-44's file must
   be on the tree and verify, or the script refuses before any read.

**The read.** Stage 2's engine reads the bars and the atlas itself, so `main` authorises them first
(`extended.reader.authorise_engine_read`, purpose `identity`, declaration `--row`, the decision row that registers this
identity -- the lead's; the reader refuses a row that does not exist or does not mention an identity). Nothing is read
without it.

**Its waits** (8.1): Q-80 (the re-composed gate's 500-path identities) for item 1 and 3's gates; Q-93 (U1's start rows
with a class) and Q-101 (with the recorder) for the replays; Q-44's per-start file for item 6.
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

from extended import payout_policy as PP  # noqa: E402

#: the reference policy -- constants, never an argument (8.1, T-11)
CELL = "ref"
L1, L2 = PP.CELL_LEVERS[CELL]
HELD_MODE = "declared"
FUNDED_CLASS = PP.REF_CLASS
VENDOR = ROOT / "vendor" / "stage2"
DESIGNS = ("p14", "p16")


def guard(funded_class: Any = None, protocol: Any = None) -> None:
    """Refuse (`RuntimeError`) unless this script runs the reference policy: the cell `ref`, L1 `elig`, L2 `max`, the
    declared held-state rule, the reference class -- and, given a protocol, the levers off on it (`payout_frac` 1.0,
    no balance kept)."""
    cls = FUNDED_CLASS if funded_class is None else funded_class
    bad = []
    if CELL != "ref" or (L1, L2) != ("elig", "max") or HELD_MODE != "declared":
        bad.append(f"the cell is {CELL!r} ({L1}, {L2}), the rule {HELD_MODE!r}")
    if cls is not PP.REF_CLASS or getattr(cls, "LOCK", True) or getattr(cls, "HELD_MODE", None) != "declared":
        bad.append(f"the class is {cls!r}")
    if protocol is not None and not PP.levers_off(cls, protocol):
        bad.append(f"the protocol asks payout_frac {protocol.payout_frac}, keeps {protocol.keep_balance}")
    if bad:
        raise RuntimeError("REFUSED (RD-02 8.1, T-11): identity/pp_identity.py runs the reference policy only -- "
                           + "; ".join(bad))


#: 8.1 item 4: the counts this script checked, by (design, what, arm or shift) -- written on its HOLDS lines
COUNTS: dict[tuple[str, str, str], dict[str, int]] = {}


def _zero(rows: Any, what: str, key: tuple[str, str, str]) -> list[str]:
    """8.1 item 4: the levers' own counts (`payout_policy.LEVER_KEYS`; the two `cons_*` counts are the engine's)
    zero, counted and kept for the log."""
    tot = PP.lever_totals(rows)
    COUNTS[key] = tot
    return [] if not any(tot.values()) else [f"{what}: the levers are not off ({tot})"]


# ------------------------------------------------------------------------------------------------ the inputs


#: the reading's own inputs, one instance a (paths, starts) setting -- built in the comparison, after its guard
_INPUTS: dict[tuple[int | None, int | None], Any] = {}


def _real_inputs(n_paths: int | None = None, starts: int | None = None) -> Any:
    """The reading's `RealInputs` (`extended/pp_inputs.py`; D2), kept a design's comparisons long so U1's jobs are
    built once."""
    from extended import pp_inputs as PI

    key = (None if n_paths is None else int(n_paths), None if starts is None else int(starts))
    if key not in _INPUTS:
        _INPUTS[key] = PI.RealInputs(starts=starts, n_paths=int(n_paths) if n_paths else 500)
    return _INPUTS[key]


# ------------------------------------------------------------------------------------------------ items 1 and 3


TWIN_RUN = "zero_edge_twin"


def gate_problems(design: str, n: int, workers: int) -> list[str]:
    """Item 1 (P-14) or 3 (P-16): the registered gate paths -- the `gate` run and its `zero_edge_twin`, point and bound
    -- through `extended/gate.py` with the reference class, each call built by `RealInputs.gate_call(design, "ref",
    twin)`; and item 4 on the paths through the counters' channel."""
    guard()
    from extended import gate as XG
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    ri = _real_inputs(n_paths=n)
    probs: list[str] = []
    ref = None
    for twin in (False, True):
        g = ri.gate_call(design, CELL, twin)
        kw = dict(g["kw"])
        guard(FUNDED_CLASS, kw["protocol"])
        counters = PP.GateCounters()
        XG.run_gate(kw.pop("blocks"), workers=int(workers), funded_account_cls=FUNDED_CLASS, counters=counters, **kw)
        if ref is None:
            ref = read_result(RESULTS_DIR / ri.registered_paths_file(design))
        theirs = TWIN_RUN if twin else "gate"
        probs += zd.path_problems(g["sink"], ref, [(g["label"], s, theirs, s) for s in ("point", "lower_bound")],
                                  int(n))
        what = "twin" if twin else "gate"
        for shift in ("point", "lower_bound"):
            probs += _zero((r for k in counters.keys() if k[0] == shift for r in counters.paths(*k[:2])[k[2]]),
                           f"{design} {what} {shift}", (design, "gate paths", f"{what} {shift}"))
    return probs


# ------------------------------------------------------------------------------------------------ items 2, 3 and 6


def u1_problems(design: str, starts: int | None, workers: int) -> list[str]:
    """Item 2 (P-14) or 3 (P-16): U1's start rows through `run_starts` with the reference class, both arms, the jobs
    and the comparison `RealInputs.jobs` and `identity_problems`; and item 4 on the starts through the counters'
    channel."""
    guard()
    import user_journey as UJ

    from extended import pp_inputs as PI
    from extended import user_beside as B

    ri = _real_inputs(starts=starts)
    try:
        jobs = ri.jobs(design)
    except PI.Refused as exc:
        return [str(exc)]
    probs: list[str] = []
    for arm in UJ.ARMS:
        job = jobs[arm]
        guard(FUNDED_CLASS, job["args"]["draws"]["protocol"])
        chosen = UJ.start_choice(len(job["blocks"]), starts)
        counters = PP.ReplayCounters()
        outs = B.run_starts(design, arm, B.BY_NAME["off"], job, chosen, int(workers), funded_account_cls=FUNDED_CLASS,
                            counters=counters)
        probs += ri.identity_problems(design, arm, outs)
        probs += _zero((r for v in counters.starts(design, arm, "off").values() for r in v), f"{design} {arm} starts",
                       (design, "U1 start rows", arm))
    return probs


def ladder_problems(design: str, starts: int | None, workers: int) -> list[str]:
    """Item 6 at `ref` (D2): `ref` under the denial ladder and the placement on, verdict arm, at the identity's starts,
    through `run_starts` with the reference class, against Q-44's per-start rows by `RealInputs.ladder_problems`; and
    the levers' own counts zero under each (item 4; the two `cons_*` counts are the engine's)."""
    guard()
    import user_journey as UJ

    from extended import pp_inputs as PI
    from extended import user_beside as B

    ri = _real_inputs(starts=starts)
    try:
        job = ri.jobs(design)["verdict"]
    except PI.Refused as exc:
        return [str(exc)]
    guard(FUNDED_CLASS, job["args"]["draws"]["protocol"])
    chosen = UJ.start_choice(len(job["blocks"]), starts)
    probs: list[str] = []
    for rname in PI.BESIDE:
        counters = PP.ReplayCounters()
        outs = B.run_starts(design, "verdict", B.BY_NAME[rname], job, chosen, int(workers),
                            funded_account_cls=FUNDED_CLASS, counters=counters)
        probs += ri.ladder_problems(design, rname, outs)
        probs += _zero((r for v in counters.starts(design, "verdict", rname).values() for r in v),
                       f"{design} verdict {rname} starts", (design, "ladder rows", rname))
    return probs


def q44_problems() -> list[str]:
    """Item 6's reference before any read: Q-44's per-start file on the tree, verifying, with every column and the
    verdict rows of each design and response beside (`RealInputs.preflight`'s Q-44 part)."""
    from extended import pp_inputs as PI
    from extended import results as XR

    p = ROOT / "results" / "user_beside_starts.csv"
    if not p.is_file():
        return ["Q-44's per-start file results/user_beside_starts.csv is not on the tree (8.1 item 6 at ref waits for it)"]
    ok, msg = XR.verify_result(p)
    if not ok:
        return [f"Q-44's per-start file: {msg}"]
    return [q for q in PI.RealInputs().preflight(DESIGNS) if q.startswith("Q-44")]


# ------------------------------------------------------------------------------------------------ main


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

    if a.u1_starts:                                 # item 6's reference, before any read is authorised
        probs = q44_problems()
        if probs:
            print("REFUSED (RD-02 8.1 item 6 at ref): " + "; ".join(probs))
            print("EXIT 3", flush=True)
            return 3

    try:                                            # the engine's reads authorised first (ledgered in a clean run only)
        reader.authorise_engine_read(reader.CHOICE_START, reader.JUDGED_END, purpose=reader.IDENTITY,
                                     declaration=a.row, files=SI.engine_files(VENDOR, bars="p16" in designs),
                                     what=f"{a.row}'s identity (identity/pp_identity.py): RD-02's reference policy, "
                                          f"{', '.join(designs)}, gate paths {a.paths}, U1 starts {a.u1_starts}")
    except (reader.ReadRefused, FileNotFoundError) as exc:
        print(SI.refusal(exc))
        print("EXIT 3", flush=True)
        return 3
    bad = False
    for d in designs:
        for what, run in (("gate paths", (lambda: gate_problems(d, a.paths, a.workers)) if a.paths else None),
                          ("U1 start rows", (lambda: u1_problems(d, starts, a.workers)) if a.u1_starts else None),
                          ("ladder rows", (lambda: ladder_problems(d, starts, a.workers)) if a.u1_starts else None)):
            if run is None:
                continue
            t0 = time.time()
            probs = run()
            if probs:
                bad = True
                print(f"identity FAILS: RD-02 ref {d} {what} -- {len(probs)} problem(s): " + "; ".join(probs[:6]),
                      flush=True)
            else:
                counts = "; ".join(f"{k[2]}: {v}" for k, v in COUNTS.items() if k[:2] == (d, what))
                print(f"identity HOLDS: RD-02 ref {d} {what} ({time.time() - t0:.0f} s); 8.1 item 4, the levers' counts "
                      f"-- {counts}", flush=True)
        _INPUTS.clear()                             # a design's inputs released before the next
    pm = SI.peak_memory()
    if pm:
        print(pm)
    print(f"EXIT {3 if bad else 0}", flush=True)
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
