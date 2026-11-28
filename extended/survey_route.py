"""Q-215: the survey's real-bar route -- a survey point of the Topstep $50K lever space (the design dict
`search_space.from_lever_space` decodes) turned into `extended.design_trades` specs, and through `build_trades` and
`facts_for` into the trade table, its aux frame and the `three_way_baseline.TradeFacts` the survey's evaluation
consumes. **One convention with H4-B**: nothing here walks, fills, costs or formats a trade -- every one of those steps
is `design_trades`' (itself H4's `h4_coin_source` plumbing, held to P-16's registered trades hash by Q-213's identity);
this module only maps levers to a spec and stitches the per-day specs' tables into the design's one table.

    from extended import survey_route as SR
    rt = SR.route(space, design, side_rules={"p14": "with_breakout", "rl3": "fade"},
                  source_params={"rl3": {"kind": "pd", "cutoff": cutoff}})       # every lever mapped or refused
    out = SR.build(rt, hist, cal=cal, day_kinds=kinds, news_windows=None, fresh_rr=crr, fee_for_stop=fee,
                   tick_value=tv, market_entry_ticks=slip)                       # -> RouteTrades(trades, aux, ...)
    facts = SR.facts(out, hist.days, tick_value=tv)                              # (day, j) -> TB.TradeFacts

**Every lever is mapped, passed on, or refused, by name** (`LEVER_ROUTE`, a partition of `lever_space.LEVERS` that a
test holds equal to the table): the slot levers T1 (the source), T2 (the slot on), T3 (the window's offsets), T4 (L),
T5 (the entry), S1 (the stop multiple) and S2 (w) are the route's; T7 is the route's and maps only `off` (`admit` needs
the admission forecast wired into the route, which it is not: refused by name); the declared T2b, T6 and T8 are read
through the library (the space's NY split; `triggers.LIMIT_WINDOW`; T8's coin is the evaluation's redraw, the table
carrying the design's own trigger side, as `design_trades` does); the dollar-risk, mix and account-policy levers (S3 to
S5, A1 to A21) are the firm path's and are returned unchanged in `Route.firm_levers`; the dropped S6 to S9, A13 and
A14 hold their table settings (no time stop, no breakeven move -- the walk is `triggers.JOURNEY` --, one bracket, the
contracts derived downstream). A design key whose lever is in none of these, a source with no playbook side
(`trigger_sides.NO_SIDE`: `coin`, `p16`), a missing side rule, RL3 without its declared level kind and cutoff, a space
without S1, a design the space refuses, or a T8 other than the coin: each refuses (`RouteRefused`), never a default.

**A component on a date** (`components.Design`'s convention): the slot's offsets read from that date's session start
(`Space.windows_on`), an offer belonging to it when its order goes live inside the window (`Windowed`, the filter of
`components.schedule_day`). P-14's alerts are the window less L, clipped to P-14's span -- the playbook's
`_trigger_on` (C3-2), so the playbook and the route build one trigger (a test holds them equal); RL3's tickets are its
declared kind's, alert 08:30 and live 09:00 CT (the space holds that slot inside the window), cut off at the declared
cutoff, one-cancels-other by kind. The side is the design's own (`trigger_sides.trigger_side` under the declared
rules); the evaluation's redraw removes direction later (CHARTER 2).

**The stop (S1)**: k times the session's trailing range T(d) (`s1_range.LEVER_SESSIONS`: `ny_am` and `ny_pm` take
`ny`'s `trail20_range_pts`, an overnight session its own), computed here from the history exactly as
`s1_range.add_trailing` computes it (`trailing`: the same window ranges, eligibility, void rule and trailing mean,
from **earlier days only**; an identity on synthetic bars holds the two equal). A day stands aside -- counted by reason,
never traded -- when T(d) is undefined (`no_trail`) or k x T(d) points lies outside `lever_space.stop_caps()` (unrounded,
both edges inclusive: S1's declared translation, `s1_range.k_bounds`; `below_floor`, `above_cap`). Inside the caps the
stop is k x T(d) in whole ticks, half up, at least one (`vol_descriptive.band_ticks`, RD-04's and Q-121's rule for a
bracket scaled by the trailing range; the caps hold after rounding since they are whole ticks). **The target** is
floor(w x stop) whole ticks (`walker.target_ticks`, the lever table's S2). The walk is at every component's w (the
design's R grid, `RouteTrades.rr_grid`), each trade's own w in the aux frame's `rr`.

**Costs** are `design_trades`' (Stage 2's): `fee_for_stop(stop)` is the caller's `atlas_a3.fee_by_stop` at the day's
stop, a market fill pays `market_entry_ticks`, a resting fill none; each trade's entry ticks go to its facts
(`facts` sets `e_ticks` trade by trade, since one design may mix a market and a resting component).

**Nothing here reads a file or a bar store**: the bars come in as a `triggers.History` the caller built inside
`extended.search_cut` (search years only: refused past 2023-12-29 and in the confirmation window), the void calendar
as `day_calendar.Sources`, the day kinds as Stage 2's days table gives them (every day named, never defaulted). Nothing
here draws randomness.
"""
from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import day_calendar as DC
from extended import design_trades as DT
from extended import h4_coin_source as CS
from extended import lever_space as LS
from extended import s1_range as S1R
from extended import search_space as SS
from extended import three_way_baseline as TB
from extended import trigger_sides as TS
from extended import triggers as T
from extended import vol_descriptive as V
from extended import walker as W

TASK = "Q-215"
FIRM = "topstep_50k"                       # `search_space.from_lever_space`'s firm: the only lever space routed here
MARKET_NAME = "NQ"                         # the void calendar's market (`day_calendar.MARKETS`)

#: how the route handles each lever of the table (`lever_space.LEVERS`): a partition, held equal to the table
ROUTE, LIBRARY, FIRM_PATH, DROPPED = "route", "library", "firm_path", "dropped"
LEVER_ROUTE: dict[str, str] = {
    "T1": ROUTE, "T2": ROUTE, "T3": ROUTE, "T4": ROUTE, "T5": ROUTE, "T7": ROUTE, "S1": ROUTE, "S2": ROUTE,
    "T2b": LIBRARY, "T6": LIBRARY, "T8": LIBRARY,
    "S3": FIRM_PATH, "S4": FIRM_PATH, "S5": FIRM_PATH,
    "A1": FIRM_PATH, "A2": FIRM_PATH, "A3": FIRM_PATH, "A4": FIRM_PATH, "A5": FIRM_PATH, "A6": FIRM_PATH,
    "A7": FIRM_PATH, "A8": FIRM_PATH, "A9": FIRM_PATH, "A10": FIRM_PATH, "A11": FIRM_PATH, "A12": FIRM_PATH,
    "A15": FIRM_PATH, "A16": FIRM_PATH, "A17": FIRM_PATH, "A18": FIRM_PATH, "A19": FIRM_PATH, "A20": FIRM_PATH,
    "A21": FIRM_PATH,
    "S6": DROPPED, "S7": DROPPED, "S8": DROPPED, "S9": DROPPED, "A13": DROPPED, "A14": DROPPED,
}
#: a slot dimension's key (after `<session>.<i>.`) and the lever it carries (`search_space.from_lever_space`)
SLOT_KEYS = {"on": "T2", "T1": "T1", "T4": "T4", "T5": "T5", "first": "T3", "last": "T3", "S1": "S1", "S2": "S2"}
#: the sources a component may take here: those with a playbook side (`trigger_sides.RULES`)
SIDED = tuple(TS.RULES)
RL3_PARAMS = ("kind", "cutoff")
T7_MAPPED = ("off",)                       # T7's cells the route maps: no admission forecast is wired into it
T8_EVALUATION = "coin"                     # the lever table's T8: the evaluation's coin (CHARTER 3.2), never traded
STAND_ASIDE = ("no_trail", "below_floor", "above_cap")
#: aux columns this route adds beside `design_trades`' own
AUX_ADDED = ("component", "source", "rr", "k", "stop_ticks", "entry_ticks", "latency")


class RouteRefused(ValueError):
    """A survey point, a lever or an input the route cannot stand behind (the module docstring)."""


# ------------------------------------------------------------------------------------------------ the component


@dataclass(frozen=True)
class Windowed:
    """A trigger restricted to a component's window: an offer belongs to it when its order goes live inside
    [first, last] (`components.schedule_day`'s filter). Its `source` and `calendar_reads` are the trigger's."""

    trigger: Any
    first: int
    last: int

    @property
    def source(self) -> str:
        return self.trigger.source

    def calendar_reads(self) -> tuple[bool, bool]:
        return self.trigger.calendar_reads()

    def offers(self, hist: T.History, i: int, ctx: T.DayContext) -> list[T.Offer]:
        return [o for o in self.trigger.offers(hist, i, ctx) if int(self.first) <= int(o.live) <= int(self.last)]


def p14_alerts(first: int, last: int, latency: int) -> tuple[int, int]:
    """P-14's alert slots for a window [first, last] of live slots: the window less L, clipped to P-14's span (the
    playbook's `_trigger_on`, C3-2)."""
    lat = int(latency)
    lo = min(max(int(first) - lat, 0), T.P14_LAST)
    hi = max(min(int(last) - lat, T.P14_LAST), lo)
    return lo, hi


@dataclass(frozen=True)
class SlotRoute:
    """One active slot of the point: its session, source, L, entry, window offsets, stop multiple k, w, side rule and
    the source's declared parameters (RL3's kind and cutoff)."""

    name: str
    session: str
    order: int
    source: str
    latency: int | None
    entry: str
    first: int
    last: int
    k: float
    w: float
    side_rule: Any
    params: Mapping[str, Any] = field(default_factory=dict)

    @property
    def entry_kind(self) -> str:
        return "market" if self.entry == T.MARKET else "resting"

    @property
    def s1_session(self) -> str:
        return S1R.LEVER_SESSIONS[self.session]

    def trigger(self, first: int, last: int) -> Any:
        """The library's trigger for this slot on a date whose window is [first, last] (live slots)."""
        try:
            if self.source == "p14":
                lo, hi = p14_alerts(first, last, int(self.latency))
                return T.P14Breakout(latency=int(self.latency), entry=self.entry, first=lo, last=hi, k=T.P14_K)
            return T.RL3Tickets(str(self.params["kind"]), int(self.params["cutoff"]))
        except (T.TriggerRefused, T.OvernightRefused) as e:
            raise RouteRefused(f"slot {self.name}: the trigger library refuses its {self.source} trigger on the window "
                               f"[{first}, {last}]: {e}") from e

    def side_of(self, trigger: Any) -> Callable[[T.Offer], int]:
        rule = self.side_rule
        if self.source == "rl3" and isinstance(rule, str):
            rule = {n: rule for n in TS.rl3_names(trigger)}

        def side(offer: T.Offer) -> int:
            return int(TS.trigger_side(trigger, rule, offer).side)

        return side


@dataclass(frozen=True)
class Route:
    """A survey point as the route reads it: its id, its active slots in the space's order, the firm path's levers
    unchanged, and how every lever of the point was handled (`provenance`)."""

    design_id: str
    slots: tuple[SlotRoute, ...]
    firm_levers: Mapping[str, Any]
    provenance: Mapping[str, str]
    space: Any = field(repr=False, compare=False)
    design: Mapping[str, Any] = field(repr=False, compare=False)

    def windows_on(self, day: date) -> dict[str, tuple[int, int]]:
        """The active slots' windows on trading day `day`, live slots after the reopen (`Space.windows_on`)."""
        return {name: (int(a), int(b)) for name, _, a, b in self.space.windows_on(self.design, day)}


def _lever_of(space: Any, key: str) -> str:
    try:
        return space.dim(key).lever
    except KeyError:
        return ""


def route(space: Any, design: Mapping[str, Any], *, side_rules: Mapping[str, Any],
          source_params: Mapping[str, Mapping[str, Any]]) -> Route:
    """The point's route, every lever mapped, passed on to the firm path, or refused by name (the module docstring).
    `side_rules` the declared playbook side rule per source used (`trigger_sides.RULES`; RL3's one word applies to every
    level of its kind); `source_params` each source's declared parameters (RL3: exactly `kind` and `cutoff`)."""
    if getattr(space, "firm", None) != FIRM:
        raise RouteRefused(f"the route maps the Topstep $50K lever space (firm {FIRM!r}), not {space.firm!r}")
    why = space.check(design)
    if why is not None:
        raise RouteRefused(f"REFUSED: a point the space refuses ({why[0]}: {why[1]})")
    prov: dict[str, str] = {}
    firm: dict[str, Any] = {}
    slot_names = {s.name for s in space.slots}
    for key, value in design.items():
        if key in (SS.OVERLAP_KEY, SS.FIRMS_KEY):
            prov[key] = f"checked by the space ({value!r})"
            continue
        lever = _lever_of(space, key)
        slot, _, sub = key.rpartition(".")
        how = LEVER_ROUTE.get(lever)
        if how is None:
            raise RouteRefused(f"REFUSED: the point's key {key!r} carries lever {lever or '(none)'!r}, which the route "
                               "neither maps nor passes to the firm path")
        if slot in slot_names:
            if SLOT_KEYS.get(sub) != lever or how != ROUTE:
                raise RouteRefused(f"REFUSED: slot key {key!r} ({lever}) is not one of the route's slot levers "
                                   f"{sorted(SLOT_KEYS)}")
            continue
        if how == FIRM_PATH:
            firm[key] = value
            prov[key] = "firm path (passed on unchanged)"
        elif lever == "T7":
            if value not in T7_MAPPED:
                raise RouteRefused(f"REFUSED: T7 = {value!r} -- the route maps only {T7_MAPPED}: no admission forecast "
                                   "(t7_forecast) is wired into it")
            prov[key] = "route: no admission (T7 off)"
        else:
            raise RouteRefused(f"REFUSED: the point's key {key!r} ({lever}, {how}) is not a design-wide lever the "
                               "route reads")
    for key, value in space.fixed.items():
        if key in (SS.OVERLAP_KEY, SS.FIRMS_KEY):
            continue
        how = LEVER_ROUTE.get(key)
        if how is None:
            raise RouteRefused(f"REFUSED: the space fixes {key!r}, which the route neither maps nor passes on")
        if how == FIRM_PATH:
            firm[key] = value
            prov[key] = "firm path (fixed by the space, passed on)"
        elif key == "T8":
            if tuple(value) != (T8_EVALUATION,):
                raise RouteRefused(f"REFUSED: T8 is fixed at {value!r}, not the evaluation's {T8_EVALUATION!r}: the "
                                   "route's side convention would need re-examining")
            prov[key] = ("library: the evaluation's coin, applied by the redraw downstream; the table carries the "
                         "design's own trigger side (trigger_sides)")
        elif key == "T6":
            if tuple(value) != (T.LIMIT_WINDOW,):
                raise RouteRefused(f"REFUSED: T6 is fixed at {value!r}, the library's limit window is "
                                   f"{T.LIMIT_WINDOW}")
            prov[key] = "library: triggers.LIMIT_WINDOW"
        elif key == "T2b":
            prov[key] = "library: the space's NY split (lever_space.check_ny_boundary, Space.check)"
        else:
            raise RouteRefused(f"REFUSED: the space fixes {key!r} ({how}), which the route does not read")
    for key, cls in space.refused.items():
        if key in LEVER_ROUTE:
            prov.setdefault(key, f"refused by the loader ({cls})")
    slots = []
    for order, sl in enumerate(space.slots):
        if design.get(SS.slot_dim(sl.name, "on")) != SS.ON:
            continue
        slots.append(_slot(space, design, sl, order, side_rules, source_params))
    if not slots:
        raise RouteRefused("REFUSED: no component is on")
    for lever in ("T1", "T2", "T3", "T4", "T5", "S1", "S2"):
        prov[lever] = "route: per slot"
    return Route(SS.design_id(design), tuple(slots), dict(firm), dict(prov), space, dict(design))


def _slot(space: Any, design: Mapping[str, Any], sl: Any, order: int, side_rules: Mapping[str, Any],
          source_params: Mapping[str, Mapping[str, Any]]) -> SlotRoute:
    name = sl.name
    g = lambda k: design.get(SS.slot_dim(name, k))  # noqa: E731
    src = g("T1")
    if src in TS.NO_SIDE:
        raise RouteRefused(f"REFUSED: slot {name}'s source {src!r} offers no playbook side: {TS.NO_SIDE[src]}")
    if src not in SIDED:
        raise RouteRefused(f"REFUSED: slot {name}'s source {src!r} is not one of the route's sources {SIDED}")
    if SS.slot_dim(name, "S1") not in space.names():
        cls = space.refused.get("S1", "absent from the space")
        raise RouteRefused(f"REFUSED: slot {name} has no stop width: S1 is not a lever of the space ({cls}); the "
                           "route never types a stop")
    if src not in side_rules:
        raise RouteRefused(f"REFUSED: no declared side rule for source {src!r} (slot {name})")
    rule = side_rules[src]
    lat, entry = g("T4"), g("T5")
    params: dict[str, Any] = {}
    if src == "p14":
        if entry not in T.ENTRIES or lat not in LS.latency_cells("p14"):
            raise RouteRefused(f"REFUSED: slot {name}: P-14 takes an entry of {T.ENTRIES} and an L of "
                               f"{LS.latency_cells('p14')}, got {entry!r}, {lat!r}")
        probe = T.P14Breakout(latency=int(lat), entry=entry, first=T.RTH_OPEN, last=T.P14_LAST)
        try:
            TS.check_rule(probe, rule)
        except TS.SideRefused as e:
            raise RouteRefused(f"REFUSED: slot {name}: {e}") from e
    else:
        if entry != SS.TICKET or lat is not None:
            raise RouteRefused(f"REFUSED: slot {name}: RL3 takes its tickets, latency-free, got {entry!r}, {lat!r}")
        got = source_params.get("rl3")
        if not isinstance(got, Mapping) or sorted(got) != sorted(RL3_PARAMS):
            raise RouteRefused(f"REFUSED: slot {name}: RL3's declared parameters are exactly {RL3_PARAMS}, got "
                               f"{None if got is None else sorted(got)}")
        params = {"kind": str(got["kind"]), "cutoff": int(got["cutoff"])}
        try:
            probe = T.RL3Tickets(params["kind"], params["cutoff"])
        except T.TriggerRefused as e:
            raise RouteRefused(f"REFUSED: slot {name}: {e}") from e
        full = {n: rule for n in TS.rl3_names(probe)} if isinstance(rule, str) else rule
        try:
            TS.check_rule(probe, full)
        except TS.SideRefused as e:
            raise RouteRefused(f"REFUSED: slot {name}: {e}") from e
    if sl.session not in S1R.LEVER_SESSIONS:
        raise RouteRefused(f"REFUSED: slot {name}: session {sl.session!r} has no trailing range (s1_range)")
    k, w = float(g("S1")), float(g("S2"))
    if not (math.isfinite(k) and k > 0 and math.isfinite(w) and w > 0):
        raise RouteRefused(f"REFUSED: slot {name}: S1 and S2 are positive, got {k!r}, {w!r}")
    return SlotRoute(name, sl.session, order, src, None if lat is None else int(lat), entry, int(g("first")),
                     int(g("last")), k, w, rule if isinstance(rule, str) else dict(rule), params)


# ------------------------------------------------------------------------------------------------ the stop (S1)


def _date(d: str) -> date:
    return date.fromisoformat(str(d)[:10])


def _kinds(hist: T.History, day_kinds: Mapping[str, str]) -> np.ndarray:
    missing = [d for d in hist.days if d not in day_kinds]
    if missing:
        raise RouteRefused(f"REFUSED: day kinds are given for every day, not for {len(missing)} (first {missing[0]})")
    return np.array([str(day_kinds[d]) for d in hist.days])


def day_ranges(hist: T.History, cal: DC.Sources) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Each day's own range per S1 session (`s1_range.day_table`'s `range_<session>`: `ny` the walker day's, the bars
    ending 17:01 to 15:10 CT; an overnight session its window's) and its void per session (`s1_range.VOID_RULE`)."""
    n = len(hist)
    rng = {s: np.full(n, np.nan) for s in S1R.SESSIONS}
    void = {s: np.zeros(n, dtype=bool) for s in S1R.SESSIONS}
    for i, d in enumerate(hist.days):
        o, h, l, _ = hist.day(i)
        dd = _date(d)
        rng["ny"][i] = S1R.window_range(h, l, 0, W.C_FLAT)
        for s, (a, b) in S1R.session_windows(dd).items():
            rng[s][i] = S1R.window_range(h, l, a, b)
        for s in S1R.SESSIONS:
            ro, r0829 = S1R.VOID_RULE[s]
            void[s][i] = bool(DC.day_flags(cal, MARKET_NAME, dd, reads_overnight=ro, reads_0829=r0829).void)
    return rng, void


def trailing(hist: T.History, *, day_kinds: Mapping[str, str], cal: DC.Sources) -> dict[str, np.ndarray]:
    """Each S1 session's trailing range T(d) on every day of the history, from **earlier days only**
    (`s1_range.add_trailing`'s rule: the mean over the 20 most recent earlier eligible days, `eligible`)."""
    DT.check_search_days(hist.days)
    kinds = _kinds(hist, day_kinds)
    rng, void = day_ranges(hist, cal)
    walked = np.isin(kinds, S1R.WALKED_KINDS)
    out = {}
    for s in S1R.SESSIONS:
        ok = walked if s == "ny" else walked & ~void[s]
        out[s] = S1R.trailing_ranges(rng[s], ok)
    return out


def stop_on(k: float, trail_pts: float, caps: Mapping[str, Any], tick: float = W.TICK) -> tuple[int | None, str]:
    """(stop ticks, '') or (None, the stand-aside reason): S1's translation, the caps checked unrounded, then whole
    ticks half up (`vol_descriptive.band_ticks`)."""
    if not math.isfinite(float(trail_pts)):
        return None, "no_trail"
    x = float(k) * float(trail_pts)
    if x < int(caps["floor_ticks"]) * tick:
        return None, "below_floor"
    if x > int(caps["cap_ticks"]) * tick:
        return None, "above_cap"
    s = V.band_ticks(float(trail_pts), float(k))
    if s is None or not int(caps["floor_ticks"]) <= s <= int(caps["cap_ticks"]):
        raise RouteRefused(f"the rounded stop {s} left the caps: {caps}")
    return int(s), ""


def stops(rt: Route, trail: Mapping[str, np.ndarray], caps: Mapping[str, Any] | None = None
          ) -> dict[str, list[tuple[int | None, str]]]:
    """Per slot, per history day: its stop in ticks, or why it stands aside."""
    caps = LS.stop_caps() if caps is None else caps
    return {sl.name: [stop_on(sl.k, float(x), caps) for x in trail[sl.s1_session]] for sl in rt.slots}


# ------------------------------------------------------------------------------------------------ the trades


@dataclass
class RouteTrades:
    """The design's one trade table (`resolved_coin.cell_trades`' schema, every component's, at the design's R grid),
    the aux frame row for row (with `AUX_ADDED`), the counts per slot, and the R grid."""

    trades: pd.DataFrame
    aux: pd.DataFrame
    counts: dict[str, Any]
    rr_grid: tuple[float, ...]


def rr_grid(rt: Route) -> tuple[float, ...]:
    """The design's R grid: every component's w, refused when two distinct w share one column label (`:g`)."""
    ws = sorted({float(sl.w) for sl in rt.slots})
    labels = [f"{w:g}" for w in ws]
    if len(set(labels)) != len(labels):
        raise RouteRefused(f"REFUSED: two components' w {ws} share a column label {labels}")
    return tuple(ws)


def _context(trigger: Any, cal: DC.Sources, hist: T.History, i: int,
             news_windows: Callable[[int], Sequence[T.Window]] | None) -> T.DayContext:
    wins = tuple(news_windows(i)) if news_windows is not None else ()
    return T.context_for(trigger, cal, _date(hist.days[i]), i, wins, market=MARKET_NAME, rules=T.JOURNEY)


def _plans(rt: Route, hist: T.History, st: Mapping[str, list[tuple[int | None, str]]]
           ) -> dict[str, dict[tuple[int, int, int], list[int]]]:
    """Per slot, its traded days grouped by (stop, window first, window last) on each date."""
    out: dict[str, dict[tuple[int, int, int], list[int]]] = {sl.name: {} for sl in rt.slots}
    for i, d in enumerate(hist.days):
        wins = rt.windows_on(_date(d))
        for sl in rt.slots:
            s, _ = st[sl.name][i]
            if s is None:
                continue
            a, b = wins[sl.name]
            out[sl.name].setdefault((int(s), a, b), []).append(i)
    return out


def build(rt: Route, hist: T.History, *, cal: DC.Sources, day_kinds: Mapping[str, str],
          news_windows: Callable[[int], Sequence[T.Window]] | None, fresh_rr: float,
          fee_for_stop: Callable[[int], float], tick_value: float, market_entry_ticks: float,
          trail: Mapping[str, np.ndarray] | None = None, caps: Mapping[str, Any] | None = None,
          tick: float = W.TICK) -> RouteTrades:
    """The design's trades on the history's days (the module docstring), every step `design_trades.build_trades`'
    on each slot's days grouped by their stop and window. `news_windows(i)` the verified news windows of day i, or None
    where none reaches the firm's accounts (the caller states which; never defaulted). `trail` may be passed when
    already computed (`trailing`)."""
    DT.check_search_days(hist.days)
    _kinds(hist, day_kinds)
    trail = trailing(hist, day_kinds=day_kinds, cal=cal) if trail is None else trail
    st = stops(rt, trail, caps)
    grid = rr_grid(rt)
    frames, auxes = [], []
    counts: dict[str, Any] = {}
    cache: dict[tuple[tuple[bool, bool], int], T.DayContext] = {}
    for sl, (name, groups) in zip(rt.slots, _plans(rt, hist, st).items()):
        c: dict[str, Any] = {"days": len(hist), "traded_days": 0, "stand_aside": {r: 0 for r in STAND_ASIDE},
                             "offers": 0, "admitted": 0, "filled": 0, "oco_cancelled": 0, "dropped_sigma_lt_2": 0,
                             "refused": {}, "unfilled": {}}
        for s, why in st[name]:
            if s is None:
                c["stand_aside"][why] += 1
        for (s, a, b), days in sorted(groups.items()):
            trig = sl.trigger(a, b)
            reads = trig.calendar_reads()
            for i in days:
                if (reads, i) not in cache:
                    cache[(reads, i)] = _context(trig, cal, hist, i, news_windows)
            fee = float(fee_for_stop(int(s)))
            if not (math.isfinite(fee) and fee >= 0):
                raise RouteRefused(f"REFUSED: the fee at stop {s} is {fee!r}")
            spec = DT.DesignSpec(f"{name}@{s}:{a}-{b}", Windowed(trig, a, b), sl.side_of(trig), int(s), T.JOURNEY,
                                 "journey", True, sl.entry_kind)
            out = DT.build_trades(spec, hist, lambda i, r=reads: cache[(r, i)], day_kinds=day_kinds, rr_grid=grid,
                                  fresh_rr=fresh_rr, fee_micro_eq=fee, tick_value=tick_value,
                                  market_entry_ticks=market_entry_ticks, days=days, tick=tick)
            c["traded_days"] += len(days)
            for key in ("offers", "admitted", "filled", "oco_cancelled", "dropped_sigma_lt_2"):
                c[key] += int(out.counts[key])
            for key in ("refused", "unfilled"):
                for why, n in out.counts[key].items():
                    c[key][why] = c[key].get(why, 0) + int(n)
            if len(out.trades):
                ax = out.aux.copy()
                ax["component"], ax["source"], ax["rr"], ax["k"] = name, sl.source, float(sl.w), float(sl.k)
                ax["stop_ticks"], ax["entry_ticks"] = int(s), float(out.counts["entry_ticks"])
                ax["latency"] = sl.latency
                ax["_slot"] = int(sl.order)
                frames.append(out.trades)
                auxes.append(ax)
        c["refused"] = dict(sorted(c["refused"].items()))
        c["unfilled"] = dict(sorted(c["unfilled"].items()))
        counts[name] = c
    if not frames:
        return RouteTrades(pd.DataFrame(), pd.DataFrame(), counts, grid)
    cols = list(frames[0].columns)
    if any(list(f.columns) != cols for f in frames):
        raise RouteRefused("the components' tables differ in their columns")
    trades = pd.concat(frames, ignore_index=True)
    aux = pd.concat(auxes, ignore_index=True)
    order = np.lexsort((np.arange(len(aux)), aux["_slot"].to_numpy(int),
                        trades["decision_slot_minutes"].to_numpy(int), trades["entry_t"].to_numpy(float),
                        trades["date"].astype(str).str.replace("-", "").astype(np.int64).to_numpy()))
    trades = trades.iloc[order].reset_index(drop=True)
    aux = aux.iloc[order].drop(columns="_slot").reset_index(drop=True)
    return RouteTrades(trades, aux, counts, grid)


def facts(rt_trades: RouteTrades, dates: Sequence[str], *, tick_value: float) -> dict[tuple[int, int], TB.TradeFacts]:
    """`design_trades.facts_for` on the design's table, each trade's entry ticks its own component's."""
    if not len(rt_trades.trades):
        return {}
    got = DT.facts_for(rt_trades.trades, rt_trades.aux, dates, tick_value=tick_value, rr_cols=rt_trades.rr_grid,
                       entry_ticks=0.0)
    e = rt_trades.aux["entry_ticks"].to_numpy(float)
    if len(got) != len(e):
        raise RouteRefused("the facts and the aux frame differ in length")
    return {key: dataclasses.replace(f, e_ticks=float(x)) for (key, f), x in zip(got.items(), e)}


# ------------------------------------------------------------------------------------------------ what is decided when


def decisions(rt: Route, hist: T.History, i: int, *, cal: DC.Sources, day_kinds: Mapping[str, str],
              news_windows: Callable[[int], Sequence[T.Window]] | None, trail: Mapping[str, np.ndarray] | None = None,
              caps: Mapping[str, Any] | None = None, tick: float = W.TICK) -> list[dict[str, Any]]:
    """Everything the route decides for day i's offers before any fill, by the code path `build` takes: per slot its
    stop (or stand-aside), its window, and each offer of its windowed trigger with its moment, level, admission and
    side, and the volatility at its alert. The shift-invariance test holds every record with alert <= t unchanged
    when every bar stamped t or later is replaced."""
    trail = trailing(hist, day_kinds=day_kinds, cal=cal) if trail is None else trail
    caps = LS.stop_caps() if caps is None else caps
    wins = rt.windows_on(_date(hist.days[i]))
    closes = [hist.c[j] for j in range(len(hist))]
    out: list[dict[str, Any]] = []
    for sl in rt.slots:
        s, why = stop_on(sl.k, float(trail[sl.s1_session][i]), caps, tick)
        a, b = wins[sl.name]
        out.append({"slot": sl.name, "kind": "stop", "alert": -1, "stop": s, "why": why, "window": (a, b),
                    "target": None if s is None else W.target_ticks(sl.w, s)})
        trig = sl.trigger(a, b)
        ctx = _context(trig, cal, hist, i, news_windows)
        src = Windowed(trig, a, b)
        offers = src.offers(hist, i, ctx)
        kept, refused = T.admit(offers, ctx)
        ref = {id(o): r for o, r in refused}
        side = sl.side_of(trig)
        for o in offers:
            lvl = float(o.level)
            out.append({"slot": sl.name, "kind": "offer", "alert": int(o.alert), "decision": int(o.decision),
                        "sub": int(o.sub), "live": int(o.live), "entry": o.entry,
                        "level": None if math.isnan(lvl) else lvl, "role": int(o.role), "expires": o.expires,
                        "group": o.group, "tag": o.tag, "void": o.void, "refused": ref.get(id(o), ""),
                        "segments": tuple(T.segments(o, ctx)) if id(o) not in ref else (),
                        "side": int(side(o)) if not o.void else 0,
                        "sigma": CS.alert_sigma_cross_session(closes, i, int(o.alert), tick=tick)})
    return out


__all__ = ["TASK", "FIRM", "LEVER_ROUTE", "ROUTE", "LIBRARY", "FIRM_PATH", "DROPPED", "SLOT_KEYS", "SIDED",
           "RL3_PARAMS", "T7_MAPPED", "T8_EVALUATION", "STAND_ASIDE", "AUX_ADDED", "RouteRefused", "Windowed",
           "p14_alerts", "SlotRoute", "Route", "route", "day_ranges", "trailing", "stop_on", "stops", "RouteTrades",
           "rr_grid", "build", "facts", "decisions"]
