"""Q-144 (B-ON): the feature library extended to the overnight alerts -- `extended.features.compute_overnight` -- on
synthetic bars only. No real bar is read.

What is held here:

* **Nothing of the RTH library moved.** `compute` and `compute_chunked` give, bit for bit, what the library gave before
  the extension (its blob, `OLD_BLOB`, loaded from git), on two synthetic series; and `compute` still refuses an
  overnight mark.
* **The shift-invariance test overnight** (feature-rules section 2): every bar stamped at or after a cut is replaced
  (and, separately, deleted) and every feature and normaliser at every overnight alert up to the cut must be unchanged,
  NaN equal to NaN -- cuts at the trading day's 17:00 open (the end of the daily halt), its first minutes, the evening,
  the night, the 07:30 CT release minute and the last overnight minutes, on a Monday (a Sunday open), the roll day,
  the first CDT day (its Sunday open follows the DST change) and an ordinary day, plus minute cuts drawn with a seeded
  child stream; the alerts are every minute the latencies 5, 3 and 2 put an alert at (`LATENCY_ALERTS`).
* **The harness is not vacuous overnight:** a feature written with the library's old negative-index reads (which wrap
  round to the same day's later bars at an alert before 19:01) is caught, as is a one-minute look-ahead.
* **Each formula against the direct, timestamp-filtered reference** (`tests/feature_reference.py`) at overnight alerts,
  every defined feature; the undefined ones (`F.OVERNIGHT_UNDEFINED`) all NaN.
* **The 17:00 alert** reads no bar of its day: every feature that reads the day's bars is NaN there, every day-level
  one equals its value later that day.
* **Availability as documented** (`F.OVERNIGHT_FROM`), no defined feature all-NaN or constant overnight, the DST clock
  overnight, and the chunked computation equal to the one-shot one.

Seeds: the build's block **20262048** (Q-144's draft, section 21), every draw a child
`numpy.random.SeedSequence(20262048, spawn_key=(stream, i))`: stream 0 the spring series, 1 the minute cuts,
2 the replacement walks (i the cut's index), 3 the reference's sampled rows, 4 the no-missing-bar series, 5 the DST
series, 6 the year for the chunked test, 7 the leak tests' replacements.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from extended import features as F
from extended import synthetic_bars as sb

import feature_reference as ref

SEED = 20262048
S_SERIES, S_CUTS, S_REPLACE, S_REF, S_FULL, S_DST, S_YEAR, S_LEAK = range(8)
#: the library's blob before the overnight extension (c2aa709:extended/features.py)
OLD_BLOB = "ab5246f0217a3869f75e27156a07574de81c4fe2"
ROOT = Path(__file__).resolve().parent.parent
COLS = list(F.NAMES) + [n for n, _ in F.NORMALISERS]
LATENCIES = (5, 3, 2)
#: every overnight alert a latency puts at an entry mark m (17:00 .. 08:25, every 5 minutes): max(0, m - L)
LATENCY_ALERTS = tuple(sorted({max(0, m - L) for m in range(F.slot(17, 0), F.slot(8, 25) + 1, 5) for L in LATENCIES}))
FIXED_DAYS = ("2021-03-01", "2021-03-12", "2021-03-15", "2021-03-24")       # Monday, roll, first CDT, ordinary
FIXED_TIMES = ((17, 0), (17, 1), (17, 2), (17, 3), (17, 5), (17, 30), (18, 0), (19, 0), (19, 1), (20, 0), (2, 0),
               (7, 30), (8, 22), (8, 25), (8, 29))


def child(stream: int, i: int = 0) -> np.random.SeedSequence:
    return np.random.SeedSequence(SEED, spawn_key=(int(stream), int(i)))


def seed_int(stream: int, i: int = 0) -> int:
    """An integer drawn from a child stream, for the helpers that take an int seed."""
    return int(np.random.default_rng(child(stream, i)).integers(0, 2 ** 31 - 1))


@pytest.fixture(scope="module")
def cal():
    return F.load_calendars()


@pytest.fixture(scope="module")
def bars():
    return sb.generate(sb.Spec(date(2021, 2, 1), date(2021, 4, 1), seed=seed_int(S_SERIES)))


@pytest.fixture(scope="module")
def on_base(bars, cal):
    return F.compute_overnight(bars, LATENCY_ALERTS, calendars=cal, normalisers=True)


def violations(before: pd.DataFrame, after: pd.DataFrame, cut: int, cols: list[str]) -> list[tuple]:
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


def cuts(base: pd.DataFrame) -> list[int]:
    out = [sb.ts_of(d, h, m) for d in FIXED_DAYS for h, m in FIXED_TIMES]
    rng = np.random.default_rng(child(S_CUTS))
    post = base[base["day"] >= "2021-02-26"]
    out += [int(x) for x in rng.choice(post["alert_ts"].to_numpy(), 16, replace=False)]
    return sorted(set(out))


# ------------------------------------------------------------------------------------------- the RTH library unchanged

def _old_library():
    """The library as it was before the extension, from its git blob, as a module of its own."""
    try:
        src = subprocess.run(["git", "cat-file", "-p", OLD_BLOB], cwd=ROOT, capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:                  # pragma: no cover - git is always here
        pytest.fail(f"the old library's blob {OLD_BLOB} is not readable: {exc}")
    path = Path(tempfile.mkdtemp(prefix="q144_")) / "q144_old_features.py"
    path.write_bytes(src)
    spec = importlib.util.spec_from_file_location("q144_old_features", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["q144_old_features"] = mod
    spec.loader.exec_module(mod)
    return mod


def _same(a: pd.DataFrame, b: pd.DataFrame) -> list[str]:
    bad = [] if list(a.columns) == list(b.columns) and len(a) == len(b) else ["shape"]
    for name in a.columns:
        x, y = a[name].to_numpy(), b[name].to_numpy()
        ok = np.array_equal(x, y, equal_nan=True) if x.dtype.kind == "f" else bool((x == y).all())
        if not ok:
            bad.append(name)
    return bad


def test_rth_output_is_bit_for_bit_the_old_librarys(bars, cal):
    old = _old_library()
    assert old.NAMES == F.NAMES and old.ALERT_MARKS == F.ALERT_MARKS and old.META == F.META
    assert old.describe() == F.describe()
    other = sb.generate(sb.Spec(date(2021, 9, 1), date(2021, 12, 31), seed=seed_int(S_SERIES, 1)))
    for b in (bars, other):
        assert not _same(old.compute(b, calendars=cal, normalisers=True), F.compute(b, calendars=cal, normalisers=True))
        assert not _same(old.compute_chunked(b, calendars=cal, normalisers=True, chunk_days=30),
                         F.compute_chunked(b, calendars=cal, normalisers=True, chunk_days=30))
    minute = [F.slot(8, 30), F.slot(8, 31), F.slot(10, 7), F.slot(14, 58), F.slot(15, 0)]
    assert not _same(old.compute(bars, minute, calendars=cal), F.compute(bars, minute, calendars=cal))


def test_rth_compute_still_refuses_overnight_marks(bars, cal):
    with pytest.raises(ValueError, match="08:30..15:00"):
        F.compute(bars, marks=[F.slot(8, 25)], calendars=cal)
    with pytest.raises(ValueError, match="17:00..08:29"):
        F.compute_overnight(bars, marks=[F.slot(8, 30)], calendars=cal)
    with pytest.raises(ValueError, match="17:00..08:29"):
        F.compute_overnight(bars, marks=[-5], calendars=cal)


# ------------------------------------------------------------------------------------------------- shift invariance

def test_cuts_cover_the_overnight_cases(on_base):
    cs = cuts(on_base)
    assert len(cs) >= 70
    at = set(on_base["alert_ts"])
    assert sum(c in at for c in cs) >= 60
    # the Monday's trading day opens on the Sunday; the first CDT day's Sunday open is after the 02:00 change
    assert pd.Timestamp(sb.ts_of("2021-03-01", 17, 0), unit="s", tz="UTC").tz_convert(sb.CHICAGO).weekday() == 6
    assert sb.ts_of("2021-03-15", 17, 0) - sb.ts_of("2021-03-12", 17, 0) == 3 * 86400 - 3600
    assert {F.slot(17, 0), F.slot(17, 2), F.slot(17, 3), F.slot(8, 22), F.slot(8, 23), F.slot(8, 20)} <= set(LATENCY_ALERTS)


def test_replacing_the_future_changes_nothing_overnight(bars, on_base, cal):
    bad, bit = [], 0
    for i, cut in enumerate(cuts(on_base)):
        changed = sb.replace_from(bars, cut, seed=seed_int(S_REPLACE, i))
        after = F.compute_overnight(changed, LATENCY_ALERTS, calendars=cal, normalisers=True)
        bad += [(cut,) + v for v in violations(on_base, after, cut, COLS)]
        later = on_base["alert_ts"] > cut
        if later.any():
            x, y = on_base.loc[later, "ret_day"].to_numpy(), after.loc[later, "ret_day"].to_numpy()
            bit += int(not np.array_equal(x, y, equal_nan=True))
    assert not bad, bad[:20]
    assert bit >= 60


def test_deleting_the_future_changes_nothing_overnight(bars, on_base, cal):
    """Deleting from a day's 17:00 open removes that day from the frame (a day without a bar has no rows), so its 17:00
    row cannot be compared here; the replacement test and `test_the_17_00_alert_reads_only_bars_closed_by_the_halt`
    hold that boundary row. Every row of every day the shortened frame still holds is compared."""
    bad, gone = [], 0
    for cut in cuts(on_base):
        after = F.compute_overnight(bars[bars["ts"] < cut], LATENCY_ALERTS, calendars=cal, normalisers=True)
        kept = on_base[on_base["day"].isin(set(after["day"]))]
        lost = on_base[(on_base["alert_ts"] <= cut) & ~on_base["day"].isin(set(after["day"]))]
        assert len(lost) <= 1 and (lost["slot"] == 0).all()
        gone += len(lost)
        bad += [(cut,) + v for v in violations(kept, after, cut, COLS)]
    assert not bad, bad[:20]
    assert gone == len(FIXED_DAYS)                     # exactly the four 17:00 cuts drop their day


def test_the_17_00_alert_reads_only_bars_closed_by_the_halt(bars, on_base, cal):
    """Replace every bar from a trading day's 17:00 open on: its 17:00 row (alert_ts == the cut) is unchanged -- it
    reads the earlier days only, every one of whose bars closed by 16:00 CT, an hour before the entry."""
    for i, d in enumerate(FIXED_DAYS):
        cut = sb.ts_of(d, 17, 0)
        after = F.compute_overnight(sb.replace_from(bars, cut, seed=seed_int(S_REPLACE, 500 + i)), LATENCY_ALERTS,
                                    calendars=cal, normalisers=True)
        row = (on_base["day"] == d) & (on_base["slot"] == 0)
        assert row.sum() == 1 and int(on_base.loc[row, "alert_ts"].iloc[0]) == cut
        assert not violations(on_base, after, cut, COLS), d


# ---------------------------------------------------------------------------------------- the harness is not vacuous

def _wrapping_ret_120(bars: pd.DataFrame, marks) -> np.ndarray:
    """ret_120 written with the pre-extension reads, `Cff[:, s - 1 - w]` and `Cff[:, s - 1]` unguarded: before 19:01
    the index is negative and numpy wraps round to the same day's last slots -- the future."""
    g = F.grid(bars)
    Cff = F._ffill_close(g.C)
    out = np.full((len(g.days), len(marks)), np.nan)
    for k, s in enumerate(marks):
        with np.errstate(invalid="ignore"):
            out[:, k] = (Cff[:, s - 1] - Cff[:, s - 1 - 120])
    return out.ravel()


def test_harness_catches_the_wrapping_index_and_a_one_minute_leak(bars, cal):
    marks = list(LATENCY_ALERTS)
    base = F.compute_overnight(bars, marks, calendars=cal)
    base["wrap"] = _wrapping_ret_120(bars, marks)
    close_at = bars.set_index("ts")["close"]
    base["leak"] = base["alert_ts"].map(close_at).to_numpy(dtype=float)
    caught_wrap = caught_leak = 0
    for i, d in enumerate(FIXED_DAYS):
        cut = sb.ts_of(d, 17, 30)
        changed = sb.replace_from(bars, cut, seed=seed_int(S_LEAK, i))
        after = F.compute_overnight(changed, marks, calendars=cal)
        after["wrap"] = _wrapping_ret_120(changed, marks)
        after["leak"] = after["alert_ts"].map(changed.set_index("ts")["close"]).to_numpy(dtype=float)
        caught_wrap += bool(violations(base, after, cut, ["wrap"]))
        caught_leak += bool(violations(base, after, cut, ["leak"]))
        assert not violations(base, after, cut, list(F.NAMES))
    assert caught_wrap == len(FIXED_DAYS) and caught_leak == len(FIXED_DAYS)


# ------------------------------------------------------------------------------------- formulas against the reference

def test_every_overnight_feature_matches_the_direct_reference(bars, on_base, cal):
    B = ref.prepare(bars)
    rng = np.random.default_rng(child(S_REF))
    X = on_base[on_base["slot"] > 0]
    must = [int(i) for d in FIXED_DAYS for a in ("17:07", "17:02", "17:03", "17:05", "17:57", "18:58", "19:00",
                                                 "19:03", "02:00", "07:28", "08:20", "08:23")
            for i in X.index[(X["day"] == d) & (X["alert"] == a)]]
    days = sorted(X["day"].unique())
    early = [int(i) for i in X.index[X["day"].isin(days[:2])]]
    pick = sorted(set(must) | set(int(i) for i in rng.choice(X.index, 60, replace=False))
                  | set(int(i) for i in rng.choice(early, 6, replace=False)))
    assert len(must) == 48
    bad = []
    for i in pick:
        row = on_base.loc[i]
        want = ref.reference(B, row["day"], int(row["alert_ts"]), cal)
        for name in COLS:
            got = float(row[name])
            if name in F.OVERNIGHT_UNDEFINED:
                if not np.isnan(got):
                    bad.append((row["day"], row["alert"], name, got, "undefined overnight"))
                continue
            if not np.isclose(got, want[name], rtol=1e-9, atol=1e-11, equal_nan=True):
                bad.append((row["day"], row["alert"], name, got, want[name]))
    assert not bad, bad[:20]


def test_the_reference_comparison_is_not_vacuous(on_base):
    post = on_base[(on_base["day"] >= "2021-03-02") & (on_base["slot"] >= F.slot(19, 1))]
    defined = [n for n in F.NAMES if n not in F.OVERNIGHT_UNDEFINED]
    assert np.isfinite(post[defined].to_numpy()).mean() > 0.97
    assert np.isnan(on_base[list(F.OVERNIGHT_UNDEFINED)].to_numpy()).all()


# -------------------------------------------------------------------------------------------- the 17:00 alert, NaNs

def test_the_17_00_alert_has_only_day_level_values(on_base):
    post = on_base[on_base["day"] >= "2021-03-02"]
    for d, sub in post.groupby("day"):
        first = sub[sub["slot"] == 0].iloc[0]
        later = sub[sub["slot"] == F.slot(2, 0)].iloc[0]
        for name in F.NAMES:
            frm = F.OVERNIGHT_FROM.get(name)
            if frm == 0:
                if name == "tod":
                    assert float(first[name]) == -15.5
                else:
                    assert np.array_equal([first[name]], [later[name]], equal_nan=True), (d, name)
            else:
                assert np.isnan(first[name]), (d, name, "reads the day's bars at 17:00")
        for name, _ in F.NORMALISERS:
            if name in ("norm_atr14", "norm_atr5"):
                assert first[name] == later[name]


def test_overnight_availability_is_as_documented(cal):
    """No minute without a bar and a higher volatility (no flat minute): every defined feature is finite at every
    overnight alert from its `OVERNIGHT_FROM` and NaN before it, on ordinary days after the warm-up; on the roll day
    the cross-day features are NaN."""
    bars = sb.generate(sb.Spec(date(2021, 2, 1), date(2021, 4, 1), seed=seed_int(S_FULL), overnight_missing=0.0,
                               rth_missing=0.0, vol_scale=4.0))
    marks = list(range(0, F.slot(8, 29) + 1))
    X = F.compute_overnight(bars, marks, calendars=cal)
    assert set(F.OVERNIGHT_FROM) | set(F.OVERNIGHT_UNDEFINED) == set(F.NAMES)
    assert not set(F.OVERNIGHT_FROM) & set(F.OVERNIGHT_UNDEFINED)
    for d in ("2021-03-02", "2021-03-12", "2021-03-15", "2021-03-24"):
        sub = X[X["day"] == d]
        roll = d == "2021-03-12"
        s = sub["slot"].to_numpy()
        for f in F.REGISTRY:
            v = sub[f.name].to_numpy()
            if f.name in F.OVERNIGHT_UNDEFINED or (roll and f.cross_day):
                assert np.isnan(v).all(), (d, f.name)
                continue
            frm = F.OVERNIGHT_FROM[f.name]
            assert np.isnan(v[s < frm]).all(), (d, f.name, "a value before it is available")
            assert np.isfinite(v[s >= frm]).all(), (d, f.name, "missing where documented available")


def test_no_overnight_feature_all_nan_or_constant(on_base):
    post = on_base[on_base["day"] >= "2021-03-02"]
    n_days = post["day"].nunique()
    for f in F.REGISTRY:
        if f.name in F.OVERNIGHT_UNDEFINED:
            continue
        v = post[f.name].to_numpy()
        v = v[np.isfinite(v)]
        assert v.size and np.unique(v).size >= 2, f.name
        if f.kind == "real":
            assert np.unique(v).size >= (n_days - 3 if f.daily else 20), f.name
    one = on_base[on_base["day"] == "2021-03-24"]
    for f in F.REGISTRY:
        if f.name in F.OVERNIGHT_UNDEFINED:
            continue
        v = one.loc[one["slot"] >= max(F.OVERNIGHT_FROM[f.name], F.slot(19, 1)), f.name].to_numpy()
        if f.daily:
            assert np.unique(v).size == 1, f.name
        elif f.kind == "real":
            assert np.unique(v[np.isfinite(v)]).size >= 10, f.name


def test_registry_documents_the_overnight_reading():
    table = F.describe_overnight().splitlines()
    assert len(table) == len(F.REGISTRY) + 2
    for i, f in enumerate(F.REGISTRY):
        line = table[i + 2]
        assert f"`{f.name}`" in line
        assert ("not defined" in line) is (f.name in F.OVERNIGHT_UNDEFINED)
    assert F.ON_ALERT_MARKS[0] == F.slot(17, 0) and F.ON_ALERT_MARKS[-1] == F.slot(8, 25)
    assert len(F.ON_ALERT_MARKS) == 186
    # the library's notes (the module docstring) name the extension and its guard
    assert "compute_overnight" in F.__doc__ and "wrap" in F.__doc__


# ------------------------------------------------------------------------------------------------------ DST, chunks

def test_dst_change_keeps_the_ct_clock_overnight(cal):
    """Volume a fixed function of the CT minute, no missing bar: every time-of-day volume feature is exactly 0 at
    every overnight alert after the warm-up (17:00 excepted, where it is NaN), on both sides of the 2021-03-14 change,
    whose Sunday-evening open is the first CDT one."""
    bars = sb.generate(sb.Spec(date(2021, 2, 1), date(2021, 3, 31), seed=seed_int(S_DST),
                               volume_profile="deterministic", overnight_missing=0.0, rth_missing=0.0))
    X = F.compute_overnight(bars, calendars=cal)
    post = X[(X["day"] >= "2021-03-02") & (X["slot"] > 0)]
    for name in ("vol_5", "vol_30", "vol_day"):
        assert (post[name].to_numpy() == 0.0).all(), name
    assert np.isnan(X.loc[X["slot"] == 0, "vol_5"]).all()
    a = X[(X["day"] == "2021-03-12") & (X["alert"] == "17:00")]["alert_ts"].iloc[0]
    b = X[(X["day"] == "2021-03-15") & (X["alert"] == "17:00")]["alert_ts"].iloc[0]
    assert int(a) == sb.ts_of("2021-03-12", 17, 0) and int(b) == sb.ts_of("2021-03-15", 17, 0)
    assert int(b) - int(a) == 3 * 86400 - 3600


def test_chunked_overnight_equals_one_shot(cal):
    bars = sb.generate(sb.Spec(date(2021, 5, 3), date(2021, 9, 30), seed=seed_int(S_YEAR)))
    X = F.compute_overnight(bars, calendars=cal, normalisers=True)
    Y = F.compute_chunked(bars, F.ON_ALERT_MARKS, calendars=cal, normalisers=True, chunk_days=40, overnight=True)
    assert not _same(X, Y)
    assert len(X) == bars["day"].nunique() * len(F.ON_ALERT_MARKS)
