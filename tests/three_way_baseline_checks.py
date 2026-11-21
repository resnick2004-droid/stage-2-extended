"""Q-185c: the baseline mode's checks in their own process (`extended/three_way_baseline.py` imports the vendored engine):
prints one JSON line, read by `tests/test_three_way_baseline.py`. A synthetic job on P-16's machinery -- tier sizing
(`SizingRule.from_ledger`, `TierSizedDraw`), every trade's outcome and exit at two Rs (`r_by_rr`, `exit_by_rr`), the
legs at different Rs, the vendored router with the strict rule (`one_at_a_time` 5, D-429) and `can_take` (`route_able`),
held to each account's own exit (`hold_to_own_exit`) -- with same-bar exits and breakeven kinds. No bar, no result.

- `identity` -- with the vendored P&L passed through, the baseline mode's replay equals `customer_slices.replay` bit
  for bit, field for field, at several starts; and the race arm's paths differ from it (not vacuous);
- `race` -- the race arm: every trade booked by the law of its kind at the R its account used (t and s raced, f walked,
  b by the move), both Rs used, same-bar exits taken; the engine's ledger holds no two positions open across accounts
  within the strict gap on the bar-end clock, at each account's own R. (Each law's own exactness is the runner's and
  `three_way_move`'s tests'.)
"""
from __future__ import annotations

import dataclasses
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402

import customer_slices as CS  # noqa: E402
from propedge.campaign.lockstep import ConductModel  # noqa: E402
from propedge.campaign.payout_method import payout_method_terms  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.campaign.risk_policy import RiskPolicy  # noqa: E402
from propedge.campaign.sizing import SizingRule  # noqa: E402
from propedge.contract.adapter import rules_from_ledger  # noqa: E402
from propedge.contract.rules import load_rules  # noqa: E402
from propedge.outcomes.distribution import DayBlock  # noqa: E402

import three_way_firm_checks as FC  # noqa: E402  (its record comparison)
from extended import three_way_baseline as TB  # noqa: E402
from extended import three_way_journey as J  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402

SEED = S.issue("tests")
PART = S.PARTS["tests"]
N_DAYS = 70
RS = (1.5, 2.0)
STOP = 40                                  # ticks
TICK = 0.5                                 # a micro's tick value (MNQ)
OPENS = (0, 120, 930, 1200)                # FV3's session opens on the bar-end clock (17:00, 19:00, 08:30, 13:00 CT)
LIMIT = 1330                               # 15:10 CT


def _kind(i: int, j: int, R: float) -> str:
    return "tsfb"[(i * 3 + j + int(R * 2)) % 4]


def job() -> tuple[list, dict, dict]:
    rng = np.random.default_rng([int(SEED), 185])
    blocks, facts = [], {}
    for i in range(N_DAYS):
        k = 1 + i % 3
        et = np.array([940.0 + 70.0 * j for j in range(k)])
        r_by, ex_by = {}, {}
        for R in RS:
            kinds = [_kind(i, j, R) for j in range(k)]
            r = np.array([{"t": R, "s": -1.0, "f": float(rng.normal(0, 0.3)), "b": 0.0}[c] - 0.05 for c in kinds])
            ex = np.array([et[j] if (i + j) % 7 == 0 else et[j] + 20.0 + 10.0 * j for j in range(k)])  # same-bar
            r_by[R], ex_by[R] = r, ex
        rpc = np.full(k, STOP * TICK)
        blocks.append(DayBlock(pnl=r_by[2.0] * 500.0, risked=np.full(k, 500.0), exit_reasons=tuple("x" * k),
                               risk_per_contract=rpc, mae=np.full(k, 250.0), entry_t=et, exit_t=ex_by[2.0],
                               r_by_rr=r_by, mae_by_rr={R: np.full(k, 0.5) for R in RS}, fee=np.full(k, 0.74),
                               sides=np.ones(k), exit_by_rr=ex_by))
        for j in range(k):
            ent = int(et[j])
            be = next((o + 1 for o in OPENS if o > ent), None)
            kinds = {R: _kind(i, j, R) for R in RS}
            facts[(i, j)] = TB.TradeFacts(decision=ent - 5, entry=ent, stop_ticks=STOP, tick_value=TICK, kinds=kinds,
                                          limit=LIMIT, sigma=1.5, be_open=be if be is not None and be < LIMIT else None,
                                          e_ticks=0.5, xt_ticks=0.0, xs_ticks=1.0, xf_ticks=2.0)
    # a breakeven kind with no move bar left before the limit is not a fact this job may carry: drop its b
    facts = {key: (f if f.be_open is not None else dataclasses.replace(
        f, kinds={R: ("f" if c == "b" else c) for R, c in f.kinds.items()})) for key, f in facts.items()}
    rules = rules_from_ledger()
    proto = Protocol(name="q185c_synthetic", combine_rr=1.5, combine_risk=500.0, funded_rr=2.0, funded_risk=400.0,
                     trades_per_day=4, max_concurrent_accounts=5)
    lag = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
    args = {"draws": {"protocol": proto, "mode": "rotation", "flip": None, "sizing": SizingRule.from_ledger(),
                      "route_able": True, "one_at_a_time": 5.0, "hold_to_own_exit": True},
            "path": dict(edge=0.0, rules=rules, initial_bankroll=1e9, max_concurrent_accounts=5,
                         subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                         activation=float(rules.activation), payout_lag_days=lag, max_concurrent_combines=2,
                         max_total_accounts=3, conduct=ConductModel(rtp=False, enforcement_p=0.0),
                         combine_max_days=2000, funded_horizon_days=100_000, record_trades=True,
                         risk_policy=RiskPolicy.from_protocol(proto, with_rr=True)),     # each leg at its own R
            "seed": int(SEED)}
    return blocks, args, facts


def identity(blocks, args, facts) -> dict:
    h, diffs, cross = 42, [], 0
    for start in (0, 7, 20):
        theirs = CS.replay(blocks[start:start + h], args, h)
        mine = TB.replay(blocks[start:start + h], args, h, outcome="vendored")
        diffs += FC.same(mine, theirs, f"start{start}")
        rec = TB.simulate(blocks, args, facts, start, range(2), h, seed=SEED, part=PART, history=0,
                          block_sessions=N_DAYS, outcome="race", keep_paths=True, log_rr=2.0)
        cross += len(FC.same(rec.paths[0], theirs, "race"))
    return {"n_diffs": len(diffs), "diffs": diffs[:5], "cross_diffs": cross,
            "trades": len(theirs.trades), "passes": sum(int(c.passed) for c in theirs.combines)}


def race(blocks, args, facts) -> dict:
    h, lanes, start = 42, 16, 3
    rec = TB.simulate(blocks, args, facts, start, range(lanes), h, seed=SEED, part=PART, history=0,
                      block_sessions=N_DAYS, outcome="race", keep_paths=True, log=True, log_rr=2.0)
    laws, rs, kinds, bad, overlap, same_bar = {}, set(), {}, 0, 0, 0
    want = {"t": "race", "s": "race", "f": "walk", "b": "move"}
    for rows, path in zip(rec.logs, rec.paths):
        booked = {(int(t["day"]), int(t["trade_index"])): float(t["pnl"]) for t in path.trades}
        for i, j, R, kind, room, law, out in rows:
            laws[law] = laws.get(law, 0) + 1
            kinds[kind] = kinds.get(kind, 0) + 1
            rs.add(R)
            if law in ("race", "walk", "move") and want[kind] != law:
                bad += 1
            if law == "fill_fail" and booked.get((i - start + 1, j)) != -room:   # the engine booked the whole room
                bad += 1
            same_bar += int(facts[(i, j)].entry == int(blocks[i].exit_by_rr[R][j]))
        # the engine's ledger: no two positions within the strict gap across accounts, at each account's own R
        spans = []
        for t in path.trades:
            day = int(t["day"])
            i = start + day - 1
            j = int(t["trade_index"])
            R = float(t.get("rr_used", t.get("rr")))
            spans.append((day * 1440 + float(blocks[i].entry_t[j]), day * 1440 + float(blocks[i].exit_by_rr[R][j])))
        spans.sort()
        overlap += sum(1 for a, b in zip(spans, spans[1:]) if b[0] < a[1] + 5.0)
    return {"laws": laws, "kinds": kinds, "rs": sorted(rs), "bad": bad, "overlap": overlap, "same_bar": same_bar,
            "lanes": lanes, "accounts": int(rec.accounts.sum())}


def main() -> None:
    blocks, args, facts = job()
    out = {"identity": identity(blocks, args, facts), "race": race(blocks, args, facts)}
    print(json.dumps(out, default=str))


if __name__ == "__main__":
    main()
