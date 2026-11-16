"""RD-01's account adapters A-2 to A-7 (`prereg/RD-01_firm_contracts.md` 4.3-4.6, 4.9, 5): DayTraders' evaluation and
Pro account, TradeDay's evaluation, Fast Pass's and Quick Pay's funded accounts -- subclasses of the vendored
`CombineAccount` and `FundedAccount`, through the engine's own seams (`combine_account_cls`, `funded_account_cls`), the
vendored tree never edited. Values come from `extended.firm_terms` (the verified records; section 5's table); no rule
value is typed here (14.2).

**Each class is the vendored behaviour plus its plan's declared rules, each behind a switch** (a class attribute).
With every switch at its Topstep setting (`TWINS`) a class is the vendored one bit for bit (T-1, 9.1 item 2):

* `DayTradersCombine` (A-2): `DLL` the soft daily loss limit (the account's `dll`: the engine's own day-loss mechanics);
  `QUALIFYING` a pass needs two Qualifying Days (a day of at least the minimum whose close has the best day at most the
  share of total profit) -- at or above target with days owed the account trades on at the table's lookup as it stands;
  `INACTIVITY` the closure (below); `SELLS_RESET` (DayTraders sells none: a reset is refused).
* `DayTradersFunded` (A-3): `QUALIFYING` eligibility by Qualifying Days since the last payout or activation (the request
  day excluded; the cycle's best day within its share of the cycle's profit, both read as the engine reads the
  Consistency path's cycle, `w_best` and `w_profit`, the request day out) with the request gate; `REQUEST_RULE` the
  balance left after a request and the rounding down to the increment; `DLL`; `INACTIVITY`; `TABLE_INPUTS` 4.9's row.
* `TradeDayCombine` (A-4): `MIN_DAYS` sessions with an executed trade before a pass (0: none); at or above target with
  days owed, at most one trade a session at one micro and the table's R -- the session's decision read where the
  engine sets it (`acct.decision`), its `max_trades` 1 (the router's cap, Stage 2 D-162), and the draw's rule sized at
  one micro for that session; `SELLS_RESET`.
* `FastPassFunded` (A-5): `SHARE_RULE` the 45 % rule on gross profit; `PASS_OVER` the session after a request forced
  untraded wherever its cell would trade (its decision's `max_trades` 0: the router passes over it, D-162) -- counted,
  never asserted; `FIFTH` the fifth request at its two ends (`"unpaid"`: the account ends at it, unpaid; `"paid"`: paid,
  then ends); `TABLE_INPUTS` 4.9's row.
* `QuickPayFunded` (A-7): `INTRADAY` the wrapper on the draw (5.4's bracketed peak inside each trade, `PEAK` "pess" or
  "opt"); `FLOOR_GROSS` the floor trailing the gross profit's peak, frozen at start, a payout lowering the balance and
  not the floor; `SPLIT_TIERED`; `CEILING` (None, "strict", "lenient"); `REQUEST` ("engine", "every", "cadence", 5.6);
  `TABLE_INPUTS`.

**DayTraders' inactivity** (A-2, A-3): the account ends, not breached, once a window of the record's calendar days holds
no day of at least the minimum. The windows run from the purchase (an evaluation) or the activation (a Pro account):
the first is [that date, that date + 29 days], then each window after the last such day. Exact on the session dates of
a replay (`with_calendar`): the account ends at the first close at which a window has ended (or will end before the
next session) without such a day. In the gate, whose days carry no date, Stage 2's session translation (21 sessions). A
purchase on the replay's day 0 is dated the day before its first session.

**Counts** (9.3): each account keeps its counters (`counters()`); every adapter account built in a process is registered
in `TALLY` until `collect()` reads and clears it, so a runner reads them after each replay.

**Calendars and arms.** `with_calendar` makes a subclass holding one start's session dates; `with_point` a Quick Pay
class holding the run's point outcomes (M3), so the peak bracket reads each trade's point outcomes on every arm. Both are made in the process that replays (they are not module attributes and do not pickle); the module's
own classes (`CLASSES`, `TWINS`) pickle by name.
"""
from __future__ import annotations

import math
from dataclasses import replace
from datetime import date, timedelta
from typing import Any, ClassVar, Sequence

import numpy as np

from extended import use_vendored_stage2

use_vendored_stage2()

from propedge.campaign.lockstep import EPS, CombineAccount, FundedAccount  # noqa: E402

from extended import firm_terms as T  # noqa: E402
from extended import walker as W  # noqa: E402

STRICT, LENIENT = T.STRICT, T.LENIENT

#: every adapter account built in this process since the last `collect()` (9.3's counts)
TALLY: list[Any] = []
#: the names of the module's own run classes (`CLASSES`): a per-start subclass's family is the first of them in its MRO
NAMED: set[str] = set()


def collect() -> list[dict[str, Any]]:
    """Each registered account's counters (`counters()`), in the order built; the register cleared."""
    out = [a.counters() for a in TALLY]
    TALLY.clear()
    return out


class _Counted:
    """The counters an adapter account keeps (9.3), registered in `TALLY`."""

    COUNTERS: ClassVar[tuple[str, ...]] = ()

    def _register(self) -> None:
        for k in self.COUNTERS:
            setattr(self, k, 0)
        TALLY.append(self)

    def counters(self) -> dict[str, Any]:
        kind = "funded" if isinstance(self, FundedAccount) else "combine"
        day = self.activation_day if kind == "funded" else self.purchase_day
        family = next((c.__name__ for c in type(self).__mro__ if c.__name__ in NAMED and c.__module__ == __name__),
                      type(self).__name__)
        return {"class": type(self).__name__, "family": family, "kind": kind, "index": int(self.index),
                "day": int(day), **{k: getattr(self, k) for k in self.COUNTERS}}


# ------------------------------------------------------------------------------------------------ inactivity (A-2, A-3)


def gate_window_sessions() -> int:
    """The gate's translation of DayTraders' rolling window into sessions: Stage 2's `billing_days` for its
    `billing_period_calendar_days`, which must be the window's length."""
    if int(T.stage2_value("billing_period_calendar_days")) != int(T.plan_terms("DT").inactivity_window_days):
        raise T.TermParseError("Stage 2's 30-day translation no longer matches DayTraders' window")
    return int(T.stage2_value("billing_days"))


class _Inactivity:
    """A-2 / A-3: the inactivity closure (the module docstring)."""

    CALENDAR: ClassVar[tuple[date, ...] | None] = None
    INACTIVITY: ClassVar[bool] = False

    def _date_of(self, calendar_day: int) -> date | None:
        cal = self.CALENDAR
        k = int(calendar_day)
        if cal is None or k > len(cal):
            return None
        return cal[k - 1] if k >= 1 else cal[0] - timedelta(days=1)

    def _inactive(self, calendar_day: int, day_pnl: float, anchor_day: int) -> bool:
        """At this close (the day counted): whether the account ends for inactivity."""
        if not self.INACTIVITY:
            return False
        t = T.plan_terms("DT")
        if int(t.inactivity_days) != 1:
            raise T.TermParseError("DayTraders' inactivity rule asks for one day a window; the closure reads one")
        c = int(calendar_day)
        if day_pnl >= float(t.qualifying_day_min) - EPS:
            self._last_profit = c
        if self.CALENDAR is None:                                       # the gate: Stage 2's 21 sessions
            last = self._last_profit if self._last_profit is not None else int(anchor_day)
            return c - last >= gate_window_sessions()
        window = int(t.inactivity_window_days)
        d = self._date_of(c)
        if d is None:
            return False
        last_d = (self._date_of(self._last_profit) if self._last_profit is not None
                  else self._date_of(int(anchor_day)) - timedelta(days=1))
        nxt = self._date_of(c + 1)
        return (d - last_d).days >= window or (nxt is not None and (nxt - last_d).days > window)


def with_calendar(cls: type, session_dates: Any) -> type:
    """A subclass of `cls` holding one start's session dates (`session_dates[k - 1]` the date of the replay's calendar
    day k): A-2's and A-3's windows are then exact in calendar days. Made per start, in the replaying process."""
    if not issubclass(cls, _Inactivity):
        raise TypeError("only DayTraders' classes read a calendar")
    dates = tuple(d if isinstance(d, date) else date.fromisoformat(str(d)[:10]) for d in session_dates)
    if any(b <= a for a, b in zip(dates, dates[1:])):
        raise ValueError("the session dates must ascend")
    return type(f"{cls.__name__}AtCalendar", (cls,), {"CALENDAR": dates, "__module__": cls.__module__})


# ------------------------------------------------------------------------------------------------ A-2


class DayTradersCombine(_Counted, _Inactivity, CombineAccount):
    """A-2: DayTraders' EOD 50K evaluation."""

    DLL: ClassVar[bool] = True
    QUALIFYING: ClassVar[bool] = True
    SELLS_RESET: ClassVar[bool] = False
    COUNTERS = ("qualifying_days", "sessions_held", "inactive_closed", "dll_days")

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.DLL:
            self.dll = float(T.plan_terms("DT").eval_dll)
        self._last_profit: int | None = None
        self._register()

    def reset(self, calendar_day: int, *, rtp_dll: float | None = None) -> None:
        if not self.SELLS_RESET:
            raise RuntimeError("DayTraders sells no reset (daytraders.eod50k.eval_reset_fee); none is bought")
        super().reset(calendar_day, rtp_dll=rtp_dll)

    def trade_day(self, rules: Any, policy: Any, rel_day: int, calendar_day: int, ledger: Any = None,
                  need_aware: bool = False, consistency_cap: bool = False) -> None:
        super().trade_day(rules, policy, rel_day, calendar_day, ledger=ledger, need_aware=need_aware,
                          consistency_cap=consistency_cap)
        if self.failed:
            return
        t = T.plan_terms("DT")
        day = float(self.last_day_pnl)
        if self.DLL and self.dll is not None and day <= -float(self.dll) + EPS:
            self.dll_days += 1
        if self.QUALIFYING:
            if day >= float(t.qualifying_day_min) - EPS and self.B > EPS \
                    and self.best_day <= float(t.eval_consistency) * self.B + EPS:
                self.qualifying_days += 1
            if self.passed and self.qualifying_days < int(t.eval_qualifying_days):
                self.passed, self.pass_day, self.resolved_on = False, -1, None     # at target, days owed: trades on
                self.sessions_held += 1
        if not self.passed and self._inactive(calendar_day, day, self.purchase_day):
            self.inactive_closed = 1
            self.abandoned = True                                          # ends, not breached, not passed
            self.resolved_on = int(calendar_day)


# ------------------------------------------------------------------------------------------------ A-3


class DayTradersFunded(_Counted, _Inactivity, FundedAccount):
    """A-3: DayTraders' EOD Pro account."""

    DLL: ClassVar[bool] = True
    QUALIFYING: ClassVar[bool] = True
    REQUEST_RULE: ClassVar[bool] = True
    TABLE_INPUTS: ClassVar[bool] = True
    COUNTERS = ("q", "sessions_held", "share_blocked", "gate_blocked", "requests_rounded", "requests_cut_by_left",
                "inactive_closed", "dll_days")

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.DLL:
            self.dll = float(T.plan_terms("DT").funded_dll)
        self._last_profit: int | None = None
        self._held = False
        self._register()

    def _standard_eligible(self, rules: Any) -> bool:
        if not self.QUALIFYING:
            return FundedAccount._standard_eligible(self, rules)
        t = T.plan_terms("DT")
        day = float(self.last_day_pnl)
        share_ok = self.w_profit > EPS and self.w_best <= float(t.funded_consistency) * self.w_profit + EPS
        if not self.last_request_day and day >= float(t.winning_day_min) - EPS and share_ok:
            self.q += 1
        done = self.q >= int(t.winning_days)
        gate_ok = self.B >= float(t.request_gate) - EPS
        self._held = bool(done and not (gate_ok and share_ok))
        self.share_blocked += int(done and not share_ok)
        self.gate_blocked += int(done and not gate_ok)
        return bool(done and gate_ok and share_ok)

    def trade_day(self, rules: Any, policy: Any, cap: float, rel_day: int, calendar_day: int, ledger: Any = None,
                  second_trade: bool = False, collect: bool = False) -> float | None:
        t = T.plan_terms("DT")
        pol = policy
        if self.REQUEST_RULE:                                           # at least the balance left after a request
            pol = replace(policy, keep_balance=max(float(policy.keep_balance), float(t.request_leave)))
        self._held = False
        net = super().trade_day(rules, pol, cap, rel_day, calendar_day, ledger=ledger, second_trade=second_trade,
                                collect=collect)
        if net is not None and self.REQUEST_RULE:
            r = float(self.last_request)
            at_close = float(self.B) + r
            plain = float(policy.payout_frac) * min(float(rules.payout_max_frac_of_balance) * at_close, float(cap))
            self.requests_cut_by_left += int(r < plain - EPS)
            inc = float(t.request_increment)
            r_inc = math.floor(r / inc + 1e-9) * inc
            if r_inc < r - EPS:                                         # rounded down to the increment
                delta = r - r_inc
                self.B += delta
                self.gross_paid -= delta
                new = float(rules.profit_split) * r_inc - float(rules.payout_fee)
                self.cash += new - float(net)
                self.payout_cash[-1] = new
                self.last_request = r_inc
                self.requests_rounded += 1
                net = new
        if net is not None and self.QUALIFYING:
            self.q = 0
        if not self.closed and self.ended_on is None and self._inactive(calendar_day, float(self.last_day_pnl),
                                                                          self.activation_day):
            self.inactive_closed = 1
            self.ended_on = int(calendar_day)                          # ends, not breached; its balance not credited
        if self.DLL and self.dll is not None and float(self.last_day_pnl) <= -float(self.dll) + EPS:
            self.dll_days += 1
        if self.TABLE_INPUTS and self.QUALIFYING:                       # 4.9: the plan's days still needed, held at 4
            self.sessions_held += int(self._held)
            owed = max(0, int(t.winning_days) - self.q)
            self.win_days = 4 if self._held else min(5, max(0, 5 - owed))
        return net


# ------------------------------------------------------------------------------------------------ the decision seam


class _DecisionSeam:
    """A-4 / A-5: the account's session decision, read where the engine sets it (`acct.decision = dec`, after the
    draw's `set_risk`), so the router's cap (Stage 2 D-162) and the draw's size follow the plan's rule that session."""

    def _adjust_decision(self, dec: Any) -> Any:
        return dec

    @property
    def decision(self) -> Any:
        return self.__dict__.get("_decision")

    @decision.setter
    def decision(self, dec: Any) -> None:
        self.__dict__["_decision"] = dec if dec is None else self._adjust_decision(dec)


# ------------------------------------------------------------------------------------------------ A-4


class TradeDayCombine(_Counted, _DecisionSeam, CombineAccount):
    """A-4: TradeDay's End of Day 50K evaluation (both plans)."""

    PLAN: ClassVar[str] = "FP"
    MIN_DAYS: ClassVar[int] = 0
    SELLS_RESET: ClassVar[bool] = False
    COUNTERS = ("trade_days", "sessions_held", "logging_sessions", "logging_trades", "logging_stood_aside")

    def __post_init__(self) -> None:
        super().__post_init__()
        self._sizing_rule = None
        self._logging_now = False
        self._table_risk = 0.0
        self._register()

    def reset(self, calendar_day: int, *, rtp_dll: float | None = None) -> None:
        if not self.SELLS_RESET:
            raise RuntimeError("TradeDay's reset fee is unsettled and no design buys one (U-7)")
        super().reset(calendar_day, rtp_dll=rtp_dll)

    def _at_target_days_owed(self) -> bool:
        if int(self.MIN_DAYS) <= 0 or not self.alive or self.trade_days >= int(self.MIN_DAYS):
            return False
        t = T.plan_terms(self.PLAN)
        return self.B >= max(float(t.eval_target), self.best_day / float(t.eval_consistency)) - EPS

    def _adjust_decision(self, dec: Any) -> Any:
        draw = self.draw
        rule = getattr(draw, "rule", None)
        if self._sizing_rule is None:
            self._sizing_rule = rule
        if rule is not None and rule is not self._sizing_rule:
            draw.rule = self._sizing_rule                               # the design's own sizing, restored
        self._logging_now = False
        if getattr(dec, "abandon", False) or not self._at_target_days_owed():
            return dec
        if dec.max_trades is not None and int(dec.max_trades) < 1:
            return dec                                                  # the cell sits the session out
        if rule is None or not hasattr(draw, "target_risk") or rule.cap_micros("combine", float(self.B)) is None:
            raise RuntimeError("A-4's day-logging micro needs the design's tier-sized draw")
        # one micro (m1): the design's own stand-aside kept; a headroom of 1 so a one-micro limit floors to one
        draw.rule = replace(self._sizing_rule, combine_limit_micros=1, headroom_frac=1.0)
        rpc = getattr(draw, "_rpc", None) or []
        top = max((float(np.max(r)) for r in rpc if len(r)), default=0.0)
        self._table_risk = float(draw.target_risk)
        draw.target_risk = max(float(draw.target_risk), top)            # one micro at every stop, at the table's R
        self._logging_now = True
        self.logging_sessions += 1
        return replace(dec, max_trades=1)

    def trade_day(self, rules: Any, policy: Any, rel_day: int, calendar_day: int, ledger: Any = None,
                  need_aware: bool = False, consistency_cap: bool = False) -> None:
        n0 = self.trades
        st0 = int(getattr(getattr(self.draw, "stats", None), "stood_aside", 0))
        super().trade_day(rules, policy, rel_day, calendar_day, ledger=ledger, need_aware=need_aware,
                          consistency_cap=consistency_cap)
        if self._logging_now:
            self.logging_trades += self.trades - n0
            self.logging_stood_aside += int(getattr(getattr(self.draw, "stats", None), "stood_aside", 0)) - st0
            if self.trades > n0:
                self._record_table_risk(ledger)
        if self.trades > n0:
            self.trade_days += 1
        if self.passed and self.trade_days < int(self.MIN_DAYS):
            self.passed, self.pass_day, self.resolved_on = False, -1, None
            self.sessions_held += 1

    def _record_table_risk(self, ledger: Any) -> None:
        """m1: a day-logging trade's intended risk recorded as the table's (the draw sized it at a raised target so
        that one micro buys at every stop) -- in the trade's record, the draw's stats and the ledger row."""
        lt = getattr(self.draw, "last_trade", None)
        if not lt or not lt.get("contracts"):
            return
        table = float(self._table_risk)
        capped = min(table, float(lt["risk_per_contract"]) * int(lt["cap_micros"] or 1))
        stats = self.draw.stats
        stats.intended_risk += table - float(lt["intended_risk"])
        stats.intended_capped_risk += capped - float(lt["intended_capped_risk"])
        lt["intended_risk"], lt["intended_capped_risk"] = table, capped
        if ledger and ledger[-1].get("kind") == "combine" and int(ledger[-1].get("index", -1)) == int(self.index):
            ledger[-1]["intended_risk"], ledger[-1]["intended_capped_risk"] = table, capped


# ------------------------------------------------------------------------------------------------ A-5


def _undo_request(a: FundedAccount, net: float) -> None:
    """A request made at this close taken back, its bookkeeping undone (the account ends at this close, unpaid)."""
    r = float(a.last_request)
    a.payout_cash.pop()
    a.payout_days.pop()
    a.cash -= float(net)
    a.B += r
    a.gross_paid -= r
    a.n_payouts -= 1
    if a.n_payouts == 0:
        a.first_payout_day = -1
        a.paid_once = False
        a.balance_at_first_payout = float("nan")
    a.last_request = 0.0
    a.request_day_next = False


class FastPassFunded(_Counted, _DecisionSeam, FundedAccount):
    """A-5: TradeDay Fast Pass's Funded Sim account."""

    SHARE_RULE: ClassVar[bool] = True
    PASS_OVER: ClassVar[bool] = True
    FIFTH: ClassVar[str | None] = "unpaid"
    TABLE_INPUTS: ClassVar[bool] = True
    COUNTERS = ("sessions_held", "share_blocked", "forced_untraded", "sat_out", "fifth_ended", "fifth_unpaid")

    def __post_init__(self) -> None:
        super().__post_init__()
        self._life_best = 0.0
        self._true_win_days = 0
        self._held = False
        self._register()

    def _adjust_decision(self, dec: Any) -> Any:
        if not self.PASS_OVER or not self.request_day_next or getattr(dec, "abandon", False):
            return dec
        if dec.max_trades is not None and int(dec.max_trades) <= 0:
            self.sat_out += 1                                           # the cell sits the session out already
            return dec
        self.forced_untraded += 1
        return replace(dec, max_trades=0)

    def _standard_eligible(self, rules: Any) -> bool:
        base = FundedAccount._standard_eligible(self, rules)
        if not self.SHARE_RULE:
            return base
        t = T.plan_terms("FP")
        self._life_best = max(self._life_best, float(self.last_day_pnl))
        share_ok = self._life_best <= float(t.funded_consistency) * (self.B + self.gross_paid) + EPS
        # 4.9's Fast Pass row (M2): held whenever the five days are counted and the 45 % rule blocks -- whatever the
        # profit since the request (the table's own line_gap) and the balance; eligibility needs all of them
        days_done = self.win_days >= int(rules.std_winning_days)
        self._held = bool(days_done and not share_ok)
        self.share_blocked += int(self._held)
        return bool(base and self.B > EPS and share_ok)

    def _after_payout(self, calendar_day: int) -> None:
        if self.FIFTH == "paid" and self.n_payouts >= int(T.plan_terms("FP").fifth_request):
            self.fifth_ended = 1
            self.ended_on = int(calendar_day)

    def trade_day(self, rules: Any, policy: Any, cap: float, rel_day: int, calendar_day: int, ledger: Any = None,
                  second_trade: bool = False, collect: bool = False) -> float | None:
        if self.PASS_OVER and self.request_day_next and self.decision is None:
            raise RuntimeError("A-5's untraded session needs the design's state table (a decision each session)")
        if self.TABLE_INPUTS:
            self.win_days = self._true_win_days
        self._held = False
        net = super().trade_day(rules, policy, cap, rel_day, calendar_day, ledger=ledger, second_trade=second_trade,
                                collect=collect)
        if net is not None and self.FIFTH == "unpaid" and self.n_payouts >= int(T.plan_terms("FP").fifth_request):
            _undo_request(self, float(net))                            # the fifth request moves it Live, unpaid
            self.fifth_ended = 1
            self.fifth_unpaid = 1
            self.ended_on = int(calendar_day)
            net = None
        if self.TABLE_INPUTS:
            self._true_win_days = self.win_days
            self.sessions_held += int(self._held)
            if self._held:
                self.win_days = 4
        return net


# ------------------------------------------------------------------------------------------------ A-7


class _PeakDraw:
    """A-7's wrapper on a Quick Pay account's draw: each trade's peak bracketed from its outcomes at the menu's R values
    (5.4), the floor raised inside the trade by it, and a trade whose path after its peak crosses that floor ended
    there. Every other read or write passes to the wrapped draw."""

    def __init__(self, inner: Any, account: "QuickPayFunded"):
        self.__dict__["_inner"] = inner
        self.__dict__["_acct"] = account

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__dict__["_inner"], name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self.__dict__["_inner"], name, value)

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray, **kw: Any) -> np.ndarray:
        inner, acct = self.__dict__["_inner"], self.__dict__["_acct"]
        res = inner(n, day, slot, cushion, **kw)
        pnl = float(np.asarray(res, float).ravel()[0])
        lt = getattr(inner, "last_trade", None)
        if not np.isfinite(pnl):
            return res
        if not lt or not lt.get("contracts"):
            raise RuntimeError("A-7 brackets a trade sized in contracts; this draw sizes none (n9: fixed risk refused)")
        return np.array([acct._through_trade(pnl, lt, inner)])


def ticks_of(risk_per_contract: float) -> int:
    """A trade's stop in ticks from its risk per micro (`DayBlock.risk_per_contract`, at MNQ's tick value)."""
    tv = float(W.Costs(fee_micro_eq=0.0).tick_value)
    s = int(round(float(risk_per_contract) / tv))
    if s < 1 or abs(s * tv - float(risk_per_contract)) > 1e-6:
        raise ValueError(f"a risk per micro of {risk_per_contract!r} is not a whole number of ticks")
    return s


def won_at(u_point: float, R: float, S: int, fee: float) -> bool:
    """Whether a trade's point outcome `u_point` at R (in R, net of its log's fee and entry) is a fill at its target.
    A target fill nets the target less the trade's own cost (its fee, and at most one entry tick); any other exit at R
    nets at least two ticks less (a flatten fills two ticks under a price that has not traded through the target), so
    the gap above the fee splits them at a tick and a half -- read on the walk's own booking (5.4). Refused: a gap
    below zero (an outcome above its own target net of its fee is not this walk's)."""
    if not np.isfinite(u_point):
        return False
    tv = float(W.Costs(fee_micro_eq=0.0).tick_value)
    gap = W.target_ticks(float(R), int(S)) / S - float(u_point) - float(fee) / (S * tv)
    if gap < -1e-6:
        raise ValueError(f"an outcome of {u_point!r} at R {R:g} lies above its target net of its fee: not this walk's")
    return gap <= 1.5 / S


def peak_bracket(by_rr: dict[float, float], R_x: float, S: int, fee: float) -> dict[str, Any]:
    """5.4 on one trade's point outcomes `by_rr` (R -> outcome): whether it won at its R_x; R_lo, the largest menu R
    below R_x at which it won (0 if none); R_hi, the smallest menu R above R_lo with an outcome it did not win (at most
    R_x)."""
    menu = sorted(float(k) for k in by_rr)
    won = {R: won_at(float(by_rr[R]), R, S, fee) for R in menu}
    lo = [R for R in menu if R < R_x - 1e-12 and won[R]]
    R_lo = max(lo) if lo else 0.0
    hi = [R for R in menu if R_lo + 1e-12 < R <= R_x + 1e-12 and np.isfinite(float(by_rr[R])) and not won[R]]
    return {"won": bool(won.get(float(R_x), False)), "R_lo": float(R_lo), "R_hi": float(min(hi)) if hi else float(R_x)}


class QuickPayFunded(_Counted, FundedAccount):
    """A-7: TradeDay Quick Pay's Funded Sim account."""

    INTRADAY: ClassVar[bool] = True
    PEAK: ClassVar[str] = "pess"
    FLOOR_GROSS: ClassVar[bool] = True
    SPLIT_TIERED: ClassVar[bool] = True
    CEILING: ClassVar[str | None] = STRICT
    REQUEST: ClassVar[str] = "every"
    TABLE_INPUTS: ClassVar[bool] = True
    #: M3: the run's point outcomes, one `r_by_rr` a historical day of the draw's own day list (`with_point`): the
    #: bracket reads them on every arm; a class without them refuses to bracket
    POINT: ClassVar[tuple | None] = None
    COUNTERS = ("floor_rises", "breaches_at_raised_floor", "split_low", "split_high", "split_crossing",
                "ceiling_ended", "ceiling_withdrawn", "mae_unknown")

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.PEAK not in ("pess", "opt") or self.REQUEST not in ("engine", "every", "cadence") \
                or self.CEILING not in (None, STRICT, LENIENT):
            raise ValueError("Quick Pay's switches: PEAK pess|opt, REQUEST engine|every|cadence, CEILING None|strict|"
                             "lenient")
        self.g_peak = 0.0
        self.ceiling_forfeit = 0.0
        self._true_win_days = 0
        if self.INTRADAY:
            self.draw = _PeakDraw(self.draw, self)
        self._register()

    # ---- the floor
    def _gross_floor(self) -> float:
        t = T.plan_terms("QP")
        return min(float(t.funded_lock), max(float(self.floor_start), self.g_peak - float(t.funded_mll)))

    def _through_trade(self, pnl: float, lt: dict[str, Any], inner: Any) -> float:
        """One trade's path as 5.4 brackets it: its peak raises the floor; a path after the peak crossing the raised
        floor ends there (the account then breaches at the engine's own check)."""
        if lt.get("stretch") or lt.get("at_need"):
            raise RuntimeError("A-7 brackets a trade at its own R; a stretch or need exit is not one (D-306, D-368)")
        h, j = int(lt["historical_day"]), int(lt["trade_index"])
        risk, n = float(lt["realised_risk"]), int(lt["contracts"])
        S = ticks_of(float(lt["risk_per_contract"]))
        tv = float(W.Costs(fee_micro_eq=0.0).tick_value)
        fees, by = inner._fee[h], inner._r_by_rr[h]
        if fees is None or by is None or lt.get("rr") is None:
            raise RuntimeError("A-7's bracket needs each trade's fee and its outcomes at the menu's R (4.8, 5.4)")
        if self.POINT is None or h >= len(self.POINT) or self.POINT[h] is None:
            raise RuntimeError("A-7 classifies on the run's point outcomes on every arm (M3): this class holds none "
                               "for this day (firm_accounts.with_point)")
        ref = self.POINT[h]
        if set(map(float, ref)) != set(map(float, by)) or any(len(ref[R]) != len(by[R]) for R in ref):
            raise RuntimeError("A-7's point reference is not this draw's day: the menu or the trades differ")
        R_x = float(lt["rr"])
        point = {float(R): float(v[j]) for R, v in ref.items()}
        br = peak_bracket(point, R_x, S, float(fees[j]))
        B0, G0 = float(self.B), float(self.B + self.gross_paid)
        if br["won"]:
            if self.PEAK == "pess":                                     # a tick short of its target, then its MAE
                peak = (W.target_ticks(R_x, S) - 1) * tv * n
                mae = float(lt.get("mae", float("nan")))
                if not np.isfinite(mae):
                    self.mae_unknown += 1
                    mae = risk
                low = B0 - abs(mae)
            else:                                                       # every adverse excursion first: peak at exit
                peak, low = pnl, B0 + pnl
        else:
            if self.PEAK == "pess":                                     # a tick short of R_hi's target, then its exit
                peak = (W.target_ticks(br["R_hi"], S) - 1) * tv * n
            else:                                                       # R_lo's target, or a profitable flatten's exit
                peak = W.target_ticks(br["R_lo"], S) * tv * n if br["R_lo"] > 0 else 0.0
                if pnl > 0:
                    peak = max(peak, pnl)
            low = B0 + pnl
        before = float(self.F)
        self.g_peak = max(self.g_peak, G0 + max(peak, 0.0))
        self.F = max(before, self._gross_floor())
        raised = self.F > before + EPS
        self.floor_rises += int(raised)
        if raised and low <= self.F + EPS:                              # crossed the floor its own peak raised
            self.breaches_at_raised_floor += 1
            return float(self.F) - B0
        self.g_peak = max(self.g_peak, G0 + pnl)
        self.F = max(self.F, self._gross_floor())
        return pnl

    # ---- eligibility and the request
    def _standard_eligible(self, rules: Any) -> bool:
        if self.REQUEST == "engine":
            return FundedAccount._standard_eligible(self, rules)
        if self.B <= EPS:
            return False
        if self.REQUEST == "every":
            return self.days >= 1
        return self.win_days >= int(rules.std_winning_days)            # the reference's cadence (5.6), none excluded

    def _tiered(self, r: float, c: float) -> float:
        """The tiered split of a request `r` taken from a balance `c` above start (`tradeday.quickpay_eod50k`)."""
        t = T.plan_terms("QP")
        above = min(r, max(0.0, c - float(t.split_line)))
        if above >= r - EPS:
            self.split_high += 1
        elif above > EPS:
            self.split_crossing += 1
        else:
            self.split_low += 1
        return float(t.split_high) * above + float(t.split_low) * (r - above) - float(t.payout_fee)

    def trade_day(self, rules: Any, policy: Any, cap: float, rel_day: int, calendar_day: int, ledger: Any = None,
                  second_trade: bool = False, collect: bool = False) -> float | None:
        t = T.plan_terms("QP")
        if self.TABLE_INPUTS and self.REQUEST == "every":
            self.win_days = self._true_win_days
        net = super().trade_day(rules, policy, cap, rel_day, calendar_day, ledger=ledger, second_trade=second_trade,
                                collect=collect)
        if self.closed:
            return net
        if self.FLOOR_GROSS:                                            # a payout lowers the balance, not the floor
            self.g_peak = max(self.g_peak, float(self.B + self.gross_paid))
            self.F = self._gross_floor()
        if self.CEILING is not None and self.B + self.gross_paid >= float(t.profit_ceiling) - EPS:
            excess = float(self.B + self.gross_paid) - float(t.profit_ceiling)
            if net is not None:
                _undo_request(self, float(net))                         # the close's request goes with the review
                net = None
            self.B -= excess
            self.ceiling_forfeit += excess
            self.ceiling_ended = 1
            if self.CEILING == LENIENT and self.B >= float(rules.payout_min) - EPS:
                net = self._withdraw_all(rel_day)
                self.ceiling_withdrawn = 1
            self.ended_on = int(calendar_day)
        elif net is not None and self.SPLIT_TIERED:                     # the tiered split, on the balance before it
            r = float(self.last_request)
            new = self._tiered(r, float(self.B) + r)
            self.cash += new - float(net)
            self.payout_cash[-1] = new
            net = new
        if self.TABLE_INPUTS and self.REQUEST == "every":
            self._true_win_days = self.win_days
            self.win_days = 5 if self.days >= 1 else 0
        return net

    def _withdraw_all(self, rel_day: int) -> float:
        """The ceiling's lenient end: the whole remaining balance above start requested at this close, at the tiered
        split (no cap stated, U-10)."""
        rest = float(self.B)
        new = self._tiered(rest, rest) if self.SPLIT_TIERED else rest
        if self.n_payouts == 0:
            self.balance_at_first_payout = float(self.B)
        self.last_request = rest
        self.B = 0.0
        self.gross_paid += rest
        self.cash += new
        self.n_payouts += 1
        self.since_pay = 0.0
        self.paid_once = True
        if self.first_payout_day < 0:
            self.first_payout_day = int(rel_day)
        self.payout_days.append(int(rel_day))
        self.payout_cash.append(new)
        return new


# ------------------------------------------------------------------------------------------------ the classes run


def _named(base: type, name: str, attrs: dict[str, Any]) -> type:
    cls = type(name, (base,), {**attrs, "__module__": __name__, "__qualname__": name})
    globals()[name] = cls
    NAMED.add(name)
    return cls


def _build() -> dict[tuple, type]:
    """Every class a run of 7.3 uses, made once at import under a stable name, so each pickles to a pool worker; and
    the Topstep twins (T-1, 9.1 item 2): every switch at the vendored behaviour."""
    out: dict[tuple, type] = {}
    for inact in (True, False):
        tag = "Inactive" if inact else "Active"
        out[("DT", "combine", inact)] = _named(DayTradersCombine, f"DayTradersCombine{tag}", {"INACTIVITY": inact})
        out[("DT", "funded", inact)] = _named(DayTradersFunded, f"DayTradersFunded{tag}", {"INACTIVITY": inact})
    for plan in ("FP", "QP"):
        for d in sorted(set(T.min_days_ends(plan))):
            out[(plan, "combine", d)] = _named(TradeDayCombine, f"TradeDayCombine{plan}{d}", {"PLAN": plan, "MIN_DAYS": d})
    for paid in (False, True):
        out[("FP", "funded", paid)] = _named(FastPassFunded, f"FastPassFunded{'FifthPaid' if paid else 'FifthUnpaid'}",
                                             {"FIFTH": "paid" if paid else "unpaid"})
    for peak in ("pess", "opt"):
        for ceil in (STRICT, LENIENT):
            for req in ("every", "cadence"):
                out[("QP", "funded", peak, ceil, req)] = _named(
                    QuickPayFunded, f"QuickPayFunded_{peak}_{ceil}_{req}", {"PEAK": peak, "CEILING": ceil, "REQUEST": req})
    out[("twin", "A-2")] = _named(DayTradersCombine, "DayTradersCombineTwin",
                                  {"DLL": False, "QUALIFYING": False, "INACTIVITY": False, "SELLS_RESET": True})
    out[("twin", "A-3")] = _named(DayTradersFunded, "DayTradersFundedTwin",
                                  {"DLL": False, "QUALIFYING": False, "REQUEST_RULE": False, "TABLE_INPUTS": False,
                                   "INACTIVITY": False})
    out[("twin", "A-4")] = _named(TradeDayCombine, "TradeDayCombineTwin", {"MIN_DAYS": 0, "SELLS_RESET": True})
    out[("twin", "A-5")] = _named(FastPassFunded, "FastPassFundedTwin",
                                  {"SHARE_RULE": False, "PASS_OVER": False, "FIFTH": None, "TABLE_INPUTS": False})
    out[("twin", "A-7")] = _named(QuickPayFunded, "QuickPayFundedTwin",
                                  {"INTRADAY": False, "FLOOR_GROSS": False, "SPLIT_TIERED": False, "CEILING": None,
                                   "REQUEST": "engine", "TABLE_INPUTS": False})
    return out


CLASSES = _build()
#: T-1's and 9.1 item 2's adapters at their Topstep setting: (adapter, account kind, class)
TWINS = tuple((a, "combine" if a in ("A-2", "A-4") else "funded", CLASSES[("twin", a)])
              for a in ("A-2", "A-3", "A-4", "A-5", "A-7"))


def classes_for(settings: T.Settings) -> tuple[type | None, type | None]:
    """(evaluation class, funded class) of a run's settings; (None, None) at TS and LU (the vendored classes, and
    Lucid's own through `lucid_setup`)."""
    p = settings.plan
    if p in ("TS", "LU"):
        return (None, None)
    if p == "DT":
        return CLASSES[("DT", "combine", bool(settings.inactivity))], CLASSES[("DT", "funded", bool(settings.inactivity))]
    if p == "FP":
        return CLASSES[("FP", "combine", int(settings.min_days))], CLASSES[("FP", "funded", bool(settings.fifth_paid))]
    if p == "QP":
        return (CLASSES[("QP", "combine", int(settings.min_days))],
                CLASSES[("QP", "funded", settings.peak, settings.ceiling, settings.request)])
    raise ValueError(f"unknown plan {p!r}")


def with_point(cls: type, point_blocks: Sequence[Any]) -> type:
    """A Quick Pay class holding the run's point outcomes (each block's `r_by_rr`), so the
    peak bracket classifies each trade on its point outcomes on every arm (M3: the draw's day list, a replay's start
    slice or the gate's whole list, whose shifted arm keeps its order). Made in the running process."""
    if not issubclass(cls, QuickPayFunded):
        raise TypeError("only Quick Pay's class reads the point outcomes")
    return type(f"{cls.__name__}Point", (cls,), {"POINT": tuple(b.r_by_rr for b in point_blocks),
                                                 "__module__": cls.__module__})


__all__ = ["TALLY", "collect", "gate_window_sessions", "with_calendar", "DayTradersCombine", "DayTradersFunded",
           "TradeDayCombine", "FastPassFunded", "QuickPayFunded", "ticks_of", "won_at", "peak_bracket", "CLASSES",
           "TWINS", "classes_for", "with_point", "NAMED"]
