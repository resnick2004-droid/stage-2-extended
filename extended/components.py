"""Q-152 (the restart plan's Wave 3.3, first part): the component scheduler -- a design as a schedule of components
across the firm's sessions, chained one position at a time across the firm, with the user-wide guards of conduct tier 1.

    from extended import components as C, triggers as T
    rl3 = C.Component("am_rl3", "ny_am", 960, 1015, T.RL3Tickets("pd", T.RL3_CUTOFFS[0]), stop_ticks=100, rr=1.5)
    design = C.Design("topstep", (rl3, C.Component("pm_brk", "ny_pm", 1080, 1260, T.P14Breakout(), 100, 1.0)))
    day = C.schedule_day(design, hist, i, ctx, unit)             # one firm's day: trades, refusals, skips, unfilled
    book = C.schedule_user((design_a, design_b), hist, i, ctx, unit)   # every firm's day, guarded across them

**A component** (CHARTER 2's term; lever table T1-T3) is one trigger (`extended.triggers`) with its trade shape (a stop
in ticks and one reward-to-risk) over an offer window [first, last] of the trading-day clock inside one session of the
firm's day (lever table T2, `lever_space.session_windows`). An offer belongs to a component when its order goes live
inside the window.

**A design** (`Design`) is one firm's components. It refuses, at construction:
* two components whose windows collide (CHARTER 3.5: "Components' windows are scheduled not to collide");
* a window outside its session or outside the firm's day (from `trading_hours`' reopen to its last new entry,
  `lever_space.trading_day`). **NY has three names** (the red team's m1, the lead's ruling): `ny_am` and `ny_pm`
  are strict at T2b's split (noon New York, `lever_space.session_windows` splits at it on each date), and `ny` is the
  whole NY session, for a design whose window crosses noon -- the registered baselines' whole-NY windows name `ny`. A
  searched design uses the split forms only (`search_space.from_lever_space` refuses `ny`, m2);
* any overlap mode but `refused`: a design holding two positions of the user at once is refused until the search
  template defines overlap (`docs/plans/THREE_WAY_TEST_design.md` 1.6).

**The chain** (`schedule_day`; Stage 2 D-429; F-04 5.5, the lead's ruling on B-3): the firm's offers of the day, every
component's, admitted by `triggers.admit`, are taken in order of their live slot, one group at a time (an offer alone,
or RL3's one-cancels-other tickets of a kind). An order is placed only when **the firm is flat, no other entry order is
working, and at least five minutes have passed since the last position's exit**; otherwise the offer is skipped and
counted by the firm's state at its live minute (`order` while an entry order works, `position` while a position is
open, `gap` in the five minutes after its exit; corrective cycle 1, M-7). A placed group's sides are drawn from the
coin (`triggers.coin_side`), each member is executed (`triggers.execute`), and the earliest fill is the position; the
others are cancelled at that fill.
* **An unfilled group keeps the firm busy until the last of its working stretches ends** (`Execution.busy_until`): a
  stretch cancelled at its cutoff or a window's start, and a re-written ticket that the re-write finds void, which
  waited through the window for it (corrective cycle 1, B-1: freeing the firm from the void's first live made a later
  offer's placement depend on the price after the window).
* **Two members filling on one bar** (the order of their fills inside the bar is unknown) book the member whose walked
  trade is worse for the user -- the lower gross, the walk settling a two-barrier bar stop first; then the later exit;
  then the lower sub -- flagged `oco_tie`, the other counted `oco_tie_cancelled`; never no trade. The firm stays busy
  to the later of the two walked exits (`busy_until`), so no later offer's placement depends on which one is booked,
  an outcome decided after that offer's moment (**the M-6 ruling (lead)**: E-223's booking, its busy time amended by
  the lead to the later exit, E-223's "busy to its exit" being a look-ahead as worded). In the user's book a tie is
  either ticket's position, both sides, over [fill, busy_until) (`positions_of`; the re-read's m-1, conduct tier 1).
* **A day whose bars end before the walk's end** (`W.last_bar` before `rules.walk_end`: under `JOURNEY`, no bar
  stamped 15:07 CT or later) is refused (`DayRefused`) unless the caller voided it (`DayContext.void`, or an FOMC day):
  the walker's last fill bar is the bar before its walk's end, so on such a day a fill would depend on whether later
  bars exist (the re-read's m-3). The void condition: an early close or a data defect on the pinned calendar.

The chain is fixed by the walks as run (the run's exit times), before any redraw (the design note 1.6: overlap is
decided on the scheduled entries and the run's exits, never the path's). Every decision -- placed, skipped and why,
refused -- depends on bars before its own moment only (`tests/test_components.py`'s decision shift test, M-5).

**The user's book** (`UserBook`, `schedule_user`): every position of the user, on every firm and account. Adding one
that overlaps another in time is refused -- **opposite sides as conduct tier 1** (`TierOneRefused`: no hedging across
accounts or firms, CHARTER 3.4, 4), the same side as an overlap the template has not defined (`OverlapRefused`). Two
positions overlap when their holding intervals [open, close) on the absolute clock intersect: the open is the fill bar's
open minute, the close the exit bar's end. Inside one firm the chain makes overlap impossible; across firms the book
refuses the design. A tie's alternatives (`positions_of`) are each checked against every other position; a
refusal is a property of the design on that day, never a reason to drop the day (the re-read's n-6).

**The schedule's fields** (`ScheduledTrade`; the design note 1.7): firm, component and source; the session, its date;
the decision, alert and live slots; the order kind (and a ticket's fade or break); the side and its source (`coin`);
the fill's minute and price; the bracket (stop and target ticks, R); the exit's minute and kind; the flatten slot and
whether it is a window's; the instrument and underlying; the gross ticks and, with costs, the net R; whether it was
booked from a same-bar tie, and the minute the firm stays busy to (its exit, or a tie's later exit). The causal
volatility of the holding window (the shared path's clock) is not computed here: it is the three-way runner's.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from typing import Iterable, Sequence

from extended import day_calendar as DC
from extended import lever_space as LS
from extended import triggers as T
from extended import walker as W

TASK = "Q-152"
OVERLAP_MODES = ("refused",)
SKIP_REASONS = ("position", "order", "gap")


class DesignRefused(ValueError):
    """A design this scheduler cannot stand behind (a collision, a window off its session, an undefined overlap)."""


class OverlapRefused(RuntimeError):
    """Two positions of the user held at once, on the same side: refused until the search template defines overlap."""


class TierOneRefused(RuntimeError):
    """Two opposite positions of the user held at once, across accounts or firms: conduct tier 1."""


class DayRefused(RuntimeError):
    """A day the caller did not void whose bars end before the walk's end (m-3): the walker's last fill bar would
    depend on whether later bars exist."""


# ------------------------------------------------------------------------------------------------ components and designs


@dataclass(frozen=True)
class Component:
    """One trigger with its trade shape over an offer window [first, last] (slots; the order's live slot) of one
    session (`lever_space` T2's names)."""

    name: str
    session: str
    first: int
    last: int
    trigger: object
    stop_ticks: int
    rr: float
    instrument: str = "MNQ"

    def __post_init__(self) -> None:
        if not 0 <= int(self.first) <= int(self.last):
            raise DesignRefused(f"component {self.name}: a window is first <= last, got {self.first}, {self.last}")
        if int(self.stop_ticks) <= 0 or float(self.rr) <= 0:
            raise DesignRefused(f"component {self.name}: a stop and an R are positive")
        if self.instrument not in T.UNDERLYING:
            raise DesignRefused(f"component {self.name}: unknown instrument {self.instrument!r}")
        if not hasattr(self.trigger, "offers") or getattr(self.trigger, "source", None) not in T.SOURCES:
            raise DesignRefused(f"component {self.name}: its trigger is not one of the library's sources {T.SOURCES}")

    @property
    def target_ticks(self) -> int:
        return W.target_ticks(self.rr, self.stop_ticks)


def session_windows_of(day: date) -> dict[str, tuple[int, int | None]]:
    """**The one function every session window is read through** (Q-169 (5)): trading day `day`'s sessions as
    [start, end) in minutes after the reopen, from `lever_space.session_windows(day)` -- each start its local market
    time converted for that date (E-231 (3), `day_calendar.anchored_starts`). Nothing else reads them."""
    return LS.session_windows(day)


def session_bounds(day: date | None = None) -> dict[str, tuple[int, int]]:
    """Each session's [start, end) in trading-day slots from the firm's day (`session_windows_of`, minutes after the
    reopen): `ny_am` and `ny_pm` strict at T2b's split, `ny` the whole NY session (from `ny_am`'s start to `ny_pm`'s
    end; the red team's m1); and the day's last new entry. The clock is 17:00-based: a firm reopening at another time is
    refused.

    The session starts are anchored to their local market times per date (E-231 (3)). With `day`, that trading day's
    sessions; without, **the bounds that hold on every weekday of the search years** (`day_calendar.SEARCH_START` to
    `SEARCH_END`): each session from its latest start to its earliest end, so a window inside them is inside its session
    on every date."""
    td = LS.trading_day()
    if int(td["reopen"]) != 17 * 60:
        raise DesignRefused("the trading-day clock starts at 17:00 CT; this firm reopens at another time")
    days = [day] if day is not None else LS.trading_dates(DC.SEARCH_START, DC.SEARCH_END)
    out: dict[str, tuple[int, int]] = {}
    for d in days:
        sw = session_windows_of(d)
        cur = {k: (int(a), int(b)) for k, (a, b) in sw.items()}
        cur["ny"] = (int(sw["ny_am"][0]), int(sw["ny_pm"][1]))     # the whole NY session (m1)
        for k, (a, b) in cur.items():
            a0, b0 = out.get(k, (a, b))
            out[k] = (max(a0, a), min(b0, b))
    for k, (a, b) in out.items():
        if not a < b:
            raise DesignRefused(f"session {k} holds no slot on every date of {days[0]} to {days[-1]}")
    out["_last_entry"] = (0, int(td["last_entry_offset"]))
    return out


@dataclass(frozen=True)
class Design:
    """One firm's components (the module docstring's refusals)."""

    firm: str
    components: tuple[Component, ...]
    overlap: str = "refused"
    day: date | None = None                 # checked against that trading day's sessions; None: every search-year day

    def __post_init__(self) -> None:
        if self.overlap not in OVERLAP_MODES:
            raise DesignRefused(f"overlap {self.overlap!r}: a design holding two positions at once is refused until the "
                                "search template defines overlap (the three-way design note 1.6)")
        comps = tuple(self.components)
        if not comps:
            raise DesignRefused("a design has at least one component")
        names = [c.name for c in comps]
        if len(set(names)) != len(names):
            raise DesignRefused(f"component names repeat: {names}")
        if self.day is not None and not isinstance(self.day, date):
            raise DesignRefused(f"a design's day is a date, got {self.day!r}")
        bounds = session_bounds(self.day)
        last_entry = bounds["_last_entry"][1]
        for c in comps:
            if c.session not in bounds or c.session.startswith("_"):
                raise DesignRefused(f"component {c.name}: unknown session {c.session!r}")
            a, b = bounds[c.session]
            if not (a <= int(c.first) and int(c.last) < b):
                raise DesignRefused(f"component {c.name}: its window {c.first}..{c.last} is outside session "
                                    f"{c.session} [{a}, {b})")
            if int(c.last) > last_entry:
                raise DesignRefused(f"component {c.name}: its window ends after the firm's last new entry")
        order = sorted(comps, key=lambda c: int(c.first))
        for x, y in zip(order, order[1:]):
            if int(y.first) <= int(x.last):
                raise DesignRefused(f"components {x.name} and {y.name}: their windows collide (CHARTER 3.5)")
        object.__setattr__(self, "components", comps)


# ------------------------------------------------------------------------------------------------ the schedule


@dataclass(frozen=True)
class ScheduledTrade:
    """One position of the schedule (the module docstring's fields)."""

    firm: str
    component: str
    source: str
    session: int
    date: str
    decision: int
    alert: int
    live: int
    tag: str
    order_kind: str
    ticket_rule: str
    side: int
    side_source: str
    fill_slot: int
    fill_price: float
    resting: bool
    stop_ticks: int
    target_ticks: int
    rr: float
    exit_slot: int
    exit_kind: str
    flatten_slot: int
    window_flatten: bool
    instrument: str
    underlying: str
    gross_ticks: int
    net_r: float | None
    oco_tie: bool = False
    busy_until: int = -1
    tie_sides: tuple[int, ...] = ()


@dataclass
class DaySchedule:
    """One firm's day: the trades; the offers refused by the rules (`triggers.admit`), skipped by the chain, and placed
    but unfilled (void or cancelled), each with its reason."""

    firm: str
    session: int
    date: str
    trades: list[ScheduledTrade] = field(default_factory=list)
    refused: list[tuple[T.Offer, str]] = field(default_factory=list)
    skipped: list[tuple[T.Offer, str]] = field(default_factory=list)
    unfilled: list[tuple[T.Offer, str]] = field(default_factory=list)

    def counts(self) -> dict[str, Counter]:
        return {"refused": Counter(r for _, r in self.refused), "skipped": Counter(r for _, r in self.skipped),
                "unfilled": Counter(r for _, r in self.unfilled), "trades": Counter(t.component for t in self.trades)}


def _groups(offers: Sequence[tuple[int, T.Offer]]) -> list[list[tuple[int, T.Offer]]]:
    """(component index, offer) grouped: an offer alone, or a component's one-cancels-other group; in order of live
    slot, then component."""
    by: dict[tuple, list[tuple[int, T.Offer]]] = {}
    for k, (ci, off) in enumerate(offers):
        key = (ci, off.group) if off.group else (ci, "", k)
        by.setdefault(key, []).append((ci, off))
    groups = list(by.values())
    for g in groups:
        if len({int(o.live) for _, o in g}) != 1:
            raise T.TriggerRefused("a one-cancels-other group's tickets go live together")
    groups.sort(key=lambda g: (int(g[0][1].live), g[0][0], int(g[0][1].sub)))
    return groups


def _trade_row(design: Design, comp: Component, ex: T.Execution, ctx: T.DayContext, oco_tie: bool = False,
               busy_until: int | None = None, tie_sides: tuple[int, ...] = ()) -> ScheduledTrade:
    off, tr = ex.offer, ex.trade
    ticket = ""
    if off.entry == T.TICKET:
        ticket = "break" if ex.order_kind == W.STOP_ENTRY else "fade"
    return ScheduledTrade(
        firm=design.firm, component=comp.name, source=off.source, session=int(off.session), date=ctx.date,
        decision=int(off.decision), alert=int(off.alert), live=int(tr.order.live), tag=off.tag,
        order_kind=ex.order_kind, ticket_rule=ticket, side=int(ex.side), side_source="coin",
        fill_slot=ex.fill_slot, fill_price=float(tr.fill.price), resting=bool(tr.fill.resting),
        stop_ticks=int(comp.stop_ticks), target_ticks=int(comp.target_ticks), rr=float(comp.rr),
        exit_slot=ex.exit_slot, exit_kind=W.KIND_CODE[int(tr.rule.kind[0])], flatten_slot=ex.flatten_slot,
        window_flatten=ex.window_flatten, instrument=comp.instrument,
        underlying="NQ", gross_ticks=int(tr.rule.gross[0]),
        net_r=None if tr.rule.net_r is None else float(tr.rule.net_r[0]), oco_tie=bool(oco_tie),
        busy_until=ex.exit_slot if busy_until is None else int(busy_until), tie_sides=tuple(int(x) for x in tie_sides))


def _worse(e: T.Execution) -> tuple:
    """The order of badness of a tied member's walked trade for the user (the M-6 ruling, E-223 as amended): the lower gross first (the
    walk's own stop-first settlement on two-barrier bars), then the later exit, then the lower sub."""
    return int(e.trade.rule.gross[0]), -e.exit_slot, int(e.offer.sub)


def calendar_contexts(design: Design, cal, hist: T.History, i: int, *, windows: Sequence[T.Window] = (),
                      market: str = "NQ", rules: W.Rules = T.JOURNEY) -> tuple[T.DayContext, dict[str, T.DayContext]]:
    """Q-169 (2): the day's contexts from the void calendar (`extended.day_calendar`): the day-wide one (a source reading
    nothing: its `void` is the day-wide void, which `schedule_day`'s day-end guard honours), and each component's, from
    what its source reads (`triggers.context_for`), so every source drops its void days by the calendar. The session
    index is the history's index `i`. Raises on a held-out or a confirmation-window day."""
    from datetime import date as _date

    d = _date.fromisoformat(hist.days[i])
    base = T.context_for(None, cal, d, i, windows, market=market, rules=rules)
    return base, {c.name: T.context_for(c.trigger, cal, d, i, windows, market=market, rules=rules)
                  for c in design.components}


def coin_component(name: str, session: str, latency: int, *, stop_ticks: int, rr: float, entry: str = T.MARKET,
                   day=None, instrument: str = "MNQ") -> Component:
    """The naive coin over one session (Q-169 (3)): its moments every `mark_step_min` minutes from the session's start
    to the last moment whose order goes live before the session's end (and before the firm's last new entry), the
    session read through `session_windows_of`; the component's window is the orders' live slots. `day` given, that
    trading day's session (build its `Design` with the same `day=`); None, the bounds holding on every search-year
    weekday (`session_bounds`)."""
    b = session_bounds(day)
    start, end = b[session]
    end = min(end, b["_last_entry"][1] + 1)
    first = -(-int(start) // T.MARK_STEP) * T.MARK_STEP
    last = ((end - 1 - int(latency)) // T.MARK_STEP) * T.MARK_STEP
    trig = T.CoinMarks(first, last, latency=latency, entry=entry)
    return Component(name, session, first + int(latency), last + int(latency), trig, stop_ticks, rr, instrument)


def schedule_day(design: Design, hist: T.History, i: int, ctx: T.DayContext, unit: T.CoinUnit, *,
                 rules: W.Rules = T.JOURNEY, costs: W.Costs | None = None,
                 contexts: dict[str, T.DayContext] | None = None) -> DaySchedule:
    """One firm's day under the chain (the module docstring). `ctx` is the day-wide context; `contexts`, when given
    (`calendar_contexts`), each component's own, under which its offers are admitted and executed. A design checked
    against one day's sessions (`Design(day=...)`) is scheduled on that day only."""
    if design.day is not None and design.day.isoformat() != ctx.date:
        raise DesignRefused(f"a design checked against the sessions of {design.day} is scheduled on {ctx.date}")
    if hist.days[i] != ctx.date:
        raise ValueError(f"the day's context is {ctx.date}, the history's day {i} is {hist.days[i]}")
    if not (ctx.void or ctx.fomc):                                   # m-3: a data-integrity refusal, not a decision
        last = W.last_bar(hist.o[i])
        if last is None or last < int(rules.walk_end):
            raise DayRefused(f"{ctx.date}: the day's last bar ends at slot {last}, before the walk's end "
                             f"{int(rules.walk_end)}; such a day is voided by the caller's calendar (DayContext.void)")
    out = DaySchedule(design.firm, int(ctx.session), ctx.date)
    mine: list[tuple[int, T.Offer]] = []
    cctx = {c.name: (contexts[c.name] if contexts is not None else ctx) for c in design.components}
    for ci, comp in enumerate(design.components):
        cx = cctx[comp.name]
        if (cx.session, cx.date) != (ctx.session, ctx.date):
            raise ValueError(f"component {comp.name}'s context is not the day's")
        offs = [o for o in comp.trigger.offers(hist, i, cx) if int(comp.first) <= int(o.live) <= int(comp.last)]
        kept, refused = T.admit(offs, cx)
        out.refused += refused
        mine += [(ci, o) for o in kept]
    # the firm's state from the last placed group: [start, end) stretches labelled 'order' (an entry order working),
    # 'position' (a position open) and 'gap' (the five minutes flat after an exit); free from `free_at`
    busy: list[tuple[int, int, str]] = []
    free_at = -1
    for grp in _groups(mine):
        live = int(grp[0][1].live)
        if live < free_at:
            reason = next(lbl for a, b, lbl in busy if a <= live < b)     # M-7: the state at the skip's live minute
            out.skipped += [(o, reason) for _, o in grp]
            continue
        comp = design.components[grp[0][0]]
        exs = [T.execute(o, T.coin_side(unit, o), hist, i, cctx[comp.name], comp.stop_ticks, comp.rr, rules=rules,
                         costs=costs) for _, o in grp]
        filled = [e for e in exs if e.filled]
        if filled:
            first_bar = min(e.trade.fill.bar for e in filled)
            tied = [e for e in filled if e.trade.fill.bar == first_bar]
            win = min(tied, key=_worse)                                     # M-6: the worse walked trade on a tie
            end = max(e.exit_slot for e in tied)                            # busy to the later exit, whichever booked
            out.trades.append(_trade_row(design, comp, win, ctx, oco_tie=len(tied) > 1, busy_until=end,
                                         tie_sides=tuple(e.side for e in tied) if len(tied) > 1 else ()))
            for e in exs:
                if e is not win:
                    out.unfilled.append((e.offer, "oco_tie_cancelled" if any(e is x for x in tied)
                                         else "oco_cancelled"))
            # the fill on the bar stamped first_bar - 1 is known when that bar closes, at first_bar: until then the
            # state is a working order (an offer at the fill bar's own minute cannot know of the fill)
            busy = [(live, first_bar, "order"), (first_bar, end, "position"), (end, end + T.GAP_MINUTES, "gap")]
            free_at = end + T.GAP_MINUTES
        else:
            out.unfilled += [(e.offer, f"{e.trade.fill.status}:{e.trade.fill.reason}") for e in exs]
            ends = [b for b in (e.busy_until for e in exs) if b is not None]   # B-1: every stretch that worked
            if ends:
                busy = [(live, max(ends), "order")]
                free_at = max(ends)
    for a, b in zip(out.trades, out.trades[1:]):
        if int(b.fill_slot) < int(a.busy_until) + T.GAP_MINUTES:         # the chain's own invariant, checked
            raise OverlapRefused(f"{design.firm}: trades at {a.fill_slot} and {b.fill_slot} break the chain")
    return out


# ------------------------------------------------------------------------------------------------ the user's book


@dataclass(frozen=True)
class Position:
    """A position of the user: its firm and account, its session, the minutes it opens (the fill bar's open) and closes
    (the exit bar's end), its side and underlying, and a reference for messages. `group`: the alternatives of one
    same-bar tie (`positions_of`) share a non-empty group and are never checked against each other -- they are the two
    positions the user may hold, of which the user holds one."""

    firm: str
    account: str
    session: int
    open_slot: int
    close_slot: int
    side: int
    underlying: str = "NQ"
    ref: str = ""
    group: str = ""

    def interval(self) -> tuple[int, int]:
        base = int(self.session) * T.DAY_SLOTS
        return base + int(self.open_slot), base + int(self.close_slot)


def position_of(tr: ScheduledTrade, account: str = "") -> Position:
    """The booked position of a trade, [fill, exit). For the user's book use `positions_of`, which covers a tie."""
    return Position(tr.firm, account, tr.session, tr.fill_slot, tr.exit_slot, tr.side, tr.underlying,
                    f"{tr.firm}/{tr.component}/{tr.date}@{tr.fill_slot}")


def positions_of(tr: ScheduledTrade, account: str = "") -> list[Position]:
    """The positions the user may hold from a trade (the re-read's m-1, conduct tier 1): the booked one, [fill, exit);
    or, for a same-bar tie, where which ticket the broker filled is unknown, every tied ticket's side over
    [fill, busy_until) -- so another account's or firm's position in that span is refused, as tier 1 where it opposes
    either side."""
    ref = f"{tr.firm}/{tr.component}/{tr.date}@{tr.fill_slot}"
    if not tr.oco_tie:
        return [position_of(tr, account)]
    return [Position(tr.firm, account, tr.session, tr.fill_slot, tr.busy_until, int(s), tr.underlying,
                     f"{ref} (tie, side {int(s):+d})", group=ref) for s in sorted(set(tr.tie_sides))]


class UserBook:
    """Every position of the user across accounts and firms; `add` refuses an overlap -- as conduct tier 1 when any
    position it overlaps has the opposite side, else as an undefined overlap."""

    def __init__(self, overlap: str = "refused"):
        if overlap not in OVERLAP_MODES:
            raise DesignRefused(f"overlap {overlap!r} is undefined until the search template defines it")
        self.positions: list[Position] = []

    def add(self, p: Position) -> None:
        if int(p.side) not in (1, -1) or int(p.close_slot) < int(p.open_slot):
            raise ValueError(f"a position has a side and closes after it opens: {p}")
        a0, a1 = p.interval()
        hits = [q for q in self.positions if not (p.group and q.group == p.group)
                and a0 < q.interval()[1] and q.interval()[0] < a1]
        opposed = [q for q in hits if int(q.side) != int(p.side)]
        if opposed:
            q = opposed[0]
            raise TierOneRefused(f"REFUSED (conduct tier 1): {p.ref} ({p.firm}/{p.account}) opposes {q.ref} "
                                 f"({q.firm}/{q.account}) while both may be open")
        if hits:
            raise OverlapRefused(f"REFUSED: {p.ref} and {hits[0].ref} are held at once; overlap is undefined until the "
                                 "search template defines it")
        self.positions.append(p)

    def extend(self, ps: Iterable[Position]) -> None:
        for p in ps:
            self.add(p)


def schedule_user(designs: Sequence[Design], hist: T.History, i: int, ctx: T.DayContext, unit: T.CoinUnit, *,
                  rules: W.Rules = T.JOURNEY, costs: W.Costs | None = None,
                  book: UserBook | None = None) -> tuple[list[DaySchedule], UserBook]:
    """Every firm's day for one user (one coin unit, shared by every firm), its positions added to the user's book
    (refusing any overlap, opposite sides first)."""
    firms = [d.firm for d in designs]
    if len(set(firms)) != len(firms):
        raise DesignRefused(f"one design a firm: {firms}")
    book = UserBook() if book is None else book
    days = [schedule_day(d, hist, i, ctx, unit, rules=rules, costs=costs) for d in designs]
    for day in days:
        book.extend(p for t in day.trades for p in positions_of(t))
    return days, book


__all__ = ["TASK", "OVERLAP_MODES", "SKIP_REASONS", "DesignRefused", "OverlapRefused", "TierOneRefused", "DayRefused",
           "Component", "session_windows_of", "session_bounds", "Design", "calendar_contexts", "coin_component",
           "ScheduledTrade", "DaySchedule", "schedule_day", "Position",
           "position_of", "positions_of", "UserBook", "schedule_user"]
