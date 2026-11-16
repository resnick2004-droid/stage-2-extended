"""RD-02's identities, refusing (`prereg/RD-02_payout_policy.md` 8.1 items 1 to 3, with item 4 on the paths; Q-105):
the reference policy (`elig`, `max`) run through this reading's whole adapter -- its funded-account class, the
held-state rule, the payout fields -- reproduces P-14's and P-16's registered gate paths and U1's start rows.

    python identity/pp_identity.py --paths 4 --u1-starts 4 --row E-NNN        # T-8, slow: the lead's, under the lock
    python identity/pp_identity.py --paths 500 --u1-starts all --row E-NNN    # heavy: the lead's, under the lock

**The reference policy only (8.1; Q-102's m1; T-11).** The reader's `identity` purpose is allowed in any tree, as often
as it runs, and is ledgered only inside a clean run, so this script can never read a policy cell: its cell, class and
payout fields are the constants below, equal to `ref`'s; no argument selects a policy, a lever or a payout field; and
`guard` -- called first in each comparison, before any input is built, any start runs or any path -- refuses unless both
levers are off and the class is the reference's under the declared rule.

**What it compares** (each refusing; E-010's tolerances):

1. **P-14's registered gate paths** -- `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`, the `gate` run, 0 %,
   point and bound -- through `extended/gate.py` with the class given, every `zero_edge_decomposition.PATH_COLS` column
   to 1e-6, at P-14's seed (`identity/gate_identity.py`'s P-14 call, the class added);
2. **U1's start rows for P-14** -- `vendor/stage2/results/user_journey.csv` section `start`, config `p14`, both arms --
   through `extended.user_beside.run_starts` with the class given and the response `off`
   (`identity/user_beside_identity.py`'s comparison);
3. **the same for P-16** (its trades' hash first; `rc_s150_all_gate_paths.csv`; U1's `p16` rows);
4. **on the paths and the starts, the levers off**: through the counters' channel (`GateCounters`, `ReplayCounters`),
   every counter zero -- no held read, no first request held, no request cut, no close where the policy's eligibility
   differs from the firm's.

**The read.** Stage 2's engine reads the bars and the atlas itself, so `main` authorises them first
(`extended.reader.authorise_engine_read`, purpose `identity`, declaration `--row`, the decision row that registers this
identity -- the lead's; the reader refuses a row that does not exist or does not mention an identity). Nothing is read
without it.

**Its waits** (8.1): Q-80 (the re-composed gate's 500-path identities) for item 1 and 3's gates; Q-93 (U1's start rows
with a class) and Q-101 (with the recorder) for the replays.
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


def _zero(rows: Any, what: str) -> list[str]:
    tot = PP.total_counters(rows)
    return [] if not any(tot.values()) else [f"{what}: the levers are not off ({tot})"]


# ------------------------------------------------------------------------------------------------ items 1 and 3


def _build_gate_inputs(design: str, n: int) -> dict[str, Any]:
    """The registered gate call's keywords, as `identity/gate_identity.py` builds P-14's and P-16's (the inputs read
    through the vendored builders)."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc_screen as S
    import score_fv3_grid as gf
    import stage2_identity as SI

    if design == "p14":
        I = S.inputs()
        L = I["L"]
        t, days = B.cell_trades(L)
        seed, gap, budget, ref = S.SEED, S.STRICT_GAP, S.BUDGET, S.P14_PATHS
    else:
        import rc150_dev_test as P
        import rc_dev_test as D

        sp = P.SPEC
        I, b = sp.build()
        L = I["L"]
        t, days = b["cells"][sp.cell]["trades"], b["days"]
        if D.trades_hash(t) != sp.trades_sha256:
            raise RuntimeError(f"P-16's trades hash is not the pinned {sp.trades_sha256}")
        seed, gap, budget, ref = SI.P16_SEED, C.STRICT_GAP, C.BUDGET, SI.P16_PATHS
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    keys = B.rrs(t)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise RuntimeError("the blocks hold a different number of trades")
    cap = B.capacity(t, fcfg)
    sink: list[dict] = []
    pc = fcfg["portfolio"]
    inner = ps.composed_hook({"margin": float(pc["margin"]), "block_days": int(pc["block_days"])}, sink=sink)
    hook = lt.lever_hook(inner)
    label = f"{design}_pp_identity"
    ps._label(inner, label)
    kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, hook, seed=seed, n_paths=int(n),
                       horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=cap, levels=(0.0,), rtp=False,
                       one_at_a_time=gap, purchase_budget=budget)
    return {"kw": kw, "sink": sink, "label": label, "ref": ref}


def gate_problems(design: str, n: int, workers: int) -> list[str]:
    """Item 1 (P-14) or 3 (P-16): the registered gate paths through `extended/gate.py` with the reference class, and
    item 4 on the paths through the counters' channel."""
    guard()
    from extended import gate as XG
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    g = _build_gate_inputs(design, n)
    kw = g["kw"]
    guard(FUNDED_CLASS, kw["protocol"])
    counters = PP.GateCounters()
    XG.run_gate(kw.pop("blocks"), workers=int(workers), funded_account_cls=FUNDED_CLASS, counters=counters, **kw)
    probs = zd.path_problems(g["sink"], read_result(RESULTS_DIR / g["ref"]),
                             [(g["label"], s, "gate", s) for s in ("point", "lower_bound")], int(n))
    probs += _zero((r for k in counters.keys() for r in counters.paths(*k[:2])[k[2]]), f"{design} gate")
    return probs


# ------------------------------------------------------------------------------------------------ items 2 and 3


def _build_u1_job(design: str) -> tuple[dict[str, Any], dict[str, Any], list[str], dict[str, Any]]:
    """U1's jobs for a configuration (`identity/user_beside_identity.py`'s `build`) and U1's file (its reference)."""
    import user_beside_identity as UI

    from propedge import RESULTS_DIR

    jobs, c, probs = UI.build(RESULTS_DIR, design)
    return jobs, c, probs, UI.u1_reference(RESULTS_DIR, [design])


def u1_problems(design: str, starts: int | None, workers: int) -> list[str]:
    """Item 2 (P-14) or 3 (P-16): U1's start rows through `run_starts` with the reference class, both arms, and item 4
    on the starts through the counters' channel."""
    guard()
    import user_beside_identity as UI
    import user_journey as UJ

    from extended import user_beside as B

    jobs, c, probs, ref = _build_u1_job(design)
    for arm in UJ.ARMS:
        job = jobs[arm]
        guard(FUNDED_CLASS, job["args"]["draws"]["protocol"])
        n_window = len(job["blocks"])
        chosen = UJ.start_choice(n_window, starts)
        counters = PP.ReplayCounters()
        outs = B.run_starts(design, arm, B.BY_NAME["off"], job, chosen, int(workers), funded_account_cls=FUNDED_CLASS,
                            counters=counters)
        probs += UI.u1_compare_outs(design, c, arm, outs, ref, n_window, starts)
        probs += _zero((r for v in counters.starts(design, arm, "off").values() for r in v), f"{design} {arm} starts")
    return probs


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
                          ("U1 start rows", (lambda: u1_problems(d, starts, a.workers)) if a.u1_starts else None)):
            if run is None:
                continue
            t0 = time.time()
            probs = run()
            if probs:
                bad = True
                print(f"identity FAILS: RD-02 ref {d} {what} -- {len(probs)} problem(s): " + "; ".join(probs[:6]),
                      flush=True)
            else:
                print(f"identity HOLDS: RD-02 ref {d} {what} ({time.time() - t0:.0f} s)", flush=True)
    pm = SI.peak_memory()
    if pm:
        print(pm)
    print(f"EXIT {3 if bad else 0}", flush=True)
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
