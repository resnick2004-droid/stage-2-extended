"""T-13 (the Phase 0 audit, track D; the lead's change to Q-10, 2026-11-15): the mirror's zero, per side rule (`break`
and `fade` separately, never pooled) and per R, on synthetic walks whose one-minute ranges reach the stop on a
declared share of fill bars -- under F-01's declared settlement it must FAIL (D-1, D-13); under the pair rule with the
symmetric booking it must hold.

Fixed before the test was first run (none tuned to a reading; the day count sized from a pilot at a separate seed for
the interval's width only):

* **the walk:** tick-continuous -- one tick a step, 2,500 steps a minute (sd 50 ticks a minute, Appendix B's middle
  row), so every price between two prints trades and a trigger is the market's price at the fill (Gaussian steps would
  overshoot it, which is D-13's booking effect, not the settlement's); bars before 08:30 CT flat at the base, the walk
  from the bar stamped 08:30 to the bar ending 15:10; one path a day, seed `SEED`, `DAYS` days, generated a day at a
  time (memory stays small);
* **the tickets:** every five minutes from 08:30 to 13:25 CT, one `break` ticket (a buy stop above or a sell stop below
  the price at live, by a fair draw) and one `fade` ticket (a sell limit above or a buy limit below), each 50 to 150
  ticks away (uniform; one to three sds, Appendix B's spread), cancelled at 14:00 CT; F-01's walk otherwise
  (`DECLARED_F01`: stop first, the 15:10 close); stop `STOP` = 100 ticks, R in (1, 1.5, 3);
* **the statistic:** per side rule and R, the mean over fills of 1/2 [win(rule) - win(mirror)], its standard error
  clustered by day (tickets on one path overlap), the interval mean +/- `Z` se with Z = 2.64 (two-sided, Bonferroni over
  the 2 x 3 cells at a family-wise 95 %); the interval's half-width must be under a quarter of a point of win
  probability (`HALF_WIDTH_MAX` 0.0025) and at least `SPAN_MIN` = 20 % of the fill bars must span the stop (range >=
  100 ticks; Appendix B's middle row read 27 %), else the test is refused as unable to see D-1.

What each mode is expected to show (the audit's D-1, D-13): `declared` + `rule_fill` -- the fill-bar rule charges the
side trading in the bar's direction a pre-fill adverse move (`break`'s rule side, `fade`'s mirror), and the rule's fill
starts a tick behind its mirror's: `break` biased down, `fade` up less a tick; `pair` + `symmetric` -- the four barriers
are symmetric about the trigger and an ambiguous fill bar settles both sides as losses, so the lift is zero by symmetry.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extended import walker as W  # noqa: E402

SEED = 20261118                          # T-13's own, used nowhere else
DAYS = 9000                              # the pilot (seed 20261190, 300 days, lifts not read): the widest cell needs
                                         # about 7,800 days for HALF_WIDTH_MAX; 9,000 for margin (~470,000 fills a rule)
SIGMA_TICKS = 50
STEPS_A_MINUTE = SIGMA_TICKS ** 2        # one tick a step
STOP = 100
RRS = (1.0, 1.5, 3.0)
LIVES = tuple(range(W.slot(8, 30), W.slot(13, 30), 5))
CUTOFF = W.slot(14, 0)
OFFSET_TICKS = (50, 150)
Z = 2.64
HALF_WIDTH_MAX = 0.0025
SPAN_MIN = 0.20
BASE_TICKS = 80000
RULES = ("break", "fade")
MODES = {"declared_rule_fill": ("declared", "rule_fill"), "pair_symmetric": ("pair", "symmetric")}
D1 = ("the audit's D-1 and D-13: F-01's fill-bar rule charges the side trading in the bar's direction a pre-fill "
      "adverse move and books the mirror at the rule's fill -- break's lift biased down, fade's up (T-13 must fail)")


def tick_day(rng: np.random.Generator) -> tuple[np.ndarray, ...]:
    """One day: flat at the base to the bar ending 08:30, then one tick a step from the bar stamped 08:30."""
    first = W.slot(8, 30) + 1
    m = W.C_FLAT - first + 1
    bits = np.unpackbits(np.frombuffer(rng.bytes(m * STEPS_A_MINUTE // 8), dtype=np.uint8))
    path = BASE_TICKS + np.cumsum(bits.astype(np.int32) * 2 - 1, dtype=np.int32)
    p = path.reshape(m, STEPS_A_MINUTE)
    n = W.C_FLAT + 1
    o, h, l, c = (np.full(n, float(BASE_TICKS)) for _ in range(4))
    close = p[:, -1].astype(float)
    opens = np.concatenate([[float(BASE_TICKS)], close[:-1]])
    o[first:], c[first:] = opens, close
    h[first:] = np.maximum(p.max(axis=1), opens)
    l[first:] = np.minimum(p.min(axis=1), opens)
    for x in (o, h, l, c):
        x[0] = np.nan
    return o * W.TICK, h * W.TICK, l * W.TICK, c * W.TICK


def run(days: int, seed: int, modes=MODES) -> dict:
    """Per (mode, rule): per-day lift sums by R (days x R) and fill counts (days), the ambiguous counts by R, and the
    fills whose bar spans the stop -- everything the statistic needs, a day at a time."""
    rng = np.random.default_rng(seed)
    bl = W.brackets((STOP,), RRS)
    out = {(mo, ru): {"sum": np.zeros((days, len(RRS))), "n": np.zeros(days), "amb": np.zeros(len(RRS)),
                      "span": 0} for mo in modes for ru in RULES}
    for di in range(days):
        o, h, l, c = tick_day(rng)
        fills: dict[str, list] = {ru: [] for ru in RULES}
        for t in LIVES:
            ref = c[t]
            for ru in RULES:
                above = bool(rng.random() < 0.5)
                k = int(rng.integers(OFFSET_TICKS[0], OFFSET_TICKS[1] + 1))
                price = ref + (k if above else -k) * W.TICK
                if ru == "break":
                    order = W.Order(W.STOP_ENTRY, +1 if above else -1, t, price, CUTOFF)
                else:
                    order = W.Order(W.LIMIT_ENTRY, -1 if above else +1, t, price, CUTOFF)
                f = W.fill_order(order, o, h, l, c, rules=W.DECLARED_F01)
                if f.status == "filled":
                    fills[ru].append((f, order.side))
        for ru in RULES:
            if not fills[ru]:
                continue
            fb = np.array([f.bar for f, _ in fills[ru]])
            span = int(((h[fb] - l[fb]) / W.TICK >= STOP).sum())
            for mo, (fill_bar, booking) in modes.items():
                res = W.walk_pair(o, h, l, c, fb, [f.price for f, _ in fills[ru]],
                                  [W.mirror_price(f, booking) for f, _ in fills[ru]], [s for _, s in fills[ru]],
                                  True, bl, rules=W.DECLARED_F01, fill_bar=fill_bar)
                lift = 0.5 * ((res["rule"]["kind"] == W.TARGET).astype(float)
                              - (res["mirror"]["kind"] == W.TARGET).astype(float))
                acc = out[(mo, ru)]
                acc["sum"][di] = lift.sum(axis=0)
                acc["n"][di] = len(fb)
                acc["amb"] += res["ambiguous"].sum(axis=0)
                acc["span"] += span
    return out


def stats(acc: dict) -> list[dict]:
    """Per R: fills, the lift, its day-clustered se, the interval's half-width at Z, the ambiguous and spanning shares."""
    N = float(acc["n"].sum())
    D = int((acc["n"] > 0).sum())
    rows = []
    for b, R in enumerate(RRS):
        m = acc["sum"][:, b].sum() / N
        resid = acc["sum"][:, b] - acc["n"] * m
        se = math.sqrt(D / (D - 1) * float((resid ** 2).sum())) / N
        rows.append({"R": R, "fills": int(N), "lift": m, "se": se, "half_width": Z * se,
                     "ambiguous": float(acc["amb"][b] / N), "span": float(acc["span"] / N)})
    return rows


def outside(mode: str, res: dict) -> list[str]:
    bad = []
    for ru in RULES:
        bad += [f"{ru} R {r['R']:g}: lift {100 * r['lift']:+.2f} points (se {100 * r['se']:.2f}, n {r['fills']}, "
                f"ambiguous {100 * r['ambiguous']:.1f} %, spanning {100 * r['span']:.1f} %)"
                for r in stats(res[(mode, ru)]) if abs(r["lift"]) > Z * r["se"]]
    return bad


@pytest.fixture(scope="module")
def t13():
    return run(DAYS, SEED)


@pytest.mark.slow
def test_t13_is_sharp_enough_to_see_d1(t13):
    """The precondition, apart from the readings (so the expected failure below can fail only on the bias)."""
    for (mode, ru), acc in t13.items():
        for r in stats(acc):
            assert r["span"] >= SPAN_MIN, f"{ru}: only {r['span']:.3f} of fill bars span the stop"
            assert r["half_width"] <= HALF_WIDTH_MAX, (mode, ru, r["R"], r["half_width"])


@pytest.mark.slow
@pytest.mark.xfail(strict=True, reason=D1)
def test_t13_the_declared_settlement_is_not_side_neutral(t13):
    bad = outside("declared_rule_fill", t13)
    assert not bad, "outside the mirror's zero: " + "; ".join(bad)


@pytest.mark.slow
def test_t13_the_pair_rule_with_the_symmetric_booking_is_side_neutral(t13):
    bad = outside("pair_symmetric", t13)
    assert not bad, "outside the mirror's zero: " + "; ".join(bad)
