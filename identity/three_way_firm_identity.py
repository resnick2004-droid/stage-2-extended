"""Q-185 (the red team's F7, the lead's ruling): the firm path's identity against Stage 2's registered rows, refusing.

    python identity/three_way_firm_identity.py --synthetic       # light, the fast tier: synthetic blocks, no bars
    python identity/three_way_firm_identity.py --paths 4         # heavy (reads A1 and A3): the lead's, under run.lock

**What is compared.** The firm path's own engine call (`extended.three_way_firm.path_call`), its pass-through of a
caller's draws (`PassThrough`) and its path runner (`registered_runner`), put in the gate through Q-185's seam
(`extended.gate.run_gate(path_fn=...)`, `extended.campaign`'s `path_fn`):

- `--paths N` (heavy): **P-14's registered gate call** made exactly as `identity/gate_identity.py`'s `p14_problems`
  makes it (`rc_screen.inputs()`, A3-BRK30's cell trades, the era rule's bounds, the gate blocks,
  `atlas_a3.gate_kwargs` with P-14's seed, strict gap and budget, 0 % only, the placement off), every path made by the
  firm path's runner, against the first N paths of `results/a3_brk30_cb20_gate_paths.csv`'s `gate` run, both shifts,
  every `zero_edge_decomposition.PATH_COLS` column to 1e-6 (`zd.path_problems`, Stage 2's own comparison). Beside it,
  each path's `final_cash` as `three_way_firm.records_of` reads it (its last close plus the bankroll) against the
  registered column, to 1e-6.
- `--synthetic` (light): on `identity/gate_identity.py`'s synthetic blocks and gate arguments (seed and construction
  its own), the gate with the firm path's runner against the vendored gate: every row and every path's record equal;
  some path paid (not vacuous); the seam refused beside a recorder; the seam's source re-composition holds (the
  campaign and the gate with the Q-185 lines removed are the vendored functions).

**The read.** With `--paths`, the engine's read is authorised through `extended.reader.authorise_engine_read` under
`identity/gate_identity.py`'s declaration row (P-14's A1 and A3 files), before anything is read; a refusal ends the run
(`EXIT 3`). `--synthetic` reads no bar or walk. Nothing is written. Exit 0 when every part run holds.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402

import gate_identity as GI  # noqa: E402  (identity/gate_identity.py: its synthetic construction and P-14's call)
import stage2_identity as SI  # noqa: E402

from extended import campaign as XC  # noqa: E402
from extended import gate as XG  # noqa: E402
from extended import reader  # noqa: E402
from extended import three_way_firm as TF  # noqa: E402


def synthetic_problems() -> dict[str, list[str]]:
    from propedge.campaign import gate as vg

    out: dict[str, list[str]] = {}
    blocks, kw = GI.syn_blocks(), GI.syn_kwargs()
    hv, sv = GI._hook()
    rows_v, ok_v = vg.run_gate(blocks, path_hook=hv, **kw)
    hf, sf = GI._hook()
    rows_f, ok_f = XG.run_gate(blocks, path_hook=hf, path_fn=TF.registered_runner, **kw)
    p = GI.rows_problems(rows_v, rows_f, "firm path's runner") + GI.sink_problems(sv, sf, "firm path's runner")
    if ok_v != ok_f:
        p.append(f"the gate flag {ok_f} against {ok_v}")
    if not sum(float(r["payouts"]) for r in sv) > 0:
        p.append("the synthetic campaign pays nothing: the comparison would be vacuous on payouts")
    out["firm path's runner: rows and paths equal the vendored gate's"] = p
    try:
        XC.check_path_fn(TF.registered_runner, object(), None)
        out["path_fn refused beside a recorder"] = ["not refused"]
    except ValueError:
        out["path_fn refused beside a recorder"] = []
    out["campaign re-composed (Q-185 marked)"] = XC.campaign_recomposition_problems()
    out["gate re-composed (Q-185 marked)"] = XG.gate_recomposition_problems()
    return out


def p14_problems(n: int) -> list[str]:
    """P-14's gate call as `gate_identity.p14_problems` makes it, every path by the firm path's runner."""
    import a3_brk30 as B
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc_screen as S
    import score_fv3_grid as gf
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    I = S.inputs()
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    t, days = B.cell_trades(L)
    keys = B.rrs(t)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        return ["the blocks hold a different number of trades"]
    cap = B.capacity(t, fcfg)
    horizon = int(fcfg["gate"]["campaign"]["horizon_days"])
    ref = read_result(RESULTS_DIR / S.P14_PATHS)
    sink: list[dict] = []
    inner = ps.composed_hook({"margin": float(fcfg["portfolio"]["margin"]),
                              "block_days": int(fcfg["portfolio"]["block_days"])}, sink=sink)
    hook = lt.lever_hook(inner)
    label = "p14_identity_firm_path"
    ps._label(inner, label)
    kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, hook, seed=S.SEED, n_paths=int(n), horizon=horizon,
                       capacity=cap, levels=(0.0,), rtp=False, one_at_a_time=S.STRICT_GAP, purchase_budget=S.BUDGET)
    bankroll = float(kw["bankroll"])
    seen: list = []

    def runner(*a, **k):                                   # the firm path's runner, its paths kept for `records_of`
        paths = TF.registered_runner(*a, **k)
        seen.append(paths)
        return paths

    XG.run_gate(kw.pop("blocks"), workers=1, path_fn=runner, **kw)
    out = zd.path_problems(sink, ref, [(label, s, "gate", s) for s in ("point", "lower_bound")], int(n))
    for shift, paths in zip(("point", "lower_bound"), seen):
        b = ref[(ref["run"].astype(str) == "gate") & (ref["shift"].astype(str) == shift)
                & np.isclose(ref["enforcement_p"].astype(float), 0.0)].sort_values("path").head(int(n))
        for i, (p, want) in enumerate(zip(paths, b["final_cash"].astype(float))):
            r = TF.records_of(p, bankroll=bankroll, lag=0, horizon=len(p.path.cash_series) - 1, budget=None)
            if abs(float(r["rel"][-1]) + bankroll - want) > 1e-6:
                out.append(f"records_of {shift} path {i}: final cash {float(r['rel'][-1]) + bankroll!r} against {want!r}")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--synthetic", action="store_true", help="the light identity on synthetic blocks (no bars)")
    ap.add_argument("--paths", type=int, default=None, help="P-14's registered gate paths at N paths (heavy)")
    a = ap.parse_args(argv)
    if not a.synthetic and a.paths is None:
        ap.error("give --synthetic or --paths N")
    bad, t0 = False, time.time()
    if a.paths is not None:
        try:
            reader.authorise_engine_read(reader.CHOICE_START, reader.JUDGED_END, purpose=reader.IDENTITY,
                                         declaration=GI.READ_ROW, files=SI.engine_files(GI.VENDOR, bars=False),
                                         what=f"Q-185's identity (identity/three_way_firm_identity.py): P-14's "
                                              f"registered gate paths ({a.paths}) through the firm path's runner")
        except (reader.ReadRefused, FileNotFoundError) as exc:
            print(SI.refusal(exc))
            print("EXIT 3", flush=True)
            return 3
    if a.synthetic:
        for check, probs in synthetic_problems().items():
            bad |= bool(probs)
            print(f"FAILS: {check} -- " + "; ".join(probs) if probs else f"holds: {check}")
        print(("synthetic identity FAILS" if bad else "synthetic identity HOLDS") +
              f" (Q-185, the firm path's runner through extended.gate; {time.time() - t0:.0f} s)", flush=True)
    if a.paths is not None:
        probs = p14_problems(int(a.paths))
        if probs:
            bad = True
            print(f"identity FAILS: P-14 through the firm path's runner -- {len(probs)} problem(s): "
                  + "; ".join(probs[:6]), flush=True)
        else:
            print(f"identity HOLDS: P-14 through the firm path's runner -- the first {a.paths} paths of "
                  "results/a3_brk30_cb20_gate_paths.csv's gate run, both shifts, every PATH_COLS column to 1e-6, and "
                  "records_of's final cash", flush=True)
    pm = SI.peak_memory()
    if pm:
        print(pm)
    print(f"EXIT {3 if bad else 0}", flush=True)
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
