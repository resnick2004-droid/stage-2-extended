"""EXPLORATORY (D-240; T15 item 6a): stage one's geometries through the five-account campaign on NQ's and ES's measured
2020-2025 inputs at actual prices -- does the contract pay a trader with no edge whose brackets resolve today?

    python scripts/today_noedge_campaign.py [--paths 500] [--workers 4]

Fixed in D-240 before it ran:

* **Inputs**: the regime map's counts (R090 NQ, R091 ES; D-238) for 2020-01-01 to 2025-06-30 -- development data
  (D-237) -- fixed stops in points only.
* **Arms** (`ARMS`): stage one's geometries in the engine -- `s1_zero_edge_static`, `s1_low_edge` (T5 2a's best pair at
  zero edge), `s1_high_edge` -- and `im2_lifecycle`'s legs, for feasibility only.
* **A leg's stop**, one per leg and market: among the fixed stops that at the leg's R resolve on at least 98 % overall
  and in every year at a decision time (D-212), and realise at least 90 % of the leg's risk in whole micros under its
  state's cap (D-212 (1), D-201), the one with the lowest pooled cost in R over the times where it qualifies. An arm is
  feasible on a market when every leg has one; its times are those where every leg's stop qualifies.
* **Each leg's edge**, in R, over the arm's times: a target pays R, a stop costs 1, an open bracket a full loss, less
  D-238's cost (`regime_then_now.cost_per_micro`); the point pooled, the lower bound the yearly estimates' mean less the
  one-sided 95 % t quantile for the years present times their standard error.
* **The campaign**: D-227's (`nq_noedge_campaign`) for each feasible two-leg arm, at most one Combine live and five, at
  the lower bounds and the points, at 0 % denial -- the gate (D-234) -- and 25 %, kept in the file only (D-236).

Writes results/today_noedge_campaign.csv: `feasibility` (per arm, market and leg: the stop, its micros and realised
risk, the times), `inputs` (per arm, market, leg and year, and pooled) and `campaign` rows.
"""
from __future__ import annotations

import argparse
import math
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

import no_edge_contract as nec  # noqa: E402

SCRIPT = "scripts/today_noedge_campaign.py"
MARKETS = ("NQ", "ES")
YEARS = (2020, 2025)
RESOLVED_MIN, RISK_MIN = 0.98, 0.90                     # D-212
# each arm's legs: (leg, R, dollar risk, the stop band's state for its cap), as score_resolution_map.LEGS
ARMS = {
    "s1_zero_edge_static": (("combine", 1.0, 1500.0, "combine"), ("funded", 2.0, 750.0, "funded_below_2000")),
    "s1_low_edge": (("combine", 2.0, 750.0, "combine"), ("funded", 1.5, 1000.0, "funded_below_2000")),
    "s1_high_edge": (("combine", 1.5, 500.0, "combine"), ("funded", 1.5, 1000.0, "funded_below_2000")),
    "im2_lifecycle": (("combine", 1.0, 1500.0, "combine"), ("build", 2.0, 1000.0, "funded_below_2000"),
                      ("harvest", 1.0, 300.0, "funded_at_or_above_2000")),
}
CAMPAIGN_ARMS = ("s1_zero_edge_static", "s1_low_edge", "s1_high_edge")    # two legs: Combine and funded draws
CAPS = (1, 5)
DENIALS = (0.0, 0.25)                                   # the gate's (D-234), then the file's (D-236)
READINGS = ("lower_bound", "point")
# one-sided 95 % t quantiles by the number of yearly blocks (degrees of freedom = blocks - 1)
T95 = {2: 6.313751514675043, 3: 2.919985580355516, 4: 2.353363434801823, 5: 2.131846786326649,
       6: 2.015048372669157}


def now_counts(results_dir: Path) -> pd.DataFrame:
    from propedge.data.regime_kit import REGIME_RUNS

    frames = []
    for m in MARKETS:
        f = results_dir / f"manual_{REGIME_RUNS[m].replace('-', '_')}.csv"
        if f.exists():
            frames.append(pd.read_csv(f))
    if not frames:
        return pd.DataFrame()
    d = pd.concat(frames, ignore_index=True)
    return d[d["year"].between(*YEARS) & ((d["kind"] == "spread") | (d["stop_kind"] == "points"))]


def _slip_fees():
    from propedge.execution.fills import FillModel

    fm = FillModel.load("assumed")
    return {"entry": fm.entry_slippage_ticks, "stop": fm.stop_slippage_ticks,
            "flatten": fm.flatten_slippage_ticks}, dict(fm.round_turn_by_instrument)


def _reading(c: pd.DataFrame, sp: pd.DataFrame, ev: pd.DataFrame, R: float, q: dict, fee: float, slip: dict) -> dict:
    """Shares, cost and edge of one set of count rows at R (`ev`: the same cells at the largest R, for the gaps)."""
    from regime_then_now import cost_per_micro

    tick_dollars = q["micro_tick"] * q["micro_point_value"]
    n, t, s, o = (int(c[k].sum()) for k in ("n", "target", "stop", "open"))
    qn = float(sp["spread_count"].sum())
    spread = float((sp["spread_ticks_mean"] * sp["spread_count"]).sum()) / qn if qn else float("nan")
    exits = int(ev["stop"].sum())
    over = float(ev["overshoot_ticks_sum"].sum()) / exits if exits else 0.0
    stop_dollars = float(c["stop_value"].iloc[0]) * q["micro_point_value"]
    cost_r = cost_per_micro(fee, tick_dollars, spread, s / n, o / n, over, slip) / stop_dollars
    gross = (t * R - s - o) / n
    return {"n": n, "target_share": t / n, "stop_share": s / n, "open_share": o / n, "spread_ticks_mean": spread,
            "overshoot_ticks_per_exit": over, "e_gross": gross, "cost_r": cost_r, "e_net": gross - cost_r}


def qualifying(cnt: pd.DataFrame, market: str, R: float, risk: float, cap: int) -> pd.DataFrame:
    """Every (decision, fixed stop) at R that resolves on 98 % overall and in every year and realises at least 90 % of
    `risk` in whole micros under `cap`: decision_slot, stop_value, micros, realised share."""
    from propedge.data.regime_kit import params

    q = params(market)
    c = cnt[(cnt["kind"] == "count") & (cnt["market"] == market) & (cnt["R"] == R)]
    rows = []
    for (slot, stop), g in c.groupby(["decision_slot", "stop_value"]):
        by = g.groupby("year")[["n", "target", "stop"]].sum()
        share = (by["target"] + by["stop"]) / by["n"]
        overall = float((by["target"] + by["stop"]).sum() / by["n"].sum())
        micros = min(math.floor(risk / (float(stop) * q["micro_point_value"])), cap)
        realised = micros * float(stop) * q["micro_point_value"] / risk
        if overall >= RESOLVED_MIN and share.min() >= RESOLVED_MIN and realised >= RISK_MIN:
            rows.append({"decision_slot": int(slot), "stop_value": float(stop), "micros": micros,
                         "realised_risk_share": realised})
    return pd.DataFrame(rows, columns=["decision_slot", "stop_value", "micros", "realised_risk_share"])


def choose_stop(cnt: pd.DataFrame, market: str, R: float, qual: pd.DataFrame) -> float | None:
    """The qualifying stop with the lowest pooled cost in R over the times where it qualifies."""
    from propedge.data.regime_kit import params

    if qual.empty:
        return None
    q = params(market)
    slip, fees = _slip_fees()
    fee, r_max = float(fees[q["micro"]]), max(q["rr"])
    best = None
    for stop, g in qual.groupby("stop_value"):
        slots = set(g["decision_slot"])
        c = cnt[(cnt["kind"] == "count") & (cnt["market"] == market) & (cnt["stop_value"] == stop)
                & cnt["decision_slot"].isin(slots)]
        sp = cnt[(cnt["kind"] == "spread") & (cnt["market"] == market) & cnt["decision_slot"].isin(slots)]
        cost = _reading(c[c["R"] == R], sp, c[c["R"] == r_max], R, q, fee, slip)["cost_r"]
        if best is None or cost < best[0]:
            best = (cost, float(stop))
    return best[1]


def feasibility(cnt: pd.DataFrame, caps: dict) -> tuple[pd.DataFrame, dict]:
    """Per arm, market and leg: the chosen stop; and {(arm, market): (stops per leg, decision slots)} for the
    feasible ones."""
    rows, feasible = [], {}
    for arm, legs in ARMS.items():
        for market in MARKETS:
            if cnt[(cnt["market"] == market)].empty:
                continue
            chosen, slot_sets = {}, []
            for leg, R, risk, state in legs:
                qual = qualifying(cnt, market, R, risk, caps.get((market, state), 0))
                stop = choose_stop(cnt, market, R, qual)
                q = qual[qual["stop_value"] == stop] if stop is not None else qual.iloc[0:0]
                chosen[leg] = stop
                slot_sets.append(set(q["decision_slot"]))
                rows.append({"section": "feasibility", "arm": arm, "market": market, "leg": leg, "R": R,
                             "risk_dollars": risk, "cap_state": state, "cap_micros": caps.get((market, state), 0),
                             "stop_points": stop, "micros": int(q["micros"].iloc[0]) if len(q) else pd.NA,
                             "realised_risk_share": float(q["realised_risk_share"].iloc[0]) if len(q) else pd.NA,
                             "qualifying_times": len(q)})
            slots = sorted(set.intersection(*slot_sets)) if all(chosen.values()) else []
            ok = bool(slots)
            for r in rows[-len(legs):]:
                r.update({"arm_feasible": ok, "arm_times": len(slots)})
            if ok:
                feasible[(arm, market)] = (chosen, slots)
    return pd.DataFrame(rows), feasible


def leg_inputs(cnt: pd.DataFrame, arm: str, market: str, chosen: dict, slots: list[int]) -> pd.DataFrame:
    """Per leg, per year and pooled over the arm's times: shares, cost and net edge; the pooled row carries the lower
    bound."""
    from propedge.data.regime_kit import params

    q = params(market)
    slip, fees = _slip_fees()
    fee, r_max = float(fees[q["micro"]]), max(q["rr"])
    rows = []
    for leg, R, risk, _ in ARMS[arm]:
        c = cnt[(cnt["kind"] == "count") & (cnt["market"] == market) & (cnt["stop_value"] == chosen[leg])
                & cnt["decision_slot"].isin(slots)]
        sp = cnt[(cnt["kind"] == "spread") & (cnt["market"] == market) & cnt["decision_slot"].isin(slots)]
        groups = [(int(y), c[c["year"] == y], sp[sp["year"] == y]) for y in sorted(c["year"].unique())]
        for year, cy, sy in groups + [("pooled", c, sp)]:
            r = _reading(cy[cy["R"] == R], sy, cy[cy["R"] == r_max], R, q, fee, slip)
            rows.append({"section": "inputs", "arm": arm, "market": market, "leg": leg, "year": year, "R": R,
                         "risk_dollars": risk, "stop_points": chosen[leg], **r})
    out = pd.DataFrame(rows)
    for leg, *_ in ARMS[arm]:
        y = out[(out["leg"] == leg) & (out["year"] != "pooled")]["e_net"].astype(float)
        tq = T95.get(len(y))
        lb = float(y.mean() - tq * y.std(ddof=1) / math.sqrt(len(y))) if tq else float("nan")
        sel = (out["leg"] == leg) & (out["year"] == "pooled")
        out.loc[sel, "e_net_lower_bound"] = lb
        out.loc[sel, "years"] = len(y)
    return out


def campaign(arm: str, e_combine: float, e_funded: float, cap: int, denial: float, n_paths: int):
    """D-227's campaign for `arm`: each account type draws stage one's binary process at its own leg's edge."""
    from propedge.campaign.lockstep import ConductModel, child_seed, simulate_lockstep_campaign
    from propedge.campaign.payout_method import rules_for_method
    from propedge.contract.adapter import BinaryDraw

    protocol, policy = nec.arm(arm)
    rules = rules_for_method("aeropay")
    cp, fp = protocol.combine_policy(), protocol.funded_policy()

    def factories(path_seed: int):
        return (lambda i, d: BinaryDraw(cp, e_combine, child_seed(path_seed, 1, i), rules),
                lambda i, d: BinaryDraw(fp, e_funded, child_seed(path_seed, 2, i), rules))

    return simulate_lockstep_campaign(
        protocol, edge=float(e_combine), seed=nec.SEED, rules=rules, initial_bankroll=nec.BANKROLL,
        horizon_days=nec.HORIZON, n_paths=n_paths, payout_method="aeropay", max_concurrent_accounts=nec.ACCOUNTS,
        max_concurrent_combines=cap, max_total_accounts=nec.ACCOUNTS, require_verified_cap=False, ledger=None,
        conduct=ConductModel(enforcement_p=float(denial)), risk_policy=policy, draw_factories_for_path=factories)


def point(job: tuple) -> dict:
    warnings.filterwarnings("ignore")
    arm, market, e_c, e_f, cap, denial, reading, n_paths = job
    summary, paths = campaign(arm, e_c, e_f, cap, denial, n_paths)
    row = nec.point_row(arm, e_c, denial, summary, paths)
    row.update({"section": "campaign", "market": market, "combines_at_once": cap, "reading": reading,
                "e_combine": e_c, "e_funded": e_f,
                "gate_passed": bool(row["median_log_growth"] > 0) if denial == DENIALS[0] and
                reading == "lower_bound" else pd.NA})
    return row


def main(n_paths: int = 500, results_dir: Path | None = None, workers: int = 4, record: bool = True) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.pin import engine_pin
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cnt = now_counts(rd)
    if cnt.empty:
        print("REFUSED: no regime-map run for NQ or ES is ingested (R090, R091).")
        return 2
    band = pd.read_csv(rd / "stop_band.csv")
    caps = {(r["market"], r["state"]): int(r["cap_micros"]) for _, r in band.iterrows()}
    feas, feasible = feasibility(cnt, caps)
    inputs, jobs = [], []
    for (arm, market), (chosen, slots) in feasible.items():
        inp = leg_inputs(cnt, arm, market, chosen, slots)
        inp["decision_slots"] = ",".join(str(s) for s in slots)
        inputs.append(inp)
        if arm not in CAMPAIGN_ARMS:
            continue
        p = inp[inp["year"] == "pooled"].set_index("leg")
        e = {"lower_bound": (float(p.loc["combine", "e_net_lower_bound"]), float(p.loc["funded", "e_net_lower_bound"])),
             "point": (float(p.loc["combine", "e_net"]), float(p.loc["funded", "e_net"]))}
        jobs += [(arm, market, *e[r], cap, d, r, n_paths) for cap in CAPS for r in READINGS for d in DENIALS]
    t0 = time.time()
    if jobs:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            camp = pd.DataFrame(list(pool.map(point, jobs)))
    else:
        camp = pd.DataFrame()
    print(f"{len(jobs)} campaigns of {n_paths} paths in {time.time() - t0:.0f}s", flush=True)
    out = pd.concat([feas, *inputs, camp], ignore_index=True)
    write_result(out, "today_noedge_campaign", script=SCRIPT, seed=nec.SEED, exploratory=True, results_dir=results_dir,
                 provenance={"engine": engine_pin()},
                 parameters={"markets": list(MARKETS), "years": list(YEARS), "stops": "fixed points only",
                             "arms": {k: [list(x) for x in v] for k, v in ARMS.items()},
                             "campaign_arms": list(CAMPAIGN_ARMS), "resolved_min": RESOLVED_MIN,
                             "realised_risk_min": RISK_MIN, "size_caps": "results/stop_band.csv cap_micros",
                             "trades_per_day_per_account": 1, "combines_at_once": list(CAPS),
                             "denials": list(DENIALS), "gate_denial": DENIALS[0], "readings": list(READINGS),
                             "open_bracket": "a full loss", "lower_bound": "yearly mean - t(0.95, years - 1) x SE",
                             "cost": "D-221 with the measured overshoot (D-238)", "n_paths": n_paths,
                             "bankroll": nec.BANKROLL, "horizon_days": nec.HORIZON, "decision": "D-240"},
                 notes={"status": "EXPLORATORY: D-240, stage one's geometries on NQ's and ES's 2020-2025 measured "
                                  "inputs at actual prices, chosen after D-239; development data"},
                 description="EXPLORATORY: which of stage one's geometries can be built from brackets that resolve on "
                             "NQ and ES today, and the five-account campaign on each feasible one at its legs' measured "
                             "net edge (lower bound and point), one Combine live and five; the gate at 0 % denial.")
    if record and jobs:
        VariantCounter().record(prereg_id="D-240:today_noedge_campaign", seed=nec.SEED, exploratory=True,
                                params={"study": "no-edge campaign on 2020-2025 measured inputs",
                                        "feasible": [f"{a} {m}" for a, m in feasible], "caps": list(CAPS),
                                        "denials": list(DENIALS), "readings": list(READINGS), "n_paths": n_paths},
                                label="EXPLORATORY: stage one's geometries on NQ/ES today, measured inputs, D-145 gate")
    pd.set_option("display.width", 250)
    print(feas.to_string(index=False))
    if inputs:
        allin = pd.concat(inputs)
        print(allin[allin["year"] == "pooled"][["arm", "market", "leg", "stop_points", "n", "target_share",
                                               "open_share", "e_gross", "cost_r", "e_net", "e_net_lower_bound"]]
              .round(4).to_string(index=False))
    if not camp.empty:
        print(camp[["arm", "market", "combines_at_once", "reading", "denial_p", "median_log_growth",
                    "ruin_probability", "median_days_to_first_payout", "gate_passed"]].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--paths", type=int, default=500)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    raise SystemExit(main(n_paths=a.paths, workers=a.workers))
