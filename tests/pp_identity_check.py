"""T-11's checks of `identity/pp_identity.py` (RD-02 13.3; Q-105), run by `tests/test_pp_identity.py` in a process of
its own (the script puts the vendored tree on `sys.path`). Nothing is read and no engine runs: the script's input
builders are replaced by tripwires, so a check that got past the guard would trip them.

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
I._build_gate_inputs = trip
I._build_u1_job = trip
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
                 ("the start rows", lambda: I.u1_problems("p14", 4, 1))):
    if refused(fn) != "tripped":
        problems.append(f"{what} at the reference did not reach its builder (the tripwire is not where it should be)")

print(json.dumps({"problems": problems, "options": opts}))
