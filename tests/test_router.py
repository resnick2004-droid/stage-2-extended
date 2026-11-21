"""Q-169 (4, 2, 5): the mix router (`extended/router.py`; lever table A15, A16) and the calendar's day contexts per
component (`components.calendar_contexts`), on synthetic data only -- never a real bar.

What is held:
* **alternation** (E-221 O-4: different accounts take different trades at different moments): every trade goes to one
  account, never copied; under `longest_waiting` (the base, Stage 2 D-429) and `round_robin` a firm's consecutive
  trades go to different accounts; the two differ when an account joins; `by_component` keeps a component's trades in
  the pool the router deals it (A16's assignment, `lever_space.deal_pools`, in opening order);
* **refusals**: a rotation outside the declared values, hand-built pools, `by_component` without the `Design` or with
  a caller's component order that is not the design's window order (m5), a trade of a component not in the design, a
  firm with no account, a firm whose own A15 / A16 is to declare (MFFU, Lucid; n4), a second route call for one date
  (n5); opposite positions across accounts or firms through `UserBook` as conduct tier 1 (with m-1's tie positions),
  the same side at once as an undefined overlap -- the cross-firm cases with MFFU's A15 **simulated declared** (a test
  stand-in for a per-firm declaration that does not exist yet; without it MFFU is refused);
* **the names NY takes** (m1): a window crossing noon New York names `ny`, the whole session; `ny_am` and `ny_pm` are
  strict at T2b's split;
* **shift-invariance**: each routed trade's account is unchanged when the bars from its moment on are replaced or
  deleted (the router reads no bar; it reads the schedule's earlier exits);
* **the calendar per component**: a design's components each get their own context (what each source reads), the
  day-wide one beside, and a calendar-void day schedules nothing; the session windows are read through the one
  function `components.session_windows_of`, repointed by Wave 3.4 to the per-date windows (E-231 (3)).

Seeds fixed for this file (the test's own, used nowhere else): 20261527 (the synthetic series), 20261528 (the coin
unit's role seed), 20261529 (the shift test's replacement walks, each cut a child `SeedSequence(20261529,
spawn_key=(day, cut))`).
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pytest

from extended import components as C
from extended import day_calendar as DC
from extended import router as R
from extended import synthetic_bars as sb
from extended import triggers as T
from extended import walker as W

SEED_SERIES, SEED_COIN, SEED_SHIFT = 20261527, 20261528, 20261529
P = 13000.0
TK = T.TICK
UNIT = T.CoinUnit(SEED_COIN, 0, 0, 0, 0)


@pytest.fixture(scope="module")
def hist() -> T.History:
    return T.History.from_bars(sb.generate(sb.Spec(date(2021, 3, 1), date(2021, 3, 19), seed=SEED_SERIES)))


def flat_day(price: float = P) -> list[np.ndarray]:
    a = np.full(1441, price)
    a[0] = np.nan
    return [a.copy(), a.copy(), a.copy(), a.copy()]


def set_bar(day, stamped, o, h, lo, c):
    j = int(stamped) + 1
    day[0][j], day[1][j], day[2][j], day[3][j] = o, h, lo, c


def one_day(day, when="2021-03-03"):
    return T.History.from_arrays([when], ["NQH1"], *[x[None, :] for x in day])


def quick_day(marks) -> T.History:
    """A day on which every mark's trade stops out within three minutes, whichever its side: a wide bar two minutes
    after each mark."""
    day = flat_day()
    for m in marks:
        set_bar(day, m + 2, P, P + 50 * TK, P - 50 * TK, P)
    return one_day(day)


def marks_design(firm, name, first, last, marks, session="ny_am"):
    return C.Design(firm, (C.Component(name, session, first, last, T.P16Marks(tuple(marks)), 40, 1.0),))


@pytest.fixture
def mffu_routing_declared(monkeypatch):
    """A test stand-in: MFFU's A15 treated as declared, so the cross-firm book (tier 1) can be reached through the
    router. No such declaration exists; without this fixture `Routing(firm="mffu")` is refused (n4)."""
    real = R.LS.require_declared

    def fake(firm, rows):
        if firm != "mffu":
            real(firm, rows)
    monkeypatch.setattr(R.LS, "require_declared", fake)
    return {f: R.Routing(firm=f) for f in ("topstep", "mffu")}


# ------------------------------------------------------------------------------------------------ alternation


def test_accounts_alternate_under_longest_waiting_and_round_robin():
    """Catches: every trade to the first account, one trade copied to several accounts, a rotation ignoring its
    state between trades."""
    marks = (960, 980, 1000, 1020, 1040, 1060)
    h = quick_day(marks)
    d = marks_design("topstep", "m", 960, 1100, marks, session="ny")          # crosses noon: the whole NY session
    for rot in ("longest_waiting", "round_robin"):
        day = C.schedule_day(d, h, 0, T.DayContext(0, h.days[0]), UNIT)
        assert len(day.trades) == 6
        routed = R.Router(R.Routing(rot, firm="topstep")).route([day], {"topstep": ("a", "b", "c")}, date=day.date)
        assert [r.account for r in routed] == ["a", "b", "c", "a", "b", "c"]
        assert len({(r.trade.fill_slot, r.account) for r in routed}) == len(routed) == len(day.trades)


def test_longest_waiting_and_round_robin_differ_when_an_account_joins():
    """An account joining on the second day: longest-waiting gives it the next trade (it has waited longest), round
    robin keeps its cycle. Catches: the two rules the same code path; a new account never used."""
    marks = (960, 980, 1000)
    h = quick_day(marks)
    d = marks_design("topstep", "m", 960, 1100, marks, session="ny")
    got = {}
    for rot in ("longest_waiting", "round_robin"):
        r = R.Router(R.Routing(rot, firm="topstep"))
        day0 = C.schedule_day(d, h, 0, T.DayContext(0, h.days[0]), UNIT)
        first = [x.account for x in r.route([day0], {"topstep": ("a", "b")}, date=day0.date)]
        h1 = T.History.from_arrays(["2021-03-04"], ["NQH1"], h.o, h.h, h.l, h.c)
        day1 = C.schedule_day(d, h1, 0, T.DayContext(1, "2021-03-04"), UNIT)
        got[rot] = first + [x.account for x in r.route([day1], {"topstep": ("a", "b", "c")}, date=day1.date)]
    assert got["longest_waiting"] == ["a", "b", "a", "c", "b", "a"]
    assert got["round_robin"] == ["a", "b", "a", "b", "c", "a"]


def test_by_component_keeps_each_components_trades_in_its_dealt_pool():
    """A16's assignment: the router deals the pools itself (`deal_pools` over the components in window order and the
    accounts in opening order: a, b, c all opened today, ties by id, so am takes a and c, pm takes b), longest-waiting
    inside each pool; the caller's account order changes no pool. Catches: a pool ignored, a pool leaking to other
    accounts, the deal following the caller's order."""
    am, pm = (960, 980, 1000), (1100, 1120, 1140)
    h = quick_day(am + pm)
    d = C.Design("topstep", (C.Component("am", "ny_am", 960, 1050, T.P16Marks(am), 40, 1.0),
                             C.Component("pm", "ny_pm", 1080, 1200, T.P16Marks(pm), 40, 1.0)))
    day = C.schedule_day(d, h, 0, T.DayContext(0, h.days[0]), UNIT)
    by = R.Routing("by_component", design=d, firm="topstep")
    assert by.components == ("am", "pm") == R.window_order(d)                  # the design's window order (m5)
    routed = R.Router(by).route([day], {"topstep": ("a", "b", "c")}, date=day.date)
    assert [(r.trade.component, r.account) for r in routed] == [("am", "a"), ("am", "c"), ("am", "a")] + \
        [("pm", "b")] * 3
    rev = R.Router(R.Routing("by_component", ("am", "pm"), design=d, firm="topstep")).route(
        [day], {"topstep": ("c", "b", "a")}, date=day.date)
    assert {r.account for r in rev if r.trade.component == "am"} == {"a", "c"}
    assert {r.account for r in rev if r.trade.component == "pm"} == {"b"}


def test_the_opening_order_is_the_routers_not_the_callers():
    """L-m1: an account's opening index is the day the router first sees it (ties by id); an account opened later is
    dealt after the older ones whatever its id or the caller's order. Catches: a deal by the caller's order or by id."""
    xy = C.Design("topstep", (C.Component("y", "ny_pm", 1100, 1200, T.P16Marks((1100,)), 40, 1.0),
                              C.Component("x", "ny_am", 960, 1000, T.P16Marks((960,)), 40, 1.0)))
    r = R.Router(R.Routing("by_component", design=xy, firm="topstep"))       # x's window first: x, then y
    r.route([], {"topstep": ("c", "b")}, date="2021-03-03")                        # day 0: b and c open (ties by id)
    r.route([], {"topstep": ("a", "c", "b")}, date="2021-03-04")                   # day 1: a opens
    assert r.opened == {("topstep", "b"): 0, ("topstep", "c"): 0, ("topstep", "a"): 1}
    assert r.dealt_pools("topstep", ("a", "c", "b")) == {"x": ("b", "a"), "y": ("c",)}
    assert r.dealt_pools("topstep", ("b", "a", "c")) == {"x": ("b", "a"), "y": ("c",)}
    with pytest.raises(R.RoutingRefused):
        r.dealt_pools("topstep", ("a", "z"))                                       # z never passed: no opening index


# ------------------------------------------------------------------------------------------------ refusals


def test_router_refusals():
    ts = {"firm": "topstep"}
    xd = marks_design("topstep", "x", 960, 1000, (960,))
    with pytest.raises(R.RoutingRefused):
        R.Routing("random", **ts)
    with pytest.raises(R.RoutingRefused):
        R.Routing("longest_waiting", ("am",), **ts)                           # components are by_component's only
    with pytest.raises(R.RoutingRefused):
        R.Routing("longest_waiting", design=xd, **ts)                         # and so is a design
    with pytest.raises(R.RoutingRefused):
        R.Routing("by_component", **ts)                                       # would route as longest_waiting (L-M2)
    with pytest.raises(R.RoutingRefused):
        R.Routing("by_component", ("x",), **ts)                               # names without the Design (m5)
    with pytest.raises(R.RoutingRefused):
        R.Routing("by_component", {"am": ("a",)}, design=xd, **ts)            # hand-built pools (L-M2)
    with pytest.raises(R.RoutingRefused):
        R.Routing("by_component", ("x", "x"), design=xd, **ts)
    with pytest.raises(R.RoutingRefused):
        R.Routing("by_component", design=marks_design("mffu", "x", 960, 1000, (960,)), **ts)   # another firm's
    with pytest.raises(TypeError):
        R.Routing()                                                           # a routing names its firm (n4)
    h = quick_day((960,))
    day = C.schedule_day(marks_design("topstep", "m", 960, 1000, (960,)), h, 0, T.DayContext(0, h.days[0]), UNIT)
    with pytest.raises(R.RoutingRefused):                                    # m is not one of the design's components
        R.Router(R.Routing("by_component", design=xd, **ts)).route([day], {"topstep": ("a", "b")}, date=day.date)
    with pytest.raises(R.RoutingRefused):
        R.Router(R.Routing(**ts)).route([day], {"topstep": ()}, date=day.date)
    with pytest.raises(R.RoutingRefused):
        R.Router(R.Routing(**ts)).route([day], {"mffu": ("m1",)}, date=day.date)  # no routing, no account at the firm
    with pytest.raises(R.RoutingRefused):
        R.Router(R.Routing(**ts)).route([day], {"topstep": ("a",)}, date="2021-03-04")   # a schedule of another date
    with pytest.raises(TypeError):
        R.Router(R.Routing(**ts)).route([day], {"topstep": ("a",)})                       # route names its date
    assert R.ROTATIONS == ("longest_waiting", "round_robin", "by_component")


def test_by_component_takes_the_designs_window_order_never_the_callers():
    """m5: the components' order is the Design's (windows' first slots, ties by name), so the first-opened account
    goes to the earliest window whatever order a caller names. Catches: a deal over a caller's order."""
    d = C.Design("topstep", (C.Component("pm", "ny_pm", 1080, 1200, T.P16Marks((1100,)), 40, 1.0),
                             C.Component("am", "ny_am", 960, 1050, T.P16Marks((960,)), 40, 1.0)))
    assert R.window_order(d) == ("am", "pm")
    assert R.Routing("by_component", design=d, firm="topstep").components == ("am", "pm")
    assert R.Routing("by_component", ("am", "pm"), design=d, firm="topstep").components == ("am", "pm")
    with pytest.raises(R.RoutingRefused, match="window order"):
        R.Routing("by_component", ("pm", "am"), design=d, firm="topstep")
    r = R.Router(R.Routing("by_component", design=d, firm="topstep"))
    r.route([], {"topstep": ("a1", "a2")}, date="2021-03-03")
    assert r.dealt_pools("topstep", ("a2", "a1")) == {"am": ("a1",), "pm": ("a2",)}


@pytest.mark.parametrize("firm", ["mffu", "lucid"])
def test_a_firm_whose_rows_are_to_declare_is_refused(firm):
    """n4: MFFU's and Lucid's A15, A16, A17 and T2b are to declare for those firms (Q-181c): no Routing, no dealt pool,
    no state rule and no NY boundary is served for them -- Topstep's declared values are never carried over -- and an
    unknown firm is refused too."""
    d = marks_design(firm, "x", 960, 1000, (960,))
    for rot in R.ROTATIONS:
        with pytest.raises(R.RoutingRefused, match="to declare for this firm"):
            R.Routing(rot, design=d if rot == "by_component" else None, firm=firm)
    with pytest.raises(R.LS.NotDeclared):
        R.LS.deal_pools(("x",), ("a",), firm=firm)
    with pytest.raises(R.LS.NotDeclared):
        R.LS.state_risk("none", 100.0, firm=firm, room=1.0, start_room=1.0, to_goal=1.0, stop_ticks=1,
                        target_ticks=1, tick_value=1.0)
    with pytest.raises(R.LS.NotDeclared):
        R.LS.check_ny_boundary(int(R.LS.bounds("T2b").values[0]), firm=firm)
    for bad in ("ts", "", None, "Topstep"):
        with pytest.raises(R.RoutingRefused):
            R.Routing(firm=bad)
        with pytest.raises(R.LS.LeverRefused):
            R.LS.deal_pools(("x",), ("a",), firm=bad)
    assert R.LS.deal_pools(("x",), ("a",), firm="topstep") == {"x": ("a",)}


def test_one_route_call_per_date():
    """n5: the opening index counts dates, so a date is routed by one call: a second call for it is refused (with the
    accounts first seen in the second call it would otherwise rank them after the first call's)."""
    h = quick_day((960,))
    day = C.schedule_day(marks_design("topstep", "m", 960, 1000, (960,)), h, 0, T.DayContext(0, h.days[0]), UNIT)
    r = R.Router(R.Routing(firm="topstep"))
    r.route([day], {"topstep": ("a",)}, date=day.date)
    for again in (day.date, date.fromisoformat(day.date)):
        with pytest.raises(R.RoutingRefused, match="already routed"):
            r.route([], {"topstep": ("a", "b")}, date=again)
    assert r.routed == [day.date] and ("topstep", "b") not in r.opened
    r.route([], {"topstep": ("a", "b")}, date="2021-03-04")
    assert r.opened == {("topstep", "a"): 0, ("topstep", "b"): 1}


def test_opposite_positions_across_firms_are_tier_one_and_the_same_side_an_overlap(mffu_routing_declared):
    """Two firms trading at overlapping moments on a flat day (both held to the flatten): tier 1 exactly when the coin
    gives the two moments opposite sides, else an undefined overlap. Catches: the router not adding positions to the
    user's book, the opposite-side check missing."""
    h = one_day(flat_day())
    a, b = marks_design("topstep", "a", 960, 1005, (1000,)), marks_design("mffu", "b", 1006, 1100, (1010,), session="ny")
    days = [C.schedule_day(x, h, 0, T.DayContext(0, h.days[0]), UNIT) for x in (a, b)]
    s1, s2 = days[0].trades[0].side, days[1].trades[0].side
    with pytest.raises(C.TierOneRefused if s1 != s2 else C.OverlapRefused):
        R.Router(mffu_routing_declared).route(days, {"topstep": ("a1", "a2"), "mffu": ("m1",)}, date=h.days[0])


def test_a_tie_reaches_the_router_as_either_ticket(mffu_routing_declared):
    """m-1 through the router: a same-bar tie on one firm and another firm's position inside its later exit are
    refused as tier 1, whatever account each lands on. Catches: the router booking the tie's booked side only."""
    prev = flat_day(13050.0)
    set_bar(prev, W.slot(9, 0), 13050.0, 13150.0, 12950.0, 13050.0)
    tie = flat_day(13050.0)
    set_bar(tie, 1020, 13050.0, 13150.0 + 2 * TK, 12950.0 - 2 * TK, 13050.0)
    for s in range(1030, 1439):
        set_bar(tie, s, 12850.0, 12850.0, 12850.0, 12850.0)
    set_bar(tie, 1100, 12850.0, 12850.0, 12849.0, 12850.0)
    h = T.History.from_arrays(["2021-03-02", "2021-03-03"], ["NQH1", "NQH1"],
                              *[np.stack([x, y]) for x, y in zip(prev, tie)])
    ctx = T.DayContext(1, "2021-03-03")
    ts = C.Design("topstep", (C.Component("rl3", "ny_am", 960, 1015, T.RL3Tickets("pd", T.RL3_CUTOFFS[2]), 400, 3.0),))
    mf = marks_design("mffu", "m", 1016, 1300, (1040,), session="ny")
    days = [C.schedule_day(x, h, 1, ctx, UNIT) for x in (ts, mf)]
    tie, other = days[0].trades[0], days[1].trades[0]
    assert tie.oco_tie and tie.fill_slot < other.fill_slot < tie.busy_until
    opposed = any(s != other.side for s in tie.tie_sides)                     # either ticket's side counts
    with pytest.raises(C.TierOneRefused if opposed else C.OverlapRefused):
        R.Router(mffu_routing_declared).route(days, {"topstep": ("a1",), "mffu": ("m1",)}, date=ctx.date)


# ------------------------------------------------------------------------------------------------ shift-invariance


def shifted(h: T.History, i: int, t: int, mode: str, seed) -> T.History:
    arrs = [x.copy() for x in (h.o, h.h, h.l, h.c)]
    mask = np.zeros(arrs[0].shape, dtype=bool)
    mask[i, t + 1:] = True
    mask[i + 1:, 1:] = True
    mask &= ~np.isnan(arrs[0])
    if mode == "delete":
        mask[i, W.FLAT_ENTRY:] = False                                        # the day still ends where it did
        for a in arrs:
            a[mask] = np.nan
    else:
        rng = np.random.default_rng(seed)
        k = int(mask.sum())
        walk = 13000.0 + TK * (rng.integers(-1600, 1600) + np.cumsum(rng.integers(-12, 13, k)))
        wid = TK * rng.integers(0, 30, (k, 2))
        o = walk + TK * rng.integers(-8, 9, k)
        arrs[0][mask], arrs[3][mask] = o, walk
        arrs[1][mask] = np.maximum(o, walk) + wid[:, 0]
        arrs[2][mask] = np.minimum(o, walk) - wid[:, 1]
    return T.History(h.days, h.contract, *arrs)


def routed_accounts(design, h, i, ctx, rot) -> dict:
    """{trade key: (its fill minute, its account)}."""
    day = C.schedule_day(design, h, i, ctx, UNIT)
    return {(r.trade.source, r.trade.decision, r.trade.tag): (r.trade.fill_slot, r.account)
            for r in R.Router(R.Routing(rot, firm="topstep")).route([day], {"topstep": ("a", "b", "c")},
                                                                     date=day.date)}


@pytest.mark.parametrize("rot", ["longest_waiting", "round_robin"])
def test_routing_is_shift_invariant(hist, rot):
    """Every trade filled before a cut (on a bar stamped before it) is routed to the same account when the bars from
    the cut on are replaced or deleted. A fill on the bar stamped at the cut is the walker's execution at that moment,
    not a routing decision, and is not compared. Catches: an account chosen from a trade's own outcome or a later
    trade's (the router may read only earlier busy times)."""
    design = C.Design("topstep", (
        C.Component("coin", "ny_am", 960, 1075, T.CoinMarks(955, 1070, latency=5), 40, 1.0),
        C.Component("brk", "ny_pm", 1080, 1260, T.P14Breakout(latency=3), 40, 1.0),
    ))
    compared = 0
    for i in range(1, 6):
        ctx = T.DayContext(i, hist.days[i])
        base = routed_accounts(design, hist, i, ctx, rot)
        for c, t in enumerate(sorted({f + 1 for f, _ in base.values()})):
            for mode in ("replace", "delete"):
                seed = np.random.SeedSequence(SEED_SHIFT, spawn_key=(i, c))
                got = routed_accounts(design, shifted(hist, i, t, mode, seed), i, ctx, rot)
                for k, v in base.items():
                    if v[0] < t:
                        assert got.get(k) == v, (hist.days[i], mode, t, k, v, got.get(k))
                        compared += 1
    assert compared > 100


# ------------------------------------------------------------------------------------------------ the calendar per component


def test_calendar_contexts_per_component_and_a_void_day_schedules_nothing(hist):
    """Q-169 (2) at the scheduler: each component is admitted under its own source's context; on a day the calendar
    voids for overnight readers only (H2's VOID), an overnight-reading component offers nothing while a day-only one
    still trades; a day-wide void schedules nothing at all. Catches: one context for every component, the calendar
    not consulted."""
    days = list(hist.days)
    h2void, defect = days[4], days[6]
    ds = [date.fromisoformat(d) for d in days]
    fl = {d: {"missing_after_reopen": "0", "verdict": "OK", "void": "", "special": ""} for d in ds}
    fl[date.fromisoformat(h2void)] = {"missing_after_reopen": "0", "verdict": "VOID", "void": "long_gap", "special": ""}
    cal = DC.Sources(ds, {date.fromisoformat(defect): {"date": defect, "kind": "data_defect_candidate", "close_ct": "",
                                                       "source": "t"}},
                     frozenset(), frozenset(), {d: "15:59" for d in ds}, frozenset(), frozenset(), fl)
    design = C.Design("topstep", (C.Component("rl3", "ny_am", 960, 960, T.RL3Tickets("rn100", T.RL3_CUTOFFS[0]), 100, 1.0),
                             C.Component("coin", "ny", 1025, 1200, T.CoinMarks(1020, 1195), 40, 1.0)))
    for d, rl3_void, coin_void in ((h2void, True, False), (defect, True, True)):
        i = days.index(d)
        base, per = C.calendar_contexts(design, cal, hist, i)
        assert base.void == coin_void and per["rl3"].void == rl3_void and per["coin"].void == coin_void
        s = C.schedule_day(design, hist, i, base, UNIT, contexts=per)
        assert not [t for t in s.trades if t.component == "rl3"]
        rl3_refused = [r for o, r in s.refused if o.source == "rl3" and not o.void]   # by its own context, not run
        assert rl3_refused and set(rl3_refused) == {"calendar"}
        assert not [o for o, _ in s.unfilled if o.source == "rl3"]
        assert bool([t for t in s.trades if t.component == "coin"]) == (not coin_void)
    # one function, repointed by Wave 3.4 to the per-date windows (E-231 (3)): asia moves with US daylight time
    winter, summer = date(2021, 1, 15), date(2021, 7, 15)
    assert C.session_windows_of(winter) == C.LS.session_windows(winter)
    assert C.session_windows_of(winter)["asia"][0] != C.session_windows_of(summer)["asia"][0]
    assert C.session_windows_of(winter)["asia"][0] == DC.anchored_starts(winter)["asia"]
