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
    c = np.array([float(bars[bars["ts"] <= t - 60]["close"].iloc[-1]) for t in X["alert_ts"].to_numpy()])
    H, L, O, C, VW = (rows[k].to_numpy() for k in ("H", "L", "O", "C", "VW"))
    return {"width": (H - L) / A, "position": (c - L) / (H - L), "move": (C - O) / A, "vwap": (c - VW) / A}


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
