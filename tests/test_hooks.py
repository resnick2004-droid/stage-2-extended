"""The Claude Code hooks in `.claude/settings.json` deny, warn and allow what they claim to.

A hook is configuration, and configuration drifts silently: a renamed script, a changed payload field, a typo in a
path, and the guard stops firing while the settings file still looks correct. These tests invoke each hook the way
Claude Code does -- a JSON payload on stdin -- and check the exit code (2 denies with the reason on stderr; 0 allows).

Worktrees and clean checkouts live outside this folder, so the vendor and results guards are also exercised on a fake
tree in a temporary directory: a folder holding a `.git` *file* (a worktree) or a `.git` directory (a repository).

`scripts/hooks/run_tests.py` is never exercised on a `.py` payload inside this repository: it runs pytest, and calling
it from inside pytest would recurse. Its ignore paths are tested.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / "scripts" / "hooks"
SETTINGS = ROOT / ".claude" / "settings.json"

DENY = 2
ALLOW = 0


def invoke(hook: str, payload: dict) -> tuple[int, str, str]:
    proc = subprocess.run([sys.executable, str(HOOKS / hook)], input=json.dumps(payload), capture_output=True,
                          text=True, timeout=120, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return proc.returncode, proc.stdout, proc.stderr


def pre(tool: str, path: str, cwd: Path = ROOT, **extra) -> dict:
    key = "notebook_path" if tool == "NotebookEdit" else "file_path"
    return {"tool_name": tool, "cwd": str(cwd), "tool_input": {key: path, **extra}}


@pytest.fixture
def worktree(tmp_path: Path) -> Path:
    """A fake linked worktree: a `.git` file, a vendor/ and a results/ folder."""
    wt = tmp_path / "stage2-extended-wt" / "wt-test"
    (wt / "vendor" / "stage2").mkdir(parents=True)
    (wt / "results").mkdir()
    (wt / ".git").write_text("gitdir: C:/somewhere/.git/worktrees/wt-test\n", encoding="utf-8")
    return wt


# ------------------------------------------------------------------ settings


def _commands() -> list[str]:
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    return [h["command"] for event in settings["hooks"].values() for group in event for h in group["hooks"]]


def test_settings_reference_hooks_that_exist():
    commands = _commands()
    assert commands, "no hooks configured"
    for cmd in commands:
        name = cmd.split("/")[-1].strip('"')
        assert (HOOKS / name).is_file(), f"settings.json references missing hook script {name}"


def test_every_hook_is_wired_and_the_live_tools_denied():
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    commands = " ".join(_commands())
    for name in ("protect_vendor.py", "protect_results.py", "decisions_append_only.py", "run_tests.py",
                 "qc_no_live_trading.py", "qc_window_guard.py"):
        assert name in commands, f"{name} is not wired into settings.json"
    deny = set(settings["permissions"]["deny"])
    sys.path.insert(0, str(HOOKS))
    try:
        import qc_no_live_trading as Q
    finally:
        sys.path.pop(0)
    assert {f"mcp__quantconnect__{t}" for t in Q.LIVE_TOOLS} <= deny
    assert settings["env"]["PYTHONDONTWRITEBYTECODE"] == "1"


# ------------------------------------------------------------ protect_vendor


@pytest.mark.parametrize("tool", ["Write", "Edit", "MultiEdit", "NotebookEdit"])
def test_writes_into_this_trees_vendor_are_denied(tool):
    code, _, err = invoke("protect_vendor.py", pre(tool, "vendor/stage2/propedge/campaign/gate.py"))
    assert code == DENY, f"{tool} into vendor/ was allowed"
    assert "READ-ONLY" in err and "E-002" in err


@pytest.mark.parametrize("rel", ["vendor/stage2/vendor/propsim/propsim.py", "vendor/MANIFEST_stage2.sha256",
                                 "vendor/stage2/data/bars/NQ/x.parquet", "vendor/stage2/results/user_journey.csv"])
def test_absolute_paths_under_vendor_are_denied(rel):
    code, _, err = invoke("protect_vendor.py", pre("Edit", str(ROOT / rel), cwd=Path.home()))
    assert code == DENY, rel
    assert "extended/" in err, "the denial should say what to do instead"


def test_a_worktrees_vendor_is_denied(worktree):
    code, _, _ = invoke("protect_vendor.py", pre("Write", str(worktree / "vendor" / "stage2" / "CLAUDE.md")))
    assert code == DENY


def test_a_repositorys_vendor_is_denied(tmp_path):
    repo = tmp_path / "clone"
    (repo / ".git").mkdir(parents=True)
    code, _, _ = invoke("protect_vendor.py", pre("Write", str(repo / "vendor" / "x.py")))
    assert code == DENY


def test_a_vendor_folder_outside_any_tree_root_is_allowed(tmp_path):
    code, _, _ = invoke("protect_vendor.py", pre("Write", str(tmp_path / "notes" / "vendor" / "x.py")))
    assert code == ALLOW


@pytest.mark.parametrize("path", ["extended/results.py", "docs/notes.md", "scripts/vendor_stage2.py",
                                  "config/rules_extended.yaml"])
def test_writes_elsewhere_are_allowed(path):
    code, _, _ = invoke("protect_vendor.py", pre("Write", path))
    assert code == ALLOW, f"{path} was wrongly denied"


def test_reads_of_vendor_are_allowed():
    code, _, _ = invoke("protect_vendor.py", pre("Read", "vendor/stage2/propedge/__init__.py"))
    assert code == ALLOW


@pytest.mark.parametrize("payload", [{}, {"nonsense": 1}, {"tool_name": "Write"}, {"tool_name": "Write",
                                                                                  "tool_input": {}}])
def test_vendor_hook_fails_open_on_unexpected_input(payload):
    code, _, _ = invoke("protect_vendor.py", payload)
    assert code == ALLOW


# ----------------------------------------------------------- protect_results


@pytest.mark.parametrize("path", ["results/f01_stage_a.csv", "results/f01_stage_a.csv.manifest.json"])
def test_direct_writes_to_results_are_denied(path):
    code, _, err = invoke("protect_results.py", pre("Write", path))
    assert code == DENY
    assert "never hand-edited" in err and "extended.results" in err


@pytest.mark.parametrize("name", ["README.md", "variants.jsonl", ".gitkeep", ".last_test_run.json",
                                  "read_ledger.jsonl"])
def test_bookkeeping_files_under_results_are_allowed(name):
    code, _, _ = invoke("protect_results.py", pre("Write", f"results/{name}"))
    assert code == ALLOW, f"results/{name} must remain writable"


LEDGER = '{"n":1}\n{"n":2}\n'


@pytest.mark.parametrize("tool,extra", [
    ("Write", {"content": '{"n":1}\n{"n":20}\n'}),                       # a line rewritten
    ("Write", {"content": ""}),                                           # the ledger emptied
    ("Edit", {"old_string": '{"n":2}', "new_string": '{"n":3}'}),         # a line replaced
    ("MultiEdit", {"edits": [{"old_string": '{"n":1}\n', "new_string": ""}]}),
])
def test_a_read_ledger_rewrite_is_allowed_but_made_visible(worktree, tool, extra):
    """Q-32: the read ledger is append-only. The hook lets a write through (the brief: the ledger is a file
    `protect_results.py` allows) and says, to the user and to Claude, that existing lines were changed;
    `tests/test_reader.py`'s history check is the proof."""
    led = worktree / "results" / "read_ledger.jsonl"
    led.write_text(LEDGER, encoding="utf-8")
    code, out, _ = invoke("protect_results.py", pre(tool, str(led), **extra))
    assert code == ALLOW
    msg = json.loads(out)
    assert "append-only" in msg["systemMessage"] and "read_ledger.jsonl" in msg["systemMessage"]
    assert msg["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


@pytest.mark.parametrize("tool,extra", [
    ("Write", {"content": LEDGER + '{"n":3}\n'}),
    ("Edit", {"old_string": '{"n":2}\n', "new_string": '{"n":2}\n{"n":3}\n'}),
])
def test_a_read_ledger_append_is_silent(worktree, tool, extra):
    led = worktree / "results" / "read_ledger.jsonl"
    led.write_text(LEDGER, encoding="utf-8")
    code, out, _ = invoke("protect_results.py", pre(tool, str(led), **extra))
    assert code == ALLOW and out.strip() == ""


def test_a_new_read_ledger_is_silent(worktree):
    code, out, _ = invoke("protect_results.py", pre("Write", str(worktree / "results" / "read_ledger.jsonl"),
                                                    content='{"n":1}\n'))
    assert code == ALLOW and out.strip() == ""


def test_a_worktrees_results_are_denied(worktree):
    code, _, _ = invoke("protect_results.py", pre("Edit", str(worktree / "results" / "x.csv")))
    assert code == DENY
    code, _, _ = invoke("protect_results.py", pre("Write", str(worktree / "results" / "variants.jsonl")))
    assert code == ALLOW


@pytest.mark.parametrize("path", ["docs/table.csv", "extended/fixtures/x.csv"])
def test_csvs_outside_results_are_allowed(path):
    code, _, _ = invoke("protect_results.py", pre("Write", path))
    assert code == ALLOW


# ------------------------------------------------------ decisions_append_only

ROW4 = "| E-004 | 2026-11-16 | **E-002's identity read at every registered path** ... | E-002 |"


def test_rewriting_an_existing_row_warns():
    code, out, _ = invoke("decisions_append_only.py",
                          pre("Edit", "DECISIONS.md", old_string=ROW4, new_string=ROW4.replace("every", "some")))
    assert code == ALLOW, "the append-only rule warns; it never blocks"
    msg = json.loads(out)
    assert "append-only" in msg["systemMessage"] and "E-004" in msg["systemMessage"]
    assert "/decide" in msg["systemMessage"]
    assert msg["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_an_append_anchored_on_the_last_row_is_silent(tmp_path):
    # A stand-in for the main tree (`.git` a directory), so the test holds whichever tree the suite runs in -- from a
    # worktree (`.git` a file) the hook rightly adds its single-writer warning (E-008: this test failed in every
    # worktree and refused their commits).
    main = tmp_path / "main"
    (main / ".git").mkdir(parents=True)
    new = ROW4 + "\n| E-006 | 2026-11-16 | **new** | basis |"
    code, out, _ = invoke("decisions_append_only.py",
                          pre("Edit", str(main / "DECISIONS.md"), cwd=main, old_string=ROW4, new_string=new))
    assert code == ALLOW
    assert out.strip() == ""


def test_a_multiedit_that_removes_a_row_warns():
    code, out, _ = invoke("decisions_append_only.py", pre("MultiEdit", "DECISIONS.md",
                                                          edits=[{"old_string": ROW4, "new_string": ""}]))
    assert code == ALLOW
    assert "E-004" in json.loads(out)["systemMessage"]


def test_a_whole_file_write_warns():
    code, out, _ = invoke("decisions_append_only.py", pre("Write", "DECISIONS.md", content="x"))
    assert code == ALLOW
    assert "wholesale" in json.loads(out)["systemMessage"]


def test_a_write_in_a_worktree_warns_single_writer(worktree):
    code, out, _ = invoke("decisions_append_only.py", pre("Edit", str(worktree / "DECISIONS.md"), old_string="x",
                                                          new_string="x\n| E-099 | d | **y** | z |"))
    assert code == ALLOW
    assert "only the lead writes the decision log" in json.loads(out)["systemMessage"]


def test_other_files_and_the_vendored_log_are_not_checked():
    for path in ("README.md", "vendor/stage2/DECISIONS.md"):
        code, out, _ = invoke("decisions_append_only.py", pre("Edit", path, old_string=ROW4, new_string="z"))
        assert code == ALLOW and out.strip() == "", path


# ------------------------------------------------------------------ run_tests


def test_the_test_hook_ignores_non_python_edits():
    code, out, _ = invoke("run_tests.py", pre("Edit", "README.md"))
    assert code == ALLOW and out.strip() == ""


def test_the_test_hook_ignores_python_outside_this_project(tmp_path):
    (tmp_path / "elsewhere" / ".git").mkdir(parents=True)
    code, out, _ = invoke("run_tests.py", pre("Edit", str(tmp_path / "elsewhere" / "x.py")))
    assert code == ALLOW and out.strip() == ""


def test_the_fast_tier_is_one_selection_everywhere():
    expr = "not slow and not heavy"
    assert f'FAST_TIER = "{expr}"' in (HOOKS / "run_tests.py").read_text(encoding="utf-8")
    assert f'FAST_TIER="{expr}"' in (ROOT / "scripts" / "pre-commit").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for marker in ("slow", "heavy"):
        assert f'"{marker}: ' in pyproject, f"the {marker} marker is not registered in pyproject.toml"


def test_the_git_hooks_keep_lf_and_install_into_the_common_dir():
    for name in ("pre-commit", "post-commit"):
        assert b"\r\n" not in (ROOT / "scripts" / name).read_bytes(), f"scripts/{name} has CRLF"
    text = (ROOT / "scripts" / "install_hooks.py").read_text(encoding="utf-8")
    assert "--git-common-dir" in text
    assert "vendor_stage2.py --verify" in (ROOT / "scripts" / "pre-commit").read_text(encoding="utf-8")


# ------------------------------------------------------------- the QuantConnect guards


@pytest.mark.parametrize("tool", ["mcp__quantconnect__create_live_algorithm", "mcp__quantconnect__read_live_orders",
                                  "mcp__qc2__deploy_project", "mcp__quantconnect__broadcast_live_command"])
def test_live_tools_are_denied(tool):
    code, _, err = invoke("qc_no_live_trading.py", {"tool_name": tool, "tool_input": {}})
    assert code == DENY and "live-trading" in err


def test_research_tools_are_not_denied_as_live():
    code, _, _ = invoke("qc_no_live_trading.py", {"tool_name": "mcp__quantconnect__read_backtest", "tool_input": {}})
    assert code == ALLOW


def _algo(start: tuple[int, int, int], end: tuple[int, int, int]) -> str:
    return (f"class A(QCAlgorithm):\n    def initialize(self):\n        self.set_start_date({start[0]}, {start[1]}, "
            f"{start[2]})\n        self.set_end_date({end[0]}, {end[1]}, {end[2]})\n")


def test_a_development_cloud_run_is_allowed():
    payload = {"tool_name": "mcp__quantconnect__create_file",
               "tool_input": {"name": "main.py", "content": _algo((2020, 1, 2), (2024, 12, 31))}}
    assert invoke("qc_window_guard.py", payload)[0] == ALLOW


@pytest.mark.parametrize("end", [(2026, 7, 31), (2025, 7, 1)])
def test_a_cloud_run_reaching_a_confirmation_window_is_denied(end):
    payload = {"tool_name": "mcp__quantconnect__create_file",
               "tool_input": {"name": "main.py", "content": _algo((2020, 1, 2), end), "prereg_id": "P-16"}}
    code, _, err = invoke("qc_window_guard.py", payload)
    assert code == DENY and "REFUSED" in err


@pytest.mark.parametrize("tool_input", [{}, {"content": "class A(QCAlgorithm):\n    pass\n" * 20}])
def test_a_cloud_run_with_no_code_or_no_dates_is_denied(tool_input):
    code, _, _ = invoke("qc_window_guard.py", {"tool_name": "mcp__quantconnect__create_backtest",
                                               "tool_input": tool_input})
    assert code == DENY


def test_tools_that_launch_nothing_are_not_window_guarded():
    code, _, _ = invoke("qc_window_guard.py", {"tool_name": "mcp__quantconnect__read_backtest", "tool_input": {}})
    assert code == ALLOW
