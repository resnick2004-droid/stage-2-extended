"""Q-209: the tiered pre-commit fast tier -- scripts/fasttier_select.py's tiers and selection, on synthetic repositories.

* each tier's selection: T1 by the import graph (direct importers, importers through extended/, a test that runs a
  script that imports the changed module), T0 for records only, T2 for the main tree's code, merges and every fallback;
* a planted break in a module that only an indirect importer tests is caught by the T1 selection;
* a records-only commit with a broken identity token is refused by T0, end to end through the real pre-commit hook
  (its vendor and licence steps stubbed, the fast-tier lock pointed at a private folder), and a worker's code commit is
  verified as T1, a main-tree code commit as T2, each tier written in the verdict line;
* each fallback triggers; the declared walk scopes cover every walking source of this repository.
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

import fasttier_select as S  # noqa: E402

LIMIT = 600

FILES = {
    "extended/__init__.py": "",
    "extended/core.py": "def f():\n    return 1\n",
    "extended/mid.py": "from extended import core\n\n\ndef g():\n    return core.f()\n",
    "extended/deep.py": "def h():\n    return 'ok'\n",
    "extended/unrelated.py": "def u():\n    return 0\n",
    "extended/cfg.py": textwrap.dedent('''\
        from pathlib import Path
        ROOT = Path(__file__).resolve().parent.parent


        def load():
            return (ROOT / "config" / "known.yaml").read_text(encoding="utf-8")
        '''),
    "scripts/tool.py": textwrap.dedent('''\
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from extended import deep
        print(deep.h())
        '''),
    "tests/test_direct.py": "from extended import core\n\n\ndef test_f():\n    assert core.f() == 1\n",
    "tests/test_via_mid.py": "from extended import mid\n\n\ndef test_g():\n    assert mid.g() == 1\n",
    "tests/test_indirect.py": textwrap.dedent('''\
        import subprocess
        import sys
        from pathlib import Path
        ROOT = Path(__file__).resolve().parent.parent


        def test_the_tool_says_ok():
            out = subprocess.run([sys.executable, str(ROOT / "scripts" / "tool.py")], capture_output=True, text=True)
            assert out.stdout.strip() == "ok", out.stdout + out.stderr
        '''),
    "tests/test_other.py": "import helper_x\n\n\ndef test_u():\n    assert helper_x.X == 1\n",
    "tests/helper_x.py": "X = 1\n",
    "tests/test_cfg.py": "from extended import cfg\n\n\ndef test_load():\n    assert cfg.load()\n",
    "tests/test_identity_tokens.py": textwrap.dedent('''\
        from pathlib import Path
        ROOT = Path(__file__).resolve().parent.parent


        def test_the_log_has_no_broken_token():
            assert "identity: BROKEN" not in (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
        '''),
    "config/known.yaml": "a: 1\n",
    # a script named by its file name only, run from its folder
    "extended/solo.py": "def s():\n    return 0\n",
    "scripts/tool2.py": "import sys\nsys.path.insert(0, '..')\nfrom extended import solo\nprint(solo.s())\n",
    "tests/test_by_name.py": textwrap.dedent('''\
        import subprocess
        import sys
        from pathlib import Path
        HERE = Path(__file__).resolve().parent.parent


        def test_tool2_prints_zero():
            out = subprocess.run([sys.executable, "tool2.py"], cwd=HERE / "scripts", capture_output=True, text=True)
            assert out.stdout.strip() == "0", out.stdout + out.stderr
        '''),
    # a sub-package imported only by its dotted name
    "extended/sub/__init__.py": "",
    "extended/sub/leaf.py": "V = 3\n",
    "tests/test_leaf.py": "import extended.sub.leaf as L\n\n\ndef test_v():\n    assert L.V == 3\n",
    # a walker bounded by its declared scope (WALK_SCOPES: *.csv, *.tsv), and a reader of what it returns
    "extended/price_levels.py": "def tracked():\n    return ['git', 'ls-files']\n",
    "tests/test_levels.py": "from extended import price_levels\n\n\ndef test_t():\n    assert price_levels.tracked()\n",
    "DECISIONS.md": "# log\n| E-001 | 2026-11-21 | a row | basis |\n",
    "docs/reviews/R1.md": "a review\n",
    "STATUS.md": "status\n",
}
#: the always-run guards, as trivial passing tests in the synthetic repository
GUARDS = sorted(set(S.ALWAYS) | {p for p in S.T0_ALWAYS if "*" not in p})
PASS = "def test_ok():\n    assert True\n"


def clean_env(**extra) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_") and not k.startswith("S2X_")}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "1", "GIT_TERMINAL_PROMPT": "0"})
    env.update({k: str(v) for k, v in extra.items()})
    return env


def git(cwd: Path, *args: str, check: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    p = subprocess.run(["git", "-c", "user.name=q209", "-c", "user.email=q209@example.invalid", *args], cwd=cwd,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=LIMIT,
                       env=env or clean_env())
    if check and p.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}: {p.stdout}{p.stderr}")
    return p


def build(root: Path, files: dict[str, str] = FILES) -> Path:
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8", newline="\n")
    for rel in GUARDS:
        if not (root / rel).exists():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(PASS, encoding="utf-8", newline="\n")
    return root


@pytest.fixture()
def repo(tmp_path, monkeypatch) -> Path:
    monkeypatch.setattr(S, "FULL_FRACTION", 1.0)            # a small repository: the share rule has its own test
    return build(tmp_path / "r")


def decide(repo: Path, changed, main_tree=False, merging=False) -> S.Decision:
    return S.decide(list(changed), main_tree=main_tree, merging=merging, root=repo)


def guards() -> set[str]:
    return set(S.ALWAYS)


# ------------------------------------------------------------------------------------------------ the tiers

def test_t1_selects_direct_importers_importers_through_extended_and_runners_of_an_importing_script(repo):
    d = decide(repo, ["extended/core.py"])
    assert d.tier == "T1", d
    assert set(d.tests) == {"tests/test_direct.py", "tests/test_via_mid.py"} | guards(), d.tests
    d = decide(repo, ["extended/deep.py"])                    # imported only by a script that a test runs
    assert set(d.tests) == {"tests/test_indirect.py"} | guards(), d.tests
    d = decide(repo, ["scripts/tool.py"])
    assert set(d.tests) == {"tests/test_indirect.py"} | guards(), d.tests


def test_t1_selects_a_changed_test_its_helpers_importers_and_the_readers_of_a_named_file(repo):
    assert set(decide(repo, ["tests/test_other.py"]).tests) == {"tests/test_other.py"} | guards()
    assert set(decide(repo, ["tests/helper_x.py"]).tests) == {"tests/test_other.py"} | guards()
    assert set(decide(repo, ["config/known.yaml"]).tests) == {"tests/test_cfg.py"} | guards()
    assert set(decide(repo, ["extended/unrelated.py"]).tests) == guards()


def test_t1_names_a_script_by_its_file_name_alone(repo):
    assert "tests/test_by_name.py" in decide(repo, ["scripts/tool2.py"]).tests


def test_t1_follows_a_dotted_import_through_each_package_init(repo):
    assert "tests/test_leaf.py" in decide(repo, ["extended/sub/__init__.py"]).tests
    assert "tests/test_leaf.py" in decide(repo, ["extended/sub/leaf.py"]).tests


def test_a_declared_walk_scope_bounds_the_walker(repo):
    assert "extended/price_levels.py" in S.WALK_SCOPES and S.Graph(repo).sources["extended/price_levels.py"].wide
    assert "tests/test_levels.py" not in decide(repo, ["extended/core.py"]).tests       # outside its scope
    (repo / "results").mkdir()
    (repo / "results" / "x.csv").write_text("a\n1\n", encoding="utf-8")
    d = decide(repo, ["results/x.csv"])                                                 # inside it: selected, placed
    assert d.tier == "T1" and "tests/test_levels.py" in d.tests, d


def test_t1_follows_a_package_init_to_every_importer(repo):
    d = decide(repo, ["extended/__init__.py"])
    assert {"tests/test_direct.py", "tests/test_via_mid.py", "tests/test_cfg.py", "tests/test_indirect.py"} <= set(
        d.tests), d.tests


def test_t0_for_records_only_runs_the_record_readers(repo):
    d = decide(repo, ["DECISIONS.md", "docs/reviews/R1.md", "STATUS.md"])
    assert d.tier == "T0", d
    assert "tests/test_identity_tokens.py" in d.tests
    assert {p for p in S.T0_ALWAYS if "*" not in p} <= set(d.tests)
    assert "tests/test_direct.py" not in d.tests
    assert decide(repo, ["docs/plans/x/y.md"]).tier == "T0"
    assert decide(repo, ["DECISIONS.md", "extended/core.py"]).tier == "T1"      # one code path: not records only


def test_t0_in_the_main_tree_too_but_its_code_commits_are_t2(repo):
    assert decide(repo, ["DECISIONS.md"], main_tree=True).tier == "T0"
    d = decide(repo, ["extended/core.py"], main_tree=True)
    assert d.tier == "T2" and "main tree" in d.reason


def test_a_merge_commit_is_t2(repo):
    assert decide(repo, ["extended/core.py"], merging=True).tier == "T2"
    assert decide(repo, ["DECISIONS.md"], merging=True).tier == "T2"


def test_a_selection_over_the_share_runs_the_full_tier(repo, monkeypatch):
    monkeypatch.setattr(S, "FULL_FRACTION", 0.1)
    d = decide(repo, ["extended/core.py"])
    assert d.tier == "T2" and "over" in d.reason


@pytest.mark.parametrize("path", ["conftest.py", "tests/conftest.py", "pyproject.toml", ".gitattributes",
                                  "scripts/pre-commit", "scripts/commit-msg", "scripts/post-commit",
                                  "scripts/pre-merge-commit", "scripts/install_hooks.py", "scripts/hooks/guard.py",
                                  "scripts/fasttier_lock.py", "scripts/fasttier_select.py", "extended/fasttier_report.py",
                                  "vendor/stage2/x.py", ".claude/settings.json"])
def test_each_fallback_path_runs_the_full_tier(repo, path):
    d = decide(repo, ["extended/core.py", path])
    assert d.tier == "T2" and d.reason.startswith("fallback"), d


def test_a_python_file_that_does_not_parse_falls_back(repo):
    (repo / "extended" / "core.py").write_text("def f(:\n", encoding="utf-8")
    d = decide(repo, ["extended/core.py"])
    assert d.tier == "T2" and "does not parse" in d.reason


def test_a_new_test_helper_no_test_reaches_falls_back(repo):
    (repo / "tests" / "helper_new.py").write_text("Y = 2\n", encoding="utf-8")
    d = decide(repo, ["tests/helper_new.py"])
    assert d.tier == "T2" and "cannot place" in d.reason
    (repo / "tests" / "test_new.py").write_text("import helper_new\n\n\ndef test_y():\n    assert helper_new.Y\n",
                                                encoding="utf-8")
    d = decide(repo, ["tests/helper_new.py", "tests/test_new.py"])
    assert d.tier == "T1" and "tests/test_new.py" in d.tests


def test_a_new_test_file_is_selected_itself(repo):
    (repo / "tests" / "test_brand_new.py").write_text(PASS, encoding="utf-8")
    d = decide(repo, ["tests/test_brand_new.py"])
    assert d.tier == "T1" and "tests/test_brand_new.py" in d.tests


def test_an_unnamed_config_prereg_or_identity_file_falls_back(repo):
    for rel in ("config/unnamed.yaml", "prereg/F-99_x.md", "identity/nothing.txt"):
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text("x\n", encoding="utf-8")
        d = decide(repo, [rel])
        assert d.tier == "T2" and "cannot place" in d.reason, (rel, d)


def test_a_selector_error_falls_back_in_the_hooks_call(repo, monkeypatch, capsys):
    def boom(*a, **k):
        raise RuntimeError("planted")

    monkeypatch.setattr(S, "staged", boom)
    assert S.main(["--hook"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "T2" and "selector failed" in out[1] and "planted" in out[1]


def test_nothing_staged_is_t2(repo):
    assert decide(repo, []).tier == "T2"


# ------------------------------------------------------------------------------------------------ a planted break is caught

def _pytest(repo: Path, tests: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-o", "addopts=", "-p", "no:cacheprovider",
                           "-m", "not slow and not heavy", *tests], cwd=repo, capture_output=True, text=True,
                          timeout=LIMIT, env=clean_env())


def test_a_break_in_a_module_only_an_indirect_importer_tests_is_caught_by_t1(repo):
    (repo / "extended" / "deep.py").write_text("def h():\n    return 'broken'\n", encoding="utf-8")
    d = decide(repo, ["extended/deep.py"])
    assert d.tier == "T1" and "tests/test_indirect.py" in d.tests
    p = _pytest(repo, d.tests)
    assert p.returncode == 1 and "test_the_tool_says_ok" in p.stdout, p.stdout + p.stderr
    # and the direct tests alone would have missed it
    assert _pytest(repo, ["tests/test_direct.py", "tests/test_via_mid.py"]).returncode == 0


# ------------------------------------------------------------------------------------------------ the real hook, end to end

STUB_OK = "import sys\nsys.exit(0)\n"


@pytest.fixture()
def hooked(tmp_path, monkeypatch):
    """A synthetic main repository and a linked worker worktree, with this tree's real pre-commit and commit-msg hooks,
    the real fasttier_lock / fasttier_select / check_verdicts, stub vendor and licence checks, and a private lock."""
    monkeypatch.setattr(S, "FULL_FRACTION", 1.0)
    main = build(tmp_path / "main")
    for rel in ("fasttier_lock.py", "fasttier_select.py", "check_verdicts.py", "run_lock.py"):
        (main / "scripts" / rel).write_bytes((SCRIPTS / rel).read_bytes())
    (main / "scripts" / "vendor_stage2.py").write_text(STUB_OK, encoding="utf-8")
    (main / "scripts" / "check_price_levels.py").write_text(STUB_OK, encoding="utf-8")
    # the synthetic tree is small: let any T1 run (the share rule is the real tree's)
    sel = main / "scripts" / "fasttier_select.py"
    sel.write_text(sel.read_text(encoding="utf-8").replace("FULL_FRACTION = 0.6", "FULL_FRACTION = 1.0"),
                   encoding="utf-8", newline="\n")
    git(main, "init", "-q", "-b", "master")
    git(main, "add", "-A")
    git(main, "commit", "-q", "--no-verify", "-m", "base")
    hooks = main / ".git" / "hooks"
    for name in ("pre-commit", "commit-msg"):
        (hooks / name).write_bytes((SCRIPTS / name).read_bytes())
    wt = tmp_path / "wt-x"
    git(main, "worktree", "add", "-q", "-b", "wt/x", str(wt))
    local = tmp_path / "localappdata"
    local.mkdir()
    env = clean_env(LOCALAPPDATA=local, PYTHON=sys.executable, GIT_PUSH_ON_COMMIT="0")
    return main, wt, env


def _commit(tree: Path, env: dict, msg: str) -> subprocess.CompletedProcess:
    return git(tree, "commit", "-q", "-m", msg, check=False, env=env)


def _verdicts(main: Path) -> list[list[str]]:
    log = main / ".git" / "fasttier-verdicts.log"
    return [ln.split("\t") for ln in log.read_text(encoding="utf-8").splitlines()] if log.is_file() else []


def test_end_to_end_t0_refuses_a_broken_token_and_passes_a_clean_record(hooked):
    main, _, env = hooked
    with open(main / "DECISIONS.md", "a", encoding="utf-8", newline="\n") as f:
        f.write("| E-002 | 2026-11-21 | identity: BROKEN | basis |\n")
    git(main, "add", "DECISIONS.md")
    head = git(main, "rev-parse", "HEAD").stdout.strip()
    p = _commit(main, env, "a broken record")
    out = p.stdout + p.stderr
    assert p.returncode != 0, out
    assert "tier T0" in out and "test_the_log_has_no_broken_token" in out, out
    assert git(main, "rev-parse", "HEAD").stdout.strip() == head
    assert (Path(env["LOCALAPPDATA"]) / "stage2-extended-fasttier-t0.lock.queue").is_dir(), "T0 ran in its own lane"
    (main / "DECISIONS.md").write_text(FILES["DECISIONS.md"] + "| E-002 | 2026-11-21 | a clean row | basis |\n",
                                       encoding="utf-8", newline="\n")
    git(main, "add", "DECISIONS.md")
    p = _commit(main, env, "a clean record")
    assert p.returncode == 0, p.stdout + p.stderr
    tree = git(main, "rev-parse", "HEAD^{tree}").stdout.strip()
    assert [r for r in _verdicts(main) if r[0] == tree][-1][-1] == "tier=T0"


def test_end_to_end_a_worker_code_commit_is_t1_and_the_main_trees_is_t2(hooked):
    main, wt, env = hooked
    (wt / "extended" / "core.py").write_text("def f():\n    return 1  # touched\n", encoding="utf-8", newline="\n")
    git(wt, "add", "extended/core.py")
    p = _commit(wt, env, "a worker's change")
    out = p.stdout + p.stderr
    assert p.returncode == 0 and "tier T1" in out, out
    tree = git(wt, "rev-parse", "HEAD^{tree}").stdout.strip()
    rec = [r for r in _verdicts(main) if r[0] == tree][-1]
    assert rec[-1] == "tier=T1"
    # exactly the selection ran (each synthetic test file holds one test), not the whole suite
    selected = S.decide(["extended/core.py"], main_tree=False, merging=False, root=wt).tests
    total = len(list((wt / "tests").glob("test_*.py")))
    assert rec[3].startswith(f"{len(selected)} passed") and len(selected) < total, (rec, selected)
    assert "fasttier_full.py" in out                         # the hand-back reminder
    (main / "extended" / "unrelated.py").write_text("def u():\n    return 0  # touched\n", encoding="utf-8",
                                                     newline="\n")
    git(main, "add", "extended/unrelated.py")
    p = _commit(main, env, "the main tree's change")
    out = p.stdout + p.stderr
    assert p.returncode == 0 and "tier T2" in out, out
    tree = git(main, "rev-parse", "HEAD^{tree}").stdout.strip()
    assert [r for r in _verdicts(main) if r[0] == tree][-1][-1] == "tier=T2"


def test_end_to_end_t1_refuses_a_planted_indirect_break(hooked):
    _, wt, env = hooked
    (wt / "extended" / "deep.py").write_text("def h():\n    return 'broken'\n", encoding="utf-8", newline="\n")
    git(wt, "add", "extended/deep.py")
    p = _commit(wt, env, "a planted break")
    out = p.stdout + p.stderr
    assert p.returncode != 0 and "tier T1" in out and "test_the_tool_says_ok" in out, out


# ------------------------------------------------------------------------------------------------ this repository

def test_every_walking_source_of_this_repository_has_a_declared_scope_or_reason():
    g = S.Graph(ROOT)
    wide = {r for r, s in g.sources.items() if s.wide and not S.is_test_file(r)}
    declared = set(S.WALK_SCOPES) | set(S.WALK_UNSCOPED)
    assert wide <= declared, f"a new walk the graph cannot bound: {sorted(wide - declared)}"
    assert all((ROOT / r).is_file() for r in declared), "a stale entry"
    assert not set(S.WALK_SCOPES) & set(S.WALK_UNSCOPED)


def test_on_this_repository_a_record_change_is_t0_with_its_named_readers():
    d = S.decide(["DECISIONS.md"], main_tree=True, merging=False, root=ROOT)
    assert d.tier == "T0"
    for p in ("tests/test_identity_tokens.py", "tests/test_declarations_fixed.py", "tests/test_reader.py",
              "tests/test_reader_heldout.py", "tests/test_vendor_integrity.py", "tests/test_seed_derivation_guard.py",
              "tests/test_trace_check.py", "tests/test_archive_queue.py", "tests/test_status.py"):
        assert p in d.tests, p


def test_on_this_repository_the_selector_is_t2_for_its_own_change():
    d = S.decide(["scripts/fasttier_select.py"], main_tree=False, merging=False, root=ROOT)
    assert d.tier == "T2" and d.reason.startswith("fallback")


# ------------------------------------------------------------------------------------------------ the pre-flight (E-274)

def test_the_preflight_is_the_guards_the_staged_tests_and_the_direct_tests_when_few(repo):
    guards = set(S._expand(repo, S.PREFLIGHT_GUARDS))
    assert "tests/test_identity_tokens.py" in guards and "tests/test_vendor_integrity.py" in guards
    pre = set(S.preflight_tests(["extended/core.py"], repo))
    assert pre == guards | {"tests/test_direct.py"}           # one step only: test_via_mid reaches core through mid
    assert set(S.preflight_tests(["tests/test_other.py"], repo)) == guards | {"tests/test_other.py"}
    assert set(S.preflight_tests(["extended/core.py"], repo, direct_max=0)) == guards     # too many: the guards
    assert set(S.preflight_tests([], repo)) == guards


def test_the_hooks_call_writes_the_preflight(repo, tmp_path, monkeypatch):
    monkeypatch.setattr(S, "ROOT", repo)
    monkeypatch.setattr(S, "staged", lambda root, index=None: ["tests/test_other.py"])
    monkeypatch.setattr(S, "is_main", lambda root: False)
    monkeypatch.setattr(S, "merging", lambda root: False)
    out, pre = tmp_path / "sel.txt", tmp_path / "pre.txt"
    assert S.main(["--hook", "--out", str(out), "--preflight-out", str(pre)]) == 0
    assert "tests/test_other.py" in pre.read_text(encoding="utf-8").splitlines()
    assert set(S._expand(repo, S.PREFLIGHT_GUARDS)) <= set(pre.read_text(encoding="utf-8").splitlines())


def test_end_to_end_a_broken_guard_is_refused_at_the_preflight_before_the_line(hooked):
    main, wt, env = hooked
    with open(wt / "DECISIONS.md", "a", encoding="utf-8", newline="\n") as f:
        f.write("| E-003 | 2026-11-21 | identity: BROKEN | basis |\n")
    (wt / "extended" / "core.py").write_text("def f():\n    return 1  # touched\n", encoding="utf-8", newline="\n")
    git(wt, "add", "DECISIONS.md", "extended/core.py")
    head = git(wt, "rev-parse", "HEAD").stdout.strip()
    p = _commit(wt, env, "a code commit beside a broken record")
    out = p.stdout + p.stderr
    assert p.returncode != 0 and "pre-flight FAILED" in out and "test_the_log_has_no_broken_token" in out, out
    assert git(wt, "rev-parse", "HEAD").stdout.strip() == head
    local = Path(env["LOCALAPPDATA"])
    assert (local / "stage2-extended-fasttier-t0.lock.queue").is_dir(), "the pre-flight ran in the T0 lane"
    assert not (local / "stage2-extended-fasttier.lock.queue").exists(), "the tier's stage never joined the line"
