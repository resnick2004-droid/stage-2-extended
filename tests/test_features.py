"""Q-11: the feature library (`extended/features.py`) on synthetic bars -- its registry and documentation, its
calendars, each formula against a direct timestamp-filtered reference, the documented availability, no feature all-NaN
or constant, the DST clock and the roll. The look-ahead tests are `tests/test_features_lookahead.py`.

Every series here is `extended.synthetic_bars` at a fixed seed (20261120-20261129, fixed for this file); no real bar
is read.
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from extended import features as F
from extended import synthetic_bars as sb

import feature_reference as ref

SEED_SPRING, SEED_REF, SEED_DST, SEED_ROLL = 20261120, 20261121, 20261122, 20261123


@pytest.fixture(scope="module")
def cal():
    return F.load_calendars()


@pytest.fixture(scope="module")
def spring():
    """42 trading days, 2021-02-01 .. 2021-04-01: the 2021-03-12 roll (NQH1 -> NQM1, +60 points) and the DST change of
    2021-03-14 (trading day 2021-03-15 is the first on CDT)."""
    return sb.generate(sb.Spec(date(2021, 2, 1), date(2021, 4, 1), seed=SEED_SPRING))


@pytest.fixture(scope="module")
def spring_X(spring, cal):
    return F.compute(spring, calendars=cal, normalisers=True)


# ------------------------------------------------------------------------------------------------------------ registry

def test_registry_counts_and_documentation():
    assert 30 <= len(F.REGISTRY) <= 50
    assert len(set(F.NAMES)) == len(F.NAMES)
    for f in F.REGISTRY:
        for field in ("formula", "window", "normaliser", "reads", "group"):
            assert getattr(f, field).strip(), (f.name, field)
        assert f.kind in ("real", "integer", "binary")
        assert F.RTH_OPEN <= f.available_from <= F.RTH_END
    table = F.describe().splitlines()
    assert len(table) == len(F.REGISTRY) + 2
    assert all(f"`{f.name}`" in table[i + 2] for i, f in enumerate(F.REGISTRY))


def test_family_b_declaration_carries_this_registry():
    """Family B's declaration (the draft, or its pinned successor) embeds `describe()`'s table line for line, so the
    features it declares are the features this library computes."""
    from pathlib import Path
    files = sorted((Path(__file__).resolve().parent.parent / "prereg").glob("*multifeature*.md"))
    assert files, "family B's declaration is missing"
    text = files[-1].read_text(encoding="utf-8")
    for line in F.describe().splitlines():
        assert line in text, line


def test_columns_are_the_registry(spring_X):
    assert list(spring_X.columns) == list(F.META) + list(F.NAMES) + [n for n, _ in F.NORMALISERS]
    days = spring_X["day"].nunique()
    assert len(spring_X) == days * len(F.ALERT_MARKS)
    assert F.ALERT_MARKS[0] == F.slot(8, 30) and F.ALERT_MARKS[-1] == F.slot(15, 0) and len(F.ALERT_MARKS) == 79


def test_no_raw_price_level_feature(spring, cal):
    """Adding a constant to every price changes no feature but the two flagged level-dependent ones. (The constant
    is on the tick grid and not a multiple of 100 points, so the round-number feature must move.)"""
    shifted = spring.copy()
    for col in ("open", "high", "low", "close"):
        shifted[col] = shifted[col] + 1037.25
    a = F.compute(spring, calendars=cal)
    b = F.compute(shifted, calendars=cal)
    for f in F.REGISTRY:
        x, y = a[f.name].to_numpy(), b[f.name].to_numpy()
        if f.level_dependent:
            assert not np.allclose(x, y, equal_nan=True), f.name
        else:
            assert np.allclose(x, y, rtol=1e-9, atol=1e-9, equal_nan=True), f.name


# ----------------------------------------------------------------------------------------------------------- calendars

def test_calendars(cal):
    assert cal.bls_major <= cal.bls
    for y in range(2020, 2026):
        assert sum(d.year == y for d in cal.bls) >= 40
    sched = dict(cal.fomc_scheduled)
    # unscheduled meetings, notation votes and conference calls are statements, never scheduled in advance
    for d in (date(2020, 3, 3), date(2020, 3, 15), date(2020, 3, 23), date(2019, 10, 11), date(2010, 5, 9)):
        assert d in cal.fomc_statements and d not in sched, d
    for y in range(2021, 2026):
        assert sum(d.year == y and until is None for d, until in cal.fomc_scheduled) == 8, y
    assert sched[date(2020, 3, 18)] == date(2020, 3, 13)            # scheduled, then cancelled on 2020-03-15
    assert date(2020, 3, 18) not in cal.fomc_statements
    assert date(2026, 7, 29) in sched


def test_fomc_day_counts_as_known_on_the_day(cal):
    days = [date(2020, 3, 11), date(2020, 3, 13), date(2020, 3, 16), date(2021, 1, 26), date(2021, 1, 27),
            date(2020, 3, 3), date(2020, 3, 4), date(2020, 3, 17)]
    to = F._days_to_fomc(days, cal)
    since = F._days_since_fomc(days, cal)
    # to: 2020-03-18 counts while it was scheduled (to 2020-03-13), then 2020-04-29 (beyond the cap)
    assert list(to) == [7, 5, 30, 1, 0, 15, 14, 30]
    # since: strictly before the day (2020-03-03's own 10:00 ET statement counts from the next day); the unscheduled
    # statements count once made; 2021-01-26 is 41 days after 2020-12-16 (capped)
    assert list(since) == [8, 10, 1, 30, 30, 30, 1, 2]


# ----------------------------------------------------------------------------------------- formulas against reference

def _sample_rows(X: pd.DataFrame, rng: np.random.Generator, k: int) -> list[int]:
    days = sorted(X["day"].unique())
    must = []
    for d in ("2021-03-11", "2021-03-12", "2021-03-15", "2021-03-16"):       # around the roll and the DST change
        for hhmm in ("08:30", "08:35", "09:00", "09:05", "15:00"):
            must.append(int(X.index[(X["day"] == d) & (X["alert"] == hhmm)][0]))
    early = [i for i in X.index if X.at[i, "day"] in days[:3]]               # the frame's first days (warm-up)
    must += list(rng.choice(early, 6, replace=False))
    rest = rng.choice(len(X), k, replace=False)
    return sorted(set(must) | set(int(i) for i in rest))


def test_every_feature_matches_the_direct_reference(spring, spring_X, cal):
    B = ref.prepare(spring)
    rng = np.random.default_rng(SEED_REF)
    cols = list(F.NAMES) + [n for n, _ in F.NORMALISERS]
    bad = []
    for i in _sample_rows(spring_X, rng, 60):
        row = spring_X.loc[i]
        want = ref.reference(B, row["day"], int(row["alert_ts"]), cal)
        for name in cols:
            got = float(row[name])
            if not np.isclose(got, want[name], rtol=1e-9, atol=1e-11, equal_nan=True):
                bad.append((row["day"], row["alert"], name, got, want[name]))
    assert not bad, bad[:20]


def test_reference_sees_the_whole_window(spring, cal):
    """The comparison is not vacuous: most sampled values are finite numbers, not NaN on both sides."""
    X = F.compute(spring, calendars=cal)
    post = X[X["day"] >= "2021-03-02"]
    finite = np.isfinite(post[list(F.NAMES)].to_numpy()).mean()
    assert finite > 0.97


# ------------------------------------------------------------------------------------------- availability, NaN, spread

def test_availability_is_as_documented(spring_X):
    """On a day with its history (after every warm-up), its previous day of the same contract, and its bars: each
    feature has a value at every alert from its `available_from` and none before; on the roll day every cross-day
    feature is NaN and every other one is as on an ordinary day."""
    X = spring_X
    ordinary = ["2021-03-02", "2021-03-15", "2021-03-24", "2021-03-31"]
    for d in ordinary + ["2021-03-12"]:
        sub = X[X["day"] == d]
        roll = d == "2021-03-12"
        assert bool(sub["prior_ok"].iloc[0]) is (not roll)
        for f in F.REGISTRY:
            v = sub[f.name].to_numpy()
            before = sub["slot"].to_numpy() < f.available_from
            if roll and f.cross_day:
                assert np.isnan(v).all(), (d, f.name)
                continue
            assert np.isnan(v[before]).all(), (d, f.name, "has a value before it is available")
            assert np.isfinite(v[~before]).all(), (d, f.name, "missing where documented available")


def test_warmup_is_as_documented(spring_X):
    days = sorted(spring_X["day"].unique())
    for f in F.REGISTRY:
        if f.warmup == 0 or f.cross_day:
            continue
        first = spring_X[spring_X["day"] == days[f.warmup]]
        last_missing = spring_X[spring_X["day"] == days[f.warmup - 1]]
        late = first["slot"] >= max(f.available_from, F.OR_END)
        assert np.isfinite(first.loc[late, f.name]).all(), f.name
        assert np.isnan(last_missing[f.name]).all() or f.warmup == F.TOD_MIN_DAYS, f.name


def test_no_feature_all_nan_or_constant(spring_X):
    """After the warm-up (22 sessions): no feature all-NaN or constant; a real alert-level feature takes many values,
    a real day-level one a value a day; within one realistic session every alert-level feature but the calendar's
    `tod` moves, and every day-level one holds still (the `daily` documentation is true)."""
    post = spring_X[spring_X["day"] >= "2021-03-02"]
    n_days = post["day"].nunique()
    for f in F.REGISTRY:
        v = post[f.name].to_numpy()
        v = v[np.isfinite(v)]
        assert v.size > 0, f"{f.name} is all NaN"
        assert np.unique(v).size >= 2, f"{f.name} is constant"
        if f.kind == "real":
            # a roll day blanks a cross-day daily feature; a share of at most 30 changes (up_share_30) is discrete
            need = n_days - 3 if f.daily else 20
            assert np.unique(v).size >= need, f"{f.name} takes too few values"
    for d in ("2021-03-24", "2021-03-15"):
        one = spring_X[spring_X["day"] == d]
        for f in F.REGISTRY:
            v = one.loc[one["slot"] >= f.available_from, f.name].to_numpy()
            if f.daily:
                assert np.unique(v).size == 1, (d, f.name, "a daily feature moved within the day")
            elif f.kind == "real":
                assert np.unique(v[np.isfinite(v)]).size >= 10, (d, f.name, "an intraday feature held still")


# --------------------------------------------------------------------------------------------------------- DST clock

def test_dst_change_keeps_the_ct_clock():
    """Volume is a fixed function of the CT minute (no missing bars): every time-of-day-normalised volume feature is
    exactly 0 after the warm-up -- before and after the 2021-03-14 change, though 08:30 CT moves from 14:30 to 13:30
    UTC. A clock keyed on UTC minutes would misalign the medians by an hour after the change."""
    bars = sb.generate(sb.Spec(date(2021, 2, 1), date(2021, 3, 31), seed=SEED_DST, volume_profile="deterministic",
                               overnight_missing=0.0, rth_missing=0.0))
    X = F.compute(bars, calendars=F.load_calendars())
    post = X[X["day"] >= "2021-03-02"]
    for name in ("vol_5", "vol_30", "vol_day"):
        assert (post[name].to_numpy() == 0.0).all(), name
    before = X[(X["day"] == "2021-03-12") & (X["alert"] == "08:30")]
    after = X[(X["day"] == "2021-03-15") & (X["alert"] == "08:30")]
    assert int(before["alert_ts"].iloc[0]) == sb.ts_of("2021-03-12", 8, 30)
    assert int(after["alert_ts"].iloc[0]) == sb.ts_of("2021-03-15", 8, 30)
    assert (sb.ts_of("2021-03-15", 8, 30) - sb.ts_of("2021-03-12", 8, 30)) % 86400 == 86400 - 3600
    assert float(before["tod"].iloc[0]) == float(after["tod"].iloc[0]) == 0.0
    # the opening range is the bars stamped 08:30-08:59 CT on both sides of the change
    for d in ("2021-03-12", "2021-03-15"):
        day = bars[bars["day"] == d]
        lo, hi = sb.ts_of(d, 8, 30), sb.ts_of(d, 8, 59)
        orb = day[(day["ts"] >= lo) & (day["ts"] <= hi)]
        row = X[(X["day"] == d) & (X["alert"] == "09:00")]
        A = float(F.compute(bars, calendars=F.load_calendars(), normalisers=True)
                  .query("day == @d and alert == '09:00'")["norm_atr14"].iloc[0])
        assert np.isclose(float(row["or_width"].iloc[0]), (orb["high"].max() - orb["low"].min()) / A)


# --------------------------------------------------------------------------------------------------------------- roll

def test_roll_spread_moves_no_feature(cal):
    """The same series with and without a +60-point calendar spread at each roll: every feature but the two
    level-dependent ones is identical (the spread never enters a range, a return or a normaliser), and on each roll day
    every cross-day feature is NaN -- the old contract's levels are not compared with the new contract's prices."""
    spec = dict(start=date(2021, 2, 1), end=date(2021, 7, 1), seed=SEED_ROLL)
    a = F.compute(sb.generate(sb.Spec(**spec, roll_spread=60.0)), calendars=cal, normalisers=True)
    b = F.compute(sb.generate(sb.Spec(**spec, roll_spread=0.0)), calendars=cal, normalisers=True)
    assert set(a.loc[~a["prior_ok"], "day"]) - {a["day"].iloc[0]} == {"2021-03-12", "2021-06-11"}
    for name in list(F.NAMES) + [n for n, _ in F.NORMALISERS]:
        if name in F.BY_NAME and F.BY_NAME[name].level_dependent:
            continue
        assert np.allclose(a[name], b[name], rtol=1e-9, atol=1e-9, equal_nan=True), name
    for d in ("2021-03-12", "2021-06-11"):
        sub = a[a["day"] == d]
        for f in F.REGISTRY:
            if f.cross_day:
                assert sub[f.name].isna().all(), (d, f.name)


def test_roll_jump_would_show_without_the_guard(cal):
    """The guard is what removes the spread: computed by hand on the roll day, the prior day's high against the new
    contract's price differs between the series with and without the spread by exactly the spread in ATR units --
    the library gives NaN there in both, and a value the next day."""
    naive, rows = [], []
    for spread in (60.0, 0.0):
        bars = sb.generate(sb.Spec(date(2021, 2, 1), date(2021, 4, 1), seed=SEED_ROLL, roll_spread=spread))
        X = F.compute(bars, calendars=cal, normalisers=True)
        prev = bars[(bars["day"] == "2021-03-11")]
        prev = prev[(prev["ts"] >= sb.ts_of("2021-03-11", 8, 30)) & (prev["ts"] < sb.ts_of("2021-03-11", 15, 0))]
        row = X[(X["day"] == "2021-03-12") & (X["alert"] == "10:00")].iloc[0]
        c = float(bars[bars["ts"] <= int(row["alert_ts"]) - 60]["close"].iloc[-1])
        naive.append((c - prev["high"].max()) / row["norm_atr14"])
        rows.append(row)
        nxt = X[(X["day"] == "2021-03-15") & (X["alert"] == "10:00")].iloc[0]
        assert np.isnan(row["d_pdh"]) and np.isfinite(nxt["d_pdh"])
    assert rows[0]["norm_atr14"] == rows[1]["norm_atr14"]
    assert np.isclose(naive[0] - naive[1], 60.0 / rows[0]["norm_atr14"])


# -------------------------------------------------------------------------------------------------------- input checks

def test_grid_refuses_bad_input(spring):
    b = spring.head(5000).copy()
    with pytest.raises(ValueError, match="whole minute"):
        F.grid(b.assign(ts=b["ts"] + 1))
    with pytest.raises(ValueError, match="share a trading day and minute"):
        F.grid(pd.concat([b, b.head(1)], ignore_index=True))
    with pytest.raises(ValueError, match="disagrees"):
        F.grid(b.assign(day="2021-02-02"))
    two = b.copy()
    two.loc[two.index[-1], "contract"] = "NQZ9"
    with pytest.raises(ValueError, match="two contracts"):
        F.grid(two)
    with pytest.raises(ValueError, match="08:30..15:00"):
        F.compute(b, marks=[F.slot(8, 25)], calendars=F.load_calendars())
