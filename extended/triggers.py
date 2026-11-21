"""Q-152 (the restart plan's Wave 3.3, first part): the trigger library's first coin-sided sources -- one interface, the
execution rules every source obeys, and the coin that sets every offer's side.

    from extended import triggers as T
    hist = T.History.from_bars(bars)                         # the bar store's frame -> walker-layout day arrays
    src = T.P14Breakout(latency=5, entry="market")            # or T.P16Marks(marks), T.RL3Tickets("pd", cutoff)
    offers = src.offers(hist, i, ctx)                         # day i's offers: moments and levels, no side
    kept, refused = T.admit(offers, ctx)                      # the calendar, window and overnight rules
    side = T.coin_side(unit, offer)                           # the coin (the design note's choice 3 keying)
    ex = T.execute(offer, side, hist, i, ctx, stop_ticks, rr)  # the walker's fill and walk under the window rules

Nothing here reads a file of bars (the caller passes them through the window guard), a result, or the held-out years;
`DECISIONS.md` is read only by the overnight guard. **Read, not typed**: the latencies, the limit's working window, the
mark step and the entry types come from the lever table's declared parameters (`extended.lever_space.DECLARED`). **Typed
here, each with its citation** (the red team's N-5): the five-minute flat between trades, the 07:35 and 08:30-08:59
bounds, P-14's k and last slot, RL3's cutoffs and round-number step; the tests hold the clock slots and the cutoff grid.

**The clock** is the walker's (`extended/walker.py`): a slot is minutes after 17:00 CT of the evening the trading day
opens; a day's arrays o, h, l, c are indexed by each bar's END minute, so the bar stamped (opening at) slot s is index
s + 1 and closes at s + 1. **An offer's alert** is the slot by which its information is complete: it reads bars stamped
at or before alert - 1 only (feature-rules section 1), of its own day and earlier days. **Its live** is the slot its
order starts working: a market order fills at the open of the first present bar stamped at or after live, a resting
order only on bars stamped at or after live (`walker.fill_order`).

**An offer** (`Offer`) carries its moment and its level and **never its side**: the side comes from the coin
(`coin_side`), drawn by the caller for the unit (start, seed) that trades it. Its fields: the source, the day's session
index, the **decision** slot (Stage 2's `decision_slot_minutes`: P-14's event slot, P-16's mark, RL3's alert) and a
sub-index among one decision's offers -- the two make the coin key's moment --, the alert, the live slot, the entry
(`market`, `limit` or RL3's `ticket`), the level a resting order works at, a ticket's role (+1 a resistance, -1 a
support), the last slot it may fill on (`expires`: bars stamped at or before it), its one-cancels-other group, whether
it is re-written after a window (RL3 4.6) and, for an offer the source voids, the reason (kept so that it is counted).

**The sources** (lever table T1; E-208's dispositions):

* `P14Breakout` -- P-14's breakout timing, coin-sided: Stage 2's `brk` pattern at k = 30 minutes
  (`propedge/outcomes/atlas_core.py`, `config/atlas_a3.yaml`'s `brk30`): with the 30-minute bars aligned to the
  trading-day clock from 17:00, the first one-minute close above the previous completed 30-minute bar's high and the
  first below its low, each at most once per reference bar, events to 14:00 CT (`last_decision_ct`). The event's
  direction is dropped: each event is one offer moment. Alert = the event slot (its bar has closed); live = alert + L,
  L in the declared latencies, counted in clock minutes (F-04 5.1). A limit rests at the price at the alert (the close
  of the last bar closed by then, `walker.price_at`; F-04 6.1) and works `limit_window_min` minutes. Its events run
  from 17:00 CT, P-14's registered span, since H2's row (E-231) admits overnight triggers on the search years.
* `P16Marks` -- P-16's marks, coin-sided, latency-free (E-203 B-2; F-04 5.1): each mark is scheduled, so the alert is
  sent `latency.reference` minutes before it and the order goes live at the mark; every declared L is met by that one
  timing (`lever_space.latency_cells('p16')` is one cell). A limit rests at the price at the alert. The marks are the
  caller's (P-16's admitted marks come from its registered cutoff, a Stage 2 reading); `p16_grid` is D-525's grid.
  **Day marks** (08:30 to 15:10 CT); **overnight marks** (17:00 to 08:29 CT) behind `overnight=True`, which refuses
  until H2's data-integrity row exists (`H2_ROW`).
* `RL3Tickets` -- RL3's pre-session tickets (E-204, E-208; `prereg/DRAFT_F-RL3_resting_levels.md` 4 and 5.1-5.5):
  one level kind (`pd`, `on`, `pdc`, `rn100`), its levels frozen from bars stamped at or before 08:29 (alert 08:30),
  live from 09:00 (the bar stamped 09:00), latency-free; the coin chooses, per ticket, the fade limit at the level or
  the break stop one tick beyond it on the other side -- the same-bar pair of E-204 (`order_for`). The two tickets of a
  kind are one group (one-cancels-other, RL3 5.3 / 11.2). Unfilled tickets are cancelled at the cutoff (fills on bars
  closing at or before it), cancelled at a window's start and re-written after it, void if already through.

**The execution rules, for every source** (`admit`, `segments`, `execute`; CHARTER 4 as amended by E-210):

* **News** (E-202 (2)(a), (d); E-200 R-1): no entry and no fill inside a verified window (`Window`, the caller's, from
  the record). An offer whose order would go live inside a window is refused; an alert inside a window whose order goes
  live after it is not. A working order is cancelled at a window's start: it fills only on bars stamped before it, and,
  since the walker never opens a position on the bar it would flatten on, not on the bar stamped `first - 1` either
  (one minute conservative; the red team's N-1). A position open at a window's start is walked to the window's first
  slot and **booked at the adverse extreme of the window's first bar less two ticks, exiting at that bar's end** (at its
  stop where that extreme reaches it) -- **E-223 M-4 ruling (lead)**, RL3 4.6 / 5.4's convention, the as-walked
  convention for every source until the search template pins one (`window_flatten_trade`); for an unscheduled release,
  known only from its minute, at the first bar after that minute.
* **The closed window**, 08:30-08:59 CT (bars stamped 08:30 to 08:59), every day and **for every source**: a window of
  kind `closed` under the same rules (E-202 (2)(a): "RL3's 08:30-08:59 fill window stays closed"), applied to every
  source as a conservative floor -- **E-223 M-8 ruling (lead)**, which the lead records in a row.
* **BLS 08:30 release days**: no entry at or before 07:35:00 CT (E-007 (d), CHARTER 4: strictly after it): a window of
  kind `bls` over the bars stamped 17:00 to 07:35, so the earliest fill is the open of the bar stamped 07:36.
* **FOMC statement days are out** whole (CHARTER 4), and a calendar void day (an early close, a data defect: the
  caller's calendars) carries no offer.
* **L**: every offer satisfies live - alert >= L (`check_latency`): L in the declared latencies (5 the reference, 3, 2)
  for a timed source, every one of them for a latency-free source.
* **Market or limit entry** (T5): a market order at live; a limit at its level, live at live, filled only on a trade
  through by a tick at its price and never better (the walker's `LIMIT_ENTRY`), void if marketable at live, working
  `limit_window_min` minutes (T6).
* **Overnight** (17:00 to 08:29 CT): no offer goes live there until H2's row exists (`overnight_allowed`), whatever
  its source -- a guard in `admit` beside the sources' own.

**The coin** (`docs/plans/THREE_WAY_TEST_design.md` 1.5, choice 3): an offer's side is +1 when the unit's uniform for
it is below one half. The uniform's key is the design note's fixed-length coin key
[role seed, 3, part, history, seed index, start, underlying, moment, draw kind] (`three_way_arith.seed_key`'s layout):
it carries the unit's **start** and its seed index, **never an account or a firm index** -- which, in the evaluation,
means only that opposite positions across a user's accounts or firms are refused (`components.UserBook`); it is not
the traded side rule: in the playbook, sides come from each design's own trigger, under the no-harm floor, with
accounts alternating (E-221, the operator's O-4 ruling) --, the **underlying** (MNQ and NQ are one), and the moment as
(session x 1440 + decision slot) x 16 + sub -- a session index and a minute offset, never an epoch time. Every word is
below 2^32. **The generator, declared:** numpy's counter-based Philox (4x64), seeded by `SeedSequence(key)`; the
first raw 64-bit output's top 52 bits i give the uniform (2 i + 1) 2^-53, on the note's symmetric grid.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

from extended import lever_space as LS
from extended import walker as W

ROOT = Path(__file__).resolve().parent.parent
TASK = "Q-152"

# ------------------------------------------------------------------------------------------------ declared parameters

#: the declared latencies (E-202 (2)(c); lever table T4), the reference first
LATENCIES: tuple[int, ...] = tuple(int(x) for x in LS.declared("latency"))
REFERENCE_L = int(LS.declared("latency.reference"))
#: how long a limit works from going live (lever table T6; F-04 6.1)
LIMIT_WINDOW = int(LS.declared("limit_window_min"))
#: the offer-mark step of a scheduled source (Stage 2 D-525 (2))
MARK_STEP = int(LS.declared("mark_step_min"))
ENTRIES = tuple(LS.declared("entry_types"))                 # ('market', 'limit')
MARKET, LIMIT, TICKET = W.MARKET, W.LIMIT_ENTRY, "ticket"

TICK = W.TICK
DAY_SLOTS = 1440
RTH_OPEN = W.slot(8, 30)                                    # 930: the first regular-session bar is stamped 08:30
LIVE_0900 = W.slot(9, 0)                                    # 960
CLOSED_FIRST, CLOSED_LAST = W.slot(8, 30), W.slot(8, 59)    # the closed window: bars stamped 08:30..08:59
BLS_CLEAR = W.slot(7, 35)                                   # 875: on a BLS day no entry at or before 07:35:00 CT
SESSION_END = W.C_FLAT                                      # 1330: 15:10 CT (resolved_coin.SESSION_END)
#: the flat between two chain trades of one firm (Stage 2 D-429; resolved_coin.GAP_MINUTES); used by the scheduler
GAP_MINUTES = 5
#: the library's base walk: Stage 2's end and flatten (the bar ending 15:08 CT; the worst of the bars ending 15:08-15:10
#: less two ticks), with no stop move (lever table S7 dropped; RL3 5.4)
JOURNEY = W.Rules("journey", W.FLAT_ENTRY, "worst_less_two", False)

#: P-14's pattern (`config/atlas_a3.yaml`: `brk30`, `last_decision_ct` 14:00)
P14_K = 30
P14_LAST = W.slot(14, 0)                                    # 1260
#: RL3's level kinds, its cutoff grid (6.1: the latest of 14:30, 14:00, ..., 10:00 CT), and the round-number step
RL3_KINDS = ("pd", "on", "pdc", "rn100")
RL3_CUTOFFS = tuple(W.slot(h, m) for h, m in ((10, 0), (10, 30), (11, 0), (11, 30), (12, 0), (12, 30), (13, 0),
                                                (13, 30), (14, 0), (14, 30)))
RL3_ROUND = 100.0
#: the previous day's regular session RL3's `pd` and `pdc` read: the bars stamped 08:30 to 14:59 (slots, stamps)
PRIOR_RTH = (RTH_OPEN, W.slot(15, 0) - 1)
#: the order of RL3's tickets inside one decision (the coin key's sub-index)
RL3_SUBS = {("pd", "hi"): 0, ("pd", "lo"): 1, ("on", "hi"): 2, ("on", "lo"): 3, ("pdc", "lvl"): 4,
            ("rn100", "up"): 5, ("rn100", "dn"): 6}

WINDOW_KINDS = ("news", "closed", "bls", "unscheduled")
#: windows after which an RL3 ticket is re-written (4.6); an unscheduled release cancels it for the day (4.7 (d))
REWRITE_AFTER = ("news", "closed")

# ------------------------------------------------------------------------------------------------ the overnight guard

#: the decision row recording H2's pass (the overnight bars' data integrity, the restart plan's Wave 3): E-231 -- the
#: search years' overnight bars are clean apart from the void calendar's days (`extended.day_calendar`). Overnight
#: offers are admitted only while it names a row of the decision log (the guard stays: a row removed refuses them).
H2_ROW: str | None = "E-231"


class OvernightRefused(RuntimeError):
    """An overnight trigger (an offer live from 17:00 to 08:29 CT) before H2's data-integrity row exists."""


class TriggerRefused(ValueError):
    """A source or an offer this library cannot stand behind (a latency not declared, a mark off the clock, ...)."""


@lru_cache(maxsize=1)
def decision_rows() -> frozenset[str]:
    """The ids of the rows in this repository's `DECISIONS.md` (E-nnn), read once."""
    p = ROOT / "DECISIONS.md"
    if not p.exists():
        return frozenset()
    return frozenset(re.findall(r"^\| (E-\d{3,}) \|", p.read_text(encoding="utf-8"), flags=re.M))


def overnight_allowed() -> bool:
    """True only when `H2_ROW` names a row of the decision log."""
    return H2_ROW is not None and H2_ROW in decision_rows()


def require_overnight(what: str) -> None:
    if not overnight_allowed():
        raise OvernightRefused(f"REFUSED: {what} is an overnight trigger (17:00 to 08:29 CT); overnight triggers wait "
                               "for H2's data-integrity row (the restart plan, Wave 3.3; E-208), and `H2_ROW` names none")


# ------------------------------------------------------------------------------------------------ the bars


@dataclass(frozen=True)
class History:
    """The trading days of a bar frame in the walker's layout: `o`, `h`, `l`, `c` of shape [days, 1441], column j the
    bar ending at slot j (the bar stamped j - 1), NaN where no bar, column 0 unused; `days` ISO dates, `contract` the
    contract each day charts (one a day, the store's rule)."""

    days: tuple[str, ...]
    contract: tuple[str, ...]
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray

    @classmethod
    def from_bars(cls, bars: pd.DataFrame) -> "History":
        """From bars in the store's shape (`ts` the bar's OPEN, epoch seconds UTC), through `features.grid` (Chicago
        time, DST-aware; a trading day opens at 17:00 CT the evening before)."""
        from extended import features as F

        g = F.grid(bars)
        pad = np.full((len(g.days), 1), np.nan)
        arrs = [np.concatenate([pad, x], axis=1) for x in (g.O, g.H, g.L, g.C)]
        return cls(tuple(d.isoformat() for d in g.days), tuple(str(x) for x in g.contract), *arrs)

    @classmethod
    def from_arrays(cls, days: Sequence[str], contract: Sequence[str], o, h, l, c) -> "History":
        arrs = [np.atleast_2d(np.asarray(x, dtype=float)) for x in (o, h, l, c)]
        return cls(tuple(days), tuple(contract), *arrs)

    def __len__(self) -> int:
        return len(self.days)

    def day(self, i: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        return self.o[i], self.h[i], self.l[i], self.c[i]


# ------------------------------------------------------------------------------------------------ windows and the day


@dataclass(frozen=True)
class Window:
    """A window in slots: no fill on the bars stamped `first` .. `last` (inclusive). `kind`: 'news' (a verified release
    window), 'closed' (08:30-08:59), 'bls' (a report day to 07:35), 'unscheduled' (a release known only from its minute,
    `first`). `source`: its provenance (the record key or calendar file)."""

    first: int
    last: int
    kind: str = "news"
    source: str = ""

    def __post_init__(self) -> None:
        if self.kind not in WINDOW_KINDS:
            raise ValueError(f"unknown window kind {self.kind!r}; one of {WINDOW_KINDS}")
        if not 0 <= int(self.first) <= int(self.last) < DAY_SLOTS:
            raise ValueError(f"a window is slots first <= last on the trading-day clock, got {self.first}, {self.last}")

    def contains(self, s: int) -> bool:
        return int(self.first) <= int(s) <= int(self.last)

    @property
    def flatten_index(self) -> int:
        """The walker's walk end for a position open at the window's start: the bar ending at `first` (the position is
        closed at the price at `first`), or for an unscheduled release the bar ending one minute later (the first bar
        after the release minute, RL3 4.7 (d))."""
        return int(self.first) + (1 if self.kind == "unscheduled" else 0)


def release_window(release_slot: int, before: int, after: int, source: str, kind: str = "news") -> Window:
    """The window around a release at `release_slot`: the bars stamped `before` minutes before it to `after` minutes
    after it. `before` and `after` are the caller's, parsed from the verified record (`modes_news.window_minutes`)."""
    return Window(int(release_slot) - int(before), int(release_slot) + int(after), kind, source)


@dataclass(frozen=True)
class DayContext:
    """One trading day's calendar, as published in advance: `session` its index in the history (the coin key's
    moment), `date` ISO, `bls` a BLS 08:30 ET release day, `fomc` a scheduled FOMC statement day (out whole), `void` a
    calendar void (an early close, a data defect), `prior_void` the previous day voids the prior-session levels (RL3's
    `pd`, `pdc`: an early close or defect the day before), `windows` the verified news windows."""

    session: int
    date: str
    bls: bool = False
    fomc: bool = False
    void: bool = False
    prior_void: bool = False
    windows: tuple[Window, ...] = ()

    def all_windows(self) -> tuple[Window, ...]:
        """The verified windows, the closed 08:30-08:59 window and, on a BLS day, the report window to 07:35, sorted."""
        ws = list(self.windows) + [Window(CLOSED_FIRST, CLOSED_LAST, "closed", "E-202 (2)(a)")]
        if self.bls:
            ws.append(Window(0, BLS_CLEAR, "bls", "E-007 (d); CHARTER 4"))
        return tuple(sorted(ws, key=lambda w: (w.first, w.last)))


# ------------------------------------------------------------------------------------------------ the offer


@dataclass(frozen=True)
class Offer:
    """One offer moment of a source (the module docstring). No side: the coin sets it."""

    source: str
    session: int
    decision: int
    sub: int
    alert: int
    live: int
    entry: str
    level: float = float("nan")
    role: int = 0
    expires: int | None = None
    group: str = ""
    rewrite: bool = False
    tag: str = ""
    void: str = ""

    def __post_init__(self) -> None:
        if self.entry not in (MARKET, LIMIT, TICKET):
            raise ValueError(f"unknown entry {self.entry!r}")
        if not 0 <= int(self.decision) < DAY_SLOTS or not 0 <= int(self.sub) < MOMENT_SUBS:
            raise ValueError(f"decision {self.decision} or sub {self.sub} off the key's grid")
        if int(self.live) < int(self.alert):
            raise ValueError("an order cannot go live before its alert")


def check_latency(offer: Offer, latency: int | None) -> None:
    """Every offer is known at least L minutes before its order goes live: L the source's latency, or every declared L
    for a latency-free source (`latency` None)."""
    need = max(LATENCIES) if latency is None else int(latency)
    if int(offer.live) - int(offer.alert) < need:
        raise TriggerRefused(f"{offer.source} offer at {offer.alert}: live {offer.live} is less than {need} minutes "
                             "after its alert")


def _latency(source: str, latency: int | None) -> int | None:
    cells = LS.latency_cells(source)
    if latency not in cells:
        raise TriggerRefused(f"latency {latency!r} is not a cell of source {source!r} ({cells}; lever table T4)")
    return latency


def _entry(entry: str) -> str:
    if entry not in ENTRIES:
        raise TriggerRefused(f"entry {entry!r} is not one of the declared entry types {ENTRIES} (lever table T5)")
    return entry


def _limit_level(o: np.ndarray, c: np.ndarray, alert: int) -> tuple[float, str]:
    """A timed source's limit price: the price at the alert (`walker.price_at`: bars stamped <= alert - 1)."""
    p = W.price_at(o, c, int(alert))
    return (p, "") if math.isfinite(p) else (float("nan"), "no_reference")


# ------------------------------------------------------------------------------------------------ P-14's breakout timing


def breakout_events(c: np.ndarray, o: np.ndarray, h: np.ndarray, l: np.ndarray, k: int = P14_K, first: int = 0,
                    last: int = P14_LAST) -> list[tuple[int, int]]:
    """Stage 2's `brk` events of one day (`atlas_core.a_events`, kind `brk`), as (slot, direction), sorted by slot
    then long first: per completed k-minute bar aligned from 17:00 (minutes ending (k b, k b + k]; a bar with no minute
    left out), the first minute in the next k whose close is above its high (+1) and the first below its low (-1), kept
    when first <= slot <= last. The slot is the minute's END: the close is known at it."""
    n = len(o) - 1
    ev: list[tuple[int, int]] = []
    b = 0
    while (b + 1) * k <= n:
        lo_j, hi_j = b * k + 1, (b + 1) * k
        seg = slice(lo_j, hi_j + 1)
        present = ~np.isnan(o[seg])
        if present.any():
            bh, bl = float(np.nanmax(np.where(present, h[seg], np.nan))), float(np.nanmin(np.where(present, l[seg],
                                                                                                    np.nan)))
            s = (b + 1) * k
            j0, j1 = s + 1, min(s + k, n)
            if j0 <= j1:
                js = np.arange(j0, j1 + 1)
                cc = c[js]
                ok = ~np.isnan(o[js]) & ~np.isnan(cc)
                for d, hit in ((1, ok & (cc > bh)), (-1, ok & (cc < bl))):
                    if hit.any():
                        j = int(js[int(np.argmax(hit))])
                        if first <= j <= last:
                            ev.append((j, d))
        b += 1
    ev.sort(key=lambda x: (x[0], -x[1]))
    return ev


@dataclass(frozen=True)
class P14Breakout:
    """P-14's breakout timing, coin-sided (the module docstring). `latency` one of the declared L; `entry` market or
    limit; `first`, `last` the alert slots kept (17:00 to 14:00 CT by default, P-14's registered span)."""

    latency: int = REFERENCE_L
    entry: str = MARKET
    first: int = 0
    last: int = P14_LAST
    k: int = P14_K
    source: str = field(default="p14", init=False)
    latency_free: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        _latency("p14", self.latency)
        _entry(self.entry)
        if int(self.first) < RTH_OPEN:
            require_overnight(f"P-14's breakout timing from slot {self.first}")
        if not 0 <= int(self.first) <= int(self.last) <= P14_LAST:
            raise TriggerRefused(f"P-14's events lie in 17:00 to 14:00 CT, got {self.first}..{self.last}")

    def calendar_reads(self) -> tuple[bool, bool]:
        """(reads overnight bars, reads the bar stamped 08:29) for the void calendar: an event at or before 09:00 is
        measured against a 30-minute bar ending at or before 08:30, of overnight bars; the 08:29 bar is not needed."""
        return int(self.first) <= RTH_OPEN + int(self.k), False

    def offers(self, hist: History, i: int, ctx: DayContext) -> list[Offer]:
        o, h, l, c = hist.day(i)
        out = []
        seen = set()
        for j, d in breakout_events(c, o, h, l, int(self.k), int(self.first), int(self.last)):
            if j in seen:
                raise TriggerRefused(f"two P-14 events at one slot {j}: the coin key's moment would repeat")
            seen.add(j)
            live = j + int(self.latency)
            if self.entry == LIMIT:
                lvl, why = _limit_level(o, c, j)
                off = Offer("p14", ctx.session, j, 0, j, live, LIMIT, lvl, expires=live + LIMIT_WINDOW - 1,
                            tag=f"brk{self.k}{'+' if d > 0 else '-'}", void=why)
            else:
                off = Offer("p14", ctx.session, j, 0, j, live, MARKET, tag=f"brk{self.k}{'+' if d > 0 else '-'}")
            check_latency(off, self.latency)
            out.append(off)
        return out


# ------------------------------------------------------------------------------------------------ P-16's marks


def p16_grid(first: int = 0, end: int = SESSION_END, step: int = MARK_STEP) -> tuple[int, ...]:
    """D-525's offer grid (`resolved_coin.marks`): 17:00 CT and every `step` minutes after it, before 15:10 CT,
    restricted to [first, end)."""
    return tuple(m for m in range(0, int(end), int(step)) if m >= int(first))


@dataclass(frozen=True)
class P16Marks:
    """P-16's marks, coin-sided and latency-free (the module docstring). `marks` the caller's (P-16's admitted marks);
    `overnight` False for day marks (08:30 to 15:10 CT), True for overnight marks (17:00 to 08:29 CT), admitted since
    H2's row (E-231)."""

    marks: tuple[int, ...]
    entry: str = MARKET
    overnight: bool = False
    latency: int | None = None
    source: str = field(default="p16", init=False)
    latency_free: bool = field(default=True, init=False)

    def __post_init__(self) -> None:
        _latency("p16", self.latency)
        _entry(self.entry)
        ms = tuple(int(m) for m in self.marks)
        if not ms or len(set(ms)) != len(ms) or list(ms) != sorted(ms):
            raise TriggerRefused("P-16's marks are distinct and ascending")
        if any(m % MARK_STEP for m in ms):
            raise TriggerRefused(f"P-16's marks lie on D-525's {MARK_STEP}-minute grid")
        if self.overnight:
            require_overnight("P-16's overnight marks")
            if any(not REFERENCE_L <= m < RTH_OPEN for m in ms):
                raise TriggerRefused("P-16's overnight marks lie in 17:05 to 08:25 CT (the alert five minutes before)")
        elif any(not RTH_OPEN <= m < SESSION_END for m in ms):
            raise TriggerRefused("P-16's day marks lie in 08:30 to 15:05 CT")
        object.__setattr__(self, "marks", ms)

    def calendar_reads(self) -> tuple[bool, bool]:
        """Overnight marks trade on overnight bars; a day limit whose alert is at or before 08:30 rests at an overnight
        bar's close; a day market order reads no bar."""
        early = self.entry == LIMIT and min(self.marks) - REFERENCE_L <= RTH_OPEN
        return bool(self.overnight or early), False

    def offers(self, hist: History, i: int, ctx: DayContext) -> list[Offer]:
        o, h, l, c = hist.day(i)
        out = []
        for m in self.marks:
            alert = m - REFERENCE_L
            if self.entry == LIMIT:
                lvl, why = _limit_level(o, c, alert)
                off = Offer("p16", ctx.session, m, 0, alert, m, LIMIT, lvl, expires=m + LIMIT_WINDOW - 1,
                            tag="mark", void=why)
            else:
                off = Offer("p16", ctx.session, m, 0, alert, m, MARKET, tag="mark")
            check_latency(off, None)
            out.append(off)
        return out


# ------------------------------------------------------------------------------------------------ RL3's tickets


def rl3_levels(hist: History, i: int, kind: str, prior_void: bool = False) -> tuple[float, list[tuple[str, float, int,
                                                                                                        str]]]:
    """(P_ref, [(name, level, role, void reason)]) of one day's tickets of a kind (RL3 4.3-4.4, 5.1), from bars stamped
    at or before 08:29 of the day and the previous day's regular session: `role` +1 a resistance (above P_ref), -1 a
    support; a level exactly at P_ref void except `on`'s; `pd` and `pdc` void when the calendar voids the prior
    session's levels (`prior_void`: a roll, the store's first day, after an abbreviated or void day -- the void
    calendar's rules, `extended.day_calendar`, never a copy here; Q-169) and when the history holds no previous day;
    `pdc` void without its bar stamped 14:59; every ticket void without a bar stamped 08:29 (data, read at the alert)."""
    if kind not in RL3_KINDS:
        raise TriggerRefused(f"unknown RL3 level kind {kind!r}; one of {RL3_KINDS}")
    o, h, l, c = hist.day(i)
    ref_j = RTH_OPEN                                    # the bar stamped 08:29 ends at 08:30
    p_ref = float(c[ref_j]) if not math.isnan(o[ref_j]) else float("nan")
    names = [n for (k, n) in RL3_SUBS if k == kind]
    if math.isnan(p_ref):
        return p_ref, [(n, float("nan"), 0, "no_ref_bar") for n in names]
    out: list[tuple[str, float, int, str]] = []
    if kind in ("pd", "pdc"):
        why = ""
        if prior_void:
            why = "prior_void"
        elif i == 0:
            why = "no_prior_day"
        if why:
            return p_ref, [(n, float("nan"), 0, why) for n in names]
        po, ph, pl, pc = hist.day(i - 1)
        rth = slice(PRIOR_RTH[0] + 1, PRIOR_RTH[1] + 2)  # bars stamped 08:30 .. 14:59
        pres = ~np.isnan(po[rth])
        if kind == "pd":
            if not pres.any():
                return p_ref, [(n, float("nan"), 0, "no_prior_session") for n in names]
            hi = float(np.nanmax(np.where(pres, ph[rth], np.nan)))
            lo = float(np.nanmin(np.where(pres, pl[rth], np.nan)))
            out = [("hi", hi, 0, ""), ("lo", lo, 0, "")]
        else:
            j = PRIOR_RTH[1] + 1                        # the bar stamped 14:59 ends at 15:00
            if math.isnan(po[j]):
                return p_ref, [("lvl", float("nan"), 0, "no_prior_close")]
            out = [("lvl", float(pc[j]), 0, "")]
    elif kind == "on":
        seg = slice(1, RTH_OPEN + 1)                    # bars stamped 17:00 .. 08:29
        pres = ~np.isnan(o[seg])
        hi = float(np.nanmax(np.where(pres, h[seg], np.nan)))
        lo = float(np.nanmin(np.where(pres, l[seg], np.nan)))
        return p_ref, [("hi", hi, 1, ""), ("lo", lo, -1, "")]
    else:                                               # rn100
        q = p_ref / RL3_ROUND
        if abs(q - round(q)) < 1e-9:
            up, dn = (round(q) + 1) * RL3_ROUND, (round(q) - 1) * RL3_ROUND
        else:
            up, dn = math.ceil(q) * RL3_ROUND, math.floor(q) * RL3_ROUND
        out = [("up", float(up), 0, ""), ("dn", float(dn), 0, "")]
    res = []
    for n, lvl, _, why in out:
        if why:
            res.append((n, lvl, 0, why))
        elif abs(lvl - p_ref) < 1e-9:
            res.append((n, lvl, 0, "at_reference"))
        else:
            res.append((n, lvl, 1 if lvl > p_ref else -1, ""))
    return p_ref, res


@dataclass(frozen=True)
class RL3Tickets:
    """RL3's pre-session tickets of one level kind, coin-sided (the module docstring). `cutoff` one of RL3's cutoffs
    (`RL3_CUTOFFS`): a ticket fills only on bars closing at or before it."""

    kind: str
    cutoff: int
    latency: int | None = None
    source: str = field(default="rl3", init=False)
    latency_free: bool = field(default=True, init=False)

    def __post_init__(self) -> None:
        _latency("rl3", self.latency)
        if self.kind not in RL3_KINDS:
            raise TriggerRefused(f"unknown RL3 level kind {self.kind!r}; one of {RL3_KINDS}")
        if int(self.cutoff) not in RL3_CUTOFFS:
            raise TriggerRefused(f"RL3's cutoff {self.cutoff} is not one of its declared cutoffs (6.1)")

    def calendar_reads(self) -> tuple[bool, bool]:
        """Every kind reads the bar stamped 08:29 (P_ref, an overnight bar, sets every ticket's side), and `on` the
        whole overnight range: all four are overnight readers needing the 08:29 bar (the conservative reading)."""
        return True, True

    def offers(self, hist: History, i: int, ctx: DayContext) -> list[Offer]:
        _, levels = rl3_levels(hist, i, self.kind, prior_void=ctx.prior_void)
        out = []
        for name, lvl, role, why in levels:
            off = Offer("rl3", ctx.session, RTH_OPEN, RL3_SUBS[(self.kind, name)], RTH_OPEN, LIVE_0900, TICKET, lvl,
                        role, expires=int(self.cutoff) - 1, group=f"rl3:{self.kind}", rewrite=True,
                        tag=f"{self.kind}_{name}", void=why)
            check_latency(off, None)
            out.append(off)
        return out


# ------------------------------------------------------------------------------------------------ the naive coin


@dataclass(frozen=True)
class CoinMarks:
    """The naive coin (CHARTER 3.2's baseline; lever table T1 `coin`): a fixed schedule of moments with a coin side,
    entering at alert + L like P-14 (its latency has the lever table's three cells, `lever_space.latency_cells`, unlike
    P-16's latency-free cell). **Its moments, declared:** every `mark_step_min` minutes (lever table T3's step) from
    `first` to `last` inclusive, both on that grid from the 17:00 reopen -- the clock alone chooses them, no bar is read
    to choose a moment. Each moment is the alert and the decision; the order goes live L minutes later; a limit rests
    at the price at the alert and works `limit_window_min` minutes. A session's schedule is
    `components.coin_component`'s (the session's bounds through `components.session_windows_of`)."""

    first: int
    last: int
    latency: int | None = REFERENCE_L
    entry: str = MARKET
    source: str = field(default="coin", init=False)
    latency_free: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        _latency("coin", self.latency)
        _entry(self.entry)
        if not 0 <= int(self.first) <= int(self.last) < DAY_SLOTS:
            raise TriggerRefused(f"the coin's schedule is first <= last on the trading-day clock, got {self.first}, "
                                 f"{self.last}")
        if int(self.first) % MARK_STEP or int(self.last) % MARK_STEP:
            raise TriggerRefused(f"the coin's moments lie on the {MARK_STEP}-minute grid from the reopen")
        if int(self.first) < RTH_OPEN:
            require_overnight(f"the coin's moments from slot {self.first}")

    @property
    def marks(self) -> tuple[int, ...]:
        return tuple(range(int(self.first), int(self.last) + 1, MARK_STEP))

    def calendar_reads(self) -> tuple[bool, bool]:
        """Overnight moments trade on overnight bars; a limit alert at or before 08:30 rests at an overnight bar's
        close; a day market order reads no bar."""
        early = int(self.first) < RTH_OPEN or (self.entry == LIMIT and int(self.first) <= RTH_OPEN)
        return bool(early), False

    def offers(self, hist: History, i: int, ctx: DayContext) -> list[Offer]:
        o, h, l, c = hist.day(i)
        out = []
        for m in self.marks:
            live = m + int(self.latency)
            if self.entry == LIMIT:
                lvl, why = _limit_level(o, c, m)
                off = Offer("coin", ctx.session, m, 0, m, live, LIMIT, lvl, expires=live + LIMIT_WINDOW - 1,
                            tag="coin", void=why)
            else:
                off = Offer("coin", ctx.session, m, 0, m, live, MARKET, tag="coin")
            check_latency(off, self.latency)
            out.append(off)
        return out


SOURCES = ("p14", "p16", "rl3", "coin")


def context_for(trigger, cal, d, session: int, windows: Sequence[Window] = (), *, market: str = "NQ",
                rules: W.Rules = JOURNEY) -> DayContext:
    """A source's day context from the void calendar (Q-169; `extended.day_calendar.day_context` with what the source
    reads, `trigger.calendar_reads()`; None reads nothing), the verified news `windows` added. The calendar raises on a
    held-out or a confirmation-window day (`day_calendar.HeldOutDay`, `ConfirmationDay`)."""
    from extended import day_calendar as DC

    ro, r0829 = trigger.calendar_reads() if trigger is not None else (False, False)
    ctx = DC.day_context(cal, market, d, int(session), reads_overnight=ro, reads_0829=r0829, rules=rules)
    return replace(ctx, windows=tuple(windows))

# ------------------------------------------------------------------------------------------------ the rules for every source


def admit(offers: Iterable[Offer], ctx: DayContext) -> tuple[list[Offer], list[tuple[Offer, str]]]:
    """(kept, refused with the reason) under the calendar, window and overnight rules (the module docstring), decided
    from the clock and the calendar alone: a source's void ('<its reason>'), 'fomc', 'calendar', 'overnight', a window's
    kind ('news', 'closed', 'bls', 'unscheduled') where the order would go live inside it (a re-written ticket is
    refused only when no working stretch remains), 'expired' when nothing of its working window is left."""
    kept: list[Offer] = []
    refused: list[tuple[Offer, str]] = []
    wins = ctx.all_windows()
    for off in offers:
        if off.void:
            refused.append((off, off.void))
        elif ctx.fomc:
            refused.append((off, "fomc"))
        elif ctx.void:
            refused.append((off, "calendar"))
        elif int(off.live) < RTH_OPEN and not overnight_allowed():
            refused.append((off, "overnight"))
        else:
            inside = next((w for w in wins if w.contains(off.live)), None)
            if inside is not None and not off.rewrite:
                refused.append((off, inside.kind))
            elif not segments(off, ctx):
                refused.append((off, inside.kind if inside is not None else "expired"))
            else:
                kept.append(off)
    return kept, refused


def segments(offer: Offer, ctx: DayContext) -> list[tuple[int, int | None]]:
    """The stretches an offer's order works, [(live, last)] (fills on bars stamped live .. last; last None to the
    walk's end): from its live slot to the earliest of its expiry and the next window's start; a re-written offer
    (RL3) again from the minute after a news or closed window ends, never past its expiry. An order that would go live
    inside a window works nothing (or, re-written, from the window's end)."""
    wins = ctx.all_windows()
    end = offer.expires
    cur = int(offer.live)
    out: list[tuple[int, int | None]] = []
    while end is None or cur <= int(end):
        inside = [w for w in wins if w.contains(cur)]
        if inside:
            if not offer.rewrite or any(w.kind not in REWRITE_AFTER for w in inside):
                break
            cur = max(w.last for w in inside) + 1
            continue
        nxt = next((w for w in wins if w.first > cur), None)
        last = end if nxt is None else (nxt.first - 1 if end is None else min(int(end), nxt.first - 1))
        out.append((cur, None if last is None else int(last)))
        if nxt is None or not offer.rewrite or nxt.kind not in REWRITE_AFTER:
            break
        cur = nxt.last + 1
    return out


def rules_for(live: int, ctx: DayContext, base: W.Rules = JOURNEY) -> W.Rules:
    """The walk for an order going live at `live`: `base`, or -- when a window starts after `live` and before the
    base's end -- walked to that window's flatten index and closed there at the price (`flatten="close"`)."""
    nxt = next((w for w in ctx.all_windows() if w.first > int(live)), None)
    if nxt is None or nxt.flatten_index >= int(base.walk_end):
        return base
    return replace(base, name=f"{base.name}+{nxt.kind}@{nxt.first}", walk_end=nxt.flatten_index, flatten="close")


def order_for(offer: Offer, side: int) -> tuple[str, float | None]:
    """(walker order kind, price) of an offer traded on `side`: a market order; a limit at the level; a ticket's fade
    limit at the level (the side against its role: a sell at a resistance, a buy at a support) or break stop one tick
    beyond it (the side of its role: a buy stop a tick above a resistance, a sell stop a tick below a support)."""
    s = int(side)
    if s not in (1, -1):
        raise ValueError(f"side {side} is not +1 or -1")
    if offer.entry == MARKET:
        return W.MARKET, None
    if offer.entry == LIMIT:
        return W.LIMIT_ENTRY, float(offer.level)
    if int(offer.role) not in (1, -1):
        raise TriggerRefused(f"ticket {offer.tag} has no role")
    if s == int(offer.role):
        return W.STOP_ENTRY, float(offer.level) + s * TICK
    return W.LIMIT_ENTRY, float(offer.level)


@dataclass(frozen=True)
class Execution:
    """An offer traded on a side: `trade` the walker's (fill, walk at the bracket) of the stretch that decided it,
    `rules` the walk used there, `attempts` every stretch's trade in order (a re-written ticket can have several) and
    `attempt_rules` each one's walk, `base` the walk without windows."""

    offer: Offer
    side: int
    order_kind: str
    trade: W.Trade
    rules: W.Rules
    attempts: tuple[W.Trade, ...]
    attempt_rules: tuple[W.Rules, ...] = ()
    base: W.Rules = JOURNEY
    flatten_bar: int = -1

    @property
    def filled(self) -> bool:
        return self.trade.fill.status == "filled"

    @property
    def fill_slot(self) -> int:
        """The minute the fill bar opens (the bar stamped it)."""
        return int(self.trade.fill.bar) - 1

    @property
    def exit_slot(self) -> int:
        """The minute the position closes (its exit bar's end)."""
        return int(self.trade.rule.exit[0])

    @property
    def window_flatten(self) -> bool:
        """Whether a window's start ends this stretch's walk (a position open then is flattened there)."""
        return int(self.rules.walk_end) < int(self.base.walk_end)

    @property
    def flatten_slot(self) -> int:
        """Where an open position would close: the end of the window's flatten bar actually booked
        (`window_flatten_trade`: the first present bar from the window's first minute, so it agrees with `exit_slot`
        when the nominal bar is missing; the re-read's n-5), the walker's own walk end when no such bar exists, or the
        base walk's end."""
        if not self.window_flatten:
            return int(self.rules.walk_end)
        return int(self.flatten_bar) if int(self.flatten_bar) >= 0 else int(self.rules.walk_end)

    @property
    def busy_until(self) -> int | None:
        """For an order that never filled: the first minute at which none of its stretches is working any more --
        the latest over its attempts of a cancelled stretch's end (its cutoff, or its walk's end) and of a later
        stretch's live where the re-write found it void (it waited through the window for that re-write). None when it
        never worked (void at its first live). Corrective cycle 1, B-1: a re-written ticket that turns void keeps the
        firm busy for the stretches it worked, so no later decision depends on the price at the re-write."""
        if self.filled:
            raise ValueError("a filled order's busy time is its position's (the chain's)")
        ends = []
        rules = self.attempt_rules or (self.rules,) * len(self.attempts)
        for k, (a, r) in enumerate(zip(self.attempts, rules)):
            if a.fill.status == "void":
                if k > 0:
                    ends.append(int(a.order.live))
            elif a.order.cutoff is not None:
                ends.append(int(a.order.cutoff))
            else:
                ends.append(int(r.walk_end))
        return max(ends) if ends else None


def flatten_bar(o, er: W.Rules, base: W.Rules) -> int | None:
    """The bar a window's flatten books (`window_flatten_trade`): the first present bar from the one ending a minute
    after `er`'s walk end (the bar stamped at the window's first minute, or the minute after an unscheduled release)
    to the base walk's end; None when `er` is the base walk or no such bar exists."""
    if int(er.walk_end) >= int(base.walk_end):
        return None
    hi = min(int(base.walk_end), len(o) - 1)
    return next((j for j in range(int(er.walk_end) + 1, hi + 1) if not math.isnan(o[j])), None)


def window_flatten_trade(tr: W.Trade, er: W.Rules, base: W.Rules, o, h, l, c, costs: W.Costs | None) -> W.Trade:
    """**E-223 M-4 ruling (lead), the as-walked convention for every source:** a position still open when a window
    ends its walk (`rules_for`) is booked at the window's flatten bar -- the bar stamped at the window's first minute
    (for an unscheduled release, the first bar after its minute; the first present bar from there) -- at that bar's
    adverse extreme less two ticks (RL3 4.6 / 5.4's convention, the most conservative of the three texts), exiting at
    the bar's end; where that extreme reaches the trade's resting stop, at the stop. The two ticks are in the price;
    the walker's flatten cost (`EXIT_TICKS`) is charged beside, as at the 15:10 flatten under `STAGE2`. The rule and
    its mirror alike. The deciding reading redraws every outcome (CHARTER 3.2); this is the as-walked booking only."""
    if tr.fill.status != "filled" or int(er.walk_end) >= int(base.walk_end):
        return tr
    if W.walk_end(o, er) != int(er.walk_end):
        return tr                                   # the day's bars end earlier: the walker's own flatten stands
    fb = flatten_bar(o, er, base)
    if fb is None:
        return tr
    S = int(tr.stop_ticks)
    entry = costs.entry_ticks(tr.order.kind) if costs is not None else 0.0

    def rebook(out: W.Outcome | None, side: int, fill: float) -> W.Outcome | None:
        if out is None or not (out.kind == W.FLATTEN).any():
            return out
        k, g, ex, m = out.kind.copy(), out.gross.copy(), out.exit.copy(), out.mae.copy()
        f = k == W.FLATTEN
        adverse = float(l[fb]) if side > 0 else float(h[fb])
        a = int(round(side * (fill - adverse) / TICK))
        if a >= S:
            k[f], g[f], m[f] = W.STOP, -S, S
        else:
            g[f] = -a - W.FLATTEN_SLIP_TICKS
            m[f] = np.maximum(m[f], max(a, 0))
        ex[f] = fb
        nr = W.net_r(g, k, S, entry_ticks=entry, costs=costs) if costs is not None else None
        return W.Outcome(k, ex, m, g, nr)

    return replace(tr, rule=rebook(tr.rule, int(tr.order.side), float(tr.fill.price)),
                   mirror=rebook(tr.mirror, -int(tr.order.side), float(tr.mirror_price)))


def execute(offer: Offer, side: int, hist: History, i: int, ctx: DayContext, stop_ticks: int, rr: float, *,
            rules: W.Rules = JOURNEY, costs: W.Costs | None = None) -> Execution:
    """Trade an admitted offer on `side` at the bracket (stop ticks, R): each working stretch (`segments`) is one
    walker order (live at the stretch's start, cut off at its end, walked by `rules_for`) until one fills or voids; a
    position open at a window's start is booked by `window_flatten_trade`."""
    if offer.void:
        raise TriggerRefused(f"a void offer ({offer.void}) is not traded")
    segs = segments(offer, ctx)
    if not segs:
        raise TriggerRefused("an offer with no working stretch is not traded (admit refuses it)")
    o, h, l, c = hist.day(i)
    kind, price = order_for(offer, side)
    attempts, used = [], []
    tr = er = None
    for lv, last in segs:
        er = rules_for(lv, ctx, rules)
        order = W.Order(kind, int(side), int(lv), price, None if last is None else int(last) + 1)
        tr = W.trade(order, o, h, l, c, int(stop_ticks), (float(rr),), rules=er, costs=costs)
        tr = window_flatten_trade(tr, er, rules, o, h, l, c, costs)
        attempts.append(tr)
        used.append(er)
        if tr.fill.status in ("filled", "void"):
            break
    fb = flatten_bar(o, er, rules)
    return Execution(offer, int(side), kind, tr, er, tuple(attempts), tuple(used), rules, -1 if fb is None else fb)


# ------------------------------------------------------------------------------------------------ the coin

#: the design note's coin key (`docs/plans/scripts/three_way/three_way_arith.py` KEY_KINDS["coin"]): tag and fields
COIN_TAG = 3
COIN_FIELDS = ("part", "history", "seed_index", "start", "underlying", "moment", "draw_kind")
WORD = 2 ** 32
#: one code per underlying: MNQ and NQ are one (N-4)
UNDERLYING = {"NQ": 1, "MNQ": 1}
#: the draw kinds of a coin key (other kinds -- the redraw, a missed signal -- are the three-way runner's to add)
DRAW_SIDE = 1
#: offers a decision may hold (RL3's seven tickets the most)
MOMENT_SUBS = 16


@dataclass(frozen=True)
class CoinUnit:
    """One user's coin: the declaration's coin role seed, the part and history, the seed's index, the unit's start
    day and the underlying. No account and no firm index (m-9): in the evaluation that means only that opposite
    positions across the user's accounts or firms are refused; in the playbook, sides come from each design's own
    trigger, under the no-harm floor, with accounts alternating (E-221)."""

    seed: int
    part: int
    history: int
    seed_index: int
    start: int
    underlying: str = "NQ"


def moment(offer: Offer) -> int:
    """The coin key's moment: (session x 1440 + decision slot) x 16 + sub -- a session index and a minute offset."""
    m = (int(offer.session) * DAY_SLOTS + int(offer.decision)) * MOMENT_SUBS + int(offer.sub)
    if not 0 <= m < WORD:
        raise ValueError(f"moment {m} is off the key's grid (every word below 2^32)")
    return m


def coin_key(unit: CoinUnit, offer: Offer, draw_kind: int = DRAW_SIDE) -> list[int]:
    """[seed, 3, part, history, seed index, start, underlying, moment, draw kind]: refused when the seed is not
    positive, an index is negative, or any word is at or above 2^32."""
    if unit.underlying not in UNDERLYING:
        raise ValueError(f"unknown underlying {unit.underlying!r}")
    vals = [int(unit.part), int(unit.history), int(unit.seed_index), int(unit.start), UNDERLYING[unit.underlying],
            moment(offer), int(draw_kind)]
    if int(unit.seed) <= 0 or any(v < 0 for v in vals):
        raise ValueError("a seed is positive and every index non-negative")
    if int(unit.seed) >= WORD or any(v >= WORD for v in vals):
        raise ValueError("every word of a key is below 2^32: numpy splits larger integers into words")
    return [int(unit.seed), COIN_TAG, *vals]


def key_state(key: Sequence[int], words: int = 4) -> tuple[int, ...]:
    """What numpy seeds from a key (`SeedSequence(key).generate_state`), for the key guard."""
    return tuple(int(x) for x in np.random.SeedSequence(list(key)).generate_state(words))


def coin_uniform(key: Sequence[int]) -> float:
    """The key's uniform on the symmetric grid (2 i + 1) 2^-53: i the top 52 bits of Philox's first raw output."""
    raw = int(np.random.Philox(np.random.SeedSequence(list(key))).random_raw())
    return (2 * (raw >> 12) + 1) * 2.0 ** -53


def coin_side(unit: CoinUnit, offer: Offer) -> int:
    """+1 (long) when the offer's uniform is below one half, else -1."""
    return 1 if coin_uniform(coin_key(unit, offer)) < 0.5 else -1


__all__ = ["TASK", "LATENCIES", "REFERENCE_L", "LIMIT_WINDOW", "MARK_STEP", "ENTRIES", "MARKET", "LIMIT", "TICKET",
           "RTH_OPEN", "LIVE_0900", "CLOSED_FIRST", "CLOSED_LAST", "BLS_CLEAR", "SESSION_END", "GAP_MINUTES",
           "JOURNEY", "P14_K", "P14_LAST", "RL3_KINDS", "RL3_CUTOFFS", "RL3_SUBS", "PRIOR_RTH", "WINDOW_KINDS", "REWRITE_AFTER",
           "H2_ROW", "OvernightRefused", "TriggerRefused", "decision_rows", "overnight_allowed", "require_overnight",
           "History", "Window", "release_window", "DayContext", "Offer", "check_latency", "breakout_events",
           "P14Breakout", "p16_grid", "P16Marks", "rl3_levels", "RL3Tickets", "CoinMarks", "SOURCES", "context_for", "admit", "segments",
           "rules_for", "order_for", "Execution", "flatten_bar", "window_flatten_trade", "execute", "COIN_TAG", "COIN_FIELDS", "WORD",
           "UNDERLYING",
           "DRAW_SIDE", "MOMENT_SUBS", "CoinUnit", "moment", "coin_key", "key_state", "coin_uniform", "coin_side"]
