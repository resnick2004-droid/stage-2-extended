"""F-03's T-5 and T-13 (synthetic part), run in a process of its own (`tests/test_family_o_wait.py`): the waiting class
(`extended/opening_wait.py`) through the vendored router and lockstep loop on a synthetic campaign -- no bar, no atlas,
no result file of this family.

    python tests/fo_wait_synthetic.py <repository root>             # prints one JSON line last

**The campaign:** Q-70's walked synthetic trades under P-14's own table, sizing, strict rule and `able` routing
(`identity/place_records_identity.py`'s `p14_table_inputs`, `extended/synthetic_bars.py`'s bars, seed 20262070), laid
out as U1 lays a campaign out for the replay (`customer_slices.Campaign`, `user_journey._single_jobs`), replayed
through Q-17's adapter (`extended/user_beside.py`) -- so the router, the sizing's `can_take` and the lockstep loop are
the vendored ones. The offers are named by `opening_population.offer_id(date, entry bar)`.

**What it reports** (the test asserts each): with the state always on, and with W = 0, every start's output is the
vendored class's bit for bit (apart from the class's name); the wait switched off with the recorder on equals the
unrecorded vendored replay; with the state never on every opening falls at or after the sixth live session; with the
state a placebo set every in-wait opening's offer is in the set and every declined offer was out of it and declined
inside the wait (the wrapper's own count); the wait's sessions are `FundedAccount.days` 0 to W - 1 at routing; the
fallback flags and the joins by offer id on a hand-checked start; the forfeiture composed over the class (wait off)
equals the forfeiture over the vendored class; the Focused Trader models refused; the class pickles to a worker's
task and the task, run in a fresh interpreter, gives the same outputs and records; the wrapper cannot be collected
while its account lives; the gate (`extended.gate.run_gate`) with the state always on equals the gate without a
class. Seeds: the fixture's (20262070) and the placebo set's `[SEED_TESTS, 500, ...]` (section 16's test block).
"""
from __future__ import annotations

import gc
import json
import pickle
import subprocess
import sys
import tempfile
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

import a3_brk30_cb20 as C  # noqa: E402
import customer_slices as cs  # noqa: E402
import place_records_identity as PRI  # noqa: E402
import user_beside_identity as I  # noqa: E402
import user_journey as UJ  # noqa: E402

from extended import gate as XG  # noqa: E402
from extended import opening_population as OP  # noqa: E402
from extended import opening_wait as OW  # noqa: E402
from extended import place_records as PR  # noqa: E402
from extended import user_beside as B  # noqa: E402
from propedge.campaign.lockstep import FundedAccount  # noqa: E402

SEED = 20261988
W = 5
t_all = time.time()
out: dict[str, Any] = {}

P = PRI.p14_table_inputs()
camp = cs.Campaign(name="fo_syn", blocks=P["blocks"], dates=P["days"], kw=P["kw"])
jobs = UJ._single_jobs(camp, P["kw"]["risk_policy"], C.BUDGET)
t = P["t"].copy()
t["fo_offer"] = [OP.offer_id(d, int(e)) for d, e in zip(t["date"].astype(str), t["entry_t"])]
ids = PR.block_offer_ids(t, P["days"], P["blocks"], "fo_offer")
n = len(P["blocks"])
STARTS = UJ.start_choice(n, 6)
ARM = "point"
job = jobs[ARM]
blocks = job["blocks"]
out["starts"] = STARTS
out["sessions"] = n
out["able"] = bool(job["args"]["draws"].get("route_able", False))
out["sized"] = job["args"]["draws"].get("sizing") is not None


def run(resp: str = "off", cls=None, recorder=None, starts=STARTS, j=job):
    kw = {}
    if cls is not None:
        kw["funded_account_cls"] = cls
    if recorder is not None:
        kw["recorder"] = recorder
    return B.run_starts("fo_syn", ARM, B.BY_NAME[resp], j, starts, 1, **kw)


def flags(fn) -> list[np.ndarray]:
    return [np.array([bool(fn(h, k)) for k in range(len(b))], dtype=bool) for h, b in enumerate(blocks)]


base = run()
base_rec = OW.FamilyRecorder(offer_ids=ids)
run(recorder=base_rec)

# -- the state always on, and W = 0: the vendored class bit for bit
always = OW.waiting_class(OW.WaitSpec.for_blocks("always", blocks, None, W=W))
got = run(cls=always)
out["always_on"] = I.class_outs_problems(base, got, always, "always on")
rng = np.random.default_rng([SEED, 500, 0])
placebo = [rng.random(len(b)) < 1.0 / 3.0 for b in blocks]
w0 = OW.waiting_class(OW.WaitSpec.for_blocks("placebo_w0", blocks, placebo, W=0))
out["w0"] = I.class_outs_problems(base, run(cls=w0), w0, "W = 0")

# -- the wait off with the recorder on: the unrecorded vendored replay's rows
rec_w0 = OW.FamilyRecorder(offer_ids=ids)
got = run(cls=w0, recorder=rec_w0)
out["w0_recorded"] = I.class_outs_problems(base, got, w0, "W = 0, recorded")
out["w0_records_same"] = rec_w0.trades().equals(base_rec.trades()) and rec_w0.accounts().equals(base_rec.accounts())
out["w0_declined"] = int(len(rec_w0.declined("fo_syn", ARM, "off")))
out["w0_problems"] = rec_w0.problems()[:3]

# -- the state never on
never = OW.waiting_class(OW.WaitSpec.for_blocks("never", blocks, [np.zeros(len(b), bool) for b in blocks], W=W))
rec_never = OW.FamilyRecorder(offer_ids=ids)
run(cls=never, recorder=rec_never)
op_never = OW.openings(rec_never, "fo_syn", ARM, "off", W=W)
dec_never = rec_never.declined("fo_syn", ARM, "off")
out["never"] = {"openings": int(len(op_never)), "min_session": int(op_never["opening_session"].min()),
                "all_fallback": bool(op_never["fallback"].all()),
                "at_sixth": int((op_never["opening_session"] == W).sum()), "declined": int(len(dec_never)),
                "declined_inside_wait": bool((dec_never["wait_session"] < W).all()),
                "problems": rec_never.problems()[:3]}
base_open = OW.openings(base_rec, "fo_syn", ARM, "off", W=W)
out["base_openings"] = int(len(base_open))
out["base_min_session"] = int(base_open["opening_session"].min())

# -- the state the placebo set
spec_p = OW.WaitSpec.for_blocks("placebo", blocks, placebo, W=W)
cls_p = OW.waiting_class(spec_p)
rec_p = OW.FamilyRecorder(offer_ids=ids)
outs_p = run(cls=cls_p, recorder=rec_p)
in_set = {x: bool(f) for h in range(n) for x, f in zip(ids[h], placebo[h])}
op_p = OW.openings(rec_p, "fo_syn", ARM, "off", W=W)
dec_p = rec_p.declined("fo_syn", ARM, "off")
off_set = [not placebo[int(s) + int(h)][int(j)] for s, h, j in zip(dec_p["start_day"], dec_p["historical_day"],
                                                                     dec_p["trade_index"])]
out["placebo"] = {"openings": int(len(op_p)), "in_wait": int(op_p["in_wait"].sum()),
                  "fallback": int(op_p["fallback"].sum()), "declined": int(len(dec_p)),
                  "declined_off_set": bool(all(off_set)), "problems": OW.wait_problems(op_p, dec_p, in_set, W),
                  "record_problems": rec_p.problems()[:3],
                  "wait_sessions": sorted(set(int(x) for x in dec_p["wait_session"])),
                  "in_wait_sessions": sorted(set(int(x) for x in op_p.loc[op_p["in_wait"], "opening_session"])),
                  "fallback_min": int(op_p.loc[op_p["fallback"], "opening_session"].min()) if op_p["fallback"].any()
                  else None,
                  "differs_from_base": I.first_difference(base, outs_p) is not None}

# -- the off-by-one: a probe of FundedAccount.days at each routing of a waiting account
SEEN: list[tuple[int, int, int]] = []


class Probe(OW.GateWrapper):
    pass


orig_can_take = OW.GateWrapper.can_take


def probing(self, h, j, balance, floor):
    a = self._account()
    if a is not None and int(a.trades) == 0:
        SEEN.append((int(a.index), int(a.days), int(h)))
    return orig_can_take(self, h, j, balance, floor)


OW.GateWrapper.can_take = probing
try:
    rec_probe = OW.FamilyRecorder(offer_ids=ids)
    run(cls=cls_p, recorder=rec_probe, starts=[STARTS[2]])
finally:
    OW.GateWrapper.can_take = orig_can_take
opp = OW.openings(rec_probe, "fo_syn", ARM, "off", W=W)
acct = rec_probe.accounts("fo_syn", ARM, "off")
first_day = dict(zip(acct["account"].astype(int), acct["activation_day"].astype(int) + 1))
days_ok = all(int(d) == int(h) + 1 - first_day[a] for a, d, h in SEEN)      # days = sessions since its first session
out["off_by_one"] = {"asked": len(SEEN), "days_is_relative_session": bool(days_ok),
                     "openings_agree": bool((opp["opening_session"] == opp["rel_day"]).all())}

# -- a hand-checked start: its openings and declined offers in full
HAND = STARTS[2]
ho = op_p[op_p["start_day"] == HAND]
hd = dec_p[dec_p["start_day"] == HAND]
tt = t.set_index("fo_offer")
out["hand"] = {"start": int(HAND),
               "openings": [[int(r.account), int(r.opening_session), bool(r.fallback), str(r.offer),
                             bool(in_set[str(r.offer)]), str(tt.loc[str(r.offer), "date"])] for r in ho.itertuples()],
               "declined": [[int(r.account), int(r.historical_day), int(r.trade_index), int(r.wait_session),
                             str(ids[HAND + int(r.historical_day)][int(r.trade_index)])] for r in hd.itertuples()]}
hand_ok = []
for r in ho.itertuples():
    mine = hd[hd["account"] == r.account]
    hand_ok.append(bool((mine["wait_session"] <= r.opening_session).all()) and
                   (r.fallback or bool(in_set[str(r.offer)])) and
                   (not r.fallback or int(r.opening_session) >= W) and
                   str(tt.loc[str(r.offer), "date"]) == str(r.date))
out["hand_consistent"] = bool(all(hand_ok)) and len(hand_ok) > 0

# -- the forfeiture composed over the class, the wait off; the Focused Trader models refused
f_base = run("forfeit_25")
f_cls = run("forfeit_25", cls=w0)
out["forfeit"] = I.class_outs_problems(f_base, f_cls, w0, "forfeit_25, wait off")
try:
    run("ftp_slowdown_purchases_10", cls=always)
    out["ftp_refused"] = False
except ValueError:
    out["ftp_refused"] = True

# -- pickling: the class to a worker's task, run in a fresh interpreter
out["pickles"] = pickle.loads(pickle.dumps(cls_p)) is cls_p
fc = B.forfeit_class(cls_p)
try:
    pickle.dumps(fc)
    out["forfeit_class_pickles"] = True
except pickle.PicklingError:
    out["forfeit_class_pickles"] = False
red = OW.FamilyRecorder(offer_ids=ids).reducer("fo_syn", ARM, B.BY_NAME["off"], job)
task = ("fo_syn", ARM, "off", job["blocks"], job["dates"], job["args"], [HAND], 1, cls_p, red)
here_outs, here_recs = B._task(task)
with tempfile.TemporaryDirectory() as d:
    tp, op_ = Path(d) / "task.pkl", Path(d) / "out.pkl"
    tp.write_bytes(pickle.dumps(task))
    code = ("import sys, pickle; sys.path.insert(0, sys.argv[3]); from extended import use_vendored_stage2; "
            "use_vendored_stage2(); import propedge.contract.adapter, customer_journey; from extended import user_beside as B; "
            "t = pickle.loads(open(sys.argv[1], 'rb').read()); open(sys.argv[2], 'wb').write(pickle.dumps(B._task(t)))")
    r = subprocess.run([sys.executable, "-c", code, str(tp), str(op_), str(REPO)], capture_output=True, text=True,
                       timeout=600)
    ok = r.returncode == 0
    if ok:
        w_outs, w_recs = pickle.loads(op_.read_bytes())
        out["worker_outs_same"] = I.first_difference(here_outs, w_outs) is None
        out["worker_declined_same"] = [x["declined"] for x in here_recs] == [x["declined"] for x in w_recs]
        out["worker_declined"] = int(sum(len(x["declined"]) for x in w_recs))
    else:
        out["worker_outs_same"] = False
        out["worker_error"] = (r.stdout + r.stderr)[-1500:]

# -- the wrapper is held by its account, not collectable while the account lives
from propedge.campaign.shared_days import SharedDayDraws  # noqa: E402

sd = SharedDayDraws({0: list(blocks)}, seed=job["args"]["seed"], replay=True, **job["args"]["draws"])
d0 = sd.draw_for("funded", 0, 0)
acct0 = cls_p(index=0, activation_day=0, draw=d0, horizon_days=100, floor_start=-2000.0)
del d0
gc.collect()
reg = sd.router._draws.get(("funded", 0))
out["held"] = reg is not None and reg is acct0._fo_gate and isinstance(reg, OW.GateWrapper)
del acct0, reg
gc.collect()
out["released_with_account"] = sd.router._draws.get(("funded", 0)) is None

# -- refusals: a router without able routing
try:
    sd2 = SharedDayDraws({0: list(blocks)}, seed=job["args"]["seed"], replay=True,
                         **{**job["args"]["draws"], "route_able": False})
    cls_p(index=0, activation_day=0, draw=sd2.draw_for("funded", 0, 0), horizon_days=100, floor_start=-2000.0)
    out["refuses_without_able"] = False
except OW.GateOpen:
    out["refuses_without_able"] = True

# -- the gate: the state always on through extended.gate.run_gate equals the gate without a class
kw14, b14 = P["kw"], P["blocks"]
h0, s0 = PRI._p14_hook(P["fcfg"], "fo_syn")
rows0, ok0 = XG.run_gate(b14, path_hook=h0, **kw14)
always_ix = OW.waiting_class(OW.WaitSpec.for_index("always_gate", None, W=W))
h1, s1 = PRI._p14_hook(P["fcfg"], "fo_syn")
rows1, ok1 = XG.run_gate(b14, path_hook=h1, funded_account_cls=always_ix, **kw14)
r1 = rows1.drop(columns=["funded_account_cls"])
out["gate_always_on"] = {"rows_same": bool(rows0.reset_index(drop=True).equals(r1.reset_index(drop=True))),
                         "flag_same": bool(ok0 == ok1), "names_class": "funded_account_cls" in rows1.columns,
                         "sink": PRI.GI.sink_problems(s0, s1, "gate") if hasattr(PRI, "GI") else []}
gate_never = OW.waiting_class(OW.WaitSpec.for_index("never_gate", [np.zeros(len(b), bool) for b in b14], W=W, blocks=b14))
h2, s2 = PRI._p14_hook(P["fcfg"], "fo_syn")
rows2, _ = XG.run_gate(b14, path_hook=h2, funded_account_cls=gate_never, **kw14)
out["gate_never_differs"] = not rows0.reset_index(drop=True).equals(
    rows2.drop(columns=["funded_account_cls"]).reset_index(drop=True))

out["seconds"] = round(time.time() - t_all, 1)
print(json.dumps(out, default=str))
