"""Q-208: the pre-merge-commit hook -- a clean merge's result is checked before its commit is written.

A clean `git merge` runs no pre-commit, so a merge could bring in, untested, a decision log that breaks the reader's
hygiene or a changed vendored file. `scripts/pre-merge-commit` (installed by `scripts/install_hooks.py`) runs
`scripts/premerge_check.py`: vendor integrity, the log's hygiene (held-out tokens, fences), the pinned declarations, the
identity tokens on the real log -- light, bounded, refusing on any failure and naming the check.

Two layers. The check runner on synthetic inputs (fake readers, stub checks, a two-file repository). Then the real hook
end to end, on a throwaway clone of this repository (shared objects, its origin removed, results/ and docs/ left out
of the checkout but docs/calibration/), the hook files as this tree has them committed on a base branch, the hooks
installed by the real installer, and one side branch per case merged with `git merge --no-ff`.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import install_hooks as I  # noqa: E402
import premerge_check as P  # noqa: E402

LIMIT = 600
#: the files the throwaway clone takes from this tree's work tree (the code under test, committed or not)
HOOK_FILES = ("scripts/pre-merge-commit", "scripts/premerge_check.py", "scripts/install_hooks.py", ".gitattributes",
              "scripts/commit-msg", "scripts/check_verdicts.py", "scripts/pre-commit")
MALFORMED_ROW = "| E-9997 | 2026-11-21 | heldout-window: NQ soon -- a malformed held-out token | Q-208's test |"
UNCLOSED_FENCE = "| E-9998 | 2026-11-21 | **Q-208's test row**, an unclosed fence follows | Q-208's test |\n```\nopen\n"


def clean_env() -> dict:
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    env.update({"PYTHON": sys.executable, "PYTHONDONTWRITEBYTECODE": "1", "GIT_TERMINAL_PROMPT": "0",
                "GIT_MERGE_AUTOEDIT": "no", "OMP_NUM_THREADS": "1"})
    return env


def git(cwd: Path, *args: str, check: bool = True, timeout: float = LIMIT) -> subprocess.CompletedProcess:
    p = subprocess.run(["git", "-c", "user.name=q208", "-c", "user.email=q208@example.invalid", *args], cwd=cwd,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
                       env=clean_env())
    if check and p.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {p.stdout}{p.stderr}")
    return p


# ------------------------------------------------------------------------------------------------ the log's hygiene

class _Reader(types.SimpleNamespace):
    pass


def test_the_fence_check_is_skipped_visibly_when_the_reader_has_no_fences():
    reader = _Reader(heldout_token_problems=lambda text: [])
    problems, notes = P.log_problems("x\n", reader)
    assert problems == [] and notes == [P.FENCE_SKIPPED] and "SKIPPED" in notes[0] and "Q-194" in notes[0]


def test_an_unclosed_fence_is_a_problem_when_the_reader_has_fences():
    reader = _Reader(heldout_token_problems=lambda text: [], _fences=lambda text: ([], 5))
    problems, notes = P.log_problems("x\n", reader)
    assert notes == [] and len(problems) == 1 and problems[0].startswith("line 6:") and "never closed" in problems[0]
    closed = _Reader(heldout_token_problems=lambda text: [], _fences=lambda text: ([], None))
    assert P.log_problems("x\n", closed) == ([], [])


def test_the_readers_own_report_of_the_fence_is_not_repeated():
    reader = _Reader(heldout_token_problems=lambda text: ["line 6: a fenced code block opened here is never closed"],
                     _fences=lambda text: ([], 5))
    assert len(P.log_problems("x\n", reader)[0]) == 1


def test_a_reader_without_the_token_check_is_refused_not_skipped():
    problems, _ = P.log_problems("x\n", _Reader())
    assert problems and "merge master" in problems[0]


def test_a_malformed_heldout_token_is_a_problem_under_the_real_reader():
    from extended import reader
    problems, _ = P.log_problems(MALFORMED_ROW + "\n", reader)
    assert problems and "E-9997" in problems[0]


def test_this_trees_decision_log_passes_the_log_check():
    p = subprocess.run([sys.executable, str(SCRIPTS / "premerge_check.py"), "--log"], capture_output=True, text=True,
                       timeout=LIMIT, env=clean_env())
    assert p.returncode == 0, p.stdout + p.stderr


# ------------------------------------------------------------------------------------------------ the runner

def _stub(name: str, code: str) -> P.Check:
    return P.Check(name, (sys.executable, "-c", code))


def _repo(tmp_path: Path) -> Path:
    r = tmp_path / "r"
    r.mkdir()
    git(r, "init", "-q")
    (r / "DECISIONS.md").write_text("log\n", encoding="utf-8")
    (r / "other.txt").write_text("x\n", encoding="utf-8")
    git(r, "add", "-A")
    git(r, "commit", "-q", "--no-verify", "-m", "base")       # a two-file repository with no hooks at all
    return r


def test_every_check_runs_and_every_failure_is_named(tmp_path, capsys):
    r = _repo(tmp_path)
    rc = P.run_checks(r, [_stub("first ok", "pass"), _stub("second bad", "import sys; print('boom'); sys.exit(3)"),
                          _stub("third bad", "raise SystemExit(4)"), _stub("fourth ok", "pass")])
    out = capsys.readouterr()
    assert rc == 1
    assert "ok   first ok" in out.out and "ok   fourth ok" in out.out
    assert "FAIL second bad (exit 3" in out.err and "boom" in out.err and "FAIL third bad (exit 4" in out.err
    assert "failed: second bad; third bad" in out.err


def test_all_checks_passing_passes(tmp_path, capsys):
    assert P.run_checks(_repo(tmp_path), [_stub("a", "pass"), _stub("b", "print('SKIPPED: a note')")]) == 0
    out = capsys.readouterr().out
    assert "OK: 2 checks" in out and "SKIPPED: a note" in out


def test_the_budget_kills_a_check_and_refuses_naming_it(tmp_path, capsys):
    t0 = time.monotonic()
    rc = P.run_checks(_repo(tmp_path), [_stub("slow one", "import time; time.sleep(60)"), _stub("after", "pass")],
                      budget_s=2)
    assert rc == 1 and time.monotonic() - t0 < 30
    err = capsys.readouterr().err
    assert "'slow one' was still running" in err and "'after' did not start" in err


def test_the_declared_budget_is_five_minutes_and_the_hook_takes_no_slot():
    assert P.BUDGET_S == 300
    hook = (SCRIPTS / "pre-merge-commit").read_text(encoding="utf-8")
    code = [ln for ln in hook.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    assert not any("fasttier_lock" in ln or "run_lock" in ln or "pytest" in ln for ln in code)
    assert "scripts/premerge_check.py" in hook and "no fast-tier slot" in hook


def test_an_unstaged_edit_of_a_checked_file_refuses(tmp_path, capsys):
    r = _repo(tmp_path)
    (r / "DECISIONS.md").write_text("edited after the merge\n", encoding="utf-8")
    assert P.run_checks(r, [_stub("never reached", "pass")]) == 1
    err = capsys.readouterr().err
    assert "DECISIONS.md" in err and "differ from the merge result" in err
    (r / "DECISIONS.md").write_text("log\n", encoding="utf-8")
    (r / "other.txt").write_text("an edit outside the checked paths\n", encoding="utf-8")
    assert P.run_checks(r, [_stub("reached", "pass")]) == 0


def test_the_check_set_is_the_declared_one():
    names = [c.name for c in P.checks()]
    assert names == ["vendor integrity", "the decision log's hygiene", "pinned declarations",
                     "identity tokens on the real log"]
    cmds = [" ".join(c.cmd[1:]) for c in P.checks()]
    assert cmds[0] == "scripts/vendor_stage2.py --verify"
    log_cmd = P.checks()[1].cmd                                # Q-209 (F11): this very file, on the tree checked
    assert Path(log_cmd[1]) == Path(P.__file__).resolve() and log_cmd[2:4] == ("--log", "--root")
    assert cmds[2].endswith("tests/test_declarations_fixed.py") and cmds[3].endswith(P.LOG_TEST)
    test_file, test_name = P.LOG_TEST.split("::")
    assert f"def {test_name}(" in (ROOT / test_file).read_text(encoding="utf-8")


def test_the_hook_traps_signals_and_keeps_lf():
    data = (SCRIPTS / "pre-merge-commit").read_bytes()
    assert b"\r\n" not in data and data.startswith(b"#!/bin/sh\n")
    text = data.decode("utf-8")
    for sig in ("HUP", "INT", "QUIT", "TERM"):
        assert f"trap 'on_signal {sig} " in text
    assert "trap '' PIPE" in text
    assert text.index("git rev-parse --show-toplevel") < text.index("unset GIT_INDEX_FILE")
    assert "scripts/pre-merge-commit text eol=lf" in (ROOT / ".gitattributes").read_text(encoding="utf-8")


def test_the_installer_installs_the_hook(tmp_path):
    assert "pre-merge-commit" in I.HOOKS
    hooks = tmp_path / "hooks"
    assert I.install_all(hooks) == 0
    assert (hooks / "pre-merge-commit").read_bytes() == (SCRIPTS / "pre-merge-commit").read_bytes()


# ------------------------------------------------------------------------------------------------ the real hook, end to end

def _common_dir() -> Path:
    out = git(ROOT, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
    return Path(out)


@pytest.fixture(scope="module")
def clone(tmp_path_factory):
    """A throwaway clone: this tree's HEAD with the hook files as this tree has them, one side branch per case, and
    the hooks installed by the clone's own `scripts/install_hooks.py`. Yields (path, base sha, installer output)."""
    if shutil.which("git") is None:
        pytest.skip("git not found")
    sha = git(ROOT, "rev-parse", "HEAD").stdout.strip()
    c = tmp_path_factory.mktemp("q208") / "clone"
    git(c.parent, "clone", "-q", "--shared", "--no-checkout", str(_common_dir()), str(c))
    git(c, "remote", "remove", "origin")                    # nothing here can ever be pushed anywhere
    git(c, "sparse-checkout", "set", "--no-cone", "/*", "!/results/", "!/docs/", "/docs/calibration/")
    git(c, "checkout", "-q", "-b", "base", sha)
    for rel in HOOK_FILES:
        (c / rel).write_bytes((ROOT / rel).read_bytes())
    git(c, "add", "-A")
    if git(c, "diff", "--cached", "--quiet", check=False).returncode:
        git(c, "commit", "-q", "--no-verify", "-m", "base: the hook files as the tree under test has them")
    base = git(c, "rev-parse", "HEAD").stdout.strip()

    def side(name, change):
        git(c, "checkout", "-q", "-b", name, "base")
        change()
        git(c, "add", "-A")
        git(c, "commit", "-q", "--no-verify", "-m", name)

    def append(rel, text):
        with open(c / rel, "a", encoding="utf-8", newline="\n") as f:
            f.write("\n" + text)

    side("side-clean", lambda: ((c / "q208_note.txt").write_text("a harmless file\n", encoding="utf-8")))
    side("side-fence", lambda: append("DECISIONS.md", UNCLOSED_FENCE))
    side("side-token", lambda: append("DECISIONS.md", MALFORMED_ROW + "\n"))
    vendored = next(ln.split("  ", 1)[1].strip() for ln in (c / "vendor" / "MANIFEST_stage2.sha256")
                    .read_text(encoding="utf-8").splitlines() if "  " in ln)
    side("side-vendor", lambda: (c / "vendor" / "stage2" / vendored).write_bytes(
        (c / "vendor" / "stage2" / vendored).read_bytes() + b"\n# changed by a merge\n"))
    side("side-nocheck", lambda: (c / "scripts" / "premerge_check.py").unlink())

    def weaken():                                             # the branch disarms its own checker, and changes vendor
        pc = c / "scripts" / "premerge_check.py"
        pc.write_text(pc.read_text(encoding="utf-8").replace(
            "    the_checks = checks(root=root) if the_checks is None else the_checks",
            "    the_checks = []"), encoding="utf-8", newline="\n")
        (c / "vendor" / "stage2" / vendored).write_bytes((c / "vendor" / "stage2" / vendored).read_bytes() + b"\n#\n")
    side("side-weaken", weaken)
    side("side-unverified", lambda: ((c / "q209_note.txt").write_text("a tip with no verdict\n", encoding="utf-8")))
    git(c, "checkout", "-q", "base")
    # Q-209: the clone is a main worktree, whose merges pass the commit-msg gate only over a merged tip with a full
    # fast tier verdict; every side but side-unverified has one
    with open(c / ".git" / "fasttier-verdicts.log", "a", encoding="utf-8", newline="\n") as f:
        for b in ("side-clean", "side-fence", "side-token", "side-vendor", "side-nocheck", "side-weaken"):
            tree = git(c, "rev-parse", f"{b}^{{tree}}").stdout.strip()
            f.write(f"{tree}\t2026-11-22T00:00:00Z\t{c.as_posix()}\t1 passed in 0.01s\ttier=T2\n")
    # the real installer, run in the clone: its common dir is the clone's own .git
    inst = subprocess.run([sys.executable, "scripts/install_hooks.py"], cwd=c, capture_output=True, text=True,
                          timeout=LIMIT, env=clean_env())
    assert inst.returncode == 0, inst.stdout + inst.stderr
    yield c, base, inst.stdout + inst.stderr


def _merge(c: Path, base: str, branch: str) -> tuple[subprocess.CompletedProcess, bool]:
    if (c / ".git" / "MERGE_HEAD").exists():
        git(c, "merge", "--abort")
    git(c, "reset", "-q", "--hard", base)
    p = git(c, "merge", "--no-ff", "-m", f"merge {branch}", branch, check=False)
    merged = git(c, "rev-parse", "HEAD").stdout.strip() != base
    return p, merged


def test_the_hook_is_installed_by_install_hooks(clone):
    c, _, out = clone
    installed = c / ".git" / "hooks" / "pre-merge-commit"
    assert installed.read_bytes() == (ROOT / "scripts" / "pre-merge-commit").read_bytes()
    assert "pre-merge-commit" in out


def test_a_clean_merge_passes_every_check(clone):
    c, base, _ = clone
    p, merged = _merge(c, base, "side-clean")
    out = p.stdout + p.stderr
    assert p.returncode == 0 and merged, out
    for name in ("vendor integrity", "the decision log's hygiene", "pinned declarations",
                 "identity tokens on the real log"):
        assert f"ok   {name}" in out, out
    assert "OK: 4 checks" in out
    parents = git(c, "rev-list", "--parents", "-n", "1", "HEAD").stdout.split()
    assert len(parents) == 3, "not a merge commit"


def test_a_merge_bringing_an_unclosed_fence_is_refused(clone):
    """With the reader's fences (Q-194d) on this tree: refused, naming the log's hygiene. Before Q-194 is on master
    the reader has no `_fences`: the check is skipped with its visible line, and the merge passes on the rest."""
    c, base, _ = clone
    from extended import reader
    p, merged = _merge(c, base, "side-fence")
    out = p.stdout + p.stderr
    if getattr(reader, "_fences", None) is None:
        assert p.returncode == 0 and merged, out
        assert "SKIPPED: the fence check" in out, out
    else:
        assert p.returncode != 0 and not merged, out
        assert "FAIL the decision log's hygiene" in out and "never closed" in out, out


def test_a_merge_bringing_a_malformed_heldout_token_is_refused(clone):
    c, base, _ = clone
    p, merged = _merge(c, base, "side-token")
    out = p.stdout + p.stderr
    assert p.returncode != 0 and not merged, out
    assert "FAIL the decision log's hygiene" in out and "E-9997" in out and "REFUSED" in out, out


def test_a_merge_changing_a_vendored_file_is_refused(clone):
    c, base, _ = clone
    p, merged = _merge(c, base, "side-vendor")
    out = p.stdout + p.stderr
    assert p.returncode != 0 and not merged, out
    assert "FAIL vendor integrity" in out and "failed: vendor integrity" in out, out


def test_heads_checker_judges_a_merge_that_removes_the_checker(clone):
    """Q-209 (the red team's F11): HEAD's copy of the checker runs, so a branch deleting it is still checked."""
    c, base, _ = clone
    p, merged = _merge(c, base, "side-nocheck")
    out = p.stdout + p.stderr
    assert p.returncode == 0 and merged and "by HEAD's copy" in out and "OK: 4 checks" in out, out


def test_heads_checker_judges_a_merge_that_disarms_the_checker(clone):
    c, base, _ = clone
    p, merged = _merge(c, base, "side-weaken")
    out = p.stdout + p.stderr
    assert p.returncode != 0 and not merged and "FAIL vendor integrity" in out and "by HEAD's copy" in out, out


def test_the_main_tree_refuses_a_merge_of_a_tip_without_a_verdict(clone):
    """Q-209 (F4, F13): the commit-msg gate reads MERGE_HEAD; the merged tip has no full-fast-tier verdict."""
    c, base, _ = clone
    tip = git(c, "rev-parse", "side-unverified").stdout.strip()
    p, merged = _merge(c, base, "side-unverified")
    out = p.stdout + p.stderr
    assert p.returncode != 0 and not merged and "commit-msg: REFUSED" in out and tip[:10] in out, out
    assert "ok   vendor integrity" in out                        # pre-merge-commit's checks passed first


def test_a_passed_main_tree_merge_leaves_a_gate_line(clone):
    c, base, _ = clone
    p, merged = _merge(c, base, "side-clean")
    assert p.returncode == 0 and merged, p.stdout + p.stderr
    tree = git(c, "rev-parse", "HEAD^{tree}").stdout.strip()
    tip = git(c, "rev-parse", "side-clean").stdout.strip()
    log = (c / ".git" / "fasttier-verdicts.log").read_text(encoding="utf-8")
    assert f"gate\t{tree}\t" in log and f"tips={tip}" in log


def test_the_installer_makes_merges_into_master_never_fast_forward(clone):
    c, _, out = clone
    assert git(c, "config", I.NO_FF_KEY).stdout.strip() == "--no-ff" and I.NO_FF_KEY in out


def test_a_merge_into_master_is_a_merge_commit_and_a_workers_merge_of_master_still_fast_forwards(tmp_path):
    """Q-209 (F4): with the installer's setting, a fast-forwardable merge into master writes a merge commit (so its
    hooks run); a worker tree merging master (fast-forwardable too) keeps git's default and fast-forwards."""
    r = tmp_path / "r"
    r.mkdir()
    git(r, "init", "-q", "-b", "master")
    git(r, "commit", "-q", "--allow-empty", "--no-verify", "-m", "base")
    assert I.set_main_merge_ff(r / ".git") == 0
    git(r, "checkout", "-q", "-b", "side")
    git(r, "commit", "-q", "--allow-empty", "--no-verify", "-m", "side")
    git(r, "checkout", "-q", "master")
    git(r, "merge", "-q", "--no-verify", "-m", "merge side", "side")
    assert len(git(r, "rev-list", "--parents", "-n", "1", "HEAD").stdout.split()) == 3, "master fast-forwarded"
    wt = tmp_path / "wt"
    git(r, "worktree", "add", "-q", "-b", "wt/x", str(wt), "side")
    git(wt, "merge", "-q", "--no-verify", "master")
    assert git(wt, "rev-parse", "HEAD").stdout.strip() == git(r, "rev-parse", "master").stdout.strip()
    assert git(wt, "config", "merge.ff", check=False).stdout.strip() == ""


def _git_sh() -> str | None:
    try:
        out = subprocess.run(["git", "var", "GIT_SHELL_PATH"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    sh = out.stdout.strip()
    return sh if out.returncode == 0 and sh and Path(sh).exists() else None


def test_the_hook_refuses_when_inherited_variables_point_at_another_tree(clone, tmp_path):
    """Q-209 (F11): pre-commit's cross-tree guard, copied -- GIT_DIR the clone's, GIT_WORK_TREE another folder."""
    sh = _git_sh()
    if sh is None:
        pytest.skip("git's own sh not found")
    c, _, _ = clone
    other = tmp_path / "elsewhere"
    other.mkdir()
    env = {**clean_env(), "GIT_DIR": str(c / ".git"), "GIT_WORK_TREE": str(other)}
    p = subprocess.run([sh, str(c / ".git" / "hooks" / "pre-merge-commit")], cwd=other, capture_output=True,
                       text=True, timeout=LIMIT, env=env)
    assert p.returncode != 0 and "REFUSED: git is merging into" in p.stderr, p.stdout + p.stderr
