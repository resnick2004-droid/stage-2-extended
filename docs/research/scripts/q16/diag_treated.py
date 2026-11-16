"""Q-16 diagnosis (the failure protocol), EXPLORATORY: the two-sample form on a whole-session filter null (the test's own
draw, seed [20261911, 10]) under both block counts -- every member and their intersection -- and the treated df's spread.
Quoted in docs/research/calibration_2026-11-15.md 7.4 and in the test's xfail reason.

    python docs/research/scripts/q16/diag_treated.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import numpy as np  # noqa: E402

import test_lift_bound as T  # noqa: E402
from extended import lift_bound as LB  # noqa: E402

rng = np.random.default_rng([20261911, 10])
A, B, W, M = T._session_filter_null(rng, 20000)
for rule in ("all", "treated"):
    for m in ("t21w", "t42w", "t63w", "cons"):
        r = LB.diff_many_levels(m, A, B, W, M, [0.01, 0.05], df_rule=rule)[0]
        print(rule, m, "at 1 %:", r[0].mean(), "at 5 %:", r[1].mean())
_, _, df = LB.diff_stats(A, B, W, M, block=21)
print("treated df (21-session blocks), p10 / p50 / p90:", np.percentile(df, [10, 50, 90]))
