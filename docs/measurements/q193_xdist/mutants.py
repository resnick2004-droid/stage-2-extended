"""Q-193 mutation check: each mutant applied in place, tests/test_fasttier_xdist.py run, the file restored.
Run from anywhere: `python docs/measurements/q193_xdist/mutants.py` (never while another run reads these files).
A mutant is killed when the test file fails. Run from the worktree root."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]                # the tree: docs/measurements/q193_xdist/ is three down
RUNNER = "scripts/fasttier_xdist.py"
PLUGIN = "extended/fasttier_report.py"
HOOK = "scripts/pre-commit"
TESTS = "tests/test_fasttier_xdist.py"
LOCK = "scripts/fasttier_lock.py"

MUTANTS = [
    ("M01 floor->ceil", RUNNER, "n = math.floor((available - reserve_gb) / per_worker_gb)",
     "n = math.ceil((available - reserve_gb) / per_worker_gb)"),
    ("M02 no max clamp", RUNNER, "top = max(1, int(max_workers))", "top = 99"),
    ("M03 unknown memory -> max", RUNNER,
     "if available is None or not isinstance(available, (int, float)) or not math.isfinite(available):\n        return 1",
     "if available is None or not isinstance(available, (int, float)) or not math.isfinite(available):\n        return max_workers"),
    ("M04 parallel count unchecked", RUNNER,
     '        v.problems += check_same_tests(expected, parallel, "the parallel run")\n    if v.problems:',
     '        pass\n    if v.problems:'),
    ("M05 still failing passes", RUNNER, "if v.still_failing or rerun.get(\"exitstatus\") != 0:", "if False:"),
    ("M06 no rerun needed", RUNNER,
     '        v.problems.append(f"{len(v.rerun)} test(s) failed in parallel and no serial rerun report was written")',
     '        return Verdict(code=EXIT_PASS, line="fast tier: 1 passed")'),
    ("M07 lengths only", RUNNER, "if len(got) != len(expected) or set(got) != want:", "if len(got) != len(expected):"),
    ("M08 dist load", RUNNER, 'DIST = "loadfile"', 'DIST = "load"'),
    ("M09 rerun everything", RUNNER,
     '(work / "rerun.txt").write_text("".join(f"{nid}\\n" for nid in failed)',
     '(work / "rerun.txt").write_text("".join(f"{nid}\\n" for nid in expected)'),
    ("M10 defects unnamed", RUNNER, "passed only serially, to fix: {_names(v.defects)}", "passed only serially"),
    ("M11 env 0 ignored", RUNNER, "    return max(1, v)\n", "    return v if v >= 1 else None\n"),
    ("M12 teardown ignored", PLUGIN, 'for when in ("setup", "teardown"):', 'for when in ("setup",):'),
    ("M13 xfail as failed", PLUGIN,
     '        if outcome == "skipped":\n            return "xfailed" if wasxfail else "skipped"',
     '        if outcome == "skipped":\n            return "failed" if wasxfail else "skipped"'),
    ("M14 any exit reruns", RUNNER, "    if status != 1:\n", "    if status not in (0, 1, 2, 3, 4, 5):\n"),
    ("M15 tab kept", HOOK, "| tr -d '\\r' | tr '\\t' ' ')", "| tr -d '\\r')"),
    ("M16 addopts kept", RUNNER, 'BASE = ("-m", "pytest", "-o", "addopts=", "-q")', 'BASE = ("-m", "pytest", "-q")'),
    ("M17 a line after the verdict", RUNNER, "    print(v.line, flush=True)", "    print(v.line, flush=True)\n    print('1 passed', flush=True)"),
    ("M18 workers always agree", PLUGIN, '"workers_agree": all(v == lists[0] for v in lists) if lists else None,',
     '"workers_agree": True,'),
    ("M19 duplicates ignored", RUNNER, "    if len(set(expected)) != len(expected):", "    if False:"),
    ("M20 rerun under a broken exit", RUNNER, "        if failed and parallel.get(\"exitstatus\") == 1:",
     "        if failed:"),
    ("M21 serial fallback branch dropped", HOOK, 'if [ -f scripts/fasttier_xdist.py ]; then', 'if true; then'),
    ("M22 no-xdist ignored", RUNNER, '    if not has_xdist:\n        n, why = 1, "pytest-xdist is not installed"',
     '    if False:\n        n, why = 1, "pytest-xdist is not installed"'),
    ("M23 clean removes all", RUNNER, "    for name in WORK_FILES:", "    for name in [p.name for p in work.iterdir()]:"),
    ("M24 nonzero-exit clean pass", RUNNER, "        if status != 0:\n            v.problems.append(f\"the parallel run exited",
     "        if False:\n            v.problems.append(f\"the parallel run exited"),
    ("M25 no kill-on-close job", RUNNER, "    if not join_kill_on_close_job():\n", "    if not False:\n"),
    ("M26 force ignored", RUNNER, "    elif force is not None:\n", "    elif False:\n"),
    ("M27 beside ignored", RUNNER, "    beside_gb = sum(L.slot_reserve_gb(w) for w in beside)",
     "    beside_gb = 0.0"),
    ("M28 own slot counted", RUNNER, 'if rec is None or rec.get("token") == mine or', 'if rec is None or'),
    ("M29 stale counted", RUNNER, ' or L.stale_reason(sp, raw) is not None:', ':'),
    ("M30 admission flat", LOCK, "sum(slot_reserve_gb(workers_of(_parse(r)), reserve)",
     "sum(slot_reserve_gb(1, reserve)"),
    ("M31 reserve ignores workers", LOCK, "    return base + max(0, int(workers) - 1) * per_worker_gb",
     "    return base"),
    ("M32 n not recorded", RUNNER, "    if record is not None:\n        record(n)\n",
     "    if record is not None:\n        pass\n"),
    ("M33 bool workers", LOCK, "isinstance(w, int) and not isinstance(w, bool) and w >= 1",
     "isinstance(w, int) and w >= 1"),
    ("M34 record any slot", LOCK, '        if rec is None or rec.get("token") != token:\n            continue\n        rec["workers"]',
     '        if rec is None:\n            continue\n        rec["workers"]'),
    ("M35 children see the real lock", TESTS, '"MKL_NUM_THREADS": "1", "LOCALAPPDATA": own_localappdata()})',
     '"MKL_NUM_THREADS": "1"})'),
]


def main() -> int:
    survivors = []
    for name, rel, old, new in MUTANTS:
        p = ROOT / rel
        orig = p.read_bytes()
        text = orig.decode("utf-8")
        if text.count(old) != 1:
            print(f"{name}: pattern found {text.count(old)} times -- NOT APPLIED")
            survivors.append(name + " (not applied)")
            continue
        try:
            p.write_bytes(text.replace(old, new).encode("utf-8"))
            r = subprocess.run([sys.executable, "-m", "pytest", "-o", "addopts=", "-q", "-x", "-p", "no:cacheprovider",
                                "tests/test_fasttier_xdist.py"], cwd=ROOT, capture_output=True, text=True,
                               timeout=900)
            killed = r.returncode != 0
            tail = [ln for ln in r.stdout.splitlines() if "passed" in ln or "failed" in ln][-1:]
            print(f"{name}: {'killed' if killed else 'SURVIVED'} {tail}", flush=True)
            if not killed:
                survivors.append(name)
        finally:
            p.write_bytes(orig)
    print(f"{len(MUTANTS) - len(survivors)} of {len(MUTANTS)} killed; survivors: {survivors}")
    return 1 if survivors else 0


if __name__ == "__main__":
    raise SystemExit(main())
