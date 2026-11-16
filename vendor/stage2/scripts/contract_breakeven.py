"""The contract break-even table (D-150): for every protocol, the edge per trade (net of costs) at which the campaign's
median log growth is zero, and the matching win rate at each leg's R, beside the brokerage break-even.

    python scripts/contract_breakeven.py

Protocols, declared here before any is run:

* stage one's lifecycle geometries (`propedge.campaign.breakeven.lifecycle_protocols`);
* one yardstick per target multiple the bracket map tests (D-149): the Combine at that R with stage one's Combine
  risk for it (0.5:1 $1,000 three a day; 1:1 $1,500; 1.5:1 $500; 2:1 $750; 3:1 $500; results_state_policy_combine.csv
  and T5 section 1) and the funded account at stage one's static 2:1 $750 (propsim D-10's branch). The map's 5:1 is
  read against the 3:1 yardstick. These are the lines `scripts/score_bracket_map.py` re-reads its screen against.

Settings: one account; one trade a day unless stated; the verified rules with Aeropay terms; D-145's conduct model
with tier-3 denial at 25 % (the gate's level) and, for the two protocols named in SENSITIVITY, 0 % and 50 %; a
$5,000 bankroll and a 504-trading-day horizon, ASSUMED pending the operator (docs/HUMAN_INPUTS.md); 200 paths per
edge on common random numbers; the edge grid -0.25 to +0.10 in steps of 0.025, extended downward while the campaign
still grows at its bottom. Writes results/contract_breakeven.csv and results/contract_breakeven_curves.csv
(EXPLORATORY: assumptions named in the manifest).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.campaign import breakeven as be  # noqa: E402
from propedge.campaign.payout_method import rules_for_method  # noqa: E402
from propedge.reporting.results import write_result  # noqa: E402

SCRIPT = "scripts/contract_breakeven.py"
SEED = 20261108
BANKROLL, HORIZON, PATHS = 5_000.0, 504, 200
GRID = tuple(np.round(np.arange(-0.25, 0.1001, 0.025), 4))
SENSITIVITY = ("s1_zero_edge_static", "fast_1p5_500")
#: The bracket map's yardsticks: Combine R -> (Combine risk, trades a day), funded static 2:1 $750.
MAP_YARDSTICKS = {0.5: (1000.0, 3), 1.0: (1500.0, 1), 1.5: (500.0, 1), 2.0: (750.0, 1), 3.0: (500.0, 1)}


def protocols() -> list[tuple[be.TieredProtocol, object, str, str]]:
    out = [(p, pol, src, "lifecycle") for p, pol, src in be.lifecycle_protocols()]
    for rr, (risk, tpd) in MAP_YARDSTICKS.items():
        out.append((be.TieredProtocol(f"map_yardstick_{rr:g}to1", combine_rr=rr, combine_risk=risk, funded_rr=2.0,
                                      funded_risk=750.0, trades_per_day=tpd, family="breakeven"), None,
                    f"Combine {rr:g}:1 ${risk:,.0f} ({tpd}/day, stage one's Combine table); funded static 2:1 $750",
                    "map_yardstick"))
    return out


#: The payout-path set (D-152's follow-up, declared 2026-09-26 before it ran): stage one's lifecycle geometries on the
#: Consistency path, and steadier profiles -- smaller risk, more trades a day, from stage one's harvest sizes
#: (results_state_policy_xfa*.csv: 1:1 $150-300, up to three a day) -- on both paths, so the comparison is like for like.
STEADY = (("steady_1p5_250_x2", 1.5, 250.0, 2), ("steady_1p5_150_x3", 1.5, 150.0, 3), ("steady_2_250_x2", 2.0, 250.0, 2))


def consistency_protocols() -> list[tuple[be.TieredProtocol, object, str, str]]:
    from dataclasses import replace

    out = []
    for p, pol, src, _ in protocols():
        if p.name.startswith("map_yardstick"):
            continue
        out.append((replace(p, name=p.name + "_cons", payout_path="consistency"), pol,
                    src + "; on the Consistency path", "consistency"))
    for name, rr, risk, tpd in STEADY:
        for path in ("standard", "consistency"):
            out.append((be.TieredProtocol(f"{name}_{path[:4]}", combine_rr=rr, combine_risk=risk, funded_rr=rr,
                                          funded_risk=risk, trades_per_day=tpd, payout_path=path, family="breakeven"),
                        None, f"{rr:g}:1 ${risk:,.0f}, {tpd} a day, both legs (stage one's harvest sizes); {path} path",
                        "steady"))
    return out


def curve_with_extension(proto, pol, rules, p_deny):
    edges = list(GRID)
    c = be.growth_curve(proto, rules=rules, bankroll=BANKROLL, horizon_days=HORIZON, n_paths=PATHS, seed=SEED,
                        edges=edges, risk_policy=pol, enforcement_p=p_deny)
    lo = min(edges)
    while c["median_log_growth"].iloc[0] >= 0 and lo > -0.5:          # still growing at the bottom: extend down
        lo = round(lo - 0.05, 4)
        extra = be.growth_curve(proto, rules=rules, bankroll=BANKROLL, horizon_days=HORIZON, n_paths=PATHS, seed=SEED,
                                edges=[lo], risk_policy=pol, enforcement_p=p_deny)
        c = pd.concat([extra, c], ignore_index=True)
    return c


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--set", choices=("lifecycle", "consistency"), default="lifecycle",
                    help="lifecycle: stage one's geometries and the map's yardsticks; consistency: the payout-path set")
    a = ap.parse_args(argv)
    chosen = protocols() if a.set == "lifecycle" else consistency_protocols()
    stem = "contract_breakeven" if a.set == "lifecycle" else "contract_breakeven_consistency"
    rules = rules_for_method("aeropay")
    curves, table = [], []
    for proto, pol, src, kind in chosen:
        chk = be.conduct_check(proto, pol)          # D-145's tiers, before anything is simulated
        if chk["status"] == "refused":
            table.append({"protocol": proto.name, "kind": kind, "status": "refused: " + chk["tier1"] + " (tier 1)",
                          "tier2_flags": chk["tier2"], "source": src})
            print(f"{proto.name}: refused ({chk['tier1']})", flush=True)
            continue
        for p_deny in ((0.0, 0.25, 0.5) if (a.set == "lifecycle" and proto.name in SENSITIVITY) else (0.25,)):
            c = curve_with_extension(proto, pol, rules, p_deny)
            c.insert(0, "protocol", proto.name)
            c.insert(1, "denial_p", p_deny)
            curves.append(c)
            b = be.break_even(c, (proto.combine_rr, proto.funded_rr))
            at0 = c.loc[(c["edge"] - 0.0).abs().idxmin()]
            table.append({"protocol": proto.name, "kind": kind, "status": "ok", "tier2_flags": chk["tier2"],
                          "denial_p": p_deny, "source": src,
                          "combine_risk": proto.combine_risk, "funded_risk": proto.funded_risk,
                          "trades_per_day": proto.trades_per_day, "risk_policy": getattr(pol, "id", ""), **b,
                          "growth_at_zero_edge": at0["median_log_growth"], "ruin_at_zero_edge": at0["ruin_probability"],
                          "combines_bought_at_zero_edge": at0["mean_combines_bought"],
                          "grid_low": float(c["edge"].min()), "grid_high": float(c["edge"].max())})
            print(f"{proto.name} (denial {p_deny:.0%}): e* = {b['e_star']:+.3f}; Combine win rate "
                  f"{b['combine_winrate_contract']:.3f} vs brokerage {b['combine_winrate_brokerage']:.3f}", flush=True)
    common = dict(script=SCRIPT, seed=SEED, exploratory=True,
                  parameters={"bankroll": BANKROLL, "horizon_days": HORIZON, "paths": PATHS, "grid": list(GRID),
                              "rules": "rules_for_method('aeropay') from the verified ledger", "accounts": 1,
                              "draw": "stage one's binary process (adapter.BinaryDraw), common random numbers",
                              "conduct": "D-145 ConductModel, tier-3 denial as stated per row",
                              "map_yardsticks": {f"{k:g}": list(v) for k, v in MAP_YARDSTICKS.items()}},
                  notes={"decision": "D-150", "assumed": "bankroll $5,000 and horizon 504 days pending the operator; "
                         "the conduct model's windows and thresholds (D-145)",
                         "upper_bound": "s1_allin_harvest: the binary process lets the all-in always resolve"})
    common["parameters"]["set"] = a.set
    write_result(pd.DataFrame(table), stem, description="The contract break-even edge and win rates "
                 f"per protocol (D-150; the {a.set} set).", **common)
    write_result(pd.concat(curves, ignore_index=True), stem + "_curves",
                 description="Median log growth, ruin and latency against the edge per trade, per protocol (D-150).",
                 **common)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
