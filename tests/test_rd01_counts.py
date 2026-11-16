"""RD-01 T-13's pure part (`prereg/RD-01_firm_contracts.md` 5.5, 9.3, A-11, 14.3): TradeDay's tier-1 windows from the
fixed calendars and the record, a trade open at a window's start at some offered R counted and booked at the strict
end, the lenient end and "no liquidation", a trade whose exit bar is stamped before the window not counted, an entry
inside a window skipped; and the 9.3 counts for martingale steps (per account and firm-wide, in micro-equivalents) and
for trades a session. Pure Python on hand-built trades: no engine, no bar."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pytest

from extended import firm_counts as C
from extended import walker as W


def test_the_windows_are_tradedays_tier1_releases_for_nq():
    w = C.window_spec()
    assert w == {"morning": (W.slot(7, 28), W.slot(7, 32)), "afternoon": (W.slot(12, 58), W.slot(13, 2))}
    days = C.tier1_days()
    # a CPI day, an employment-report day, an FOMC statement day and an FOMC minutes day of the development window
    kinds = {k for v in days.values() for k in v}
    assert kinds == {"cpi", "employment", "fomc_statement", "fomc_minutes"}
    assert all(date(2020, 1, 2) <= d <= date(2026, 7, 16) for d in days)
    assert days[date(2020, 1, 10)] == ["employment"]                    # the Employment Situation for December 2019
    from extended.calendar_fomc_minutes import release_days
    assert all("fomc_minutes" in days[d] for d in release_days())


def test_a_trade_open_at_a_window_start_at_some_offered_r_is_counted():
    t0 = W.slot(12, 58)
    # entry bar stamped 12:40 (index slot+1); exits: at R 1 the bar stamped 12:50 (before), at R 3 the bar stamped 13:20
    entry = W.bar_of(12, 40)
    exits = {1.0: float(W.bar_of(12, 50)), 3.0: float(W.bar_of(13, 20))}
    assert C.open_at(entry, exits, t0) is True
    assert C.open_at(entry, {1.0: float(W.bar_of(12, 50))}, t0) is False                # closed before the window
    assert C.open_at(entry, {1.0: float(W.bar_of(12, 57))}, t0) is False                # exit bar stamped 12:57
    assert C.open_at(entry, {1.0: float(W.bar_of(12, 58))}, t0) is True                 # stamped 12:58: open then
    assert C.entry_inside(W.bar_of(12, 58), "afternoon") and C.entry_inside(W.bar_of(13, 1), "afternoon")
    assert not C.entry_inside(W.bar_of(13, 2), "afternoon") and not C.entry_inside(W.bar_of(12, 57), "afternoon")


def test_the_bookings_are_5_5s():
    S, fee, R = 150, 1.22, 3.0
    from extended.walker import Costs, EXIT_TICKS, STOP, FLATTEN, cost_r
    costs = Costs(fee_micro_eq=fee)
    strict = C.book(R, S, fee, "strict")
    lenient = C.book(R, S, fee, "lenient")
    assert strict == pytest.approx(-1.0 - float(cost_r(np.array([STOP]), S, entry_ticks=W.SLIP_TICKS, costs=costs)[0]))
    want = (W.target_ticks(R, S) - 1) / S - float(cost_r(np.array([FLATTEN]), S, entry_ticks=W.SLIP_TICKS,
                                                          costs=costs)[0])
    assert lenient == pytest.approx(want)
    assert strict < lenient
    with pytest.raises(ValueError):
        C.book(R, S, fee, "walked")                       # the walked outcome is the trade's own, not a booking


@dataclass
class Block:                                           # a stand-in with DayBlock's fields the booking reads
    pnl: np.ndarray
    risked: np.ndarray
    exit_reasons: tuple
    risk_per_contract: np.ndarray | None = None
    mae: np.ndarray | None = None
    entry_t: np.ndarray | None = None
    exit_t: np.ndarray | None = None
    r_by_rr: dict | None = None
    mae_by_rr: dict | None = None
    markets: tuple | None = None
    fee: np.ndarray | None = None
    sides: np.ndarray | None = None
    exit_by_rr: dict | None = None


def _day(entries, exits_by_rr, outcomes_by_rr):
    n = len(entries)
    rpc = np.full(n, 75.0)                             # 150 ticks x $0.50: a 37.5-point stop
    return Block(pnl=np.array([outcomes_by_rr[1.0][j] * 75.0 for j in range(n)]), risked=np.full(n, 75.0),
                 exit_reasons=("x",) * n, risk_per_contract=rpc, mae=np.full(n, 30.0),
                 entry_t=np.array(entries, float), exit_t=np.array(exits_by_rr[1.0], float),
                 r_by_rr={k: np.array(v, float) for k, v in outcomes_by_rr.items()},
                 mae_by_rr={k: np.full(n, 0.4) for k in outcomes_by_rr}, fee=np.full(n, 1.22),
                 exit_by_rr={k: np.array(v, float) for k, v in exits_by_rr.items()})


def test_the_tier1_blocks_book_counted_trades_and_skip_entries_inside():
    d = date(2024, 1, 3)                               # an FOMC minutes day (the pinned calendar)
    assert "fomc_minutes" in C.tier1_days()[d]
    entries = [W.bar_of(12, 30), W.bar_of(11, 0), W.bar_of(12, 59)]
    exits = {1.0: [W.bar_of(13, 10), W.bar_of(11, 30), W.bar_of(13, 20)],
             3.0: [W.bar_of(14, 0), W.bar_of(11, 45), W.bar_of(14, 0)]}
    outs = {1.0: [0.98, -1.01, 0.97], 3.0: [-1.01, -1.01, 2.95]}
    day = _day(entries, exits, outs)
    quiet = _day(entries, exits, outs)
    blocks, dates = [day, quiet], [d, date(2024, 1, 4)]
    strict, n_s = C.tier1_blocks(blocks, dates, "strict")
    walked, n_w = C.tier1_blocks(blocks, dates, "walked")
    assert n_s == n_w == {"open_at_start": 1, "entries_inside": 1}
    b = strict[0]
    assert b.r_by_rr[1.0][0] == pytest.approx(C.book(1.0, 150, 1.22, "strict"))
    assert b.r_by_rr[3.0][0] == pytest.approx(C.book(3.0, 150, 1.22, "strict"))
    assert b.r_by_rr[1.0][1] == -1.01                  # closed before the window: unchanged
    assert np.isnan(b.r_by_rr[1.0][2]) and np.isnan(b.r_by_rr[3.0][2])     # entered inside the window: skipped
    assert list(b.exit_by_rr[3.0]) == list(day.exit_by_rr[3.0])            # held to its walked exit (routing)
    assert strict[1] is quiet                           # a day with no window is the same block
    assert walked[0].r_by_rr[3.0][0] == -1.01          # "no liquidation": the walked outcome
    assert np.isnan(walked[0].r_by_rr[1.0][2])         # ... and the entry inside still skipped


def test_the_martingale_count_per_account_and_firm_wide():
    trades = [  # (account, day, entry, micros, pnl)
        {"account": ("combine", 0), "day": 1, "entry": 10.0, "contracts": 3, "pnl": -100.0},
        {"account": ("funded", 0), "day": 1, "entry": 20.0, "contracts": 26, "pnl": 500.0},   # 2x after a loss, firm-wide
        {"account": ("combine", 0), "day": 2, "entry": 10.0, "contracts": 6, "pnl": -50.0},   # 2x after its own loss
        {"account": ("combine", 0), "day": 3, "entry": 10.0, "contracts": 12, "pnl": 10.0},   # 2x after a loss, both
        {"account": ("funded", 0), "day": 3, "entry": 30.0, "contracts": 11, "pnl": 10.0},    # < 2x its own last
    ]
    got = C.martingale_steps(trades)
    # per account: the combine's day 2 (6 >= 2 x 3) and day 3 (12 >= 2 x 6); firm-wide: the funded opening after the
    # combine's loss (26 >= 2 x 3) and the combine's day 3 (12 >= 2 x 6, after the day-2 loss)
    assert got == {"per_account": 2, "firm_wide": 2, "trades": 5}


def test_trades_a_session_per_account_and_across():
    trades = [{"account": ("funded", i % 2), "day": 5, "entry": float(i), "contracts": 1, "pnl": 1.0} for i in range(7)]
    trades += [{"account": ("funded", 0), "day": 6, "entry": 1.0, "contracts": 1, "pnl": 1.0}]
    got = C.trades_a_session(trades)
    assert got == {"max_per_account": 4, "max_across": 7, "line": C.trade_count_line(), "sessions_above_line": 0}
    assert C.trade_count_line() == 200
