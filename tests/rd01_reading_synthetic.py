"""RD-01's reading end to end on toy campaigns (`scripts/rd01_reading.py`'s three stages and section 15's three files
into a temporary results folder), run by `tests/test_rd01_reading.py` in a process of its own. Synthetic trades only
(seed: section 12's toy seed and its children): two toy streams standing for P-16 and P-14, each with a point arm and a
verdict arm shifted per R as `gate.shifted_blocks` shifts it (the shift recorded as the stream's registered delta, as
`firm_reading.build_with_deltas` records U1's); dates across 2023 and 2024 so the early and late blocks both hold
starts, and on CPI days a trade open at 07:28 CT and one entered inside the window. Coverage is on, at a small series
count passed through (R1), and on tiled toy records long enough for intervals to form; the negative controls show each
refusing check refuses.

    python tests/rd01_reading_synthetic.py <repository root>        # prints one JSON line last
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

REPO = Path(sys.argv[1])
for _p in (str(REPO), str(REPO / "identity"), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import rd01_reading as RDR  # noqa: E402

from extended import firm_accounts as A  # noqa: E402
from extended import firm_counts as C  # noqa: E402
from extended import firm_reading as R  # noqa: E402
from extended import firm_terms as T  # noqa: E402
from extended import user_beside as B  # noqa: E402
from extended import user_readings as UR  # noqa: E402
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
from propedge.research import u_select as S  # noqa: E402

SEED = R.F.LADDER_SEED + 2                      # section 12's toy seed
KIDS = np.random.SeedSequence(SEED).spawn(3)   # m2: every other toy draw a child of it
RS = (1.0, 1.5, 2.0, 2.5, 3.0)
TV, FEE, N_DAYS, STARTS = 0.5, 1.22, 150, 5
COV_SERIES = 40
out: dict = {}
t_all = time.time()


def toy(seed, start: str) -> tuple[list[DayBlock], list[str]]:
    rng = np.random.default_rng(seed)
    days = [d.date().isoformat() for d in pd.bdate_range(start, periods=N_DAYS)]
    cpi = {d.isoformat() for d, k in C.tier1_days().items() if "cpi" in k}
    blocks = []
    for i in range(N_DAYS):
        k = int(rng.integers(0, 6))
        S_ = rng.choice([40, 60, 80], size=k).astype(float)
        c = (TV + FEE) / (S_ * TV)
        mfe = rng.exponential(S_ * 2.2)
        stop = rng.random(k) < 0.6
        p = np.floor(mfe * rng.uniform(0, 0.9, size=k))
        term = np.where(stop, -1.0 - (2 * TV + FEE) / (S_ * TV), (p - 2) / S_ - c)
        entry = np.array([W.bar_of(8, 40) + 50 * j for j in range(k)], float)
        hold = np.full(k, 120.0)
        if days[i] in cpi and k >= 2:                # a trade open at 07:28 CT, and one entered inside the window
            entry[0], hold[0] = float(W.bar_of(7, 0)), 60.0
            entry[1] = float(W.bar_of(7, 29))
        r_by, mae_by, ex_by = {}, {}, {}
        for R_ in RS:
            tt = np.array([W.target_ticks(R_, int(x)) for x in S_], float)
            won = mfe >= tt
            r_by[R_] = np.where(won, tt / S_ - c, term)
            mae_by[R_] = np.where(won, 0.4, np.maximum(0.4, -term))
            ex_by[R_] = entry + np.where(won, np.minimum(30.0, hold), hold)
        risked = S_ * TV * 4
        blocks.append(DayBlock(pnl=r_by[2.0] * risked, risked=risked, exit_reasons=tuple("x" for _ in range(k)),
                               risk_per_contract=S_ * TV, mae=mae_by[2.0] * risked, entry_t=entry, exit_t=ex_by[2.0],
                               r_by_rr=r_by, mae_by_rr=mae_by, fee=np.full(k, FEE), sides=np.ones(k),
                               exit_by_rr=ex_by))
    return blocks, days


RULES = rules_from_ledger()
SIZING = dataclasses.replace(SizingRule.from_ledger(CURRENT_TIER), fee_schedule=T.fee_schedule("TS"))
PROTO = Protocol(name="rd01_toy", combine_rr=2.0, combine_risk=700.0, funded_rr=2.0, funded_risk=300.0,
                 trades_per_day=5, max_concurrent_accounts=5)
POLICY = RiskPolicy(id="rd01_toy", root=Phase(
    combine=Tiers("balance", ((-1e9, Leaf("combine base", 700.0, 2.0)), (3000.0, Leaf("combine top", 150.0, 2.0)))),
    funded=Tiers("request_day", ((0.0, Leaf("funded", 250.0, 2.0)), (1.0, Leaf("request day", 250.0, 1.5))))))
LAG = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
#: the registered replays' never-binding bankroll (D-312). Not the build's earlier $1e9: at that magnitude the cash
#: series' float error over Quick Pay's many fractional-cent payouts reached U1's millionth-of-a-dollar fee check (a
#: start read 1104.000001 against 1104.0 -- diagnosed: the engine's totals agree to 1e-12, the cash series carries the
#: error), which at the registered $1e8 is about ten standard deviations away
import score_fv3_grid as _gf  # noqa: E402

UNBOUND = float(_gf.UNBOUND_BANKROLL)


def args() -> dict:
    return {"draws": {"protocol": PROTO, "mode": "rotation", "flip": None, "sizing": SIZING},
            "path": dict(edge=0.0, rules=RULES, initial_bankroll=UNBOUND, max_concurrent_accounts=5,
                         subscription=float(RULES.subscription), billing_days=int(RULES.billing_days),
                         activation=float(RULES.activation), payout_lag_days=LAG, max_concurrent_combines=5,
                         max_total_accounts=5, conduct=ConductModel(rtp=False, enforcement_p=0.0),
                         combine_max_days=2000, funded_horizon_days=100_000, purchase_budget=(20, 21),
                         risk_policy=POLICY),
            "seed": B.SEED_BLOCK[1]}


DELTA = {R_: -0.03 - 0.01 * i for i, R_ in enumerate(RS)}
streams, gates = {}, {}
for name, seed in (("p16", KIDS[0]), ("p14", KIDS[1])):
    pt, days = toy(seed, "2023-08-01")
    vd = shifted_blocks(pt, DELTA[2.0], DELTA)
    streams[name] = {"jobs": {"point": {"engine": "single", "blocks": pt, "dates": days, "args": args()},
                              "verdict": {"engine": "single", "blocks": vd, "dates": days, "args": args()}},
                     "config": None, "delta": {"verdict": (DELTA[2.0], DELTA)}}
    e_by = {R_: float(np.nanmean(np.concatenate([b.r_by_rr[R_] for b in pt if len(b.pnl)]))) for R_ in RS}
    lb_by = {R_: e_by[R_] + DELTA[R_] for R_ in RS}
    gates[name] = {"blocks": pt, "hook_factory": None, "ref": None, "fresh_rr": 2.0,
                   "kw": dict(e=e_by[2.0], lb=lb_by[2.0], e_by_rr=e_by, lb_by_rr=lb_by, protocol=PROTO,
                              bankroll=1e6, horizon_days=60, n_paths=4, seed=SEED, accounts=5, sizing=SIZING,
                              rules=RULES, levels=(0.0,), risk_policy=POLICY, purchase_budget=(20, 21),
                              rtp=False)}
out["toy_tier1"] = {k: len(v) for k, v in C.tier1_trades(streams["p16"]["jobs"]["point"]["blocks"],
                                                         streams["p16"]["jobs"]["point"]["dates"]).items()}

# ------------------------------------------------------------------------------------------------ the scorecard
names = ["TS-16", "TS-14", "DT-16-s", "DT-16-price", "FP-16-s", "QP-16-s", "QP-16-req", "LU-16-l"]
runs = [r for r in T.RUNS if r.name in names]
t0 = time.time()
sc_spill, ran = RDR.scorecard_reading(streams, runs, STARTS, coverage=True, coverage_series=COV_SERIES)
df = sc_spill.frame()
out["sc_ran"] = ran
out["sc_sections"] = sorted(set(df["section"]))
out["sc_subsections"] = sorted(set(df["subsection"].dropna()))
paired = df[(df["section"] == "paired") & (df["subsection"] == "net_month") & (df["run"] == "DT-16-s")
            & (df["stat"] == "mean")]
out["sc_paired_blocks"] = sorted(set(paired["block"]))
out["sc_paired_months"] = sorted({int(m) for m in paired["month"]})
card = df[(df["section"] == "scorecard") & (df["subsection"] == "card")]
out["sc_card_blocks"] = sorted(set(card["block"]))                  # R6: the early block in every reading
out["sc_extra_blocks"] = sorted(set(df[(df["section"] == "scorecard") & (df["subsection"] == "extra")]["block"]))
out["sc_path_blocks"] = sorted(set(df[(df["section"] == "scorecard") & (df["subsection"] == "path")]["block"]))
out["sc_kinds"] = sorted(set(card["kind"].dropna()))                # the run's kind, not U1's response kind
grid = df[(df["section"] == "grid") & (df["subsection"] == "price_grid") & (df["run"] == "DT-16-s")
          & (df["measure"] == "P") & (df["block"] == "all")]
out["sc_grid_prices"] = sorted({float(p) for p in grid["price"]})
falls = []
for _arm, g_ in grid.groupby("arm"):                # each arm's P, in price order
    pv = g_.sort_values("price")["value"].to_numpy(float)
    falls.append(bool(np.all(np.diff(pv[np.isfinite(pv)]) <= 1e-12)))
out["sc_grid_P_falls_with_price"] = [len(falls), all(falls)]
be = df[(df["section"] == "grid") & (df["subsection"] == "break_even")]
out["sc_break_even"] = sorted(set(be[be["run"] == "DT-16-s"]["measure"]))
out["sc_break_even_lucid"] = sorted(set(be[be["run"] == "LU-16-l"]["note"].astype(str)))     # r3
out["sc_a10_held"] = int(((df["section"] == "oracle") & (df["subsection"] == "a10")).sum())
cnt = df[(df["section"] == "mechanics") & (df["subsection"] == "count") & (df["block"] == "all")]


def counts_of(run: str, arm: str = "point") -> dict[str, float]:
    c = cnt[(cnt["run"] == run) & (cnt["arm"] == arm)]
    return dict(zip(c["measure"], c["value"].astype(float)))


fp, dt, qp, qr, lu, ts = (counts_of(r) for r in ("FP-16-s", "DT-16-s", "QP-16-s", "QP-16-req", "LU-16-l", "TS-16"))
out["fp_keys"] = sorted(k for k in fp if not k.startswith("acct."))
out["dt_keys"] = sorted(k for k in dt if not k.startswith("acct."))
out["qp_keys"] = sorted(k for k in qp if not k.startswith("acct."))
out["lu_keys"] = sorted(k for k in lu if k.startswith("lu_"))
out["fp_counts"] = {k: fp.get(k) for k in ("trades_taken", "oracle_trades_fee_checked", "oracle_requests_checked",
                                            "acct.funded.forced_untraded", "acct.funded.forced_day_dealt_elsewhere",
                                            "acct.funded.forced_day_dealt_to_none", "fp_funded_trades_read",
                                            "contracts_compared.funded", "tier1_signals_skipped_inside",
                                            "tier1_executed_in_window", "g10_funded_accounts")}
out["dt_counts"] = {k: dt.get(k) for k in ("martingale_per_account", "acct.combine.dll_days", "acct.funded.q",
                                            "acct.combine.lost_after_limit", "acct.combine.failed_while_owed",
                                            "oracle_requests_checked", "fees_pro", "dt_limit_capped_trades")}
out["qp_counts"] = {k: qp.get(k) for k in ("acct.funded.floor_oracle_breaches", "oracle_requests_checked",
                                            "zero_qp_request_below_min", "g10_funded_sessions_no_trade")}
out["qr_requests"] = qr.get("oracle_requests_checked")
out["ts_counts"] = {k: ts.get(k) for k in ("oracle_trades_fee_checked", "oracle_requests_checked", "trades_taken")}
out["count_blocks"] = sorted(set(df[(df["section"] == "mechanics") & (df["subsection"] == "count")]["block"]))
out["diverge_blocks"] = sorted(set(df[df["section"] == "diverge"]["block"]))
out["diverge_measures"] = sorted(set(df[df["section"] == "diverge"]["measure"]))
starts_ = df[(df["section"] == "scorecard") & (df["subsection"] == "start")]
out["start_rows"] = len(starts_)
out["start_has_item6"] = all(c in starts_ for c in R.DIVERGE)
out["tier1_rows"] = int(((df["section"] == "mechanics") & (df["subsection"] == "tier1_count")).sum())
ids = df[(df["section"] == "identity") & (df["subsection"] == "items_4_5")]
out["items_4_5"] = {k: float(ids[ids["measure"] == k]["value"].sum()) for k in ("starts_compared", "trades", "accounts")}
out["sc_seconds"] = round(time.time() - t0, 1)

# R6: the user readings' early and late blocks are u_select's (the toy's TS starts)
st16 = starts_[(starts_["run"] == "TS-16") & (starts_["arm"] == "point")].copy()
st16["start_day"] = st16["start_day"].astype(int)
st16["observed"] = st16["observed"].astype(int)
same = []
for h in (21, 63):
    for b in ("early", "late"):
        want = {int(r["start_day"]) for r in S.block(st16.to_dict("records"), b, h)}
        got = set(st16["start_day"][UR._elig(st16, b, h)])
        same.append(want == got)
out["elig_is_u_select"] = all(same)
out["elig_judged_is_late"] = bool((UR._elig(st16, "judged", 21) == UR._elig(st16, "late", 21)).all())

# R1: coverage by keyword where intervals form -- a toy record tiled over enough late starts
R._COVERAGE.clear()
cj, _kw = R.cell_job(streams["p16"]["jobs"]["point"], T.settings_for("TS", "reference"),
                     streams["p16"]["jobs"]["point"]["blocks"])
real = R.run_cell("p16", "point", B.BY_NAME["off"], cj, T.settings_for("TS", "reference"), [0], {}, None,
                  direct=False)["outs"][0]["rec"]
rng = np.random.default_rng(KIDS[2])
plan_t, ts_t = [], []
for i in range(9 * 63 + 63):
    d0 = (pd.Timestamp("2024-01-02") + pd.tseries.offsets.BDay(i)).date().isoformat()
    for lst in (plan_t, ts_t):
        lst.append({**real, "start_day": i, "start_date": d0, "observed": 252, "alt": {},
                    "net_month": [float(x) for x in rng.normal(0, 100, 12)]})
prow = R.paired_rows(plan_t, ts_t, coverage=True, coverage_series=COV_SERIES)
cov = [r for r in prow if r["stat"] == "coverage"]
out["tiled_coverage_rows"] = len(cov)
out["tiled_coverage_in_unit"] = bool(cov) and all(0.0 <= r["value"] <= 1.0 for r in cov)
out["tiled_coverage_settings"] = sorted(f"{h}:{n}" for h, n in R._COVERAGE)
out["coverage_shapes_per_setting"] = sorted({len(v) for v in R._COVERAGE.values()})
out["coverage_section_rows"] = len(R.coverage_rows())

# ------------------------------------------------------------------------------------------------ the ladder
t0 = time.time()
ld_spill, lran = RDR.ladder_reading(streams, 3)
ld = ld_spill.frame()
out["ld_ran"] = lran
out["ld_runs"] = sorted(set(ld["run"]))
out["ld_responses"] = sorted(set(ld["response_name"]))
out["ld_blocks"] = sorted(set(ld[(ld["section"] == "ladder") & (ld["subsection"] == "card")]["block"]))
out["ld_start_rows"] = int(((ld["section"] == "ladder") & (ld["subsection"] == "start")).sum())
out["ld_item5"] = float(ld[(ld["section"] == "identity") & (ld["measure"] == "accounts")]["value"].sum())
out["ld_seconds"] = round(time.time() - t0, 1)

# ------------------------------------------------------------------------------------------------ the gate
t0 = time.time()
grows, orows, gran = RDR.gate_reading(4, 1, gates=gates, run_gate=run_gate)
gd = pd.DataFrame(grows)
od = pd.DataFrame(orows)
out["gt_ran"] = gran
out["gt_runs"] = len(set(gd["run"]))
out["gt_readings_qp"] = sorted(set(gd[gd["plan"] == "QP"]["reading"].dropna()))
out["gt_labels_fp"] = sorted(set(gd[gd["plan"] == "FP"]["labels"].dropna()))
out["gt_oracle_measures"] = sorted(set(od["measure"]))
out["gt_oracle_stats"] = sorted(set(od["stat"]))
out["gt_oracle_rows"] = len(od)
tw = gd[gd["reading"] == "zero_edge"]
out["gt_twin_ceilings"] = sorted({(float(a), float(b)) for a, b in zip(tw["twin_gross_per_funded_ceiling"],
                                                                       tw["twin_pass_rate_ceiling"])})
out["gt_twin_finite"] = bool(np.isfinite(tw["twin_pass_rate"].astype(float)).all())
out["gt_seconds"] = round(time.time() - t0, 1)

# ------------------------------------------------------------------------------------------------ negative controls
neg: dict = {}
s_fp = T.settings_for("FP", T.STRICT)
led = [{"contracts": 26, "fee": R.schedule_fee("FP", None, 26), "historical_day": 0}]
neg["fee_held"] = R.fee_problems(led, s_fp) == []
neg["fee_refused"] = bool(R.fee_problems([{**led[0], "fee": led[0]["fee"] + 0.01}], s_fp))
neg["fee_missing_refused"] = bool(R.fee_problems([{"contracts": 3, "historical_day": 0}], s_fp))
want26 = 2 * T.fee_schedule("FP")[1] + 6 * T.fee_schedule("FP")[0]
neg["fee_26_micros"] = abs(R.schedule_fee("FP", None, 26) - want26) < 1e-12
t_qp = T.plan_terms("QP")
neg["qp_split_page_example"] = abs(R.tiered_net("QP", 3000.0, 6000.0)
                                   - (t_qp.split_high * 2000 + t_qp.split_low * 1000)) < 1e-9


def fake_d(req: float, net: float, gross: float, before: float, after: float, kind: str = "request") -> dict:
    f = SimpleNamespace(index=0, payout_cash=(net,), gross_paid=gross)
    log = [{"day": 5, "request": req, "before": before, "after": after, "net": net, "kind": kind}]
    return {"long": SimpleNamespace(funded=(f,)), "counts": [{"kind": "funded", "index": 0, "requests": log}],
            "exact": None, "exact_counts": {}, "split": 1.0, "payout_fee": 0.0, "payout_min": 0.0, "std_cap": 1e9}


s_dt = T.settings_for("DT", T.STRICT)
neg["dt_request_held"] = R.request_problems(fake_d(1000.0, 1000.0, 1000.0, 4000.0, 3000.0), s_dt)[0] == []
neg["dt_increment_refused"] = bool(R.request_problems(fake_d(1010.0, 1010.0, 1010.0, 4010.0, 3000.0), s_dt)[0])
neg["dt_left_refused"] = bool(R.request_problems(fake_d(1000.0, 1000.0, 1000.0, 2900.0, 1900.0), s_dt)[0])
neg["dt_net_refused"] = bool(R.request_problems(fake_d(1000.0, 990.0, 1000.0, 4000.0, 3000.0), s_dt)[0])
s_q = T.settings_for("QP", T.STRICT)
neg["qp_split_refused"] = bool(R.request_problems(fake_d(500.0, 400.0, 500.0, 1000.0, 500.0), s_q)[0])
neg["qp_split_held"] = R.request_problems(fake_d(500.0, R.tiered_net("QP", 500.0, 1000.0), 500.0, 1000.0, 500.0),
                                          s_q)[0] == []
neg["fp_cap_refused"] = bool(R.request_problems(fake_d(1600.0, 1280.0, 1600.0, 4000.0, 2400.0), s_fp)[0])
neg["fp_half_counted"] = R.request_problems(fake_d(1500.0, 1200.0, 1500.0, 2000.0, 500.0), s_fp)[2][
    "zero_fp_request_above_half_profit"]
s_ts = T.settings_for("TS", "reference")
d_ts = {"long": SimpleNamespace(funded=(SimpleNamespace(index=0, payout_cash=(900.0,), gross_paid=1000.0),)),
        "counts": [], "exact": None, "exact_counts": {}, "split": 0.9, "payout_fee": 0.0, "payout_min": 500.0,
        "std_cap": 2000.0}
neg["ts_held"] = R.request_problems(d_ts, s_ts)[0] == []
neg["ts_gross_refused"] = bool(R.request_problems({**d_ts, "long": SimpleNamespace(funded=(SimpleNamespace(
    index=0, payout_cash=(900.0,), gross_paid=1100.0),))}, s_ts)[0])
cap, pcap = R.twin_bounds(s_dt, RULES)
neg["twin_bounds_dt"] = [cap, round(pcap, 12)]
neg["twin_held"] = R.twin_problems({"twin_gross_per_funded": cap + 10, "twin_gross_per_funded_se": 50.0,
                                    "twin_pass_rate": pcap + 0.01, "twin_pass_rate_se": 0.01}, s_dt, RULES) == []
neg["twin_refused"] = bool(R.twin_problems({"twin_gross_per_funded": cap + 500, "twin_gross_per_funded_se": 10.0,
                                            "twin_pass_rate": 0.3, "twin_pass_rate_se": 0.01}, s_dt, RULES))
pt16 = streams["p16"]["jobs"]["point"]["blocks"]
neg["delta_held"] = R.delta_problems(pt16, streams["p16"]["jobs"]["verdict"]["blocks"], (DELTA[2.0], DELTA)) == []
neg["delta_refused"] = bool(R.delta_problems(pt16, streams["p16"]["jobs"]["verdict"]["blocks"],
                                             (DELTA[2.0], {k: v + 1e-6 for k, v in DELTA.items()})))
import customer_slices as cs                        # r6: the registered shift captured as U1's builder makes the arm

camp = cs.Campaign("toy", pt16, list(streams["p16"]["jobs"]["point"]["dates"]),
                   {"e": 0.11, "lb": 0.08, "e_by_rr": {R_: 0.1 for R_ in RS}, "lb_by_rr": {R_: 0.1 + DELTA[R_] for R_ in RS}})
orig_arm_blocks = cs.arm_blocks
made, seen = R.build_with_deltas(lambda: {a_: cs.arm_blocks(camp, a_) for a_ in ("point", "verdict")})
neg["capture"] = [len(seen), abs(seen[0][0] - (0.08 - 0.11)) < 1e-15,
                  all(abs(seen[0][1][R_] - ((0.1 + DELTA[R_]) - 0.1)) < 1e-15 for R_ in RS),
                  cs.arm_blocks is orig_arm_blocks]
neg["captured_reproduces_the_arm"] = R.delta_problems(pt16, made["verdict"], seen[0]) == []
bad_streams = {k: {**v, "delta": {"verdict": (DELTA[2.0] + 1e-6, DELTA)}} for k, v in streams.items()}
try:
    RDR.scorecard_reading(bad_streams, runs[:1], 2, coverage=False)
    neg["scorecard_stops_on_a_wrong_delta"] = False
except R.Refused as exc:
    neg["scorecard_stops_on_a_wrong_delta"] = "r6" in str(exc)
try:                                               # r5: a cell's refusal stops the run before the next cell
    import extended.firm_reading as RR

    orig = RR.fee_problems
    RR.fee_problems = lambda ledger, s: ["planted"] if s.plan == "DT" else []
    seen = []
    RDR.scorecard_reading(streams, [r for r in runs if r.name in ("TS-16", "DT-16-s", "FP-16-s")], 2, coverage=False,
                          log=lambda *a, **k: seen.append(a[0]))
    neg["stops_at_first_refusal"] = False
except R.Refused as exc:
    neg["stops_at_first_refusal"] = ("planted" in str(exc) and not any("FP-16-s" in x for x in seen))
finally:
    RR.fee_problems = orig


class Router:                                     # a router stand-in: slot k of the day dealt `lst[k]`
    def __init__(self, lst, n):
        self.lst, self.table, self.n_trades = lst, SimpleNamespace(historical_day=lambda t: 0), [n]

    def trade_index(self, key, t, slot):
        return self.lst[slot] if slot < len(self.lst) else None

    def assignments(self, t):
        return {("funded", 0): [j for j in self.lst if j is not None], ("combine", 1): [9]}


drw = SimpleNamespace(router=Router([3, 5, 7, None], 12), key=("combine", 0), relative_days=True,
                      last_trade={"trade_index": 5})
neg["g12_lost_after_stop"] = A.dealt_after_stop(drw, 4, 4)               # slot 2's trade 7 was dealt, not taken
neg["g12_none_when_last"] = A.dealt_after_stop(SimpleNamespace(**{**vars(drw), "last_trade": {"trade_index": 7}}),
                                               4, 4)
neg["fp_forced_day_signals"] = list(A.day_signals(drw, 4))                 # dealt 3, 5, 7 and 9 of 12 offered


class RoutedStub:                                  # a DayTraders evaluation's draw: each slot's dealt trade, a P&L
    settlement = "pessimistic"
    relative_days = True

    def __init__(self, pnls, dealt):
        self.pnls, self.router, self.key, self.last_trade = list(pnls), Router(dealt, len(dealt)), ("combine", 0), None

    def __call__(self, n, day, slot, cushion, **kw):
        j = self.router.trade_index(self.key, day, slot)
        if j is None or not self.pnls:
            self.last_trade = None
            return np.array([np.nan])
        self.last_trade = {"trade_index": j}
        return np.array([self.pnls.pop(0)])


DT_RULES = R.F.plan_rules(RULES, s_dt)
POL4 = SimpleNamespace(trades_per_day=4, stop_day_on_win=False, stop_day_on_loss=False)
dtc = A.CLASSES[("DT", "combine", False)](index=0, purchase_day=0, draw=RoutedStub([-800.0, -800.0], [0, 1, 2, 3]),
                                         floor_start=-float(DT_RULES.mll))
dtc.trade_day(DT_RULES, POL4, 1, 1)
neg["g12_in_the_adapter"] = [dtc.dll_days, dtc.lost_after_limit, round(float(dtc.last_day_pnl), 6), bool(dtc.failed)]
dtw = A.CLASSES[("DT", "combine", False)](index=0, purchase_day=0, draw=RoutedStub([100.0] + [-800.0] * 8, [0, 1]),
                                         floor_start=-float(DT_RULES.mll))
dtw.B, dtw.best_day, dtw.qualifying_days = 3100.0, 300.0, 1           # at target with a Qualifying Day owed
for k in range(1, 7):
    if dtw.failed:
        break
    dtw.trade_day(DT_RULES, SimpleNamespace(trades_per_day=2 if k > 1 else 1, stop_day_on_win=False,
                                            stop_day_on_loss=False), k, k)
neg["failed_while_owed"] = [dtw.sessions_held, bool(dtw.failed), dtw.failed_while_owed, dtw.qualifying_days]
neg["n4_refused"] = bool(A.logging_share_problem(dataclasses.replace(SIZING, stand_aside=(("combine", 0.5, 0.0),))))
neg["n4_held"] = A.logging_share_problem(dataclasses.replace(SIZING, stand_aside=(("combine", 0.0, 22.5),))) is None
fp_rule = dataclasses.replace(R.F.plan_sizing(SIZING, s_fp), room_cap=None)
neg["uncapped_none_below_cap"] = R.uncapped_ladder_differs(
    [{"kind": "funded", "index": 0, "day": 3, "balance_before": 500.0, "risk_per_contract": 30.0,
      "intended_risk": 300.0, "contracts": 10, "room": 5000.0}], fp_rule)[0]
neg["uncapped_differs_at_9000"] = R.uncapped_ladder_differs(
    [{"kind": "funded", "index": 0, "day": 3, "balance_before": 9000.0, "risk_per_contract": 30.0,
      "intended_risk": 3000.0, "contracts": fp_rule.cap_micros("funded", 9000.0), "room": 1e9}], fp_rule)[0]
# 10.1 item 5's flag on a hand-made paired card: a plan whose two corners straddle TS
card_toy = pd.DataFrame([{"section": "paired", "subsection": "card", "run": run_, "plan": "DT", "stream": "P-16",
                          "arm": "verdict", "corner": c_, "flip": "", "kind": "corner", "request_rule": "",
                          "block": "all", "measure": "P", "stat": st_, "value": v_}
                         for run_, c_, pl, tsv in (("DT-16-s", "strict", 0.40, 0.45), ("DT-16-l", "lenient", 0.50, 0.45))
                         for st_, v_ in (("plan", pl), ("ts", tsv))])
from extended import firm_menu as FM  # noqa: E402

fl = FM.flag_rows(card_toy)
neg["flag_unread_terms"] = [r["raised"] for r in fl if r.get("flag") == "depends on its unread terms"
                            and r.get("arm") == "verdict"]
out["neg"] = neg

# ------------------------------------------------------------------------------------------------ the third read's
# the single pass (g): A-9's own replays captured are the outputs it gives without the capture, bit for bit, and their
# ledger, counts and request logs are the second build's direct replays' (the route it replaces)
from user_beside_identity import first_difference  # noqa: E402

third: dict = {}
for rname, s_ in (("TS-16", T.settings_for("TS", "reference")), ("DT-16-s", T.settings_for("DT", T.STRICT)),
                  ("FP-16-s", T.settings_for("FP", T.STRICT)), ("QP-16-s", T.settings_for("QP", T.STRICT))):
    for arm in ("point", "verdict"):
        job = streams["p16"]["jobs"][arm]
        blocks_, ref_, _ = R.arm_inputs(streams["p16"]["jobs"]["point"], job, s_, arm,
                                        streams["p16"]["delta"].get(arm))
        cj_, kw_ = R.cell_job(job, s_, blocks_)
        plain = R.F.run_plan("p16", arm, B.BY_NAME["off"], cj_, s_, [0, 37, 74], kw_, point=ref_)
        capt = R.F.run_plan("p16", arm, B.BY_NAME["off"], cj_, s_, [0, 37, 74], kw_, point=ref_, capture=True)
        same_out = all(not first_difference(a_[0], b_[0]) for a_, b_ in zip(plain, capt))
        same_led = True
        for (o_, by_, got_), st_ in zip(capt, [0, 37, 74]):
            dc = R.captured_start(cj_, s_, st_, kw_, ref_, B.BY_NAME["off"], 1, by_, got_)
            dd = R.direct_start("p16", arm, B.BY_NAME["off"], cj_, s_, st_, kw_, ref_, 1)
            same_led &= (dc["ledger"] == dd["ledger"] and dc["counts"] == dd["counts"]
                         and dc["exact_counts"] == dd["exact_counts"]
                         and sorted(dc["exact"] or {}) == sorted(dd["exact"] or {}))
        third[f"{rname}|{arm}"] = [same_out, same_led]
out["single_pass"] = third

# the break-even search: the shared one gives the plain search's answers exactly, with fewer recompositions
be_cmp = {}
for rname, s_ in (("DT-16-s", T.settings_for("DT", T.STRICT)), ("FP-16-s", T.settings_for("FP", T.STRICT)),
                  ("LU-16-l", T.settings_for("LU", T.LENIENT))):
    job = streams["p16"]["jobs"]["point"]
    blocks_, ref_, _ = R.arm_inputs(job, job, s_, "point")
    cj_, kw_ = R.cell_job(job, s_, blocks_)
    cell_ = R.run_cell("p16", "point", B.BY_NAME["off"], cj_, s_, [0, 37, 74, 111], kw_, ref_, direct=True)
    tsj, tkw = R.cell_job(job, T.settings_for("TS", "reference"), job["blocks"])
    ts_recs = [o["rec"] for o in R.run_cell("p16", "point", B.BY_NAME["off"], tsj, T.settings_for("TS", "reference"),
                                            [0, 37, 74, 111], tkw, None, direct=False)["outs"]]
    a_rows, _ = R.grid_rows(cell_, "p16", "point", B.BY_NAME["off"], s_, ts_recs, search="known")
    b_rows, _ = R.grid_rows(cell_, "p16", "point", B.BY_NAME["off"], s_, ts_recs, search="plain")
    ka = {r["measure"]: (r["price"], r["n"]) for r in a_rows if r["subsection"] == "break_even"}
    kb = {r["measure"]: (r["price"], r["n"]) for r in b_rows if r["subsection"] == "break_even"}
    be_cmp[rname] = {m: [repr(ka[m][0]) == repr(kb[m][0]), ka[m][1], kb[m][1]] for m in ka}
out["break_even_same"] = be_cmp
# and on a toy measure with a crossing inside a grid cell, at a cent's resolution
fs = {"lin": lambda x: 1.0 - x / 200.0, "step": lambda x: 0.0 if x > 137.3 else 1.0}
known_cmp = {}
for nm, fn in fs.items():
    calls = []
    grid_ = {q: fn(q) for q in T.DT_PRICE_GRID}
    a1 = R.break_even_known(lambda x: (calls.append(x), fn(x))[1], 0.3, grid_, 0.0, 250.0, 0.01)
    plain_calls = []
    a2 = R.F.break_even_price(lambda x: (plain_calls.append(x), fn(x))[1], 0.3, 0.0, 250.0, tol=0.01)
    known_cmp[nm] = [repr(a1) == repr(a2), len(calls), len(plain_calls)]
out["break_even_toy"] = known_cmp

# m3: the uncapped ladder's control refuses a rebuild that misses a trade's own contracts
fp_rule3 = dataclasses.replace(R.F.plan_sizing(SIZING, T.settings_for("FP", T.STRICT)), room_cap=None)
row3 = {"kind": "funded", "index": 0, "day": 3, "balance_before": 500.0, "risk_per_contract": 30.0,
        "intended_risk": 300.0, "contracts": 10, "room": 5000.0}
out["uncapped_control"] = [R.uncapped_ladder_differs([row3], fp_rule3)[2],
                           R.uncapped_ladder_differs([{**row3, "contracts": 9}], fp_rule3)[2]]

# m2 and n3: G-10 on hand-made funded records (a CPI-free stretch of the toy's dates)
ctx3 = R.stream_context("p16", streams["p16"]["jobs"]["point"])
F3 = lambda **kw: SimpleNamespace(**{"index": 0, "activation_day": 1, "ended_on": None, "closed": False, "days": 40,  # noqa: E731
                                     "balance": 10.0, "floor": 0.0, **kw})
d30 = {"kind": "funded", "index": 0}
out["g10"] = {
    "drained_open": R.g10_counts([F3()], [], ctx3, 0, 60)["g10_accounts_drained"],
    "drained_ended": R.g10_counts([F3(ended_on=30)], [], ctx3, 0, 60)["g10_accounts_drained"],
    "drained_breached": R.g10_counts([F3(closed=True, ended_on=30)], [], ctx3, 0, 60)["g10_accounts_drained"],
}
k31 = next(k for k in range(2, 60) if (R._date_of(ctx3, 0, k) - R._date_of(ctx3, 0, 1)).days >= 31)
out["g10"]["idle_gaps"] = [(R._date_of(ctx3, 0, k) - R._date_of(ctx3, 0, 1)).days for k in (k31 - 1, k31)]
out["g10"]["idle_at"] = [R.g10_counts([F3(balance=5000.0, ended_on=k)], [{**d30, "day": 1}], ctx3, 0, 60)
                         ["g10_accounts_idle_30"] for k in (k31 - 1, k31)]

# m4 and m5: the twin call's sizing carries no fee schedule; its pass rate is over resolved evaluations
seen_sz = []


def spy_gate(blocks, **kw):
    seen_sz.append(kw["sizing"].fee_schedule)
    return run_gate(blocks, **kw)


R.gate_rows(gates["p16"]["blocks"], gates["p16"]["kw"], T.settings_for("DT", T.LENIENT), spy_gate, fresh_rr=2.0)
out["twin_fees"] = [list(seen_sz[0]) if seen_sz[0] is not None else None, seen_sz[1]]
lp_toy = SimpleNamespace(funded=(), combines=(SimpleNamespace(passed=True, failed=False),
                                              SimpleNamespace(passed=False, failed=True),
                                              SimpleNamespace(passed=False, failed=False)))
tm = R.twin_measures([lp_toy, lp_toy])
out["twin_resolved"] = [tm["twin_pass_rate"], tm["twin_evaluations_resolved"],
                        tm["twin_evaluations_unresolved_or_closed"]]

# m6 and n5: the menu's windows on start positions
x6 = np.arange(4 * 63 * 2, dtype=float) % 7 - 3.0
gap = x6.copy()
gap[5:9] = np.nan                                         # a gap inside a kept window: still its window
hole = x6.copy()
hole[0:63] = np.nan                                       # a kept window with no value: no interval
cov6 = {(63, 4): 0.9}
r_gap = FM._reading(gap, 63, cov6, paired=True)
r_hole = FM._reading(hole, 63, cov6, paired=True)
r_zero = FM._reading(np.zeros(8 * 63), 63, cov6, paired=False)
out["menu_windows"] = [r_gap["n_w"], "interval_lo" in r_gap, r_gap.get("coverage"), r_hole["note"], r_zero["note"],
                       FM._reading(np.zeros(8 * 63), 63, cov6, paired=True)["note"]]
out["coverage_settings"] = sorted(R.coverage_settings(plan_t))

# M1: U1's own reported lines on the tiled records, by block
u1t = R.u1_reported_rows(plan_t)
out["u1_lines"] = sorted({r["stat"] for r in u1t})
out["u1_keys"] = sorted({r["measure"].split("@")[0] for r in u1t if not r["measure"].startswith("luck:share_paid")})
out["u1_years"] = sorted({r["measure"] for r in u1t if r["measure"].startswith("luck:share_paid")})
out["u1_blocks"] = sorted({r["block"] for r in u1t})
la = R.luck_across({"a": u1t, "b": R.u1_reported_rows(ts_t)})
out["u1_luck_runs"] = sorted({r["run"] for r in la})

# the guards, on this tree: no decision row yet records the waited identities, so the run refuses
probs, found = RDR.identity_problems()
out["guard_refuses"] = [bool(probs), sorted(p.split(" ")[0] for p in probs), found]
pin, pbad = RDR.pin_row()
out["pin"] = [pin["row"] if pin else None, pbad]
entries, ebad = RDR.record_entries()
out["record_entries"] = [len(entries), ebad[:3], sorted({e["plan"] for e in entries}),
                         all(e["date_read"] not in ("", "None") for e in entries)]

# ------------------------------------------------------------------------------------------------ the files
with tempfile.TemporaryDirectory(prefix="rd01_e2e_") as td:
    toy_found = {"Q-7": {"row": "E-000", "sha": "ab" * 20, "head": "cd" * 20, "what": "a toy identity"}}
    params = RDR.manifest_params(toy_found, pin, entries, RULES, argparse.Namespace(repeat=None, workers=1), "toy")
    params["toy"] = True
    counts = {**ran, **lran, **gran}
    # the scorecard's own coverage rows are empty on five starts; the tiled check's settings stand in for them; the
    # rows spilled to a folder and read back once, as the run does (m7)
    spill = RDR.Spill(Path(td) / "rows")
    spill.add(RDR.identity_rows(toy_found, pin))
    for part in (df, ld):
        spill.add(part.to_dict("records"))
    spill.add(R.coverage_rows() + orows)
    out["spill_parts"] = len(list((Path(td) / "rows").glob("*.pkl")))
    wrote = RDR.write_all(spill, grows, params, Path(td), counts)
    out["files"] = sorted(wrote)
    fr = read_result(Path(td) / "fc_reading.csv")
    if os.environ.get("RD01_PROBE_DUMP"):                     # scripts/rd01_cost_probe.py's files stage, on request
        fr.to_pickle(os.environ["RD01_PROBE_DUMP"])
    fg = read_result(Path(td) / "fc_gate.csv")
    fm = read_result(Path(td) / "fc_menu.csv")
    out["fr_sections"] = sorted(set(fr["section"]))
    raw = (Path(td) / "fc_reading.csv").read_text(encoding="utf-8")
    ident = fr[(fr["section"] == "identity") & (fr["subsection"] == "waited")]
    out["fr_identity"] = [list(ident["row"]), [str(x)[:4] for x in ident["sha"]], [str(x)[:4] for x in ident["head"]],
                          "identity-holds" in raw, "identity-holds" in (Path(td) / "fc_reading.csv.manifest.json"
                                                                        ).read_text(encoding="utf-8")]
    out["fr_u1_lines"] = sorted(set(fr[(fr["section"] == "scorecard") & (fr["subsection"] == "u1_reported")]["stat"]))
    out["fr_u1_paired"] = sorted(set(fr[(fr["section"] == "paired") & (fr["subsection"] == "u1_reported")]["stat"]))
    out["fr_u1_luck"] = int(((fr["section"] == "scorecard") & (fr["subsection"] == "u1_luck")).sum())
    out["fr_months_ahead_u1"] = bool(pd.to_numeric(fr[fr["subsection"] == "start"]["months_ahead_u1"],
                                                   errors="coerce").notna().any())
    out["fm_year_measures"] = sorted(set(fm[(fm["section"] == "menu") & fm["block"].astype(str).str.startswith("year_")]
                                         ["measure"]))
    out["fr_status"] = sorted(set(fr["status"])) + sorted(set(fg["status"])) + sorted(set(fm["status"]))
    out["fm_sections"] = sorted(set(fm["section"]))
    out["fm_flags"] = sorted(set(fm[fm["section"] == "flags"]["flag"].dropna()))
    out["fm_menu_labels_qp"] = sorted({x for v in fm[(fm["section"] == "menu") & (fm["plan"] == "QP")]["labels"].dropna()
                                       for x in str(v).split("; ") if x.startswith("QP's request rule")})
    out["fm_menu_runs"] = sorted(set(fm[fm["section"] == "menu"]["run"].dropna()))
    out["fm_paired_more_measures"] = len(set(fm[fm["section"] == "paired_more"]["measure"]))
    out["fm_variance_rows"] = int((fm["section"] == "variance_share").sum())
    out["fm_evenness_rows"] = int((fm["section"] == "evenness").sum())
    out["fm_distribution_rows"] = int((fm["section"] == "distribution").sum())
    m = read_manifest(Path(td) / "fc_reading.csv")
    md = m if isinstance(m, dict) else dataclasses.asdict(m) if dataclasses.is_dataclass(m) else vars(m)
    pm = md["parameters"]
    out["manifest"] = {"prereg_id": md.get("prereg_id"), "exploratory": md.get("exploratory"),
                       "variant_count": md.get("variant_count"),
                       "keys": sorted(k for k in pm if k in ("pinning_row", "identity_rows", "run_counts",
                                                            "cost_and_table_inputs", "seeds", "readings",
                                                            "record_entries", "data_manifest_sha256", "status",
                                                            "horizon_of_month", "conventions"))}
    out["manifest_seeds"] = [len(pm["seeds"]["block"]),
                             sorted({v.split(":")[0].split(",")[0] for v in pm["seeds"]["block"].values()})]
    out["manifest_counts"] = {k: pm["run_counts"].get(k) for k in ("replays", "new", "references", "ladder_replays",
                                                                  "gates")}
    out["manifest_plans"] = sorted(pm["cost_and_table_inputs"])
    out["manifest_dt_schedules"] = sorted(pm["cost_and_table_inputs"]["DT"]["cost_schedule_round_turn_micro_mini"])
    out["manifest_month_9"] = pm["horizon_of_month"].get("9")
    out["manifest_data_sha"] = len(str(pm["data_manifest_sha256"]))
    mm = read_manifest(Path(td) / "fc_menu.csv")
    mmd = mm if isinstance(mm, dict) else dataclasses.asdict(mm) if dataclasses.is_dataclass(mm) else vars(mm)
    out["menu_manifest_step"] = "fc_reading.csv" in str(mmd["parameters"].get("step"))
    out["bytes"] = {p.name: p.stat().st_size for p in Path(td).glob("*.csv")}
    out["rows"] = {"fc_reading": len(fr), "fc_gate": len(fg), "fc_menu": len(fm)}
    out["start_rows_by_section"] = {s_: int(((fr["section"] == s_) & (fr["subsection"] == "start")).sum())
                                    for s_ in ("scorecard", "ladder")}
out["seconds"] = round(time.time() - t_all, 1)
print(json.dumps(out, default=str))
