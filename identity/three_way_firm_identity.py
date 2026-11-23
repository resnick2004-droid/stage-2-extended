"""Q-185 (the red team's F7 and C1-1, the lead's rulings): the firm path's identity against Stage 2's registered rows,
refusing. No source of this repository is edited for it: the paths' runner is rebound in this process only.

    python identity/three_way_firm_identity.py --synthetic       # light, the fast tier: synthetic blocks, no bars
    python identity/three_way_firm_identity.py --paths 4         # heavy (reads A1 and A3): the lead's, under run.lock

**The rebinding.** `extended.campaign.simulate_lockstep_campaign` runs its paths through the module's `_run_paths`
whenever no recorder or levers are given (`extended.campaign.path_runner`, looked up at call time). Inside `rebound`,
and in this process only, that name is bound to a wrapper of the firm path's runner (`three_way_firm.registered_runner`:
every path made by the firm path's own engine call, `path_call`, the caller's draws passed through, `PassThrough`), and
restored after, whatever happens. The wrapper counts its calls; the identity **refuses unless it was called once per
(shift, level) campaign the gate ran** -- a rebinding that silently does not apply fails it.

**What is compared.**
- `--paths N` (heavy): **P-14's registered gate call** made exactly as `identity/gate_identity.py`'s `p14_problems`
  makes it, through `extended.gate.run_gate` (master's, unedited), every path by the firm path's runner, against the
  first N paths of `results/a3_brk30_cb20_gate_paths.csv`'s `gate` run, both shifts, every
  `zero_edge_decomposition.PATH_COLS` column to 1e-6 (`zd.path_problems`); beside it, each path's final cash as
  `three_way_firm.records_of` reads it. **And the firm path's own inputs against the registered call**: the
  `path_kwargs` P-14's campaign hands its runner against `three_way_firm.engine_kwargs(topstep(), ...)` on every key
  the firm path sets from the firm -- the engine `Rules` field for field, the subscription, the billing days, the
  activation, the payout lag and the funded cap (`terms_problems`).
- `--synthetic` (light): on `identity/gate_identity.py`'s synthetic blocks and gate arguments, the gate with the firm
  path's runner rebound against the vendored gate: every row and every path's record equal; some path paid (not
  vacuous); the runner called once per campaign; the firm's ledger terms against the synthetic campaign's
  `path_kwargs` (its rules are `rules_from_ledger()` without a payout method, so the payout fee is set apart and
  reported); and **the engine's defaults the firm path relies on**: every key the campaign passes its paths that
  `engine_kwargs` omits has the same default in `simulate_lockstep_path` as in `simulate_lockstep_campaign`.

What the registered rows cannot reach is the firm path's race draw, `LaneDraw`, and its router: those are held by
`tests/three_way_firm_checks.py`'s identities against the vendored path (the binary arm and the race at no cost, bit for
bit).

**The read.** With `--paths`, the engine's read is authorised through `extended.reader.authorise_engine_read` under
`identity/gate_identity.py`'s declaration row (P-14's A1 and A3 files), before anything is read; a refusal ends the run
(`EXIT 3`). `--synthetic` reads no bar or walk. Nothing is written. Exit 0 when every part run holds.
"""
from __future__ import annotations

import argparse
import contextlib
import dataclasses
import inspect
import sys
import time
from pathlib import Path
from typing import Any, Iterator

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

#: the keys the firm path sets from the firm's terms (`three_way_firm.engine_kwargs`), compared with a campaign's
FIRM_KEYS = ("subscription", "billing_days", "activation", "payout_lag_days", "max_concurrent_accounts")


class Calls:
    """The rebound runner's record: each campaign's path keywords and its paths."""

    def __init__(self) -> None:
        self.kwargs: list[dict[str, Any]] = []
        self.paths: list[list] = []

    def __call__(self, protocol, path_kwargs, seeds, *a, **k):
        self.kwargs.append(dict(path_kwargs))
        out = TF.registered_runner(protocol, path_kwargs, seeds, *a, **k)
        self.paths.append(out)
        return out


@contextlib.contextmanager
def rebound(calls: Calls) -> Iterator[Calls]:
    """`extended.campaign._run_paths` bound to `calls` in this process, restored after whatever happens."""
    orig = XC._run_paths
    XC._run_paths = calls
    try:
        yield calls
    finally:
        XC._run_paths = orig
    if XC._run_paths is not orig:
        raise RuntimeError("the paths' runner was not restored")


def terms_problems(path_kwargs: dict[str, Any], firm: TF.Firm, what: str, *, rules_apart: tuple = ()) -> list[str]:
    """The firm's terms (`engine_kwargs`'s firm keys and its `Rules`) against a campaign's path keywords."""
    plan = TF.AccountPlan()
    mine = TF.engine_kwargs(firm, plan, 1)
    out = [f"{what}: {k} {mine[k]!r} against the campaign's {path_kwargs.get(k)!r}"
           for k in FIRM_KEYS if mine[k] != path_kwargs.get(k)]
    theirs = path_kwargs.get("rules")
    if theirs is None or not dataclasses.is_dataclass(theirs):
        return out + [f"{what}: the campaign passes no engine Rules"]
    for f in dataclasses.fields(mine["rules"]):
        if f.name in rules_apart:
            continue
        a, b = getattr(mine["rules"], f.name), getattr(theirs, f.name)
        if a != b:
            out.append(f"{what}: Rules.{f.name} {a!r} against the campaign's {b!r}")
    return out


def default_problems(path_kwargs: dict[str, Any]) -> list[str]:
    """Every key a campaign passes its paths that `engine_kwargs` omits: its default in `simulate_lockstep_path` equals
    its default in `simulate_lockstep_campaign` (the firm path takes the path's default where a campaign would pass
    the campaign's)."""
    from propedge.campaign import lockstep as LS

    p = inspect.signature(LS.simulate_lockstep_path).parameters
    c = inspect.signature(LS.simulate_lockstep_campaign).parameters
    omitted = sorted(set(path_kwargs) - set(TF.engine_kwargs(TF.topstep(), TF.AccountPlan(), 1)))
    out = []
    for k in omitted:
        if k in p and k in c and p[k].default is not inspect.Parameter.empty \
                and c[k].default is not inspect.Parameter.empty and repr(p[k].default) != repr(c[k].default):
            out.append(f"{k}: the path's default {p[k].default!r} against the campaign's {c[k].default!r}")
    return out


def synthetic_problems() -> dict[str, list[str]]:
    from propedge.campaign import gate as vg

    out: dict[str, list[str]] = {}
    blocks, kw = GI.syn_blocks(), GI.syn_kwargs()
    hv, sv = GI._hook()
    rows_v, ok_v = vg.run_gate(blocks, path_hook=hv, **kw)
    hf, sf = GI._hook()
    with rebound(Calls()) as calls:
        rows_f, ok_f = XG.run_gate(blocks, path_hook=hf, **kw)
    p = GI.rows_problems(rows_v, rows_f, "firm path's runner") + GI.sink_problems(sv, sf, "firm path's runner")
    if ok_v != ok_f:
        p.append(f"the gate flag {ok_f} against {ok_v}")
    if not sum(float(r["payouts"]) for r in sv) > 0:
        p.append("the synthetic campaign pays nothing: the comparison would be vacuous on payouts")
    out["firm path's runner: rows and paths equal the vendored gate's"] = p
    out["the rebound runner ran every campaign"] = (
        [] if len(calls.kwargs) == len(rows_v) and len(calls.kwargs) > 0 and sum(map(len, calls.paths)) > 0 else
        [f"the runner was called {len(calls.kwargs)} times for {len(rows_v)} campaigns"])
    firm = TF.topstep()
    out["the firm's ledger terms against the synthetic campaign's"] = sorted(
        {q for k in calls.kwargs for q in terms_problems(k, firm, "synthetic", rules_apart=("payout_fee",))})
    out["the engine's defaults the firm path relies on"] = sorted({q for k in calls.kwargs for q in default_problems(k)})
    fees = sorted({float(k["rules"].payout_fee) for k in calls.kwargs})
    print(f"beside: the synthetic campaign's payout fee {fees} (rules_from_ledger, no method); the firm's "
          f"{firm.rules.payout_fee!r} ({firm.payout_method})", flush=True)
    return out


def p14_problems(n: int) -> list[str]:
    """P-14's gate call as `gate_identity.p14_problems` makes it, every path by the firm path's runner, rebound."""
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
    with rebound(Calls()) as calls:
        XG.run_gate(kw.pop("blocks"), workers=1, **kw)
    out = zd.path_problems(sink, ref, [(label, s, "gate", s) for s in ("point", "lower_bound")], int(n))
    if len(calls.kwargs) != 2:                             # (point, lower bound) x the one level 0 %
        out.append(f"the rebound runner was called {len(calls.kwargs)} times, not once per campaign (2)")
    firm = TF.topstep()
    for k in calls.kwargs:
        out += terms_problems(k, firm, "P-14")
        out += default_problems(k)
    for shift, paths in zip(("point", "lower_bound"), calls.paths):
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
              f" (Q-185, the firm path's runner rebound in extended.campaign; {time.time() - t0:.0f} s)", flush=True)
    if a.paths is not None:
        probs = p14_problems(int(a.paths))
        if probs:
            bad = True
            print(f"identity FAILS: P-14 through the firm path's runner -- {len(probs)} problem(s): "
                  + "; ".join(probs[:6]), flush=True)
        else:
            print(f"identity HOLDS: P-14 through the firm path's runner -- the first {a.paths} paths of "
                  "results/a3_brk30_cb20_gate_paths.csv's gate run, both shifts, every PATH_COLS column to 1e-6, "
                  "records_of's final cash, and the firm's terms against the registered call's", flush=True)
    pm = SI.peak_memory()
    if pm:
        print(pm)
    print(f"EXIT {3 if bad else 0}", flush=True)
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
