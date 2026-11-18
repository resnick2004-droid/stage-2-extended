"""T-11 (`prereg/RD-03_contract_levers.md` 14.3): `identity/cl_identity.py` and `identity/cl_fit_identity.py` run the
reference only -- every option a constant at its off value, no argument naming a lever, a cell, a price or an option,
and with any option flipped the guard refuses before the first start, path or solve. Prints one JSON line.

    python tests/cl_identity_check.py <repository root>
"""
from __future__ import annotations

import ast
import dataclasses
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
for _p in (str(ROOT), str(ROOT / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

from extended import levers_path as LP  # noqa: E402

problems: list[str] = []
FORBIDDEN = re.compile(r"lever|cell|price|react|expir|house|naf|inventory|banking|option|subscription|activation|"
                       r"count_react|edge|fee", re.I)


def load(rel: str):
    spec = importlib.util.spec_from_file_location(Path(rel).stem, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def options_of(m) -> list[str]:
    return [a.dest for a in m.parser()._actions if a.dest != "help"]


def refuses(fn) -> bool:
    try:
        fn()
    except RuntimeError:
        return True
    return False


m = load("identity/cl_identity.py")
if m.CELL != "ref" or not m.LEVERS.off:
    problems.append("cl_identity: its constants are not the reference")
bad = [o for o in options_of(m) if FORBIDDEN.search(o)]
if bad:
    problems.append(f"cl_identity: arguments naming a lever, a cell, a price or an option: {bad}")
m.guard()
fee = 1.0
flipped = [LP.Levers(reactivations=1, reactivation_fee=fee, reactivation_window_days=1, reactivation_window_sessions=1),
           LP.Levers(house="stop"), LP.Levers(max_concurrent_combines=1), LP.Levers(subscription=fee),
           LP.Levers(lift_joint_cap=True), LP.Levers(stop_buying_when_queued=False),
           LP.Levers(house="zero", expiry="30", expiry_days=1, expiry_sessions=1)]
for lv in flipped:
    if not refuses(lambda: m.guard(lv)):
        problems.append(f"cl_identity: the guard does not refuse {lv}")
calls = {"gate_problems", "u1_problems"}
src = (ROOT / "identity" / "cl_identity.py").read_text(encoding="utf-8")
tree = ast.parse(src)
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in calls:
        first = node.body[1] if isinstance(node.body[0], ast.Expr) else node.body[0]
        if not (isinstance(first, ast.Expr) and isinstance(first.value, ast.Call)
                and getattr(first.value.func, "id", "") == "guard"):
            problems.append(f"cl_identity: {node.name} does not call guard() first")
# with the module's constant flipped, the guard refuses before anything runs
orig = m.LEVERS
m.LEVERS = dataclasses.replace(orig, house="stop")
if not refuses(m.guard) or not refuses(lambda: m.gate_problems("p14", 1, 1)) or \
        not refuses(lambda: m.u1_problems("p14", 1, 1)):
    problems.append("cl_identity: with the constant flipped, a comparison runs")
m.LEVERS = orig

fit = ROOT / "identity" / "cl_fit_identity.py"
fit_problems: list[str] = []
if fit.is_file():
    f = load("identity/cl_fit_identity.py")
    bad = [o for o in options_of(f) if FORBIDDEN.search(o)]
    if bad:
        fit_problems.append(f"cl_fit_identity: arguments naming a lever, a cell, a price or an option: {bad}")
    f.guard()
    for k, v in f.FLIPS.items():
        if not refuses(lambda: f.guard(**{k: v})):
            fit_problems.append(f"cl_fit_identity: the guard does not refuse {k}={v!r}")
else:
    fit_problems.append("identity/cl_fit_identity.py is not written (A-5 unbuilt)")

print(json.dumps({"problems": problems, "fit_problems": fit_problems}))
