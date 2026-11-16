"""Scoring the reversion-to-the-open design with stage two's own execution model.

Draft design: `config/open_reversion.yaml`. Written before the design is fixed and before any
statistic about reversion to the open has been computed; the script refuses to run while the
design's `status` is `draft`. Reuses the panel, the day status, the swing detection, the
bootstrap and the era rescaling from `gap_reversal.py`.

The execution model (D-114 anchors sizing elsewhere; this is the per-trade shape):

* the target is fair value itself, a resting limit at the 08:30 CT open price;
* the stop is structural: one tick beyond the trigger bar's far extreme, or beyond the most recent
  confirmed swing extreme on the far side, never inside the cost floor;
* reward-to-risk is known at entry and is a FILTER: no trade below `r_min`.

u = pnl_net / intended risk, so winners are variable (about R) and losers about -1.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import yaml

from propedge import CONFIG_DIR
from propedge.outcomes import gap_reversal as _gap
from propedge.outcomes.gap_reversal import (  # noqa: F401  (re-exported for the script)
    SLOTS, TICK, Fills, Panel, ZERO_COST_MES, _ffill, block_lower_bound, fills_from_config,
    panel_from_bars, slot_of, swing_levels,
)


def load_design() -> dict:
    return yaml.safe_load((CONFIG_DIR / "open_reversion.yaml").read_text(encoding="utf-8"))


def gate_from_measures(x: np.ndarray, y: dict[int, np.ndarray], *, block: int, reps: int, seed: int,
                       bar_pct: float) -> dict:
    """The knob-free gate from per-day measurements (x, y30, y45, y60 in percent), for runs whose
    bars stayed in the cloud. Same statistic and bootstrap as `gate`; days are in date order."""
    x = np.asarray(x, float)
    ys = {m: np.asarray(v, float) for m, v in y.items()}
    ok = ~np.isnan(x)
    for v in ys.values():
        ok &= ~np.isnan(v)
    x = x[ok]
    ys = {m: v[ok] for m, v in ys.items()}
    n = len(x)
    if n < 3:
        return {"n_days": n, "passes": False}
    betas = {m: _slope(x, ys[m]) for m in ys}
    rng = np.random.default_rng(seed)
    k = math.ceil(n / block)
    boot = np.empty(reps)
    for r in range(reps):
        starts = rng.integers(0, max(n - block + 1, 1), size=k)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n]
        boot[r] = _slope(x[idx], ys[45][idx])
    ub = float(np.quantile(boot, 0.95))
    sd_x = float(x.std(ddof=1))
    effect = -betas[45] * sd_x
    return {"n_days": n, "beta_30": betas[30], "beta_45": betas[45], "beta_60": betas[60],
            "beta_45_ub95": ub, "beta_45_lb05": float(np.quantile(boot, 0.05)), "sd_x": sd_x,
            "effect_size_pct": effect, "effect_lo90": -ub * sd_x,
            "effect_hi90": -float(np.quantile(boot, 0.05)) * sd_x, "mean_abs_x": float(np.abs(x).mean()),
            "passes": bool(ub < 0 and effect >= bar_pct)}


def status_from_days(days: pd.DataFrame) -> pd.Series:
    """The gap design's day filter from per-day metadata alone (d, pst, sk, lt, has_open), for runs
    whose bars stayed in the cloud (D-120). Same rules, same order as `gap_reversal.day_status`."""
    gcfg = _gap.load_design()
    early = {str(x) for x in gcfg["event"].get("early_close_sessions", [])}
    cutoff = slot_of(gcfg["timing"]["cutoff_ct"].replace(":", ""))
    last_hhmm = int(_gap.alg.gap_slot_hhmm(cutoff))
    num = lambda s: pd.to_numeric(s, errors="coerce")   # noqa: E731
    d = np.where(num(days["d"]).isna(), "", num(days["d"]).fillna(0).astype("int64").astype(str))
    pst = np.where(num(days["pst"]).isna(), "", num(days["pst"]).fillna(0).astype("int64").astype(str))
    sk = days["sk"].fillna("").astype(str).to_numpy()
    lt = num(days["lt"]).fillna(-1).astype(int).to_numpy()
    has_open = days["has_open"].astype(bool).to_numpy()
    next_pst = np.concatenate([pst[1:], [d[-1]]])
    settled = next_pst == d
    reason, last_settled = [], ""
    for i in range(len(d)):
        r = ""
        if sk[i]:
            r = "settlement:" + sk[i]
        elif pst[i] != last_settled:
            r = "stale_settlement"
        elif not settled[i]:
            r = "no_settlement_session"
        elif any(last_settled < e < d[i] for e in early):
            r = "reference_is_early_close"
        elif lt[i] != last_hhmm:
            r = "incomplete_window"
        elif not has_open[i]:
            r = "no_0830_bar"
        reason.append(r)
        if settled[i]:
            last_settled = d[i]
    return pd.Series(reason, index=days.index)


def day_status(p: Panel, cfg: dict | None = None) -> pd.DataFrame:
    """The gap design's skip rules apply unchanged (settlement chain, holiday sessions, early
    closes, incomplete windows); the gap itself is not used here."""
    return _gap.day_status(p, _gap.load_design())


# ------------------------------------------------------------------ stage 1: the gate (no knobs)

def excursion_and_returns(p: Panel, days: np.ndarray, *, setup_end: str = "0845",
                          minutes=(30, 45, 60)) -> pd.DataFrame:
    """x = 100 ln(close(setup_end) / fair value); y_m = 100 ln(close(setup_end + m) / close(setup_end))."""
    open_slot, s = slot_of("0831"), slot_of(setup_end)
    rows = []
    for i in days:
        c = _ffill(p.c[i])
        fv = p.o[i, open_slot]
        if np.isnan(fv) or np.isnan(c[s]):
            continue
        row = {"n": int(p.n[i]), "date": p.date[i], "x": 100.0 * math.log(c[s] / fv)}
        for m in minutes:
            j = min(s + m, SLOTS - 1)
            row[f"y{m}"] = 100.0 * math.log(c[j] / c[s])
        rows.append(row)
    return pd.DataFrame(rows)


def _slope(x: np.ndarray, y: np.ndarray) -> float:
    x = x - x.mean()
    d = float(x @ x)
    return float(x @ (y - y.mean()) / d) if d > 0 else float("nan")


def gate(p: Panel, cfg: dict, days: np.ndarray, *, seed: int | None = None,
         setup_end: str = "0845") -> dict:
    """beta_m = OLS slope of y_m on x; reversion is beta < 0. Effect size = -beta_45 x sd(x)."""
    g = cfg["gate"]
    b = g["bootstrap"]
    t = excursion_and_returns(p, days, setup_end=setup_end).sort_values("date").reset_index(drop=True)
    n = len(t)
    if n < 3:
        return {"n_days": n, "passes": False}
    x = t["x"].to_numpy()
    betas = {m: _slope(x, t[f"y{m}"].to_numpy()) for m in (30, 45, 60)}
    # block bootstrap of beta_45 over days
    rng = np.random.default_rng(b["seed"] if seed is None else seed)
    block, reps = b["block_days"], b["replicates"]
    k = math.ceil(n / block)
    boot = np.empty(reps)
    y45 = t["y45"].to_numpy()
    for r in range(reps):
        starts = rng.integers(0, max(n - block + 1, 1), size=k)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n]
        boot[r] = _slope(x[idx], y45[idx])
    ub = float(np.quantile(boot, 0.95))
    sd_x = float(x.std(ddof=1))
    effect = -betas[45] * sd_x
    passes = (ub < g["pass"]["beta_45_one_sided_95_upper_bound_below"]
              and effect >= g["pass"]["effect_size_pct_at_least"])
    return {"n_days": n, "beta_30": betas[30], "beta_45": betas[45], "beta_60": betas[60],
            "beta_45_ub95": ub, "beta_45_lb05": float(np.quantile(boot, 0.05)), "sd_x": sd_x,
            "effect_size_pct": effect, "mean_abs_x": float(np.abs(x).mean()), "passes": bool(passes)}


# ------------------------------------------------------------------ stage 2: the trade

def _is_structural_trigger(o, h, l, c, t: int, d: int, w: float, swing_from: int) -> bool:
    """Structure break + displacement bar in direction d at bar t (the gap design's definitions)."""
    if np.isnan(c[t]) or np.isnan(o[t]):
        return False
    swings = [s for s in swing_levels(h, l, "low" if d < 0 else "high", swing_from, t) if s[0] + 2 <= t]
    if not swings:
        return False
    level = swings[-1][1]
    if d < 0:
        return (c[t] < level and c[t] < o[t] and (o[t] - l[t]) > 0
                and (c[t] - l[t]) <= w * (o[t] - l[t]) + 1e-12)
    return (c[t] > level and c[t] > o[t] and (h[t] - o[t]) > 0
            and (h[t] - c[t]) <= w * (h[t] - o[t]) + 1e-12)


def far_side_anchor(o, h, l, c, t: int, d: int, kind: str, swing_from: int) -> float:
    """The price where the reversal thesis is wrong: the trigger bar's far extreme, or the extreme
    of the confirmed swings on the far side since the open (the top of the move away for a short,
    the bottom for a long). NaN if no swing has been confirmed."""
    if kind == "trigger_bar":
        return float(h[t] if d < 0 else l[t])
    swings = [s[1] for s in swing_levels(h, l, "high" if d < 0 else "low", swing_from, t) if s[0] + 2 <= t]
    if not swings:
        return float("nan")
    return float(max(swings) if d < 0 else min(swings))


def score_trade(o, h, l, c, t: int, d: int, fv: float, *, anchor: str, r_min: float,
                floor_ticks: int, fills: Fills, cutoff: int, swing_from: int,
                flip: bool = False) -> dict:
    """One trade from the close of bar t toward fair value (direction d). With `flip`, the same
    stop and reward distances are placed on the far side of the entry and the position reversed:
    the permutation null's trade, which has the real trade's odds when there is no reversion."""
    a = far_side_anchor(o, h, l, c, t, d, anchor, swing_from)
    if np.isnan(a):
        return {"reason": "no_swing_anchor"}
    entry = c[t] + d * fills.entry * TICK
    if (d < 0 and entry <= fv) or (d > 0 and entry >= fv):
        return {"reason": "past_fair_value"}
    stop_px = a - d * TICK                              # one tick beyond the anchor
    dist = abs(stop_px - entry)
    stop_ticks = max(int(round(dist / TICK)), floor_ticks)
    reward = abs(fv - entry)
    R = reward / (stop_ticks * TICK)
    if R < r_min - 1e-12:
        return {"reason": "r_below_min", "R_at_entry": R}
    if flip:
        d = -d
        entry = c[t] + d * fills.entry * TICK
    stop_px = entry - d * stop_ticks * TICK
    tgt = fv if not flip else entry + d * reward
    exit_px, kind, slip, j_exit = None, "time", fills.flatten, cutoff
    for j in range(t + 1, cutoff + 1):
        if np.isnan(o[j]):
            continue
        if (o[j] >= stop_px) if d < 0 else (o[j] <= stop_px):
            exit_px, kind, slip, j_exit = o[j], "stop_gap", 0.0, j
            break
        stop_hit = h[j] >= stop_px if d < 0 else l[j] <= stop_px
        tgt_hit = l[j] < tgt if d < 0 else h[j] > tgt      # a trade THROUGH the target
        if stop_hit:
            exit_px, kind, slip, j_exit = stop_px - d * fills.stop * TICK, "stop", fills.stop, j
            break
        if tgt_hit:
            exit_px, kind, slip, j_exit = tgt - d * fills.target * TICK, "target", fills.target, j
            break
    if exit_px is None:
        exit_px = _ffill(c)[cutoff] - d * fills.flatten * TICK
    pnl_gross = d * (exit_px - entry) * fills.point_value
    pnl_net = pnl_gross - fills.round_turn
    risk = stop_ticks * fills.tick_value
    return {"reason": "", "t": t, "anchor_px": a, "stop_ticks": stop_ticks,
            "floor_bound": stop_ticks == floor_ticks, "R_at_entry": R, "entry": entry,
            "exit": exit_px, "exit_kind": kind, "minutes": j_exit - t, "slip_ticks": fills.entry + slip,
            "pnl_gross": pnl_gross, "pnl_net": pnl_net, "risk": risk, "u": pnl_net / risk,
            "u_gross": pnl_gross / risk}


def variants(cfg: dict) -> list[dict]:
    f = cfg["features_searched"]
    return [{"key": f"{a}|r{r}", "anchor": a, "r_min": r}
            for a in f["stop_anchor"]["grid"] for r in f["r_min"]["grid"]]


def score_variant(p: Panel, status: pd.DataFrame, days: np.ndarray, v: dict, cfg: dict,
                  fills: Fills, *, scale_to: float | None = None, baseline: bool = False,
                  flip: bool = False) -> pd.DataFrame:
    """One row per day: the first bar in the window that triggers (structural, or the plain
    baseline: the first bar at which the R filter holds) toward fair value, and its trade."""
    tr = cfg["trigger"]
    first = slot_of(tr["window_ct"][0].replace(":", ""))
    last = slot_of(tr["window_ct"][1].replace(":", ""))
    cutoff = slot_of("1030")
    swing_from = slot_of("0831")
    w = tr["displacement_w"]
    floor_ticks = int(cfg["features_searched"]["stop_anchor"]["floor_ticks"])
    rows = []
    for i in days:
        f = 1.0 if scale_to is None else scale_to / p.ps[i]
        o, h, l, c = p.o[i] * f, p.h[i] * f, p.l[i] * f, p.c[i] * f
        fv = o[swing_from]
        base = {"n": int(p.n[i]), "d": p.d[i], "date": p.date[i], "weekday": p.weekday[i],
                "variant": v["key"], "anchor": v["anchor"], "r_min": v["r_min"],
                "baseline": baseline, "scale": "actual" if scale_to is None else scale_to}
        trade, last_reason = None, "no_trigger"
        for t in range(first, last + 1):
            if np.isnan(c[t]):
                continue
            d = -1 if c[t] > fv else (1 if c[t] < fv else 0)
            if d == 0:
                continue
            if not baseline and not _is_structural_trigger(o, h, l, c, t, d, w, swing_from):
                continue
            r = score_trade(o, h, l, c, t, d, fv, anchor=v["anchor"], r_min=v["r_min"],
                            floor_ticks=floor_ticks, fills=fills, cutoff=cutoff, swing_from=swing_from,
                            flip=flip)
            if r["reason"] == "":
                trade = {**r, "direction": -d if flip else d}
                break
            last_reason = r["reason"]
            if not baseline:
                break                                   # the structural trigger fires once
        if trade is None:
            rows.append({**base, "reason": last_reason, "u": np.nan})
        else:
            rows.append({**base, **trade})
    return pd.DataFrame(rows)


def stats(trades: pd.DataFrame, *, block: int, reps: int, seed: int) -> dict:
    t = trades[trades["u"].notna()].sort_values("date")
    bb = block_lower_bound(t["u"].to_numpy(), block=block, reps=reps, seed=seed)
    if len(t) == 0:
        return {**bb, "n_days": int(len(trades)), "win_over_loss": np.nan}
    wins, losses = t.loc[t["u"] > 0, "u"], t.loc[t["u"] < 0, "u"]
    k = t["exit_kind"]
    return {**bb, "n_days": int(len(trades)), "p_target": float((k == "target").mean()),
            "p_stop": float(k.str.startswith("stop").mean()), "p_time": float((k == "time").mean()),
            "floor_bound_share": float(t["floor_bound"].mean()), "mean_minutes": float(t["minutes"].mean()),
            "mean_R_at_entry": float(t["R_at_entry"].mean()),
            "win_over_loss": float(wins.mean() / -losses.mean()) if len(wins) and len(losses) else np.nan}


def permutation_null(u_real: dict[str, np.ndarray], u_flip: dict[str, np.ndarray], *,
                     permutations: int, seed: int, block: int, reps: int, boot_seed: int) -> np.ndarray:
    """Best-of-K selection-half lower bound when each day's trade geometry is flipped with
    probability 1/2 (the same flips for every variant)."""
    keys = list(u_real)
    n_days = len(next(iter(u_real.values())))
    rng = np.random.default_rng(seed)
    best = np.empty(permutations)
    for k in range(permutations):
        flip = rng.random(n_days) < 0.5
        lbs = [block_lower_bound(np.where(flip, u_flip[key], u_real[key]), block=block, reps=reps,
                                 seed=boot_seed + k)["lb"] for key in keys]
        best[k] = np.nanmax(lbs)
    return best


def select(rows: list[dict], cfg: dict) -> dict:
    """Plateau on r_min (ordered); the anchor is binary and compared directly; the structural
    trigger must beat its plain-entry baseline at the same cell."""
    rs = cfg["features_searched"]["r_min"]["grid"]
    lb = {(r["anchor"], r["r_min"]): r["lb"] for r in rows if not r.get("baseline")}
    base = {(r["anchor"], r["r_min"]): r["lb"] for r in rows if r.get("baseline")}

    def pos(v):
        return v is not None and not np.isnan(v) and v > 0

    def eligible(a, r):
        ri = rs.index(r)
        cells = [(a, r)] + [(a, rs[j]) for j in (ri - 1, ri + 1) if 0 <= j < len(rs)]
        return all(pos(lb.get(cell)) for cell in cells)

    elig = {k: eligible(*k) for k in lb}
    cands = [k for k in lb if elig[k] and lb[k] > base.get(k, -np.inf)]
    if not cands:
        return {"selected": None, "eligible": elig,
                "why": "no cell has a positive lower bound with its neighbours AND beats its plain-entry baseline"}
    top = max(lb[k] for k in cands)
    tied = sorted([k for k in cands if abs(lb[k] - top) < 1e-12],
                  key=lambda k: abs(rs.index(k[1]) - (len(rs) - 1) / 2))
    return {"selected": tied[0], "eligible": elig, "why": "highest eligible lower bound that beats its baseline"}
