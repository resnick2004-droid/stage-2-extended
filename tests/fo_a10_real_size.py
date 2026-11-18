"""F-03's A10 consequence on a toy of the real choice span's size and day-kind mix (the second build read's V2): it runs
on a layout of 2021-2023's ~754 sessions, ~190 marks, kinds n, b, o (FOMC), e (early close) and x (no bar) -- the kinds
B2's declared two bootstraps must leave empty -- at a few selections, and its time per B2 run is measured. Synthetic
values only (`[SEED_TESTS, 1500, ...]`, section 16's test block); nothing is read or written.

    python tests/fo_a10_real_size.py <repository root> [selections] [inner]     # prints one JSON line last
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(sys.argv[1])
sys.path.insert(0, str(REPO))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import opening_stats as ST  # noqa: E402

SEL = int(sys.argv[2]) if len(sys.argv) > 2 else 4
INNER = int(sys.argv[3]) if len(sys.argv) > 3 else 200
rng = np.random.default_rng([ST.SEED_TESTS, 1500, 0])
days = pd.bdate_range("2021-01-04", "2023-12-29")
kinds = np.array(["b" if (d.weekday() == 4 and d.day <= 7) else "n" for d in days], dtype=object)
for k, m in (("o", 24), ("e", 9), ("x", 3)):
    kinds[rng.choice(np.flatnonzero(kinds == "n"), size=m, replace=False)] = k
kinds = kinds.astype(str)
sessions = [str(d.date()) for d in days]
marks = list(range(0, 926, 5))
rows = []
slow = 0.05 * ST.slow_sign(rng, len(sessions))
for i, (s, k) in enumerate(zip(sessions, kinds)):
    walked = k in ("n", "b")
    for m in marks:
        if k == "b" and m < 880:
            continue
        rows.append((s, m, k, int(s[:4]), walked))
pop = pd.DataFrame(rows, columns=["date", "slot", "day_kind", "year", "population"])
pop["c"] = np.where(pop["population"], rng.normal(0, 1.0, len(pop)), np.nan) + \
    np.repeat(slow, pd.Series(pop["date"]).groupby(pop["date"], sort=False).size().reindex(sessions).to_numpy())
L = ST.layout(pop, sessions, kinds=dict(zip(sessions, kinds)), values=("c",))
t0 = time.time()
res = ST.a10_consequence(L, "c", "window", 0.0, selections=SEL, inner=INNER)
secs = time.time() - t0
t1 = time.time()
naive = ST.a10_consequence(L, "c", "window", 0.0, selections=SEL, inner=INNER, shortcut=False)
secs_naive = time.time() - t1
print(json.dumps({"sessions": L.n, "marks": len(L.marks), "kinds": {k: int((kinds == k).sum()) for k in set(kinds)},
                  "offers": int(L.population.sum()), "selections": SEL, "inner": INNER, "b2_runs": res.b2_runs,
                  "seconds": round(secs, 1), "naive_b2_runs": naive.b2_runs, "naive_seconds": round(secs_naive, 1),
                  "seconds_per_b2_replicate": round(secs_naive / max(1, naive.b2_runs * INNER), 5),
                  "closed": res.closed, "same_decisions": res.decisions == naive.decisions}))
