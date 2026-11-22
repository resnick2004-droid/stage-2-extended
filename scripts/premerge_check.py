"""The pre-merge-commit hook's checks (Q-208): a short, deterministic set on the merge result, never the fast tier.

    python scripts/premerge_check.py            # every check, as the hook runs it (exit 0 pass, 1 refused)
    python scripts/premerge_check.py --log      # the decision log's hygiene alone

**Why.** A clean `git merge` runs neither pre-commit nor its fast tier, so a merge could bring in, untested, a decision
log that breaks the reader's hygiene (an unclosed fence, a malformed held-out token) or a changed vendored file. Git runs
`pre-merge-commit` (installed by `scripts/install_hooks.py`) after a merge is computed and before its commit is written,
with the work tree and index holding the merge result; this script is what it runs, from the merged tree's root.

**The checks** (each in its own process, from the tree's root, git's variables removed; all run, every failure named):

1. *vendor integrity* -- `scripts/vendor_stage2.py --verify`: vendor/stage2 against its manifest, and the data where
   present (E-002);
2. *the decision log's hygiene* -- `extended.reader.heldout_token_problems` on DECISIONS.md is empty, and its fences
   close (`extended.reader._fences`, Q-194d). A reader without `_fences` (before wt/wt-verify's Q-194 is on master) has
   the fence check skipped with a visible SKIPPED line, never silently; a reader without `heldout_token_problems` is
   refused (merge master);
3. *pinned declarations* -- `tests/test_declarations_fixed.py`;
4. *identity tokens on the real log* -- `tests/test_identity_tokens.py::test_the_repository_decision_log_has_no_breach`.

Before them, the files the checks read must be the merge result: a tracked file under CHECKED_PATHS whose work-tree copy
differs from the index (an unstaged edit kept through the merge) refuses the merge, naming it.

**Light.** Seconds in all (no data read beyond hashing the vendored tree, no engine), so it takes no fast-tier slot and
no run lock; the whole set is bounded by BUDGET_S (5 minutes) -- a check still running then is killed and the merge
refused, naming it. The next commit's pre-commit fast tier still tests the merged tree in full. A merge with conflicts
runs no pre-merge-commit (its commit runs pre-commit), and a fast-forward writes no merge commit.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
BUDGET_S = 300.0                 # the whole check set, at most five minutes
TAIL_LINES = 30                  # a failing check's last output lines, printed with its refusal
#: the files the checks read; a work-tree edit to any of them would be checked instead of the merge result
CHECKED_PATHS = ("DECISIONS.md", "vendor", "prereg", "config", "docs/calibration", "extended", "identity", "scripts",
                 "tests", "conftest.py", "pyproject.toml")
LOG_TEST = "tests/test_identity_tokens.py::test_the_repository_decision_log_has_no_breach"
FENCE_SKIPPED = ("SKIPPED: the fence check -- this tree's extended.reader has no _fences yet (it arrives with "
                 "wt/wt-verify's Q-194); the held-out tokens were checked without it")


def _say(msg: str, err: bool = False) -> None:
    print(f"pre-merge-commit: {msg}", file=sys.stderr if err else sys.stdout, flush=True)


@dataclass(frozen=True)
class Check:
    name: str
    cmd: tuple[str, ...]


def checks(python: str = sys.executable) -> list[Check]:
    pytest = (python, "-m", "pytest", "-q", "-o", "addopts=", "-p", "no:cacheprovider")
    return [
        Check("vendor integrity", (python, "scripts/vendor_stage2.py", "--verify")),
        Check("the decision log's hygiene", (python, "scripts/premerge_check.py", "--log")),
        Check("pinned declarations", (*pytest, "tests/test_declarations_fixed.py")),
        Check("identity tokens on the real log", (*pytest, LOG_TEST)),
    ]


def clean_env() -> dict:
    """The environment a shell gives the checks: no git variables (a nested git would read the merge's index from
    them), no bytecode written into the read-only vendored tree, one BLAS thread."""
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "1"})
    return env


# ------------------------------------------------------------------------------------------------ the log's hygiene

def log_problems(text: str, reader) -> tuple[list[str], list[str]]:
    """(problems, notes) of the decision log `text` under `reader` (extended.reader): its held-out token problems and a
    fence never closed. A reader without `_fences` gives the note FENCE_SKIPPED, never a silent pass."""
    if not hasattr(reader, "heldout_token_problems"):
        return (["this tree's extended.reader has no heldout_token_problems: merge master and merge again"], [])
    problems = [str(p) for p in reader.heldout_token_problems(text)]
    notes = []
    fences = getattr(reader, "_fences", None)
    if fences is None:
        notes.append(FENCE_SKIPPED)
    else:
        _, unclosed = fences(text)
        if unclosed is not None and not any(f"line {unclosed + 1}:" in p for p in problems):
            problems.append(f"line {unclosed + 1}: a fenced code block opened here is never closed, so every line "
                            f"after it is fenced")
    return problems, notes


def check_log(root: Path = ROOT) -> int:
    log = root / "DECISIONS.md"
    try:
        text = log.read_text(encoding="utf-8")
    except OSError as e:
        _say(f"cannot read {log}: {e}", err=True)
        return 1
    sys.path.insert(0, str(root))
    try:
        from extended import reader
    except Exception as e:                                # noqa: BLE001 -- any import failure refuses, named
        _say(f"cannot import extended.reader from {root}: {type(e).__name__}: {e}", err=True)
        return 1
    problems, notes = log_problems(text, reader)
    for n in notes:
        _say(n)
    for p in problems:
        _say(f"DECISIONS.md: {p}", err=True)
    if not problems:
        _say("DECISIONS.md: no held-out token problem" + ("" if notes else ", every fence closed"))
    return 1 if problems else 0


# ------------------------------------------------------------------------------------------------ the set

def dirty_checked_files(root: Path = ROOT, paths: tuple[str, ...] = CHECKED_PATHS) -> list[str] | None:
    """Tracked files under `paths` whose work-tree copy differs from the index (the merge result); None if git fails."""
    try:
        out = subprocess.run(["git", "diff", "--name-only", "--", *paths], cwd=root, capture_output=True, text=True,
                             timeout=120, env=clean_env())
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return [ln for ln in out.stdout.splitlines() if ln.strip()]


def _git_out(root: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=120, env=clean_env())
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout.strip()


def merge_gate(root: Path = ROOT, environ: dict | None = None, main_tree: bool | None = None) -> str | None:
    """Q-209: in the main tree a merge commit is written only over merged tips that each have a T2 verdict (the full
    fast tier on the tip's own tree). The merged commits are the names git puts in GIT_REFLOG_ACTION (`merge <name>
    ...`; MERGE_HEAD is not yet written when pre-merge-commit runs). None when the merge may go on, else why not --
    including when the names cannot be read (fail closed). A worker tree's merge (of master) is not gated here."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from check_verdicts import LOG_NAME, tree_has_t2
    from fasttier_lock import is_main_worktree
    if not (is_main_worktree(root) if main_tree is None else main_tree):
        return None
    env = os.environ if environ is None else environ
    action = env.get("GIT_REFLOG_ACTION", "")
    names = action.split()[1:] if action.split()[:1] == ["merge"] else []
    how = ("run `python scripts/fasttier_full.py` in the merged branch's tree (its tip's T2 verdict), or merge with "
           "`--no-commit` and then `git commit`, whose pre-commit hook runs T2 on the merge itself")
    if not names:
        return (f"the main tree merges only tips with a T2 verdict, and the merged commits cannot be read from "
                f"GIT_REFLOG_ACTION={action!r}: {how}")
    try:
        log = Path(_git_out(root, "rev-parse", "--path-format=absolute", "--git-common-dir")) / LOG_NAME
        missing = []
        for n in names:
            sha = _git_out(root, "rev-parse", "--verify", f"{n}^{{commit}}")
            tree = _git_out(root, "rev-parse", f"{sha}^{{tree}}")
            if not tree_has_t2(tree, log):
                missing.append(f"{n} ({sha[:10]}, tree {tree[:12]})")
    except (OSError, RuntimeError, subprocess.SubprocessError) as e:
        return f"the merged tips' verdicts cannot be read ({e}): {how}"
    if missing:
        return f"the merged tip(s) {', '.join(missing)} have no T2 verdict: {how}"
    return None


def _tail(text: str, n: int = TAIL_LINES) -> str:
    return "\n".join(text.splitlines()[-n:])


def run_checks(root: Path = ROOT, the_checks: list[Check] | None = None, budget_s: float = BUDGET_S,
               monotonic: Callable[[], float] = time.monotonic, main_tree: bool | None = None) -> int:
    """Run every check from `root` within `budget_s` in all; 0 if each passed, else 1, every failure named."""
    the_checks = checks() if the_checks is None else the_checks
    t0 = monotonic()
    gate = merge_gate(root, main_tree=main_tree)
    if gate is not None:
        _say(f"REFUSED: {gate}", err=True)
        return 1
    dirty = dirty_checked_files(root)
    if dirty is None:
        _say("REFUSED: cannot compare the work tree with the merge's index (git diff failed)", err=True)
        return 1
    if dirty:
        _say("REFUSED: these checked files differ from the merge result in the work tree (an unstaged edit kept "
             "through the merge), so the checks would read them instead of the merge: " + ", ".join(dirty[:20])
             + (f" and {len(dirty) - 20} more" if len(dirty) > 20 else "")
             + ". Set them aside (commit them, or `git restore` them), then merge again.", err=True)
        return 1
    failed = []
    for c in the_checks:
        left = budget_s - (monotonic() - t0)
        if left <= 0:
            failed.append(c.name)
            _say(f"REFUSED: the check '{c.name}' did not start: the {budget_s:.0f} s budget ran out", err=True)
            continue
        t = monotonic()
        try:
            p = subprocess.run(list(c.cmd), cwd=root, env=clean_env(), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=left)
        except subprocess.TimeoutExpired:
            failed.append(c.name)
            _say(f"REFUSED: the check '{c.name}' was still running when the {budget_s:.0f} s budget ran out; killed",
                 err=True)
            continue
        except OSError as e:
            failed.append(c.name)
            _say(f"REFUSED: the check '{c.name}' could not start: {e}", err=True)
            continue
        out = (p.stdout or "") + (p.stderr or "")
        took = monotonic() - t
        if p.returncode == 0:
            skipped = [ln for ln in out.splitlines() if "SKIPPED" in ln]
            _say(f"ok   {c.name} ({took:.1f} s)" + "".join(f"\n    {ln.strip()}" for ln in skipped))
        else:
            failed.append(c.name)
            _say(f"FAIL {c.name} (exit {p.returncode}, {took:.1f} s):\n{_tail(out)}", err=True)
    if failed:
        _say("REFUSED: the merge commit is not written -- failed: " + "; ".join(failed) + ". The merge is left in "
             "progress: fix the cause and `git commit`, or `git merge --abort`.", err=True)
        return 1
    _say(f"OK: {len(the_checks)} checks on the merge result ({monotonic() - t0:.1f} s)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--log", action="store_true", help="only the decision log's hygiene")
    ap.add_argument("--budget-s", type=float, default=BUDGET_S)
    a = ap.parse_args(argv)
    if a.log:
        return check_log(ROOT)
    return run_checks(ROOT, budget_s=a.budget_s)


if __name__ == "__main__":
    sys.exit(main())
