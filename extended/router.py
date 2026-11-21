"""Q-169 (the restart plan's Wave 3.3, rest): the mix router -- which of the user's accounts takes each scheduled trade
(lever table A15, routing; A16's account assignment), with accounts alternating (E-221, the operator's O-4 ruling).

    from extended import router as R
    days = [components.schedule_day(d, hist, i, ctx, unit) for d in designs]     # one per firm
    routed = R.Router(R.Routing("longest_waiting")).route(days, {"ts": ("ts1", "ts2"), "mffu": ("m1",)})

**What it does.** Each firm's day is already chained one position (or working order) at a time across the firm
(`components.schedule_day`; Stage 2 D-429). The router gives each of those trades **one** of that firm's accounts --
never several: copying one trade to every account correlates their failures and defeats the fee asymmetry (E-221).
Its trades are taken in time order (session, fill minute, firm order), and every position the user may hold from a
trade (`components.positions_of`: on a same-bar tie, either ticket's, both sides, to the later exit, the re-read's m-1)
is added to the user's book (`components.UserBook`) under the account it lands on. The book refuses two positions
held at once: **opposite sides across accounts or firms as conduct tier 1** (`TierOneRefused`), the same side as an
overlap the search template has not defined (`OverlapRefused`). A refusal is a property of the design on that day,
never a reason to drop the day.

**The rotation (A15; declared values, `ROTATIONS`):**

| value | which account takes the next trade of a firm |
|---|---|
| `longest_waiting` | the base (Stage 2 D-429): the account whose last trade ended longest ago (never-used first; ties in the account order) |
| `round_robin` | the account after the one that took the firm's last trade, in the account order (the first when that one is gone) |
| `by_component` | A16's assignment: each component's trades go to its declared pool of the firm's accounts (`Routing.pools`; a component without a pool uses every account), longest-waiting inside the pool |

An account's last trade "ends" at the trade's busy time (`ScheduledTrade.busy_until`: its exit, or a tie's later exit),
on the absolute clock (session x 1440 + minute). **The router reads no bar:** an assignment depends on the order of
the scheduled trades and the busy times of earlier ones, each known before the trade goes live (the chain's five
minutes flat), so it inherits the schedule's causality (`tests/test_router.py`'s shift test).

**Not here:** A16's shares on the simplex over the sources (a design's components fix which source trades when; a
share rule is the search template's to declare), and which accounts exist on a day (the journey engine's: evaluations
bought, passed, failed -- the caller passes each day's accounts).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Mapping, Sequence

from extended import components as C
from extended import triggers as T

TASK = "Q-169"
#: lever table A15's declared values (A16's account assignment is `by_component`'s pools)
ROTATIONS = ("longest_waiting", "round_robin", "by_component")


class RoutingRefused(ValueError):
    """A routing this module cannot stand behind (a rotation not declared, a pool naming an account the firm does not
    hold, a firm with no account)."""


@dataclass(frozen=True)
class Routing:
    """A15's rotation and, for `by_component`, A16's pools: component name -> the accounts its trades may take."""

    rotation: str = "longest_waiting"
    pools: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.rotation not in ROTATIONS:
            raise RoutingRefused(f"rotation {self.rotation!r} is not one of the declared values {ROTATIONS} (A15)")
        if self.pools and self.rotation != "by_component":
            raise RoutingRefused("pools are `by_component`'s assignment (A16); another rotation takes none")
        for name, pool in self.pools.items():
            if not pool or len(set(pool)) != len(pool):
                raise RoutingRefused(f"component {name}'s pool is empty or repeats an account")


@dataclass(frozen=True)
class RoutedTrade:
    """A scheduled trade and the one account that takes it."""

    trade: C.ScheduledTrade
    account: str


class Router:
    """The router's state across days: each (firm, account)'s last busy minute and each firm's last account."""

    def __init__(self, routing: Routing, book: C.UserBook | None = None):
        self.routing = routing
        self.book = book if book is not None else C.UserBook()
        self.last_busy: dict[tuple[str, str], int] = {}
        self.last_account: dict[str, str] = {}

    def _pick(self, tr: C.ScheduledTrade, accounts: Sequence[str]) -> str:
        rot = self.routing.rotation
        if rot == "round_robin":
            prev = self.last_account.get(tr.firm)
            if prev in accounts:
                return accounts[(list(accounts).index(prev) + 1) % len(accounts)]
            return accounts[0]
        pool = list(accounts)
        if rot == "by_component" and tr.component in self.routing.pools:
            pool = list(self.routing.pools[tr.component])
            missing = [a for a in pool if a not in accounts]
            if missing:
                raise RoutingRefused(f"component {tr.component}'s pool names {missing}, not accounts of {tr.firm} today")
        order = {a: k for k, a in enumerate(accounts)}
        return min(pool, key=lambda a: (self.last_busy.get((tr.firm, a), -1), order[a]))

    def peek(self, firm: str, component: str, accounts: Sequence[str]) -> str:
        """The account the next trade of `component` at `firm` would take now, by the rotation and this router's state
        (each account's last busy minute, the firm's last account), changing nothing -- the account a hand-traded
        alert names (the lead's m-5 ruling on Wave 3.5); the trade is routed (`route`) once it exists."""
        accs = tuple(accounts)
        if not accs or len(set(accs)) != len(accs):
            raise RoutingRefused(f"{firm}'s accounts are empty or repeat: {accs}")
        return self._pick(SimpleNamespace(firm=firm, component=component), accs)

    def route(self, days: Sequence[C.DaySchedule], accounts: Mapping[str, Sequence[str]]) -> list[RoutedTrade]:
        """Route one day's schedules (one per firm) to the firms' accounts today, in time order; each trade's possible
        positions go to the user's book under its account (refusing opposite positions as tier 1, any other overlap
        as undefined)."""
        firm_order = {d.firm: k for k, d in enumerate(days)}
        trades = sorted((t for d in days for t in d.trades),
                        key=lambda t: (int(t.session), int(t.fill_slot), firm_order[t.firm]))
        out = []
        for tr in trades:
            accs = tuple(accounts.get(tr.firm, ()))
            if not accs:
                raise RoutingRefused(f"{tr.firm} holds no account today: its trade at {tr.fill_slot} has nowhere to go")
            if len(set(accs)) != len(accs):
                raise RoutingRefused(f"{tr.firm}'s accounts repeat: {accs}")
            acct = self._pick(tr, accs)
            self.book.extend(C.positions_of(tr, acct))
            self.last_busy[(tr.firm, acct)] = int(tr.session) * T.DAY_SLOTS + int(tr.busy_until)
            self.last_account[tr.firm] = acct
            out.append(RoutedTrade(tr, acct))
        return out


__all__ = ["TASK", "ROTATIONS", "RoutingRefused", "Routing", "RoutedTrade", "Router"]
