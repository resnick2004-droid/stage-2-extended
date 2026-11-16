"""Q-16 diagnosis (the failure protocol), EXPLORATORY: the P module's first placeholder (`obm126`) failed its fixed-null
size test. This prints (1) the test's own draw (seed 20261910) for the batch-type candidates, (2) their rates on iid
normal series (exact by construction), (3) each batch variance's expectation against the true variance of the mean on
that MA(21) null, (4) the rate on 200,000 fresh replications. Quoted in docs/research/calibration_2026-11-15.md 7.4.

    python docs/research/scripts/q16/diag_obm.py
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from extended import p_bound as PB  # noqa: E402


def ma(rng, reps, n=595, q=21):
    e = rng.standard_normal((n + q - 1, reps))
    c = np.cumsum(np.vstack([np.zeros((1, reps)), e]), axis=0)
    return (c[q:] - c[:-q])[:n] / math.sqrt(q)


rng = np.random.default_rng(20261910)                    # the test's own seed and draw
D = ma(rng, 20000)
for m in ("obm63", "obm126", "bm63", "bm126"):
    print("test draw MA21", m, {a: int(PB.rejects(m, D, level=a).sum()) for a in (0.01, 0.05)})
rng2 = np.random.default_rng([20261912, 100])
Z = rng2.standard_normal((595, 40000))
for m in ("obm63", "obm126", "bm63", "bm126"):
    print("iid", m, {a: float(PB.rejects(m, Z, level=a).mean()) for a in (0.01, 0.05)})
q, n = 21, 595
rho = np.array([(q - k) / q for k in range(q)])
true_var = (1 + 2 * sum((1 - k / n) * rho[k] for k in range(1, q))) / n
print("E[var obm126]/true", float((PB.obm(D, 126)[1] ** 2).mean() / true_var),
      "obm63", float((PB.obm(D, 63)[1] ** 2).mean() / true_var),
      "bm63", float((PB.batch_t(D, batches=9)[1] ** 2).mean() / true_var))
rng3 = np.random.default_rng([20261912, 101])
k = 0
for _ in range(10):
    k += int(PB.rejects("obm126", ma(rng3, 20000), level=0.01).sum())
print("obm126 MA21 at 1 % over 200,000 fresh replications:", k / 200000)
