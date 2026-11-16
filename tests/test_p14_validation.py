"""Q-18: Stage 2 D-663's validation readings on P-14 (`scripts/p14_validation.py`, `extended/v1_adapter.py`).

* fast, synthetic (`tests/v1_adapter_checks.py`, in a process of its own: it imports the vendored tree): each adapter is
  the vendored V1 part it adapts when given D-663's seeds, and moves only with its own; D-583's slippage part runs the
  declared arms on the stressed trades and reads the family's turning level; the runner's row picker, its file and
  variant ledger, and its refusals.
* fast, pure: the seeds fixed for Q-18 (20261950-20261952) appear in no other code, configuration or result manifest.
* slow (the bars, the engine at 4 paths): `--check` -- every identity (P-14's trades and bounds against its registered
  file; the registered call's first 4 paths, the verdict and the 0.05 bound, against its per-path file) and every
  part's smoke.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "vendor" / "stage2" / "data"
CHECKS = ("engine_hook", "b1_era", "b1_pooled", "c1", "slip", "rows", "writing", "refusals")
SEEDS = ("20261950", "20261951", "20261952")
#: where Q-18's seeds may appear in code, configuration and manifests: its runner, its tests, its own result
SEED_HOMES = {"scripts/p14_validation.py", "tests/test_p14_validation.py", "tests/v1_adapter_checks.py",
              "results/p14_validation.csv.manifest.json", "results/variants.jsonl"}


def test_the_adapters_are_the_vendored_parts_on_synthetic_data():
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "v1_adapter_checks.py")], capture_output=True, text=True,
                       timeout=900)
    assert r.returncode == 0, r.stdout[-4000:] + r.stderr[-4000:]
    for name in CHECKS:
        assert f"HOLDS: {name}" in r.stdout, r.stdout


def test_q18s_seeds_are_used_nowhere_else():
    """Each seed Q-18 fixed is fresh (the brief's range, Stage 2 D-663's practice): no other code, configuration or
    result manifest of this repository or the vendored tree holds it. Documents may cite it."""
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    pat = re.compile("|".join(SEEDS))
    found = []
    for rel in out:
        if not re.search(r"\.(py|ya?ml|toml|json|jsonl|cfg|ini)$", rel) or rel in SEED_HOMES:
            continue
        try:
            text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if pat.search(text):
            found.append(rel)
    assert not found, found


@pytest.mark.slow
def test_check_reproduces_p14_and_smokes_every_part():
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "p14_validation.py"), "--check"], capture_output=True,
                       text=True, timeout=3600)
    assert r.returncode == 0, r.stdout[-4000:] + r.stderr[-4000:]
    assert "REFUSED" not in r.stdout, r.stdout[-4000:]
    for line in ("identity HOLDS: P14's registered call -- the first 4 paths equal results/a3_brk30_cb20_gate_paths.csv",
                 "identity HOLDS: P14's call at the 0.05 bound -- the first 4 paths",
                 "identity HOLDS: P-14's trades and bounds are results/a3_brk30_cb20_gate.csv's",
                 "--check done: parts ['A1', 'B2', 'A0', 'B1', 'C1', 'SLIP']"):
        assert line in r.stdout, (line, r.stdout[-4000:])
