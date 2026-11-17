"""F-03's run 1 end to end on synthetic inputs (`tests/test_family_o_run1.py` runs it in a process of its own): the
runner's stages A and B (`scripts/fo_opening.py`'s `run1`) with its reads replaced by seams -- no bar, no atlas, no
result value of any design is read.

    python tests/fo_run1_synthetic.py <repository root>       # prints one JSON line last

**The inputs:** `extended/synthetic_bars.py`'s bars (seed `[SEED_TESTS, 700]`, fast: `vol_scale` 10, so overnight 3R brackets
resolve) on 2020-06-01 .. 2020-12-31 and the first quarter of 2021, 2022 and 2023 (each year of stage A's span), a day table
with report days (`b`, the first Friday of each month) and one FOMC day (`f`); every mark 17:00 .. 09:00 admitted; the
walk by this repository's walker; P-16's configuration, plan and money side from the vendored tree (no registered
outcome: the per-R shift is a synthetic constant, the capacity the busiest day, `mean_dv` a constant); the judged
session list 657 synthetic dates (the coin's grid only). The replays are Q-17's adapter's on the synthetic job (both
arms built, the verdict arm run) at six starts; K0 at 200 replications, A10 at 20 selections a class and share, stage B
at 50 draws, A3 at 10 cuts -- a smoke's sizes, so nothing is written (the frame is checked here).
"""
from __future__ import annotations

import json
import sys
import time
from datetime import date
from pathlib import Path

REPO = Path(sys.argv[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
sys.path.insert(0, str(REPO / "scripts"))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import fo_opening as FO  # noqa: E402

from extended import features as F  # noqa: E402
from extended import opening_population as OP  # noqa: E402
from extended import opening_run as R  # noqa: E402
from extended import synthetic_bars as sb  # noqa: E402

t0 = time.time()
SPEC = sb.Spec(date(2020, 6, 1), date(2023, 3, 31), seed=[20261988, 700], rolls=((date(2021, 1, 15), "NQM1"),),
               first_contract="NQH1", holidays=frozenset(), early_closes=frozenset(), vol_scale=10.0)
bars = sb.generate(SPEC)
_d = pd.to_datetime(bars["day"])
bars = bars[(_d.dt.year == 2020) | ((_d.dt.month <= 2) & (_d.dt.day <= 31) & (_d < pd.Timestamp(f"{2021}-03-31")))
            | ((_d.dt.year == 2022) & (_d < pd.Timestamp("2022-03-31"))) | ((_d.dt.year == 2023) & (_d < pd.Timestamp("2023-03-31")))]
bars = bars.reset_index(drop=True)
G = F.grid(bars)
DAYS = [d.isoformat() for d in G.days]
kind = {}
for d in G.days:
    k = "n"
    if d.weekday() == 4 and d.day <= 7:
        k = "b"
    kind[d.isoformat()] = k
kind["2021-01-27"] = "f"
A1 = pd.DataFrame({"date": DAYS, "day_kind": [kind[d] for d in DAYS]})
ARR = {d.isoformat(): tuple(np.r_[np.nan, X[i][:1330]] for X in (G.O, G.H, G.L, G.C)) for i, d in enumerate(G.days)}
ADMITTED = list(range(0, F.slot(9, 0) + 1, 5))
JUDGED = [str(x.date()) for x in pd.bdate_range("2024-01-02", periods=657)]


class SynCtx(FO.Ctx):
    def a1_days(self, start, end):
        return A1.copy()

    def span(self, start, end, all_dates):
        return OP.build_span(DAYS[0], DAYS[-1], all_dates, arrays_for=lambda chunk: (lambda d: ARR[d]),
                             days_table=A1, admitted=ADMITTED, log=lambda m: None)

    def grid(self, start, end, walked):
        return F.grid(bars[bars["day"].astype(str).isin(walked)].reset_index(drop=True))

    def p16(self):
        import a3_brk30_cb20 as Cb
        import atlas_a3 as A
        import zero_edge_decomposition as zd

        from propedge import RESULTS_DIR

        cfg = A.config(A.FAMILY)
        fcfg = A.fv3_config(cfg)
        plan = Cb.noclose_plan(RESULTS_DIR)
        keys = sorted(set(float(x) for x in A.rrs(cfg)) | set(zd.policy_rrs(plan)))
        return {"cfg": cfg, "fcfg": fcfg, "tv": float(A.TICK_VALUE), "plan": plan,
                "e_by": {k: 0.0 for k in keys}, "lb_by": {k: -0.02 for k in keys}, "cap": 200, "keys": keys}

    def restricted_replay_problems(self, job, starts, workers):
        return []

    def mean_dv(self):
        return 1000.0


pre = R.PreRun({q: ["E-999"] for q in R.WAITS}, JUDGED)
ctx = SynCtx(sizes=FO.Sizes(starts=6, k0=200, a10=20, stage_b=50, a3_cuts=10), smoke=True)
code, df, params = FO.run1(ctx, pre, 1)
out = {"code": code, "seconds": round(time.time() - t0, 1)}
if df is not None:
    out["sections"] = sorted(df["section"].unique())
    out["rows"] = int(len(df))
    ch = df[df["section"] == "choice"]
    out["pick"] = R.choice_pick(ch) if (ch["kind"] == "pick").any() else None
    out["killed"] = params.get("killed")
    out["forecast_sha_ok"] = (params.get("forecast_sha256") is not None and
                              len(params["forecast_sha256"]) == 64)
    out["identity_holds"] = [bool(x) for x in df.loc[df["section"] == "identity", "holds"]]
    out["k0_rows"] = int(((df["section"] == "level_control") & (df.get("check") == "K0")).sum())
    out["a10_rows"] = int(((df["section"] == "level_control") & (df.get("check") == "A10")).sum())
    out["openings_rows"] = int((df["section"] == "openings").sum())
    out["wait_rows"] = int((df["section"] == "wait").sum())
    out["forecast_rows"] = int(((df["section"] == "states") & (df.get("kind") == "forecast")).sum())
    out["screen"] = params.get("screen")
    out["param_keys"] = sorted(params)
    out["choice_cells"] = sorted(str(x) for x in ch.loc[ch["kind"] == "cell", "cell"])
    out["choice_finite"] = bool(np.isfinite(pd.to_numeric(ch.loc[ch["kind"] == "cell", "V_B_lower"])).all())
    out["q_B"] = float(pd.to_numeric(ch.loc[ch["kind"] == "q_B", "value"]).iloc[0])
    out["written"] = ctx.write(df, params)


# V2 (the second build read): A10 forced to flag the deciding class `window` (s1's and s2's), so its consequence runs
# inside run 1 -- once for the class (n9), its rows and verdict rows written, any closure counted, stage B continuing


class FlagCtx(SynCtx):
    consequence_calls: list = []

    def a10(self, L, y, selections):
        t = super().a10(L, y, selections)
        t["lax"] = t["lax"] | (t["class"] == "window")
        return t

    def a10_consequence(self, L, model, a_b, z):
        FlagCtx.consequence_calls.append(model)
        return super().a10_consequence(L, model, a_b, z)


fctx = FlagCtx(sizes=FO.Sizes(starts=6, k0=200, a10=20, stage_b=50, a3_cuts=10, a10_inner=200), smoke=True)
t1 = time.time()
code2, df2, params2 = FO.run1(fctx, pre, 1)
v2 = {"code": code2, "calls": list(FlagCtx.consequence_calls), "seconds": round(time.time() - t1, 1)}
if df2 is not None:
    lc = df2[df2["section"] == "level_control"]
    v2["consequence_rows"] = int((lc.get("check") == "A10_consequence").sum())
    vr = lc[lc.get("check") == "A10_consequence_verdict"]
    v2["verdict_cells"] = sorted(str(x) for x in vr["cell"])
    v2["verdict_closed"] = {str(c): bool(x) for c, x in zip(vr["cell"], vr["closed"])}
    v2["killed"] = params2.get("killed")
    ch2 = df2[df2["section"] == "choice"]
    v2["pick_row"] = bool((ch2["kind"] == "pick").any())
    v2["choice_cells"] = sorted(str(x) for x in ch2.loc[ch2["kind"] == "cell", "cell"])
out["v2"] = v2
print(json.dumps(out, default=str))
if "--debug" in sys.argv and df is not None:
    print(df[df["section"] == "supply"].dropna(axis=1, how="all").to_string())
