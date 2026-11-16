"""Q-100's synthetic check (`tests/test_user_beside_seams.py` runs it in a process of its own: the vendored tree goes on
its `sys.path`): Q-17's adapter (`extended/user_beside.py`) with its two more declared, off-by-default keywords --
`household_closure` (a route for the engine's household rule, Stage 2 R7) and `seed_base` (the base the start seeds are
drawn from) -- on Q-76's deterministic synthetic campaign through the vendored engine: no bar, no atlas, no generator
(every value a function of the day's and the trade's index; the shared-day seed `user_beside.SEED_BLOCK[1]`, as
`tests/q76_synthetic.py` and `tests/q94_synthetic.py` use it).

    python tests/q100_synthetic.py <repository root>            # prints one JSON line last

What it reports (the test asserts each):

* **absent = before, bit for bit**: master's adapter at be41efd (`git show be41efd:extended/user_beside.py`, its text
  pinned by sha256; the file last changed at 60de26c) and the adapter now give the same per-start outputs (Q-76's
  canonical form) on all 19 responses, the same tasks to the pool, the same `response_args` and `base_problems`; also
  with the pass-through class (the 9 responses it can run) and with a recorder (outputs and records);
* **`household_closure=False`**: every output equal to the absent run's apart from one key, `household_closure`, named
  after `seed` on every start, on all 19 responses; the same with the pass-through class (the class's key stays last)
  and with a recorder (the records the same too); on the path as given for every response but the forfeiture, whose
  path keeps its own True;
* **`household_closure=True`**: refused (`ValueError`) for Topstep's class -- none declared, the vendored
  `FundedAccount` given, the pass-through -- on every response, before any start; with a class that declares a
  household rule (two probes, strict and count-only by default, ending an account at its second payout as Lucid's ends
  one at its fifth) the route reaches the engine: each start's output equals the vendored engine called directly with
  that reading (the U1 record, the daily measures, the response's record, the seed), at the class's default, True and
  False; the closing reading closes the household on some start (nothing bought after it, every account ended by it,
  another account closed by it), the counting reading closes none (only the account that raised it ends, and another
  account outlives that close);
* **`seed_base`**: 20261920 given equals the default apart from naming on all 19 responses; another base (20261990,
  the firms reading's ladder seed) makes every start's seed `child_seed(base, 0, start)`, leaves the thirteen responses
  without an enforcement draw equal apart from `seed` and the naming, changes the ladder's draws on some start, equals
  the engine called directly at those seeds (denial at 10, 25, 50 %), and is the recorded start seed;
* **composed**: a household class, `household_closure=False`, the ladder's seed base and a recorder together equal the
  engine called directly; with a recorder the outputs are the unrecorded ones; the key order;
* **refusals**, each before any start runs: bad household values (six kinds), bad seed bases (seven kinds), a path
  already carrying `household_closure` (with the keyword and without, as before);
* the entries for a result's parameters, the signatures' defaults, a worker's task (it pickles back with its keywords
  and gives the same outputs), and the identity's comparison (`seam_outs_problems`) holding and refusing.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import pickle
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
from extended import replay_records as RR  # noqa: E402
from extended import user_beside as B  # noqa: E402
from extended import user_measures as M  # noqa: E402
from propedge.campaign.lockstep import ConductModel, FundedAccount, child_seed, simulate_lockstep_path  # noqa: E402
from propedge.campaign.payout_method import payout_method_terms  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.campaign.shared_days import SharedDayDraws  # noqa: E402
from propedge.contract.adapter import rules_from_ledger  # noqa: E402
from propedge.contract.rules import load_rules  # noqa: E402
from propedge.outcomes.distribution import DayBlock  # noqa: E402
from propedge.research import user_journey as U  # noqa: E402

#: the adapter before Q-100: master at be41efd (the file's text last changed at 60de26c, Q-94); the sha256 of its LF text
BASE_COMMIT = "be41efd"
BASE_SHA256 = "759e5771852ae9a4f8e8e0c3a9fdfe46b49a202303fd8914697a2300b0667b5e"
N_DAYS = 160
STARTS = [0, 5, 14, 21, 40, 77, N_DAYS - 3]
#: the firms reading's ladder seed (`prereg/DRAFT_RD_firms.md` section 12): another base
OTHER_BASE = 20261990
PT = XG.PassThroughFundedAccount
NAME_HC, NAME_SB, NAME_CLS = "household_closure", "seed_base", "funded_account_cls"


class StrictHouseholdFundedAccount(FundedAccount):
    """A probe household rule, closing by default (as Lucid's declares its own): an account ends at the close of its
    second payout and raises the rule there (Lucid's ends at its fifth, `LucidFundedAccount._after_payout`); a denied
    payout lowers it again (as Lucid's `deny_last_payout`)."""

    HOUSEHOLD_CLOSES_AT_LIVE = True
    LIMIT = 2
    closes_household = False

    def _after_payout(self, calendar_day: int) -> None:
        if self.n_payouts >= self.LIMIT:
            self.closes_household = True
            self.ended_on = int(calendar_day)

    def deny_last_payout(self, calendar_day: int) -> None:
        super().deny_last_payout(calendar_day)
        self.closes_household = False


class CountOnlyHouseholdFundedAccount(StrictHouseholdFundedAccount):
    """The same rule, counting only by default (`HOUSEHOLD_CLOSES_AT_LIVE = False`)."""

    HOUSEHOLD_CLOSES_AT_LIVE = False


# ------------------------------------------------------------------------------------------------ the campaign

days = [d.date().isoformat() for d in pd.bdate_range("2023-01-02", periods=N_DAYS)]
blocks = []
for i in range(N_DAYS):
    k = 1 + (i % 4)
    et = np.array([500.0 + 60.0 * j for j in range(k)])
    bad = (i % 13) in (11, 12)                         # a bad spell: every trade lost (breaches, so stacking shows)
    win = np.array([(not bad) and ((i * 7 + j) % 5) < 3 for j in range(k)])
    pnl = np.where(win, 1000.0, -500.0)
    blocks.append(DayBlock(pnl=pnl, risked=np.full(k, 500.0),
                           exit_reasons=tuple("target" if w else "stop" for w in win), entry_t=et, exit_t=et + 30.0))
offer_ids = [[f"{days[i]}#{j}" for j in range(len(b))] for i, b in enumerate(blocks)]
rules = rules_from_ledger()
proto = Protocol(name="q100_synthetic", combine_rr=2.0, combine_risk=500.0, funded_rr=2.0, funded_risk=500.0,
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
out: dict[str, Any] = {}
t_all = time.time()


def before_module() -> tuple[types.ModuleType, str]:
    raw = subprocess.run(["git", "-C", str(REPO), "show", f"{BASE_COMMIT}:extended/user_beside.py"],
                         capture_output=True, check=True).stdout
    src = raw.decode("utf-8").replace("\r\n", "\n")
    sha = hashlib.sha256(src.encode("utf-8")).hexdigest()
    mod = types.ModuleType("user_beside_before_q100")
    mod.__file__ = f"<{BASE_COMMIT}:extended/user_beside.py>"
    sys.modules[mod.__name__] = mod
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod, sha


OLD, sha = before_module()
out["base_sha_ok"] = sha == BASE_SHA256
out["base_had_no_keywords"] = all(k not in inspect.signature(OLD.run_starts).parameters
                                  for k in (NAME_HC, NAME_SB))


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


def run(mod, resp_name: str, j: dict = job, starts: list[int] = STARTS, **kw) -> list[dict]:
    return mod.run_starts("syn", "point", mod.BY_NAME[resp_name], j, starts, 1, **kw)


def diff(a, b) -> str | None:
    return I.first_difference(a, b)


def strip(outs: list[dict], keys=(NAME_HC, NAME_SB)) -> list[dict]:
    return [{k: v for k, v in o.items() if k not in keys} for o in outs]


def same_frames(a: pd.DataFrame, b: pd.DataFrame) -> str | None:
    try:
        pd.testing.assert_frame_equal(a.reset_index(drop=True), b.reset_index(drop=True), check_exact=True)
    except AssertionError as exc:
        return str(exc).splitlines()[0][:300]
    return None


def named_after_seed(outs: list[dict], want: dict[str, Any], cls: type | None = None) -> bool:
    """Every output names exactly `want` (values and types) right after `seed`, then the class (last) when given."""
    tail = [*want] + ([NAME_CLS] if cls is not None else [])
    for o in outs:
        keys = list(o)
        i = keys.index("seed")
        if keys[i + 1:] != tail:
            return False
        if any(type(o[k]) is not type(v) or o[k] != v for k, v in want.items()):
            return False
        if cls is not None and o[NAME_CLS] != B.class_name(cls):
            return False
    return bool(outs)


def refused(call, exc: type) -> bool:
    n = len(POOL.calls)
    try:
        call()
    except exc:
        return len(POOL.calls) == n                 # refused before the pool was reached
    except Exception:  # noqa: BLE001
        return False
    return False


NON_FTP = [r.name for r in B.RESPONSES if r.kind != "ftp"]
NO_DRAW = [r.name for r in B.RESPONSES if r.kind in ("off", "rtp", "ftp")]          # no enforcement draw at all
LADDER = [r.name for r in B.RESPONSES if r.kind in ("denial", "forfeit")]

# -- absent = before Q-100, bit for bit: every response; with the pass-through class; with a recorder
absent: dict[str, list[dict]] = {}
absent_diff: dict[str, str | None] = {}
tasks_same: dict[str, bool] = {}
for r in B.RESPONSES:
    POOL.calls.clear()
    old = run(OLD, r.name)
    new = run(B, r.name)
    absent[r.name] = new
    absent_diff[r.name] = diff(old, new)
    t_old, t_new = POOL.calls
    tasks_same[r.name] = (len(t_old) == len(t_new) and all(
        len(a) == len(b) == 8 and a[:3] == b[:3] and a[6:] == b[6:] and all(x is y for x, y in zip(a[3:6], b[3:6]))
        for a, b in zip(t_old, t_new)))
out["absent_diff"] = absent_diff
out["absent_tasks_same"] = tasks_same
out["absent_named"] = sorted(r for r, o in absent.items() if any(NAME_HC in x or NAME_SB in x for x in o))
absent_pt: dict[str, list[dict]] = {}
pt_same = {}
for name in NON_FTP:
    POOL.calls.clear()
    old = run(OLD, name, funded_account_cls=PT)
    absent_pt[name] = run(B, name, funded_account_cls=PT)
    t_old, t_new = POOL.calls
    pt_same[name] = (diff(old, absent_pt[name]) is None and len(t_old) == len(t_new)
                     and all(len(a) == len(b) == 9 and a[8] is b[8] is PT for a, b in zip(t_old, t_new)))
out["absent_with_class_same"] = pt_same
REC_RESPONSES = ("off", "denial_50", "forfeit_25", "rtp", "ftp_corrective_lost_3")
rec_same = {}
for name in REC_RESPONSES:
    r_old, r_new = RR.ReplayRecorder(offer_ids=offer_ids), RR.ReplayRecorder(offer_ids=offer_ids)
    POOL.calls.clear()
    o_old = run(OLD, name, recorder=r_old)
    o_new = run(B, name, recorder=r_new)
    t_old, t_new = POOL.calls
    rec_same[name] = {"outputs": diff(o_old, o_new), "records": same_frames(r_old.trades(), r_new.trades())
                      or same_frames(r_old.accounts(), r_new.accounts()),
                      "tasks": len(t_old) == len(t_new) and all(len(a) == len(b) == 10 for a, b in zip(t_old, t_new))}
out["absent_with_recorder_same"] = rec_same


def cls_view(c: type) -> tuple:
    return (c.__qualname__, tuple(k.__qualname__ for k in c.__mro__), getattr(c, "HOUSEHOLD_CLOSES_AT_LIVE", None))


def path_view(p: dict) -> dict:
    return {k: (cls_view(v) if isinstance(v, type) else v) for k, v in p.items()}


ra_same = {}
for r in B.RESPONSES:
    a_old = OLD.response_args(args, OLD.BY_NAME[r.name])
    a_new = B.response_args(args, r)
    ra_same[r.name] = (list(a_old) == list(a_new) and list(a_old["path"]) == list(a_new["path"])
                       and path_view(a_old["path"]) == path_view(a_new["path"])
                       and all(a_old[k] == a_new[k] for k in a_old if k != "path"))
out["response_args_same"] = ra_same
carrying = {**args, "path": {**args["path"], NAME_HC: False}}
probe_args = [args, carrying, {**args, "path": {**args["path"], "funded_account_cls": FundedAccount}},
              {**args, "draws": {**args["draws"], "flip": object()}},
              {**args, "path": {**args["path"], "conduct": ConductModel(rtp=True, enforcement_p=0.0)}}]
out["base_problems_same"] = [OLD.base_problems(a) == B.base_problems(a) for a in probe_args]
out["base_problems_refuses_household"] = any("household_closure" in p for p in B.base_problems(carrying))

# -- household_closure=False: equal apart from naming, on all 19; with the class; with a recorder
hf_diff, hf_named, hf_tasks = {}, {}, {}
for r in B.RESPONSES:
    POOL.calls.clear()
    got = run(B, r.name, household_closure=False)
    (t,) = POOL.calls
    hf_tasks[r.name] = all(len(x) == 11 and x[8] is None and x[9] is None and x[10] == {NAME_HC: False}
                           for x in t)
    hf_named[r.name] = named_after_seed(got, {NAME_HC: False})
    hf_diff[r.name] = diff(absent[r.name], strip(got))
out["hf_diff"], out["hf_named"], out["hf_tasks"] = hf_diff, hf_named, hf_tasks
hf_pt_diff, hf_pt_named = {}, {}
for name in NON_FTP:
    got = run(B, name, funded_account_cls=PT, household_closure=False)
    hf_pt_named[name] = named_after_seed(got, {NAME_HC: False}, PT)
    hf_pt_diff[name] = diff(absent_pt[name], strip(got))
out["hf_pt_diff"], out["hf_pt_named"] = hf_pt_diff, hf_pt_named
hf_rec = {}
for name in REC_RESPONSES:
    r_off, r_on = RR.ReplayRecorder(offer_ids=offer_ids), RR.ReplayRecorder(offer_ids=offer_ids)
    o_off = run(B, name, recorder=r_off)
    POOL.calls.clear()
    o_on = run(B, name, recorder=r_on, household_closure=False)
    (t,) = POOL.calls
    hf_rec[name] = {"outputs": diff(o_off, strip(o_on)), "records": same_frames(r_off.trades(), r_on.trades())
                    or same_frames(r_off.accounts(), r_on.accounts()),
                    "tasks": all(len(x) == 11 and x[8] is None and isinstance(x[9], RR.ReplayReducer) for x in t),
                    "problems": r_on.problems()[:3]}
out["hf_recorder"] = hf_rec
out["np_bool_named_as_bool"] = named_after_seed(run(B, "off", starts=[5], household_closure=np.bool_(False)),
                                                {NAME_HC: False})


def path_of(resp_name: str, **kw) -> dict:
    return B.response_args(args, B.BY_NAME[resp_name], **kw)["path"]


fc = path_of("forfeit_10", household_closure=False)
out["paths"] = {
    "off_false": path_of("off", household_closure=False).get(NAME_HC, "absent") is False,
    "denial_false": path_of("denial_25", household_closure=False).get(NAME_HC, "absent") is False,
    "rtp_false": path_of("rtp_w3", household_closure=False).get(NAME_HC, "absent") is False,
    "ftp_false": (lambda p: p.get(NAME_HC, "absent") is False and p["focused_trader"] is not None)(
        path_of("ftp_slowdown_lost_5", household_closure=False)),
    "forfeit_keeps_true": fc[NAME_HC] is True and fc["funded_account_cls"] is B.forfeit_class(),
    "forfeit_pt_keeps_true": (lambda p: p[NAME_HC] is True and p["funded_account_cls"] is B.forfeit_class(PT))(
        path_of("forfeit_50", funded_account_cls=PT, household_closure=False)),
    "absent_none": all(NAME_HC not in path_of(r.name) for r in B.RESPONSES if r.kind != "forfeit"),
    "class_false": (lambda p: p[NAME_HC] is False and p["funded_account_cls"] is StrictHouseholdFundedAccount)(
        path_of("denial_10", funded_account_cls=StrictHouseholdFundedAccount, household_closure=False)),
    "class_true": (lambda p: p[NAME_HC] is True and p["funded_account_cls"] is CountOnlyHouseholdFundedAccount)(
        path_of("off", funded_account_cls=CountOnlyHouseholdFundedAccount, household_closure=True))}

# -- household_closure=True: refused for Topstep's class; with a household class, the engine's own reading
out["true_refused"] = {
    "absent_class": {r.name: refused(lambda r=r: run(B, r.name, household_closure=True), ValueError)
                     for r in B.RESPONSES},
    "vendored_class": {r.name: refused(lambda r=r: run(B, r.name, funded_account_cls=FundedAccount,
                                                         household_closure=True), ValueError) for r in B.RESPONSES},
    "pass_through": {r.name: refused(lambda r=r: run(B, r.name, funded_account_cls=PT, household_closure=True),
                                     ValueError) for r in B.RESPONSES},
    "response_args": {r.name: refused(lambda r=r: B.response_args(args, r, household_closure=True), ValueError)
                      for r in B.RESPONSES}}
try:                                                    # the engine refuses it the same way
    B.replay(blocks[:40], {**args, "path": {**args["path"], NAME_HC: True}}, B.start_seed(0))
    out["engine_refuses_true_topstep"] = False
except ValueError as exc:
    out["engine_refuses_true_topstep"] = "has no household rule" in str(exc)


def direct(resp_name: str, cls: type | None = None, hc: bool | None = None, base: int = B.DENIAL_SEED,
           starts: list[int] = STARTS) -> list[dict[str, Any]]:
    """Each start as the vendored engine gives it called directly -- the path's arguments made here by hand (the job's,
    the response's conduct, the class and the household reading put on as given), the shared day draws and the engine
    call as `customer_slices.replay` makes them, the path seed `child_seed(base, 0, start)` -- its long run read by the
    adapter's own `long_record`, `user_measures.daily` and `response_record`. For responses without a model or a view
    (off, denial, rtp)."""
    resp = B.BY_NAME[resp_name]
    if resp.kind not in ("off", "denial", "rtp"):
        raise ValueError(resp_name)
    path = dict(args["path"])
    path["conduct"] = ConductModel(rtp=bool(resp.rtp), enforcement_p=float(resp.enforcement_p),
                                   rtp_warnings=int(resp.rtp_warnings))
    if cls is not None:
        path["funded_account_cls"] = cls
    if hc is not None:
        path[NAME_HC] = hc

    def pay(lp, obs):
        return U.payout_arrivals([(f.activation_day, lag, f.payout_days, f.payout_cash) for f in lp.funded], obs)

    def totals(lp):
        return lp.path.total_fees, lp.path.total_payouts

    res = []
    for s in starts:
        L = min(U.HORIZON, N_DAYS - s)
        sd = SharedDayDraws({0: list(blocks[s:s + L])}, seed=args["seed"], replay=True, **args["draws"])
        seed = int(child_seed(int(base), 0, int(s)))
        lp = simulate_lockstep_path(proto, seed=seed, horizon_days=L + 1, **path, **sd.lockstep_kwargs())
        mine = B.long_record(s, days[s], lp, pay, totals)
        rel = np.asarray(lp.path.cash_series, float) - float(lp.path.initial_bankroll)
        res.append({"rec": mine["rec"], "daily": M.daily(rel), "response": B.response_record(lp, resp), "seed": seed,
                    "lp": lp})
    return res


def against_direct(outs: list[dict], ref: list[dict]) -> str | None:
    """The adapter's outputs against the direct engine's, start by start: the U1 record (its exact-length `alt` taken
    out), the daily measures, the response's record, the seed -- bit for bit; and U1's checks of the engine's totals."""
    if len(outs) != len(ref):
        return f"{len(outs)} outputs against {len(ref)}"
    for o, d in zip(outs, ref):
        s = o["rec"]["start_day"]
        mine = {"rec": {k: v for k, v in o["rec"].items() if k != "alt"}, "daily": o["daily"],
                "response": o["response"], "seed": o["seed"]}
        x = diff({k: d[k] for k in mine}, mine)
        if x:
            return f"start {s}: {x}"
        if o["pay_bad"] or o["cash_bad"] or o["fee_bad"]:
            return f"start {s}: U1's checks of the engine's totals fail"
    return None


def household_view(ref: list[dict]) -> dict[str, Any]:
    """What the engine's household rule did on the direct runs: the reading, the starts it triggered and closed on, and
    the closing reading's and the counting reading's consequences checked on each start."""
    v = {"readings": sorted({str(d["lp"].household.get("reading")) for d in ref}), "triggered": 0, "closed": 0,
         "others_closed": 0, "outlived": 0, "after_close_ok": True, "count_only_ok": True}
    for d in ref:
        lp, h = d["lp"], d["lp"].household
        if int(h.get("triggers", 0)) > 0:
            v["triggered"] += 1
        c = int(h.get("closed_on", -1))
        if c >= 0:
            v["closed"] += 1
            if int(h.get("funded_closed", 0)) + int(h.get("combines_closed", 0)) + int(h.get("passes_closed", 0)) > 0:
                v["others_closed"] += 1
            if (any(x.purchase_day > c for x in lp.combines)
                    or any(x.resolved_on is None or int(x.resolved_on) > c for x in lp.combines)
                    or any(f.ended_on is None or int(f.ended_on) > c for f in lp.funded)):
                v["after_close_ok"] = False
        elif h.get("reading") == "count_only" and int(h.get("triggers", 0)) > 0:
            if any(f.household_closed for f in lp.funded) or any(x.household_closed for x in lp.combines):
                v["count_only_ok"] = False
            first = min((int(f.ended_on) for f in lp.funded
                         if f.n_payouts >= StrictHouseholdFundedAccount.LIMIT and f.ended_on is not None
                         and not f.closed), default=None)
            if first is None:                       # a trigger with no account that raised it: the probe is wrong
                v["count_only_ok"] = False
                continue
            if any(f.activation_day < first and (f.ended_on is None or int(f.ended_on) > first) for f in lp.funded) \
                    or any(x.purchase_day > first for x in lp.combines):
                v["outlived"] += 1
    return v


HCLS = {"strict": StrictHouseholdFundedAccount, "count_only": CountOnlyHouseholdFundedAccount}
hh: dict[str, Any] = {}
for cname, cls in HCLS.items():
    for hc in (None, True, False):
        key = f"{cname}_{'default' if hc is None else str(hc).lower()}"
        kw = {"funded_account_cls": cls} if hc is None else {"funded_account_cls": cls, "household_closure": hc}
        got = run(B, "off", **kw)
        ref = direct("off", cls, hc)
        hh[key] = {"against_direct": against_direct(got, ref), "view": household_view(ref),
                   "named": named_after_seed(got, {} if hc is None else {NAME_HC: hc}, cls), "outs": got}
out["household"] = {k: {kk: vv for kk, vv in v.items() if kk != "outs"} for k, v in hh.items()}
out["household_equal"] = {
    "strict_true_is_default": diff(strip(hh["strict_default"]["outs"]), strip(hh["strict_true"]["outs"])),
    "count_only_false_is_default": diff(strip(hh["count_only_default"]["outs"]), strip(hh["count_only_false"]["outs"])),
    "strict_false_differs": diff(strip(hh["strict_default"]["outs"]), strip(hh["strict_false"]["outs"])) is not None,
    "count_only_true_differs": diff(strip(hh["count_only_default"]["outs"]),
                                    strip(hh["count_only_true"]["outs"])) is not None,
    "closing_readings_agree": diff(strip(hh["strict_default"]["outs"], (NAME_HC, NAME_SB, NAME_CLS)),
                                   strip(hh["count_only_true"]["outs"], (NAME_HC, NAME_SB, NAME_CLS))),
    "counting_readings_agree": diff(strip(hh["strict_false"]["outs"], (NAME_HC, NAME_SB, NAME_CLS)),
                                    strip(hh["count_only_default"]["outs"], (NAME_HC, NAME_SB, NAME_CLS)))}
den = {}
for name in ("denial_50", "rtp"):
    den[name] = against_direct(run(B, name, funded_account_cls=StrictHouseholdFundedAccount, household_closure=False),
                               direct(name, StrictHouseholdFundedAccount, False))
out["household_other_responses"] = den
out["household_forfeit_refused"] = {
    r.name: refused(lambda r=r: run(B, r.name, funded_account_cls=StrictHouseholdFundedAccount,
                                    household_closure=False), ValueError) for r in B.RESPONSES if r.kind == "forfeit"}
out["household_ftp_refused"] = refused(lambda: run(B, "ftp_corrective_lost_3",
                                                   funded_account_cls=StrictHouseholdFundedAccount,
                                                   household_closure=True), ValueError)

# -- seed_base: the default given; another base
sd_diff, sd_named, sd_tasks = {}, {}, {}
for r in B.RESPONSES:
    POOL.calls.clear()
    got = run(B, r.name, seed_base=B.DENIAL_SEED)
    (t,) = POOL.calls
    sd_tasks[r.name] = all(len(x) == 11 and x[8] is None and x[9] is None and x[10] == {NAME_SB: B.DENIAL_SEED}
                           for x in t)
    sd_named[r.name] = named_after_seed(got, {NAME_SB: B.DENIAL_SEED})
    sd_diff[r.name] = diff(absent[r.name], strip(got))
out["sd_default_diff"], out["sd_default_named"], out["sd_default_tasks"] = sd_diff, sd_named, sd_tasks
other: dict[str, list[dict]] = {}
for r in B.RESPONSES:
    other[r.name] = run(B, r.name, seed_base=OTHER_BASE)
want_seeds = [int(child_seed(OTHER_BASE, 0, s)) for s in STARTS]
out["other_base"] = {
    "seeds": all([x["seed"] for x in o] == want_seeds for o in other.values()),
    "seeds_differ": all(a != b for a, b in zip(want_seeds, [B.start_seed(s) for s in STARTS])),
    "start_seed_fn": [B.start_seed(s, OTHER_BASE) for s in STARTS] == want_seeds,
    "named": all(named_after_seed(o, {NAME_SB: OTHER_BASE}) for o in other.values()),
    "no_draw_equal": {n: diff(strip(absent[n], ("seed",)), strip(other[n], ("seed", NAME_SB))) for n in NO_DRAW},
    "ladder_differs": sorted(n for n in LADDER if diff(absent[n], strip(other[n])) is not None),
    "against_direct": {n: against_direct(other[n], direct(n, base=OTHER_BASE))
                       for n in ("denial_10", "denial_25", "denial_50")},
    "default_against_direct": {n: against_direct(absent[n], direct(n)) for n in ("off", "denial_50", "rtp")}}
out["np_int_named_as_int"] = named_after_seed(run(B, "off", starts=[5], seed_base=np.int64(OTHER_BASE)),
                                              {NAME_SB: OTHER_BASE})
r_sb = RR.ReplayRecorder(offer_ids=offer_ids)
o_sb = run(B, "denial_50", recorder=r_sb, seed_base=OTHER_BASE)
t_sb = r_sb.trades()
out["seed_base_recorded"] = {
    "outputs": diff(other["denial_50"], o_sb),
    "start_seed": bool(len(t_sb)) and all((t_sb.loc[t_sb["start_day"] == s, "start_seed"] == w).all()
                                         for s, w in zip(STARTS, want_seeds)),
    "per_start": [int(x["start_seed"]) for x in r_sb.per_start("syn", "point", "denial_50")] == want_seeds}

# -- composed: a household class, False, the other base and a recorder, against the engine called directly
POOL.calls.clear()
r_all = RR.ReplayRecorder(offer_ids=offer_ids)
o_all = run(B, "denial_25", funded_account_cls=StrictHouseholdFundedAccount, household_closure=False,
            seed_base=OTHER_BASE, recorder=r_all)
(t_all_tasks,) = POOL.calls
o_plain = run(B, "denial_25", funded_account_cls=StrictHouseholdFundedAccount, household_closure=False,
              seed_base=OTHER_BASE)
out["composed"] = {
    "against_direct": against_direct(o_all, direct("denial_25", StrictHouseholdFundedAccount, False, OTHER_BASE)),
    "recorder_changes_nothing": diff(o_plain, o_all),
    "named": named_after_seed(o_all, {NAME_HC: False, NAME_SB: OTHER_BASE}, StrictHouseholdFundedAccount),
    "tasks": all(len(x) == 11 and x[8] is StrictHouseholdFundedAccount and isinstance(x[9], RR.ReplayReducer)
                 and x[10] == {NAME_HC: False, NAME_SB: OTHER_BASE} for x in t_all_tasks),
    "recorded_seeds": [int(x["start_seed"]) for x in r_all.per_start("syn", "point", "denial_25")] == want_seeds,
    "problems": r_all.problems()[:3]}
o_both = run(B, "off", household_closure=False, seed_base=B.DENIAL_SEED, funded_account_cls=PT)
out["composed"]["both_given_pt"] = (diff(absent_pt["off"], strip(o_both)) is None
                                    and named_after_seed(o_both, {NAME_HC: False, NAME_SB: B.DENIAL_SEED}, PT))

# -- refusals, each before any start runs
bad_hc = {"zero": 0, "one": 1, "string_false": "False", "string_true": "True", "float": 0.0, "list": [False]}
bad_sb = {"true": True, "false": False, "float": 1.5, "float_whole": 20261920.0, "string": "20261920",
          "np_float": np.float64(3.0), "negative": -1}
out["refused_household"] = {k: refused(lambda v=v: run(B, "off", household_closure=v), TypeError)
                            for k, v in bad_hc.items()}
out["refused_household_args"] = {k: refused(lambda v=v: B.response_args(args, B.BY_NAME["off"], household_closure=v),
                                            TypeError) for k, v in bad_hc.items()}
out["refused_seed_base"] = {k: refused(lambda v=v: run(B, "denial_50", seed_base=v),
                                       ValueError if k == "negative" else TypeError) for k, v in bad_sb.items()}
job_carrying = {**job, "args": carrying}
out["refused_path_carrying"] = {
    "run_starts_with_keyword": refused(lambda: run(B, "off", j=job_carrying, household_closure=False), ValueError),
    "run_starts_with_seed_base": refused(lambda: run(B, "off", j=job_carrying, seed_base=B.DENIAL_SEED), ValueError),
    "response_args_with_keyword": refused(lambda: B.response_args(carrying, B.BY_NAME["off"], household_closure=False),
                                          ValueError),
    "response_args_without": refused(lambda: B.response_args(carrying, B.BY_NAME["off"]), ValueError)}
try:                                                # without a keyword: refused inside the task, as before Q-100
    run(B, "off", j=job_carrying)
    out["refused_path_carrying"]["run_starts_without"] = False
except ValueError as exc:
    out["refused_path_carrying"]["run_starts_without"] = "already carry 'household_closure'" in str(exc)

# -- the entries for a result's parameters; the signatures
out["parameters"] = {
    "absent": B.seam_parameters() == {} and B.run_parameters() == {},
    "household": B.seam_parameters(False) == {NAME_HC: False},
    "seed": B.seam_parameters(seed_base=OTHER_BASE) == {NAME_SB: OTHER_BASE},
    "both_ordered": list(B.seam_parameters(np.bool_(True), np.int64(7)).items()) == [(NAME_HC, True), (NAME_SB, 7)]
    and type(B.seam_parameters(np.bool_(True))[NAME_HC]) is bool,
    "run_ordered": list(B.run_parameters(PT, False, OTHER_BASE).items()) == [
        (NAME_HC, False), (NAME_SB, OTHER_BASE), (NAME_CLS, "extended.gate.PassThroughFundedAccount")],
    "class_alone": B.run_parameters(PT) == B.class_parameters(PT)}
out["signature"] = {f: all(inspect.signature(getattr(B, f)).parameters[k].default is None for k in ks)
                    for f, ks in (("run_starts", (NAME_HC, NAME_SB, NAME_CLS, "recorder")),
                                  ("response_args", (NAME_HC, NAME_CLS)))}

# -- a worker's task: pickles back with its keywords and class; the same outputs
POOL.calls.clear()
run(B, "denial_50", funded_account_cls=StrictHouseholdFundedAccount, household_closure=True, seed_base=OTHER_BASE)
(task,) = POOL.calls[-1]
back = pickle.loads(pickle.dumps(task))
out["task_given"] = {"length": len(task), "class": back[8] is StrictHouseholdFundedAccount, "no_reducer": back[9] is None,
                     "keywords": back[10] == {NAME_HC: True, NAME_SB: OTHER_BASE},
                     "same_outputs": diff(B._task(task), B._task(back)) is None}

# -- the identity's comparison
given = run(B, "off", **I.Q100_GIVEN)
out["identity_compare"] = {
    "given": I.seam_outs_problems(absent["off"], given, I.Q100_GIVEN, "syn"),
    "not_named": bool(I.seam_outs_problems(absent["off"], absent["off"], I.Q100_GIVEN, "syn")),
    "named_wrong": bool(I.seam_outs_problems(absent["off"], run(B, "off", household_closure=False), I.Q100_GIVEN,
                                             "syn")),
    "other_base": bool(I.seam_outs_problems(absent["off"], run(B, "off", household_closure=False,
                                                               seed_base=OTHER_BASE), I.Q100_GIVEN, "syn")),
    "fewer": bool(I.seam_outs_problems(absent["off"], given[:-1], I.Q100_GIVEN, "syn")),
    "default_named": bool(I.seam_outs_problems(given, given, I.Q100_GIVEN, "syn"))}
out["identity_given"] = I.Q100_GIVEN == {NAME_HC: False, NAME_SB: 20261920}
out["exercised"] = {"paid_starts_off": sum(1 for x in absent["off"] if x["rec"]["pay_days"]),
                    "denied_starts_50": sum(1 for x in absent["denial_50"] if x["response"]["payouts_denied"] > 0),
                    "denied_starts_50_other": sum(1 for x in other["denial_50"]
                                                  if x["response"]["payouts_denied"] > 0)}
out["seconds"] = round(time.time() - t_all, 1)
print(json.dumps(out, default=str))
