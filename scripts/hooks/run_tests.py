"""PostToolUse hook: after a .py edit, run the edited file's own tests and the two foundation checks in the edited tree
and report failures. Never blocks.

The tool call has already happened, so this cannot and should not undo anything. What it does is make a break visible
at the moment it is introduced rather than at the next manual run -- which matters most for the checks that keep the
foundation honest (the vendored snapshot's integrity, the declarations' pinned hashes, the hooks themselves).

Reporting convention:
  * tests pass  -> exit 0, one-line summary on stdout.
  * tests fail  -> exit 2 with the failing output on stderr. For PostToolUse this surfaces the text to Claude without
    reverting anything, which is exactly "report, do not block".

**What runs (Q-147, E-205): the edited file's tests and the foundation's two checks**, not the whole fast tier:

  * the edited file's matching `tests/test_<stem>.py`, when the tree has one -- or the edited file itself, when it is a
    test file under `tests/` (`test_*.py`);
  * `tests/test_vendor_integrity.py` (E-002) and `tests/test_declarations_fixed.py` (E-003), whatever was edited.

A file with no matching test runs only the two. The whole fast tier used to run after every edit while the pre-commit
hook ran it too, and several at once ran this 16 GB machine out of memory. The pre-commit hook keeps the whole fast
tier on every commit (`scripts/pre-commit`, unchanged), so a break elsewhere is still caught before it lands.

The fast tier's marker selection `-m "not slow and not heavy"` still applies to the files chosen, with a 600 s limit:
the identity (`slow`) and anything that reads the full bars or runs a campaign (`heavy`, one at a time under
`run.lock`) never run from here.

**Which tree.** The suite runs in the tree that holds the edited file -- this repository, or a worktree or clean
checkout of it (a directory holding `.git` whose `pyproject.toml` names this project) -- so a worker's edit in
`%LOCALAPPDATA%\\stage2-extended-wt\\<name>` is tested against that worktree's code. A .py file in any other tree is
not ours to test. Since E-027 an edit inside a worktree or clean checkout (`.git` a file) runs nothing: there the
pre-commit hook's fast tier is the check.

Writes `<tree>/results/.last_test_run.json` (git-ignored) so `/status` can say when the hook last ran and what it said
-- the same keys as before; the summary names the files run, so it is never read as the whole tier's. `-o addopts=`
clears the project's own `-q` (the two would combine into `-qq` and suppress the count); `PYTHONDONTWRITEBYTECODE=1`
keeps the run from writing `__pycache__` into the vendored tree.

Fails open: if pytest is missing or anything unexpected happens, exit 0.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

WRITE_TOOLS = {"Write", "Edit", "MultiEdit"}
TIMEOUT_SECONDS = 600
#: The commit-time fast tier, the same selection scripts/pre-commit runs.
FAST_TIER = "not slow and not heavy"
#: How a tree of this repository is recognised: its pyproject.toml names the project.
PROJECT_MARK = 'name = "stage2-extended"'
#: Run after every .py edit, whatever was edited (Q-147): the vendored snapshot's integrity and the pinned declarations.
FIXED_TESTS = ("tests/test_vendor_integrity.py", "tests/test_declarations_fixed.py")


def tests_for(edited: Path, tree: Path) -> list[str]:
    """The test files to run after `edited` changed in `tree`, as tree-relative posix paths, in order, each once.

    First the edited file's own test: the file itself when it is a `test_*.py` under the tree's `tests/`, else
    `tests/test_<stem>.py` when the tree has it. Then `FIXED_TESTS`. A file missing from the tree is left out; an
    edited file outside the tree maps to the fixed pair alone. Paths compare case-blind on Windows."""
    out: list[str] = []
    try:
        rel = os.path.relpath(os.path.normcase(os.path.abspath(edited)), os.path.normcase(os.path.abspath(tree)))
    except ValueError:                                    # on another drive
        rel = os.pardir
    parts = Path(rel).parts
    if parts and parts[0] != os.pardir and not Path(rel).is_absolute():
        name = Path(edited).name
        if len(parts) >= 2 and parts[0] == os.path.normcase("tests") and name.lower().startswith("test_"):
            # the edited file itself, its directories below tests/ taken from the path as written (not normcased)
            own = "/".join(("tests", *Path(edited).parts[-(len(parts) - 1):]))
        else:
            own = f"tests/test_{Path(edited).stem}.py"
        if (tree / own).is_file():
            out.append(own)
    for fixed in FIXED_TESTS:
        if (tree / fixed).is_file() and all(os.path.normcase(fixed) != os.path.normcase(o) for o in out):
            out.append(fixed)
    return out


def summarise(output: str) -> str:
    """Pull pytest's own summary line out of its output."""
    for pattern in (r"\d+ failed[^\n]*", r"\d+ passed[^\n]*", r"no tests ran[^\n]*", r"ERROR[^\n]*"):
        m = re.search(pattern, output)
        if m:
            return m.group(0).strip()
    return output.strip().splitlines()[-1] if output.strip() else "(no output)"


def record(tree: Path, exit_code: int, summary: str) -> None:
    try:
        path = tree / "results" / ".last_test_run.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                    "exit_code": exit_code, "tier": FAST_TIER, "summary": summary}, indent=2) + "\n",
                        encoding="utf-8", newline="\n")
    except OSError:
        pass


def our_tree(target: Path) -> Path | None:
    import _trees as T

    root = T.tree_root(target)
    if root is None:
        return None
    try:
        if PROJECT_MARK not in (root / "pyproject.toml").read_text(encoding="utf-8"):
            return None
    except OSError:
        return None
    return root


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    try:
        import _trees as T

        if (payload.get("tool_name") or "") not in WRITE_TOOLS:
            return 0
        raw = T.target_of(payload) or ""
        if not raw.endswith(".py"):
            return 0
        tree = our_tree(T.candidates(raw, payload.get("cwd"))[-1])
        if tree is None:
            return 0
        # E-027: not in a worktree or clean checkout (`.git` a file). There the fast tier took 2-3 minutes and a share
        # of the machine's memory after every .py edit, with several workers at once; the pre-commit hook runs the same
        # tier on every commit, so a break is still caught before it lands on a branch.
        if T.is_worktree(tree):
            return 0

        # Q-147: the edited file's own tests and the fixed pair only; the pre-commit hook keeps the whole fast tier.
        files = tests_for(T.candidates(raw, payload.get("cwd"))[-1], tree)
        if not files:
            return 0
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        proc = subprocess.run([sys.executable, "-m", "pytest", "-o", "addopts=", "-q", "--no-header", "-m", FAST_TIER,
                               *files], cwd=tree, capture_output=True, text=True, timeout=TIMEOUT_SECONDS, env=env)
        out = (proc.stdout or "") + (proc.stderr or "")
        names = ", ".join(Path(f).name for f in files)
        summary = f"edited file's tests and the fixed pair ({names}): {summarise(out)}"
        record(tree, proc.returncode, summary)

        if proc.returncode == 0:
            sys.stdout.write(f"pytest after editing {Path(raw).name} in {tree} ({summary})\n")
            return 0

        tail = "\n".join(out.splitlines()[-80:])
        sys.stderr.write(
            f"pytest FAILED after editing {Path(raw).name} in {tree}: {summary}\n\n{tail}\n\n"
            "Reported, not blocked -- the edit stands. Fix the failure before building on it. A failed vendor-integrity "
            "or declaration-hash test means something under vendor/ or a pinned declaration (a family's prereg/F-xx or "
            "a described reading's prereg/RD-xx file, E-025 (1)) changed: restore it, never re-pin it (E-002, E-003). "
            "A failed check stays on record (the failure protocol).\n")
        return 2
    except subprocess.TimeoutExpired:
        sys.stderr.write(f"pytest (the edited file's tests) timed out after {TIMEOUT_SECONDS}s; run them by hand.\n")
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
