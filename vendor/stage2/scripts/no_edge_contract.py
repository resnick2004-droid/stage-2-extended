"""EXPLORATORY (D-213, part 1): does Topstep's contract pay a trader with no edge whose every trade resolves at its stop
or target, and how much cost per trade can it absorb?

    python scripts/no_edge_contract.py [--paths 500] [--workers 4] [--added]

Stage one's binary process (`adapter.BinaryDraw` behind `simulate_lockstep_campaign`'s default draws): a trade at R
wins R x risk with probability p = (1 + e) / (1 + R) and loses the risk otherwise (propsim D-01), e the edge per trade
net of costs -- so a trader with no gross edge paying c per trade sits at e = -c, and c* = -e* is the cost the contract
absorbs before the campaign stops growing. The binary process lets every trade resolve, which is what D-212 requires
of a model; whether real markets allow it at a cost below c* is part 2.

Run as IM2's gate ran its campaigns (`propedge.campaign.gate.run_gate`): five accounts in total, five Combines at the
start, $5,000, 504 days, 500 paths, `rules_for_method('aeropay')`, the hold queue, D-145's conduct model with the
Responsible Trading Program on. Two arms from stage one, fixed in D-213:

* `s1_zero_edge_static`: Combine 1:1 $1,500, funded static 2:1 $750, one trade a day (propsim D-08, D-10, D-15;
  D-150's row of the same name);
* `im2_lifecycle`: P-04's policy -- Combine 1:1 $1,500, funded build 2:1 $1,000 below +$2,000, then harvest 1:1 $300 up
  to three a day (`im2_score.policy`).

`--added` (D-217, ADDED AFTER part 1's result, labelled so) runs instead two arms from stage one whose Combine
winners are larger than its losers, so the Responsible Trading Program's "losers not smaller than winners" trigger does
not fire by design and funded accounts can stay on the Standard path -- `s1_low_edge`, Combine 2:1 $750 with funded
1.5:1 $1,000 (T5 2a at e <= 0.05; propsim D-36), and `s1_high_edge`, Combine 1.5:1 $500 with funded 1.5:1 $1,000 (T5
2a at e >= 0.10) -- writing results/no_edge_contract_added.csv, part 1's own file left as run.

Each on e = -0.25 to +0.05 in steps of 0.025, one seed (common random numbers), at denial 0 -- the operator's reading
for this test -- and 0.25, D-145's gate level, reported beside it. Writes results/no_edge_contract.csv: one `curve` row
per arm, denial and e, and one `break_even` row per arm and denial with e* (D-150's zero crossing) and c* = -e*.
**The engine check first**: at e = 0 the first Combine's pass rate at 1:1 $1,500 must not exceed stage one's 16/49 by
more than the sampling error; a rate above it is an engine error and stops the script.
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
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/no_edge_contract.py"
SEED = 20261213
EDGES = tuple(round(x, 4) for x in np.arange(-0.25, 0.05001, 0.025))
DENIALS = (0.0, 0.25)
ARMS = ("s1_zero_edge_static", "im2_lifecycle")
ARMS_ADDED = ("s1_low_edge", "s1_high_edge")       # D-217: added after part 1's result
ACCOUNTS, BANKROLL, HORIZON = 5, 5000.0, 504
CEILING_1TO1_1500 = 16 / 49                     # stage one's Combine pass ceiling at 1:1 $1,500, zero edge
CEILING_ANY = 0.327131                          # stage one's supremum over every fair Combine strategy, zero edge


def arm(name: str):
    """(protocol, risk policy or None) for an arm."""
    from propedge.campaign.protocols import Protocol
    from propedge.research import im2_score as sc

    if name == "s1_zero_edge_static":
        return Protocol(name, combine_rr=1.0, combine_risk=1500.0, funded_rr=2.0, funded_risk=750.0,
                        trades_per_day=1, max_concurrent_accounts=ACCOUNTS, family="no_edge",
                        source="propsim D-08, D-10, D-15; D-150"), None
    if name == "s1_low_edge":
        return Protocol(name, combine_rr=2.0, combine_risk=750.0, funded_rr=1.5, funded_risk=1000.0,
                        trades_per_day=1, max_concurrent_accounts=ACCOUNTS, family="no_edge",
                        source="T5 2a at e <= 0.05; propsim D-36; D-150's s1_conduct_low_edge"), None
    if name == "s1_high_edge":
        return Protocol(name, combine_rr=1.5, combine_risk=500.0, funded_rr=1.5, funded_risk=1000.0,
                        trades_per_day=1, max_concurrent_accounts=ACCOUNTS, family="no_edge",
                        source="T5 2a at e >= 0.10; D-150's s1_high_edge"), None
    if name == "im2_lifecycle":
        return Protocol(name, combine_rr=1.0, combine_risk=1500.0, funded_rr=2.0, funded_risk=1000.0,
                        trades_per_day=3, max_concurrent_accounts=ACCOUNTS, family="no_edge",
                        source="prereg/P-04_im2_lifecycle_v3.md §3"), sc.policy()
    raise ValueError(name)


def campaign(name: str, e: float, denial: float, n_paths: int, combines: int = ACCOUNTS, rtp_warnings: int = 0):
    """(summary, paths) of one campaign: an arm at an edge and a denial level, on the script's seed. `combines` is the
    most Combines live at once (D-34's `max_concurrent_combines`; part 1 ran five) and `rtp_warnings` the trigger days
    answered by a warning before placement (D-220; part 1 ran none) -- both D-220's, for item 7 of T14."""
    from propedge.campaign.lockstep import ConductModel, simulate_lockstep_campaign
    from propedge.campaign.payout_method import rules_for_method

    protocol, policy = arm(name)
    return simulate_lockstep_campaign(
        protocol, edge=float(e), seed=SEED, rules=rules_for_method("aeropay"), initial_bankroll=BANKROLL,
        horizon_days=HORIZON, n_paths=n_paths, payout_method="aeropay", max_concurrent_accounts=ACCOUNTS,
        max_concurrent_combines=combines, max_total_accounts=ACCOUNTS, require_verified_cap=False, ledger=None,
        conduct=ConductModel(enforcement_p=float(denial), rtp_warnings=rtp_warnings), risk_policy=policy)


def run_point(job: tuple) -> dict:
    """One campaign: an arm at an edge and a denial level."""
    warnings.filterwarnings("ignore")
    name, e, denial, n_paths = job
    summary, paths = campaign(name, e, denial, n_paths)
    return point_row(name, e, denial, summary, paths)


def point_row(name: str, e: float, denial: float, summary, paths) -> dict:
    """A campaign's `curve` row."""
    s = summary.as_dict()
    first = [p.combines[0] for p in paths if p.combines]
    resolved = [c for p in paths for c in p.combines if c.resolved_on is not None]
    return {"section": "curve", "arm": name, "denial_p": float(denial), "edge": float(e),
            "median_log_growth": s["median_log_growth"], "ruin_probability": s["ruin_probability"],
            "mean_final_cash": s["mean_final_cash"], "median_final_cash": s["median_final_cash"],
            "p10_final_cash": s["p10_final_cash"], "p90_final_cash": s["p90_final_cash"],
            "median_days_to_first_payout": s["median_days_to_first_payout"],
            "share_accounts_ever_paid": s["share_accounts_ever_paid"],
            # the charter: drawdown and latency beside growth (the audit of 2026-10-01)
            "mean_max_drawdown": s["mean_max_drawdown"], "p90_max_drawdown": s["p90_max_drawdown"],
            "mean_accounts_funded": s["mean_accounts_funded"], "mean_combines_abandoned": s["mean_combines_abandoned"],
            "mean_passes_forfeited": s["mean_passes_forfeited"],
            "mean_same_day_multi_breach_days": s["mean_same_day_multi_breach_days"],
            "first_combine_pass_rate": float(np.mean([c.passed for c in first])) if first else float("nan"),
            "combine_pass_rate_resolved": (float(np.mean([c.passed for c in resolved])) if resolved
                                           else float("nan")),
            "mean_combines_bought": float(np.mean([len(p.combines) for p in paths])),
            "share_paths_rtp_placed": float(np.mean([p.conduct.get("rtp_placed_day", -1) >= 0 for p in paths]))}


def engine_check(rows: list[dict], n_paths: int) -> str:
    """At e = 0 the first Combine's pass rate sits at or under stage one's ceiling within three standard errors: 16/49
    at 1:1 $1,500, the supremum over every fair strategy for any other geometry."""
    worst = []
    for r in rows:
        if r["edge"] == 0.0:
            ceiling = CEILING_1TO1_1500 if r["arm"] in ARMS else CEILING_ANY
            se = math.sqrt(ceiling * (1 - ceiling) / max(n_paths, 1))
            if r["first_combine_pass_rate"] > ceiling + 3 * se:
                worst.append(f"{r['arm']} at denial {r['denial_p']}: {r['first_combine_pass_rate']:.4f}")
    if worst:
        raise SystemExit("ENGINE CHECK FAILED -- the first Combine passes above stage one's 16/49 at zero edge, an "
                         "engine error, never a finding: " + "; ".join(worst))
    return f"engine check passed: the first Combine's pass rate at e = 0 is at or under 16/49 (+3 se, {n_paths} paths)"


def main(n_paths: int = 500, results_dir: Path | None = None, workers: int = 4, record: bool = True,
         added: bool = False) -> int:
    """`workers` processes (four fit the machine's free memory on 2026-10-01; twenty did not); the count cannot change
    a number, every campaign has its own seed."""
    from propedge.backtest.harness import VariantCounter
    from propedge.campaign.breakeven import zero_crossing
    from propedge.reporting.pin import engine_pin
    from propedge.reporting.results import write_result

    arms = ARMS_ADDED if added else ARMS
    name = "no_edge_contract_added" if added else "no_edge_contract"
    jobs = [(a, e, d, n_paths) for a in arms for d in DENIALS for e in EDGES]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(run_point, jobs))
    print(f"{len(jobs)} campaigns of {n_paths} paths in {time.time() - t0:.0f}s", flush=True)
    check = engine_check(rows, n_paths)
    print(check, flush=True)
    curve = pd.DataFrame(rows)
    be = []
    for (a, d), g in curve.groupby(["arm", "denial_p"], sort=False):
        g = g.sort_values("edge")
        e_star = zero_crossing(g["edge"], g["median_log_growth"])
        z = g[g["edge"] == 0.0].iloc[0]
        be.append({"section": "break_even", "arm": a, "denial_p": d, "e_star": e_star,
                   "c_star": -e_star if np.isfinite(e_star) else float("nan"),
                   "median_log_growth": float(z["median_log_growth"]), "ruin_probability": float(z["ruin_probability"]),
                   "edge": 0.0, "first_combine_pass_rate": float(z["first_combine_pass_rate"])})
    out = pd.concat([curve, pd.DataFrame(be)], ignore_index=True)
    write_result(out, name, script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 provenance={"engine": engine_pin()},
                 parameters={"arms": list(arms), "edges": list(EDGES), "denials": list(DENIALS), "n_paths": n_paths,
                             "accounts": ACCOUNTS, "combines_at_start": ACCOUNTS, "total_accounts": ACCOUNTS,
                             "bankroll": BANKROLL, "horizon_days": HORIZON, "draw": "stage one's binary process",
                             "rules": "rules_for_method('aeropay')",
                             "conduct": repr(__import__("propedge.campaign.lockstep", fromlist=["ConductModel"])
                                             .ConductModel(enforcement_p=0.0)).replace("enforcement_p=0.0",
                                                                                         "enforcement_p=<denial>"),
                             "engine_check": check, "decision": "D-213"},
                 notes={"status": ("EXPLORATORY: D-217, arms ADDED AFTER D-213 part 1's result" if added else
                                   "EXPLORATORY: D-213 part 1, synthetic") + "; read at denial 0 (the operator), "
                                  "D-145's 25 % beside it"},
                 description="EXPLORATORY: the no-edge contract test, part 1 -- binary trades that always resolve, "
                             "net edge e from -0.25 to +0.05 R, through the five-account engine for "
                             + ("stage one's 2:1 $750 and 1.5:1 $500 Combine geometries (D-217, added after part 1's "
                                "result)" if added else "stage one's zero-edge geometry and P-04's lifecycle")
                             + ", at denial 0 and 0.25: the growth curve and the break-even e* (c* = -e*, the cost "
                               "per trade the contract absorbs).")
    if record:
        VariantCounter().record(prereg_id="D-213:no_edge_contract", seed=SEED, exploratory=True,
                                params={"study": "part 1, synthetic" + (", arms added (D-217)" if added else ""),
                                        "arms": list(arms), "edges": list(EDGES),
                                        "denials": list(DENIALS), "n_paths": n_paths},
                                label="EXPLORATORY: the contract's break-even for trades with no edge that resolve")
    pd.set_option("display.width", 220)
    print(pd.DataFrame(be).round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--paths", type=int, default=500)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--added", action="store_true", help="D-217: the two arms added after part 1's result")
    a = ap.parse_args()
    raise SystemExit(main(n_paths=a.paths, workers=a.workers, added=a.added))
