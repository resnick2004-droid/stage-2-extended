"""HYPOTHETICAL campaign test of cross-account hedging (D-153; declared in NEXT_STEPS 5j before it ran).

    python scripts/hypo_hedge_campaign.py            # the engine-reproduction check, then the three structures

NOT A CANDIDATE. Cross-account hedging is prohibited (10296582) and stays tier 1 under D-145; this asks only what the
contract's structure would do if the rule did not exist, at the operator's request.

A hedge cannot change any account's average (results/hypo_hedge_pairs.csv), so the one place it could add money is the
joint path under reinvestment: a steadier flow of Combine passes with a limited bankroll and the funded cap. Three
structures, on the days as they happened from each start day:

* `pair`      -- two Combines always on opposite sides; a finished one is replaced at once on the side opposite
                 the survivor;
* `unrelated` -- two Combines, each on a side chosen by a seeded coin at purchase;
* `single`    -- one Combine at a time, on a coin side.

The funded account keeps its Combine's side. Entries, geometry and rules as the structure study
(`scripts/hypo_hedge_pairs.py`): 08:35 CT at the 0.4 D stop, the Combine at 1:1 $1,500, the funded account at static
2:1 $750, the verified rules, the Aeropay lag, the funded cap from the ledger, the hold queue; no payout denial and no
conduct model.

The campaign clock is `propedge.campaign.lockstep.simulate_lockstep_path`'s order of events, written out here because
the engine buys a replacement without knowing the survivor's side, and a pair cannot be held without that. Before any
structure runs, the clock must reproduce the engine exactly on fixed-side accounts, one and two Combines at a time
(`_check_against_engine`); it raises otherwise. Writes results/hypo_hedge_campaign.csv.
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
import yaml  # noqa: E402

import hypo_hedge_pairs as hp  # noqa: E402
from propedge.backtest.harness import VariantCounter  # noqa: E402
from propedge.campaign.lockstep import CombineAccount, FundedAccount, simulate_lockstep_path  # noqa: E402
from propedge.campaign.payout_method import payout_method_terms, rules_for_method  # noqa: E402
from propedge.campaign.reinvest import TRADING_DAYS_PER_YEAR  # noqa: E402
from propedge.contract.rules import load_rules  # noqa: E402
from propedge.execution.fills import FillModel  # noqa: E402
from propedge.reporting.results import write_result  # noqa: E402

SCRIPT = "scripts/hypo_hedge_campaign.py"
SEED = 20261112
HORIZON = 504
STRIDE = 5
BANKROLLS = (1_000.0, 5_000.0)
STRUCTURES = ("pair", "unrelated", "single")
CHECK_STARTS = (0, 400, 800, 1200, 1600, 2000)


def _opposite(running, rng):
    """A pair: the side opposite the survivor; long when both are bought together (the second is then short)."""
    return -running[0][0] if running else 1


def _coin(running, rng):
    return 1 if rng.random() < 0.5 else -1


def _long(running, rng):
    return 1


#: structure -> (Combines at a time, the side rule for the next purchase)
LAYOUT = {"pair": (2, _opposite), "unrelated": (2, _coin), "single": (1, _coin)}


def campaign(s, start, slots, side_rule, bankroll, rules, terms, max_funded, rng):
    """One campaign from `start` over HORIZON sessions; the lockstep engine's order of events, day by day."""
    cpol, fpol = hp.PROTOCOL.combine_policy(), hp.PROTOCOL.funded_policy()
    cap = rules.std_cap if fpol.payout_path == "standard" else rules.cons_cap
    sub, act, billing, lag = rules.subscription, rules.activation, rules.billing_days, terms.lag_days
    cash = float(bankroll)
    running, funded, queue, pending = [], [], [], []
    fees = payouts = 0.0
    attempts = n_funded = 0
    first_payout = None
    ruined = False
    for day in range(HORIZON):
        # 1. subscriptions due
        keep = []
        for side, c in running:
            due = 1 + max(0, (day - c.purchase_day - 1) // billing)
            alive = True
            while c.subs_paid < due:
                if cash < sub:
                    alive = False
                    break
                cash -= sub
                fees += sub
                c.subs_paid += 1
            if alive:
                keep.append((side, c))
            else:
                c.abandoned = True
                c.resolved_on = day
        running = keep
        # 2. every live account trades today's session
        for side, c in running:
            if day >= c.start_day and c.alive:
                c.trade_day(rules, cpol, day - c.start_day, day)
        for side, a in funded:
            if day >= a.start_day and a.alive and a.ended_on is None:
                net = a.trade_day(rules, fpol, cap, day - a.start_day, day)
                if net is not None:
                    pending.append((day + lag, net))
        # 3. payouts arriving today
        still = []
        for arrival, amount in pending:
            if arrival <= day:
                cash += amount
                payouts += amount
                first_payout = day if first_payout is None else first_payout
            else:
                still.append((arrival, amount))
        pending = still
        # 4. Combines that resolved today: a pass joins the hold queue
        keep = []
        for side, c in running:
            if c.resolved_on is None:
                keep.append((side, c))
            elif c.passed:
                queue.append((side, c))
        running = keep
        # 5. funded slots free the day after the last trading day; the queue activates, paying then
        funded = [(sd, a) for sd, a in funded if not (a.ended_on is not None and a.ended_on < day)]
        while queue and len(funded) < max_funded:
            if cash < act:
                break
            cash -= act
            fees += act
            side, _ = queue.pop(0)
            funded.append((side, FundedAccount(index=n_funded, activation_day=day,
                                               draw=hp._Seq(s[(side, "f")], start + day + 1,
                                                            hp.PROTOCOL.funded_risk),
                                               horizon_days=HORIZON, floor_start=rules.xfa_mll_start)))
            n_funded += 1
        # 6. new Combines, none while a pass waits in the queue
        while not queue and len(running) < slots and cash >= sub:
            side = side_rule(running, rng)
            cash -= sub
            fees += sub
            running.append((side, CombineAccount(index=attempts, purchase_day=day,
                                                 draw=hp._Seq(s[(side, "c")], start + day + 1,
                                                              hp.PROTOCOL.combine_risk),
                                                 floor_start=-rules.mll)))
            attempts += 1
        # 7. ruin: nothing live, and the campaign cannot take its next step
        if not ruined and not running and not funded:
            ruined = cash < act if queue else cash < sub
    years = HORIZON / TRADING_DAYS_PER_YEAR
    growth = float(np.log(cash / bankroll) / years) if cash > 0 else float("-inf")
    return {"final_cash": cash, "log_growth": growth, "ruined": ruined, "fees": fees, "payouts": payouts,
            "combines": attempts, "funded": n_funded, "first_payout_day": first_payout}


def _check_against_engine(s, rules, terms, max_funded):
    """The clock must reproduce `simulate_lockstep_path` on fixed-side (long) accounts, field for field."""
    for slots in (1, 2):
        for start in CHECK_STARTS:
            for bankroll in BANKROLLS:
                mine = campaign(s, start, slots, _long, bankroll, rules, terms, max_funded, None)
                eng = simulate_lockstep_path(
                    hp.PROTOCOL, edge=0.0, seed=0, rules=rules, initial_bankroll=bankroll, horizon_days=HORIZON,
                    max_concurrent_accounts=max_funded, subscription=rules.subscription,
                    billing_days=rules.billing_days, activation=rules.activation, payout_lag_days=terms.lag_days,
                    max_concurrent_combines=slots, funded_horizon_days=HORIZON,
                    combine_draw_factory=lambda k, d: hp._Seq(s[(1, "c")], start + d + 1, hp.PROTOCOL.combine_risk),
                    funded_draw_factory=lambda j, d: hp._Seq(s[(1, "f")], start + d + 1, hp.PROTOCOL.funded_risk)).path
                want = {"final_cash": eng.final_cash, "ruined": eng.ruined, "fees": eng.total_fees,
                        "payouts": eng.total_payouts, "combines": eng.attempts_started, "funded": eng.accounts_funded,
                        "first_payout_day": eng.days_to_first_payout}
                got = {k: mine[k] for k in want}
                if any((abs(got[k] - want[k]) > 1e-6) if isinstance(want[k], float) else got[k] != want[k]
                       for k in want):
                    raise AssertionError(f"clock differs from the engine (slots {slots}, start {start}, "
                                         f"${bankroll:,.0f}): {got} vs {want}")
    return len(CHECK_STARTS) * 2 * len(BANKROLLS)


def main() -> int:
    cfg = yaml.safe_load((ROOT / "config" / "bracket_map.yaml").read_text(encoding="utf-8"))
    rules = rules_for_method("aeropay")
    terms = payout_method_terms("aeropay")
    max_funded = int(load_rules().value("max_active_funded_accounts"))
    fm = FillModel.load("assumed")
    rows = []
    for m_i, (market, runs) in enumerate(cfg["runs"].items()):
        ent, fills = hp._entries(cfg, fm, market, runs)
        s, days = hp._sequences(ent, fills, np.random.default_rng(0))     # the coin-flip keys are not used here
        checked = _check_against_engine(s, rules, terms, max_funded)
        print(f"[{market}] clock reproduces the engine on {checked} fixed-side campaigns", flush=True)
        starts = range(0, len(days) - HORIZON + 1, STRIDE)
        for bankroll in BANKROLLS:
            per = {}
            for structure in STRUCTURES:
                slots, side_rule = LAYOUT[structure]
                per[structure] = pd.DataFrame([
                    campaign(s, st, slots, side_rule, bankroll, rules, terms, max_funded,
                             np.random.default_rng([SEED, m_i, int(bankroll), STRUCTURES.index(structure), st]))
                    for st in starts])
            for structure, g in per.items():
                fp = g["first_payout_day"].dropna()
                rows.append({"market": market, "bankroll": bankroll, "structure": structure, "campaigns": len(g),
                             "median_log_growth": float(np.median(g["log_growth"])),
                             "share_reaching_zero_cash": float((~np.isfinite(g["log_growth"])).mean()),
                             "ruin_probability": float(g["ruined"].mean()),
                             "median_final_cash": float(g["final_cash"].median()),
                             "p10_final_cash": float(g["final_cash"].quantile(0.10)),
                             "share_ending_below_bankroll": float((g["final_cash"] < bankroll).mean()),
                             "mean_fees": float(g["fees"].mean()), "mean_payouts": float(g["payouts"].mean()),
                             "mean_combines_bought": float(g["combines"].mean()),
                             "mean_accounts_funded": float(g["funded"].mean()),
                             "share_with_a_payout": float(g["first_payout_day"].notna().mean()),
                             "median_days_to_first_payout": float(fp.median()) if len(fp) else float("nan"),
                             "share_starts_pair_beats_unrelated": (
                                 float((per["pair"]["log_growth"] > per["unrelated"]["log_growth"]).mean())
                                 if structure == "pair" else float("nan"))})
            print(f"[{market}] ${bankroll:,.0f}: {len(starts)} start days", flush=True)
    out = pd.DataFrame(rows)
    verdict = all(
        out[(out.market == m) & (out.bankroll == b) & (out.structure == "pair")]["median_log_growth"].iloc[0]
        > out[(out.market == m) & (out.bankroll == b) & (out.structure == "unrelated")]["median_log_growth"].iloc[0]
        for m in out.market.unique() for b in BANKROLLS)
    out["declared_criterion_met"] = verdict
    VariantCounter().record(prereg_id="D-153:hypothetical_hedge_campaign",
                            params={"structures": list(STRUCTURES), "bankrolls": list(BANKROLLS), "horizon": HORIZON,
                                    "stride": STRIDE}, seed=SEED, exploratory=True, label=hp.LABEL)
    write_result(out, "hypo_hedge_campaign" + hp.SUFFIX, script=SCRIPT, seed=SEED, exploratory=True,
                 parameters={"design": "NEXT_STEPS 5j (declared before the run)", "structures": list(STRUCTURES),
                             "combine": "1:1 at $1,500 (propsim D-08)", "funded": "static 2:1 at $750 (propsim D-10)",
                             "entry": "08:35 CT, 0.4 D stop", "bankrolls": list(BANKROLLS), "horizon_sessions": HORIZON,
                             "start_stride": STRIDE, "payout_lag_days": terms.lag_days, "max_funded": max_funded,
                             "denial_p": 0.0, "conduct_model": "none: the pattern is tier 1",
                             "settlement": hp.SETTLEMENT,
                             "criterion": "pair median log growth above unrelated on both markets at both bankrolls"},
                 notes={"decision": "D-153", "status": hp.LABEL,
                        "engine_check": "the clock reproduced simulate_lockstep_path on fixed-side accounts first"},
                 description="HYPOTHETICAL: campaigns under reinvestment with Combines held in opposite-side pairs, "
                             "on unrelated coin sides, or one at a time, on the days as they happened.")
    pd.set_option("display.width", 250)
    print(hp.LABEL)
    print(out.drop(columns=["declared_criterion_met"]).round(3).to_string(index=False))
    print("declared criterion met (the pair grows faster than unrelated accounts everywhere):", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
