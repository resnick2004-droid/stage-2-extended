"""Q-86 (CHARTER section 2; E-014, E-015): money spent and the return on spend, per start day, beside Q-44's readings --
a small reading of its own (`scripts/user_spend.py` writes `results/user_spend.csv`); `extended/user_beside.py` is
imported, never edited.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import user_spend as US
    outs = US.run_starts("p14", "verdict", job, starts, workers=1)       # the replay, the day recorder on (engine)
    t = US.start_table("p14", "P-14", "verdict", outs)                    # one row a start
    rows = US.summary_rows(t)                                             # p10 .. p90, spread, share never there

**Why a reading of its own.** Q-44's writer records no fees column, so the cash spent before break-even and a return on
spend are not in its files (Q-69's page). The operator measures a design by the user's path -- time **and money** to
the first passed account, to the first payout and to being ahead, and how evenly that is spread across start days
(E-014, E-015) -- so this reading books, close by close, every fee paid and every payout received.

**The replay** is U1's as Q-17 adapted it (`extended.user_beside`): every start of the design's development window,
its long run of min(252, sessions left) sessions, the start's own path seed (`user_beside.start_seed`), every firm
response off -- `ConductModel(rtp=False, enforcement_p=0.0)`, the vendored 0 %, placement-off call
(`user_beside.response_args` with `off`) -- and **the engine's day recorder on (`record_days=True`), nothing else
changed**, as Q-35 (`extended.openings.ledger_args`) switched the per-trade ledger on. The recorder only records
("Reads state only; the path is identical with it on or off", `lockstep.simulate_lockstep_path`); the synthetic test
holds a path equal with it on and off, and the script's identity holds every start's record equal to U1's file.

**The money, close by close** (`day_ledger`): the recorder's `campaign_days` -- one row a campaign day, its
subscription, activation and reset fees and its payouts arrived. Day 0 is the purchase evening, day k the k-th
session's close (U1's clock). **At an event** means at the close of the session it happens on, every fee and payout
of that session booked: the first pass (U1's `first_pass`, a Combine's pass close), the first payout (U1's
`first_payout`, the first cash arrival), break-even (`user_measures.break_even_day`: the first close k >= 1 whose net
-- payouts received less fees paid, so far -- is at or above zero, to a millionth of a dollar). **Month m's end** is
close 21 m. **The cash out of pocket before break-even** is U1's `spent_before` at the break-even close: the deepest
net below zero over the closes before it (what Q-69's page found missing from Q-44's file, beside the cash before the
first pass and payout U1 records). **Return on spend** at a month end is the net there over the fees paid by then.
**Break-even lost**: a
close after the break-even close below zero (`user_measures.fell_back`). **Evaluations bought before the first pass**:
the Combines bought on a day before the first pass close (purchases happen at a close's end, so one bought on the pass
day is bought after the pass); a reset of a failed Combine (D-146, off in U1's replay) is counted apart.

**Identities first, refusing** (the script writes nothing when one fails; a failure prints the check, the column and
the count of differing starts, never a value):

* `ledger_problems` -- the day ledger against the engine itself: at every close the payouts received less the fees
  paid equal the cash less the starting bankroll; at the window's end the fees and payouts equal the engine's totals;
  every subscription and rebill day equals the Combines' own records (bought on its purchase day, rebilled on purchase
  day + j x billing days + 1 while it trades, `lockstep.py` step 1), every activation day the funded accounts'
  activation days, every reset day the Combines' reset days, every payout's arrival U1's own `payout_arrivals` of the
  funded accounts' requests;
* `u1_money_problems` -- the money against **U1's own money columns** for the start (`user_journey.csv`, section
  `start`): the fees paid and the net at every month end 1-12 inside the window (`fees_month_k`, `net_month_k`), the
  cash spent before the first pass and the first payout, the first payout's cash, the pay days;
* the script also holds every start's U1 record from this replay to U1's start row, all 68 columns (E-010's
  comparison, as Q-35); and `output_problems` holds the written frame to itself.

The tolerance is U1's (a millionth of a dollar) plus the cash's own float resolution at the bankroll's magnitude
(`money_tol`): the engine's cash is one float summed at the bankroll's scale, the ledger's sums are of the bookings.

**What is written** (`frame`, one file): section `identity` (each held check, the count compared), section `start`
(one row a design, arm and start day: `START_COLS`, money to the cent, the return on spend as computed) and section
`summary` (per design, arm and block -- all start days with the reading's window left, and the judged block, the
starts from 2024 -- each measure's p10, p25, p50, p75, p90, the spread p90 - p10, and, for a measure read at an event,
the share of start days never there inside the window). Windows and eligibility are Q-44's (`extended.user_readings`):
the first pass and payout read the starts with 126 sessions left and their window is 126; break-even reads those with
252 and its window is 252; a month end m those with 21 m.

Importing this module touches no `sys.path` and imports no engine: the replay (`run_starts`, `_task`) imports the
vendored tree lazily, in a process that called `extended.use_vendored_stage2()`.
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import user_measures as M
from extended import user_readings as UR
from extended.reader import JUDGED_START

#: the decision row the reading's re-read of P-14, P-15 and P-16 is authorised under (E-037's purpose
#: `registered_design`): E-024, the row that merged Q-17 -- the replay this reading re-runs -- naming all three
READ_ROW = "E-024"
DESIGNS = ("p14", "p15", "p16")
DESIGN_IDS = {"p14": "P-14", "p15": "P-15", "p16": "P-16"}
ARMS = ("verdict", "point")                      # Stage 2's `user_journey.ARMS`: the cautious arm, the as-traded beside

MONTH = UR.MONTH                                 # 21 sessions
FIRST_WINDOW = UR.FIRST_WINDOW                   # 126: the first pass and the first payout
YEAR_WINDOW = UR.YEAR_WINDOW                     # 252: break-even
BLOCKS = UR.BLOCKS                               # ("all", "judged")
#: the judged block's first year (Stage 2 `u_select.JUDGED_FIRST_YEAR`, checked by the script; D-621 (4)(b))
JUDGED_FIRST_YEAR = JUDGED_START.year
SPEND_MONTHS = (1, 2, 3, 4, 5, 6)
U1_MONTHS = tuple(range(1, 13))
PCTS = (10, 25, 50, 75, 90)
QUANTILES = tuple(f"p{p}" for p in PCTS)
#: U1's money tolerance and the bookings' rounding allowed at the bankroll's magnitude (`money_tol`)
TOL = M.TOL
TOL_BOOKINGS = 1000
#: money to the cent in the file: a quantile of it is within half a cent of the summary's
CENT_TOL = 0.005 + 1e-9

#: the events, their per-start day column and their window
EVENTS = (("first_pass", "first_pass", FIRST_WINDOW), ("first_payout", "first_payout", FIRST_WINDOW),
          ("break_even", "break_even_day", YEAR_WINDOW))
SPEND_KEYS = (
    "first_pass", "fees_at_first_pass", "payouts_at_first_pass", "evaluations_before_first_pass",
    "resets_before_first_pass",
    "first_payout", "fees_at_first_payout", "payouts_at_first_payout",
    "break_even_day", "fees_at_break_even", "payouts_at_break_even", "spent_before_break_even", "break_even_lost",
    *(f"fees_month_{m}" for m in SPEND_MONTHS), *(f"payouts_month_{m}" for m in SPEND_MONTHS),
    *(f"return_on_spend_month_{m}" for m in SPEND_MONTHS),
    "fees_end", "payouts_end", "evaluations_bought", "resets",
)
MONEY_KEYS = tuple(k for k in SPEND_KEYS if k.startswith(("fees_", "payouts_", "spent_")))
START_COLS = ("design", "prereg", "arm", "start_day", "start_date", "observed", *SPEND_KEYS)
SECTIONS = ("identity", "start", "summary")
COLUMNS = ("section", "reading", "design", "prereg", "arm", "block", "measure", "stat", "value", "n", "note",
           "start_day", "start_date", "observed", *SPEND_KEYS)

_EVENT_STATS = (*QUANTILES, "spread", "share_never")
_PLAIN_STATS = (*QUANTILES, "spread")
#: every summary measure and its stats, in the file's order
SUMMARY_MEASURES: dict[str, tuple[str, ...]] = {}
for _ev, _, _w in EVENTS:
    SUMMARY_MEASURES[f"sessions_to_{_ev}"] = _EVENT_STATS
    SUMMARY_MEASURES[f"fees_at_{_ev}"] = _EVENT_STATS
    SUMMARY_MEASURES[f"payouts_at_{_ev}"] = _EVENT_STATS
    if _ev == "first_pass":
        SUMMARY_MEASURES["evaluations_before_first_pass"] = _EVENT_STATS
    if _ev == "break_even":
        SUMMARY_MEASURES["spent_before_break_even"] = _EVENT_STATS
SUMMARY_MEASURES["break_even_lost"] = ("share",)
for _m in SPEND_MONTHS:
    for _c in ("fees", "payouts", "return_on_spend"):
        SUMMARY_MEASURES[f"{_c}_month_{_m}"] = _PLAIN_STATS
#: the summary's money measures (compared to the start rows within half a cent)
SUMMARY_MONEY = tuple(m for m in SUMMARY_MEASURES if m.startswith(("fees_", "payouts_", "spent_")))
#: the per-start column each summary measure reads, and its event (None: a month end) and window
MEASURE_SOURCE: dict[str, tuple[str, str | None, int]] = {}
for _ev, _day, _w in EVENTS:
    MEASURE_SOURCE[f"sessions_to_{_ev}"] = (_day, _ev, _w)
    MEASURE_SOURCE[f"fees_at_{_ev}"] = (f"fees_at_{_ev}", _ev, _w)
    MEASURE_SOURCE[f"payouts_at_{_ev}"] = (f"payouts_at_{_ev}", _ev, _w)
MEASURE_SOURCE["evaluations_before_first_pass"] = ("evaluations_before_first_pass", "first_pass", FIRST_WINDOW)
MEASURE_SOURCE["spent_before_break_even"] = ("spent_before_break_even", "break_even", YEAR_WINDOW)
MEASURE_SOURCE["break_even_lost"] = ("break_even_lost", "break_even", YEAR_WINDOW)
for _m in SPEND_MONTHS:
    for _c in ("fees", "payouts", "return_on_spend"):
        MEASURE_SOURCE[f"{_c}_month_{_m}"] = (f"{_c}_month_{_m}", None, MONTH * _m)
EVENT_DAY = {ev: day for ev, day, _ in EVENTS}

READING = ("EXPLORATORY (Q-86; E-014, E-015): money spent and the return on spend per start day, beside Q-44's "
           "readings -- beside the verdict, never deciding; R* stays P-14; the verdict stays at 0 % denial with the "
           "placement off (E-008 (2))")
NAN = float("nan")


class SpendRefused(RuntimeError):
    """An input or an output this reading cannot stand behind."""


def money_tol(initial_bankroll: float) -> float:
    """U1's tolerance (a millionth of a dollar) plus `TOL_BOOKINGS` bookings' rounding (half a unit in the last place
    each) at the bankroll's magnitude: the engine's cash is a float sum there, the ledger's sums are of the bookings."""
    return float(TOL + TOL_BOOKINGS * float(np.spacing(abs(float(initial_bankroll)))) / 2.0)


# ------------------------------------------------------------------------------------------------ one start


def _arrays(fees: Sequence[float], payouts: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    f, p = np.asarray(fees, float), np.asarray(payouts, float)
    if f.ndim != 1 or f.shape != p.shape or not len(f):
        raise SpendRefused(f"REFUSED: fees ({f.shape}) and payouts ({p.shape}) are not one value a close each")
    if not (np.isfinite(f).all() and np.isfinite(p).all()) or (f < 0).any() or (p < 0).any():
        raise SpendRefused("REFUSED: a fee or a payout is negative or blank")
    return f, p


def _day(x: Any, observed: int) -> int | None:
    """An event's close as an index, or None: never, or after the window's last close."""
    if x is None:
        return None
    v = float(x)
    if not math.isfinite(v):
        return None
    k = int(round(v))
    if abs(v - k) > 1e-9 or k < 0:
        raise SpendRefused(f"REFUSED: an event's close {x!r} is not a session index")
    return k if k <= int(observed) else None


def _spent_before(net: np.ndarray, k: int | None) -> float:
    """U1's `customer_journey.spent_before`: the deepest net below zero over the closes before close `k` (0 when there
    are none); NaN when the event never came inside the window."""
    if k is None:
        return NAN
    return float(max(0.0, -float(np.min(net[:k])))) if k > 0 else 0.0


def spend_record(fees: Sequence[float], payouts: Sequence[float], purchase_days: Iterable[int],
                 reset_days: Iterable[int], first_pass: Any, first_payout: Any) -> dict[str, float]:
    """One start's money (`SPEND_KEYS`) from its fees paid and payouts received at each close 0 .. observed, the days
    its evaluations were bought and reset, and its first pass and payout closes (U1's record; NaN: none)."""
    f, p = _arrays(fees, payouts)
    obs = len(f) - 1
    cf, cp = np.cumsum(f), np.cumsum(p)
    net = cp - cf
    buys = sorted(int(d) for d in purchase_days)
    rsts = sorted(int(d) for d in reset_days)
    out: dict[str, float] = {}
    fp, fy = _day(first_pass, obs), _day(first_payout, obs)
    be = M.break_even_day(net)
    bk = _day(be, obs)

    def at(prefix: str, k: int | None) -> None:
        out[f"fees_at_{prefix}"] = float(cf[k]) if k is not None else NAN
        out[f"payouts_at_{prefix}"] = float(cp[k]) if k is not None else NAN

    out["first_pass"] = float(fp) if fp is not None else NAN
    at("first_pass", fp)
    out["evaluations_before_first_pass"] = float(sum(1 for d in buys if d < fp)) if fp is not None else NAN
    out["resets_before_first_pass"] = float(sum(1 for d in rsts if d < fp)) if fp is not None else NAN
    out["first_payout"] = float(fy) if fy is not None else NAN
    at("first_payout", fy)
    out["break_even_day"] = float(bk) if bk is not None else NAN
    at("break_even", bk)
    out["spent_before_break_even"] = _spent_before(net, bk)
    lost = M.fell_back(net, be)
    out["break_even_lost"] = NAN if lost is None else float(lost)
    for m in SPEND_MONTHS:
        d = MONTH * m
        if d <= obs:
            out[f"fees_month_{m}"] = float(cf[d])
            out[f"payouts_month_{m}"] = float(cp[d])
        else:
            out[f"fees_month_{m}"] = out[f"payouts_month_{m}"] = NAN
    for m in SPEND_MONTHS:
        fe, pa = out[f"fees_month_{m}"], out[f"payouts_month_{m}"]
        out[f"return_on_spend_month_{m}"] = (pa - fe) / fe if math.isfinite(fe) and fe > 0 else NAN
    out["fees_end"], out["payouts_end"] = float(cf[-1]), float(cp[-1])
    out["evaluations_bought"], out["resets"] = float(len(buys)), float(len(rsts))
    return {k: out[k] for k in SPEND_KEYS}


def u1_money(fees: Sequence[float], payouts: Sequence[float], first_pass: Any, first_payout: Any) -> dict[str, Any]:
    """What U1's start row holds of the money, made from this ledger: the fees paid and the net at each month end 1-12
    inside the window (`fees_month_k`, `net_month_k`), the deepest cash below the start over the closes before the
    first pass and the first payout (`customer_journey.spent_before`), the cash arrived on the first payout's close,
    the closes on which cash arrived."""
    f, p = _arrays(fees, payouts)
    obs = len(f) - 1
    cf, cp = np.cumsum(f), np.cumsum(p)
    net = cp - cf
    out: dict[str, Any] = {}
    for k in U1_MONTHS:
        d = MONTH * k
        out[f"fees_month_{k}"] = float(cf[d]) if d <= obs else NAN
        out[f"net_month_{k}"] = float(net[d]) if d <= obs else NAN
    for ev, x in (("pass", first_pass), ("payout", first_payout)):
        out[f"spent_before_first_{ev}"] = _spent_before(net, _day(x, obs))
    k = _day(first_payout, obs)
    out["first_payout_day_cash"] = float(p[k]) if k is not None else NAN
    out["pay_days"] = [int(d) for d in np.nonzero(p > 0)[0]]
    return out


# ------------------------------------------------------------------------------------------------ the engine's ledger


def day_ledger(lp: Any) -> tuple[np.ndarray, np.ndarray]:
    """(fees paid, payouts received) at each close 0 .. observed, from the engine's day recorder (`campaign_days`:
    subscription + activation + reset fees; payouts arrived). Refuses a ledger that is not one row a close in order."""
    days = list(getattr(lp, "campaign_days", ()) or ())
    n = len(lp.path.cash_series)
    if len(days) != n or [int(r["day"]) for r in days] != list(range(n)):
        raise SpendRefused(f"REFUSED: the day recorder holds {len(days)} rows for {n} closes (is record_days on?)")
    f = np.array([float(r["fee_subscription"]) + float(r["fee_activation"]) + float(r["fee_reset"]) for r in days])
    p = np.array([float(r["payouts_in"]) for r in days])
    return f, p


def ledger_problems(lp: Any, *, lag: int, subscription: float, activation: float, reset_fee: float,
                    billing_days: int, what: str = "") -> list[str]:
    """The day ledger against the engine itself (empty: it holds) -- the cash at every close, the totals, and the
    per-account records day by day: subscriptions and rebills (each Combine's purchase day and `subscriptions_paid`),
    activations (each funded account's activation day), resets (each Combine's reset days), payouts (U1's
    `payout_arrivals` of each funded account's requests, `lag` sessions after)."""
    days = list(lp.campaign_days)
    f, p = day_ledger(lp)
    n = len(f)
    tol = money_tol(lp.path.initial_bankroll)
    out = []
    rel = np.asarray(lp.path.cash_series, float) - float(lp.path.initial_bankroll)
    net = np.cumsum(p) - np.cumsum(f)
    bad = np.nonzero(np.abs(net - rel) > tol)[0]
    if len(bad):
        out.append(f"{what}the cash at {len(bad)} of {n} closes is not the payouts received less the fees paid "
                   f"(first: close {int(bad[0])})")
    if abs(float(f.sum()) - float(lp.path.total_fees)) > tol:
        out.append(f"{what}the fees paid are not the engine's total fees")
    if abs(float(p.sum()) - float(lp.path.total_payouts)) > tol:
        out.append(f"{what}the payouts received are not the engine's total payouts")

    def by_day(want: np.ndarray, column: str, words: str) -> None:
        got = np.array([float(r[column]) for r in days])
        diff = np.nonzero(np.abs(got - want) > tol)[0]
        if len(diff):
            out.append(f"{what}{words} on {len(diff)} of {n} days are not the accounts' records (first: day "
                       f"{int(diff[0])})")

    sub = np.zeros(n)
    rst = np.zeros(n)
    for c in lp.combines:
        pd0 = int(c.purchase_day)
        for j in range(int(c.subscriptions_paid)):
            d = pd0 + (j * int(billing_days) + 1 if j else 0)
            if not 0 <= d < n:
                out.append(f"{what}Combine {c.index}'s subscription {j + 1} falls on day {d}, outside the window")
                continue
            sub[d] += float(subscription)
        for d in getattr(c, "reset_days", ()):
            if not 0 <= int(d) < n:
                out.append(f"{what}Combine {c.index}'s reset on day {d} is outside the window")
                continue
            rst[int(d)] += float(reset_fee)
        if len(getattr(c, "reset_days", ())) != int(getattr(c, "resets", 0)):
            out.append(f"{what}Combine {c.index}: {len(c.reset_days)} reset days against its {c.resets} resets")
    act = np.zeros(n)
    for a in lp.funded:
        d = int(a.activation_day)
        if 0 <= d < n:
            act[d] += float(activation)
        else:
            out.append(f"{what}funded account {a.index}'s activation day {d} is outside the window")
    by_day(sub, "fee_subscription", "the subscription fees")
    by_day(act, "fee_activation", "the activation fees")
    by_day(rst, "fee_reset", "the reset fees")
    arrived = np.zeros(n)
    for d, c in _arrivals(lp, lag, n - 1):
        arrived[int(d)] += float(c)
    by_day(arrived, "payouts_in", "the payouts arrived")
    return out


def _arrivals(lp: Any, lag: int, observed: int) -> list[tuple[int, float]]:
    """U1's `payout_arrivals` (`propedge.research.user_journey`), restated here for a process without the vendored tree
    and held to it by the synthetic test: each request's cash arrives on campaign day activation + 1 + its relative day
    + lag; after the observed closes it never arrived."""
    out = []
    for a, f in enumerate(lp.funded):
        if len(f.payout_days) != len(f.payout_cash):
            raise SpendRefused(f"REFUSED: funded account {a}: {len(f.payout_days)} payout days against "
                               f"{len(f.payout_cash)} amounts")
        for j, (r, c) in enumerate(zip(f.payout_days, f.payout_cash)):
            day = int(f.activation_day) + 1 + int(r) + int(lag)
            if day <= int(observed):
                out.append((day, a, j, float(c)))
    out.sort(key=lambda x: x[:3])
    return [(d, c) for d, _, _, c in out]


# ------------------------------------------------------------------------------------------------ U1's columns


def _num(x: Any) -> float:
    if x is None:
        return NAN
    if isinstance(x, str):
        return float(x) if x.strip() else NAN
    try:
        return float(x)
    except (TypeError, ValueError):
        return NAN


def _days_of(x: Any) -> list[int]:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return []
    return [int(float(t)) for t in str(x).split()]


def u1_money_problems(money: Mapping[int, Mapping[str, Any]], file_rows: Sequence[Mapping[str, Any]], *, tol: float,
                      what: str) -> list[str]:
    """Each start's money (`u1_money`, by start day) against U1's start rows for the design and arm (its file's
    columns): `fees_month_k` and `net_month_k` for k = 1..12 (blank where the window holds no such month end), the cash
    spent before the first pass and payout, the first payout's cash (where it arrived alone on its close), the pay days
    (the closes cash arrived on). Messages name the column and the count of differing starts -- never a value."""
    by = {}
    for r in file_rows:
        by[int(_num(r["start_day"]))] = r
    out = []
    absent = sorted(set(money) - set(by))
    if absent:
        out.append(f"{what}: {len(absent)} of our starts not in U1's file (first: start {absent[0]})")
    common = sorted(set(money) & set(by))
    cols = [*(f"fees_month_{k}" for k in U1_MONTHS), *(f"net_month_{k}" for k in U1_MONTHS),
            "spent_before_first_pass", "spent_before_first_payout", "first_payout_cash", "pay_days"]
    bad: Counter = Counter()
    for s in common:
        mine, theirs = money[s], by[s]
        for c in cols:
            if c == "pay_days":
                if sorted(set(_days_of(theirs.get("pay_days")))) != list(mine["pay_days"]):
                    bad[c] += 1
                continue
            if c == "first_payout_cash":
                fy = _num(theirs.get("first_payout"))
                pays = _days_of(theirs.get("pay_days"))
                a, b = mine["first_payout_day_cash"], _num(theirs.get(c))
                if math.isnan(fy):
                    ok = math.isnan(a) and math.isnan(b)
                elif pays.count(int(fy)) == 1:
                    ok = abs(a - b) <= tol
                else:                                    # two payouts arrived together: the close holds both
                    ok = a >= b - tol
                if not ok:
                    bad[c] += 1
                continue
            a, b = float(mine[c]), _num(theirs.get(c))
            if not ((math.isnan(a) and math.isnan(b)) or abs(a - b) <= tol):
                bad[c] += 1
    out += [f"{what} {c}: {bad[c]} of {len(common)} starts differ" for c in cols if bad[c]]
    return out


# ------------------------------------------------------------------------------------------------ the tables


def start_table(design: str, prereg: str, arm: str, outs: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """One row a start: its date and sessions observed (U1's record) and its money (`spend_record`), unrounded."""
    rows = []
    for x in outs:
        r = x["rec"]
        rows.append({"design": design, "prereg": prereg, "arm": arm, "start_day": int(r["start_day"]),
                     "start_date": str(r["start_date"]), "observed": int(r["observed"]),
                     **{k: float(x["spend"][k]) for k in SPEND_KEYS}})
    return pd.DataFrame(rows, columns=list(START_COLS))


def rounded(t: pd.DataFrame) -> pd.DataFrame:
    """The file's form of the start rows: money to the cent (the summary is read before rounding)."""
    t = t.copy()
    for c in MONEY_KEYS:
        t[c] = t[c].astype(float).round(2)
    return t


def _elig(t: pd.DataFrame, block: str, h: int) -> np.ndarray:
    """Q-44's eligibility (`user_readings._elig`): the starts with `h` sessions observed; in the judged block those
    whose start date is from `JUDGED_FIRST_YEAR` on."""
    if block not in BLOCKS:
        raise ValueError(f"a block is one of {BLOCKS}, got {block!r}")
    m = t["observed"].to_numpy(int) >= int(h)
    if block == "judged":
        m &= t["start_date"].astype(str).str[:4].astype(int).to_numpy() >= int(JUDGED_FIRST_YEAR)
    return m


def _row(block: str, measure: str, stat: str, value: float, n: int, note: str = "") -> dict[str, Any]:
    return {"block": block, "measure": measure, "stat": stat, "value": float(value), "n": int(n), "note": note}


def _quantile_rows(block: str, measure: str, x: np.ndarray, note: str) -> list[dict[str, Any]]:
    v = np.asarray(x, float)
    v = v[np.isfinite(v)]
    q = {f"p{p}": (float(np.percentile(v, p)) if len(v) else NAN) for p in PCTS}
    out = [_row(block, measure, k, q[k], len(v), note) for k in QUANTILES]
    out.append(_row(block, measure, "spread", q["p90"] - q["p10"], len(v), "p90 less p10"))
    return out


def summary_rows(t: pd.DataFrame) -> list[dict[str, Any]]:
    """One design and arm's summary (`SUMMARY_MEASURES`, both blocks) from its start rows: each row carries the
    design, prereg and arm."""
    keys = t[["design", "prereg", "arm"]].drop_duplicates()
    if len(keys) != 1:
        raise SpendRefused(f"REFUSED: a summary reads one design and arm, not {len(keys)}")
    head = {k: str(keys.iloc[0][k]) for k in ("design", "prereg", "arm")}
    out: list[dict[str, Any]] = []
    for b in BLOCKS:
        for ev, day, w in EVENTS:
            e = _elig(t, b, w)
            first = t[day].to_numpy(float)[e]
            hit = np.isfinite(first) & (first <= w)
            never = float(1.0 - hit.mean()) if len(first) else NAN
            note = f"window {w}; an unreached start beyond"
            rows = [_row(b, f"sessions_to_{ev}", f"p{p}", M.days_quantile(first, w, p), len(first), note)
                    for p in PCTS]
            p10, p90 = rows[0]["value"], rows[-1]["value"]
            rows.append(_row(b, f"sessions_to_{ev}", "spread", p90 - p10, len(first), "p90 less p10; blank when "
                             "either is beyond the window"))
            rows.append(_row(b, f"sessions_to_{ev}", "share_never", never, len(first),
                             f"the share of the starts with {w} sessions not there within them"))
            out += rows
            money = [f"fees_at_{ev}", f"payouts_at_{ev}"] + {"first_pass": ["evaluations_before_first_pass"],
                                                            "break_even": ["spent_before_break_even"]}.get(ev, [])
            for m in money:
                x = t[m].to_numpy(float)[e][hit]
                out += _quantile_rows(b, m, x, f"among the starts there within {w} sessions")
                out.append(_row(b, m, "share_never", never, len(first),
                                f"the share of the starts with {w} sessions not there within them"))
        e = _elig(t, b, YEAR_WINDOW)
        be = t["break_even_day"].to_numpy(float)[e]
        hit = np.isfinite(be) & (be <= YEAR_WINDOW)
        lost = t["break_even_lost"].to_numpy(float)[e][hit]
        out.append(_row(b, "break_even_lost", "share", float(lost.mean()) if len(lost) else NAN, len(lost),
                        f"of the starts back to break-even within {YEAR_WINDOW}: a later close below zero"))
        for m in SPEND_MONTHS:
            e = _elig(t, b, MONTH * m)
            for c in ("fees", "payouts", "return_on_spend"):
                col = f"{c}_month_{m}"
                out += _quantile_rows(b, col, t[col].to_numpy(float)[e], f"the starts with {MONTH * m} sessions")
    order = {m: i for i, m in enumerate(SUMMARY_MEASURES)}
    out.sort(key=lambda r: (BLOCKS.index(r["block"]), order[r["measure"]]))
    return [{**head, **r} for r in out]


def identity_row(design: str, prereg: str, arm: str, check: str, compared: int, note: str = "") -> dict[str, Any]:
    """A held identity's row (a failed one ends the run before anything is written)."""
    return {"design": design, "prereg": prereg, "arm": arm, "block": "all", "measure": check, "stat": "holds",
            "value": 1.0, "n": int(compared), "note": note}


def frame(identity: Sequence[Mapping[str, Any]], tables: Sequence[pd.DataFrame], summary: Sequence[Mapping[str, Any]],
          reading: str) -> pd.DataFrame:
    """The reading's frame, `COLUMNS` in order: the identity rows, the start rows (money to the cent), the summary."""
    parts = [pd.DataFrame([{**r, "section": "identity"} for r in identity])]
    for t in tables:
        parts.append(rounded(t).assign(section="start"))
    parts.append(pd.DataFrame([{**r, "section": "summary"} for r in summary]))
    df = pd.concat([p for p in parts if len(p)], ignore_index=True)
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = np.nan
    df["reading"] = reading
    return df.loc[:, list(COLUMNS)]


# ------------------------------------------------------------------------------------------------ the checks


def _close(a: float, b: float, tol: float) -> bool:
    if math.isnan(a) and math.isnan(b):
        return True
    return abs(a - b) <= tol + 1e-12 * max(1.0, abs(b))


def start_tables(df: pd.DataFrame) -> dict[tuple[str, str], pd.DataFrame]:
    """The frame's start rows by (design, arm), each in start order, typed as `start_table` makes them."""
    st = df[df["section"].astype(str) == "start"].copy()
    out = {}
    for (d, a), g in st.groupby(["design", "arm"], sort=False):
        g = g.loc[:, list(START_COLS)].sort_values("start_day", kind="stable").reset_index(drop=True)
        g["start_day"] = g["start_day"].astype(int)
        g["observed"] = g["observed"].astype(int)
        g["start_date"] = g["start_date"].astype(str)
        for c in ("design", "prereg", "arm"):
            g[c] = g[c].astype(str)
        for c in SPEND_KEYS:
            g[c] = pd.to_numeric(g[c], errors="coerce").astype(float)
        out[(str(d), str(a))] = g
    return out


def summary_index(df: pd.DataFrame) -> dict[tuple[str, ...], tuple[float, float]]:
    """The frame's summary rows by (design, arm, block, measure, stat) -> (value, n)."""
    s = df[df["section"].astype(str) == "summary"]
    out: dict[tuple[str, ...], tuple[float, float]] = {}
    vals = pd.to_numeric(s["value"], errors="coerce").to_numpy(float)
    ns = pd.to_numeric(s["n"], errors="coerce").to_numpy(float)
    keys = zip(*(s[c].astype(str).tolist() for c in ("design", "arm", "block", "measure", "stat")))
    for i, k in enumerate(keys):
        if k in out:
            raise SpendRefused(f"REFUSED: two summary rows for {k}")
        out[k] = (float(vals[i]), float(ns[i]))
    return out


def cross_problems(df: pd.DataFrame) -> tuple[int, list[str]]:
    """The summary rows against the writer's own `summary_rows` on the frame's start rows: (the comparisons made, the
    differences) -- counts exactly, money within half a cent (the start rows are to the cent), the rest to 1e-9."""
    have = summary_index(df)
    tables = start_tables(df)
    compared, out = 0, []
    seen = set()
    for (d, a), t in tables.items():
        for r in summary_rows(t):
            k = (d, a, r["block"], r["measure"], r["stat"])
            seen.add(k)
            if k not in have:
                out.append(f"the summary has no row {k}")
                continue
            v, n = have[k]
            tol = CENT_TOL if r["measure"] in SUMMARY_MONEY and r["stat"] != "share_never" else 1e-9
            compared += 1
            if int(n) != int(r["n"]) or not _close(float(r["value"]), v, tol):
                out.append(f"{k}: the start rows give {r['value']!r} on {r['n']}, the summary {v!r} on {n:g}")
    extra = sorted(set(have) - seen)
    if extra:
        out.append(f"{len(extra)} summary rows for no start rows (first: {extra[0]})")
    return compared, out


def output_problems(df: pd.DataFrame) -> list[str]:
    """Why a frame is not this reading's: its columns are not `COLUMNS`; an unknown section; a design and arm without
    start rows or summary; a start twice; a fee or payout negative, cumulative money falling from one month end to the
    next, more evaluations before the first pass than bought; the summary not its start rows' (`cross_problems`); a
    share outside [0, 1]; the percentiles out of order; a spread that is not p90 less p10."""
    if tuple(df.columns) != COLUMNS:
        return [f"the columns are {list(df.columns)}, not {list(COLUMNS)}"]
    out = []
    unknown = sorted(set(df["section"].astype(str)) - set(SECTIONS))
    if unknown:
        out.append(f"unknown section(s) {unknown}")
    tables = start_tables(df)
    if not tables:
        out.append("no start rows")
    for (d, a), t in tables.items():
        w = f"{d} {a}"
        if t["start_day"].duplicated().any():
            out.append(f"{w}: a start day twice")
        money = t[list(MONEY_KEYS)].to_numpy(float)
        if (money[np.isfinite(money)] < 0).any():
            out.append(f"{w}: a negative fee or payout")
        for c in ("fees", "payouts"):
            x = t[[f"{c}_month_{m}" for m in SPEND_MONTHS]].to_numpy(float)
            dx = np.diff(x, axis=1)
            if (dx[np.isfinite(dx)] < -1e-9).any():
                out.append(f"{w}: cumulative {c} fall from one month end to the next")
        ev, bought = t["evaluations_before_first_pass"].to_numpy(float), t["evaluations_bought"].to_numpy(float)
        if (ev[np.isfinite(ev)] > bought[np.isfinite(ev)]).any():
            out.append(f"{w}: more evaluations before the first pass than bought")
    if out:
        return out
    _, cross = cross_problems(df)
    out += cross[:6]
    s = df[df["section"].astype(str) == "summary"]
    v = pd.to_numeric(s["value"], errors="coerce")
    share = s["stat"].astype(str).isin(("share", "share_never"))
    if ((v[share] < -1e-12) | (v[share] > 1 + 1e-12)).any():
        out.append("a share outside [0, 1]")
    idx = summary_index(df)
    for (d, a, b, m, st), (val, _) in idx.items():
        if st != "p10":
            continue
        q = [idx.get((d, a, b, m, k), (NAN, 0))[0] for k in QUANTILES]
        f = [x for x in q if math.isfinite(x)]
        if f != sorted(f) or (len(f) == len(q) and any(x > y + 1e-9 for x, y in zip(q, q[1:]))):
            out.append(f"{d} {a} {b} {m}: the percentiles are out of order")
        sp = idx.get((d, a, b, m, "spread"), (NAN, 0))[0]
        if not _close(sp, q[-1] - q[0], 1e-9):
            out.append(f"{d} {a} {b} {m}: the spread is not p90 less p10")
    return out


# ------------------------------------------------------------------------------------------------ the replay


def spend_args(args: dict[str, Any]) -> dict[str, Any]:
    """The replay's arguments with every response off (`user_beside.response_args(args, off)`: refuses anything but
    the vendored 0 %, placement-off call) and the engine's day recorder on -- nothing else changed. Refuses arguments
    already carrying the recorder or the per-trade ledger, or another activation timing (the ledger's activation check
    reads the activation fee as paid on the activation day)."""
    from extended import user_beside as B
    from propedge.campaign.lockstep import ACTIVATION_ON_ACTIVATION

    for k in ("record_days", "record_trades"):
        if k in args["path"]:
            raise SpendRefused(f"REFUSED: the replay's path arguments already carry {k}")
    timing = args["path"].get("activation_timing", ACTIVATION_ON_ACTIVATION)
    if timing != ACTIVATION_ON_ACTIVATION:
        raise SpendRefused(f"REFUSED: the activation timing {timing!r} is not U1's ({ACTIVATION_ON_ACTIVATION!r})")
    a = B.response_args(args, B.BY_NAME["off"])
    return {**a, "path": {**a["path"], "record_days": True}}


def _terms(a: dict[str, Any]) -> dict[str, Any]:
    p = a["path"]
    rules = p["rules"]
    fee = p.get("reset_fee")
    return {"subscription": float(p["subscription"]), "activation": float(p["activation"]),
            "reset_fee": float(getattr(rules, "reset_fee", 0.0) if fee is None else fee),
            "billing_days": int(p["billing_days"]), "lag": int(p["payout_lag_days"])}


def _task(task: tuple) -> list[dict[str, Any]]:
    """(design, arm, blocks, dates, args, starts) -> per start: its U1 record from the long replay
    (`user_beside.long_record`, with its three checks against the engine's totals), its money (`spend_record`), what
    U1's start row holds of it (`u1_money`) and the ledger's problems against the engine. The path itself is dropped
    before the next start."""
    import warnings

    from extended import user_beside as B
    from propedge.research import user_journey as U

    warnings.filterwarnings("ignore")
    design, arm, blocks, dates, args, starts = task
    a = spend_args(args)
    terms = _terms(a)
    lag = terms.pop("lag")
    n = len(blocks)

    def pay(lp, obs):
        return U.payout_arrivals([(f.activation_day, lag, f.payout_days, f.payout_cash) for f in lp.funded], obs)

    def totals(lp):
        return lp.path.total_fees, lp.path.total_payouts

    out = []
    for s in starts:
        L = min(U.HORIZON, n - s)
        lp = B.replay(blocks[s:s + L], a, B.start_seed(s))
        if len(lp.path.cash_series) != L + 1:
            raise RuntimeError(f"{design} {arm} start {s}: {len(lp.path.cash_series)} closes, not {L + 1}")
        rec = B.long_record(s, dates[s], lp, pay, totals)
        what = f"{design} {arm} start {s}: "
        probs = ledger_problems(lp, lag=lag, what=what, **terms)
        f, p = day_ledger(lp)
        r = rec["rec"]
        sp = spend_record(f, p, [c.purchase_day for c in lp.combines],
                          [d for c in lp.combines for d in c.reset_days], r["first_pass"], r["first_payout"])
        rel = np.asarray(lp.path.cash_series, float) - float(lp.path.initial_bankroll)
        be = M.break_even_day(rel)
        if not ((math.isnan(be) and math.isnan(sp["break_even_day"])) or be == sp["break_even_day"]):
            probs.append(f"{what}the break-even close from the ledger is not the cash's")
        if int(r["observed"]) != L:
            probs.append(f"{what}the record observes {r['observed']} sessions, the replay {L}")
        out.append({"rec": r, "differs": [], "checked": [], "pay_bad": rec["pay_bad"], "cash_bad": rec["cash_bad"],
                    "fee_bad": rec["fee_bad"], "spend": sp, "money": u1_money(f, p, r["first_pass"], r["first_payout"]),
                    "tol": money_tol(lp.path.initial_bankroll), "problems": probs})
        del lp
    return out


def run_starts(design: str, arm: str, job: dict[str, Any], starts: Sequence[int], workers: int,
               chunk: int = 20) -> list[dict[str, Any]]:
    """Every chosen start of one design and arm, in start order, across `customer_journey._pool_run`'s guarded pool
    (`workers`; 1 runs in this process)."""
    import customer_journey as CJ

    if job.get("engine") != "single":
        raise SpendRefused("REFUSED: Q-86 replays single-firm designs only")
    chunks = [list(starts[j:j + chunk]) for j in range(0, len(starts), chunk)]
    tasks = [(design, arm, job["blocks"], job["dates"], job["args"], c) for c in chunks]
    res = CJ._pool_run(tasks, _task, int(workers), f"Q-86 {design} {arm}")
    return [x for part in res for x in part]


def ledger_summary(outs: Sequence[Mapping[str, Any]], what: str) -> list[str]:
    """The starts' ledger problems as printed: each check once, with the count of starts it failed on."""
    kinds: Counter = Counter()
    for x in outs:
        for p in x["problems"]:
            body = p.split(": ", 1)[1] if ": " in p else p
            kinds[body.split(" (first:")[0]] += 1
    return [f"{what}: {k} -- on {c} of {len(outs)} starts" for k, c in kinds.items()]


__all__ = ["READ_ROW", "DESIGNS", "DESIGN_IDS", "ARMS", "MONTH", "FIRST_WINDOW", "YEAR_WINDOW", "BLOCKS",
           "JUDGED_FIRST_YEAR", "SPEND_MONTHS", "U1_MONTHS", "PCTS", "QUANTILES", "TOL", "TOL_BOOKINGS", "CENT_TOL",
           "EVENTS", "SPEND_KEYS", "MONEY_KEYS", "START_COLS", "SECTIONS", "COLUMNS", "SUMMARY_MEASURES",
           "SUMMARY_MONEY", "MEASURE_SOURCE", "EVENT_DAY", "READING", "SpendRefused", "money_tol", "spend_record",
           "u1_money", "day_ledger", "ledger_problems", "u1_money_problems", "start_table", "rounded", "summary_rows",
           "identity_row", "frame", "start_tables", "summary_index", "cross_problems", "output_problems", "spend_args",
           "run_starts", "ledger_summary"]
