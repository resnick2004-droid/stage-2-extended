"""F-03's W1 (the third build read) on synthetic inputs, in a process of its own (`tests/test_family_o_run2_w1.py`):
run 2 writes stage C's file before `stage_C_scorecard` is authorised, so a scorecard failure leaves the verdict
written; and the choice-block beside's refusing checks run before any judged purpose is authorised. The fixture is
`tests/fo_synthetic_data.py`'s (no bar, walk or registered value read; nothing ledgered); stage C's file goes to a
temporary folder named on the command line.

    python tests/fo_run2_w1.py <repository root> <work folder>      # prints one JSON line last
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO, WORK = Path(sys.argv[1]), Path(sys.argv[2])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "identity"), str(REPO / "tests")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
import fo_opening as FO  # noqa: E402
import fo_synthetic_data as SD  # noqa: E402

from extended import opening_run as R  # noqa: E402

fx = SD.Fixture()
Syn = SD.syn_ctx_class(FO)
pre = R.PreRun({q: ["E-999"] for q in R.WAITS}, fx.judged_sessions)
c1 = Syn(sizes=FO.Sizes(starts=4, k0=200, a10=10, stage_b=30, a3_cuts=5), smoke=True)
c1.fx = fx
code1, df1, par1 = FO.run1(c1, pre, 1)
df1 = df1.copy()
m = (df1["section"] == "choice") & (df1["kind"] == "pick")
df1.loc[m, "cell"] = "s1"
df1.loc[m, "killed"] = False
sizes = FO.Sizes(starts=4, k0=200, b2=100, gate_paths=4, responses=("off",))
out = {"run1_code": code1}

# (a) a choice-beside check fails: run 2 refuses before any judged purpose is authorised
bad = {**par1, "_sha256": "0" * 64,
       "forecast_folds": {k: {**v, "sha256": "f" * 64} for k, v in par1["forecast_folds"].items()}}
ca = Syn(sizes=sizes, smoke=True)
ca.fx = fx
code_a, *_ = FO.run2(ca, pre, 1, df1, bad)
out["precheck"] = {"code": code_a, "authorised": list(ca.authorised)}


# (b) a failure planted at the scorecard stage: stage C's file is already written, the scorecard never ledgered
class Planted(Exception):
    pass


class FailAtScorecard(Syn):
    def authorise(self, purpose):
        if purpose == "stage_C_scorecard":
            raise Planted("a planted scorecard-stage failure")
        super().authorise(purpose)


cb = FailAtScorecard(sizes=sizes, smoke=False, results_dir=WORK)
cb.fx = fx
try:
    FO.run2(cb, pre, 1, df1, {**par1, "_sha256": "0" * 64})
    out["raised"] = False
except Planted:
    out["raised"] = True
f = WORK / f"{FO.RESULT_JUDGED}.csv"
out["judged_written"] = f.is_file() and Path(str(f) + ".manifest.json").is_file()
out["judged_path"] = cb.judged_path
out["authorised"] = list(cb.authorised)
if f.is_file():
    import pandas as pd

    d = pd.read_csv(f, low_memory=False)
    out["judged_sections"] = sorted(d["section"].unique())
    out["verdict_row"] = int(((d["section"] == "level") & (d["line"] == "verdict")).sum())
out["journey_written"] = (WORK / f"{R.JOURNEY}.csv").is_file()
print(json.dumps(out, default=str))
