"""Wave 3.1 (`docs/plans/RESTART_PLAN_journey_objective.md`, lane `wt-user`): the journey measures `docs/MEASURES.md`
marks "to build", as it defines them -- pure functions on one unit's path or on many units' values, numpy only (no
engine, no draw, no data; safe to import in any process). Each function names its measure's number in MEASURES.md.

**The unit's path** (MEASURES.md 1.1, 1.2). `rel[k]` is the unit's net cash at close k (payouts received less every
fee paid by it), k = 0 .. its observed closes; `arrivals` its payouts' (arrival close, cash) in arrival order (U1's
`payout_arrivals`); `first_pass` its first Combine pass close (blank: none). **Every field read at horizon h is read
from closes 0 .. h only**: a function that reads a horizon refuses (`ValueError`) a path holding fewer closes -- such a
unit is not in `E_h`, and reading it would read outside its window.

**The rules of MEASURES.md 1.3 carried here.**
* Days to an event within a window W: an unreached unit is censored at W + 1 (`user_measures.censored_days`); the
  percentile is never blank.
* A dollar quantity up to an event: an unreached unit's value through W is a lower bound, flagged censored, and a
  percentile of them follows **the strict rule** (`strict_quantiles`): it is exact only if every censored unit's lower
  bound lies strictly above it -- and, as the rule's "only if" leaves room for (Wave 3.1's reading, reported with it),
  only if the percentile does not move when every censored unit's value is raised without limit (numpy's linear
  percentile interpolates between two order statistics; a censored unit at the upper one moves it, even above it).
  Otherwise the percentile reads "at least" that value.
* "Ahead" is a net above `TOL` (1e-6), break-even a net at or above `-TOL` (`user_measures.TOL`).

**What is here, by measure.** (1), (5), (9): `days_reading` (the censored headline; Stage 2's blanking form beside
through `user_measures.days_quantile`). (2), (6): `spent_to_event` per unit, `strict_quantiles` over `E_W`. (3):
`evaluations_to_first_pass`. Section 2's `P_B`: `months_ahead_under` per unit, `p_bankroll` (with the sub-reading
"before the first payout"). (13): `share_ahead_at` (S4a, S4b). (15): `return_on_money_at_risk`. (16):
`monthly_changes`, `monthly_net_4_12`. (21): `longest_wait`. (24): `bankroll_state`, `bankroll_stop`. (25):
`peak_oop`. (30): `workload`. (31): `account_ending`, `account_lifetime`, `km_survival`, `km_quantile`,
`funded_lifetime`. (32): `by_year`, `subset_reading`. (33): `break_even_denial_rate`, `exposed_share`. (34):
`variance_decomposition`. (37): `supply`. (38): `coverage`, `trading_day_of`. (39): `idle`. Section 1.4's three coin
readings: `coin_readings` (per-unit measures) and `design_coin_readings` (design-level measures: readings 1 and 3).

Not here: (28) and (29) are stress arms of a runner (the missed or late signals re-simulated; Q-148's worse fills), and
(33)'s ladder needs the enforcement stream seeded apart from the coin (`user_beside.base_problems`): only the reading of
a ladder already run is here. Every budget B, window W, latency L, session window, news window, grid of p and coin seed
is a parameter: none is chosen here (MEASURES.md 7: a value set with the held-out years visible is a ledger entry).
"""
from __future__ import annotations

import math
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np

from extended import user_measures as M

MONTH = M.MONTH                      # 21 sessions
MONTHS = M.MONTHS                    # 12
YEAR = MONTH * MONTHS                # 252 sessions
TOL = M.TOL                          # 1e-6 dollars
PERCENTILES = M.PERCENTILES          # (10, 50, 90)
NAN = float("nan")

#: (24)'s three states, in the order they are reported
STATES = ("paid_within", "run_out", "censored")
#: (31): how a funded account ends -- the endings by a firm rule are the event (lost), every other is censored
LOST = ("breach", "denied", "ftp")
CENSORED = ("policy", "live", "cap", "window", "horizon")
ENDINGS = LOST + CENSORED


# ------------------------------------------------------------------------------------------------ the unit's path


def closes(rel: Sequence[float], h: int, what: str = "a reading") -> np.ndarray:
    """The unit's closes 0 .. h (`rel[:h + 1]`); refused (`ValueError`) when it holds fewer -- the unit is not in
    `E_h` -- or a close is blank."""
    r = np.asarray(rel, float)
    h = int(h)
    if h < 0 or len(r) < h + 1:
        raise ValueError(f"{what} at horizon {h} reads closes 0 .. {h}; the unit holds {len(r)} (it is not in E_{h})")
    r = r[:h + 1]
    if not np.isfinite(r).all():
        raise ValueError(f"{what}: a blank close among 0 .. {h}")
    return r


def _day(x: Any) -> float:
    """An event's close as a float (NaN for none)."""
    if x is None:
        return NAN
    v = float(x)
    return v if math.isfinite(v) else NAN


def first_within(day: Any, window: int) -> float:
    """The event's close if it came by close `window`, else NaN."""
    v = _day(day)
    return v if math.isfinite(v) and v <= int(window) else NAN


def first_arrival(arrivals: Iterable[tuple[int, float]], window: int | None = None) -> float:
    """The first payout's arrival close (within `window` when given), NaN when none."""
    days = sorted(int(d) for d, _ in arrivals)
    if window is not None:
        days = [d for d in days if d <= int(window)]
    return float(days[0]) if days else NAN


# ------------------------------------------------------------------------------------------------ (1), (5), (9): days


def days_reading(first: Sequence[float], window: int, pcts: Sequence[int] = PERCENTILES) -> dict[str, Any]:
    """(1), (5), (9), (21)'s days form over the units of `E_W`: the censored percentiles (an unreached unit at W + 1,
    never blank), the share reached by W, the counts. Stage 2's blanking form is `user_measures.days_quantile`'s
    default, kept beside by the caller."""
    x = M.censored_days(np.asarray(first, float), window)
    out: dict[str, Any] = {f"p{p}": (float(np.percentile(x, p)) if len(x) else NAN) for p in pcts}
    hit = x <= int(window)
    out["share_by"] = float(hit.mean()) if len(x) else NAN
    out["n"], out["n_censored"] = int(len(x)), int((~hit).sum())
    return out


# ------------------------------------------------------------------------------------------------ the strict rule


def strict_quantiles(x: Sequence[float], censored: Sequence[bool], pcts: Sequence[int] = PERCENTILES
                     ) -> dict[str, Any]:
    """Percentiles of a dollar quantity over every unit, censored units at their lower bounds, by MEASURES.md 1.3's
    strict rule (N-1): `p{p}` the percentile, `p{p}_exact` whether it is exact -- every censored lower bound strictly
    above it, and the percentile unmoved when every censored value is raised without limit (the module docstring);
    otherwise it reads "at least" `p{p}`. With no censored unit every percentile is exact."""
    v = np.asarray(x, float)
    c = np.asarray(censored, bool)
    if v.shape != c.shape:
        raise ValueError("one censored flag a value")
    if not np.isfinite(v).all():
        raise ValueError("a value is blank: every unit of E_W has a value or a lower bound")
    out: dict[str, Any] = {"n": int(len(v)), "n_censored": int(c.sum())}
    if not len(v):
        for p in pcts:
            out[f"p{p}"], out[f"p{p}_exact"] = NAN, False
        return out
    span = float(np.max(np.abs(v))) if len(v) else 0.0
    raised = np.where(c, 4.0 * span + 1e12, v)
    for p in pcts:
        q = float(np.percentile(v, p))
        q_hi = float(np.percentile(raised, p))
        out[f"p{p}"] = q
        out[f"p{p}_exact"] = bool(((v[c] > q).all() if c.any() else True) and q_hi == q)
    return out


# ------------------------------------------------------------------------------------------------ (2), (3), (6)


def spent_to_event(rel: Sequence[float], event_day: Any, window: int) -> tuple[float, bool]:
    """(2) and (6) per unit, on closes 0 .. W: `spent_before(rel, k*)` with k* the event's close if it came by W
    (exact), else W + 1 (every close 0 .. W counts; a censored lower bound). Returns (the value, censored)."""
    r = closes(rel, window, "the cash to an event")
    e = first_within(event_day, window)
    if math.isfinite(e):
        return M.spent_before(r, int(e)), False
    return M.spent_before(r, int(window) + 1), True


def evaluations_to_first_pass(purchase_days: Iterable[int], first_pass: Any, window: int) -> tuple[float, bool]:
    """(3) per unit: the Combines bought on a close before the first pass (a purchase is at a close's end, so one
    bought on the pass close is bought after it); for a unit not passed by W, those bought through close W, a censored
    lower bound. Returns (the count, censored)."""
    days = [int(d) for d in purchase_days]
    fp = first_within(first_pass, window)
    if math.isfinite(fp):
        return float(sum(1 for d in days if d < fp)), False
    return float(sum(1 for d in days if d <= int(window))), True


# ------------------------------------------------------------------------------------------------ section 2: P_B


def months_ahead_under(rel: Sequence[float], budget: float | None = None, *, before_first_payout: bool = False,
                       arrivals: Iterable[tuple[int, float]] = ()) -> int:
    """Section 2's per-unit count (0 .. 3) on closes 0 .. 63: the months m in {1, 2, 3} with `rel[21 m] > TOL` and,
    under a budget B, `max(0, -min_{0 <= j < 21 m} rel[j]) <= B` -- the peak out-of-pocket through the month close
    (spending exactly B is within it). `budget` None: P's own count. `before_first_payout=True`: the named sub-reading,
    the spending before the first payout (`spent_before(rel, first arrival)`, the arrivals by 21 m) in place of the
    peak."""
    r = closes(rel, MONTH * 3, "P")
    pays = list(arrivals)
    c = 0
    for m in (1, 2, 3):
        k = MONTH * m
        if not r[k] > TOL:
            continue
        if budget is not None:
            if before_first_payout:
                fy = first_arrival(pays, k)
                if not math.isfinite(fy):
                    raise ValueError("a unit ahead has no payout by the month close: the path is inconsistent")
                spent = M.spent_before(r, int(fy))
            else:
                spent = M.spent_before(r, k)
            if spent > float(budget):
                continue
        c += 1
    return c


def p_bankroll(rels: Sequence[Sequence[float]], budget: float | None = None, *, before_first_payout: bool = False,
               arrivals: Sequence[Iterable[tuple[int, float]]] | None = None) -> dict[str, Any]:
    """Section 2: P (no budget) or `P_B` over the units of `E_63` -- the months ahead (under B) summed over units,
    over 3 n; the three month shares beside. With `before_first_payout=True`, the sub-reading (`arrivals` one list a
    unit)."""
    n = len(rels)
    if before_first_payout and (arrivals is None or len(arrivals) != n):
        raise ValueError("the sub-reading needs each unit's arrivals")
    hits = np.zeros((n, 3), bool)
    for i, r in enumerate(rels):
        rr = closes(r, MONTH * 3, "P")
        pays = list(arrivals[i]) if arrivals is not None else []
        for j, m in enumerate((1, 2, 3)):
            hits[i, j] = _ahead_under_at(rr, m, budget, before_first_payout, pays)
        if int(hits[i].sum()) != months_ahead_under(rr, budget, before_first_payout=before_first_payout,
                                                    arrivals=pays):
            raise RuntimeError("the month shares and the per-unit count disagree")
    out = {f"share_month_{m}": (float(hits[:, j].mean()) if n else NAN) for j, m in enumerate((1, 2, 3))}
    out["P"] = float(hits.sum() / (3 * n)) if n else NAN
    out["n"] = n
    return out


def _ahead_under_at(r: np.ndarray, m: int, budget: float | None, before_first_payout: bool,
                    arrivals: Sequence[tuple[int, float]]) -> bool:
    """Whether a unit counts as ahead under B at month m (section 2), on its closes 0 .. 63."""
    k = MONTH * m
    if not r[k] > TOL:
        return False
    if budget is None:
        return True
    if before_first_payout:
        fy = first_arrival(arrivals, k)
        if not math.isfinite(fy):
            raise ValueError("a unit ahead has no payout by the month close: the path is inconsistent")
        spent = M.spent_before(r, int(fy))
    else:
        spent = M.spent_before(r, k)
    return bool(spent <= float(budget))


def share_ahead_at(rels: Sequence[Sequence[float]], k: int) -> dict[str, Any]:
    """(13)'s S4a (k = 126) and S4b (k = 252), and any month's share ahead: the share of `E_k` with `rel[k] > TOL`."""
    x = np.array([closes(r, k, "a share ahead")[int(k)] for r in rels], float)
    return {"share": float((x > TOL).mean()) if len(x) else NAN, "n": int(len(x))}


# ------------------------------------------------------------------------------------------------ (15), (16), (25)


def peak_oop(rel: Sequence[float], h: int = YEAR) -> float:
    """(25): `PeakOOP = max(0, -min_{0 <= k <= h} rel[k])` -- Stage 2's `drawdown_from_start` over closes 0 .. h."""
    return M.peak_through(closes(rel, h, "the peak out-of-pocket"), int(h))


def return_on_money_at_risk(rel: Sequence[float], h: int = YEAR) -> float:
    """(15): `rel[h] / PeakOOP` over closes 0 .. h; blank (NaN) when the peak is zero (no real start: day 0 books the
    purchase)."""
    r = closes(rel, h, "the return on money at risk")
    peak = M.peak_through(r, int(h))
    return float(r[int(h)] / peak) if peak > 0 else NAN


def monthly_changes(rel: Sequence[float], months: int = MONTHS) -> np.ndarray:
    """(16), (18), (19)'s `D_m`: `D_1 = rel[21]` (from zero: day 0's fees fall in month 1), `D_m = rel[21 m] -
    rel[21 (m - 1)]`."""
    r = closes(rel, MONTH * int(months), "the monthly changes")
    ends = r[[MONTH * m for m in range(1, int(months) + 1)]]
    return np.diff(np.concatenate([[0.0], ends]))


def monthly_net_4_12(rel: Sequence[float]) -> dict[str, float]:
    """(16) per unit on closes 0 .. 252: the median of `D_4 .. D_12` (the headline) and their mean,
    `(rel[252] - rel[63]) / 9`, beside."""
    d = monthly_changes(rel, MONTHS)[3:]
    r = closes(rel, YEAR, "the monthly net")
    return {"median": float(np.median(d)), "mean": float((r[YEAR] - r[MONTH * 3]) / 9.0)}


# ------------------------------------------------------------------------------------------------ (21)


def longest_wait(arrival_days: Iterable[int], window: int = 126) -> tuple[float, bool]:
    """(21) per unit of `E_W` (B-6): the largest difference between consecutive marks of `(0, a_1, ..., a_r, W)`, the
    arrivals at or before W -- the wait to the first payout counts. A unit never paid by W is censored: its value in
    the censored form is W + 1. Returns (the wait, censored)."""
    w = int(window)
    a = sorted(int(d) for d in arrival_days if 0 < int(d) <= w)
    if not a:
        return float(w + 1), True
    marks = np.array([0, *a, w], float)
    return float(np.diff(marks).max()), False


# ------------------------------------------------------------------------------------------------ (24)


def bankroll_state(rel: Sequence[float], first_payout: Any, window: int, budget: float) -> str:
    """(24) per unit of `E_W` at budget B (B-3): `paid_within` -- paid by W with `spent_before(rel, first payout) <= B`;
    `run_out` -- `spent_before(rel, k*) > B` (the spending went above B before a first payout by W); `censored` --
    unpaid by W with `spent_before(rel, W + 1) <= B` (still paying fees, not yet paid)."""
    x, cens = spent_to_event(rel, first_payout, window)
    if x > float(budget):
        return "run_out"
    return "censored" if cens else "paid_within"


def bankroll_stop(rels: Sequence[Sequence[float]], first_payouts: Sequence[Any], window: int,
                  budgets: Sequence[float]) -> dict[float, dict[str, Any]]:
    """(24) over the units of `E_W`, for each budget B: the three states' shares, the limit's reading "not paid within
    B by W" (run out plus censored), and beside it the peak form -- the share whose peak out-of-pocket through close W
    exceeds B, before or after a first payout ((25)'s quantity at the window's end; B-2)."""
    if len(rels) != len(first_payouts):
        raise ValueError("one first payout a unit")
    n = len(rels)
    out: dict[float, dict[str, Any]] = {}
    for b in budgets:
        states = [bankroll_state(r, fy, window, float(b)) for r, fy in zip(rels, first_payouts)]
        peaks = np.array([M.peak_through(closes(r, window, "the peak form"), int(window)) for r in rels], float)
        row: dict[str, Any] = {f"share_{s}": (float(sum(x == s for x in states) / n) if n else NAN) for s in STATES}
        row["share_not_paid_within"] = (row["share_run_out"] + row["share_censored"]) if n else NAN
        row["share_peak_over"] = float((peaks > float(b)).mean()) if n else NAN
        row["n"] = n
        out[float(b)] = row
    return out


# ------------------------------------------------------------------------------------------------ (31)


def account_ending(acc: Mapping[str, Any], window: int) -> str:
    """How a funded account's observed life ends inside closes 0 .. W (B-7, v2 m-6), from the engine's funded record's
    fields (`user_beside`'s journey `accounts`): still open at W (`ended_on` blank or after W) -- `window`; a tier-3
    denial's closure -- `denied`; the Focused Trader Program's Corrective Path -- `ftp`; a household rule (the firm moves
    the account live; R7) -- `live`; the policy's abandon -- `policy`; a breach of the floor -- `breach`; the engine's
    own horizon reached with none of these -- `horizon`. A payout cap ending (`cap`) has no field in the engine's
    record: no Topstep account ends that way in the vendored engine, and a record naming one is read as named
    (`acc["ending"]`). `LOST` endings are the event; `CENSORED` ones are censored."""
    if acc.get("ending") is not None:
        if acc["ending"] not in ENDINGS:
            raise ValueError(f"an ending {acc['ending']!r} that is not one of {ENDINGS}")
        return str(acc["ending"])
    end = acc.get("ended_on")
    if end is None or int(end) > int(window):
        return "window"
    if int(acc.get("denied", 0)) > 0:
        return "denied"
    if acc.get("ftp_closed"):
        return "ftp"
    if acc.get("household_closed"):
        return "live"
    if acc.get("abandoned"):
        return "policy"
    if acc.get("closed"):
        return "breach"
    return "horizon"


def account_lifetime(acc: Mapping[str, Any], window: int) -> dict[str, Any]:
    """(31) per funded account activated by close W: its ending (`account_ending`), its payouts whose cash arrived
    before it ended (an open account's: by close W), and its sessions alive (its end, or W, less its activation)."""
    act = int(acc["activation_day"])
    if act > int(window):
        raise ValueError("an account activated after the window is not the unit's within it")
    kind = account_ending(acc, window)
    end = int(window) if kind == "window" else int(acc["ended_on"])
    arr = [int(d) for d in acc.get("arrivals", ())]
    count = sum(1 for d in arr if (d <= end if kind == "window" else d < end))
    return {"ending": kind, "lost": kind in LOST, "payouts": int(count), "sessions": int(end - act)}


def km_survival(times: Sequence[float], lost: Sequence[bool], weights: Sequence[float] | None = None
                ) -> list[tuple[int, float]]:
    """A weighted Kaplan-Meier curve on whole-number times: `[(k, S(k))]` for k = 0 .. max time + 1, with `S(k)` the
    chance the time reaches k, `S(0) = 1`, `S(k) = prod_{t < k} (1 - d_t / n_t)` -- `d_t` the weight of the events at
    t, `n_t` the weight of every observation with time >= t (a censored one stays in the risk set at its own time and
    leaves after it, the usual convention)."""
    t = np.asarray(times, float)
    e = np.asarray(lost, bool)
    w = np.ones(len(t)) if weights is None else np.asarray(weights, float)
    if not (t.shape == e.shape == w.shape):
        raise ValueError("one time, event flag and weight an observation")
    if len(t) and ((t < 0).any() or (t != np.round(t)).any() or (w <= 0).any()):
        raise ValueError("times are whole numbers of at least 0 and weights above 0")
    top = int(t.max()) if len(t) else 0
    s, out = 1.0, [(0, 1.0)]
    for k in range(0, top + 1):
        n_k = float(w[t >= k].sum())
        d_k = float(w[(t == k) & e].sum())
        if n_k > 0:
            s *= 1.0 - d_k / n_k
        out.append((k + 1, float(s)))
    return out


def km_quantile(curve: Sequence[tuple[int, float]], q: float) -> float:
    """The q-quantile of the time read off a curve (`km_survival`): the smallest t with `S(t + 1) <= 1 - q`, i.e. the
    chance of a time at most t at least q; NaN -- "beyond" -- where the curve does not fall that far."""
    for k, s in curve:
        if k >= 1 and s <= 1.0 - float(q) + 1e-12:
            return float(k - 1)
    return NAN


def funded_lifetime(units: Sequence[Sequence[Mapping[str, Any]]], window: int,
                    pcts: Sequence[int] = PERCENTILES) -> dict[str, Any]:
    """(31) over the units of `E_W`, one list of funded-account records a unit (the accounts activated by W): the
    Kaplan-Meier curve of payouts before loss (and, beside, of sessions alive), each unit weighted equally (an account
    of a unit holding A funded accounts carries 1 / A), its percentiles read off it ("beyond" -- NaN with `p{p}_beyond`
    -- where it does not fall that far), the censored count and share (by accounts, and weighted), and every censored
    ending by kind."""
    rows = []
    for accs in units:
        mine = [a for a in accs if int(a["activation_day"]) <= int(window)]
        for a in mine:
            rows.append({**account_lifetime(a, window), "weight": 1.0 / len(mine)})
    pay = [r["payouts"] for r in rows]
    ses = [r["sessions"] for r in rows]
    lost = [r["lost"] for r in rows]
    w = [r["weight"] for r in rows]
    curve = km_survival(pay, lost, w)
    curve_s = km_survival(ses, lost, w)
    out: dict[str, Any] = {"curve_payouts": curve, "curve_sessions": curve_s, "n_accounts": len(rows),
                           "n_units": int(sum(1 for accs in units if any(int(a["activation_day"]) <= int(window)
                                                                         for a in accs))),
                           "n_lost": int(sum(lost)), "n_censored": int(len(rows) - sum(lost))}
    out["share_censored"] = float(out["n_censored"] / len(rows)) if rows else NAN
    tw = float(sum(w))
    out["share_censored_weighted"] = float(sum(x for x, l in zip(w, lost) if not l) / tw) if rows else NAN
    out["censored_by_kind"] = {k: int(sum(1 for r in rows if r["ending"] == k)) for k in CENSORED}
    out["lost_by_kind"] = {k: int(sum(1 for r in rows if r["ending"] == k)) for k in LOST}
    for p in pcts:
        v = km_quantile(curve, p / 100.0)
        out[f"p{p}"], out[f"p{p}_beyond"] = v, not math.isfinite(v)
        v = km_quantile(curve_s, p / 100.0)
        out[f"sessions_p{p}"], out[f"sessions_p{p}_beyond"] = v, not math.isfinite(v)
    return out


# ------------------------------------------------------------------------------------------------ (30), (37) - (39)


def _union(intervals: Iterable[tuple[float, float]], lo: float | None = None, hi: float | None = None
           ) -> list[tuple[float, float]]:
    """The union of closed intervals (clipped to [lo, hi] when given), as disjoint sorted intervals."""
    iv = []
    for a, b in intervals:
        a, b = float(a), float(b)
        if b < a:
            raise ValueError(f"an interval [{a}, {b}] ends before it starts")
        if lo is not None:
            a, b = max(a, lo), max(b, lo)
        if hi is not None:
            a, b = min(a, hi), min(b, hi)
        iv.append((a, b))
    iv.sort()
    out: list[list[float]] = []
    for a, b in iv:
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [(a, b) for a, b in out]


def _taken(day: Mapping[str, Any]) -> list[tuple[float, float]]:
    out = []
    for t in day.get("taken", ()):
        entry, exit_ = float(t[0]), float(t[1])
        if exit_ < entry:
            raise ValueError("a trade exits before it enters")
        out.append((entry, exit_))
    return out


def _check_day(day: Mapping[str, Any]) -> None:
    if int(day["accounts"]) < 0:
        raise ValueError("a negative count of accounts")
    if int(day["accounts"]) == 0 and len(day.get("taken", ())):
        raise ValueError("a session with no account live takes no trade")


def workload(days: Sequence[Mapping[str, Any]], latency: float) -> dict[str, float]:
    """(30) per unit over its observed sessions, each `{"accounts": live at the close, "taken": ((entry, exit), ...)
    minutes, one entry ticket an order}`: `orders_d` the trades entered, `accounts_d` the accounts live, `screen_d` the
    hours of the union over the session's trades of [entry - L, exit] (the alert is the entry less the latency L);
    their means and maxima. A session with no account live has none of the three."""
    o, a, s = [], [], []
    for d in days:
        _check_day(d)
        t = _taken(d)
        o.append(len(t))
        a.append(int(d["accounts"]))
        s.append(sum(b - x for x, b in _union((e - float(latency), x_) for e, x_ in t)) / 60.0)
    if not days:
        raise ValueError("a unit has at least one observed session")
    return {"orders_mean": float(np.mean(o)), "orders_max": float(np.max(o)), "accounts_mean": float(np.mean(a)),
            "accounts_max": float(np.max(a)), "screen_hours_mean": float(np.mean(s)),
            "screen_hours_max": float(np.max(s))}


def supply(days: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    """(37) per unit over its observed sessions: the means of `offered_d` (the signals the schedule offers, `offered`),
    `taken_d` (the trades entered) and `taken_d / accounts_d` (over the sessions with an account live), with the count
    of sessions without one beside."""
    if not days:
        raise ValueError("a unit has at least one observed session")
    off, tak, per, none = [], [], [], 0
    for d in days:
        _check_day(d)
        off.append(len(d.get("offered", ())))
        k = len(d.get("taken", ()))
        tak.append(k)
        if int(d["accounts"]) >= 1:
            per.append(k / int(d["accounts"]))
        else:
            none += 1
    return {"offered_mean": float(np.mean(off)), "taken_mean": float(np.mean(tak)),
            "taken_per_account_mean": float(np.mean(per)) if per else NAN, "sessions_without_account": int(none)}


def trading_day_of(date: Any, minute_ct: float, reopen: int, length: int) -> tuple[Any, float]:
    """(38), (39): a wall-clock moment (its calendar date, minutes after midnight CT) as (its trading day, minutes after
    that day's reopen). The firm's day opens at `reopen` on the evening before its date and runs `length` minutes
    (Topstep: 17:00 CT to the 15:10 CT flat, `lever_space.trading_day()` from the verified `trading_hours`); an
    evening entry belongs to the trading day it opens, the date after the evening it falls on. A moment after the flat
    and before the reopen is refused."""
    from datetime import date as _date, timedelta

    d = date if isinstance(date, _date) else _date.fromisoformat(str(date))
    m = float(minute_ct)
    if not 0 <= m < 1440:
        raise ValueError("minutes after midnight are in [0, 1440)")
    if m >= int(reopen):
        return d + timedelta(days=1), m - int(reopen)
    off = m + 1440 - int(reopen)
    if off > int(length):
        raise ValueError(f"{d} {m:.0f} min CT falls after the flat, outside the firm's trading day")
    return d, off


def firm_day() -> dict[str, int]:
    """The firm's trading day from its verified rules (`extended.lever_space.trading_day`: Topstep's `trading_hours`,
    8284206): `reopen` and `flat` (minutes CT), `length` (minutes from the reopen to the flat)."""
    from extended import lever_space as LS

    return LS.trading_day()


def coverage(days: Sequence[Mapping[str, Any]], windows: Mapping[str, tuple[float, float]]) -> dict[str, float]:
    """(38) per unit over its observed trading days (`taken`, `offered` in minutes after the day's reopen, as
    `trading_day_of` gives them): for each session window w = [start, end) (minutes after the reopen; the trigger
    library's declaration), the share of the days with at least one trade taken whose entry falls in w, and beside it
    the same share for the trades offered."""
    if not days:
        raise ValueError("a unit has at least one observed trading day")
    out: dict[str, float] = {}
    for name, (a, b) in windows.items():
        a, b = float(a), float(b)
        if not b > a:
            raise ValueError(f"window {name!r} is empty")
        tk = [any(a <= e < b for e, _ in _taken(d)) for d in days]
        of = [any(a <= float(e) < b for e in d.get("offered", ())) for d in days]
        out[f"taken_{name}"] = float(np.mean(tk))
        out[f"offered_{name}"] = float(np.mean(of))
    return out


def _longest_gap(busy: Sequence[tuple[float, float]], length: float) -> float:
    """The longest stretch of [0, length] outside the busy intervals."""
    best, cur = 0.0, 0.0
    for a, b in _union(busy, 0.0, float(length)):
        best = max(best, a - cur)
        cur = max(cur, b)
    return float(max(best, float(length) - cur))


def idle(days: Sequence[Mapping[str, Any]], length: float) -> dict[str, float]:
    """(39) per unit over its observed trading days (minutes after the reopen, the day `length` minutes long): each
    day's longest interval in which no account holds a position (the union of every taken trade's [entry, exit]; a
    news-barred window counts as idle); beside it, the same with the news windows (`news`) taken out -- the longest
    stretch the user could have traded and did not -- and the longest interval with no offered signal (between the
    reopen, the signals' moments and the flat). Their medians and maxima over the days. A day with no trade is idle
    throughout."""
    if not days:
        raise ValueError("a unit has at least one observed trading day")
    a, b, c = [], [], []
    for d in days:
        pos = _taken(d)
        news = [(float(x), float(y)) for x, y in d.get("news", ())]
        a.append(_longest_gap(pos, length))
        b.append(_longest_gap(pos + news, length))
        sig = sorted(float(e) for e in d.get("offered", ()) if 0.0 <= float(e) <= float(length))
        marks = np.array([0.0, *sig, float(length)])
        c.append(float(np.diff(marks).max()))
    return {"idle_median": float(np.median(a)), "idle_max": float(np.max(a)),
            "idle_tradeable_median": float(np.median(b)), "idle_tradeable_max": float(np.max(b)),
            "no_signal_median": float(np.median(c)), "no_signal_max": float(np.max(c))}


# ------------------------------------------------------------------------------------------------ 1.4: the coin readings


def _matrix(x: Any) -> np.ndarray:
    v = np.asarray(x, float)
    if v.ndim != 2 or v.shape[0] < 1 or v.shape[1] < 1:
        raise ValueError("x is one row a start day and one column a coin seed")
    if not np.isfinite(v).all():
        raise ValueError("a blank unit: every unit of E_h has a value under every seed")
    return v


def coin_readings(x: Any, *, share: bool = False, stat: Callable[[np.ndarray], float] | None = None,
                  lag: int = 63, pcts: Sequence[int] = PERCENTILES) -> dict[str, Any]:
    """MEASURES.md 1.4's three readings of a per-unit measure, `x[s, c]` its value on start day s under coin seed c
    (start order down the rows).

    1. "A random user": the pooled units' p10, p50, p90 (a share: the mean).
    2. "The user's payout variance": per start day the p10, p50, p90 across the seeds; summarised by the median over
       start days of the within-day p10 and of the within-day p90, and the p10, p50, p90 over start days of the
       within-day spread (p90 less p10). A share: `q_s`, the share of seeds in the state, by its p10, p50, p90 over s.
    3. "The design statistic's coin noise" (not a user quantity): the statistic computed for each seed over its start
       days -- `stat` (default: the mean for a share, the median otherwise) -- and its p10, p50, p90 across the seeds.

    Beside: `n_eff_bartlett` of each seed's column in start order at `lag` (the reading's horizon), the median across
    seeds, and the `n_eff` of the start-day means (the history-limited count)."""
    v = _matrix(x)
    out: dict[str, Any] = {"n_starts": int(v.shape[0]), "n_seeds": int(v.shape[1])}
    pooled = v.ravel()
    if share:
        if not np.isin(pooled, (0.0, 1.0)).all():
            raise ValueError("a share's per-unit value is 0 or 1")
        out["r1_share"] = float(pooled.mean())
        q = v.mean(axis=1)
        for p in pcts:
            out[f"r2_q_p{p}"] = float(np.percentile(q, p))
    else:
        for p in pcts:
            out[f"r1_p{p}"] = float(np.percentile(pooled, p))
        lo, hi = np.percentile(v, 10, axis=1), np.percentile(v, 90, axis=1)
        out["r2_median_day_p10"] = float(np.median(lo))
        out["r2_median_day_p90"] = float(np.median(hi))
        for p in pcts:
            out[f"r2_spread_p{p}"] = float(np.percentile(hi - lo, p))
    f = stat if stat is not None else (np.mean if share else np.median)
    per_seed = np.array([float(f(v[:, c])) for c in range(v.shape[1])])
    for p in pcts:
        out[f"r3_p{p}"] = float(np.percentile(per_seed, p))
    ne = [M.n_eff_bartlett(v[:, c], lag) for c in range(v.shape[1])]
    ne = [e for e in ne if math.isfinite(e)]
    out["n_eff_median_seed"] = float(np.median(ne)) if ne else NAN
    out["n_eff_day_means"] = M.n_eff_bartlett(v.mean(axis=1), lag)
    return out


def design_coin_readings(x: Any, stat: Callable[[np.ndarray], float], pcts: Sequence[int] = PERCENTILES
                         ) -> dict[str, Any]:
    """Readings 1 and 3 of a design-level measure ((22), (27), (31), (33), (34)): reading 1 the statistic on the pooled
    units (`stat` of every value of `x[s, c]`), reading 3 its p10, p50, p90 across the seeds (each seed's column).
    Reading 2 needs a per-unit value and is not made."""
    v = _matrix(x)
    per_seed = np.array([float(stat(v[:, c])) for c in range(v.shape[1])])
    out: dict[str, Any] = {"r1": float(stat(v.ravel())), "n_starts": int(v.shape[0]), "n_seeds": int(v.shape[1])}
    for p in pcts:
        fin = per_seed[np.isfinite(per_seed)]
        out[f"r3_p{p}"] = float(np.percentile(fin, p)) if len(fin) else NAN
    return out


# ------------------------------------------------------------------------------------------------ (34)


def variance_decomposition(x: Any) -> dict[str, float]:
    """(34)'s coin-layer decomposition by the ANOVA estimator (m-5), `x[s, c]` with at least two seeds: `within` the
    mean over start days of the variance across seeds (ddof 1); `between` the variance over start days of the
    start-day means (ddof 1) less `within / n_c`; the start day's share `between / (between + within)`, truncated at
    zero, the untruncated value beside."""
    v = _matrix(x)
    n_s, n_c = v.shape
    if n_c < 2 or n_s < 2:
        raise ValueError("the decomposition needs at least two start days and two seeds")
    within = float(v.var(axis=1, ddof=1).mean())
    between = float(v.mean(axis=1).var(ddof=1) - within / n_c)
    tot = between + within
    raw = between / tot if tot != 0 else NAN
    return {"within": within, "between": between, "share_start_day_raw": raw,
            "share_start_day": max(0.0, raw) if math.isfinite(raw) else NAN}


# ------------------------------------------------------------------------------------------------ (32), (33)


def by_year(values: Sequence[float], years: Sequence[int], stat: Callable[[np.ndarray], float], *,
            bad: str, year_set: Sequence[int] | None = None) -> dict[str, Any]:
    """(32)'s start-year reading: the statistic on each start year's units, the worst in the measure's bad direction
    (`bad` "low" or "high") and its year, on `year_set` (default: the years present) -- every design compared reads
    the same set, which the result records (m-9)."""
    if bad not in ("low", "high"):
        raise ValueError("bad is 'low' or 'high'")
    v, y = np.asarray(values, float), np.asarray(years, int)
    ys = sorted(set(y.tolist())) if year_set is None else sorted(int(t) for t in year_set)
    per = {}
    for t in ys:
        sel = v[y == t]
        if not len(sel):
            raise ValueError(f"the year set holds {t}, with no unit")
        per[t] = float(stat(sel))
    pick = min if bad == "low" else max
    worst = pick(per, key=lambda t: (per[t], t)) if per else None
    return {"by_year": per, "worst": per[worst] if worst is not None else NAN, "worst_year": worst,
            "years": list(ys)}


def subset_reading(values: Sequence[float], mask: Sequence[bool], stat: Callable[[np.ndarray], float]
                   ) -> dict[str, Any]:
    """(32)'s highest-volatility period: the statistic on the units whose start falls in the period a rule on
    search-year data only defines (`mask`, the rule's own output)."""
    v, m = np.asarray(values, float), np.asarray(mask, bool)
    if v.shape != m.shape:
        raise ValueError("one flag a unit")
    return {"value": float(stat(v[m])) if m.any() else NAN, "n": int(m.sum())}


def break_even_denial_rate(grid: Sequence[float], s4b: Sequence[float]) -> dict[str, Any]:
    """(33) (m-2): with `M(p) = S4b(p) - 1/2` on the grid of enforcement probabilities (its first point 0, rising),
    `p*` is the first crossing in grid order -- the first grid point with `M(p) <= 0`, refined by linear interpolation
    between it and the point before; `p* = 0` if `M(0) <= 0`; "untested beyond the grid" (`p_star` NaN, `status`
    `untested`) if `M` stays above zero. Reported, never a limit."""
    p, s = np.asarray(grid, float), np.asarray(s4b, float)
    if p.shape != s.shape or not len(p) or p[0] != 0.0 or (np.diff(p) <= 0).any():
        raise ValueError("the grid starts at 0 and rises, one S4b a point")
    m = s - 0.5
    if m[0] <= 0:
        return {"p_star": 0.0, "status": "at_zero"}
    for i in range(1, len(p)):
        if m[i] <= 0:
            ps = p[i - 1] + (p[i] - p[i - 1]) * m[i - 1] / (m[i - 1] - m[i])
            return {"p_star": float(ps), "status": "crossed"}
    return {"p_star": NAN, "status": "untested"}


def exposed_share(requested: Sequence[float], exposed: Sequence[float]) -> float:
    """(33) beside: the pooled share of payouts exposed, `sum exposed / sum requested` (blank with none requested); a
    design that never shows the stacking pattern is untested, not robust."""
    r, e = float(np.sum(requested)), float(np.sum(exposed))
    return e / r if r > 0 else NAN


__all__ = ["MONTH", "MONTHS", "YEAR", "TOL", "PERCENTILES", "STATES", "LOST", "CENSORED", "ENDINGS", "closes",
           "first_within", "first_arrival", "days_reading", "strict_quantiles", "spent_to_event",
           "evaluations_to_first_pass", "months_ahead_under", "p_bankroll", "share_ahead_at", "peak_oop",
           "return_on_money_at_risk", "monthly_changes", "monthly_net_4_12", "longest_wait", "bankroll_state",
           "bankroll_stop", "account_ending", "account_lifetime", "km_survival", "km_quantile", "funded_lifetime",
           "workload", "supply", "trading_day_of", "firm_day", "coverage", "idle", "coin_readings",
           "design_coin_readings", "variance_decomposition", "by_year", "subset_reading", "break_even_denial_rate",
           "exposed_share"]
