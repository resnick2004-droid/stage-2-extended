"""How many setups a day the contract needs (D-154): the time a Combine and a funded account take, by size and frequency.

    python scripts/setups_per_day.py

The operator's requirement (2026-09-26): no model that takes one trade a day, because slow setups keep Combines open
into new billing periods and leave accounts idle. The minimum is derived from the contract, not chosen: for each size
stage one uses, the Combine's time to resolve on the engine's own account (`lockstep.CombineAccount`) with stage one's
binary process (`adapter.BinaryDraw`, which keeps the floor barrier race), at 1, 2, 3, 5 and 8 trades a day and edges
0, 0.05 and 0.10 -- and, from D-274, at a trade on a share of days (0.1, 0.2, 0.25, 1/3 and 0.5 a day: on each day a
seeded coin decides whether the day's one slot trades; an idle day still counts as a day), so the minimum is the
contract's and not the table's floor of one a day (D-269 (3)).

* `min_setups_per_day`: the fewest trades a day at which the median Combine resolves inside one billing period
  (`billing_days` on the verified ledger), so the typical Combine never rebills. Under rotation across n live
  accounts each account sees about 1/n of the setups, so a model needs about n times this.
* `best_setups_per_day_for_passes`: the trades a day with the most passes per fee dollar; at large sizes more trades a
  day lowers the pass rate (the Combine's best-day rule), so frequency has a ceiling there as well as a floor.

The funded side (`lockstep.FundedAccount`, both payout paths) is descriptive: the share of accounts that reach a
first payout request before closing and the days it takes, by the same frequencies. Sizes: stage one's Combine and
funded geometries (T5 2a; the state-policy results) and D-150's declared steady profiles. Writes
results/setups_per_day.csv (Combine) and results/setups_per_day_funded.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.campaign.lockstep import CombineAccount, FundedAccount, child_seed  # noqa: E402
from propedge.campaign.payout_method import rules_for_method  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.contract.adapter import BinaryDraw, Policy  # noqa: E402
from propedge.reporting.results import write_result  # noqa: E402

SCRIPT = "scripts/setups_per_day.py"
SEED = 20261113
FREQUENCIES = (0.1, 0.2, 0.25, 1 / 3, 0.5, 1, 2, 3, 5, 8)      # D-274: below one, a trade on that share of days


class SparseDraw:
    """A draw that trades on a seeded share `rate` of days: on the day's first slot a coin decides; on an idle day
    every slot is no trade (NaN), which the account reads as an empty slot and still counts the day (D-274)."""

    def __init__(self, draw, rate: float, seed: int):
        self.draw, self.rate = draw, float(rate)
        self.rng = np.random.default_rng(seed)
        self._day, self._on = None, False

    def __call__(self, n, day, slot, cushion):
        if day != self._day:
            self._day, self._on = day, bool(self.rng.random() < self.rate)
        return self.draw(n, day, slot, cushion) if self._on else np.full(n, np.nan)

    def __getattr__(self, name):
        return getattr(self.draw, name)


def _slots(tpd: float) -> int:
    return max(1, int(round(tpd))) if tpd >= 1 else 1
EDGES = (0.0, 0.05, 0.10)
N_COMBINE, N_FUNDED = 2000, 1000
FUNDED_DAYS = 252

#: (R, dollar risk, source) -- the Combine sizes stage one uses, and D-150's steady profiles
COMBINE_SIZES = (
    (1.0, 1500.0, "propsim D-08: best at zero edge"),
    (0.5, 1000.0, "results_state_policy_combine.csv: close alternative (3 a day there)"),
    (0.825, 2000.0, "results_state_policy_combine.csv: close alternative"),
    (2.0, 750.0, "propsim D-36; T5 2a for e <= 0.05: conduct-constrained"),
    (1.5, 500.0, "T5 2a: at e >= 0.10"),
    (2.0, 250.0, "D-150 steady profile"),
    (1.5, 250.0, "D-150 steady profile"),
    (1.5, 150.0, "D-150 steady profile"),
)
#: the funded sizes stage one uses outside the one-shot day-one all-in
FUNDED_SIZES = (
    (2.0, 750.0, "propsim D-10: static when s < 0.75"),
    (2.0, 1000.0, "results_state_policy_xfa.csv: build"),
    (1.0, 300.0, "results_state_policy_xfa_allin.csv: harvest"),
    (1.0, 150.0, "results_state_policy_xfa_allin.csv: harvest"),
    (1.5, 1000.0, "T5 2a: at e >= 0.10"),
    (1.5, 500.0, "propsim D-45: after the first payout"),
)
#: D-284: Combine sizes a declared model searches beyond stage one's, tabulated after every cell above so their seeds
#: leave the existing rows unchanged
EXTRA_COMBINE_SIZES = (
    (1.5, 1000.0, "D-283: FV2's searched Combine -- JJ Simon's 38/25 evaluations, a $1,500 target (D-267)"),
    (1.5, 2000.0, "D-315: the v4 state table's fresh Combine at its negative-edge cells (D-313's candidate)"),
    (0.75, 2000.0, "D-317: the v5 state table's fresh Combine at its cells from -0.05 to +0.05 (D-316's candidate)"),
    (1.0, 1600.0, "D-434: T24-GF15's two-shot Combine -- two wins net the $3,000 target after costs (D-425, D-426)"),
)


def combine_cell(rr, risk, tpd, e, rules, cell):
    pol = Policy(rr=rr, risk=risk, trades_per_day=_slots(tpd))
    days, passed, subs = np.zeros(N_COMBINE), np.zeros(N_COMBINE, bool), np.zeros(N_COMBINE)
    for i in range(N_COMBINE):
        draw = BinaryDraw(pol, e, child_seed(SEED, cell, i), rules)
        if tpd < 1:
            draw = SparseDraw(draw, tpd, child_seed(SEED + 1, cell, i))
        acc = CombineAccount(index=i, purchase_day=0, draw=draw, floor_start=-rules.mll)
        d = 0
        while acc.alive and d < 2000:
            acc.trade_day(rules, pol, d, d + 1)
            d += 1
        days[i], passed[i] = acc.days, acc.passed
        subs[i] = 1 + max(acc.days - 1, 0) // rules.billing_days
    return {"p_pass": float(passed.mean()), "median_days_to_resolve": float(np.median(days)),
            "mean_days_to_resolve": float(days.mean()),
            "share_resolved_in_one_billing_period": float((days <= rules.billing_days).mean()),
            "mean_subscriptions": float(subs.mean()),
            "passes_per_100_usd_fees": float(100 * passed.sum() / (subs.sum() * rules.subscription))}


def funded_cell(rr, risk, tpd, e, path, rules, cell):
    proto = Protocol("setups_per_day", combine_rr=1.0, combine_risk=1500.0, funded_rr=rr, funded_risk=risk,
                     trades_per_day=_slots(tpd), payout_path=path, family="setups_per_day")
    pol = proto.funded_policy()
    cap = rules.std_cap if path == "standard" else rules.cons_cap
    first = np.full(N_FUNDED, np.nan)
    for i in range(N_FUNDED):
        draw = BinaryDraw(pol, e, child_seed(SEED, cell, i), rules)
        if tpd < 1:
            draw = SparseDraw(draw, tpd, child_seed(SEED + 1, cell, i))
        acc = FundedAccount(index=i, activation_day=0, draw=draw, horizon_days=FUNDED_DAYS,
                            floor_start=rules.xfa_mll_start)
        for d in range(FUNDED_DAYS):
            if not acc.alive:
                break
            if acc.trade_day(rules, pol, cap, d, d + 1) is not None:
                first[i] = d + 1
                break
    got = first[~np.isnan(first)]
    return {"share_reaching_first_payout": float(len(got) / N_FUNDED),
            "median_days_to_first_payout": float(np.median(got)) if len(got) else float("nan")}


def main() -> int:
    rules = rules_for_method("aeropay")
    rows, cell = [], 0
    for rr, risk, source in COMBINE_SIZES:
        for e in EDGES:
            for tpd in FREQUENCIES:
                cell += 1
                rows.append({"rr": rr, "risk": risk, "edge": e, "setups_per_day": tpd, "source": source,
                             **combine_cell(rr, risk, tpd, e, rules, cell)})
            print(f"Combine {rr:g}:1 ${risk:,.0f} e={e:+.2f} done", flush=True)
    comb_rows = rows
    rows = []
    for rr, risk, source in FUNDED_SIZES:
        for path in ("standard", "consistency"):
            for e in EDGES:
                for tpd in FREQUENCIES:
                    cell += 1
                    rows.append({"rr": rr, "risk": risk, "payout_path": path, "edge": e, "setups_per_day": tpd,
                                 "source": source, **funded_cell(rr, risk, tpd, e, path, rules, cell)})
            print(f"funded {rr:g}:1 ${risk:,.0f} {path} done", flush=True)
    fund = pd.DataFrame(rows)
    for rr, risk, source in EXTRA_COMBINE_SIZES:                     # after every cell above: their seeds unchanged
        for e in EDGES:
            for tpd in FREQUENCIES:
                cell += 1
                comb_rows.append({"rr": rr, "risk": risk, "edge": e, "setups_per_day": tpd, "source": source,
                                  **combine_cell(rr, risk, tpd, e, rules, cell)})
            print(f"Combine {rr:g}:1 ${risk:,.0f} e={e:+.2f} done", flush=True)
    comb = pd.DataFrame(comb_rows)
    derived = []
    for (rr, risk, e), g in comb.groupby(["rr", "risk", "edge"], sort=False):
        ok = g[g["median_days_to_resolve"] <= rules.billing_days]
        derived.append({"rr": rr, "risk": risk, "edge": e,
                        "min_setups_per_day": float(ok["setups_per_day"].min()) if len(ok) else np.nan,
                        "best_setups_per_day_for_passes": float(g.loc[g["passes_per_100_usd_fees"].idxmax(),
                                                                      "setups_per_day"])})
    comb = comb.merge(pd.DataFrame(derived), on=["rr", "risk", "edge"])
    common = dict(script=SCRIPT, seed=SEED, exploratory=False,
                  notes={"decision": "D-154, D-274", "process": "stage one's binary process through the engine's accounts; "
                         "a contract calculation, not a strategy"})
    write_result(comb, "setups_per_day", parameters={"frequencies": list(FREQUENCIES), "edges": list(EDGES),
                 "combines_per_cell": N_COMBINE, "billing_days": rules.billing_days,
                 "min_rule": "fewest setups a day with the median Combine resolved inside one billing period"},
                 description="Combine time to resolve, subscriptions and passes per fee dollar by size, setups per "
                             "day and edge; the contract's minimum setups per day.", **common)
    write_result(fund, "setups_per_day_funded", parameters={"frequencies": list(FREQUENCIES), "edges": list(EDGES),
                 "accounts_per_cell": N_FUNDED, "horizon_days": FUNDED_DAYS},
                 description="Funded accounts: share reaching a first payout request and the days it takes, by size, "
                             "payout path, setups per day and edge.", **common)
    pd.set_option("display.width", 220)
    print(comb.drop_duplicates(["rr", "risk", "edge"])[["rr", "risk", "edge", "min_setups_per_day",
                                                        "best_setups_per_day_for_passes"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
