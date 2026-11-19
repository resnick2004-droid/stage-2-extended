"""Q-169 (4, 2, 5): the mix router (`extended/router.py`; lever table A15, A16) and the calendar's day contexts per
component (`components.calendar_contexts`), on synthetic data only -- never a real bar.

What is held:
* **alternation** (E-221 O-4: different accounts take different trades at different moments): every trade goes to one
  account, never copied; under `longest_waiting` (the base, Stage 2 D-429) and `round_robin` a firm's consecutive
  trades go to different accounts; the two differ when an account joins; `by_component` keeps a component's trades in
  its declared pool (A16's assignment);
* **refusals**: a rotation outside the declared values, a pool naming an account the firm does not hold, a firm with no
  account; opposite positions across accounts or firms through `UserBook` as conduct tier 1 (with m-1's tie positions),
  the same side at once as an undefined overlap;
* **shift-invariance**: each routed trade's account is unchanged when the bars from its moment on are replaced or
  deleted (the router reads no bar; it reads the schedule's earlier exits);
* **the calendar per component**: a design's components each get their own context (what each source reads), the
  day-wide one beside, and a calendar-void day schedules nothing; the session windows are read through the one
  function `components.session_windows_of` (to repoint to per-date windows when Wave 3.4's change lands).

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


# ------------------------------------------------------------------------------------------------ alternation


def test_accounts_alternate_under_longest_waiting_and_round_robin():
    """Catches: every trade to the first account, one trade copied to several accounts, a rotation ignoring its
    state between trades."""
    marks = (960, 980, 1000, 1020, 1040, 1060)
    h = quick_day(marks)
    d = marks_design("ts", "m", 960, 1100, marks)
    for rot in ("longest_waiting", "round_robin"):
        day = C.schedule_day(d, h, 0, T.DayContext(0, h.days[0]), UNIT)
        assert len(day.trades) == 6
        routed = R.Router(R.Routing(rot)).route([day], {"ts": ("a", "b", "c")})
        assert [r.account for r in routed] == ["a", "b", "c", "a", "b", "c"]
        assert len({(r.trade.fill_slot, r.account) for r in routed}) == len(routed) == len(day.trades)


def test_longest_waiting_and_round_robin_differ_when_an_account_joins():
    """An account joining on the second day: longest-waiting gives it the next trade (it has waited longest), round
    robin keeps its cycle. Catches: the two rules the same code path; a new account never used."""
    marks = (960, 980, 1000)
    h = quick_day(marks)
    d = marks_design("ts", "m", 960, 1100, marks)
    got = {}
    for rot in ("longest_waiting", "round_robin"):
        r = R.Router(R.Routing(rot))
        day0 = C.schedule_day(d, h, 0, T.DayContext(0, h.days[0]), UNIT)
        first = [x.account for x in r.route([day0], {"ts": ("a", "b")})]
        h1 = T.History.from_arrays(["2021-03-04"], ["NQH1"], h.o, h.h, h.l, h.c)
        day1 = C.schedule_day(d, h1, 0, T.DayContext(1, "2021-03-04"), UNIT)
        got[rot] = first + [x.account for x in r.route([day1], {"ts": ("a", "b", "c")})]
    assert got["longest_waiting"] == ["a", "b", "a", "c", "b", "a"]
    assert got["round_robin"] == ["a", "b", "a", "b", "c", "a"]


def test_by_component_keeps_each_components_trades_in_its_pool():
    """A16's assignment: a component's trades go only to its declared pool, longest-waiting inside it; a component
    without a pool uses every account of its firm. Catches: a pool ignored, a pool leaking to other accounts."""
    am, pm = (960, 980, 1000), (1100, 1120, 1140)
    h = quick_day(am + pm)
    d = C.Design("ts", (C.Component("am", "ny_am", 960, 1050, T.P16Marks(am), 40, 1.0),
                        C.Component("pm", "ny_pm", 1051, 1200, T.P16Marks(pm), 40, 1.0)))
    day = C.schedule_day(d, h, 0, T.DayContext(0, h.days[0]), UNIT)
    routed = R.Router(R.Routing("by_component", {"am": ("a",), "pm": ("b", "c")})).route([day], {"ts": ("a", "b", "c")})
    assert [(r.trade.component, r.account) for r in routed] == [("am", "a")] * 3 + [("pm", "b"), ("pm", "c"),
                                                                                     ("pm", "b")]
    free = R.Router(R.Routing("by_component", {"am": ("a",)})).route([day], {"ts": ("a", "b", "c")})
    assert [r.account for r in free][3:] == ["b", "c", "a"]                    # pm: every account, longest-waiting


# ------------------------------------------------------------------------------------------------ refusals


def test_router_refusals():
    with pytest.raises(R.RoutingRefused):
        R.Routing("random")
    with pytest.raises(R.RoutingRefused):
        R.Routing("longest_waiting", {"am": ("a",)})                          # a pool is by_component's only
    h = quick_day((960,))
    day = C.schedule_day(marks_design("ts", "m", 960, 1000, (960,)), h, 0, T.DayContext(0, h.days[0]), UNIT)
    with pytest.raises(R.RoutingRefused):
        R.Router(R.Routing("by_component", {"m": ("z",)})).route([day], {"ts": ("a", "b")})
    with pytest.raises(R.RoutingRefused):
        R.Router(R.Routing()).route([day], {"ts": ()})
    with pytest.raises(R.RoutingRefused):
        R.Router(R.Routing()).route([day], {"mffu": ("m1",)})                  # no account at the trade's firm
    assert R.ROTATIONS == ("longest_waiting", "round_robin", "by_component")


def test_opposite_positions_across_firms_are_tier_one_and_the_same_side_an_overlap():
    """Two firms trading at overlapping moments on a flat day (both held to the flatten): tier 1 exactly when the coin
    gives the two moments opposite sides, else an undefined overlap. Catches: the router not adding positions to the
    user's book, the opposite-side check missing."""
    h = one_day(flat_day())
    a, b = marks_design("ts", "a", 960, 1005, (1000,)), marks_design("mffu", "b", 1006, 1100, (1010,))
    days = [C.schedule_day(x, h, 0, T.DayContext(0, h.days[0]), UNIT) for x in (a, b)]
    s1, s2 = days[0].trades[0].side, days[1].trades[0].side
    with pytest.raises(C.TierOneRefused if s1 != s2 else C.OverlapRefused):
        R.Router(R.Routing()).route(days, {"ts": ("a1", "a2"), "mffu": ("m1",)})


def test_a_tie_reaches_the_router_as_either_ticket():
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
    ts = C.Design("ts", (C.Component("rl3", "ny_am", 960, 1015, T.RL3Tickets("pd", T.RL3_CUTOFFS[2]), 400, 3.0),))
    mf = marks_design("mffu", "m", 1016, 1300, (1040,))
    days = [C.schedule_day(x, h, 1, ctx, UNIT) for x in (ts, mf)]
    tie, other = days[0].trades[0], days[1].trades[0]
    assert tie.oco_tie and tie.fill_slot < other.fill_slot < tie.busy_until
    opposed = any(s != other.side for s in tie.tie_sides)                     # either ticket's side counts
    with pytest.raises(C.TierOneRefused if opposed else C.OverlapRefused):
        R.Router(R.Routing()).route(days, {"ts": ("a1",), "mffu": ("m1",)})


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
            for r in R.Router(R.Routing(rot)).route([day], {"ts": ("a", "b", "c")})}


@pytest.mark.parametrize("rot", ["longest_waiting", "round_robin"])
def test_routing_is_shift_invariant(hist, rot):
    """Every trade filled before a cut (on a bar stamped before it) is routed to the same account when the bars from
    the cut on are replaced or deleted. A fill on the bar stamped at the cut is the walker's execution at that moment,
    not a routing decision, and is not compared. Catches: an account chosen from a trade's own outcome or a later
    trade's (the router may read only earlier busy times)."""
    design = C.Design("ts", (
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
    design = C.Design("ts", (C.Component("rl3", "ny_am", 960, 960, T.RL3Tickets("rn100", T.RL3_CUTOFFS[0]), 100, 1.0),
                             C.Component("coin", "ny_am", 1025, 1200, T.CoinMarks(1020, 1195), 40, 1.0)))
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
    assert C.session_windows_of() == C.session_windows_of(date(2021, 3, 15))   # one function, date-free until 3.4
