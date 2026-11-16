"""Apply D-91/D-96's GC exit rule to the D-100 measurement.

    python scripts/c007_gc_rule.py

D-91 states the rule as the pooled requirement `S >= 0.937 * sqrt([1+(k-1)rho]/k)` with and without
GC, each leg at its upper 95 % sd bound. That form assumes equal sds; with unequal ones the Sharpe
of a pooled test is the requirement on the common edge `e` (in units of intended risk), which is
what this computes -- equal-weight pooling of every trade, one confirmation window for all legs:

    Var(e_hat) = [sum_i f_i sd_i^2 + rho * sum_{i!=j} f_ij sd_i sd_j] / ((sum_i f_i)^2 * 252 * W)
    e_required = 2 z sqrt(Var(e_hat))        (the lower bound must clear e/2; cf = 1)

With equal sds and f = 1 this is exactly D-91's formula (`e_required * sqrt(252) / sd`); the
test pins that. GC stays if `e_required` is lower with it. The rule's own inputs: f = 1 (one trade
a day per leg, as D-91's formula assumes), the average development rho. Two sensitivities are
reported beside it and labelled so: rho at its bootstrap 95th percentile, and the development
trade rates (which size_zero days cut sharply for CL). Nothing here uses the mean of `u`.

Writes results/c007_gc_rule.csv.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.backtest.metrics import Z_95_ONE_SIDED  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402

SD = ROOT / "results" / "c007_leg_sd.csv"
RHO = ROOT / "results" / "c007_leg_rho.csv"
DAYS = 252
CRITERION_EDGE = 0.10                                   # propsim D-47


def conf_window() -> float:
    """The D-49 confirmation window, from the frontier result's manifest."""
    m = json.loads((ROOT / "results" / "time_exit_frontier.csv.manifest.json").read_text("utf-8"))
    return float(m["parameters"]["confirmation_window_years"])


def e_required(sd: np.ndarray, f: np.ndarray, rho: float, window: float) -> float:
    sd, f = np.asarray(sd, float), np.asarray(f, float)
    cross = np.outer(f * sd, f * sd)                    # f_ij approximated by f_i f_j
    np.fill_diagonal(cross, 0.0)
    var = (np.sum(f * sd ** 2) + rho * cross.sum()) / (f.sum() ** 2 * DAYS * window)
    return float(2.0 * Z_95_ONE_SIDED * np.sqrt(var))


def main() -> int:
    legs = read_result(SD).set_index("market")
    rho = read_result(RHO).set_index("pair").loc["average"]
    window = conf_window()
    sd = legs["sd_planning_q95"]
    rate = legs["trades"] / (legs["days_in_evidence"] - legs["no_trade_burn_in"])
    designs = {"with GC": ["GC", "CL", "6E", "ES"], "without GC": ["CL", "6E", "ES"]}
    variants = {
        "rule (D-91/D-96)": (float(rho["rho"]), False),
        "sensitivity: rho at bootstrap q95": (float(rho["rho_boot_q95"]), False),
        "sensitivity: development trade rates": (float(rho["rho"]), True),
    }
    rows = []
    for vname, (r, use_rate) in variants.items():
        req = {}
        for dname, ms in designs.items():
            f = rate[ms].to_numpy() if use_rate else np.ones(len(ms))
            req[dname] = e_required(sd[ms].to_numpy(), f, r, window)
            rows.append({"variant": vname, "design": dname, "legs": "+".join(ms), "k": len(ms),
                         "rho": r, "trade_rates": "development" if use_rate else "one a day",
                         "e_required": req[dname],
                         "fits_criterion_edge": bool(req[dname] <= CRITERION_EDGE)})
        keep = req["with GC"] < req["without GC"]
        for row in rows[-2:]:
            row["gc_verdict"] = "GC stays" if keep else "GC dropped"
    out = pd.DataFrame(rows)
    write_result(out, "c007_gc_rule", script="scripts/c007_gc_rule.py", seed=None, require_seed=False,
                 parameters={"inputs": ["results/c007_leg_sd.csv", "results/c007_leg_rho.csv"],
                             "confirmation_window_years": window, "z": Z_95_ONE_SIDED,
                             "cluster_factor": 1.0, "criterion_edge": CRITERION_EDGE,
                             "sd": "each leg's sd_planning_q95 (D-43 upper 95 % bound)"},
                 notes={"rule": "D-91 confirmed by D-96; the first variant decides",
                        "sensitivities": "reported beside the rule, never used to decide",
                        "f_ij": "pairwise overlap approximated by f_i * f_j in the trade-rate "
                                "sensitivity; exact when f = 1",
                        "mean_of_u": "not used (D-100)"},
                 description="D-91/D-96 GC exit rule for Stage 2B C-007: common edge required by "
                             "the pooled confirmation test with and without GC, development data. Closed form, no randomness.")
    print(out.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
