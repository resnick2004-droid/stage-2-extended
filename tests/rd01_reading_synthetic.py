"""RD-01's reading end to end on toy campaigns (`scripts/rd01_reading.py`'s three purposes into a temporary results
folder), run by `tests/test_rd01_reading.py` in a process of its own. Synthetic trades only (seed 20261992, the build's
toy campaigns): two toy streams standing for P-16 and P-14, each with a point arm and a verdict arm shifted per R as
`gate.shifted_blocks` shifts it; dates across 2023 and 2024 so the early and late blocks both hold starts.

    python tests/rd01_reading_synthetic.py <repository root>        # prints one JSON line last
"""
from __future__ import annotations

import dataclasses
import json
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(sys.argv[1])
for _p in (str(REPO), str(REPO / "identity"), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import rd01_reading as RDR  # noqa: E402

from extended import firm_reading as R  # noqa: E402
from extended import firm_terms as T  # noqa: E402
from extended import user_beside as B  # noqa: E402
from extended import walker as W  # noqa: E402
from extended.gate import run_gate  # noqa: E402
from extended.results import read_manifest, read_result  # noqa: E402
from propedge.campaign.gate import shifted_blocks  # noqa: E402
from propedge.campaign.lockstep import ConductModel  # noqa: E402
from propedge.campaign.payout_method import payout_method_terms  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy, Tiers  # noqa: E402
from propedge.campaign.sizing import CURRENT_TIER, SizingRule  # noqa: E402
from propedge.contract.adapter import rules_from_ledger  # noqa: E402
from propedge.contract.rules import load_rules  # noqa: E402
from propedge.outcomes.distribution import DayBlock  # noqa: E402

SEED = 20261992
#: m2: the second toy stream a child of section 12's toy seed (20261993 is reserved, never drawn)
KIDS = np.random.SeedSequence(SEED).spawn(2)
RS = (1.0, 1.5, 2.0, 2.5, 3.0)
TV, FEE, N_DAYS, STARTS = 0.5, 1.22, 150, 5
out: dict = {}
t_all = time.time()


def toy(seed: int, start: str) -> tuple[list[DayBlock], list[str]]:
    rng = np.random.default_rng(seed)
    days = [d.date().isoformat() for d in pd.bdate_range(start, periods=N_DAYS)]
    blocks = []
    for i in range(N_DAYS):
        k = int(rng.integers(0, 4))
        S = rng.choice([40, 60, 80], size=k).astype(float)
        c = (TV + FEE) / (S * TV)
        mfe = rng.exponential(S * 2.2)
        stop = rng.random(k) < 0.6
        p = np.floor(mfe * rng.uniform(0, 0.9, size=k))
        term = np.where(stop, -1.0 - (2 * TV + FEE) / (S * TV), (p - 2) / S - c)
        entry = np.array([W.bar_of(8, 40) + 50 * j for j in range(k)], float)
        r_by, mae_by, ex_by = {}, {}, {}
        for R_ in RS:
            tt = np.array([W.target_ticks(R_, int(x)) for x in S], float)
            won = mfe >= tt
            r_by[R_] = np.where(won, tt / S - c, term)
            mae_by[R_] = np.where(won, 0.4, np.maximum(0.4, -term))
            ex_by[R_] = entry + np.where(won, 30.0, 120.0)
        risked = S * TV * 4
        blocks.append(DayBlock(pnl=r_by[2.0] * risked, risked=risked, exit_reasons=tuple("x" for _ in range(k)),
                               risk_per_contract=S * TV, mae=mae_by[2.0] * risked, entry_t=entry, exit_t=ex_by[2.0],
                               r_by_rr=r_by, mae_by_rr=mae_by, fee=np.full(k, FEE), sides=np.ones(k),
                               exit_by_rr=ex_by))
    return blocks, days


RULES = rules_from_ledger()
SIZING = dataclasses.replace(SizingRule.from_ledger(CURRENT_TIER), fee_schedule=T.fee_schedule("TS"))
PROTO = Protocol(name="rd01_toy", combine_rr=2.0, combine_risk=300.0, funded_rr=2.0, funded_risk=300.0,
                 trades_per_day=4, max_concurrent_accounts=5)
POLICY = RiskPolicy(id="rd01_toy", root=Phase(
    combine=Tiers("balance", ((-1e9, Leaf("combine base", 300.0, 2.0)), (3000.0, Leaf("combine top", 150.0, 2.0)))),
    funded=Tiers("request_day", ((0.0, Leaf("funded", 250.0, 2.0)), (1.0, Leaf("request day", 250.0, 1.5))))))
LAG = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)


def args() -> dict:
    return {"draws": {"protocol": PROTO, "mode": "rotation", "flip": None, "sizing": SIZING},
            "path": dict(edge=0.0, rules=RULES, initial_bankroll=1e9, max_concurrent_accounts=5,
                         subscription=float(RULES.subscription), billing_days=int(RULES.billing_days),
                         activation=float(RULES.activation), payout_lag_days=LAG, max_concurrent_combines=5,
                         max_total_accounts=5, conduct=ConductModel(rtp=False, enforcement_p=0.0),
                         combine_max_days=2000, funded_horizon_days=100_000, purchase_budget=(20, 21),
                         risk_policy=POLICY),
            "seed": B.SEED_BLOCK[1]}


DELTA = {R_: -0.03 - 0.01 * i for i, R_ in enumerate(RS)}
streams, gates = {}, {}
for name, seed, start in (("p16", SEED, "2023-08-01"), ("p14", KIDS[0], "2023-08-01")):
    pt, days = toy(seed, start)
    vd = shifted_blocks(pt, DELTA[2.0], DELTA)
    streams[name] = {"jobs": {"point": {"engine": "single", "blocks": pt, "dates": days, "args": args()},
                              "verdict": {"engine": "single", "blocks": vd, "dates": days, "args": args()}},
                     "config": None}
    e_by = {R_: float(np.nanmean(np.concatenate([b.r_by_rr[R_] for b in pt if len(b.pnl)]))) for R_ in RS}
    lb_by = {R_: e_by[R_] + DELTA[R_] for R_ in RS}
    gates[name] = {"blocks": pt, "hook_factory": None, "ref": None,
                   "kw": dict(e=e_by[2.0], lb=lb_by[2.0], e_by_rr=e_by, lb_by_rr=lb_by, protocol=PROTO,
                              bankroll=1e6, horizon_days=60, n_paths=2, seed=SEED, accounts=5, sizing=SIZING,
                              rules=RULES, levels=(0.0,), risk_policy=POLICY, purchase_budget=(20, 21),
                              rtp=False)}

# ------------------------------------------------------------------------------------------------ the scorecard
names = ["TS-16", "TS-14", "DT-16-s", "DT-16-price", "FP-16-s", "QP-16-s", "QP-16-req", "LU-16-l"]
runs = [r for r in T.RUNS if r.name in names]
t0 = time.time()
rows, table, probs = RDR.scorecard_reading(streams, runs, STARTS, coverage=False)
df = pd.DataFrame(rows)
out["sc_problems"] = probs[:6]
out["sc_runs"] = sorted(set(df["run"].dropna()))
out["sc_sections"] = sorted(set(df["section"]))
out["sc_rows"] = len(df)
out["sc_starts_rows"] = len(table)
paired = df[(df["section"] == "paired") & (df["run"] == "DT-16-s") & (df["stat"] == "mean")]
out["sc_paired_blocks"] = sorted(set(paired["block"]))
out["sc_paired_months"] = sorted({int(m) for m in paired["month"]})
grid = df[(df["section"] == "price_grid") & (df["run"] == "DT-16-s") & (df["measure"] == "P") & (df["block"] == "all")]
out["sc_grid_prices"] = sorted({float(p) for p in grid["price"]})
pv = grid.sort_values("price")["value"].to_numpy(float)
out["sc_grid_P_falls_with_price"] = bool(np.all(np.diff(pv[np.isfinite(pv)]) <= 1e-12))
out["sc_break_even"] = sorted(set(df[df["section"] == "break_even"]["measure"]))
cnt = df[(df["section"] == "counts") & (df["run"] == "FP-16-s")].set_index("measure")["value"].to_dict()
out["sc_fp_counts"] = {k: cnt.get(k) for k in ("trades", "fee_off_schedule", "funded.forced_untraded",
                                              "share_starts_differing_by_63", "contracts_compared")}
dtc = df[(df["section"] == "counts") & (df["run"] == "DT-16-s")].set_index("measure")["value"].to_dict()
out["sc_dt_counts"] = {k: dtc.get(k) for k in ("martingale_per_account", "martingale_firm_wide", "funded.q")}
out["sc_tier1"] = int((df["section"] == "tier1_count").sum())
ids = df[(df["section"] == "identity_items_4_5")]
out["sc_items_4_5"] = {k: float(ids[ids["measure"] == k]["value"].sum()) for k in ("trades", "accounts")}
out["sc_seconds"] = round(time.time() - t0, 1)

# the pro fee: DT's readings carry it (the card's fees differ from the A-9 outputs' where a Pro account lived 21+ sessions)
out["sc_dt_fee_rows"] = int(((df["section"] == "scorecard") & (df["run"] == "DT-16-s")).sum())

# ------------------------------------------------------------------------------------------------ the ladder
t0 = time.time()
lrows, lprobs = RDR.ladder_reading(streams, 3)
ld = pd.DataFrame(lrows)
out["ld_problems"] = lprobs[:6]
out["ld_runs"] = sorted(set(ld["run"]))
out["ld_responses"] = sorted(set(ld["response"]))
out["ld_seconds"] = round(time.time() - t0, 1)

# ------------------------------------------------------------------------------------------------ the gate
t0 = time.time()
grows, gpaths, gprobs = RDR.gate_reading(2, 1, gates=gates, run_gate=run_gate)
gd = pd.DataFrame(grows)
out["gt_problems"] = gprobs
out["gt_runs"] = len(set(gd["run"]))
out["gt_readings_qp"] = sorted(set(gd[gd["plan"] == "QP"]["reading"]))
out["gt_readings_dt"] = sorted(set(gd[gd["plan"] == "DT"]["reading"]))
out["gt_labels_fp"] = sorted(set(gd[gd["plan"] == "FP"]["labels"]))
out["gt_seconds"] = round(time.time() - t0, 1)

# ------------------------------------------------------------------------------------------------ the files
with tempfile.TemporaryDirectory(prefix="rd01_e2e_") as td:
    wrote = []
    params = {"declaration": R.DECLARATION, "toy": True, "seeds": RDR.SEEDS, "code_blobs": RDR.code_blobs()}
    wrote += RDR.write_all("firm_scorecard", [df, table], {**params, "purpose": "firm_scorecard"}, Path(td))
    wrote += RDR.write_all("firm_ladder_beside", [ld], {**params, "purpose": "firm_ladder_beside"}, Path(td))
    wrote += RDR.write_all("firm_gate_beside", [gd, gpaths if len(gpaths) else pd.DataFrame({"x": []})],
                           {**params, "purpose": "firm_gate_beside"}, Path(td))
    out["files"] = sorted(wrote)
    m = read_manifest(Path(td) / "rd01_scorecard.csv")
    md = m if isinstance(m, dict) else dataclasses.asdict(m) if dataclasses.is_dataclass(m) else vars(m)
    out["manifest_keys"] = sorted(k for k in md if k in ("git_commit", "parameters", "prereg_id", "script", "seed",
                                                          "sha256", "provenance"))
    out["manifest_prereg"] = md.get("prereg_id")
    out["read_back_rows"] = len(read_result(Path(td) / "rd01_scorecard.csv"))
    blobs = md["parameters"]["code_blobs"]
    out["manifest_blobs"] = [len(blobs), all(len(v) == 40 for v in blobs.values())]
out["seconds"] = round(time.time() - t_all, 1)
print(json.dumps(out, default=str))
