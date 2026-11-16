"""Q-47's identities (`extended/gate.py`: the gate re-composed so a design can declare another funded-account class),
refusing.

    python identity/gate_identity.py --synthetic                # light, the fast tier: synthetic blocks, no bars
    python identity/gate_identity.py --paths 4                  # slow (the run lock): P-14 and P-16 at 4 paths
    python identity/gate_identity.py --paths 500 --workers 1    # heavy, the lead's (the run lock): every registered path

**`--paths N`.** The registered gate calls, made exactly as the registered rows were made, through
`extended.gate.run_gate` in place of the vendored `gate.run_gate`. Each runs twice: once with no class (`none`: the
vendored engine call), once with `extended.gate.PassThroughFundedAccount` (`passthrough`: a subclass that overrides
nothing, given through the seam). Each is compared on the first N paths of the registered paths file, both shifts,
every `zero_edge_decomposition.PATH_COLS` column to 1e-6, by Stage 2's own comparison (`zd.path_problems`):

- **P-14** (A3-BRK30-CB20; Stage 2 D-509/D-513). The call is P-14's engine call as `rc_screen.Runner.run` makes it for
  `rc_screen.identity_problems`: `rc_screen.inputs()`, A3-BRK30's cell trades, the era rule's bounds
  (`atlas_a3.bounds`), the gate blocks, `atlas_a3.gate_kwargs` with P-14's seed, strict gap and budget, 0 % only, the
  placement off. The paths are compared against `results/a3_brk30_cb20_gate_paths.csv`'s `gate` run.
- **P-16** (`rc_s150_all_nr`; Stage 2 D-544/D-547). The call is identity/stage2_identity.py's `p16_problems`: the cell
  rebuilt by `rc150_dev_test.SPEC`, its trades' hash against the pinned one, seed 20261206. The paths are compared
  against `results/rc_s150_all_gate_paths.csv`'s `gate` run.

`--cls none|passthrough|both` (default both) chooses the arms; `--only p14|p16` chooses the designs.

**`--synthetic` (light).** On synthetic trade blocks (seed 20261947, F-P's draft section 11: the build's toy
campaigns), through the vendored engine, with the gate's options rotation, flat-account routing, a purchase budget,
the four denial levels and the placement off, eight checks. The strict one-position gap is not used here: the vendored
engine needs each trade's exit at every R for it (D-349, D-351), which synthetic one-R blocks lack. The P-14 and P-16
checks exercise it on the registered trades.

1. **source pinned:** the vendored `run_gate`'s source hashes to `extended.gate.VENDORED_RUN_GATE_SHA256`;
2. **wrong pin refused:** a different pin is refused;
3. **no class:** the adapter's rows equal the vendored gate's exactly, and so does every path's record
   (`portfolio_stage.composed_hook`'s sink, every key);
4. **pass-through class:** the same, the rows apart from the added `funded_account_cls` column, which names the class;
5. **probe reaches the engine:** a probe subclass that is never eligible for a payout leaves every path unpaid, where
   the vendored gate pays some;
6. **probe reaches path workers:** the probe at two workers gives every path's record exactly as at one worker;
7. **non-account class refused;**
8. **unpicklable class refused:** a class defined inside a function, at two workers.

Exit 0 when every part run holds; 3 when one is refused. Nothing is written. Peak memory printed last.
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.campaign.lockstep import FundedAccount  # noqa: E402

import stage2_identity as SI  # noqa: E402  (identity/stage2_identity.py: P-16's seed and paths file, peak memory)

from extended import gate as XG  # noqa: E402

#: the synthetic campaigns' seed: F-P's draft section 11 assigns 20261947 to "the build's toy campaigns", and this
#: adapter is F-P's build (its 13.1 item 3; E-025 (2))
SYN_SEED = 20261947
SYN_DAYS = 160
SYN_PATHS = 6
CLS_ARMS = ("none", "passthrough")


class NeverPaysFundedAccount(FundedAccount):
    """The synthetic probe: never eligible for a Standard-path payout, so no path is ever paid. It shows that a class
    given to the adapter reaches the engine, and reaches path workers (a module-level class pickles by reference)."""

    def _standard_eligible(self, rules: Any) -> bool:
        return False


# ------------------------------------------------------------------------------------------------ synthetic


def syn_blocks() -> list:
    """SYN_DAYS synthetic days of zero to two trades at $500 risk, won at 1.5R with probability 0.55, each with its
    entry and exit minute (so rotation routes only to a flat account)."""
    from propedge.outcomes.distribution import DayBlock

    rng = np.random.default_rng([SYN_SEED, 1])
    out = []
    for _ in range(SYN_DAYS):
        k = int(rng.integers(0, 3))
        win = rng.random(k) < 0.55
        entry = 510.0 + 90.0 * np.arange(k, dtype=float)
        out.append(DayBlock(pnl=np.where(win, 750.0, -500.0).astype(float), risked=np.full(k, 500.0),
                            exit_reasons=tuple("target" if w else "stop" for w in win),
                            entry_t=entry, exit_t=entry + 45.0))
    return out


def syn_kwargs() -> dict[str, Any]:
    from propedge.campaign.protocols import Protocol
    from propedge.contract.adapter import rules_from_ledger

    proto = Protocol(name="q47_synthetic", combine_rr=1.5, combine_risk=500.0, funded_rr=1.5, funded_risk=500.0,
                     trades_per_day=2, max_concurrent_accounts=5)
    return dict(e=0.375, lb=0.10, protocol=proto, bankroll=5000.0, horizon_days=150, n_paths=SYN_PATHS,
                seed=SYN_SEED, accounts=5, sizing=None, rules=rules_from_ledger(), combines=1, total_accounts=5,
                purchase_budget=(20, 21), rtp=False)


def _hook():
    import portfolio_stage as ps

    sink: list[dict] = []
    hook = ps.composed_hook({}, sink=sink)
    ps._label(hook, "q47_synthetic")
    return hook, sink


def _same(a: Any, b: Any) -> bool:
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return type(a) is type(b) and a == b


def sink_problems(a: list[dict], b: list[dict], what: str) -> list[str]:
    if len(a) != len(b):
        return [f"{what}: {len(a)} path records against {len(b)}"]
    out = []
    for i, (x, y) in enumerate(zip(a, b)):
        if set(x) != set(y):
            out.append(f"{what}: record {i}'s keys differ ({sorted(set(x) ^ set(y))})")
            continue
        bad = [k for k in x if not _same(x[k], y[k])]
        if bad:
            out.append(f"{what}: record {i} differs on {bad[:6]}")
    return out[:8]


def rows_problems(a: pd.DataFrame, b: pd.DataFrame, what: str) -> list[str]:
    try:
        pd.testing.assert_frame_equal(a, b, check_exact=True)
    except AssertionError as exc:
        return [f"{what}: the rows differ -- {str(exc).splitlines()[0]}"]
    return []


def synthetic_problems() -> dict[str, list[str]]:
    """Each check's problems (an empty list where it holds), in the docstring's order."""
    from propedge.campaign import gate as vg
    from propedge.campaign.lockstep import path_pool

    out: dict[str, list[str]] = {}
    got = XG.vendored_run_gate_sha256()
    out["source pinned"] = ([] if got == XG.VENDORED_RUN_GATE_SHA256 else
                            [f"the vendored run_gate hashes to {got}, the pin is {XG.VENDORED_RUN_GATE_SHA256}"])
    try:
        XG.check_vendored_source("0" * 64)
        out["wrong pin refused"] = ["a wrong pin was not refused"]
    except RuntimeError:
        out["wrong pin refused"] = []

    blocks = syn_blocks()
    kw = syn_kwargs()
    hv, sv = _hook()
    rows_v, ok_v = vg.run_gate(blocks, path_hook=hv, **kw)
    paid_v = sum(float(r["payouts"]) for r in sv)

    hx, sx = _hook()
    rows_x, ok_x = XG.run_gate(blocks, path_hook=hx, **kw)
    p = rows_problems(rows_v, rows_x, "no class") + sink_problems(sv, sx, "no class")
    if ok_v != ok_x:
        p.append(f"no class: the gate flag {ok_x} against {ok_v}")
    if not paid_v > 0:
        p.append("the synthetic campaign pays nothing: the comparison would be vacuous on payouts")
    out["no class: rows and paths equal"] = p

    hp, sp = _hook()
    rows_p, ok_p = XG.run_gate(blocks, path_hook=hp, funded_account_cls=XG.PassThroughFundedAccount, **kw)
    p = []
    name = XG.class_name(XG.PassThroughFundedAccount)
    if "funded_account_cls" not in rows_p.columns or set(rows_p["funded_account_cls"]) != {name}:
        p.append(f"pass-through class: the rows do not name {name}")
    else:
        p += rows_problems(rows_v, rows_p.drop(columns="funded_account_cls"), "pass-through class")
    p += sink_problems(sv, sp, "pass-through class")
    if ok_v != ok_p:
        p.append(f"pass-through class: the gate flag {ok_p} against {ok_v}")
    out["pass-through class: rows and paths equal"] = p

    h1, s1 = _hook()
    XG.run_gate(blocks, path_hook=h1, funded_account_cls=NeverPaysFundedAccount, **kw)
    paid_1 = sum(float(r["payouts"]) for r in s1)
    out["probe reaches the engine"] = ([] if paid_1 == 0.0 and paid_v > 0 else
                                       [f"the probe's paths were paid {paid_1} (vendored: {paid_v})"])

    pool, n = path_pool(2, n_tasks=SYN_PATHS, memory_per_worker_gb=0.5)
    if pool is not None:
        pool.shutdown()
    if int(n) < 2:
        out["probe reaches path workers"] = [f"not checked: the memory guard allows {n} worker(s) now"]
    else:
        h2, s2 = _hook()
        XG.run_gate(blocks, path_hook=h2, funded_account_cls=NeverPaysFundedAccount, workers=2,
                    memory_per_worker_gb=0.5, **kw)
        out["probe reaches path workers"] = sink_problems(s1, s2, "probe, two workers against one")

    try:
        XG.run_gate(blocks, funded_account_cls=dict, **kw)
        out["non-account class refused"] = ["a class that is not a funded account was not refused"]
    except TypeError:
        out["non-account class refused"] = []

    def local_class() -> type:
        class LocalFundedAccount(FundedAccount):
            pass

        return LocalFundedAccount

    try:
        XG.run_gate(blocks, funded_account_cls=local_class(), workers=2, **kw)
        out["unpicklable class refused"] = ["a class defined inside a function was not refused at two workers"]
    except TypeError:
        out["unpicklable class refused"] = []
    return out


# ------------------------------------------------------------------------------------------------ the registered paths


def _cls(arm: str) -> type | None:
    return None if arm == "none" else XG.PassThroughFundedAccount


def p14_problems(n: int, workers: int, arms: tuple[str, ...]) -> dict[str, list[str]]:
    """P-14's gate call as `rc_screen.Runner.run` makes it for `rc_screen.identity_problems`, through the adapter."""
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
        return {a: ["the blocks hold a different number of trades"] for a in arms}
    cap = B.capacity(t, fcfg)
    horizon = int(fcfg["gate"]["campaign"]["horizon_days"])
    ref = read_result(RESULTS_DIR / S.P14_PATHS)
    out = {}
    for arm in arms:
        sink: list[dict] = []
        inner = ps.composed_hook({"margin": float(fcfg["portfolio"]["margin"]),
                                  "block_days": int(fcfg["portfolio"]["block_days"])}, sink=sink)
        hook = lt.lever_hook(inner)
        label = f"p14_identity_{arm}"
        ps._label(inner, label)
        kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, hook, seed=S.SEED, n_paths=int(n),
                           horizon=horizon, capacity=cap, levels=(0.0,), rtp=False, one_at_a_time=S.STRICT_GAP,
                           purchase_budget=S.BUDGET)
        XG.run_gate(kw.pop("blocks"), workers=int(workers), funded_account_cls=_cls(arm), **kw)
        out[arm] = zd.path_problems(sink, ref, [(label, s, "gate", s) for s in ("point", "lower_bound")], int(n))
    return out


def p16_problems(n: int, workers: int, arms: tuple[str, ...]) -> dict[str, list[str]]:
    """P-16's gate call as identity/stage2_identity.py's `p16_problems` makes it, through the adapter."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc150_dev_test as P
    import rc_dev_test as D
    import score_fv3_grid as gf
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    sp = P.SPEC
    if int(sp.seed) != SI.P16_SEED:
        return {a: [f"P-16's seed in the vendored script is {sp.seed}, not {SI.P16_SEED}"] for a in arms}
    I, b = sp.build()
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    t = b["cells"][sp.cell]["trades"]
    days = b["days"]
    th = D.trades_hash(t)
    if th != sp.trades_sha256:
        return {a: [f"P-16's trades hash {th} is not the pinned {sp.trades_sha256}"] for a in arms}
    keys = B.rrs(t)
    cap = B.capacity(t, fcfg)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        return {a: ["the blocks hold a different number of trades"] for a in arms}
    pcfg = fcfg["portfolio"]
    ref = read_result(RESULTS_DIR / SI.P16_PATHS)
    out = {}
    for arm in arms:
        sink: list[dict] = []
        inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])}, sink=sink)
        hook = lt.lever_hook(inner)
        label = f"p16_identity_{arm}"
        ps._label(inner, label)
        kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, hook, seed=SI.P16_SEED, n_paths=int(n),
                           horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=cap, levels=(0.0,),
                           rtp=False, one_at_a_time=C.STRICT_GAP, purchase_budget=C.BUDGET)
        XG.run_gate(kw.pop("blocks"), workers=int(workers), funded_account_cls=_cls(arm), **kw)
        out[arm] = zd.path_problems(sink, ref, [(label, s, "gate", s) for s in ("point", "lower_bound")], int(n))
    return out


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--synthetic", action="store_true", help="the light identity on synthetic blocks (no bars)")
    ap.add_argument("--paths", type=int, default=None, help="the registered gate paths at N paths (slow or heavy)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--only", choices=("p14", "p16"), default=None)
    ap.add_argument("--cls", choices=("none", "passthrough", "both"), default="both")
    a = ap.parse_args(argv)
    if not a.synthetic and a.paths is None:
        ap.error("give --synthetic or --paths N")
    if a.paths is not None and a.paths < 1:
        ap.error("--paths takes a whole number of at least 1")
    bad = False
    t0 = time.time()
    if a.synthetic:
        res = synthetic_problems()
        for check, probs in res.items():
            if probs:
                bad = True
                print(f"FAILS: {check} -- " + "; ".join(probs))
            else:
                print(f"holds: {check}")
        print(("synthetic identity FAILS" if any(res.values()) else "synthetic identity HOLDS") +
              f" (Q-47, extended.gate; {time.time() - t0:.0f} s)", flush=True)
    if a.paths is not None:
        arms = CLS_ARMS if a.cls == "both" else (a.cls,)
        designs = [("P-14", p14_problems, "a3_brk30_cb20_gate_paths.csv"),
                   ("P-16", p16_problems, SI.P16_PATHS)]
        for name, fn, ref in designs:
            if a.only is not None and name.replace("-", "").lower() != a.only:
                continue
            t1 = time.time()
            print(f"{name}: the registered gate call through extended.gate, {a.paths} paths, arms {arms}...",
                  flush=True)
            for arm, probs in fn(int(a.paths), int(a.workers), arms).items():
                if probs:
                    bad = True
                    print(f"identity FAILS: {name} gate through extended.gate ({arm}) -- {len(probs)} problem(s): "
                          + "; ".join(probs[:6]), flush=True)
                else:
                    print(f"identity HOLDS: {name} gate through extended.gate ({arm}) -- the first {a.paths} paths of "
                          f"results/{ref}'s gate run, both shifts, every PATH_COLS column to 1e-6", flush=True)
            print(f"  {name}: {time.time() - t1:.0f} s", flush=True)
    pm = SI.peak_memory()
    if pm:
        print(pm)
    print(f"EXIT {3 if bad else 0}", flush=True)
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
