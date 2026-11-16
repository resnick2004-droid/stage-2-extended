"""EXPLORATORY (D-620, program U's study U1): the user's journey over twelve months -- pure functions on a unit's
records. No engine, no draw; the only seed is the bootstrap's (`BOOT_SEED`).

A *unit* is one replay start (D-620 (3)(a)): a trading day of a configuration's development window as a fresh start, its
trades in historical order, run for min(`HORIZON`, sessions left) sessions. Day 0 is the purchase evening, day k closes
the k-th session, a month is `MONTH` sessions. A reading at h sessions is read only on starts with at least h sessions
left. `scripts/user_journey.py` builds the units from the engine's records and writes the files.

* **The record** (`start_record`, D-620 (3)(d)): the sessions observed; every pass day and funded activation day; every
  payout's arrival day and cash (`payout_arrivals`: the engine's own `payout_days` / `payout_cash` of each funded
  account, moved to the campaign day the cash arrives); the net cash (the cash less the start: the bankroll never
  binds) at each month end 1 to 12 and the fees paid by each (`payouts received - net`: before and after a payout the
  cash moves only by fees and payouts); the deepest cash below the start before the first pass and before the first
  payout (`customer_journey.spent_before`); and the net at session 30, which Q1's sensitivity reads.
* **The exact-length runs** (D-620 (3)(f)): where a start's long replay and a run of exactly h sessions (h in `EXACT`)
  disagree on the event days up to h, the record carries the exact run's record under `alt[h]`, and every reading at h
  sessions reads that start from it (`Views.at`).
* **The readings** (`metric_rows`, D-620 (3)(e)): first pass, first payout, periodic, money back, consistency, quit
  rules (`Q1` / `Q2` of D-620 (1)(a)), luck against design; `luck_rows` the part that needs every configuration.
* **Paired with the reference** (`paired_rows`): on the common start days, the difference of every share and mean
  (`stats`) with a moving-block bootstrap interval, blocks as long as the reading's horizon (`paired_interval`,
  D-620 (1)(c) G2: seed 20261700, 2,000 draws). A description: U1 selects nothing.

Percentiles are numpy's linear; an unreached unit counts as beyond and a percentile beyond the observed days is blank
(`customer_journey._days_q`, D-518 (3)).
"""
from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from propedge.research.customer_journey import _days_q, _q, spent_before

DECISION = "D-620"
STUDY = "U1"
RESULT = "user_journey"
PAYOUTS_RESULT = "user_journey_payouts"
FAMILY_ID = f"{DECISION}:user_journey"
SCRIPT = "scripts/user_journey.py"
READING = ("EXPLORATORY (D-620, U1): a start-day measurement over twelve months; no new design, no selection; beside "
           "the verdicts, never a gate (D-234)")

MONTH = 21
MONTHS = 12
HORIZON = MONTH * MONTHS                    # 252 sessions
#: the runs of exactly h sessions the long replay's event days are checked against (D-620 (3)(f), D-518 (5))
EXACT = (21, 63, 90, 126)
PASS_DAYS = (5, 10, 21, 42)
PAYOUT_DAYS = (21, 30, 42, 63, 90, 126)
PASS_WINDOW = max(PASS_DAYS)
PAYOUT_WINDOW = max(PAYOUT_DAYS)
PERIODIC_MONTHS = (1, 2, 3, 6, 9, 12)
NET_PERCENTILES = (5, 10, 25, 50, 75, 90)
MONEY_BACK_MONTHS = (1, 3, 6, 12)
NO_PAYOUT_MONTHS = (1, 2, 3, 6)
GAP_WINDOWS = (126, 252)
CONCENTRATION_MONTHS = (3, 6, 12)
LUCK_MONTHS = (1, 3, 6, 12)
#: the quit rules (D-620 (1)(a)): Q1 stops a unit with no payout by `QUIT_DAY` (read also at `QUIT_SENSITIVITY`), Q2
#: also a unit not ahead at `QUIT_CHECK`; a unit that goes on keeps its `QUIT_END`-session net
QUIT_DAY = 21
QUIT_SENSITIVITY = (30, 42)
QUIT_CHECK = 63
QUIT_END = 126
#: a session that is not a month end and whose net a reading needs (Q1's sensitivity at session 30)
EXTRA_NET_DAY = 30
PAID_BY_YEAR_DAY = 21
#: the bootstrap of a paired difference (D-620 (1)(c) G2)
BOOT_SEED = 20261700
BOOT_DRAWS = 2000
#: the interval's level. G2 divides 0.05 by the number of design cells run under program U so far; U1 runs none (its
#: interval is "a description"), so it is read at 0.05 itself, two-sided
ALPHA = 0.05
#: the screens' seeds (D-620 (1)(e)); a replay draws nothing
CAMPAIGN_SEED = 20261131
COIN_SEED = 20261102
ARMS = ("verdict", "point")
#: the nine configurations (D-620 (3)(c)), none new
CONFIGS = ("fv3c", "p13", "p14", "p15", "p16", "p16_funded_cap", "p16_4+0", "p16_5+1", "rc_s150_london")
N_READINGS = len(CONFIGS) * len(ARMS)       # 18, counted under `FAMILY_ID`
REFERENCE = "p16"                           # the result's reference (D-620 (1)(b)); the limits' is P-14
LIMIT_REFERENCE = "p14"
LUCID_LABEL = "lucid_upper_bound"
SECTIONS = ("identity", "metric", "month", "start", "paired")
TOL = 1e-6

#: the record's keys (`start_record`); a record in a file also carries `start_day`, `start_date` and, on a start whose
#: exact run differs, `alt`
RECORD_KEYS = ("observed", "pass_days", "funded_days", "pay_days", "pay_cash", "first_pass", "first_funded",
               "first_payout", "first_payout_cash", "spent_before_first_pass", "spent_before_first_payout",
               "net_month", "fees_month", "net_30")


# ------------------------------------------------------------------------------------------------ the record


def payout_arrivals(accounts: Iterable[tuple[int, int, Sequence[int], Sequence[float]]], observed: int
                    ) -> list[tuple[int, float]]:
    """Every payout's (arrival day, cash) from the engine's own records. `accounts`: one tuple per funded account, in
    the engine's order -- (its activation day, its firm's payout lag in sessions, its `payout_days`, its `payout_cash`).
    `payout_days` is engine-relative per account: the account's first session is the day after its activation, so a
    payout requested at the close of its relative day r is requested on campaign day `activation + 1 + r` and its cash
    arrives `lag` sessions later. A payout arriving after the `observed` sessions was never received and is left out.
    Sorted by arrival day, then the accounts' order, then the request's."""
    out = []
    for a, (activation, lag, days, cash) in enumerate(accounts):
        if len(days) != len(cash):
            raise ValueError(f"account {a}: {len(days)} payout days against {len(cash)} payout amounts")
        for j, (r, c) in enumerate(zip(days, cash)):
            day = int(activation) + 1 + int(r) + int(lag)
            if day <= int(observed):
                out.append((day, a, j, float(c)))
    out.sort(key=lambda x: x[:3])
    return [(d, c) for d, _, _, c in out]


def _received(payouts: Sequence[tuple[int, float]], day: int) -> float:
    return float(sum(c for d, c in payouts if d <= int(day)))


def fees_paid(net: float, received: float) -> float:
    """The fees paid by a close: the payouts received by it less the net cash at it (the cash moves only by fees and
    payouts), to the millionth of a dollar (the engine's cash is a float sum at the bankroll's magnitude)."""
    return round(float(received) - float(net), 6)


def start_record(cash: Sequence[float], initial: float, pass_days: Iterable[int], funded_days: Iterable[int],
                 payouts: Sequence[tuple[int, float]]) -> dict[str, Any]:
    """One start's record (D-620 (3)(d)). `cash` holds the closes 0 .. observed of the start's run; `payouts` every
    payout's (arrival day, cash) in arrival order (`payout_arrivals`). An event after the observed sessions is not the
    start's."""
    cash = np.asarray(cash, float)
    observed = int(len(cash) - 1)
    rel = cash - float(initial)
    passes = sorted(int(d) for d in pass_days if 0 <= int(d) <= observed)
    funded = sorted(int(d) for d in funded_days if 0 <= int(d) <= observed)
    pays = [(int(d), float(c)) for d, c in payouts if 0 <= int(d) <= observed]
    if any(b[0] < a[0] for a, b in zip(pays, pays[1:])):
        raise ValueError("the payouts are not in arrival order")
    fp = float(passes[0]) if passes else float("nan")
    fy = float(pays[0][0]) if pays else float("nan")
    net_month, fees_month = [], []
    for k in range(1, MONTHS + 1):
        d = MONTH * k
        if d <= observed:
            net_month.append(float(rel[d]))
            fees_month.append(fees_paid(rel[d], _received(pays, d)))
        else:
            net_month.append(float("nan"))
            fees_month.append(float("nan"))
    return {"observed": observed, "pass_days": passes, "funded_days": funded,
            "pay_days": [d for d, _ in pays], "pay_cash": [c for _, c in pays],
            "first_pass": fp, "first_funded": float(funded[0]) if funded else float("nan"), "first_payout": fy,
            "first_payout_cash": float(pays[0][1]) if pays else float("nan"),
            "spent_before_first_pass": spent_before(rel, int(fp)) if np.isfinite(fp) else float("nan"),
            "spent_before_first_payout": spent_before(rel, int(fy)) if np.isfinite(fy) else float("nan"),
            "net_month": net_month, "fees_month": fees_month,
            "net_30": float(rel[EXTRA_NET_DAY]) if EXTRA_NET_DAY <= observed else float("nan")}


def events_upto(pass_days: Iterable[int], funded_days: Iterable[int], pay_days: Iterable[int], h: int
                ) -> tuple[list[int], list[int], list[int]]:
    """The event days up to session h (the identity of D-620 (3)(f) compares a long run's with an exact run's)."""
    return (sorted(int(d) for d in pass_days if int(d) <= int(h)), sorted(int(d) for d in funded_days if int(d) <= int(h)),
            sorted(int(d) for d in pay_days if int(d) <= int(h)))


def record_problems(a: Mapping[str, Any], b: Mapping[str, Any], *, tol: float = TOL) -> list[str]:
    """The record keys on which two records of one start differ (an empty list: the same start): the sessions observed
    and every event day exactly, every dollar figure to `tol` (a blank equal to a blank)."""
    def money(x, y) -> bool:
        x, y = np.asarray(x, float).ravel(), np.asarray(y, float).ravel()
        return len(x) == len(y) and bool(np.all((np.isnan(x) & np.isnan(y)) | (np.abs(x - y) <= tol)))

    out = []
    for k in RECORD_KEYS:
        if k in ("observed", "pass_days", "funded_days", "pay_days"):
            same = (int(a[k]) == int(b[k])) if k == "observed" else ([int(d) for d in a[k]] == [int(d) for d in b[k]])
        else:
            same = money([_nan(v) for v in a[k]] if isinstance(a[k], (list, tuple)) else _nan(a[k]),
                         [_nan(v) for v in b[k]] if isinstance(b[k], (list, tuple)) else _nan(b[k]))
        if not same:
            out.append(k)
    return out


def monthly_mean_over_sd(net_month: Sequence[float]) -> float:
    """A start's twelve monthly changes of net cash (month 1's from zero): their mean over their sample standard
    deviation (ddof 1); blank on a start without twelve months, or with no variation."""
    x = np.asarray(net_month, float)
    if len(x) != MONTHS or not np.isfinite(x).all():
        return float("nan")
    ch = np.diff(np.concatenate([[0.0], x]))
    sd = float(ch.std(ddof=1))
    return float(ch.mean() / sd) if sd > 0 else float("nan")


def payout_rhythm(pay_days: Sequence[int], observed: int, window: int) -> tuple[float, float, float]:
    """D-518's payout rhythm within `window` sessions (`customer_journey.unit`'s, the window a parameter): (the longest
    gap after the first payout -- between payouts and to the window's end; the months after the first payout's month;
    those of them without a payout). A start observed fewer sessions is blank; one observed with no payout in the
    window has no gap and no months."""
    w = int(window)
    if int(observed) < w:
        return float("nan"), float("nan"), float("nan")
    in_w = sorted(int(d) for d in pay_days if int(d) <= w)
    if not in_w:
        return float("nan"), 0.0, 0.0
    marks = in_w + [w]
    gap = float(max(b - a for a, b in zip(marks, marks[1:])))
    m0 = (in_w[0] - 1) // MONTH
    months = list(range(m0 + 1, w // MONTH))
    paid = {(d - 1) // MONTH for d in in_w}
    return gap, float(len(months)), float(sum(1 for m in months if m not in paid))


def concentration(nets: Sequence[float]) -> float:
    """The profit concentration: the net summed over the best quarter of starts (the ceil(n / 4) largest nets) over the
    net summed over all; blank when the total is not positive."""
    x = np.asarray(nets, float)
    x = x[np.isfinite(x)]
    if not len(x):
        return float("nan")
    total = float(x.sum())
    if not total > 0:
        return float("nan")
    k = int(math.ceil(len(x) / 4.0))
    return float(np.sort(x)[::-1][:k].sum() / total)


def quit1(first_payout: np.ndarray, net_stop: np.ndarray, net_end: np.ndarray, day: int) -> np.ndarray:
    """Q1 per start: no payout by session `day` -- the unit stops and keeps its `day`-session net (`net_stop`);
    otherwise its `QUIT_END`-session net (`net_end`)."""
    fp = np.asarray(first_payout, float)
    paid = np.isfinite(fp) & (fp <= int(day))
    return np.where(paid, np.asarray(net_end, float), np.asarray(net_stop, float))


def quit2(first_payout: np.ndarray, net_stop: np.ndarray, net_check: np.ndarray, net_end: np.ndarray) -> np.ndarray:
    """Q2 per start: Q1 at `QUIT_DAY`, and a unit not ahead (net not above zero) at session `QUIT_CHECK` stops there
    and keeps its `QUIT_CHECK`-session net."""
    fp = np.asarray(first_payout, float)
    paid = np.isfinite(fp) & (fp <= QUIT_DAY)
    check = np.asarray(net_check, float)
    return np.where(paid, np.where(check > 0, np.asarray(net_end, float), check), np.asarray(net_stop, float))


# ------------------------------------------------------------------------------------------------ the table


def _nan(x: Any) -> float:
    return float("nan") if x is None else float(x)


def table(records: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """The records as a table, one row a start in the order given: the month-end nets and fees in columns
    (`net_month_k`, `fees_month_k`), the payout days as a tuple (`pays`), the start's year."""
    rows = []
    for r in records:
        row = {"start_day": int(r["start_day"]), "start_date": str(r["start_date"]),
               "year": int(str(r["start_date"])[:4]), "observed": int(r["observed"]),
               "pays": tuple(int(d) for d in r["pay_days"]),
               **{k: _nan(r[k]) for k in ("first_pass", "first_funded", "first_payout", "first_payout_cash",
                                          "spent_before_first_pass", "spent_before_first_payout", "net_30")}}
        for k in range(1, MONTHS + 1):
            row[f"net_month_{k}"] = _nan(r["net_month"][k - 1])
            row[f"fees_month_{k}"] = _nan(r["fees_month"][k - 1])
        rows.append(row)
    cols = ["start_day", "start_date", "year", "observed", "pays", "first_pass", "first_funded", "first_payout",
            "first_payout_cash", "spent_before_first_pass", "spent_before_first_payout", "net_30",
            *[f"net_month_{k}" for k in range(1, MONTHS + 1)], *[f"fees_month_{k}" for k in range(1, MONTHS + 1)]]
    return pd.DataFrame(rows, columns=cols)


def monthly_ratios(t: pd.DataFrame) -> np.ndarray:
    """Every start's `monthly_mean_over_sd` (blank on a start observed fewer than `HORIZON` sessions)."""
    nets = t[[f"net_month_{k}" for k in range(1, MONTHS + 1)]].to_numpy(float)
    obs = t["observed"].to_numpy(int)
    return np.array([monthly_mean_over_sd(nets[i]) if obs[i] >= HORIZON else float("nan") for i in range(len(t))],
                    float)


def effective(record: Mapping[str, Any], h: int) -> Mapping[str, Any]:
    """The record a reading at h sessions reads: the exact-length run's where the long replay's event days up to h
    differed from it (`alt`), else the long replay's."""
    alt = (record.get("alt") or {}).get(str(int(h)))
    return record if alt is None else {**record, **alt, "alt": None}


class Views:
    """One configuration and arm's starts, as each horizon reads them (D-620 (3)(f)): `at(h)` is the table of the long
    replays with every start whose exact h-session run differed replaced by that run's record."""

    def __init__(self, records: Sequence[Mapping[str, Any]]):
        self.records = list(records)
        self.base = table(self.records)
        self._with_alt = sorted({int(h) for r in self.records for h in (r.get("alt") or {})})
        self._cache: dict[int, pd.DataFrame] = {}

    def at(self, h: int) -> pd.DataFrame:
        h = int(h)
        if h not in self._with_alt:
            return self.base
        if h not in self._cache:
            self._cache[h] = table([effective(r, h) for r in self.records])
        return self._cache[h]

    def replaced(self) -> dict[int, int]:
        """{h: the starts read from the exact h-session run}."""
        return {h: sum(1 for r in self.records if str(h) in (r.get("alt") or {})) for h in self._with_alt}

    @property
    def years(self) -> list[int]:
        return sorted(set(self.base["year"].astype(int)))


# ------------------------------------------------------------------------------------------------ shares and means


@dataclass(frozen=True)
class Stat:
    """One share or mean of D-620 (3)(e): per start a numerator and a denominator, the reading their sums' ratio over
    the eligible starts (a share or a mean: the denominator is 1 on every eligible start). `block` is the reading's
    horizon in sessions -- the starts it needs observed, and the bootstrap's block."""

    group: str
    measure: str
    at_days: int
    block: int
    section: str
    fn: Callable[[Views], tuple[np.ndarray, np.ndarray, np.ndarray]]
    year: int | None = None

    @property
    def key(self) -> str:
        return f"{self.group}:{self.measure}@{int(self.at_days)}" + ("" if self.year is None else f"[{self.year}]")


def _obs(t: pd.DataFrame, h: int) -> np.ndarray:
    return t["observed"].to_numpy(int) >= int(h)


def _unit(elig: np.ndarray, value: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    v = np.where(elig, np.asarray(value, float), 0.0)
    return v, elig.astype(float), elig


def _reached_by(col: str, d: int, *, miss: bool = False, year: int | None = None):
    def fn(V: Views):
        t = V.at(d)
        elig = _obs(t, d)
        if year is not None:
            elig = elig & (t["year"].to_numpy(int) == int(year))
        f = t[col].to_numpy(float)
        hit = np.isfinite(f) & (f <= d)
        return _unit(elig, ~hit if miss else hit)
    return fn


def _net_at(V: Views, d: int) -> np.ndarray:
    """Every start's net at session d (a month end, or `EXTRA_NET_DAY`), as the reading at d reads it."""
    t = V.at(d)
    if d == EXTRA_NET_DAY:
        return t["net_30"].to_numpy(float)
    if d % MONTH or not 1 <= d // MONTH <= MONTHS:
        raise ValueError(f"no net is recorded at session {d}")
    return t[f"net_month_{d // MONTH}"].to_numpy(float)


def _net_stat(m: int, positive: bool):
    def fn(V: Views):
        d = MONTH * m
        x = _net_at(V, d)
        elig = _obs(V.at(d), d) & np.isfinite(x)
        return _unit(elig, (x > 0) if positive else x)
    return fn


def _rhythm_stat(window: int):
    def fn(V: Views):
        t = V.at(window)
        elig = _obs(t, window)
        r = [payout_rhythm(p, o, window) for p, o in zip(t["pays"], t["observed"])]
        after = np.array([x[1] if np.isfinite(x[1]) else 0.0 for x in r], float)
        without = np.array([x[2] if np.isfinite(x[2]) else 0.0 for x in r], float)
        return np.where(elig, without, 0.0), np.where(elig, after, 0.0), elig
    return fn


def _quit_stat(day: int | None):
    """Q1 at `day`, or Q2 (None)."""
    def fn(V: Views):
        end = _net_at(V, QUIT_END)
        elig = _obs(V.at(QUIT_END), QUIT_END) & np.isfinite(end)
        if day is None:
            fp = V.at(QUIT_DAY)["first_payout"].to_numpy(float)
            v = quit2(fp, _net_at(V, QUIT_DAY), _net_at(V, QUIT_CHECK), end)
        else:
            fp = V.at(day)["first_payout"].to_numpy(float)
            v = quit1(fp, _net_at(V, day), end, day)
        return _unit(elig, v)
    return fn


def stats(years: Sequence[int] = ()) -> list[Stat]:
    """Every share and mean of D-620 (3)(e), in its order -- the readings `paired_rows` differences. `years`: the start
    years the share paid by session 21 is read in."""
    out: list[Stat] = []
    for d in PASS_DAYS:
        out.append(Stat("first_pass", "share_by", d, d, "metric", _reached_by("first_pass", d)))
    for d in PAYOUT_DAYS:
        out.append(Stat("first_payout", "share_by", d, d, "metric", _reached_by("first_payout", d)))
    out.append(Stat("first_payout", "share_not_reached", PAYOUT_WINDOW, PAYOUT_WINDOW, "metric",
                    _reached_by("first_payout", PAYOUT_WINDOW, miss=True)))
    for m in PERIODIC_MONTHS:
        out.append(Stat("periodic", "share_positive", MONTH * m, MONTH * m, "month", _net_stat(m, True)))
    for m in NO_PAYOUT_MONTHS:
        out.append(Stat("consistency", "share_no_payout_by", MONTH * m, MONTH * m, "month",
                        _reached_by("first_payout", MONTH * m, miss=True)))
    for w in GAP_WINDOWS:
        out.append(Stat("consistency", "share_months_without_payout", w, w, "metric", _rhythm_stat(w)))
    for d in (QUIT_DAY, *QUIT_SENSITIVITY):
        out.append(Stat("quit", "q1_mean_net", d, QUIT_END, "metric", _quit_stat(d)))
    out.append(Stat("quit", "q2_mean_net", QUIT_CHECK, QUIT_END, "metric", _quit_stat(None)))
    for m in LUCK_MONTHS:
        out.append(Stat("luck", "net_mean", MONTH * m, MONTH * m, "month", _net_stat(m, False)))
    for y in years:
        out.append(Stat("luck", "share_paid_by", PAID_BY_YEAR_DAY, PAID_BY_YEAR_DAY, "metric",
                        _reached_by("first_payout", PAID_BY_YEAR_DAY, year=int(y)), year=int(y)))
    return out


def _ratio(num: np.ndarray, den: np.ndarray) -> float:
    d = float(np.sum(den))
    return float(np.sum(num) / d) if d > 0 else float("nan")


def _row(section: str, group: str, measure: str, at_days: int, value: float, n: int, *, year: int | None = None
         ) -> dict[str, Any]:
    key = f"{group}:{measure}@{int(at_days)}" + ("" if year is None else f"[{year}]")
    return {"section": section, "key": key, "group": group, "measure": measure, "at_days": int(at_days),
            "month": int(at_days) // MONTH if section == "month" else float("nan"),
            "year": float("nan") if year is None else int(year), "value": float(value), "n": int(n)}


# ------------------------------------------------------------------------------------------------ the readings


def _sd(x: np.ndarray) -> float:
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return float(x.std(ddof=1)) if len(x) >= 2 else float("nan")


def metric_rows(V: Views) -> list[dict[str, Any]]:
    """One configuration and arm's readings of D-620 (3)(e) (all but the part that needs every configuration,
    `luck_rows`): rows of sections `metric` and `month` -- key, group, measure, at_days, month, year, value, n."""
    rows: list[dict[str, Any]] = []
    for s in stats(V.years):
        num, den, elig = s.fn(V)
        n = int((den > 0).sum()) if s.measure == "share_months_without_payout" else int(elig.sum())
        rows.append(_row(s.section, s.group, s.measure, s.at_days, _ratio(num, den), n, year=s.year))

    # first pass and first payout: the days to it and the cash before it
    for group, col, last, pcts, spent in (("first_pass", "first_pass", PASS_WINDOW, (50, 90), "spent_before_first_pass"),
                                          ("first_payout", "first_payout", PAYOUT_WINDOW, (50, 90, 95),
                                           "spent_before_first_payout")):
        t = V.at(last)
        m = _obs(t, last)
        first = t[col].to_numpy(float)
        for p in pcts:
            rows.append(_row("metric", group, f"days_p{p}", last, _days_q(first[m], last, p), m.sum()))
        r = m & np.isfinite(first) & (first <= last)
        s_ = t[spent].to_numpy(float)[r]
        for p in (50, 90, 95):
            rows.append(_row("metric", group, f"spent_before_p{p}", last, _q(s_, p), r.sum()))
        if group == "first_payout":
            c = t["first_payout_cash"].to_numpy(float)[r]
            for p in (10, 50, 90):
                rows.append(_row("metric", group, f"cash_p{p}", last, _q(c, p), r.sum()))

    # periodic: the net's percentiles
    for mth in PERIODIC_MONTHS:
        d = MONTH * mth
        x = _net_at(V, d)
        x = x[_obs(V.at(d), d) & np.isfinite(x)]
        for p in NET_PERCENTILES:
            rows.append(_row("month", "periodic", f"net_p{p}", d, _q(x, p), len(x)))

    # money back: payouts received per dollar of fees
    for mth in MONEY_BACK_MONTHS:
        d = MONTH * mth
        t = V.at(d)
        net, fees = t[f"net_month_{mth}"].to_numpy(float), t[f"fees_month_{mth}"].to_numpy(float)
        ok = _obs(t, d) & np.isfinite(net) & np.isfinite(fees)
        got = net[ok] + fees[ok]
        rows.append(_row("month", "money_back", "payouts_per_fee_dollar_pooled", d,
                         float(got.sum() / fees[ok].sum()) if ok.any() and fees[ok].sum() > 0 else float("nan"),
                         ok.sum()))
        pos = fees[ok] > 0
        rows.append(_row("month", "money_back", "payouts_per_fee_dollar_median", d, _q(got[pos] / fees[ok][pos], 50),
                         pos.sum()))

    # consistency: the longest gap after the first payout, and the concentration
    for w in GAP_WINDOWS:
        t = V.at(w)
        g = np.array([payout_rhythm(p, o, w)[0] for p, o in zip(t["pays"], t["observed"])], float)
        g = g[np.isfinite(g)]
        rows.append(_row("metric", "consistency", "longest_gap_p50", w, _q(g, 50), len(g)))
        rows.append(_row("metric", "consistency", "longest_gap_p90", w, _q(g, 90), len(g)))
        rows.append(_row("metric", "consistency", "longest_gap_longest", w, float(g.max()) if len(g) else float("nan"),
                         len(g)))
    for mth in CONCENTRATION_MONTHS:
        d = MONTH * mth
        x = _net_at(V, d)
        x = x[_obs(V.at(d), d) & np.isfinite(x)]
        rows.append(_row("month", "consistency", "concentration", d, concentration(x), len(x)))

    # luck against design: the spread of the net across starts, and each start's monthly mean over sd
    for mth in LUCK_MONTHS:
        d = MONTH * mth
        x = _net_at(V, d)
        x = x[_obs(V.at(d), d) & np.isfinite(x)]
        rows.append(_row("month", "luck", "sd_net_across_starts", d, _sd(x), len(x)))
    ms = monthly_ratios(V.at(HORIZON))
    ms = ms[np.isfinite(ms)]
    for p in (10, 50, 90):
        rows.append(_row("metric", "luck", f"monthly_mean_over_sd_p{p}", HORIZON, _q(ms, p), len(ms)))
    return rows


def luck_rows(by_config: Mapping[str, Sequence[Mapping[str, Any]]]) -> list[dict[str, Any]]:
    """The part of luck against design that needs every configuration (one arm): at each of `LUCK_MONTHS` the sample
    standard deviation (ddof 1) of the configurations' mean nets (a row under configuration `all`), and each
    configuration's spread across starts over it. `by_config`: {configuration: its `metric_rows`}."""
    def value(rows, key):
        hit = [float(r["value"]) for r in rows if r["key"] == key]
        return hit[0] if hit else float("nan")

    out: list[dict[str, Any]] = []
    for mth in LUCK_MONTHS:
        d = MONTH * mth
        means = {c: value(rows, f"luck:net_mean@{d}") for c, rows in by_config.items()}
        between = _sd(np.array(list(means.values()), float))
        n = int(np.isfinite(np.array(list(means.values()), float)).sum())
        out.append({"config": "all", **_row("month", "luck", "sd_of_configuration_means", d, between, n)})
        for c, rows in by_config.items():
            within = value(rows, f"luck:sd_net_across_starts@{d}")
            ratio = within / between if np.isfinite(within) and np.isfinite(between) and between > 0 else float("nan")
            out.append({"config": c, **_row("month", "luck", "sd_across_starts_over_sd_of_configuration_means", d,
                                            ratio, n)})
    return out


# ------------------------------------------------------------------------------------------------ the bootstrap


def block_indices(n: int, block: int, *, draws: int = BOOT_DRAWS, seed: int = BOOT_SEED) -> np.ndarray | None:
    """The moving-block bootstrap's resamples of n ordered starts: `draws` rows of n indices, each row ceil(n / block)
    blocks of `block` consecutive starts -- every block's first start drawn uniformly from the n - block + 1 there are
    -- laid end to end and cut to n. None when there are fewer starts than one block."""
    n, b = int(n), int(block)
    if b < 1:
        raise ValueError(f"a block is at least one start, got {block!r}")
    if n < b or n < 1:
        return None
    rng = np.random.default_rng(int(seed))
    k = -(-n // b)
    first = rng.integers(0, n - b + 1, size=(int(draws), k))
    return (first[:, :, None] + np.arange(b)[None, None, :]).reshape(int(draws), k * b)[:, :n]


def paired_interval(num_a: Sequence[float], den_a: Sequence[float], num_b: Sequence[float], den_b: Sequence[float],
                    block: int, *, alpha: float = ALPHA, draws: int = BOOT_DRAWS, seed: int = BOOT_SEED
                    ) -> dict[str, Any]:
    """A paired difference on the same ordered starts -- sum(num_a) / sum(den_a) - sum(num_b) / sum(den_b) (a share's
    or a mean's denominators are 1) -- and its two-sided 1 - alpha percentile interval from the moving-block bootstrap
    (D-620 (1)(c) G2; `block_indices`). The interval is blank with fewer starts than one block, or when a resample
    leaves a denominator empty."""
    na, da, nb, db = (np.asarray(x, float) for x in (num_a, den_a, num_b, den_b))
    n = len(na)
    if not (len(da) == len(nb) == len(db) == n):
        raise ValueError("a paired difference needs the same starts on both sides")
    out = {"value": _ratio(na, da), "reference": _ratio(nb, db), "n": int(n), "block": int(block), "draws": int(draws),
           "seed": int(seed), "alpha": float(alpha), "lo": float("nan"), "hi": float("nan")}
    out["difference"] = out["value"] - out["reference"]
    idx = block_indices(n, block, draws=draws, seed=seed)
    if idx is None:
        return out
    sa, sb = da[idx].sum(axis=1), db[idx].sum(axis=1)
    if (sa <= 0).any() or (sb <= 0).any():
        return out
    boot = na[idx].sum(axis=1) / sa - nb[idx].sum(axis=1) / sb
    out["lo"] = float(np.percentile(boot, 100.0 * alpha / 2.0))
    out["hi"] = float(np.percentile(boot, 100.0 * (1.0 - alpha / 2.0)))
    return out


def paired_rows(V: Views, R: Views, *, alpha: float = ALPHA, draws: int = BOOT_DRAWS, seed: int = BOOT_SEED
                ) -> list[dict[str, Any]]:
    """A configuration against the reference (the same arm) on their common start days, in date order: for every share
    and mean (`stats`) the two readings on the starts both hold eligible, their difference and its interval."""
    a_dates, r_dates = list(V.base["start_date"]), list(R.base["start_date"])
    ia = {d: i for i, d in enumerate(a_dates)}
    ir = {d: i for i, d in enumerate(r_dates)}
    common = sorted(set(ia) & set(ir))
    pa = np.array([ia[d] for d in common], int)
    pr = np.array([ir[d] for d in common], int)
    rows = []
    for s in stats(sorted(set(V.years) & set(R.years))):
        na, da, ea = s.fn(V)
        nb, db, eb = s.fn(R)
        if len(common):
            ok = ea[pa] & eb[pr]
            p = paired_interval(na[pa][ok], da[pa][ok], nb[pr][ok], db[pr][ok], s.block, alpha=alpha, draws=draws,
                                seed=seed)
        else:
            p = paired_interval([], [], [], [], s.block, alpha=alpha, draws=draws, seed=seed)
        rows.append({**_row("paired", s.group, s.measure, s.at_days, p["value"], p["n"], year=s.year),
                     "reference_value": p["reference"], "difference": p["difference"], "lo": p["lo"], "hi": p["hi"],
                     "alpha": p["alpha"], "block": p["block"], "draws": p["draws"], "seed": p["seed"]})
    return rows


# ------------------------------------------------------------------------------------------------ the declaration

#: DECISIONS.md's D-620 row (LF, the line itself): its sha256 and the phrases this module's constants rest on
DECLARATION_SHA256 = "3b6574afc220ce1b36ca624f90293cc5ad58b01baeaa7f68e4e71aefc0a0eafb"
D620_WORDS = (
    "its first study U1, a start-day measurement over twelve months that runs no new design",
    f"each start run for min({HORIZON}, sessions left) sessions",
    "a reading at h sessions is read only on starts with at least h sessions left",
    f"Day 0 is the purchase evening, day k closes the k-th session, a month is {MONTH} sessions",
    "`verdict` (every R shifted to the bound the design's gate read; a cell on P-16's trades takes P-16's) and `point`",
    f"nine, none new, each at both arms, {N_READINGS} readings counted under `{FAMILY_ID}`",
    "P-15 (`rc_s100_all`); P-16 (`rc_s150_all_nr`)",
    "the funded leg's realised risk held to the 25-point cell's (D-542, D-544), four Topstep seats (D-567's 4 + 0), "
    f"five Topstep seats plus one Lucid seat (D-593's 5 + 1, `{LUCID_LABEL}`), and the London window (D-538's "
    "`rc_s150_london`)",
    "every payout's arrival day and its cash, from the engine's own records (`payout_days`, `payout_cash`)",
    "the cash at each month end 1 to 12 and the fees paid by each",
    "the deepest cash below the start before the first pass and before the first payout",
    "an unreached unit counts as beyond and a percentile beyond the observed days is blank, as D-518 (3)",
    "the share reached by " + " / ".join(str(d) for d in PASS_DAYS) + " sessions, days p50 / p90, cash spent before "
    "it p50 / p90 / p95",
    "the share by " + " / ".join(str(d) for d in PAYOUT_DAYS) + ", days p50 / p90 / p95, cash spent before it p50 / "
    f"p90 / p95 among units reaching it by {PAYOUT_WINDOW} with the share not reaching it beside, and the first "
    "payout's cash p10 / p50 / p90",
    "at months 1, 2, 3, 6, 9 and 12 the share of starts with net cash above zero and the net's "
    + " / ".join(f"p{p}" for p in NET_PERCENTILES),
    "payouts received per dollar of fees at months 1, 3, 6 and 12, pooled over starts and the per-start median",
    "the share with no payout by months 1, 2, 3 and 6, the longest gap after the first payout within 126 and within "
    "252 sessions p50 / p90 / longest, the share of months after the first payout's with none",
    "the concentration at months 3, 6 and 12 (the net summed over the best quarter of starts over the net summed over "
    "all, blank when the total is not positive)",
    f"Q1 (no payout by session {QUIT_DAY}: the unit stops and keeps its {QUIT_DAY}-session net; otherwise its "
    f"{QUIT_END}-session net) and Q2 (Q1, and a unit not ahead at session {QUIT_CHECK} stops there and keeps its "
    f"{QUIT_CHECK}-session net)",
    "Q1 and Q2 of (1)(a), with Q1 read also at sessions 30 and 42 as a sensitivity",
    "the standard deviation of the net across starts inside a configuration against the standard deviation of the "
    "configurations' means at months 1, 3, 6 and 12, the share paid by session 21 by start year, and per start with "
    "252 sessions the mean over the standard deviation of its twelve monthly changes",
    "on the common start days, the difference of each share and mean above with G2's bootstrap interval",
    f"a moving-block bootstrap with blocks as long as the reading's horizon (seed {BOOT_SEED}, 2,000 draws)",
    "a long replay's event days up to h equal those of a run of exactly h sessions at "
    + ", ".join(str(h) for h in EXACT[:-1]) + f" and {EXACT[-1]} (D-518 (5)) -- where they differ a measure is read "
    "from the exact-length run",
    "The funded-capped and London cells have no start-day rows on record: their identity is the cell's pinned trades "
    "and the settings of the registered file's beside rows, stated beside their readings",
    f"`results/{RESULT}.csv` (sections " + ", ".join(f"`{s}`" for s in SECTIONS[:-1]) + f", `{SECTIONS[-1]}`) and "
    f"`results/{PAYOUTS_RESULT}.csv` (one row per payout: configuration, arm, start, day, cash)",
    f"campaign {CAMPAIGN_SEED}, coin {COIN_SEED}; a replay draws nothing",
    "**Selection: none.**",
)


def declaration(path: Path | str | None = None) -> dict[str, Any]:
    """DECISIONS.md's D-620 row (LF line ends, the line itself) and its sha256 (`rc150_added_lucid.declaration`'s
    way)."""
    p = Path(path) if path is not None else Path(__file__).resolve().parents[2] / "DECISIONS.md"
    text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    rows = [line for line in text.split("\n") if line.startswith(f"| {DECISION} |")]
    row = rows[0] if len(rows) == 1 else ""
    return {"path": str(p), "rows": len(rows), "row": row, "sha256": hashlib.sha256(row.encode("utf-8")).hexdigest()}


def declaration_problems(decl: Mapping[str, Any]) -> list[str]:
    """Every way this module's constants differ from D-620's row (an empty list: they agree)."""
    out = []
    if int(decl["rows"]) != 1:
        out.append(f"DECISIONS.md holds {decl['rows']} {DECISION} rows, not one")
    if str(decl["sha256"]) != DECLARATION_SHA256:
        out.append(f"the {DECISION} row's sha256 is {str(decl['sha256'])[:16]}, not the pinned "
                   f"{DECLARATION_SHA256[:16]}")
    row = re.sub(r"\s+", " ", str(decl["row"]))
    out += [f"{DECISION} does not say {w!r}" for w in D620_WORDS if w not in row]
    if BOOT_DRAWS != 2000 or HORIZON != 252 or N_READINGS != 18 or len(CONFIGS) != 9:
        out.append("the module's draws, horizon or configuration count are not D-620's")
    return out


__all__ = ["DECISION", "STUDY", "RESULT", "PAYOUTS_RESULT", "FAMILY_ID", "SCRIPT", "READING", "MONTH", "MONTHS",
           "HORIZON", "EXACT", "PASS_DAYS", "PAYOUT_DAYS", "PASS_WINDOW", "PAYOUT_WINDOW", "PERIODIC_MONTHS",
           "NET_PERCENTILES", "MONEY_BACK_MONTHS", "NO_PAYOUT_MONTHS", "GAP_WINDOWS", "CONCENTRATION_MONTHS",
           "LUCK_MONTHS", "QUIT_DAY", "QUIT_SENSITIVITY", "QUIT_CHECK", "QUIT_END", "EXTRA_NET_DAY", "BOOT_SEED",
           "BOOT_DRAWS", "ALPHA", "CAMPAIGN_SEED", "COIN_SEED", "ARMS", "CONFIGS", "N_READINGS", "REFERENCE",
           "LIMIT_REFERENCE", "LUCID_LABEL", "SECTIONS", "RECORD_KEYS", "payout_arrivals", "fees_paid", "start_record",
           "events_upto", "record_problems", "monthly_mean_over_sd", "payout_rhythm", "concentration", "quit1", "quit2", "table",
           "monthly_ratios", "effective", "Views", "Stat", "stats", "metric_rows", "luck_rows", "block_indices", "paired_interval",
           "paired_rows", "DECLARATION_SHA256", "D620_WORDS", "declaration", "declaration_problems"]
