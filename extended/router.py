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
| `by_component` | A16's assignment: each component's trades go to its pool of the firm's accounts, **dealt by the router each day** (`lever_space.deal_pools` over `Routing.components`, the design's components in window order, and the firm's accounts in opening order), longest-waiting inside the pool |

**A16's pools are the router's, never the caller's** (the red team's L-M2, the lead's order): `Routing` takes no pools,
only `by_component`'s component names; a mapping of hand-built pools is refused, and so is `by_component` without
components (it would route exactly as `longest_waiting`, a second cell of the base under another name). A trade of a
component not named is refused. **The opening order** (L-m1): an account's index is the route call (the day) on which
the router first sees it among its firm's accounts, ties broken by account id; the pools are dealt over the accounts
sorted by that index, so the caller's order on a later day changes no pool. The caller passes each day every account
it holds, an account first on the day it is opened.

An account's last trade "ends" at the trade's busy time (`ScheduledTrade.busy_until`: its exit, or a tie's later exit),
on the absolute clock (session x 1440 + minute). **The router reads no bar:** an assignment depends on the order of
the scheduled trades and the busy times of earlier ones, each known before the trade goes live (the chain's five
minutes flat), so it inherits the schedule's causality (`tests/test_router.py`'s shift test).

**Not here:** A16's shares on the simplex over the sources (declared derived: a source's share is its components',
T1 per component, so no share parameter exists), and which accounts exist on a day (the journey engine's: evaluations
bought, passed, failed -- the caller passes each day's accounts).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from extended import components as C
from extended import lever_space as LS
from extended import triggers as T

TASK = "Q-169"
#: lever table A15's declared values (A16's account assignment is `by_component`'s pools)
ROTATIONS = ("longest_waiting", "round_robin", "by_component")


class RoutingRefused(ValueError):
    """A routing this module cannot stand behind (a rotation not declared, a pool naming an account the firm does not
    hold, a firm with no account)."""


@dataclass(frozen=True)
class Routing:
    """A15's rotation and, for `by_component`, the design's components in the order of their windows' first slots,
    over which the router deals A16's pools each day (`lever_space.deal_pools`)."""

    rotation: str = "longest_waiting"
    components: Any = ()

    def __post_init__(self) -> None:
        if self.rotation not in ROTATIONS:
            raise RoutingRefused(f"rotation {self.rotation!r} is not one of the declared values {ROTATIONS} (A15)")
        if isinstance(self.components, Mapping):
            raise RoutingRefused("hand-built pools are refused: the router deals A16's pools itself (deal_pools)")
        comps = tuple(self.components)
        if any(not isinstance(c, str) or not c for c in comps) or len(set(comps)) != len(comps):
            raise RoutingRefused(f"by_component's components are distinct names, got {comps}")
        if self.rotation == "by_component" and not comps:
            raise RoutingRefused("by_component without components would route as longest_waiting: refused (A15, A16)")
        if comps and self.rotation != "by_component":
            raise RoutingRefused("components are `by_component`'s (A16); another rotation takes none")
        object.__setattr__(self, "components", comps)


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
        self.opened: dict[tuple[str, str], int] = {}      # (firm, account) -> the route call it was first seen on
        self.day_no = 0

    def _see(self, accounts: Mapping[str, Sequence[str]]) -> None:
        for firm, accs in accounts.items():
            for a in accs:
                self.opened.setdefault((firm, a), self.day_no)

    def dealt_pools(self, firm: str, accounts: Sequence[str]) -> dict[str, tuple[str, ...]]:
        """A16: `by_component`'s pools of `firm` over `accounts`, dealt in opening order (index, then account id)."""
        if self.routing.rotation != "by_component":
            raise RoutingRefused("pools are by_component's")
        unseen = [a for a in accounts if (firm, a) not in self.opened]
        if unseen:
            raise RoutingRefused(f"accounts {unseen} of {firm} were never passed to route: no opening index")
        try:
            return LS.deal_pools(self.routing.components, accounts,
                                 opened={a: self.opened[(firm, a)] for a in accounts})
        except LS.LeverRefused as exc:
            raise RoutingRefused(str(exc)) from None

    def _pick(self, tr: C.ScheduledTrade, accounts: Sequence[str]) -> str:
        rot = self.routing.rotation
        if rot == "round_robin":
            prev = self.last_account.get(tr.firm)
            if prev in accounts:
                return accounts[(list(accounts).index(prev) + 1) % len(accounts)]
            return accounts[0]
        pool = list(accounts)
        if rot == "by_component":
            pools = self.dealt_pools(tr.firm, accounts)
            if tr.component not in pools:
                raise RoutingRefused(f"component {tr.component} is not one of by_component's {self.routing.components}")
            pool = list(pools[tr.component])
        order = {a: k for k, a in enumerate(accounts)}
        return min(pool, key=lambda a: (self.last_busy.get((tr.firm, a), -1), order[a]))

    def route(self, days: Sequence[C.DaySchedule], accounts: Mapping[str, Sequence[str]]) -> list[RoutedTrade]:
        """Route one day's schedules (one per firm) to the firms' accounts today, in time order; each trade's possible
        positions go to the user's book under its account (refusing opposite positions as tier 1, any other overlap
        as undefined)."""
        self._see(accounts)
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
        self.day_no += 1
        return out


__all__ = ["TASK", "ROTATIONS", "RoutingRefused", "Routing", "RoutedTrade", "Router"]
