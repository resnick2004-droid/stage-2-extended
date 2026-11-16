"""NQB1's one confirmation verdict (D-229), under its registered pre-registration -- the rules of
config/nqb1_confirmation.yaml applied to the held-back window's counts, once.

    python scripts/confirm_nqb1.py

Reads the ingested confirmation kit (`rmap_kit.CONFIRM_RUN`, `results/manual_R088_rmap_confirm_NQ_2026.csv`) and
applies, in order, what the pre-registration fixed before any of the window was read:

1. **Resolution (D-212)**: per leg (the Combine's 1:1 bracket, the funded account's 2:1), pooled over the registered
   decision slots on full sessions (early closes apart, D-215), the share of brackets at their target or stop is at
   least `resolved_share_min` overall and in every calendar year of the window.
2. **The D-145 gate**: each leg's net edge per trade from the counts -- a target pays R, a stop costs 1, a bracket open
   at the flatten counts as a full loss, less D-221's cost (`score_resolution_map.bracket_cost`), every day counted --
   at its lower bound (the yearly estimates' mean less the one-sided 95 % t quantile with years - 1 degrees of freedom
   times their standard error), through the campaign (`nq_noedge_campaign.campaign`: the registered arm, one Combine
   live, one trade a day per account, five accounts, the bankroll, horizon, paths and seed) at 25 % denial: median log
   growth above zero.

PASS is both; anything else is FAIL. Beside it, never instead: the point estimates, denial 0, ruin, drawdown, the first
payout, RTP placement, and the old gate (e >= 0.10 net, bound >= 0.05; failed by construction). Writes
results/nqb1_confirmation.csv. Refuses unless the config's pre-registration is a runnable row of prereg/REGISTRY.md and
the confirmation run is ingested; refuses a second verdict (the window is read once).
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import no_edge_contract as nec  # noqa: E402
import nq_noedge_campaign as q  # noqa: E402

SCRIPT = "scripts/confirm_nqb1.py"
RESULT = "nqb1_confirmation"


def config_matches_the_engine(c: dict) -> list[str]:
    """The registered campaign settings are the ones the campaign code runs; any difference is refused."""
    k = c["campaign"]
    want = {"arm": q.ARM, "accounts": nec.ACCOUNTS, "bankroll": nec.BANKROLL, "horizon_days": nec.HORIZON,
            "seed": nec.SEED, "gate_denial": 0.25, "rtp_warnings": 0, "trades_per_day": 1, "open_bracket": "loss"}
    out = [f"campaign.{key} is {k.get(key)!r}, the code runs {v!r}" for key, v in want.items() if k.get(key) != v]
    legs = {name: (float(v["R"]), float(v["stop_dollars"])) for name, v in c["legs"].items()}
    if legs != q.LEGS:
        out.append(f"legs {legs} are not the campaign code's {q.LEGS}")
    if c["market"] != q.MARKET:
        out.append(f"market {c['market']} is not the campaign code's {q.MARKET}")
    return out


def resolution(cnt: pd.DataFrame, c: dict) -> pd.DataFrame:
    """Rule 1: per leg, overall and in every registered year, the share resolved on full sessions at the registered
    slots; a registered year with no brackets fails (D-230)."""
    floor = float(c["resolved_share_min"])
    x = cnt[(cnt["kind"] == "count") & (cnt["day_type"] == "full") & cnt["decision_slot"].isin(c["decision_slots"])]
    rows = []
    for leg, (R, stop) in q.LEGS.items():
        g = x[(x["R"] == R) & (x["stop_dollars"] == stop)]
        years = [("all", g)] + [(int(y), g[g["year"] == y]) for y in c.get("years") or sorted(g["year"].unique())]
        for year, gy in years:
            n, t, s = int(gy["n"].sum()), int(gy["target"].sum()), int(gy["stop"].sum())
            share = (t + s) / n if n else float("nan")
            rows.append({"section": "resolution", "leg": leg, "year": year, "n": n, "resolved_share": share,
                         "passes": bool(n and share >= floor)})
    return pd.DataFrame(rows)


def chosen_run(results_dir: Path, runs_dir: Path, c: dict) -> tuple[str | None, str | None]:
    """D-230: (the run the verdict reads, None) -- or (None, why there is nothing to read yet), or ('UNUSABLE', why)
    when both permitted runs were unusable, which is a FAIL. The fix runs only after the first run is unusable."""
    first, second = c["runs"]
    ingested = [r for r in c["runs"] if (results_dir / f"manual_{r.replace('-', '_')}.csv").is_file()]
    unusable = [r for r in c["runs"] if (runs_dir / r / "unusable.json").is_file()]
    both = sorted(set(ingested) & set(unusable))
    if both:                                                  # D-232: an unusable run's counts are never read
        return None, f"{', '.join(both)} is recorded unusable and also ingested; an unusable run is never read"
    if len(ingested) > 1:
        return None, "both permitted runs are ingested; the window is read once"
    if ingested:
        if ingested[0] == second and first not in unusable:
            return None, f"{second} is ingested but {first} is not recorded unusable; the fix runs only after it"
        return ingested[0], None
    if len(unusable) == 2:
        return "UNUSABLE", "both permitted runs were unusable (D-230)"
    return None, "the confirmation run is not ingested"


def main(results_dir: Path | None = None, n_paths: int | None = None, workers: int = 4,
         runs_dir: Path | None = None) -> int:
    from concurrent.futures import ProcessPoolExecutor

    from scipy import stats

    from propedge import RESULTS_DIR
    from propedge.data.cloud_guard import confirmation_run_authorised
    from propedge.data.rmap_kit import confirm_config
    from propedge.data.run_kit import RUNS_DIR
    from propedge.reporting.pin import engine_pin
    from propedge.reporting.results import write_result

    c = confirm_config()
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if not confirmation_run_authorised(str(c.get("prereg_id"))):
        print(f"REFUSED: {c.get('prereg_id')!r} is not a runnable row of prereg/REGISTRY.md (D-81, D-229).")
        return 2
    bad = config_matches_the_engine(c)
    if bad:
        print("REFUSED: the registered settings and the code differ: " + "; ".join(bad))
        return 2
    if (rd / f"{RESULT}.csv").exists():
        print(f"REFUSED: {RESULT}.csv exists; the held-back window is read once (D-229).")
        return 2
    run, why = chosen_run(rd, Path(runs_dir) if runs_dir is not None else RUNS_DIR, c)
    if run == "UNUSABLE":                                   # D-230: two unusable runs are a FAIL, no count read
        out = pd.DataFrame([{"section": "verdict", "verdict": "FAIL", "rule_resolution": False, "rule_gate": False,
                             "reason": why, "prereg": c["prereg_id"]}])
        write_result(out, RESULT, script=SCRIPT, seed=int(c["campaign"]["seed"]), exploratory=False,
                     results_dir=results_dir, provenance={"prereg": c["prereg_id"]},
                     parameters={"config": "config/nqb1_confirmation.yaml", "prereg": c["prereg_id"],
                                 "runs": c["runs"], "decision": "D-229, D-230"},
                     notes={"status": f"PRE-REGISTERED ({c['prereg_id']}): FAIL, both permitted runs unusable"},
                     description=f"NQB1's confirmation under {c['prereg_id']}: FAIL, both permitted runs unusable.")
        print(f"VERDICT ({c['prereg_id']}): FAIL -- {why}")
        return 0
    if run is None:
        print(f"REFUSED: {why}.")
        return 2
    src = rd / f"manual_{run.replace('-', '_')}.csv"
    cnt = pd.read_csv(src)
    res = resolution(cnt, c)
    rule1 = bool(res["passes"].all())
    years = sorted({int(y) for y in cnt.loc[cnt["kind"] == "count", "year"]})
    t95 = {len(years): float(stats.t.ppf(0.95, len(years) - 1))}
    inputs = q.leg_edges(cnt, [int(s) for s in c["decision_slots"]], t95=t95)
    pooled = inputs[inputs["year"] == "pooled"].set_index("leg")
    lb = (float(pooled.loc["combine", "e_net_lower_bound"]), float(pooled.loc["funded", "e_net_lower_bound"]))
    pt = (float(pooled.loc["combine", "e_net"]), float(pooled.loc["funded", "e_net"]))
    k = c["campaign"]
    paths = int(n_paths or k["n_paths"])
    cap = int(k["combines_at_once"])
    jobs = [(*lb, cap, float(k["gate_denial"]), "lower_bound", paths),
            (*lb, cap, float(k["beside_denial"]), "lower_bound", paths),
            (*pt, cap, float(k["gate_denial"]), "point", paths),
            (*pt, cap, float(k["beside_denial"]), "point", paths)]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        camp = pd.DataFrame(list(pool.map(q.point, jobs)))
    gate_row = camp[(camp["reading"] == "lower_bound") & (camp["denial_p"] == float(k["gate_denial"]))].iloc[0]
    rule2 = bool(gate_row["median_log_growth"] > 0)
    verdict = "PASS" if rule1 and rule2 else "FAIL"
    old_gate = bool(min(pt) >= 0.10 and min(lb) >= 0.05)
    rd_runs = Path(runs_dir) if runs_dir is not None else RUNS_DIR
    ing = rd_runs / run / "ingested.json"
    days = (json.loads(ing.read_text(encoding="utf-8")).get("summary") or {}).get("days") if ing.is_file() else None
    # D-201: the break-even hit rate -- the target share at which a leg's net edge is nil, open brackets lost
    be = {leg: (1.0 + float(pooled.loc[leg, "cost_r"])) / (1.0 + R) for leg, (R, _) in q.LEGS.items()}
    # beside, never as the verdict (D-230): each leg's bound at D-189's one-sided 0.05/N
    tN = float(stats.t.ppf(1.0 - 0.05 / int(c["ledger_n"]), len(years) - 1))
    yearly = inputs[inputs["year"] != "pooled"]
    lbN = {leg: float(g["e_net"].astype(float).mean() - tN * g["e_net"].astype(float).std(ddof=1)
                      / np.sqrt(len(g))) for leg, g in yearly.groupby("leg")}
    head = pd.DataFrame([{"section": "verdict", "verdict": verdict, "rule_resolution": rule1, "rule_gate": rule2,
                          "gate_median_log_growth": float(gate_row["median_log_growth"]),
                          "e_combine_lower_bound": lb[0], "e_funded_lower_bound": lb[1], "years": len(years),
                          "t95": t95[len(years)], "old_gate_met": old_gate, "prereg": c["prereg_id"], "run": run,
                          "days": days, "combine_target_share": float(pooled.loc["combine", "target_share"]),
                          "combine_breakeven_hit": be["combine"],
                          "funded_target_share": float(pooled.loc["funded", "target_share"]),
                          "funded_breakeven_hit": be["funded"],
                          "beside_e_combine_bound_at_005_over_N": lbN["combine"],
                          "beside_e_funded_bound_at_005_over_N": lbN["funded"], "ledger_n": int(c["ledger_n"])}])
    out = pd.concat([head, res, inputs, camp], ignore_index=True)
    write_result(out, RESULT, script=SCRIPT, seed=int(k["seed"]), exploratory=False, results_dir=results_dir,
                 provenance={"engine": engine_pin(), "prereg": c["prereg_id"]},
                 parameters={"config": "config/nqb1_confirmation.yaml", "prereg": c["prereg_id"],
                             "source": src.name, "run": run, "years": years, "decision": "D-229, D-230",
                             **{"campaign": k}},
                 notes={"status": f"PRE-REGISTERED ({c['prereg_id']}): NQB1's one confirmation, read once"},
                 description=f"NQB1's confirmation under {c['prereg_id']}: resolution on the held-back window and the "
                             "D-145 gate on its measured inputs; the point estimates and denial 0 beside it.")
    pd.set_option("display.width", 250)
    print(res.round(4).to_string(index=False))
    print(camp[["reading", "denial_p", "e_combine", "e_funded", "median_log_growth", "ruin_probability",
                "median_days_to_first_payout", "mean_max_drawdown"]].round(4).to_string(index=False))
    print(f"VERDICT ({c['prereg_id']}): {verdict} -- resolution {'met' if rule1 else 'NOT met'}, gate "
          f"{'passed' if rule2 else 'NOT passed'}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--workers", type=int, default=4)
    raise SystemExit(main(workers=ap.parse_args().workers))
