"""Q-213: `extended.design_trades` on synthetic bars -- RL3's base cell (fade at `pd`, 50 ticks, cutoff 14:30 CT) filled
and walked by the route the early look and the Wave 5 survey use, and the registered mode held to H4's I-5 builder
(`h4_coin_source.build_p16_i5_trades`) frame for frame on toy bars. Every bar here is invented; no store is read.

The toy days (`planted`): day 0 sets the prior range (a high of 18100, a low of 17900 in the regular session); day 1
trades a tick through the high at the bar stamped 10:00 (the sell limit fills there) and later a tick through the low
(the buy limit's fill is cancelled by the kind's one-cancels-other); day 2 trades through its levels inside the closed
window and after the 14:30 cutoff only (no fill); day 3 opens 09:00 beyond its high (void, already through) with its
low at the reference (void, at the reference). The overnight closes alternate by a tick so each alert has a volatility.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import design_trades as DT  # noqa: E402
from extended import h4_coin_source as CS  # noqa: E402
from extended import three_way_baseline as TB  # noqa: E402
from extended import trigger_sides as TS  # noqa: E402
from extended import triggers as T  # noqa: E402
from extended import walker as W  # noqa: E402

DAYS = ("2021-03-01", "2021-03-02", "2021-03-03", "2021-03-04")
BASE = 18000.0
CUTOFF = W.slot(14, 30)
RULE = {"hi": "fade", "lo": "fade"}


def _day() -> tuple[np.ndarray, ...]:
    o, h, l, c = (np.full(1441, np.nan) for _ in range(4))
    for j in range(1, W.C_FLAT + 1):
        o[j] = h[j] = l[j] = c[j] = BASE
    for j in range(1, T.RTH_OPEN):                         # overnight: closes alternate by a tick
        if j % 2:
            c[j] = h[j] = BASE + W.TICK
    return o, h, l, c


def planted() -> tuple[list[str], dict[str, tuple[np.ndarray, ...]]]:
    arrs = {d: _day() for d in DAYS}
    o, h, l, c = arrs[DAYS[0]]
    h[W.bar_of(10, 0)], l[W.bar_of(11, 0)] = 18100.0, 17900.0
    o, h, l, c = arrs[DAYS[1]]
    h[W.bar_of(10, 0)] = 18100.0 + W.TICK                  # a tick through the high: the sell limit fills
    l[W.bar_of(11, 0)] = 17900.0 - W.TICK                  # a tick through the low: cancelled by the OCO
    o, h, l, c = arrs[DAYS[2]]
    h[W.bar_of(8, 45)] = 18101.0                            # inside the closed window: no fill
    h[W.bar_of(14, 45)] = 18101.0                           # after the cutoff: no fill
    o, h, l, c = arrs[DAYS[3]]
    c[W.bar_of(8, 59)] = h[W.bar_of(8, 59)] = 18102.0       # the price at 09:00 is past the high: void
    return list(DAYS), arrs


def _build(spec=None, ctxs=None):
    days, arrs = planted()
    hist = DT.history_from_arrays(days, arrs)
    spec = spec or DT.rl3_spec("pd", CUTOFF, RULE, 50)
    ctxs = ctxs or {i: T.DayContext(i, d) for i, d in enumerate(days)}
    out = DT.build_trades(spec, hist, lambda i: ctxs[i], day_kinds={d: "n" for d in days}, rr_grid=CS.RR_GRID,
                          fresh_rr=1.5, fee_micro_eq=1.22, tick_value=0.5, market_entry_ticks=1.0)
    return days, hist, out


def test_the_base_cell_fills_once_at_the_high_and_counts_every_other_ticket():
    days, _, out = _build()
    t = out.trades
    assert len(t) == 1
    r = t.iloc[0]
    assert r["date"] == DAYS[1] and r["side"] == "short"                     # a fade sells at the resistance
    assert int(r["decision_slot_minutes"]) == T.RTH_OPEN                      # the alert: 08:30 CT
    assert int(r["entry_t"]) == W.bar_of(10, 0)                               # the bar trading a tick through
    assert int(r["S"]) == 50
    c = out.counts
    assert c["filled"] == 1 and c["oco_cancelled"] == 1
    assert c["unfilled"] == {"cancelled:cutoff": 2, "void:through": 1}
    assert c["refused"] == {"at_reference": 1, "no_prior_day": 2}
    assert c["entry_ticks"] == 0.0                                            # a resting fill pays no entry tick


def test_costs_are_stage2s_with_no_entry_tick_on_a_resting_fill():
    _, _, out = _build()
    r = out.trades.iloc[0]
    for R in CS.RR_GRID:
        k = {"t": W.TARGET, "s": W.STOP, "f": W.FLATTEN}[r[f"o_{R:g}"]]
        want = (0.0 * 0.5 + 1.22 + W.EXIT_TICKS[k] * 0.5) / (50 * 0.5)
        assert math.isclose(float(r[f"c_{R:g}"]), want, rel_tol=0, abs_tol=1e-12)


def test_no_move_bar_under_the_journey_walk_and_the_facts_follow():
    days, _, out = _build()
    a = out.aux.iloc[0]
    assert a["be_open"] is None or (isinstance(a["be_open"], float) and math.isnan(a["be_open"]))
    assert int(a["time_limit"]) == W.FLAT_ENTRY
    facts = DT.facts_for(out.trades, out.aux, days, tick_value=0.5, rr_cols=CS.RR_GRID, entry_ticks=0.0)
    f = facts[(1, 0)]
    assert f.be_open is None and not f.has_move and f.e_ticks == 0.0
    assert f.decision <= f.entry <= f.limit and f.sigma > 0


def test_the_side_is_the_designs_own_and_a_break_rule_is_another_trade():
    """A positive control: the same tickets under `break` fill as buy stops a tick above the high."""
    _, _, out = _build(DT.rl3_spec("pd", CUTOFF, {"hi": "break", "lo": "break"}, 50))
    assert out.trades.iloc[0]["side"] == "long"
    trig = T.RL3Tickets("pd", CUTOFF)
    off = T.Offer("rl3", 1, T.RTH_OPEN, 0, T.RTH_OPEN, T.LIVE_0900, T.TICKET, 18100.0, 1, tag="pd_hi")
    assert TS.trigger_side(trig, RULE, off).side == -1


def test_a_held_out_day_and_a_confirmation_day_refuse():
    days, arrs = planted()
    with pytest.raises(DT.DesignRefused, match="E-208"):
        DT.history_from_arrays(["2023-12-29", "2024-01-02"], {"2023-12-29": arrs[days[0]], "2024-01-02": arrs[days[1]]})
    with pytest.raises(DT.DesignRefused, match="confirmation"):
        DT.check_search_days(["2026-07-17"])
    DT.check_search_days(["2023-12-29"])


def test_a_spec_mixing_entry_kinds_refuses():
    spec = DT.rl3_spec("pd", CUTOFF, RULE, 50)
    bad = DT.DesignSpec("bad", spec.source, spec.side, 50, T.JOURNEY, "journey", True, "market")
    with pytest.raises(DT.DesignRefused, match="one entry kind"):
        _build(bad)


def test_a_news_window_cancels_the_working_ticket():
    days, arrs = planted()
    win = T.Window(W.slot(9, 30), W.slot(10, 30), "news", "toy")
    ctxs = {i: T.DayContext(i, d, windows=(win,) if i == 1 else ()) for i, d in enumerate(days)}
    _, _, out = _build(ctxs=ctxs)
    # the touch at 10:00 lies inside the window: no fill there; re-written after it, the low's touch at 11:00 fills
    assert len(out.trades) == 1 and out.trades.iloc[0]["side"] == "long"
    assert int(out.trades.iloc[0]["entry_t"]) == W.bar_of(11, 0)


# ------------------------------------------------------------------------------------------------ registered mode


def _tests_seed() -> int:
    """The early look's tests' role (`scripts/early_look.py`, the block's owner), never a literal here."""
    import importlib.util

    name = "early_look_for_design_trades"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / "early_look.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name].issue("el_tests")


def _toy_registered(n=6, seed_word=7):
    rng = np.random.default_rng(np.random.SeedSequence(_tests_seed(), spawn_key=(1, seed_word)))
    days = [f"2021-05-{k:02d}" for k in (3, 4, 5, 6, 7, 10)][:n]
    arrs = {}
    for d in days:
        steps = rng.integers(-4, 5, size=W.C_FLAT) * W.TICK
        c = 15000.0 + np.cumsum(steps)
        o = np.concatenate([[15000.0], c[:-1]])
        hi = np.maximum(o, c) + rng.integers(0, 3, size=W.C_FLAT) * W.TICK
        lo = np.minimum(o, c) - rng.integers(0, 3, size=W.C_FLAT) * W.TICK
        arr = [np.full(1441, np.nan) for _ in range(4)]
        for k, x in enumerate((o, hi, lo, c)):
            arr[k][1:W.C_FLAT + 1] = x
        arrs[d] = tuple(arr)
    kinds = {d: ("b" if i % 2 else "n") for i, d in enumerate(days)}
    marks = [0, 300, 865, 870, 875, 900, 1000, 1320]
    coins = {(d, m): int(rng.choice((-1, 1))) for d in days for m in marks}
    return days, arrs, kinds, marks, coins


def _registered_frames(report_clear=CS.RELEASE_CLEAR_SLOT):
    days, arrs, kinds, marks, coins = _toy_registered()
    hist = DT.history_from_arrays(days, arrs)
    spec = DT.registered_spec(marks, coins, 150, report_clear=report_clear)
    out = DT.build_trades(spec, hist, lambda i: T.DayContext(i, days[i], bls=kinds[days[i]] == "b"), day_kinds=kinds,
                          rr_grid=CS.RR_GRID, fresh_rr=1.5, fee_micro_eq=1.94, tick_value=0.5, market_entry_ticks=1.0)
    ddf = pd.DataFrame({"date": days, "day_kind": [kinds[d] for d in days]})
    ref = CS.build_p16_i5_trades(ddf, lambda d: arrs[d], marks, coins, fee_micro_eq=1.94, tick_value=0.5,
                                 entry_ticks=1.0, stop_ticks=150, rr_grid=CS.RR_GRID, fresh_rr=1.5)
    return out.trades.reset_index(drop=True), ref.reset_index(drop=True)


def test_the_registered_mode_is_i5s_builder_frame_for_frame():
    got, ref = _registered_frames()
    assert len(got) > 20
    pd.testing.assert_frame_equal(got, ref, check_exact=True)


def test_the_registered_comparison_can_fail():
    """A positive control: the report-day clear one mark earlier keeps a trade I-5's builder drops."""
    got, ref = _registered_frames(report_clear=CS.RELEASE_CLEAR_SLOT - 5)
    assert len(got) != len(ref)


def test_the_route_never_reads_a_file():
    src = (ROOT / "extended" / "design_trades.py").read_text(encoding="utf-8")
    for bad in ("read_parquet", "read_csv", "open(", "read_bars(", "read_text("):
        assert bad not in src, bad
