"""Q-04: the trace check (`extended/trace.py`, `scripts/trace_check.py`). An empty registry is NOT CHECKED (exit 2),
never a vacuous pass; a registered number recomputed from its result file (through `read_result`, the manifest
checked first) is found in its document, and a drifted document or an edited result fails.

Child processes: the trace imports the vendored engine (CLAUDE.md).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_empty_registry_is_not_checked():
    # Q-27 registers the report pages' numbers, so the registry is emptied here explicitly: the assertion is the same
    # (an empty registry is NOT CHECKED, exit 2, never a pass), no longer resting on nothing having been registered
    code = f"""
        import sys
        sys.path.insert(0, {str(ROOT)!r})
        import importlib.util
        import extended.trace as T
        spec = importlib.util.spec_from_file_location("s2x_trace_check", {str(ROOT / 'scripts' / 'trace_check.py')!r})
        TC = importlib.util.module_from_spec(spec); spec.loader.exec_module(TC)
        T.REGISTRY[:] = []
        raise SystemExit(TC.main([]))
    """
    r = subprocess.run([sys.executable, "-c", textwrap.dedent(code)], cwd=ROOT, capture_output=True, text=True,
                       timeout=300)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "NOT CHECKED" in r.stdout
    assert "OK" not in r.stdout.replace("NOT CHECKED", "")


def test_registry_traces_the_report_pages():
    # Q-27: every number of every registered report page (extended/trace.py REPORT_PAGES) recomputes from its file
    # and is found on the committed page -- the check the brief names as done
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "trace_check.py")], cwd=ROOT, capture_output=True,
                       text=True, timeout=600)
    assert r.returncode == 0, r.stdout[-4000:] + r.stderr[-2000:]
    first = r.stdout.splitlines()[0]
    assert first.startswith("trace check: "), first
    ok, total = (int(x) for x in first.split()[2].split("/"))
    assert ok == total > 100, first
    assert "demo_stage2_u1: " in r.stdout


def test_registered_number_found_drifted_and_edited(tmp_path):
    code = f"""
        import json, sys
        from pathlib import Path
        sys.path.insert(0, {str(ROOT)!r})
        sys.path.insert(0, {str(ROOT / 'scripts')!r})
        import pandas as pd
        import extended.results as X
        import extended.trace as T
        import importlib.util
        spec = importlib.util.spec_from_file_location("s2x_trace_check", {str(ROOT / 'scripts' / 'trace_check.py')!r})
        TC = importlib.util.module_from_spec(spec); spec.loader.exec_module(TC)
        base = Path({str(tmp_path)!r})
        res = base / "results"
        X.write_result(pd.DataFrame({{"x": [1.5, 2.25]}}), "t_trace", script="t", seed=1, parameters={{}},
                       results_dir=res)
        (base / "docs").mkdir()
        (base / "docs" / "good.md").write_text("the mean is 1.88 here\\n", encoding="utf-8")
        (base / "docs" / "stale.md").write_text("the mean is 1.80 here\\n", encoding="utf-8")
        mean = T.TracedNumber("mean x", "t_trace.csv", lambda df: df["x"].mean(), ("docs/good.md",), decimals=2)
        stale = T.TracedNumber("mean x", "t_trace.csv", lambda df: df["x"].mean(), ("docs/stale.md",), decimals=2)
        good = T.run([mean], results_dir=res, repo_root=base)
        bad = T.run([stale], results_dir=res, repo_root=base)
        T.REGISTRY[:] = [mean]
        T.RESULTS_DIR, T.ROOT = res, base
        exit_good = TC.main([])
        T.REGISTRY[:] = [stale]
        exit_bad = TC.main([])
        (res / "t_trace.csv").write_text("x\\n9\\n", encoding="utf-8")
        T.REGISTRY[:] = [mean]
        exit_edited = TC.main([])
        print(json.dumps({{"good": good.passed, "good_n": good.checked, "bad": bad.passed,
                          "exit_good": exit_good, "exit_bad": exit_bad, "exit_edited": exit_edited}}))
    """
    r = subprocess.run([sys.executable, "-c", textwrap.dedent(code)], cwd=ROOT, capture_output=True, text=True,
                       timeout=300, env={k: v for k, v in os.environ.items() if k != "S2X_CLEAN_RUN"})
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    out = json.loads(r.stdout.strip().splitlines()[-1])
    assert out["good"] and out["good_n"] == 1
    assert not out["bad"]
    assert out["exit_good"] == 0 and out["exit_bad"] == 1 and out["exit_edited"] == 1
