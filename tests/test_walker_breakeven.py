"""Q-20 (E-012 (2), E-013 (2)): the breakeven move's two fidelity corrections in the shared walker, on hand-built bars.

Stage 2's move (`fv3_rung_walk.py:140-190`, reproduced by `extended.walker`'s `STAGE2`): at the next FV3 session open
after the entry (its first bar within five minutes), if that open is a tick or more in the trade's favour and the trade
still open, the stop moves to the entry -- in force on that open bar itself -- and a bar that both touches the entry and
trades through the target books the target. The corrections, each a `Rules` option whose default is Stage 2's:

* `breakeven_tie="stop"` -- (a): on such a bar the stop first, as the walk's own convention on a two-barrier bar;
* `breakeven_delay=5` -- (b): the move made five minutes after the session open (D-266: at least five minutes from
  alert to order): decided on the open bar's open as before, in force from the first bar opening five minutes after
  that open (index >= the open bar + 5); until then the original bracket governs.

Long market entries at 08:30 CT (bar 931's open, 20000.00); stop 100 ticks (19975.00), 1R's target 100 ticks (a trade
through 20025.00). The 13:00 session's open bar is 1201 (its move bar under the delay: 1206).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extended import walker as W  # noqa: E402

BASE = 20000.0
LIVE = W.slot(8, 30)
S2 = W.STAGE2
TIE = W.STAGE2_BE_STOP_FIRST
LATE = W.STAGE2_BE_DELAY5
BOTH = W.STAGE2_BE_BOTH
OPEN = 1201                           # the 13:00 CT session's first bar


def mk(bars: dict[int, tuple[float, float, float, float]]) -> tuple[np.ndarray, ...]:
    """A full day flat at 20000.00, each given bar (o, h, l, c) set and every later bar flat at its close."""
    n = W.C_FLAT + 1
    o, h, l, c = (np.full(n, np.nan) for _ in range(4))
    price = BASE
    spec = dict(sorted(bars.items()))
    for j in range(1, n):
        if j in spec:
            o[j], h[j], l[j], c[j] = spec[j]
            price = spec[j][3]
        else:
            o[j] = h[j] = l[j] = c[j] = price
    return o, h, l, c


def walk(arr, rules, side: int = +1):
    t = W.trade(W.Order(W.MARKET, side, LIVE), *arr, 100, (1.0,), rules=rules)
    r = t.rule
    return int(r.kind[0]), int(r.exit[0]), int(r.gross[0])


ENTRY = {931: (20000.0, 20001.0, 19999.0, 20000.0)}


def test_the_defaults_are_stage2s_and_bad_options_are_refused():
    assert (S2.breakeven_tie, S2.breakeven_delay) == ("target", 0)
    assert (TIE.breakeven_tie, TIE.breakeven_delay) == ("stop", 0)
    assert (LATE.breakeven_tie, LATE.breakeven_delay) == ("target", 5)
    assert (BOTH.breakeven_tie, BOTH.breakeven_delay) == ("stop", 5)
    for p in (TIE, LATE, BOTH):
        assert (p.walk_end, p.flatten, p.breakeven) == (S2.walk_end, S2.flatten, S2.breakeven)
    with pytest.raises(ValueError):
        W.Rules("x", W.FLAT_ENTRY, "worst_less_two", True, breakeven_tie="maybe")
    with pytest.raises(ValueError):
        W.Rules("x", W.FLAT_ENTRY, "worst_less_two", True, breakeven_delay=-1)


def test_a_bar_touching_the_entry_and_trading_through_the_target():
    # (a): the 13:00 open 10 points in favour; bar 1250 touches the entry and trades through the target
    arr = mk({**ENTRY, OPEN: (20010.0, 20011.0, 20009.0, 20010.0), 1250: (20010.0, 20030.0, 19999.0, 20010.0)})
    assert walk(arr, S2) == (W.TARGET, 1250, 100)         # Stage 2's walk books the target
    assert walk(arr, TIE) == (W.BREAKEVEN, 1250, 0)       # the stop first
    assert walk(arr, LATE) == (W.TARGET, 1250, 100)
    assert walk(arr, BOTH) == (W.BREAKEVEN, 1250, 0)


def test_the_tie_for_a_short():
    arr = mk({**ENTRY, OPEN: (19990.0, 19991.0, 19989.0, 19990.0), 1250: (19990.0, 20001.0, 19970.0, 19990.0)})
    assert walk(arr, S2, -1) == (W.TARGET, 1250, 100)
    assert walk(arr, TIE, -1) == (W.BREAKEVEN, 1250, 0)


def test_a_touch_inside_the_five_minutes_does_not_exit_under_the_delay():
    # (b): bar 1203 touches the entry (not the stop) two minutes after the open; bar 1210 trades through the target
    arr = mk({**ENTRY, OPEN: (20010.0, 20011.0, 20009.0, 20010.0), 1203: (20010.0, 20011.0, 19999.0, 20010.0),
              1210: (20010.0, 20030.0, 20009.0, 20010.0)})
    assert walk(arr, S2) == (W.BREAKEVEN, 1203, 0)        # zero latency: out at the entry on 1203
    assert walk(arr, TIE) == (W.BREAKEVEN, 1203, 0)
    assert walk(arr, LATE) == (W.TARGET, 1210, 100)       # the move only from 1206: the trade runs on
    assert walk(arr, BOTH) == (W.TARGET, 1210, 100)


def test_the_original_stop_governs_until_the_move():
    # bar 1203 falls through the original stop: zero latency books it at the entry, the delayed move is too late
    arr = mk({**ENTRY, OPEN: (20010.0, 20011.0, 20009.0, 20010.0), 1203: (20010.0, 20011.0, 19970.0, 19980.0)})
    assert walk(arr, S2) == (W.BREAKEVEN, 1203, 0)
    assert walk(arr, LATE) == (W.STOP, 1203, -100)
    assert walk(arr, BOTH) == (W.STOP, 1203, -100)


def test_a_touch_after_the_move_exits_at_the_entry_in_every_variant():
    arr = mk({**ENTRY, OPEN: (20010.0, 20011.0, 20009.0, 20010.0), 1208: (20010.0, 20011.0, 19999.0, 20005.0)})
    for p in (S2, TIE, LATE, BOTH):
        assert walk(arr, p) == (W.BREAKEVEN, 1208, 0)


def test_both_corrections_together():
    # a touch inside the five minutes, then a bar touching the entry and trading through the target after the move
    arr = mk({**ENTRY, OPEN: (20010.0, 20011.0, 20009.0, 20010.0), 1203: (20010.0, 20011.0, 19999.0, 20010.0),
              1208: (20010.0, 20030.0, 19999.0, 20010.0)})
    assert walk(arr, S2) == (W.BREAKEVEN, 1203, 0)
    assert walk(arr, TIE) == (W.BREAKEVEN, 1203, 0)
    assert walk(arr, LATE) == (W.TARGET, 1208, 100)
    assert walk(arr, BOTH) == (W.BREAKEVEN, 1208, 0)


def test_an_open_not_in_favour_moves_nothing():
    arr = mk({**ENTRY, OPEN: (20000.0, 20001.0, 19999.0, 20000.0), 1250: (20000.0, 20030.0, 19999.0, 20000.0)})
    for p in (S2, TIE, LATE, BOTH):
        assert walk(arr, p) == (W.TARGET, 1250, 100)


def test_the_move_bar_is_the_first_present_bar_five_minutes_on():
    # bars 1206-1209 missing: under the delay the move is in force from 1210; a touch on 1205 does not count
    arr = list(mk({**ENTRY, OPEN: (20010.0, 20011.0, 20009.0, 20010.0), 1205: (20010.0, 20011.0, 19999.0, 20010.0),
                   1210: (20010.0, 20011.0, 19999.0, 20010.0)}))
    for x in arr:
        x[1206:1210] = np.nan
    assert walk(arr, S2) == (W.BREAKEVEN, 1205, 0)
    assert walk(arr, LATE) == (W.BREAKEVEN, 1210, 0)
