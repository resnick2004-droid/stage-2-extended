"""Q-04: `scripts/status.py` prints the board's five parts -- the queue's states from TASK_QUEUE.md, the run lock, the
worktrees, every result file with its manifest check, the last test run -- and parses the queue table correctly.

A child process for the script itself (it lists results through the vendored reader); the queue parser is checked in
process on a synthetic table.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_status_prints_every_part():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "status.py")], cwd=ROOT, capture_output=True, text=True,
                       timeout=300)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    for part in ("== queue", "== run lock", "== worktrees", "== results", "== last test run"):
        assert part in r.stdout, part
    # Every row of the live queue is listed (Q-05 was named here until Q-147's archive could move a done row out);
    # once the archive exists its rows are counted.
    S = _status()
    live = S.queue_rows((ROOT / "TASK_QUEUE.md").read_text(encoding="utf-8"))
    assert live and all(f"  {row['id']} " in r.stdout for row in live)
    archive = ROOT / "docs" / "archive" / "TASK_QUEUE_ARCHIVE.md"
    if archive.is_file():
        assert f"archived: {len(S.queue_rows(archive.read_text(encoding='utf-8')))} row(s)" in r.stdout


def _status():
    spec = importlib.util.spec_from_file_location("s2x_status", ROOT / "scripts" / "status.py")
    S = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(S)          # importing it reads nothing vendored: the results are listed only in main()
    return S


def test_queue_rows_parse_from_both_ends():
    S = _status()
    text = """
| id | task | owner | state | depends on | weight | retries | row |
|---|---|---|---|---|---|---|---|
| Q-01 | Skeleton: a | b (with a pipe \\| inside) | lead | done | -- | light | 0 | E-005 |
| Q-02 | **Agents** | wt-x | running | Q-01 | light; heavy later | 1 | -- |
"""
    rows = S.queue_rows(text)
    assert [r["id"] for r in rows] == ["Q-01", "Q-02"]
    assert rows[0]["state"] == "done" and rows[0]["owner"] == "lead" and rows[0]["row"] == "E-005"
    assert rows[1]["state"] == "running" and rows[1]["retries"] == "1" and rows[1]["weight"] == "light; heavy later"
    assert "pipe" in rows[0]["task"]
