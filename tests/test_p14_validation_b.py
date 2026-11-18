"""Q-18b: the parts of P-14's stress checks `results/p14_validation.csv` lacks (`scripts/p14_validation_b.py`,
`extended/p14_stress_b.py`; E-125's caveats, the lead's E-132).

* fast, synthetic (`tests/p14_validation_b_checks.py`, in a process of its own: it imports the vendored tree): the
  engine record is the vendored one plus the kept columns; the ruin figures; A2 is the vendored part but its seed;
  D-583's readings run the right calls and read the declared reading; the slice and file identities catch a change;
  the assumptions are read from the engine call; the runner's wiring and refusals.
* fast, pure: Q-18b's new seed appears in no other code, configuration or result manifest; the existing runner and its
  adapter are byte for byte the ones `results/p14_validation.csv` was made by, so that file stays reproducible.
* slow (the atlas, the engine at 4 paths): `--check` -- every identity at 4 paths and every part's smoke.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "vendor" / "stage2" / "data"
CHECKS = ("engine_run", "ruin", "a2_source", "a2_rows", "slip_b", "slices", "file_identity", "assumptions", "runner")
SEED = "20261953"
SEED_HOMES = {"scripts/p14_validation_b.py", "tests/p14_validation_b_checks.py", "tests/test_p14_validation_b.py",
              "results/p14_validation_b.csv.manifest.json", "results/variants.jsonl"}
#: the commit `results/p14_validation.csv` was made from (its manifest's `git_commit`; E-124)
MADE_AT = "f7eda0d02e31daea7bfb92847f4ad1203cef014e"
UNCHANGED = ("scripts/p14_validation.py", "extended/v1_adapter.py")


def test_the_parts_on_synthetic_data():
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "p14_validation_b_checks.py")], capture_output=True,
                       text=True, timeout=900)
    assert r.returncode == 0, r.stdout[-4000:] + r.stderr[-4000:]
    for name in CHECKS:
        assert f"HOLDS: {name}" in r.stdout, r.stdout


def test_q18bs_seed_is_used_nowhere_else():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    found = []
    for rel in out:
        if not re.search(r"\.(py|ya?ml|toml|json|jsonl|cfg|ini)$", rel) or rel in SEED_HOMES:
            continue
        try:
            text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if SEED in text:
            found.append(rel)
    assert not found, found


def test_the_existing_runner_is_the_one_its_file_was_made_by():
    """`results/p14_validation.csv` stays reproducible byte for byte: its runner and adapter are unchanged since the
    commit its manifest names (git's blob ids, line endings as committed)."""
    have = subprocess.run(["git", "cat-file", "-e", f"{MADE_AT}^{{commit}}"], cwd=ROOT, capture_output=True)
    if have.returncode != 0:
        pytest.skip(f"{MADE_AT[:7]} is not in this clone")
    for rel in UNCHANGED:
        then = subprocess.run(["git", "rev-parse", f"{MADE_AT}:{rel}"], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
        now = subprocess.run(["git", "rev-parse", f"HEAD:{rel}"], cwd=ROOT, capture_output=True, text=True,
                             check=True).stdout.strip()
        assert now == then, f"{rel} changed since {MADE_AT[:7]}"


@pytest.mark.slow
@pytest.mark.heavy         # Q-134: reads the real bars or atlas; the lock guard skips it while run.lock is held
def test_check_holds_every_identity_and_smokes_every_part():
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "p14_validation_b.py"), "--check"], capture_output=True,
                       text=True, timeout=3600)
    assert r.returncode == 0, r.stdout[-4000:] + r.stderr[-4000:]
    assert "REFUSED" not in r.stdout, r.stdout[-4000:]
    for line in ("provenance: commit ",
                 "identity HOLDS: P14's registered call -- the first 4 paths equal results/a3_brk30_cb20_gate_paths.csv",
                 "identity HOLDS: P14's call at the 0.05 bound -- the first 4 paths",
                 "identity HOLDS: the base arm's zero-edge twin's first 4 paths equal",
                 "--check done: parts ['SLIPB', 'A2', 'RERUN']"):
        assert line in r.stdout, (line, r.stdout[-4000:])
