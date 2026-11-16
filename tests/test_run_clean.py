"""Q-04: `scripts/run_clean.py` -- a clean, detached checkout of a commit; the stores linked by junction; the command
run with the clean-run marker and its log beside the checkout; `--collect` bringing results home and refusing clashes
and overwrites; `--remove` unlinking the junctions first; the run lock taken and released around the command.

Q-67 (E-044 (4)): the append-only files (`results/read_ledger.jsonl`, `results/variants.jsonl`) are collected as a
union -- two runs made from a commit whose ledger lacks the other's lines both come home, whichever is collected first
and whether or not the first collection was committed; a run that edited, dropped or cut a line of its commit's copy,
a tree that lost a line of the run's commit or of its own HEAD, and a union the reader's `read_ledger` does not verify
are refused with nothing copied; collecting twice is a no-op; `--remove` counts the file home once every line of the
run's copy is in this tree's (a multiset); and a CRLF checkout of the variant log (core.autocrlf, text=auto) unions too.

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

from extended import reader  # noqa: E402  (run_clean put this repository's root on the path)


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


LEDGER = "results/read_ledger.jsonl"
VARIANTS = "results/variants.jsonl"


def rec(n: int, run: str = "r") -> bytes:
    """One ledger line as the reader writes it: a JSON object with the ledger's keys, canonical, LF-terminated."""
    r = {k: None for k in reader.LEDGER_KEYS}
    r.update({"ledger": 1, "when": f"2026-11-16T00:00:{n:02d}+00:00", "purpose": "identity",
              "who": {"run_id": f"{run}@{n}", "pid": 1000 + n}, "declaration": {"ref": "E-901", "kind": "identity"}})
    return (json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


LEDGER_REWRITE = "import pathlib; pathlib.Path('results/read_ledger.jsonl').write_bytes(b'L9' + bytes([10]))"


def _commit_ledger(repo: Path, data: bytes | None = None) -> str:
    (repo / LEDGER).write_bytes(rec(1, "base") if data is None else data)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "ledger")
    return git(repo, "rev-parse", "HEAD")


def _ledger_append_body(payload: Path) -> str:
    """A command that appends the bytes of `payload` (a file outside the repository) to the checkout's ledger."""
    return ("import pathlib; p = pathlib.Path('results/read_ledger.jsonl'); "
            f"p.write_bytes(p.read_bytes() + pathlib.Path({str(payload)!r}).read_bytes())")


def test_the_read_ledger_comes_home_when_it_extends_this_trees(repo, tmp_path):
    """Q-32: a clean run's judged reads append to its checkout's `results/read_ledger.jsonl`; `--collect` brings the
    lines home when the run's ledger extends this tree's, as for the variant log."""
    _commit_ledger(repo)
    payload = tmp_path / "payload.jsonl"
    payload.write_bytes(rec(2, "g1"))
    assert RC.main(["--name", "g1", "--", *code(_ledger_append_body(payload))]) == 0
    assert RC.main(["--name", "g1", "--collect"]) == 0
    assert (repo / LEDGER).read_bytes() == rec(1, "base") + rec(2, "g1")


def test_a_rewritten_read_ledger_is_never_collected(repo):
    _commit_ledger(repo)
    assert RC.main(["--name", "g2", "--", *code(LEDGER_REWRITE)]) == 0
    with pytest.raises(SystemExit):
        RC.main(["--name", "g2", "--collect"])
    assert (repo / "results" / "read_ledger.jsonl").read_bytes() == rec(1, "base")


# ------------------------------------------------- Q-67: the append-only files collected as a union (E-044 (4))


def _run_appends(name: str, sha: str, *lines: bytes, path: str = LEDGER) -> Path:
    """A clean checkout of `sha` whose run appended `lines` to `path`: the run simulated by writing its output into
    the checkout (no command runs)."""
    wt = RC.create(name, sha)
    p = wt / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((p.read_bytes() if p.exists() else b"") + b"".join(lines))
    return wt


def _ledger(repo: Path) -> bytes:
    return (repo / LEDGER).read_bytes()


def _results(repo: Path) -> list[str]:
    return sorted(p.name for p in (repo / "results").iterdir())


@pytest.mark.parametrize("commit_between", [True, False], ids=["committed-between", "uncommitted-between"])
def test_two_runs_from_one_commit_both_come_home_as_a_union(repo, commit_between):
    """The gap of E-044 (4): two runs made from a commit whose ledger lacks the other's lines each append their own;
    the first collected, the second's copy no longer extends this tree's -- it comes home as a union all the same,
    after the base, the first run's lines, then its own; and `--remove` then counts both runs' ledgers home."""
    sha = _commit_ledger(repo)
    a = _run_appends("u1", sha, rec(2, "u1"), rec(3, "u1"))
    (a / "results" / "u1.csv").write_text("x\n1\n", encoding="utf-8")
    b = _run_appends("u2", sha, rec(4, "u2"))
    (b / "results" / "u2.csv").write_text("x\n2\n", encoding="utf-8")
    for name in ("u1", "u2"):
        with pytest.raises(SystemExit, match="not brought home"):
            RC.main(["--name", name, "--remove"])                     # nothing is home yet
    assert RC.main(["--name", "u1", "--collect"]) == 0
    assert _ledger(repo) == rec(1, "base") + rec(2, "u1") + rec(3, "u1")
    if commit_between:                                                # the lead commits the first run's lines
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "u1 home")
    with pytest.raises(SystemExit, match="not brought home"):
        RC.main(["--name", "u2", "--remove"])                         # u2's line is not home yet
    assert RC.main(["--name", "u2", "--collect"]) == 0
    assert _ledger(repo) == rec(1, "base") + rec(2, "u1") + rec(3, "u1") + rec(4, "u2")
    assert [r["who"]["run_id"] for r in reader.read_ledger(repo / LEDGER)] == ["base@1", "u1@2", "u1@3", "u2@4"]
    assert (repo / "results" / "u2.csv").read_text(encoding="utf-8") == "x\n2\n", "its other results as before"
    assert not reader.missing_lines((b / LEDGER).read_text(encoding="utf-8"), _ledger(repo).decode("utf-8"))
    assert RC.main(["--name", "u1", "--remove"]) == 0
    assert RC.main(["--name", "u2", "--remove"]) == 0
    assert not (RC.RUNS / "u1").exists() and not (RC.RUNS / "u2").exists()


def test_a_run_from_a_commit_without_a_ledger_comes_home_beside_this_trees_lines(repo):
    """The waiting checkout's case: the run's commit had no ledger; this tree has since committed another run's line."""
    sha = git(repo, "rev-parse", "HEAD")
    assert "read_ledger" not in git(repo, "ls-tree", "-r", "--name-only", sha)
    _run_appends("n1", sha, rec(5, "n1"), rec(6, "n1"))
    _commit_ledger(repo)
    assert RC.main(["--name", "n1", "--collect"]) == 0
    assert _ledger(repo) == rec(1, "base") + rec(5, "n1") + rec(6, "n1")
    assert RC.main(["--name", "n1", "--remove"]) == 0


@pytest.mark.parametrize("how", ["edited", "dropped", "reordered"])
def test_a_run_that_did_more_than_append_is_refused(repo, how):
    """The run's copy must start with its commit's copy byte for byte: a base line edited, dropped or moved is
    refused (a multiset check alone would pass the reordered one), nothing copied, and the run is not home."""
    base = rec(1, "base") + rec(2, "base")
    sha = _commit_ledger(repo, base)
    wt = RC.create("e1", sha)
    edited = rec(2, "base").replace(b'"pid":1002', b'"pid":9999')
    assert edited != rec(2, "base")
    head = {"edited": rec(1, "base") + edited, "dropped": rec(1, "base"),
            "reordered": rec(2, "base") + rec(1, "base")}[how]
    (wt / LEDGER).write_bytes(head + rec(3, "e1"))
    (wt / "results" / "e1.csv").write_text("x\n1\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="does not start with"):
        RC.main(["--name", "e1", "--collect"])
    assert _ledger(repo) == base and not (repo / "results" / "e1.csv").exists(), "nothing copied"
    with pytest.raises(SystemExit, match="not brought home"):
        RC.main(["--name", "e1", "--remove"])


@pytest.mark.parametrize("where", ["working-copy", "committed"])
def test_a_tree_that_lost_a_line_of_the_runs_commit_is_refused(repo, where):
    sha = _commit_ledger(repo, rec(1, "base") + rec(2, "base"))
    wt = _run_appends("t1", sha, rec(3, "t1"))
    (wt / "results" / "t1.csv").write_text("x\n1\n", encoding="utf-8")
    (repo / LEDGER).write_bytes(rec(1, "base"))                       # this tree lost rec(2)
    if where == "committed":
        git(repo, "commit", "-q", "-am", "a line lost")
    with pytest.raises(SystemExit, match="lost"):
        RC.main(["--name", "t1", "--collect"])
    assert _ledger(repo) == rec(1, "base") and not (repo / "results" / "t1.csv").exists(), "nothing copied"


def test_a_tree_whose_working_copy_lost_a_line_committed_at_head_is_refused(repo):
    """A line committed after the run's commit (another run's, collected) and then lost from the working copy is not
    in the run's base, so the base check alone would pass it; the union is refused all the same."""
    sha = _commit_ledger(repo)
    _run_appends("h1", sha, rec(3, "h1"))
    _commit_ledger(repo, rec(1, "base") + rec(2, "other"))
    (repo / LEDGER).write_bytes(rec(1, "base"))
    with pytest.raises(SystemExit, match="HEAD"):
        RC.main(["--name", "h1", "--collect"])
    assert _ledger(repo) == rec(1, "base")


def test_collecting_twice_is_a_no_op(repo):
    """Multiset-aware: a line the run wrote twice comes home twice, once; a second collection (before or after the
    commit) appends nothing and does not rewrite the file."""
    sha = _commit_ledger(repo)
    _run_appends("d1", sha, rec(2, "d1"), rec(2, "d1"), rec(3, "d1"))
    assert RC.main(["--name", "d1", "--collect"]) == 0
    once = _ledger(repo)
    assert once == rec(1, "base") + rec(2, "d1") * 2 + rec(3, "d1")
    stamp = os.stat(repo / LEDGER).st_mtime_ns
    assert RC.main(["--name", "d1", "--collect"]) == 0
    assert _ledger(repo) == once and os.stat(repo / LEDGER).st_mtime_ns == stamp, "not rewritten"
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "d1 home")
    assert RC.main(["--name", "d1", "--collect"]) == 0
    assert _ledger(repo) == once
    assert RC.main(["--name", "d1", "--remove"]) == 0


def test_remove_counts_a_run_home_by_its_lines_not_its_bytes(repo):
    """Once a later line sits in this tree's copy, the run's copy differs from it byte for byte; it is home when every
    one of its lines is (with multiplicity) -- and not home while one copy of a twice-written line is missing."""
    sha = _commit_ledger(repo)
    _run_appends("m1", sha, rec(2, "m1"), rec(2, "m1"))
    (repo / LEDGER).write_bytes(rec(1, "base") + rec(7, "other") + rec(2, "m1"))
    with pytest.raises(SystemExit, match="not brought home"):
        RC.main(["--name", "m1", "--remove"])                         # one of its two copies is missing
    (repo / LEDGER).write_bytes(rec(1, "base") + rec(7, "other") + rec(2, "m1") * 2)
    assert RC.main(["--name", "m1", "--remove"]) == 0


@pytest.mark.parametrize("tail,why", [
    (rec(2, "c1")[:-1], "newline"),                                   # the run's last line was cut
    (b"not json\n", "does not verify"),                               # the union is not a ledger
    (b'{"ledger": 1}\n', "does not verify"),                          # a line without the ledger's fields
], ids=["cut", "not-json", "no-fields"])
def test_a_cut_or_unverifiable_line_is_refused(repo, tail, why):
    sha = _commit_ledger(repo)
    _run_appends("c1", sha, rec(3, "c1"), tail)
    names = _results(repo)
    with pytest.raises(SystemExit, match=why):
        RC.main(["--name", "c1", "--collect"])
    assert _ledger(repo) == rec(1, "base")
    assert _results(repo) == names, "no temporary file is left behind"


@pytest.mark.parametrize("path", [LEDGER, VARIANTS])
@pytest.mark.parametrize("blank", [b"\n", b"  \r\n"], ids=["empty", "spaces"])
def test_a_blank_line_in_what_the_run_appended_is_refused(repo, path, blank):
    """`missing_lines` skips blank lines, so a union alone would drop one silently (and `--remove` would then count
    the run home): neither writer ever writes one, so it is refused, nothing copied, the run kept for a look."""
    first = rec(1, "base") if path == LEDGER else b'{"v": 1}\n'
    (repo / path).write_bytes(first)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "the base")
    sha = git(repo, "rev-parse", "HEAD")
    _run_appends("k1", sha, rec(3, "k1"), blank, rec(4, "k1"), path=path)
    with pytest.raises(SystemExit, match="blank line"):
        RC.main(["--name", "k1", "--collect"])
    assert (repo / path).read_bytes() == first
    with pytest.raises(SystemExit, match="not brought home"):
        RC.main(["--name", "k1", "--remove"])


def test_a_tree_copy_without_its_last_newline_is_refused(repo):
    sha = _commit_ledger(repo)
    _run_appends("w1", sha, rec(3, "w1"))
    (repo / LEDGER).write_bytes(rec(1, "base")[:-1])
    with pytest.raises(SystemExit, match="newline"):
        RC.main(["--name", "w1", "--collect"])
    assert _ledger(repo) == rec(1, "base")[:-1]


def test_the_variant_log_unions_from_a_crlf_checkout(repo):
    """The variant log is `text=auto`: under core.autocrlf its checkout is CRLF while the run appends LF lines. Its
    base is the commit's copy as the checkout holds it (`git cat-file --filters`), so the union still comes home."""
    git(repo, "config", "core.autocrlf", "true")
    (repo / ".gitattributes").write_text("* text=auto\nresults/read_ledger.jsonl text eol=lf\n", encoding="utf-8")
    (repo / VARIANTS).write_bytes(b'{"v": 1}\n')
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "variants")
    sha = git(repo, "rev-parse", "HEAD")
    wt = RC.create("v1", sha)
    held = (wt / VARIANTS).read_bytes()
    assert held == b'{"v": 1}\r\n', "the checkout converts the variant log: the case under test"
    (wt / VARIANTS).write_bytes(held + b'{"v": 2}\n')                 # the variant counter appends LF lines
    (repo / VARIANTS).write_bytes(b'{"v": 1}\n{"v": 3}\n')            # this tree's own later line, committed
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "a later variant")
    assert RC.main(["--name", "v1", "--collect"]) == 0
    assert (repo / VARIANTS).read_bytes() == b'{"v": 1}\n{"v": 3}\n{"v": 2}\n'
    assert RC.main(["--name", "v1", "--collect"]) == 0
    assert (repo / VARIANTS).read_bytes() == b'{"v": 1}\n{"v": 3}\n{"v": 2}\n'
    assert RC.main(["--name", "v1", "--remove"]) == 0


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
