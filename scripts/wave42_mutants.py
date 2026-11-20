"""Wave 4.2's mutation check (the red team's B-6, `docs/reviews/WAVE42_RULE_2026-11-20.md`): each mechanism of the
setting rule W42-R1 broken by one edit of `extended/wave42.py`, on a scratch copy, and `tests/test_wave42_rule.py` run
against it. A mutant is **killed** when the tests fail on it. The unmutated control must pass, and every mutant must be
killed; the script exits 1 otherwise.

    python scripts/wave42_mutants.py --scratch <a new folder outside the repository>

Light: no bar, no result, no engine; each run takes seconds. The scratch folder holds copies of the files the tests
read (the rule, its tests, its declaration, the three-way note and its arithmetic, CHARTER.md, CLAUDE.md and the two
modules the rule imports), never a junction or a data file; nothing in the repository is written.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = "extended/wave42.py"
FILES = ("extended/__init__.py", "extended/family_stats.py", "extended/lift_bound.py", TARGET,
         "tests/test_wave42_rule.py", "docs/plans/WAVE42_SETTING_RULE.md", "docs/plans/THREE_WAY_TEST_design.md",
         "docs/plans/scripts/three_way/three_way_arith.py", "CHARTER.md", "CLAUDE.md")

#: (name, the text replaced, its replacement): each text occurs exactly once in the rule's module
MUTANTS: tuple[tuple[str, str, str], ...] = (
    # the red team's nineteen, as they apply to the corrected rule
    ("z ignores the direction", "    return u if dim.direction > 0 else 1.0 - u", "    return u"),
    ("best's sigma without sqrt(2)",
     "s = math.sqrt(2.0) * math.sqrt(float(np.mean(np.var(unit[best], axis=1, ddof=1))))",
     "s = math.sqrt(float(np.mean(np.var(unit[best], axis=1, ddof=1))))"),
    ("q_factor's strata not nested",
     "count = int(test_starts[h]) - (int(test_starts[hs[i + 1]]) if i + 1 < len(hs) else 0)",
     "count = int(test_starts[h])"),
    ("P_B, run out and not paid at the median budget, not B*",
     "**bankroll_states(vals[b], Bstar)}", "**bankroll_states(vals[b], budgets[0])}"),
    ("headroom se_test without its sqrt(|E_h| / (J n_h)) scaling",
     "se = sd[bb] * math.sqrt(n_search[L.horizon] / (J * int(test_starts[L.horizon])))", "se = sd[bb]"),
    ("sigma of unit[b] in place of unit[best] - unit[b]",
     "np.var(unit[best] - unit[b], axis=1, ddof=1)", "np.var(unit[b], axis=1, ddof=1)"),
    ("every pair's delta equal to delta*",
     "deltas = {b: delta + (C[best] - C[b]) for b in BASELINES}", "deltas = {b: delta for b in BASELINES}"),
    ("sessions left without the start session",
     "sl = np.asarray([len(cal) - pos[str(d)] for d in ref.starts])",
     "sl = np.asarray([len(cal) - pos[str(d)] - 1 for d in ref.starts])"),
    ("not_paid_within_B ignores B",
     '"not_paid_within_B": 1.0 - (paid & (x6 <= B)).astype(float)}', '"not_paid_within_B": 1.0 - paid.astype(float)}'),
    ("P_B with the bankroll stop removed (P_B = P)",
     'ahead = sum(((v[f"net_month_{m}"] > AHEAD_TOL) & (v[f"peak_month_{m}"] <= B)).astype(float) for m in (1, 2, 3))',
     'ahead = sum((v[f"net_month_{m}"] > AHEAD_TOL).astype(float) for m in (1, 2, 3))'),
    ("P_B's stop at < B", '(v[f"peak_month_{m}"] <= B)', '(v[f"peak_month_{m}"] < B)'),
    ("run out at >= B", '"run_out": (x6 > B).astype(float)', '"run_out": (x6 >= B).astype(float)'),
    ("day caps not clamped to W + 1",
     "lo, hi = max(a, ql - CAP_MARGIN * span), min(b, qh + CAP_MARGIN * span)",
     "lo, hi = max(a, ql - CAP_MARGIN * span), qh + CAP_MARGIN * span"),
    ("a floor's headroom with the ceiling's sign",
     "need = M[bb] + zp * se if ceil_ else M[bb] - zp * se", "need = M[bb] + zp * se"),
    ("pairing checks seeds only",
     "if tuple(b.starts) != tuple(ref.starts) or tuple(b.seeds) != tuple(ref.seeds):",
     "if tuple(b.seeds) != tuple(ref.seeds):"),
    ("test-start counts' monotonicity refusal removed",
     "if any(c < 1 for c in counts) or any(b > a for a, b in zip(counts, counts[1:])):",
     "if any(c < 1 for c in counts):"),
    ("fee-source refusal removed", "    if fee_source != FEE_SOURCE:\n", "    if False:\n"),
    ("J_needed off by one", "        Jn = lo_j\n", "        Jn = lo_j + 1\n"),
    # B-1, B-2, B-8: the binding, the calendar, the held-out guard
    ("the manifest's file sha256 not checked", 'if man["sha256"] != h4.result_sha256:', "if False:"),
    ("the content digest not checked", 'if readings_digest(readings) != man["readings_sha256"]:', "if False:"),
    ("the start days not checked against the manifest",
     'if [str(d) for d in ref.starts] != [str(d) for d in man["starts"]]:', "if False:"),
    ("the seeds not checked against the manifest",
     'if [int(s) for s in ref.seeds] != [int(s) for s in man["seeds"]]:', "if False:"),
    ("the optional measures not checked against the manifest",
     'if present != set(man["optional_measures"]):', "if False:"),
    ("the reading tag not checked", "if b.reading != READING:", "if False:"),
    ("a second application not refused", 'if rid.startswith("W42-"):', "if False:"),
    ("the minimum seed count not enforced for a resolution", "resolvable = nJ >= H4_MIN_SEEDS", "resolvable = True"),
    ("a start off the calendar not refused", "    if off:\n", "    if False:\n"),
    ("the calendar's ends not checked",
     "if not cal or cal != sorted(set(cal)) or cal[0] != SEARCH_FIRST or cal[-1] != SEARCH_LAST:", "if not cal:"),
    ("the calendar's sha256 not checked", 'if man["calendar_sha256"] != cal_sha:', "if False:"),
    ("the manifest's W not checked", 'if int(man["W"]) != W:', "if False:"),
    ("the test counts' source not checked",
     "if any(not (isinstance(src.get(k), str) and src[k].strip()) for k in TEST_STARTS_SOURCE_KEYS) \\",
     "if False \\"),
    ("the block guard removed",
     "        if b.block != BLOCK:\n            raise _refuse(f\"{b.name!r} is tagged block",
     "        if False:\n            raise _refuse(f\"{b.name!r} is tagged block"),
    ("the search-years guard removed",
     "if not (SEARCH_FIRST <= str(d) <= SEARCH_LAST) or str(d) >= HELD_OUT_FIRST:", "if False:"),
    # B-3: J
    ("the headroom at H4's seed count, not the declared J",
     "se = sd[bb] * math.sqrt(n_search[L.horizon] / (J * int(test_starts[L.horizon])))",
     "se = sd[bb] * math.sqrt(n_search[L.horizon] / (nJ * int(test_starts[L.horizon])))"),
    ("Q at H4's seed count, not the declared J", "Q = q_factor(w, hk, test_starts, J)",
     "Q = q_factor(w, hk, test_starts, nJ)"),
    # B-4, B-5, m-1: the composite
    ("cost scores an unpassed unit by its spending",
     "z[b][d.name] = np.where(ok[b], _z(d, per[b][d.key], lo, hi), 0.0)", "z[b][d.name] = _z(d, per[b][d.key], lo, hi)"),
    ("cost's caps from every unit, not the passed ones",
     "pooled = np.concatenate([per[b][d.key][r][ok[b][r]] for b in BASELINES])",
     "pooled = np.concatenate([per[b][d.key][r].ravel() for b in BASELINES])"),
    ("a redundancy drop reinstated (cost dropped at rho >= 0.9 with speed)",
     'kept = ["money"] if form == "fallback" else names',
     'kept = ["money"] if form == "fallback" else [n for n in names if not (n == "cost" and '
     '(rho.get("speed|cost") or 0) >= 0.9)]'),
    ("the fallback when any other dimension is constant",
     'form = "fallback" if all(rec["constant"] for rec in dims_out[1:]) else "composite"',
     'form = "fallback" if any(rec["constant"] for rec in dims_out[1:]) else "composite"'),
    ("rank-order-centroid weights in place of equal weights",
     "    w = equal_weights(kept)\n",
     "    w = {k: sum(1.0 / j for j in range(i, len(kept) + 1)) / len(kept) for i, k in enumerate(kept, 1)}\n"),
    # m-2, m-3
    ("resolution at z = 1, not 2", '"resolved": bool(resolvable and g > RESOLVE_Z * se)',
     '"resolved": bool(resolvable and g > 1.0 * se)'),
    ("delta* not capped from above", "delta = min(DELTA_MAX, max(DELTA_MIN, raw))", "delta = max(DELTA_MIN, raw)"),
    ("delta*'s floor removed", "delta = min(DELTA_MAX, max(DELTA_MIN, raw))", "delta = min(DELTA_MAX, raw)"),
    ("the headroom's z per limit, not joint", "zp = limit_z(len(present))", "zp = limit_z(1)"),
    ("a days limit at W + 1 not flagged on its range",
     'top = {"share": 1.0, "days": W + 1.0}.get(L.kind, math.inf)', 'top = {"share": 1.0}.get(L.kind, math.inf)'),
)


def _copy(scratch: Path) -> None:
    for f in FILES:
        (scratch / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / f, scratch / f)


def _run(scratch: Path, timeout: int) -> tuple[bool, float, str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
           "MKL_NUM_THREADS": "1"}
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-o", "addopts=", "-p", "no:cacheprovider",
                        "tests/test_wave42_rule.py"], cwd=scratch, env=env, capture_output=True, text=True,
                       timeout=timeout)
    tail = (p.stdout.strip().splitlines() or [""])[-1]
    return p.returncode == 0, time.monotonic() - t0, tail


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scratch", required=True, help="a new, empty folder outside the repository")
    ap.add_argument("--timeout", type=int, default=600, help="seconds a run may take")
    a = ap.parse_args(argv)
    scratch = Path(a.scratch).resolve()
    if scratch == ROOT or ROOT in scratch.parents:
        raise SystemExit("the scratch folder must be outside the repository")
    if scratch.exists() and any(scratch.iterdir()):
        raise SystemExit("the scratch folder must be new or empty")
    scratch.mkdir(parents=True, exist_ok=True)
    _copy(scratch)
    clean = (ROOT / TARGET).read_text(encoding="utf-8")
    for name, old, _ in MUTANTS:
        if clean.count(old) != 1:
            raise SystemExit(f"mutant {name!r}: its text occurs {clean.count(old)} times in {TARGET}, not once")
    ok, secs, tail = _run(scratch, a.timeout)
    print(f"control (unmutated): {'passes' if ok else 'FAILS'} in {secs:.1f} s  [{tail}]")
    survived = []
    for i, (name, old, new) in enumerate(MUTANTS, 1):
        (scratch / TARGET).write_text(clean.replace(old, new), encoding="utf-8", newline="\n")
        passed, secs, tail = _run(scratch, a.timeout)
        print(f"{i:2d}. {'SURVIVED' if passed else 'killed  '}  {name}  ({secs:.1f} s)  [{tail}]")
        if passed:
            survived.append(name)
    (scratch / TARGET).write_text(clean, encoding="utf-8", newline="\n")
    print(f"{len(MUTANTS) - len(survived)} of {len(MUTANTS)} mutants killed; control "
          f"{'passes' if ok else 'FAILS'}")
    return 0 if ok and not survived else 1


if __name__ == "__main__":
    sys.exit(main())
