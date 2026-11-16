"""HYPOTHETICAL (D-203, D-204): Firm H, two parties hedging each other. NOT A CANDIDATE.

    python scripts/hypo_firm_h.py [--paths 500]

Cross-account hedging is prohibited at Topstep (10296582, tier 1) and stays so; this is a contract-structure study at
the operator's request (`propedge/research/firm_h.py` states the model). Nine arms, each two parties of five accounts
on stage one's lifecycle, on zero-edge trades five a day (D-154's minimum of one a day per account):

1. **normal rotation** -- each party rotates its own accounts, on its own days;
2. **paired by seat, hedged** -- each trade to the same seat in both parties, one long and one short, the same days;
3. **paired by seat, independent days** -- arm 2's routing without the hedge;
4. **paired by state, hedged** (D-204) -- a Combine against a Combine, a funded account against one in the same state;
5. **funded against Combine, hedged** (D-204) -- a funded account set against a Combine wherever one is free;
6. **paired by state, hedged, risk capped at room** (D-205) -- arm 4 with each trade risking no more than the
   account's room above its loss limit (at least one micro);
7. **paired by seat, independent days, risk capped at room** (D-205) -- arm 3 with the same cap: the cap alone;
8. **paired by state then similar room, hedged** (D-205) -- within each state, accounts with similar room together;
9. **paired by state then most room against least, hedged** (D-205).

Party 1 of arm 2 also serves arm 3, so the two differ only in party 2's days. Six workers run in parallel; arms 4 and 5
run their two parties in step in two threads. Writes results/hypo_firm_h.csv (EXPLORATORY, labelled) with two
sections: `accounts` -- per arm and scope (each party and the pair) the Combine side (A), the funded side (B) and the
money; and `hedged pairs` (arms 2, 4 and 5) -- what the hedged pairs held, all together and by composition: each
side's balance and room above its loss limit, the pair's net P&L and the dollars the hedge left open, how often both
sides lost, and in mixed pairs how often the funded side won.
"""
from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.research import firm_h as fh  # noqa: E402

SCRIPT = "scripts/hypo_firm_h.py"
SHARED, OTHER = fh.SEED + 1, fh.SEED + 2          # the campaign seeds: the shared days, and party 2's own days
ARMS = {1: "1 normal rotation", 2: "2 paired by seat, hedged", 3: "3 paired by seat, independent days",
        4: "4 paired by state, hedged", 5: "5 funded against Combine, hedged",
        6: "6 paired by state, hedged, risk capped at room", 7: "7 paired by seat, independent days, risk capped at room",
        8: "8 paired by state then similar room, hedged", 9: "9 paired by state then most room against least, hedged"}
#: (what runs, and how): a party on its own, or both parties of a hedged arm; the last field caps risk at the room
JOBS = {"arm1_p1": ("party", "l", SHARED, None, False), "arm1_p2": ("party", "s", OTHER, None, False),
        "arm3_p2": ("party", "s", OTHER, fh.SEAT, False), "arm2": ("pair", fh.SEAT, 2, False),
        "arm4": ("pair", fh.MATCHED, 4, False), "arm5": ("pair", fh.CROSSED, 5, False),
        "arm6": ("pair", fh.MATCHED, 6, True), "arm7_p1": ("party", "l", SHARED, fh.SEAT, True),
        "arm7_p2": ("party", "s", OTHER, fh.SEAT, True), "arm8": ("pair", fh.BALANCE_MATCHED, 8, False),
        "arm9": ("pair", fh.BALANCE_OPPOSED, 9, False)}


def per_day() -> int:
    """D-154: one setup a day per account at the 1:1 $1,500 Combine at zero edge, for each of the five slots."""
    from propedge.research.model_card import setups_minimum

    return int(round(setups_minimum(1.0, 1500.0, 0.0) * fh.SLOTS))


def _blocks(side: str, k: int):
    trades = fh.mirrored_trades(fh.N_HISTORY * k, np.random.default_rng(fh.SEED))
    cost, rpc = fh.trade_cost_r()
    return fh.day_blocks(trades, side, k, cost_r=cost, rpc=rpc)


def _strip(run: fh.PartyRun) -> fh.PartyRun:
    return fh.PartyRun(measures=run.measures, cash=run.cash, initial=run.initial, taken=run.taken)


def _job(args: tuple):
    import warnings

    warnings.filterwarnings("ignore")
    job, n_paths, k = args
    _, rpc = fh.trade_cost_r()
    if job[0] == "party":
        _, side, seed, router, cap = job
        return fh.run_party(_blocks(side, k), seed=seed, router=router, record=cap, cap_at_room=cap, min_risk=rpc,
                            n_paths=n_paths)
    _, rule, arm, cap = job
    a, b = fh.run_pair(_blocks("l", k), _blocks("s", k), seed=SHARED, rule=rule, n_paths=n_paths,
                       cap_at_room=cap, min_risk=rpc)
    rows = fh.arm_rows(ARMS[arm], a, b, hedged=True) + fh.pair_rows(ARMS[arm], a, b)
    return _strip(a), _strip(b), rows


def main(n_paths: int = 500, results_dir: Path | None = None) -> int:
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    k = per_day()
    cost, rpc = fh.trade_cost_r()
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=len(JOBS)) as pool:
        out = dict(zip(JOBS, pool.map(_job, [(job, n_paths, k) for job in JOBS.values()])))
    print(f"{len(JOBS)} jobs of {n_paths} paths in {time.time() - t0:.0f}s", flush=True)
    p1_seat = out["arm2"][0]
    rows = (fh.arm_rows(ARMS[1], out["arm1_p1"], out["arm1_p2"], hedged=False) + out["arm2"][2]
            + fh.arm_rows(ARMS[3], p1_seat, out["arm3_p2"], hedged=False) + out["arm4"][2] + out["arm5"][2]
            + out["arm6"][2] + fh.arm_rows(ARMS[7], out["arm7_p1"], out["arm7_p2"], hedged=False)
            + out["arm8"][2] + out["arm9"][2])
    df = pd.DataFrame(rows)
    df = pd.concat([df[df["section"] == "accounts"], df[df["section"] == "hedged pairs"]], ignore_index=True)
    params = {"accounts_per_party": fh.SLOTS, "setups_per_day": k, "n_paths": n_paths, "horizon_days": fh.HORIZON,
              "bankroll_per_party": fh.BANKROLL, "lifecycle": "P-04 §3 (im2_score.policy)", "edge": 0.0,
              "trades": f"zero-edge brackets on a driftless walk, step {fh.STEP} of the stop, both sides read off it",
              "cost_per_trade_r": cost, "risk_per_contract": rpc, "stop": f"{fh.MICRO} {fh.STOP_TICKS} ticks",
              "history_days": fh.N_HISTORY, "seeds": {"trades": fh.SEED, "shared_days": SHARED, "own_days": OTHER},
              "arms": ARMS, "pairing": "each account at most one trade a day in every paired arm",
              "rules": "rules_for_method('aeropay') from the verified ledger", "settlement": "mae",
              "denial_p": 0.0, "conduct_model": "none: the hypothetical firm allows the pattern (as D-153)",
              "bankrolls": "separate; the pair's figures are sums", "balance": "profit since the account began"}
    write_result(df, "hypo_firm_h", script=SCRIPT, seed=fh.SEED, exploratory=True, results_dir=results_dir,
                 parameters=params, notes={"decisions": ["D-203", "D-204", "D-205"], "status": fh.LABEL},
                 description="HYPOTHETICAL: Firm H, two parties of five accounts on stage one's lifecycle, zero-edge "
                             "trades, nine arms (normal rotation; paired by seat hedged and on independent days; "
                             "paired by state; funded against Combine; the room cap hedged and alone; paired by "
                             "state and room, similar and opposed): the accounts per party and for the pair, and "
                             "what the hedged pairs held.")
    VariantCounter().record(prereg_id="D-203:hypothetical_firm_h", params={"arms": sorted(ARMS.values()),
                            "n_paths": n_paths, "decision": "D-205"}, seed=fh.SEED, exploratory=True, label=fh.LABEL)
    pd.set_option("display.width", 300)
    print(fh.LABEL)
    print(df.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--paths", type=int, default=500)
    raise SystemExit(main(n_paths=ap.parse_args().paths))
