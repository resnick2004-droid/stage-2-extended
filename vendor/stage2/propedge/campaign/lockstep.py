"""Lockstep campaign: every live account steps through the same calendar day (D-119, slice 2).

`propedge.campaign.reinvest` samples whole account lifetimes from a pool the vendored engine
built on an account-relative day index. Two accounts alive on the same calendar day therefore
never share a market day, and the campaign cannot see inside an account. This module keeps the
campaign clock -- the same daily order of events, fees, hold queue, cap and ruin -- but steps
every live account's own state machine, the Combine and funded rules exactly as the engine
applies them, one calendar day at a time. That is what the later slices need: shared
historical days for correlated accounts (slice 3) and per-trade sizing from the account's
current scaling tier (slice 4) are both impossible while an account's life is one
pre-computed record.

Calendar convention, shared with `reinvest.py`
-----------------------------------------------
A Combine bought on calendar day `d`, or a funded account activated on day `d`, trades from
day `d + 1`, which is its engine day 0. A resolution is recognised on the day it occurs. A
funded slot frees the day after the account's last trading day. The subscription rebills every
`billing_days` of the account's own trading days and is charged at the start of the calendar
day, as the engine charges it at the start of engine day `k * billing_days`.

Order of events within a day: (1) subscriptions due; (2) every live account trades its
session and locks at 16:00 CT; (3) payouts arriving today are credited, including those the
day's trading has just produced when the lag is zero; (4) Combines that resolved today join
the hold queue; (5) funded accounts that finished yesterday free their slot and the queue
activates, paying the activation fee then (D-21); (6) new Combines are bought; (7) ruin.
Step (2) is the only addition to `reinvest.simulate_path`; the rest is placed so the two loops
agree day for day. A payout requested at step (2) is made after 5:00 PM CT by default, so the
account's next session is the Payout request day and does not count toward the new cycle
(8284233; `propedge.contract.payout_timing`).

Exactness (the D-19 pattern)
----------------------------
Given the same per-account outcome streams, this loop reproduces `reinvest.simulate_path`
field for field, and each account's state machine reproduces the engine on scripted streams
(`tests/test_lockstep.py`), at either payout timing when both sides are given the same one
(the vendored engine's is `REQUEST_4_TO_5PM`). The trade-level loop is trusted because the
stage-level one is, and every later extension must keep both reductions.

Outcome draws
-------------
Each account owns an `OutcomeDraw` built by a factory from its index in activation order and
its start day; the account calls `draw(1, rel_day, slot, cushion)` with its own engine-relative
day, so the vendored `RandomDraw` (through `adapter.BinaryDraw`) and every stage-two draw plug
in unchanged. Shared calendar days (slice 3) will be a factory whose draw maps
`start_day + 1 + rel_day` onto a common day table; nothing here changes for that.

Everything that produces a number is seeded. The per-account seeds derive from the path seed,
the account kind and the account index, so a path is reproducible from its seed alone.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np

from propedge.campaign.protocols import Protocol
from propedge.contract.payout_timing import (
    DEFAULT_PAYOUT_TIMING,
    PAYOUT_TIMING_NOTES,
    check_payout_timing,
    request_day_excluded,
)
from propedge.campaign.reinvest import (
    ACTIVATION_ON_ACTIVATION,
    ACTIVATION_ON_PASS,
    ACTIVATION_TIMINGS,
    CampaignPath,
    CampaignSummary,
    summarise_paths,
)

#: The engine's comparison tolerance (`vendor/propsim/propsim.py`: EPS = 1e-9). Reproduced here,
#: not imported, so this module never touches the vendored tree.
EPS = 1e-9

#: `factory(index, start_day) -> OutcomeDraw`, where the draw is called as
#: `draw(1, rel_day, slot, cushion)` with the account's engine-relative day.
DrawFactory = Callable[[int, int], Any]

#: `day_hook(day, keys)`: called before any account trades on a calendar day, with the live
#: accounts in rotation order as `("combine" | "funded", index)` keys. The trade router of
#: `shared_days.ROTATION` uses it; other draws need none. A hook that takes a third argument also
#: gets each account's trade limit for the session (D-162), and one that takes a fourth each
#: account's balance and loss-limit floor at the start of the session, `{key: (balance, floor)}` (D-205).
DayHook = Callable[[int, list[tuple[str, int]]], None]

#: Child-seed kind for the payout-enforcement stream (D-145); 1 and 2 are the account draws.
_KIND_ENFORCEMENT = 9
_KIND_FLIP_DIRECTION = 10         # D-339: the day's shared direction for the flip stream's brackets
_KIND_FLIP_BINARY = 11            # D-339: a funded account's binary flip draw in the engine's own campaign (the table's model)


@dataclass(frozen=True)
class ConductModel:
    """D-145's tiers 2 and 3 on the lockstep loop. `simulate_lockstep_path(conduct=None)` (the
    default) runs neither, so every result before D-145 reproduces exactly.

    Tier 2, the Responsible Trading Program (13620045, verified; consequences D-43): the triggers
    the simulated path can show are checked at each day's close on the accounts that traded --
    two or more accounts at the MLL that day; an account whose average losing trade is not smaller
    than its average winning trade over its last `losers_window` trades (once it has
    `min_trades`); an account sized at its full contract allowance on more than
    `max_position_share` of its trades (once it has `min_trades`). Placement takes effect the day
    after the trigger day -- or, with `rtp_warnings` = k, after the (k+1)-th trigger day, the first k
    answered by a warning (13620045: "While warnings will often be sent out first, Topstep reserves
    the right to send Traders directly to RTP"; D-220) -- and lasts to the end of the path: the only
    exit is $10,000 of profit in a Live Funded Account, and the call-up to Live closes every XFA
    (13620045, 10657969; D-219), so an XFA campaign never leaves. From then on
    the `rtp_dll` daily loss limit (50K: $1,000, 10490293) is on every Combine bought, every
    Combine reset and every funded account activated (13620045: "All new Trading Combines® and
    XFAs automatically get a Daily Loss Limit (DLL)"; "If Reset, the new Trading Combine will
    follow RTP rules — it will be a Consistency Trading Combine account with a Daily Loss Limit
    (DLL)"). Hitting the limit stops that account's session; it does not fail the account. The
    payout path is decided by the Combine's purchase, not the activation day: a Combine bought (or
    reset) after placement is a Consistency Trading Combine and its funded account is on the
    Consistency path; a Combine bought before placement "will remain as a Standard Trading Combine.
    If passed, it may be activated as either a Standard XFA or Consistency XFA", so its funded
    account keeps the protocol's path -- with the daily loss limit, if activated after placement.

    Tier 3, account stacking and excessive purchases (10305426, 10296582): a payout requested on a
    day when the campaign has hit the MLL at least `pattern_breaches` times in the preceding
    `pattern_window_days` trading days (that day included) is *exposed*; an exposed payout is
    denied, and its account closed, when a uniform draw from the path's own enforcement stream
    falls below `enforcement_p`. The draw is made for every exposed payout whatever
    `enforcement_p` is, so runs at different probabilities share their random numbers.

    The window lengths and thresholds are declared assumptions (D-145), not published values.
    """

    rtp: bool = True
    rtp_dll: float = 1000.0
    losers_window: int = 30
    min_trades: int = 20
    max_position_share: float = 0.5
    enforcement_p: float = 0.0
    pattern_breaches: int = 2
    pattern_window_days: int = 21
    rtp_warnings: int = 0       # trigger days answered by a warning before placement (D-220); 0: the strictest reading

    def __post_init__(self) -> None:
        if not 0.0 <= self.enforcement_p <= 1.0:
            raise ValueError(f"enforcement_p must be in [0, 1], got {self.enforcement_p}")
        if self.rtp_dll <= 0 or self.pattern_breaches < 1 or self.pattern_window_days < 1:
            raise ValueError("rtp_dll, pattern_breaches and pattern_window_days must be positive")
        if self.rtp_warnings < 0:
            raise ValueError(f"rtp_warnings must be at least 0, got {self.rtp_warnings}")

    def as_dict(self) -> dict[str, Any]:
        """The fields; `rtp_warnings` only when set, so a provenance written before D-220 reproduces exactly."""
        from dataclasses import asdict

        d = asdict(self)
        if not self.rtp_warnings:
            del d["rtp_warnings"]
        return d


#: D-495 (4): the Focused Trader Program's two paths (10551016).
FTP_SLOWDOWN = "slowdown"
FTP_CORRECTIVE = "corrective"
FTP_PATHS = (FTP_SLOWDOWN, FTP_CORRECTIVE)


@dataclass(frozen=True)
class FocusedTraderModel:
    """D-495 (4): Topstep's Focused Trader Program as a campaign-level event (`RULES_LEDGER.md` / `config/rules.yaml`
    row `focused_trader_program`, article 10551016, read 2026-10-30). `simulate_lockstep_path(focused_trader=None)` (the
    default) runs none of it, so every result before D-495 reproduces exactly.

    What the page says, quoted from the verified row:

    * **Slowdown Path** -- reasons "Excessive Resets and Trading Combine purchases" and "Activating and losing many
      Express Funded Accounts in a short period of time"; consequences "You may continue trading in your existing
      active accounts", "You cannot purchase new Trading Combines, Resets, or B2F Reactivations", "Current active
      accounts can remain open but limited to 1 active $50K account at a time (Trading Combine, XFA, or LFA) once
      closed"; time requirement "None".
    * **Corrective Path** -- reason "Excessive recycling of Trading Combines® or XFAs"; consequences "All current
      accounts (Live, Express Funded Account, Trading Combine) are closed", "No refunds are issued", "Any pending
      payouts are denied", "Any pending Express Funded Accounts or banked resets are removed (if applicable)", "1
      active $50K account at a time (Trading Combine, XFA, or LFA)"; time requirement "6 months".

    The page publishes no number, threshold or window ("excessive", "many", "short period" are undefined) and no rule
    for which path a pattern draws, so all of it is declared here (D-495 (4)), never read from the firm:

    * the measures watched, each counted over the last `window_days` trading days (that day included) -- Combine
      purchases and resets (`combine_purchases`: the threshold, None = not watched) and funded accounts lost, an XFA
      ended by a breach, by closure at request or by a tier-3 denial's closure (`funded_lost`: the threshold, None = not
      watched). Placement happens at the close of the first day any watched measure reaches its threshold;
    * `path` -- which path that placement takes.

    The engine's reading of the consequences (each a declared reading, the help centre states no more):

    * placement is decided at that day's close, after the day's purchases, and binds from the next day;
    * **Slowdown**: no Combine is bought and no reset taken from the next day while any account is live; once none is,
      at most `account_limit` (1) account is live at a time -- a Combine is bought only while the live accounts
      (running Combines, funded accounts and passes waiting for a seat) are fewer. A pass of a Combine live at
      placement still activates (it is that account's own conversion, not a purchase). Resets stay refused, and the
      placement lasts to the end of the path (time requirement "None"; the review needs Live Funded Account profits,
      out of scope);
    * **Corrective**: at that close every live account ends -- Combines (one bought that evening included) and funded
      accounts alike, no breach, nothing refunded, nothing of a balance credited -- the passes waiting for a seat are
      removed, and every payout requested and not yet arrived is denied (its account's bookkeeping undone, as tier 3's
      denial does). Then at most `account_limit` account is live at a time for `corrective_days` trading days (126:
      six months of 21), after which the program ends; with `repeat` the measures are watched again, counted only from
      the day after the end.
    """

    path: str
    combine_purchases: int | None = None
    funded_lost: int | None = None
    window_days: int = 21
    account_limit: int = 1
    corrective_days: int = 126
    repeat: bool = True

    def __post_init__(self) -> None:
        if self.path not in FTP_PATHS:
            raise ValueError(f"path must be one of {FTP_PATHS}, got {self.path!r}")
        if self.combine_purchases is None and self.funded_lost is None:
            raise ValueError("the Focused Trader Program needs at least one watched measure (combine_purchases or "
                             "funded_lost); the page publishes none, so each is declared (D-495 (4))")
        for name in ("combine_purchases", "funded_lost"):
            v = getattr(self, name)
            if v is not None and int(v) < 1:
                raise ValueError(f"{name} must be at least 1, got {v}")
        if self.window_days < 1 or self.account_limit < 1 or self.corrective_days < 1:
            raise ValueError("window_days, account_limit and corrective_days must be at least 1")

    @property
    def label(self) -> str:
        parts = [self.path]
        if self.combine_purchases is not None:
            parts.append(f"purchases>={int(self.combine_purchases)}/{self.window_days}d")
        if self.funded_lost is not None:
            parts.append(f"lost>={int(self.funded_lost)}/{self.window_days}d")
        return " ".join(parts)

    def as_dict(self) -> dict[str, Any]:
        from dataclasses import asdict

        return {**asdict(self), "article": "10551016", "ledger_row": "focused_trader_program"}


def _rolling_max(x: np.ndarray, w: int) -> int:
    """The largest sum of `w` consecutive days (the whole array when shorter)."""
    if len(x) >= w:
        return int(np.convolve(x, np.ones(w, dtype=int), "valid").max())
    return int(x.sum())


def _count_max(account: Any, draw: Any) -> None:
    """Count a trade sized at the account's full contract allowance (RTP: "You max position a
    majority of your trades"). Only a draw that sizes in contracts can say; others count nothing."""
    last = getattr(draw, "last_trade", None) or {}
    allowance = getattr(draw, "current_allowance_micros", None)
    contracts = last.get("contracts")
    if allowance and contracts is not None and contracts >= allowance:
        account.at_max += 1


def _losers_not_smaller(pnls: list[float], window: int, min_trades: int) -> bool:
    """RTP: "You don't keep losers smaller than winners", over the last `window` trades."""
    if len(pnls) < min_trades:
        return False
    recent = pnls[-window:]
    wins = [p for p in recent if p > 0]
    losses = [-p for p in recent if p < 0]
    if not wins or not losses:
        return bool(losses) and not wins
    return sum(losses) / len(losses) >= sum(wins) / len(wins)


def _ledger_row(
    kind: str, index: int, day: int, rel_day: int, slot: int, pnl: float,
    before: float, after: float, floor: float, draw: Any,
) -> dict[str, Any]:
    """One executed trade for the per-trade ledger: which account, which day, what it did to
    the balance, and what the draw reports about the trade it handed out (historical day,
    trade index, contracts, realised risk) when it reports anything."""
    row: dict[str, Any] = {
        "day": int(day), "kind": kind, "index": int(index), "rel_day": int(rel_day),
        "slot": int(slot), "pnl": float(pnl), "balance_before": float(before),
        "balance_after": float(after), "floor": float(floor),
    }
    last = getattr(draw, "last_trade", None)
    if last:
        row.update(last)
    return row


# --------------------------------------------------------------- account state machines


@dataclass
class CombineAccount:
    """One Combine, stepped a day at a time. Mirrors `propsim.simulate_combine` for n = 1."""

    index: int                    # attempt number, in purchase order
    purchase_day: int             # calendar day the subscription was bought
    draw: Any                     # OutcomeDraw, called with n = 1 and this account's engine day
    floor_start: float            # -rules.mll
    subs_paid: int = 1
    B: float = 0.0
    F: float = field(init=False)
    best_day: float = 0.0
    days: int = 0
    trades: int = 0
    passed: bool = False
    failed: bool = False
    unresolved: bool = False      # ran out of `combine_max_days` without resolving
    abandoned: bool = False       # dropped because the next subscription was unaffordable
    pass_day: int = -1            # engine-relative
    fail_day: int = -1            # engine-relative
    resolved_on: int | None = None  # calendar day the account stopped
    dll: float | None = None      # a daily loss limit (D-145: an RTP Combine's); None = none
    # RTP (13620045): the current attempt was bought, or reset, while the Responsible Trading Program was in force,
    # so it is a Consistency Trading Combine and a pass is activated on the Consistency path. `purchase_day` above is
    # the day the subscription was bought, which decides it for an attempt that was never reset.
    rtp: bool = False
    pnls: list[float] = field(default_factory=list)     # every trade's P&L, for the RTP checks
    at_max: int = 0               # trades sized at the full contract allowance
    # D-146: the last session, for the daily recorder; and the resets this account has taken.
    last_day_pnl: float = 0.0
    last_target: float = 0.0      # the effective target after the lock (consistency can raise it)
    resets: int = 0
    reset_days: list[int] = field(default_factory=list)
    attempt_start_day: int = -1   # calendar day the current attempt began trading
    decision: Any = None          # D-147: the risk policy's decision for the current session
    out_of_room: bool = False     # D-318: ended because its room bought no trade at its state's R (failed, not breached)
    abandoned_by_policy: bool = False   # D-329: the policy ended the attempt (cancelled, 8284121), not the bankroll
    household_closed: bool = False      # R7 (multi-firm D-30): ended by the firm's household rule, not failed
    ftp_closed: bool = False            # D-495 (4): ended by the Focused Trader Program's Corrective Path, not failed

    def __post_init__(self) -> None:
        from propedge.outcomes.settlement import settlement_of

        settlement_of(self.draw)                 # D-156: a draw must say how it settles against the room
        self.F = float(self.floor_start)
        self.attempt_start_day = self.purchase_day + 1

    def close_ftp(self, calendar_day: int) -> None:
        """D-495 (4): the Focused Trader Program's Corrective Path ends the attempt at this close -- "All current
        accounts (Live, Express Funded Account, Trading Combine) are closed", "No refunds are issued" (10551016). Not a
        failure, not a breach; nothing refunded."""
        self.ftp_closed = True
        self.resolved_on = int(calendar_day)

    def close_household(self, calendar_day: int) -> None:
        """R7 (multi-firm D-30; docs/TWO_FIRMS.md): the firm's household rule ends the attempt at this close -- Lucid
        closes every simulated account in the household when a trader is moved live or cashes out (16558826). Not a
        failure, not a breach, not the bankroll's or the policy's abandonment; the path buys no replacement."""
        self.household_closed = True
        self.resolved_on = int(calendar_day)

    def finish_abandoned(self, calendar_day: int) -> None:
        """D-329: the policy's abandon -- the trader cancels the subscription (8284121: irreversible, nothing refunded)
        and the slot frees like any resolved attempt's. Taken at the close whose state decides it (D-334), so the
        replacement trades the next session as after a breach. Not a failure (no breach, no reset) and not the
        bankroll's abandonment (`abandoned` alone)."""
        self.abandoned = True
        self.abandoned_by_policy = True
        self.resolved_on = int(calendar_day)

    def finish_out_of_room(self, rel_day: int, calendar_day: int) -> None:
        """D-318: the attempt ends out of room -- under the room cap its room above the floor buys no micro at any stop
        its state's R is offered at, so it could never trade again and never fail. It is a failed attempt (the trader
        stops it and buys, or resets, another), not a breach of the floor. Taken at the close that finds it (D-335), so
        the replacement trades the next session as after a breach; D-318's start-of-session form stays as a fallback."""
        self.failed = True
        self.out_of_room = True
        self.fail_day = int(rel_day)
        self.resolved_on = int(calendar_day)

    def reset(self, calendar_day: int, *, rtp_dll: float | None = None) -> None:
        """D-146: a failed Combine is reset to its starting balance and trades again from the next
        session. The subscription and its billing dates are unchanged; the failure stays counted.

        `rtp_dll`: the Responsible Trading Program's daily loss limit when the reset happens while RTP is in force
        (13620045: "If Reset, the new Trading Combine will follow RTP rules — it will be a Consistency Trading Combine
        account with a Daily Loss Limit (DLL)"). The reset attempt then carries it; None leaves the limit as it was."""
        if rtp_dll is not None:
            self.dll = float(rtp_dll)
            self.rtp = True
        self.resets += 1
        self.reset_days.append(int(calendar_day))
        self.B = 0.0
        self.F = float(self.floor_start)
        self.best_day = 0.0
        self.failed = False
        self.out_of_room = False
        self.fail_day = -1
        self.resolved_on = None
        self.attempt_start_day = int(calendar_day) + 1

    @property
    def start_day(self) -> int:
        """First trading day: engine day 0 is the day after purchase."""
        return self.purchase_day + 1

    @property
    def alive(self) -> bool:
        return not (self.passed or self.failed or self.unresolved or self.abandoned or self.household_closed
                    or self.ftp_closed)

    def need_to_pass(self, rules: Any, day_pnl: float) -> float | None:
        """D-306: what the account must net on its next trade to pass at today's lock -- the profit target, or the
        consistency-raised target (the best day so far over the allowed fraction), less the balance -- or None when
        no gain today can pass it, because the day's gain would itself raise the consistency target out of reach
        (`today's net <= frac x the balance after it`, 8284208) or the account is already at a pass."""
        frac = float(rules.consistency_max_day_frac)
        x = max(float(rules.profit_target), self.best_day / frac) - self.B
        if x <= EPS:
            return None
        if frac < 1.0 and day_pnl + x > frac * (self.B + x) + EPS:
            return None
        return float(x)

    def at_pass(self, rules: Any, day_pnl: float) -> bool:
        """Whether the balance would pass at the lock if the day ended now (the consistency target read with today)."""
        best = max(self.best_day, day_pnl)
        return self.B >= max(float(rules.profit_target), best / float(rules.consistency_max_day_frac)) - EPS

    def day_allowance(self, rules: Any, day_pnl: float) -> float:
        """D-313: what today may still gain without lifting the consistency target -- the allowed fraction of the
        current effective target (8284208: the best day at most 55 % of the profit target) less today's gain so far."""
        frac = float(rules.consistency_max_day_frac)
        target_eff = max(float(rules.profit_target), self.best_day / frac)
        return float(frac * target_eff - day_pnl)

    def trade_day(
        self, rules: Any, policy: Any, rel_day: int, calendar_day: int,
        ledger: list[dict[str, Any]] | None = None, need_aware: bool = False, consistency_cap: bool = False,
    ) -> None:
        """One engine day: the trade slots, then the 16:00 CT lock and the pass check.

        `ledger`, if given, receives one row per executed trade (the per-trade ledger, D-130),
        with whatever the draw reports about how it sized the trade. `need_aware` (D-306; the operator, 2026-10-06):
        a draw that honours it (`takes_need`) is told what the account needs to pass and closes the trade there,
        and once the balance is at a pass the account takes nothing more that day -- the lock makes it a pass.
        `consistency_cap` (D-313; the operator, 2026-10-07): when the pass cannot be taken today, the draw is told the
        day's remaining consistency allowance instead and closes a winning trade there, so no day lifts the target;
        once the allowance is used the account takes nothing more that day."""
        active = True
        day_pnl = 0.0
        takes_need = (bool(need_aware) or bool(consistency_cap)) and bool(getattr(self.draw, "takes_need", False))
        for slot in range(policy.trades_per_day):
            if not active:
                break
            cushion = self.B - self.F
            # D-145: under a daily loss limit the nearer barrier is the limit's remaining room; the draw is told it
            # so a draw that races its barrier (the vendored RandomDraw) races that one, not the floor.
            room = cushion if self.dll is None else min(cushion, self.dll + day_pnl)
            exit_kind = None
            if takes_need:
                x = self.need_to_pass(rules, day_pnl) if need_aware else None
                exit_kind = "pass" if x is not None else None
                if x is None and consistency_cap:
                    allowance = self.day_allowance(rules, day_pnl)
                    if allowance <= EPS:
                        break                      # D-313: today's allowance is used
                    x, exit_kind = allowance, "consistency"
                pnl = float(self.draw(1, rel_day, slot, np.array([room]), need=x)[0])
                last = getattr(self.draw, "last_trade", None)
                if last is not None:
                    last["exit_kind"] = exit_kind if last.get("at_need") else None
            else:
                pnl = float(self.draw(1, rel_day, slot, np.array([room]))[0])
            if math.isnan(pnl):
                continue                           # no trade in this slot
            # The draw has settled the trade against `room` (D-156: it raced the barrier, or used the trade's
            # MAE, or assumed the worst); these clips only hold the balance at the barrier it touched.
            if rules.liquidate_at_floor:
                pnl = max(pnl, -cushion)
            if self.dll is not None:
                pnl = max(pnl, -(self.dll + day_pnl))   # liquidated at the daily loss limit
            before = self.B
            self.B += pnl
            day_pnl += pnl
            self.trades += 1
            self.pnls.append(pnl)
            _count_max(self, self.draw)
            if ledger is not None:
                ledger.append(_ledger_row(
                    "combine", self.index, calendar_day, rel_day, slot, pnl, before, self.B,
                    self.F, self.draw,
                ))
            if self.B <= self.F + EPS:
                self.failed = True
                self.fail_day = rel_day
                self.resolved_on = calendar_day
                active = False
                break
            if self.dll is not None and day_pnl <= -self.dll + EPS:
                active = False                     # the limit ends the day; it is not a violation
            if policy.stop_day_on_win and pnl > 0:
                active = False
            if policy.stop_day_on_loss and pnl < 0:
                active = False
            if need_aware and self.at_pass(rules, day_pnl):
                active = False                     # D-306: at a passing balance nothing more is risked today
            if consistency_cap and self.day_allowance(rules, day_pnl) <= EPS:
                active = False                     # D-313: the day's consistency allowance is used
        # 16:00 CT lock. The day counts even if the account breached during it.
        self.days += 1
        self.last_day_pnl = day_pnl
        if self.failed:
            return
        self.best_day = max(self.best_day, day_pnl)
        new_floor = max(self.F, self.B - rules.mll)
        if rules.combine_mll_lock_at is not None:
            new_floor = min(rules.combine_mll_lock_at, new_floor)
        self.F = new_floor
        target_eff = max(rules.profit_target, self.best_day / rules.consistency_max_day_frac)
        self.last_target = target_eff
        if self.B >= target_eff - EPS:
            self.passed = True
            self.pass_day = rel_day
            self.resolved_on = calendar_day


@dataclass
class FundedAccount:
    """One funded account, stepped a day at a time. Mirrors `simulate_xfa_dated` for n = 1 at the same
    `payout_timing`. The default timing is the payout policy's rule for a request made after 5:00 PM CT
    (`propedge.contract.payout_timing`); the vendored engine's, which `simulate_xfa_dated` keeps by default, needs
    `payout_timing=REQUEST_4_TO_5PM` -- a request submitted between 4:00 and 5:00 PM CT on the eligible day."""

    index: int                    # activation number, in activation order
    activation_day: int           # calendar day the activation fee was paid
    draw: Any
    horizon_days: int             # trading days after which the account is closed out
    floor_start: float            # rules.xfa_mll_start
    B: float = 0.0
    F: float = field(init=False)
    days: int = 0
    trades: int = 0
    closed: bool = False          # breached the floor
    win_days: int = 0
    w_days: int = 0
    w_profit: float = 0.0
    w_best: float = 0.0
    since_pay: float = 0.0
    paid_once: bool = False
    cash: float = 0.0
    gross_paid: float = 0.0
    n_payouts: int = 0
    first_payout_day: int = -1    # engine-relative
    payout_days: list[int] = field(default_factory=list)      # engine-relative
    payout_cash: list[float] = field(default_factory=list)    # net to the trader
    ended_on: int | None = None   # calendar day of the last trading day
    ever_credited: bool = False   # a payout has reached the campaign's cash
    policy_override: Any = None   # D-145: an RTP account's Consistency-path policy; None = the protocol's
    # RTP (13620045): "All new Trading Combines® and XFAs automatically get a Daily Loss Limit (DLL)". A funded
    # account activated after placement carries it: the session stops at the limit, which is not a violation.
    dll: float | None = None      # None = no daily loss limit
    # The Combine this account was activated from (RTP decides the path by its purchase, 13620045); -1 = none given.
    combine_index: int = -1
    combine_purchase_day: int = -1
    # When a payout is requested (8284233; `propedge.contract.payout_timing`). The default is a request made after
    # 5:00 PM CT: the next trading day is the Payout request day and does not count toward the new cycle.
    payout_timing: str = DEFAULT_PAYOUT_TIMING
    request_day_next: bool = False  # the next session is the Payout request day
    last_request_day: bool = False  # the last session was the Payout request day (left out of the cycle)
    pnls: list[float] = field(default_factory=list)
    at_max: int = 0
    last_request: float = 0.0     # gross amount of the payout requested at the last close
    denied: int = 0               # payouts denied under D-145's tier 3
    # D-146: the last session, for the daily recorder.
    last_day_pnl: float = 0.0
    last_eligible: bool = False   # payout-eligible at the last close (before any request)
    last_cons_blocked: bool = False  # consistency path: the best-day share blocked eligibility
    decision: Any = None          # D-147: the risk policy's decision for the current session
    abandoned: bool = False       # D-329: closed at the policy's request (10657969; nothing of the balance credited)
    # D-339: the flip stream -- the account's own scheduled bracket, drawn from `flip_draw` on the sessions the policy's
    # state is a flip state (`flip_today`), instead of a routed signal; counted apart.
    flip_draw: Any = None
    flip_today: bool = False
    flips: int = 0
    flips_won: int = 0
    # D-384: the secured balance -- the highest close before the first payout, and the balance at that payout's close
    peak_before_payout: float = 0.0
    balance_at_first_payout: float = float("nan")
    # D-368: the second trades taken after a first that fell short of the winning-day minimum, and the days they made
    # winning days
    second_trades: int = 0
    second_qualified: int = 0
    # D-368: the trades taken in the collect phase (a take-profit at the shortfall to the winning-day minimum) and the
    # days they made winning days
    collect_trades: int = 0
    collect_qualified: int = 0
    household_closed: bool = False  # R7 (multi-firm D-30): ended by the firm's household rule (no breach, not credited)
    ftp_closed: bool = False        # D-495 (4): ended by the Focused Trader Program's Corrective Path (no breach)
    ftp_denied: int = 0             # D-495 (4): pending payouts the Corrective Path denied

    def close_ftp(self, calendar_day: int) -> None:
        """D-495 (4): the Focused Trader Program's Corrective Path ends the account at this close -- "All current
        accounts (Live, Express Funded Account, Trading Combine) are closed", "No refunds are issued" (10551016). Not a
        breach (`closed` stays False); nothing of the balance reaches the campaign."""
        self.ftp_closed = True
        self.ended_on = int(calendar_day)

    def deny_pending_ftp(self, net: float, rules: Any) -> None:
        """D-495 (4): "Any pending payouts are denied" (10551016) -- a payout requested and not yet arrived is refused;
        its bookkeeping is undone as tier 3's denial undoes it (`deny_last_payout`). The pending payouts are an
        account's latest, so they are undone latest first; the gross is the request the net came from."""
        if not self.payout_cash or abs(float(self.payout_cash[-1]) - float(net)) > 1e-9:
            raise RuntimeError("a pending payout is undone latest first")
        self.payout_cash.pop()
        self.payout_days.pop()
        self.cash -= float(net)
        self.gross_paid -= (float(net) + float(rules.payout_fee)) / float(rules.profit_split)
        self.n_payouts -= 1
        if self.n_payouts == 0:
            self.first_payout_day = -1
            self.paid_once = False
        self.ftp_denied += 1

    def close_household(self, calendar_day: int) -> None:
        """R7 (multi-firm D-30; docs/TWO_FIRMS.md): the firm's household rule ends the account at this close (Lucid:
        "All simulated prop accounts are closed when a trader is moved live, or opts out of trading live via cash-out",
        16558826). Not a breach (`closed` stays False) and nothing of the balance reaches the campaign -- an account
        moved live is out of scope, as the live account is; payouts already requested still arrive."""
        self.household_closed = True
        self.ended_on = int(calendar_day)

    def close_abandoned(self, calendar_day: int) -> None:
        """D-329: the policy's abandon -- the account is closed as a trader closes an XFA by contacting Support
        (10657969; ToU s.8); the help centre states no payout terms for it, so nothing of the balance reaches the
        campaign. Taken at the close whose state decides it (D-334), so the slot frees the next day as after any
        closure; it is not a breach."""
        self.closed = True
        self.abandoned = True
        self.ended_on = int(calendar_day)

    def __post_init__(self) -> None:
        from propedge.outcomes.settlement import settlement_of

        settlement_of(self.draw)                 # D-156: a draw must say how it settles against the room
        self.F = float(self.floor_start)
        check_payout_timing(self.payout_timing)

    def deny_last_payout(self, calendar_day: int) -> None:
        """D-145 tier 3: the payout requested at today's close is refused and the account closed.
        Undoes the request's bookkeeping; nothing reaches the campaign's cash."""
        if not self.payout_cash:
            raise RuntimeError("no payout to deny")
        net = self.payout_cash.pop()
        self.payout_days.pop()
        self.cash -= net
        self.gross_paid -= self.last_request
        self.n_payouts -= 1
        if self.n_payouts == 0:
            self.first_payout_day = -1
            self.paid_once = False
        self.denied += 1
        self.closed = True
        self.ended_on = calendar_day

    @property
    def start_day(self) -> int:
        return self.activation_day + 1

    @property
    def alive(self) -> bool:
        return not self.closed

    def trade_day(
        self, rules: Any, policy: Any, cap: float, rel_day: int, calendar_day: int,
        ledger: list[dict[str, Any]] | None = None, second_trade: bool = False, collect: bool = False,
    ) -> float | None:
        """One engine day. Returns the net payout requested at today's close, or None.

        Under a daily loss limit (`dll`, the RTP's, 13620045) the day runs exactly as a Combine's does: the draw is
        handed the nearer barrier, min(room to the MLL, room to the day's limit); a trade is liquidated at the limit;
        the session stops once the day has lost the limit; the account survives. With `dll` None nothing changes.

        `second_trade` (D-368; the engine decides it, off unless the protocol declares `xfa_second_trade`): the
        account's first trade of the day is its state's; if the day then stands below the Standard path's winning-day
        minimum, a second routed signal is taken in the draw's stretch mode -- the same dollar risk, bracketed at the
        smallest carried R covering the shortfall and closed at exactly the minimum when reached; the day stops once it
        is a winning day, and after the second trade.

        `collect` (D-368; the engine decides it, off unless the protocol declares `xfa_collect_from`): every strategy
        trade of the session is taken in the draw's stretch mode for the shortfall to the winning-day minimum (the whole
        minimum on the first), at the dollar risk the engine set on the draw; the session stops once the day is a
        winning day."""
        active = True
        day_pnl = 0.0
        traded = False
        # D-339: a flip session draws one bracket from the account's own flip draw; a strategy session the routed
        # signals from its draw, as before
        flip = bool(self.flip_today)
        if flip and self.flip_draw is None:
            raise ValueError("a flip session needs the account's flip draw (D-339)")
        drw = self.flip_draw if flip else self.draw
        n_slots = 1 if flip else int(policy.trades_per_day)
        second = bool(second_trade) and not flip
        coll = bool(collect) and not flip
        win_min = float(rules.std_winning_day_min)
        for slot in range(n_slots):
            if not active:
                break
            cushion = self.B - self.F
            # The nearer barrier is handed to the draw, so a draw that races its barrier races the limit's room.
            room = cushion if self.dll is None else min(cushion, self.dll + day_pnl)
            if coll:
                # D-368: the collect phase -- a take-profit at what the day still needs to be a winning day
                need = win_min - day_pnl
                if need <= EPS:
                    break
                pnl = float(drw(1, rel_day, slot, np.array([room]), need=need, stretch=True)[0])
            elif second and slot >= 1:
                # D-368: the second trade, bracketed at the shortfall to the winning-day minimum -- only after a first
                # trade was taken today and left the day short of it
                need = win_min - day_pnl
                if not traded or need <= EPS:
                    break
                pnl = float(drw(1, rel_day, slot, np.array([room]), need=need, stretch=True)[0])
            else:
                # D-343: a flip draw is keyed by the CALENDAR day, so copied flips share the day's outcome
                pnl = float(drw(1, calendar_day if flip else rel_day, slot, np.array([room]))[0])
            if math.isnan(pnl):
                if second and slot >= 1:
                    break                                  # D-368: at most one second trade
                continue
            if rules.liquidate_at_floor:
                pnl = max(pnl, -cushion)
            if self.dll is not None:
                pnl = max(pnl, -(self.dll + day_pnl))   # liquidated at the daily loss limit
            before = self.B
            self.B += pnl
            day_pnl += pnl
            self.trades += 1
            traded = True
            self.pnls.append(pnl)
            _count_max(self, drw)
            if coll:
                self.collect_trades += 1               # D-368 / D-379: every trade taken, one that ends the account too
            if second and slot >= 1:
                self.second_trades += 1
            if flip:
                self.flips += 1
                self.flips_won += int(pnl > 0)
            if ledger is not None:
                row = _ledger_row("funded", self.index, calendar_day, rel_day, slot, pnl, before, self.B, self.F, drw)
                row["source"] = "flip" if flip else "strategy"
                ledger.append(row)
            if self.B <= self.F + EPS:
                self.closed = True
                self.ended_on = calendar_day
                active = False
                break
            if self.dll is not None and day_pnl <= -self.dll + EPS:
                active = False                     # the limit ends the session; it is not a violation
            if policy.stop_day_on_win and pnl > 0:
                active = False
            if policy.stop_day_on_loss and pnl < 0:
                active = False
            if coll:
                if day_pnl >= win_min - EPS:
                    self.collect_qualified += 1
                    active = False                 # D-368: a winning day is not risked again
            if second:
                if slot >= 1:
                    self.second_qualified += int(day_pnl >= win_min - EPS)
                    active = False                 # D-368: at most one second trade
                if day_pnl >= win_min - EPS:
                    active = False                 # D-368: a winning day is not risked again
        self.days += 1
        if self.n_payouts == 0:                     # D-384: the secured balance's high, at the closes before any payout
            self.peak_before_payout = max(self.peak_before_payout, float(self.B))
        self.last_day_pnl = day_pnl
        self.last_eligible = False
        self.last_cons_blocked = False
        if self.closed:
            return None
        if self.days >= self.horizon_days:
            self.ended_on = calendar_day        # last trading day; the lock below still runs

        # 16:00 CT lock and the payout window, exactly as the engine orders them.
        self.F = min(rules.xfa_lock_at, max(self.F, self.B - rules.mll))
        # 8284233: a request made after 5:00 PM CT belongs to the next trading day, which "becomes the Payout request
        # day and is excluded from the new cycle". Its P&L is in the balance, the floor and the profit since the
        # payout; it is not a winning day, a trading day, or part of the Consistency path's profit and best day.
        excluded = self.request_day_next
        self.request_day_next = False
        self.last_request_day = excluded
        if not excluded:
            if traded:                              # "3 trading days with at least 1 trade per day" (8284208)
                self.w_days += 1
            self.w_profit += day_pnl
            self.w_best = max(self.w_best, day_pnl)
        self.since_pay += day_pnl
        if not excluded and day_pnl >= rules.std_winning_day_min - EPS:
            self.win_days += 1

        if policy.payout_path == "standard":
            eligible = self._standard_eligible(rules)
        else:
            eligible = (
                self.w_days >= rules.cons_min_days
                and self.w_profit > 0
                and self.w_best <= rules.cons_max_day_frac * self.w_profit + EPS
            )
            self.last_cons_blocked = bool(
                self.w_days >= rules.cons_min_days and self.w_profit > 0
                and self.w_best > rules.cons_max_day_frac * self.w_profit + EPS
            )
        self.last_eligible = bool(eligible)
        allowed = min(rules.payout_max_frac_of_balance * self.B, cap)
        request = policy.payout_frac * allowed
        if policy.keep_balance > 0:
            request = min(request, max(self.B - policy.keep_balance, 0.0))
        if not (eligible and request >= rules.payout_min - EPS):
            return None

        net = rules.profit_split * request - rules.payout_fee
        self.last_request = request
        if self.n_payouts == 0:                     # D-384: the balance the first payout was taken from
            self.balance_at_first_payout = float(self.B)
        self.B -= request
        self.gross_paid += request
        self.cash += net
        self.n_payouts += 1
        self.since_pay = 0.0
        self.paid_once = True
        if self.first_payout_day < 0:
            self.first_payout_day = rel_day
        self.F = rules.xfa_lock_at                 # the floor hardens at $0 on any payout
        self.win_days = 0
        self.w_days = 0
        self.w_profit = 0.0
        self.w_best = 0.0
        # Balance and floor move at the request, before the next session (the engine's convention; no page says
        # whether at request or at approval). Under the default timing the next session is the Payout request day.
        self.request_day_next = request_day_excluded(self.payout_timing)
        self.payout_days.append(rel_day)
        self.payout_cash.append(net)
        self._after_payout(calendar_day)
        return net

    def _standard_eligible(self, rules: Any) -> bool:
        """The Standard path's payout eligibility at today's close (8284233): the winning days, and with
        `require_profit_since_payout` a profit since the last payout. R7: a seam for another firm's funded account
        (`propedge.contract.lucid.LucidFundedAccount`); Topstep's account is exactly as before."""
        eligible = self.win_days >= rules.std_winning_days
        if rules.require_profit_since_payout:
            eligible = eligible and ((not self.paid_once) or self.since_pay > EPS)
        return eligible

    def _after_payout(self, calendar_day: int) -> None:
        """R7: called once a payout has been requested at today's close, after its bookkeeping. Nothing at Topstep;
        another firm's account ends here when its contract says so (Lucid: moved live after its fifth payout)."""
        return None


# --------------------------------------------------------------------------- records


@dataclass(frozen=True)
class CombineRecord:
    index: int
    purchase_day: int
    resolved_on: int | None
    passed: bool
    failed: bool
    unresolved: bool
    abandoned: bool
    pass_day: int
    fail_day: int
    days: int
    trades: int
    balance: float
    floor: float
    subscriptions_paid: int
    sizing: dict[str, Any] | None = None    # `SizingStats.as_dict()` when the draw sized trades
    resets: int = 0                         # D-146: failures answered with a reset
    reset_days: tuple[int, ...] = ()
    dll: float | None = None                # the daily loss limit the last attempt carried (RTP), None for none
    rtp: bool = False                       # the last attempt was bought or reset under RTP (a Consistency Combine)
    out_of_room: bool = False               # D-318: the last attempt ended out of room (failed, not breached)
    abandoned_by_policy: bool = False       # D-329: the policy cancelled the attempt (a slot freed, no breach)
    household_closed: bool = False          # R7: ended by the firm's household rule (multi-firm D-30)
    ftp_closed: bool = False                # D-495 (4): ended by the Focused Trader Program's Corrective Path


@dataclass(frozen=True)
class FundedRecord:
    index: int
    activation_day: int
    ended_on: int | None
    closed: bool
    days: int
    trades: int
    balance: float
    floor: float
    n_payouts: int
    first_payout_day: int
    payout_days: tuple[int, ...]
    payout_cash: tuple[float, ...]
    gross_paid: float
    cash: float
    sizing: dict[str, Any] | None = None
    denied: int = 0                         # payouts denied under D-145's tier 3
    dll: float | None = None                # the RTP daily loss limit the account carried, None for none
    combine_index: int = -1                 # the Combine it was activated from, and that Combine's purchase day
    combine_purchase_day: int = -1
    consistency_forced: bool = False        # RTP put it on the Consistency path (its Combine was an RTP Combine)
    abandoned: bool = False                 # D-329: closed at the policy's request, nothing of the balance credited
    flips: int = 0                          # D-339: flip brackets taken (the flip stream), and of them the winners
    flips_won: int = 0
    second_trades: int = 0                  # D-368: second trades after a first short of the winning-day minimum
    second_qualified: int = 0               # ... and the days they made winning days
    collect_trades: int = 0                 # D-368: trades in the collect phase (a take-profit at the shortfall)
    collect_qualified: int = 0              # ... and the days they made winning days
    peak_before_payout: float = 0.0         # D-384: the highest close before the first payout
    balance_at_first_payout: float = float("nan")   # ... and the balance that payout was taken from (NaN: never paid)
    household_closed: bool = False          # R7: ended by the firm's household rule (multi-firm D-30)
    ftp_closed: bool = False                # D-495 (4): ended by the Focused Trader Program's Corrective Path
    ftp_denied: int = 0                     # D-495 (4): pending payouts the Corrective Path denied

    @property
    def given_back(self) -> float:
        """D-384: the secured balance given back -- the highest close before the first payout less the balance at that
        payout, or at the end for an XFA never paid (never below zero)."""
        end = self.balance_at_first_payout if self.n_payouts > 0 else self.balance
        return max(0.0, float(self.peak_before_payout) - float(end))


def _sizing_of(draw: Any) -> dict[str, Any] | None:
    stats = getattr(draw, "stats", None)
    as_dict = getattr(stats, "as_dict", None)
    return as_dict() if callable(as_dict) else None


@dataclass(frozen=True)
class LockstepPath:
    """One lockstep campaign: the campaign-level record plus every account's final state."""

    path: CampaignPath
    combines: tuple[CombineRecord, ...]
    funded: tuple[FundedRecord, ...]
    breaches_per_day: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=int))
    # accounts (Combine or funded) that hit the loss limit on each calendar day (D-30)
    trades: tuple[dict[str, Any], ...] = ()     # the per-trade ledger, when recorded (D-130)
    conduct: dict[str, Any] = field(default_factory=dict)   # D-145 state and pattern measures; empty when off
    # D-146 daily recorder, when on: one row per live account per trading day, and one row per
    # calendar day of campaign cash flows by type. Empty when off.
    account_days: tuple[dict[str, Any], ...] = ()
    campaign_days: tuple[dict[str, Any], ...] = ()
    # R7 (multi-firm D-30): a funded class with a household rule (Lucid's) records its events here -- the reading, the
    # accounts that reached the rule's trigger, the close it ended the household on, and what it ended. Empty otherwise.
    household: dict[str, Any] = field(default_factory=dict)
    # D-495 (4): the Focused Trader Program's model, its placements (day, path, the measure that crossed, what a
    # Corrective placement closed and denied) and the pattern measures' maxima. Empty when off.
    focused_trader: dict[str, Any] = field(default_factory=dict)
    # D-501: the self-imposed purchase budget -- K Combine purchases and resets in any `window_days` trading days -- and
    # what it refused. Empty when off.
    purchase_budget: dict[str, Any] = field(default_factory=dict)
    # D-630: the three entry options, each the campaign's own restraint on buying evaluations and each empty when off --
    # `wallet_stop` (no purchase while the cash out of pocket is above W), `pause_after_funded` (none at a purchase
    # step where the campaign holds F funded accounts and its first payout has not arrived; D-632's wording) and
    # `seat_ramp` (s0 seats at first, one more for each payout arrived, up to the base's) -- and what each refused.
    wallet_stop: dict[str, Any] = field(default_factory=dict)
    pause_after_funded: dict[str, Any] = field(default_factory=dict)
    seat_ramp: dict[str, Any] = field(default_factory=dict)


def _record_combine(c: CombineAccount) -> CombineRecord:
    return CombineRecord(
        index=c.index, purchase_day=c.purchase_day, resolved_on=c.resolved_on,
        passed=c.passed, failed=c.failed, unresolved=c.unresolved, abandoned=c.abandoned,
        pass_day=c.pass_day, fail_day=c.fail_day, days=c.days, trades=c.trades,
        balance=float(c.B), floor=float(c.F), subscriptions_paid=c.subs_paid,
        sizing=_sizing_of(c.draw), resets=c.resets, reset_days=tuple(c.reset_days), dll=c.dll, rtp=c.rtp,
        out_of_room=c.out_of_room, abandoned_by_policy=c.abandoned_by_policy, household_closed=c.household_closed,
        ftp_closed=c.ftp_closed,
    )


def _record_funded(a: FundedAccount) -> FundedRecord:
    return FundedRecord(
        index=a.index, activation_day=a.activation_day, ended_on=a.ended_on, closed=a.closed,
        days=a.days, trades=a.trades, balance=float(a.B), floor=float(a.F),
        n_payouts=a.n_payouts, first_payout_day=a.first_payout_day,
        payout_days=tuple(a.payout_days), payout_cash=tuple(a.payout_cash),
        gross_paid=float(a.gross_paid), cash=float(a.cash),
        sizing=_sizing_of(a.draw), denied=a.denied, dll=a.dll, combine_index=a.combine_index,
        combine_purchase_day=a.combine_purchase_day, consistency_forced=a.policy_override is not None,
        abandoned=a.abandoned, flips=int(a.flips), flips_won=int(a.flips_won),
        second_trades=int(a.second_trades), second_qualified=int(a.second_qualified),
        collect_trades=int(a.collect_trades), collect_qualified=int(a.collect_qualified),
        peak_before_payout=float(a.peak_before_payout), balance_at_first_payout=float(a.balance_at_first_payout),
        household_closed=a.household_closed, ftp_closed=a.ftp_closed, ftp_denied=int(a.ftp_denied),
    )


# ------------------------------------------------------------------ default draws (binary)


def session_slots(trades_per_day: int, max_trades: int | None, *, waits: bool = True) -> int:
    """An account's trade slots this session: the protocol's, limited by its state's `max_trades` (D-162). A state with
    no trade (0) holds the account only where it `waits` -- D-324 (the v7 audit, finding 1): a policy's no-trade states
    are the Standard path's (the table is solved for it, and it waits there for a payout that path pays at the close or
    sits out the request day); an account on another payout path would wait for ever, so it trades the state's action
    (one slot) instead."""
    tpd = int(trades_per_day)
    if max_trades is None or int(max_trades) >= tpd:
        return tpd
    mt = int(max_trades)
    if mt == 0 and not waits:
        mt = 1
    return min(mt, tpd)


def _takes_caps(hook: Any) -> bool:
    """Whether a day hook accepts a third argument, each account's trade limit (D-162); older hooks take two."""
    if hook is None:
        return False
    import inspect

    try:
        params = inspect.signature(hook).parameters
    except (TypeError, ValueError):
        return False
    return "caps" in params or len(params) >= 3


def _takes_states(hook: Any) -> bool:
    """Whether a day hook accepts a fourth argument, each account's balance and loss-limit floor at the start of the
    session (D-205); hooks written before take two or three."""
    if hook is None:
        return False
    import inspect

    try:
        params = inspect.signature(hook).parameters
    except (TypeError, ValueError):
        return False
    return "states" in params or len(params) >= 4


def _takes_flips(hook: Any) -> bool:
    """Whether a day hook accepts a fifth argument, the day's flips (D-339: (account, start, end, direction) per
    flip-state account), so the router can place them among the log's trades for the cross-account rule."""
    if hook is None:
        return False
    import inspect

    try:
        params = inspect.signature(hook).parameters
    except (TypeError, ValueError):
        return False
    return "flips" in params or len(params) >= 5


def _takes_rrs(hook: Any) -> bool:
    """Whether a day hook accepts a sixth argument, each account's R for the session (D-349: the table's decision, else
    the leg's), so the router can hold a routed position to its exit at that R."""
    if hook is None:
        return False
    import inspect

    try:
        params = inspect.signature(hook).parameters
    except (TypeError, ValueError):
        return False
    return "rrs" in params or len(params) >= 6


def _takes_seconds(hook: Any) -> bool:
    """D-368: whether a day hook accepts a seventh argument, the accounts allowed a second trade today with their
    risk, R and the winning-day minimum, so the router hands one only after a first that fell short of it."""
    if hook is None:
        return False
    import inspect

    try:
        params = inspect.signature(hook).parameters
    except (TypeError, ValueError):
        return False
    return "seconds" in params or len(params) >= 7


def _takes_collect(hook: Any) -> bool:
    """D-368: whether a day hook accepts an eighth argument, the accounts in the collect phase today with the
    winning-day minimum, so the router asks each one whether it would bracket a signal at it and holds the position to
    the latest exit the trade carries."""
    if hook is None:
        return False
    import inspect

    try:
        params = inspect.signature(hook).parameters
    except (TypeError, ValueError):
        return False
    return "collect" in params or len(params) >= 8


def child_seed(seed: int, kind: int, index: int) -> int:
    """A reproducible per-account seed from the path seed, the account kind and its index."""
    return int(np.random.default_rng([int(seed), int(kind), int(index)]).integers(0, 2**31 - 1))


def binary_draw_factories(
    protocol: Protocol, edge: float, seed: int, rules: Any
) -> tuple[DrawFactory, DrawFactory]:
    """Independent binary draws per account -- the validation limit, through the engine's own
    `RandomDraw` (via `adapter.BinaryDraw`) so the floor barrier race and the drift solve are
    the engine's."""
    from propedge.contract.adapter import BinaryDraw

    combine_policy = protocol.combine_policy()
    funded_policy = protocol.funded_policy()

    def combine(index: int, start_day: int):
        return BinaryDraw(combine_policy, edge, child_seed(seed, 1, index), rules)

    def funded(index: int, start_day: int):
        return BinaryDraw(funded_policy, edge, child_seed(seed, 2, index), rules)

    return combine, funded


def binary_flip_for_path(risk: float, rr: float, edge: float, risk_per_contract: float | None = None,
                         p_scratch: float = 0.0, copy: bool = False) -> Callable[[int], tuple]:
    """D-339: the flip stream in the engine's own binary campaign (the state table's campaign check, D-290 (8)) -- the
    table's model of the flip: a bracket at `risk` and `rr` won with p = (1 + edge / (1 - p_scratch)) / (1 + rr) on the
    attempts that resolve (stage one's binary process, propsim D-06), a scratch worth nothing on the rest (D-343), no
    cost (the edge carries it), raced against the room as any trade; `copy` shares the day's outcome across the funded
    accounts. Returns `flip_for_path(path_seed) -> (flip_draw_factory, spec)` for
    `simulate_lockstep_campaign(flip_for_path=...)`; each account's draw is seeded from the path seed and its index
    (or one seed for all under `copy`), so the check is reproducible."""
    from propedge.campaign.flip import FlipDraw, FlipSpec

    if not 0.0 <= float(p_scratch) < 1.0:
        raise ValueError("the scratch share lies in [0, 1)")
    p = (1.0 + float(edge) / (1.0 - float(p_scratch))) / (1.0 + float(rr))
    if not 0.0 < p < 1.0:
        raise ValueError(f"the flip's binary win probability must lie in (0, 1); edge {edge} at {rr}R gives {p}")
    live = 1.0 - float(p_scratch)
    spec = FlipSpec(risk=float(risk), rr=float(rr), p_target=live * p, p_stop=live * (1.0 - p), p_open=0.0, cost_r=0.0,
                    risk_per_contract=float(risk if risk_per_contract is None else risk_per_contract),
                    slots=(0,), mean_minutes=1.0, edge=float(edge), p_scratch=float(p_scratch), copy=bool(copy),
                    source="the table's binary model (D-339, D-343)")

    def flip_for_path(path_seed: int) -> tuple:
        return (lambda index, start_day: FlipDraw(spec, seed=child_seed(path_seed, _KIND_FLIP_BINARY,
                                                                          0 if spec.copy else index))), spec

    return flip_for_path


def binary_flip_menu_for_path(flips: Sequence[tuple], copy: bool = False) -> Callable[[int], tuple]:
    """D-384: `binary_flip_for_path` for a menu of brackets -- each (risk, R, edge, scratch share) as the table priced
    it, one binary spec each, one `FlipMenu`; every account's draw shares the day's uniform under `copy`."""
    from propedge.campaign.flip import FlipDraw, FlipMenu

    specs = []
    for f in flips:
        sc = float(f[3]) if len(f) > 3 else 0.0
        _, spec = binary_flip_for_path(float(f[0]), float(f[1]), float(f[2]), None, p_scratch=sc, copy=copy)(0)
        specs.append(spec)
    menu = FlipMenu(tuple(specs))

    def flip_for_path(path_seed: int) -> tuple:
        return (lambda index, start_day: FlipDraw(menu, seed=child_seed(path_seed, _KIND_FLIP_BINARY,
                                                                          0 if menu.copy else index))), menu

    return flip_for_path


# ------------------------------------------------------------------------- the path


def check_purchase_budget(purchase_budget: Any) -> tuple[int, int]:
    """D-501: a purchase budget `(K, window_days)` as two whole numbers of at least 1; (0, 0) for None (off)."""
    if purchase_budget is None:
        return 0, 0
    try:
        k, w = purchase_budget
    except (TypeError, ValueError):
        raise ValueError(f"purchase_budget is (K, window_days), got {purchase_budget!r}") from None
    if isinstance(k, bool) or isinstance(w, bool) or int(k) != k or int(w) != w or int(k) < 1 or int(w) < 1:
        raise ValueError(f"purchase_budget's K and window_days must be whole numbers of at least 1, got "
                         f"{purchase_budget!r}")
    return int(k), int(w)


def check_wallet_stop(wallet_stop: Any) -> float | None:
    """D-630 (a): a wallet stop W as a finite number of dollars, zero or more; None for None (off)."""
    if wallet_stop is None:
        return None
    if isinstance(wallet_stop, bool) or not isinstance(wallet_stop, (int, float, np.integer, np.floating)):
        raise ValueError(f"wallet_stop is a number of dollars, got {wallet_stop!r}")
    w = float(wallet_stop)
    if not math.isfinite(w) or w < 0:
        raise ValueError(f"wallet_stop must be a finite number of dollars, zero or more, got {wallet_stop!r}")
    return w


def _whole_at_least_one(value: Any, name: str) -> int:
    if (isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating))
            or not math.isfinite(float(value)) or int(value) != value or int(value) < 1):
        raise ValueError(f"{name} must be a whole number of at least 1, got {value!r}")
    return int(value)


def check_pause_after_funded(pause_after_funded: Any) -> int | None:
    """D-630 (b), as D-632 words it: the funded accounts F at or above which no Combine is bought before the first
    payout arrives, a whole number of at least 1; None for None (off)."""
    if pause_after_funded is None:
        return None
    return _whole_at_least_one(pause_after_funded, "pause_after_funded")


def check_seat_ramp(seat_ramp: Any, max_total_accounts: Any) -> int | None:
    """D-630 (c): the seats s0 a campaign starts with, a whole number of at least 1; None for None (off). The ramp ends
    at the base's own seats, so it needs the base's joint cap (`max_total_accounts`): refused without one."""
    if seat_ramp is None:
        return None
    s0 = _whole_at_least_one(seat_ramp, "seat_ramp")
    if max_total_accounts is None:
        raise ValueError("seat_ramp needs the base's joint cap (max_total_accounts; the gate's total_accounts): the "
                         "ramp runs up to the base's own seats and the three seat limits move together (D-630)")
    return s0


def simulate_lockstep_path(
    protocol: Protocol,
    *,
    edge: float,
    seed: int,
    rules: Any,
    initial_bankroll: float,
    horizon_days: int,
    max_concurrent_accounts: int,
    subscription: float,
    billing_days: int,
    activation: float,
    payout_lag_days: int,
    max_concurrent_combines: int = 1,
    reinvest: bool = True,
    max_attempts: int | None = None,
    stop_buying_when_queued: bool = True,
    activation_timing: str = ACTIVATION_ON_ACTIVATION,
    combine_max_days: int = 2000,
    funded_horizon_days: int = 504,
    combine_draw_factory: DrawFactory | None = None,
    funded_draw_factory: DrawFactory | None = None,
    day_hook: DayHook | None = None,
    record_trades: bool = False,
    conduct: ConductModel | None = None,
    record_days: bool = False,
    near_miss_frac: float = 0.2,
    reset_failed_combines: bool = False,
    reset_fee: float | None = None,
    risk_policy: Any = None,
    max_total_accounts: int | None = None,
    payout_timing: str = DEFAULT_PAYOUT_TIMING,
    wallet: Any = None,
    flip_draw_factory: Callable[[int, int], Any] | None = None,
    flip: Any = None,
    funded_account_cls: type | None = None,
    household_closure: bool | None = None,
    focused_trader: FocusedTraderModel | None = None,
    purchase_budget: tuple[int, int] | None = None,
    combine_account_cls: type | None = None,
    wallet_stop: float | None = None,
    pause_after_funded: int | None = None,
    seat_ramp: int | None = None,
) -> LockstepPath:
    """Simulate one campaign, stepping every live account through each calendar day.

    D-619: `combine_account_cls` is the evaluation account's class -- a subclass of `CombineAccount` for another
    contract's evaluation (`propedge.research.hedge_cycle.StaticCombineAccount`, a HYPOTHETICAL firm's green-day pass
    rule); None is `CombineAccount`, Topstep's, exactly as before.

    D-495 (4): `focused_trader` is Topstep's Focused Trader Program (`FocusedTraderModel`, article 10551016) as a
    campaign-level event: the declared pattern measures watched over a rolling window and, once one reaches its
    declared threshold, the declared path's placement -- Slowdown (no purchases or resets, then one account at a time)
    or Corrective (every account closed at that close, pending payouts denied, one account at a time for six months).
    None (the default) runs none of it, exactly as before; a model whose thresholds are never reached leaves the path
    identical to None. `LockstepPath.focused_trader` records the model, every placement and the measures' maxima.
    Topstep's program: refused with another firm's funded class.

    D-501: `purchase_budget=(K, window_days)` is a self-imposed restraint, the campaign's own (no firm rule): a Combine
    purchase or a reset is refused while the campaign's Combine purchases and resets in the last `window_days` trading
    days (that day included, its purchases so far counted) have reached K; a refused reset ends the Combine as a
    failure, as any refused reset does; purchases resume as the window rolls. None (the default) runs none of it,
    exactly as before. `LockstepPath.purchase_budget` records the budget, the purchases and resets taken, their
    rolling maximum, the days a purchase was refused by the budget alone and the resets it refused.

    D-630: three more restraints of the campaign's own on buying evaluations (no firm rule), each None (the default)
    for off, exactly as before, and each a condition of the purchase step beside the budget's -- a purchase is made
    only when every condition allows it. (a) `wallet_stop=W`: no Combine is bought while the cash out of pocket
    (`initial_bankroll` less the cash at that moment, read before each purchase) is above W dollars; subscriptions
    already running and activation fees are paid as before. (b) `pause_after_funded=F` (D-632's wording; no latch):
    no Combine is bought at a purchase step where the campaign holds at least F funded accounts (activated and not
    ended, counted after that evening's activations) and its first payout has not yet ARRIVED (the cash received,
    `payout_lag_days` after the request); when it holds fewer than F, purchases are as the base's -- the condition is
    read again at every purchase step -- and once the first payout has arrived the option never binds again; open
    Combines keep trading and their passes are activated as before. (c) `seat_ramp=s0`: the
    campaign holds at most s0 accounts of both kinds together (running Combines, funded accounts, passes waiting) and
    one more for each payout that has arrived, up to the base's `max_total_accounts`, which it needs; the funded and
    the Combine limits follow, since neither count can pass the total. As with the budget (D-502) a reset counts with
    the purchases under (a) and (b) -- a refused reset ends its Combine as a failure -- while (c) never refuses one (a
    reset keeps a seat already held). `LockstepPath.wallet_stop`, `.pause_after_funded` and `.seat_ramp` record each
    option, the days it alone refused a purchase and the resets it refused; the pause's record also counts the
    purchase steps at which its condition held, their separate spells, and the days purchases resumed because the
    funded accounts held fell below F.

    R7 (docs/TWO_FIRMS.md): `funded_account_cls` is the funded account's class -- a subclass of `FundedAccount` for
    another firm's funded contract (`propedge.contract.lucid.LucidFundedAccount`); None is `FundedAccount`, Topstep's,
    exactly as before.

    R7 (the multi-firm repository's D-30; docs/TWO_FIRMS.md): `household_closure` applies a funded class's household
    rule. A class that has one says so with `HOUSEHOLD_CLOSES_AT_LIVE` (its default reading) and raises
    `closes_household` on the account that triggers it (Lucid: the account took its fifth payout and the household
    enters the live review pool, 12945796, 16558826). With the rule on, the first account to raise it at a close ends
    every other live account of this campaign at that close (`close_household`: no breach, nothing of a balance
    credited; payouts already requested still arrive), a pass waiting for a seat or made that day is never activated,
    and the path buys nothing more. None takes the class's default; False only counts the triggers (the optimistic
    reading). `LockstepPath.household` records the reading and the counts. A class without the rule (Topstep's) records
    nothing and refuses True.

    D-339: `flip_draw_factory(index, activation_day)` gives each funded account its flip draw and `flip` is the
    `FlipSpec` (the slots and the window the router reads); a policy decision whose source is 'flip' then draws the
    account's own bracket that session instead of a routed signal.

    Arguments match `reinvest.simulate_path` where they overlap, with the same meaning. The
    additions:

    Args:
        rules: engine `Rules` (the contract). Pass `rules_from_ledger()` for a research run;
            `Rules()` is stage one's defaults, for validation.
        combine_max_days: trading days after which an unresolved Combine ends without a pass,
            as the engine's `max_days`; it then frees nothing and buys nothing.
        funded_horizon_days: trading days after which a funded account is closed out, as the
            attempt pool's fixed funded horizon. Inherited from the stage-level model so the
            two agree; a later slice may let a funded account live to the campaign horizon.
        combine_draw_factory / funded_draw_factory: `factory(index, start_day) -> draw`; None
            uses independent binary draws at `edge` (`binary_draw_factories`).
        day_hook: called before any account trades on a day with the live accounts in
            rotation order (earliest start first, funded before Combine on a tie, then index);
            `shared_days.SharedDayDraws.day_hook` under `rotation` mode. None otherwise.
        record_trades: keep the per-trade ledger on the result (`LockstepPath.trades`).
        conduct: D-145's tiers 2 and 3 (`ConductModel`); None runs neither, exactly as before.
        record_days: D-146's daily recorder (`LockstepPath.account_days`, `campaign_days`).
            Reads state only; the path is identical with it on or off.
        near_miss_frac: the recorder's near-miss threshold, a declared value: a session that
            closes with less than this share of the MLL left above the floor, without breaching,
            is an MLL near-miss; a daily-loss-limited session that loses more than (1 - this)
            of the limit without reaching it is a daily-loss near-miss.
        reset_failed_combines: D-146: a Combine that hits the loss limit is reset for
            `reset_fee` (the verified `reset_fee` on `rules` if None) and trades again from the
            next session, keeping its subscription; when the bankroll cannot pay the fee it ends
            as a failure. Off by default: a failure is replaced by a new purchase (D-34).
        risk_policy: D-147: a `propedge.campaign.risk_policy.RiskPolicy`. At the start of every
            account's session the policy reads the account's state (phase, balance, cushion to
            the MLL, days in state) and sets the session's dollar risk (and R, where the draw
            can honour it) through the draw's `set_risk`; every ledger row and every recorded
            account-day carries the decision (policy, regime, inputs, risk, R). None keeps each
            leg's fixed risk, exactly as before; `RiskPolicy.from_protocol` reproduces it too.
        max_total_accounts: a cap on live accounts of both kinds together -- running Combines,
            funded accounts and passes waiting for a slot; a Combine is bought only while the
            total is below it (D-34's "at most 5 concurrent accounts including Combines"). With
            the cap at or below the funded cap a pass never waits. None: no joint cap, as before.
        payout_timing: when a funded account requests its payout (8284233,
            `propedge.contract.payout_timing`). The default, `REQUEST_AFTER_5PM`, is the rule for a
            request made after 5:00 PM CT: the next trading day is the Payout request day and does
            not count toward the new cycle. `REQUEST_4_TO_5PM` is the engine's old timing and
            requires the operator to submit between 4:00 and 5:00 PM CT on the eligible day. Either
            way the balance and the MLL change at the request, before the next session, and the
            payout is dated on the eligible day.
        wallet: D-206: a cash pot shared with another campaign, any object with a `cash` attribute. The path
            starts from `wallet.cash` instead of `initial_bankroll`, hands its cash to the wallet just before
            each call of `day_hook` and takes it back just after, and leaves its final cash there; the campaigns
            sharing it must take turns between their hooks (the hook is where they meet). None: the path's own
            cash, exactly as before.
    """
    check_payout_timing(payout_timing)
    combine_cls = CombineAccount if combine_account_cls is None else combine_account_cls  # D-619
    if not (isinstance(combine_cls, type) and issubclass(combine_cls, CombineAccount)):
        raise TypeError(f"combine_account_cls must be CombineAccount or a subclass of it, got {combine_account_cls!r}")
    funded_cls = FundedAccount if funded_account_cls is None else funded_account_cls      # R7
    if not (isinstance(funded_cls, type) and issubclass(funded_cls, FundedAccount)):
        raise TypeError(f"funded_account_cls must be FundedAccount or a subclass of it, got {funded_account_cls!r}")
    household_rule = hasattr(funded_cls, "HOUSEHOLD_CLOSES_AT_LIVE")                       # R7 (multi-firm D-30)
    if household_closure and not household_rule:
        raise ValueError(f"{funded_cls.__qualname__} has no household rule: household_closure=True applies only to a "
                         "funded class that declares one (HOUSEHOLD_CLOSES_AT_LIVE)")
    household_on = household_rule and bool(
        funded_cls.HOUSEHOLD_CLOSES_AT_LIVE if household_closure is None else household_closure)
    budget_k, budget_w = check_purchase_budget(purchase_budget)                              # D-501
    wallet_w = check_wallet_stop(wallet_stop)                                                # D-630 (a)
    pause_f = check_pause_after_funded(pause_after_funded)                                   # D-630 (b)
    ramp_s0 = check_seat_ramp(seat_ramp, max_total_accounts)                                 # D-630 (c)
    ftp = focused_trader                                                                     # D-495 (4)
    if ftp is not None:
        if not isinstance(ftp, FocusedTraderModel):
            raise TypeError(f"focused_trader must be a FocusedTraderModel, got {type(ftp).__name__}")
        if funded_cls is not FundedAccount:
            raise ValueError("the Focused Trader Program is Topstep's (10551016): it applies to Topstep's FundedAccount "
                             f"only, not {funded_cls.__qualname__}")
    if risk_policy is not None:
        risk_policy.validate()
    if activation_timing not in ACTIVATION_TIMINGS:
        raise ValueError(
            f"activation_timing must be one of {ACTIVATION_TIMINGS}, got {activation_timing!r}"
        )
    on_pass = activation_timing == ACTIVATION_ON_PASS
    if combine_draw_factory is None or funded_draw_factory is None:
        default_c, default_f = binary_draw_factories(protocol, edge, seed, rules)
        combine_draw_factory = combine_draw_factory or default_c
        funded_draw_factory = funded_draw_factory or default_f

    combine_policy = protocol.combine_policy()
    funded_policy = protocol.funded_policy()
    cap = rules.std_cap if funded_policy.payout_path == "standard" else rules.cons_cap
    hook_takes_caps = _takes_caps(day_hook)       # D-162: a hook that accepts each account's trade limit
    hook_takes_states = hook_takes_caps and _takes_states(day_hook)   # D-205: and each account's balance and floor
    hook_takes_flips = hook_takes_states and _takes_flips(day_hook)   # D-339: and the day's flips
    hook_takes_rrs = hook_takes_flips and _takes_rrs(day_hook)        # D-349: and each account's R for the session
    hook_takes_seconds = hook_takes_rrs and _takes_seconds(day_hook)  # D-368: and the accounts allowed a second trade
    hook_takes_collect = hook_takes_seconds and _takes_collect(day_hook)   # D-368: and the accounts collecting
    if flip is not None and flip_draw_factory is None:
        raise ValueError("a flip stream needs a flip draw factory (D-339)")
    seat_frees = str((getattr(protocol, "params", None) or {}).get("seat_frees", "next_session"))   # D-339
    if seat_frees not in ("next_session", "same_evening"):
        raise ValueError(f"seat_frees is 'next_session' or 'same_evening', got {seat_frees!r}")
    seat_same_evening = seat_frees == "same_evening"
    flip_rng = np.random.default_rng(child_seed(seed, _KIND_FLIP_DIRECTION, 0)) if flip is not None else None

    cash = float(initial_bankroll) if wallet is None else float(wallet.cash)   # D-206: a shared pot
    peak_cash = cash
    max_dd = 0.0

    running: list[CombineAccount] = []
    funded: list[FundedAccount] = []
    queue: list[CombineAccount] = []
    pending: list[tuple[int, float, FundedAccount]] = []     # (arrival day, amount, account)
    finished_combines: list[CombineAccount] = []
    finished_funded: list[FundedAccount] = []
    finished_trades, n_finished_c, n_finished_f = 0, 0, 0      # R11: the finished accounts' trades, kept as a total
    capped_memo: dict = {}                                     # R11: `_capped`'s protocols, one per (protocol, limit)

    cash_series = np.zeros(horizon_days, dtype=float)
    active_series = np.zeros(horizon_days, dtype=int)
    breaches_per_day = np.zeros(horizon_days, dtype=int)
    trades_by_day = np.zeros(horizon_days, dtype=int)     # D-305: executed trades across every account, per day
    trades_so_far = 0
    # D-306: the protocol declares need-aware Combine exits in its params; a draw that cannot honour them is unchanged
    need_aware = bool((getattr(protocol, "params", None) or {}).get("need_aware_exits", False))
    # D-313: and the Combine's consistency-capped exits (a day never lifts the target when the pass cannot be taken)
    consistency_cap = bool((getattr(protocol, "params", None) or {}).get("consistency_cap_exits", False))
    # D-324: a policy's no-trade states hold only Standard-path funded accounts (`_capped` below)
    standard_waits_only = bool((getattr(protocol, "params", None) or {}).get("no_trade_standard_path_only", False))
    # D-328: the policy's dollar inputs read to the cent, as the firm's ledger carries them
    decision_cents = bool((getattr(protocol, "params", None) or {}).get("decision_inputs_cents", False))
    # D-368: an XFA collecting Standard-path winning days may take a second trade after a first that left the day short
    xfa_second = bool((getattr(protocol, "params", None) or {}).get("xfa_second_trade", False))
    # D-368: the collect phase -- an XFA collecting Standard-path winning days whose balance has reached this many dollars
    # above its start trades at the fresh funded leg's dollar risk with a take-profit at the shortfall to the minimum
    collect_from = (getattr(protocol, "params", None) or {}).get("xfa_collect_from")
    collect_from = None if collect_from is None else float(collect_from)
    if collect_from is not None and xfa_second:
        raise ValueError("xfa_collect_from and xfa_second_trade together are not defined (D-368): test them apart")

    ruined = False
    ruin_day: int | None = None
    attempts_started = 0
    accounts_funded = 0
    accounts_ever_paid = 0
    total_fees = 0.0
    total_payouts = 0.0
    peak_queue = 0
    passes_forfeited = 0
    combines_abandoned = 0
    combines_out_of_room = 0                      # D-318
    combines_abandoned_by_policy = 0              # D-329: attempts the policy cancelled
    funded_abandoned = 0                          # D-329: XFAs the policy closed
    passes_on_hold_at_end = 0
    multi_breach_days = 0
    max_breached = 0
    payout_days_campaign: list[int] = []
    ledger: list[dict[str, Any]] | None = [] if record_trades else None

    # D-145 state. Nothing below reads it when `conduct` is None.
    rtp_day: int | None = None                 # the day RTP placement took effect from the next day
    rtp_trigger = ""
    rtp_warning_days: list[int] = []           # trigger days answered by a warning (D-220)
    enforce_rng = (np.random.default_rng(child_seed(seed, _KIND_ENFORCEMENT, 0))
                   if conduct is not None else None)
    payouts_requested = payouts_exposed = payouts_denied = 0
    purchase_days: list[int] = []
    rtp_policy = None
    if conduct is not None and conduct.rtp:
        from dataclasses import replace as _replace
        rtp_policy = _replace(funded_policy, payout_path="consistency")

    def _rtp_dll_on(d: int) -> float | None:
        # The RTP daily loss limit for an account bought, reset or activated on calendar day `d`: placement decided
        # at a day's close applies from the next day (13620045: "All new Trading Combines® and XFAs automatically
        # get a Daily Loss Limit (DLL)"; "If Reset, the new Trading Combine will follow RTP rules").
        if conduct is not None and rtp_day is not None and d > rtp_day:
            return float(conduct.rtp_dll)
        return None

    # D-146 state. The fee arrays are cheap and always kept; rows are built only when recording.
    fee_sub = np.zeros(horizon_days)
    fee_act = np.zeros(horizon_days)
    fee_reset = np.zeros(horizon_days)
    pay_in = np.zeros(horizon_days)
    account_days: list[dict[str, Any]] = []
    the_reset_fee = float(getattr(rules, "reset_fee", 0.0) if reset_fee is None else reset_fee)
    resets_taken = 0
    # R7 (multi-firm D-30): the household rule's state; read only when the funded class has the rule.
    household_closed_on: int | None = None
    household_triggers = household_combines = household_funded = household_passes = 0
    # D-495 (4): the Focused Trader Program's state; nothing below reads it when `focused_trader` is None.
    ftp_bought = np.zeros(horizon_days, dtype=int)        # Combine purchases and resets, per day
    ftp_lost = np.zeros(horizon_days, dtype=int)          # funded accounts lost (breach, closure at request, denial)
    ftp_placed: dict[str, Any] | None = None              # the placement in force
    ftp_until: int | None = None                          # Corrective: the last day of its limit
    ftp_watch_from = 0                                    # the measures count from this day (after a program ended)
    ftp_done = False                                      # a program ended and `repeat` is off: nothing more watched
    ftp_placements: list[dict[str, Any]] = []
    ftp_blocked_days = ftp_resets_refused = 0
    # D-501: the purchase budget's state; nothing below reads it when `purchase_budget` is None.
    budget_on = purchase_budget is not None
    budget_bought = np.zeros(horizon_days, dtype=int)     # Combine purchases and resets, per day
    budget_blocked_days = budget_resets_refused = 0

    def _budget_spent(d: int) -> bool:
        # D-501: the purchases and resets in the last `budget_w` trading days (day d included) have reached K
        return budget_on and int(budget_bought[max(0, d - budget_w + 1):d + 1].sum()) >= budget_k

    # D-630: the three entry options' state; nothing below reads it when all three are None.
    entry_on = wallet_w is not None or pause_f is not None or ramp_s0 is not None
    start_bankroll = float(initial_bankroll)              # (a): the cash out of pocket is this less the cash
    wallet_blocked_days = wallet_resets_refused = 0
    wallet_first_blocked = wallet_final = -1
    wallet_max_out = 0.0                                  # the most out of pocket just before a purchase or reset taken
    pause_first = -1                                      # (b): the first day the pause refused a purchase or a reset
    pause_in_force = pause_now = False                    # its condition at the last purchase step; at today's resets
    pause_blocked_days = pause_resets_refused = 0
    pause_days = pause_spells = 0                         # purchase steps at which the condition held; their spells
    pause_resumed: list[int] = []                         # days it stopped holding because fewer than F were held
    ramp_base = int(max_total_accounts) if ramp_s0 is not None else 0
    ramp_blocked_days = 0
    ramp_first_blocked = -1
    ramp_full_on = (0 if ramp_s0 >= ramp_base else -1) if ramp_s0 is not None else -1

    def _entry_refusals(cash_now: float, held: int, paused: bool, arrived: int) -> tuple[bool, bool, bool]:
        # D-630: which options refuse a purchase now -- (a) the cash out of pocket above W, (b) the pause's condition,
        # (c) the accounts held at the ramp's seats (s0 and one more for each payout arrived)
        return (wallet_w is not None and start_bankroll - cash_now > wallet_w,
                paused,
                ramp_s0 is not None and held >= ramp_s0 + arrived)

    if cash < subscription:
        cash_series[:] = cash
        return LockstepPath(
            path=CampaignPath(
                final_cash=cash, initial_bankroll=float(initial_bankroll),
                cash_series=cash_series, active_funded_series=active_series,
                ruined=True, ruin_day=0, max_drawdown=0.0, max_drawdown_frac=0.0,
                attempts_started=0, accounts_funded=0, accounts_ever_paid=0,
                days_to_first_payout=None, payout_gaps=(), total_fees=0.0,
                total_payouts=0.0, peak_queue_length=0,
            ),
            combines=(), funded=(), breaches_per_day=breaches_per_day,
        )

    for day in range(horizon_days):
        # D-495 (4): a Corrective placement's limit ends after its trading days; the program ends and, with `repeat`,
        # the measures are watched again from today. A placement made at a close binds from the next day.
        if ftp_placed is not None and ftp_until is not None and day > ftp_until:
            ftp_placed["ended_on"] = int(ftp_until)
            ftp_placed, ftp_until, ftp_watch_from = None, None, day
            ftp_done = not ftp.repeat
        ftp_in_force = ftp_placed is not None
        ftp_no_resets = ftp_in_force and ftp_placed["path"] == FTP_SLOWDOWN
        # 1. subscriptions due at the start of the day. Engine day 0 is the day after purchase,
        #    so the k-th rebill (engine day k * billing_days) falls on purchase + 1 + k * billing_days.
        keep: list[CombineAccount] = []
        for c in running:
            elapsed = day - c.purchase_day
            due = 1 + max(0, (elapsed - 1) // billing_days)
            alive = True
            while c.subs_paid < due:
                if cash < subscription:
                    alive = False
                    combines_abandoned += 1
                    break
                cash -= subscription
                total_fees += subscription
                fee_sub[day] += subscription
                c.subs_paid += 1
            if alive:
                keep.append(c)
            else:
                c.abandoned = True
                c.resolved_on = day
                finished_combines.append(c)
        running = keep

        # 2. every live account trades today's session and locks at 16:00 CT. A draw that
        #    sizes from the tier reads the balance at the start of the session (D-53; the tier
        #    is fixed within a session) through `begin_session`; other draws have no such hook.
        #    Under rotation the router is told, first, which accounts are live today and in
        #    what order (earliest start first, funded before Combine on a tie, then index).
        trading_c = [c for c in running if day >= c.start_day and c.alive]
        trading_f = [a for a in funded if day >= a.start_day and a.alive and a.ended_on is None]

        def _decide(acct: Any, kind: str) -> None:
            # D-147: the policy reads the account's state at the start of the session.
            if risk_policy is None:
                return
            from propedge.campaign.risk_policy import account_state

            dec = risk_policy.decide(account_state(acct, kind=kind, day=day, cents=decision_cents))
            if getattr(dec, "abandon", False):                    # D-329: nothing to size; the account ends below
                acct.decision = dec
                return
            if getattr(dec, "source", "strategy") == "flip":      # D-339: the account's own bracket today, no signal
                if kind != "funded" or getattr(acct, "flip_draw", None) is None:
                    raise ValueError("a flip decision needs a funded account with a flip draw (D-339)")
                acct.flip_today = True
                acct.flip_draw.set_risk(dec.risk, dec.rr)
                acct.decision = dec
                return
            setr = getattr(acct.draw, "set_risk", None)
            if setr is None:
                raise ValueError(
                    f"a risk policy needs a draw that can change its risk; {type(acct.draw).__name__} "
                    "cannot (use the binary draws or SharedDayDraws)"
                )
            setr(dec.risk, dec.rr)
            acct.decision = dec

        def _stamp(acct: Any, n0: int) -> None:
            if ledger is not None and acct.decision is not None:
                row = acct.decision.as_row()
                for r in ledger[n0:]:
                    r.update(row)

        def _capped(pol: Any, acct: Any) -> Any:
            # D-162: the session's trade slots, limited by the state's `max_trades` when the policy sets one.
            dec = acct.decision if risk_policy is not None else None
            if dec is None or dec.max_trades is None or int(dec.max_trades) >= int(pol.trades_per_day):
                return pol
            waits = not (standard_waits_only and getattr(acct, "policy_override", None) is not None)
            mt = session_slots(int(pol.trades_per_day), dec.max_trades, waits=waits)
            if mt >= int(pol.trades_per_day):
                return pol
            hit = capped_memo.get((id(pol), mt))           # R11: the same frozen protocol, built once per path
            if hit is not None and hit[0] is pol:
                return hit[1]
            from dataclasses import replace as _rep
            out = _rep(pol, trades_per_day=mt)
            capped_memo[(id(pol), mt)] = (pol, out)        # the key's protocol held, so its id cannot be reused
            return out

        # D-162: every account's session decision comes first, so the day hook (rotation's router) can be told each
        # account's trade limit before it routes; the decision reads the state at the start of the session either way.
        for c in trading_c:
            _decide(c, "combine")
        for a in trading_f:
            a.flip_today = False                              # D-339: a flip session is the day's decision, never carried
            _decide(a, "funded")
        # D-339 / D-343: the day's shared direction (one seeded draw a day) and each flip's slot, set on the flip draw
        # for its ledger row whether or not a router reads them
        flip_direction, flip_slots = 0, {}
        if flip is not None and any(a.flip_today for a in trading_f):
            flip_direction = 1 if float(flip_rng.random()) < 0.5 else -1
            for a in trading_f:
                if a.flip_today:
                    flip_slots[a.index] = flip.slot_for(day, a.index, max_concurrent_accounts)
                    a.flip_draw.today = (int(flip_slots[a.index]), int(flip_direction))
        # D-318: a room-capped Combine whose room buys no trade at its state's R is out of room -- it ends here, before
        # the router sees it, and its slot frees like any failed attempt's; a draw without the room cap never is.
        for c in trading_c:
            oor = getattr(c.draw, "out_of_room", None)
            if oor is not None and oor(c.B, c.F):
                c.finish_out_of_room(day - c.start_day, day)
                combines_out_of_room += 1
        # D-329: the policy's abandon read at the session's start -- the account ends before the router sees it and its
        # slot frees: a Combine cancelled, an XFA closed at the trader's request, nothing credited. Since D-334 the
        # abandon is taken at the previous close (below), which reads the same state, so this fires only for a state
        # that close could not read.
        for c in trading_c:
            if c.alive and c.decision is not None and getattr(c.decision, "abandon", False):
                c.finish_abandoned(day)
                combines_abandoned_by_policy += 1
        for a in trading_f:
            if a.alive and a.decision is not None and getattr(a.decision, "abandon", False):
                a.close_abandoned(day)
                funded_abandoned += 1
        trading_c = [c for c in trading_c if c.alive]
        trading_f = [a for a in trading_f if a.alive]
        # D-368: the XFAs that may take a second trade today -- a strategy session of one trade, collecting the Standard
        # path's winning days, not the Payout request day, no daily loss limit -- with the risk and R of their first
        # and the minimum, for the router
        second_keys: dict[tuple[str, int], tuple[float, float, float]] = {}
        if xfa_second:
            if not hook_takes_seconds:
                raise ValueError("xfa_second_trade needs the rotation router's day hook (D-368): only it hands a second "
                                 "signal after a first that fell short")
            for a in trading_f:
                dec = a.decision
                leg = a.policy_override or funded_policy
                if (not a.flip_today and dec is not None and getattr(dec, "source", "strategy") == "strategy"
                        and dec.max_trades is not None and int(dec.max_trades) == 1
                        and leg.payout_path == "standard" and a.win_days < int(rules.std_winning_days)
                        and not a.request_day_next and a.dll is None):
                    rr1 = float(dec.rr) if getattr(dec, "rr", None) is not None else float(leg.rr)
                    second_keys[("funded", a.index)] = (float(dec.risk), rr1, float(rules.std_winning_day_min))
        # D-368: the XFAs in the collect phase today -- a strategy session the table trades, collecting the Standard
        # path's winning days, not the Payout request day, no daily loss limit, the balance at or above `collect_from`
        # -- each sized at the fresh funded leg's dollar risk (the table's own fresh decision, D-329), its R unchanged
        collect_keys: dict[tuple[str, int], float] = {}
        by_table = [a for a in trading_f if not a.flip_today and a.decision is not None
                    and getattr(a.decision, "source", "strategy") == "collect"
                    and (a.decision.max_trades is None or int(a.decision.max_trades) >= 1)]
        if collect_from is not None or by_table:
            if not hook_takes_collect:
                raise ValueError("a collect phase or a collect decision needs the rotation router's day hook (D-368, "
                                 "D-379): only it asks an account whether it would bracket a signal at the need")
            for a in by_table:
                # D-379: the table's own collect decision -- the leaf's risk (set by `_decide`), the take-profit at the
                # shortfall to the winning-day minimum
                collect_keys[("funded", a.index)] = float(rules.std_winning_day_min)
            for a in (trading_f if collect_from is not None else []):
                dec = a.decision
                leg = a.policy_override or funded_policy
                if (not a.flip_today and dec is not None and getattr(dec, "source", "strategy") == "strategy"
                        and (dec.max_trades is None or int(dec.max_trades) >= 1)
                        and leg.payout_path == "standard" and a.win_days < int(rules.std_winning_days)
                        and not a.request_day_next and a.dll is None and a.B >= collect_from - EPS):
                    a.draw.set_risk(float(protocol.funded_risk), dec.rr)
                    collect_keys[("funded", a.index)] = float(rules.std_winning_day_min)
        if day_hook is not None:
            order = sorted(
                [(a.start_day, 0, a.index, ("funded", a.index)) for a in trading_f]
                + [(c.start_day, 1, c.index, ("combine", c.index)) for c in trading_c]
            )
            keys = [k for _, _, _, k in order]
            owner = getattr(day_hook, "__self__", None)
            if getattr(owner, "wants_progress", False):   # D-568 R5: each account's progress toward its goal, unit-free
                owner.progress = {("combine", c.index): max(0.0, float(c.B)) / float(rules.profit_target)
                                  for c in trading_c}
                owner.progress.update({("funded", a.index): float(a.win_days) / float(rules.std_winning_days)
                                       for a in trading_f})
            if wallet is not None:                      # D-206: the pot holds the cash while the other campaign moves
                wallet.cash = cash
            if hook_takes_caps:
                caps = {("combine", c.index): int(_capped(combine_policy, c).trades_per_day) for c in trading_c}
                # D-339: a flip-state account takes no routed signal today (its bracket is its own)
                caps.update({("funded", a.index): (0 if a.flip_today else
                                                   int(_capped(a.policy_override or funded_policy, a).trades_per_day))
                             for a in trading_f})
                caps.update({k: 2 for k in second_keys})                  # D-368: a second only after a first short
                if hook_takes_states:
                    states = {("combine", c.index): (float(c.B), float(c.F)) for c in trading_c}
                    states.update({("funded", a.index): (float(a.B), float(a.F)) for a in trading_f})
                    if hook_takes_flips and (flip is not None or hook_takes_rrs):
                        # D-339: each flip's slot, window and the day's direction, so the router places the flips
                        # among the log's trades for the cross-account rule
                        # D-384: the window of the account's own bracket (a menu's pick), the stream's otherwise
                        flips = ([(("funded", a.index), float(flip_slots[a.index]),
                                   float(flip_slots[a.index] + getattr(a.flip_draw, "spec", flip).window_minutes(
                                       flip_slots[a.index])), flip_direction)
                                  for a in trading_f if a.flip_today] if flip is not None else [])
                        if hook_takes_rrs:
                            # D-349: each account's R for the session -- the table's decision, else the leg's -- so the
                            # router holds a routed position to its exit at that R (the rule's and flat routing's clock)
                            def _rr_of(acct: Any, leg: Any) -> float:
                                dec = acct.decision
                                return float(dec.rr) if (dec is not None and getattr(dec, "rr", None) is not None) else float(leg.rr)
                            rrs = {("combine", c.index): _rr_of(c, combine_policy) for c in trading_c}
                            rrs.update({("funded", a.index): _rr_of(a, a.policy_override or funded_policy) for a in trading_f})
                            if collect_from is not None or collect_keys:   # D-368, D-379: the accounts collecting
                                day_hook(day, keys, caps, states, flips, rrs, second_keys, collect_keys)
                            elif xfa_second:                      # D-368: the accounts allowed a second trade
                                day_hook(day, keys, caps, states, flips, rrs, second_keys)
                            else:
                                day_hook(day, keys, caps, states, flips, rrs)
                        else:
                            day_hook(day, keys, caps, states, flips)
                    else:
                        day_hook(day, keys, caps, states)
                else:
                    day_hook(day, keys, caps)
            else:
                day_hook(day, keys)
            if wallet is not None:
                cash = float(wallet.cash)

        for c in trading_c:
            begin = getattr(c.draw, "begin_session", None)
            if begin is not None:
                begin(balance=c.B, floor=c.F)
            n0 = len(ledger) if ledger is not None else 0
            c.trade_day(rules, _capped(combine_policy, c), day - c.start_day, day, ledger=ledger,
                        need_aware=need_aware, consistency_cap=consistency_cap)
            _stamp(c, n0)
            if c.alive and c.days >= combine_max_days:
                c.unresolved = True
                c.resolved_on = day
        requested_today: list[tuple[int, float, FundedAccount]] = []
        for a in trading_f:
            begin = getattr(a.draw, "begin_session", None)
            if begin is not None:
                begin(balance=a.B, floor=a.F)
            pol = _capped(a.policy_override if a.policy_override is not None else funded_policy, a)
            a_cap = cap if a.policy_override is None else (
                rules.std_cap if pol.payout_path == "standard" else rules.cons_cap)
            second_ok = ("funded", a.index) in second_keys                 # D-368
            if second_ok and int(pol.trades_per_day) < 2:
                from dataclasses import replace as _rep2
                pol = _rep2(pol, trades_per_day=2)
            n0 = len(ledger) if ledger is not None else 0
            net = a.trade_day(rules, pol, a_cap, day - a.start_day, day, ledger=ledger, second_trade=second_ok,
                              collect=("funded", a.index) in collect_keys)
            _stamp(a, n0)
            if net is not None:
                entry = (day + int(payout_lag_days), net, a)
                pending.append(entry)
                requested_today.append(entry)
        if record_days:
            mll = float(rules.mll)
            for c in trading_c:
                room = float(c.B - c.F)
                row = {
                    "day": day, "kind": "combine", "index": c.index,
                    "state": ("failed" if c.failed else "passed" if c.passed else "unresolved" if c.unresolved else "combine"),
                    "balance": float(c.B), "floor": float(c.F), "room": room, "day_pnl": float(c.last_day_pnl),
                    "near_mll": bool(not c.failed and room < near_miss_frac * mll),
                    "near_dll": bool(c.dll is not None and not c.failed
                                     and -c.dll + EPS < c.last_day_pnl <= -(1.0 - near_miss_frac) * c.dll),
                    "consistency_binding": bool(not c.failed and c.last_target > rules.profit_target + EPS),
                    "target": float(c.last_target), "eligible": None, "requested": 0.0,
                    "attempt": c.resets,
                    "regime": c.decision.regime if c.decision is not None else None,
                    "policy_risk": c.decision.risk if c.decision is not None else None,
                }
                account_days.append(row)
            for a in trading_f:
                room = float(a.B - a.F)
                req = next((float(a.last_request) for e in requested_today if e[2] is a), 0.0)
                row = {
                    "day": day, "kind": "funded", "index": a.index,
                    "state": ("closed" if a.closed else "paid" if a.n_payouts > 0 else "funded"),
                    "balance": float(a.B), "floor": float(a.F), "room": room, "day_pnl": float(a.last_day_pnl),
                    "near_mll": bool(not a.closed and room < near_miss_frac * mll),
                    "near_dll": bool(a.dll is not None and not a.closed
                                     and -a.dll + EPS < a.last_day_pnl <= -(1.0 - near_miss_frac) * a.dll),
                    "consistency_binding": bool(a.last_cons_blocked),
                    "target": None, "eligible": bool(a.last_eligible), "requested": req,
                    "attempt": 0,
                    "regime": a.decision.regime if a.decision is not None else None,
                    "policy_risk": a.decision.risk if a.decision is not None else None,
                }
                account_days.append(row)
        # D-334: the policy's abandon is taken at the close whose state decides it. The inputs the policy reads are the
        # close's (the balance and floor lock at 16:00 CT; the payout conditions settle there), so the next session's
        # decision is known now: the account is read as that session will find it (`day + 1` for the day-keyed
        # inputs) and, if the decision is abandon, ends at this close -- a Combine cancelled this evening, its
        # replacement bought below and trading tomorrow, as after a breach; an XFA closed at the trader's request, its
        # slot freed tomorrow, as after any closure. An abandon then costs the slot what a breach costs, which is what
        # the table prices (the audit of D-333, finding 3: read at the next session's start, the abandon idled the slot
        # one session more than a breach, 5-6 % of the slot-days available).
        if day + 1 < horizon_days:
            if risk_policy is not None:
                from propedge.campaign.risk_policy import account_state

                for c in trading_c:
                    if not c.alive:
                        continue
                    dec = risk_policy.decide(account_state(c, kind="combine", day=day + 1, cents=decision_cents))
                    if getattr(dec, "abandon", False):
                        c.finish_abandoned(day)
                        combines_abandoned_by_policy += 1
                    else:
                        # D-335: the next session's risk and R on the draw now, so the room below is read at them -- the
                        # same call `_decide` makes at that session's start, which repeats it unchanged
                        setr = getattr(c.draw, "set_risk", None)
                        if setr is not None:
                            setr(dec.risk, dec.rr)
                for a in trading_f:
                    if a.alive and a.ended_on is None and getattr(
                            risk_policy.decide(account_state(a, kind="funded", day=day + 1, cents=decision_cents)), "abandon", False):
                        a.close_abandoned(day)
                        funded_abandoned += 1
            # D-335 (the audit of D-334, finding 9): a room-capped Combine whose room buys no trade at its next session's R
            # is out of room at this close and ends now (D-318: a failed attempt, not a breach), its replacement bought
            # below -- the same timing as the abandon above, which is read first, so a state the policy abandons is
            # counted as abandoned as before and no policy campaign's row can change; without a policy (the fixed-legs
            # twin) this is the only way such an attempt ends. The start-of-session check above remains for a state this
            # close could not read.
            for c in trading_c:
                oor = getattr(c.draw, "out_of_room", None)
                if c.alive and oor is not None and oor(c.B, c.F):
                    c.finish_out_of_room(day - c.start_day, day)
                    combines_out_of_room += 1
        # Accounts that hit the loss limit today, Combine or funded. Two or more on one day is
        # the Responsible Trading Program's first trigger (D-30); only a loop that steps
        # accounts through the same day can count it.
        breached_today = sum(1 for c in running if c.failed and not c.out_of_room and c.resolved_on == day) + sum(
            1 for a in funded if a.closed and not a.abandoned and a.ended_on == day      # D-329: a closure, no breach
        )
        breaches_per_day[day] = breached_today
        if breached_today >= 2:
            multi_breach_days += 1
        max_breached = max(max_breached, breached_today)

        if conduct is not None:
            # Tier 3 (D-145): a payout requested while the campaign shows the stacking pattern is
            # exposed; an exposed payout is denied, and its account closed, with the stated
            # probability. One draw per exposed payout, whatever the probability.
            lo = max(0, day - conduct.pattern_window_days + 1)
            exposed = int(breaches_per_day[lo:day + 1].sum()) >= conduct.pattern_breaches
            for entry in requested_today:
                payouts_requested += 1
                if not exposed:
                    continue
                payouts_exposed += 1
                if float(enforce_rng.random()) < conduct.enforcement_p:
                    payouts_denied += 1
                    pending.remove(entry)
                    entry[2].deny_last_payout(day)
            # Tier 2 (D-145): Responsible Trading Program placement, effective from tomorrow; the
            # first `rtp_warnings` trigger days bring a warning instead (D-220).
            if conduct.rtp and rtp_day is None:
                traded = trading_c + trading_f
                fired = ""
                if breached_today >= 2:
                    fired = "multiple accounts hit the MLL in one day"
                elif any(_losers_not_smaller(x.pnls, conduct.losers_window, conduct.min_trades)
                         for x in traded):
                    fired = "losers not smaller than winners"
                elif any(len(x.pnls) >= conduct.min_trades
                         and x.at_max > conduct.max_position_share * len(x.pnls) for x in traded):
                    fired = "maximum position on most trades"
                if fired and len(rtp_warning_days) < conduct.rtp_warnings:
                    rtp_warning_days.append(day)
                elif fired:
                    rtp_trigger, rtp_day = fired, day

        # R7 (multi-firm D-30; docs/TWO_FIRMS.md): the household rule, read once the day's payouts are requested (and any
        # denied). An account that raised it at this close is counted (Lucid: its fifth payout -- the household enters
        # the live review pool, and a live move or the cash-out closes every simulated account, 16558826); with the rule
        # on, the first one ends every other live account here and the path buys nothing more.
        if household_rule:
            raised = [a for a in funded if a.ended_on == day and getattr(a, "closes_household", False)]
            household_triggers += len(raised)
            if raised and household_on and household_closed_on is None:
                household_closed_on = day
                for c in running:
                    if c.alive:
                        c.close_household(day)
                        household_combines += 1
                for a in funded:
                    if a.ended_on is None and a.alive:
                        a.close_household(day)
                        household_funded += 1
                for c in queue:
                    c.household_closed = True
                household_passes += len(queue)
                queue.clear()

        # D-495 (4): the funded accounts lost today -- ended by a breach, a closure at request or a tier-3 denial's
        # closure -- counted while they are still in `funded` (step 5 moves them).
        if ftp is not None:
            ftp_lost[day] = sum(1 for a in funded if a.closed and a.ended_on == day)

        # 3. payouts arriving today, in the order they were requested.
        still_pending: list[tuple[int, float, FundedAccount]] = []
        for arrival, amount, acc in pending:
            if arrival <= day:
                cash += amount
                total_payouts += amount
                pay_in[day] += amount
                payout_days_campaign.append(day)
                if not acc.ever_credited:
                    acc.ever_credited = True
                    accounts_ever_paid += 1
            else:
                still_pending.append((arrival, amount, acc))
        pending = still_pending
        if entry_on:
            # D-630 (b), D-632: the pause's condition as today's resets find it -- F funded accounts held (before this
            # evening's activations) and no payout arrived (the arrivals are just above)
            pause_now = (pause_f is not None and not payout_days_campaign
                         and sum(1 for a in funded if a.ended_on is None) >= pause_f)
            # D-630 (c): the day the ramp reached the base's seats
            if ramp_s0 is not None and ramp_full_on < 0 and ramp_s0 + len(payout_days_campaign) >= ramp_base:
                ramp_full_on = day

        # 4. Combines that resolved today: a pass joins the hold queue; anything else ends.
        still: list[CombineAccount] = []
        for c in running:
            if c.resolved_on is None:
                still.append(c)
                continue
            # D-146: a failure answered with a reset. The breach was counted above; the account
            # keeps its subscription and trades again tomorrow from its starting balance.
            if (reset_failed_combines and c.failed and c.resolved_on == day
                    and cash >= the_reset_fee and ftp_no_resets):
                ftp_resets_refused += 1                       # D-495 (4): "You cannot purchase new ... Resets"
            elif (reset_failed_combines and c.failed and c.resolved_on == day
                    and cash >= the_reset_fee and _budget_spent(day)):
                budget_resets_refused += 1                    # D-501: the budget refuses the reset; the Combine fails
            elif (reset_failed_combines and c.failed and c.resolved_on == day
                    and cash >= the_reset_fee and wallet_w is not None and start_bankroll - cash > wallet_w):
                wallet_resets_refused += 1                    # D-630 (a): as the budget's refusal; the Combine fails
            elif (reset_failed_combines and c.failed and c.resolved_on == day
                    and cash >= the_reset_fee and pause_now):
                pause_resets_refused += 1                     # D-630 (b): as the budget's refusal; the Combine fails
                pause_first = day if pause_first < 0 else pause_first
            elif (reset_failed_combines and c.failed and c.resolved_on == day
                    and cash >= the_reset_fee):
                if ftp is not None:
                    ftp_bought[day] += 1                      # D-495 (4): a reset counts with the purchases
                if budget_on:
                    budget_bought[day] += 1                   # D-501: a reset counts with the purchases
                if wallet_w is not None:
                    wallet_max_out = max(wallet_max_out, start_bankroll - cash)   # D-630 (a)
                cash -= the_reset_fee
                total_fees += the_reset_fee
                fee_reset[day] += the_reset_fee
                resets_taken += 1
                c.reset(day, rtp_dll=_rtp_dll_on(day))
                still.append(c)
                continue
            finished_combines.append(c)
            if c.passed:
                if household_closed_on is not None:          # R7: the household rule closed it with its pass
                    c.household_closed = True
                    household_passes += 1
                    continue
                if on_pass:
                    if cash < activation:
                        passes_forfeited += 1
                        continue
                    cash -= activation
                    total_fees += activation
                    fee_act[day] += activation
                queue.append(c)
        running = still

        # 5. funded accounts that finished free their seat: the day after they ended (the stage-level loop's
        #    convention, which the lockstep reproduces exactly by default -- the validation limit), or at that close
        #    under `Protocol.params["seat_frees"] == "same_evening"` (D-339; the help centre, re-read 2026-10-10 under
        #    D-336: activation is "minutes after paying the Activation Fee" and a breached XFA is "closed at the end of
        #    the day", so a waiting pass activates the same evening and trades the next session; the default idles the
        #    seat one session per funded ending, pessimistic by up to a session) ...
        ended = (lambda a: a.ended_on is not None and (a.ended_on <= day if seat_same_evening else a.ended_on < day))
        ending = [a for a in funded if ended(a)]
        finished_funded.extend(ending)
        funded = [a for a in funded if not ended(a)]
        # ... and the hold queue fills any free slot, paying the activation fee then (D-21).
        while queue and len(funded) < max_concurrent_accounts:
            c = queue[0]
            if not on_pass:
                if cash < activation:
                    break
                cash -= activation
                total_fees += activation
                fee_act[day] += activation
            queue.pop(0)
            j = accounts_funded
            # RTP (13620045): the path is decided by the Combine, not the activation day. A Combine bought (or reset)
            # under RTP is a Consistency Trading Combine and its pass is activated on the Consistency path; "Any
            # Standard Trading Combine subscription started before RTP placement will remain as a Standard Trading
            # Combine. If passed, it may be activated as either a Standard XFA or Consistency XFA" -- the protocol's
            # path. Either way an XFA activated after placement carries the daily loss limit ("XFAs activated from
            # Trading Combines purchased before your RTP placement can be Standard or Consistency with a Daily Loss
            # Limit").
            funded.append(
                funded_cls(
                    index=j, activation_day=day, draw=funded_draw_factory(j, day),
                    horizon_days=int(funded_horizon_days), floor_start=rules.xfa_mll_start,
                    policy_override=rtp_policy if (rtp_policy is not None and c.rtp) else None,
                    dll=_rtp_dll_on(day), combine_index=c.index, combine_purchase_day=c.purchase_day,
                    payout_timing=payout_timing,
                    flip_draw=flip_draw_factory(j, day) if flip_draw_factory is not None else None,   # D-339
                )
            )
            accounts_funded += 1
        peak_queue = max(peak_queue, len(queue))

        # 6. new Combines. With reinvestment off, only the initial bankroll is ever spent.
        spendable = cash if reinvest else min(cash, float(initial_bankroll) - total_fees)
        blocked_by_queue = stop_buying_when_queued and bool(queue)
        # D-630 (b), D-632: the pause's condition, read again at every purchase step -- the campaign holds at least F
        # funded accounts (activated, this evening's included, and not ended) and its first payout has not arrived.
        # No latch: with fewer than F held the purchases below are the base's.
        if pause_f is not None:
            held_before = pause_in_force
            pause_in_force = (not payout_days_campaign
                              and sum(1 for a in funded if a.ended_on is None) >= pause_f)
            if pause_in_force:
                pause_days += 1
                pause_spells += 0 if held_before else 1
            elif held_before and not payout_days_campaign:
                pause_resumed.append(day)                     # fewer than F held again, no payout yet
        if ftp_in_force and (                                 # D-495 (4): a purchase the program alone refuses today
            not blocked_by_queue
            and len(running) < max_concurrent_combines
            and (max_total_accounts is None or len(running) + len(funded) + len(queue) < max_total_accounts)
            and spendable >= subscription
            and (max_attempts is None or attempts_started < max_attempts)
            and household_closed_on is None
            and len(running) + len(funded) + len(queue) >= ftp.account_limit
            and not (entry_on and any(_entry_refusals(       # D-630: nor an entry option
                cash, len(running) + len(funded) + len(queue), pause_in_force, len(payout_days_campaign))))
        ):
            ftp_blocked_days += 1
        while (
            not blocked_by_queue
            and len(running) < max_concurrent_combines
            and (max_total_accounts is None or len(running) + len(funded) + len(queue) < max_total_accounts)
            and spendable >= subscription
            and (max_attempts is None or attempts_started < max_attempts)
            and household_closed_on is None                  # R7: the household rule ended the campaign's buying
            # D-495 (4): under the Focused Trader Program at most `account_limit` live account ("1 active $50K account
            # at a time", 10551016): no purchase while the current accounts are open
            and (not ftp_in_force or len(running) + len(funded) + len(queue) < ftp.account_limit)
            and not _budget_spent(day)                       # D-501: the self-imposed purchase budget
            and not (entry_on and any(_entry_refusals(       # D-630: the wallet stop, the pause, the seat ramp
                cash, len(running) + len(funded) + len(queue), pause_in_force, len(payout_days_campaign))))
        ):
            k = attempts_started
            if wallet_w is not None:
                wallet_max_out = max(wallet_max_out, start_bankroll - cash)       # D-630 (a)
            cash -= subscription
            spendable -= subscription
            total_fees += subscription
            fee_sub[day] += subscription
            running.append(
                combine_cls(
                    index=k, purchase_day=day, draw=combine_draw_factory(k, day),
                    floor_start=-rules.mll,
                    dll=_rtp_dll_on(day), rtp=_rtp_dll_on(day) is not None,
                )
            )
            purchase_days.append(day)
            attempts_started += 1
            if ftp is not None:
                ftp_bought[day] += 1                          # D-495 (4)
            if budget_on:
                budget_bought[day] += 1                       # D-501
        if budget_on and _budget_spent(day) and (            # D-501: a day the budget alone stopped a purchase
            not blocked_by_queue
            and len(running) < max_concurrent_combines
            and (max_total_accounts is None or len(running) + len(funded) + len(queue) < max_total_accounts)
            and spendable >= subscription
            and (max_attempts is None or attempts_started < max_attempts)
            and household_closed_on is None
            and (not ftp_in_force or len(running) + len(funded) + len(queue) < ftp.account_limit)
            and not (entry_on and any(_entry_refusals(       # D-630: nor an entry option
                cash, len(running) + len(funded) + len(queue), pause_in_force, len(payout_days_campaign))))
        ):
            budget_blocked_days += 1
        if entry_on and (                                     # D-630: a day one entry option alone stopped a purchase
            not blocked_by_queue
            and len(running) < max_concurrent_combines
            and (max_total_accounts is None or len(running) + len(funded) + len(queue) < max_total_accounts)
            and spendable >= subscription
            and (max_attempts is None or attempts_started < max_attempts)
            and household_closed_on is None
            and (not ftp_in_force or len(running) + len(funded) + len(queue) < ftp.account_limit)
            and not _budget_spent(day)
        ):
            refusals = _entry_refusals(cash, len(running) + len(funded) + len(queue), pause_in_force,
                                       len(payout_days_campaign))
            if sum(refusals) == 1:
                if refusals[0]:
                    wallet_blocked_days += 1
                    wallet_first_blocked = day if wallet_first_blocked < 0 else wallet_first_blocked
                elif refusals[1]:
                    pause_blocked_days += 1
                    pause_first = day if pause_first < 0 else pause_first
                else:
                    ramp_blocked_days += 1
                    ramp_first_blocked = day if ramp_first_blocked < 0 else ramp_first_blocked
        # D-630 (a): a stop that can no longer lift -- above W with nothing live, no pass waiting and no payout on its
        # way, so the cash cannot rise: the stop is final. Recorded only; the campaign idles to the horizon and is not
        # ruined by it (step 7 reads the cash against the fees). The pause cannot end so (D-632): with no funded
        # account held it does not bind.
        if (wallet_w is not None and wallet_final < 0 and start_bankroll - cash > wallet_w and not running
                and not queue and not pending and not any(a.ended_on is None for a in funded)):
            wallet_final = day

        # D-495 (4): the Focused Trader Program's placement, read at this close once the day's purchases are made: the
        # first watched measure at its declared threshold over the window places the campaign on the declared path,
        # binding from tomorrow. A Corrective placement closes every live account here (no breach, nothing refunded),
        # removes the passes waiting for a seat and denies every payout requested and not yet arrived (10551016).
        if ftp is not None and ftp_placed is None and not ftp_done:
            lo = max(0, day - int(ftp.window_days) + 1, ftp_watch_from)
            crossed = []
            if ftp.combine_purchases is not None:
                v = int(ftp_bought[lo:day + 1].sum())
                if v >= int(ftp.combine_purchases):
                    crossed.append(("combine_purchases", v))
            if ftp.funded_lost is not None:
                v = int(ftp_lost[lo:day + 1].sum())
                if v >= int(ftp.funded_lost):
                    crossed.append(("funded_lost", v))
            if crossed:
                ftp_placed = {"day": int(day), "path": ftp.path, "measure": crossed[0][0], "value": crossed[0][1],
                              "measures": dict(crossed), "combines_closed": 0, "funded_closed": 0,
                              "passes_removed": 0, "payouts_denied": 0, "payout_cash_denied": 0.0, "ended_on": -1}
                ftp_placements.append(ftp_placed)
                if ftp.path == FTP_CORRECTIVE:
                    ftp_until = day + int(ftp.corrective_days)
                    for c in running:
                        c.close_ftp(day)
                        finished_combines.append(c)
                    ftp_placed["combines_closed"] = len(running)
                    running = []
                    for c in queue:
                        c.ftp_closed = True
                    ftp_placed["passes_removed"] = len(queue)
                    queue.clear()
                    for a in funded:
                        if a.ended_on is None:
                            a.close_ftp(day)
                            ftp_placed["funded_closed"] += 1
                    for _, amount, acc in reversed(pending):      # an account's pending payouts are its latest
                        acc.deny_pending_ftp(amount, rules)
                        ftp_placed["payouts_denied"] += 1
                        ftp_placed["payout_cash_denied"] += float(amount)
                    pending = []

        # 7. ruin: nothing live, and the campaign cannot take its next step (after the household rule there is none).
        if not ruined and household_closed_on is None:
            nothing_live = not running and not funded
            if queue:
                stuck = cash < activation and (stop_buying_when_queued or cash < subscription)
            else:
                stuck = cash < subscription
            if nothing_live and stuck:
                ruined = True
                ruin_day = day

        cash_series[day] = cash
        active_series[day] = len(funded)
        # R11: a finished account never trades again and the finished lists only grow, so their trades are added once,
        # as each account finishes; the same integer total as summing them all each day
        for c in finished_combines[n_finished_c:]:
            finished_trades += c.trades
        for a in finished_funded[n_finished_f:]:
            finished_trades += a.trades
        n_finished_c, n_finished_f = len(finished_combines), len(finished_funded)
        now_trades = finished_trades + sum(c.trades for c in running) + sum(a.trades for a in funded)
        trades_by_day[day] = now_trades - trades_so_far       # D-305: the day's executed trades, every account
        trades_so_far = now_trades
        peak_cash = max(peak_cash, cash)
        max_dd = max(max_dd, peak_cash - cash)

    if wallet is not None:                              # D-206: leave the final cash in the shared pot
        wallet.cash = cash
    if queue:
        if len(funded) < max_concurrent_accounts and not on_pass:
            passes_forfeited += len(queue)
        else:
            passes_on_hold_at_end = len(queue)

    gaps = tuple(
        int(b - a) for a, b in zip(payout_days_campaign, payout_days_campaign[1:])
    )
    # Sizing diagnostics, summed over every account whose draw sized trades in contracts.
    sized = at_cap = unsized = stood = need_exits = room_capped = 0
    intended = realised = intended_capped = 0.0
    for acct in finished_combines + running + finished_funded + funded:
        stats = getattr(acct.draw, "stats", None)
        if stats is None:
            continue
        sized += int(stats.trades)
        at_cap += int(stats.at_cap)
        unsized += int(stats.unsized)
        stood += int(getattr(stats, "stood_aside", 0))
        need_exits += int(getattr(stats, "need_exits", 0))
        room_capped += int(getattr(stats, "room_capped", 0))
        intended += float(stats.intended_risk)
        intended_capped += float(getattr(stats, "intended_capped_risk", stats.intended_risk))
        realised += float(stats.realised_risk)
    path = CampaignPath(
        final_cash=float(cash),
        initial_bankroll=float(initial_bankroll),
        cash_series=cash_series,
        active_funded_series=active_series,
        trades_by_day=tuple(int(x) for x in trades_by_day),
        ruined=ruined,
        ruin_day=ruin_day,
        max_drawdown=float(max_dd),
        max_drawdown_frac=float(max_dd / peak_cash) if peak_cash else 0.0,
        attempts_started=attempts_started,
        accounts_funded=accounts_funded,
        accounts_ever_paid=accounts_ever_paid,
        days_to_first_payout=payout_days_campaign[0] if payout_days_campaign else None,
        payout_gaps=gaps,
        total_fees=float(total_fees),
        total_payouts=float(total_payouts),
        peak_queue_length=peak_queue,
        passes_forfeited=passes_forfeited,
        combines_abandoned=combines_abandoned,
        passes_on_hold_at_end=passes_on_hold_at_end,
        same_day_multi_breach_days=multi_breach_days,
        max_breaches_in_one_day=max_breached,
        trades_sized=sized,
        trades_at_tier_cap=at_cap,
        trades_unsized=unsized,
        trades_stood_aside=stood,
        trades_need_exits=need_exits,
        trades_room_capped=room_capped,
        combines_out_of_room=combines_out_of_room,
        combines_abandoned_by_policy=combines_abandoned_by_policy,
        funded_abandoned=funded_abandoned,
        funded_flips=sum(int(a.flips) for a in finished_funded + funded),             # D-339
        funded_flips_won=sum(int(a.flips_won) for a in finished_funded + funded),
        intended_risk_total=intended,
        intended_capped_risk_total=intended_capped,
        realised_risk_total=realised,
    )
    # A queued pass is already in `finished_combines` (it resolved); only the unresolved ones
    # in `running` are missing from it.
    all_combines = sorted(finished_combines + running, key=lambda c: c.index)
    all_funded = sorted(finished_funded + funded, key=lambda a: a.index)
    conduct_out: dict[str, Any] = {}
    if conduct is not None:
        w = conduct.pattern_window_days
        bought = np.zeros(horizon_days, dtype=int)
        for d in purchase_days:
            bought[d] += 1
        roll = lambda x: int(np.convolve(x, np.ones(w, dtype=int), "valid").max()) if len(x) >= w \
            else int(x.sum())                                                          # noqa: E731
        conduct_out = {
            "rtp_placed_day": -1 if rtp_day is None else int(rtp_day), "rtp_trigger": rtp_trigger,
            "payouts_requested": payouts_requested, "payouts_exposed": payouts_exposed,
            "payouts_denied": payouts_denied, "max_mll_breaches_in_window": roll(breaches_per_day),
            "max_combine_purchases_in_window": roll(bought), "combine_purchases": len(purchase_days),
            "mll_breaches": int(breaches_per_day.sum()), "window_days": w,
        }
        if conduct.rtp_warnings:
            conduct_out["rtp_warning_days"] = tuple(rtp_warning_days)
    if reset_failed_combines:
        conduct_out = dict(conduct_out, resets=resets_taken)
    campaign_days: tuple[dict[str, Any], ...] = ()
    if record_days:
        campaign_days = tuple(
            {"day": d, "fee_subscription": float(fee_sub[d]), "fee_activation": float(fee_act[d]),
             "fee_reset": float(fee_reset[d]), "payouts_in": float(pay_in[d]), "cash": float(cash_series[d]),
             "active_funded": int(active_series[d]), "breaches": int(breaches_per_day[d])}
            for d in range(horizon_days)
        )
    return LockstepPath(
        path=path,
        combines=tuple(_record_combine(c) for c in all_combines),
        funded=tuple(_record_funded(a) for a in all_funded),
        breaches_per_day=breaches_per_day,
        trades=tuple(ledger) if ledger is not None else (),
        conduct=conduct_out,
        account_days=tuple(account_days),
        campaign_days=campaign_days,
        focused_trader=({} if ftp is None else {
            "decision": "D-495", "model": ftp.as_dict(), "placements": tuple(dict(x) for x in ftp_placements),
            "placed": bool(ftp_placements), "first_placed_day": int(ftp_placements[0]["day"]) if ftp_placements else -1,
            "total_combine_purchases_and_resets": int(ftp_bought.sum()), "total_funded_lost": int(ftp_lost.sum()),
            "max_combine_purchases_in_window": _rolling_max(ftp_bought, int(ftp.window_days)),
            "max_funded_lost_in_window": _rolling_max(ftp_lost, int(ftp.window_days)),
            "purchase_days_blocked": int(ftp_blocked_days), "resets_refused": int(ftp_resets_refused),
            **{k: sum(x[k] for x in ftp_placements) for k in ("combines_closed", "funded_closed", "passes_removed",
                                                              "payouts_denied", "payout_cash_denied")}}),
        purchase_budget=({} if not budget_on else {
            "decision": "D-501", "k": int(budget_k), "window_days": int(budget_w),
            "purchases_and_resets": int(budget_bought.sum()),
            "max_purchases_in_window": _rolling_max(budget_bought, int(budget_w)),
            "purchase_days_blocked": int(budget_blocked_days), "resets_refused": int(budget_resets_refused)}),
        wallet_stop=({} if wallet_w is None else {
            "decision": "D-630", "w": float(wallet_w), "purchase_days_blocked": int(wallet_blocked_days),
            "resets_refused": int(wallet_resets_refused), "first_blocked_day": int(wallet_first_blocked),
            "max_out_of_pocket_at_purchase": float(wallet_max_out), "final_on": int(wallet_final),
            "on_at_end": bool(start_bankroll - cash > wallet_w)}),      # above W at the horizon: the stop is on
        pause_after_funded=({} if pause_f is None else {
            "decision": "D-630", "wording": "D-632", "f": int(pause_f), "paused_on": int(pause_first),
            "released_on": int(payout_days_campaign[0]) if (pause_first >= 0 and payout_days_campaign) else -1,
            "purchase_days_blocked": int(pause_blocked_days), "resets_refused": int(pause_resets_refused),
            "in_force_days": int(pause_days), "spells": int(pause_spells),
            "resumed_below_f": len(pause_resumed), "resumed_below_f_days": tuple(int(d) for d in pause_resumed)}),
        seat_ramp=({} if ramp_s0 is None else {
            "decision": "D-630", "s0": int(ramp_s0), "base_seats": int(ramp_base),
            "payouts_arrived": len(payout_days_campaign),
            "seats_at_end": int(min(ramp_base, ramp_s0 + len(payout_days_campaign))),
            "purchase_days_blocked": int(ramp_blocked_days), "first_blocked_day": int(ramp_first_blocked),
            "full_on": int(ramp_full_on)}),
        household=({"reading": "closes_household" if household_on else "count_only",
                    "triggers": household_triggers,
                    "closed_on": -1 if household_closed_on is None else int(household_closed_on),
                    "combines_closed": household_combines, "funded_closed": household_funded,
                    "passes_closed": household_passes} if household_rule else {}),
    )


# --------------------------------------------------------------------- paths in parallel (R11)

#: R11: one path worker's physical memory, in GB. Measured 2026-10-29 (one spawned worker, its peak working set read
#: from the process before the pool closed): 0.22 GB on P-06's gate (FV3-C, the confirmation window, 504 days) and
#: 0.21-0.22 GB on P-10's (T24-GF15b, R152's window, 504 days), each with 4-path chunks; a path's record pickles to
#: about 0.17 MB, so a 500-path verdict's 63-path chunks at 2 workers hold some tens of MB more. Rounded up to 0.3.
WORKER_MEMORY_GB = 0.3
#: R11: one path worker's peak private commit, in GB, which Windows charges against RAM plus the page file whether or not
#: the pages are touched. numpy's OpenBLAS commits about 0.73 GB at import for its 24 threads on this machine, so a
#: worker started with them peaked at 0.92 GB; started with one BLAS thread (`WORKER_ENV`) it peaked at 0.20 GB on
#: P-10's gate (measured 2026-10-29, as above). Rounded up to 0.3.
WORKER_COMMIT_GB = 0.3
#: R11: the environment a path worker starts with -- one BLAS / OpenMP thread, since the paths are spread over processes.
#: No engine code a worker runs calls BLAS (no dot, matmul or linalg in the path step), and the bitwise tests compare
#: these workers with the caller's own process (`tests/test_parallel_paths.py`).
WORKER_ENV = {"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}


def _windows_memory_status() -> tuple[float, float] | None:
    """(available physical memory, available commit) in GB from `GlobalMemoryStatusEx`; None off Windows or on failure."""
    import sys

    if sys.platform != "win32":
        return None
    import ctypes

    class _Status(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

    try:
        st = _Status()
        st.dwLength = ctypes.sizeof(_Status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
            return None
        return float(st.ullAvailPhys) / 2**30, float(st.ullAvailPageFile) / 2**30
    except (OSError, ValueError, AttributeError):
        return None


def available_memory_gb() -> float:
    """The physical memory free for new processes, in GB: Windows' available memory (`GlobalMemoryStatusEx`, free and
    standby pages), Linux's `MemAvailable`, else the free pages `os.sysconf` reports; NaN when none can be read."""
    import os
    import sys

    if sys.platform == "win32":
        st = _windows_memory_status()
        return st[0] if st is not None else float("nan")
    try:
        meminfo = Path("/proc/meminfo")
        if meminfo.is_file():
            for line in meminfo.read_text().splitlines():
                if line.startswith("MemAvailable:"):
                    return float(line.split()[1]) / 2**20
        return float(os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")) / 2**30
    except (OSError, ValueError, AttributeError):
        return float("nan")


def available_commit_gb() -> float:
    """The commit charge still available (RAM plus page file, less what every process has committed), in GB, on Windows,
    where a process that cannot commit fails (OpenBLAS: "Memory allocation still failed"); infinite elsewhere."""
    import sys

    if sys.platform != "win32":
        return float("inf")
    st = _windows_memory_status()
    return st[1] if st is not None else float("nan")


def guarded_workers(requested: int, *, n_tasks: int, memory_per_worker_gb: float | None = None,
                    available_gb: float | None = None, commit_per_worker_gb: float | None = None,
                    available_commit: float | None = None) -> int:
    """R11's memory guard: never more workers than the free physical memory divided by one worker's memory
    (`WORKER_MEMORY_GB` unless given), nor than the free commit divided by one worker's commit (`WORKER_COMMIT_GB`), nor
    than the tasks or the processors; at least 1. Free memory or commit unknown: 1."""
    import os

    req = max(1, int(requested))
    if req == 1:
        return 1
    per = float(WORKER_MEMORY_GB if memory_per_worker_gb is None else memory_per_worker_gb)
    free = available_memory_gb() if available_gb is None else float(available_gb)
    by_memory = int(free // per) if (math.isfinite(free) and per > 0) else 1
    per_c = float(WORKER_COMMIT_GB if commit_per_worker_gb is None else commit_per_worker_gb)
    free_c = available_commit_gb() if available_commit is None else float(available_commit)
    by_commit = (req if free_c == float("inf") else int(free_c // per_c) if (math.isfinite(free_c) and per_c > 0)
                 else 1)
    return max(1, min(req, by_memory, by_commit, max(1, int(n_tasks)), os.cpu_count() or 1))


def path_pool(workers: int, *, n_tasks: int, memory_per_worker_gb: float | None = None):
    """`(executor, workers)`: a spawn-context process pool of the guarded size, or `(None, 1)` when one process is all
    the memory (or the request) allows, or when this process is itself a pool's daemonic worker (a caller already
    parallel over campaigns, e.g. a screen's cells, which cannot start children). The caller shuts the executor down
    (`with` or `shutdown()`)."""
    import multiprocessing

    if int(workers) > 1 and multiprocessing.current_process().daemon:
        return None, 1
    n = guarded_workers(workers, n_tasks=n_tasks, memory_per_worker_gb=memory_per_worker_gb)
    if int(workers) > 1 and n < int(workers):
        import sys

        print(f"[lockstep] workers {int(workers)} -> {n}: {available_memory_gb():.2f} GB free at "
              f"{WORKER_MEMORY_GB if memory_per_worker_gb is None else memory_per_worker_gb} GB a worker, "
              f"{available_commit_gb():.2f} GB of commit free at {WORKER_COMMIT_GB} GB a worker (R11's guard)",
              file=sys.stderr)
    if n <= 1:
        return None, 1
    from concurrent.futures import ProcessPoolExecutor

    return ProcessPoolExecutor(max_workers=n, mp_context=multiprocessing.get_context("spawn")), n


class _WorkerEnvironment:
    """`WORKER_ENV` set while a pool's workers are started (an executor starts them as tasks are submitted), then the
    caller's environment put back; this process's own BLAS, already loaded, is untouched."""

    def __enter__(self):
        import os

        self.old = {k: os.environ.get(k) for k in WORKER_ENV}
        os.environ.update(WORKER_ENV)
        return self

    def __exit__(self, *exc):
        import os

        for k, v in self.old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        return False


def path_seeds(seed: int, n_paths: int) -> list[int]:
    """Every path's seed: the campaign seed's stream, one draw a path in path order. Path i's seed is the i-th draw
    whatever `n_paths` is, so a k-path run's paths are the first k of a longer run's."""
    rng = np.random.default_rng(seed)
    return [int(rng.integers(0, 2**31 - 1)) for _ in range(int(n_paths))]


def _one_path(protocol: Protocol, path_index: int, path_seed: int, path_kwargs: dict[str, Any],
              draw_factories_for_path: Callable[[int], tuple] | None, flip_for_path: Callable[[int], tuple] | None,
              wallet_for_path: Callable[[int], Any] | None) -> LockstepPath:
    """One path of `simulate_lockstep_campaign` from its seed: the draws the caller's factory makes for it (or the
    independent binary draws), then `simulate_lockstep_path`."""
    hook: DayHook | None = None
    if draw_factories_for_path is not None:
        made = draw_factories_for_path(path_seed)
        flip_factory = flip_spec = None
        if len(made) == 5:                            # D-339: with the flip stream's draw factory and spec
            c_factory, f_factory, hook, flip_factory, flip_spec = made
        elif len(made) == 3:
            c_factory, f_factory, hook = made
        else:
            c_factory, f_factory = made
    else:
        c_factory, f_factory = binary_draw_factories(protocol, path_kwargs["edge"], path_seed, path_kwargs["rules"])
        # D-339: the flip stream beside the binary draws, when the caller gives one (the table's campaign check)
        flip_factory, flip_spec = flip_for_path(path_seed) if flip_for_path is not None else (None, None)
    return simulate_lockstep_path(
        protocol, seed=path_seed,
        combine_draw_factory=c_factory, funded_draw_factory=f_factory, day_hook=hook,
        flip_draw_factory=flip_factory, flip=flip_spec,                                       # D-339
        wallet=wallet_for_path(path_index) if wallet_for_path is not None else None,
        **path_kwargs,
    )


def check_parallel_inputs(*inputs: Any, wallet_for_path: Any = None) -> None:
    """R11: what path workers need -- every input pickles (a lambda or closure cannot reach a spawned worker) and no
    shared wallet (D-206: a pot shared with another campaign makes the paths depend on each other). Raises ValueError."""
    import pickle

    if wallet_for_path is not None:
        raise ValueError("wallet_for_path shares one pot between campaigns, so its paths cannot run apart: workers=1")
    try:
        pickle.dumps(inputs)
    except Exception as exc:
        raise ValueError(f"workers > 1 needs every input to pickle (no lambda or closure): {exc}") from exc


def _path_chunk(task: tuple) -> tuple[list[LockstepPath], Any]:
    """A worker's share: its paths in order, and the draw factory's `export_state()` after them (None without one)."""
    protocol, path_kwargs, factories, flip_for_path, items = task
    out = [_one_path(protocol, i, s, path_kwargs, factories, flip_for_path, None) for i, s in items]
    export = getattr(factories, "export_state", None)
    return out, (export() if callable(export) else None)


def _run_paths(protocol: Protocol, path_kwargs: dict[str, Any], seeds: Sequence[int],
               draw_factories_for_path: Callable[[int], tuple] | None, flip_for_path: Callable[[int], tuple] | None,
               wallet_for_path: Callable[[int], Any] | None, *, workers: int = 1, pool: Any = None,
               memory_per_worker_gb: float | None = None) -> list[LockstepPath]:
    """The paths in path order: here, one after another (workers 1, or the guard allowing one), or split into
    contiguous chunks across a process pool and put back in order (R11)."""
    items = list(enumerate(seeds))
    if int(workers) > 1 or pool is not None:         # refused whatever the memory guard then allows
        check_parallel_inputs(protocol, path_kwargs, draw_factories_for_path, flip_for_path,
                              wallet_for_path=wallet_for_path)
    own = None
    n = 1
    if pool is not None:
        n = max(1, int(workers))
    elif int(workers) > 1 and len(items) > 1:
        own, n = path_pool(int(workers), n_tasks=len(items), memory_per_worker_gb=memory_per_worker_gb)
    if (pool is None and own is None) or len(items) <= 1:
        if own is not None:
            own.shutdown()
        return [_one_path(protocol, i, s, path_kwargs, draw_factories_for_path, flip_for_path, wallet_for_path)
                for i, s in items]
    k = min(len(items), 4 * n)                        # a few chunks a worker, so a slow chunk does not idle the rest
    bounds = [round(j * len(items) / k) for j in range(k + 1)]
    tasks = [(protocol, path_kwargs, draw_factories_for_path, flip_for_path, items[bounds[j]:bounds[j + 1]])
             for j in range(k)]
    try:
        with _WorkerEnvironment():                    # workers start during the submissions, with one BLAS thread
            futures = [(pool or own).submit(_path_chunk, task) for task in tasks]
        done = [f.result() for f in futures]
    finally:
        if own is not None:
            own.shutdown()
    results: list[LockstepPath] = []
    absorb = getattr(draw_factories_for_path, "import_state", None)
    for chunk, state in done:
        results.extend(chunk)
        if state is not None and callable(absorb):
            absorb(state)
    return results


# --------------------------------------------------------------------- the campaign


def simulate_lockstep_campaign(
    protocol: Protocol,
    *,
    edge: float,
    seed: int,
    initial_bankroll: float,
    rules: Any | None = None,
    horizon_days: int = 504,
    n_paths: int = 500,
    subscription: float | None = None,
    billing_days: int | None = None,
    activation: float | None = None,
    payout_lag_days: int | None = None,
    payout_method: str = "aeropay",
    activation_timing: str = ACTIVATION_ON_ACTIVATION,
    max_concurrent_accounts: int | None = None,
    max_concurrent_combines: int = 1,
    reinvest: bool = True,
    max_attempts: int | None = None,
    stop_buying_when_queued: bool = True,
    combine_max_days: int = 2000,
    funded_horizon_days: int = 504,
    draw_factories_for_path: Callable[[int], tuple] | None = None,
    record_trades: bool = False,
    require_verified_cap: bool = True,
    ledger: Any | None = None,
    conduct: ConductModel | None = None,
    record_days: bool = False,
    near_miss_frac: float = 0.2,
    reset_failed_combines: bool = False,
    reset_fee: float | None = None,
    risk_policy: Any = None,
    max_total_accounts: int | None = None,
    payout_timing: str = DEFAULT_PAYOUT_TIMING,
    wallet_for_path: Callable[[int], Any] | None = None,
    flip_for_path: Callable[[int], tuple] | None = None,
    funded_account_cls: type | None = None,
    household_closure: bool | None = None,
    focused_trader: FocusedTraderModel | None = None,
    purchase_budget: tuple[int, int] | None = None,
    workers: int = 1,
    pool: Any = None,
    memory_per_worker_gb: float | None = None,
    wallet_stop: float | None = None,
    pause_after_funded: int | None = None,
    seat_ramp: int | None = None,
) -> tuple[CampaignSummary, list[LockstepPath]]:
    """Run `n_paths` lockstep campaigns and summarise them exactly as `simulate_campaign` does.

    `workers` (R11): paths run in that many processes (spawn), at most what the free memory carries
    (`guarded_workers`); 1 (the default) runs them here, one after another, as before. A path depends only on its own
    seed -- the i-th draw of the campaign seed's stream (`path_seeds`) -- and the inputs, so the paths, their order and
    the summary are bit-for-bit those of one process. With workers > 1 every input must pickle (no lambda or closure:
    `draw_factories_for_path` and `flip_for_path` module-level callables), `wallet_for_path` is refused (a shared pot
    makes paths depend on each other), and the caller needs an `if __name__ == "__main__"` guard. A draw factory object
    that keeps per-path state for its caller may define `export_state()` (called in the worker after its chunk) and
    `import_state(state)` (called here, in path order); `gate._GateDraws` does. `pool`: an executor of the caller's
    (`path_pool`) to share across campaigns, with `workers` its size.

    `flip_for_path(path_seed) -> (flip_draw_factory, flip_spec)` (D-339) gives each path a flip stream beside the
    default binary draws -- the state table's campaign check runs its exported policy's flip leaves through the
    table's own binary model of the flip (`binary_flip_for_path`); a `draw_factories_for_path` five-tuple carries its
    own and ignores this.

    `record_days`, `near_miss_frac`, `reset_failed_combines` and `reset_fee` pass through to
    every path (D-146; see `simulate_lockstep_path`), as does `payout_timing` (8284233; the
    default is a request made after 5:00 PM CT), which the provenance records.
    `wallet_for_path(i)` (D-206) gives path i (0, 1, ...) a cash pot shared with another campaign
    (`simulate_lockstep_path`'s `wallet`); None: every path keeps its own cash, as before.
    `funded_account_cls` (R7) passes through to every path (`simulate_lockstep_path`); None is Topstep's
    `FundedAccount`, and only a given class is named in the provenance. `household_closure` (R7, multi-firm D-30)
    passes through too; the provenance records the reading only for a class with a household rule.
    `focused_trader` (D-495 (4); `FocusedTraderModel`) passes through to every path; the provenance names it only when
    given, so a run without it is recorded exactly as before. `purchase_budget` (D-501: `(K, window_days)`, the
    campaign's own restraint) likewise, and D-630's three entry options (`wallet_stop`, dollars; `pause_after_funded`
    and `seat_ramp`, whole numbers; `simulate_lockstep_path` says what each refuses), each passed and named only when
    given.

    Args:
        rules: engine `Rules`; stage one's defaults if omitted. Fees default to the values on
            `rules` (`subscription`, `billing_days`, `activation`) unless given.
        payout_lag_days / payout_method / max_concurrent_accounts / require_verified_cap /
            ledger: as `reinvest.simulate_campaign` -- the lag and the cap come from the
            verified ledger when not given (D-24, D-21).
        draw_factories_for_path: `f(path_seed) -> (combine_factory, funded_factory)` or
            `-> (combine_factory, funded_factory, day_hook)`; None uses independent binary
            draws at `edge` for every path. `SharedDayDraws.lockstep_kwargs()` gives the
            three as a dict if you prefer to build the tuple from it.
        record_trades: keep every path's per-trade ledger (`LockstepPath.trades`).
        conduct: D-145's tiers 2 and 3 on every path (`ConductModel`); None runs neither. The
            stage-level loop (`reinvest.simulate_campaign`) has no such switch.

    Returns:
        (summary, paths). The summary's provenance names the simulation as lockstep.
    """
    from propedge.contract.adapter import Rules

    check_payout_timing(payout_timing)
    rules = rules or Rules()
    subscription = float(rules.subscription if subscription is None else subscription)
    billing_days = int(rules.billing_days if billing_days is None else billing_days)
    activation = float(rules.activation if activation is None else activation)

    need_ledger = (max_concurrent_accounts is None and require_verified_cap) or (
        payout_lag_days is None
    )
    if need_ledger and ledger is None:
        from propedge.contract.rules import load_rules

        ledger = load_rules()
    if max_concurrent_accounts is None:
        if require_verified_cap:
            max_concurrent_accounts = int(ledger.value("max_active_funded_accounts"))
        else:
            max_concurrent_accounts = protocol.max_concurrent_accounts
    if payout_lag_days is None:
        from propedge.campaign.payout_method import payout_method_terms

        terms = payout_method_terms(payout_method, ledger=ledger)
        payout_lag_days = terms.lag_days
        lag_source = f"ledger {terms.lag_key} (article {terms.article_id})"
    else:
        lag_source = "explicit argument"

    path_kwargs = dict(
        edge=edge, rules=rules,
        initial_bankroll=initial_bankroll, horizon_days=horizon_days,
        max_concurrent_accounts=max_concurrent_accounts,
        subscription=subscription, billing_days=billing_days, activation=activation,
        payout_lag_days=int(payout_lag_days),
        max_concurrent_combines=max_concurrent_combines, reinvest=reinvest,
        max_attempts=max_attempts, stop_buying_when_queued=stop_buying_when_queued,
        activation_timing=activation_timing, combine_max_days=combine_max_days,
        funded_horizon_days=funded_horizon_days,
        record_trades=record_trades, conduct=conduct,
        record_days=record_days, near_miss_frac=near_miss_frac,
        reset_failed_combines=reset_failed_combines, reset_fee=reset_fee,
        risk_policy=risk_policy, max_total_accounts=max_total_accounts,
        payout_timing=payout_timing,
        funded_account_cls=funded_account_cls,                                  # R7
        household_closure=household_closure,                                    # R7 (multi-firm D-30)
    )
    if focused_trader is not None:                        # D-495 (4): passed only when given
        path_kwargs["focused_trader"] = focused_trader
    if purchase_budget is not None:                       # D-501: passed only when given
        budget = check_purchase_budget(purchase_budget)
        path_kwargs["purchase_budget"] = budget
    entry: dict[str, Any] = {}                            # D-630: each passed only when given
    if wallet_stop is not None:
        entry["wallet_stop"] = check_wallet_stop(wallet_stop)
    if pause_after_funded is not None:
        entry["pause_after_funded"] = check_pause_after_funded(pause_after_funded)
    if seat_ramp is not None:
        entry["seat_ramp"] = check_seat_ramp(seat_ramp, max_total_accounts)
    path_kwargs.update(entry)
    seeds = path_seeds(seed, n_paths)
    results = _run_paths(protocol, path_kwargs, seeds, draw_factories_for_path, flip_for_path, wallet_for_path,
                         workers=workers, pool=pool, memory_per_worker_gb=memory_per_worker_gb)

    provenance_extra: dict[str, Any] = {}
    if funded_account_cls is not None:                    # R7: named only when given, so Topstep's provenance is as before
        provenance_extra["funded_account_cls"] = f"{funded_account_cls.__module__}.{funded_account_cls.__qualname__}"
        if hasattr(funded_account_cls, "HOUSEHOLD_CLOSES_AT_LIVE"):      # R7 (multi-firm D-30): the reading taken
            provenance_extra["household_closure"] = bool(
                funded_account_cls.HOUSEHOLD_CLOSES_AT_LIVE if household_closure is None else household_closure)
    if focused_trader is not None:                        # D-495 (4): named only when given
        provenance_extra["focused_trader"] = {"decision": "D-495", **focused_trader.as_dict()}
    if purchase_budget is not None:                       # D-501: named only when given
        provenance_extra["purchase_budget"] = {"decision": "D-501", "k": budget[0], "window_days": budget[1]}
    for name, value in entry.items():                     # D-630: named only when given
        provenance_extra[name] = {"decision": "D-630", "value": value}
    summary = summarise_paths(
        [r.path for r in results],
        protocol=protocol, edge=edge, seed=seed, initial_bankroll=initial_bankroll,
        horizon_days=horizon_days, n_paths=n_paths, payout_lag_days=int(payout_lag_days),
        payout_schedule="exact (lockstep, trade-level)",
        max_concurrent_accounts=int(max_concurrent_accounts),
        payout_method=payout_method, activation_timing=activation_timing,
        provenance={
            "simulation": "propedge.campaign.lockstep.simulate_lockstep_campaign",
            "subscription": subscription,
            "billing_days": billing_days,
            "activation": activation,
            "activation_timing": activation_timing,
            "payout_method": payout_method,
            "payout_lag_source": lag_source,
            "reinvest": reinvest,
            "max_concurrent_combines": max_concurrent_combines,
            "max_attempts": max_attempts,
            "combine_max_days": combine_max_days,
            "funded_horizon_days": funded_horizon_days,
            "conduct": None if conduct is None else {"decision": "D-145", **conduct.as_dict()},
            "payout_timing": payout_timing,
            "payout_timing_note": PAYOUT_TIMING_NOTES[payout_timing],
            "draws": (
                "independent binary draws per account (validation limit)"
                if draw_factories_for_path is None
                else "caller-supplied draw factories"
            ),
            "note": (
                "Every account is stepped through each calendar day by its own state machine "
                "(Combine and funded rules as the vendored engine applies them). With "
                "independent streams this reproduces reinvest.simulate_path exactly "
                "(tests/test_lockstep.py)."
            ),
            **provenance_extra,
        },
    )
    return summary, results


__all__ = [
    "EPS",
    "ConductModel",
    "FocusedTraderModel",
    "check_purchase_budget",
    "check_wallet_stop",
    "check_pause_after_funded",
    "check_seat_ramp",
    "FTP_SLOWDOWN",
    "FTP_CORRECTIVE",
    "FTP_PATHS",
    "CombineAccount",
    "FundedAccount",
    "CombineRecord",
    "FundedRecord",
    "LockstepPath",
    "DrawFactory",
    "DayHook",
    "child_seed",
    "binary_draw_factories",
    "simulate_lockstep_path",
    "simulate_lockstep_campaign",
    "WORKER_MEMORY_GB",
    "available_memory_gb",
    "guarded_workers",
    "path_pool",
    "path_seeds",
    "check_parallel_inputs",
    "WORKER_COMMIT_GB",
    "WORKER_ENV",
    "available_commit_gb",
]
