"""Q-209 as reworked (the lead's ruling on the red team's BLOCK): the pre-commit's pre-flight, then the full fast tier on
every commit; and the work tree must be the commit (the red team's F5).

* the pre-flight's list: E-274's always-on guards, the staged test files, and the tests that import, name or list a
  staged file directly (one step; at most PREFLIGHT_DIRECT_MAX of them) -- the direct edges each tested, on a synthetic
  repository (an `importlib.import_module` import, a file in a listed folder, a recursive listing, a dotted `-m` name);
* end to end through the real pre-commit hook (its vendor and licence steps stubbed, the fast-tier lock pointed at a
  private folder, the runner serial): a broken guard is refused by the pre-flight and the full tier never starts; a
  clean commit runs the pre-flight and then the full fast tier, in the main tree and in a worker tree alike, its
  verdict `tier=T2`; a commit staged with `git add -p` leaving a hunk unstaged is refused, as is an untracked module,
  and a log file at the top of the tree is not counted.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import fasttier_preflight as P  # noqa: E402

LIMIT = 600

FILES = {
    "extended/__init__.py": "",
    "extended/core.py": "def f():\n    return 1\n",
    "extended/mid.py": "from extended import core\n\n\ndef g():\n    return core.f()\n",
    "extended/dyn.py": "V = 7\n",
    "scripts/dynbare.py": "B = 5\n",
    "extended/sub/__init__.py": "",
    "extended/sub/leaf.py": "W = 3\n",
    "tests/test_direct.py": "from extended import core\n\n\ndef test_f():\n    assert core.f() == 1\n",
    "tests/test_via_mid.py": "from extended import mid\n\n\ndef test_g():\n    assert mid.g() == 1\n",
    "tests/test_dynamic.py": textwrap.dedent('''\
        import importlib


        def test_v():
            assert importlib.import_module("extended.dyn").V == 7
        '''),
    "tests/test_dotted.py": "import extended.sub.leaf as L\n\n\ndef test_w():\n    assert L.W == 3\n",
    "tests/test_lists_reviews.py": textwrap.dedent('''\
        from pathlib import Path
        ROOT = Path(__file__).resolve().parent.parent


        def test_reviews_are_markdown():
            assert all(p.suffix == ".md" for p in (ROOT / "docs" / "reviews").iterdir())
        '''),
    "tests/test_walks_plans.py": textwrap.dedent('''\
        from pathlib import Path
        ROOT = Path(__file__).resolve().parent.parent


        def test_plans_are_markdown():
            assert all(p.suffix == ".md" for p in (ROOT / "docs" / "plans").rglob("*.md"))
        '''),
    "tests/test_runs_module.py": textwrap.dedent('''\
        import subprocess
        import sys


        def test_m():
            assert subprocess.run([sys.executable, "-c", "pass"]).returncode == 0
            assert "extended.sub.leaf"
        '''),
    "tests/test_identity_tokens.py": textwrap.dedent('''\
        import os
        from pathlib import Path
        ROOT = Path(__file__).resolve().parent.parent


        def test_the_log_has_no_broken_token():
            assert "identity: BROKEN" not in (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
        '''),
    # outside every pre-flight: it marks (outside the repository) that the full fast tier ran
    "tests/test_zz_sentinel.py": textwrap.dedent('''\
        import os


        def test_the_full_tier_ran():
            mark = os.environ.get("Q209_SENTINEL")
            if mark:
                with open(mark, "a", encoding="utf-8") as f:
                    f.write("ran\\n")
        '''),
    "docs/reviews/R1.md": "a review\n",
    "docs/plans/deep/P1.md": "a plan\n",
    "DECISIONS.md": "# log\n| E-001 | 2026-11-21 | a row | basis |\n",
    "long.txt": "".join(f"line {i}\n" for i in range(40)),
}
PASS = "def test_ok():\n    assert True\n"


def build(root: Path) -> Path:
    for rel, text in FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8", newline="\n")
    for rel in P._expand(ROOT, P.PREFLIGHT_GUARDS):         # the guards, as trivial passing tests here
        if not (root / rel).exists():
            (root / rel).write_text(PASS, encoding="utf-8", newline="\n")
    return root


def guards(root: Path) -> set[str]:
    return set(P._expand(root, P.PREFLIGHT_GUARDS))


@pytest.fixture()
def repo(tmp_path) -> Path:
    return build(tmp_path / "r")


# ------------------------------------------------------------------------------------------------ the list

def test_the_guards_are_e274s_list():
    names = {Path(g).name for g in P.PREFLIGHT_GUARDS}
    assert {"test_heavy_marker_guard.py", "test_heavy_guard.py", "test_seed_derivation_guard.py",
            "test_identity_tokens.py", "test_declarations_fixed.py", "test_git_scan.py", "test_trace_check.py",
            "test_vendor_integrity.py", "test_reader*.py"} == names
    found = P._expand(ROOT, P.PREFLIGHT_GUARDS)
    assert "tests/test_reader.py" in found and "tests/test_reader_heldout.py" in found
    assert all((ROOT / g).is_file() for g in found) and len(found) >= 10


def test_the_preflight_is_the_guards_the_staged_tests_and_the_direct_tests(repo):
    g = guards(repo)
    assert set(P.preflight_tests(["extended/core.py"], repo)) == g | {"tests/test_direct.py"}   # one step, not mid's
    assert set(P.preflight_tests(["tests/test_via_mid.py"], repo)) == g | {"tests/test_via_mid.py"}
    assert set(P.preflight_tests([], repo)) == g
    assert set(P.preflight_tests(["extended/core.py"], repo, direct_max=0)) == g             # too many: guards only


def test_an_import_module_call_is_a_direct_import(repo):
    assert "tests/test_dynamic.py" in P.preflight_tests(["extended/dyn.py"], repo)
    # a bare name, resolved through scripts/ as the suite's sys.path inserts make it: an import edge, never a name
    (repo / "tests" / "test_dynbare.py").write_text(
        "import importlib\n\n\ndef test_b():\n    assert importlib.import_module('dynbare').B == 5\n",
        encoding="utf-8")
    assert "tests/test_dynbare.py" in P.preflight_tests(["scripts/dynbare.py"], repo)


def test_a_dotted_import_reaches_through_each_package_init(repo):
    assert "tests/test_dotted.py" in P.preflight_tests(["extended/sub/__init__.py"], repo)
    assert "tests/test_dotted.py" in P.preflight_tests(["extended/sub/leaf.py"], repo)


def test_a_dotted_module_name_is_a_name(repo):
    assert "tests/test_runs_module.py" in P.preflight_tests(["extended/sub/leaf.py"], repo)


def test_a_listed_folder_sees_its_own_files_and_a_recursive_listing_its_nested_ones(repo):
    assert "tests/test_lists_reviews.py" in P.preflight_tests(["docs/reviews/R2.md"], repo)       # a direct child
    assert "tests/test_lists_reviews.py" not in P.preflight_tests(["docs/reviews/sub/R3.md"], repo)  # not recursive
    assert "tests/test_walks_plans.py" in P.preflight_tests(["docs/plans/deep/P1.md"], repo)     # rglob: nested
    assert "tests/test_walks_plans.py" not in P.preflight_tests(["docs/plans/deep/P1.txt"], repo)  # its pattern


def test_the_hooks_call_writes_the_list(repo, tmp_path, monkeypatch):
    monkeypatch.setattr(P, "ROOT", repo)
    monkeypatch.setattr(P, "staged", lambda root, index=None: ["tests/test_direct.py"])
    out = tmp_path / "pre.txt"
    assert P.main(["--out", str(out)]) == 0
    lines = out.read_text(encoding="utf-8").splitlines()
    assert "tests/test_direct.py" in lines and guards(repo) <= set(lines)


def test_a_failure_to_read_the_change_leaves_the_guards(repo, tmp_path, monkeypatch, capsys):
    def boom(*a, **k):
        raise RuntimeError("planted")

    monkeypatch.setattr(P, "ROOT", repo)
    monkeypatch.setattr(P, "staged", boom)
    out = tmp_path / "pre.txt"
    assert P.main(["--out", str(out)]) == 0
    assert set(out.read_text(encoding="utf-8").splitlines()) == guards(repo)
    assert "planted" in capsys.readouterr().err


# ------------------------------------------------------------------------------------------------ the real hook

STUB_OK = "import sys\nsys.exit(0)\n"


def clean_env(**extra) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_") and not k.startswith("S2X_")}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "1", "GIT_TERMINAL_PROMPT": "0"})
    env.update({k: str(v) for k, v in extra.items()})
    return env


def git(cwd: Path, *args: str, check: bool = True, env: dict | None = None,
        stdin: str | None = None) -> subprocess.CompletedProcess:
    p = subprocess.run(["git", "-c", "user.name=q209", "-c", "user.email=q209@example.invalid", *args], cwd=cwd,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=LIMIT,
                       env=env or clean_env(), input=stdin)
    if check and p.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}: {p.stdout}{p.stderr}")
    return p


@pytest.fixture()
def hooked(tmp_path):
    """A synthetic main repository and a linked worker worktree, with this tree's real pre-commit and commit-msg hooks,
    its real lock, pre-flight, runner and verdict checker, stub vendor and licence checks, a private lock folder, and
    the runner serial (S2X_FASTTIER_WORKERS=1)."""
    main = build(tmp_path / "main")
    (main / "scripts").mkdir(exist_ok=True)
    for rel in ("fasttier_lock.py", "fasttier_preflight.py", "fasttier_xdist.py", "check_verdicts.py", "run_lock.py"):
        (main / "scripts" / rel).write_bytes((SCRIPTS / rel).read_bytes())
    (main / "scripts" / "vendor_stage2.py").write_text(STUB_OK, encoding="utf-8")
    (main / "scripts" / "check_price_levels.py").write_text(STUB_OK, encoding="utf-8")
    (main / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    git(main, "init", "-q", "-b", "master")
    git(main, "add", "-A")
    git(main, "commit", "-q", "--no-verify", "-m", "base")
    for name in ("pre-commit", "commit-msg"):
        (main / ".git" / "hooks" / name).write_bytes((SCRIPTS / name).read_bytes())
    wt = tmp_path / "wt-x"
    git(main, "worktree", "add", "-q", "-b", "wt/x", str(wt))
    local = tmp_path / "localappdata"
    local.mkdir()
    sentinel = tmp_path / "sentinel.txt"
    env = clean_env(LOCALAPPDATA=local, PYTHON=sys.executable, GIT_PUSH_ON_COMMIT="0", S2X_FASTTIER_WORKERS="1",
                    Q209_SENTINEL=sentinel)
    return main, wt, env, sentinel


def _commit(tree: Path, env: dict, msg: str) -> subprocess.CompletedProcess:
    return git(tree, "commit", "-q", "-m", msg, check=False, env=env)


def _verdicts(main: Path) -> list[list[str]]:
    log = main / ".git" / "fasttier-verdicts.log"
    return [ln.split("\t") for ln in log.read_text(encoding="utf-8").splitlines()] if log.is_file() else []


def test_end_to_end_a_broken_guard_is_refused_by_the_preflight_and_the_full_tier_never_starts(hooked):
    main, wt, env, sentinel = hooked
    with open(wt / "DECISIONS.md", "a", encoding="utf-8", newline="\n") as f:
        f.write("| E-002 | 2026-11-21 | identity: BROKEN | basis |\n")
    git(wt, "add", "DECISIONS.md")
    head = git(wt, "rev-parse", "HEAD").stdout.strip()
    p = _commit(wt, env, "a broken record")
    out = p.stdout + p.stderr
    assert p.returncode != 0 and "pre-flight FAILED" in out and "test_the_log_has_no_broken_token" in out, out
    assert "the full fast tier did not start" in out
    assert git(wt, "rev-parse", "HEAD").stdout.strip() == head
    assert not sentinel.exists(), "the full fast tier ran after a failed pre-flight"


@pytest.mark.parametrize("where", ["main", "worker"])
def test_end_to_end_every_commit_runs_the_preflight_and_then_the_full_tier(hooked, where):
    main, wt, env, sentinel = hooked
    tree = main if where == "main" else wt
    (tree / "extended" / "core.py").write_text("def f():\n    return 1  # touched\n", encoding="utf-8", newline="\n")
    git(tree, "add", "extended/core.py")
    p = _commit(tree, env, f"a {where} code change")
    out = p.stdout + p.stderr
    assert p.returncode == 0, out
    assert "pre-flight passed; the full fast tier follows" in out, out
    assert sentinel.read_text(encoding="utf-8").count("ran") == 1, "the full fast tier did not run"
    t = git(tree, "rev-parse", "HEAD^{tree}").stdout.strip()
    rec = [r for r in _verdicts(main) if r[0] == t][-1]
    assert rec[-1] == "tier=T2"
    total = len(list((tree / "tests").glob("test_*.py")))
    assert rec[3].startswith(f"{total} passed"), rec           # the whole suite: every test file holds one test


def test_end_to_end_a_hunk_left_unstaged_by_add_p_is_refused(hooked):
    main, _, env, sentinel = hooked
    lines = FILES["long.txt"].splitlines(keepends=True)
    lines[0], lines[-1] = "line 0 changed\n", "line 39 changed\n"   # two hunks, far apart
    (main / "long.txt").write_text("".join(lines), encoding="utf-8", newline="\n")
    git(main, "add", "-p", "long.txt", stdin="y\nn\n")              # the first hunk staged, the second left
    assert git(main, "diff", "--name-only").stdout.split() == ["long.txt"]
    assert git(main, "diff", "--cached", "--name-only").stdout.split() == ["long.txt"]
    p = _commit(main, env, "a partial stage")
    out = p.stdout + p.stderr
    assert p.returncode != 0 and "work tree differs from the commit" in out and "unstaged  long.txt" in out, out
    assert not sentinel.exists()
    git(main, "add", "long.txt")                                    # the whole change staged: it goes through
    p = _commit(main, env, "the whole change")
    assert p.returncode == 0, p.stdout + p.stderr


def test_end_to_end_an_untracked_module_is_refused_and_a_top_level_log_is_not(hooked):
    main, _, env, _ = hooked
    (main / "extended" / "core.py").write_text("from extended import new\n\n\ndef f():\n    return new.ONE\n",
                                               encoding="utf-8", newline="\n")
    (main / "extended" / "new.py").write_text("ONE = 1\n", encoding="utf-8", newline="\n")   # forgotten: not added
    (main / "commit.log").write_text("a worker's commit log\n", encoding="utf-8")
    git(main, "add", "extended/core.py")
    p = _commit(main, env, "a module not added")
    out = p.stdout + p.stderr
    assert p.returncode != 0 and "untracked extended/new.py" in out and "commit.log" not in out, out
    git(main, "add", "extended/new.py")
    p = _commit(main, env, "the module added")
    assert p.returncode == 0, p.stdout + p.stderr


# ------------------------------------------------------------------------------------------------ fasttier_full.py

def test_fasttier_full_refuses_any_untracked_file_but_a_top_level_log_and_records_t2_on_a_clean_tip(hooked):
    """The red team's F12: an untracked file anywhere (a test may read any file) makes the tree not HEAD; a log at the
    top of the tree does not. On a clean tip the full tier's verdict is recorded as T2 for HEAD's tree."""
    main, _, env, _ = hooked
    import fasttier_full as FF
    (main / "docs" / "notes.txt").write_text("untracked\n", encoding="utf-8")
    (main / "commit.log").write_text("a log\n", encoding="utf-8")
    assert FF.dirt(main) == ["untracked docs/notes.txt"]
    assert FF.main([], runner=lambda c, e: 0, root=main) == FF.EXIT_DIRTY
    (main / "docs" / "notes.txt").unlink()
    assert FF.dirt(main) == []
    ran = []
    assert FF.main([], runner=lambda c, e: ran.append(c) or 0, root=main) == 0 and len(ran) == 1
    tree = git(main, "rev-parse", "HEAD^{tree}").stdout.strip()
    rec = [r for r in _verdicts(main) if r[0] == tree][-1]
    assert "tier=T2" in rec
    assert FF.main([], runner=lambda c, e: ran.append(c) or 0, root=main) == 0 and len(ran) == 1   # already verified
