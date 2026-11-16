"""The contract break-even (D-150): for a protocol, the edge -- and so the win rate -- a strategy's trades need for the
campaign's time-aware return to be exactly zero.

    e*  such that  median log growth (D-14) = 0

The campaign runs through the lockstep engine (`propedge.campaign.lockstep.simulate_lockstep_campaign`) with the
verified rules, the payout method's fee and lag, fees, the hold queue and the account cap, and D-145's conduct model
(tier 2 applied; tier 3 at the stated denial probability). Trades are stage one's binary process
(`adapter.BinaryDraw` -> the vendored `RandomDraw`, which keeps the floor barrier race and the drift solve): a trade at
R wins `R x risk` with probability p = (1 + e) / (1 + R) and loses `risk` otherwise (propsim D-01), where e is the
edge per trade in units of risk **net of costs** -- the same quantity as the bracket map's and every model's mean R net,
so a strategy is compared with e* directly. The win rate that matches e* at a leg's R is p* = (1 + e*) / (1 + R); the
brokerage break-even is e = 0, p = 1 / (1 + R).

Every edge on the grid runs on the same seed (the same path seeds and per-account child seeds), so the growth curve is
compared on common random numbers; e* is the first zero crossing, interpolated linearly between grid points.

Stage one's zero-edge geometry (Combine 1:1 at $1,500; the funded day-one all-in on the $2,000 cushion) is D-145's
tier 2: allowed, flagged, and priced by the engine's conduct model. Since D-151 the engine's own `Protocol` and
`RiskPolicy` apply the tiers (`propedge.campaign.conduct`), so `TieredProtocol` and `TieredRiskPolicy` are the engine's
classes under the names D-150 first used.

What the binary process cannot show: whether a bracket completes inside a session. The bracket map (D-149) shows
stage one's funded all-in at 3:1 or 5:1 rarely does on ES and NQ, so a row that uses it is an upper bound.
"""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import pandas as pd

from propedge.campaign.conduct import policy_findings, protocol_findings
from propedge.campaign.protocols import Protocol
from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy, Tiers

#: The grid the break-even is searched on (net edge per trade, in units of risk).
EDGE_GRID = tuple(np.round(np.arange(-0.15, 0.1001, 0.025), 4))

#: The engine's classes (D-151 put D-145's tiers into them); the names are D-150's.
TieredProtocol = Protocol
TieredRiskPolicy = RiskPolicy


def conduct_check(protocol: Any, policy: RiskPolicy | None = None) -> dict[str, str]:
    """D-145's tiers (`propedge.campaign.conduct`) applied to a protocol and its policy before anything is simulated.

    Returns {'status': 'ok' | 'refused', 'tier1': reasons refused, 'tier2': flags whose consequences the engine
    applies}. Takes an already built protocol (so its own tier-1 check has passed) or any object with its fields."""
    t1, t2 = protocol_findings(protocol)
    if policy is not None:
        a, b = policy_findings(policy.root.leaves(frozenset({"combine", "funded", "paid"})), policy.id)
        t1, t2 = t1 + a, t2 + b
    return {"status": "refused" if t1 else "ok", "tier1": "; ".join(dict.fromkeys(t1)),
            "tier2": "; ".join(dict.fromkeys(t2))}


# ------------------------------------------------------------------------ stage one's lifecycle geometries


def lifecycle_protocols() -> list[tuple[TieredProtocol, RiskPolicy | None, str]]:
    """Stage one's geometries by lifecycle state (config/bracket_map.yaml `lifecycle_geometry`), one trade a day.

    Returns (protocol, risk policy or None, source)."""
    P = TieredProtocol
    out: list[tuple[TieredProtocol, RiskPolicy | None, str]] = [
        (P("s1_zero_edge_static", combine_rr=1.0, combine_risk=1500.0, funded_rr=2.0, funded_risk=750.0,
           family="breakeven"), None,
         "Combine 1:1 $1,500 (propsim D-08, D-15); funded static 2:1 $750 (D-10's branch when the all-in cannot "
         "complete in a session, which the bracket map shows is the usual case)"),
        (P("s1_conduct_low_edge", combine_rr=2.0, combine_risk=750.0, funded_rr=1.5, funded_risk=1000.0,
           family="breakeven"), None, "T5 2a at e <= 0.05 (propsim D-36)"),
        (P("s1_high_edge", combine_rr=1.5, combine_risk=500.0, funded_rr=1.5, funded_risk=1000.0,
           family="breakeven"), None, "T5 2a at e >= 0.10"),
        (P("fast_1p5_500", combine_rr=1.5, combine_risk=500.0, funded_rr=1.5, funded_risk=500.0,
           family="breakeven"), None, "1.5:1 $500 on both legs, the maximum payout as soon as eligible (FV1's)"),
        (P("buffer_8000", combine_rr=1.5, combine_risk=500.0, funded_rr=1.5, funded_risk=500.0, keep_balance=8000.0,
           family="breakeven"), None, "1.5:1 $500 keeping $8,000 (propsim D-45, exploratory there)"),
    ]
    allin = TieredRiskPolicy(
        id="s1_allin_harvest", description="Combine 1:1 $1,500; funded day one 3:1 on the $2,000 cushion, then 1:1 $150",
        root=Phase(combine=Leaf("combine 1:1 $1,500", 1500.0, 1.0),
                   funded=Tiers(on="days_in_state", name="funded day",
                                tiers=((0.0, Leaf("day-one all-in 3:1 $2,000", 2000.0, 3.0)),
                                       (1.0, Leaf("harvest 1:1 $150", 150.0, 1.0)))),
                   paid=Leaf("harvest 1:1 $150", 150.0, 1.0)))
    out.append((P("s1_allin_harvest", combine_rr=1.0, combine_risk=1500.0, funded_rr=3.0, funded_risk=2000.0,
                  family="breakeven"), allin,
                "propsim D-09, results_state_policy_xfa_allin.csv; an UPPER BOUND: the binary process lets the "
                "all-in always resolve, which the bracket map shows it rarely does inside a session"))
    return out


# ------------------------------------------------------------------------ the search


def zero_crossing(edges: Sequence[float], growth: Sequence[float]) -> float:
    """The first edge where growth crosses from below zero to at or above it, interpolated; NaN if none."""
    e = np.asarray(edges, float)
    g = np.asarray(growth, float)
    for i in range(1, len(e)):
        if np.isfinite(g[i - 1]) and np.isfinite(g[i]) and g[i - 1] < 0 <= g[i]:
            return float(e[i - 1] + (0 - g[i - 1]) * (e[i] - e[i - 1]) / (g[i] - g[i - 1]))
    if len(g) and np.isfinite(g[0]) and g[0] >= 0:
        return float("-inf")                      # already growing at the bottom of the grid
    return float("nan")


def growth_curve(protocol: TieredProtocol, *, rules: Any, bankroll: float, horizon_days: int, n_paths: int,
                 seed: int, accounts: int = 1, enforcement_p: float = 0.25, edges: Sequence[float] = EDGE_GRID,
                 risk_policy: RiskPolicy | None = None, conduct: bool = True, ledger: Any = None) -> pd.DataFrame:
    """The campaign at every edge on the grid, on common random numbers: one row per edge."""
    from dataclasses import replace

    from propedge.campaign.lockstep import ConductModel, simulate_lockstep_campaign

    proto = replace(protocol, max_concurrent_accounts=int(accounts))
    rows = []
    for e in edges:
        summary, paths = simulate_lockstep_campaign(
            proto, edge=float(e), seed=seed, rules=rules, initial_bankroll=bankroll, horizon_days=horizon_days,
            n_paths=n_paths, payout_method="aeropay", max_concurrent_accounts=int(accounts),
            require_verified_cap=False, ledger=ledger, risk_policy=risk_policy,
            conduct=ConductModel(enforcement_p=float(enforcement_p)) if conduct else None)
        first = [p.combines[0] for p in paths if p.combines]
        s = summary.as_dict()
        rows.append({
            "edge": float(e), "median_log_growth": s["median_log_growth"], "ruin_probability": s["ruin_probability"],
            "median_final_cash": s["median_final_cash"], "p10_final_cash": s["p10_final_cash"],
            "p90_final_cash": s["p90_final_cash"], "median_days_to_first_payout": s["median_days_to_first_payout"],
            "share_accounts_ever_paid": s["share_accounts_ever_paid"],
            "first_combine_pass_rate": float(np.mean([c.passed for c in first])) if first else float("nan"),
            "mean_combines_bought": float(np.mean([len(p.combines) for p in paths])),
            "share_paths_rtp_placed": (float(np.mean([p.conduct.get("rtp_placed_day", -1) >= 0 for p in paths]))
                                       if conduct else float("nan")),
        })
    return pd.DataFrame(rows)


def break_even(curve: pd.DataFrame, legs_rr: Sequence[float]) -> dict:
    """e* from a growth curve, with the matching win rate at each leg's R and the brokerage break-even beside it."""
    e_star = zero_crossing(curve["edge"], curve["median_log_growth"])
    out = {"e_star": e_star}
    for name, rr in zip(("combine", "funded"), legs_rr):
        out[f"{name}_rr"] = float(rr)
        out[f"{name}_winrate_contract"] = (1 + e_star) / (1 + rr) if np.isfinite(e_star) else float("nan")
        out[f"{name}_winrate_brokerage"] = 1 / (1 + rr)
    return out


__all__ = ["EDGE_GRID", "TieredProtocol", "TieredRiskPolicy", "conduct_check", "lifecycle_protocols",
           "zero_crossing", "growth_curve", "break_even"]
