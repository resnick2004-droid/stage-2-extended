"""Q-16 diagnosis (the failure protocol), EXPLORATORY: the lift's power test written before the choice failed for `cons`
on a 300-session calendar. This prints each member's blocks, df and power on the test's own draw, then the same on the
judged block's 657 sessions. Quoted in docs/research/calibration_2026-11-15.md 7.4 and in the test's xfail reason.

    python docs/research/scripts/q16/diag_power.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import numpy as np  # noqa: E402

import test_lift_bound as T  # noqa: E402
from extended import lift_bound as LB  # noqa: E402

rng = np.random.default_rng(20261910)                    # the test's own seed and draw
S, N = T._iid(rng, 4000)
se21 = np.median(LB.t_stats(S, N, block=21, weight="trades")[1])
for b in (21, 42, 63):
    _, G = LB.block_index(300, b)
    r = LB.rejects(f"t{b}w", S + 5 * se21 * N, N, level=0.01).mean()
    print(f"t{b}w: blocks {G}, df {G - 1}, power at 5 t21w-se: {r:.3f}")
print("cons:", LB.rejects("cons", S + 5 * se21 * N, N, level=0.01).mean())
rng = np.random.default_rng([20261910, 657])
S2, N2 = T._iid(rng, 4000, n=657)
se21b = np.median(LB.t_stats(S2, N2, block=21, weight="trades")[1])
se63b = np.median(LB.t_stats(S2, N2, block=63, weight="trades")[1])
for m in ("t21w", "t42w", "t63w", "cons"):
    print("657 sessions", m, "at 5 t21w-se:", LB.rejects(m, S2 + 5 * se21b * N2, N2, level=0.01).mean(),
          "at 5 t63w-se:", LB.rejects(m, S2 + 5 * se63b * N2, N2, level=0.01).mean())
