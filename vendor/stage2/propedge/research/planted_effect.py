"""L5, the planted effect (D-195), and the power curve D-192 reads from it.

**End to end.** Synthetic one-minute sessions for the four markets, with or without a planted trend, go through the
registered chain unchanged: `im2_core.run_day` (the kit's core) -> shaped as `parse_im2` shapes a kit's output ->
`im2_score.entry_table` (costs, treatments) -> `im2_score.edge` (e and the repository's lower bound, D-197) ->
`im2_score.blocks` -> `im2_score.run_gate` (P-04's lifecycle, rotation, MAE settlement). The chain must recover a
planted edge -- the lower bound above zero at R = 1 and 2 and the gate passing -- and must not create one from noise:
on driftless sessions the lower bound stays at or below zero and the gate fails.

**The planted trend.** Each session picks a direction at random and, from its open, adds `drift` of a step to every
minute's move in that direction; a driftless session has none. The noise band then admits entries with the day's move,
and the trend carries them to their targets more often than to their stops. What e that plants is not set exactly --
it is measured, and the check is that the chain finds it, not a value.

**The power curve** (D-192). At a planted edge e and R, trades are brackets -- +R with probability (1 + e) / (1 + R),
else -1, so the mean is e -- spread over days at a declared rate, and scored by `im2_score.edge`, the registered
statistic (the lower of the 20-day moving-block bootstrap and the day-clustered normal bound). Power is the share of
replications whose bound is above zero; at e = 0 it is the false-positive rate. A registration reads the trades it
needs at its own R and effect size from the curve. Binary brackets are the widest outcome a bracket can have at R
(time exits narrow it), so the trades read from the curve are, if anything, too many.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Sequence

import numpy as np
import pandas as pd

from propedge.data.im2_releases import hot_slots
from propedge.data.qc_algorithms import im2_params
from propedge.outcomes import im2_core as core
from propedge.research import im2_score as sc

SEED = 20261202
START = {"ES": 4000.0, "CL": 70.0, "6E": 1.10, "NG": 3.00}
STEP_BP = 4.0                       # a minute's move, about 4 basis points: sd of the synthetic walk
LOOKBACK_WARM = 14                  # sessions before the first that can be decided (P-04: 14 complete past sessions)


def round_turns(cfg: dict | None = None) -> dict[str, float]:
    """{market: its micro's round turn}: `config/fills.yaml`'s published totals, raised to P-04's floors for MCL and
    MNG (`config/model_im2.yaml`) -- the costs the scorer will apply, without waiting for the 2026-10-01 re-read,
    which this synthetic check does not need."""
    import yaml

    from propedge import CONFIG_DIR

    cfg = cfg or sc.config()
    vals = yaml.safe_load((CONFIG_DIR / "fills.yaml").read_text(encoding="utf-8"))["round_turn_by_instrument"]["values"]
    floors = cfg["fee_floor_round_turn"]
    out = {}
    for m, spec in cfg["markets"].items():
        micro = spec["micro"]
        out[m] = max(float(vals[micro]), float(floors.get(micro, 0.0)))
    return out


def synthetic_session(market: str, rng: np.random.Generator, *, drift: float = 0.0, holes: float = 0.0,
                      gap_start: int = 0, level: float | None = None) -> tuple[list, list, list, list, list]:
    """One session of `market` as slot arrays (o, h, l, c, v; None where a minute has no bar), on the standard
    contract's tick: a walk of about `STEP_BP` basis points a minute from `level` (the market's `START` by default),
    with `drift` steps a minute in a direction drawn for the day; the first `gap_start` minutes and a share `holes` of
    the rest have no bar."""
    q = im2_params(market)
    tick, n = q["tick"], q["slots"]
    step = max(1, round(START[market] * STEP_BP / 1e4 / tick))
    px = round((level if level is not None else START[market]) / tick)
    push = drift * step * int(rng.choice([-1, 1]))
    o, h, l, c, v = ([None] * n for _ in range(5))
    carry = 0.0
    for i in range(n):
        op = px
        carry += push
        k = int(carry)
        carry -= k
        px = px + k + int(rng.integers(-step, step + 1))
        if i < gap_start or rng.random() < holes:
            continue
        o[i], c[i], v[i] = op * tick, px * tick, float(rng.integers(50, 500))
        h[i] = (max(op, px) + int(rng.integers(0, step))) * tick
        l[i] = (min(op, px) - int(rng.integers(0, step))) * tick
    return o, h, l, c, v


def synthetic_market(market: str, n_days: int, *, drift: float, seed: int,
                     start: date = date(2019, 6, 3)) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(sessions, entries) for `n_days` weekday sessions of `market`, as `parse_im2` shapes a kit's output, the
    entries from `im2_core.run_day` itself. `drift`: the planted trend, in steps a minute (0 is noise)."""
    q = im2_params(market)
    n = q["slots"]
    rng = np.random.default_rng(seed)
    dates, d = [], start
    while len(dates) < n_days:
        if d.weekday() < 5:
            dates.append(d)
        d += timedelta(days=1)
    prof, pc, srows, erows = [], None, [], []
    for day in dates:
        o, h, l, c, v = synthetic_session(market, rng, drift=drift,
                                          level=START[market] * (1 + float(rng.normal(0, 0.01))))
        key = day.strftime("%Y%m%d")
        sk = "" if (pc is not None and len(prof) >= LOOKBACK_WARM) else "look"
        res = core.run_day(o, h, l, c, v, pc, prof, q["p"], q["fills"], q["p_ref"],
                           hot_slots([], q["open_min"], n, q["hot_minutes"])) if not sk else None
        srows.append({"kind": "day", "d": key, "sym": market, "cal": "F", "sk": sk, "st": 1, "full": 1, "bad": 0,
                      "cov": 1.0, "ref": o[0], "pc": pc if pc is not None else np.nan, "np": len(prof), "rel": "",
                      "gone": ""})
        for e in (res["entries"] if res else []):
            row = {"kind": "entry", "d": key, "side": e["d"], "t": e["t"], "j0": e["j0"], "cl": e["cl"],
                   "ub": e["ub"], "lb": e["lb"], "vw": e["vw"], "mn": e["mn"]}
            for s, w in zip("pa", e["walks"]):
                row[f"dist_{s}"] = w["dist"] if w else np.nan
                for R, br in zip(q["p"]["rr"], w["br"] if w else [None] * 3):
                    row.update({f"kind{R}_{s}": br[0] if br else "", f"j{R}_{s}": br[1] if br else -1,
                                f"r{R}_{s}": br[2] if br else np.nan, f"mae{R}_{s}": br[3] if br else np.nan})
            erows.append(row)
        prof = (prof + [core.move_profile(o, c)])[-LOOKBACK_WARM:]
        pc = c[-1]
    return pd.DataFrame(srows), pd.DataFrame(erows)


def score_chain(drift: float, *, n_days: int, seed: int, n_paths: int, horizon_days: int,
                scales: Sequence[str] = sc.SCALES, reps: int = sc.REPS) -> tuple[list[dict], bool]:
    """The chain on synthetic sessions for the four markets: (one row per scale and R with e, its bounds and the
    gate's outcome at that scale; whether the gate passed at every scale)."""
    cfg = sc.config()
    specs, rt = sc.micro_specs(cfg), round_turns(cfg)
    tables, sessions = [], {}
    for i, m in enumerate(sc.MARKETS):
        s, e = synthetic_market(m, n_days, drift=drift, seed=seed + i)
        sessions[m] = s
        tables.append(sc.entry_table(m, s, e, round_turn=rt[m], spec=specs[m], cfg=cfg))
    table = pd.concat(tables, ignore_index=True)
    days = sorted(set().union(*(set(s.loc[s["sk"] == "", "d"]) for s in sessions.values())))
    rows, all_passed = [], True
    for s in scales:
        stats = {}
        for R in sc.RR_GATE:
            st = sc.edge(table, days, R, s, "v", seed=seed, reps=reps)
            stats[float(R)] = st
        df, passed = sc.run_gate(sc.blocks(table, days, s, "v"), stats, seed=seed, n_paths=n_paths,
                                 horizon_days=horizon_days)
        g = df[df["is_gate_row"]].iloc[0]
        all_passed = all_passed and passed
        for R in sc.RR_GATE:
            st = stats[float(R)]
            rows.append({"drift": drift, "scale": s, "R": R, "entries": st["entries"], "days": st["days"],
                         "e": st["e"], "lb": st["lb"], "lb_bootstrap": st["lb_bootstrap"],
                         "lb_normal": st["lb_normal"], "gate_passed": bool(passed),
                         "gate_median_log_growth": float(g["median_log_growth"]) if "median_log_growth" in g
                         else float("nan")})
    return rows, all_passed


def bracket_trades(e: float, R: float, n_trades: int, rate: float, rng: np.random.Generator
                   ) -> tuple[np.ndarray, np.ndarray, int]:
    """(outcomes in R, day index of each, number of days): brackets at R with mean e, `rate` trades a day on
    average (Poisson), days without a trade kept."""
    n_days = max(2, int(round(n_trades / rate)))
    day = np.sort(rng.integers(0, n_days, size=n_trades))
    p = (1.0 + e) / (1.0 + R)
    r = np.where(rng.random(n_trades) < p, R, -1.0)
    return r, day, n_days


def power_cell(e: float, R: int, n_trades: int, *, rate: float, replications: int, reps: int, seed: int,
               boot_len: int = sc.BOOT_LEN) -> dict[str, Any]:
    """Power at one cell: the share of replications whose registered lower bound (`im2_score.edge`) is above zero."""
    rng = np.random.default_rng(seed)
    hits, lbs = 0, []
    for i in range(replications):
        r, day, n_days = bracket_trades(e, R, n_trades, rate, rng)
        days = [f"{k:06d}" for k in range(n_days)]
        t = pd.DataFrame({"d": [days[k] for k in day], "dist_p": 1.0, f"v{R}_p": r, f"r{R}_p": r, f"u{R}_p": r,
                          f"kind{R}_p": np.where(r > 0, "t", "s")})
        st = sc.edge(t, days, R, "p", "v", seed=seed + 1 + i, boot_len=boot_len, reps=reps)
        lbs.append(st["lb"])
        hits += bool(st["lb"] > 0)
    return {"R": R, "e": e, "trades": n_trades, "rate": rate, "replications": replications, "boot_reps": reps,
            "boot_len": boot_len, "power": hits / replications, "median_lb": float(np.median(lbs))}


def required_trades(curve: pd.DataFrame, R: int, e: float, power: float = 0.8) -> float:
    """The fewest trades on the curve at (R, e) whose power reaches `power`; NaN when none does."""
    x = curve[(curve["R"] == R) & (np.isclose(curve["e"], e))].sort_values("trades")
    ok = x[x["power"] >= power]
    return float(ok["trades"].iloc[0]) if len(ok) else float("nan")


__all__ = ["SEED", "round_turns", "synthetic_session", "synthetic_market", "score_chain", "bracket_trades",
           "power_cell", "required_trades"]
