"""Q-152: the component scheduler (`extended/components.py`) on synthetic data only -- never a real bar.

What is held:
* a design's refusals: colliding component windows (CHARTER 3.5), a window outside its session or after the firm's
  last new entry, any overlap mode but `refused` (the three-way design note 1.6), repeated names, a trigger that is not
  one of the library's sources;
* one position at a time across a firm (Stage 2 D-429): offers while a position is open are skipped (`position`),
  within five minutes of its exit (`gap`), while an entry order is working (`order`); every schedule's trades are five
  minutes apart at least, on hand-built and synthetic days;
* RL3's one-cancels-other tickets: the first fill wins and cancels the other; two fills on one bar book the worse
  walked trade and keep the firm busy to the later exit (the M-6 ruling, E-223 as amended);
* a group keeps the firm busy until its last working stretch ends, a re-written ticket that turns void included
  (corrective cycle 1, B-1; the red team's day `docs/reviews/BUILD_W31_Q152_2026-11-18.md`);
* **every decision of `schedule_day` -- placed, skipped (with its reason), refused -- is unchanged when the bars from
  that decision's moment on are replaced or deleted** (M-5): on the red team's day and on synthetic days with news
  windows after 09:00 and re-written tickets;
* a skip is counted by the state at its live minute: `order` while an order works, `position`, `gap` (M-7);
* the user's book: two positions held at once refused -- opposite sides as conduct tier 1 (across accounts and
  firms), the same side as an undefined overlap; touching intervals and other sessions accepted; `schedule_user`
  refuses two firms trading at once, on hand-built days whose overlap is certain (N-8);
* the coin: one unit's draw shared by every firm, the schedule a function of the unit (same unit, same schedule);
* the schedule's fields are the walker's trade.

Seeds fixed for this file (the test's own, used nowhere else): 20261524 (the synthetic series), 20261525 (the coin
unit's role seed), 20261526 (the shift test's replacement walks; each cut a child `SeedSequence(20261526,
spawn_key=(day, cut))`). The red team's day uses its own unit, seed 1 (as `chk_rewrite_void.py` ran it).
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

SEED_SERIES, SEED_COIN, SEED_SHIFT = 20261524, 20261525, 20261526
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
    b = C.session_bounds()                                  # every search-year weekday at once (E-231 (3))
    assert b["ny_am"] == b["ny_pm"] == (930, 1330) and b["asia"] == (120, 540) and b["_last_entry"][1] == 1328
    assert b["evening"] == (0, 60) and b["london"] == (600, 930)
    winter, summer, mismatch = (C.session_bounds(date(2021, 1, 15)), C.session_bounds(date(2021, 7, 15)),
                                C.session_bounds(date(2021, 3, 17)))   # Tokyo 09:00 at 18:00 / 19:00 CT; London 03:00
    assert winter["asia"] == (60, 540) and summer["asia"] == (120, 540) and mismatch["london"] == (600, 930)
    early = marks_component("x", 60, 100, (960,), session="asia")      # the window is what is checked
    assert C.Design("ts", (early,), day=date(2021, 1, 15)).day == date(2021, 1, 15)
    for day in (None, date(2021, 7, 15)):                   # 18:00 CT is not Tokyo's open under US daylight time
        with pytest.raises(C.DesignRefused, match="outside session"):
            C.Design("ts", (early,), day=day)


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

TIE_STOP, TIE_RR = 400, 3.0                             # 100 points; targets 300 points away
TIE_KINDS = ("flat", "up", "down")
TIE_MK_MARKS = (1025, 1035, 1060, 1105, 1110, 1200)


def tie_component() -> C.Component:
    return C.Component("rl3", "ny_am", 960, 1015, T.RL3Tickets("pd", T.RL3_CUTOFFS[2]), TIE_STOP, TIE_RR)


def tie_history(kind: str) -> T.History:
    """The M-6 tie days: a prior day whose regular session spans 12950-13150 (`pd`), and a day on which both levels
    trade through on the bar stamped 10:20; then flat, up (to 13250 at 10:30, a short from 13150 stopped there; through
    13250 at 11:40, a long from 12950's target) or down (the mirror)."""
    prev = flat_day(13050.0)
    set_bar(prev, W.slot(9, 0), 13050.0, 13150.0, 12950.0, 13050.0)
    tie = flat_day(13050.0)
    set_bar(tie, 1020, 13050.0, 13150.0 + 2 * TK, 12950.0 - 2 * TK, 13050.0)
    if kind == "up":
        for s in range(1030, 1439):
            set_bar(tie, s, 13250.0, 13250.0, 13250.0, 13250.0)
        set_bar(tie, 1100, 13250.0, 13251.0, 13250.0, 13250.0)
    elif kind == "down":
        for s in range(1030, 1439):
            set_bar(tie, s, 12850.0, 12850.0, 12850.0, 12850.0)
        set_bar(tie, 1100, 12850.0, 12850.0, 12849.0, 12850.0)
    return T.History.from_arrays(["2021-03-02", "2021-03-03"], ["NQH1", "NQH1"],
                                 *[np.stack([a, b]) for a, b in zip(prev, tie)])


def test_a_same_bar_tie_books_the_worse_trade_and_stays_busy_to_the_later_exit():
    """The M-6 ruling (lead; E-223 as amended to this rule): both one-cancels-other tickets filling on one bar book the
    ticket whose walked trade is worse for the user (lower gross; then the later exit; then the lower sub), never no
    trade, and the firm stays busy to the later of the two walked exits (the booked one may be the earlier: the
    decision of a later offer must not depend on which is booked, M-5). Catches: no trade booked on a tie, the better
    trade booked, the firm freed at the tie bar or at the booked trade's own exit."""
    stop, rr = TIE_STOP, TIE_RR
    rl3 = tie_component()
    mk = marks_component("mk", 1016, 1300, TIE_MK_MARKS, stop=40, rr=1.0)
    ctx = T.DayContext(1, "2021-03-03")
    earlier_booked = 0
    for kind in TIE_KINDS:
        ht = tie_history(kind)
        offs = rl3.trigger.offers(ht, 1, ctx)
        exs = [T.execute(o, T.coin_side(UNIT, o), ht, 1, ctx, stop, rr) for o in offs]
        assert all(e.filled and e.trade.fill.bar == 1021 for e in exs)
        worst = min(exs, key=lambda e: (int(e.trade.rule.gross[0]), -e.exit_slot, e.offer.sub))
        end = max(e.exit_slot for e in exs)
        earlier_booked += worst.exit_slot < end
        st = C.schedule_day(C.Design("ts", (rl3, mk)), ht, 1, ctx, UNIT)
        rl3_rows = [t for t in st.trades if t.component == "rl3"]
        assert len(rl3_rows) == 1 and rl3_rows[0].tag == worst.offer.tag and rl3_rows[0].oco_tie
        assert rl3_rows[0].gross_ticks == int(worst.trade.rule.gross[0]) and rl3_rows[0].busy_until == end
        other = next(o for o in offs if o.tag != worst.offer.tag)
        assert (other, "oco_tie_cancelled") in st.unfilled
        tie_skips = [(o.live, r) for o, r in st.skipped if o.live < end + T.GAP_MINUTES]
        assert tie_skips and all(r == ("position" if live < end else "gap") for live, r in tie_skips)
        mk_rows = [t for t in st.trades if t.component == "mk"]
        assert all(t.live >= end + T.GAP_MINUTES for t in mk_rows)
        assert mk_rows or end + T.GAP_MINUTES > 1200                 # the last mark is 13:00
    assert earlier_booked >= 1                                       # a case where the booked trade closes first


def test_m2_decisions_on_the_tie_days_are_shift_invariant():
    """m-2 (the re-read): the decision shift test on the three tie days. Catches: the firm kept busy only to the
    booked trade's exit (the M-6 wording before its amendment), which the red team's read found makes three decisions
    depend on later bars here."""
    design = C.Design("ts", (tie_component(), marks_component("mk", 1016, 1300, TIE_MK_MARKS, stop=40, rr=1.0)))
    ctx = T.DayContext(1, "2021-03-03")
    total = 0
    for k, kind in enumerate(TIE_KINDS):
        bad, n = shift_violations(design, tie_history(kind), 1, ctx, UNIT, day_key=200 + k)
        assert not bad, (kind, bad[:3])
        total += n
    assert total > 30


@pytest.mark.parametrize("mfffu_mark, refused", [(1040, True), (1110, False)])
def test_m1_a_tie_counts_as_either_ticket_in_the_users_book(mfffu_mark, refused):
    """m-1 (the re-read; conduct tier 1): on a same-bar tie the user may hold either ticket's position until the
    group's busy time, so the book holds both possible positions, both sides, over [fill, busy_until), and another
    firm's position inside that span is refused -- as tier 1, since one of the two sides opposes it. The red team's
    input: the "down" tie day (the booked long closes at 10:11, the short could be open to 11:21) and an MFFU mark at
    10:20 CT; a mark at 11:30, after the later exit, is accepted. Catches: the book closing the tie at the booked
    ticket's exit, the book checking the booked side only."""
    ts = C.Design("ts", (tie_component(),))
    mf = C.Design("mffu", (marks_component("m", 1016, 1300, (mfffu_mark,), stop=40),))
    h, ctx = tie_history("down"), T.DayContext(1, "2021-03-03")
    row = C.schedule_day(ts, h, 1, ctx, UNIT).trades[0]
    assert row.oco_tie and row.exit_slot < row.busy_until and set(row.tie_sides) == {1, -1}
    alts = C.positions_of(row)
    assert {p.side for p in alts} == {1, -1} and all(p.interval()[1] - p.session * 1440 == row.busy_until
                                                      for p in alts)
    if refused:
        with pytest.raises(C.TierOneRefused):
            C.schedule_user((ts, mf), h, 1, ctx, UNIT)
    else:
        days, book = C.schedule_user((ts, mf), h, 1, ctx, UNIT)
        assert len(book.positions) == 3 and days[1].trades[0].fill_slot == mfffu_mark


def test_m3_a_day_ending_before_the_walks_end_is_refused_unless_voided():
    """m-3 (the re-read): a day whose last bar is before `rules.walk_end` (under `JOURNEY`, no bar stamped 15:07 or
    later) is refused unless the caller voided it -- the walker's last fill bar would otherwise depend on whether later
    bars exist. Catches: the guard missing, a guard off by a bar (a day ending at 15:07 is accepted)."""
    comp = marks_component("m", 1016, 1300, (1200,), stop=40)
    day = flat_day()
    for a in day:
        a[W.slot(15, 3) + 1:] = np.nan                                      # the last bar is stamped 15:02
    h = one_day(day)
    with pytest.raises(C.DayRefused):
        C.schedule_day(C.Design("ts", (comp,)), h, 0, ctx0(h), UNIT)
    s = C.schedule_day(C.Design("ts", (comp,)), h, 0, ctx0(h, void=True), UNIT)
    assert s.trades == [] and {r for _, r in s.refused} == {"calendar"}
    ok = flat_day()
    for a in ok:
        a[W.slot(15, 8) + 1:] = np.nan                                      # the last bar is stamped 15:07
    assert C.schedule_day(C.Design("ts", (comp,)), one_day(ok), 0, ctx0(one_day(ok)), UNIT).trades


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


def test_schedule_user_on_certain_overlap_and_certain_separation():
    """N-8: on hand-built days whose overlap is certain, `schedule_user` refuses -- as tier 1 exactly when the coin
    gives the two moments opposite sides -- and on a day whose separation is certain it books both. Catches: the book
    not consulted (no refusal), the opposite-side check missing or swapped, a refusal of separated positions."""
    ts = C.Design("ts", (marks_component("a", 960, 1005, (1000,), stop=40),))
    mf = C.Design("mffu", (marks_component("b", 1006, 1100, (1010,), stop=40),))
    h = one_day(flat_day())                                                    # flat: both held to the flatten
    s1 = T.coin_side(UNIT, T.Offer("p16", 0, 1000, 0, 995, 1000, T.MARKET))
    s2 = T.coin_side(UNIT, T.Offer("p16", 0, 1010, 0, 1005, 1010, T.MARKET))
    with pytest.raises(C.TierOneRefused if s1 != s2 else C.OverlapRefused):
        C.schedule_user((ts, mf), h, 0, ctx0(h), UNIT)
    day = flat_day()
    set_bar(day, 1002, P, P + 50 * TK, P - 50 * TK, P)                         # stops the 10:00 trade, either side
    h2 = one_day(day)
    days, book = C.schedule_user((ts, mf), h2, 0, ctx0(h2), UNIT)
    assert [t.exit_slot for t in days[0].trades] == [1003] and [t.fill_slot for t in days[1].trades] == [1010]
    assert len(book.positions) == 2


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


# ------------------------------------------------------------------------------------------------ corrective cycle 1

RT_UNIT = T.CoinUnit(1, 0, 0, 0, 0)                     # the red team's unit (`chk_rewrite_void.py`: seed 1)


def red_team_day(moved: bool) -> tuple[T.History, T.DayContext, C.Design]:
    """B-1's failing input (the review, B-1): a prior day with one bar, stamped 14:59, at 13100 (`pdc` 13100, a
    resistance above P_ref 13050); the day flat at 13050; a news window 09:40-09:50 CT; the ticket re-written at 09:51.
    `moved`: the bars stamped 09:45 and later at 13200, so the re-write finds the ticket through (void)."""
    prev = [np.full(1441, np.nan) for _ in range(4)]
    set_bar(prev, W.slot(14, 59), 13100.0, 13100.0, 13100.0, 13100.0)
    day = flat_day(13050.0)
    if moved:
        for s in range(1005, 1439):
            set_bar(day, s, 13200.0, 13200.0, 13200.0, 13200.0)
    h = T.History.from_arrays(["2021-03-02", "2021-03-03"], ["NQH1", "NQH1"],
                              *[np.stack([a, b]) for a, b in zip(prev, day)])
    ctx = T.DayContext(1, "2021-03-03", windows=(T.Window(1000, 1010, "news", "the red team's window"),))
    design = C.Design("ts", (C.Component("rl3", "ny_am", 960, 960, T.RL3Tickets("pdc", W.slot(14, 30)), 100, 1.0),
                             C.Component("mk", "ny_am", 961, 995, T.P16Marks((970, 980, 990)), 100, 1.0)))
    return h, ctx, design


def decisions(design: C.Design, hist: T.History, i: int, ctx: T.DayContext, unit: T.CoinUnit) -> dict:
    """Every offer's decision, {(source, decision, tag): (its moment = live, 'placed' | 'skipped:<why>' |
    'refused:<why>')}, read from `schedule_day`'s outputs only (so the old code runs it too)."""
    s = C.schedule_day(design, hist, i, ctx, unit)
    live = {}
    for comp in design.components:
        for o in comp.trigger.offers(hist, i, ctx):
            live[(o.source, o.decision, o.tag)] = int(o.live)
    out = {}
    for t in s.trades:
        out[(t.source, t.decision, t.tag)] = "placed"
    for o, _ in s.unfilled:
        out[(o.source, o.decision, o.tag)] = "placed"
    for o, r in s.skipped:
        out[(o.source, o.decision, o.tag)] = f"skipped:{r}"
    for o, r in s.refused:
        out[(o.source, o.decision, o.tag)] = f"refused:{r}"
    return {k: (live[k], v) for k, v in out.items()}


def shifted(h: T.History, i: int, t: int, mode: str, seed: np.random.SeedSequence) -> T.History:
    """The history with every bar of day i stamped at or after slot t, and every bar of every later day, replaced by
    a seeded random walk on the tick grid at another level (`replace`; which minutes hold a bar unchanged) or deleted
    (`delete`: minutes without a trade). The delete keeps day i's bars from the walk's end on (the bars ending 15:08 CT
    and later), so the day still ends where it did: where a day's bars end is the walker's `walk_end` (its last present
    bar, identity-covered Stage 2 convention), a calendar fact on the store (an early close or a data defect is a
    calendar void), and a day cut short would move the walker's own last fill bar."""
    arrs = [x.copy() for x in (h.o, h.h, h.l, h.c)]
    mask = np.zeros(arrs[0].shape, dtype=bool)
    mask[i, t + 1:] = True
    mask[i + 1:, 1:] = True
    mask &= ~np.isnan(arrs[0])
    if mode == "delete":
        mask[i, W.FLAT_ENTRY:] = False
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


def shift_violations(design, hist, i, ctx, unit, *, day_key: int, modes=("replace", "delete")) -> tuple[list, int]:
    """For each decision moment t of day i: the decisions with moment <= t, recomputed on `shifted` bars, against the
    base. Returns (violations, decisions compared)."""
    base = decisions(design, hist, i, ctx, unit)
    bad, n = [], 0
    for c, t in enumerate(sorted({m for m, _ in base.values()})):
        for mode in modes:
            seed = np.random.SeedSequence(SEED_SHIFT, spawn_key=(day_key, c))
            got = decisions(design, shifted(hist, i, t, mode, seed), i, ctx, unit)
            for k, (m, v) in base.items():
                if m <= t:
                    n += 1
                    if got.get(k) != (m, v):
                        bad.append((mode, t, k, (m, v), got.get(k)))
    return bad, n


def test_b1_a_rewritten_ticket_that_turns_void_keeps_the_firm_busy():
    """B-1: the ticket worked from 09:00 to the window, so the offers at 09:10, 09:20 and 09:30 meet a working order
    on both days, whatever the price after the window. Catches: `Execution.ended` taking the void re-write's live and
    the chain dropping executions whose last stretch is void (the old code trades 09:10 on the moved day)."""
    got = {}
    for moved in (False, True):
        h, ctx, design = red_team_day(moved)
        s = C.schedule_day(design, h, 1, ctx, RT_UNIT)
        assert s.unfilled[0][1] == ("void:through" if moved else "cancelled:cutoff")
        assert {o.live: r for o, r in s.skipped} == {970: "order", 980: "order", 990: "order"}
        assert s.trades == []
        got[moved] = {k: v for k, v in decisions(design, h, 1, ctx, RT_UNIT).items() if v[0] <= 1004}
    assert got[False] == got[True] and len(got[False]) == 4


def test_m5_every_decision_is_shift_invariant_on_the_red_teams_day():
    """M-5 on B-1's day: every decision is unchanged when the bars from its moment on are replaced or deleted.
    Catches B-1 (the old code fails here: the 09:10 offer is placed when a replacement leaves the ticket through at
    its re-write)."""
    for moved in (False, True):
        h, ctx, design = red_team_day(moved)
        bad, n = shift_violations(design, h, 1, ctx, RT_UNIT, day_key=int(moved))
        assert not bad, bad[:3]
        assert n >= 8


def test_m5_every_decision_is_shift_invariant_on_synthetic_days(hist):
    """M-5 on synthetic days with a news window after 09:00 (09:40-09:50) and an unscheduled release (11:10), so RL3
    tickets are re-written and cancelled: placed, skipped (with reasons) and refused decisions never depend on bars
    after their moment. Catches: a busy time computed from a stretch's outcome after the moment (B-1), a skip reason
    read from a later state or a fill known before its bar closes (M-7). These days hold no same-bar tie: the tie's
    busy time is held by `test_m2_decisions_on_the_tie_days_are_shift_invariant`."""
    design = C.Design("ts", (
        C.Component("rl3", "ny_am", 960, 960, T.RL3Tickets("pdc", W.slot(12, 0)), 100, 1.0),
        C.Component("lim", "ny_am", 961, 1075, T.P16Marks(T.p16_grid(965, 1080), entry=T.LIMIT), 60, 1.0),
        C.Component("brk", "ny_pm", 1080, 1260, T.P14Breakout(latency=3), 50, 1.5),
    ))
    windows = (T.Window(1000, 1010, "news", "test"), T.Window(1150, 1152, "unscheduled", "test"))
    total = rl3_placed = 0
    for i in range(1, 9):
        ctx = T.DayContext(i, hist.days[i], windows=windows)
        bad, n = shift_violations(design, hist, i, ctx, UNIT, day_key=100 + i)
        assert not bad, (hist.days[i], bad[:3])
        total += n
        s = C.schedule_day(design, hist, i, ctx, UNIT)
        rl3_placed += sum(1 for o, _ in s.unfilled if o.source == "rl3") + sum(1 for t in s.trades
                                                                                if t.source == "rl3")
    assert total > 500 and rl3_placed > 0


def test_m7_skips_are_counted_by_the_state_at_their_live_minute():
    """M-7: a ticket working from 09:00 and filling at 10:40: the offer at 10:00 meets a working order (`order`), the
    one at 11:40 an open position (`position`). Catches: the skip reason taken from the group's final state."""
    prev = [np.full(1441, np.nan) for _ in range(4)]
    set_bar(prev, W.slot(14, 59), 13100.0, 13100.0, 13100.0, 13100.0)          # pdc 13100, a resistance
    day = flat_day(13050.0)
    # gapping up to the level and through it by two ticks: the fade (sell limit at 13100) and the break (buy stop at
    # 13100.25) both fill, neither near its stop on the fill bar
    set_bar(day, W.slot(10, 40), 13100.0, 13100.0 + 2 * TK, 13100.0, 13100.0 + 2 * TK)
    for s in range(W.slot(10, 41), 1439):
        set_bar(day, s, 13100.0 + 2 * TK, 13100.0 + 2 * TK, 13100.0 + 2 * TK, 13100.0 + 2 * TK)
    h = T.History.from_arrays(["2021-03-02", "2021-03-03"], ["NQH1", "NQH1"],
                              *[np.stack([a, b]) for a, b in zip(prev, day)])
    design = C.Design("ts", (C.Component("rl3", "ny_am", 960, 960, T.RL3Tickets("pdc", W.slot(14, 30)), 100, 1.0),
                             C.Component("mk", "ny_am", 961, 1300, T.P16Marks((W.slot(10, 0), W.slot(11, 40))),
                                         100, 1.0)))
    s = C.schedule_day(design, h, 1, T.DayContext(1, "2021-03-03"), UNIT)
    assert [t.fill_slot for t in s.trades] == [W.slot(10, 40)]
    assert {o.live: r for o, r in s.skipped} == {W.slot(10, 0): "order", W.slot(11, 40): "position"}
