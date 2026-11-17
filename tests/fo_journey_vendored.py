"""F-03's scorecard parts against the vendored definitions they follow, in a process of its own
(`tests/test_family_o_journey.py`): `opening_journey.purged_table` is Stage 2's `u_select.block(..., "early", h)` purge
at every horizon the scorecard reads; `FRONTIER_HIGHER` is `user_drivers.FRONTIER_MEASURES`' directions; `luck_rows`'
design-against-luck rows are `user_drivers.variance_split`'s. Synthetic start tables only.

    python tests/fo_journey_vendored.py <repository root>      # prints one JSON line last
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(sys.argv[1])
sys.path.insert(0, str(REPO))
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from propedge.research import u_select as S  # noqa: E402
from propedge.research import user_drivers as UD  # noqa: E402

from extended import opening_journey as J  # noqa: E402
from extended import opening_stats as ST  # noqa: E402

out: dict = {}
dates = [str(d.date()) for d in pd.bdate_range("2020-01-02", "2023-12-29")]
n = len(dates)
first = next(i for i, d in enumerate(dates) if d >= J.CHOICE_FIRST)
starts = list(range(first, n))
t = pd.DataFrame({"start_day": starts, "start_date": [dates[s] for s in starts],
                  "observed": [min(252, n - s) for s in starts]})
rng = np.random.default_rng([ST.SEED_TESTS, 1100, 0])
for m in J.OUTCOME_MONTHS:
    t[f"net_month_{m}"] = np.where(t["observed"] >= 21 * m, rng.normal(size=len(t)), np.nan)
t["months_ahead"] = np.where(t["observed"] >= 63, rng.integers(0, 4, len(t)), np.nan)
records = t[["start_day", "start_date", "observed"]].to_dict("records")
tp = J.purged_table(t)
same = {}
for h in sorted({*S.HORIZONS, 21, 42, 63, 126, 252}):
    want = sorted(int(r["start_day"]) for r in S.block(records, S.EARLY, h))
    got = sorted(int(x) for x in tp.loc[J.eligible(tp, "choice", h), "start_day"])
    same[str(h)] = want == got
out["purge_same"] = same
out["purge_drops_more_than_the_end"] = int((t["observed"] >= 63).sum() - (tp["observed"] >= 63).sum())
out["frontier_same"] = {m: (d == S.HIGHER) for m, d in UD.FRONTIER_MEASURES} == J.FRONTIER_HIGHER
tables = {d: t.assign(**{f"net_month_{m}": t[f"net_month_{m}"] + k for m in J.OUTCOME_MONTHS})
          for k, d in enumerate(("design", "twin", "p16"))}
tables = {d: J.purged_table(x) for d, x in tables.items()}
rows = J.luck_rows(tables, "choice", "verdict", [m for m in J.LUCK_MEASURES if m[0].startswith("net_month")])
r3 = {r["stat"]: r["value"] for r in rows if r["section"] == "design_vs_luck" and r["measure"] == "net_month_3"}
want = UD.variance_split({d: J.measure_values(x, "choice", "net_month_3", 63, "value") for d, x in tables.items()})
out["luck_same"] = all(abs(r3[k] - want[k]) <= 1e-12 for k in want if k != "n")
out["luck_shares_sum"] = r3["design_share"] + r3["start_day_share"]
from extended import user_measures as M  # noqa: E402

ne = {r["measure"]: r for r in rows if r["section"] == "uncertainty" and r["design"] == "design"
      and r["stat"] == "n_eff_bartlett"}
out["n_eff_lags"] = {k: v["lag"] for k, v in ne.items()}
out["n_eff_same"] = all(abs(v["value"] - M.n_eff_bartlett(J.measure_values(tables["design"], "choice", k, v["lag"],
                                                                           "value"), v["lag"])) <= 1e-12
                        for k, v in ne.items() if np.isfinite(v["value"]))
print(json.dumps(out))
