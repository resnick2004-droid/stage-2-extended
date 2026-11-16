"""Scoring the opening-gap reversal design from the recorded minute paths (D-105 to D-109).

Everything the design fixes is read from `config/gap_reversal.yaml`; the slot arithmetic follows
from the kit's recording window (`qc_algorithms.GAP_REC_HM`). Stage 1, the existence gate, has no
free parameter. Stage 2 scores the twelve variants on the selection half, applies the plateau and
ablation rules, scores the selection once on the validation half, and runs the direction-flip
permutation null. Before costs are applied the day's prices may be rescaled to a stated level
(D-106): the ATR, the stop and the target scale with the price; the tick, the slippage and the
round turn do not.

Nothing here reads a date on or after the confirmation boundary; the script asserts it.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
import yaml

from propedge import CONFIG_DIR
from propedge.data import qc_algorithms as alg

SLOTS = alg.GAP_SLOTS
TICK = alg.GAP_TICK
_FIRST_MIN = alg.GAP_REC_HM[0][0] * 60 + alg.GAP_REC_HM[0][1]
WEEKDAY = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday",
           "Fri": "Friday"}


def slot_of(hhmm: str) -> int:
    """'0840' -> the slot of the bar ENDING at 08:40."""
    return int(hhmm[:2]) * 60 + int(hhmm[2:]) - _FIRST_MIN


def load_design() -> dict:
    return yaml.safe_load((CONFIG_DIR / "gap_reversal.yaml").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ fills and vehicle

@dataclass(frozen=True)
class Fills:
    entry: float            # adverse ticks
    stop: float
    target: float
    flatten: float
    round_turn: float       # USD per contract
    tick_value: float       # USD per tick per contract
    point_value: float      # USD per point per contract


def fills_from_config(profile: str = "assumed", vehicle: str = "MES") -> Fills:
    from propedge.execution.fills import FillModel
    from propedge.outcomes.time_exit_sd import vehicle as _vehicle

    fm, veh = FillModel.load(profile), _vehicle(vehicle)
    return Fills(fm.entry_slippage_ticks, fm.stop_slippage_ticks, fm.target_slippage_ticks,
                 fm.flatten_slippage_ticks, veh.round_turn, veh.tick_value, veh.point_value)


ZERO_COST_MES = Fills(0.0, 0.0, 0.0, 0.0, 0.0, 1.25, 5.0)


# ------------------------------------------------------------------ the panel

@dataclass
class Panel:
    n: np.ndarray
    date: pd.DatetimeIndex
    d: np.ndarray
    weekday: np.ndarray
    sym: np.ndarray
    ps: np.ndarray
    pst: np.ndarray
    sk: np.ndarray
    base: np.ndarray
    nb: np.ndarray
    lt: np.ndarray
    prev_d: np.ndarray
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray

    def __len__(self) -> int:
        return len(self.n)


def panel_from_bars(df: pd.DataFrame) -> Panel:
    """The long bar table (one row per recorded minute) -> arrays (days x slots), NaN where missing."""
    df = df.copy()
    # Date-like columns come back from CSV as floats when a first-day value is empty ("20090601.0");
    # normalise them to plain digit strings before anything compares them (the D-101 lesson).
    for col in ("d", "pst", "lt"):
        num = pd.to_numeric(df[col], errors="coerce")
        df[col] = np.where(num.isna(), "", num.fillna(0).astype("int64").astype(str))
    df["lt"] = df["lt"].str.zfill(4)
    days = df.drop_duplicates("n").sort_values("n").reset_index(drop=True)
    idx = {int(n): i for i, n in enumerate(days["n"])}
    o, h, l, c = (np.full((len(days), SLOTS), np.nan) for _ in range(4))
    rows = df["n"].astype(int).map(idx).to_numpy()
    cols = df["t"].astype(str).str.zfill(4).map(slot_of).to_numpy()
    o[rows, cols], h[rows, cols], l[rows, cols], c[rows, cols] = (
        df["o"].to_numpy(float), df["h"].to_numpy(float), df["l"].to_numpy(float),
        df["c"].to_numpy(float))
    date = pd.to_datetime(days["d"], format="%Y%m%d")
    d = days["d"].to_numpy(str)
    return Panel(n=np.array(days["n"], int), date=pd.DatetimeIndex(date), d=d,
                 weekday=np.array(date.dt.day_name(), str), sym=np.array(days["sym"], str),
                 ps=np.array(days["ps"], float), pst=np.array(days["pst"].fillna(""), str),
                 sk=np.array(days["sk"].fillna(""), str), base=np.array(days["base"], float),
                 nb=np.array(days["nb"], int), lt=np.array(days["lt"], str),
                 prev_d=np.concatenate([[""], d[:-1]]), o=o, h=h, l=l, c=c)


# ------------------------------------------------------------------ the event (fixed)

def day_status(p: Panel, cfg: dict) -> pd.DataFrame:
    """Per day: the gap in %, the skip reason (timestamps and settlement only), the release flag."""
    open_slot = slot_of("0831")                          # the bar covering 08:30-08:31
    cutoff = slot_of(cfg["timing"]["cutoff_ct"].replace(":", ""))
    reason = np.array([""] * len(p), dtype=object)
    # A day settled if the next day's reference date is this day (the kit sets it at the 15:00 CT
    # bar). A holiday or early-close session has no settlement; it is skipped, and the day after
    # it measures its gap from the last SETTLED session, as the cash market does.
    next_pst = np.concatenate([p.pst[1:], [p.d[-1]]])   # the final day is taken as settled
    settled = next_pst == p.d
    early = {str(x) for x in cfg["event"].get("early_close_sessions", [])}
    last_settled = ""
    for i in range(len(p)):
        if p.sk[i]:
            reason[i] = "settlement:" + p.sk[i]
        elif p.pst[i] != last_settled:
            reason[i] = "stale_settlement"                # the reference is not the last settlement
        elif not settled[i]:
            reason[i] = "no_settlement_session"           # holiday / early close: no cash open
        elif any(last_settled < e < p.d[i] for e in early):
            reason[i] = "reference_is_early_close"        # D-111/D-113: an early close sits between
                                                          # this day and its reference settlement
        elif int(p.lt[i]) != int(alg.gap_slot_hhmm(cutoff)):
            reason[i] = "incomplete_window"
        elif math.isnan(p.o[i, open_slot]):
            reason[i] = "no_0830_bar"
        if settled[i]:
            last_settled = p.d[i]
    ok = reason == ""
    gap = np.full(len(p), np.nan)
    gap[ok] = 100.0 * np.log(p.o[ok, open_slot] / p.ps[ok])
    rng = (p.h[:, open_slot] - p.l[:, open_slot]) / p.base
    present = ~np.isnan(rng)
    thresh = np.quantile(rng[present], 0.95) if present.any() else np.inf
    release = present & (rng >= thresh)
    return pd.DataFrame({"n": p.n, "d": p.d, "date": p.date, "weekday": p.weekday, "gap": gap,
                         "reason": reason.astype(str), "release_flag": release})


def event_mask(status: pd.DataFrame, cfg: dict, *, threshold: float | None = None,
               sign: str | None = None, weekdays: list[str] | None = None) -> np.ndarray:
    threshold = cfg["event"]["threshold_pct"] if threshold is None else threshold
    sign = cfg["event"]["sign"] if sign is None else sign
    names = [WEEKDAY[w] for w in (cfg["event"]["weekdays"] if weekdays is None else weekdays)]
    g = status["gap"].to_numpy()
    ok = (status["reason"].to_numpy() == "") & status["weekday"].isin(names).to_numpy()
    if sign == "up_only":
        return ok & (g >= threshold)
    if sign == "down_only":
        return ok & (g <= -threshold)
    return ok & (np.abs(g) >= threshold)


def against_the_gap(status: pd.DataFrame) -> np.ndarray:
    """Trade direction per day: -1 after a gap up, +1 after a gap down."""
    return -np.sign(np.nan_to_num(status["gap"].to_numpy())).astype(int)


# ------------------------------------------------------------------ stage 1: the gate

def _ffill(row: np.ndarray) -> np.ndarray:
    out = row.copy()
    for j in range(1, len(out)):
        if np.isnan(out[j]):
            out[j] = out[j - 1]
    return out


def favourable_returns(p: Panel, days: np.ndarray, dirs: np.ndarray, entry_slot: int,
                       minutes: np.ndarray) -> np.ndarray:
    """100 x d x ln(P(entry + m) / P(entry)) per day and minute; closes forward-filled."""
    out = np.full((len(days), len(minutes)), np.nan)
    for k, (i, d) in enumerate(zip(days, dirs)):
        c = _ffill(p.c[i])
        if np.isnan(c[entry_slot]):
            continue
        j = np.minimum(entry_slot + minutes, SLOTS - 1)
        out[k] = 100.0 * d * np.log(c[j] / c[entry_slot])
    return out


def block_lower_bound(x: np.ndarray, *, block: int, reps: int, seed: int,
                      alpha: float = 0.05) -> dict:
    """Mean, sd and the one-sided (1 - alpha) lower bound from a moving-block bootstrap."""
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    n = len(x)
    if n < 2:
        return {"n": n, "mean": float(x.mean()) if n else float("nan"), "sd": float("nan"),
                "lb": float("nan")}
    rng = np.random.default_rng(seed)
    k = math.ceil(n / block)
    means = np.empty(reps)
    chunk = max(1, min(reps, 4_000_000 // max(n, 1)))
    for lo in range(0, reps, chunk):
        r = min(chunk, reps - lo)
        starts = rng.integers(0, max(n - block + 1, 1), size=(r, k))
        idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(r, -1)[:, :n]
        means[lo:lo + r] = x[idx].mean(axis=1)
    return {"n": n, "mean": float(x.mean()), "sd": float(x.std(ddof=1)),
            "lb": float(np.quantile(means, alpha))}


def gate(p: Panel, status: pd.DataFrame, cfg: dict, mask: np.ndarray, *,
         seed: int | None = None) -> dict:
    """The existence gate on the days in `mask`: G = mean favourable ACAR at 30/45/60 min."""
    g = cfg["gate"]
    entry = slot_of(cfg["timing"]["entry_earliest_ct"].replace(":", ""))
    days = np.flatnonzero(mask)
    dirs = against_the_gap(status)[days]
    path_minutes = np.arange(5, SLOTS - entry, 5)
    path = favourable_returns(p, days, dirs, entry, path_minutes)
    key = favourable_returns(p, days, dirs, entry, np.array([30, 45, 60]))
    per_day = key.mean(axis=1)
    b = g["bootstrap"]
    bb = block_lower_bound(per_day, block=b["block_days"], reps=b["replicates"],
                           seed=b["seed"] if seed is None else seed)
    ret60 = favourable_returns(p, days, dirs, entry, np.array([60]))[:, 0]
    sd60 = float(np.nanstd(ret60, ddof=1)) if len(days) > 1 else float("nan")
    # Grant's ten-minute continuation: the move from the 08:30 open to the entry close, IN the gap's
    # direction (positive = continuation). D-113: reported here so it is on record.
    open_slot = slot_of("0831")
    cont = 100.0 * (-dirs) * np.log(p.c[days, entry] / p.o[days, open_slot])
    passes = (bb["mean"] >= g["pass"]["min_fraction_of_grant"] * g["grant_value_pct"]
              and bb["lb"] > g["pass"]["lower_bound_one_sided_95_above_pct"])
    return {"n_days": int(len(days)), "G": bb["mean"], "G_lb": bb["lb"], "G_sd": bb["sd"],
            "grant_G": g["grant_value_pct"], "G_over_grant": bb["mean"] / g["grant_value_pct"],
            "sd_60min": sd60, "G_over_sd60": bb["mean"] / sd60 if sd60 else float("nan"),
            "acar60_se": sd60 / math.sqrt(len(days)) if len(days) else float("nan"),
            "continuation_0830_0840_pct": float(np.nanmean(cont)) if len(days) else float("nan"),
            "passes": bool(passes),
            "acar": dict(zip((int(m) for m in path_minutes), np.nanmean(path, axis=0).tolist()))}


# ------------------------------------------------------------------ stage 2: triggers, stop, trade

def swing_levels(h: np.ndarray, l: np.ndarray, kind: str, start: int, upto: int) -> list[tuple[int, float]]:
    """Williams fractals (2 bars each side) with all five bars present, i in [start+2, upto-2]."""
    out = []
    for i in range(start + 2, upto - 1):
        win_h, win_l = h[i - 2:i + 3], l[i - 2:i + 3]
        if np.isnan(win_h).any() or np.isnan(win_l).any():
            continue
        if kind == "low" and all(l[i] < l[k] for k in (i - 2, i - 1, i + 1, i + 2)):
            out.append((i, float(l[i])))
        elif kind == "high" and all(h[i] > h[k] for k in (i - 2, i - 1, i + 1, i + 2)):
            out.append((i, float(h[i])))
    return out


def trigger_slot(o, h, l, c, d: int, kind: str, w: float | None, first: int, last: int,
                 swing_from: int) -> int:
    """The entry bar's slot, or -1. `time`: the first slot. `structural`: the first bar in
    [first, last] that is both a market structure break and a displacement bar in direction d."""
    if kind == "time":
        return first if not np.isnan(c[first]) else -1
    for t in range(first, last + 1):
        if np.isnan(c[t]) or np.isnan(o[t]):
            continue
        swings = swing_levels(h, l, "low" if d < 0 else "high", swing_from, t)
        swings = [(i, lvl) for i, lvl in swings if i + 2 <= t]
        if not swings:
            continue
        level = swings[-1][1]
        if d < 0:
            msb = c[t] < level
            disp = c[t] < o[t] and (o[t] - l[t]) > 0 and (c[t] - l[t]) <= w * (o[t] - l[t]) + 1e-12
        else:
            msb = c[t] > level
            disp = c[t] > o[t] and (h[t] - o[t]) > 0 and (h[t] - c[t]) <= w * (h[t] - o[t]) + 1e-12
        if msb and disp:
            return t
    return -1


def atr(h, l, c, t: int, n: int = 14) -> float:
    """Mean true range of the n bars ending at t; NaN unless all n are present."""
    lo = t - n + 1
    if lo < 0:
        return float("nan")
    hh, ll, cc = h[lo:t + 1], l[lo:t + 1], c[lo:t + 1]
    if np.isnan(hh).any() or np.isnan(ll).any() or np.isnan(cc).any():
        return float("nan")
    prev = np.concatenate([[c[lo - 1] if lo >= 1 else np.nan], cc[:-1]])
    tr = hh - ll
    ok = ~np.isnan(prev)
    tr[ok] = np.maximum(tr[ok], np.maximum(np.abs(hh[ok] - prev[ok]), np.abs(ll[ok] - prev[ok])))
    return float(tr.mean())


def score_trade(o, h, l, c, t: int, d: int, m: float, *, floor_ticks: int, R: float,
                fills: Fills, cutoff: int, daily_risk: float = 250.0,
                max_contracts: int = 20) -> dict:
    """One bracket from the close of bar t in direction d. Returns the trade, or a reason."""
    a = atr(h, l, c, t)
    if np.isnan(a):
        return {"reason": "atr_bars_missing"}
    stop_ticks = max(int(math.ceil(m * a / TICK - 1e-9)), floor_ticks)
    target_ticks = int(math.floor(R * stop_ticks + 0.5))
    entry = c[t] + d * fills.entry * TICK
    stop_px = entry - d * stop_ticks * TICK
    tgt_px = entry + d * target_ticks * TICK
    exit_px, kind, slip, j_exit = None, "time", fills.flatten, cutoff
    for j in range(t + 1, cutoff + 1):
        if np.isnan(o[j]):
            continue
        through_open = o[j] >= stop_px if d < 0 else o[j] <= stop_px
        if through_open:
            exit_px, kind, slip, j_exit = o[j], "stop_gap", 0.0, j
            break
        stop_hit = h[j] >= stop_px if d < 0 else l[j] <= stop_px
        tgt_hit = l[j] < tgt_px if d < 0 else h[j] > tgt_px
        if stop_hit:                                   # same bar: stop first
            exit_px, kind, slip, j_exit = stop_px - d * fills.stop * TICK, "stop", fills.stop, j
            break
        if tgt_hit:
            exit_px, kind, slip, j_exit = tgt_px - d * fills.target * TICK, "target", fills.target, j
            break
    if exit_px is None:
        cc = _ffill(c)
        exit_px = cc[cutoff] - d * fills.flatten * TICK
    pnl_gross = d * (exit_px - entry) * fills.point_value
    pnl_net = pnl_gross - fills.round_turn
    risk = stop_ticks * fills.tick_value
    # floor_bound: the floor set the stop, i.e. ceil(m x ATR / tick) <= floor_ticks (audit D-113).
    return {"reason": "", "t": t, "atr_ticks": a / TICK, "stop_ticks": stop_ticks,
            "target_ticks": target_ticks, "floor_bound": stop_ticks == floor_ticks,
            "entry": entry, "exit": exit_px, "exit_kind": kind, "minutes": j_exit - t,
            "slip_ticks": fills.entry + slip, "pnl_gross": pnl_gross, "pnl_net": pnl_net,
            "risk": risk, "u": pnl_net / risk, "u_gross": pnl_gross / risk,
            "contracts": min(max_contracts, int(risk and daily_risk // risk))}


def variants(cfg: dict) -> list[dict]:
    ms = cfg["stop"]["multiplier_grid"]
    out = [{"key": f"time|m{m}", "kind": "time", "w": None, "m": m} for m in ms]
    for w in cfg["trigger"]["structural"]["w_grid"]:
        out += [{"key": f"struct|w{w}|m{m}", "kind": "structural", "w": w, "m": m} for m in ms]
    return out


def score_variant(p: Panel, status: pd.DataFrame, days: np.ndarray, dirs: np.ndarray, v: dict,
                  cfg: dict, fills: Fills, *, scale_to: float | None = None) -> pd.DataFrame:
    """One row per day in `days`: the trade in direction dirs[k], or the reason there was none."""
    tm = cfg["timing"]
    first = slot_of(tm["entry_earliest_ct"].replace(":", ""))
    last = slot_of(tm["entry_latest_ct"].replace(":", ""))
    cutoff = slot_of(tm["cutoff_ct"].replace(":", ""))
    swing_from = slot_of("0831")
    rows = []
    for i, d in zip(days, dirs):
        f = 1.0 if scale_to is None else scale_to / p.ps[i]
        o, h, l, c = p.o[i] * f, p.h[i] * f, p.l[i] * f, p.c[i] * f
        t = trigger_slot(o, h, l, c, int(d), v["kind"], v["w"], first, last, swing_from)
        base = {"n": int(p.n[i]), "d": p.d[i], "date": p.date[i], "gap": status["gap"].iloc[i],
                "direction": int(d), "variant": v["key"], "kind": v["kind"], "w": v["w"],
                "m": v["m"], "scale": "actual" if scale_to is None else scale_to,
                "release_flag": bool(status["release_flag"].iloc[i])}
        if t < 0:
            rows.append({**base, "reason": "no_trigger", "u": np.nan})
            continue
        r = score_trade(o, h, l, c, t, int(d), v["m"], floor_ticks=cfg["stop"]["floor_ticks"],
                        R=cfg["target"]["R"], fills=fills, cutoff=cutoff,
                        daily_risk=cfg["sizing"]["daily_risk_usd"])
        rows.append({**base, **r} if r["reason"] == "" else {**base, "reason": r["reason"],
                                                              "u": np.nan})
    return pd.DataFrame(rows)


def stats(trades: pd.DataFrame, *, block: int, reps: int, seed: int) -> dict:
    """Selection statistics for one variant's trade table (rows without a trade are ignored)."""
    t = trades[trades["u"].notna()].sort_values("date")
    bb = block_lower_bound(t["u"].to_numpy(), block=block, reps=reps, seed=seed)
    if len(t) == 0:
        return {**bb, "n_days": int(len(trades)), "p_target": np.nan, "p_stop": np.nan,
                "p_time": np.nan, "floor_bound_share": np.nan, "mean_minutes": np.nan,
                "mean_u_gross": np.nan}
    k = t["exit_kind"]
    return {**bb, "n_days": int(len(trades)), "p_target": float((k == "target").mean()),
            "p_stop": float(k.str.startswith("stop").mean()), "p_time": float((k == "time").mean()),
            "floor_bound_share": float(t["floor_bound"].mean()),
            "mean_minutes": float(t["minutes"].mean()), "mean_u_gross": float(t["u_gross"].mean())}


# ------------------------------------------------------------------ selection

def select(rows: list[dict], cfg: dict) -> dict:
    """Plateau eligibility on w and m, then the ablation against the time trigger (design §3)."""
    ws = cfg["trigger"]["structural"]["w_grid"]
    ms = cfg["stop"]["multiplier_grid"]
    lb = {(r["kind"], r["w"], r["m"]): r["lb"] for r in rows}

    def pos(v):
        return v > 0 and not np.isnan(v)

    def eligible(kind, w, m):
        mi = ms.index(m)
        cells = [(kind, w, m)] + [(kind, w, ms[j]) for j in (mi - 1, mi + 1) if 0 <= j < len(ms)]
        if kind == "structural":
            wi = ws.index(w)
            cells += [(kind, ws[j], m) for j in (wi - 1, wi + 1) if 0 <= j < len(ws)]
        return all(pos(lb.get(cell, np.nan)) for cell in cells)

    elig = {k: eligible(*k) for k in lb}

    def best(kind):
        cands = [k for k in lb if k[0] == kind and elig[k]]
        if not cands:
            return None
        top = max(lb[k] for k in cands)
        tied = [k for k in cands if abs(lb[k] - top) < 1e-12]
        return sorted(tied, key=lambda k: (abs(ms.index(k[2]) - (len(ms) - 1) / 2),
                                           abs(ws.index(k[1]) - (len(ws) - 1) / 2) if k[1] else 0))[0]

    t_best, s_best = best("time"), best("structural")
    chosen, why = None, "no eligible cell: nothing on the grid has a positive lower bound with its neighbours"
    if s_best is not None and lb[s_best] > lb.get(("time", None, s_best[2]), -np.inf):
        chosen, why = s_best, "structural: its best eligible cell beats the time trigger at the same m"
    elif t_best is not None:
        chosen, why = t_best, ("time: the structural trigger did not beat it" if s_best else
                               "time: no eligible structural cell")
    return {"selected": chosen, "why": why, "eligible": elig, "time_best": t_best,
            "structural_best": s_best}


def permutation_null(u_minus: dict[str, np.ndarray], u_plus: dict[str, np.ndarray], *,
                     permutations: int, seed: int, block: int, reps: int, boot_seed: int) -> np.ndarray:
    """Best-of-K selection-half lower bound under random direction flips, per permutation.

    `u_minus[key][i]` is day i's u in the actual direction, `u_plus` in the flipped one (NaN where
    that direction had no trade). Every variant sees the same flips on the same day.
    """
    keys = list(u_minus)
    n_days = len(next(iter(u_minus.values())))
    rng = np.random.default_rng(seed)
    best = np.empty(permutations)
    for k in range(permutations):
        flip = rng.random(n_days) < 0.5
        lbs = []
        for key in keys:
            u = np.where(flip, u_plus[key], u_minus[key])
            lbs.append(block_lower_bound(u, block=block, reps=reps, seed=boot_seed + k)["lb"])
        best[k] = np.nanmax(lbs)
    return best
