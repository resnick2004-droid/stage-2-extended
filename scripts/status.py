"""The board at a glance (Q-04): the queue's states, the run lock, the worktrees, every result file with its manifest
check, and the last test run.

    python scripts/status.py

Reads only: `TASK_QUEUE.md` (this tree's), `run.lock` (the main tree's, through `scripts/run_lock.py`), `git worktree
list` (through `scripts/worktrees.py`), every `results/*.csv` with its manifest (through `extended.results.
list_results`, the vendored check), and `results/.last_test_run.json` when the fast-tier hook has written one. It holds
no result number: a result file is named with its check, never read for a figure. Exit 0.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import run_lock as RL  # noqa: E402
import worktrees as W  # noqa: E402

QUEUE = ROOT / "TASK_QUEUE.md"
LAST_TESTS = ROOT / "results" / ".last_test_run.json"
#: the queue table's columns after the task, read from the right so a pipe inside a task does not shift them
RIGHT = ("owner", "state", "depends", "weight", "retries", "row")


def queue_rows(text: str) -> list[dict[str, str]]:
    """Every `| Q-nn | task | owner | state | depends on | weight | retries | row |` row of the queue's tables."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("| Q-"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2 + len(RIGHT):
            continue
        right = dict(zip(RIGHT, cells[-len(RIGHT):]))
        out.append({"id": cells[0], "task": " | ".join(cells[1:-len(RIGHT)]), **right})
    return out


def show_queue() -> None:
    print(f"== queue ({QUEUE.name}) ==")
    if not QUEUE.is_file():
        print("  no TASK_QUEUE.md")
        return
    rows = queue_rows(QUEUE.read_text(encoding="utf-8"))
    counts = Counter(r["state"] for r in rows)
    print("  " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) if rows else "  no rows")
    for r in rows:
        task = r["task"].replace("**", "")
        task = task if len(task) <= 90 else task[:87] + "..."
        print(f"  {r['id']:<5} {r['state']:<15} {r['owner']:<12} {r['weight'][:24]:<24} {task}")


def show_lock() -> None:
    print("== run lock ==")
    held = RL.read()
    gb = RL.available_gb()
    mem = "memory unknown" if gb is None else f"{gb:.1f} GB available"
    print(f"  {RL.LOCK}: {RL.describe(held) if held else 'FREE'}  ({mem})")


def show_worktrees() -> None:
    print("== worktrees ==")
    try:
        W.listing()
    except SystemExit as e:
        print(f"  could not list: {e}")


def show_results() -> None:
    print("== results ==")
    from extended.results import RESULTS_DIR, list_results

    rows = list_results()
    if not rows:
        print(f"  no result file in {RESULTS_DIR} yet")
        return
    bad = [r for r in rows if not r.get("verified")]
    print(f"  {len(rows)} result file(s), {len(bad)} failing its manifest")
    for r in rows:
        mark = "ok  " if r.get("verified") else "FAIL"
        extra = "" if r.get("verified") else f" -- {r.get('message')}"
        print(f"  [{mark}] {r['file']}  commit {str(r.get('git_commit', '?'))[:12]}  seed {r.get('seed')}{extra}")


def show_tests() -> None:
    print("== last test run ==")
    if not LAST_TESTS.is_file():
        print("  not recorded (the fast-tier hook writes results/.last_test_run.json)")
        return
    try:
        t = json.loads(LAST_TESTS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"  unreadable: {e}")
        return
    print(f"  {t.get('timestamp')}  exit {t.get('exit_code')}  tier '{t.get('tier')}'  {t.get('summary')}")


def main(argv: list[str] | None = None) -> int:
    print(f"status of {ROOT}")
    for part in (show_queue, show_lock, show_worktrees, show_results, show_tests):
        part()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
