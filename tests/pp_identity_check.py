"""T-11's checks of `identity/pp_identity.py` (RD-02 13.3; Q-105), run by `tests/test_pp_identity.py` in a process of
its own (the script puts the vendored tree on `sys.path`). Nothing is read and no engine runs: the script's one input
builder (`_real_inputs`, the reading's `RealInputs` since Q-105e's D2) is replaced by a tripwire, so a check that got
past the guard would trip it; and the duplicate gate builder the script once carried is gone.

    python tests/pp_identity_check.py <repository root>          # prints one JSON line last
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(sys.argv[1])
for _p in (str(REPO), str(REPO / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import dataclasses  # noqa: E402

import pp_identity as I  # noqa: E402

from extended import payout_policy as PP  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402

problems: list[str] = []
base = Protocol(name="t11", combine_rr=2.0, combine_risk=300.0, funded_rr=2.0, funded_risk=300.0)


class Tripped(Exception):
    pass


def trip(*a, **k):
    raise Tripped("an input was built, a start or a path was about to run")


def refused(fn) -> str:
    try:
        fn()
    except RuntimeError as exc:
        return "refused" if "REFUSED" in str(exc) else f"another error: {exc}"
    except Tripped:
        return "tripped"
    return "ran"


# (a) the constants are the reference's
if not (I.CELL == "ref" and (I.L1, I.L2) == ("elig", "max") and I.HELD_MODE == "declared"
        and I.FUNDED_CLASS is PP.REF_CLASS and PP.levers_off(I.FUNDED_CLASS, base)):
    problems.append(f"the constants are not ref's: {I.CELL}, {I.L1}, {I.L2}, {I.HELD_MODE}, {I.FUNDED_CLASS}")

# (b) no option names a policy, a lever or a payout field
words = ("policy", "lever", "cell", "lock", "half", "frac", "payout", "held", "class", "protocol", "minimal", "l1",
         "l2", "keep", "elig", "max", "rescue")
opts = [s for a in I.parser()._actions for s in a.option_strings]
named = [o for o in opts if any(w in o.lower() for w in words)]
if named:
    problems.append(f"the parser has options naming a policy, a lever or a payout field: {named}")

# (c) the guard refuses every flipped flag, and the reference passes
if hasattr(I, "_build_gate_inputs") or hasattr(I, "_build_u1_job"):
    problems.append("the identity still carries its own input builders (D2: every input through RealInputs)")
I._real_inputs = trip
if refused(I.guard) != "ran":
    problems.append("the guard refuses the reference policy")
if refused(lambda: I.guard(PP.REF_CLASS, base)) != "ran":
    problems.append("the guard refuses the reference policy's protocol")
flips = {"CELL": "lock", "L1": "lock", "L2": "half", "HELD_MODE": "minimal", "FUNDED_CLASS": PP.PPLock}
for name, value in flips.items():
    keep = getattr(I, name)
    setattr(I, name, value)
    try:
        for what, fn in (("the guard", I.guard), ("the gate paths", lambda: I.gate_problems("p14", 4, 1)),
                         ("the start rows", lambda: I.u1_problems("p14", 4, 1)),
                         ("the ladder rows", lambda: I.ladder_problems("p14", 4, 1)),
                         ("main", lambda: I.main(["--paths", "4", "--row", "E-001"]))):
            got = refused(fn)
            if got != "refused":
                problems.append(f"{name} = {value!r}: {what} {got}, not refused before the first start or path")
    finally:
        setattr(I, name, keep)
for cls in (PP.PPLock, PP.PPEligMinimal, PP.PPLockMinimal, PP.PayoutPolicyFundedAccount):
    if refused(lambda: I.guard(cls)) != "refused":
        problems.append(f"the guard passes {cls.__name__}")
if refused(lambda: I.guard(PP.REF_CLASS, dataclasses.replace(base, payout_frac=PP.half_fraction()))) != "refused":
    problems.append("the guard passes the half request's protocol")
# positive control: with the reference's constants, each comparison gets past the guard and reaches its builder
for what, fn in (("the gate paths", lambda: I.gate_problems("p14", 4, 1)),
                 ("the start rows", lambda: I.u1_problems("p14", 4, 1)),
                 ("the ladder rows", lambda: I.ladder_problems("p14", 4, 1))):
    if refused(fn) != "tripped":
        problems.append(f"{what} at the reference did not reach its builder (the tripwire is not where it should be)")

# (d) D2: every input through the reading's RealInputs -- the gate and its twin by gate_call(design, "ref", twin), the
# twin against the registered zero_edge_twin, U1's rows by jobs and identity_problems, and item 6 at ref through
# ladder_problems under each response beside -- with stand-ins for RealInputs, the gate, the comparator and the replay
# (nothing runs, nothing is read)
import pandas as pd  # noqa: E402
import zero_edge_decomposition as zd  # noqa: E402

from extended import gate as XG  # noqa: E402
from extended import pp_inputs as PI  # noqa: E402
from extended import user_beside as B  # noqa: E402
from propedge.reporting import results as VR  # noqa: E402

seen: dict[str, list] = {"gate_call": [], "run_gate": [], "pairs": [], "identity": [], "ladder": [], "starts": []}
job = {"blocks": [None] * 10, "args": {"draws": {"protocol": base}}}


class StubInputs:
    def gate_call(self, design, cell, twin):
        seen["gate_call"].append((design, cell, twin))
        return {"kw": {"blocks": [], "protocol": base, "horizon_days": 10}, "sink": [],
                "label": f"{design}_{cell}{'_twin' if twin else ''}"}

    def registered_paths_file(self, design):
        return "registered.csv"

    def jobs(self, design):
        return {"verdict": job, "point": job}

    def identity_problems(self, design, arm, outs):
        seen["identity"].append((design, arm))
        return []

    def ladder_problems(self, design, response, outs):
        seen["ladder"].append((design, response))
        return []


keep = (I._real_inputs, XG.run_gate, zd.path_problems, VR.read_result, B.run_starts)
I._real_inputs = lambda *a, **k: StubInputs()
XG.run_gate = lambda blocks, workers, funded_account_cls, counters, **kw: (
    seen["run_gate"].append(funded_account_cls), (pd.DataFrame(), True))[1]
zd.path_problems = lambda sink, ref, pairs, n: (seen["pairs"].append(list(pairs)), [])[1]
VR.read_result = lambda *a, **k: pd.DataFrame()
B.run_starts = lambda design, arm, resp, job_, chosen, workers, funded_account_cls=None, counters=None, **kw: (
    seen["starts"].append((arm, resp.name, funded_account_cls)), [])[1]
try:
    got = I.gate_problems("p14", 4, 1) + I.u1_problems("p14", 4, 1) + I.ladder_problems("p14", 4, 1)
    if got:
        problems.append(f"D2: the stand-ins gave problems {got[:3]}")
    if seen["gate_call"] != [("p14", "ref", False), ("p14", "ref", True)]:
        problems.append(f"D2: the gate calls are not RealInputs.gate_call at ref, gate then twin: {seen['gate_call']}")
    if seen["run_gate"] != [PP.REF_CLASS, PP.REF_CLASS]:
        problems.append(f"D2: the gate ran with {seen['run_gate']}, not the reference class twice")
    want = [[("p14_ref", s, "gate", s) for s in ("point", "lower_bound")],
            [("p14_ref_twin", s, "zero_edge_twin", s) for s in ("point", "lower_bound")]]
    if seen["pairs"] != want:
        problems.append(f"D2: the paths compared are not the registered gate and zero_edge_twin runs: {seen['pairs']}")
    if seen["identity"] != [("p14", "verdict"), ("p14", "point")]:
        problems.append(f"D2: U1's rows not compared by RealInputs.identity_problems on both arms: {seen['identity']}")
    if seen["ladder"] != [("p14", r) for r in PI.BESIDE]:
        problems.append(f"D2: item 6 at ref not through RealInputs.ladder_problems for every response: {seen['ladder']}")
    ladder_runs = [x for x in seen["starts"] if x[1] != "off"]
    if ladder_runs != [("verdict", r, PP.REF_CLASS) for r in PI.BESIDE]:
        problems.append(f"D2: the ladder's replays are not ref's on the verdict arm: {ladder_runs}")
finally:
    I._real_inputs, XG.run_gate, zd.path_problems, VR.read_result, B.run_starts = keep

print(json.dumps({"problems": problems, "options": opts}))
