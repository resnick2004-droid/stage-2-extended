"""H4's replay cost (the red team's F4-4 on text 4): the vendored engine's cost of one long replay of one unit, as the
firm path's baseline mode runs it (one `customer_slices.replay` -- one `simulate_lockstep_path` -- per (start, seed
index)), timed on a deterministic synthetic campaign: no bar, no atlas, no generator, no outcome of any market. The
campaign is `tests/q76_synthetic.py`'s (every value a function of the day's and the trade's index), at up to
`three_way_arith.TAU` trades a session, over `h4_plan.WINDOWS`' longest window.

It prints the median seconds a replay over `REPEATS` timings of `REPLAYS` starts; `h4_plan.REPLAY_S` declares the
value the plan sizes H4-B at (this measurement rounded up, with the margin the plan states), and the cut rule re-sizes
the parts at H4-0's measurement on real starts before any part runs.

    python docs/plans/scripts/h4/h4_replay_cost.py <repository root>
"""
from __future__ import annotations

import statistics
import sys
import time
from pathlib import Path

REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import customer_slices as cs  # noqa: E402
from propedge.campaign.lockstep import ConductModel  # noqa: E402
from propedge.campaign.payout_method import payout_method_terms  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.contract.adapter import rules_from_ledger  # noqa: E402
from propedge.contract.rules import load_rules  # noqa: E402
from propedge.outcomes.distribution import DayBlock  # noqa: E402

N_DAYS, WINDOW, REPLAYS, REPEATS = 400, 252, 8, 3


def campaign():
    blocks = []
    for i in range(N_DAYS):
        k = 1 + (i % 4)
        et = np.array([500.0 + 60.0 * j for j in range(k)])
        bad = (i % 13) in (11, 12)
        win = np.array([(not bad) and ((i * 7 + j) % 5) < 3 for j in range(k)])
        pnl = np.where(win, 1000.0, -500.0)
        blocks.append(DayBlock(pnl=pnl, risked=np.full(k, 500.0),
                               exit_reasons=tuple("target" if w else "stop" for w in win), entry_t=et, exit_t=et + 30.0))
    rules = rules_from_ledger()
    proto = Protocol(name="h4_replay_cost", combine_rr=2.0, combine_risk=500.0, funded_rr=2.0, funded_risk=500.0,
                     trades_per_day=4, max_concurrent_accounts=5)
    lag = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
    args = {"draws": {"protocol": proto, "mode": "rotation", "flip": None},
            "path": dict(edge=0.0, rules=rules, initial_bankroll=1e9, max_concurrent_accounts=5,
                         subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                         activation=float(rules.activation), payout_lag_days=lag, max_concurrent_combines=5,
                         max_total_accounts=5, conduct=ConductModel(rtp=False, enforcement_p=0.0), combine_max_days=2000,
                         funded_horizon_days=100_000, purchase_budget=(20, 21)),
            "seed": 1}
    return blocks, args


def main() -> None:
    blocks, args = campaign()
    pd.options.mode.chained_assignment = None
    cs.replay(blocks[0:WINDOW], args)                     # warm-up, untimed
    per = []
    for _ in range(REPEATS):
        t = time.perf_counter()
        for s in range(REPLAYS):
            cs.replay(blocks[s * 10:s * 10 + WINDOW], args)
        per.append((time.perf_counter() - t) / REPLAYS)
    print(f"replay of {WINDOW} sessions, up to 4 trades a session: median {statistics.median(per):.4f} s "
          f"(runs {', '.join(f'{x:.4f}' for x in per)})")


if __name__ == "__main__":
    main()
