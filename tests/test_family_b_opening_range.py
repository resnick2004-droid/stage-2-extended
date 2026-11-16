"""Q-43 (family B's third draft; the red team's M2-1): the opening range is excluded **in substance** -- at every admitted
alert, no feature family B uses reads a bar stamped 08:30-08:59 CT of the alert's day.

`prereg/DRAFT_F-B_multifeature.md` (version 3, sections 3 and 7) declares the family's features (`FAMILY_B_FEATURES`,
37 of the library's 47) and alerts (`FAMILY_B_ALERTS`, 10:05-15:00 CT). This file holds that declaration to the bars:

* **invariance:** every bar stamped 08:30-08:59 of one day replaced by arbitrary values changes none of the 37
  features at any of that day's admitted alerts, bit for bit -- so no used feature is a function of the opening range
  (of 5, 15, 30 or 60 minutes: each contains those bars), on eight days including a roll and the first CDT day;
* **not vacuous:** the same replacement does change the excluded features (`or_width`, `range_rth`, `pos_rth`, `ret_rth`,
  `d_vwap`, `range_day`, `pos_day`, `vol_day`, and `ret_120` at 10:35-11:00), so the replacement bites;
* **no structural equality:** at no admitted alert is a used feature equal, on every day, to an opening-range quantity
  (its width, the position in it, its net move, the distance to its VWAP), while the harness does find the identity
  the red team found at the 09:00 alert (`range_rth` = `or_width`, `pos_rth` = `or_pos` on every day);
* **the declaration says the same:** the draft's table of used features lists exactly `FAMILY_B_FEATURES`.

**Added for the fourth draft** (the third review's M3-2 and m3-1; the lead's ruling E-036):

* **the disclosed identity:** `d_pdc - gap - ret_60 = (C[t-61] - C[08:29]) / atr14` exactly at every admitted alert
  of a non-roll day -- the move from the 08:29 close to the close as of t - 61, which at 10:30 is the 60-minute
  opening range's net move. No single feature reads the half-hour; this combination of three carries its net move;
* **linear recoverability, as the draft discloses it:** on a synthetic year, the 60-minute range's net move at
  10:30 is a linear function of the 37 features (R-squared at least 0.99), while the half-hour's **width** and the
  **position** in it -- which a breakout needs -- are not (R-squared below 0.9 at 10:05, 10:30 and 12:00);
* **the as-of rule (m3-1):** with no bar stamped 09:00-09:24 on a day, the 60-minute windows' as-of close at the
  alerts 10:05-10:25 falls back into the half-hour. The declared per-row rule (`or_free_rows`, a reference for the
  build's refusing check) flags exactly those rows, and only on them does replacing the half-hour move a used
  feature.

Synthetic bars only (`extended.synthetic_bars`); seeds `numpy.random.default_rng([20261968, 20 + i])`, the draft's
proposed build-test seed (its section 19).
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from extended import features as F
from extended import synthetic_bars as sb

SEED = 20261968
EXCLUDED = ("or_width", "or_pos", "ret_120", "ret_rth", "range_rth", "pos_rth", "d_vwap", "range_day", "pos_day",
            "vol_day")
FAMILY_B_FEATURES = tuple(n for n in F.NAMES if n not in EXCLUDED)
FAMILY_B_ALERTS = tuple(range(F.slot(10, 5), F.slot(15, 0) + 1, 5))
OR_LO, OR_HI = F.slot(8, 30), F.slot(9, 0)                # bars stamped 08:30 .. 08:59
DAYS = ("2021-02-25", "2021-03-03", "2021-03-11", "2021-03-12", "2021-03-15", "2021-03-23", "2021-03-30",
        "2021-04-08")
DRAFT = Path(__file__).resolve().parent.parent / "prereg" / "DRAFT_F-B_multifeature.md"


@pytest.fixture(scope="module")
def cal():
    return F.load_calendars()


@pytest.fixture(scope="module")
def bars():
    return sb.generate(sb.Spec(date(2021, 1, 4), date(2021, 4, 15), seed=int(np.random.default_rng([SEED, 20])
                                                                              .integers(1, 2**31))))


@pytest.fixture(scope="module")
def base(bars, cal):
    return F.compute(bars, FAMILY_B_ALERTS, cal, normalisers=True)


def replace_opening_range(bars: pd.DataFrame, day: str, seed: int) -> pd.DataFrame:
    """A copy with the day's bars stamped 08:30-08:59 CT replaced by a seeded walk at another level and random
    volumes (stamps kept)."""
    rng = np.random.default_rng(seed)
    out = bars.copy()
    lo, hi = sb.ts_of(day, 8, 30), sb.ts_of(day, 8, 59)
    m = (out["day"].to_numpy() == day) & (out["ts"].to_numpy() >= lo) & (out["ts"].to_numpy() <= hi)
    k = int(m.sum())
    walk = 9000.0 + 0.25 * np.cumsum(np.rint(rng.normal(0.0, 60.0, k)))
    o = walk + 0.25 * np.rint(rng.normal(0.0, 8.0, k))
    out.loc[m, "open"], out.loc[m, "close"] = o, walk
    out.loc[m, "high"] = np.maximum(o, walk) + 0.25 * np.rint(np.abs(rng.normal(0.0, 30.0, k)))
    out.loc[m, "low"] = np.minimum(o, walk) - 0.25 * np.rint(np.abs(rng.normal(0.0, 30.0, k)))
    out.loc[m, "volume"] = rng.integers(1, 80_000, k)
    return out


def test_the_family_is_the_declared_one():
    assert len(FAMILY_B_FEATURES) == 37 and set(EXCLUDED) <= set(F.NAMES)
    assert FAMILY_B_ALERTS[0] == F.slot(10, 5) and FAMILY_B_ALERTS[-1] == F.slot(15, 0) and len(FAMILY_B_ALERTS) == 60


def test_no_used_feature_reads_the_opening_range(bars, base, cal):
    changed = {n: 0 for n in EXCLUDED}
    for i, day in enumerate(DAYS):
        after = F.compute(replace_opening_range(bars, day, int(np.random.default_rng([SEED, 21 + i])
                                                              .integers(1, 2**31))), FAMILY_B_ALERTS, cal)
        a = base[base["day"] == day].reset_index(drop=True)
        b = after[after["day"] == day].reset_index(drop=True)
        assert len(a) == len(FAMILY_B_ALERTS) == len(b)
        for name in FAMILY_B_FEATURES:
            x, y = a[name].to_numpy(), b[name].to_numpy()
            assert np.array_equal(x, y, equal_nan=True), (day, name)
        for name in EXCLUDED:
            changed[name] += int(not np.array_equal(a[name].to_numpy(), b[name].to_numpy(), equal_nan=True))
    # not vacuous: every excluded feature reads the replaced bars at some admitted alert
    assert all(v > 0 for v in changed.values()), changed


def _close_as_of(bars: pd.DataFrame, when: np.ndarray) -> np.ndarray:
    """The close of the last bar stamped at or before each time in `when` -- for each t the value of
    `bars[bars["ts"] <= t]["close"].iloc[-1]`, by one binary search over the bars' time order (Q-96: that per-row scan
    of every bar took most of these tests' time). Refuses bars not in strict time order, or a time before them."""
    ts = bars["ts"].to_numpy()
    assert (np.diff(ts) > 0).all(), "the bars are not in strict time order: the as-of lookup needs it"
    idx = np.searchsorted(ts, np.asarray(when), side="right") - 1
    assert (idx >= 0).all(), "a time before the first bar has no as-of close"
    return bars["close"].to_numpy(dtype=float)[idx]


def _or_quantities(bars: pd.DataFrame, X: pd.DataFrame) -> dict[str, np.ndarray]:
    """Per row of X (a day and an alert): the opening range's width, the position of c in it, its net move and the
    distance of c to its VWAP, each in X's ATR units -- from the bars, independently of the library."""
    local = pd.to_datetime(bars["ts"], unit="s", utc=True).dt.tz_convert(sb.CHICAGO).dt.tz_localize(None)
    slot = ((local.dt.hour * 60 + local.dt.minute - 17 * 60) % 1440).to_numpy()
    orb = bars[(slot >= OR_LO) & (slot < OR_HI)].copy()
    tp = (orb["high"] + orb["low"] + orb["close"]) / 3.0
    g = orb.assign(pv=tp * orb["volume"]).groupby("day")
    per = pd.DataFrame({"H": g["high"].max(), "L": g["low"].min(), "O": g["open"].first(), "C": g["close"].last(),
                        "VW": g["pv"].sum() / g["volume"].sum()})
    rows = per.reindex(X["day"].to_numpy())
    A = X["norm_atr14"].to_numpy()
    c = _close_as_of(bars, X["alert_ts"].to_numpy() - 60)
    H, L, O, C, VW = (rows[k].to_numpy() for k in ("H", "L", "O", "C", "VW"))
    return {"width": (H - L) / A, "position": (c - L) / (H - L), "move": (C - O) / A, "vwap": (c - VW) / A}


def test_the_as_of_close_is_the_per_row_scan_it_replaced(bars, base):
    """Q-96: `_close_as_of` gives, row for row, what the per-row scan gave, on a spread of the admitted alerts."""
    rows = base.iloc[:: max(1, len(base) // 250)]
    want = np.array([float(bars[bars["ts"] <= t - 60]["close"].iloc[-1]) for t in rows["alert_ts"].to_numpy()])
    assert len(want) >= 200 and np.array_equal(_close_as_of(bars, rows["alert_ts"].to_numpy() - 60), want)


def _identical_over_days(x: np.ndarray, y: np.ndarray) -> bool:
    ok = np.isfinite(x) & np.isfinite(y)
    return ok.sum() >= 10 and bool(np.allclose(x[ok], y[ok], rtol=0, atol=1e-12))


def test_no_used_feature_equals_an_opening_range_quantity(bars, base, cal):
    post = base[base["day"] >= "2021-02-05"].reset_index(drop=True)          # after the warm-up
    q = _or_quantities(bars, post)
    hits = []
    for s in FAMILY_B_ALERTS:
        rows = (post["slot"] == s).to_numpy()
        for name in FAMILY_B_FEATURES:
            for qn, qv in q.items():
                if _identical_over_days(post.loc[rows, name].to_numpy(), qv[rows]):
                    hits.append((F.slot_label(s), name, qn))
    assert not hits, hits
    # the harness finds the identity the red team found at the 09:00 alert
    X9 = F.compute(bars, [F.slot(9, 0)], cal, normalisers=True)
    X9 = X9[X9["day"] >= "2021-02-05"].reset_index(drop=True)
    q9 = _or_quantities(bars, X9)
    assert _identical_over_days(X9["range_rth"].to_numpy(), q9["width"])
    assert _identical_over_days(X9["pos_rth"].to_numpy(), q9["position"])
    assert _identical_over_days(X9["or_width"].to_numpy(), q9["width"])


def test_the_draft_declares_these_features():
    text = DRAFT.read_text(encoding="utf-8")
    block = re.search(r"<!-- family-b-features:start -->(.*?)<!-- family-b-features:end -->", text, re.S)
    assert block, "the draft's table of used features is not marked"
    names = re.findall(r"^\| `([a-z0-9_]+)` \|", block.group(1), re.M)
    assert tuple(names) == FAMILY_B_FEATURES


# --------------------------------------------------------------- the fourth draft: the identity, recoverability, m3-1

AS_OF_OFFSETS = (1, 6, 16, 31, 61)        # c, ret_5, ret_15, ret_30 / eff_30 / up_share_30, ret_60 / rv_60's first change


def _slots(bars: pd.DataFrame) -> np.ndarray:
    local = pd.to_datetime(bars["ts"], unit="s", utc=True).dt.tz_convert(sb.CHICAGO).dt.tz_localize(None)
    return ((local.dt.hour * 60 + local.dt.minute - 17 * 60) % 1440).to_numpy()


def or_free_rows(bars: pd.DataFrame, X: pd.DataFrame) -> np.ndarray:
    """The declared per-row rule (m3-1): a row (session, alert slot s) is kept only if the bars the 37 features read
    as of s - 1, s - 6, s - 16, s - 31 and s - 61, and the day's first bar, are none of them stamped 08:30-08:59."""
    sl = _slots(bars)
    by_day = {d: np.sort(sl[(bars["day"] == d).to_numpy()]) for d in X["day"].unique()}
    keep = np.ones(len(X), dtype=bool)
    for i, (d, s) in enumerate(zip(X["day"].to_numpy(), X["slot"].to_numpy())):
        present = by_day[d]
        if present.size == 0 or OR_LO <= present[0] < OR_HI:
            keep[i] = False
            continue
        for off in AS_OF_OFFSETS:
            j = np.searchsorted(present, s - off, side="right") - 1
            if j >= 0 and OR_LO <= present[j] < OR_HI:
                keep[i] = False
                break
    return keep


def test_the_disclosed_identity(bars, base):
    sl = _slots(bars)
    b = bars.assign(slot=sl)
    rows = base[np.isfinite(base["d_pdc"]) & np.isfinite(base["gap"]) & np.isfinite(base["ret_60"])]
    assert len(rows) > 500
    got = (rows["d_pdc"] - rows["gap"] - rows["ret_60"]).to_numpy()
    want = []
    for d, s, A in zip(rows["day"], rows["slot"], rows["norm_atr14"]):
        day = b[b["day"] == d]
        c61 = float(day.loc[day["slot"] <= s - 61, "close"].iloc[-1])
        c829 = float(day.loc[day["slot"] <= OR_LO - 1, "close"].iloc[-1])
        want.append((c61 - c829) / A)
    assert np.allclose(got, np.array(want), rtol=0, atol=1e-9)


def test_linear_recoverability_is_as_disclosed(cal):
    year = sb.generate(sb.Spec(date(2021, 1, 4), date(2021, 12, 31),
                               seed=int(np.random.default_rng([SEED, 29]).integers(1, 2**31))))
    marks = [F.slot(10, 5), F.slot(10, 30), F.slot(12, 0)]
    X = F.compute(year, marks, cal, normalisers=True)
    X = X[X["day"] >= "2021-02-05"].reset_index(drop=True)
    q = _or_quantities(year, X)
    b = year.assign(slot=_slots(year))
    first = b[b["slot"] >= OR_LO].groupby("day")["open"].first()
    c929 = b[b["slot"] <= F.slot(9, 29)].groupby("day")["close"].last()
    q["move60"] = (c929.reindex(X["day"]).to_numpy() - first.reindex(X["day"]).to_numpy()) / X["norm_atr14"].to_numpy()

    def r2(rows, y):
        Z = pd.get_dummies(X.loc[rows, list(FAMILY_B_FEATURES)], columns=["dow"], drop_first=True, dtype=float)
        Zv = Z.to_numpy(dtype=float)
        ok = np.isfinite(Zv).all(1) & np.isfinite(y)
        A = np.c_[np.ones(ok.sum()), Zv[ok]]
        beta, *_ = np.linalg.lstsq(A, y[ok], rcond=None)
        return 1.0 - np.var(y[ok] - A @ beta) / np.var(y[ok])

    for s in marks:
        rows = (X["slot"] == s).to_numpy()
        assert r2(rows, q["width"][rows]) < 0.9, F.slot_label(s)
        assert r2(rows, q["position"][rows]) < 0.9, F.slot_label(s)
    rows = (X["slot"] == F.slot(10, 30)).to_numpy()
    assert r2(rows, q["move60"][rows]) >= 0.99


def test_the_as_of_rule_flags_exactly_the_rows_that_read_the_half_hour(bars, cal):
    day = "2021-03-24"
    sl = _slots(bars)
    gap = (bars["day"].to_numpy() == day) & (sl >= F.slot(9, 0)) & (sl <= F.slot(9, 24))
    holed = bars.loc[~gap].reset_index(drop=True)
    X = F.compute(holed, FAMILY_B_ALERTS, cal)
    keep = or_free_rows(holed, X)
    flagged = X.loc[~keep, ["day", "alert"]]
    assert list(flagged["day"]) == [day] * 5
    assert list(flagged["alert"]) == ["10:05", "10:10", "10:15", "10:20", "10:25"]
    after = F.compute(replace_opening_range(holed, day, int(np.random.default_rng([SEED, 33]).integers(1, 2**31))),
                      FAMILY_B_ALERTS, cal)
    a = X[X["day"] == day].reset_index(drop=True)
    b2 = after[after["day"] == day].reset_index(drop=True)
    k = keep[(X["day"] == day).to_numpy()]
    moved = np.zeros(len(a), dtype=bool)
    for name in FAMILY_B_FEATURES:
        x, y = a[name].to_numpy(), b2[name].to_numpy()
        moved |= ~((x == y) | (np.isnan(x) & np.isnan(y)))
    assert not moved[k].any()                 # every kept row is invariant
    assert moved[~k].all()                    # every flagged row does read the half-hour
