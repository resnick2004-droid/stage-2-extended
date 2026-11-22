"""Q-169 (the restart plan's Wave 3.3, rest): the mix router -- which of the user's accounts takes each scheduled trade
(lever table A15, routing; A16's account assignment), with accounts alternating (E-221, the operator's O-4 ruling).

    from extended import router as R
    days = [components.schedule_day(d, hist, i, ctx, unit) for d in designs]     # one per firm
    routed = R.Router(R.Routing("longest_waiting", firm="topstep")).route(days, {"topstep": ("ts1", "ts2")},
                                                                           date=ctx.date)

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
| `by_component` | A16's assignment: each component's trades go to its pool of the firm's accounts, **dealt by the router each day** (`lever_space.deal_pools` over `Routing.components`, **the `Design`'s components in the order of their windows' first slots**, and the firm's accounts in opening order), longest-waiting inside the pool |

**A16's pools are the router's, never the caller's** (the red team's L-M2, the lead's order): `Routing` takes no pools,
and `by_component` takes **the `Design`** (`design=`), whose components, sorted by their windows' first slots (ties by
name), are the order the pools are dealt in (the red team's m5): a caller's `components` in another order is refused,
a mapping of hand-built pools is refused, and so is `by_component` without a design (it would route exactly as
`longest_waiting`, a second cell of the base under another name). A trade of a component not in the design is
refused. **The opening order** (L-m1): an account's index is the date (one route call per date, n5) on which the
router first sees it among its firm's accounts, ties broken by account id; the pools are dealt over the accounts
sorted by that index, so the caller's order on a later day changes no pool. The caller passes each day every account
it holds, an account first on the day it is opened.

**The firm** (the red team's n4, the lead's ruling): a `Routing` names its firm (`firm=`, one of
`lever_space.FIRMS`, which is also the firm of its schedules and its accounts), and is refused unless that firm's own
A15 (and, for `by_component`, A16) is declared (`lever_space.require_declared`): MFFU's and Lucid's are to declare for
those firms (Q-181c), so Topstep's rotation never routes their accounts. A `Router` holds one routing per firm; a
schedule or an account of a firm without one is refused. **One call per date** (n5): `route(..., date=)` names the
trading day, every schedule passed is that day's, and a second call for a date already routed is refused.

An account's last trade "ends" at the trade's busy time (`ScheduledTrade.busy_until`: its exit, or a tie's later exit),
on the absolute clock (session x 1440 + minute). **The router reads no bar:** an assignment depends on the order of
the scheduled trades and the busy times of earlier ones, each known before the trade goes live (the chain's five
minutes flat), so it inherits the schedule's causality (`tests/test_router.py`'s shift test).

**Not here:** A16's shares on the simplex over the sources (declared derived: a source's share is its components',
T1 per component, so no share parameter exists), and which accounts exist on a day (the journey engine's: evaluations
bought, passed, failed -- the caller passes each day's accounts).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date as Date
from types import SimpleNamespace
from typing import Any, Mapping, Sequence

from extended import components as C
from extended import lever_space as LS
from extended import triggers as T

TASK = "Q-169"
#: lever table A15's declared values (A16's account assignment is `by_component`'s pools)
ROTATIONS = ("longest_waiting", "round_robin", "by_component")


class RoutingRefused(ValueError):
    """A routing this module cannot stand behind (a rotation not declared, a firm whose rows are to declare, a pool
    naming an account the firm does not hold, a firm with no account, a date routed twice)."""


def window_order(design: C.Design) -> tuple[str, ...]:
    """The design's component names in the order of their windows' first slots, ties by name (m5)."""
    return tuple(c.name for c in sorted(design.components, key=lambda c: (int(c.first), str(c.name))))


@dataclass(frozen=True)
class Routing:
    """A15's rotation for one firm (`firm`, n4) and, for `by_component`, the `Design` whose components, in the order of
    their windows' first slots (`window_order`, m5), the router deals A16's pools over each day
    (`lever_space.deal_pools`). `components`, when given, must be that order."""

    rotation: str = "longest_waiting"
    components: Any = ()
    firm: str = field(kw_only=True)
    design: Any = field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        if self.rotation not in ROTATIONS:
            raise RoutingRefused(f"rotation {self.rotation!r} is not one of the declared values {ROTATIONS} (A15)")
        rows = ("A15", "A16") if self.rotation == "by_component" else ("A15",)
        try:
            LS.require_declared(self.firm, rows)
        except LS.LeverRefused as exc:
            raise RoutingRefused(f"routing refused: {exc}") from None
        if isinstance(self.components, Mapping):
            raise RoutingRefused("hand-built pools are refused: the router deals A16's pools itself (deal_pools)")
        comps = tuple(self.components)
        if any(not isinstance(c, str) or not c for c in comps) or len(set(comps)) != len(comps):
            raise RoutingRefused(f"by_component's components are distinct names, got {comps}")
        if self.rotation != "by_component":
            if comps or self.design is not None:
                raise RoutingRefused("components and a design are `by_component`'s (A16); another rotation takes none")
            object.__setattr__(self, "components", ())
            return
        if not isinstance(self.design, C.Design):
            raise RoutingRefused("by_component deals over the Design's components (m5): without one it would route "
                                 "as longest_waiting, or in a caller's order -- refused (A15, A16)")
        if self.design.firm != self.firm:
            raise RoutingRefused(f"the design is {self.design.firm!r}'s, the routing {self.firm!r}'s")
        order = window_order(self.design)
        if comps and comps != order:
            raise RoutingRefused(f"components {comps} are not the design's window order {order} (m5): refused")
        object.__setattr__(self, "components", order)


@dataclass(frozen=True)
class RoutedTrade:
    """A scheduled trade and the one account that takes it."""

    trade: C.ScheduledTrade
    account: str


class Router:
    """The router's state across days: each (firm, account)'s last busy minute and each firm's last account. `routing`
    is one firm's `Routing`, or a mapping firm -> its `Routing` (each keyed by its own firm)."""

    def __init__(self, routing: Routing | Mapping[str, Routing], book: C.UserBook | None = None):
        if isinstance(routing, Routing):
            routings = {routing.firm: routing}
        elif isinstance(routing, Mapping) and routing:
            routings = dict(routing)
            for firm, r in routings.items():
                if not isinstance(r, Routing) or r.firm != firm:
                    raise RoutingRefused(f"the routing under {firm!r} is not that firm's Routing")
        else:
            raise RoutingRefused("a router takes a Routing, or a mapping firm -> Routing")
        self.routings: dict[str, Routing] = routings
        self.book = book if book is not None else C.UserBook()
        self.last_busy: dict[tuple[str, str], int] = {}
        self.last_account: dict[str, str] = {}
        self.opened: dict[tuple[str, str], int] = {}      # (firm, account) -> the date index it was first seen on
        self.routed: list[str] = []                       # the dates routed, one call each (n5)
        self.day_no = 0

    def _routing(self, firm: str) -> Routing:
        r = self.routings.get(firm)
        if r is None:
            raise RoutingRefused(f"no routing for firm {firm!r} (this router's: {sorted(self.routings)}; n4)")
        return r

    def _see(self, accounts: Mapping[str, Sequence[str]]) -> None:
        for firm, accs in accounts.items():
            for a in accs:
                self.opened.setdefault((firm, a), self.day_no)

    def dealt_pools(self, firm: str, accounts: Sequence[str], *,
                    opened: Mapping[str, int] | None = None) -> dict[str, tuple[str, ...]]:
        """A16: `by_component`'s pools of `firm` over `accounts`, dealt in opening order (index, then account id);
        `opened` (account -> index), when given, is used instead of this router's own (`peek`'s: nothing is written)."""
        routing = self._routing(firm)
        if routing.rotation != "by_component":
            raise RoutingRefused("pools are by_component's")
        index = {a: self.opened[(firm, a)] for a in accounts if (firm, a) in self.opened} if opened is None             else dict(opened)
        unseen = [a for a in accounts if a not in index]
        if unseen:
            raise RoutingRefused(f"accounts {unseen} of {firm} were never passed to route: no opening index")
        try:
            return LS.deal_pools(routing.components, accounts, firm=routing.firm,
                                 opened={a: index[a] for a in accounts})
        except LS.LeverRefused as exc:
            raise RoutingRefused(str(exc)) from None

    def _pick(self, tr: C.ScheduledTrade, accounts: Sequence[str], *,
              opened: Mapping[str, int] | None = None) -> str:
        routing = self._routing(tr.firm)
        rot = routing.rotation
        if rot == "round_robin":
            prev = self.last_account.get(tr.firm)
            if prev in accounts:
                return accounts[(list(accounts).index(prev) + 1) % len(accounts)]
            return accounts[0]
        pool = list(accounts)
        if rot == "by_component":
            pools = self.dealt_pools(tr.firm, accounts, opened=opened)
            if tr.component not in pools:
                raise RoutingRefused(f"component {tr.component} is not one of by_component's {routing.components}")
            pool = list(pools[tr.component])
        order = {a: k for k, a in enumerate(accounts)}
        return min(pool, key=lambda a: (self.last_busy.get((tr.firm, a), -1), order[a]))

    def peek(self, firm: str, component: str, accounts: Sequence[str]) -> str:
        """The account the next trade of `component` at `firm` would take now, among `accounts` (those alive today),
        by the rotation and this router's state, **changing nothing** (the playbook's alert, Wave 3.5's m-5 and N-c2-1):
        an account this router has not yet seen is given the opening index `route` would give it today."""
        accs = tuple(accounts)
        if not accs or len(set(accs)) != len(accs):
            raise RoutingRefused(f"{firm}'s accounts are empty or repeat: {accs}")
        opened = {a: self.opened.get((firm, a), self.day_no) for a in accs}
        return self._pick(SimpleNamespace(firm=firm, component=component), accs, opened=opened)

    def route(self, days: Sequence[C.DaySchedule], accounts: Mapping[str, Sequence[str]], *,
              date: str | Date) -> list[RoutedTrade]:
        """Route trading day `date`'s schedules (one per firm) to the firms' accounts that day, in time order; each
        trade's possible positions go to the user's book under its account (refusing opposite positions as tier 1, any
        other overlap as undefined). One call per date (n5): a date already routed is refused, and so is a schedule of
        another date or of a firm without a routing (n4)."""
        if isinstance(date, Date):
            date = date.isoformat()
        if not isinstance(date, str) or not date:
            raise RoutingRefused(f"route names its trading day's date, got {date!r}")
        if date in self.routed:
            raise RoutingRefused(f"{date} is already routed: one route call per date (the red team's n5)")
        for d in days:
            self._routing(d.firm)
            if d.date != date:
                raise RoutingRefused(f"a schedule of {d.date} passed to route {date}")
        for firm in accounts:
            self._routing(firm)
        self.routed.append(date)
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


__all__ = ["TASK", "ROTATIONS", "RoutingRefused", "window_order", "Routing", "RoutedTrade", "Router"]
