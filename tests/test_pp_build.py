"""Q-105: RD-02's build (`prereg/RD-02_payout_policy.md` 13.1-13.3) -- the adapter `extended/payout_policy.py`, the
counters' channel (`extended/user_beside.py`, `extended/gate.py`, lines marked Q-105), the reading's horizons and
uncertainty `extended/pp_reading.py` -- held to the declared tests on synthetic inputs only:

* T-1, T-2, T-3, T-4, T-5, T-7 and T-10 run in `tests/pp_synthetic.py`, one section a process (the vendored engine on
  that process's `sys.path`), each a list of problems that must be empty; a check the memory guard did not let run at
  two workers is printed NOT CHECKED, never counted a pass;
* the channel absent: the replay adapter equals master's before Q-105 bit for bit on all 19 responses (`absent`);
* T-6's build form: `extended/pp_reading.py` gives what `tests/test_pp_draft.py`'s declaration-stage functions give,
  value for value, on the same inputs and the same draws;
* T-9: section 11's seeds appear in none of the build's files (each imports its seed from its one home), and 13.2's
  literal check -- no 2000, 125 or 0.5 among the adapter's numbers.

T-11 (`identity/pp_identity.py` runs the reference policy only) is `tests/test_pp_identity.py`; T-8 (the identities at
4 paths and 4 starts) is slow there.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
SYN = ROOT / "tests" / "pp_synthetic.py"
BUILD_FILES = ("extended/payout_policy.py", "extended/pp_reading.py", "identity/pp_identity.py", "tests/pp_synthetic.py",
               "tests/test_pp_build.py", "tests/test_pp_identity.py")


def _run(section: str, timeout: int = 300) -> dict:
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, str(SYN), str(ROOT), section], cwd=ROOT, capture_output=True, text=True,
                       timeout=timeout, env=env)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    assert r.returncode == 0 and lines, f"{section} did not run:\n{r.stdout[-2000:]}\n{r.stderr[-3000:]}"
    out = json.loads(lines[-1])
    for note in out.get("notes", []):
        print(note)
    return out


@pytest.mark.parametrize("section", ["t1", "t2", "t3", "t4", "t5", "t7", "t10r", "t10g", "absent"])
def test_section_holds(section):
    out = _run(section)
    assert out["n_problems"] == 0, "\n".join(out["problems"])


# ------------------------------------------------------------------------------------------------ T-6 (build form)


def _draft():
    spec = importlib.util.spec_from_file_location("test_pp_draft_ref", ROOT / "tests" / "test_pp_draft.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _reading():
    spec = importlib.util.spec_from_file_location("pp_reading_build", ROOT / "extended" / "pp_reading.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_t6_the_build_gives_the_declaration_stage_values():
    D, R = _draft(), _reading()
    g = np.random.default_rng([D.COVERAGE_SEED, D.T6_KEY, 500])
    for h in (21, 63, 252):
        for n in (0, 3 * h, 7 * h + 5, 11 * h):
            for rule in ("separated", "adjacent"):
                assert R.kept_windows(n, h, rule) == D.windows(n, h, rule)
    for n_w in (2, 3, 4, 5, 9, 13):
        m = g.normal(size=n_w)
        assert R.t_interval(m) == D.t_interval(m) and R.mdd(m) == D.mdd(m)
        b = g.normal(size=n_w)
        assert R.sign_count(m, b) == D.sign_count(m, b)
    for series in (np.zeros(5 * 63), np.r_[np.zeros(6 * 63), 1.0], np.r_[np.zeros(7 * 63), 1.0],
                   np.r_[g.normal(size=9 * 63)]):
        want = D.describe(series, 63)
        if want == "interval" and D.t_interval(R.window_means(series, 63)) is None:
            # 9.2 item 6's second sentence, which the declaration-stage helper leaves to `t_interval`: kept means all
            # equal print the sign count and no interval
            want = "no spread across the separated windows"
        assert R.describe(series, 63) == want
    cov = {"gauss": 0.90, "ahead": 0.87, "paired": 0.91, "lumpy_0.05_0.005": 0.4}
    assert R.label(cov) == D.label(cov) and R.label(dict(cov, ahead=0.89)) == D.label(dict(cov, ahead=0.89))
    # the coverage on the same draws: the build's code and the declaration's give the same number
    for kind, n_w, rule, case in (("gauss", 5, "adjacent", 1), ("gauss", 9, "separated", 102), ("ahead", 9, "separated",
                                                                                                    103)):
        want = D.coverage(kind, n_w, rule, case)
        got = R.coverage(kind, n_w, D.H, np.random.default_rng([D.COVERAGE_SEED, D.T6_KEY, case]), D.REPS, rule=rule)
        assert got["coverage"] == want, (kind, n_w, rule, got, want)
    lump = R.coverage("lumpy", 13, D.H, np.random.default_rng([D.COVERAGE_SEED, D.T6_KEY, 210]), D.REPS, p=0.05,
                      s=0.005)
    assert lump["coverage"] == D.coverage("lumpy", 13, "separated", 210, p=0.05, s=0.005)
    assert lump["coverage"] + lump["miss_above"] + lump["miss_below"] == pytest.approx(1.0)
    line = R.rare_line({"gauss": 0.9, "lumpy_a": 0.5, "persistent_b": 0.4}, {"lumpy_a": 0.4, "persistent_b": 0.55},
                       {"lumpy_a": 0.1, "persistent_b": 0.05})
    assert line == {"shape": "persistent_b", "coverage": 0.4, "miss_above": 0.55, "miss_below": 0.05}
    assert len(R.SHAPES) == 21 and [R.shape_name(*s) for s in R.SHAPES][:4] == ["gauss", "ahead", "paired",
                                                                                 "lumpy_0.05_0.0025"]


# ------------------------------------------------------------------------------------------------ T-9 and 13.2


def test_t9_section_11s_seeds_appear_in_none_of_the_build_files():
    pat = re.compile(rb"\b2026194[0-9]\b")
    for rel in BUILD_FILES:
        p = ROOT / rel
        if p.exists():
            assert not pat.search(p.read_bytes()), f"{rel} writes a seed of RD-02's block; import it from its home"


def test_13_2_no_rule_literal_in_the_adapter():
    tree = ast.parse((ROOT / "extended" / "payout_policy.py").read_text(encoding="utf-8"))
    bad = sorted({n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)
                  and isinstance(n.value, (int, float)) and not isinstance(n.value, bool)
                  and float(n.value) in (2000.0, 125.0, 0.5)})
    assert not bad, f"rule values written in the adapter: {bad} (13.2: read them from the ledger)"
