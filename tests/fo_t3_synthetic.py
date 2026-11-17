"""F-03's T-3 on a synthetic bar store (`tests/test_family_o_t3.py` runs it in a process of its own): run 1's result
sections other than `identity`, and u3's final forecast hash, are byte-identical when every judged-block bar of the
store is replaced by another seeded synthetic walk (the test block's T-3 key, section 16).

    python tests/fo_t3_synthetic.py <repository root> <work folder>      # prints one JSON line last

**The stores.** Two temporary trees, each with a bar store (`vendor/stage2/data/bars/NQ/bars.parquet`, the store's
columns) and A1's day table (`vendor/stage2/data/atlas/A1/days.parquet`) written from `tests/fo_synthetic_data.py`'s
generated bars -- the same "choice block", and a "judged block" generated afresh from a different seed in the second.
Nothing is copied from, or derived from, the licensed data. Run 1 then reads **through `extended/reader.py`** on each
tree (`Ctx.repo`): A1's day table, the bars for the states, the bars for the population's walks -- so the reader's seal
is what keeps the judged block out. Only P-16's registered inputs are replaced by the fixture's (no registered value
is read).
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import time
from pathlib import Path

REPO = Path(sys.argv[1])
WORK = Path(sys.argv[2])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "identity"), str(REPO / "tests")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import pandas as pd  # noqa: E402

import fo_opening as FO  # noqa: E402
import fo_synthetic_data as SD  # noqa: E402

from extended import opening_population as OP  # noqa: E402
from extended import opening_run as R  # noqa: E402
from extended import reader  # noqa: E402

T3_KEY = 100                               # the replacement walk's part of the test block's key (section 16)
t0 = time.time()


def store(tree: Path, fx: SD.Fixture) -> None:
    bars = pd.concat([fx.cb, fx.jb], ignore_index=True).sort_values("ts", kind="stable").reset_index(drop=True)
    b = tree / reader.STORE_REL / "NQ"
    a = tree / reader.ATLAS_REL / "A1"
    b.mkdir(parents=True, exist_ok=True)
    a.mkdir(parents=True, exist_ok=True)
    bars[["ts", "day", "contract", "open", "high", "low", "close", "volume"]].to_parquet(b / "bars.parquet",
                                                                                        index=False)
    pd.concat([fx.A1c, fx.A1j], ignore_index=True).to_parquet(a / "days.parquet", index=False)


class StoreCtx(SD.syn_ctx_class(FO)):
    """The fixture's context with run 1's reads made through the reader on the generated store (`tree`): A1's day
    table, the bars for the states, the bars for the population's walks (handed to the span builder's seams)."""

    tree: Path = None

    def a1_days(self, start, end):
        d = reader.read_walks("A1", "days", start, end, columns=["date", "day_kind"], repo=self.tree, what="T-3")
        return d.assign(date=d["date"].astype(str), day_kind=d["day_kind"].astype(str))

    def _bars(self, start, end):
        return reader.read_bars(start, end, repo=self.tree, what="T-3")

    def grid(self, start, end, walked):
        from extended import features as F

        b = self._bars(start, end)
        return F.grid(b[b["day"].astype(str).isin(walked)].reset_index(drop=True))

    def span(self, start, end, all_dates):
        import numpy as np

        from extended import features as F

        b = self._bars(start, end)
        g = F.grid(b)
        arr = {d.isoformat(): tuple(np.r_[np.nan, X[i][:1330]] for X in (g.O, g.H, g.L, g.C)) for i, d in enumerate(g.days)}
        return OP.build_span(start, end, all_dates, arrays_for=lambda chunk: (lambda d: arr[d]),
                             days_table=self.a1_days(start, end), admitted=SD.ADMITTED, log=lambda m: None)


def run(tree: Path, fx: SD.Fixture):
    ctx = StoreCtx(sizes=FO.Sizes(starts=4, k0=100, a10=10, stage_b=30, a3_cuts=5), smoke=True)
    ctx.tree = tree
    ctx.fx = fx
    pre = R.PreRun({q: ["E-999"] for q in R.WAITS}, fx.judged_sessions)
    code, df, params = FO.run1(ctx, pre, 1)
    body = df[df["section"] != "identity"]
    buf = io.StringIO()
    body.to_csv(buf, index=False)
    return code, buf.getvalue(), params


a_fx, b_fx = SD.Fixture(judged_seed=1), SD.Fixture(judged_seed=T3_KEY)
ta, tb = WORK / "store_a", WORK / "store_b"
store(ta, a_fx)
store(tb, b_fx)
ca, sa, pa = run(ta, a_fx)
cb, sb_, pb = run(tb, b_fx)
judged_differs = not a_fx.jb[["open", "close"]].equals(b_fx.jb[["open", "close"]])
refused = False
try:
    reader.read_bars(str(reader.JUDGED_START), "2024-03-01", repo=ta, what="T-3: a judged read without a purpose")
except reader.JudgedBlockSealed:
    refused = True
out = {"codes": [ca, cb], "judged_bars_differ": judged_differs, "same_sections": sa == sb_,
       "sections_sha256": hashlib.sha256(sa.encode()).hexdigest(), "rows": sa.count("\n"),
       "forecast_same": pa.get("forecast_sha256") == pb.get("forecast_sha256") and pa.get("forecast_sha256") is not None,
       "states_same": pa.get("states_sha256") == pb.get("states_sha256"),
       "population_same": pa.get("population_sha256") == pb.get("population_sha256"),
       "untagged_judged_read_refused": refused, "seconds": round(time.time() - t0, 1)}
print(json.dumps(out))
