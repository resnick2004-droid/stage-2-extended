"""The atlas screen's cells (R6, D-460; EXPLORATORY): each (pattern, side rule) through the family's plan in the campaign
engine. Called by `scripts/atlas_screen.py --screen`; see its docstring. T24's machinery is imported, never copied:
eligibility and the stop map (`t24_exec`), the costing (`t23_choose.trade_r`), the plan (`t24_exec.fixed_policy`,
`t24_gf15b.policy`, or `t24_exec.table_policy`), the blocks and edge statistics (`score_fv3_grid`, `confirm_fv3`), the
campaign call's arguments (`t24_exec.run_config`'s, with the screen's path count).

The plans: `gf15` (A1's first screen) and `gf15b` (A1's rescreen, D-469) are fixed policies, the same for every cell;
`table` (family A2, D-481) is FV3-C's kind of state table re-solved on each cell's own trades -- `t24_exec.table_policy`
at the edge cell nearest the lowest of the cell's R's one-sided bounds (`t24_wide.edge_cell`), exactly as T24's
execution screen builds it -- its oracles first: a cell whose table fails one is recorded REFUSED with its oracle and edge
rows, never run and never ranked (D-429). Among the cells whose table passed and whose offered R's resolve, the screen
ranks by growth on the required bankroll at the bound (D-481 (3)), each cell's row in the walk family's screen beside it."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/atlas_screen.py"
RRS = (1.0, 1.5, 2.0, 3.0)
CUT = 870                                   # 07:30 CT on the trading-day clock
DELAY = 5


def hour_label(slot: int) -> str:
    """The R137 decision slot an event's minute is costed at: its hour start in CT, 08:30-08:59 the 08:30 slot."""
    m = (17 * 60 + int(slot)) % 1440
    if 8 * 60 + 30 <= m < 9 * 60:
        return "08:30"
    return f"{m // 60:02d}:00"


def cell_walks(events: pd.DataFrame, walks: pd.DataFrame, days: pd.DataFrame, pid: int, rule: str) -> pd.DataFrame:
    """One cell's walks in T24's capture columns: its pattern's events five bars late, on the side the rule takes."""
    import t24_screen as ts

    ev = events[events["pattern"].astype(int) == pid].copy()
    w = walks[walks["delay"].astype(int) == DELAY]
    if rule == "coin":
        ev = ev.drop_duplicates(["date", "slot"]).rename(columns={"slot": "decision_slot_minutes"})
        ev["side"] = ts.coin(ev).to_numpy()
        ev = ev.rename(columns={"decision_slot_minutes": "slot"})
    elif rule == "fade":
        ev["side"] = -ev["side"].astype(int)
    ev = ev.drop_duplicates(["date", "slot", "side"])
    t = ev[["date", "slot", "side"]].merge(w, on=["date", "slot", "side"], how="inner", validate="one_to_one")
    t = t.rename(columns={"slot": "decision_slot_minutes"})
    t["decision_ct"] = [hour_label(s) for s in t["decision_slot_minutes"]]
    t["year"] = t["date"].astype(str).str[:4].astype(int)
    t["day_kind"] = t["date"].map(dict(zip(days["date"].astype(str), days["day_kind"].astype(str))))
    return t


def cell_trades(t: pd.DataFrame, top: int, spread: dict, bix: dict) -> tuple[pd.DataFrame, list[dict]]:
    """`t24_exec.trades`' steps on a cell's walks: eligibility by event hour, the map, the cut, each R's net R."""
    import t23_choose as tc
    import t24_exec as te
    import t24_wide as tw

    elig, rows = te.eligibility(t, bix)
    smap = te.stop_map(elig, top)
    rows += [{"section": "map", "decision_ct": ct, "stop": S,
              "offered": ",".join(f"{R:g}" for R in RRS if elig[(ct, S, R)])} for ct, S in smap.items()]
    t = t[t["decision_ct"].astype(str).isin(smap)].copy()
    t = t[~((t["day_kind"].astype(str) == "b") & (t["decision_slot_minutes"].astype(int) < CUT))]
    if t.empty:
        return t, rows
    t["S"] = t["decision_ct"].astype(str).map(smap).astype(int)
    t["entry_t"] = t["entry_slot"].astype(float)
    parts = []
    for S, g in t.groupby("S"):
        g = g.copy()
        for R in RRS:
            b = bix[(R * S, float(S))]
            offered = np.array([elig[(ct, S, R)] for ct in g["decision_ct"].astype(str)])
            r = tc.trade_r(g, b, R * S, float(S), spread, tw.FEE_MICRO)
            gr, co = tc.trade_parts(g, b, R * S, float(S), spread, tw.FEE_MICRO)
            g[f"r_{R:g}"] = np.where(offered, r, np.nan)
            g[f"g_{R:g}"] = np.where(offered, gr, np.nan)
            g[f"c_{R:g}"] = np.where(offered, co, np.nan)
            g[f"o_{R:g}"] = np.where(offered, g[f"o{b}"].astype(str), "")
            g[f"exit_t_{R:g}"] = np.where(offered, g["entry_t"] + g[f"m{b}"].astype(float), np.nan)
            g[f"mae_{R:g}"] = np.nan
        g["stop_ticks"] = int(round(S / 0.25))
        parts.append(g)
    t = pd.concat(parts).sort_values(["date", "entry_t"], kind="stable").reset_index(drop=True)
    t["exit_t"] = t[[f"exit_t_{R:g}" for R in RRS]].max(axis=1)
    t["flat"] = t["o_1"] == "f"
    t["fee_micro_eq"] = tw.FEE_MICRO
    t["side"] = np.where(t["side"].astype(int) > 0, "long", "short")
    t["date"] = t["date"].astype(str)
    return t, rows


PLANS = ("gf15", "gf15b", "table")
TABLE_LABEL = "m40"                         # the map the table's rungs come from (t24_exec's label for its policy)


def plan_policy(plan: str):
    """The family's declared plan when it is one policy for every cell: T24-GF15b's (D-439: every state closed once it
    cannot carry its trade; D-469's rescreen) or T24-GF15's (D-432; the first screen, with the stuck-seat fault D-438
    found). The table plan depends on the cell's trades: `cell_policy`."""
    if plan == "gf15b":
        import t24_gf15b as tb
        return tb.policy()
    if plan == "gf15":
        import t24_exec as te
        return te.fixed_policy("gf15")
    if plan == "table":
        raise ValueError("the table plan is solved on each cell's own trades: cell_policy(plan, t, lb_by)")
    raise ValueError(f"unknown plan {plan!r}")


def cell_policy(plan: str, t: pd.DataFrame, lb_by: dict[float, float]) -> tuple[object, list[dict]]:
    """(the cell's policy, the rows that record it). A fixed plan is `plan_policy`'s, with no rows. The table (D-481
    (2)) is `t24_exec.table_policy` on the cell's trades at `t24_wide.edge_cell(lb_by)` -- as `t24_exec.screen_config`
    builds it: one rung a stop of the cell's map at its share of the cell's trades, each R's availability the share of
    the rung's trades offering it, FV3-C's v12 solver configuration -- with its oracle rows and its `table` row (edge,
    rent, rate, p_pass, the rungs' stops and shares). A failed oracle raises `t24_wide.OracleRefused` carrying the
    oracle rows (D-429)."""
    if plan != "table":
        return plan_policy(plan), []
    import gc

    import t24_exec as te
    import t24_wide as tw

    pol, rows = te.table_policy(t, tw.edge_cell(lb_by), TABLE_LABEL)
    gc.collect()                                # the solver's chain objects go before the campaign's arrays arrive
    return pol, rows


def run_cell(t: pd.DataFrame, days: list[str], n_paths: int, seed: int, plan: str = "gf15") -> pd.DataFrame:
    """The plan through the campaign engine: `t24_exec.run_config`'s arguments with the screen's path count; the
    protocol's day capacity raised to the cell's busiest day where T24's 23 is too few (D-469: a capacity, never a
    choice -- a cell within 23 runs T24's protocol unchanged). The table plan is solved on the cell's trades first
    (`cell_policy`); its oracle refusal is raised before any campaign runs, carrying the oracle rows and the cell's edge
    rows, and its rows join the returned frame after the edge rows (a fixed plan's frame is unchanged)."""
    from dataclasses import replace
    import confirm_fv3 as cf
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import score_fv3_grid as gf
    import t24_exec as te
    import t24_wide as tw

    from propedge.campaign import gate
    from propedge.campaign.payout_method import rules_for_method

    menu = list(RRS)
    stats = cf.edge_stats(t, menu, days, tw.BLOCK, None)
    e_by, lb_by = ps._by(stats, "e"), ps._by(stats, "lb")
    edge_rows = [{"section": "edge", "rr": R, "e": stats[R]["e"], "lb": stats[R]["lb"], "n": stats[R]["n"]}
                 for R in menu]
    try:
        policy, plan_rows = cell_policy(plan, t, lb_by)
    except tw.OracleRefused as exc:
        raise tw.OracleRefused(str(exc), list(exc.rows) + edge_rows) from None
    blocks, n_used = gf.gate_blocks(t, days, 0.25 * 2.0, menu, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise RuntimeError("the blocks hold a different number of trades")
    hook = lt.lever_hook(ps.composed_hook({"margin": tw.MARGIN, "block_days": tw.BLOCK}))
    busiest = int(t.groupby("date").size().max()) if len(t) else 0
    proto = tw.protocol()
    if busiest > int(proto.trades_per_day):
        proto = replace(proto, trades_per_day=busiest)
    df, _ = gate.run_gate(list(blocks), e=e_by[1.0], lb=lb_by[1.0], protocol=proto, bankroll=gf.UNBOUND_BANKROLL,
                          horizon_days=tw.HORIZON, n_paths=n_paths, seed=seed, accounts=tw.ACCOUNTS,
                          sizing=tw.sizing(), rules=rules_for_method("aeropay"), mode="rotation",
                          settlement="pessimistic", combines=tw.ACCOUNTS, total_accounts=tw.ACCOUNTS,
                          risk_policy=policy, e_by_rr=e_by, lb_by_rr=lb_by, levels=(0.0,),
                          path_hook=hook, rtp=False, routing="able", cross_account=True, hold_to_own_exit=True,
                          one_at_a_time=tw.GAP)
    edge = pd.DataFrame(edge_rows)
    parts = [df.assign(section="campaign"), edge] + ([pd.DataFrame(plan_rows)] if plan_rows else [])
    return pd.concat(parts, ignore_index=True)


def cells(cfg: dict) -> list[tuple[int, str, str]]:
    """(pattern id, name, side rule): the clock's coin, every other pattern followed and faded."""
    out = []
    for pid, p in enumerate(cfg["patterns"]):
        if p["kind"] == "clock":
            out.append((pid, p["name"], "coin"))
        else:
            out += [(pid, p["name"], r) for r in cfg["side_rules"]]
    return out


_LOADED: dict = {}


def _loaded(family: str):
    """The walk tables and the costs, once per worker process."""
    if family not in _LOADED:
        import t23_choose as tc

        from propedge.reporting.results import read_result
        import atlas_screen as sc

        cfg, q, tables = sc.load_walk(family)
        sp = read_result(ROOT / tc.R137)
        sp = sp[sp["kind"] == "spread"]
        spread = {(str(r.decision_ct), int(r.year)): float(r.spread_ticks_mean) for r in sp.itertuples()
                  if float(r.quotes) > 0}
        _LOADED[family] = (cfg, q, tables, spread)
    return _LOADED[family]


def resolution(t: pd.DataFrame) -> tuple[dict, bool]:
    """Each offered R's unresolved share in the cell's trades, overall and in its worst year; whether all resolve."""
    res = {}
    for R in RRS:
        o = t[f"o_{R:g}"].astype(str)
        m = o != ""
        if m.any():
            f = o[m] == "f"
            res[f"unresolved_{R:g}"] = float(f.mean())
            res[f"unresolved_worst_year_{R:g}"] = float(f.groupby(t.loc[m, "year"]).mean().max())
    return res, all(v <= 0.05 for k, v in res.items() if k.startswith("unresolved"))


def table_screen(df: pd.DataFrame) -> dict:
    """The table's record on a cell's screen row: the edge cell it was solved at, the rent, the rate, P(pass) and the
    rungs (its `table` row, `t24_exec.table_policy`'s)."""
    tab = df[df["section"] == "table"].iloc[0]
    return {"table_passed": True, "table_edge": float(tab["edge"]), "table_rent": float(tab["rent"]),
            "table_rate": float(tab["rate"]), "table_p_pass": float(tab["p_pass"]),
            "table_rung_stops": str(tab["rung_stops"]), "table_rung_shares": str(tab["rung_shares"])}


def _job(args) -> dict:
    """One cell in a worker. `args`: (family, pattern id, name, side rule[, the trades the walk family's screen holds
    for the cell -- a table cell built on a borrowed walk must hold exactly those, D-481 (1)])."""
    family, pid, name, rule, *expect = args
    try:
        cfg, q, (events, walks, days), spread = _loaded(family)
        bix = {(float(T), float(S)): i for i, (T, S) in enumerate(q["bracket_points"])}
        t = cell_walks(events, walks, days, pid, rule)
        t, rows = cell_trades(t, 40, spread, bix)
        plan = str(cfg["plan"])
        if plan in ("gf15b", "table") and len(t):
            import t24_gf15b as tb
            t = tb.gap_as_cost(t)                  # P-08's declared split, as T24-GF15b books it (net R unchanged)
        day_set = sorted(days["date"].astype(str))            # every day record, as t24_exec's day set
        if expect and expect[0] is not None and int(expect[0]) != len(t):
            raise RuntimeError(f"{len(t)} trades where the walk family's screen holds {int(expect[0])}: the walk is not "
                               "the one that screen read (D-481 (1)); nothing run")
        if t.empty:
            return {"pid": pid, "name": name, "rule": rule, "rows": rows, "screen": {"trades": 0, "refused": "no trade"}}
        if plan == "table":
            import t24_wide as tw
            try:
                df = run_cell(t, day_set, int(cfg["screen"]["paths"]), int(cfg["screen"]["seed"]), plan)
            except tw.OracleRefused as exc:                # D-429: recorded with its oracle rows, never run or ranked
                res, resolves = resolution(t)
                return {"pid": pid, "name": name, "rule": rule, "rows": rows + list(exc.rows),
                        "screen": {"trades": int(len(t)), "trades_per_day": len(t) / max(len(day_set), 1),
                                   "refused": str(exc), "table_passed": False, "resolves": resolves, **res}}
        else:
            df = run_cell(t, day_set, int(cfg["screen"]["paths"]), int(cfg["screen"]["seed"]), plan)
        g = df[(df["section"] == "campaign") & (df["shift"] == "lower_bound")].iloc[0]
        p = df[(df["section"] == "campaign") & (df["shift"] == "point")].iloc[0]
        res, resolves = resolution(t)
        trades_per_day = len(t) / max(len(day_set), 1)
        screen = {"trades": int(len(t)), "trades_per_day": trades_per_day,
                  "growth_at_bound": float(g["pf_growth_on_base_p50"]), "growth_at_point": float(p["pf_growth_on_base_p50"]),
                  "required_p90": float(g["pf_required_p90"]), "break_even_denial": float(g["pf_break_even_denial_p50"]),
                  "days_to_first_payout": float(g["median_days_to_first_payout"]),
                  "payouts_per_month": float(g.get("st_payouts_per_month_p50", np.nan)), "resolves": resolves, **res}
        if plan == "table":
            screen.update(table_screen(df))
        return {"pid": pid, "name": name, "rule": rule, "rows": rows, "campaign": df, "screen": screen}
    except BaseException:                                            # noqa: B036 -- returned, never lost
        import traceback
        return {"pid": pid, "name": name, "rule": rule, "error": traceback.format_exc()}


def free_gb() -> float:
    """The physical memory available now, in GB (2.0 where it cannot be read)."""
    try:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("tot", ctypes.c_ulonglong),
                        ("avail", ctypes.c_ulonglong), ("tp", ctypes.c_ulonglong), ("ap", ctypes.c_ulonglong),
                        ("tv", ctypes.c_ulonglong), ("av", ctypes.c_ulonglong), ("ae", ctypes.c_ulonglong)]
        m = MS()
        m.l = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.avail / 2 ** 30
    except Exception:
        return 2.0


#: GB a worker needs, by plan. A fixed plan's worker holds the walk tables and one cell's campaign: 2 GB (D-464 (5),
#: with the BLAS threads at one). A table worker also solves the cell's table before its campaign. Measured on a toy
#: (2026-10-30, D-481's build; synthetic trades, never a cell): `t24_exec.table_policy` on two rungs (20 and 40-point
#: stops, the most an m40 cell carries) at edge -0.05 peaked near 0.80 GB of private memory against 0.06 GB for the
#: interpreter and its modules -- about 0.74 GB for the solve, rounded up here. It is counted on top of the campaign's
#: 2 GB though the two never overlap in time (the conservative side). The same toy took about 1,470 s on one core: the
#: oracles about 320 s, then about 370 to 410 s for each chain solve (two rent rounds and the tie-broken export).
TABLE_SOLVE_GB = 1.0
WORKER_GB = {"gf15": 2.0, "gf15b": 2.0, "table": 2.0 + TABLE_SOLVE_GB}


def workers(plan: str = "gf15", avail: float | None = None) -> int:
    """Memory-guarded: one worker per WORKER_GB[plan] of free memory, at most four, at least one; ATLAS_WORKERS
    overrides (still at most four)."""
    avail = free_gb() if avail is None else float(avail)
    return int(max(1, min(4, os.environ.get("ATLAS_WORKERS") and int(os.environ["ATLAS_WORKERS"])
                          or avail // WORKER_GB[plan])))


def screen_name(family: str, cfg: dict) -> str:
    """The screen's result name: `atlas_screen_<family>`, the plan's suffix where a family was screened under a second
    fixed plan (A1's rescreen, D-469: `atlas_screen_a1_gf15b`); A2's table screen is `atlas_screen_a2` (D-481)."""
    plan = str(cfg["plan"])
    return f"atlas_screen_{family.lower()}" + ("" if plan in ("gf15", "table") else f"_{plan}")


BESIDE_COLS = ("rank", "trades", "growth_at_bound", "growth_at_point", "required_p90", "resolves")


def beside(family: str, results_dir: Path | None = None) -> tuple[str, Path, pd.DataFrame] | None:
    """For a family on a borrowed walk (D-481: A2 on A1's): (the walk family, its screen's file, that screen's rows,
    renamed `<walk family>_<column>`) -- each cell's row beside it, read through its manifest; None for a family on its
    own walk."""
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result
    from propedge.research import atlas_walk as AW

    src, wcfg = AW.walk_source(family)
    if src == family:
        return None
    path = Path(results_dir if results_dir is not None else RESULTS_DIR) / f"{screen_name(src, wcfg)}.csv"
    b = read_result(path)
    b = b[b["section"] == "screen"][["pattern", "rule", *BESIDE_COLS]].reset_index(drop=True)
    if b.duplicated(["pattern", "rule"]).any():
        raise ValueError(f"{path.name}: a cell appears twice in its screen rows")
    return src, path, b.rename(columns={c: f"{src.lower()}_{c}" for c in BESIDE_COLS})


def rank_screen(s: pd.DataFrame, plan: str) -> pd.DataFrame:
    """The screen rows ranked. A fixed plan (A1, D-460): every cell by growth on the required bankroll at the bound,
    highest first. The table (A2, D-481 (3)): only the cells whose table passed its oracles, whose offered R's resolve
    and that carry a growth reading are ranked, highest first; the rest follow unranked (rank empty) with the reason."""
    if plan != "table":
        s = s.sort_values("growth_at_bound", ascending=False, na_position="last")
        s.insert(1, "rank", range(1, len(s) + 1))
        return s
    s = s.copy()
    passed = (s["table_passed"] if "table_passed" in s else pd.Series(False, index=s.index)).fillna(False).astype(bool)
    resolves = (s["resolves"] if "resolves" in s else pd.Series(False, index=s.index)).fillna(False).astype(bool)
    growth = pd.to_numeric(s["growth_at_bound"] if "growth_at_bound" in s else pd.Series(np.nan, index=s.index),
                           errors="coerce")
    trades = pd.to_numeric(s["trades"], errors="coerce").fillna(0)
    ok = passed & resolves & growth.notna()
    why = np.select([trades <= 0, ~passed, ~resolves, growth.isna()],
                    ["no trade", "table refused by an oracle", "an offered R does not resolve", "no growth reading"],
                    default="")
    s["unranked_reason"] = np.where(ok, None, why)
    s["_ok"], s["_g"] = ok, growth
    s = s.sort_values(["_ok", "_g"], ascending=[False, False], na_position="last", kind="stable")
    s.insert(1, "rank", [float(i + 1) if o else np.nan for i, o in enumerate(s["_ok"])])
    return s.drop(columns=["_ok", "_g"])


def screen(family: str) -> int:
    from propedge.backtest.harness import VariantCounter
    from propedge import RESULTS_DIR
    from propedge.reporting.results import write_result
    from propedge.research import atlas_walk as AW

    cfg = AW.config(family)
    plan = str(cfg["plan"])
    if plan not in PLANS:
        raise ValueError(f"unknown plan {plan!r}")
    for var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(var, "1")          # D-464 (5): the workers inherit it; about 0.7 GB less each
    bes = beside(family)
    if bes is None:
        jobs = [(family, pid, name, rule) for pid, name, rule in cells(cfg)]
    else:                                        # D-481 (1): each cell must hold the trades the walk family screened
        held = {(str(r.pattern), str(r.rule)): int(getattr(r, f"{bes[0].lower()}_trades"))
                for r in bes[2].itertuples(index=False)}
        jobs = [(family, pid, name, rule, held.get((name, rule))) for pid, name, rule in cells(cfg)]
    n = workers(plan)
    print(f"{len(jobs)} cells on {n} worker(s) ({free_gb():.1f} GB free, {WORKER_GB[plan]:g} GB a worker)", flush=True)
    import time

    def _progress(i: int, o: dict, t0: float) -> None:
        sc = o.get("screen") or {}
        tail = "error" if "error" in o else (f"growth at bound {sc.get('growth_at_bound', float('nan')):+.4f}"
                                              if "growth_at_bound" in sc else str(sc.get("refused", "")))
        print(f"[{i}/{len(jobs)} {time.time() - t0:7.0f}s] {o['name']} {o['rule']}: {tail}", flush=True)

    t0 = time.time()
    outs = []
    if n > 1:
        from multiprocessing import Pool
        with Pool(n) as pool:
            for o in pool.imap_unordered(_job, jobs):
                outs.append(o)
                _progress(len(outs), o, t0)
    else:
        for j in jobs:
            outs.append(_job(j))
            _progress(len(outs), outs[-1], t0)
    errors = [o for o in outs if "error" in o]
    for o in errors:
        print(f"ERROR at {o['name']} {o['rule']}:\n{o['error']}", flush=True)
    frames, scr = [], []
    vc = VariantCounter(path=RESULTS_DIR / "variants.jsonl")
    for o in sorted((o for o in outs if "error" not in o), key=lambda x: (x["pid"], x["rule"])):
        tag = {"pattern": o["name"], "pattern_id": o["pid"], "rule": o["rule"]}
        scr.append({"section": "screen", **tag, **o["screen"]})
        frames.append(pd.DataFrame([{**r, **tag} for r in o["rows"]]))
        if "campaign" in o:
            frames.append(o["campaign"].assign(**tag))
        vc.record(prereg_id=f"{cfg['decision']}:atlas_{family}", seed=int(cfg["screen"]["seed"]), exploratory=True,
                  params={"study": f"atlas {family} screen", **tag}, label=f"atlas {family} {o['name']} {o['rule']}")
    s = rank_screen(pd.DataFrame(scr), plan)
    if bes is not None:
        s = s.merge(bes[2], on=["pattern", "rule"], how="left", validate="one_to_one")
    frames.insert(0, s)
    out = pd.concat(frames, ignore_index=True)
    name = screen_name(family, cfg)
    parameters = {"family": family, "config": f"config/atlas_{family.lower()}.yaml", "cells": len(jobs),
                  "paths": int(cfg["screen"]["paths"]), "delay": DELAY, "map": "m40", "plan": plan,
                  "rule": "strict one position at a time, five minutes", "errors": len(errors)}
    description = (f"Signal atlas {family}'s screen on the local bars (R6): every declared cell through "
                   "T24's gf15 plan, ranked by growth on the required bankroll at each R's bound.")
    status = "EXPLORATORY screen (D-460): it picks the cell for the registered development verdict; never a verdict"
    if bes is not None:
        parameters.update({"walk_family": bes[0], "walk_config": f"config/atlas_{bes[0].lower()}.yaml",
                           "walk_cache_inputs": AW.inputs_digest(bes[0], str(cfg["market"])),
                           "beside": f"results/{bes[1].name}"})
    if plan == "table":
        refused = int((s.get("table_passed", pd.Series(dtype=object)) == False).sum())        # noqa: E712
        parameters.update({"solver": "scripts/t24_exec.table_policy (config/state_policy_v12.yaml's rules, rent and "
                                     "export; FV3-C's)", "edge_cell": "t24_wide.edge_cell (the grid edge nearest the "
                                     "lowest of the cell's R's one-sided bounds)", "refused": refused,
                           "ranked": int(s["rank"].notna().sum()), "variant_label": f"{cfg['decision']}:atlas_{family}"})
        description = (f"Signal atlas {family}'s screen on the local bars ({cfg['decision']}): every declared cell sized "
                       "by FV3-C's kind of state table re-solved on its own trades, the oracles first (a failing table "
                       "REFUSED, never run or ranked); ranked by growth on the required bankroll at each R's bound "
                       "among the cells whose table passed and whose offered R's resolve; each cell's "
                       f"{bes[0] if bes else family} row beside it.")
        status = (f"EXPLORATORY screen ({cfg['decision']}): it picks the cell for the registered development verdict; "
                  "never a verdict")
    write_result(out, name, script=SCRIPT, seed=int(cfg["screen"]["seed"]), exploratory=True, parameters=parameters,
                 description=description, notes={"status": status})
    show = ["rank", "pattern", "rule", "trades_per_day", "growth_at_point", "growth_at_bound", "resolves"]
    if plan == "table":
        show += [c for c in ("table_passed", "table_edge", "unranked_reason",
                             *(f"{bes[0].lower()}_{c}" for c in ("rank", "growth_at_bound") if bes)) if c in s]
    print(s[show].to_string(), flush=True)
    return 4 if errors else 0
