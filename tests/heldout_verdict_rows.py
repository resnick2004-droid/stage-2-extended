"""Q-194b, Q-194c: the joint held-out test's verdict, made in a test tree the way it is made for real -- the synthetic
F-98 declared and pinned, its finalists' token, **its `heldout_test` read through the reader in a simulated clean
run** (ledgered from the commit before the verdict), then its verdict row in the one form
`heldout-verdict: <MARKET> F-NN @ <its LF sha256> -- ...`. A tree whose registered-design or described-reading
held-out reads are the ones made after the verdict calls `settle`; the reader's refusals before it are
`tests/test_reader_q194b.py`'s and `tests/test_reader_q194c.py`'s. Synthetic only: none of this repository's rows."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

HT_ID = "F-98"
HT_PATH = "prereg/F-98_heldout_test.md"
HT_TEXT = ("# F-98: a synthetic joint held-out test (Q-194c's tests; not a declaration of this repository)\n\n"
           "- **Judged-block reads:** `heldout_test`, `heldout_stress`\n")
HT_SHA = hashlib.sha256(HT_TEXT.encode("utf-8")).hexdigest()
HT_LIST = "7" * 64
SEED_RUN_ID = "verdict-seed@run-0"
PIN_ROW = (f"| E-980 | 2026-11-19 | **{HT_ID} declared** (a synthetic joint held-out test), `{HT_PATH}` sha256 "
           f"`{HT_SHA}` | test |")
FINALISTS_ROW = f"| E-981 | 2026-11-19 | heldout-finalists: {HT_ID} @ {HT_SHA} list {HT_LIST} -- the joint list | test |"


def verdict_row(row: int = 982, market: str = "NQ", fid: str = HT_ID, sha: str = HT_SHA) -> str:
    return (f"| E-{row} | 2026-11-19 | heldout-verdict: {market} {fid} @ {sha} -- the joint held-out test's verdict "
            "| test |")


VERDICT_ROW = verdict_row()
#: the three rows a log carries after the joint test's verdict, in order
ROWS = (PIN_ROW, FINALISTS_ROW, VERDICT_ROW)


def without_rows(decisions: str) -> str:
    """A log's text with `ROWS` taken out (a tree's first commit, before `settle` adds them around the read)."""
    return "".join(x for x in decisions.splitlines(keepends=True) if x.rstrip("\r\n") not in ROWS)


def only_seed(run: dict) -> bool:
    """For a child driver's run record (its `ledger_refs`, every ledger line's declaration): the tree's ledger holds
    the seeded joint test's line and nothing else."""
    return run["ledger_refs"] == [HT_PATH]


def _git(t: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=t, capture_output=True, text=True, check=True).stdout.strip()


def append_rows(t: Path, *rows: str) -> None:
    """Append decision rows to the tree's DECISIONS.md and commit them."""
    p = t / "DECISIONS.md"
    text = p.read_bytes().decode("utf-8")
    if not text.endswith("\n"):
        text += "\n"
    p.write_bytes((text + "".join(r + "\n" for r in rows)).encode("utf-8"))
    _git(t, "add", "DECISIONS.md")
    _git(t, "commit", "-q", "-m", "rows")


def seed_line(t: Path) -> dict | None:
    """F-98's ledgered held-out read in the tree, or None."""
    p = t / "results" / "read_ledger.jsonl"
    if not p.exists():
        return None
    for x in p.read_text(encoding="utf-8").splitlines():
        rec = json.loads(x)
        if (rec.get("declaration") or {}).get("ref") == HT_PATH:
            return rec
    return None


def settle(t: Path, files, *, market: str = "NQ", verdict: bool = True, start: str = "2024-01-02",
           end: str = "2026-07-16") -> dict:
    """In the committed git tree `t` (at `<runs>/<name>`, as a clean run's checkout is): write F-98 and pin it, add its
    finalists' token, commit; make its `heldout_test` read of `start`..`end` of `market` through the reader, inside a
    simulated clean run of `t` with its own run id (`SEED_RUN_ID`); then, if `verdict`, append its verdict row and
    commit. The environment and `reader.RUNS_DIR` are restored. Returns the read's ledger line."""
    from extended import reader as R
    (t / "prereg").mkdir(exist_ok=True)
    (t / HT_PATH).write_bytes(HT_TEXT.encode("utf-8"))
    _git(t, "add", HT_PATH)
    append_rows(t, PIN_ROW, FINALISTS_ROW)
    saved = {k: os.environ.get(k) for k in ("S2X_CLEAN_RUN", "S2X_RUN_ID")}
    saved_dir = R.RUNS_DIR
    os.environ["S2X_CLEAN_RUN"], os.environ["S2X_RUN_ID"] = t.name, SEED_RUN_ID
    R.RUNS_DIR = t.parent
    try:
        R.authorise_engine_read(start, end, purpose="heldout_test", declaration=HT_PATH, files=list(files),
                                what="the joint held-out test (a synthetic seed)", repo=t, market=market)
    finally:
        R.RUNS_DIR = saved_dir
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    if verdict:
        append_rows(t, verdict_row(market=market))
    line = seed_line(t)
    assert line is not None
    return line
