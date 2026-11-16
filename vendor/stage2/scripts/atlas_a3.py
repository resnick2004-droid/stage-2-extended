"""Signal atlas family A3 (D-490, D-491, D-492; EXPLORATORY screen): FV3-C's whole design driven by family A1's mechanical
events -- A1's 31 cells walked on FV3-C's rungs, sized by FV3-C's exact exported v12 policy under FV3-C's protocol.

    python scripts/atlas_screen.py --family A3 --walk      # A1's cache checked, A3's rung walk cached under data/atlas/A3
    python scripts/atlas_screen.py --family A3 --screen    # the identity, then every cell -> results/atlas_screen_a3.csv
    python scripts/atlas_a3.py --identity                  # the identity alone (nothing written)

Run the screen once, from a clean checkout (D-474), after the commit that adds this file (D-492 (7)).

**The trades** (D-492 (1)-(2)). A1's events exactly as A1's walk found them (`data/atlas/A1`, read only; refused unless its
manifest names the inputs A1's walk would name today, `a3_resolution_map.load_a1`). Every distinct event minute of A1's
sixteen patterns (the clock's slots included, for the null cell) on the 'n' and 'b' days -- a 'b' day's events before the
07:30 CT cut dropped -- is walked long and short, five bars late, by `propedge/research/fv3_rung_walk.py` on FV3-C's 12.5
and 25-point rungs at every quarter R to 3R, with FV3's breakeven move, MAE and FV3-C's 15:10 flatten; the walk is cached
under `data/atlas/A3` with its own digest (A1's inputs, the walk's code, the rungs, the R grid, the delay; A1's cache
untouched). A cell's events (`atlas_cells.cell_walks`: the pattern, the side rule, the clock's seeded coin) take the rung
the rung rule gives their event hour and every R offered there; an hour with no rung trades nothing.

**The rung rule** is read from step 0's map (`results/a3_resolution_map.csv`, pinned by sha256 in the config): per event
hour the wider of the two rungs whose 1:1 row is eligible (at most 5 % unresolved overall and in every year on normal days,
a breakeven exit resolved), the narrower where only it is, no trade where neither; every R whose row at that hour and rung
is eligible is offered.

**Each trade's record** is the one FV3-C's campaign path consumes (`score_fv3_grid.gate_trades`' columns): its date, year,
entry bar, side, stop ticks, and at every R the net R, MAE in R and exit bar (NaN where the R is not offered), the log's
single exit and flatten flag at the fresh Combine's R (1.5), the fee a micro-equivalent priced in. Costs: one tick at
entry (A1's walk's entry slip, in place of FV3's spread) and the rest FV3-C's (`Signals3.outcome`): the fee at the fresh
Combine's size, a tick on a stop or a breakeven, none at a target, two on the flatten, over the stop.

**The campaign** (D-492 (3)): FV3-C's exported policy `state_dp_e-0.050_lamstar` (not re-solved) and FV3-C's protocol
verbatim -- `portfolio_stage.run_campaign`'s engine call under `config/fv3_corrected_portfolio.yaml`, as
`zero_edge_decomposition.run_fv3c` applies it -- EXCEPT the day capacity, raised to a cell's busiest day where FV3-C's five
is too few (D-469), and the bounds: each R's one-sided 95 % bound over 21-session blocks with P-11's era rule (the lower
era's bounds read when the eras are flagged), not FV3-C's yearly bound. The identity comes first: FV3-C's own trades
through this campaign path, with FV3-C's own yearly bounds, must reproduce the first paths of
`results/fv3_corrected_v1_paths.csv` exactly (point, bound and zero-edge twin), or nothing is screened.

**The screen** (D-492 (4), (6)): 150 paths, seed 20261030 (A1's), each cell's gate rows read as the scoreboard reads them
(the bound arm at 0 % denial, placement off: growth on the required bankroll at p90), ranked among the cells whose offered
R's resolve; beside each cell its A1 gf15b and A2 rows, and the share of payouts exposed to tier-3 denial, the break-even
denial and Combine purchases in any 21 days. Writes `results/atlas_screen_a3.csv` (exploratory), each cell a variant under
`D-492:atlas_A3`.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/atlas_screen.py"
FAMILY = "A3"
PLAN = "v12_exact"
RESULT = "atlas_screen_a3"
CUT = 870                                   # 07:30 CT on the trading-day clock (atlas_cells.CUT)
KIND_CODE = {0: "s", 1: "t", 2: "f", 3: "b"}            # fv3_rung_walk's kinds as the atlas's outcome codes
UNRESOLVED_MAX = 0.05
A2_SCREEN = "atlas_screen_a2.csv"
BESIDE_COLS = ("rank", "trades", "growth_at_bound", "growth_at_point", "required_p90", "resolves")


def config(family: str = FAMILY) -> dict[str, Any]:
    from propedge.research import atlas_walk as AW

    cfg = AW.config(family)
    if str(cfg.get("plan")) != PLAN:
        raise ValueError(f"{family}'s plan is {cfg.get('plan')!r}, not {PLAN!r}")
    return cfg


def rrs(cfg: dict) -> tuple[float, ...]:
    return tuple(float(R) for R in cfg["rungs"]["rr_grid"])


def stops(cfg: dict) -> tuple[int, ...]:
    return tuple(int(S) for S in cfg["rungs"]["stops_ticks"])


def fv3_config(cfg: dict) -> dict:
    import score_fv3_grid as gf

    return gf.config(ROOT / cfg["policy"]["config"])


# ------------------------------------------------------------------------------------------------ the rung rule


def rung_rule_from_map(m: pd.DataFrame, rungs, cap: int) -> tuple[dict[str, int], dict[str, tuple[float, ...]], list[dict]]:
    """D-492 (2) on step 0's map rows: ({hour: the rung's stop ticks}, {hour: the R offered there}, the rule's rows). Per
    hour the widest rung (at most `cap`) whose 1:1 row is eligible; every R eligible at that hour and rung offered."""
    mp = m[m["section"].astype(str) == "map"].copy()
    mp["stop_ticks"] = pd.to_numeric(mp["stop_ticks"]).astype(int)
    mp["rr"] = pd.to_numeric(mp["rr"]).astype(float)
    mp["ok"] = mp["eligible"].astype(str).str.lower().eq("true")
    allowed = sorted(int(S) for S in rungs if int(S) <= int(cap))
    rung, offered, rows = {}, {}, []
    for hour in mp["hour"].astype(str).drop_duplicates():
        h = mp[mp["hour"].astype(str) == hour]
        ok1 = {S: bool(h[(h["stop_ticks"] == S) & np.isclose(h["rr"], 1.0)]["ok"].any()) for S in allowed}
        rr_ok = [S for S in allowed if ok1[S]]
        row = {"section": "rung", "hour": hour, **{f"eligible_1r_{S}": ok1[S] for S in allowed}}
        if not rr_ok:
            rows.append({**row, "stop_ticks": np.nan, "stop_points": np.nan, "offered": "", "traded": False})
            continue
        S = max(rr_ok)
        offs = tuple(sorted(float(R) for R in h[(h["stop_ticks"] == S) & h["ok"]]["rr"]))
        rung[hour], offered[hour] = S, offs
        rows.append({**row, "stop_ticks": S, "stop_points": S / 4.0, "offered": ",".join(f"{R:g}" for R in offs),
                     "traded": True})
    return rung, offered, rows


def rung_rule(cfg: dict, rd: Path | None = None):
    """The rung rule from the pinned step-0 file (read through its manifest; a different file REFUSED)."""
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result, sha256_of

    rd = Path(rd) if rd is not None else RESULTS_DIR
    path = rd / Path(cfg["rung_map"]["file"]).name
    have = sha256_of(path)
    if have != str(cfg["rung_map"]["sha256"]):
        raise ValueError(f"REFUSED: {path.name} is not step 0's file (sha256 {have} != {cfg['rung_map']['sha256']})")
    return rung_rule_from_map(read_result(path), stops(cfg), int(cfg["rungs"]["cap_ticks"]))


# ------------------------------------------------------------------------------------------------ the rung walk


def pool_minutes(events: pd.DataFrame, days: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Every distinct event minute of A1's sixteen patterns (the clock's included) on the 'n' and 'b' days, a 'b' day's
    events before the cut dropped (`a3_resolution_map.pool_events`' rule): date, slot, day_kind."""
    import a3_resolution_map as m0

    _, with_clock = m0.pool_events(events, days, cfg)
    out = with_clock.drop_duplicates(["date", "slot"])[["date", "slot", "day_kind"]]
    return out.sort_values(["date", "slot"], kind="stable").reset_index(drop=True)


def walk_columns(rungs, rr_grid) -> list[str]:
    cols = []
    for S in rungs:
        for R in rr_grid:
            cols += [f"k{S}_{R:g}", f"x{S}_{R:g}", f"a{S}_{R:g}", f"g{S}_{R:g}"]
    return cols


def walk_minutes(minutes: pd.DataFrame, arrays: Callable[[str], tuple], delay: int, tick: float, rungs,
                 rr_grid) -> pd.DataFrame:
    """Each minute walked long and short `delay` bars late by `fv3_rung_walk` on the rungs at every R: one row a
    (date, slot, side) with `delay`, `entry_slot` and per (stop S, R) the kind `k`, exit bar `x`, MAE `a` and gross `g`
    in ticks."""
    from propedge.research import fv3_rung_walk as RW

    bl = RW.brackets(tuple(int(S) for S in rungs), tuple(float(R) for R in rr_grid))
    cols = walk_columns(rungs, rr_grid)
    parts = []
    for day, g in minutes.groupby("date", sort=True):
        o, h, l, c = arrays(str(day))
        ent, res = RW.day_walks(o, h, l, c, g["slot"].astype(int).tolist(), int(delay), float(tick), bl)
        if not ent:
            continue
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


def walk_inputs(cfg: dict, a1_inputs: dict) -> dict[str, Any]:
    """What A3's cache depends on: A1's cache inputs (bars, A1's config and walk code, its days), the rung walk's code
    and this file's pool and walk functions, the rungs, the R grid, the delay and the tick."""
    from propedge.research import fv3_rung_walk as RW

    code = inspect.getsource(RW) + inspect.getsource(pool_minutes) + inspect.getsource(walk_minutes)
    return {"a1_cache": dict(a1_inputs), "rung_walk_sha256": hashlib.sha256(code.encode("utf-8")).hexdigest(),
            "stops_ticks": list(stops(cfg)), "rr_grid": list(rrs(cfg)), "delay": int(cfg["screen_delay_min"]),
            "tick": float(cfg["contract"]["tick"])}


def cache_dir() -> Path:
    from propedge.research import atlas_walk as AW

    return AW.CACHE / FAMILY


def bar_arrays(cfg: dict, dates: list[str]) -> Callable[[str], tuple]:
    """The development bars for `dates` (the window guard first), one day's arrays on demand."""
    from propedge.data.bars import read_bars
    from propedge.research import atlas_local

    bars = read_bars(cfg["market"], min(dates), max(dates), "development", what="A3 rung walk (D-492)")
    by_day = {d: g for d, g in bars.groupby("day", sort=False)}

    def arrays(day: str):
        return tuple(np.array([np.nan if x is None else x for x in v], dtype=float)
                     for v in atlas_local.day_arrays(by_day.get(day, bars.iloc[0:0])))
    return arrays


def cached_walk(cfg: dict, events: pd.DataFrame, days: pd.DataFrame, a1_inputs: dict, *,
                arrays: Callable[[str], tuple] | None = None, rebuild: bool = False, write: bool = True,
                cache: Path | None = None) -> pd.DataFrame:
    """A3's rung walk: from `data/atlas/A3` when its manifest's inputs are today's, else walked (the bars read through
    `bar_arrays` unless `arrays` is given) and cached; `write=False` refuses instead of walking (a screen worker)."""
    d = Path(cache) if cache is not None else cache_dir()
    want = walk_inputs(cfg, a1_inputs)
    man = d / "manifest.json"
    if not rebuild and man.is_file() and json.loads(man.read_text(encoding="utf-8")).get("inputs") == want:
        return pd.read_parquet(d / "walks.parquet")
    if not write:
        raise RuntimeError(f"REFUSED: A3's rung walk at {d} is missing or stale; build it first (--walk)")
    mins = pool_minutes(events, days, cfg)
    arr = arrays if arrays is not None else bar_arrays(cfg, sorted(mins["date"].astype(str).unique()))
    w = walk_minutes(mins, arr, int(cfg["screen_delay_min"]), float(cfg["contract"]["tick"]), stops(cfg), rrs(cfg))
    d.mkdir(parents=True, exist_ok=True)
    w.to_parquet(d / "walks.parquet", index=False)
    man.write_text(json.dumps({"inputs": want, "rows": {"minutes": int(len(mins)), "walks": int(len(w))},
                               "written": date.today().isoformat()}, indent=1) + "\n", encoding="utf-8")
    return w


# ------------------------------------------------------------------------------------------------ the cell's trades


def fee_by_stop(fcfg: dict, rungs, tick_value: float) -> dict[int, float]:
    """The fee a micro-equivalent pays at each rung's stop, at the fresh Combine's size (FV3-C's `fee_micro_eq`,
    `Signals3.fee` at `leg_spec(cfg, 'combine')`), the assumed fill model's MNQ and NQ round turns."""
    import score_fv3_grid as gf
    from orb5_exploratory import mini_mix_fee

    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel

    q, fm = params("NQ"), FillModel.load("assumed")
    _, _, risk, cap = gf.leg_spec(fcfg, "combine")
    return {int(S): float(mini_mix_fee(np.array([float(S)]), risk, cap, tick_value,
                                       float(fm.round_turn_by_instrument[q["micro"]]),
                                       float(fm.round_turn_by_instrument["NQ"]))[0]) for S in rungs}


def cell_trades(events: pd.DataFrame, walks: pd.DataFrame, days: pd.DataFrame, pid: int, rule: str,
                rung: dict[str, int], offered: dict[str, tuple[float, ...]], fees: dict[int, float], *,
                rr_grid, fresh_rr: float, tick_value: float, entry_ticks: float) -> pd.DataFrame:
    """One cell's trades in FV3-C's gate-trades shape: its events (`atlas_cells.cell_walks`: the pattern, the side rule,
    the clock's coin) at the rung its hour takes, every R offered there settled as FV3 settles it."""
    import atlas_cells as ac
    from propedge.research.fv3_rung_walk import EXIT_TICKS

    w = ac.cell_walks(events, walks, days, pid, rule)
    w = w[w["decision_ct"].astype(str).isin(rung)]
    w = w[~((w["day_kind"].astype(str) == "b") & (w["decision_slot_minutes"].astype(int) < CUT))]
    if w.empty:
        return pd.DataFrame()
    w = w.reset_index(drop=True)
    hours = w["decision_ct"].astype(str)
    S = hours.map(rung).astype(int).to_numpy()
    t = pd.DataFrame({"date": w["date"].astype(str), "year": w["year"].astype(int), "decision_ct": hours,
                      "day_kind": w["day_kind"].astype(str), "decision_slot_minutes": w["decision_slot_minutes"].astype(int),
                      "S": S, "stop_ticks": S.astype(float), "entry_t": w["entry_slot"].astype(float),
                      "side": np.where(w["side"].astype(int) > 0, "long", "short")})
    fee = np.array([fees[int(s)] for s in S])
    t["fee_micro_eq"] = fee
    td = float(tick_value)
    exit_ticks = np.vectorize(lambda k: float(EXIT_TICKS[int(k)]), otypes=[float])
    for R in rr_grid:
        off = np.array([float(R) in offered[h] for h in hours])
        pick = lambda p: np.select([S == s for s in sorted(set(S))],                            # noqa: E731
                                   [w[f"{p}{s}_{R:g}"].to_numpy() for s in sorted(set(S))])
        kind, ex, mae, gt = pick("k").astype(int), pick("x").astype(float), pick("a").astype(float), pick("g").astype(float)
        gross = gt / S
        cost = (float(entry_ticks) * td + fee + exit_ticks(kind) * td) / (S * td)
        t[f"r_{R:g}"] = np.where(off, gross - cost, np.nan)
        t[f"g_{R:g}"] = np.where(off, gross, np.nan)
        t[f"c_{R:g}"] = np.where(off, cost, np.nan)
        t[f"mae_{R:g}"] = np.where(off, mae / S, np.nan)
        t[f"exit_t_{R:g}"] = np.where(off, ex, np.nan)
        t[f"o_{R:g}"] = np.where(off, [KIND_CODE[int(k)] for k in kind], "")
    xs = t[[f"exit_t_{R:g}" for R in rr_grid]]
    base = f"exit_t_{float(fresh_rr):g}"
    t["exit_t"] = t[base].where(t[base].notna(), xs.max(axis=1)) if base in t else xs.max(axis=1)
    ob = f"o_{float(fresh_rr):g}"
    t["flat"] = (t[ob] == "f") if ob in t else False
    return t.sort_values(["date", "entry_t"], kind="stable").reset_index(drop=True)


def resolution(t: pd.DataFrame, rr_grid) -> tuple[dict, bool]:
    """Each offered R's unresolved share (the 15:10 flatten; a breakeven exit resolved) in the cell's trades, overall
    and in its worst year; whether every offered R resolves (at most 5 % both ways)."""
    res = {}
    for R in rr_grid:
        o = t[f"o_{R:g}"].astype(str)
        m = o != ""
        if m.any():
            f = o[m] == "f"
            res[f"unresolved_{R:g}"] = float(f.mean())
            res[f"unresolved_worst_year_{R:g}"] = float(f.groupby(t.loc[m, "year"]).mean().max())
    return res, all(v <= UNRESOLVED_MAX + 1e-12 for v in res.values())


# ------------------------------------------------------------------------------------------------ the bounds


def bounds(t: pd.DataFrame, days: list[str], keys, cfg: dict) -> tuple[dict, dict, dict, list[dict], bool]:
    """(the pooled statistics, e by R, the bound read by R, the era rows, flagged) -- P-11's convention: each R's
    one-sided 95 % bound over 21-session blocks, the lower era's when the whole-year bootstrap flags the eras
    (`t24_gf15.eras`); an R offered in only one era keeps its pooled bound (no era to compare, its row says so), an R
    offered nowhere has e = lb = 0 (nothing to shift)."""
    import confirm_fv3 as cf
    import t24_gf15 as tg

    keys = [float(R) for R in keys]
    b = cfg["bounds"]
    spans = tuple(tuple(int(y) for y in x) for x in b["eras"])
    st = cf.edge_stats(t, keys, days, int(b["block_days"]), None)
    yr = t["year"].astype(int)
    both = [R for R in keys if all(((yr >= lo) & (yr <= hi) & t[f"g_{R:g}"].notna()).any() for lo, hi in spans)]
    era_rows, flagged, low = [], False, {}
    if both:
        era_rows, flagged, low, _ = tg.eras(t, days, both, 1, seed=int(b["era_seed"]), era_spans=spans)
    era_rows += [{"section": "eras", "rr": R, "offered": int(st[R]["n"]), "flagged": False,
                  "note": "offered in at most one era: its pooled bound read"} for R in keys if R not in both]
    e_by, lb_by = {}, {}
    for R in keys:
        if int(st[R]["n"]) == 0:
            e_by[R], lb_by[R] = 0.0, 0.0
            continue
        e_by[R] = float(st[R]["e"])
        lb_by[R] = float(low[R]) if (flagged and R in low) else float(st[R]["lb"])
    return st, e_by, lb_by, era_rows, bool(flagged)


# ------------------------------------------------------------------------------------------------ the plan and campaign


def policy(cfg: dict, fcfg: dict):
    """FV3-C's exported v12 policy at its own cell (`cfg['policy']['id']`), read from FV3-C's own policy file."""
    from propedge.campaign.risk_policy import RiskPolicy

    if str(cfg["policy"]["policies_json"]) != str(fcfg["state_policy"]["policies_json"]):
        raise ValueError("REFUSED: A3's policy file is not FV3-C's")
    pols = json.loads((ROOT / cfg["policy"]["policies_json"]).read_text(encoding="utf-8"))
    pid = str(cfg["policy"]["id"])
    if pid not in pols:
        raise ValueError(f"REFUSED: no exported policy {pid}")
    p = RiskPolicy.from_dict(pols[pid])
    p.validate()
    return p


def run_campaign(blocks, fcfg: dict, tick_value: float, pol, e_by: dict, lb_by: dict, hook, *, seed: int, n_paths: int,
                 horizon: int, capacity: int | None = None, levels=(0.0,), rtp: bool = False,
                 one_at_a_time: float | None = None, focused_trader: Any = None,
                 purchase_budget: tuple[int, int] | None = None) -> pd.DataFrame:
    """FV3-C's engine call (`portfolio_stage.run_campaign` under FV3-C's config, every switch from it) with one change
    D-492 (3) declares: the protocol's day capacity raised to `capacity` where FV3-C's five is too few (D-469). With
    `capacity` at or below five it is that call exactly (the identity checks it). `rtp` -- the placement on, beside a
    verdict (D-289; `portfolio_stage.run_campaign`'s own switch) -- is False in the screen and in every gate arm; A3-BRK30's
    registered run (`scripts/a3_brk30.py`) sets it for its placement-on reading only. `one_at_a_time` -- the operator's
    strict rule (R2, D-409; `gate.run_gate`'s D-429 switch: no trade while any account holds a position or within that
    many minutes of one closing) -- is None (off) in the screen and the identity, exactly FV3-C's call; A3-BRK30's
    registered run sets it to five minutes on every deciding arm, as P-11 and P-12 ran (the operator's rule, D-496).
    `focused_trader` -- a `lockstep.FocusedTraderModel`, Topstep's Focused Trader Program at a declared threshold and
    path (`gate.run_gate`'s D-497 switch; beside a verdict, never the gate: its rows are never gate rows) -- is None
    (off, not passed to the engine) in the screen and the identity, exactly FV3-C's call; A3-BRK30's registered run sets
    it for its program reading only (section `ftp`, D-499). `purchase_budget` -- `(K, window_days)`, the campaign's own
    restraint on Combine purchases and resets (`gate.run_gate`'s D-501 switch) -- is None (off, not passed) everywhere
    but D-501's compliance study (`scripts/a3_compliance.py`)."""
    from propedge.campaign import gate

    kw = gate_kwargs(blocks, fcfg, tick_value, pol, e_by, lb_by, hook, seed=seed, n_paths=n_paths, horizon=horizon,
                     capacity=capacity, levels=levels, rtp=rtp, one_at_a_time=one_at_a_time,
                     focused_trader=focused_trader, purchase_budget=purchase_budget)
    df, _ = gate.run_gate(kw.pop("blocks"), **kw)
    df["placement"] = "on" if rtp else "off"
    return df


def gate_kwargs(blocks, fcfg: dict, tick_value: float, pol, e_by: dict, lb_by: dict, hook, *, seed: int, n_paths: int,
                horizon: int, capacity: int | None = None, levels=(0.0,), rtp: bool = False,
                one_at_a_time: float | None = None, focused_trader: Any = None,
                purchase_budget: tuple[int, int] | None = None, wallet_stop: float | None = None,
                pause_after_funded: int | None = None, seat_ramp: int | None = None) -> dict[str, Any]:
    """`run_campaign`'s `gate.run_gate` arguments, every one as it passes them (a switch that is off is not passed), so
    a caller may hand the same campaign to `gate.ftp_sweep` (D-501). `wallet_stop`, `pause_after_funded` and
    `seat_ramp` are D-630's entry options (`gate.run_gate`'s), each None (off, not passed) for every caller on record."""
    from dataclasses import replace

    import portfolio_stage as ps
    import score_fv3_grid as gf

    from propedge.campaign.payout_method import rules_for_method

    camp, f = fcfg["gate"]["campaign"], gf.fidelity_of(fcfg)
    fr = float(fcfg["state_policy"]["fresh"]["funded_rr"])
    proto = ps.protocol_of(fcfg)
    if capacity is not None and int(capacity) > int(proto.trades_per_day):
        proto = replace(proto, trades_per_day=int(capacity))
    return dict(
        blocks=list(blocks), e=e_by[fr], lb=lb_by[fr], protocol=proto, bankroll=gf.bankroll_of(fcfg),
        horizon_days=int(horizon), n_paths=int(n_paths), seed=int(seed), accounts=int(camp["accounts"]),
        sizing=gf.sizing_rule(fcfg, tick_value), rules=rules_for_method(camp["payout_method"]), mode=camp["mode"],
        settlement=camp["settlement"], combines=int(camp["combines"]), total_accounts=int(camp["accounts"]),
        risk_policy=pol, e_by_rr=e_by, lb_by_rr=lb_by, levels=tuple(levels), path_hook=hook, rtp=bool(rtp),
        routing=f["routing"], cross_account=bool(f.get("cross_account_rule", False)), flip=gf.flip_spec_of(fcfg),
        hold_to_own_exit=bool(f.get("hold_to_own_exit", False)),
        **({} if one_at_a_time is None else {"one_at_a_time": float(one_at_a_time)}),    # off: FV3-C's call exactly
        **({} if focused_trader is None else {"focused_trader": focused_trader}),        # D-497: off, not passed
        **({} if purchase_budget is None else {"purchase_budget": purchase_budget}),     # D-501: off, not passed
        **({} if wallet_stop is None else {"wallet_stop": wallet_stop}),                 # D-630: off, not passed
        **({} if pause_after_funded is None else {"pause_after_funded": pause_after_funded}),
        **({} if seat_ramp is None else {"seat_ramp": seat_ramp}))


def campaign(t: pd.DataFrame, days: list[str], tick_value: float, keys, e_by: dict, lb_by: dict, pol, fcfg: dict, *,
             seed: int, n_paths: int, horizon: int, hook, inner=None, label: str = "", twin: bool = False,
             capacity: int | None = None) -> dict[str, pd.Series]:
    """A trade set's gate rows on A3's path: the point and bound arms in one engine call ({'point', 'bound'}), and with
    `twin` the zero-edge twin (every R shifted to a zero mean, `portfolio_stage.zero_edge_blocks`) in a second. The
    capacity is the trades' busiest day unless given."""
    import portfolio_stage as ps
    import score_fv3_grid as gf

    keys = [float(R) for R in keys]
    blocks, n_used = gf.gate_blocks(t, days, tick_value, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise RuntimeError("the blocks hold a different number of trades")
    cap = int(t.groupby("date").size().max()) if capacity is None and len(t) else capacity
    fr = float(fcfg["state_policy"]["fresh"]["funded_rr"])
    ps._label(inner, f"{label} gate")
    g = run_campaign(blocks, fcfg, tick_value, pol, e_by, lb_by, hook, seed=seed, n_paths=n_paths, horizon=horizon,
                     capacity=cap)
    out = {"point": g[g["shift"] == "point"].iloc[0], "bound": g[g["shift"] == "lower_bound"].iloc[0], "frame": g}
    if twin:
        zero = {k: 0.0 for k in e_by}
        ps._label(inner, f"{label} twin")
        z = run_campaign(ps.zero_edge_blocks(blocks, e_by, fr), fcfg, tick_value, pol, zero, zero, hook, seed=seed,
                         n_paths=n_paths, horizon=horizon, capacity=cap)
        out["twin"] = z[z["shift"] == "point"].iloc[0]
    return out


# ------------------------------------------------------------------------------------------------ the identity


def identity(cfg: dict, rd: Path | None = None, n_paths: int | None = None) -> tuple[list[str], dict]:
    """FV3-C's own development trades through `campaign` with FV3-C's own yearly bounds, FV3-C's gate seed and the
    policy A3 carries: the first `n_paths` of point, bound and twin must equal `results/fv3_corrected_v1_paths.csv`'s
    (zero_edge_decomposition's cell a). (the problems, empty when it holds; its record)."""
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    rd = Path(rd) if rd is not None else RESULTS_DIR
    n = int(cfg["identity"]["paths"] if n_paths is None else n_paths)
    seed = int(cfg["identity"]["seed"])
    fcfg = fv3_config(cfg)
    pol = policy(cfg, fcfg)
    pid = zd.fv3_cell(rd)
    if pid != pol.id:
        return [f"FV3-C's development run used {pid}, A3 carries {pol.id}"], {}
    t, days, tv = zd.fv3_trades(rd)
    t = zd.pad(t, sorted(set(zd.rr_keys(t)) | set(zd.policy_rrs(pol))))
    keys = zd.rr_keys(t)
    st = zd.stats_of(t, days, keys, "yearly")
    sink: list[dict] = []
    hook, inner = zd.hook_for(sink)
    campaign(t, days, tv, keys, {k: v["e"] for k, v in st.items()}, {k: v["lb"] for k, v in st.items()}, pol, fcfg,
             seed=seed, n_paths=n, horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), hook=hook, inner=inner,
             label="a", twin=True)
    bad = zd.path_problems(sink, read_result(rd / f"{zd.FV3_RUN}_paths.csv"), zd.FV3_PAIRS, n)
    return bad, {"section": "identity", "check": f"FV3-C's trades on A3's campaign path, its yearly bounds, seed {seed}: "
                 f"the first {n} paths (point, bound, twin) equal {zd.FV3_RUN}_paths.csv's",
                 "compared": ",".join(zd.PATH_COLS), "paths": n, "trades": int(len(t)), "policy_id": pol.id,
                 "holds": not bad}


# ------------------------------------------------------------------------------------------------ the screen


_LOADED: dict = {}


TICK_VALUE = 0.5                            # MNQ: a quarter point at $2 a point (FV3-C's tick value, `_rebuild`'s)


def load_inputs(family: str = FAMILY, *, write_walk: bool = False) -> dict[str, Any]:
    """Everything a cell reads: the config, A1's events and days (A1's cache read only and checked,
    `a3_resolution_map.load_a1`) and its inputs, A3's walk (from its cache; built only with `write_walk`), the rung rule
    and its rows, FV3-C's config, the policy, the fees and the tick value."""
    import a3_resolution_map as m0

    cfg = config(family)
    _, events, days, a1_inputs = m0.load_a1()
    walks = cached_walk(cfg, events, days, a1_inputs, write=write_walk)
    rung, offered, rows = rung_rule(cfg)
    fcfg = fv3_config(cfg)
    return {"cfg": cfg, "events": events, "days": days, "a1_inputs": a1_inputs, "walks": walks, "rung": rung,
            "offered": offered, "rung_rows": rows, "fcfg": fcfg, "policy": policy(cfg, fcfg),
            "fees": fee_by_stop(fcfg, stops(cfg), TICK_VALUE), "tv": TICK_VALUE}


def _loaded(family: str):
    if family not in _LOADED:
        _LOADED[family] = load_inputs(family)
    return _LOADED[family]


def gate_reading(rows: dict[str, pd.Series]) -> dict[str, float]:
    """The scoreboard's columns from a cell's gate rows (the bound arm at 0 % denial, placement off; the point beside)."""
    g, p = rows["bound"], rows["point"]
    num = lambda r, c: float(r[c]) if c in r.index and pd.notna(r[c]) else float("nan")             # noqa: E731
    return {"growth_at_bound": num(g, "pf_growth_on_base_p50"), "growth_at_point": num(p, "pf_growth_on_base_p50"),
            "required_p90": num(g, "pf_required_p90"), "required_p50": num(g, "pf_required_p50"),
            "break_even_denial": num(g, "pf_break_even_denial_p50"),
            "share_payouts_exposed": num(g, "share_payouts_exposed"),
            "max_combine_purchases_21d": num(g, "mean_max_combine_purchases_21d"),
            "mean_combine_purchases": num(g, "mean_combine_purchases"),
            "days_to_first_payout": num(g, "median_days_to_first_payout"),
            "payouts_per_month": num(g, "st_payouts_per_month_p50"),
            "median_payouts_per_path": num(g, "median_payouts_per_path"),
            "realised_to_intended_capped_risk": num(g, "realised_to_intended_capped_risk"),
            "share_trades_skipped_opposite": num(g, "share_trades_skipped_opposite"),
            "share_trades_unsized": num(g, "share_trades_unsized")}


def run_cell(t: pd.DataFrame, day_set: list[str], cfg: dict, fcfg: dict, pol, tv: float, *, n_paths: int, seed: int
             ) -> tuple[pd.DataFrame, dict]:
    """One cell's campaign on A3's path at A3's bounds: (its rows -- the gate rows, the edge rows, the era rows -- and
    its screen reading)."""
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import zero_edge_decomposition as zd

    keys = list(rrs(cfg))
    t = zd.pad(t, sorted(set(keys) | set(zd.policy_rrs(pol))))
    keys = zd.rr_keys(t)
    st, e_by, lb_by, era_rows, flagged = bounds(t, day_set, keys, cfg)
    pcfg = fcfg["portfolio"]
    hook = lt.lever_hook(ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])}))
    busiest = int(t.groupby("date").size().max())
    rows = campaign(t, day_set, tv, keys, e_by, lb_by, pol, fcfg, seed=seed, n_paths=n_paths,
                    horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), hook=hook, capacity=busiest)
    edge = [{"section": "edge", "rr": R, "e": st[R]["e"], "lb_pooled": st[R]["lb"], "lb_read": lb_by[R],
             "n": int(st[R]["n"]), "blocks": int(st[R]["blocks"])} for R in keys]
    df = pd.concat([rows["frame"].assign(section="campaign"), pd.DataFrame(edge), pd.DataFrame(era_rows)],
                   ignore_index=True)
    fr = float(fcfg["state_policy"]["fresh"]["funded_rr"])
    reading = {**gate_reading(rows), "busiest_day": busiest,
               "capacity": max(busiest, int(ps.protocol_of(fcfg).trades_per_day)), "era_flagged": flagged,
               "bounds_read": "the lower era's" if flagged else "pooled", "lb_funded_fresh": lb_by[fr],
               "lowest_offered_lb": float(min(v for R, v in lb_by.items() if st[R]["n"] > 0))
               if any(st[R]["n"] > 0 for R in keys) else float("nan"), "policy_id": pol.id}
    return df, reading


def _job(args) -> dict:
    """One cell in a worker: (family, pattern id, name, side rule)."""
    family, pid, name, rule = args
    try:
        L = _loaded(family)
        cfg, days, fcfg, pol, tv = L["cfg"], L["days"], L["fcfg"], L["policy"], L["tv"]
        t = cell_trades(L["events"], L["walks"], days, pid, rule, L["rung"], L["offered"], L["fees"], rr_grid=rrs(cfg),
                        fresh_rr=float(fcfg["state_policy"]["fresh"]["combine_rr"]), tick_value=tv,
                        entry_ticks=float(cfg["slip_ticks"]))
        day_set = sorted(days["date"].astype(str))
        if t.empty:
            return {"pid": pid, "name": name, "rule": rule, "rows": [], "screen": {"trades": 0, "refused": "no trade"}}
        res, resolves = resolution(t, rrs(cfg))
        df, reading = run_cell(t, day_set, cfg, fcfg, pol, tv, n_paths=int(cfg["screen"]["paths"]),
                               seed=int(cfg["screen"]["seed"]))
        hours = t.groupby("decision_ct").size()
        screen = {"trades": int(len(t)), "trades_per_day": len(t) / max(len(day_set), 1),
                  "hours_traded": int(len(hours)), "share_rung_50": float((t["S"] == 50).mean()),
                  **reading, "resolves": resolves, **res}
        return {"pid": pid, "name": name, "rule": rule, "rows": [], "campaign": df, "screen": screen}
    except BaseException:                                            # noqa: B036 -- returned, never lost
        import traceback
        return {"pid": pid, "name": name, "rule": rule, "error": traceback.format_exc()}


def rank_screen(s: pd.DataFrame) -> pd.DataFrame:
    """D-492 (4): the cells whose offered R's resolve and that carry a growth reading, by growth on the required
    bankroll at the bound, highest first; the rest follow unranked with the reason."""
    s = s.copy()
    resolves = (s["resolves"] if "resolves" in s else pd.Series(False, index=s.index)).fillna(False).astype(bool)
    growth = pd.to_numeric(s["growth_at_bound"] if "growth_at_bound" in s else pd.Series(np.nan, index=s.index),
                           errors="coerce")
    trades = pd.to_numeric(s["trades"], errors="coerce").fillna(0)
    ok = resolves & growth.notna() & (trades > 0)
    why = np.select([trades <= 0, ~resolves, growth.isna()],
                    ["no trade", "an offered R does not resolve", "no growth reading"], default="")
    s["unranked_reason"] = np.where(ok, None, why)
    s["_ok"], s["_g"] = ok, growth
    s = s.sort_values(["_ok", "_g"], ascending=[False, False], na_position="last", kind="stable")
    s.insert(1, "rank", [float(i + 1) if o else np.nan for i, o in enumerate(s["_ok"])])
    return s.drop(columns=["_ok", "_g"])


def beside(results_dir: Path | None = None) -> tuple[pd.DataFrame, dict[str, str]]:
    """Each cell's A1 gf15b row (`atlas_cells.beside`, A1's rescreen) and A2 row (`results/atlas_screen_a2.csv`), read
    through their manifests: (the rows by pattern and rule, prefixed a1_ and a2_; the files)."""
    import atlas_cells as ac

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    b1 = ac.beside(FAMILY, results_dir=rd)
    if b1 is None or b1[0] != "A1":
        raise ValueError("A3 reads A1's events: its beside rows are A1's")
    a2 = read_result(rd / A2_SCREEN)
    a2 = a2[a2["section"] == "screen"][["pattern", "rule", *BESIDE_COLS]].reset_index(drop=True)
    if a2.duplicated(["pattern", "rule"]).any():
        raise ValueError(f"{A2_SCREEN}: a cell appears twice in its screen rows")
    a2 = a2.rename(columns={c: f"a2_{c}" for c in BESIDE_COLS})
    out = b1[2].merge(a2, on=["pattern", "rule"], how="outer", validate="one_to_one")
    return out, {"a1": f"results/{b1[1].name}", "a2": f"results/{A2_SCREEN}"}


def free_gb() -> float:
    import atlas_cells as ac

    return ac.free_gb()


#: GB a worker needs. Measured on toys (2026-10-30, D-492's build; synthetic trades only, never a cell; one BLAS thread):
#: `run_cell` -- the bounds and one campaign under FV3-C's protocol and v12 policy at 150 paths x 504 sessions over
#: 1,691 days -- peaked at 0.62 GB of private memory with 10 trades a day (16,870 trades, busiest day 21) and 1.07 GB
#: with 48 a day (81,473 trades, busiest day 75: brk15's density in A1's rescreen), against 0.06 GB for the interpreter;
#: about 65 to 95 s each. A worker also holds A1's events and A3's rung walk (about 0.3 GB at the real walk's size,
#: estimated from its 96 columns), so WORKER_PEAK_GB; WORKER_GB rounds it up to A1's fixed-plan worker's 2 GB.
WORKER_PEAK_GB = 1.4
WORKER_GB = 2.0


def workers(avail: float | None = None) -> int:
    """Memory-guarded: one worker per WORKER_GB of free memory, at most four, at least one; ATLAS_WORKERS overrides
    (still at most four)."""
    avail = free_gb() if avail is None else float(avail)
    return int(max(1, min(4, os.environ.get("ATLAS_WORKERS") and int(os.environ["ATLAS_WORKERS"])
                          or avail // WORKER_GB)))


def build_walk(family: str = FAMILY) -> int:
    """`--walk`: A1's cache checked, A3's rung walk built (or confirmed current) under data/atlas/A3."""
    import a3_resolution_map as m0

    cfg = config(family)
    _, events, days, a1_inputs = m0.load_a1()
    w = cached_walk(cfg, events, days, a1_inputs, write=True)
    print(f"A3's rung walk: {len(w)} walks on {w['date'].nunique() if len(w) else 0} days at {cache_dir()}")
    return 0


def screen(family: str = FAMILY, *, results_dir: Path | None = None) -> int:
    import atlas_cells as ac
    import time

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    for var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(var, "1")          # D-464 (5): the workers inherit it
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if (rd / f"{RESULT}.csv").exists():
        print(f"REFUSED: {RESULT}.csv exists -- the screen is read once.")
        return 3
    cfg = config(family)
    print(f"the identity: FV3-C's trades on A3's campaign path, {cfg['identity']['paths']} paths...", flush=True)
    bad, ident = identity(cfg, rd)
    if bad:
        print("REFUSED (identity): " + "; ".join(bad[:8]))
        return 3
    print("  HOLDS", flush=True)
    L = load_inputs(family, write_walk=True)                 # A3's walk built here, once, before any worker reads it
    _LOADED[family] = L
    walks, rung, offered, pol, fees = L["walks"], L["rung"], L["offered"], L["policy"], L["fees"]
    bes, bes_files = beside(rd)
    jobs = [(family, pid, name, rule) for pid, name, rule in ac.cells(cfg)]
    n = workers()
    print(f"{len(jobs)} cells on {n} worker(s) ({free_gb():.1f} GB free, {WORKER_GB:g} GB a worker); "
          f"{len(walks)} rung walks", flush=True)
    t0, outs = time.time(), []

    def progress(o: dict) -> None:
        sc = o.get("screen") or {}
        tail = "error" if "error" in o else (f"growth at bound {sc['growth_at_bound']:+.4f}" if "growth_at_bound" in sc
                                              else str(sc.get("refused", "")))
        print(f"[{len(outs)}/{len(jobs)} {time.time() - t0:7.0f}s] {o['name']} {o['rule']}: {tail}", flush=True)

    if n > 1:
        from multiprocessing import Pool
        with Pool(n) as pool:
            for o in pool.imap_unordered(_job, jobs):
                outs.append(o)
                progress(o)
    else:
        for j in jobs:
            outs.append(_job(j))
            progress(outs[-1])
    errors = [o for o in outs if "error" in o]
    for o in errors:
        print(f"ERROR at {o['name']} {o['rule']}:\n{o['error']}", flush=True)
    frames, scr = [], []
    vc = VariantCounter(path=rd / "variants.jsonl")
    label = f"{cfg['decision']}:atlas_{family}"
    for o in sorted((o for o in outs if "error" not in o), key=lambda x: (x["pid"], x["rule"])):
        tag = {"pattern": o["name"], "pattern_id": o["pid"], "rule": o["rule"]}
        scr.append({"section": "screen", **tag, **o["screen"]})
        if "campaign" in o:
            frames.append(o["campaign"].assign(**tag))
        vc.record(prereg_id=label, seed=int(cfg["screen"]["seed"]), exploratory=True,
                  params={"study": f"atlas {family} screen", **tag}, label=f"atlas {family} {o['name']} {o['rule']}")
    s = rank_screen(pd.DataFrame(scr)).merge(bes, on=["pattern", "rule"], how="left", validate="one_to_one")
    out = pd.concat([s, pd.DataFrame(L["rung_rows"]), pd.DataFrame([ident]), *frames], ignore_index=True)
    parameters = {"family": family, "decision": cfg["decision"], "config": f"config/atlas_{family.lower()}.yaml",
                  "cells": len(jobs), "paths": int(cfg["screen"]["paths"]), "seed": int(cfg["screen"]["seed"]),
                  "plan": PLAN, "policy_id": pol.id, "policies_json": cfg["policy"]["policies_json"],
                  "protocol": "FV3-C's verbatim (config/fv3_corrected_portfolio.yaml, portfolio_stage.run_campaign's "
                              "engine call) except the day capacity raised to a cell's busiest day (D-469) and the "
                              "bounds (21-session blocks with P-11's era rule)",
                  "bounds": cfg["bounds"], "rungs": cfg["rungs"], "rung_map": cfg["rung_map"],
                  "rung_rule": {h: {"stop_ticks": rung[h], "offered": list(offered[h])} for h in rung},
                  "costs": cfg["costs"], "day_set": cfg["day_set"], "walk_family": "A1",
                  "walk_cache_inputs": walk_inputs(cfg, L["a1_inputs"]),
                  "fees_micro_eq": {str(k): v for k, v in fees.items()}, "identity": ident, "beside": bes_files,
                  "errors": len(errors), "ranked": int(s["rank"].notna().sum()), "variant_label": label}
    write_result(out, RESULT, script=SCRIPT, seed=int(cfg["screen"]["seed"]), exploratory=True, results_dir=results_dir,
                 parameters=parameters,
                 description=f"Signal atlas {family}'s screen ({cfg['decision']}): family A1's 31 cells walked on "
                             "FV3-C's 12.5 and 25-point rungs (FV3's breakeven, MAE and flatten; the rung per hour by "
                             "step 0's 1:1 map), sized by FV3-C's exported v12 policy under FV3-C's protocol (the day "
                             "capacity raised to a cell's busiest day, the bounds over 21-session blocks with P-11's "
                             "era rule); ranked by growth on the required bankroll at the bound among the cells whose "
                             "offered R's resolve; each cell's A1 gf15b and A2 rows and its tier-3 exposure beside it.",
                 notes={"status": f"EXPLORATORY screen ({cfg['decision']}): it picks the cell for the registered "
                                  "development verdict; never a verdict"})
    show = [c for c in ("rank", "pattern", "rule", "trades_per_day", "growth_at_point", "growth_at_bound",
                        "required_p90", "share_payouts_exposed", "break_even_denial", "max_combine_purchases_21d",
                        "resolves", "a1_growth_at_bound", "a2_growth_at_bound") if c in s]
    pd.set_option("display.width", 250)
    print(s[show].to_string(), flush=True)
    return 4 if errors else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--identity", action="store_true", help="the identity alone; nothing written")
    ap.add_argument("--paths", type=int, default=None)
    a = ap.parse_args(argv)
    if a.identity:
        bad, _ = identity(config(), n_paths=a.paths)
        print("identity " + ("HOLDS" if not bad else "FAILS: " + "; ".join(bad[:8])))
        return 0 if not bad else 3
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
