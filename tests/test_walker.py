"""Q-10 (F-01 section 7 item 3, the walker's part): the bracket walker's fill and walk rules on synthetic bars.

Every bar here is built by hand on Stage 2's trading-day clock (index j = the bar's END minute after 17:00 CT; the bar
stamped with OPEN time hh:mm is index slot(hh, mm) + 1). Prices are NQ's, on the 0.25 tick grid. The stop is 100 ticks
(25 points) unless a test says otherwise, so 1R's target is 100 ticks and needs a trade 101 ticks through.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extended import walker as W  # noqa: E402

TICK = 0.25
BASE = 20000.0
LIVE = W.slot(8, 30)                     # 930: the order works from 08:30 CT (bars 931 on)
F01 = W.DECLARED_F01
S2 = W.STAGE2


def mk(base: float = BASE, bars: dict[int, tuple[float, float, float, float]] | None = None, *,
       missing: tuple[int, ...] = ()) -> tuple[np.ndarray, ...]:
    """A full day (bars 1..1330 present), flat at `base`; each given bar (o, h, l, c) set, and every bar after it flat
    at its close until the next given bar; `missing` bars removed (NaN)."""
    n = W.C_FLAT + 1
    o, h, l, c = (np.full(n, np.nan) for _ in range(4))
    price = base
    spec = dict(sorted((bars or {}).items()))
    for j in range(1, n):
        if j in spec:
            o[j], h[j], l[j], c[j] = spec[j]
            price = spec[j][3]
        else:
            o[j] = h[j] = l[j] = c[j] = price
    for j in missing:
        o[j] = h[j] = l[j] = c[j] = np.nan
    return o, h, l, c


def buy_stop(p, live=LIVE, cutoff=None):
    return W.Order(W.STOP_ENTRY, +1, live, p, cutoff)


def sell_stop(p, live=LIVE, cutoff=None):
    return W.Order(W.STOP_ENTRY, -1, live, p, cutoff)


def buy_limit(p, live=LIVE, cutoff=None):
    return W.Order(W.LIMIT_ENTRY, +1, live, p, cutoff)


def sell_limit(p, live=LIVE, cutoff=None):
    return W.Order(W.LIMIT_ENTRY, -1, live, p, cutoff)


def one(order, arr, stop=100, rrs=(1.0,), rules=F01, costs=None):
    return W.trade(order, *arr, stop, rrs, rules=rules, costs=costs)


# ------------------------------------------------------------------------------------------------ the clock


def test_the_clock_is_stage2s():
    assert W.slot(17, 0) == 0 and W.slot(8, 30) == 930 and W.slot(15, 10) == 1330 and W.slot(16, 59) == 1439
    assert W.bar_of(8, 25) == 926            # the 08:25 bar closes at 08:26
    assert W.bar_of(8, 30) == 931
    assert W.bar_of(15, 9) == W.C_FLAT       # the bar stamped 15:09 is the bar ending 15:10
    assert W.FLAT_ENTRY == 1328 and W.FLATTEN_BARS == (1328, 1329, 1330)
    assert W.target_ticks(1.5, 150) == 225 and W.target_ticks(0.25, 150) == 37 and W.target_ticks(3, 100) == 300


# ------------------------------------------------------------------------------------------------ market entries


def test_a_market_order_fills_at_the_open_of_the_first_bar_opening_at_or_after_live():
    arr = mk(bars={931: (20001.0, 20002.0, 20000.0, 20001.0)})
    f = W.fill_order(W.Order(W.MARKET, +1, LIVE), *arr, rules=F01)
    assert (f.status, f.bar, f.price, f.resting) == ("filled", 931, 20001.0, False)
    arr = mk(bars={932: (20003.0, 20004.0, 20002.0, 20003.0)}, missing=(931,))
    f = W.fill_order(W.Order(W.MARKET, -1, LIVE), *arr, rules=F01)
    assert (f.status, f.bar, f.price) == ("filled", 932, 20003.0)


def test_the_market_fill_bars_helper_is_the_single_order_rule():
    arr = mk(missing=(931, 932, 1000))
    lives = np.array([0, 929, 930, 931, 999, 1300, 1327], dtype=int)
    got = W.market_fill_bars(arr[0], lives, rules=S2)
    want = [W.fill_order(W.Order(W.MARKET, 1, int(t)), *arr, rules=S2).bar for t in lives]
    assert got.tolist() == want and want[2] == 933 and want[-1] == W.NONE      # 1328 is the walk's end: no entry


# ------------------------------------------------------------------------------------------------ stop entries


def test_a_buy_stop_fills_on_a_touch_at_its_price_plus_a_tick():
    arr = mk(bars={940: (20005.0, 20010.0, 20004.0, 20008.0)})
    f = W.fill_order(buy_stop(20010.0), *arr, rules=F01)
    assert (f.status, f.bar, f.price, f.gap, f.resting) == ("filled", 940, 20010.25, False, True)


def test_a_stop_not_reached_is_cancelled_at_the_end():
    arr = mk(bars={940: (20005.0, 20009.75, 20004.0, 20008.0)})
    f = W.fill_order(buy_stop(20010.0), *arr, rules=F01)
    assert (f.status, f.reason, f.bar) == ("cancelled", "end", W.NONE)
    assert math.isnan(f.price)


def test_a_stop_gapped_through_fills_at_the_open_plus_a_tick():
    arr = mk(bars={939: (20005.0, 20006.0, 20004.0, 20005.0), 940: (20012.0, 20014.0, 20011.0, 20013.0)})
    f = W.fill_order(buy_stop(20010.0), *arr, rules=F01)
    assert (f.status, f.bar, f.price, f.gap) == ("filled", 940, 20012.25, True)
    arr = mk(bars={939: (19995.0, 19996.0, 19994.0, 19995.0), 940: (19985.0, 19986.0, 19984.0, 19985.0)})
    f = W.fill_order(sell_stop(19990.0), *arr, rules=F01)
    assert (f.status, f.bar, f.price, f.gap) == ("filled", 940, 19984.75, True)


def test_a_sell_stop_fills_on_a_touch_at_its_price_less_a_tick():
    arr = mk(bars={940: (19995.0, 19996.0, 19990.0, 19992.0)})
    f = W.fill_order(sell_stop(19990.0), *arr, rules=F01)
    assert (f.status, f.bar, f.price, f.gap) == ("filled", 940, 19989.75, False)


# ------------------------------------------------------------------------------------------------ limit entries


def test_a_limit_touch_is_not_a_fill_and_a_trade_through_is():
    touch_only = mk(bars={940: (20005.0, 20010.0, 20004.0, 20008.0)})
    f = W.fill_order(sell_limit(20010.0), *touch_only, rules=F01)
    assert (f.status, f.reason, f.touch_bar) == ("cancelled", "end", 940)
    through = mk(bars={940: (20005.0, 20010.0, 20004.0, 20008.0), 945: (20008.0, 20010.25, 20007.0, 20009.0)})
    f = W.fill_order(sell_limit(20010.0), *through, rules=F01)
    assert (f.status, f.bar, f.price, f.touch_bar, f.resting) == ("filled", 945, 20010.0, 940, True)
    through = mk(bars={950: (19995.0, 19996.0, 19989.75, 19992.0)})
    f = W.fill_order(buy_limit(19990.0), *through, rules=F01)
    assert (f.status, f.bar, f.price, f.touch_bar) == ("filled", 950, 19990.0, 950)


def test_a_limit_gapped_through_fills_at_its_price_never_better():
    arr = mk(bars={939: (19995.0, 19996.0, 19994.0, 19995.0), 940: (19985.0, 19986.0, 19984.0, 19985.0)})
    f = W.fill_order(buy_limit(19990.0), *arr, rules=F01)
    assert (f.status, f.bar, f.price, f.gap) == ("filled", 940, 19990.0, False)


# ------------------------------------------------------------------------------------------------ void tickets


@pytest.mark.parametrize("order, ref, void", [
    (buy_stop(20010.0), 20010.0, True), (buy_stop(20010.0), 20011.0, True), (buy_stop(20010.0), 20009.75, False),
    (sell_stop(19990.0), 19990.0, True), (sell_stop(19990.0), 19985.0, True), (sell_stop(19990.0), 19990.25, False),
    (sell_limit(20010.0), 20010.0, True), (sell_limit(20010.0), 20012.0, True), (sell_limit(20010.0), 20009.75, False),
    (buy_limit(19990.0), 19990.0, True), (buy_limit(19990.0), 19980.0, True), (buy_limit(19990.0), 19990.25, False),
])
def test_a_ticket_at_or_through_its_price_at_live_is_void(order, ref, void):
    arr = mk(bars={LIVE: (ref, ref, ref, ref), LIVE + 1: (BASE, BASE, BASE, BASE)})
    f = W.fill_order(order, *arr, rules=F01)
    assert f.reference == ref
    assert (f.status == "void") is void
    if void:
        assert f.reason == "through" and f.bar == W.NONE


def test_the_price_at_live_is_the_close_of_the_last_bar_closed_by_then():
    # the bar ending at 08:30 closes below the stop; the first live bar opens beyond it: a gap fill, not a void
    arr = mk(bars={LIVE: (20000.0, 20001.0, 19999.0, 20000.0), LIVE + 1: (20012.0, 20013.0, 20011.0, 20012.0)})
    f = W.fill_order(buy_stop(20010.0), *arr, rules=F01)
    assert (f.status, f.reference, f.bar, f.price, f.gap) == ("filled", 20000.0, LIVE + 1, 20012.25, True)
    # bars missing at 08:30: the last close before it is the price
    arr = mk(bars={925: (20011.0, 20011.0, 20011.0, 20011.0)}, missing=tuple(range(926, 931)))
    assert W.fill_order(buy_stop(20010.0), *arr, rules=F01).status == "void"


def test_no_bar_closed_by_live_is_a_void_ticket():
    arr = mk(missing=tuple(range(1, 931)))
    f = W.fill_order(buy_stop(20010.0), *arr, rules=F01)
    assert (f.status, f.reason) == ("void", "no_reference")


def test_a_bar_before_live_never_fills():
    arr = mk(bars={LIVE: (20005.0, 20020.0, 20004.0, 20005.0)})       # trades the stop before the order works
    f = W.fill_order(buy_stop(20010.0), *arr, rules=F01)
    assert (f.status, f.reason) == ("cancelled", "end")


def test_an_off_grid_price_is_refused():
    with pytest.raises(ValueError):
        W.fill_order(buy_stop(20010.1), *mk(), rules=F01)


# ------------------------------------------------------------------------------------------------ the cutoff


def test_an_unfilled_ticket_is_cancelled_at_the_cutoff():
    cut = W.slot(14, 30)                                                 # 1290: bars ending by 14:30 only
    late = mk(bars={cut + 1: (20005.0, 20010.0, 20004.0, 20008.0)})     # the bar stamped 14:30
    f = W.fill_order(buy_stop(20010.0, cutoff=cut), *late, rules=F01)
    assert (f.status, f.reason) == ("cancelled", "cutoff")
    on_time = mk(bars={cut: (20005.0, 20010.0, 20004.0, 20008.0)})      # the bar stamped 14:29, ending 14:30
    f = W.fill_order(buy_stop(20010.0, cutoff=cut), *on_time, rules=F01)
    assert (f.status, f.bar) == ("filled", cut)
    t = one(buy_stop(20010.0, cutoff=cut), late)
    assert t.rule is None and t.mirror is None


# ------------------------------------------------------------------------------------------------ one fill a ticket


def test_a_ticket_fills_once():
    arr = mk(bars={940: (20005.0, 20010.0, 20004.0, 20008.0), 950: (20008.0, 20008.0, 19990.0, 19995.0),
                   1000: (19995.0, 20012.0, 19995.0, 20011.0)})
    t = one(buy_stop(20010.0), arr)
    assert t.fill.bar == 940 and t.fill.price == 20010.25
    assert isinstance(t, W.Trade) and t.rule.kind.shape == (1,)


# ------------------------------------------------------------------------------------------------ the walk


def mkt_long(arr, rrs=(1.0,), rules=F01, stop=100):
    return one(W.Order(W.MARKET, +1, LIVE), arr, stop=stop, rrs=rrs, rules=rules)


def test_stop_first_on_a_bar_touching_both():
    arr = mk(bars={931: (20000.0, 20001.0, 19999.0, 20000.0), 950: (20000.0, 20030.0, 19970.0, 20000.0)})
    r = mkt_long(arr).rule
    assert (r.kind[0], r.exit[0], r.gross[0], r.mae[0]) == (W.STOP, 950, -100, 100)


def test_a_stop_is_reached_by_a_touch_and_a_target_needs_a_trade_through():
    arr = mk(bars={931: (20000.0, 20001.0, 19999.0, 20000.0), 950: (20000.0, 20025.0, 19999.0, 20010.0),
                   960: (20010.0, 20025.25, 20009.0, 20020.0)})
    r = mkt_long(arr).rule
    assert (r.kind[0], r.exit[0], r.gross[0]) == (W.TARGET, 960, 100)
    arr = mk(bars={931: (20000.0, 20001.0, 19999.0, 20000.0), 950: (20000.0, 20001.0, 19975.0, 19990.0)})
    r = mkt_long(arr).rule
    assert (r.kind[0], r.exit[0], r.gross[0]) == (W.STOP, 950, -100)


def test_a_market_entry_bar_is_walked_whole():
    arr = mk(bars={931: (20000.0, 20025.25, 19999.0, 20020.0)})
    r = mkt_long(arr).rule
    assert (r.kind[0], r.exit[0]) == (W.TARGET, 931)


LOW = 19990.0                            # a day based below the 19999.75 stops, so they are live (not void) at 08:30


def test_the_fill_bar_rule_target_touch_not_counted():
    # buy stop at 19999.75 fills at 20000.00 on bar 931; that bar trades 120 ticks beyond: not a target
    arr = mk(LOW, bars={931: (19995.0, 20030.0, 19994.0, 20020.0), 1000: (20020.0, 20025.25, 20019.0, 20022.0)})
    t = one(buy_stop(19999.75), arr)
    assert (t.fill.bar, t.fill.price) == (931, 20000.0)
    assert (t.rule.kind[0], t.rule.exit[0]) == (W.TARGET, 1000)


def test_the_fill_bar_rule_stop_touch_is_a_loss():
    arr = mk(LOW, bars={931: (19990.0, 20001.0, 19975.0, 19995.0)})   # fill at 20000.00, low 100 ticks below
    t = one(buy_stop(19999.75), arr)
    assert (t.rule.kind[0], t.rule.exit[0], t.rule.gross[0]) == (W.STOP, 931, -100)


def test_the_mirror_is_the_opposite_side_at_the_same_fill_with_the_same_rules():
    arr = mk(LOW, bars={931: (19990.0, 20001.0, 19974.75, 19995.0), 1000: (19995.0, 19996.0, 19974.75, 19980.0)})
    t = one(buy_stop(19999.75), arr, rrs=(1.0, 1.5))
    assert (t.rule.kind[0], t.rule.exit[0]) == (W.STOP, 931)
    m = t.mirror
    # the mirror's favourable move on the fill bar (101 ticks) is not a target; on bar 1000 it trades through again
    assert (m.kind.tolist(), m.exit.tolist(), m.gross.tolist()) == ([W.TARGET, W.FLATTEN], [1000, W.C_FLAT],
                                                                     [100, int(round((20000.0 - 19980.0) / TICK))])
    o, h, l, c = arr
    ref = W.walk(o, h, l, c, [931], [20000.0], [-1], [True], W.brackets((100,), (1.0, 1.5)), rules=F01)
    assert ref["kind"][0].tolist() == m.kind.tolist() and ref["exit"][0].tolist() == m.exit.tolist()


def test_the_1510_flatten_declared_and_stage2s():
    arr = mk(bars={931: (20000.0, 20001.0, 19999.0, 20004.0), 1330: (20004.0, 20005.0, 20003.0, 20004.5)})
    r = mkt_long(arr).rule
    assert (r.kind[0], r.exit[0], r.gross[0]) == (W.FLATTEN, W.C_FLAT, 18)        # the 15:10 bar's close
    arr = mk(bars={931: (20000.0, 20001.0, 19999.0, 20004.0), 1328: (20004.0, 20005.0, 20003.0, 20004.0),
                   1329: (20004.0, 20005.0, 20002.5, 20004.0), 1330: (20004.0, 20005.0, 20003.0, 20004.5)})
    r = mkt_long(arr, rules=S2).rule
    assert (r.kind[0], r.exit[0], r.gross[0]) == (W.FLATTEN, W.FLAT_ENTRY, 10 - 2)  # worst of 15:08-15:10 less two


def test_a_stop_after_1508_counts_in_the_declared_walk_and_not_in_stage2s():
    arr = mk(bars={931: (20000.0, 20001.0, 19999.0, 20000.0), 1329: (20000.0, 20001.0, 19975.0, 19990.0)})
    assert mkt_long(arr).rule.kind[0] == W.STOP
    r = mkt_long(arr, rules=S2).rule
    assert (r.kind[0], r.gross[0]) == (W.FLATTEN, -100 - 2)


def test_stage2s_breakeven_and_none_in_the_declared_walk():
    # entered 08:30; the 13:00 session opens 10 points in favour; a later bar touches the entry
    arr = mk(bars={931: (20000.0, 20001.0, 19999.0, 20000.0), 1201: (20010.0, 20011.0, 20009.0, 20010.0),
                   1250: (20010.0, 20010.0, 19999.0, 19999.0)})
    r = mkt_long(arr, rules=S2).rule
    assert (r.kind[0], r.exit[0], r.gross[0]) == (W.BREAKEVEN, 1250, 0)
    r = mkt_long(arr).rule
    assert (r.kind[0], r.gross[0]) == (W.FLATTEN, -4)


def test_unresolved_and_mae_at_three_r():
    arr = mk(bars={931: (20000.0, 20001.0, 19990.0, 20000.0), 1000: (20000.0, 20050.25, 19999.0, 20040.0)})
    r = mkt_long(arr, rrs=(1.0, 1.5, 3.0)).rule
    assert r.kind.tolist() == [W.TARGET, W.TARGET, W.FLATTEN]
    assert r.mae.tolist() == [40, 40, 40]


# ------------------------------------------------------------------------------------------------ costs


def test_costs_are_stage2s_arithmetic():
    k = W.Costs(fee_micro_eq=1.37, tick_value=0.5)
    kinds = np.array([W.STOP, W.TARGET, W.FLATTEN, W.BREAKEVEN])
    gross = np.array([-150, 225, 12, 0])
    got = W.net_r(gross, kinds, 150, entry_ticks=1.0, costs=k)
    exit_ticks = np.array([1.0, 0.0, 2.0, 1.0])
    cost = (1.0 * 0.5 + 1.37 + exit_ticks * 0.5) / (150 * 0.5)
    assert np.array_equal(got, gross / 150 - cost)
    assert np.array_equal(W.cost_r(kinds, 150, entry_ticks=1.0, costs=k), cost)


def test_a_resting_fill_pays_no_entry_tick_and_a_market_fill_one():
    k = W.Costs(fee_micro_eq=1.0, tick_value=0.5)
    arr = mk(bars={940: (20005.0, 20010.0, 20004.0, 20008.0), 1000: (20008.0, 20035.5, 20008.0, 20030.0)})
    t = one(buy_stop(20010.0), arr, costs=k)            # fill 20010.25, target 20035.25 traded through at 20035.50
    assert t.rule.kind[0] == W.TARGET
    assert t.rule.net_r[0] == 100 / 100 - (0.0 * 0.5 + 1.0 + 0.0 * 0.5) / (100 * 0.5)
    t = one(W.Order(W.MARKET, +1, LIVE), mk(bars={931: (20000.0, 20025.25, 19999.0, 20020.0)}), costs=k)
    assert t.rule.net_r[0] == 1.0 - (1.0 * 0.5 + 1.0 + 0.0) / (100 * 0.5)


# ------------------------------------------------------------------------------------------------ the lead's change
# (2026-11-15, the Phase 0 audit's track D: D-1 the fill-bar rule's asymmetry, D-13 the mirror's booking price):
# every fill carries its trigger price; the mirror's booking ("rule_fill" or "symmetric") and the fill bar's settlement
# ("declared" or "pair") are parameters.


def test_every_fill_carries_its_trigger_price():
    f = W.fill_order(buy_stop(20010.0), *mk(bars={940: (20005.0, 20010.0, 20004.0, 20008.0)}), rules=F01)
    assert (f.trigger, f.price) == (20010.0, 20010.25)                            # a touch: the stop's price
    gap = mk(bars={939: (20005.0, 20006.0, 20004.0, 20005.0), 940: (20012.0, 20014.0, 20011.0, 20013.0)})
    f = W.fill_order(buy_stop(20010.0), *gap, rules=F01)
    assert (f.trigger, f.price) == (20012.0, 20012.25)                            # a gap: the open
    thru = mk(bars={945: (20008.0, 20010.25, 20007.0, 20009.0)})
    f = W.fill_order(sell_limit(20010.0), *thru, rules=F01)
    assert (f.trigger, f.price) == (20010.25, 20010.0)                            # the trade a tick through
    f = W.fill_order(buy_limit(19990.0), *mk(bars={950: (19995.0, 19996.0, 19989.75, 19992.0)}), rules=F01)
    assert (f.trigger, f.price) == (19989.75, 19990.0)
    lgap = mk(bars={939: (19995.0, 19996.0, 19994.0, 19995.0), 940: (19985.0, 19986.0, 19984.0, 19985.0)})
    f = W.fill_order(buy_limit(19990.0), *lgap, rules=F01)
    assert (f.trigger, f.price) == (19985.0, 19990.0)                             # opened through: the open
    f = W.fill_order(W.Order(W.MARKET, +1, LIVE), *mk(bars={931: (20001.0, 20002.0, 20000.0, 20001.0)}), rules=F01)
    assert f.trigger == f.price == 20001.0
    f = W.fill_order(buy_stop(20010.0), *mk(), rules=F01)
    assert f.status == "cancelled" and math.isnan(f.trigger)


def test_the_mirror_booking_modes():
    brk = mk(bars={940: (20005.0, 20010.0, 20004.0, 20008.0)})
    assert one(buy_stop(20010.0), brk).mirror_price == 20010.25                   # rule_fill: the rule's fill
    t = W.trade(buy_stop(20010.0), *brk, 100, (1.0,), rules=F01, mirror_booking="symmetric")
    assert (t.fill.price, t.mirror_price) == (20010.25, 20009.75)                 # a tick the other side of 20010
    fade = mk(bars={945: (20008.0, 20010.25, 20007.0, 20009.0)})
    t = W.trade(sell_limit(20010.0), *fade, 100, (1.0,), rules=F01, mirror_booking="symmetric")
    assert (t.fill.price, t.mirror_price) == (20010.0, 20010.5)                   # 20010.25 +/- a tick
    mkt = mk(bars={931: (20001.0, 20002.0, 20000.0, 20001.0)})
    t = W.trade(W.Order(W.MARKET, +1, LIVE), *mkt, 100, (1.0,), rules=F01, mirror_booking="symmetric")
    assert t.mirror_price == 20001.0
    # the mirror walks from its own booking: its stop is 25 points above it
    later = mk(bars={940: (20005.0, 20010.0, 20004.0, 20008.0), 1000: (20008.0, 20035.0, 20007.0, 20030.0)})
    rf = one(buy_stop(20010.0), later).mirror
    sym = W.trade(buy_stop(20010.0), *later, 100, (1.0,), rules=F01, mirror_booking="symmetric").mirror
    assert rf.kind[0] == W.FLATTEN and (sym.kind[0], sym.exit[0]) == (W.STOP, 1000)  # 20035.25 vs 20034.75


def test_the_pair_rule_marks_a_fill_bar_touching_either_trades_barrier_ambiguous():
    rule_stop = mk(LOW, bars={931: (19990.0, 20001.0, 19975.0, 19995.0)})       # fill 20000, low at the rule's stop
    t = W.trade(buy_stop(19999.75), *rule_stop, 100, (1.0, 3.0), rules=F01, fill_bar="pair")
    assert t.ambiguous.tolist() == [True, True]
    for side in (t.rule, t.mirror):
        assert side.kind.tolist() == [W.AMBIGUOUS] * 2 and side.gross.tolist() == [-100, -100]
        assert side.exit.tolist() == [931, 931] and not side.win.any()
    mirror_stop = mk(LOW, bars={931: (19995.0, 20025.0, 19994.0, 20020.0)})     # the high at the mirror's stop
    t = W.trade(buy_stop(19999.75), *mirror_stop, 100, (1.0,), rules=F01, fill_bar="pair")
    assert t.ambiguous.tolist() == [True]
    # per bracket: a half-R target touched on the fill bar, no stop and no 1R target
    half = mk(LOW, bars={931: (19995.0, 20015.0, 19994.0, 20010.0)})            # 60 ticks above the fill
    t = W.trade(buy_stop(19999.75), *half, 100, (0.5, 1.0), rules=F01, fill_bar="pair")
    assert t.ambiguous.tolist() == [True, False]
    assert t.rule.kind[0] == W.AMBIGUOUS and t.rule.kind[1] != W.AMBIGUOUS


def test_the_pair_rule_walks_a_clean_pair_from_the_next_bar():
    arr = mk(bars={940: (20005.0, 20010.0, 20004.0, 20008.0)})                  # fill 20010.25; fill-bar low 25 ticks
    declared = one(buy_stop(20010.0), arr)
    pair = W.trade(buy_stop(20010.0), *arr, 100, (1.0,), rules=F01, fill_bar="pair")
    assert pair.ambiguous.tolist() == [False]
    assert declared.rule.mae[0] == 25 and pair.rule.mae[0] == 9                   # 20010.25 - 20008.00 from bar 941
    assert declared.rule.kind[0] == pair.rule.kind[0] == W.FLATTEN
    assert one(buy_stop(20010.0), arr, rrs=(1.0,)).ambiguous.tolist() == [False]  # declared: nothing is ambiguous


def test_a_market_fill_is_walked_whole_in_every_mode():
    arr = mk(bars={931: (20000.0, 20025.25, 19999.0, 20020.0)})
    for fb in ("declared", "pair"):
        for mb in ("rule_fill", "symmetric"):
            t = W.trade(W.Order(W.MARKET, +1, LIVE), *arr, 100, (1.0,), rules=F01, fill_bar=fb, mirror_booking=mb)
            assert (t.rule.kind[0], t.rule.exit[0], t.ambiguous[0]) == (W.TARGET, 931, False)


def test_unknown_modes_are_refused():
    arr = mk(bars={940: (20005.0, 20010.0, 20004.0, 20008.0)})
    with pytest.raises(ValueError):
        W.trade(buy_stop(20010.0), *arr, 100, (1.0,), fill_bar="strict")
    with pytest.raises(ValueError):
        W.trade(buy_stop(20010.0), *arr, 100, (1.0,), mirror_booking="market")


def test_an_ambiguous_pair_is_costed_as_a_stopped_loss():
    k = W.Costs(fee_micro_eq=1.0, tick_value=0.5)
    assert W.KIND_CODE[W.AMBIGUOUS] == "a" and W.EXIT_TICKS[W.AMBIGUOUS] == W.EXIT_TICKS[W.STOP]
    t = W.trade(buy_stop(19999.75), *mk(LOW, bars={931: (19990.0, 20001.0, 19975.0, 19995.0)}), 100, (1.0,),
                rules=F01, fill_bar="pair", costs=k)
    assert t.rule.net_r[0] == t.mirror.net_r[0] == -1.0 - (0.0 + 1.0 + 1.0 * 0.5) / (100 * 0.5)
