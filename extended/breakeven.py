"""Q-20 (E-012 (2), E-013 (2)): P-14's and P-16's trades re-walked with the breakeven move's two fidelity corrections --
only the trades' walk substituted, as E-011's runner substitutes it (`identity/walker_identity.py`); every other line
Stage 2's, vendored and unedited. Imports the vendored engine at call time: run in a process with
`use_vendored_stage2()` done (and this repository's `identity/` on `sys.path` for P-16's narrow substitution).

**The rule sets** (`RULE_SETS`): `stage2` (`extended.walker.STAGE2`: Stage 2's walk, the identity), `stop_first`
(`STAGE2_BE_STOP_FIRST`, correction (a)), `delay5` (`STAGE2_BE_DELAY5`, correction (b)), `both` (`STAGE2_BE_BOTH`).

**The walk** (`walk_minutes_for`): `atlas_a3.walk_minutes`' frame -- one row a (date, slot, side), the same columns,
types and order -- with Stage 2's entries (`fv3_rung_walk.entries`, unchanged: the `delay`-th bar with an open after
the slot, before the bar ending 15:08 CT) walked by `extended.walker.walk` under the rule set, at each (stop, R).

**P-14** (A3-BRK30-CB20 on A3-BRK30's trades, five bars late on the 50- and 100-tick rungs): A3's rung walk, which
Stage 2 caches in `data/atlas/A3` and reads through `atlas_a3.cached_walk`, is re-walked from the development bars
(`a3_frame`: `atlas_a3.pool_minutes`, `bar_arrays`, the config's delay, tick, rungs and R grid) and handed to Stage 2's
builders in the cache's place (`a3_walk`: `atlas_a3.cached_walk` replaced inside the block, restored on leaving it;
nothing is written -- the cache is never touched). Under `stage2` the frame must equal the cache's frame exactly.

**P-16** (`rc_s150_all`): `walker_identity.build_p16(walk)` -- `rc_width_screen.build(I, (150,))` with
`atlas_a3.walk_minutes` replaced for that one call, the inputs loaded under Stage 2's walk (E-011's corrective cycle).
Under `stage2` the cell's trades must have P-16's pinned content hash.

The design's U1 jobs (both arms, `user_journey`'s builders' own steps) and its gate (P-14: `rc_screen.Runner`, P-14's
engine call; P-16: `stage2_identity.p16_problems`' call) are then built from the re-walked trades by Stage 2's code --
the verdict arm's bound and the gate's bounds recomputed from those trades by the design's own rule (`atlas_a3.bounds`).
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any

import numpy as np
import pandas as pd

from extended import walker as W

RULE_SETS = (("stage2", W.STAGE2), ("stop_first", W.STAGE2_BE_STOP_FIRST), ("delay5", W.STAGE2_BE_DELAY5),
             ("both", W.STAGE2_BE_BOTH))
RULES = dict(RULE_SETS)
#: the registered campaign seeds the gate re-reads run at (common random numbers with the registered rows)
P14_GATE_SEED = 20261131
P16_GATE_SEED = 20261206
#: the gate row's columns read beside the registered rows (all present in both registered gate files)
GATE_COLS = ("pf_growth_on_base_p50", "pf_required_p90", "pf_growth_on_base_p10", "pf_net_p50", "median_log_growth",
             "mean_payouts_per_path", "mean_combine_purchases", "mean_accounts_funded", "share_accounts_ever_paid",
             "median_days_to_first_payout", "ruin_probability", "mean_max_drawdown",
             "realised_to_intended_capped_risk", "mean_r_used", "paths")
P14_GATE_FILE = "a3_brk30_cb20_gate.csv"
P16_GATE_FILE = "rc_s150_all_gate.csv"
P16_PATHS_FILE = "rc_s150_all_gate_paths.csv"
#: Q-132 (C1): P-15 (`rc_s100_all`, D-527), built by the same `atlas_a3.walk_minutes` walk as P-16 -- its registered
#: gate (seed 20261204, D-529 (2)); no per-path file of it is vendored, so its gate is held to the registered row only
P15_GATE_SEED = 20261204
P15_GATE_FILE = "rc_s100_all_gate.csv"
#: `rc_dev_test.build_cells`' two lines, which `p15_cells` reproduces (refused if the vendored function differs)
P15_BUILD_CELLS_LINES = ("I = S.inputs()", "return I, RS.build(I)")
GATE_FILES = {"p14": P14_GATE_FILE, "p15": P15_GATE_FILE, "p16": P16_GATE_FILE}


# ------------------------------------------------------------------------------------------------ the walk


def walk_minutes_for(rules: W.Rules):
    """`atlas_a3.walk_minutes(minutes, arrays, delay, tick, rungs, rr_grid)` with Stage 2's entries walked by this
    repository's walker under `rules`."""

    def walk_minutes(minutes, arrays, delay: int, tick: float, rungs, rr_grid):
        import atlas_a3 as A

        from propedge.research import fv3_rung_walk as RW

        bl = W.brackets(tuple(int(S) for S in rungs), tuple(float(R) for R in rr_grid))
        cols = A.walk_columns(rungs, rr_grid)
        parts = []
        for day, g in minutes.groupby("date", sort=True):
            o, h, l, c = (np.asarray(x, dtype=float) for x in arrays(str(day)))
            ent = RW.entries(o, g["slot"].astype(int).tolist(), int(delay))
            if not ent:
                continue
            bars = [int(x[2]) for x in ent]
            res = W.walk(o, h, l, c, bars, o[bars], [x[1] for x in ent], False, bl, tick=float(tick), rules=rules)
            head = pd.DataFrame(ent, columns=["slot", "side", "entry_slot"]).assign(date=str(day), delay=int(delay))
            body = np.empty((len(ent), 4 * len(bl)), dtype=np.int32)
            body[:, 0::4], body[:, 1::4] = res["kind"], res["exit"]
            body[:, 2::4], body[:, 3::4] = res["mae"], res["gross"]
            parts.append(pd.concat([head, pd.DataFrame(body, columns=cols)], axis=1))
        lead = ["date", "slot", "delay", "side", "entry_slot"]
        if not parts:
            return pd.DataFrame(columns=lead + cols)
        w = pd.concat(parts, ignore_index=True)[lead + cols]
        w = w.astype({"slot": "int16", "delay": "int8", "side": "int8", "entry_slot": "int16",
                      **{c: ("int8" if c.startswith("k") else "int32") for c in cols}})
        return w.sort_values(["date", "slot", "side"], kind="stable").reset_index(drop=True)

    walk_minutes.rules = rules
    return walk_minutes


def frame_problems(mine: pd.DataFrame, theirs: pd.DataFrame) -> list[str]:
    """Exact equality of two walk frames (`walker_identity.frame_problems`)."""
    import walker_identity as WI

    return WI.frame_problems(mine, theirs)


# ------------------------------------------------------------------------------------------------ P-14


def a3_inputs() -> dict[str, Any]:
    """A3's walk's inputs as `atlas_a3.cached_walk` reads them: the config, A1's events and days, A1's cache inputs, the
    pooled minutes, and Stage 2's cached frame (read, never written)."""
    import a3_resolution_map as m0
    import atlas_a3 as A

    cfg = A.config()
    _, events, days, a1 = m0.load_a1()
    return {"cfg": cfg, "events": events, "days": days, "a1": a1, "minutes": A.pool_minutes(events, days, cfg),
            "cached": A.cached_walk(cfg, events, days, a1, write=False)}


def a3_frame(rules: W.Rules, X: dict[str, Any]) -> pd.DataFrame:
    """A3's rung walk re-walked under `rules` from the development bars (A3's minutes, delay, tick, rungs, R grid),
    a calendar year of bars in memory at a time (the walk is day by day, so the frame is the same; the runner's
    identity holds it to the cache's under `STAGE2`)."""
    import atlas_a3 as A

    cfg, mins = X["cfg"], X["minutes"]
    walk = walk_minutes_for(rules)
    dates = mins["date"].astype(str)
    parts = []
    for year in sorted(dates.str[:4].unique()):
        m = mins[(dates.str[:4] == year).to_numpy()]
        arr = A.bar_arrays(cfg, sorted(m["date"].astype(str).unique()))
        parts.append(walk(m, arr, int(cfg["screen_delay_min"]), float(cfg["contract"]["tick"]), A.stops(cfg),
                          A.rrs(cfg)))
        del arr
    w = pd.concat(parts, ignore_index=True)
    w = w.astype({c: parts[0][c].dtype for c in w.columns})
    return w.sort_values(["date", "slot", "side"], kind="stable").reset_index(drop=True).copy()   # consolidated


@contextmanager
def a3_walk(frame: pd.DataFrame):
    """`atlas_a3.cached_walk` answering `frame` inside the block (Stage 2's restored on leaving it, also on an error):
    A3's walk substituted for every builder that loads P-14's inputs; nothing read from or written to the cache."""
    import atlas_a3 as A

    stage2 = A.cached_walk

    def cached_walk(cfg, events, days, a1_inputs, **kw):
        return frame

    A.cached_walk = cached_walk
    try:
        yield
    finally:
        A.cached_walk = stage2


def p14_build(frame: pd.DataFrame, rd) -> dict[str, Any]:
    """P-14 on `frame`: its U1 jobs (`user_journey.build_d518`), its gate inputs (`rc_screen.inputs`) and its trades
    (`a3_brk30.cell_trades`), every builder Stage 2's, loaded under the substitution."""
    import a3_brk30 as B
    import rc_screen as S
    import user_journey as UJ

    with a3_walk(frame):
        jobs, _ = UJ.build_d518(rd, ["p14"])
        I = S.inputs()
        t, days = B.cell_trades(I["L"])
    return {"jobs": jobs["p14"], "I": I, "trades": t, "days": days}


def p14_gate(b: dict[str, Any], n_paths: int, workers: int) -> tuple[pd.DataFrame, list[str]]:
    """P-14's gate on `b`'s trades by P-14's engine call (`rc_screen.Runner`, seed 20261131, 0 %, both shifts), and
    the per-path identity against the registered paths (only meaningful on Stage 2's walk)."""
    import rc_screen as S
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    if int(S.SEED) != P14_GATE_SEED:
        raise SystemExit(f"REFUSED: P-14's seed in the vendored screen is {S.SEED}, not {P14_GATE_SEED}")
    R = S.Runner(b["I"], workers)
    df = R.run("p14_q20", b["trades"], b["days"], int(n_paths))
    ref = read_result(RESULTS_DIR / S.P14_PATHS)
    bad = zd.path_problems(R.sink, ref, [("p14_q20", s, "gate", s) for s in ("point", "lower_bound")], int(n_paths))
    return df, bad


# ------------------------------------------------------------------------------------------------ P-16


def p16_build(rules: W.Rules, rd) -> dict[str, Any]:
    """P-16 re-walked under `rules`: `walker_identity.build_p16` (the one narrow substitution), then its U1 jobs as
    `user_journey.build_p16` makes them (`_rc_campaign`, `_single_jobs` at P-16's plan and budget)."""
    import a3_brk30_cb20 as C
    import rc150_dev_test as P
    import user_journey as UJ
    import walker_identity as WI

    I, b = WI.build_p16(walk_minutes_for(rules))
    camp = UJ._rc_campaign(I, b, P.SPEC.cell, P.SPEC)
    jobs = UJ._single_jobs(camp, I["plan"], C.BUDGET)
    return {"jobs": jobs, "I": I, "b": b, "trades": b["cells"][P.SPEC.cell]["trades"], "days": b["days"]}


def p16_gate(x: dict[str, Any], n_paths: int, workers: int) -> tuple[pd.DataFrame, list[str]]:
    """P-16's gate on `x`'s trades exactly as `stage2_identity.p16_problems` calls it (seed 20261206, 0 %, both
    shifts), and the per-path identity against the registered paths (only meaningful on Stage 2's walk)."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc150_dev_test as P
    import score_fv3_grid as gf
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.campaign import gate
    from propedge.reporting.results import read_result

    if int(P.SPEC.seed) != P16_GATE_SEED:
        raise SystemExit(f"REFUSED: P-16's seed in the vendored script is {P.SPEC.seed}, not {P16_GATE_SEED}")
    I = x["I"]
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    t, days = x["trades"], x["days"]
    keys = B.rrs(t)
    cap = B.capacity(t, fcfg)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades")
    pcfg = fcfg["portfolio"]
    sink: list[dict] = []
    inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])}, sink=sink)
    hook = lt.lever_hook(inner)
    ps._label(inner, "p16_q20")
    kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, hook, seed=P16_GATE_SEED, n_paths=int(n_paths),
                       horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=cap, levels=(0.0,), rtp=False,
                       one_at_a_time=C.STRICT_GAP, purchase_budget=C.BUDGET)
    df, _ = gate.run_gate(kw.pop("blocks"), workers=int(workers), **kw)
    ref = read_result(RESULTS_DIR / P16_PATHS_FILE)
    bad = zd.path_problems(sink, ref, [("p16_q20", s, "gate", s) for s in ("point", "lower_bound")], int(n_paths))
    return df, bad


# ------------------------------------------------------------------------------------------------ P-15 (Q-132, C1)


def p15_cells(walk=None):
    """P-15's cells as `rc_dev_test.build_cells()` builds them -- its two lines, `rc_screen.inputs()` then
    `rc_reentry_screen.build(I)` -- with `walk` (None: Stage 2's) substituted for the second line only, the one call
    that walks P-15's marks (both of FV3-C's rungs, as the screen walks them; the cutoff and cells read that walk), the
    inputs (P-14's, A3's cached walk among them) loaded under Stage 2's walk (`walker_identity.substituted_walk`, the
    narrow substitution P-16's `build_p16` uses). Refused if the vendored `build_cells` is not those two lines."""
    import inspect

    import rc_dev_test as D
    import rc_reentry_screen as RS
    import rc_screen as S
    import walker_identity as WI

    src = inspect.getsource(D.build_cells)
    if not all(x in src for x in P15_BUILD_CELLS_LINES):
        raise RuntimeError("REFUSED: rc_dev_test.build_cells is not the two lines this runner reproduces")
    I = S.inputs()
    if walk is None:
        return I, RS.build(I)
    with WI.substituted_walk(walk):
        b = RS.build(I)
    return I, b


def p15_build(rules: W.Rules, rd) -> dict[str, Any]:
    """P-15 re-walked under `rules` (`p15_cells`), then its U1 jobs as `user_journey.build_p15` makes them
    (`_rc_campaign` at P-15's spec, `_single_jobs` at the plan and budget)."""
    import a3_brk30_cb20 as C
    import rc_dev_test as D
    import user_journey as UJ

    I, b = p15_cells(walk_minutes_for(rules))
    camp = UJ._rc_campaign(I, b, D.P15.cell, D.P15)
    jobs = UJ._single_jobs(camp, I["plan"], C.BUDGET)
    return {"jobs": jobs, "I": I, "b": b, "trades": b["cells"][D.P15.cell]["trades"], "days": b["days"]}


def p15_trade_problems(x: dict[str, Any], rd) -> list[str]:
    """P-15's registered identity of its trades (`rc_dev_test.trade_problems`): the screen's row (`rc_reentry_screen.csv`,
    its sha256 pinned -- count, busiest day, capacity, long share, candidates a day, every R's unresolved share) and the
    pinned content hash `TRADES_SHA256`. Meaningful on Stage 2's walk only."""
    import rc_dev_test as D

    return D.trade_problems(rd, x["b"], x["I"]["L"]["fcfg"], spec=D.P15)


def p15_gate(x: dict[str, Any], n_paths: int, workers: int) -> tuple[pd.DataFrame, list[str]]:
    """P-15's gate on `x`'s trades exactly as `rc_dev_test.run` calls its section `gate` (seed 20261204, P-14's engine
    call: `atlas_a3.gate_kwargs` with the cell's busiest-day capacity, the no-closure plan, the strict rule, the budget,
    the lever hook, both shifts), at 0 % only (the registered row's other levels do not change its 0 % row: P-16's
    identity at 500 paths, E-188). No per-path reference is vendored for P-15: the second item is always []."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc_dev_test as D
    import score_fv3_grid as gf

    from propedge.campaign import gate

    if int(D.P15.seed) != P15_GATE_SEED:
        raise SystemExit(f"REFUSED: P-15's seed in the vendored script is {D.P15.seed}, not {P15_GATE_SEED}")
    I = x["I"]
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    t, days = x["trades"], x["days"]
    keys = B.rrs(t)
    cap = B.capacity(t, fcfg)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades")
    pcfg = fcfg["portfolio"]
    sink: list[dict] = []
    inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])}, sink=sink)
    hook = lt.lever_hook(inner)
    ps._label(inner, "p15_q132")
    kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, hook, seed=P15_GATE_SEED, n_paths=int(n_paths),
                       horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=cap, levels=(0.0,), rtp=False,
                       one_at_a_time=C.STRICT_GAP, purchase_budget=C.BUDGET)
    df, _ = gate.run_gate(kw.pop("blocks"), workers=int(workers), **kw)
    return df, []


# ------------------------------------------------------------------------------------------------ the readings


def gate_rows(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    """{shift: {column: value}} of a gate run's 0 % rows (section `gate` where the frame names one)."""
    d = df.copy()
    if "section" in d.columns:
        d = d[d["section"].astype(str) == "gate"]
    d = d[np.isclose(d["enforcement_p"].astype(float), 0.0)]
    out = {}
    for s in ("point", "lower_bound"):
        r = d[d["shift"].astype(str) == s]
        if len(r) != 1:
            raise ValueError(f"{len(r)} gate rows at 0 % for shift {s}")
        out[s] = {c: float(r.iloc[0][c]) for c in GATE_COLS if c in r.columns}
    return out


def registered_gate(design: str) -> dict[str, dict[str, float]]:
    """The registered gate rows at 0 % (section `gate`), read through the vendored reader (its manifest verified)."""
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    return gate_rows(read_result(RESULTS_DIR / GATE_FILES[design]))


def gate_problems(mine: dict[str, dict[str, float]], ref: dict[str, dict[str, float]], tol: float = 1e-6) -> list[str]:
    """Every `GATE_COLS` column of the registered rows against this run's, both shifts, to `tol` relative (absolute
    below 1); a column missing from either side is a difference."""
    out = []
    for s in ("point", "lower_bound"):
        for c in GATE_COLS:
            v, m = ref.get(s, {}).get(c), mine.get(s, {}).get(c)
            if v is None or m is None:
                out.append(f"{s} {c}: missing ({'registered' if v is None else 'this run'})")
            elif not ((np.isnan(m) and np.isnan(v)) or abs(m - v) <= tol * max(1.0, abs(v))):
                out.append(f"{s} {c}: {m} against the registered {v}")
    return out


def trade_rows(t: pd.DataFrame, ref: pd.DataFrame, rr_grid) -> list[dict[str, Any]]:
    """Per R: the trades, the share of each exit kind, the mean net R, and how many trades' kind or gross differ from
    Stage 2's walk (`ref`, the same trades in the same order)."""
    out = []
    same_rows = len(t) == len(ref) and (t[["date", "entry_t", "side"]].to_numpy() ==
                                        ref[["date", "entry_t", "side"]].to_numpy()).all()
    for R in rr_grid:
        o, r = t.get(f"o_{R:g}"), t.get(f"r_{R:g}")
        if o is None or r is None:
            continue
        off = o.astype(str) != ""
        row = {"rr": float(R), "trades": int(off.sum()), "mean_net_r": float(r[off].astype(float).mean())}
        for code, name in (("s", "stop"), ("t", "target"), ("f", "flatten"), ("b", "breakeven")):
            row[f"share_{name}"] = float((o[off].astype(str) == code).mean()) if off.any() else float("nan")
        if same_rows:
            g, g0 = t[f"g_{R:g}"].to_numpy(float), ref[f"g_{R:g}"].to_numpy(float)
            k, k0 = o.astype(str).to_numpy(), ref[f"o_{R:g}"].astype(str).to_numpy()
            row["changed_kind"] = int((k != k0).sum())
            row["changed_gross"] = int((~((g == g0) | (np.isnan(g) & np.isnan(g0)))).sum())
        else:
            row["changed_kind"] = row["changed_gross"] = -1        # the trade sets differ (entries are Stage 2's)
        out.append(row)
    return out


__all__ = ["RULE_SETS", "RULES", "GATE_COLS", "P14_GATE_SEED", "P15_GATE_SEED", "P16_GATE_SEED", "GATE_FILES",
           "walk_minutes_for", "frame_problems", "a3_inputs", "a3_frame", "a3_walk", "p14_build", "p14_gate",
           "p16_build", "p16_gate", "p15_cells", "p15_build", "p15_trade_problems", "p15_gate", "gate_rows",
           "registered_gate", "gate_problems", "trade_rows"]
