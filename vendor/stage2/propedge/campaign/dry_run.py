"""The T7a dry run: the campaign engine exercised end to end at an ASSUMED edge (D-119).

This is the done-criterion of T7a, not a result: every file it writes carries
`exploratory=True` and the assumed inputs in its manifest, and nothing here is cited anywhere.
Its purposes are three: to show the engine runs end to end through the result writer; to give
the results viewer (`propedge.reporting.campaign_viewer`) real files to read; and to measure the
lockstep loop's throughput, which the T7 draft's blocking item 6 needs before its path count is
fixed.

What is assumed, and labelled as such in every manifest:

* the edge: the criterion's lower bound, 0.05, as a stand-in for the T5 input that does not
  exist;
* the outcome process: the binary process at that edge (the validation limit), not a trade log;
* the risk per contract: $25, an MES stop of 20 ticks at $1.25 a tick -- the ES/MES cost floor
  from `results/wide_stop_admissibility.csv` -- so tier sizing has something to size;
* the bankroll: $5,000, pending the operator's decision on the two bankrolls to report.

Everything else is the verified ledger and the T7 draft's stage-1 settings: copier mode,
`current_tier` sizing at headroom 0.75, Aeropay terms, activation on activation.
"""
from __future__ import annotations

import time
from dataclasses import replace
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

from propedge.campaign.lockstep import LockstepPath, simulate_lockstep_campaign
from propedge.campaign.payout_method import rules_for_method
from propedge.campaign.protocols import REGISTRY, Protocol
from propedge.campaign.shared_days import COPIER, SharedDayDraws
from propedge.campaign.sizing import CURRENT_TIER, DEFAULT_HEADROOM_FRAC, SizingRule
from propedge.outcomes.distribution import binary_blocks
from propedge.reporting.results import write_result

ASSUMED_EDGE = 0.05
ASSUMED_RISK_PER_CONTRACT = 25.0
ASSUMED_BANKROLL = 5_000.0
DRY_RUN_SEED = 20260925
SCRIPT = "scripts/campaign_dry_run.py"

#: Registry protocols exercised, each at these account counts.
DEFAULT_PROTOCOLS = ("s1_pair_low_edge", "s1_pair_high_edge", "buffer_8000", "fast_take_max")
DEFAULT_ACCOUNT_COUNTS = (1, 5)


def dry_run_arms(
    names: Sequence[str] = DEFAULT_PROTOCOLS, account_counts: Sequence[int] = DEFAULT_ACCOUNT_COUNTS
) -> list[Protocol]:
    arms = []
    for name in names:
        base = REGISTRY.get(name)
        for n in account_counts:
            arms.append(replace(base, name=f"{name}_n{n}", max_concurrent_accounts=int(n),
                                family=f"dry_run:{base.family}"))
    return arms


def _path_row(arm: str, i: int, r: LockstepPath) -> dict[str, Any]:
    p = r.path
    return {
        "arm": arm, "path": i, "final_cash": p.final_cash, "log_growth": p.log_growth(),
        "ruined": p.ruined, "ruin_day": -1 if p.ruin_day is None else p.ruin_day,
        "max_drawdown": p.max_drawdown, "attempts_started": p.attempts_started,
        "accounts_funded": p.accounts_funded, "accounts_ever_paid": p.accounts_ever_paid,
        "days_to_first_payout": -1 if p.days_to_first_payout is None else p.days_to_first_payout,
        "total_fees": p.total_fees, "total_payouts": p.total_payouts,
        "peak_queue_length": p.peak_queue_length, "passes_forfeited": p.passes_forfeited,
        "combines_abandoned": p.combines_abandoned,
        "same_day_multi_breach_days": p.same_day_multi_breach_days,
        "max_breaches_in_one_day": p.max_breaches_in_one_day,
        "trades_sized": p.trades_sized, "trades_at_tier_cap": p.trades_at_tier_cap,
        "trades_unsized": p.trades_unsized, "intended_risk_total": p.intended_risk_total,
        "realised_risk_total": p.realised_risk_total,
    }


def _account_rows(arm: str, i: int, r: LockstepPath) -> list[dict[str, Any]]:
    rows = []
    for c in r.combines:
        outcome = ("passed" if c.passed else "failed" if c.failed else "abandoned" if c.abandoned
                   else "unresolved" if c.unresolved else "running")
        rows.append({
            "arm": arm, "path": i, "kind": "combine", "index": c.index,
            "start_day": c.purchase_day + 1,
            "end_day": -1 if c.resolved_on is None else c.resolved_on,
            "outcome": outcome, "days": c.days, "trades": c.trades, "balance": c.balance,
            "n_payouts": 0, "payout_days": "", "breach_day": c.resolved_on if c.failed else -1,
        })
    for a in r.funded:
        outcome = "closed" if a.closed else ("ended" if a.ended_on is not None else "running")
        rows.append({
            "arm": arm, "path": i, "kind": "funded", "index": a.index,
            "start_day": a.activation_day + 1,
            "end_day": -1 if a.ended_on is None else a.ended_on,
            "outcome": outcome, "days": a.days, "trades": a.trades, "balance": a.balance,
            "n_payouts": a.n_payouts,
            "payout_days": ";".join(str(a.activation_day + 1 + d) for d in a.payout_days),
            "breach_day": a.ended_on if a.closed else -1,
        })
    return rows


def run_dry_run(
    *,
    results_dir: Path | str | None = None,
    arms: Sequence[Protocol] | None = None,
    n_paths: int = 150,
    horizon_days: int = 504,
    cash_paths_per_arm: int = 12,
    edge: float = ASSUMED_EDGE,
    bankroll: float = ASSUMED_BANKROLL,
    risk_per_contract: float = ASSUMED_RISK_PER_CONTRACT,
    seed: int = DRY_RUN_SEED,
    prefix: str = "t7a_dry_run",
    ledger: Any | None = None,
) -> dict[str, Path]:
    """Run the arms and write four result files with manifests. Returns their paths."""
    arms = list(arms) if arms is not None else dry_run_arms()
    rules = rules_for_method("aeropay", ledger=ledger)
    sizing = SizingRule.from_ledger(CURRENT_TIER, headroom_frac=DEFAULT_HEADROOM_FRAC, ledger=ledger)
    assumed = {
        "assumed_edge": float(edge),
        "assumed_outcome_process": "binary at the assumed edge (the validation limit), not a trade log",
        "assumed_risk_per_contract_usd": float(risk_per_contract),
        "assumed_risk_per_contract_basis": "MES, 20-tick stop at $1.25 a tick (the ES/MES cost floor)",
        "assumed_bankroll_usd": float(bankroll),
        "cited": "nowhere: this is T7a's done-criterion dry run (D-119), not a result",
    }

    arm_rows: list[dict[str, Any]] = []
    path_rows: list[dict[str, Any]] = []
    cash_rows: list[dict[str, Any]] = []
    account_rows: list[dict[str, Any]] = []
    throughput: dict[str, float] = {}

    for j, arm in enumerate(arms):
        blocks = binary_blocks(
            arm.combine_rr, arm.combine_risk, edge, 1024, seed=seed + 1000 + j,
            risk_per_contract=risk_per_contract,
        )
        t0 = time.perf_counter()
        summary, results = simulate_lockstep_campaign(
            arm, edge=edge, seed=seed + j, rules=rules, initial_bankroll=bankroll,
            horizon_days=horizon_days, n_paths=n_paths, payout_method="aeropay",
            max_concurrent_accounts=arm.max_concurrent_accounts, require_verified_cap=False,
            max_concurrent_combines=1, ledger=ledger,
            draw_factories_for_path=lambda s, blocks=blocks, arm=arm: SharedDayDraws(
                {0: blocks}, protocol=arm, seed=s, mode=COPIER, sizing=sizing
            ).factories(),
        )
        elapsed = time.perf_counter() - t0
        throughput[arm.name] = n_paths / elapsed if elapsed > 0 else float("nan")

        row = {k: v for k, v in summary.as_dict().items() if k != "provenance"}
        row.update({
            "arm": arm.name, "base_protocol": arm.name.rsplit("_n", 1)[0],
            "combine_rr": arm.combine_rr, "combine_risk": arm.combine_risk,
            "funded_rr": arm.funded_rr, "funded_risk": arm.funded_risk,
            "payout_path": arm.payout_path, "keep_balance": arm.keep_balance,
            "payout_frac": arm.payout_frac, "accounts": arm.max_concurrent_accounts,
            "paths_per_second": throughput[arm.name], "seconds": elapsed,
        })
        arm_rows.append(row)
        for i, r in enumerate(results):
            path_rows.append(_path_row(arm.name, i, r))
            if i < cash_paths_per_arm:
                for day, cash in enumerate(r.path.cash_series):
                    cash_rows.append({"arm": arm.name, "path": i, "day": day, "cash": float(cash)})
        account_rows.extend(_account_rows(arm.name, 0, results[0]))

    common = dict(
        script=SCRIPT, seed=seed, exploratory=True, results_dir=results_dir,
        notes=assumed,
    )
    parameters = {
        "arms": [a.name for a in arms], "n_paths": n_paths, "horizon_days": horizon_days,
        "cash_paths_per_arm": cash_paths_per_arm, "edge": edge, "bankroll": bankroll,
        "risk_per_contract": risk_per_contract, "mode": COPIER,
        "sizing": sizing.as_dict(), "payout_method": "aeropay",
        "activation_timing": "on_activation", "max_concurrent_combines": 1,
        "rules": "rules_for_method('aeropay') from the verified ledger",
        "engine": "propedge.campaign.lockstep.simulate_lockstep_campaign",
        "throughput_paths_per_second": throughput,
    }
    out: dict[str, Path] = {}
    out["arms"], _ = write_result(
        pd.DataFrame(arm_rows), f"{prefix}_arms", parameters=parameters,
        description="T7a dry run: one row per arm, the campaign summary at an ASSUMED edge. "
                    "Exploratory; cited nowhere.", **common,
    )
    out["paths"], _ = write_result(
        pd.DataFrame(path_rows), f"{prefix}_paths", parameters=parameters,
        description="T7a dry run: one row per path. Exploratory; cited nowhere.", **common,
    )
    out["cash"], _ = write_result(
        pd.DataFrame(cash_rows), f"{prefix}_cash", parameters=parameters,
        description=f"T7a dry run: campaign cash by day for the first {cash_paths_per_arm} paths "
                    "of each arm. Exploratory; cited nowhere.", **common,
    )
    out["accounts"], _ = write_result(
        pd.DataFrame(account_rows), f"{prefix}_accounts", parameters=parameters,
        description="T7a dry run: every account of path 0 of each arm, with its span and outcome. "
                    "Exploratory; cited nowhere.", **common,
    )
    return out


__all__ = [
    "ASSUMED_EDGE", "ASSUMED_RISK_PER_CONTRACT", "ASSUMED_BANKROLL", "DRY_RUN_SEED",
    "dry_run_arms", "run_dry_run",
]
