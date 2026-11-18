"""F-03's T-3 replacement below every loader (V1 of the second build read), in a process of its own
(`tests/test_family_o_t3_wrapper.py`): on a small generated synthetic store (never the licensed data), a choice-block
read through the reader enters the wrapper and replaces nothing; a planted judged read through the vendored loader is caught
and counted; a wrapper never entered refuses; the loaders are restored on exit.

    python tests/fo_t3_wrapper.py <repository root> <work folder>      # prints one JSON line last
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

REPO, WORK = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(REPO))
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
import pandas as pd  # noqa: E402

from extended import opening_stats as ST  # noqa: E402
from extended import opening_t3 as T3  # noqa: E402
from extended import reader  # noqa: E402
from extended import synthetic_bars as sb  # noqa: E402
import importlib  # noqa: E402

#: the planted forbidden read this test exists to catch: Stage 2's own bar loader, called past the reader's seal (by
#: name, so the one-door scan -- which forbids it everywhere else -- is not tripped by the plant itself)
VB = importlib.import_module("propedge.data." + "bars")

bars = sb.generate(sb.Spec(date(2023, 12, 18), date(2024, 1, 12), seed=[ST.SEED_TESTS, 100, 1], vol_scale=10.0))
store = WORK / reader.STORE_REL
(store / "NQ").mkdir(parents=True, exist_ok=True)
path = store / "NQ" / "bars.parquet"
bars[["ts", "day", "contract", "open", "high", "low", "close", "volume"]].to_parquet(path, index=False)
out = {}
orig = pd.read_parquet
with T3.JudgedReplacement(roots=[WORK / "vendor" / "stage2" / "data"]) as jr:
    b = reader.read_bars("2023-12-18", "2023-12-29", repo=WORK, what="T-3 wrapper test: a choice read")
    out["choice"] = {"entered": jr.entered, "replaced": jr.rows_replaced, "verdict": jr.verdict(), "rows": len(b)}
    j = VB.read_bars("NQ", "2024-01-02", "2024-01-12", "development", store=store, what="a planted judged read")
    want = bars[bars["day"].astype(str) >= "2024-01-02"]
    out["planted"] = {"replaced": jr.rows_replaced, "verdict": jr.verdict(),
                      "prices_moved": bool((j["close"].to_numpy() != want.sort_values("ts")["close"].to_numpy()).any())}
out["restored"] = pd.read_parquet is orig
with T3.JudgedReplacement(roots=[WORK / "nowhere"]) as idle:
    reader.read_bars("2023-12-18", "2023-12-29", repo=WORK, what="T-3 wrapper test: outside the roots")
out["idle_verdict"] = idle.verdict()
print(json.dumps(out, default=str))
