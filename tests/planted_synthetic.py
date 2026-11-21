"""Q-196's synthetic check of the planted-difference check (`extended/planted_diffs.py`; `tests/test_planted_diffs.py`
runs it in a process of its own: the vendored tree goes on its `sys.path`) -- Q-17's adapter and the vendored engine
on a deterministic synthetic campaign of the search years only (2022-09-01 to 2023-12-29): no bar, no atlas, no
generator (every value a function of the day's and the trade's index, as `tests/w31_synthetic.py`'s; the shared-day
seed `user_beside.SEED_BLOCK[1]`, and a replay draws nothing with it).

    python tests/planted_synthetic.py <repository root>             # prints one JSON line last

What it reports (the test asserts each):

* **main** -- the check on the campaign under both responses: its verdict, failures, `cannot`, and per response and
  kind the plants made, the starts they stand on and the differing horizons expected;
* **mutants** -- the check under `off` with one thing broken, each of which must not pass: the comparator blind
  (`_one_start` reports nothing), at the wrong horizon (each reported horizon moved to the next checked one), firing
  unplanted (the least checked horizon added on every start), the planter inert (every perturbation returns the
  blocks given), the count's groups swapped (`exact_run_diffs.count_rows` told the other group); its verdict and its
  failures' count;
* **no_events** -- a campaign whose every trade loses (no pass, so no event): the control holds, and the check must say
  it cannot show power (verdict 6), never that it held;
* **refusals** -- a job holding 2024-01-02, or 2026-07-17 (the confirmation window, named as such), or workers 2:
  refused before any run.
"""
from __future__ import annotations

import copy
import json
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(sys.argv[1])
for _p in (str(REPO), str(REPO / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import user_journey as UJ  # noqa: E402

from extended import exact_run_diffs as X  # noqa: E402
from extended import planted_diffs as PD  # noqa: E402
from extended import user_beside as B  # noqa: E402
from propedge.campaign.lockstep import ConductModel  # noqa: E402
from propedge.campaign.payout_method import payout_method_terms  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.contract.adapter import rules_from_ledger  # noqa: E402
from propedge.contract.rules import load_rules  # noqa: E402
from propedge.outcomes.distribution import DayBlock  # noqa: E402

days = [d.date().isoformat() for d in pd.bdate_range("2022-09-01", "2023-12-29")]
#: sessions where every trade loses: the declared control start 42 begins inside it, so its first event falls after
#: session 21 and its forced plants stand at a later horizon (63), `blank_long` expected at 63, 90 and 126 only
LOSING_SPELL = (40, 75)


def campaign(losing: bool = False) -> list:
    blocks = []
    for i in range(len(days)):
        k = 1 + (i % 4)
        et = np.array([500.0 + 60.0 * j for j in range(k)])
        bad = losing or (i % 13) in (11, 12) or LOSING_SPELL[0] <= i <= LOSING_SPELL[1]
        win = np.array([(not bad) and ((i * 7 + j) % 5) < 3 for j in range(k)])
        pnl = np.where(win, 1000.0, -500.0)
        blocks.append(DayBlock(pnl=pnl, risked=np.full(k, 500.0),
                               exit_reasons=tuple("target" if w else "stop" for w in win), entry_t=et, exit_t=et + 30.0))
    return blocks


rules = rules_from_ledger()
proto = Protocol(name="planted_synthetic", combine_rr=2.0, combine_risk=500.0, funded_rr=2.0, funded_risk=500.0,
                 trades_per_day=4, max_concurrent_accounts=5)
lag = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
args = {"draws": {"protocol": proto, "mode": "rotation", "flip": None},
        "path": dict(edge=0.0, rules=rules, initial_bankroll=1e9, max_concurrent_accounts=5,
                     subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                     activation=float(rules.activation), payout_lag_days=lag, max_concurrent_combines=5,
                     max_total_accounts=5, conduct=ConductModel(rtp=False, enforcement_p=0.0), combine_max_days=2000,
                     funded_horizon_days=100_000, purchase_budget=(20, 21)),
        "seed": B.SEED_BLOCK[1]}
job = {"engine": "single", "blocks": campaign(), "dates": days, "args": args}
out: dict[str, Any] = {"n_days": len(days)}
t0 = time.time()


def brief(rep: dict) -> dict:
    kinds = {}
    for r in rep["control"]:
        for k in PD.KINDS:
            ps = [p for p in rep["plants"] if p["response"] == r and p["kind"] == k]
            kinds[f"{r}|{k}"] = {"plants": len(ps), "starts": len({p["start"] for p in ps}),
                                 "expected": sum(p["expected"] for p in ps), "held": all(p["held"] for p in ps)}
    return {"verdict": PD.verdict(rep), "failures": rep["failures"], "cannot": rep["cannot"],
            "control": rep["control"], "kinds": kinds, "starts": {str(k): v for k, v in rep["starts"].items()},
            "groups_forced": {r: {g: len(v) for g, v in PD.forced_starts(
                [PD.Plan(p["kind"], p["start"], p["group"], "", 0, (0, 0), ()) for p in rep["plants"]
                 if p["response"] == r]).items()} for r in rep["control"]}}


rep = PD.run_check(job, "syn", "point")
out["main"] = brief(rep)
out["main_lines"] = PD.summary_lines(rep)
out["main_s"] = round(time.time() - t0, 1)
# the plans of the start that begins inside the losing spell (a synthetic campaign: its horizons may be shown)
c42 = B.run_starts("syn", "point", B.BY_NAME["off"], job, [42], 1, journey=True, journey_block="search")[0]
out["plans_42"] = [[p.kind, p.target, p.length, list(p.span), None if p.expected is None else list(p.expected)]
                   for p in PD.plans_for(42, "control", len(days), c42["checked"], PD.first_event(c42["rec"]))]
out["first_event_42"] = PD.first_event(c42["rec"])

# ------------------------------------------------------------------------------------------------ the mutants

REAL_ONE = UJ._one_start
REAL_COUNT = X.count_rows


def one_start_with(edit):
    def f(*a, **k):
        o = REAL_ONE(*a, **k)
        return edit(o)
    return f


def blind(o):
    rec = {k: v for k, v in o["rec"].items() if k != "alt"}
    return {**o, "rec": rec, "differs": []}


def wrong_horizon(o):
    ch = sorted(o["checked"])
    alt = dict(o["rec"].get("alt") or {})
    new, new_alt = [], {}
    for h in o["differs"]:
        later = [x for x in ch if x > h]
        if later:
            new.append(later[0])
            new_alt[str(later[0])] = alt[str(h)]
    rec = {**{k: v for k, v in o["rec"].items() if k != "alt"}, **({"alt": new_alt} if new_alt else {})}
    return {**o, "rec": rec, "differs": sorted(set(new))}


def spurious(o):
    if not o["checked"]:
        return o
    h = min(o["checked"])
    if h in o["differs"]:
        return o
    alt = copy.deepcopy(dict(o["rec"].get("alt") or {}))
    fake = {k: v for k, v in o["rec"].items() if k != "alt"}
    alt[str(h)] = {**fake, "pass_days": sorted([*fake["pass_days"], 0])}
    return {**o, "rec": {**o["rec"], "alt": alt}, "differs": sorted([*o["differs"], h])}


def swapped_count(outs, *, groups=None, **k):
    other = {"cut": "control", "control": "cut"}
    return REAL_COUNT(outs, groups={s: other[g] for s, g in dict(groups).items()}, **k)


def inert(plan, job_blocks, given):
    return list(given)


mutants: dict[str, dict] = {}
for name in ("blind", "wrong_horizon", "spurious", "inert", "swapped_count"):
    t1 = time.time()
    try:
        if name in ("blind", "wrong_horizon", "spurious"):
            UJ._one_start = one_start_with(globals()[name])
        if name == "swapped_count":
            X.count_rows = swapped_count
        r = PD.run_check(job, "syn", "point", responses=("off",), perturb=inert if name == "inert" else None)
        mutants[name] = {"verdict": PD.verdict(r), "failures": len(r["failures"]),
                         "first": r["failures"][:2], "s": round(time.time() - t1, 1)}
    except Exception as exc:                                      # a mutant refused by the check: it did not pass
        mutants[name] = {"verdict": "raised", "error": f"{type(exc).__name__}: {exc}"[:300],
                         "s": round(time.time() - t1, 1)}
    finally:
        UJ._one_start = REAL_ONE
        X.count_rows = REAL_COUNT
out["mutants"] = mutants

# ------------------------------------------------------------------------------------------------ no events, refusals

r = PD.run_check({**job, "blocks": campaign(losing=True)}, "syn", "point", responses=("off",))
out["no_events"] = {"verdict": PD.verdict(r), "failures": r["failures"], "cannot": r["cannot"],
                    "control": r["control"]}


def refused(j: dict, **k) -> str | None:
    try:
        PD.run_check(j, "syn", "point", responses=("off",), **k)
    except PD.PlantRefused as exc:
        return str(exc)
    return None


late = {**job, "dates": [*days, "2024-01-02"], "blocks": [*job["blocks"], job["blocks"][-1]]}
conf = {**job, "dates": [*days, "2026-07-17"], "blocks": [*job["blocks"], job["blocks"][-1]]}
out["refusals"] = {"late": refused(late), "confirmation": refused(conf), "workers": refused(job, workers=2)}
out["total_s"] = round(time.time() - t0, 1)
print(json.dumps(out, default=str))
