"""Q-152: the component scheduler (`extended/components.py`) on synthetic data only -- never a real bar.

What is held:
* a design's refusals: colliding component windows (CHARTER 3.5), a window outside its session or after the firm's
  last new entry, any overlap mode but `refused` (the three-way design note 1.6), repeated names, a trigger that is not
  one of the library's sources;
* one position at a time across a firm (Stage 2 D-429): offers while a position is open are skipped (`position`),
  within five minutes of its exit (`gap`), while an entry order is working (`order`); every schedule's trades are five
  minutes apart at least, on hand-built and synthetic days;
* RL3's one-cancels-other tickets: the first fill wins and cancels the other; two fills on one bar void the group;
* the user's book: two positions held at once refused -- opposite sides as conduct tier 1 (across accounts and
  firms), the same side as an undefined overlap; touching intervals and other sessions accepted; `schedule_user`
  refuses two firms trading at once;
* the coin: one unit's draw shared by every firm, the schedule a function of the unit (same unit, same schedule);
* the schedule's fields are the walker's trade.

Seeds fixed for this file (the test's own, used nowhere else): 20261524 (the synthetic series), 20261525 (the coin
unit's role seed).
"""
from __future__ import annotations

from dataclasses import replace
from datetime import date

import numpy as np
import pytest

from extended import components as C
from extended import synthetic_bars as sb
from extended import triggers as T
from extended import walker as W

SEED_SERIES, SEED_COIN = 20261524, 20261525
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


def ctx0(h: T.History, **kw) -> T.DayContext:
    return T.DayContext(0, h.days[0], **kw)


def marks_component(name, first, last, marks, stop=40, rr=1.0, entry=T.MARKET, session="ny_am"):
    return C.Component(name, session, first, last, T.P16Marks(tuple(marks), entry=entry), stop, rr)


# ------------------------------------------------------------------------------------------------ design refusals


def test_design_refusals():
    a = marks_component("a", 960, 1000, (960,))
    with pytest.raises(C.DesignRefused, match="collide"):
        C.Design("ts", (a, marks_component("b", 1000, 1100, (1000,))))
    with pytest.raises(C.DesignRefused, match="outside session"):
        C.Design("ts", (marks_component("x", 960, 1000, (960,), session="asia"),))
    with pytest.raises(C.DesignRefused, match="last new entry"):
        C.Design("ts", (marks_component("x", 1300, 1329, (1300,), session="ny_pm"),))
    with pytest.raises(C.DesignRefused, match="overlap"):
        C.Design("ts", (a,), overlap="shared_path")
    with pytest.raises(C.DesignRefused, match="repeat"):
        C.Design("ts", (a, replace(a, first=1100, last=1200)))
    with pytest.raises(C.DesignRefused):
        C.Component("y", "ny_am", 960, 1000, object(), 40, 1.0)
    with pytest.raises(C.DesignRefused):
        C.UserBook(overlap="shared_path")
    d = C.Design("ts", (a, marks_component("b", 1001, 1100, (1005,))))
    assert [c.name for c in d.components] == ["a", "b"]
    b = C.session_bounds()
    assert b["ny_am"] == b["ny_pm"] == (930, 1330) and b["asia"] == (60, 540) and b["_last_entry"][1] == 1328


# ------------------------------------------------------------------------------------------------ the chain


def test_one_position_at_a_time_with_five_minutes_flat():
    day = flat_day()
    for s in range(1001, 1021):                                               # 20 minutes flat, then a stop-out
        set_bar(day, s, P, P, P, P)
    set_bar(day, 1021, P, P, P - 40 * TK, P - 40 * TK)
    for s in range(1022, 1439):
        set_bar(day, s, P - 40 * TK, P - 40 * TK, P - 40 * TK, P - 40 * TK)
    h = one_day(day)
    side = T.coin_side(UNIT, T.Offer("p16", 0, 1000, 0, 995, 1000, T.MARKET))
    if side == -1:                                                             # make the first trade's stop-out certain
        for s in range(1021, 1439):
            set_bar(day, s, P + 40 * TK, P + 40 * TK, P + 40 * TK, P + 40 * TK)
        set_bar(day, 1021, P, P + 40 * TK, P, P + 40 * TK)
        h = one_day(day)
    comp = marks_component("m", 1000, 1100, (1000, 1010, 1020, 1025, 1030, 1035))
    s = C.schedule_day(C.Design("ts", (comp,)), h, 0, ctx0(h), UNIT)
    first = s.trades[0]
    assert (first.fill_slot, first.exit_slot, first.exit_kind) == (1000, 1022, "s")
    reasons = {o.live: r for o, r in s.skipped}
    # 1022 + 5 = 1027: 1025 too soon; the 1030 trade never reaches a barrier, so 1035 meets an open position
    assert reasons == {1010: "position", 1020: "position", 1025: "gap", 1035: "position"}
    assert [t.fill_slot for t in s.trades] == [1000, 1030]


def test_a_working_limit_blocks_other_offers():
    lim = C.Component("lim", "ny_am", 960, 965, T.P16Marks((960,), entry=T.LIMIT), 40, 1.0)
    mk = marks_component("mkt", 966, 1100, (970, 985, 995))
    day = flat_day(P)                                          # the limit's level: the price at 09:55, P
    for s in range(955, 1439):                                 # then two ticks up: a buy limit at P never fills
        set_bar(day, s, P + 2 * TK, P + 2 * TK, P + 2 * TK, P + 2 * TK)
    h = one_day(day)
    s = C.schedule_day(C.Design("ts", (lim, mk)), h, 0, ctx0(h), UNIT)
    side = T.coin_side(UNIT, T.Offer("p16", 0, 960, 0, 955, 960, T.LIMIT, P))
    if side == 1:                                              # a resting buy at P below the market: works 960..989
        assert {o.live: r for o, r in s.skipped} == {970: "order", 985: "order"}
        assert s.unfilled[0][1] == "cancelled:cutoff" and [t.live for t in s.trades] == [995]
    else:                                                      # a sell limit at P is marketable at live: void
        assert s.unfilled[0][1] == "void:through" and s.trades[0].live == 970
        assert {o.live: r for o, r in s.skipped} == {985: "position", 995: "position"}


def test_rl3_one_cancels_other_and_a_same_bar_tie():
    prev, day = flat_day(13050.0), flat_day(13050.0)
    set_bar(prev, W.slot(9, 0), 13050.0, 13150.0, 12950.0, 13050.0)            # pd: high 13150, low 12950
    h2 = T.History.from_arrays(["2021-03-02", "2021-03-03"], ["NQH1", "NQH1"],
                               *[np.stack([a, b]) for a, b in zip(prev, day)])
    comp = C.Component("rl3", "ny_am", 960, 1015, T.RL3Tickets("pd", T.RL3_CUTOFFS[2]), 100, 1.0)
    ctx = T.DayContext(1, "2021-03-03")
    offs = comp.trigger.offers(h2, 1, ctx)
    sides = {o.tag: T.coin_side(UNIT, o) for o in offs}
    # the high's ticket first: a bar through 13150 by two ticks at 10:00, the low's at 10:20
    set_bar(day, 1020, 13050.0, 13150.0 + 2 * TK, 13050.0, 13050.0)
    set_bar(day, 1040, 13050.0, 13050.0, 12950.0 - 2 * TK, 13050.0)
    h = T.History.from_arrays(["2021-03-02", "2021-03-03"], ["NQH1", "NQH1"],
                              *[np.stack([a, b]) for a, b in zip(prev, day)])
    s = C.schedule_day(C.Design("ts", (comp,)), h, 1, ctx, UNIT)
    assert len(s.trades) == 1 and s.trades[0].tag == "pd_hi" and s.trades[0].fill_slot == 1020
    assert s.trades[0].ticket_rule == ("break" if sides["pd_hi"] == 1 else "fade")
    assert s.unfilled == [(next(o for o in offs if o.tag == "pd_lo"), "oco_cancelled")]
    tie = flat_day(13050.0)
    set_bar(tie, 1020, 13050.0, 13150.0 + 2 * TK, 12950.0 - 2 * TK, 13050.0)   # both levels traded through on one bar
    ht = T.History.from_arrays(["2021-03-02", "2021-03-03"], ["NQH1", "NQH1"],
                               *[np.stack([a, b]) for a, b in zip(prev, tie)])
    st = C.schedule_day(C.Design("ts", (comp,)), ht, 1, ctx, UNIT)
    assert st.trades == [] and {r for _, r in st.unfilled} == {"oco_tie"}


def test_the_chain_on_synthetic_days(hist):
    design = C.Design("ts", (
        C.Component("rl3", "ny_am", 960, 965, T.RL3Tickets("rn100", T.RL3_CUTOFFS[0]), 100, 1.5),
        marks_component("p16", 1020, 1075, T.p16_grid(1020, 1080), stop=150),
        C.Component("brk", "ny_pm", 1080, 1260, T.P14Breakout(latency=3), 50, 2.0),
    ))
    n = skipped = 0
    for i in range(len(hist)):
        ctx = T.DayContext(i, hist.days[i], bls=(i % 5 == 4))
        s = C.schedule_day(design, hist, i, ctx, UNIT)
        for a, b in zip(s.trades, s.trades[1:]):
            assert b.fill_slot >= a.exit_slot + T.GAP_MINUTES and b.live >= a.exit_slot + T.GAP_MINUTES
        for t in s.trades:
            comp = next(c for c in design.components if c.name == t.component)
            assert comp.first <= t.live <= comp.last and t.side in (1, -1) and t.side_source == "coin"
            assert t.exit_slot >= t.fill_slot and t.exit_slot <= T.JOURNEY.walk_end
        n += len(s.trades)
        skipped += len(s.skipped)
        assert set(s.counts()["skipped"]) <= set(C.SKIP_REASONS)
    assert n > len(hist) and skipped > 0
    again = C.schedule_day(design, hist, 3, T.DayContext(3, hist.days[3]), UNIT)
    assert again.trades == C.schedule_day(design, hist, 3, T.DayContext(3, hist.days[3]), UNIT).trades


def test_the_schedule_is_the_walkers_trade(hist):
    comp = C.Component("brk", "ny_pm", 1080, 1260, T.P14Breakout(latency=5), 60, 1.5)
    costs = W.Costs(fee_micro_eq=0.74)
    for i in range(4):
        ctx = T.DayContext(i, hist.days[i])
        s = C.schedule_day(C.Design("ts", (comp,)), hist, i, ctx, UNIT, costs=costs)
        for t in s.trades:
            off = next(o for o in comp.trigger.offers(hist, i, ctx) if o.decision == t.decision)
            ex = T.execute(off, T.coin_side(UNIT, off), hist, i, ctx, 60, 1.5, costs=costs)
            tr = ex.trade
            assert (t.fill_slot, t.fill_price, t.exit_slot, t.gross_ticks) == (
                tr.fill.bar - 1, tr.fill.price, int(tr.rule.exit[0]), int(tr.rule.gross[0]))
            assert t.exit_kind == W.KIND_CODE[int(tr.rule.kind[0])] and t.net_r == float(tr.rule.net_r[0])
            assert t.target_ticks == W.target_ticks(1.5, 60) and t.order_kind == W.MARKET and t.ticket_rule == ""


# ------------------------------------------------------------------------------------------------ the user's book


def pos(firm, account, open_, close, side, session=10):
    return C.Position(firm, account, session, open_, close, side, ref=f"{firm}:{open_}")


def test_user_book_refuses_overlap_and_opposition():
    b = C.UserBook()
    b.add(pos("ts", "a1", 1000, 1050, 1))
    with pytest.raises(C.TierOneRefused):
        b.add(pos("ts", "a2", 1020, 1060, -1))                                 # across accounts of one firm
    with pytest.raises(C.TierOneRefused):
        b.add(pos("mffu", "m1", 1049, 1100, -1))                               # across firms
    with pytest.raises(C.OverlapRefused):
        b.add(pos("mffu", "m1", 1000, 1050, 1))                                # the same trade copied: overlap
    b.add(pos("mffu", "m1", 1050, 1100, -1))                                   # opens as the first closes: no overlap
    b.add(pos("ts", "a1", 1000, 1050, -1, session=11))                         # another session
    assert len(b.positions) == 3
    with pytest.raises(ValueError):
        b.add(pos("ts", "a1", 1200, 1100, 1))


def test_schedule_user_refuses_two_firms_at_once_and_shares_the_coin(hist):
    comp = C.Component("brk", "ny_pm", 1080, 1260, T.P14Breakout(latency=5), 60, 1.5)
    a, b = C.Design("ts", (comp,)), C.Design("mffu", (comp,))
    i = next(k for k in range(len(hist))
             if C.schedule_day(a, hist, k, T.DayContext(k, hist.days[k]), UNIT).trades)
    ctx = T.DayContext(i, hist.days[i])
    with pytest.raises(C.OverlapRefused):                                      # the same moments, the same coin side
        C.schedule_user((a, b), hist, i, ctx, UNIT)
    sa = C.schedule_day(a, hist, i, ctx, UNIT)
    sb_ = C.schedule_day(b, hist, i, ctx, UNIT)
    assert [t.side for t in sa.trades] == [t.side for t in sb_.trades]
    with pytest.raises(C.DesignRefused):
        C.schedule_user((a, a), hist, i, ctx, UNIT)
    am = C.Design("mffu", (marks_component("am", 960, 1000, (960,), stop=40, rr=0.5),))
    pa = [C.position_of(t) for t in sa.trades]
    pm = [C.position_of(t) for t in C.schedule_day(am, hist, i, ctx, UNIT).trades]
    clash = any(x.interval()[0] < y.interval()[1] and y.interval()[0] < x.interval()[1] for x in pa for y in pm)
    if clash:
        with pytest.raises((C.OverlapRefused, C.TierOneRefused)):
            C.schedule_user((a, am), hist, i, ctx, UNIT)
    else:
        days, book = C.schedule_user((a, am), hist, i, ctx, UNIT)
        assert len(book.positions) == len(pa) + len(pm) > len(pa)


def test_the_coin_follows_the_unit(hist):
    comp = C.Component("brk", "ny_pm", 1080, 1260, T.P14Breakout(latency=2), 60, 1.5)
    d = C.Design("ts", (comp,))
    offs = []
    for i in range(len(hist)):
        offs += comp.trigger.offers(hist, i, T.DayContext(i, hist.days[i]))
    a = [T.coin_side(UNIT, o) for o in offs]
    b = [T.coin_side(replace(UNIT, start=1), o) for o in offs]
    assert a != b and len(offs) > 100
    assert C.schedule_day(d, hist, 2, T.DayContext(2, hist.days[2]), UNIT).trades == \
        C.schedule_day(d, hist, 2, T.DayContext(2, hist.days[2]), T.CoinUnit(SEED_COIN, 0, 0, 0, 0, "MNQ")).trades
