"""EXPLORATORY (D-414): T23's "big trade first, then flips" in stage one's account model -- the Combine and a funded
account at or below its start at stage one's sizes, the flip-day bracket above its start (after the big win) until the
payout, on D-411's 5-MNQ 1x schedule (02:00, 08:30, 09:00, 10:00, 12:00 CT).

    python scripts/t23_contract_fit_big.py

Variant (i), one distance: every trade the 20-point 1:1 bracket -- the Combine at 35 micros ($1,400), the funded big
trade at 20 micros ($800), the flip at 5 micros ($200) -- at the schedule's measured net edge. Variant (ii), stage one's
funded anchor: the big trade 1.5:1 at $1,000 (25-point stop, 37.5-point target, 20 micros) at an ESTIMATED edge (gross
zero less the 20-point bracket's cost per micro over $50 a micro), the flip as (i). The funded table holds both trades
and allows in each state only the one the rule names (D-325's `allowed`). A variant passes when an attempt brings more
cash than its fees at the point edge (`chain_cash_no_rent`); the better passing variant by cash per slot-day is first.

Writes results/t23_contract_fit_big.csv (`variant` and `verdict` rows) with its manifest.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/t23_contract_fit_big.py"
DECISION = "D-414"
FIT = "results/t23_contract_fit.csv"
SCREEN = "results/t23_fixed_time_screen.csv"
CELLS = "results/collect_map_nq.csv"
CONTRACTS, MULTIPLE = 5, 1.0                       # D-411's 20-point schedule: 5 MNQ at 1x
DISTANCE = 20.0                                    # points: the 20-point target and stop
MPV = 2.0
COMBINE = {"risk": 1400.0, "rr": 1.0}              # 35 micros at 20 points (D-412's whole-micro rule)
FLIP = {"risk": 200.0, "rr": 1.0}                  # 5 micros at 20 points: the flip day (R3)
BIG = {"i": {"risk": 800.0, "rr": 1.0, "stop_points": 20.0},          # 20 micros at 20 points (the allowance)
       "ii": {"risk": 1000.0, "rr": 1.5, "stop_points": 25.0}}        # stage one's funded anchor (propsim D-36)


def funded_leg(cfg: dict, rules, edge_big: float, edge_flip: float, variant: str, horizon: int | None = None):
    """The funded table with both trades and the state rule: the big trade at a balance at or below the start, the
    flip above it. Returns (table, solution, forward summary, big index, flip index)."""
    from propedge.campaign import state_policy as sp

    T = int(horizon or cfg["horizon_days"])
    step = float(cfg["menu"]["step"])
    big = BIG[variant]
    kw = dict(balance_cap=float(cfg["funded"]["balance_cap"]), payout_grid_step=float(cfg["funded"]["payout_grid_step"]),
              payout_choice="max")
    if variant == "i":                          # one distance: both trades on the table's own outcomes at one edge
        menu = sp.Menu(risks=(FLIP["risk"], big["risk"]), rrs=(1.0,), skip=False, step=step)
        f = sp.FundedDP(rules, menu, float(edge_big), T, 0.0, **kw)
    else:                                       # the flip a menu bracket at its own edge (D-384's mechanism)
        menu = sp.Menu(risks=(big["risk"],), rrs=(big["rr"],), skip=False, step=step,
                       flips=((FLIP["risk"], FLIP["rr"], float(edge_flip), 0.0),))
        f = sp.FundedDP(rules, menu, float(edge_big), T, 0.0, **kw)
    bi = f.actions.index((big["risk"], big["rr"]))
    fi = f.actions.index((FLIP["risk"], FLIP["rr"]))
    above = f.B > 1e-9                          # the balance above the start: after the big win
    allowed = np.zeros((len(f.actions), f.nS), bool)
    allowed[bi], allowed[fi] = ~above, above
    f.allowed = allowed
    fsol = f.solve()
    return f, fsol, f.forward(fsol), bi, fi


def legs_values(cfg: dict, rules, variant: str, edge20: float, edge_big: float) -> dict:
    import state_policy_dp as dp
    from propedge.campaign import state_policy as sp

    T = int(cfg["horizon_days"])
    f, fsol, ff, _, _ = funded_leg(cfg, rules, edge_big, edge20, variant)
    c = sp.CombineDP(rules, sp.Menu.fixed(COMBINE["risk"], COMBINE["rr"], float(cfg["menu"]["step"])), float(edge20), T, 0.0)
    csol = c.solve(fsol.fresh_value[1:T + 1] - rules.activation)
    cf = c.forward(csol)
    row = dp.row_of("variant", edge20, 0.0, variant, rules, fsol, ff, csol, cf)
    cash, days, rate = dp.cycle_rate(rules, ff, cf)
    return {"p_pass": row["p_pass"], "combine_mean_days": row["combine_mean_days"],
            "subscriptions_accrued": row["subscriptions_accrued"], "xfa_mean_cash": row["xfa_mean_cash"],
            "xfa_mean_gross_paid": row["xfa_mean_gross_paid"], "xfa_mean_days": row["xfa_mean_days"],
            "xfa_p_paid": row["xfa_p_paid"], "chain_cash_no_rent": row["chain_cash_no_rent"], "cash_per_slot_day": rate}


def edges(rd: Path) -> dict:
    """The 20-point bracket's measured net edge and bound (D-412's row) and the cost per micro of its scheduled slots;
    variant (ii)'s big trade estimated from them (D-414 (4))."""
    import t23_contract_fit as cf

    from propedge.reporting.results import read_result

    fit = read_result(rd / Path(FIT).name)
    row = fit[(fit["section"] == "pair") & (fit["contracts"].astype(float) == CONTRACTS)
              & ((fit["stop_multiple"].astype(float) - MULTIPLE).abs() < 1e-9)].iloc[0]
    e20, lb20 = float(row["e_net"]), float(row["e_net_lower_bound"])
    screen, cells = read_result(rd / Path(SCREEN).name), read_result(rd / Path(CELLS).name)
    s = screen[(screen["section"] == "slot") & (screen["contracts"].astype(float) == CONTRACTS)
               & ((screen["stop_multiple"].astype(float) - MULTIPLE).abs() < 1e-9)
               & (screen["in_schedule"].astype(str).str.lower() == "true")]
    c = cells[cells["section"] == "cell"]
    c = c[(c["period"] == "choice") & (c["delay_min"].astype(int) == 0) & (c["contracts"].astype(int) == CONTRACTS)
          & ((c["stop_multiple"].astype(float) - MULTIPLE).abs() < 1e-9)]
    costs = []
    for r in s.itertuples():
        m = c[(c["decision_slot_minutes"].astype(int) == int(r.decision_slot_minutes))
              & (c["box_minutes"].astype(int) == int(r.box_minutes))]
        costs.append(float(m.iloc[0]["cost_dollars"]))
    cpm = float(np.mean(costs)) / CONTRACTS
    e_big = -cpm / (BIG["ii"]["stop_points"] * MPV)
    assert abs(cf.edges_of(screen, cells, CONTRACTS, MULTIPLE)[0] - e20) < 1e-9
    return {"e20": e20, "lb20": lb20, "cost_per_micro": cpm, "e_big_ii": e_big, "lb_big_ii": e_big - (e20 - lb20),
            "schedule": str(row["schedule"]), "flip_only_cash_point": float(row["chain_cash_no_rent_point"]),
            "flip_only_cash_zero": float(row["chain_cash_no_rent_zero"])}


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import state_policy_dp as dp

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.campaign.payout_method import rules_for_method
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    E = edges(rd)
    cfg = dp.config(dp.config_for(12))
    rules = rules_for_method(cfg["campaign_check"]["payout_method"])
    rows = []
    for v in ("i", "ii"):
        big = BIG[v]
        base = {"section": "variant", "variant": v, "schedule": E["schedule"], "combine_risk": COMBINE["risk"],
                "combine_rr": COMBINE["rr"], "big_risk": big["risk"], "big_rr": big["rr"],
                "big_stop_points": big["stop_points"], "flip_risk": FLIP["risk"], "flip_rr": FLIP["rr"],
                "e20": E["e20"], "lb20": E["lb20"], "cost_per_micro": E["cost_per_micro"],
                "e_big": E["e20"] if v == "i" else E["e_big_ii"], "lb_big": E["lb20"] if v == "i" else E["lb_big_ii"],
                "big_edge_measured": v == "i", "flip_only_cash_point": E["flip_only_cash_point"],
                "flip_only_cash_zero": E["flip_only_cash_zero"]}
        for arm, e20, eb in (("point", E["e20"], base["e_big"]), ("lower_bound", E["lb20"], base["lb_big"]),
                             ("zero", 0.0, 0.0)):
            out = legs_values(cfg, rules, v, e20, eb)
            base.update({f"{k}_{arm}": x for k, x in out.items()})
        base["passes"] = bool(base["chain_cash_no_rent_point"] > 0.0)
        rows.append(base)
        print(f"variant ({v}): big ${big['risk']:.0f} at {big['rr']:g}R; p_pass {base['p_pass_point']:.3f}; xfa cash "
              f"{base['xfa_mean_cash_point']:.0f}; cash/attempt {base['chain_cash_no_rent_point']:+.1f} (zero edge "
              f"{base['chain_cash_no_rent_zero']:+.1f}); per slot-day {base['cash_per_slot_day_point']:+.2f}", flush=True)
    out = pd.DataFrame(rows)
    passing = out[out["passes"]].sort_values("cash_per_slot_day_point", ascending=False)
    verdict = {"section": "verdict", "passing": len(passing),
               "first": (f"variant ({passing.iloc[0]['variant']})" if len(passing)
                         else "none: T23's fixed-time route closes (D-414 (7))")}
    res = pd.concat([out, pd.DataFrame([verdict])], ignore_index=True)
    write_result(res, "t23_contract_fit_big", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"decision": DECISION, "sources": [FIT, SCREEN, CELLS], "contracts": CONTRACTS,
                             "multiple": MULTIPLE, "combine": COMBINE, "flip": FLIP, "big": BIG,
                             "model": "D-412 (4)'s, with the funded table's state rule (D-325's allowed): the big trade "
                                      "at or below the start, the flip above it",
                             "line": "chain_cash_no_rent above zero at the point edge; ranked by cash per slot-day"},
                 notes={"status": "EXPLORATORY: T23's big-then-flip contract fit in stage one's model (D-414)",
                        "seed": "none: no randomness -- exact dynamic programmes over the binary process",
                        "estimate": "variant (ii)'s big-trade edge is estimated (gross zero less the cost per micro over "
                                    "its stop), not measured"},
                 description="EXPLORATORY: T23's big-trade-first-then-flips contract fit (D-414): two variants on D-411's "
                             "20-point schedule in stage one's account model, at the point edge, its bound and zero edge.")
    counter = VariantCounter(path=rd / "variants.jsonl")
    for x in rows:
        counter.record(prereg_id=f"{DECISION}:t23_big_then_flip", seed=0, exploratory=True,
                       params={"study": "T23 big then flip", "variant": x["variant"], "big_risk": x["big_risk"],
                               "big_rr": x["big_rr"]},
                       label=f"T23's big-then-flip contract fit (D-414): variant ({x['variant']})")
    print(f"VERDICT (D-414): {verdict['first']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
