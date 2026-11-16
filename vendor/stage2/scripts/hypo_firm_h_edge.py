"""HYPOTHETICAL (D-206): Firm H with a planted edge, and with the two parties sharing one bankroll. NOT A CANDIDATE.

    python scripts/hypo_firm_h_edge.py [--paths 500]

The operator's question (2026-09-29): counting only the two parties' summed result, is it better to hedge or to
trade the way the project studies -- an edge, unhedged? For a planted edge of 0, 0.05 and 0.10 R per trade at 1:1
(`firm_h.up_probability`: the long side has it; at 2:1 the same walk's edge is measured and reported), four arms,
each two parties of five accounts on stage one's lifecycle, zero-edge otherwise as `scripts/hypo_firm_h.py`:

* **unhedged, own bankrolls** -- both parties trade the edge, each its own rotation on its own days;
* **hedged, own bankrolls** -- paired by state (D-204's tightest hedge), party 1 with the edge, party 2 against it, the
  same days;
* **unhedged, pooled** and **hedged, pooled** -- the same two, with one bankroll of twice a party's for the whole
  run: every fee comes out of it and every payout goes into it, so a party that runs dry keeps buying Combines from
  the other's payouts (`firm_h.run_pair(pooled=True)`, the engine's shared wallet, D-206).

Writes results/hypo_firm_h_edge.csv (EXPLORATORY, labelled): per edge, arm and scope the Combine side, the funded side
and the money, as `firm_h.arm_rows`; under pooling the money is the pair's only. Cross-account hedging stays tier 1 at
Topstep; nothing here is a candidate.
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

SCRIPT = "scripts/hypo_firm_h_edge.py"
SHARED, OTHER = fh.SEED + 1, fh.SEED + 2
EDGES = (0.0, 0.05, 0.10)
ARMS = ("unhedged, own bankrolls", "hedged, own bankrolls", "unhedged, pooled", "hedged, pooled")


def per_day() -> int:
    from propedge.research.model_card import setups_minimum

    return int(round(setups_minimum(1.0, 1500.0, 0.0) * fh.SLOTS))


def trades_for(edge: float, k: int) -> dict:
    return fh.mirrored_trades(fh.N_HISTORY * k, np.random.default_rng(fh.SEED), p_up=fh.up_probability(edge))


def _blocks(edge: float, side: str, k: int):
    cost, rpc = fh.trade_cost_r()
    return fh.day_blocks(trades_for(edge, k), side, k, cost_r=cost, rpc=rpc)


def _strip(run: fh.PartyRun) -> fh.PartyRun:
    return fh.PartyRun(measures=run.measures, cash=run.cash, initial=run.initial, taken=run.taken)


def _job(args: tuple):
    import warnings

    warnings.filterwarnings("ignore")
    (edge, what), n_paths, k = args
    if what in ("u_sep_1", "u_sep_2"):
        return fh.run_party(_blocks(edge, "l", k), seed=SHARED if what.endswith("1") else OTHER, router=None,
                            n_paths=n_paths)
    if what == "h_sep":
        a, b = fh.run_pair(_blocks(edge, "l", k), _blocks(edge, "s", k), seed=SHARED, rule=fh.MATCHED,
                           n_paths=n_paths)
        return _strip(a), _strip(b), fh.arm_rows(ARMS[1], a, b, hedged=True)
    if what == "u_pool":
        a, b = fh.run_pair(_blocks(edge, "l", k), _blocks(edge, "l", k), seed=SHARED, seed_2=OTHER, rule=None,
                           n_paths=n_paths, pooled=True)
        return _strip(a), _strip(b), fh.arm_rows(ARMS[2], a, b, hedged=False, pooled=True)
    a, b = fh.run_pair(_blocks(edge, "l", k), _blocks(edge, "s", k), seed=SHARED, rule=fh.MATCHED, n_paths=n_paths,
                       pooled=True)
    return _strip(a), _strip(b), fh.arm_rows(ARMS[3], a, b, hedged=True, pooled=True)


def main(n_paths: int = 500, results_dir: Path | None = None) -> int:
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    k = per_day()
    cost, rpc = fh.trade_cost_r()
    jobs = [(e, w) for e in EDGES for w in ("u_sep_1", "u_sep_2", "h_sep", "u_pool", "h_pool")]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=len(jobs)) as pool:
        out = dict(zip(jobs, pool.map(_job, [(j, n_paths, k) for j in jobs])))
    print(f"{len(jobs)} jobs of {n_paths} paths in {time.time() - t0:.0f}s", flush=True)
    rows = []
    for e in EDGES:
        t = trades_for(e, k)
        measured = {"edge_1to1": e, "edge_1to1_measured_net": float(t["rl1"].mean() - cost),
                    "edge_2to1_measured_net": float(t["rl2"].mean() - cost)}
        arm_rows = (fh.arm_rows(ARMS[0], out[(e, "u_sep_1")], out[(e, "u_sep_2")], hedged=False)
                    + out[(e, "h_sep")][2] + out[(e, "u_pool")][2] + out[(e, "h_pool")][2])
        rows += [{**measured, **r} for r in arm_rows]
    df = pd.DataFrame(rows)
    params = {"edges_1to1": list(EDGES), "arms": list(ARMS), "accounts_per_party": fh.SLOTS, "setups_per_day": k,
              "n_paths": n_paths, "horizon_days": fh.HORIZON, "bankroll_per_party": fh.BANKROLL,
              "pooled_bankroll": 2 * fh.BANKROLL, "lifecycle": "P-04 §3 (im2_score.policy)",
              "trades": f"brackets on a walk of step {fh.STEP} of the stop, the up step's chance set by the edge",
              "cost_per_trade_r": cost, "risk_per_contract": rpc, "hedge": "paired by state (D-204)",
              "seeds": {"trades": fh.SEED, "shared_days": SHARED, "own_days": OTHER},
              "rules": "rules_for_method('aeropay') from the verified ledger", "settlement": "mae", "denial_p": 0.0,
              "conduct_model": "none: the hypothetical firm allows the pattern (as D-153)"}
    write_result(df, "hypo_firm_h_edge", script=SCRIPT, seed=fh.SEED, exploratory=True, results_dir=results_dir,
                 parameters=params, notes={"decisions": ["D-203", "D-204", "D-205", "D-206"], "status": fh.LABEL},
                 description="HYPOTHETICAL: Firm H with a planted edge of 0, 0.05 and 0.10 R at 1:1: unhedged and "
                             "hedged (paired by state) pairs, each with its own bankrolls and with one shared "
                             "bankroll; the Combine side, the funded side and the pair's money.")
    VariantCounter().record(prereg_id="D-203:hypothetical_firm_h", params={"study": "edge sweep, pooled bankroll",
                            "edges": list(EDGES), "n_paths": n_paths, "decision": "D-206"}, seed=fh.SEED,
                            exploratory=True, label=fh.LABEL)
    pd.set_option("display.width", 300)
    print(fh.LABEL)
    cols = ["edge_1to1", "arm", "combine_pass_rate", "payouts_mean", "net_cash_mean", "net_cash_p10",
            "share_losing_money", "median_log_growth"]
    print(df[df["scope"] == "pair"][cols].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--paths", type=int, default=500)
    raise SystemExit(main(n_paths=ap.parse_args().paths))
