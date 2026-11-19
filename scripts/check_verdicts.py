"""List the commits in a range whose tree has no fast-tier verdict (Q-161), for the lead's merge checklist.

    python scripts/check_verdicts.py master..wt/wt-levels
    python scripts/check_verdicts.py HEAD~5..HEAD [more rev-list arguments]

**The verdict.** The pre-commit hook appends, only after the fast tier itself returned 0, one line to
`<git-common-dir>/fasttier-verdicts.log`: the commit's tree (from `git write-tree` on the commit's index), the UTC time,
the worktree, and pytest's pass line, tab-separated. A tree with such a line passed the fast tier; a commit whose tree
has none was written without that verdict: `--no-verify`, a rebase or cherry-pick (new trees), or a hook killed before
its fast tier returned (on Windows git reads a killed hook as a pass; 3451a10 on 2026-11-18). The post-commit hook
logs such a commit as `NO VERDICT <branch> <sha>`; this lists them over a range after the fact.

**The rule** (merges). A non-merge commit is clean when its tree has a verdict. A merge commit is clean when its tree
has a verdict, or when every parent is either outside the range (already on the side the range excludes -- for
`master..wt/x`, master's commits, accepted when they were merged) or a clean commit inside it. So a worker's
"Merge branch 'master'" is exempt when the branch's own side is clean; a merge above an unverified commit is listed with
it. The merge's own combination is not tested by this rule; the merge checklist's suite run is what tests it.

Exit 0 when every commit in the range is clean, 1 when any is listed, 2 when the range or the repository cannot be
read. Prints one line per listed commit: `<sha> <subject>` and, indented, why.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

LOG_NAME = "fasttier-verdicts.log"
_HEX = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
LIMIT_S = 300


def _git(args: list[str], cwd: Path | None = None) -> str:
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=LIMIT_S)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip() or p.stdout.strip()}")
    return p.stdout


def verdict_trees(log: Path) -> set[str]:
    """Every tree with a verdict line in the log (lines beginning `<tree>\\t`; NO VERDICT lines are not verdicts)."""
    if not log.is_file():
        return set()
    trees = set()
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        head, sep, _ = line.partition("\t")
        if sep and _HEX.match(head):
            trees.add(head)
    return trees


def unverified(rev_args: list[str], cwd: Path | None = None, log: Path | None = None) -> list[tuple[str, str, str]]:
    """The commits in the range that are not clean, oldest first: (sha, subject, why)."""
    if log is None:
        common = Path(_git(["rev-parse", "--path-format=absolute", "--git-common-dir"], cwd).strip())
        log = common / LOG_NAME
    have = verdict_trees(log)
    out = _git(["rev-list", "--topo-order", "--reverse", "--format=%H %T %P%x09%s", *rev_args, "--"], cwd)
    rows = []
    for line in out.splitlines():
        if line.startswith("commit "):
            continue
        meta, _, subject = line.partition("\t")
        sha, tree, *parents = meta.split()
        rows.append((sha, tree, parents, subject))
    in_range = {r[0] for r in rows}
    clean: dict[str, bool] = {}
    listed = []
    for sha, tree, parents, subject in rows:            # parents before children (--topo-order --reverse)
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("revs", nargs="+", help="a rev-list range, e.g. master..wt/wt-levels")
    ap.add_argument("--log", type=Path, default=None, help=f"the verdict log (default <git-common-dir>/{LOG_NAME})")
    a = ap.parse_args(argv)
    try:
        listed = unverified(a.revs, log=a.log)
    except (RuntimeError, OSError, subprocess.SubprocessError) as e:
        print(f"check_verdicts: {e}", file=sys.stderr)
        return 2
    for sha, subject, why in listed:
        print(f"{sha} {subject}")
        print(f"    {why}")
    print(f"# {len(listed)} commit(s) without a fast-tier verdict in {' '.join(a.revs)}")
    return 1 if listed else 0


if __name__ == "__main__":
    raise SystemExit(main())
