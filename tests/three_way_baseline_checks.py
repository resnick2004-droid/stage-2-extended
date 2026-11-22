"""Q-185c: the baseline mode's checks in their own process (`extended/three_way_baseline.py` imports the vendored engine):
prints one JSON line, read by `tests/test_three_way_baseline.py`. Synthetic jobs on P-16's machinery -- FV3-C's protocol
switches (`need_aware_exits`, `consistency_cap_exits`), tier sizing with the fee re-priced at size (D-324), every
trade's outcome and exit at two Rs, each leg at its own R by a risk policy, the vendored router with the strict rule
(5, D-429) and `can_take`, held to each account's own exit -- with same-bar exits and move bars; and one with a daily
loss limit (a test fixture's evaluation account). No bar, no result.

- `identity` -- the vendored P&L passed through equals `customer_slices.replay` bit for bit at several starts, through
  passes and funded accounts; the race arm differs;
- `as_walked` -- H4's as-walked reading, the reflected path: each trade's historical gross at its R on the unit's side
  coin, the stop side's cost (n-5), every row against this file's own booking on the scalar key path; it moves with
  the seed;
- `rebooked` -- each trade's historical gross at its R re-booked with the race arm's costs (the fee from the engine
  at size) equals the vendored P&L wherever the room does not bind (C2-2);
- `race` -- **an independent oracle re-books every logged row** from the trade's facts, the R the engine read it at
  (its ledger's `rr`), the room, the fee at size from the fee schedule, and the unit's own uniforms (the scalar key
  path; this file's own walker): the race, the walk, the time-limited move, the take at the fill; need-aware exits at
  the as-placed target; fill failures booked by the engine at the room; the ledger's historical fields marked not
  applicable; the draw's trade counts the race's own; the counts beside (the move law's trades, the redrawn and FV3's
  historical `b` exits, the move bars that differ from s + 1);
- `dll` -- under a daily loss limit, the day ends at the take and the account takes no later trade that session.

`p16` (argv `p16`; heavy, the lead's): the vendored identity on P-16's own job (`user_journey.BUILDERS["p16"]`), at
starts reaching funded accounts and payouts.
"""
from __future__ import annotations

import dataclasses
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402

import customer_slices as CS  # noqa: E402
from propedge.campaign.lockstep import CombineAccount, ConductModel  # noqa: E402
from propedge.campaign.payout_method import payout_method_terms  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.campaign.risk_policy import RiskPolicy  # noqa: E402
from propedge.campaign.sizing import SizingRule  # noqa: E402
from propedge.contract.adapter import rules_from_ledger  # noqa: E402
from propedge.contract.rules import load_rules  # noqa: E402
from propedge.outcomes.distribution import DayBlock  # noqa: E402

import three_way_firm_checks as FC  # noqa: E402  (its record comparison and its own scalar walker)
from extended import three_way_baseline as TB  # noqa: E402
from extended import three_way_keys as K  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402

SEED = S.issue("tests")
PART = S.PARTS["tests"]
N_DAYS = 80
RS = (1.5, 2.0)
STOP = 40                                  # ticks
TICK = 0.5                                 # a micro's tick value (MNQ)
OPENS = (0, 120, 930, 1200)                # FV3's session opens on the bar-end clock (17:00, 19:00, 08:30, 13:00 CT)
LIMIT = 1330                               # 15:10 CT
FEES = (1.22, 3.78)                        # the fixture's round turns (a micro, a mini): D-324's mini mix
E_T, XT_T, XS_T, XF_T = 0.5, 0.0, 1.0, 2.0  # the fixture's tick costs: entry spread, target, stop / breakeven, flatten
LOG_FEE = 0.74                             # the log's own fee a micro (re-priced by the draw at size)
DLL = 560.0                                # one full-stop loss ($532.40 at 25 micros) leaves $27.60, under the costs
WALK_MAX = 1024
SIGMA = 6.0                                # ticks per sqrt minute: the move's two steps differ (phase 1's from its time)


class DllCombine(CombineAccount):
    """A test fixture's evaluation with a daily loss limit (the engine's own `dll` machinery)."""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.dll = DLL


def _kind(i: int, j: int, R: float) -> str:
    return "ttsfb"[(i * 3 + j + int(R * 2)) % 5]


def job(dll: bool = False) -> tuple[list, dict, dict]:
    rng = np.random.default_rng([int(SEED), 185, int(dll)])
    blocks, facts = [], {}
    for i in range(N_DAYS):
        k = 1 + i % 3
        # odd days fill after 13:00 CT (no move bar before 15:10: the race and the walk by kind), even days before it
        et = np.array([(1210.0 + 30.0 * j) if i % 2 else (940.0 + 70.0 * j) for j in range(k)])
        bes, kinds_by = [], []
        for j in range(k):                                  # each trade's move bar and its kinds first (the block's
            ent = int(et[j])                                # booking below follows the kinds the facts carry)
            s_open = next((o for o in OPENS if o > ent), None)
            be = None if s_open is None else s_open + 1               # N-1: the move bar's end index, s + 1
            kinds = {R: _kind(i, j, R) for R in RS}
            if be is None or be >= LIMIT:
                kinds = {R: ("f" if c == "b" else c) for R, c in kinds.items()}
            bes.append(be)
            kinds_by.append(kinds)
        # under the limit's job the session's third trade has a wider stop (cheaper a tick): a day ended at the take
        # must still refuse it (C2-3's B6)
        stops = np.array([(2 * STOP if (dll and j == 2) else STOP) for j in range(k)])
        r_by, ex_by, walked_by = {}, {}, {}
        for R in RS:
            Gs = [TB.target_ticks(R, int(stops[j])) for j in range(k)]
            gross = np.array([{"t": Gs[j], "s": -float(stops[j]), "b": 0.0,
                               "f": float(np.round(rng.uniform(-stops[j] + 1, Gs[j] - 1)))}[kinds_by[j][R]]
                              for j in range(k)])
            ex_t = np.array([{"t": XT_T, "s": XS_T, "b": XS_T, "f": XF_T}[kinds_by[j][R]] for j in range(k)])
            r_by[R] = (gross - E_T - ex_t) / stops - LOG_FEE / (stops * TICK)
            ex_by[R] = np.array([et[j] if (i + j) % 7 == 0 else et[j] + 20.0 + 10.0 * j for j in range(k)])
            walked_by[R] = gross
        rpc = stops * TICK
        blocks.append(DayBlock(pnl=r_by[2.0] * 500.0, risked=np.full(k, 500.0), exit_reasons=tuple("x" * k),
                               risk_per_contract=rpc, mae=np.full(k, 150.0), entry_t=et, exit_t=ex_by[2.0],
                               r_by_rr=r_by, mae_by_rr={R: np.full(k, 0.3) for R in RS}, fee=np.full(k, LOG_FEE),
                               sides=np.ones(k), exit_by_rr=ex_by))
        for j in range(k):
            ent, be = int(et[j]), bes[j]
            facts[(i, j)] = TB.TradeFacts(
                decision=ent - 5, entry=ent, stop_ticks=int(stops[j]), tick_value=TICK, kinds=kinds_by[j],
                limit=LIMIT, sigma=SIGMA, be_open=be, be_vendored=(None if be is None else be + (1 if (i + j) % 11 == 0 else 0)),
                e_ticks=E_T, xt_ticks=XT_T, xs_ticks=XS_T, xf_ticks=XF_T, fee_per_contract=LOG_FEE,
                walked={R: float(walked_by[R][j]) for R in RS})
    rules = rules_from_ledger()
    proto = Protocol(name="q185c_synthetic", combine_rr=1.5, combine_risk=500.0, funded_rr=2.0, funded_risk=400.0,
                     trades_per_day=4, max_concurrent_accounts=5,
                     params={"need_aware_exits": True, "consistency_cap_exits": True})     # FV3-C's switches (C2-1)
    lag = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
    path = dict(edge=0.0, rules=rules, initial_bankroll=1e9, max_concurrent_accounts=5,
                subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                activation=float(rules.activation), payout_lag_days=lag, max_concurrent_combines=2,
                max_total_accounts=3, conduct=ConductModel(rtp=False, enforcement_p=0.0), combine_max_days=2000,
                funded_horizon_days=100_000, record_trades=True,
                risk_policy=RiskPolicy.from_protocol(proto, with_rr=True))     # each leg at its own R
    if dll:                                                 # one seat: one account takes the session's trades
        path.update(combine_account_cls=DllCombine, max_total_accounts=1, max_concurrent_combines=1)
    sizing = dataclasses.replace(SizingRule.from_ledger(), fee_schedule=FEES)
    args = {"draws": {"protocol": proto, "mode": "rotation", "flip": None, "sizing": sizing, "route_able": True,
                      "one_at_a_time": 5.0, "hold_to_own_exit": True},
            "path": path, "seed": int(SEED)}
    return blocks, args, facts


def run(blocks, args, facts, start, lanes, h, **kw):
    return TB.simulate(blocks, args, facts, start, range(lanes), h, seed=SEED, part=PART, history=0,
                       block_sessions=N_DAYS, **kw)


def identity(blocks, args, facts) -> dict:
    h, diffs, cross, passes, funded = 63, [], 0, 0, 0
    for start in (0, 9, 16):
        theirs = CS.replay(blocks[start:start + h], args, h)
        mine = TB.replay(blocks[start:start + h], args, h, outcome="vendored")
        diffs += FC.same(mine, theirs, f"start{start}")
        rec = run(blocks, args, facts, start, 2, h, outcome="race", keep_paths=True)
        cross += len(FC.same(rec.paths[0], theirs, "race"))
        passes += sum(int(c.passed) for c in theirs.combines)
        funded += len(theirs.funded)
    return {"n_diffs": len(diffs), "diffs": diffs[:5], "cross_diffs": cross, "passes": passes, "funded": funded}


def as_walked(blocks, args, facts) -> dict:
    """The reflected path, every row against this file's own booking: -e + side x the historical gross x d - x_s, the
    side +1 where the unit's side uniform (the scalar key path) lies below one half."""
    start, lanes = 3, 6
    rec = run(blocks, args, facts, start, lanes, 63, outcome="as_walked", log=True)
    rows = bad = longs = 0
    by_trade: dict = {}
    for lane, lg in enumerate(rec.logs):
        for r in lg:
            if r["law"] != "as_walked":
                continue
            f = facts[(r["i"], r["j"])]
            u = float(K.uniforms(K.Unit(SEED, PART, 0, lane, start).coin_key(K.moment(r["i"], f.decision, 0), K.SIDE),
                                 1)[0])
            side = 1.0 if u < 0.5 else -1.0
            e = E_T * r["d"] + r["fee"]
            want = -e + side * f.walked[r["R"]] * r["d"] - XS_T * r["d"]
            rows += 1
            longs += int(side > 0)
            bad += int(abs(r["out"] - want) > 1e-9)
            by_trade.setdefault((r["i"], r["j"]), set()).add(side)
    return {"rows": rows, "bad": bad, "long_share": longs / max(rows, 1),
            "lanes_differ": sum(1 for v in by_trade.values() if len(v) > 1)}


def rebooked(blocks, args, facts) -> dict:
    rec = run(blocks, args, facts, 3, 1, 63, outcome="rebooked", log=True)
    compared = bad = 0
    for r in rec.logs[0]:
        if r["law"] != "rebooked" or r.get("need") is not None:
            continue
        cost = 2 * (facts[(r["i"], r["j"])].stop_ticks * r["d"] + r["fee"] + 10 * r["d"])
        if r["room"] < cost:
            continue                                         # the room binds: the vendored settlement, not the walk
        compared += 1
        bad += int(abs(r["out"] - r["vendored"]) > 1e-9)
    return {"compared": compared, "bad": bad}


def _fee(contracts: int) -> float:
    minis = contracts // 10
    return minis * FEES[1] + (contracts - 10 * minis) * FEES[0]


def _step(sigma: float, T: float) -> int:
    return max(1, int(math.ceil(sigma * math.sqrt(T) / math.sqrt(WALK_MAX) - 1e-12)))


def _steps(sigma: float, T: float, s: int) -> int:
    return max(1, int(math.floor(sigma * sigma * T / (s * s) + 0.5)))


def oracle(r: dict, f: TB.TradeFacts, R: float, risk: float, contracts: int, lane: int, start: int
           ) -> tuple[float, int]:
    """This file's own re-booking of one logged trade (independent of `three_way_baseline`): (the booking, the move's
    logged inputs that differ from this file's -- the steps, x at the move bar, the barriers G' and the floor side's)."""
    d = risk / f.stop_ticks
    fee = _fee(contracts)
    e, xt, xs, xf = E_T * d + fee, XT_T * d, XS_T * d, XF_T * d
    G = Fraction(TB.target_ticks(R, f.stop_ticks))
    need = r.get("need")
    if need is not None and (need + e + xt) / d < float(G):
        G = Fraction((need + e + xt) / d)
    room = r["room"]
    if not min(f.stop_ticks * d, room - e - max(xs, xf)) > 1e-6:
        return (-room if r["law"] == "fill_fail" else float("nan")), 0
    L = min(f.stop_ticks * d, room - e - xs)
    unit = K.Unit(SEED, PART, 0, lane, start)
    moment = K.moment(r["i"], f.decision, f.sub)
    if f.has_move:
        d1, d2 = f.be_open - f.entry, f.limit - f.be_open
        s1, s2 = _step(f.sigma, d1), _step(f.sigma, d2)
        n1, n2 = _steps(f.sigma, d1, s1), _steps(f.sigma, d2, s2)
        us = K.uniforms(unit.coin_key(moment, K.WALK), n1 + n2)
        Lt = Fraction(L / d)
        v, k = FC.walk_scalar(us[:n1], G, Lt, s1)
        mism = int((r.get("s1"), r.get("n1"), r.get("s2"), r.get("n2")) != (s1, n1, s2, n2))
        if k == 0:
            moved = v >= 1
            down = v if moved else v + Lt
            mism += int(not (abs(r.get("move_x", math.nan) - float(v)) < 1e-9
                             and abs(r.get("move_G2", math.nan) - float(G - v)) < 1e-9
                             and abs(r.get("move_down2", math.nan) - float(down)) < 1e-9
                             and bool(r.get("move_moved")) == bool(moved)))
            v2, k2 = FC.walk_scalar(us[n1:n1 + n2], G - v, down, s2)
            v, k = (G, 1) if k2 == 1 else ((0, 3) if moved else (-Lt, -1)) if k2 == -1 else (v + v2, 0)
        else:
            mism += int(not math.isnan(r.get("move_x", 0.0)))   # phase 1 ended it: no x logged
        cost = xt if k == 1 else xs if k in (-1, 3) else xf
        return -e + float(v) * d - cost, mism
    kind = f.kinds[R]
    if kind in ("t", "s"):
        u = float(K.uniforms(unit.coin_key(moment, K.RACE), 1)[0])
        p = L / (L + float(G) * d)
        return ((-e + float(G) * d - xt) if u < p else (-e - L - xs)), 0
    T = max(1, f.limit - f.entry)
    s = _step(f.sigma, T)
    n = _steps(f.sigma, T, s)
    v, k = FC.walk_scalar(K.uniforms(unit.coin_key(moment, K.WALK), n), G, Fraction(L / d), s)
    return -e + float(v) * d - (xt if k == 1 else xs if k == -1 else xf), 0


def race(blocks, args, facts) -> dict:
    h, lanes, start = 63, 12, 3
    rec = run(blocks, args, facts, start, lanes, h, outcome="race", keep_paths=True, log=True)
    laws, rows, bad, needs, hist_fields, count_bad, overlap, move_inputs_bad = {}, 0, 0, 0, 0, 0, 0, 0
    for lane, (lg, path) in enumerate(zip(rec.logs, rec.paths)):
        ledger = {(int(t["day"]), int(t["trade_index"]), t["kind"], int(t["index"])): t for t in path.trades}
        for t in path.trades:                               # C2-7: no historical outcome on a race-arm row
            hist_fields += int(t.get("race_law") is not None and (t.get("u") is not None or t.get("mae") is not None))
        by_acct: dict = {}
        for t in path.trades:
            by_acct[(t["kind"], int(t["index"]))] = by_acct.get((t["kind"], int(t["index"])), 0) + 1
        for kind, recs in (("combine", path.combines), ("funded", path.funded)):   # the draw's trades: the race's own
            for c in recs:
                if c.sizing is not None:
                    count_bad += int(int(c.sizing["trades"]) != by_acct.get((kind, int(c.index)), 0))
        for r in lg:
            laws[r["law"]] = laws.get(r["law"], 0) + 1
            if r["law"] in ("day_end", "missed"):
                continue
            rows += 1
            day = r["i"] - start + 1
            t = next((v for (dd, jj, _, _), v in ledger.items() if dd == day and jj == r["j"]), None)
            if t is None:
                bad += 1
                continue
            R = float(t["rr"])                              # the R the engine read it at (C2-1): never rr_used
            needs += int(r.get("need") is not None)
            want, mism = oracle(r, facts[(r["i"], r["j"])], R, float(t["realised_risk"]), int(t["contracts"]), lane,
                                start)
            move_inputs_bad += mism
            bad += int(not (abs(r["out"] - want) <= 1e-9 or (math.isnan(want) and math.isnan(r["out"]))))
            if r["law"] == "fill_fail":
                bad += int(abs(float(t["pnl"]) + r["room"]) > 1e-9)      # the engine booked the whole room
        spans = sorted((int(t["day"]) * 1440 + float(blocks[start + int(t["day"]) - 1].entry_t[int(t["trade_index"])]),
                        int(t["day"]) * 1440 + float(blocks[start + int(t["day"]) - 1].exit_by_rr[float(t["rr"])][
                            int(t["trade_index"])])) for t in path.trades)
        overlap += sum(1 for a, b in zip(spans, spans[1:]) if b[0] < a[1] + 5.0)
    return {"rows": rows, "bad": bad, "laws": laws, "needs": needs, "hist_fields": hist_fields, "count_bad": count_bad,
            "move_inputs_bad": move_inputs_bad,
            "overlap": overlap, "move_trades": int(rec.move_trades.sum()), "b_redrawn": int(rec.b_redrawn.sum()),
            "b_historical": int(rec.b_historical.sum()), "be_differs": int(rec.be_differs.sum()), "lanes": lanes}


def dll(blocks, args, facts) -> dict:
    h, start = 42, 0
    rec = run(blocks, args, facts, start, 6, h, outcome="race", keep_paths=True, log=True)
    ends = later = count_bad = 0
    for lg, path in zip(rec.logs, rec.paths):
        by_acct: dict = {}
        for t in path.trades:
            by_acct[(t["kind"], int(t["index"]))] = by_acct.get((t["kind"], int(t["index"])), 0) + 1
        for kind, recs in (("combine", path.combines), ("funded", path.funded)):
            for c in recs:
                if c.sizing is not None:
                    count_bad += int(int(c.sizing["trades"]) != by_acct.get((kind, int(c.index)), 0))
        for r in lg:
            if r["law"] != "day_end":
                continue
            ends += 1
            day = r["i"] - start + 1
            ent = facts[(r["i"], r["j"])].entry
            # no trade of that account later that session: the day ended at the take
            later += sum(1 for t in path.trades if int(t["day"]) == day and t["kind"] == r["acct"][0]
                         and int(t["index"]) == r["acct"][1]
                         and float(blocks[r["i"]].entry_t[int(t["trade_index"])]) > ent)
    return {"day_ends": ends, "later": later, "count_bad": count_bad}


def reading(blocks, args, facts) -> dict:
    """C2-7: `extended.firm_reading.trade_problems` on a race-arm ledger: its rows pass with the historical fields
    marked not applicable, and a row carrying a historical outcome is refused."""
    from extended import firm_reading as FR

    rec = run(blocks, args, facts, 3, 1, 42, outcome="race", keep_paths=True)
    ledger = [dict(t) for t in rec.paths[0].trades]
    clean = FR.trade_problems(ledger, blocks[3:45])
    planted = [dict(ledger[0], u=0.5)] + ledger[1:]
    return {"rows": len(ledger), "clean": len(clean), "planted": len(FR.trade_problems(planted, blocks[3:45]))}


def p16(starts=(0, 100, 250), h: int = 126) -> dict:
    """Heavy (the lead's): the vendored identity on P-16's own job (reads its walk table)."""
    import user_journey as UJ

    from propedge import RESULTS_DIR

    jobs, _ = UJ.BUILDERS["p16"](RESULTS_DIR, ["p16"])
    out = {}
    for arm, job in jobs["p16"].items():
        diffs, funded, pays = [], 0, 0
        for s in starts:
            theirs = CS.replay(job["blocks"][s:s + h], job["args"], h)
            mine = TB.replay(job["blocks"][s:s + h], job["args"], h, outcome="vendored")
            diffs += FC.same(mine, theirs, f"{arm} start{s}")
            funded += len(theirs.funded)
            pays += sum(len(f.payout_days) for f in theirs.funded)
        out[arm] = {"n_diffs": len(diffs), "diffs": diffs[:5], "funded": funded, "payouts": pays}
    return out


def main() -> None:
    if sys.argv[1:] == ["p16"]:
        print(json.dumps({"p16": p16()}, default=str))
        return
    blocks, args, facts = job()
    out = {"identity": identity(blocks, args, facts), "rebooked": rebooked(blocks, args, facts),
           "as_walked": as_walked(blocks, args, facts),
           "race": race(blocks, args, facts), "reading": reading(blocks, args, facts)}
    db, da, df = job(dll=True)
    out["dll"] = dll(db, da, df)
    print(json.dumps(out, default=str))


if __name__ == "__main__":
    main()
