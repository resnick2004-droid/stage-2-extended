"""D-145's conduct tiers for protocols and risk policies: one source for the engine, the break-even calculator and
the Studio (D-151).

* **Tier 1 -- refused.** What no protocol or policy may carry: a non-positive risk or R, an unknown payout path, no
  account. `Protocol.check_conduct` and `RiskPolicy.validate` raise `ConductViolation` for these, and only these.
  (The firm's mechanical prohibitions -- cross-account hedging, simulator-fill exploitation, trading outside the
  best bid or offer, maximum size into news, coordinated trading -- and designing around detection are tier 1 too;
  they are properties of an execution model, not of a protocol's numbers, and are checked where models are built.)
* **Tier 2 -- flagged and modelled.** R at or below 1 (winners not larger than losers) and a funded position risking
  more than half the $2,000 drawdown (an account-deciding position): Responsible Trading Program triggers whose
  consequences the lockstep engine applies (`lockstep.ConductModel`). Allowed; reported as flags.
* **Tier 3 -- priced.** Account stacking and excessive purchases: a payout-denial probability in the campaign, not a
  property of a protocol (`lockstep.ConductModel.enforcement_p`).

Before D-145 the engine refused tier 2 outright (propsim D-36). The T7 comparison draft was declared under those
limits and keeps them as its own admissibility rule (`propedge.campaign.t7_grid`), so its arm count does not move.
"""
from __future__ import annotations

from typing import Any, Iterable

MIN_RR = 1.0                       # tier 2 at or below: winners not larger than losers
FUNDED_DRAWDOWN = 2000.0
MAX_FUNDED_RISK_FRACTION_OF_DRAWDOWN = 0.5   # tier 2 above: an account-deciding position
PAYOUT_PATHS = ("standard", "consistency")


def leg_findings(name: str, rr: float | None, risk: float, *, funded: bool) -> tuple[list[str], list[str]]:
    """(tier 1, tier 2) findings for one leg: its R (None = the draw's own) and dollar risk."""
    t1, t2 = [], []
    if not (risk is not None and risk > 0):
        t1.append(f"{name}: risk must be positive, got {risk}")
    if rr is not None and not rr > 0:
        t1.append(f"{name}: R must be positive, got {rr}")
    if t1:
        return t1, t2
    if rr is not None and rr <= MIN_RR:
        t2.append(f"{name}: R {rr:g}, winners not larger than losers (Responsible Trading Program)")
    cap = MAX_FUNDED_RISK_FRACTION_OF_DRAWDOWN * FUNDED_DRAWDOWN
    if funded and risk > cap:
        t2.append(f"{name}: risk ${risk:,.0f} above half the ${FUNDED_DRAWDOWN:,.0f} drawdown, an account-deciding "
                  "position (Responsible Trading Program)")
    return t1, t2


def protocol_findings(p: Any) -> tuple[list[str], list[str]]:
    t1, t2 = [], []
    for name, rr, risk, funded in (("combine", p.combine_rr, p.combine_risk, False),
                                   ("funded", p.funded_rr, p.funded_risk, True)):
        a, b = leg_findings(name, rr, risk, funded=funded)
        t1 += a
        t2 += b
    if p.payout_path not in PAYOUT_PATHS:
        t1.append(f"payout_path must be one of {PAYOUT_PATHS}, got {p.payout_path!r}")
    if getattr(p, "sizing_rule", "fixed_dollar") not in {"fixed_dollar", "fraction_of_balance"}:
        t1.append(f"unknown sizing_rule {p.sizing_rule!r}")
    if p.max_concurrent_accounts < 1:
        t1.append("max_concurrent_accounts must be at least 1")
    return t1, t2


def policy_findings(leaves: Iterable[tuple[Any, frozenset]], policy_id: str) -> tuple[list[str], list[str]]:
    """Findings for a risk policy's leaves (`RiskPolicy.root.leaves(...)`), each checked in every phase it can fire in."""
    t1, t2 = [], []
    for leaf, phases in leaves:
        if getattr(leaf, "max_trades", None) == 0:
            continue                                      # D-302: a no-trade state places nothing; nothing to find
        a, b = leg_findings(f"policy {policy_id!r}, regime {leaf.name!r}", leaf.rr, leaf.risk,
                            funded=bool(phases & {"funded", "paid"}))
        if getattr(leaf, "source", "strategy") == "collect" and not a:
            # D-379: a take-profit at the winning-day minimum against the leaf's risk -- winners smaller than losers
            b = b + [f"policy {policy_id!r}, regime {leaf.name!r}: a collect trade (a take-profit at the winning-day "
                     "minimum against its risk), winners not larger than losers (Responsible Trading Program)"]
        t1 += a
        t2 += b
    return list(dict.fromkeys(t1)), list(dict.fromkeys(t2))


__all__ = ["MIN_RR", "FUNDED_DRAWDOWN", "MAX_FUNDED_RISK_FRACTION_OF_DRAWDOWN", "PAYOUT_PATHS", "leg_findings",
           "protocol_findings", "policy_findings"]
