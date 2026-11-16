"""EXPLORATORY (D-550): family A4 -- the coin-benchmarked strategy atlas. Pure functions; `scripts/a4_coin_atlas.py`
reads the bars and writes the result.

**The menu** (D-550 (1), fixed before anything was read): 34 patterns of the atlas's own kinds (`atlas_core.a_events`)
at FV3-C's 25-point rung (100 ticks) and the coin's 37.5-point stop (150 ticks), entry delays 0 and 5 minutes (the
atlas's): 136 strategies. A pattern the atlas code cannot build at a listed parameter is dropped and listed before any
outcome is computed (`build_menu`).

**The lift** (D-550 (3)): a strategy's trade is its pattern's event on the event's side; its coin twin is the same entry
with the side a fair coin, whose expected net R is the mean of the two sides' net R at the same entry. So, per trade and
offered R, lift = r(event side) - (r(long) + r(short)) / 2 = (r(event side) - r(other side)) / 2 -- exact, no simulated
coin. The fade's lift is minus the follow's, so follow and fade are one two-sided test.

**The noise guard** (D-550 (4)): a stationary block bootstrap (Politis & Romano 1994) of trading days -- blocks of
geometric length, mean 21 sessions; 2,000 replicates; seed 20261210 -- resampling the SAME day indices for every
strategy and R jointly. Each hypothesis (strategy, R) is recentred under the null (each day's summed lift less the
observed mean lift times that day's trades), so every replicate's mean lift is noise around zero. The statistic is the
**studentised** mean lift, t = mean / sd*, sd* the hypothesis's own bootstrap standard deviation: the hypotheses differ
widely in variance (a 3R outcome against a quarter-R one; a 5-minute breakout's thousands of trades against a daily
range's hundreds), and an unstudentised maximum would be the noisiest hypothesis's almost every time, so the family-wise
test would have no power for the rest (Romano & Wolf 2005; Hansen 2005 makes the same point for White's 2000 reality
check). A hypothesis survives when |t| exceeds the 95th percentile of the replicates' max |t*| over every hypothesis --
family-wise at 5 % over the whole menu. Benjamini-Hochberg at 10 % on each hypothesis's own bootstrap p-value is
reported beside, never selecting.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

DECISION = "D-550"
FAMILY = "A4"
STOPS = (100, 150)                         # ticks: FV3-C's 25-point rung and the coin's 37.5-point stop
DELAYS = (0, 5)                            # minutes (bars): the atlas's entry delays
OFFERED_R = (0.25, 1.0, 1.5, 2.0, 2.5, 3.0)   # the no-closure table's offered R (zero_edge_decomposition.policy_rrs)
BOOT_REPS = 2000
BOOT_BLOCK = 21.0                          # mean block length in sessions
BOOT_SEED = 20261210                       # D-550 (4), fixed before anything was read
FWER = 0.05
BH_Q = 0.10
SUPPORTED_KINDS = ("brk", "inside", "nbar", "orb", "pdhl", "engulf")


# ------------------------------------------------------------------------------------------------ the menu


def menu_patterns() -> list[dict[str, Any]]:
    """D-550 (1)'s 34 patterns, in its order, each with a name."""
    out: list[dict[str, Any]] = []
    for k in (5, 10, 15, 30, 60, 90):
        out.append({"name": f"brk{k}", "kind": "brk", "k": k})
    for k in (5, 15, 30, 60):
        out.append({"name": f"inside{k}", "kind": "inside", "k": k})
    for k in (5, 15, 30):
        for n in (2, 4, 8):
            out.append({"name": f"nbar{k}x{n}", "kind": "nbar", "k": k, "n": n})
    for m in (5, 15, 30, 60):
        out.append({"name": f"orb_rth{m}", "kind": "orb", "open_ct": "08:30", "m": m})
    for label, ct in (("globex", "17:00"), ("london", "02:00")):
        for m in (15, 30, 60):
            out.append({"name": f"orb_{label}{m}", "kind": "orb", "open_ct": ct, "m": m})
    out.append({"name": "pdhl", "kind": "pdhl"})
    for k in (5, 15, 30, 60):
        out.append({"name": f"engulf{k}", "kind": "engulf", "k": k})
    return out


def _clock(ct: str) -> int:
    """A CT time on the trading-day clock (minutes after 17:00 CT; 17:00 itself is slot 0) -- `atlas_walk._clock`."""
    from propedge.outcomes.collect_core import c_slot

    if str(ct) == "17:00":
        return 0
    hh, mm = (int(x) for x in str(ct).split(":"))
    return int(c_slot(hh, mm))


def to_core(p: Mapping[str, Any]) -> dict[str, Any]:
    """A menu pattern as `atlas_core.a_events` reads it (`atlas_walk.params`' conversion: an orb's open as a slot)."""
    q = {k: v for k, v in p.items() if k != "name"}
    if q["kind"] == "orb":
        q["open_slot"] = _clock(q.pop("open_ct"))
    return q


def _synthetic_day(seed: int = 1) -> tuple[list, list, list, list]:
    """A random-walk day on the trading-day clock (1 .. 1330) -- a structural test bed, no market data."""
    rng = np.random.default_rng(seed)
    n = 1331
    c = 15000 + np.cumsum(rng.normal(0, 4, n))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + np.abs(rng.normal(0, 2, n))
    l = np.minimum(o, c) - np.abs(rng.normal(0, 2, n))
    lists = [[None] + [float(x) for x in a[1:]] for a in (o, h, l, c)]
    return tuple(lists)  # type: ignore[return-value]


def build_menu(first_slot: int, last_slot: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """(the buildable patterns, every menu row with `buildable` and its reason): a pattern is built when its kind is the
    atlas's and its parameters are positive integers that `atlas_core.a_events` builds on a synthetic day without
    error -- checked before any market outcome is computed (D-550 (1))."""
    from propedge.outcomes import atlas_core

    o, h, l, c = _synthetic_day()
    kept, rows = [], []
    for p in menu_patterns():
        why = ""
        if p["kind"] not in SUPPORTED_KINDS:
            why = f"kind {p['kind']!r} is not the atlas's"
        for key in ("k", "n", "m"):
            if not why and key in p and not (isinstance(p[key], int) and p[key] > 0):
                why = f"{key} = {p[key]!r} is not a positive integer"
        if not why:
            try:
                atlas_core.a_events(o, h, l, c, {"patterns": [to_core(p)], "first_slot": first_slot,
                                                 "last_slot": last_slot, "prior": (15010.0, 14990.0)})
            except Exception as exc:                     # noqa: BLE001 -- any failure drops the pattern, listed
                why = f"atlas_core.a_events failed: {exc!r}"
        rows.append({"pattern": p["name"], "kind": p["kind"], "params": {k: v for k, v in p.items()
                                                                          if k not in ("name", "kind")},
                     "buildable": not why, "dropped_reason": why})
        if not why:
            kept.append(p)
    return kept, rows


def strategies(patterns: Sequence[Mapping[str, Any]], stops=STOPS, delays=DELAYS) -> list[dict[str, Any]]:
    """Every (pattern, stop, delay): the strategy id, in a fixed order (pattern, then stop, then delay)."""
    out = []
    for pi, p in enumerate(patterns):
        for S in stops:
            for d in delays:
                out.append({"strategy": f"{p['name']}_s{int(S)}_d{int(d)}", "pattern": p["name"], "pattern_index": pi,
                            "stop_ticks": int(S), "delay": int(d)})
    return out


# ------------------------------------------------------------------------------------------------ the lift


def net_r(gross_ticks: np.ndarray, kind: np.ndarray, stop_ticks: int, fee: float, *, tick_value: float,
          entry_ticks: float) -> np.ndarray:
    """FV3's settlement in R (`atlas_a3.cell_trades`' arithmetic): gross ticks over the stop, less a tick at entry, the
    fee per micro-equivalent and the exit's ticks by kind, all over the stop's dollar risk."""
    from propedge.research.fv3_rung_walk import EXIT_TICKS

    S, td = float(stop_ticks), float(tick_value)
    exit_ticks = np.vectorize(lambda k: float(EXIT_TICKS[int(k)]), otypes=[float])(np.asarray(kind))
    return np.asarray(gross_ticks, float) / S - (float(entry_ticks) * td + float(fee) + exit_ticks * td) / (S * td)


def lift(r_side: np.ndarray, r_other: np.ndarray) -> np.ndarray:
    """The event side's net R less its coin twin's expected net R (the two sides' mean): (r_side - r_other) / 2."""
    return (np.asarray(r_side, float) - np.asarray(r_other, float)) / 2.0


# ------------------------------------------------------------------------------------------------ the noise guard


def stationary_counts(n_days: int, reps: int = BOOT_REPS, mean_block: float = BOOT_BLOCK,
                      seed: int = BOOT_SEED) -> np.ndarray:
    """(reps, n_days): how many times each day appears in each stationary-bootstrap replicate (Politis & Romano 1994:
    a start drawn uniformly, then each next day the following one -- circularly -- with probability 1 - 1/mean_block,
    else a fresh uniform start), each replicate n_days long. One generator, seeded, drawn in a fixed order."""
    rng = np.random.default_rng(int(seed))
    T, p = int(n_days), 1.0 / float(mean_block)
    counts = np.zeros((int(reps), T), dtype=np.int32)
    for b in range(int(reps)):
        new = rng.random(T) < p
        new[0] = True
        starts = rng.integers(0, T, size=T)
        idx = np.empty(T, dtype=np.int64)
        cur = 0
        for i in range(T):
            cur = starts[i] if new[i] else (cur + 1) % T
            idx[i] = cur
        counts[b] = np.bincount(idx, minlength=T)
    return counts


def maxstat_test(day_sum: np.ndarray, day_n: np.ndarray, counts: np.ndarray, *, fwer: float = FWER
                 ) -> dict[str, Any]:
    """The family-wise test over hypotheses h: `day_sum` (days, H) each day's summed lift, `day_n` (days, H) each day's
    trades, `counts` (reps, days) the replicates. Returns per hypothesis the mean lift, its bootstrap sd, t, the
    individual two-sided p, and the critical value (the 1 - fwer quantile of max |t*|) with the max distribution's
    quantiles. A hypothesis with no trades is NaN and never survives."""
    L = np.asarray(day_sum, float)
    N = np.asarray(day_n, float)
    tot_n = N.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = np.where(tot_n > 0, L.sum(axis=0) / tot_n, np.nan)
        centred = L - np.nan_to_num(mean)[None, :] * N              # the null: each day's lift less mean x trades
        C = np.asarray(counts, float)
        num = C @ centred                                           # (reps, H)
        den = C @ N
        star = np.where(den > 0, num / den, np.nan)
        sd = np.nanstd(star, axis=0, ddof=1)
        t = np.where(sd > 0, mean / sd, np.nan)
        tstar = np.where(sd[None, :] > 0, star / sd[None, :], np.nan)
    maxabs = np.nanmax(np.abs(tstar), axis=1)
    crit = float(np.quantile(maxabs, 1.0 - float(fwer)))
    with np.errstate(invalid="ignore"):
        p = np.array([float(np.mean(np.abs(tstar[:, h]) >= abs(t[h]))) if np.isfinite(t[h]) else np.nan
                      for h in range(L.shape[1])])
    return {"mean": mean, "sd": sd, "t": t, "p": p, "crit": crit, "trades": tot_n,
            "survives": np.where(np.isfinite(t), np.abs(t) > crit, False),
            "max_quantiles": {f"q{int(q * 100)}": float(np.quantile(maxabs, q)) for q in (0.5, 0.9, 0.95, 0.99)}}


def benjamini_hochberg(p: np.ndarray, q: float = BH_Q) -> np.ndarray:
    """BH's rejections at level q among the finite p-values (NaN never rejected)."""
    p = np.asarray(p, float)
    ok = np.isfinite(p)
    out = np.zeros(len(p), dtype=bool)
    m = int(ok.sum())
    if m == 0:
        return out
    idx = np.where(ok)[0]
    order = idx[np.argsort(p[idx], kind="stable")]
    ranks = np.arange(1, m + 1)
    below = p[order] <= q * ranks / m
    if below.any():
        kmax = int(np.max(np.where(below)[0]))
        out[order[: kmax + 1]] = True
    return out


def hypothesis_frame(strats: Sequence[Mapping[str, Any]], rrs: Sequence[float] = OFFERED_R) -> pd.DataFrame:
    """One row per (strategy, R) in the column order of the accumulators: strategy-major, R-minor."""
    return pd.DataFrame([{**s, "R": float(R)} for s in strats for R in rrs])


__all__ = ["DECISION", "FAMILY", "STOPS", "DELAYS", "OFFERED_R", "BOOT_REPS", "BOOT_BLOCK", "BOOT_SEED", "FWER", "BH_Q",
           "menu_patterns", "to_core", "build_menu", "strategies", "net_r", "lift", "stationary_counts",
           "maxstat_test", "benjamini_hochberg", "hypothesis_frame"]
