"""Q-11: the feature library on a full synthetic year -- its time, its shape, and the chunked computation equal to the
one-shot one bit for bit (so the full development window can be computed a year at a time). Seed 20261140, fixed for
this file; synthetic bars only."""
from __future__ import annotations

import time
from datetime import date

import numpy as np

from extended import features as F
from extended import synthetic_bars as sb

SEED_YEAR = 20261140
LIMIT_S = 30.0          # the bound the suite enforces; measured about 0.3 s on the development machine (Q-11)


def test_full_synthetic_year_is_fast_and_whole(capsys):
    bars = sb.generate(sb.Spec(date(2021, 1, 4), date(2021, 12, 31), seed=SEED_YEAR))
    cal = F.load_calendars()
    t0 = time.perf_counter()
    X = F.compute(bars, calendars=cal, normalisers=True)
    took = time.perf_counter() - t0
    n_days = bars["day"].nunique()
    assert len(X) == n_days * len(F.ALERT_MARKS)
    with capsys.disabled():
        print(f"\n[Q-11] features on a synthetic year: {len(bars):,} bars, {n_days} days, {len(X):,} rows x "
              f"{len(F.NAMES)} features in {took:.2f} s")
    assert took < LIMIT_S
    Y = F.compute_chunked(bars, calendars=cal, normalisers=True, chunk_days=60)
    assert list(Y.columns) == list(X.columns) and len(Y) == len(X)
    for name in X.columns:
        a, b = X[name].to_numpy(), Y[name].to_numpy()
        if a.dtype.kind == "f":
            assert np.array_equal(a, b, equal_nan=True), name
        else:
            assert (a == b).all(), name
