"""List the commits in a range whose tree has no fast-tier verdict (Q-161), for the lead's merge checklist.

    python scripts/check_verdicts.py master..wt/wt-levels           # a worker's branch, before its merge
    python scripts/check_verdicts.py --first-parent <since>..master  # master's own history, every commit and merge
    python scripts/check_verdicts.py --merge-gate                    # the commit-msg hook's call on a main-tree merge

**The verdict.** The pre-commit hook appends, only after the full fast tier itself returned 0, one line to
`<git-common-dir>/fasttier-verdicts.log`: the commit's tree (from `git write-tree` on the commit's index), the UTC time,
the worktree, pytest's pass line and `tier=T2`, tab-separated. A line without a tier field was written before Q-209 by
the same full fast tier and is a verdict too; **a line with any other tier is no verdict** (the red team's F9: an
unparsed tier never counts as the full tier). A commit whose tree has no verdict was written without one:
`--no-verify`, a rebase or cherry-pick (new trees), a clean merge (no pre-commit), or a hook killed before its fast tier
returned (on Windows git reads a killed hook as a pass; 3451a10 on 2026-11-18). The post-commit hook logs a non-merge
such commit as `NO VERDICT <branch> <sha>`.

**A range** (`master..wt/x`). A non-merge commit is clean when its tree has a verdict. A merge commit below the tip is
clean when its tree has a verdict, or when every parent is either outside the range (already on the side the range
excludes -- for `master..wt/x`, master's commits) or a clean commit inside it. **The tip** -- each commit of the range
that is no parent of another commit in it -- needs a verdict on its own tree, with no merge exemption: a worker whose
last commit merged master runs `python scripts/fasttier_full.py` before the hand-back. (The next commit's full fast
tier tests a merge's tree; a tip has no next commit.)

**Master** (`--first-parent`, the red team's F4). Walking master's first parents, a non-merge commit needs a verdict on
its tree; a merge commit needs a verdict on its tree (merged with `--no-commit`, then committed through pre-commit) or a
**gate line** -- `gate<TAB><merge tree><TAB><time><TAB>tips=<sha,...>`, which the commit-msg hook appends when it let
a main-tree merge through (`--merge-gate`). A merge made with `--no-verify`, or by a hook that never ran, has neither
and is listed: it cannot be prevented, and this is where it shows.

**The merge gate** (`--merge-gate`; the commit-msg hook calls it in the main tree only, from HEAD's copy of this file).
On a merge commit (MERGE_HEAD present), it passes when the index's tree -- the merge result being committed -- has a
verdict (a T2 run of the merge itself: `git merge --no-commit`, then `git commit`), or when every commit in MERGE_HEAD
has a verdict on its own tree (each merged tip's T2). It reads MERGE_HEAD's exact shas, never branch names (the red
team's F4 and F13). On a pass it appends the gate line. Not a merge: nothing to do.

Exit 0 when every commit is clean (or the gate passes), 1 when any is listed (or the gate refuses), 2 when the range or
the repository cannot be read. Prints one line per listed commit: `<sha> <subject>` and, indented, why.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_NAME = "fasttier-verdicts.log"
_HEX = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
LIMIT_S = 300


def _git(args: list[str], cwd: Path | None = None) -> str:
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=LIMIT_S)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip() or p.stdout.strip()}")
    return p.stdout


def _is_verdict(fields: list[str]) -> bool:
    """A verdict line: a tree, then fields; every `tier=` field, if any, is exactly `tier=T2`."""
    if len(fields) < 2 or not _HEX.match(fields[0]):
        return False
    return all(f.strip() == "tier=T2" for f in fields[1:] if f.strip().startswith("tier="))


def verdict_trees(log: Path) -> set[str]:
    """Every tree with a verdict line in the log (NO VERDICT and gate lines are not verdicts)."""
    if not log.is_file():
        return set()
    out = set()
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.split("\t")
        if _is_verdict(fields):
            out.add(fields[0])
    return out


def gate_trees(log: Path) -> set[str]:
    """Every merge tree the commit-msg gate let through (`gate<TAB><tree>...`)."""
    if not log.is_file():
        return set()
    out = set()
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.split("\t")
        if len(fields) >= 2 and fields[0] == "gate" and _HEX.match(fields[1]):
            out.add(fields[1])
    return out


def tree_has_t2(tree: str, log: Path) -> bool:
    """Whether the tree has a verdict of the full fast tier."""
    return tree in verdict_trees(log)


def _log_path(cwd: Path | None) -> Path:
    return Path(_git(["rev-parse", "--path-format=absolute", "--git-common-dir"], cwd).strip()) / LOG_NAME


def _rows(rev_args: list[str], cwd: Path | None, first_parent: bool = False) -> list[tuple[str, str, list[str], str]]:
    extra = ["--first-parent"] if first_parent else []
    out = _git(["rev-list", *extra, "--topo-order", "--reverse", "--format=%H %T %P%x09%s", *rev_args, "--"], cwd)
    rows = []
    for line in out.splitlines():
        if line.startswith("commit "):
            continue
        meta, _, subject = line.partition("\t")
        sha, tree, *parents = meta.split()
        rows.append((sha, tree, parents, subject))
    return rows


def unverified(rev_args: list[str], cwd: Path | None = None, log: Path | None = None) -> list[tuple[str, str, str]]:
    """The commits in the range that are not clean, oldest first: (sha, subject, why)."""
    log = _log_path(cwd) if log is None else log
    have = verdict_trees(log)
    rows = _rows(rev_args, cwd)
    in_range = {r[0] for r in rows}
    parents_in_range = {p for r in rows for p in r[2] if p in in_range}     # every parent, first or not (F10)
    clean: dict[str, bool] = {}
    listed = []
    for sha, tree, parents, subject in rows:            # parents before children (--topo-order --reverse)
        if sha not in parents_in_range:                 # a tip of the range: a verdict on its own tree
            clean[sha] = tree in have
            if not clean[sha]:
                listed.append((sha, subject, f"the branch tip has no verdict on its own tree {tree[:12]}; run "
                                             f"`python scripts/fasttier_full.py` in its tree"))
            continue
        if tree in have:
            clean[sha] = True
            continue
        if len(parents) >= 2:
            bad = [p for p in parents if p in in_range and not clean.get(p, False)]
            if not bad:
                clean[sha] = True
                continue
            why = f"a merge without a verdict above unclean parent(s) {', '.join(p[:10] for p in bad)}"
        else:
            why = f"no verdict for its tree {tree[:12]}"
        clean[sha] = False
        listed.append((sha, subject, why))
    return listed


def unverified_first_parent(rev_args: list[str], cwd: Path | None = None,
                            log: Path | None = None) -> list[tuple[str, str, str]]:
    """Master's first-parent commits that are not clean (F4): a non-merge without a verdict on its tree, a merge with
    neither a verdict nor a gate line for its tree."""
    log = _log_path(cwd) if log is None else log
    have, gated = verdict_trees(log), gate_trees(log)
    listed = []
    for sha, tree, parents, subject in _rows(rev_args, cwd, first_parent=True):
        if tree in have:
            continue
        if len(parents) >= 2:
            if tree in gated:
                continue
            listed.append((sha, subject, f"a merge with no gate line and no verdict for its tree {tree[:12]} "
                                         f"(--no-verify, or the commit-msg gate never ran)"))
        else:
            listed.append((sha, subject, f"no verdict for its tree {tree[:12]}"))
    return listed


def merge_gate(cwd: Path | None = None, log: Path | None = None, now: str | None = None) -> str | None:
    """The commit-msg hook's gate on a main-tree merge; None to let it through (the gate line appended), else why not."""
    gitdir = Path(_git(["rev-parse", "--absolute-git-dir"], cwd).strip())
    merge_head = gitdir / "MERGE_HEAD"
    if not merge_head.is_file():
        return None                                     # not a merge
    log = _log_path(cwd) if log is None else log
    have = verdict_trees(log)
    tips = [ln.strip() for ln in merge_head.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not tips or not all(_HEX.match(t) for t in tips):
        return f"MERGE_HEAD ({merge_head}) holds no commit ids: {tips!r}"
    result = _git(["write-tree"], cwd).strip()          # the index: the merge result being committed
    missing = []
    for t in tips:
        tree = _git(["rev-parse", f"{t}^{{tree}}"], cwd).strip()
        if tree not in have:
            missing.append(f"{t[:10]} (tree {tree[:12]})")
    if result not in have and missing:
        return (f"the merged tip(s) {', '.join(missing)} have no full-fast-tier verdict, nor has the merge result "
                f"{result[:12]}: run `python scripts/fasttier_full.py` in the merged branch's tree, or merge with "
                f"`--no-commit` and then `git commit` (the pre-commit hook runs the full fast tier on the merge itself)")
    stamp = now or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with log.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"gate\t{result}\t{stamp}\ttips={','.join(tips)}\n")
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("revs", nargs="*", help="a rev-list range, e.g. master..wt/wt-levels")
    ap.add_argument("--log", type=Path, default=None, help=f"the verdict log (default <git-common-dir>/{LOG_NAME})")
    ap.add_argument("--first-parent", action="store_true", help="master's first parents: commits and merges (F4)")
    ap.add_argument("--merge-gate", action="store_true", help="the commit-msg hook's gate on a main-tree merge")
    a = ap.parse_args(argv)
    try:
        if a.merge_gate:
            why = merge_gate(log=a.log)
            if why:
                print(f"commit-msg: REFUSED -- {why}", file=sys.stderr)
                return 1
            return 0
        if not a.revs:
            ap.error("a range is needed (or --merge-gate)")
        listed = (unverified_first_parent if a.first_parent else unverified)(a.revs, log=a.log)
    except (RuntimeError, OSError, subprocess.SubprocessError) as e:
        print(f"check_verdicts: {e}", file=sys.stderr)
        return 2
    for sha, subject, why in listed:
        print(f"{sha} {subject}")
        print(f"    {why}")
    print(f"# {len(listed)} commit(s) without a fast-tier verdict in {' '.join(a.revs)}"
          + (" (first parents)" if a.first_parent else ""))
    return 1 if listed else 0


if __name__ == "__main__":
    raise SystemExit(main())
