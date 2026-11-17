"""F-03's run 2 (stage C and the scorecard) end to end on synthetic inputs (`tests/test_family_o_run2.py` runs it in a
process of its own): `scripts/fo_opening.py`'s `run2` on `tests/fo_synthetic_data.py`'s fixture -- no bar, walk or
result value of any design is read, and no judged-block read happens (the fixture's "judged block" is synthetic, and
`SynCtx.authorise` records each purpose in order instead of ledgering it).

    python tests/fo_run2_synthetic.py <repository root>        # prints one JSON line last

Run 1 runs first on the same fixture (a smoke's sizes); its choice section's pick row is then set to s1, since the
synthetic choice block holds no lift for stage B to pick (a stand-in for the lead's pinned pick, said here). Run 2 runs
at a smoke's sizes: K0 at 200 replications, B2 at 100 replicates a line, the gate at 4 paths, four starts, four
responses. Nothing is written (the frames and parameters are checked here).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(sys.argv[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "identity"), str(REPO / "tests")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import fo_opening as FO  # noqa: E402
import fo_synthetic_data as SD  # noqa: E402

from extended import opening_run as R  # noqa: E402

t0 = time.time()
fx = SD.Fixture()
Syn = SD.syn_ctx_class(FO)
pre = R.PreRun({q: ["E-999"] for q in R.WAITS}, fx.judged_sessions)
c1 = Syn(sizes=FO.Sizes(starts=4, k0=200, a10=10, stage_b=30, a3_cuts=5), smoke=True)
c1.fx = fx
code1, df1, par1 = FO.run1(c1, pre, 1)
out = {"run1_code": code1}
df1 = df1.copy()
m = (df1["section"] == "choice") & (df1["kind"] == "pick")
df1.loc[m, "cell"] = "s1"
df1.loc[m, "killed"] = False
ctx = Syn(sizes=FO.Sizes(starts=4, k0=200, b2=100, gate_paths=4, responses=("off", "denial_25", "forfeit_25", "rtp")),
          smoke=True)
ctx.fx = fx
code, jdf, jjf, par = FO.run2(ctx, pre, 1, df1, {**par1, "_sha256": "0" * 64})
out.update({"code": code, "seconds": round(time.time() - t0, 1), "authorised": list(ctx.authorised)})
if jdf is not None:
    out["sections"] = sorted(jdf["section"].unique())
    lv = jdf[jdf["section"] == "level"]
    out["lines"] = sorted(str(x) for x in lv["line"].dropna().unique())
    out["verdict"] = str(lv.loc[lv["line"] == "verdict", "verdict"].iloc[0])
    fl = jdf[jdf["section"] == "floor"]
    out["floors"] = sorted(str(x) for x in fl["floor"].unique())
    out["floor_iii_seed_role"] = str(fl.loc[fl["floor"] == "iii", "seed_role"].iloc[0])
    bs = jdf[jdf["section"] == "beside"]
    out["beside"] = sorted(str(x) for x in bs["reading"].dropna().unique())
    out["c1_bound_finite"] = bool(np.isfinite(pd.to_numeric(lv.loc[lv["line"] == "C1", "bound"])).all())
    out["k0_forms"] = sorted(str(x) for x in lv.loc[lv["line"] == "K0", "form"])
    out["journey_sections"] = sorted(str(x) for x in jjf["section"].dropna().unique())
    out["journey_designs"] = sorted(str(x) for x in jjf["design"].dropna().unique())
    out["journey_responses"] = sorted(str(x) for x in jjf.get("response", pd.Series(dtype=str)).dropna().unique())
    out["paired_against"] = sorted(str(x) for x in jjf.loc[jjf["section"] == "paired", "against"].unique())
    out["journey_blocks"] = sorted(str(x) for x in jjf.get("block", pd.Series(dtype=str)).dropna().unique())
    pr = jjf[jjf["section"] == "paired"]
    out["paired_stats"] = sorted(str(x) for x in pr["stat"].dropna().unique())
    out["paired_blocks"] = sorted(str(x) for x in pr["block"].dropna().unique())
    out["bm63c_note"] = bool(pr.loc[pr["stat"] == "bm63c_0.05", "note"].astype(str).str.contains("not pinned").all())
    w = jjf[jjf["section"] == "wait"]
    out["wait_measures"] = sorted(str(x) for x in w["measure"].dropna().unique())
    out["wait_designs"] = sorted(str(x) for x in w["design"].dropna().unique())
    out["wait_against"] = int((w["stat"] == "minus_p16").sum())
    ev = jjf[jjf["section"] == "evenness_curve"]
    out["evenness_blocks"] = sorted(str(x) for x in ev["block"].dropna().unique())
    out["luck_rows"] = int((jjf["section"] == "design_vs_luck").sum())
    fr = jjf[jjf["section"] == "frontier"]
    out["frontier_blocks"] = sorted(str(x) for x in fr["block"].dropna().unique())
    ch = jjf[jjf.get("block", pd.Series(dtype=str)) == "choice"]
    out["choice_sections"] = sorted(str(x) for x in ch["section"].dropna().unique())
    bs2 = jdf[jdf["section"] == "beside"]
    out["floor_iv_v"] = [bool(fl.loc[fl["floor"] == k, "holds"].iloc[0]) for k in ("iv", "v")]
    out["floor_v_row"] = fl[fl["floor"] == "v"].dropna(axis=1).to_dict("records")
    out["beside_0735"] = int((bs2["reading"] == "report_day_0735_openings").sum())
    out["params"] = sorted(par)
    out["written"] = ctx.write_stage_c(jdf, jjf, par)
print(json.dumps(out, default=str))
