"""Wave 3.1's synthetic check of the journey's window and readings (`tests/test_journey_readings.py` runs it in a
process of its own: the vendored tree goes on its `sys.path`) -- Q-17's adapter (`extended/user_beside.py`) with its
`journey` keyword and the readings (`extended/user_readings.py`), on a deterministic synthetic campaign through the
vendored engine: no bar, no atlas, no generator (every value is a function of the day's and the trade's index, as
`tests/q76_synthetic.py`'s; the shared-day seed is `user_beside.SEED_BLOCK[1]`, and a replay draws nothing with it).
The calendar runs from 2022-09-01 across E-208's boundary (2023-12-29 | 2024-01-02) for sixty held-out sessions.

    python tests/w31_synthetic.py <repository root>             # prints one JSON line last

What it reports (the test asserts each):

* **absent = before, bit for bit** -- the adapter at master c35cf40 (`git show c35cf40:extended/user_beside.py`, its
  text pinned by sha256) and now give the same per-start outputs (`user_beside_identity.canonical`) for all 19
  responses, the same tasks to the pool; and the readings at c35cf40 (`user_readings.py` and `user_measures.py` of that
  commit, pinned) give the same rows and per-start table as now with Q-44's blocks named (`Q44_BLOCKS`), and both
  find no problem -- on a campaign holding no net in (0, 1e-6], where m-11 changes nothing (reported);
* **the default is the search years and refuses what is not a journey**: `summary` and every row function at their
  defaults refuse whole-window outputs; the registered blocks refuse journeys;
* **the journey's window**: every start's long run stops at its block's last session (`observed = min(252,
  block_left)`), shorter than the whole-window run exactly where the block ends first; no replayed session lies in
  another block; where the block's end is not reached the outputs are the absent run's bit for bit apart from the one
  added key `journey`, placed before `seed`; the journey's `rel` is the run's cash less the bankroll, its peaks
  `peak_by_month(rel)`, its accounts' arrivals U1's pay days;
* **refusals before any start**: a date in neither block (the holiday 2024-01-01; the confirmation window's
  2026-07-17), dates out of order, a keyword that is not a bool;
* **composition**: with the pass-through funded class too, the outputs are the journey run's apart from the class's
  naming key (still last); the task carries `True` fourteenth;
* **the readings on journeys**: `journey_readings.summary` on both E-208 blocks with two budgets, `consistency_problems` empty; `P_B`
  equal to `journey_measures.p_bankroll` recomputed from each journey's `rel` (a second code path), its sub-reading
  likewise, `P_B` at most its sub-reading and P; (24)'s three states summing to one; the per-start peak columns the
  journeys' own.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
import types
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

import customer_journey as CJ  # noqa: E402
import user_beside_identity as I  # noqa: E402

from extended import gate as XG  # noqa: E402
from extended import journey_measures as J  # noqa: E402
from extended import journey_readings as JR  # noqa: E402
from extended import user_beside as B  # noqa: E402
from extended import user_measures as M  # noqa: E402
from extended import user_readings as UR  # noqa: E402
from propedge.campaign.lockstep import ConductModel  # noqa: E402
from propedge.campaign.payout_method import payout_method_terms  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.contract.adapter import rules_from_ledger  # noqa: E402
from propedge.contract.rules import load_rules  # noqa: E402
from propedge.outcomes.distribution import DayBlock  # noqa: E402

#: the code before Wave 3.1: master at c35cf40; the sha256 of each file's LF text
BASE_COMMIT = "c35cf40"
BASE_SHA256 = {"extended/user_beside.py": "443672e41246903d565c2207261df7d895cac67a32d6e5d98385da775b689ab7",
               "extended/user_readings.py": "56ff77855a0914a80f4c7addd200e2b11ce91127834708ef290287ffed519d7d",
               "extended/user_measures.py": "7134ec4aea28255095f7826b23177ab346605e2badc279c5efc48be86339f227"}
#: the budgets the synthetic readings use (a test's own; the operator's are set in Wave 4)
BUDGETS = (1000.0, 2500.0)

# ------------------------------------------------------------------------------------------------ the campaign

search = [d.date() for d in pd.bdate_range("2022-09-01", "2023-12-29")]
held = [d.date() for d in pd.bdate_range("2024-01-02", periods=60)]
days = [d.isoformat() for d in search + held]
N_DAYS = len(days)
LAST_SEARCH = len(search) - 1
#: the starts read: 0 and 40 reach 252 sessions inside the search years; LAST_SEARCH - 251 exactly 252; 200 and
#: LAST_SEARCH - 40 are cut at the block's end (shorter than the whole-window run); LAST_SEARCH reads one session; the
#: held-out years' first start and one late in them
STARTS = [0, 40, LAST_SEARCH - 251, 200, LAST_SEARCH - 40, LAST_SEARCH, LAST_SEARCH + 1, N_DAYS - 25]
blocks = []
for i in range(N_DAYS):
    k = 1 + (i % 4)
    et = np.array([500.0 + 60.0 * j for j in range(k)])
    bad = (i % 13) in (11, 12)                         # a bad spell: every trade lost (breaches, so stacking shows)
    win = np.array([(not bad) and ((i * 7 + j) % 5) < 3 for j in range(k)])
    pnl = np.where(win, 1000.0, -500.0)
    blocks.append(DayBlock(pnl=pnl, risked=np.full(k, 500.0), exit_reasons=tuple("target" if w else "stop" for w in win),
                           entry_t=et, exit_t=et + 30.0))
rules = rules_from_ledger()
proto = Protocol(name="w31_synthetic", combine_rr=2.0, combine_risk=500.0, funded_rr=2.0, funded_risk=500.0,
                 trades_per_day=4, max_concurrent_accounts=5)
lag = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
args = {"draws": {"protocol": proto, "mode": "rotation", "flip": None},
        "path": dict(edge=0.0, rules=rules, initial_bankroll=1e9, max_concurrent_accounts=5,
                     subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                     activation=float(rules.activation), payout_lag_days=lag, max_concurrent_combines=5,
                     max_total_accounts=5, conduct=ConductModel(rtp=False, enforcement_p=0.0), combine_max_days=2000,
                     funded_horizon_days=100_000, purchase_budget=(20, 21)),
        "seed": B.SEED_BLOCK[1]}
job = {"engine": "single", "blocks": blocks, "dates": days, "args": args}
out: dict[str, Any] = {"n_days": N_DAYS, "last_search": LAST_SEARCH, "starts": STARTS}
t_all = time.time()


def at_commit(rel: str, name: str, inject: dict[str, Any] | None = None) -> tuple[types.ModuleType, str]:
    raw = subprocess.run(["git", "-C", str(REPO), "show", f"{BASE_COMMIT}:{rel}"], capture_output=True,
                         check=True).stdout
    src = raw.decode("utf-8").replace("\r\n", "\n")
    sha = hashlib.sha256(src.encode("utf-8")).hexdigest()
    mod = types.ModuleType(name)
    mod.__file__ = f"<{BASE_COMMIT}:{rel}>"
    sys.modules[name] = mod
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    for k, v in (inject or {}).items():
        setattr(mod, k, v)
    return mod, sha


OLD_M, sha_m = at_commit("extended/user_measures.py", "user_measures_c35cf40")
OLD_R, sha_r = at_commit("extended/user_readings.py", "user_readings_c35cf40", {"M": OLD_M})
OLD_B, sha_b = at_commit("extended/user_beside.py", "user_beside_c35cf40")
out["base_sha_ok"] = {"extended/user_beside.py": sha_b == BASE_SHA256["extended/user_beside.py"],
                      "extended/user_readings.py": sha_r == BASE_SHA256["extended/user_readings.py"],
                      "extended/user_measures.py": sha_m == BASE_SHA256["extended/user_measures.py"]}


class Pool:
    """`customer_journey._pool_run` recorded: the tasks each call hands it."""

    def __init__(self):
        self.calls: list[list[tuple]] = []
        self.real = CJ._pool_run

    def __call__(self, tasks, fn, workers, what):
        self.calls.append(list(tasks))
        return self.real(tasks, fn, workers, what)


POOL = Pool()
CJ._pool_run = POOL


def run(mod, resp_name: str, j: dict | None = None, **kw) -> list[dict]:
    return mod.run_starts("syn", "point", mod.BY_NAME[resp_name], j or job, STARTS, 1, **kw)


def diff(a, b) -> str | None:
    return I.first_difference(a, b)


# -- absent = before, bit for bit: every response
absent: dict[str, list[dict]] = {}
absent_diff, tasks_same = {}, {}
for r in B.RESPONSES:
    POOL.calls.clear()
    old = run(OLD_B, r.name)
    new = run(B, r.name)
    absent[r.name] = new
    absent_diff[r.name] = diff(old, new)
    t_old, t_new = POOL.calls
    tasks_same[r.name] = (len(t_old) == len(t_new) and all(
        len(a) == len(b) == 8 and a[:3] == b[:3] and a[6:] == b[6:] and all(x is y for x, y in zip(a[3:6], b[3:6]))
        for a, b in zip(t_old, t_new)))
out["absent_diff"] = absent_diff
out["absent_tasks_same"] = tasks_same
out["absent_keyed_journey"] = sorted(r for r, o in absent.items() if any("journey" in x for x in o))
out["seconds_absent"] = round(time.time() - t_all, 1)

# -- the readings before and now, Q-44's blocks named
residue = 0
readings_diff, table_diff, problems_old, problems_new = {}, {}, {}, {}
for name in ("off", "denial_50", "forfeit_25"):
    o = absent[name]
    for x in o:
        nm = np.array([v for v in x["rec"]["net_month"] if v is not None], float)
        residue += int(((nm > 0) & (nm <= M.TOL)).sum())
    rows_old, t_old = OLD_R.summary("syn", "point", B.BY_NAME[name], o)
    rows_new, t_new = UR.summary("syn", "point", B.BY_NAME[name], o, blocks=UR.Q44_BLOCKS)
    readings_diff[name] = diff(rows_old, rows_new)
    table_diff[name] = diff(t_old.to_dict("list"), t_new.to_dict("list")) or \
        (None if list(t_old.columns) == list(t_new.columns) and list(t_old.dtypes) == list(t_new.dtypes) else
         "the columns or dtypes differ")
    problems_old[name] = OLD_R.consistency_problems(rows_old, o, name)
    problems_new[name] = UR.consistency_problems(rows_new, o, name, blocks=UR.Q44_BLOCKS)
out["residue_nets"] = residue
out["readings_diff"], out["table_diff"] = readings_diff, table_diff
out["problems_old"], out["problems_new"] = problems_old, problems_new


def refused(f, *a, **k) -> str | None:
    try:
        f(*a, **k)
    except (ValueError, TypeError) as e:
        return type(e).__name__
    return None


o_off = absent["off"]
recs = [x["rec"] for x in o_off]
t_legacy = UR.start_table("syn", "point", "off", o_off)
out["default_refuses_legacy"] = {
    "summary": refused(UR.summary, "syn", "point", B.BY_NAME["off"], o_off),
    "scorecard_rows": refused(UR.scorecard_rows, recs), "extra_rows": refused(UR.extra_rows, recs),
    "path_rows": refused(UR.path_rows, t_legacy), "response_rows": refused(UR.response_rows, t_legacy),
    "journey_rows": refused(JR.journey_rows, o_off)}
out["defaults"] = {"BLOCKS": list(UR.BLOCKS), "Q44_BLOCKS": list(UR.Q44_BLOCKS)}

# -- the journey's window
t1 = time.time()
POOL.calls.clear()
jo: dict[str, list[dict]] = {}
for name in ("off", "denial_50", "forfeit_25", "rtp", "ftp_corrective_lost_3"):
    jo[name] = run(B, name, journey=True)
out["journey_task"] = [len(POOL.calls[0][0]), POOL.calls[0][0][13] is True,
                       list(POOL.calls[0][0][8:13]) == [None, None, {}, False, None]]
names, last = B.journey_window(days)
win, extra_key, same_uncut, cut, rel_ok, peak_ok, arr_ok, other_block = {}, {}, {}, {}, {}, {}, {}, {}
for name, o in jo.items():
    for x, a in zip(o, absent[name]):
        s = int(x["rec"]["start_day"])
        j = x["journey"]
        L_old, L_new = int(a["rec"]["observed"]), int(x["rec"]["observed"])
        key = f"{name}|{s}"
        win[key] = (L_new == min(252, last[s] - s + 1) and j["block_left"] == last[s] - s + 1
                    and j["block"] == names[s])
        cut[key] = L_new < L_old
        other_block[key] = any(names[k] != names[s] for k in range(s, s + L_new))
        extra_key[key] = list(x) == [k for k in a if k != "seed"] + ["journey", "seed"]
        if L_new == L_old:
            same_uncut[key] = diff({k: v for k, v in x.items() if k != "journey"}, a)
        rel = np.asarray(j["rel"], float)
        rel_ok[key] = len(rel) == L_new + 1 and all(float(rel[21 * m]) == float(x["rec"]["net_month"][m - 1])
                                                    for m in range(1, 13) if 21 * m <= L_new)
        peak_ok[key] = diff(tuple(M.peak_by_month(rel)), tuple(j["peak_month"])) is None
        got = sorted(d for acc in j["accounts"] for d in acc["arrivals"] if d <= L_new)
        arr_ok[key] = got == sorted(int(d) for d in x["rec"]["pay_days"])
out["journey_window_ok"] = all(win.values())
out["journey_cut"] = sorted(k for k, v in cut.items() if v)
out["journey_other_block"] = sorted(k for k, v in other_block.items() if v)
out["journey_key_placed"] = all(extra_key.values())
out["journey_uncut_diff"] = {k: v for k, v in same_uncut.items() if v}
out["journey_uncut_compared"] = len(same_uncut)
out["journey_rel_ok"], out["journey_peak_ok"] = all(rel_ok.values()), all(peak_ok.values())
out["journey_arrivals_ok"] = all(arr_ok.values())
out["journey_accounts"] = sum(len(x["journey"]["accounts"]) for x in jo["off"])
out["paid_starts_journey_off"] = sum(1 for x in jo["off"] if x["rec"]["pay_days"])

# -- refusals before any start
POOL.calls.clear()
holiday = sorted(search + held + [pd.Timestamp("2024-01-01").date()])
bad_jobs = {"holiday": {**job, "dates": [d.isoformat() for d in holiday][:N_DAYS]},
            "confirmation": {**job, "dates": days[:-1] + ["2026-07-17"]},
            "unordered": {**job, "dates": days[:5][::-1] + days[5:]}}
out["refusals"] = {k: refused(run, B, "off", j, journey=True) for k, j in bad_jobs.items()}
out["refusals"]["not_a_bool"] = refused(run, B, "off", None, journey="yes")
out["refusals_reached_pool"] = len(POOL.calls)
out["absent_accepts_any_calendar"] = refused(run, B, "off", bad_jobs["confirmation"]) is None

# -- composition with the pass-through class
PT = XG.PassThroughFundedAccount
got = run(B, "off", funded_account_cls=PT, journey=True)
out["class_composes"] = (diff(jo["off"], [{k: v for k, v in x.items() if k != "funded_account_cls"} for x in got])
                         is None and all(list(x)[-1] == "funded_account_cls" for x in got))

# -- the readings on journeys
summ, jprob, pb_ok, sub_ok, states_ok, peak_cols, refuse_reg = {}, {}, {}, {}, {}, {}, {}
for name in ("off", "denial_50", "forfeit_25"):
    o = jo[name]
    rows, t = JR.summary("syn", "point", B.BY_NAME[name], o, blocks=UR.E208_BLOCKS, budgets=BUDGETS)
    by = {(r["section"], r["block"], r["measure"], r["stat"]): r for r in rows}
    summ[name] = {"rows": len(rows), "sections": sorted({r["section"] for r in rows}),
                  "blocks": sorted({r["block"] for r in rows})}
    jprob[name] = JR.consistency_problems(rows, o, name, blocks=UR.E208_BLOCKS)
    ok_pb, ok_sub = True, True
    for b in UR.E208_BLOCKS:
        e63 = [x for x in o if x["journey"]["block"] == b and int(x["rec"]["observed"]) >= 63]
        rels = [np.asarray(x["journey"]["rel"], float) for x in e63]
        arrs = [list(zip(x["rec"]["pay_days"], x["rec"]["pay_cash"])) for x in e63]
        for lim in BUDGETS:
            if not e63:
                continue
            a = J.p_bankroll(rels, lim)["P"]
            c = J.p_bankroll(rels, lim, before_first_payout=True, arrivals=arrs)["P"]
            ok_pb &= by[("extra", b, f"P_B_{lim:g}", "value")]["value"] == a
            ok_sub &= by[("extra", b, f"P_B_before_first_payout_{lim:g}", "value")]["value"] == c
        if e63:
            ok_pb &= by[("extra", b, "P", "value")]["value"] == J.p_bankroll(rels)["P"]
    pb_ok[name], sub_ok[name] = bool(ok_pb), bool(ok_sub)
    sums = [sum(by[("journey", b, f"bankroll_stop_{lim:g}", f"share_{k}")]["value"]
                for k in ("paid_within", "run_out", "censored")) for b in UR.E208_BLOCKS for lim in BUDGETS
            if by[("journey", b, f"bankroll_stop_{lim:g}", "share_paid_within")]["n"] > 0]
    states_ok[name] = bool(sums) and all(abs(v - 1.0) <= 1e-12 for v in sums)
    peak_cols[name] = all(diff(tuple(float(v) for v in t.loc[i, list(UR.PEAK_COLS)]), x["journey"]["peak_month"])
                          is None for i, x in enumerate(o))
    refuse_reg[name] = refused(UR.summary, "syn", "point", B.BY_NAME[name], o, blocks=UR.Q44_BLOCKS)
    if name == "off":                                  # not vacuous: what the journey rows saw on the search years
        sr = [r for r in rows if r["block"] == "search" and r["section"] == "journey"]
        out["journey_exercised"] = {
            "strict_flags": sorted({r["value"] for r in sr if r["stat"].endswith("_exact")}),
            "states_nonzero": sorted({r["stat"] for r in sr if r["measure"].startswith("bankroll_stop_")
                                      and r["value"] > 0}),
            "accounts": by[("journey", "search", "funded_lifetime_payouts", "n_accounts")]["value"],
            "lost": by[("journey", "search", "funded_lifetime_payouts", "n_lost")]["value"],
            "e252": by[("journey", "search", "S4b", "value")]["n"],
            "p_b": sorted({r["value"] for r in rows if r["section"] == "extra" and r["measure"].startswith("P_B_")})}
out["journey_summary"], out["journey_problems"] = summ, jprob
out["journey_pb_equals_recomputed"], out["journey_sub_equals_recomputed"] = pb_ok, sub_ok
out["journey_states_sum_to_one"], out["journey_peak_columns"] = states_ok, peak_cols
out["journey_refuses_registered_blocks"] = refuse_reg
rows, _ = JR.summary("syn", "point", B.BY_NAME["off"], jo["off"], budgets=BUDGETS)
out["journey_default_block"] = sorted({r["block"] for r in rows})
out["seconds_journey"] = round(time.time() - t1, 1)
out["seconds"] = round(time.time() - t_all, 1)
print(json.dumps(out, default=str))
