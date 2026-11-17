"""F-03's index-mode placebo gate test (the build read's m3, owed before floor (iii) and run 2), run in a process of its
own (`tests/test_family_o_gate_placebo.py`): the waiting class in index mode through `extended.gate.run_gate` on a
synthetic campaign, read through Q-70's place recorder -- no bar, no atlas, no result file of this family.

    python tests/fo_gate_placebo_synthetic.py <repository root>      # prints one JSON line last

**The campaign:** Q-70's walked synthetic trades under P-14's own table, sizing, strict rule and `able` routing
(`identity/place_records_identity.py`'s `p14_table_inputs`, seed 20262070; 4 paths, 200 sessions), the gate's own call.
**The placebo set:** each trade of each gate block in the set with probability 1/3, `[SEED_TESTS, 1000, 0]` (section 16's
test block). **What it reports** (the test asserts each): the gate with the placebo class recorded through
`opening_wait.GateRecorder` (Q-70's `PlaceRecorder`, the family's reducer) gives the unrecorded gate's rows; on both arms
every in-wait opening is in the set, every fallback opening at or after the sixth live session, every declined offer
out of the set, declined inside the wait and no later than its account's opening, with both an in-wait opening and a
decline seen (`gate_wait_problems`); the state always on declines nothing and is the gate without a class; the
placebo gate differs from it; the chunked worker route (a pickle round trip of every task and result, in this process)
records the same declines and rows; the same recorded campaign held to the set shifted by one block fails the check
(it can see a misaligned lookup); a spec whose flags do not fit the gate's blocks is refused.
"""
from __future__ import annotations

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

import place_records_identity as PRI  # noqa: E402

from extended import gate as XG  # noqa: E402
from extended import opening_stats as ST  # noqa: E402
from extended import opening_wait as OW  # noqa: E402

W = OW.W_DECLARED
KEY = (ST.SEED_TESTS, 1000, 0)
t0 = time.time()
out: dict[str, Any] = {}

P = PRI.p14_table_inputs()
kw, blocks = P["kw"], P["blocks"]
rng = np.random.default_rng(list(KEY))
placebo = [rng.random(len(b)) < 1.0 / 3.0 for b in blocks]
out["trades"] = int(sum(len(b) for b in blocks))
out["in_set"] = int(sum(int(x.sum()) for x in placebo))
cls = OW.waiting_class(OW.WaitSpec.for_index("placebo_gate", placebo, W=W, blocks=blocks))


def gate(c=None, recorder=None, **extra):
    hook, _ = PRI._p14_hook(P["fcfg"], "fo_gate")
    k = dict(kw, **extra)
    if c is not None:
        k["funded_account_cls"] = c
    if recorder is not None:
        k["recorder"] = recorder
    rows, _ = XG.run_gate(blocks, path_hook=hook, **k)
    return rows.drop(columns=[x for x in ("funded_account_cls",) if x in rows.columns]).reset_index(drop=True)


plain = gate()
rows0 = gate(cls)
rec = OW.GateRecorder(dates=P["days"])
rows1 = gate(cls, rec)
out["recorded_rows_same"] = bool(rows0.equals(rows1))
out["differs_from_no_class"] = not plain.equals(rows0)
out["recorded"] = [list(k) for k in rec.recorded()]
out["arms"] = {}
for shift in sorted({k[0] for k in rec.recorded()}):
    probs, counts = OW.gate_wait_problems(rec, placebo, shift=shift, enforcement_p=0.0, W=W)
    dec = rec.declined(shift, 0.0)
    out["arms"][shift] = {"problems": probs[:5], **counts,
                          "wait_sessions": sorted({int(x) for x in dec["wait_session"]})}

# the state always on: nothing declined, the gate without a class
always = OW.waiting_class(OW.WaitSpec.for_index("always_gate_p", None, W=W))
rec_a = OW.GateRecorder(dates=P["days"])
rows_a = gate(always, rec_a)
out["always_rows_same"] = bool(plain.equals(rows_a))
out["always_declined"] = int(len(rec_a.declined()))
out["always_problems"] = rec_a.problems()[:3]


# the chunked worker route: every task and its result through a pickle round trip (what a path worker gets and sends)
class _Pool(PRI.InlinePool):
    submitted = 0

    def submit(self, fn, *args):
        _Pool.submitted += 1
        return super().submit(fn, *args)

    def shutdown(self, *a, **k):
        return None


from propedge.campaign import lockstep as _vl  # noqa: E402

_orig = _vl.path_pool
_vl.path_pool = lambda workers, **k_: (_Pool(), 2)
try:
    rec_w = OW.GateRecorder(dates=P["days"])
    rows_w = gate(cls, rec_w, workers=2)
finally:
    _vl.path_pool = _orig
out["worker_rows_same"] = bool(rows0.equals(rows_w))
out["worker_declined_same"] = bool(rec_w.declined().equals(rec.declined()))
out["worker_accounts_same"] = bool(rec_w.accounts().equals(rec.accounts()))
out["worker_tasks"] = int(_Pool.submitted)

# the check sees a misaligned lookup: the same recorded campaign held to the set shifted by one block
shifted = placebo[1:] + placebo[:1]
shifted = [np.resize(shifted[h], len(b)) if len(b) else np.zeros(0, bool) for h, b in enumerate(blocks)]
probs_s, _ = OW.gate_wait_problems(rec, shifted, shift="lower_bound", enforcement_p=0.0, W=W)
out["misaligned_caught"] = bool(probs_s)

# a spec whose flags do not fit the gate's blocks
try:
    OW.WaitSpec.for_index("short", placebo[:-1], W=W, blocks=blocks)
    out["misfit_refused"] = False
except ValueError:
    out["misfit_refused"] = True
out["seconds"] = round(time.time() - t0, 1)
print(json.dumps(out, default=str))
