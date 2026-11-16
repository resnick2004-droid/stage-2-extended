"""EXPLORATORY (D-227): D-226's NQ setting through the five-account campaign on its measured inputs -- does it pass the
D-145 gate, and what does it look like beside it?

    python scripts/nq_noedge_campaign.py [--paths 500] [--workers 4]

D-226 found NQ feasible at today's price level (D-225) and D-221's rule chose stage one's zero-edge geometry with one
Combine live at once. This reads the setting's own counts and runs the campaign on them, fixed in D-227 before it ran:

* **The setting**: NQ at today's level (R084, R085); the Combine leg a 1:1 bracket at a $125 stop a micro, the funded leg
  a 2:1 bracket at $75 (`LEGS`), at the decision times where both resolve on D-221's rule (`TIMES`, from
  `results/resolution_map_score_today.csv`); every day, early closes included.
* **Each leg's edge per trade, net**, in R: from the counts per year, a target pays R, a stop costs 1 and a bracket still
  open at the flatten is counted a full loss (conservative: its price is not in the counts), less D-221's cost
  (`score_resolution_map.bracket_cost`); the point is the pooled estimate, the lower bound the yearly estimates' mean
  less the one-sided 95 % t quantile times their standard error (2014's halves summed; the counts carry no days to
  bootstrap).
* **The campaign**: `no_edge_contract`'s settings (five accounts, $5,000, 504 days, 500 paths, its seed, verified rules
  with Aeropay, D-145's conduct model) with the Combine accounts drawing stage one's binary process at the Combine
  leg's edge and the funded accounts at the funded leg's (`adapter.BinaryDraw` on the engine's own seeds, so equal
  edges reproduce part 1's campaign), one trade a day per account (D-154's minimum for 1:1 $1,500, and its best for
  passes; accounts on different decision times, D-157), at most one Combine live (D-226's choice) and five (part 1's).
* **The gate** (D-145): median log growth above zero at each leg's lower bound with 25 % denial; beside it the point
  estimate and denial 0, with ruin, drawdown, the first payout, payouts, Combines bought and RTP placement, and the old
  gate's reading (e at least 0.10 net, bound at least 0.05: a no-edge setting fails it by construction).

Writes results/nq_noedge_campaign.csv: one `inputs` row per leg and year and one per leg pooled, one `campaign` row per
cap, reading and denial. Limits, stated: trades on different accounts the same day are drawn independently though they
share NQ's path; the counts' 2009-2019 volatility read at today's prices; a random-direction bracket's gross edge is what
the counts show, not a model.
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

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import no_edge_contract as nec  # noqa: E402

SCRIPT = "scripts/nq_noedge_campaign.py"
MARKET = "NQ"
ARM = "s1_zero_edge_static"
LEGS = {"combine": (1.0, 125.0), "funded": (2.0, 75.0)}        # (R, stop dollars per micro), D-226
CAPS = (1, 5)
DENIALS = (0.25, 0.0)                                           # the gate's, then the operator's reading
READINGS = ("lower_bound", "point")
T95_10 = 1.8124611228107335                                      # one-sided 95 % t quantile, 10 degrees of freedom


def counts(results_dir: Path) -> pd.DataFrame:
    from propedge.data.rmap_kit import RMAP_TODAY_READ

    runs = [RMAP_TODAY_READ[(MARKET, h)] for h in ("0914", "1419")]
    return pd.concat([pd.read_csv(results_dir / f"manual_{r.replace('-', '_')}.csv") for r in runs],
                     ignore_index=True)


def times(results_dir: Path) -> list[int]:
    """The decision slots at which both legs resolve on D-221's rule, from the today-scale score."""
    s = pd.read_csv(results_dir / "resolution_map_score_today.csv")
    c = s[(s["section"] == "cell") & (s["market"] == MARKET) & (s["resolves"] == True)]  # noqa: E712
    per_leg = [set(c[(c["R"] == r) & (c["stop_dollars"] == stop)]["decision_slot"].astype(int))
               for r, stop in LEGS.values()]
    return sorted(set.intersection(*per_leg))


def leg_edges(cnt: pd.DataFrame, slots: list[int], t95: dict[int, float] | None = None) -> pd.DataFrame:
    """Per leg, per year and pooled: brackets, the shares at target, stop and open, the cost and the net edge, in R.
    The lower bound uses the one-sided 95 % t quantile for the years present: `t95` {years: quantile}, by default
    D-227's eleven development years only."""
    from score_resolution_map import bracket_cost
    from propedge.data.rmap_kit import params
    from propedge.execution.fills import FillModel

    fm = FillModel.load("assumed")
    slip = {"entry": fm.entry_slippage_ticks, "stop": fm.stop_slippage_ticks, "flatten": fm.flatten_slippage_ticks}
    q = params(MARKET)
    tick_dollars, fee = q["micro_tick"] * q["micro_point_value"], fm.round_turn_by_instrument[q["micro"]]
    c = cnt[(cnt["kind"] == "count") & cnt["decision_slot"].isin(slots)]
    sp = cnt[(cnt["kind"] == "spread") & cnt["decision_slot"].isin(slots)]
    rows = []
    for leg, (R, stop) in LEGS.items():
        g = c[(c["R"] == R) & (c["stop_dollars"] == stop)]
        groups = [(int(y), gy, sp[sp["year"] == y]) for y, gy in g.groupby("year")] + [("pooled", g, sp)]
        for year, gy, sy in groups:
            n, t, s, o = (int(gy[k].sum()) for k in ("n", "target", "stop", "open"))
            qn = float(sy["spread_count"].sum())
            spread = float((sy["spread_ticks_mean"] * sy["spread_count"]).sum()) / qn if qn else float("nan")
            cost_r = bracket_cost(fee, tick_dollars, spread, s / n, o / n, slip) / stop
            gross = (t * R - s - o) / n
            rows.append({"section": "inputs", "leg": leg, "year": year, "R": R, "stop_dollars": stop, "n": n,
                         "target_share": t / n, "stop_share": s / n, "open_share": o / n,
                         "spread_ticks_mean": spread, "e_gross": gross, "cost_r": cost_r, "e_net": gross - cost_r})
    out = pd.DataFrame(rows)
    for leg in LEGS:
        y = out[(out["leg"] == leg) & (out["year"] != "pooled")]["e_net"].astype(float)
        tq = (t95 or {11: T95_10}).get(len(y))
        lb = float(y.mean() - tq * y.std(ddof=1) / math.sqrt(len(y))) if tq else float("nan")
        out.loc[(out["leg"] == leg) & (out["year"] == "pooled"), "e_net_lower_bound"] = lb
        out.loc[(out["leg"] == leg) & (out["year"] == "pooled"), "years"] = len(y)
    return out


def campaign(e_combine: float, e_funded: float, cap: int, denial: float, n_paths: int):
    """`no_edge_contract.campaign`'s call with each account type drawing at its own leg's edge."""
    from propedge.campaign.lockstep import ConductModel, child_seed, simulate_lockstep_campaign
    from propedge.campaign.payout_method import rules_for_method
    from propedge.contract.adapter import BinaryDraw

    protocol, policy = nec.arm(ARM)
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
    e_c, e_f, cap, denial, reading, n_paths = job
    summary, paths = campaign(e_c, e_f, cap, denial, n_paths)
    row = nec.point_row(ARM, e_c, denial, summary, paths)
    row.update({"section": "campaign", "combines_at_once": cap, "reading": reading, "e_combine": e_c,
                "e_funded": e_f, "gate_passed": bool(row["median_log_growth"] > 0) if denial == 0.25 and
                reading == "lower_bound" else pd.NA})
    return row


def main(n_paths: int = 500, results_dir: Path | None = None, workers: int = 4, record: bool = True) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.pin import engine_pin
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    slots = times(rd)
    inputs = leg_edges(counts(rd), slots)
    pooled = inputs[inputs["year"] == "pooled"].set_index("leg")
    e = {"lower_bound": (float(pooled.loc["combine", "e_net_lower_bound"]), float(pooled.loc["funded", "e_net_lower_bound"])),
         "point": (float(pooled.loc["combine", "e_net"]), float(pooled.loc["funded", "e_net"]))}
    jobs = [(*e[r], cap, d, r, n_paths) for cap in CAPS for r in READINGS for d in DENIALS]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(point, jobs))
    print(f"{len(jobs)} campaigns of {n_paths} paths in {time.time() - t0:.0f}s", flush=True)
    camp = pd.DataFrame(rows)
    gate = camp[camp["gate_passed"].notna()]
    out = pd.concat([inputs, camp], ignore_index=True)
    write_result(out, "nq_noedge_campaign", script=SCRIPT, seed=nec.SEED, exploratory=True, results_dir=results_dir,
                 provenance={"engine": engine_pin()},
                 parameters={"market": MARKET, "scale": "today (D-225)", "legs": {k: list(v) for k, v in LEGS.items()},
                             "decision_slots": slots, "arm": ARM, "trades_per_day_per_account": 1,
                             "combines_at_once": list(CAPS), "denials": list(DENIALS), "readings": list(READINGS),
                             "open_bracket": "a full loss", "lower_bound": "yearly mean - t(0.95, 10) x SE",
                             "n_paths": n_paths, "bankroll": nec.BANKROLL, "horizon_days": nec.HORIZON,
                             "draw": "stage one's binary process per leg at the leg's measured edge",
                             "decision": "D-227"},
                 notes={"status": "EXPLORATORY: D-227, D-226's NQ setting on its measured inputs; chosen after "
                                  "D-224, reported beside it"},
                 description="EXPLORATORY: NQ at today's price level, stage one's zero-edge geometry, through the "
                             "five-account campaign on each leg's measured net edge, at its lower bound (the gate, "
                             "25 % denial) and point, denial 0 beside, one Combine live and five.")
    if record:
        VariantCounter().record(prereg_id="D-227:nq_noedge_campaign", seed=nec.SEED, exploratory=True,
                                params={"study": "NQ no-edge campaign on measured inputs", "legs": str(LEGS),
                                        "caps": list(CAPS), "denials": list(DENIALS), "readings": list(READINGS),
                                        "n_paths": n_paths},
                                label="EXPLORATORY: NQ at today's level, measured inputs, D-145 gate")
    pd.set_option("display.width", 250)
    print(inputs[inputs["year"] == "pooled"][["leg", "n", "target_share", "stop_share", "open_share", "e_gross",
                                              "cost_r", "e_net", "e_net_lower_bound"]].round(4).to_string(index=False))
    print(camp[["combines_at_once", "reading", "denial_p", "e_combine", "e_funded", "median_log_growth",
                "ruin_probability", "median_days_to_first_payout", "mean_max_drawdown", "share_paths_rtp_placed",
                "gate_passed"]].round(4).to_string(index=False))
    print("gate (D-145):", "PASSED" if bool(gate["gate_passed"].any()) else "FAILED",
          "at", gate[gate["gate_passed"] == True]["combines_at_once"].tolist())  # noqa: E712
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--paths", type=int, default=500)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    raise SystemExit(main(n_paths=a.paths, workers=a.workers))
