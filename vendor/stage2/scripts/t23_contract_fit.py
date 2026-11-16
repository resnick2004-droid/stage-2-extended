"""EXPLORATORY (D-412): T23's contract fit -- each fixed-time schedule that meets R1-R3 (D-411) as fixed Combine and
funded legs in stage one's binary account model (propsim D-06) at the brackets' measured net edge: does an attempt
bring in more cash than its fees?

    python scripts/t23_contract_fit.py

The funded leg is the flip bracket (risk = the stop multiple x $200, R its inverse); the Combine the same distances in
points, its micros the fewer of $1,500 over the stop's dollars a micro and the 50-micro allowance, its risk on the $50
grid, the same R. The edge is the schedule's slots' mean `e_net` on CHOICE (`results/collect_map_nq.csv`), the bound's
mean beside, and zero edge beside. The legs go through the repository's fixed-leg tables as `state_policy_dp` evaluates
its baselines (stage one's Combine model, the largest payout, no rent). A pair passes when `chain_cash_no_rent` is
above zero at the point edge; the passing pairs are ranked by the cash per slot-day.

Writes results/t23_contract_fit.csv (`pair` and `verdict` rows) with its manifest.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/t23_contract_fit.py"
DECISION = "D-412"
SCREEN = "results/t23_fixed_time_screen.csv"
CELLS = "results/collect_map_nq.csv"
COMBINE_ANCHOR = 1500.0          # stage one's Combine anchor (propsim D-08): 1:1, $1,500 at risk
COMBINE_MICROS = 50              # the Combine's allowance (D-289)
TARGET = 200.0                   # the flip bracket's target before fees (R3)
MPV = 2.0                        # MNQ's dollars a point
GRID = 50.0


def legs(contracts: int, stop_multiple: float) -> dict:
    """The two legs' risk and R for a flip bracket of `contracts` MNQ at `stop_multiple` x the target (D-412 (3))."""
    target_pts = TARGET / (contracts * MPV)
    stop_pts = stop_multiple * target_pts
    per_micro = stop_pts * MPV
    micros = min(int(math.floor(COMBINE_ANCHOR / per_micro + 1e-9)), COMBINE_MICROS)

    def on_grid(x: float) -> bool:
        return abs(x / GRID - round(x / GRID)) < 1e-9

    # whole micros whose stake and win (stake / multiple) both land on the table's $50 grid: the most that do
    while micros > 0 and not (on_grid(micros * per_micro) and on_grid(micros * per_micro / stop_multiple)):
        micros -= 1
    return {"target_points": target_pts, "stop_points": stop_pts, "rr": 1.0 / stop_multiple,
            "funded_risk": stop_multiple * TARGET, "combine_micros": micros, "combine_risk": micros * per_micro}


def edges_of(screen: pd.DataFrame, cells: pd.DataFrame, contracts: int, stop_multiple: float) -> tuple[float, float]:
    """The schedule's slots' mean `e_net` and mean `e_net_lower_bound` on CHOICE, each slot at its D-411 box, on time."""
    s = screen[(screen["section"] == "slot") & (screen["contracts"].astype(float) == contracts)
               & ((screen["stop_multiple"].astype(float) - stop_multiple).abs() < 1e-9)
               & (screen["in_schedule"].astype(str).str.lower() == "true")]
    c = cells[cells["section"] == "cell"]
    c = c[(c["period"] == "choice") & (c["delay_min"].astype(int) == 0) & (c["contracts"].astype(int) == contracts)
          & ((c["stop_multiple"].astype(float) - stop_multiple).abs() < 1e-9)]
    e, lb = [], []
    for r in s.itertuples():
        m = c[(c["decision_slot_minutes"].astype(int) == int(r.decision_slot_minutes))
              & (c["box_minutes"].astype(int) == int(r.box_minutes))]
        if len(m) != 1:
            raise SystemExit(f"REFUSED: {len(m)} collect-map cells for slot {r.decision_ct} at {contracts} MNQ {stop_multiple:g}x.")
        e.append(float(m.iloc[0]["e_net"]))
        lb.append(float(m.iloc[0]["e_net_lower_bound"]))
    return float(np.mean(e)), float(np.mean(lb))


def fixed_legs(cfg: dict, rules, edge: float, combine_risk: float, funded_risk: float, rr: float) -> dict:
    """The fixed legs through the repository's tables, as `state_policy_dp` evaluates its baselines (no rent)."""
    import state_policy_dp as dp
    from propedge.campaign import state_policy as sp

    T = int(cfg["horizon_days"])
    step = float(cfg["menu"]["step"])
    fm = sp.Menu.fixed(float(funded_risk), float(rr), step)
    f = sp.FundedDP(rules, fm, float(edge), T, 0.0, balance_cap=float(cfg["funded"]["balance_cap"]),
                    payout_grid_step=float(cfg["funded"]["payout_grid_step"]), payout_choice="max")
    fsol = f.solve()
    ff = f.forward(fsol)
    # stage one's Combine (the 16/49 oracle's model): D-313's room and consistency caps need FV3's rung grid, which
    # these brackets do not have (D-412 (4))
    c = sp.CombineDP(rules, sp.Menu.fixed(float(combine_risk), float(rr), step), float(edge), T, 0.0)
    csol = c.solve(fsol.fresh_value[1:T + 1] - rules.activation)
    cf = c.forward(csol)
    row = dp.row_of("pair", edge, 0.0, "fixed", rules, fsol, ff, csol, cf)
    cash, days, rate = dp.cycle_rate(rules, ff, cf)
    return {"p_pass": row["p_pass"], "combine_mean_days": row["combine_mean_days"],
            "subscriptions_accrued": row["subscriptions_accrued"], "xfa_mean_cash": row["xfa_mean_cash"],
            "xfa_mean_days": row["xfa_mean_days"], "xfa_p_paid": row["xfa_p_paid"],
            "chain_cash_no_rent": row["chain_cash_no_rent"], "cash_per_slot_day": rate, "cycle_slot_days": days}


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import state_policy_dp as dp

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.campaign.payout_method import rules_for_method
    from propedge.reporting.results import read_result, write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    screen, cells = read_result(rd / Path(SCREEN).name), read_result(rd / Path(CELLS).name)
    cfg = dp.config(dp.config_for(12))
    rules = rules_for_method(cfg["campaign_check"]["payout_method"])
    sc = screen[(screen["section"] == "schedule") & (screen["meets_r1"].astype(str).str.lower() == "true")]
    rows = []
    for r in sc.itertuples():
        n, m = int(r.contracts), float(r.stop_multiple)
        lg = legs(n, m)
        e, lb = edges_of(screen, cells, n, m)
        base = {"section": "pair", "contracts": n, "stop_multiple": m, "schedule": str(r.schedule),
                "schedule_size": int(r.schedule_size), "supply_per_account_day": float(r.schedule_size) / 5.0,
                **lg, "e_net": e, "e_net_lower_bound": lb}
        for arm, edge in (("point", e), ("lower_bound", lb), ("zero", 0.0)):
            out = fixed_legs(cfg, rules, edge, lg["combine_risk"], lg["funded_risk"], lg["rr"])
            base.update({f"{k}_{arm}": v for k, v in out.items()})
        base["passes"] = bool(base["chain_cash_no_rent_point"] > 0.0)
        rows.append(base)
        print(f"{n} MNQ {m:g}x: e {e:+.4f} (lb {lb:+.4f}); combine ${lg['combine_risk']:.0f} ({lg['combine_micros']} micros); "
              f"p_pass {base['p_pass_point']:.3f}; cash/attempt {base['chain_cash_no_rent_point']:+.1f}; "
              f"per slot-day {base['cash_per_slot_day_point']:+.2f}", flush=True)
    out = pd.DataFrame(rows)
    passing = out[out["passes"]].sort_values("cash_per_slot_day_point", ascending=False)
    verdict = {"section": "verdict", "pairs": len(out), "passing": len(passing),
               "first": (f"{int(passing.iloc[0]['contracts'])} MNQ at {passing.iloc[0]['stop_multiple']:g}x"
                         if len(passing) else "none: the fixed-time version fails contract fit (D-412 (6))"),
               "ranking": "; ".join(f"{int(x.contracts)} MNQ {x.stop_multiple:g}x" for x in passing.itertuples())}
    res = pd.concat([out, pd.DataFrame([verdict])], ignore_index=True)
    write_result(res, "t23_contract_fit", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"decision": DECISION, "sources": [SCREEN, CELLS], "model": "stage one's binary process "
                             "(propsim D-06) through the fixed-leg tables; rules_for_method('aeropay'); stage one's Combine "
                             "model (no D-313 caps: they need FV3's rung grid); the largest payout; no rent", "combine_anchor": COMBINE_ANCHOR,
                             "combine_micros": COMBINE_MICROS, "target": TARGET, "horizon_days": int(cfg["horizon_days"]),
                             "line": "chain_cash_no_rent above zero at the point edge; ranked by cash per slot-day"},
                 notes={"status": "EXPLORATORY: T23's contract fit in stage one's account model (D-412)",
                        "seed": "none: no randomness -- exact dynamic programmes over the binary process"},
                 description="EXPLORATORY: T23's contract fit (D-412) -- each fixed-time schedule meeting R1-R3 as fixed "
                             "Combine and funded legs in stage one's account model at its measured net edge, its bound "
                             "and zero edge: the pass probability, the funded cash and the cash an attempt brings net of fees.")
    counter = VariantCounter(path=rd / "variants.jsonl")
    for x in rows:
        counter.record(prereg_id=f"{DECISION}:t23_contract_fit", seed=0, exploratory=True,
                       params={"study": "T23 contract fit", "contracts": x["contracts"], "stop_multiple": x["stop_multiple"]},
                       label=f"T23's contract fit (D-412): {x['contracts']} MNQ at {x['stop_multiple']:g}x")
    print(f"VERDICT (D-412): {verdict['first']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
