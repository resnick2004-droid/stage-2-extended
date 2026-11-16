"""Q-11: the shift-invariance test for every feature (feature-rules section 2) -- the proof that no feature or
normaliser of `extended.features` reads a bar after its alert.

For each cut time T: every bar stamped at or after T is (a) **replaced** by arbitrary values (a fresh seeded random
walk at another level and scale, random volumes, another contract label on the days after T's) or (b) **deleted**;
the features are recomputed on the whole frame, and every feature and every normaliser at every alert at or before T
must be bit-for-bit what it was (NaN equal to NaN). An alert at T reads only bars stamped <= T - 1 min, so the row at T
itself is the boundary the test bites on (a feature reading the bar stamped T fails here: `test_harness_catches_*`).

The cuts: the alert marks of the session's first minutes and later (08:30, 08:31, 08:35, 09:00, 09:05, 12:00, 15:00)
and the trading day's own open (17:00 CT the evening before) on the roll day (2021-03-12, NQH1 -> NQM1 +60 points),
the first day after the DST change (2021-03-15) and an ordinary day (2021-03-24), plus 16 alert marks drawn with a
fixed seed across the series. Seeds fixed for this file: 20261130 (the series), 20261131 (the random cuts),
20261132 + i (the replacement walks).
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from extended import features as F
from extended import synthetic_bars as sb

SEED_SERIES, SEED_CUTS, SEED_REPLACE = 20261130, 20261131, 20261132
COLS = list(F.NAMES) + [n for n, _ in F.NORMALISERS]
FIXED_DAYS = ("2021-03-12", "2021-03-15", "2021-03-24")
FIXED_TIMES = ((17, 0), (8, 30), (8, 31), (8, 35), (9, 0), (9, 5), (12, 0), (15, 0))


@pytest.fixture(scope="module")
def cal():
    return F.load_calendars()


@pytest.fixture(scope="module")
def bars():
    return sb.generate(sb.Spec(date(2021, 2, 1), date(2021, 4, 1), seed=SEED_SERIES))


@pytest.fixture(scope="module")
def base(bars, cal):
    return F.compute(bars, calendars=cal, normalisers=True)


def cuts(base: pd.DataFrame) -> list[int]:
    out = [sb.ts_of(d, h, m) for d in FIXED_DAYS for h, m in FIXED_TIMES]
    rng = np.random.default_rng(SEED_CUTS)
    post = base[base["day"] >= "2021-02-26"]
    out += [int(x) for x in rng.choice(post["alert_ts"].to_numpy(), 16, replace=False)]
    return sorted(set(out))


def violations(before: pd.DataFrame, after: pd.DataFrame, cut: int, cols: list[str]) -> list[tuple]:
    """Every (day, alert, column) at an alert <= cut whose value differs (NaN equal to NaN)."""
    a = before[before["alert_ts"] <= cut].reset_index(drop=True)
    b = after[after["alert_ts"] <= cut].reset_index(drop=True)
    if len(a) != len(b) or not (a["alert_ts"].to_numpy() == b["alert_ts"].to_numpy()).all():
        return [("rows differ", len(a), len(b))]
    bad = []
    for name in cols:
        x, y = a[name].to_numpy(dtype=float), b[name].to_numpy(dtype=float)
        diff = ~((x == y) | (np.isnan(x) & np.isnan(y)))
        for i in np.flatnonzero(diff)[:3]:
            bad.append((a.at[i, "day"], a.at[i, "alert"], name, x[i], y[i]))
    return bad


def test_cuts_cover_the_cases(base):
    cs = cuts(base)
    assert len(cs) >= 35
    at = set(base["alert_ts"])
    assert sum(c in at for c in cs) >= 30                       # most cuts fall exactly on an alert (the boundary)
    assert sb.ts_of("2021-03-15", 8, 30) - sb.ts_of("2021-03-12", 8, 30) == 3 * 86400 - 3600   # DST in between


def test_replacing_the_future_changes_nothing_up_to_the_cut(bars, base, cal):
    bad, bit = [], 0
    for i, cut in enumerate(cuts(base)):
        changed = sb.replace_from(bars, cut, seed=SEED_REPLACE + i)
        after = F.compute(changed, calendars=cal, normalisers=True)
        bad += [(cut,) + v for v in violations(base, after, cut, COLS)]
        later = base["alert_ts"] > cut
        if later.any():                                          # the perturbation is not vacuous
            x = base.loc[later, "ret_5"].to_numpy()
            y = after.loc[later, "ret_5"].to_numpy()
            bit += int(not np.array_equal(x, y, equal_nan=True))
    assert not bad, bad[:20]
    assert bit >= 30


def test_deleting_the_future_changes_nothing_up_to_the_cut(bars, base, cal):
    bad = []
    for cut in cuts(base):
        kept = bars[bars["ts"] < cut]
        after = F.compute(kept, calendars=cal, normalisers=True)
        bad += [(cut,) + v for v in violations(base, after, cut, COLS)]
    assert not bad, bad[:20]


def test_normalisers_use_the_past_only(bars, base, cal):
    """Replace every bar from a trading day's open on (the whole future of the series): the normalisers of that very
    day -- ATR and every time-of-day median, all built from earlier days -- are unchanged at all of its alerts, and so
    is everything before it; the day's own features change."""
    for i, d in enumerate(("2021-02-22", "2021-03-12", "2021-03-15", "2021-03-24")):
        cut = sb.ts_of(d, 17, 0)
        after = F.compute(sb.replace_from(bars, cut, seed=SEED_REPLACE + 100 + i), calendars=cal, normalisers=True)
        assert not violations(base, after, cut, COLS)
        today_a = base[base["day"] == d]
        today_b = after[after["day"] == d]
        for name, _ in F.NORMALISERS:
            assert np.array_equal(today_a[name].to_numpy(), today_b[name].to_numpy(), equal_nan=True), (d, name)
        assert not np.array_equal(today_a["ret_5"].to_numpy(), today_b["ret_5"].to_numpy(), equal_nan=True)


@pytest.mark.slow
def test_every_alert_of_ten_days_is_a_cut(bars, base, cal):
    """The exhaustive form (the slow tier, about a minute): every one of the 79 alert marks of ten days is a cut, the
    future replaced -- the day before the roll (2021-03-11), the roll day (2021-03-12, also the last CST day), the
    first CDT day (2021-03-15), the frame's first day with its full history, and six more drawn with seed 20261131."""
    rng = np.random.default_rng(SEED_CUTS + 1)
    days = sorted(base["day"].unique())
    pick = {"2021-03-11", "2021-03-12", "2021-03-15", days[F.HISTORY_DAYS]}
    others = [d for d in days[F.HISTORY_DAYS:] if d not in pick]
    pick |= set(rng.choice(others, 10 - len(pick), replace=False))
    rows = base[base["day"].isin(sorted(pick))]
    assert rows["day"].nunique() == 10 and len(rows) == 790
    bad = []
    for i, cut in enumerate(rows["alert_ts"].to_numpy()):
        after = F.compute(sb.replace_from(bars, int(cut), seed=SEED_REPLACE + 1000 + i), calendars=cal,
                          normalisers=True)
        bad += [(int(cut),) + v for v in violations(base, after, int(cut), COLS)]
    assert not bad, bad[:20]


# ------------------------------------------------------------------------------------- the harness is not vacuous

def _leaky(bars: pd.DataFrame, cal) -> pd.DataFrame:
    """The library plus one deliberately wrong feature: the close of the bar stamped AT the alert (it closes at
    t + 1 min) -- D-5's one-minute look-ahead."""
    X = F.compute(bars, calendars=cal, normalisers=True)
    close_at = bars.set_index("ts")["close"]
    X["leak"] = X["alert_ts"].map(close_at).to_numpy(dtype=float)
    return X


def test_harness_catches_a_one_minute_look_ahead(bars, cal):
    base = _leaky(bars, cal)
    caught = 0
    for i, cut in enumerate(sb.ts_of(d, 9, 0) for d in FIXED_DAYS):
        after = _leaky(sb.replace_from(bars, cut, seed=SEED_REPLACE + 200 + i), cal)
        v = violations(base, after, cut, ["leak"])
        caught += bool(v) and all(x[2] == "leak" and x[1] == "09:00" for x in v)
        assert not violations(base, after, cut, COLS)
    assert caught == len(FIXED_DAYS)


def test_harness_catches_a_full_sample_normaliser(bars, cal):
    """A z-score over the whole series (feature-rules section 2's forbidden normaliser) is caught by the same test."""
    def zscored(b):
        X = F.compute(b, calendars=cal)
        X["ret_5_z"] = (X["ret_5"] - X["ret_5"].mean()) / X["ret_5"].std()
        return X
    base = zscored(bars)
    cut = sb.ts_of("2021-03-24", 12, 0)
    after = zscored(sb.replace_from(bars, cut, seed=SEED_REPLACE + 300))
    assert violations(base, after, cut, ["ret_5_z"])
    assert not violations(base, after, cut, list(F.NAMES))
