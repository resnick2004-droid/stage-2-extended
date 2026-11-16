"""The sd of a time-exit trade in units of intended risk, for Stage 2B's C-007 (D-43, D-100).

Input is the per-day leg evidence recorded in QuantConnect (D-97): prices at the window start and
end, the window's extremes, the signal's direction and the window's realised variance. Everything
parameter-dependent happens here, in the order D-100 fixes:

1. a panel log-HAR forecast of each window's variance, fitted on an expanding window of days
   strictly before the day it forecasts (so it is computable before entry);
2. the stop in vehicle ticks, `max(ceil(2.0 x price sd / tick), floor)`, and the size in micros;
3. the trade under the `assumed` fill profile: 1 tick adverse on entry, stop and time exit, a stop
   judged against the window's extremes, round-turn cost per contract;
4. `u = pnl_net / r`, its sd, a 20-day moving-block bootstrap, and D-43's five diagnostics.

**The mean of `u` is never computed or returned** (D-100): development estimates the sd only.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
import yaml

from propedge import CONFIG_DIR, REPO_ROOT

MARKETS = ("GC", "CL", "6E", "ES")


@dataclass(frozen=True)
class Vehicle:
    name: str
    tick: float
    tick_value: float
    round_turn: float

    @property
    def point_value(self) -> float:
        return self.tick_value / self.tick


def load_c007() -> dict:
    return yaml.safe_load((CONFIG_DIR / "c007.yaml").read_text(encoding="utf-8"))


def vehicle(name: str) -> Vehicle:
    """Tick, tick value and round-turn cost from configuration -- never typed here."""
    inst = yaml.safe_load((CONFIG_DIR / "instruments.yaml").read_text(encoding="utf-8"))
    fills = yaml.safe_load((CONFIG_DIR / "fills.yaml").read_text(encoding="utf-8"))
    rt = fills["round_turn_by_instrument"]["values"]
    if name in inst["instruments"]:
        spec = inst["instruments"][name]
        return Vehicle(name, float(spec["tick_size"]), float(spec["tick_value"]), float(rt[name]))
    spec = inst["candidate_instruments"][name]
    if spec.get("spec_status") != "verified":
        raise ValueError(f"{name} contract spec is not verified")
    return Vehicle(name, float(spec["tick_size"]), float(spec["tick_value"]),
                   float(spec["round_turn_cost"]))


def load_evidence(market: str, cfg: dict | None = None) -> pd.DataFrame:
    cfg = cfg or load_c007()
    from propedge.reporting.results import read_result

    return prepare(read_result(REPO_ROOT / cfg["legs"][market]["evidence"]), market)


def prepare(df: pd.DataFrame, market: str) -> pd.DataFrame:
    """The same preparation for development and confirmation evidence."""
    df = df.copy()
    df["market"] = market
    df["date"] = pd.to_datetime(df["d"].astype(str))
    df["sk"] = df["sk"].fillna("").astype(str)
    if (df["rvw"] <= 0).any():
        raise ValueError(f"{market}: zero realised variance in a window; D-100 has no rule for it")
    return window_filter(df.sort_values("date").reset_index(drop=True), market)


def settlement_hhmm(market: str) -> str:
    from propedge.data.qc_algorithms import LEG_WINDOWS

    return LEG_WINDOWS[market][1].replace(":", "")


def window_filter(df: pd.DataFrame, market: str) -> pd.DataFrame:
    """D-101: drop windows not closed at the settlement minute; no signal on the day after one.

    Defined on timestamps only, never on prices or outcomes.
    """
    xt = df["xt"].astype(str).str.zfill(4)
    bad = xt != settlement_hhmm(market)
    bad_days = set(df.loc[bad, "d"].astype(str))
    out = df.loc[~bad].copy()
    pst = pd.to_numeric(out["pst"], errors="coerce").astype("Int64").astype(str)   # read as float
    after = pst.isin(bad_days)
    out.loc[after & (out["sk"] == ""), "sk"] = "bad_prev"
    out.attrs["dropped_late_windows"] = sorted(bad_days)
    return out.reset_index(drop=True)


# ------------------------------------------------------------------ 1. the forecast

def _har_design(panel: pd.DataFrame, lags) -> pd.DataFrame:
    """Per-market HAR regressors from that market's own previous records (trading days)."""
    out = []
    for m, g in panel.groupby("market", sort=False):
        g = g.sort_values("date").copy()
        y = np.log(g["rvw"].to_numpy())
        g["y"] = y
        s = pd.Series(y, index=g.index)
        for L in lags:
            g[f"x{L}"] = s.shift(1).rolling(L).mean() if L > 1 else s.shift(1)
        out.append(g)
    return pd.concat(out).sort_values(["date", "market"])


def har_forecast(panel: pd.DataFrame, *, lags=(1, 5, 22), min_fit: int = 60) -> pd.Series:
    """RV-hat per row, from a fit on rows strictly earlier in time. NaN during burn-in."""
    d = _har_design(panel, lags)
    xs = [f"x{L}" for L in lags]
    ok = d[xs].notna().all(axis=1)
    markets = sorted(d["market"].unique())
    rvhat = pd.Series(np.nan, index=d.index)
    for t in sorted(d.loc[ok, "date"].unique()):
        fit = d[ok & (d["date"] < t)]
        today = d[ok & (d["date"] == t)]
        counts = fit["market"].value_counts()
        today = today[today["market"].map(counts).fillna(0) >= min_fit]
        if today.empty:
            continue
        fm = [m for m in markets if counts.get(m, 0) > 0]
        X = np.column_stack([(fit["market"] == m).to_numpy(float) for m in fm] +
                            [fit[x].to_numpy() for x in xs])
        beta, *_ = np.linalg.lstsq(X, fit["y"].to_numpy(), rcond=None)
        resid = fit["y"].to_numpy() - X @ beta
        s2 = float(resid @ resid) / max(len(resid) - X.shape[1], 1)
        Xt = np.column_stack([(today["market"] == m).to_numpy(float) for m in fm] +
                             [today[x].to_numpy() for x in xs])
        rvhat.loc[today.index] = np.exp(Xt @ beta + s2 / 2.0)
    return rvhat.reindex(panel.index)


# ------------------------------------------------------------------ 2-3. stop, size, trade

def trades(df: pd.DataFrame, veh: Vehicle, *, floor_ticks: int, multiplier: float,
           budget: float, slip: dict) -> pd.DataFrame:
    """Per-day outcome in units of intended risk. Rows without a trade carry `reason`."""
    out = df.copy()
    price_sd = out["e"] * np.sqrt(out["rvhat"])
    fc_ticks = np.ceil(multiplier * price_sd / veh.tick - 1e-9)
    out["floor_bound"] = fc_ticks <= floor_ticks
    out["stop_ticks"] = np.maximum(fc_ticks, floor_ticks)
    out["contracts"] = np.floor(budget / (out["stop_ticks"] * veh.tick_value) + 1e-9)
    reason = np.where(out["rvhat"].isna(), "burn_in",
             np.where(out["sk"] != "", "skip_" + out["sk"],
             np.where(out["dir"] == 0, "no_signal",
             np.where(out["contracts"] < 1, "size_zero", ""))))
    out["reason"] = reason
    t = out["reason"] == ""
    side = out["dir"].astype(float)
    stop_dist = out["stop_ticks"] * veh.tick
    entry = out["e"] + side * slip["entry"] * veh.tick
    stop_px = entry - side * stop_dist                     # a real stop sits relative to the fill
    hit = np.where(side > 0, out["l"] <= stop_px, out["h"] >= stop_px)
    exit_px = np.where(hit, stop_px - side * slip["stop"] * veh.tick,
                       out["x"] - side * slip["flatten"] * veh.tick)
    gross = side * (exit_px - entry) * veh.point_value * out["contracts"]
    net = gross - veh.round_turn * out["contracts"]
    r = out["stop_ticks"] * veh.tick_value * out["contracts"]
    out["stop_hit"] = np.where(t, hit, False)
    out["u"] = np.where(t, net / r, np.nan)
    out["realised_over_forecast"] = np.sqrt(out["rvw"] / out["rvhat"])
    return out


# ------------------------------------------------------------------ 4. estimator and diagnostics

def _blocks(n: int, block: int, rng: np.random.Generator) -> np.ndarray:
    k = math.ceil(n / block)
    starts = rng.integers(0, max(n - block + 1, 1), size=k)
    return (starts[:, None] + np.arange(block)[None, :]).ravel()[:n]


def block_bootstrap_sd(u: np.ndarray, *, block: int, reps: int, seed: int) -> dict:
    """sd of u with a moving-block bootstrap; also the bootstrap t-statistic's upper tail."""
    u = np.asarray(u, float)
    n = len(u)
    rng = np.random.default_rng(seed)
    sds, ts = np.empty(reps), np.empty(reps)
    m0 = u.mean()                                        # used only to centre t; never returned
    for i in range(reps):
        s = u[_blocks(n, block, rng)]
        sds[i] = s.std(ddof=1)
        ts[i] = (s.mean() - m0) / (sds[i] / math.sqrt(n))
    return {"sd": float(u.std(ddof=1)), "sd_q05": float(np.quantile(sds, 0.05)),
            "sd_q95": float(np.quantile(sds, 0.95)),
            "t_q95": float(np.quantile(ts, 0.95)), "t_q05": float(np.quantile(ts, 0.05))}


def excess_kurtosis(u: np.ndarray) -> float:
    u = np.asarray(u, float)
    z = (u - u.mean()) / u.std(ddof=0)
    return float((z ** 4).mean() - 3.0)
