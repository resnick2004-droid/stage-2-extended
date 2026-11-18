"""Q-152: the trigger library (`extended/triggers.py`) on synthetic data only -- never a real bar.

What is held:
* the declared parameters are the lever table's (`lever_space.DECLARED`), the clock's slots the walker's;
* P-14's breakout timing is Stage 2's `brk` pattern at k = 30, event for event, against the vendored
  `propedge/outcomes/atlas_core.py` (run in a child process: nothing vendored on this runner's path);
* **shift-invariance for every bar-reading source** (feature-rules section 2): every bar stamped at or after a cut is
  replaced (a seeded random walk) or deleted, and every offer whose alert is at or before the cut -- its moment, its
  level, its void -- is unchanged; cuts on a roll day, the first day after a DST change and an ordinary day, at the
  session's first minutes and later, plus seeded random cuts; the harness catches a source that reads its alert's bar;
* each news and window rule: a live slot inside a window refused, an alert inside with live after kept, a working
  order cancelled at a window's start, an open position flattened there, RL3's re-write after a window, an unscheduled
  release from its minute, the closed 08:30-08:59 window, the BLS 07:35:00 rule, FOMC and calendar voids;
* the latency: a market entry at the open of the bar stamped alert + L, a limit never filling before alert + L, the
  latency-free sources meeting every declared L;
* the limit trade-through (a touch is no fill; a tick through fills at the limit; an open through fills at the limit,
  never better; marketable at live is void);
* RL3's levels against a direct timestamp-filtered reference, its voids, and E-204's same-bar pair (the fade limit and
  the break stop of one ticket fill on the same bar, the void boundary the only exception);
* the overnight guard (refused until H2's row exists);
* the coin key's fields (the design note's choice 3): the layout of `three_way_arith.seed_key`, the start carried, no
  account or firm, every word below 2^32, one underlying for MNQ and NQ, the symmetric grid, distinct states.

Seeds fixed for this file (the test's own, used nowhere else): 20261520 (the synthetic series), 20261521 (the random
cuts), 20261522 (the replacement walks; each cut a child stream `SeedSequence(20261522, spawn_key=(i,))`), 20261523
(the coin unit's role seed in these tests).
"""
from __future__ import annotations

import importlib.util
import inspect
import json
import math
import subprocess
import sys
from dataclasses import fields
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from extended import lever_space as LS
from extended import synthetic_bars as sb
from extended import triggers as T
from extended import walker as W

ROOT = Path(__file__).resolve().parent.parent
SEED_SERIES, SEED_CUTS, SEED_REPLACE, SEED_COIN = 20261520, 20261521, 20261522, 20261523
FIXED_DAYS = ("2021-03-12", "2021-03-15", "2021-03-24")        # the roll (NQH1 -> NQM1), after DST, ordinary
FIXED_TIMES = ((17, 0), (8, 29), (8, 30), (8, 31), (9, 0), (9, 5), (12, 0), (14, 0))
ARITH = ROOT / "docs" / "plans" / "scripts" / "three_way" / "three_way_arith.py"
ATLAS_CORE = ROOT / "vendor" / "stage2" / "propedge" / "outcomes" / "atlas_core.py"
P = 13000.0
TK = T.TICK


# ------------------------------------------------------------------------------------------------ fixtures and helpers


@pytest.fixture(scope="module")
def bars() -> pd.DataFrame:
    return sb.generate(sb.Spec(date(2021, 2, 22), date(2021, 3, 26), seed=SEED_SERIES))


@pytest.fixture(scope="module")
def hist(bars) -> T.History:
    return T.History.from_bars(bars)


def ctx_of(hist: T.History, i: int, **kw) -> T.DayContext:
    return T.DayContext(i, hist.days[i], **kw)


def flat_day(price: float = P) -> list[np.ndarray]:
    """A day in the walker's layout with every bar present at one price (index 0 unused)."""
    a = np.full(1441, price)
    a[0] = np.nan
    return [a.copy(), a.copy(), a.copy(), a.copy()]


def set_bar(day: list[np.ndarray], stamped: int, o: float, h: float, lo: float, c: float) -> None:
    j = int(stamped) + 1
    day[0][j], day[1][j], day[2][j], day[3][j] = o, h, lo, c


def one_day(day: list[np.ndarray], when: str = "2021-03-03", contract: str = "NQH1") -> T.History:
    return T.History.from_arrays([when], [contract], *[x[None, :] for x in day])


def two_days(prev: list[np.ndarray], day: list[np.ndarray], contracts=("NQH1", "NQH1")) -> T.History:
    return T.History.from_arrays(["2021-03-02", "2021-03-03"], list(contracts),
                                 *[np.stack([a, b]) for a, b in zip(prev, day)])


def hand_offer(live: int, *, alert: int | None = None, entry: str = T.MARKET, level: float = float("nan"),
               expires: int | None = None, session: int = 0, decision: int | None = None, sub: int = 0,
               source: str = "p16") -> T.Offer:
    a = live - T.REFERENCE_L if alert is None else alert
    return T.Offer(source, session, a if decision is None else decision, sub, a, live, entry, level,
                   expires=expires)


def key(o: T.Offer) -> tuple:
    """An offer as a comparable tuple (NaN as a sentinel)."""
    lv = o.level if math.isfinite(o.level) else "nan"
    return (o.source, o.session, o.decision, o.sub, o.alert, o.live, o.entry, lv, o.role, o.expires, o.group,
            o.rewrite, o.tag, o.void)


def sources() -> dict[str, object]:
    return {
        "p14_market": T.P14Breakout(latency=5),
        "p14_limit_L2": T.P14Breakout(latency=2, entry=T.LIMIT),
        "p16_limit": T.P16Marks(T.p16_grid(T.RTH_OPEN), entry=T.LIMIT),
        **{f"rl3_{k}": T.RL3Tickets(k, T.RL3_CUTOFFS[-1]) for k in T.RL3_KINDS},
    }


# ------------------------------------------------------------------------------------------------ declared parameters


def test_parameters_are_the_lever_tables_and_the_walkers():
    assert T.LATENCIES == tuple(LS.declared("latency")) == (5, 3, 2)
    assert T.REFERENCE_L == LS.declared("latency.reference") == T.LATENCIES[0]
    assert T.LIMIT_WINDOW == LS.declared("limit_window_min")
    assert T.MARK_STEP == LS.declared("mark_step_min")
    assert T.ENTRIES == ("market", "limit")
    assert (T.CLOSED_FIRST, T.CLOSED_LAST) == (W.slot(8, 30), W.slot(8, 59)) == (930, 959)
    assert T.BLS_CLEAR == W.slot(7, 35) == 875
    assert T.LIVE_0900 == 960 and T.P14_LAST == 1260 and T.SESSION_END == W.C_FLAT
    assert T.RL3_CUTOFFS == tuple(range(W.slot(10, 0), W.slot(14, 30) + 1, 30))
    assert T.JOURNEY.walk_end == W.FLAT_ENTRY and T.JOURNEY.flatten == "worst_less_two" and not T.JOURNEY.breakeven
    for s in T.SOURCES:
        assert s in LS.declared("sources")
    assert LS.latency_cells("p16") == LS.latency_cells("rl3") == (None,)


# ------------------------------------------------------------------------------------------------ P-14 against Stage 2

CHILD = r"""
import importlib.util, json, sys
from datetime import date
import numpy as np
sys.path.insert(0, sys.argv[1])
from extended import synthetic_bars as sb, triggers as T
spec = importlib.util.spec_from_file_location("atlas_core_vendored", sys.argv[2])
A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
H = T.History.from_bars(sb.generate(sb.Spec(date(2021, 2, 22), date(2021, 3, 26), seed=int(sys.argv[3]))))
P = {"patterns": [{"kind": "brk", "k": 30}], "first_slot": 0, "last_slot": 1260}
out = {}
for i, d in enumerate(H.days):
    arrs = [[None if np.isnan(v) else float(v) for v in x] for x in H.day(i)]
    out[d] = [[int(t), int(s)] for _, t, s in A.a_events(*arrs, P)]
print(json.dumps(out))
"""


def test_p14_breakout_events_are_stage2s(hist):
    r = subprocess.run([sys.executable, "-c", CHILD, str(ROOT), str(ATLAS_CORE), str(SEED_SERIES)],
                       capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    assert r.returncode == 0, r.stderr[-3000:]
    ref = json.loads(r.stdout.strip().splitlines()[-1])
    n = 0
    for i, d in enumerate(hist.days):
        o, h, l, c = hist.day(i)
        mine = [[j, s] for j, s in T.breakout_events(c, o, h, l, 30, 0, 1260)]
        assert mine == ref[d], d
        n += len(mine)
    assert n > 20 * len(hist.days)                        # dozens of events a day: the comparison bites


def test_p14_offers_carry_no_side_and_one_moment_each(hist):
    src = T.P14Breakout(latency=3)
    for i in range(len(hist)):
        offs = src.offers(hist, i, ctx_of(hist, i))
        assert all(o.alert >= T.RTH_OPEN and o.alert <= T.P14_LAST for o in offs)
        assert len({o.decision for o in offs}) == len(offs)
        assert all(o.live == o.alert + 3 and o.decision == o.alert and o.sub == 0 for o in offs)
        assert not any(hasattr(o, "side") for o in offs)


# ------------------------------------------------------------------------------------------------ shift-invariance


def offers_by_day(hist: T.History, src) -> dict[str, list[T.Offer]]:
    return {d: src.offers(hist, i, ctx_of(hist, i)) for i, d in enumerate(hist.days)}


def violations(before: dict, after: dict, cut_day: str, cut_slot: int) -> tuple[list, int]:
    """Offers of days before the cut's day, and of the cut's day with alert <= the cut's slot, that differ."""
    bad, n = [], 0
    for d, offs in before.items():
        if d > cut_day:
            continue
        a = [key(o) for o in offs if d < cut_day or o.alert <= cut_slot]
        if d not in after:
            assert d == cut_day and not a, "a deleted day had offers known before the cut"
            continue
        b = [key(o) for o in after[d] if d < cut_day or o.alert <= cut_slot]
        n += len(a)
        if a != b:
            bad.append((d, a[:2], b[:2]))
    return bad, n


def cut_list(hist: T.History) -> list[tuple[str, int, int]]:
    """(day, slot, ts) of every cut: the fixed days and times and eight seeded random (day, five-minute slot) cuts."""
    out = [(d, W.slot(h, m), sb.ts_of(d, h, m)) for d in FIXED_DAYS for h, m in FIXED_TIMES]
    rng = np.random.default_rng(SEED_CUTS)
    days = [d for d in hist.days if d >= "2021-03-01"]
    for d, s in zip(rng.choice(days, 8), rng.choice(np.arange(T.RTH_OPEN, T.P14_LAST, 5), 8)):
        hh, mm = divmod((int(s) + 17 * 60) % 1440, 60)
        out.append((str(d), int(s), sb.ts_of(str(d), hh, mm)))
    return out


@pytest.mark.parametrize("mode", ["replace", "delete"])
def test_every_bar_reading_source_is_shift_invariant(bars, hist, mode):
    srcs = sources()
    base = {name: offers_by_day(hist, s) for name, s in srcs.items()}
    compared = {name: 0 for name in srcs}
    for k, (d, s, ts) in enumerate(cut_list(hist)):
        if mode == "replace":
            seed = int(np.random.SeedSequence(SEED_REPLACE, spawn_key=(k,)).generate_state(1)[0])
            b2 = sb.replace_from(bars, ts, seed)
        else:
            b2 = bars[bars["ts"] < ts].reset_index(drop=True)
        h2 = T.History.from_bars(b2)
        for name, src in srcs.items():
            bad, n = violations(base[name], offers_by_day(h2, src), d, s)
            assert not bad, (mode, name, d, s, bad[:1])
            compared[name] += n
    for name, n in compared.items():
        assert n > 0, f"{name}: nothing compared"
    levels = [o.level for name in srcs if name != "p14_market" for offs in base[name].values() for o in offs
              if math.isfinite(o.level)]
    assert len(set(levels)) > 50                                   # levels are not constant, not all NaN


def test_harness_catches_a_source_reading_its_alerts_bar(bars, hist):
    class Leaky:
        """Every five minutes, a limit level read from the bar stamped AT its alert (index alert + 1): one too late."""
        source = "p16"

        def offers(self, h, i, ctx):
            o, hh, l, c = h.day(i)
            return [T.Offer("p16", ctx.session, a + 5, 0, a, a + 5, T.LIMIT, float(c[a + 1]), tag="leak")
                    for a in range(T.RTH_OPEN, T.P14_LAST, 5) if not math.isnan(c[a + 1])]

    base = offers_by_day(hist, Leaky())
    found = 0
    for k, (d, s, ts) in enumerate(cut_list(hist)):
        seed = int(np.random.SeedSequence(SEED_REPLACE, spawn_key=(k,)).generate_state(1)[0])
        bad, _ = violations(base, offers_by_day(T.History.from_bars(sb.replace_from(bars, ts, seed)), Leaky()), d, s)
        found += len(bad)
    assert found > 0


# ------------------------------------------------------------------------------------------------ the latency


@pytest.mark.parametrize("L", [5, 3, 2])
def test_p14_market_fills_at_the_open_of_the_bar_stamped_alert_plus_L(hist, L):
    src = T.P14Breakout(latency=L)
    n = 0
    for i in range(len(hist)):
        ctx = ctx_of(hist, i)
        kept, _ = T.admit(src.offers(hist, i, ctx), ctx)
        o = hist.o[i]
        for off in kept[:6]:
            ex = T.execute(off, 1, hist, i, ctx, 100, 1.0)
            want = next(j for j in range(off.alert + L + 1, len(o)) if not np.isnan(o[j]))
            assert ex.trade.fill.bar == want and ex.trade.fill.price == o[want]
            assert ex.fill_slot >= off.alert + L
            n += 1
    assert n > 50


def test_a_limit_never_fills_before_alert_plus_L():
    for L in T.LATENCIES:
        day = flat_day()
        alert = 1000
        for s in range(alert, alert + L):                         # through the level before live: must not fill
            set_bar(day, s, P, P, P - 4 * TK, P)
        h = one_day(day)
        off = hand_offer(alert + L, alert=alert, entry=T.LIMIT, level=P, expires=alert + L + T.LIMIT_WINDOW - 1)
        ex = T.execute(off, 1, h, 0, T.DayContext(0, h.days[0]), 50, 1.0)
        assert ex.trade.fill.status == "void"                  # at live the price is at the level: marketable, void
        day2 = flat_day(P + 2 * TK)
        for s in range(alert, alert + L):
            set_bar(day2, s, P + 2 * TK, P + 2 * TK, P - 4 * TK, P + 2 * TK)
        set_bar(day2, alert + L + 3, P + 2 * TK, P + 2 * TK, P - TK, P)
        ex2 = T.execute(off, 1, one_day(day2), 0, T.DayContext(0, "2021-03-03"), 50, 1.0)
        assert ex2.trade.fill.status == "filled" and ex2.fill_slot == alert + L + 3 and ex2.trade.fill.price == P


def test_latency_free_sources_meet_every_declared_L(hist):
    p16 = T.P16Marks(T.p16_grid(T.RTH_OPEN))
    rl3 = T.RL3Tickets("rn100", T.RL3_CUTOFFS[0])
    for i in range(len(hist)):
        ctx = ctx_of(hist, i)
        for off in p16.offers(hist, i, ctx):
            assert off.live == off.decision and off.alert == off.live - 5
            for L in T.LATENCIES:
                T.check_latency(off, L)
        for off in rl3.offers(hist, i, ctx):
            assert (off.alert, off.live, off.decision) == (930, 960, 930)
            for L in T.LATENCIES:
                T.check_latency(off, L)
    for bad in (lambda: T.P16Marks((960,), latency=5), lambda: T.RL3Tickets("pd", 1020, latency=3),
                lambda: T.P14Breakout(latency=4), lambda: T.P14Breakout(latency=None),
                lambda: T.P14Breakout(entry="stop")):
        with pytest.raises(T.TriggerRefused):
            bad()
    with pytest.raises(T.TriggerRefused):
        T.check_latency(hand_offer(1002, alert=1000), 3)


# ------------------------------------------------------------------------------------------------ the limit trade-through


@pytest.mark.parametrize("side", [1, -1])
def test_limit_fills_only_on_a_trade_through_at_its_price(side):
    alert, live = 1000, 1005
    lvl = P

    def run(build) -> W.Fill:
        day = flat_day(P + side * 2 * TK)                       # resting on the far side: not marketable at live
        build(day)
        h = one_day(day)
        off = hand_offer(live, alert=alert, entry=T.LIMIT, level=lvl, expires=live + T.LIMIT_WINDOW - 1)
        return T.execute(off, side, h, 0, T.DayContext(0, h.days[0]), 50, 1.0).trade.fill

    away = P + side * 2 * TK
    touch = run(lambda d: set_bar(d, live + 2, away, max(away, lvl), min(away, lvl), away))
    assert touch.status == "cancelled" and touch.touch_bar == live + 3          # a touch is not a fill
    thru = run(lambda d: set_bar(d, live + 2, away, max(away, lvl - side * TK), min(away, lvl - side * TK), away))
    assert thru.status == "filled" and thru.bar == live + 3 and thru.price == lvl
    gap = lvl - side * 3 * TK
    opened = run(lambda d: set_bar(d, live + 2, gap, max(gap, gap + TK), min(gap, gap - TK), gap))
    assert opened.status == "filled" and opened.price == lvl                    # never better than the limit
    day = flat_day(P - side * TK)                                              # marketable at live: void
    h = one_day(day)
    off = hand_offer(live, alert=alert, entry=T.LIMIT, level=lvl, expires=live + 29)
    assert T.execute(off, side, h, 0, T.DayContext(0, h.days[0]), 50, 1.0).trade.fill.status == "void"


def test_timed_limit_levels_are_the_price_at_the_alert(hist):
    src = T.P14Breakout(latency=3, entry=T.LIMIT)
    n = 0
    for i in range(len(hist)):
        o, _, _, c = hist.day(i)
        for off in src.offers(hist, i, ctx_of(hist, i)):
            assert off.level == W.price_at(o, c, off.alert) and off.expires == off.live + T.LIMIT_WINDOW - 1
            n += 1
    assert n > 100


# ------------------------------------------------------------------------------------------------ RL3's levels and pair


def ct_minutes(ts: pd.Series) -> np.ndarray:
    t = pd.to_datetime(ts, unit="s", utc=True).dt.tz_convert("America/Chicago")
    return (t.dt.hour * 60 + t.dt.minute).to_numpy()


def test_rl3_levels_match_a_timestamp_reference(bars, hist):
    m = ct_minutes(bars["ts"])
    for i in range(1, len(hist)):
        d, pd_ = hist.days[i], hist.days[i - 1]
        today = bars[bars["day"] == d]
        mt = m[bars["day"].to_numpy() == d]
        prev = bars[bars["day"] == pd_]
        mp = m[bars["day"].to_numpy() == pd_]
        ref_row = today[mt == 8 * 60 + 29]
        p_ref, lv = T.rl3_levels(hist, i, "on")
        if ref_row.empty:
            assert all(v[3] == "no_ref_bar" for v in lv)
            continue
        assert p_ref == float(ref_row["close"].iloc[0])
        on = today[(mt >= 17 * 60) | (mt < 8 * 60 + 30)]
        assert [(n, x, r) for n, x, r, _ in lv] == [("hi", on["high"].max(), 1), ("lo", on["low"].min(), -1)]
        rth = prev[(mp >= 8 * 60 + 30) & (mp < 15 * 60)]
        _, lp = T.rl3_levels(hist, i, "pd")
        _, lc = T.rl3_levels(hist, i, "pdc")
        if hist.contract[i] != hist.contract[i - 1]:
            assert {v[3] for v in lp + lc} == {"roll"}
            continue
        for (n, x, r, why), want in zip(lp, (rth["high"].max(), rth["low"].min())):
            assert x == want
            assert (why, r) == (("at_reference", 0) if x == p_ref else ("", 1 if x > p_ref else -1))
        last = prev[mp == 14 * 60 + 59]
        if last.empty:
            assert lc[0][3] == "no_prior_close"
        else:
            assert lc[0][1] == float(last["close"].iloc[0])
        _, lr = T.rl3_levels(hist, i, "rn100")
        exact = p_ref % 100 == 0
        up = p_ref + 100 if exact else math.ceil(p_ref / 100) * 100
        dn = p_ref - 100 if exact else math.floor(p_ref / 100) * 100
        assert lr[0][1] == up and lr[1][1] == dn
        assert lr[0][2] == 1 and lr[1][2] == -1
    _, first = T.rl3_levels(hist, 0, "pd")
    assert {v[3] for v in first} == {"first_day"}
    _, pv = T.rl3_levels(hist, 5, "pdc", prior_void=True)
    assert pv[0][3] == "prior_void" or pv[0][3] == "roll"


def test_rl3_voids_at_the_reference_and_without_the_0829_bar():
    prev, day = flat_day(13050.0), flat_day(13050.0)
    set_bar(prev, W.slot(9, 0), 13050.0, 13100.0, 13000.0, 13050.0)
    set_bar(day, W.slot(8, 29), 13000.0, 13000.0, 13000.0, 13000.0)          # P_ref 13000: on a round number
    h = two_days(prev, day)
    _, lr = T.rl3_levels(h, 1, "rn100")
    assert [(n, x, r, w) for n, x, r, w in lr] == [("up", 13100.0, 1, ""), ("dn", 12900.0, -1, "")]
    _, lp = T.rl3_levels(h, 1, "pd")
    assert [w for *_, w in lp] == ["", "at_reference"]                     # the low equals P_ref: void
    for k in range(1, T.RTH_OPEN + 1):                                         # on: high and low at P_ref, kept
        for a in day:
            a[k] = 13000.0
    _, lo = T.rl3_levels(two_days(prev, day), 1, "on")
    assert [(r, w) for _, _, r, w in lo] == [(1, ""), (-1, "")]
    for a in day:
        a[T.RTH_OPEN] = np.nan                                                  # no bar stamped 08:29
    for kind in T.RL3_KINDS:
        _, lv = T.rl3_levels(two_days(prev, day), 1, kind)
        assert {w for *_, w in lv} == {"no_ref_bar"}
    _, lroll = T.rl3_levels(two_days(prev, flat_day(), ("NQH1", "NQM1")), 1, "pdc")
    assert lroll[0][3] == "roll"


def test_rl3_fade_and_break_fill_on_the_same_bar(hist):
    pairs = boundary = filled = 0
    for kind in T.RL3_KINDS:
        src = T.RL3Tickets(kind, T.RL3_CUTOFFS[-1])
        for i in range(len(hist)):
            ctx = ctx_of(hist, i)
            kept, _ = T.admit(src.offers(hist, i, ctx), ctx)
            o, _, _, c = hist.day(i)
            for off in kept:
                ex = {s: T.execute(off, s, hist, i, ctx, 100, 1.0) for s in (1, -1)}
                kinds = {s: e.order_kind for s, e in ex.items()}
                assert set(kinds.values()) == {W.LIMIT_ENTRY, W.STOP_ENTRY}    # one fade, one break
                st = {s: e.trade.fill.status for s, e in ex.items()}
                if list(st.values()).count("void") == 1:
                    assert W.price_at(o, c, T.LIVE_0900) == off.level           # the void boundary, countable
                    boundary += 1
                    continue
                pairs += 1
                assert st[1] == st[-1]
                if st[1] == "filled":
                    assert ex[1].trade.fill.bar == ex[-1].trade.fill.bar
                    filled += 1
    assert pairs > 30 and filled > 15
    assert boundary >= 0


def test_order_for_maps_the_coin_to_fade_or_break():
    res = T.Offer("rl3", 0, 930, 0, 930, 960, T.TICKET, 13100.0, 1, expires=1019, group="g", rewrite=True)
    sup = replace_role(res, -1)
    assert T.order_for(res, 1) == (W.STOP_ENTRY, 13100.0 + TK)                  # break: buy stop a tick above
    assert T.order_for(res, -1) == (W.LIMIT_ENTRY, 13100.0)                    # fade: sell limit at the level
    assert T.order_for(sup, -1) == (W.STOP_ENTRY, 13100.0 - TK)                # break: sell stop a tick below
    assert T.order_for(sup, 1) == (W.LIMIT_ENTRY, 13100.0)                     # fade: buy limit at the level
    assert T.order_for(hand_offer(1000), -1) == (W.MARKET, None)


def replace_role(off: T.Offer, role: int) -> T.Offer:
    from dataclasses import replace
    return replace(off, role=role)


# ------------------------------------------------------------------------------------------------ the news and window rules


def test_news_window_refuses_a_live_inside_and_keeps_an_alert_inside():
    w = T.Window(1000, 1010, "news", "test")
    ctx = T.DayContext(0, "2021-03-03", windows=(w,))
    inside = hand_offer(1005, alert=1000)
    after = hand_offer(1012, alert=1007)                                       # the alert inside, live after
    before = hand_offer(995, alert=990)
    kept, refused = T.admit([inside, after, before], ctx)
    assert kept == [after, before] and refused == [(inside, "news")]
    assert T.segments(before, ctx) == [(995, 999)]                             # cancelled at the window's start
    assert T.segments(after, ctx) == [(1012, None)]


def test_a_working_limit_is_cancelled_at_a_windows_start():
    day = flat_day(P + 2 * TK)
    set_bar(day, 1003, P + 2 * TK, P + 2 * TK, P - 4 * TK, P)                 # through the level inside the window
    h = one_day(day)
    w = T.Window(1000, 1010, "news")
    ctx = T.DayContext(0, h.days[0], windows=(w,))
    off = hand_offer(990, alert=985, entry=T.LIMIT, level=P, expires=990 + 29)
    ex = T.execute(off, 1, h, 0, ctx, 50, 1.0)
    assert ex.trade.fill.status == "cancelled" and ex.trade.order.cutoff == w.first
    no_window = T.execute(off, 1, h, 0, T.DayContext(0, h.days[0]), 50, 1.0)
    assert no_window.trade.fill.status == "filled" and no_window.fill_slot == 1003     # the window did the cancelling


def test_an_open_position_is_flattened_at_a_windows_start():
    day = flat_day()
    for s in range(1010, 1439):                                                # three ticks up: no barrier reached
        set_bar(day, s, P + 3 * TK, P + 3 * TK, P + 3 * TK, P + 3 * TK)
    h = one_day(day)
    w = T.Window(1020, 1030, "news")
    ctx = T.DayContext(0, h.days[0], windows=(w,))
    off = hand_offer(995, alert=990)
    ex = T.execute(off, 1, h, 0, ctx, 200, 3.0)
    tr = ex.trade
    assert ex.rules.walk_end == w.first and ex.rules.flatten == "close"
    assert tr.rule.kind[0] == W.FLATTEN and ex.exit_slot == w.first
    assert tr.fill.price == P and tr.rule.gross[0] == 3                       # closed at the price at the start
    assert ex.rules.walk_end < T.JOURNEY.walk_end


def test_an_unscheduled_release_cancels_from_its_minute_and_flattens_after_it():
    r = 1100
    w = T.Window(r, r + 5, "unscheduled", "an unscheduled FOMC statement")
    ctx = T.DayContext(0, "2021-03-03", windows=(w,))
    day = flat_day(P + 2 * TK)
    set_bar(day, r, P + 2 * TK, P + 2 * TK, P - 4 * TK, P)                    # through on the release bar itself
    h = one_day(day)
    off = hand_offer(1090, alert=1085, entry=T.LIMIT, level=P, expires=1119)
    assert T.execute(off, 1, h, 0, ctx, 50, 1.0).trade.fill.status == "cancelled"
    m = T.execute(hand_offer(1050, alert=1045), 1, one_day(flat_day()), 0, ctx, 200, 3.0)
    assert m.exit_slot == r + 1 and m.trade.rule.kind[0] == W.FLATTEN       # the first bar after the release minute
    tkt = T.Offer("rl3", 0, 930, 0, 930, 960, T.TICKET, P, -1, expires=1199, group="g", rewrite=True)
    assert T.segments(tkt, ctx) == [(960, r - 1)]                              # no re-write after an unscheduled release


def test_rl3_tickets_are_rewritten_after_a_window_and_void_if_through():
    w = T.Window(1000, 1010, "news")
    ctx = T.DayContext(0, "2021-03-03", windows=(w,))
    tkt = T.Offer("rl3", 0, 930, 1, 930, 960, T.TICKET, P, -1, expires=1199, group="g", rewrite=True)
    assert T.segments(tkt, ctx) == [(960, 999), (1011, 1199)]
    day = flat_day(P + 2 * TK)
    set_bar(day, 1005, P + 2 * TK, P + 2 * TK, P - 4 * TK, P + 2 * TK)         # through inside the window: nothing
    set_bar(day, 1020, P + 2 * TK, P + 2 * TK, P - TK, P + 2 * TK)             # through after it: the fade fills
    ex = T.execute(tkt, 1, one_day(day), 0, ctx, 100, 1.0)
    assert ex.order_kind == W.LIMIT_ENTRY and len(ex.attempts) == 2
    assert ex.attempts[0].fill.status == "cancelled" and ex.filled and ex.fill_slot == 1020
    day2 = flat_day(P + 2 * TK)
    set_bar(day2, 1005, P + 2 * TK, P + 2 * TK, P - 4 * TK, P - 2 * TK)        # the window ends with the price through
    for s in range(1006, 1440):
        set_bar(day2, s, P - 2 * TK, P - 2 * TK, P - 2 * TK, P - 2 * TK)
    ex2 = T.execute(tkt, 1, one_day(day2), 0, ctx, 100, 1.0)
    assert ex2.trade.fill.status == "void" and ex2.trade.order.live == 1011
    kept, _ = T.admit([tkt], T.DayContext(0, "2021-03-03", windows=(T.Window(950, 1199, "news"),)))
    assert kept == []                                                          # nothing of its stretch remains


def test_the_closed_0830_0859_window_for_every_source(hist):
    p16 = T.P16Marks(T.p16_grid(T.RTH_OPEN, 1000))
    p14 = T.P14Breakout(latency=2)
    for i in range(len(hist)):
        ctx = ctx_of(hist, i)
        kept, refused = T.admit(p16.offers(hist, i, ctx), ctx)
        assert sorted(o.live for o, r in refused if r == "closed") == list(range(930, 960, 5))
        assert [o.live for o in kept] == list(range(960, 1000, 5))
        kp, rp = T.admit(p14.offers(hist, i, ctx), ctx)
        assert all(r == "closed" and T.CLOSED_FIRST <= o.live <= T.CLOSED_LAST for o, r in rp)
        assert all(not T.CLOSED_FIRST <= o.live <= T.CLOSED_LAST for o in kp)
        r3 = T.RL3Tickets("rn100", T.RL3_CUTOFFS[0])
        assert all(T.segments(o, ctx)[0][0] == 960 for o in T.admit(r3.offers(hist, i, ctx), ctx)[0])


def test_a_position_open_at_0830_is_flattened_there(monkeypatch):
    monkeypatch.setattr(T, "overnight_allowed", lambda: True)
    off = hand_offer(900, alert=895)
    ctx = T.DayContext(0, "2021-03-03")
    kept, _ = T.admit([off], ctx)
    assert kept == [off]
    ex = T.execute(off, -1, one_day(flat_day()), 0, ctx, 200, 3.0)
    assert ex.exit_slot == T.CLOSED_FIRST and ex.trade.rule.kind[0] == W.FLATTEN


def test_bls_days_have_no_entry_at_or_before_0735(monkeypatch):
    monkeypatch.setattr(T, "overnight_allowed", lambda: True)
    at, after = hand_offer(T.BLS_CLEAR, alert=T.BLS_CLEAR - 5), hand_offer(T.BLS_CLEAR + 1, alert=T.BLS_CLEAR - 4)
    early = hand_offer(300, alert=295)
    bls = T.DayContext(0, "2021-03-05", bls=True)
    kept, refused = T.admit([early, at, after], bls)
    assert kept == [after] and refused == [(early, "bls"), (at, "bls")]
    ex = T.execute(after, 1, one_day(flat_day()), 0, bls, 50, 1.0)
    assert ex.fill_slot == W.slot(7, 36)                                       # the open of the bar stamped 07:36
    kept2, _ = T.admit([early, at, after], T.DayContext(0, "2021-03-04"))
    assert kept2 == [early, at, after]
    lim = hand_offer(T.BLS_CLEAR - 20, alert=T.BLS_CLEAR - 25, entry=T.LIMIT, level=P, expires=T.BLS_CLEAR + 9)
    assert T.admit([lim], bls)[1] == [(lim, "bls")]                            # a limit working before 07:36: refused


def test_fomc_and_calendar_voids_carry_no_offer(hist):
    offs = T.P14Breakout().offers(hist, 3, ctx_of(hist, 3))
    assert offs
    for flag, why in (("fomc", "fomc"), ("void", "calendar")):
        kept, refused = T.admit(offs, ctx_of(hist, 3, **{flag: True}))
        assert kept == [] and {r for _, r in refused} == {why}


def test_windows_are_checked_and_built_from_release_minutes():
    w = T.release_window(1000, 2, 3, "mffu.news_tier1_rule")
    assert (w.first, w.last, w.kind) == (998, 1003, "news")
    for bad in (lambda: T.Window(5, 4), lambda: T.Window(0, 1440), lambda: T.Window(1, 2, "lunch")):
        with pytest.raises(ValueError):
            bad()
    ctx = T.DayContext(0, "2021-03-05", bls=True, windows=(w,))
    assert [x.kind for x in ctx.all_windows()] == ["bls", "closed", "news"]


# ------------------------------------------------------------------------------------------------ the overnight guard


def test_overnight_triggers_wait_for_h2s_row(hist, monkeypatch):
    assert T.H2_ROW is None and not T.overnight_allowed()
    with pytest.raises(T.OvernightRefused):
        T.P16Marks(T.p16_grid(5, T.RTH_OPEN), overnight=True)
    with pytest.raises(T.OvernightRefused):
        T.P14Breakout(first=0)
    with pytest.raises(T.TriggerRefused):
        T.P16Marks((900, 905))                                                 # overnight marks as day marks
    kept, refused = T.admit([hand_offer(600)], T.DayContext(0, "2021-03-03"))
    assert kept == [] and refused[0][1] == "overnight"
    monkeypatch.setattr(T, "H2_ROW", "E-999")
    assert not T.overnight_allowed()                                           # a row the log does not hold
    monkeypatch.setattr(T, "decision_rows", lambda: frozenset({"E-999"}))
    assert T.overnight_allowed()
    src = T.P16Marks(T.p16_grid(5, T.RTH_OPEN), overnight=True)
    assert src.offers(hist, 2, ctx_of(hist, 2))[0].alert == 0


# ------------------------------------------------------------------------------------------------ the coin key


def arith():
    spec = importlib.util.spec_from_file_location("three_way_arith_q152", ARITH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_coin_key_is_the_design_notes_layout():
    A = arith()
    assert A.KEY_KINDS["coin"] == (T.COIN_TAG, T.COIN_FIELDS) and A.WORD == T.WORD
    rng = np.random.default_rng(SEED_COIN)
    for _ in range(200):
        part, hist_, si, start, sess, dec, sub = (int(x) for x in rng.integers(0, [9, 9, 64, 1700, 1700, 1440, 16]))
        unit = T.CoinUnit(SEED_COIN, part, hist_, si, start)
        off = hand_offer(dec, alert=dec, session=sess, decision=dec, sub=sub)
        k = T.coin_key(unit, off)
        assert k == A.seed_key(SEED_COIN, "coin", part=part, history=hist_, seed_index=si, start=start,
                               underlying=1, moment=(sess * 1440 + dec) * 16 + sub, draw_kind=T.DRAW_SIDE)
        assert len(k) == 9 and k[1] == 3 and k[5] == start and all(0 <= w < 2 ** 32 for w in k)


def test_coin_key_carries_the_start_and_no_account_or_firm():
    assert list(inspect.signature(T.coin_key).parameters) == ["unit", "offer", "draw_kind"]
    assert [f.name for f in fields(T.CoinUnit)] == ["seed", "part", "history", "seed_index", "start", "underlying"]
    off = hand_offer(1000)
    a, b = T.CoinUnit(SEED_COIN, 0, 0, 0, 10), T.CoinUnit(SEED_COIN, 0, 0, 0, 11)
    assert T.coin_key(a, off) != T.coin_key(b, off) and T.key_state(T.coin_key(a, off)) != T.key_state(
        T.coin_key(b, off))
    assert T.coin_key(T.CoinUnit(SEED_COIN, 0, 0, 0, 10, "MNQ"), off) == T.coin_key(a, off)   # one underlying


def test_coin_key_refuses_words_at_or_above_2_32():
    off = hand_offer(1000)
    for unit in (T.CoinUnit(0, 0, 0, 0, 0), T.CoinUnit(2 ** 32, 0, 0, 0, 0), T.CoinUnit(SEED_COIN, 0, 0, -1, 0),
                 T.CoinUnit(SEED_COIN, 0, 0, 0, 2 ** 32), T.CoinUnit(SEED_COIN, 2 ** 32 + 5, 0, 0, 0),
                 T.CoinUnit(SEED_COIN, 0, 0, 0, 0, "ES")):
        with pytest.raises(ValueError):
            T.coin_key(unit, off)
    with pytest.raises(ValueError):
        T.moment(hand_offer(1000, session=2 ** 32 // (1440 * 16) + 1))
    with pytest.raises(ValueError):
        hand_offer(1000, sub=16)


def test_coin_uniforms_are_on_the_symmetric_grid_distinct_and_fair():
    unit = T.CoinUnit(SEED_COIN, 1, 2, 3, 4)
    states, ups, n = set(), 0, 4000
    for k in range(n):
        off = hand_offer(5 * (k % 288), session=k // 288, decision=5 * (k % 288), alert=5 * (k % 288))
        key_ = T.coin_key(unit, off)
        u = T.coin_uniform(key_)
        i2 = u * 2.0 ** 53
        assert i2 == int(i2) and int(i2) % 2 == 1 and 0 < u < 1
        assert (1 - u) * 2.0 ** 53 == int((1 - u) * 2.0 ** 53)                 # the antithetic twin is exact
        states.add(T.key_state(key_))
        ups += T.coin_side(unit, off) == 1
    assert len(states) == n
    assert abs(ups - n / 2) < 4 * math.sqrt(n / 4)


def test_one_moment_one_side_across_sources():
    unit = T.CoinUnit(SEED_COIN, 0, 0, 0, 7)
    a = hand_offer(1000, session=40, decision=1000, alert=995, source="p16")
    b = T.Offer("p14", 40, 1000, 0, 1000, 1005, T.MARKET)
    assert T.coin_key(unit, a) == T.coin_key(unit, b) and T.coin_side(unit, a) == T.coin_side(unit, b)
