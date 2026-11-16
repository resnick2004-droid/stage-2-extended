"""Q-76's synthetic check (`tests/test_user_beside_class.py` runs it in a process of its own: the vendored tree goes on
its `sys.path`): Q-17's adapter (`extended/user_beside.py`) with its declared funded-account class keyword
`funded_account_cls`, on a deterministic synthetic campaign through the vendored engine -- no bar, no atlas, no
generator (every value is a function of the day's and the trade's index; the shared-day seed is
`user_beside.SEED_BLOCK[1]`, as `identity/user_beside_identity.py --synthetic` uses it, and a replay draws nothing with
it; the denial ladder's coins come from the adapter's own start seeds).

    python tests/q76_synthetic.py <repository root>             # prints one JSON line last

What it reports (the test asserts each):

* **absent = before, bit for bit**: the adapter as it was before Q-76 (`git show c7ec122:extended/user_beside.py`, its
  text pinned by sha256) and the adapter now give the same per-start outputs (a canonical form: every float by its
  hex, every type by name, every key in order) for all 19 responses on five starts; the same tasks to the pool; the
  same `response_args` and `base_problems`; the same default forfeiture class;
* **a pass-through class** (the gate's `PassThroughFundedAccount`; and the vendored `FundedAccount` itself, given):
  every output equal to the absent run's apart from one added last key, `funded_account_cls`, naming the class;
  `class_parameters` names it, and is empty when absent;
* **a probe with a documented effect** (`NeverPaysFundedAccount`, never eligible for a Standard-path payout): with the
  responses off no start is paid or requests a payout while the absent run pays; the first pass and the first funding
  are the absent run's on every start; under 50 % forfeiture nothing is denied or forfeited while the absent run
  forfeits;
* **the forfeiture composed over a given class**: a subclass of it with the forfeiture's household rule, cached, the
  default class untouched; refused over a class with a household rule of its own;
* **refusals**, each before any start runs: not a `FundedAccount` subclass (five kinds); a class that cannot pickle at
  two workers (accepted at one, as the gate accepts it); a Focused Trader response with a class other than the vendored
  `FundedAccount` -- the engine's own rule, shown by the engine refusing it too; a path already carrying
  `funded_account_cls` (with the keyword and without);
* **the class reaches a worker**: a given task pickles back to the same class object and its outputs are the same;
* **the identity's comparison** (`identity/user_beside_identity.py`'s `class_outs_problems`): holds on the
  pass-through's outputs, refuses the probe's, a start not named and a start named wrongly; and the canonical form
  tells one float's last bit, -0.0 from 0.0 and an int from a float.
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
from extended import user_beside as B  # noqa: E402
from propedge.campaign.lockstep import CombineAccount, ConductModel, FocusedTraderModel, FundedAccount  # noqa: E402
from propedge.campaign.payout_method import payout_method_terms  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.contract.adapter import rules_from_ledger  # noqa: E402
from propedge.contract.rules import load_rules  # noqa: E402
from propedge.outcomes.distribution import DayBlock  # noqa: E402

#: the adapter before Q-76: master at c7ec122 (the file's text last changed at f87ffa1); the sha256 of its LF text
BASE_COMMIT = "c7ec122"
BASE_SHA256 = "bd48c6ea9108e87d66e95e59eaf0a5a3d2861a00ada0202b2a8723b06b82f7be"
N_DAYS = 160
#: the starts read: 14 and 77 forfeit a pending payout (77 at 10, 25 and 50 %), 21 makes the exact-length runs of
#: every response, the last has no pass
STARTS = [0, 5, 14, 21, 40, 77, N_DAYS - 3]


class NeverPaysFundedAccount(FundedAccount):
    """The probe (as `identity/gate_identity.py`'s): never eligible for a Standard-path payout, so with the responses
    off no account is ever paid."""

    def _standard_eligible(self, rules: Any) -> bool:
        return False


class OwnHouseholdFundedAccount(FundedAccount):
    """A class with a household rule of its own (count-only by default), as another firm's would declare one."""

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
    blocks.append(DayBlock(pnl=pnl, risked=np.full(k, 500.0), exit_reasons=tuple("target" if w else "stop" for w in win),
                           entry_t=et, exit_t=et + 30.0))
rules = rules_from_ledger()
proto = Protocol(name="q76_synthetic", combine_rr=2.0, combine_risk=500.0, funded_rr=2.0, funded_risk=500.0,
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
    mod = types.ModuleType("user_beside_before")
    mod.__file__ = f"<{BASE_COMMIT}:extended/user_beside.py>"
    sys.modules[mod.__name__] = mod
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod, sha


OLD, sha = before_module()
out["base_sha_ok"] = sha == BASE_SHA256
out["base_had_no_keyword"] = "funded_account_cls" not in inspect.signature(OLD.run_starts).parameters


class Pool:
    """`customer_journey._pool_run` recorded: the tasks each call hands it, and whether it was reached."""

    def __init__(self):
        self.calls: list[list[tuple]] = []
        self.real = CJ._pool_run

    def __call__(self, tasks, fn, workers, what):
        self.calls.append(list(tasks))
        return self.real(tasks, fn, workers, what)


POOL = Pool()
CJ._pool_run = POOL


def run(mod, resp_name: str, **kw) -> list[dict]:
    return mod.run_starts("syn", "point", mod.BY_NAME[resp_name], job, STARTS, 1, **kw)


def canon(x):
    return I.canonical(x)


def diff(a, b) -> str | None:
    return I.first_difference(a, b)


def strip(outs: list[dict]) -> list[dict]:
    return [{k: v for k, v in o.items() if k != "funded_account_cls"} for o in outs]


# -- absent = before, bit for bit: every response
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
out["absent_named"] = sorted(r for r, o in absent.items() if any("funded_account_cls" in x for x in o))


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
with_cls = {**args, "path": {**args["path"], "funded_account_cls": FundedAccount}}
probe_args = [args, with_cls, {**args, "draws": {**args["draws"], "flip": object()}},
              {**args, "path": {**args["path"], "conduct": ConductModel(rtp=True, enforcement_p=0.0)}}]
out["base_problems_same"] = [OLD.base_problems(a) == B.base_problems(a) for a in probe_args]
out["base_problems_refuses_cls"] = bool(B.base_problems(with_cls))
out["forfeit_default_same"] = cls_view(B.forfeit_class()) == cls_view(OLD.forfeit_class()) and \
    B.forfeit_class() is B.forfeit_class() and B.forfeit_class(None) is B.forfeit_class() and \
    B.forfeit_class().__bases__ == (FundedAccount,)

# -- a pass-through class, and the vendored FundedAccount given: equal apart from naming
PT = XG.PassThroughFundedAccount
out["pt_name"] = B.class_name(PT)
out["class_parameters"] = [B.class_parameters(None), B.class_parameters(PT)]
non_ftp = [r.name for r in B.RESPONSES if r.kind != "ftp"]
pt_diff, pt_named, fa_diff, fa_named = {}, {}, {}, {}
for name in non_ftp:
    got = run(B, name, funded_account_cls=PT)
    pt_named[name] = all(list(x)[-1] == "funded_account_cls" and x["funded_account_cls"] == B.class_name(PT)
                         for x in got) and len(got) == len(STARTS)
    pt_diff[name] = diff(absent[name], strip(got))
for name in ("off", "denial_50", "forfeit_25", "rtp", "ftp_slowdown_purchases_10", "ftp_corrective_lost_3"):
    got = run(B, name, funded_account_cls=FundedAccount)
    fa_named[name] = all(x["funded_account_cls"] == "propedge.campaign.lockstep.FundedAccount" for x in got)
    fa_diff[name] = diff(absent[name], strip(got))
out["pt_diff"], out["pt_named"], out["fa_diff"], out["fa_named"] = pt_diff, pt_named, fa_diff, fa_named
out["exercised"] = {"paid_starts_off": sum(1 for x in absent["off"] if x["rec"]["pay_days"]),
                    "denied_starts_50": sum(1 for x in absent["denial_50"] if x["response"]["payouts_denied"] > 0),
                    "forfeit_starts_50": sum(1 for x in absent["forfeit_50"]
                                             if np.isfinite(x["response"]["forfeit_day"])),
                    "forfeited_payouts_50": float(np.nansum([x["response"]["payouts_forfeited"]
                                                             for x in absent["forfeit_50"]])),
                    "rtp_placed": sum(1 for x in absent["rtp"] if np.isfinite(x["response"]["rtp_placed_day"]))}

# -- the probe: its documented effect
probe = run(B, "off", funded_account_cls=NeverPaysFundedAccount)
out["probe"] = {
    "named": all(x["funded_account_cls"] == B.class_name(NeverPaysFundedAccount) for x in probe),
    "no_payout": all(not x["rec"]["pay_days"] and x["response"]["payouts_requested"] == 0 for x in probe),
    "absent_pays": any(x["rec"]["pay_days"] for x in absent["off"]),
    "first_pass_same": canon([x["rec"]["first_pass"] for x in probe]) == canon([x["rec"]["first_pass"]
                                                                                 for x in absent["off"]]),
    "first_funded_same": canon([x["rec"]["first_funded"] for x in probe]) == canon([x["rec"]["first_funded"]
                                                                                     for x in absent["off"]]),
    "some_funded": any(x["rec"]["funded_days"] for x in probe),
    "differs": diff(absent["off"], strip(probe)) is not None}
pf = run(B, "forfeit_50", funded_account_cls=NeverPaysFundedAccount)
out["probe_forfeit"] = {"none_denied": all(x["response"]["payouts_denied"] == 0 for x in pf),
                        "none_forfeited": all(not np.isfinite(x["response"]["forfeit_day"]) for x in pf),
                        "absent_forfeits": any(np.isfinite(x["response"]["forfeit_day"]) for x in absent["forfeit_50"])}

# -- the forfeiture composed over a class
fpt, fnp = B.forfeit_class(PT), B.forfeit_class(NeverPaysFundedAccount)
out["forfeit_composed"] = {
    "subclass": issubclass(fpt, PT) and issubclass(fnp, NeverPaysFundedAccount) and fpt.__bases__ == (PT,),
    "rule": fpt.HOUSEHOLD_CLOSES_AT_LIVE is True and fpt.closes_household is False,
    "cached": B.forfeit_class(PT) is fpt and fpt is not B.forfeit_class() and fpt is not fnp,
    "default_untouched": B.forfeit_class().__bases__ == (FundedAccount,),
    "path": (lambda p: p["funded_account_cls"] is fpt and p["household_closure"] is True)(
        B.response_args(args, B.BY_NAME["forfeit_10"], funded_account_cls=PT)["path"]),
    "path_off": (lambda p: p["funded_account_cls"] is PT and "household_closure" not in p)(
        B.response_args(args, B.BY_NAME["off"], funded_account_cls=PT)["path"])}


def refused(call, exc: type) -> bool:
    n = len(POOL.calls)
    try:
        call()
    except exc:
        return len(POOL.calls) == n                 # refused before the pool was reached
    except Exception:  # noqa: BLE001
        return False
    return False


def local_class() -> type:
    class LocalFundedAccount(FundedAccount):
        pass
    return LocalFundedAccount


LOCAL = local_class()
bad = {"dict": dict, "an instance": FundedAccount.__new__(FundedAccount), "CombineAccount": CombineAccount,
       "a name": "FundedAccount", "an int": 1}
out["refused_bad_class"] = {k: refused(lambda v=v: run(B, "off", funded_account_cls=v), TypeError)
                            for k, v in bad.items()}
out["refused_bad_class_args"] = {k: refused(lambda v=v: B.response_args(args, B.BY_NAME["off"], funded_account_cls=v),
                                            TypeError) for k, v in bad.items()}
out["refused_local_two_workers"] = refused(
    lambda: B.run_starts("syn", "point", B.BY_NAME["off"], job, STARTS, 2, funded_account_cls=LOCAL), TypeError)
loc = run(B, "off", funded_account_cls=LOCAL)
out["local_one_worker_runs"] = diff(absent["off"], strip(loc)) is None
out["refused_ftp"] = {r.name: refused(lambda r=r: run(B, r.name, funded_account_cls=PT), ValueError)
                      for r in B.RESPONSES if r.kind == "ftp"}
out["refused_ftp_args"] = refused(lambda: B.response_args(args, B.BY_NAME["ftp_corrective_lost_3"],
                                                          funded_account_cls=PT), ValueError)
try:                                                # the engine's own rule: its Focused Trader Program is Topstep's
    p = {**args["path"], "focused_trader": FocusedTraderModel(path="corrective", window_days=21, funded_lost=3),
         "funded_account_cls": PT}
    B.replay(blocks[:40], {**args, "path": p}, B.start_seed(0))
    out["engine_refuses_ftp_subclass"] = False
except ValueError as exc:
    out["engine_refuses_ftp_subclass"] = "Focused Trader Program is Topstep's" in str(exc)
out["refused_forfeit_own_household"] = {
    r.name: refused(lambda r=r: run(B, r.name, funded_account_cls=OwnHouseholdFundedAccount), ValueError)
    for r in B.RESPONSES if r.kind == "forfeit"}
out["own_household_off_runs"] = len(run(B, "off", funded_account_cls=OwnHouseholdFundedAccount)) == len(STARTS)
job_with = {**job, "args": with_cls}
out["refused_path_carrying"] = {
    "run_starts_with_keyword": refused(lambda: B.run_starts("syn", "point", B.BY_NAME["off"], job_with, STARTS, 1,
                                                            funded_account_cls=PT), ValueError),
    "response_args_with_keyword": refused(lambda: B.response_args(with_cls, B.BY_NAME["off"], funded_account_cls=PT),
                                          ValueError),
    "response_args_without": refused(lambda: B.response_args(with_cls, B.BY_NAME["off"]), ValueError)}
try:                                                # without the keyword: refused inside the task, as before Q-76
    B.run_starts("syn", "point", B.BY_NAME["off"], job_with, STARTS, 1)
    out["refused_path_carrying"]["run_starts_without"] = False
except ValueError as exc:
    out["refused_path_carrying"]["run_starts_without"] = "already carry 'funded_account_cls'" in str(exc)

# -- the class reaches a worker: a given task pickles back to the same class, and gives the same outputs
POOL.calls.clear()
run(B, "denial_25", funded_account_cls=NeverPaysFundedAccount)
(task,) = POOL.calls[-1]
back = pickle.loads(pickle.dumps(task))
out["task_given"] = {"length": len(task), "last_is_class": task[-1] is NeverPaysFundedAccount,
                     "pickles_back": back[-1] is NeverPaysFundedAccount,
                     "same_outputs": diff(B._task(task), B._task(back)) is None}

# -- the signature
out["signature"] = {f: inspect.signature(getattr(B, f)).parameters["funded_account_cls"].default is None
                    for f in ("run_starts", "response_args")}
out["signature"]["forfeit_class"] = inspect.signature(B.forfeit_class).parameters["base"].default is None

# -- the identity's comparison
out["identity_compare"] = {
    "pass_through": I.class_outs_problems(absent["off"], run(B, "off", funded_account_cls=PT), PT, "syn"),
    "probe": bool(I.class_outs_problems(absent["off"], probe, NeverPaysFundedAccount, "syn")),
    "not_named": bool(I.class_outs_problems(absent["off"], absent["off"], PT, "syn")),
    "named_wrong": bool(I.class_outs_problems(absent["off"], run(B, "off", funded_account_cls=FundedAccount), PT,
                                              "syn")),
    "fewer": bool(I.class_outs_problems(absent["off"], run(B, "off", funded_account_cls=PT)[:-1], PT, "syn"))}
x = 0.1
out["canonical"] = {"last_bit": I.canonical([x]) != I.canonical([float(np.nextafter(x, 1.0))]),
                    "signed_zero": I.canonical(-0.0) != I.canonical(0.0),
                    "int_float": I.canonical({"a": 1}) != I.canonical({"a": 1.0}),
                    "nan_nan": I.canonical(float("nan")) == I.canonical(float("nan")),
                    "key_order": I.canonical({"a": 1, "b": 2}) != I.canonical({"b": 2, "a": 1}),
                    "found": I.first_difference({"a": [1.0, 2.0]}, {"a": [1.0, 2.5]}) is not None
                    and I.first_difference({"a": [1.0, 2.0]}, {"a": [1.0, 2.0]}) is None}
out["seconds"] = round(time.time() - t_all, 1)
print(json.dumps(out, default=str))
