"""EXPLORATORY (D-518): the customer journey's measures -- pure functions on a unit's cash and event days.

A *unit* is one customer: a replay start (every trading day of a configuration's window, its trades in historical order)
or one of a recorded run's resampled paths from day 0. Day 0 is the purchase evening; day k closes the k-th session;
a month is `MONTH` sessions. Everything here is arithmetic on what the engine recorded -- no draw, no seed.

Per unit (`unit`):

* the first Combine pass, first funded account (its activation day) and first payout (the day its cash arrives), each
  within the unit's observed sessions, else blank;
* the cash spent before the first pass and before the first payout -- the deepest cash below the start over the closes
  before the event's day (`spent_before`);
* the deepest loss before the first payout, or by day `DEEP_LOSS_DAY` when there is none by then (blank on a unit
  observed fewer days);
* the net at each of `AHEAD` and the drawdown from the start within each (`exact`: the close series of a run of exactly
  that length -- a replay's last evening differs from a longer replay's by the purchases made after the final close);
* the payout rhythm within `WINDOW`: the longest gap after the first payout (between payouts and to the window's end)
  and the months after the first payout's month without a payout.

`metrics` turns a table of units into D-518's declared measures, `curve` the share reached by every day, `frontier`
each measure's best eligible configuration and the frontier flags.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

MONTH = 21
WINDOW = 126
PASS_DAYS = (5, 10, 21, 42)
FUNDED_DAYS = (10, 21, 42)
PAYOUT_DAYS = (21, 42, 63, 90)
AHEAD = (21, 63, 126)
BANKROLL = (21, 63, 126)
DEEP_LOSS_DAY = 90
EXACT = tuple(sorted(set(AHEAD) | set(BANKROLL) | {DEEP_LOSS_DAY}))
BEYOND = 1e9                                # an unreached unit's day in a percentile (then blanked)
TIE_TOL = 1e-9
HIGHER, LOWER = "higher", "lower"

#: the unit table's columns
UNIT_COLS = ("observed", "first_pass", "first_funded", "first_payout", "spent_before_first_pass",
             "spent_before_first_payout", "deepest_loss_before_payout_or_90",
             *[f"net_{h}" for h in AHEAD], *[f"drawdown_{h}" for h in BANKROLL],
             "longest_gap_after_first_payout", "months_after_first_payout", "months_without_payout",
             "passes_in_window", "payouts_in_window")


def _first(days: Iterable[int], observed: int) -> float:
    d = sorted(int(x) for x in days if 0 <= int(x) <= int(observed))
    return float(d[0]) if d else float("nan")


def spent_before(rel: np.ndarray, day: int) -> float:
    """The deepest cash below the start over the closes before `day` (closes 0 .. day-1; 0 when there are none).
    `rel[k]` is the cash at close k less the starting bankroll."""
    k = int(day)
    if k <= 0:
        return 0.0
    return float(max(0.0, -float(np.min(rel[:k]))))


def drawdown_from_start(rel: np.ndarray) -> float:
    """D-508's `drawdown_from_start`: the cash below the start at its lowest close (0 at the start itself)."""
    return float(max(0.0, -float(np.min(np.concatenate([[0.0], rel])))))


def unit(cash: Sequence[float], initial: float, pass_days: Iterable[int], funded_days: Iterable[int],
         pay_days: Iterable[int], *, exact: Mapping[int, Sequence[float]] | None = None) -> dict[str, Any]:
    """One unit's journey. `cash` holds the closes 0 .. observed of the unit's longest run; `exact[h]`, when given, the
    closes 0 .. h of a run of exactly h sessions (else the first h + 1 of `cash`)."""
    cash = np.asarray(cash, float)
    observed = int(len(cash) - 1)
    rel = cash - float(initial)
    passes = sorted(int(d) for d in pass_days if 0 <= int(d) <= observed)
    funded = sorted(int(d) for d in funded_days if 0 <= int(d) <= observed)
    pays = sorted(int(d) for d in pay_days if 0 <= int(d) <= observed)
    fp, ff, fy = _first(passes, observed), _first(funded, observed), _first(pays, observed)
    out: dict[str, Any] = {"observed": observed, "first_pass": fp, "first_funded": ff, "first_payout": fy,
                           "spent_before_first_pass": spent_before(rel, int(fp)) if np.isfinite(fp) else float("nan"),
                           "spent_before_first_payout": spent_before(rel, int(fy)) if np.isfinite(fy) else float("nan")}

    def closes(h: int) -> np.ndarray | None:
        if exact is not None and int(h) in exact:
            x = np.asarray(exact[int(h)], float)
            if len(x) != int(h) + 1:
                raise ValueError(f"exact[{h}] holds {len(x)} closes, not {int(h) + 1}")
            return x - float(initial)
        if observed < int(h):
            return None
        return rel[:int(h) + 1]

    if np.isfinite(fy) and fy <= DEEP_LOSS_DAY and observed >= DEEP_LOSS_DAY:
        out["deepest_loss_before_payout_or_90"] = spent_before(rel, int(fy))
    else:
        r90 = closes(DEEP_LOSS_DAY)
        out["deepest_loss_before_payout_or_90"] = drawdown_from_start(r90) if r90 is not None else float("nan")
    for h in AHEAD:
        r = closes(h)
        out[f"net_{h}"] = float(r[-1]) if r is not None else float("nan")
    for h in BANKROLL:
        r = closes(h)
        out[f"drawdown_{h}"] = drawdown_from_start(r) if r is not None else float("nan")
    in_w = [d for d in pays if d <= WINDOW]
    if observed >= WINDOW and in_w:
        marks = in_w + [WINDOW]
        out["longest_gap_after_first_payout"] = float(max(b - a for a, b in zip(marks, marks[1:])))
        m0 = (in_w[0] - 1) // MONTH
        months = list(range(m0 + 1, WINDOW // MONTH))
        paid = {(d - 1) // MONTH for d in in_w}
        out["months_after_first_payout"] = len(months)
        out["months_without_payout"] = sum(1 for m in months if m not in paid)
    else:
        out["longest_gap_after_first_payout"] = float("nan")
        out["months_after_first_payout"] = 0 if observed >= WINDOW else float("nan")
        out["months_without_payout"] = 0 if observed >= WINDOW else float("nan")
    out["passes_in_window"] = sum(1 for d in passes if d <= WINDOW)
    out["payouts_in_window"] = len(in_w)
    return out


# ------------------------------------------------------------------------------------------------ the measures


def _q(x: np.ndarray, p: float) -> float:
    return float(np.percentile(x, p)) if len(x) else float("nan")


def _days_q(first: np.ndarray, last: int, p: float) -> float:
    """A percentile of the days to an event over units observed `last` days, an unreached unit beyond; blank when the
    percentile falls beyond `last`."""
    v = np.where(np.isfinite(first) & (first <= last), first, BEYOND)
    q = _q(v, p)
    return q if np.isfinite(q) and q <= last else float("nan")


def metrics(u: pd.DataFrame, subscription: float) -> list[dict[str, Any]]:
    """D-518 (3)'s declared measures over a table of units: (milestone, measure, at, value, direction, n)."""
    rows: list[dict[str, Any]] = []
    obs = u["observed"].to_numpy(int)

    def add(milestone, measure, at, value, direction, n):
        rows.append({"milestone": milestone, "measure": measure, "at_days": at, "value": float(value),
                     "direction": direction, "n": int(n)})

    for ms, col, days, spent in (("first_pass", "first_pass", PASS_DAYS, "spent_before_first_pass"),
                                 ("first_funded", "first_funded", FUNDED_DAYS, None),
                                 ("first_payout", "first_payout", PAYOUT_DAYS, "spent_before_first_payout")):
        first = u[col].to_numpy(float)
        for d in days:
            m = obs >= d
            add(ms, "chance_by", d, np.mean(np.isfinite(first[m]) & (first[m] <= d)) if m.any() else np.nan, HIGHER,
                m.sum())
        last = max(days)
        m = obs >= last
        for p, name in ((50, "days_p50"), (90, "days_p90")):
            add(ms, name, last, _days_q(first[m], last, p), LOWER, m.sum())
        if spent is not None:
            r = m & np.isfinite(first) & (first <= last)
            s = u[spent].to_numpy(float)[r]
            add(ms, "spent_before_p50", last, _q(s, 50), LOWER, r.sum())
            add(ms, "spent_before_p90", last, _q(s, 90), LOWER, r.sum())
    dl = u["deepest_loss_before_payout_or_90"].to_numpy(float)
    m = np.isfinite(dl)
    add("first_payout", "deepest_loss_before_p50", DEEP_LOSS_DAY, _q(dl[m], 50), LOWER, m.sum())
    add("first_payout", "deepest_loss_before_p90", DEEP_LOSS_DAY, _q(dl[m], 90), LOWER, m.sum())
    for h in AHEAD:
        x = u[f"net_{h}"].to_numpy(float)
        x = x[np.isfinite(x)]
        add("ahead", "share_positive", h, np.mean(x > 0) if len(x) else np.nan, HIGHER, len(x))
        add("ahead", "net_p50", h, _q(x, 50), HIGHER, len(x))
        add("ahead", "net_p10", h, _q(x, 10), HIGHER, len(x))
    g = u["longest_gap_after_first_payout"].to_numpy(float)
    g = g[np.isfinite(g)]
    add("payout_rhythm", "longest_gap_p50", WINDOW, _q(g, 50), LOWER, len(g))
    add("payout_rhythm", "longest_gap_p90", WINDOW, _q(g, 90), LOWER, len(g))
    ma = pd.to_numeric(u["months_after_first_payout"], errors="coerce").to_numpy(float)
    mn = pd.to_numeric(u["months_without_payout"], errors="coerce").to_numpy(float)
    ok = np.isfinite(ma) & (ma > 0)
    add("payout_rhythm", "share_months_without_payout", WINDOW,
        float(mn[ok].sum() / ma[ok].sum()) if ok.any() else np.nan, LOWER, ok.sum())
    for h in BANKROLL:
        x = u[f"drawdown_{h}"].to_numpy(float)
        x = x[np.isfinite(x)]
        add("bankroll", "drawdown_p95_plus_subscription", h, _q(x, 95) + float(subscription) if len(x) else np.nan,
            LOWER, len(x))
    return rows


def curve(u: pd.DataFrame, last: int = WINDOW) -> list[dict[str, Any]]:
    """The share of units observed `d` days that reached each first event by day d, d = 1 .. last."""
    obs = u["observed"].to_numpy(int)
    out = []
    for ms in ("first_pass", "first_funded", "first_payout"):
        first = u[ms].to_numpy(float)
        for d in range(1, int(last) + 1):
            m = obs >= d
            out.append({"milestone": ms, "day": d, "n": int(m.sum()),
                        "share_reached": float(np.mean(np.isfinite(first[m]) & (first[m] <= d))) if m.any()
                        else float("nan")})
    return out


# ------------------------------------------------------------------------------------------------ the frontier


def _score(v: float, direction: str) -> float:
    """Higher is better after this; a blank is the worst."""
    if not np.isfinite(v):
        return -np.inf
    return float(v) if direction == HIGHER else -float(v)


def best_flags(m: pd.DataFrame, eligible: Sequence[str]) -> pd.Series:
    """For a metric table (config, measure key, value, direction), True where the configuration is eligible and best at
    that measure among the eligible (ties all best, to `TIE_TOL`). A measure blank for every eligible configuration, or
    equal for all of them (with two or more), distinguishes nothing and marks none."""
    out = pd.Series(False, index=m.index)
    el = set(eligible)
    for _, g in m.groupby("key", sort=False):
        g = g[g["config"].isin(el)]
        if g.empty:
            continue
        s = np.array([_score(v, d) for v, d in zip(g["value"], g["direction"])])
        if not np.isfinite(s).any():
            continue
        top = np.max(s)
        hit = (s >= top - TIE_TOL) if np.isfinite(top) else np.zeros(len(s), bool)
        if len(s) >= 2 and hit.all():
            continue
        out.loc[g.index[hit]] = True
    return out


def frontier(m: pd.DataFrame, eligible: Sequence[str]) -> list[dict[str, Any]]:
    """Each eligible configuration's best count, frontier flag (best at one or more measures) and Pareto flag (no other
    eligible configuration at least as good on every measure and better on one)."""
    el = [c for c in dict.fromkeys(m["config"]) if c in set(eligible)]
    best = best_flags(m, el)
    keys = list(dict.fromkeys(m["key"]))
    S = {c: np.array([_score(*m[(m["config"] == c) & (m["key"] == k)][["value", "direction"]].iloc[0])
                      if ((m["config"] == c) & (m["key"] == k)).any() else -np.inf for k in keys]) for c in el}
    rows = []
    for c in el:
        dominated = False
        for o in el:
            if o == c:
                continue
            a, b = S[o], S[c]
            ge = (a >= b - TIE_TOL) | (np.isneginf(a) & np.isneginf(b))
            gt = (a > b + TIE_TOL) & ~np.isneginf(a) | (np.isfinite(a) & np.isneginf(b))
            if ge.all() and gt.any():
                dominated = True
                break
        n = int(best[m["config"] == c].sum())
        rows.append({"config": c, "best_count": n, "frontier": n >= 1, "pareto": not dominated,
                     "best_at": " ".join(m.loc[(m["config"] == c) & best, "key"].astype(str))})
    return rows


def metric_key(milestone: str, measure: str, at: Any) -> str:
    return f"{milestone}:{measure}@{int(at)}"


__all__ = ["MONTH", "WINDOW", "PASS_DAYS", "FUNDED_DAYS", "PAYOUT_DAYS", "AHEAD", "BANKROLL", "DEEP_LOSS_DAY", "EXACT",
           "UNIT_COLS", "HIGHER", "LOWER", "spent_before", "drawdown_from_start", "unit", "metrics", "curve",
           "best_flags", "frontier", "metric_key"]
