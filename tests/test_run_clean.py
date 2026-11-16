"""Q-04: `scripts/run_clean.py` -- a clean, detached checkout of a commit; the stores linked by junction; the command
run with the clean-run marker and its log beside the checkout; `--collect` bringing results home and refusing clashes
and overwrites; `--remove` unlinking the junctions first; the run lock taken and released around the command.

All on a temporary git repository with a dummy store (never the licensed data) and a temporary lock file.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_lock as RL  # noqa: E402
import worktrees as W  # noqa: E402


def _load():
    """This repository's run_clean.py by its path (the vendored tree has a run_clean.py too)."""
    spec = importlib.util.spec_from_file_location("s2x_run_clean", SCRIPTS / "run_clean.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RC = _load()


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "master")
    git(root, "config", "user.email", "t@example.invalid")
    git(root, "config", "user.name", "t")
    git(root, "config", "core.autocrlf", "false")
    (root / ".gitignore").write_text("vendor/stage2/data/bars/\nvendor/stage2/data/atlas/\n__pycache__/\n",
                                     encoding="utf-8")
    (root / "vendor" / "stage2" / "data").mkdir(parents=True)
    (root / "vendor" / "stage2" / "data" / "README.md").write_text("tracked\n", encoding="utf-8")
    (root / "results").mkdir()
    (root / "results" / "old.csv").write_text("a\n1\n", encoding="utf-8")
    (root / "code.txt").write_text("v1\n", encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "first")
    for s, f in (("bars", "bars.parquet"), ("atlas", "walks.parquet")):
        d = root / "vendor" / "stage2" / "data" / s
        d.mkdir()
        (d / f).write_text(f"store {s}\n", encoding="utf-8")
    assert git(root, "status", "--porcelain") == ""
    runs = tmp_path / "runs"
    monkeypatch.setattr(W, "ROOT", root)
    monkeypatch.setattr(RC, "RUNS", runs)
    monkeypatch.setattr(RL, "LOCK", tmp_path / "run.lock")
    monkeypatch.setattr(RL, "available_gb", lambda: 8.0)
    yield root
    if runs.is_dir():                     # never leave a junction behind for the temp cleaner to walk
        for wt in runs.iterdir():
            for s in W.STORES:
                W.unlink(wt, s)


def code(body: str) -> list[str]:
    return [sys.executable, "-c", body]


WRITE_MARKER = ("import os, pathlib; p = pathlib.Path('results'); p.mkdir(exist_ok=True); "
                "(p / 'out.csv').write_text(os.environ.get('S2X_CLEAN_RUN', 'none') + chr(10)); "
                "print('ran', os.environ.get('OMP_NUM_THREADS'))")


def test_create_links_the_stores_and_is_clean(repo):
    wt = RC.create("c1", "HEAD")
    assert wt == RC.RUNS / "c1"
    assert git(wt, "rev-parse", "HEAD") == git(repo, "rev-parse", "HEAD")
    assert git(wt, "status", "--porcelain", "--untracked-files=all") == ""
    for s in W.STORES:
        assert W.is_link(wt / s), s
    assert (wt / "vendor/stage2/data/bars/bars.parquet").read_text(encoding="utf-8") == "store bars\n"
    with pytest.raises(SystemExit):
        RC.create("c1", "HEAD")           # exists: --remove it first


def test_dirty_tree_refused_at_head_but_a_named_commit_runs(repo):
    sha = git(repo, "rev-parse", "HEAD")
    (repo / "code.txt").write_text("v2 uncommitted\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        RC.create("c2", "HEAD")
    assert not (RC.RUNS / "c2").exists()
    wt = RC.create("c2", sha)
    assert (wt / "code.txt").read_text(encoding="utf-8") == "v1\n"


def test_run_sets_the_marker_logs_beside_and_collects(repo, capsys):
    assert RC.main(["--name", "r1", "--", *code(WRITE_MARKER)]) == 0
    wt = RC.RUNS / "r1"
    log = RC.RUNS / "r1.log"
    text = log.read_text(encoding="utf-8")
    assert "ran 1" in text and text.rstrip().endswith("EXIT 0"), text          # one BLAS thread, the exit recorded
    assert not list(wt.glob("*.log")), "the log is beside the checkout, never inside it"
    assert (wt / "results" / "out.csv").read_text(encoding="utf-8") == "r1\n"   # the clean-run marker names it
    assert RC.main(["--name", "r1", "--collect"]) == 0
    assert (repo / "results" / "out.csv").read_text(encoding="utf-8") == "r1\n"


def test_collect_refuses_a_file_this_tree_changed(repo):
    assert RC.main(["--name", "r2", "--", *code(WRITE_MARKER)]) == 0
    (repo / "results" / "out.csv").write_text("mine\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        RC.main(["--name", "r2", "--collect"])
    assert (repo / "results" / "out.csv").read_text(encoding="utf-8") == "mine\n"


def test_collect_never_overwrites_a_result(repo):
    body = "import pathlib; pathlib.Path('results/old.csv').write_text('a' + chr(10) + '2' + chr(10))"
    assert RC.main(["--name", "r3", "--", *code(body)]) == 0
    with pytest.raises(SystemExit):
        RC.main(["--name", "r3", "--collect"])
    assert (repo / "results" / "old.csv").read_text(encoding="utf-8") == "a\n1\n"


LEDGER_APPEND = ("import pathlib; p = pathlib.Path('results/read_ledger.jsonl'); "
                 "p.write_bytes(p.read_bytes() + b'L2' + bytes([10]))")
LEDGER_REWRITE = "import pathlib; pathlib.Path('results/read_ledger.jsonl').write_bytes(b'L9' + bytes([10]))"


def _commit_ledger(repo: Path) -> None:
    (repo / "results" / "read_ledger.jsonl").write_bytes(b"L1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "ledger")


def test_the_read_ledger_comes_home_when_it_extends_this_trees(repo):
    """Q-32: a clean run's judged reads append to its checkout's `results/read_ledger.jsonl`; `--collect` brings the
    lines home when the run's ledger extends this tree's, as for the variant log."""
    _commit_ledger(repo)
    assert RC.main(["--name", "g1", "--", *code(LEDGER_APPEND)]) == 0
    assert RC.main(["--name", "g1", "--collect"]) == 0
    assert (repo / "results" / "read_ledger.jsonl").read_bytes() == b"L1\nL2\n"


def test_a_rewritten_read_ledger_is_never_collected(repo):
    _commit_ledger(repo)
    assert RC.main(["--name", "g2", "--", *code(LEDGER_REWRITE)]) == 0
    with pytest.raises(SystemExit):
        RC.main(["--name", "g2", "--collect"])
    assert (repo / "results" / "read_ledger.jsonl").read_bytes() == b"L1\n"


def test_each_run_has_its_own_run_id(repo):
    """Q-32: `S2X_RUN_ID` names one invocation of run_clean (the reader's once-rule tells runs apart by it), set
    beside the clean-run marker and inherited by the command's own workers."""
    body = "import os; print('RUNID', os.environ.get('S2X_RUN_ID'))"
    ids = []
    for _ in range(2):
        assert RC.main(["--name", "g3", "--", *code(body)]) == 0
        line = [x for x in (RC.RUNS / "g3.log").read_text(encoding="utf-8").splitlines() if x.startswith("RUNID")]
        ids.append(line[0].split()[1])
    assert all(i.startswith("g3@") for i in ids), ids
    assert ids[0] != ids[1], "a reused checkout is a new run"


def test_remove_unlinks_first_and_keeps_the_store(repo):
    assert RC.main(["--name", "r4", "--", *code(WRITE_MARKER)]) == 0
    with pytest.raises(SystemExit):
        RC.main(["--name", "r4", "--remove"])          # its result is not home yet
    assert (RC.RUNS / "r4").is_dir()
    assert RC.main(["--name", "r4", "--collect"]) == 0
    assert RC.main(["--name", "r4", "--remove"]) == 0
    assert not (RC.RUNS / "r4").exists()
    for s, f in (("bars", "bars.parquet"), ("atlas", "walks.parquet")):
        assert (repo / "vendor/stage2/data" / s / f).read_text(encoding="utf-8") == f"store {s}\n"
    assert "r4" not in git(repo, "worktree", "list")


def test_remove_discard_drops_an_uncollected_run(repo):
    assert RC.main(["--name", "r5", "--", *code(WRITE_MARKER)]) == 0
    assert RC.main(["--name", "r5", "--remove", "--discard"]) == 0
    assert not (RC.RUNS / "r5").exists()
    assert (repo / "vendor/stage2/data/bars/bars.parquet").is_file()


def test_the_lock_is_held_during_the_run_and_released_after(repo, tmp_path):
    seen = tmp_path / "seen.json"
    # the child reads the lock once its pid is recorded (set right after the process starts; waits up to 20 s)
    body = (f"import json, pathlib, time; lk = pathlib.Path({str(RL.LOCK)!r}); held = None\n"
            "for _ in range(200):\n"
            "    held = json.loads(lk.read_text()) if lk.exists() else None\n"
            "    if held is None or held.get('pid'):\n"
            "        break\n"
            "    time.sleep(0.1)\n"
            f"pathlib.Path({str(seen)!r}).write_text(json.dumps(held))\n"
            "raise SystemExit(5)")
    rc = RC.main(["--name", "l1", "--hours", "0.5", "--mem-gb", "1", "--task", "Q-04", "--", *code(body)])
    assert rc == 5, "the command's own exit"
    held = json.loads(seen.read_text())
    assert held and held["job"] == "l1" and held["task"] == "Q-04" and held["pid"], held
    assert held["log"] and Path(held["log"]) == RC.RUNS / "l1.log"
    assert not RL.LOCK.exists(), "released whatever the exit"


def test_a_held_lock_means_the_command_does_not_run(repo, tmp_path):
    assert RL.main(["take", "--job", "other", "--task", "Q-00", "--holder", "t", "--hours", "1", "--mem-gb", "1"]) == 0
    marker = tmp_path / "ran.txt"
    body = f"import pathlib; pathlib.Path({str(marker)!r}).write_text('x')"
    assert RC.main(["--name", "l2", "--hours", "1", "--mem-gb", "1", "--task", "Q-04", "--", *code(body)]) == 3
    assert not marker.exists()
    assert json.loads(RL.LOCK.read_text())["job"] == "other", "the other job's lock is untouched"


def test_short_memory_means_the_command_does_not_run(repo, tmp_path, monkeypatch):
    monkeypatch.setattr(RL, "available_gb", lambda: 0.5)
    marker = tmp_path / "ran.txt"
    body = f"import pathlib; pathlib.Path({str(marker)!r}).write_text('x')"
    assert RC.main(["--name", "l3", "--hours", "1", "--mem-gb", "3", "--task", "Q-04", "--", *code(body)]) == 4
    assert not marker.exists() and not RL.LOCK.exists()


def test_hours_and_mem_go_together(repo):
    with pytest.raises(SystemExit):
        RC.main(["--name", "l4", "--hours", "1", "--", *code("pass")])
