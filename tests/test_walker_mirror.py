"""Q-10 (F-01 section 7 item 4): the mirror's zero on synthetic random-walk bars.

On a driftless random walk no side rule can know the future, so at every fill the rule's trade and its mirror (the
opposite side at the same fill bar and price, the same stop, target and walk rules) are equally likely to win: the mean
of 1/2 [win(rule side) - win(mirror side)] must be zero within its interval, for stop (`break`) and limit (`fade`)
entries, at F-01's stops (100 and 150 ticks) and R values (1, 1.5, 3), under the declared walk (`DECLARED_F01`).

Fixed before the test was first run (none is tuned to a reading):
* SEED 20261115 (the test's own; used nowhere else), DAYS 1500 synthetic days, each one ticket of each entry kind;
* the bars: a Gaussian random walk in ticks at SUB = 10 steps a minute, each step rounded to the tick grid, a
  minute's open the previous minute's close; SIGMA_TICKS = 24 ticks (6 NQ points) a minute, about NQ's
  regular-session one-minute scale (the declared stops are 100 and 150 ticks, so a one-minute bar rarely spans one);
* each ticket live at 08:30 CT, cancelled at 14:30 CT (a cutoff F-01 can choose), its price a uniform 4 to 160 ticks
  from the price at live, above or below by a fair draw (a resistance takes a buy stop or a sell limit, a support a
  sell stop or a buy limit, as F-01's side rules place them);
* the interval: two-sided, the mean +/- Z standard errors with Z = 2.87 -- Bonferroni over the 12 (entry kind, stop, R)
  intervals at a family-wise 95 % (fills on different days are independent, one ticket of a kind a day).

A second test documents a property of the declared fill-bar rule rather than the walker: on bars as wide as the stop
the rule is not side-neutral (see the walker's docstring, "the fill-bar rule and the mirror").

**Both FAILED on their first run (2026-11-15) and stay here verbatim, as strict expected failures, on record.** The
diagnosis (the failure protocol; synthetic bars only): (1) terminal states -- no exit on a fill bar at the declared
scale, so the fill-bar rule is not the cause; (2) the walker in isolation -- every day reflected (price about the base,
high and low swapped) with every order's side flipped reproduces every fill and walk exactly, so the walker has no
long/short asymmetry; (3) replication at 20 seeds fixed beforehand (20261200 + i) -- the bias is systematic: limit cells'
mean z between -0.65 and -1.48, stop cells' between +0.43 and +0.96. **The cause is the generator's coarse steps (ten a
minute, about 7.6 ticks each):** the path jumps past an order's price between prints, so the declared fill prices --
a stop at its price plus a tick, a limit at its price -- are not the market's at the fill: the limit's rule side starts
several ticks under water and the stop's several ticks ahead, its mirror the opposite, a bias of about
(overshoot ticks) / (S + T) in win probability. That is a property of the declared fill rules on any bars whose prices
skip ticks through a level (on real NQ: fast markets, the 08:30 open), not a defect of the walker; it is reported to
the lead. The property test's premise (the fill-bar tilt alone) is confounded by the same overshoot.

**The mirror's zero on a tick-by-tick random walk** (the third test, corrective cycle 1, fixed before its first run):
from the bar stamped 08:30 the path moves one tick a step, 576 steps a minute (sd 24 ticks a minute, the declared
test's scale), so every price between two prints trades and the declared fill prices are the market's (up to the one
tick the rules give away: a stop's slippage and a limit's trade-through each start the rule side a tick behind its
mirror, a bias of -1 / (S + T), at most 0.5 % here); bars before 08:30 flat at the base (only the price at live is read
from them); seed 20261116, 1500 days, the same tickets, stops, R values and Z.

**What these tests cannot see** (the Phase 0 audit's D-1, after they were written): at 24 ticks a minute a fill bar
rarely spans a 100-tick stop and about 1,300 fills give an interval of several points, so the declared fill-bar rule's
bias passes them unseen. T-13 (`tests/test_walker_t13.py`: 50 ticks a minute, about 470,000 fills a side rule) is the
test that sees it; these stay as the record of the first cycle.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extended import walker as W  # noqa: E402

SEED = 20261115
DAYS = 1500
SUB = 10
SIGMA_TICKS = 24.0
Z = 2.87
STOPS = (100, 150)
RRS = (1.0, 1.5, 3.0)
LIVE = W.slot(8, 30)
CUTOFF = W.slot(14, 30)
BASE_TICKS = 80000                       # 20,000 NQ points
MIN_FILLS = 1000
TICK_SEED = 20261116                     # the tick-by-tick test's (corrective cycle 1), used nowhere else
STEPS_A_MINUTE = 576                     # one tick a step: sd 24 ticks a minute
DIAGNOSIS = ("first run failed (2026-11-15); diagnosed as the coarse generator's overshoot past an order's price, "
             "not the walker (the module docstring); kept verbatim on record")


def random_walk_day(rng: np.random.Generator, sigma_ticks: float) -> tuple[np.ndarray, ...]:
    """One synthetic trading day on the trading-day clock (bars 1..1330, index 0 unused), prices on the tick grid."""
    m = W.C_FLAT
    steps = rng.normal(0.0, sigma_ticks / math.sqrt(SUB), size=m * SUB)
    path = BASE_TICKS + np.round(np.cumsum(steps))
    p = path.reshape(m, SUB)
    close = p[:, -1]
    opens = np.concatenate([[float(BASE_TICKS)], close[:-1]])
    high = np.maximum(p.max(axis=1), opens)
    low = np.minimum(p.min(axis=1), opens)
    pad = lambda x: np.concatenate([[np.nan], x]) * W.TICK            # noqa: E731
    return pad(opens), pad(high), pad(low), pad(close)


def tick_walk_day(rng: np.random.Generator, sigma_ticks: float) -> tuple[np.ndarray, ...]:
    """One synthetic day: flat at the base to the bar ending 08:30, then a one-tick-a-step random walk (`sigma_ticks`
    ** 2 steps a minute) from the bar stamped 08:30 to the bar ending 15:10; prices on the tick grid."""
    steps_min = int(round(float(sigma_ticks) ** 2))
    first = LIVE + 1
    m = W.C_FLAT - first + 1
    steps = rng.integers(0, 2, size=m * steps_min, dtype=np.int8).astype(np.int32) * 2 - 1
    p = (BASE_TICKS + np.cumsum(steps)).reshape(m, steps_min).astype(float)
    close = p[:, -1]
    opens = np.concatenate([[float(BASE_TICKS)], close[:-1]])
    n = W.C_FLAT + 1
    o, h, l, c = (np.full(n, float(BASE_TICKS)) for _ in range(4))
    o[first:], c[first:] = opens, close
    h[first:] = np.maximum(p.max(axis=1), opens)
    l[first:] = np.minimum(p.min(axis=1), opens)
    for x in (o, h, l, c):
        x[0] = np.nan
    return o * W.TICK, h * W.TICK, l * W.TICK, c * W.TICK


def lifts(sigma_ticks: float, days: int, seed: int, day_fn=random_walk_day) -> dict[tuple[str, int, float], np.ndarray]:
    """{(entry kind, stop, R): the per-fill 1/2 [win(rule) - win(mirror)]} over `days` synthetic days."""
    rng = np.random.default_rng(seed)
    bl = W.brackets(STOPS, RRS)
    out: dict[tuple[str, int, float], list[float]] = {(k, S, R): [] for k in (W.STOP_ENTRY, W.LIMIT_ENTRY)
                                                      for S in STOPS for R in RRS}
    for _ in range(days):
        o, h, l, c = day_fn(rng, sigma_ticks)
        ref = c[LIVE]
        for kind in (W.STOP_ENTRY, W.LIMIT_ENTRY):
            above = bool(rng.random() < 0.5)
            k = int(rng.integers(4, 161))
            price = ref + (k if above else -k) * W.TICK
            if kind == W.STOP_ENTRY:
                side = +1 if above else -1             # break: buy stop above, sell stop below
            else:
                side = -1 if above else +1             # fade: sell limit above, buy limit below
            f = W.fill_order(W.Order(kind, side, LIVE, price, CUTOFF), o, h, l, c, rules=W.DECLARED_F01)
            assert f.status != "void"                  # placed beyond the price at live by construction
            if f.status != "filled":
                continue
            res = W.walk(o, h, l, c, [f.bar, f.bar], [f.price, f.price], [side, -side], [True, True], bl,
                         rules=W.DECLARED_F01)
            win = res["kind"] == W.TARGET               # (2, brackets): row 0 the rule's side, row 1 the mirror
            for b, (S, R, _T) in enumerate(bl):
                out[(kind, S, R)].append(0.5 * (float(win[0, b]) - float(win[1, b])))
    return {key: np.asarray(v) for key, v in out.items()}


@pytest.fixture(scope="module")
def declared():
    return lifts(SIGMA_TICKS, DAYS, SEED)


def check_zero(x: dict[tuple[str, int, float], np.ndarray]) -> None:
    for (kind, S, R), v in x.items():
        assert len(v) >= MIN_FILLS, (kind, S, R, len(v))
        assert 0.0 < float(np.mean(np.abs(v) > 0)) < 1.0, (kind, S, R)
        mean, se = float(v.mean()), float(v.std(ddof=1) / math.sqrt(len(v)))
        assert abs(mean) <= Z * se, f"{kind} stop {S} R {R}: lift {mean:+.4f}, se {se:.4f}, n {len(v)}"


def test_the_mirror_lift_is_zero_on_a_tick_by_tick_random_walk():
    check_zero(lifts(SIGMA_TICKS, DAYS, TICK_SEED, day_fn=tick_walk_day))
    assert STEPS_A_MINUTE == int(round(SIGMA_TICKS ** 2))


@pytest.mark.xfail(strict=True, reason=DIAGNOSIS)
def test_the_mirror_lift_is_zero_on_a_random_walk(declared):
    for (kind, S, R), x in declared.items():
        assert len(x) >= MIN_FILLS, (kind, S, R, len(x))
        assert 0.0 < float(np.mean(np.abs(x) > 0)) < 1.0, (kind, S, R)        # rule and mirror do differ
        mean, se = float(x.mean()), float(x.std(ddof=1) / math.sqrt(len(x)))
        assert abs(mean) <= Z * se, f"{kind} stop {S} R {R}: lift {mean:+.4f}, se {se:.4f}, n {len(x)}"


@pytest.mark.xfail(strict=True, reason=DIAGNOSIS)
def test_the_fill_bar_rule_tilts_rule_and_mirror_on_bars_as_wide_as_the_stop():
    """A property of the declared fill-bar rule (F-01 section 3), recorded so the screen's readers know it: on a resting
    order's fill bar the adverse move counts and the favourable does not, but part of that bar traded BEFORE the
    fill -- below a buy stop's fill (the bar rose through it), above a sell limit's (the bar rose to it). So on the
    fill bar the break-direction side (a stop entry's rule side; a limit entry's mirror) is charged a pre-fill adverse
    move its opposite is not. On bars as wide as the stop (SIGMA 100 ticks a minute, 600 days, seed SEED + 1, fixed
    with the test) `break`'s mirror lift is negative and `fade`'s positive, each beyond three standard errors."""
    x = lifts(100.0, 600, SEED + 1)
    for kind, sign in ((W.STOP_ENTRY, -1.0), (W.LIMIT_ENTRY, +1.0)):
        v = x[(kind, 100, 1.0)]
        mean, se = float(v.mean()), float(v.std(ddof=1) / math.sqrt(len(v)))
        assert sign * mean > 3.0 * se, f"{kind}: lift {mean:+.4f}, se {se:.4f}, n {len(v)}"
