"""EXPLORATORY (D-649; program U, measurement U2): the funded account's day budget -- the pure side.

`scripts/u_xfa_day_budget.py` re-runs the registered gate campaigns of P-14, P-15 and P-16 with the engine's own
per-trade ledger and daily account recorder on, proves each re-run path is the registered run's, and hands this module
what it read off the records. Nothing here touches the engine or a file: it holds

* the declaration's pin (`declaration`, `declaration_problems`: DECISIONS.md's D-649 row and the phrases the build's
  constants rest on);
* `account_measures` -- one funded account's sessions (day P&L, whether it traded, the day's class, the engine's
  eligibility flag, what it requested, its balance) read into the additions D-649 (3) lists: the opening trade, the
  sessions and trading days to the fifth winning day and to the first payout request, the days before a first payout by
  class, and what the Consistency test would have read day by day (`consistency_read`: the engine's own arithmetic --
  trading days, the window's profit, its best day -- from `propedge/campaign/lockstep.py`'s `FundedAccount.trade_day`,
  on the days before the account's first Standard-path request);
* `summarise` -- every section of the result in long format (section, group, measure, value, n, basis, note):
  D-363's sections (the evaluation funnel, the funded funnel and how each account ended, the days by class, timing,
  survival and accrual, payouts, signal supply, the table's leaves, loss-limit clusters) and the additions (the opening
  trade, after the opening, winning days per account-week, the Consistency description, the budget before a first
  payout, what the records cannot give).

**Words.** A *session* is a trading session an account was live for, counted from its first (1); a *trading day* is a
session on which it took at least one trade (the firm's sense, 8284208); a *qualifying winning day* is a day of at
least the Standard path's winning-day minimum (8284233). `n` is the number of units the value rests on (the
denominator of a share, the sample of a percentile). Percentiles are numpy's linear ones.

**The Consistency block is a description.** These accounts ran on the Standard path under a table solved for it; the
block reads their recorded days through the Consistency test and says when it would first have read eligible. It is
not a run on that path: on it the table's decisions, the cap and the cycle after a payout would all differ. Every row
of it says so in `basis`.
"""
from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

DECISION = "D-649"
STUDY = "U2"
RESULT = "u_xfa_day_budget"
SCRIPT = "scripts/u_xfa_day_budget.py"
READING = ("EXPLORATORY (D-649; program U's second measurement, U2): the funded account's days on registered designs, "
           "read off the engine's own records; no design run, no variant counted, nothing selected")
RECORDS = "the engine's records"
DESCRIPTION = ("a description from the records of Standard-path accounts, not a run on the Consistency path "
               "(D-649 (3))")
IDENTITY = "identity"
MISSING = "missing: the existing records cannot give it"
NOTE = "note"

DESIGNS = ("p14", "p15", "p16")
ARMS = ("verdict", "point")                 # the gate row's lower-bound arm, and the trades as traded
SHIFT_OF = {"verdict": "lower_bound", "point": "point"}
PATHS = 100                                 # D-649 (1): each design's first 100 paths
HORIZON = 504                               # D-649 (1): 504 days
WEEK = 5                                    # sessions in an account-week
#: D-363's day classes (`scripts/fv3_xfa_time_budget.py`'s `DAY_CLASSES`, checked by the script) and D-649's names
DAY_CLASSES = ("no_signal", "sat_out", "losing", "win_under_min", "qualifying_win")
CLASS_LABEL = {"no_signal": "no_trade_routed", "sat_out": "sat_out_by_table", "losing": "losing_day",
               "win_under_min": "winning_day_under_min", "qualifying_win": "qualifying_winning_day"}
SINCE = (5, 10, 15, 20, 30, 40, 60, 90)     # D-363's days since activation
COMBINE_ENDS = ("passed", "loss_limit", "closed_by_policy", "open_at_end")
FUNDED_ENDS = ("loss_limit", "closed_by_policy", "open_at_end", "other")
SECTIONS = ("identity", "evaluation_funnel", "funded_funnel", "funded_end", "funded_days", "funded_timing",
            "survival_accrual", "payouts", "signal_supply", "table_leaves", "clusters", "opening_trade",
            "after_opening", "winning_days_per_week", "consistency_description", "budget_before_first_payout",
            "missing", "notes")
COLUMNS = ("design", "prereg", "arm", "section", "group", "measure", "value", "n", "basis", "note")

#: one funded account's row: D-363's columns (`fv3_xfa_time_budget.xfa_rows`) and this measurement's additions
D363_COLS = ("path", "index", "activation_day", "life_days", "trades", "n_payouts", "first_eligible_after",
             "first_paid_after", "payout_cash", "end", *DAY_CLASSES)
MEASURE_COLS = ("trading_days", "winning_days", *[f"wins_by_{k}" for k in SINCE], "pre_sessions",
                *[f"pre_{c}" for c in DAY_CLASSES], "win5_session", "win5_trading_days", "req1_session",
                "req1_trading_days", "profit_at_req1", "opened", "open_session", "open_pnl", "open_day_pnl",
                "open_won", "lost_on_open", "open_room_after", "open_policy_risk", "open_policy_rr",
                "open_realised_risk", "open_contracts", "open_day_share", "best_day_share_at_req1",
                "cons_days_read", "cons_days_blocked", "cons_session", "cons_min_session")
ACC_COLS = (*D363_COLS, "observable_sessions", *MEASURE_COLS)

#: sha256 of DECISIONS.md's D-649 row (LF line ends, the line itself), pinned when this module was built
DECLARATION_SHA256 = "bcb42c70428f8bdb1b6b13241efaeae7c27be9b564713efbabdbe50e2e991515"
#: the phrases of D-649's row this build's constants rest on (whitespace-normalised)
D649_WORDS = (
    "the funded account's day budget on the three rows to beat (P-14, P-15, P-16)",
    "it runs no new design, counts no variant, selects nothing (EXPLORATORY)",
    "each design's registered gate campaign rebuilt as its registered run built it (the registered seed, 504 days, "
    "0 % denial, the Standard path, the placement off), its first 100 paths, the bound arm and the point arm",
    "existing recorders only; no engine file is changed, and a reading the records cannot give is reported as missing",
    "each re-run path's final cash, fees, payouts, funded accounts, evaluations and trades equal the registered run's "
    "own figures for the same paths",
    "or nothing is written",
    "(no trade routed to it, sat out by the table, a losing day, a winning day under $150, a qualifying winning day)",
    "the opening funded trade -- the share of accounts lost on it, and the opening day's share of the profit at the "
    "first payout",
    "the trading days and the sessions to the fifth winning day and to the first payout's request",
    "winning days per account-week while alive",
    "(three trading days, best day at most 40 % of the window's profit)",
    "a description from the records, not a run on that path",
    "`results/u_xfa_day_budget.csv`",
)

NAN = float("nan")


# ------------------------------------------------------------------------------------------------ the declaration


def declaration(path: Path | str | None = None) -> dict[str, Any]:
    """DECISIONS.md's D-649 row (LF line ends, the line itself) and its sha256 (`user_journey.declaration`'s way)."""
    p = Path(path) if path is not None else Path(__file__).resolve().parents[2] / "DECISIONS.md"
    text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    rows = [line for line in text.split("\n") if line.startswith(f"| {DECISION} |")]
    row = rows[0] if len(rows) == 1 else ""
    return {"path": str(p), "rows": len(rows), "row": row, "sha256": hashlib.sha256(row.encode("utf-8")).hexdigest()}


def declaration_problems(decl: Mapping[str, Any]) -> list[str]:
    """Every way this module's constants differ from D-649's row (an empty list: they agree)."""
    out = []
    if int(decl["rows"]) != 1:
        out.append(f"DECISIONS.md holds {decl['rows']} {DECISION} rows, not one")
    if str(decl["sha256"]) != DECLARATION_SHA256:
        out.append(f"the {DECISION} row's sha256 is {str(decl['sha256'])[:16]}, not the pinned "
                   f"{DECLARATION_SHA256[:16]}")
    row = re.sub(r"\s+", " ", str(decl["row"]))
    out += [f"{DECISION} does not say {w!r}" for w in D649_WORDS if w not in row]
    if PATHS != 100 or HORIZON != 504 or DESIGNS != ("p14", "p15", "p16") or len(ARMS) != 2:
        out.append("the module's paths, horizon, designs or arms are not D-649's")
    return out


# ------------------------------------------------------------------------------------------------ the rule


@dataclass(frozen=True)
class Rule:
    """The verified rule values the readings lean on, each from the ledger (`config/rules.yaml`) by the script
    (`rule_of`), never typed here: the Standard path's winning-day minimum, winning days and cap (8284233); the
    Consistency path's minimum trading days, largest-day share and cap (8284208); the smallest payout and the share of
    the balance a payout may take; and the campaign's own payout fraction and kept balance (its protocol's). `eps` is
    the engine's tolerance (`lockstep.EPS`)."""
    win_min: float
    win_days: int
    std_cap: float
    cons_min_days: int
    cons_max_day_frac: float
    cons_cap: float
    payout_min: float
    payout_max_frac: float
    payout_frac: float = 1.0
    keep_balance: float = 0.0
    eps: float = 1e-9

    def as_dict(self) -> dict[str, float]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


# ------------------------------------------------------------------------------------------------ one account


def _first(mask: np.ndarray) -> int | None:
    hit = np.flatnonzero(mask)
    return int(hit[0]) if len(hit) else None


def consistency_read(pnl: Sequence[float], traded: Sequence[bool], rule: Rule) -> dict[str, np.ndarray]:
    """What the Consistency test would read at each close of a window that starts on the first session given, by the
    engine's arithmetic (`FundedAccount.trade_day`, the branch for a payout path other than the Standard one): the
    window's trading days (sessions with a trade), its profit (every session's P&L) and its best day (never below
    zero); `read` -- the test has its days and a profit; `met` -- and the best day is at most the largest-day share of
    the profit; `met_min` -- and the request the balance allows (the smaller of the balance's share and the path's cap,
    at the campaign's payout fraction, less any kept balance) is at least the smallest payout. The balance of an
    account that has requested nothing is its profit, so the profit stands for it."""
    p = np.asarray(pnl, float)
    t = np.asarray(traded, bool)
    if not len(p):
        z = np.zeros(0, bool)
        return {"read": z, "met": z, "met_min": z, "profit": np.zeros(0), "best": np.zeros(0)}
    days, profit = np.cumsum(t), np.cumsum(p)
    best = np.maximum.accumulate(np.maximum(p, 0.0))
    read = (days >= int(rule.cons_min_days)) & (profit > 0)
    met = read & (best <= float(rule.cons_max_day_frac) * profit + rule.eps)
    request = float(rule.payout_frac) * np.minimum(float(rule.payout_max_frac) * profit, float(rule.cons_cap))
    if rule.keep_balance > 0:
        request = np.minimum(request, np.maximum(profit - float(rule.keep_balance), 0.0))
    return {"read": read, "met": met, "met_min": met & (request >= float(rule.payout_min) - rule.eps),
            "profit": profit, "best": best}


def account_measures(*, pnl: Sequence[float], traded: Sequence[bool], classes: Sequence[str],
                     requested: Sequence[float], eligible: Sequence[bool], balance: Sequence[float], end: str,
                     opening: Mapping[str, Any] | None, rule: Rule) -> tuple[dict[str, Any], list[str]]:
    """One funded account's sessions, in order from its first, as `MEASURE_COLS` -- and the ways its records disagree
    with themselves (empty when they agree; the script refuses on any).

    `pnl`, `traded`, `classes`, `requested` (the gross payout requested at the close, 0 for none), `eligible` (the
    engine's flag at the close, before any request) and `balance` (at the close, after any request) have one entry a
    session; `end` is D-363's ending; `opening` is the account's first trade -- its session's position (0-based), its
    P&L, the balance after it, the floor it was read against and what the ledger says of its size -- or None for an
    account that never traded.

    The sessions *before a first payout* are those up to and including the first request's, or every one for an account
    that never requested. The fifth winning day is the session on which the qualifying days reach the Standard path's
    count; it must be the engine's first eligible close. The Consistency read covers the same sessions, less the close
    an account ended on at the loss limit (the engine reads no payout test there)."""
    p = np.asarray(pnl, float)
    n = len(p)
    tr = np.asarray(traded, bool)
    req = np.asarray(requested, float)
    elig = np.asarray(eligible, bool)
    bal = np.asarray(balance, float)
    cls = [str(c) for c in classes]
    if not (len(tr) == len(req) == len(elig) == len(bal) == len(cls) == n):
        raise ValueError("an account's session arrays differ in length")
    bad: list[str] = []
    qual = np.array([c == "qualifying_win" for c in cls], bool)
    cum_p, cum_t, cum_q = np.cumsum(p), np.cumsum(tr), np.cumsum(qual)
    out: dict[str, Any] = {"trading_days": int(tr.sum()), "winning_days": int(qual.sum())}
    for k in SINCE:
        out[f"wins_by_{k}"] = int(qual[:k].sum())
    r = _first(req > 0)
    pre = n if r is None else r + 1
    out["pre_sessions"] = int(pre)
    for c in DAY_CLASSES:
        out[f"pre_{c}"] = int(sum(1 for x in cls[:pre] if x == c))
    w = _first(cum_q[:pre] >= int(rule.win_days))
    if w != _first(elig[:pre]):
        bad.append("the session its qualifying days reach the Standard path's count is not the engine's first "
                   "eligible close")
    out["win5_session"] = NAN if w is None else float(w + 1)
    out["win5_trading_days"] = NAN if w is None else float(cum_t[w])
    out["req1_session"] = NAN if r is None else float(r + 1)
    out["req1_trading_days"] = NAN if r is None else float(cum_t[r])
    profit = NAN if r is None else float(cum_p[r])
    out["profit_at_req1"] = profit
    quiet = n if r is None else r               # the closes before any request: the balance is the profit so far
    if quiet and not np.allclose(bal[:quiet], cum_p[:quiet], rtol=0.0, atol=1e-6):
        bad.append("its balance before its first request is not the sum of its day P&L")
    # the opening trade
    blank = {"open_session": NAN, "open_pnl": NAN, "open_day_pnl": NAN, "open_won": False, "lost_on_open": False,
             "open_room_after": NAN, "open_policy_risk": NAN, "open_policy_rr": NAN, "open_realised_risk": NAN,
             "open_contracts": NAN, "open_day_share": NAN}
    out["opened"] = opening is not None
    out.update(blank)
    if opening is None:
        if tr.any():
            bad.append("it traded and has no opening trade")
    else:
        pos = int(opening["session"])
        if not (0 <= pos < n) or not tr[pos] or tr[:pos].any():
            bad.append("its opening trade is not on its first trading day")
        else:
            o_pnl = float(opening["pnl"])
            lost = bool(float(opening["balance_after"]) <= float(opening["floor"]) + rule.eps)
            if lost and not (str(end) == "loss_limit" and pos == n - 1 and int(tr.sum()) == 1):
                bad.append("it reached its floor on its opening trade and did not end there")
            out.update({"open_session": float(pos + 1), "open_pnl": o_pnl, "open_day_pnl": float(p[pos]),
                        "open_won": bool(o_pnl > 0), "lost_on_open": lost,
                        "open_room_after": float(opening["balance_after"]) - float(opening["floor"])})
            for k in ("policy_risk", "policy_rr", "realised_risk", "contracts"):
                v = opening.get(k)
                out[f"open_{k}"] = NAN if v is None else float(v)
            if r is not None and profit > 0:
                if pos > r:
                    bad.append("its first request precedes its opening trade")
                else:
                    out["open_day_share"] = float(p[pos]) / profit
    # the Consistency test on the sessions before a first payout (a description; see the module's docstring)
    last = pre - 1 if (r is None and str(end) == "loss_limit" and pre > 0) else pre
    c = consistency_read(p[:last], tr[:last], rule)
    out["cons_days_read"] = int(c["read"].sum())
    out["cons_days_blocked"] = int((c["read"] & ~c["met"]).sum())
    k1, k2 = _first(c["met"]), _first(c["met_min"])
    out["cons_session"] = NAN if k1 is None else float(k1 + 1)
    out["cons_min_session"] = NAN if k2 is None else float(k2 + 1)
    out["best_day_share_at_req1"] = (float(max(0.0, float(p[:r + 1].max()))) / profit
                                     if (r is not None and profit > 0) else NAN)
    return {k: out[k] for k in MEASURE_COLS}, bad


# ------------------------------------------------------------------------------------------------ the tables


def _row(section: str, group: Any, measure: str, value: Any, n: Any, *, basis: str = RECORDS, note: str = ""
         ) -> dict[str, Any]:
    v = NAN if value is None else float(value)
    return {"section": section, "group": str(group), "measure": str(measure), "value": v, "n": int(n),
            "basis": basis, "note": note}


def _share(k: float, n: float) -> float:
    return float(k) / float(n) if n else NAN


def _finite(v: Any) -> np.ndarray:
    """The finite values of a column, list or array, as floats."""
    a = pd.to_numeric(pd.Series(v if isinstance(v, (pd.Series, np.ndarray)) else list(v), dtype=object),
                      errors="coerce").to_numpy(dtype=float)
    return a[np.isfinite(a)]


def _stat(v: np.ndarray, stat: str) -> float:
    if not len(v):
        return NAN
    if stat == "mean":
        return float(v.mean())
    if stat == "median":
        return float(np.quantile(v, 0.5))
    return float(np.quantile(v, int(stat[1:]) / 100.0))


def _dist(section: str, group: Any, name: str, values: Any, *, stats: Sequence[str] = ("p10", "p50", "p90", "mean"),
          basis: str = RECORDS, note: str = "") -> list[dict[str, Any]]:
    """One row a statistic of the finite values (`p10` ... numpy's linear percentiles); n the values counted."""
    v = _finite(values)
    return [_row(section, group, f"{name}_{s}", _stat(v, s), len(v), basis=basis, note=note) for s in stats]


def _flag(s: pd.Series) -> np.ndarray:
    return s.astype(bool).to_numpy() if len(s) else np.zeros(0, bool)


def evaluation_funnel(cmb: pd.DataFrame, n_paths: int) -> list[dict[str, Any]]:
    """D-363's Combine funnel: attempts, and for each ending its count, share of attempts, number a path and the
    median days and trades an attempt took."""
    S, att = "evaluation_funnel", len(cmb)
    out = [_row(S, "all", "attempts", att, n_paths), _row(S, "all", "per_path", _share(att, n_paths), n_paths),
           *_dist(S, "all", "days", cmb["days"] if att else [], stats=("median",)),
           *_dist(S, "all", "trades", cmb["trades"] if att else [], stats=("median",))]
    for end in COMBINE_ENDS:
        k = cmb[cmb["end"] == end] if att else cmb
        out += [_row(S, end, "count", len(k), att), _row(S, end, "share", _share(len(k), att), att),
                _row(S, end, "per_path", _share(len(k), n_paths), n_paths),
                *_dist(S, end, "days", k["days"] if len(k) else [], stats=("median",)),
                *_dist(S, end, "trades", k["trades"] if len(k) else [], stats=("median",))]
    return out


def funded_funnel(acc: pd.DataFrame, n_paths: int) -> list[dict[str, Any]]:
    """D-363's funded funnel -- activated, reached eligibility, paid at least once (count, share, a path, median life)
    -- the payouts an account took, and how each ended (with the share of each ending that was ever paid)."""
    S, nx = "funded_funnel", len(acc)
    elig, paid = acc["first_eligible_after"].notna().to_numpy(), (acc["n_payouts"] > 0).to_numpy()
    out = []
    for name, mask in (("activated", np.ones(nx, bool)), ("reached_eligibility", elig), ("paid_at_least_once", paid)):
        k = acc[mask]
        out += [_row(S, name, "count", len(k), nx), _row(S, name, "share", _share(len(k), nx), nx),
                _row(S, name, "per_path", _share(len(k), n_paths), n_paths),
                *_dist(S, name, "life_sessions", k["life_days"], stats=("median",))]
    out += _dist(S, "activated", "payouts_per_account", acc["n_payouts"], stats=("mean",))
    out += _dist(S, "paid_at_least_once", "payouts_per_account", acc[paid]["n_payouts"], stats=("mean", "median"))
    E = "funded_end"
    for end in FUNDED_ENDS:
        k = acc[acc["end"] == end]
        out += [_row(E, end, "count", len(k), nx), _row(E, end, "share", _share(len(k), nx), nx),
                _row(E, end, "per_path", _share(len(k), n_paths), n_paths),
                *_dist(E, end, "life_sessions", k["life_days"], stats=("median",)),
                _row(E, end, "share_paid", _share(int((k["n_payouts"] > 0).sum()), len(k)), len(k))]
    return out


def funded_days(acc: pd.DataFrame) -> list[dict[str, Any]]:
    """D-363's days by class -- over every funded account, those paid at least once and those never paid."""
    S, nx = "funded_days", len(acc)
    paid = (acc["n_payouts"] > 0).to_numpy()
    out = []
    for name, mask in (("all", np.ones(nx, bool)), ("paid", paid), ("never_paid", ~paid)):
        k = acc[mask]
        tot = float(k[list(DAY_CLASSES)].to_numpy(float).sum()) if len(k) else 0.0
        out += [_row(S, name, "accounts", len(k), nx), _row(S, name, "days", tot, len(k)),
                _row(S, name, "days_per_account", _share(tot, len(k)), len(k))]
        out += [_row(S, name, f"share_{CLASS_LABEL[c]}", _share(float(k[c].sum()) if len(k) else 0.0, tot), tot)
                for c in DAY_CLASSES]
    return out


def funded_timing(acc: pd.DataFrame) -> list[dict[str, Any]]:
    """D-363's timing: the session an account first read eligible on and the one it first requested a payout on."""
    S = "funded_timing"
    return (_dist(S, "reached_eligibility", "first_eligible_session", acc["first_eligible_after"],
                  stats=("p10", "median", "p90"))
            + _dist(S, "paid_at_least_once", "first_request_session", acc["first_paid_after"],
                    stats=("p10", "median", "p90")))


def survival_accrual(acc: pd.DataFrame) -> list[dict[str, Any]]:
    """D-363's accrual against survival by session since activation -- the share of accounts live for at least k
    sessions, eligible by k and paid by k -- with, beside, the same among the accounts the horizon left at least k
    sessions to (an account activated late is cut short by the horizon, not by its trades), and the qualifying winning
    days the accounts live at k had by then."""
    S, nx = "survival_accrual", len(acc)
    life = acc["life_days"].to_numpy(float) if nx else np.zeros(0)
    el = acc["first_eligible_after"].to_numpy(float) if nx else np.zeros(0)
    pd_ = acc["first_paid_after"].to_numpy(float) if nx else np.zeros(0)
    obs = acc["observable_sessions"].to_numpy(float) if nx else np.zeros(0)
    out = []
    for k in SINCE:
        g = f"session_{k}"
        seen = obs >= k
        alive = life >= k
        out += [_row(S, g, "share_alive", _share(int(alive.sum()), nx), nx),
                _row(S, g, "share_eligible_by", _share(int((el <= k).sum()), nx), nx),
                _row(S, g, "share_paid_by", _share(int((pd_ <= k).sum()), nx), nx),
                _row(S, g, "share_alive_among_observable", _share(int((alive & seen).sum()), int(seen.sum())),
                     int(seen.sum())),
                _row(S, g, "share_eligible_by_among_observable", _share(int(((el <= k) & seen).sum()), int(seen.sum())),
                     int(seen.sum())),
                _row(S, g, "share_paid_by_among_observable", _share(int(((pd_ <= k) & seen).sum()), int(seen.sum())),
                     int(seen.sum())),
                *_dist(S, g, "winning_days_among_alive", acc[f"wins_by_{k}"].to_numpy(float)[alive] if nx else [],
                       stats=("mean",))]
    return out


def payouts(acc: pd.DataFrame, rule: Rule) -> list[dict[str, Any]]:
    """D-363's payouts: every payout's cash to the trader, against the Standard path's cap."""
    S = "payouts"
    cash = np.array([float(c) for t in acc["payout_cash"] for c in (t or ())], float) if len(acc) else np.zeros(0)
    paid = int((acc["n_payouts"] > 0).sum()) if len(acc) else 0
    return [_row(S, "all", "count", len(cash), paid), _row(S, "all", "per_paid_account", _share(len(cash), paid), paid),
            *_dist(S, "all", "cash", cash, stats=("median", "mean")),
            _row(S, "all", "share_at_cap", _share(int((cash >= float(rule.std_cap) - 0.5).sum()), len(cash)),
                 len(cash)),
            _row(S, "all", "cap", float(rule.std_cap), 0, note="xfa_std_cap")]


def signal_supply(supply: Mapping[str, Any], n_paths: int, horizon: int) -> list[dict[str, Any]]:
    """D-363's signal supply -- trades per live account-day by account kind -- with the campaign's own router counts
    beside (every trade the day's draw offered: routed to an account, refused because an account held a position under
    the strict rule, refused for an opposite position, or left with no flat account), the trades the sizing declined,
    and the funded sessions that were Payout request days."""
    S = "signal_supply"
    out = []
    for kind in ("combine", "funded"):
        live, tr = int(supply["account_days"].get(kind, 0)), int(supply["trades"].get(kind, 0))
        out += [_row(S, kind, "account_days", live, n_paths), _row(S, kind, "trades", tr, n_paths),
                _row(S, kind, "trades_per_account_day", _share(tr, live), live)]
    live_f = int(supply["account_days"].get("funded", 0))
    out.append(_row(S, "funded", "share_payout_request_days", _share(int(supply.get("request_days", 0)), live_f),
                    live_f,
                    note="sessions after a payout request, left out of the new cycle (8284233)"))
    r = supply.get("router") or {}
    if r.get("paths", 0):
        offered = int(r["routed"]) + int(r["skipped"]) + int(r["skipped_opposite"]) + int(r["skipped_busy"])
        days = int(r["paths"]) * int(horizon)
        out += [_row(S, "router", "offered_per_path_day", _share(offered, days), days),
                _row(S, "router", "share_routed", _share(r["routed"], offered), offered),
                _row(S, "router", "share_refused_account_in_position", _share(r["skipped_busy"], offered), offered),
                _row(S, "router", "share_refused_opposite_position", _share(r["skipped_opposite"], offered), offered),
                _row(S, "router", "share_no_flat_account", _share(r["skipped"], offered), offered),
                _row(S, "router", "passed_over_per_routed", _share(r["passed_over"], r["routed"]), int(r["routed"]))]
    s = supply.get("sizing") or {}
    for k in ("trades_sized", "trades_unsized", "trades_stood_aside"):
        if k in s:
            out.append(_row(S, "sizing", f"{k}_per_path", _share(s[k], n_paths), n_paths))
    return out


def table_leaves(supply: Mapping[str, Any]) -> list[dict[str, Any]]:
    """D-363's leaves: each leaf of the table by its share of funded account-days (every leaf, most days first)."""
    leaves = dict(supply.get("leaves") or {})
    tot = int(sum(leaves.values()))
    out = []
    for name, n in sorted(leaves.items(), key=lambda kv: (-int(kv[1]), str(kv[0]))):
        out += [_row("table_leaves", name, "days", n, tot), _row("table_leaves", name, "share_of_funded_days",
                                                                  _share(n, tot), tot)]
    return out


def opening_trade(acc: pd.DataFrame, rule: Rule) -> list[dict[str, Any]]:
    """The opening funded trade (D-649 (3)): of the accounts that took one, the share lost on it (the account reached
    its loss limit on that trade), the share that won it, and the share that did not win it and lived -- with, for
    those, the room the trade left above the floor, whether they ever traded again and whether they were ever paid;
    the sessions an account waited for its opening trade; its size and R as the ledger records them; and, for the
    accounts paid, the opening day's share of the profit at the first payout request."""
    S, nx = "opening_trade", len(acc)
    op = acc[_flag(acc["opened"])]
    no = len(op)
    lost, won = _flag(op["lost_on_open"]), _flag(op["open_won"])
    lived = op[~won & ~lost]
    out = [_row(S, "all", "accounts", nx, nx), _row(S, "all", "share_never_traded", _share(nx - no, nx), nx),
           _row(S, "opened", "count", no, nx),
           _row(S, "opened", "share_lost_on_it", _share(int(lost.sum()), no), no,
                note="the account reached its loss limit on its first trade"),
           _row(S, "opened", "share_won_it", _share(int((won & ~lost).sum()), no), no),
           _row(S, "opened", "share_lost_it_and_lived", _share(len(lived), no), no,
                note="the first trade did not win and the account stayed above its floor"),
           *_dist(S, "opened", "sessions_before_it", op["open_session"].to_numpy(float) - 1.0 if no else [],
                  stats=("p50", "p90", "mean")),
           *_dist(S, "opened", "policy_risk", op["open_policy_risk"], stats=("p10", "p50", "p90")),
           *_dist(S, "opened", "policy_rr", op["open_policy_rr"], stats=("p10", "p50", "p90")),
           *_dist(S, "opened", "realised_risk", op["open_realised_risk"], stats=("p10", "p50", "p90")),
           *_dist(S, "opened", "contracts", op["open_contracts"], stats=("p10", "p50", "p90")),
           *_dist(S, "lost_opening_and_lived", "room_left_above_floor", lived["open_room_after"],
                  stats=("p10", "p50", "p90")),
           _row(S, "lost_opening_and_lived", "share_traded_again",
                _share(int((lived["trading_days"] > 1).sum()), len(lived)), len(lived)),
           _row(S, "lost_opening_and_lived", "share_ever_paid",
                _share(int((lived["n_payouts"] > 0).sum()), len(lived)), len(lived)),
           *_dist(S, "lost_opening_and_lived", "sessions_lived_after_it",
                  lived["life_days"].to_numpy(float) - lived["open_session"].to_numpy(float) if len(lived) else [],
                  stats=("p10", "p50", "p90"))]
    paid = acc[acc["open_day_share"].notna()]
    out += [_row(S, "paid", "opening_day_share_of_profit_at_first_request_pooled",
                 _share(float(paid["open_day_pnl"].sum()), float(paid["profit_at_req1"].sum())) if len(paid) else NAN,
                 len(paid), note="the opening days' P&L over the profit at the first request, summed over accounts"),
            *_dist(S, "paid", "opening_day_share_of_profit_at_first_request", paid["open_day_share"],
                   stats=("p10", "p50", "p90", "mean")),
            _row(S, "paid", "share_opening_day_above_largest_day_share",
                 _share(int((paid["open_day_share"] > float(rule.cons_max_day_frac) + rule.eps).sum()), len(paid)),
                 len(paid), note="the opening day alone is more than xfa_cons_max_day_frac of the profit")]
    return out


def after_opening(acc: pd.DataFrame) -> list[dict[str, Any]]:
    """After the opening trade (D-649 (3)): for the accounts in profit after it -- and, beside, those that lost it and
    lived, and every account that took one -- the share that reached the fifth winning day and a first payout request,
    and the sessions (from activation, and after the opening) and trading days each took."""
    S = "after_opening"
    op = acc[_flag(acc["opened"])]
    won, lost = _flag(op["open_won"]), _flag(op["lost_on_open"])
    out = []
    for name, mask in (("in_profit_after_opening", won), ("lost_opening_and_lived", ~won & ~lost),
                       ("all_opened", np.ones(len(op), bool))):
        k = op[mask]
        n = len(k)
        out += [_row(S, name, "accounts", n, len(op)),
                _row(S, name, "share_reached_fifth_winning_day", _share(int(k["win5_session"].notna().sum()), n), n),
                _row(S, name, "share_requested_first_payout", _share(int(k["req1_session"].notna().sum()), n), n)]
        for col, label in (("win5", "fifth_winning_day"), ("req1", "first_request")):
            out += _dist(S, name, f"sessions_to_{label}", k[f"{col}_session"])
            out += _dist(S, name, f"sessions_after_opening_to_{label}",
                         k[f"{col}_session"].to_numpy(float) - k["open_session"].to_numpy(float) if n else [])
            out += _dist(S, name, f"trading_days_to_{label}", k[f"{col}_trading_days"])
    return out


def winning_days_per_week(acc: pd.DataFrame) -> list[dict[str, Any]]:
    """Qualifying winning days per account-week (five sessions) while alive (D-649 (3)): pooled over the accounts'
    sessions, per account, and pooled over the sessions before a first payout."""
    S, nx = "winning_days_per_week", len(acc)
    paid = (acc["n_payouts"] > 0).to_numpy() if nx else np.zeros(0, bool)
    won = (_flag(acc["opened"]) & _flag(acc["open_won"])) if nx else np.zeros(0, bool)
    out = []
    for name, mask in (("all", np.ones(nx, bool)), ("paid", paid), ("never_paid", ~paid),
                       ("in_profit_after_opening", won)):
        k = acc[mask]
        days = float(k["life_days"].sum()) if len(k) else 0.0
        pre = float(k["pre_sessions"].sum()) if len(k) else 0.0
        live = k[k["life_days"] > 0]
        out += [_row(S, name, "pooled", WEEK * _share(float(k["winning_days"].sum()) if len(k) else 0.0, days), days),
                _row(S, name, "pooled_before_first_payout",
                     WEEK * _share(float(k["pre_qualifying_win"].sum()) if len(k) else 0.0, pre), pre),
                *_dist(S, name, "per_account", (WEEK * live["winning_days"].to_numpy(float)
                                                / live["life_days"].to_numpy(float)) if len(live) else [],
                       stats=("p10", "p50", "p90"))]
    return out


def consistency_description(acc: pd.DataFrame, rule: Rule) -> list[dict[str, Any]]:
    """Beside (D-649 (3)): what the Consistency test would have read day by day on these Standard-path accounts --
    for the accounts paid, the share it would have read eligible on a session before (and by) their actual first
    request and how many sessions earlier; for those never paid, the share it would have read eligible on some session;
    with the smallest payout also required, the same; the account-days the test had its days and a profit, and the
    share of them the largest-day test held back; and how large the best day stood at the actual first request. A
    description from the records, not a run on that path."""
    S, B, nx = "consistency_description", DESCRIPTION, len(acc)
    out = [_row(S, "rule", "min_trading_days", rule.cons_min_days, 0, basis=B, note="xfa_cons_min_days"),
           _row(S, "rule", "largest_day_share", rule.cons_max_day_frac, 0, basis=B, note="xfa_cons_max_day_frac"),
           _row(S, "rule", "cap", rule.cons_cap, 0, basis=B, note="xfa_cons_cap"),
           _row(S, "rule", "payout_min", rule.payout_min, 0, basis=B, note="payout_min")]
    paid = acc[acc["req1_session"].notna()]
    never = acc[acc["req1_session"].isna()]
    r1 = paid["req1_session"].to_numpy(float)
    for col, tag in (("cons_session", ""), ("cons_min_session", "_and_smallest_payout")):
        c = paid[col].to_numpy(float)
        before, by = c < r1, c <= r1                    # a blank (never met) compares False
        out += [_row(S, "paid", f"share_test{tag}_met_before_first_request", _share(int(before.sum()), len(paid)),
                     len(paid), basis=B),
                _row(S, "paid", f"share_test{tag}_met_by_first_request", _share(int(by.sum()), len(paid)), len(paid),
                     basis=B),
                *_dist(S, "paid", f"sessions_earlier{tag}", (r1 - c)[before], basis=B,
                       note="among the accounts it would have read eligible before their first request"),
                _row(S, "never_paid", f"share_test{tag}_met_on_some_session",
                     _share(int(never[col].notna().sum()), len(never)), len(never), basis=B),
                *_dist(S, "never_paid", f"first_session_test{tag}_met", never[col], stats=("p10", "p50", "p90"),
                       basis=B),
                _row(S, "all", f"share_test{tag}_met_before_any_request",
                     _share(int(before.sum()) + int(never[col].notna().sum()), nx), nx, basis=B)]
    read = float(acc["cons_days_read"].sum()) if nx else 0.0
    pre = float(acc["pre_sessions"].sum()) if nx else 0.0
    out += [_row(S, "all", "share_account_days_test_read", _share(read, pre), pre, basis=B,
                 note="sessions before a first payout on which the window had its trading days and a profit"),
            _row(S, "all", "share_read_days_held_back_by_largest_day",
                 _share(float(acc["cons_days_blocked"].sum()) if nx else 0.0, read), read, basis=B),
            *_dist(S, "paid", "best_day_share_of_profit_at_first_request", paid["best_day_share_at_req1"], basis=B),
            _row(S, "paid", "share_best_day_within_limit_at_first_request",
                 _share(int((paid["best_day_share_at_req1"] <= float(rule.cons_max_day_frac) + rule.eps).sum()),
                        int(paid["best_day_share_at_req1"].notna().sum())),
                 int(paid["best_day_share_at_req1"].notna().sum()), basis=B)]
    return out


#: the budget's groups: every funded account is in exactly one
BUDGET_GROUPS = ("lost_on_opening_trade", "never_traded", "lost_opening_and_lived", "won_opening")


def budget_before_first_payout(acc: pd.DataFrame) -> list[dict[str, Any]]:
    """The funded account-days before a first payout (every session of an account up to and including its first
    request's, or to its end), arranged as D-649 (4) asks the question. Every account is in one group -- lost on the
    opening trade (it reached its loss limit on its first trade), never traded, did not win the opening and lived, won
    the opening -- and each group's days are split by class; `not_qualifying` is the losing, idle and under-minimum
    days together. Then, beside and overlapping those days, the sessions between the Consistency test first reading
    eligible (with the smallest payout) and the actual first request. It arranges the readings; it selects nothing."""
    S, nx = "budget_before_first_payout", len(acc)
    tot = float(acc["pre_sessions"].sum()) if nx else 0.0
    opened, lost, won = _flag(acc["opened"]), _flag(acc["lost_on_open"]), _flag(acc["open_won"])
    masks = {"lost_on_opening_trade": opened & lost, "never_traded": ~opened,
             "lost_opening_and_lived": opened & ~lost & ~won, "won_opening": opened & ~lost & won}
    out = [_row(S, "all", "accounts", nx, nx), _row(S, "all", "account_days", tot, nx)]
    for name in BUDGET_GROUPS:
        k = acc[masks[name]]
        d = float(k["pre_sessions"].sum()) if len(k) else 0.0
        out += [_row(S, name, "accounts", len(k), nx), _row(S, name, "account_days", d, len(k)),
                _row(S, name, "share_of_account_days", _share(d, tot), tot)]
        idle = 0.0
        for c in DAY_CLASSES:
            dc = float(k[f"pre_{c}"].sum()) if len(k) else 0.0
            idle += 0.0 if c == "qualifying_win" else dc
            out += [_row(S, name, f"account_days_{CLASS_LABEL[c]}", dc, len(k)),
                    _row(S, name, f"share_of_account_days_{CLASS_LABEL[c]}", _share(dc, tot), tot)]
        out += [_row(S, name, "account_days_not_qualifying", idle, len(k),
                     note="losing, idle and under-minimum days together"),
                _row(S, name, "share_of_account_days_not_qualifying", _share(idle, tot), tot)]
    paid = acc[acc["req1_session"].notna()]
    gap = paid["req1_session"].to_numpy(float) - paid["cons_min_session"].to_numpy(float)
    gap = gap[np.isfinite(gap) & (gap > 0)]
    out += [_row(S, "the_rule", "account_days", float(gap.sum()), len(gap), basis=DESCRIPTION,
                 note="sessions from the Consistency test (with the smallest payout) first reading eligible to the "
                      "actual first request; they overlap the groups' days"),
            _row(S, "the_rule", "share_of_account_days", _share(float(gap.sum()), tot), tot, basis=DESCRIPTION)]
    return out


def table_problems(rows: Sequence[Mapping[str, Any]], tol: float = 1e-9) -> list[str]:
    """Every way one design and arm's rows fail to add up (empty when they do): each share of a count between 0 and 1;
    the evaluation endings, the funded endings, each group's day classes, the opening trade's three outcomes, the
    table's leaves and the router's four outcomes each summing to one; the paid and never-paid accounts and days to
    all; the budget's groups' accounts and days to the totals and each group's class days to its days; no more days
    before a first payout than funded days. A problem names the section and group, never a value."""
    by = {(str(r["section"]), str(r["group"]), str(r["measure"])): float(r["value"]) for r in rows}
    out: list[str] = []

    def get(section: str, group: str, measure: str) -> float:
        return by.get((section, group, measure), NAN)

    def total(section: str, parts: Sequence[tuple[str, str]], want: float, what: str) -> None:
        v = [get(section, g, m) for g, m in parts]
        if math.isnan(want) or any(math.isnan(x) for x in v):
            return                                # a blank: no unit in a group, nothing to add
        if abs(sum(v) - want) > tol * max(1.0, abs(want)):
            out.append(f"{section}: {what} do not add up")

    for (section, group, measure), v in by.items():
        ratio = measure.startswith("share_opening_day") or measure.startswith("share_best_day")
        if measure.startswith("share") and not ratio and not math.isnan(v) and not (-tol <= v <= 1.0 + tol):
            out.append(f"{section} {group} {measure}: a share outside 0 to 1")
    total("evaluation_funnel", [(e, "share") for e in COMBINE_ENDS], 1.0, "the endings' shares")
    total("evaluation_funnel", [(e, "count") for e in COMBINE_ENDS], get("evaluation_funnel", "all", "attempts"),
          "the endings' counts")
    total("funded_end", [(e, "share") for e in FUNDED_ENDS], 1.0, "the endings' shares")
    total("funded_end", [(e, "count") for e in FUNDED_ENDS], get("funded_funnel", "activated", "count"),
          "the endings' counts")
    for g in ("all", "paid", "never_paid"):
        total("funded_days", [(g, f"share_{CLASS_LABEL[c]}") for c in DAY_CLASSES], 1.0, f"{g}'s day classes")
    total("funded_days", [("paid", "accounts"), ("never_paid", "accounts")], get("funded_days", "all", "accounts"),
          "the paid and never-paid accounts")
    total("funded_days", [("paid", "days"), ("never_paid", "days")], get("funded_days", "all", "days"),
          "the paid and never-paid accounts' days")
    total("opening_trade", [("opened", m) for m in ("share_lost_on_it", "share_won_it", "share_lost_it_and_lived")],
          1.0, "the opening trade's outcomes")
    leaves = [v for (s_, _, m), v in by.items() if s_ == "table_leaves" and m == "share_of_funded_days"]
    if leaves and abs(sum(leaves) - 1.0) > 1e-9:
        out.append("table_leaves: the leaves' shares do not add up")
    total("signal_supply", [("router", m) for m in ("share_routed", "share_refused_account_in_position",
                                                    "share_refused_opposite_position", "share_no_flat_account")],
          1.0, "the router's outcomes")
    B = "budget_before_first_payout"
    total(B, [(g, "accounts") for g in BUDGET_GROUPS], get(B, "all", "accounts"), "the groups' accounts")
    total(B, [(g, "account_days") for g in BUDGET_GROUPS], get(B, "all", "account_days"), "the groups' days")
    for g in BUDGET_GROUPS:
        total(B, [(g, f"account_days_{CLASS_LABEL[c]}") for c in DAY_CLASSES], get(B, g, "account_days"),
              f"{g}'s class days")
    days, pre = get("funded_days", "all", "days"), get(B, "all", "account_days")
    if not math.isnan(days) and not math.isnan(pre) and pre > days + tol:
        out.append(f"{B}: more days before a first payout than funded days")
    return out


#: what the existing records cannot give (D-649 (1): reported as missing, never built into the engine)
MISSING_ROWS = (
    ("no_trade_day_reason_per_account_day",
     "why a live account took no trade on a session the table allowed one: the router counts, per campaign path, the "
     "trades it routed, refused under the strict rule, refused for an opposite position and left with no flat account "
     "(section signal_supply, group router), and a trade the sizing declined leaves no ledger row; none of these is "
     "recorded per account and day, so a 'no trade routed' day cannot be split into no trade offered that session, a "
     "trade offered while another account was in a position, and a trade offered and not sized"),
    ("consistency_test_withheld_per_account",
     "the engine's daily flag for the largest-day test (account_days' consistency_binding) is set only for an account "
     "on the Consistency path; on these Standard-path accounts it is always off, so the test is recomputed here from "
     "each day's recorded P&L by the engine's arithmetic (section consistency_description) and is not the engine's own "
     "reading"),
)


def missing_rows() -> list[dict[str, Any]]:
    return [_row("missing", "", name, NAN, 0, basis=MISSING, note=why) for name, why in MISSING_ROWS]


def summarise(acc: pd.DataFrame, cmb: pd.DataFrame, supply: Mapping[str, Any], rule: Rule, n_paths: int,
              horizon: int) -> list[dict[str, Any]]:
    """Every reading of one design and arm in long format, from its funded accounts' rows (`ACC_COLS`), its Combine
    attempts' rows (D-363's `combine_rows`) and its supply counts."""
    acc = acc if len(acc) else pd.DataFrame(columns=list(ACC_COLS))
    cmb = cmb if len(cmb) else pd.DataFrame(columns=["path", "index", "days", "trades", "end"])
    lack = [c for c in ACC_COLS if c not in acc.columns]
    if lack:
        raise ValueError(f"the accounts' rows lack {lack}")
    multi = int(supply.get("multi_breach_days", 0))
    return (evaluation_funnel(cmb, n_paths) + funded_funnel(acc, n_paths) + funded_days(acc) + funded_timing(acc)
            + survival_accrual(acc) + payouts(acc, rule) + signal_supply(supply, n_paths, horizon)
            + table_leaves(supply)
            + [_row("clusters", "all", "days_with_2plus_loss_limits_per_path", _share(multi, n_paths), n_paths)]
            + opening_trade(acc, rule) + after_opening(acc) + winning_days_per_week(acc)
            + consistency_description(acc, rule) + budget_before_first_payout(acc) + missing_rows())


def frame(rows: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """The result's frame: `COLUMNS` in order, every row labelled."""
    df = pd.DataFrame(list(rows))
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = "" if c in ("design", "prereg", "arm", "group", "basis", "note") else NAN
    if len(df) and not set(df["section"]) <= set(SECTIONS):
        raise ValueError(f"unknown sections {sorted(set(df['section']) - set(SECTIONS))}")
    return df[list(COLUMNS)]


__all__ = ["DECISION", "STUDY", "RESULT", "SCRIPT", "READING", "RECORDS", "DESCRIPTION", "IDENTITY", "MISSING", "NOTE",
           "DESIGNS", "ARMS", "SHIFT_OF", "PATHS", "HORIZON", "WEEK", "DAY_CLASSES", "CLASS_LABEL", "SINCE",
           "COMBINE_ENDS", "FUNDED_ENDS", "SECTIONS", "COLUMNS", "D363_COLS", "MEASURE_COLS", "ACC_COLS",
           "DECLARATION_SHA256", "D649_WORDS", "declaration", "declaration_problems", "Rule", "consistency_read",
           "account_measures", "evaluation_funnel", "funded_funnel", "funded_days", "funded_timing",
           "survival_accrual", "payouts", "signal_supply", "table_leaves", "opening_trade", "after_opening",
           "winning_days_per_week", "consistency_description", "BUDGET_GROUPS", "budget_before_first_payout",
           "table_problems", "MISSING_ROWS", "missing_rows", "summarise", "frame"]
