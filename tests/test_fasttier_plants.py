"""Q-209's rework, after the red team's BLOCK (F2): the three planted records-only commits that a T0 selection let
through each fail a test of the full fast tier -- the tier every commit now runs, after its pre-flight.

On a throwaway clone of this repository (shared objects, its origin removed, results/ left out of the checkout), each
plant is staged and the test it breaks is run: green before the plant, red with it. The hook's stage is the full fast
tier on every commit (tests/test_fasttier_xdist.py and tests/test_fasttier_preflight.py hold the wiring), so a commit
carrying any of these plants is refused.

* P1 -- PARKING_LOT.md quoting family O's seed: `test_t11` (tests/test_family_o_runner.py) allows that block only in the
  family's files and the records it lists;
* P2 -- a new plan under docs/plans/ quoting the same seed: the same test;
* P3 -- a new `.py` under docs/reviews/ holding the breakeven reading's seed block: `test_the_seed_block_is_this_readings
  _alone` (tests/test_breakeven_fidelity_2.py) allows the block only in the files that declare it.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LIMIT = 900

T11 = "tests/test_family_o_runner.py::test_t11_the_seeds_appear_only_in_the_familys_files_and_the_records_that_quote_them"
SEED_BLOCK = "tests/test_breakeven_fidelity_2.py::test_the_seed_block_is_this_readings_alone"
#: The planted seeds are built by arithmetic, never written out: this file is tracked, and the very scans it plants for
#: (git grep over the repository) would find a literal seed here and fail the full fast tier -- as they did on the
#: rework's first commit (2026-11-22), the one these tests are about.
FAMILY_O_SEED = str(20261900 + 85)               # in family O's seed block (F-03)
BREAKEVEN_SEED = str(20262200 + 61)              # in the breakeven reading's seed block
PLANTS = {
    "P1": ("PARKING_LOT.md", "append", f"\n- re-run F-03 at seed {FAMILY_O_SEED}\n", T11),
    "P2": ("docs/plans/ZZ_plan.md", "new", f"# a plan\n\nThe opening family's seed {str(20261900 + 83)}.\n", T11),
    "P3": ("docs/reviews/scripts/redteam/rt_new.py", "new", f"SEED = {BREAKEVEN_SEED}\n", SEED_BLOCK),
}


def clean_env() -> dict:
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_") and not k.startswith("S2X_")}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "1", "GIT_TERMINAL_PROMPT": "0"})
    return env


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    p = subprocess.run(["git", "-c", "user.name=q209", "-c", "user.email=q209@example.invalid", *args], cwd=cwd,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=LIMIT,
                       env=clean_env())
    if check and p.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}: {p.stdout}{p.stderr}")
    return p


@pytest.fixture(scope="module")
def clone(tmp_path_factory):
    if shutil.which("git") is None:
        pytest.skip("git not found")
    common = Path(git(ROOT, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    sha = git(ROOT, "rev-parse", "HEAD").stdout.strip()
    c = tmp_path_factory.mktemp("q209plants") / "clone"
    git(c.parent, "clone", "-q", "--shared", "--no-checkout", str(common), str(c))
    git(c, "remote", "remove", "origin")
    git(c, "sparse-checkout", "set", "--no-cone", "/*", "!/results/")
    git(c, "checkout", "-q", "--detach", sha)
    return c


def _run(c: Path, nodeid: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-o", "addopts=", "-p", "no:cacheprovider", nodeid],
                          cwd=c, capture_output=True, text=True, timeout=LIMIT, env=clean_env())


@pytest.mark.parametrize("plant", sorted(PLANTS))
def test_each_planted_records_commit_fails_a_test_of_the_full_tier(clone, plant):
    rel, how, text, nodeid = PLANTS[plant]
    git(clone, "reset", "-q", "--hard")
    git(clone, "clean", "-fdq")
    before = _run(clone, nodeid)
    assert before.returncode == 0, f"{nodeid} is not green before {plant}: {before.stdout[-2000:]}"
    path = clone / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if how == "append":
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(text)
    else:
        path.write_text(text, encoding="utf-8", newline="\n")
    git(clone, "add", rel)                                     # staged, as the commit would hold it
    try:
        after = _run(clone, nodeid)
        assert after.returncode == 1 and "1 failed" in after.stdout, f"{plant} did not fail {nodeid}: {after.stdout}"
    finally:
        git(clone, "reset", "-q", "--hard")
        git(clone, "clean", "-fdq")
