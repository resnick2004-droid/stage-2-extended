"""Q-194b to Q-194d: the joint held-out test's verdict, made in a test tree the way it is made for real -- the synthetic
F-98 (a held-out declaration in the template's form: its marker, its section headings, its path
`prereg/F-98_heldout_test_NQ.md`, NQ's only one) declared and pinned, its finalists' token, **its `heldout_test` read
through the reader in a simulated clean run**, then its verdict row in the one form
`heldout-verdict: <MARKET> F-NN @ <its LF sha256> -- ...` **committed together with the ledger that holds the read**
(Q-194d: the order is proven by the first commit adding the verdict row). A tree whose registered-design or
described-reading held-out reads are the ones made after the verdict calls `settle`; the reader's refusals before it
are `tests/test_reader_q194b.py`'s to `tests/test_reader_q194d.py`'s. Synthetic only: none of this repository's rows."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

HT_ID = "F-98"
HT_PATH = "prereg/F-98_heldout_test_NQ.md"
#: the held-out template's marker and headings (`extended.reader.HELDOUT_MARKER`, `HELDOUT_HEADINGS`), written out
HT_MARKER = "**Declaration kind: held-out test.**"
HT_HEADINGS = (
    "## 0. In plain words (for the operator)",
    "## 1. Its inputs: only the pinned searches' finalists' lists",
    "## 2. The joint order: a rule fixed now, before any search is declared",
    "## 3. The firms' states: membership fixed by an event, states decided by rule (H-1'; E-257)",
    "## 4. The k and the level",
    "## 5. The rows, in order",
    "## 6. Power at each place in the joint sequence",
    "## 7. The held-out reads",
    "## 8. What a pass and what a fail mean",
    "## 9. Anything chosen after seeing results",
)


def heldout_text(title: str, line: str = "- **Judged-block reads:** `heldout_test`, `heldout_stress`\n",
                 marker: str = HT_MARKER, headings=HT_HEADINGS) -> str:
    """A held-out declaration's text in the template's form (its marker, its headings, its line)."""
    body = "".join(f"{h}\n\n<synthetic>\n\n" for h in headings)
    return f"# {title}\n\n{marker} A synthetic declaration (Q-194d's tests).\n\n{body}{line}"


HT_TEXT = heldout_text("F-98: a synthetic joint held-out test (not a declaration of this repository)")
HT_SHA = hashlib.sha256(HT_TEXT.encode("utf-8")).hexdigest()
HT_LIST = "7" * 64
SEED_RUN_ID = "verdict-seed@run-0"
LEDGER = "results/read_ledger.jsonl"
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


def _append(t: Path, rows) -> None:
    p = t / "DECISIONS.md"
    text = p.read_bytes().decode("utf-8")
    if not text.endswith("\n"):
        text += "\n"
    p.write_bytes((text + "".join(r + "\n" for r in rows)).encode("utf-8"))


def append_rows(t: Path, *rows: str) -> None:
    """Append decision rows to the tree's DECISIONS.md and commit them."""
    _append(t, rows)
    _git(t, "add", "DECISIONS.md")
    _git(t, "commit", "-q", "-m", "rows")


def commit_verdict(t: Path, *rows: str) -> str:
    """Append rows (a verdict row among them) and commit them **together with the ledger as it stands** (`git add -f`,
    also where `results/` is ignored), as the lead commits a verdict after collecting the run's lines. Returns the
    commit."""
    _append(t, rows)
    _git(t, "add", "DECISIONS.md")
    if (t / LEDGER).exists():
        _git(t, "add", "-f", LEDGER)
    _git(t, "commit", "-q", "-m", "the verdict, with the collected ledger")
    return _git(t, "rev-parse", "HEAD")


def seed_line(t: Path) -> dict | None:
    """F-98's ledgered held-out read in the tree, or None."""
    p = t / LEDGER
    if not p.exists():
        return None
    for x in p.read_text(encoding="utf-8").splitlines():
        rec = json.loads(x)
        if (rec.get("declaration") or {}).get("ref") == HT_PATH:
            return rec
    return None


def declare(t: Path, finalists: bool = True) -> str:
    """Write F-98 and pin it (and add its finalists' token, if `finalists`), committed. Returns the commit."""
    (t / "prereg").mkdir(exist_ok=True)
    (t / HT_PATH).write_bytes(HT_TEXT.encode("utf-8"))
    _git(t, "add", HT_PATH)
    append_rows(t, PIN_ROW, *((FINALISTS_ROW,) if finalists else ()))
    return _git(t, "rev-parse", "HEAD")


def is_seed(rec: dict) -> bool:
    """Whether a ledger line is a seeded joint test's read (its run id `SEED_RUN_ID`)."""
    return (rec.get("who") or {}).get("run_id") == SEED_RUN_ID


def joint_read(t: Path, files, *, market: str = "NQ", start: str = "2024-01-02", end: str = "2026-07-16",
               run_id: str = SEED_RUN_ID, purpose: str = "heldout_test", declaration: str = HT_PATH):
    """F-98's held-out read through the reader, inside a simulated clean run of `t` with its own run id; the
    environment and `reader.RUNS_DIR` restored."""
    from extended import reader as R
    saved = {k: os.environ.get(k) for k in ("S2X_CLEAN_RUN", "S2X_RUN_ID")}
    saved_dir = R.RUNS_DIR
    os.environ["S2X_CLEAN_RUN"], os.environ["S2X_RUN_ID"] = t.name, run_id
    R.RUNS_DIR = t.parent
    try:
        return R.authorise_engine_read(start, end, purpose=purpose, declaration=declaration, files=list(files),
                                       what="the joint held-out test (a synthetic seed)", repo=t, market=market)
    finally:
        R.RUNS_DIR = saved_dir
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def seed_with(t: Path, files, declaration: str, text: str) -> dict:
    """A tree's own held-out declaration (already pinned, its finalists' row in place) as the joint test: its
    `heldout_test` read (`joint_read`), then its verdict row committed with the ledger. Returns the read's line."""
    fid = declaration.split("/")[1].split("_")[0]
    joint_read(t, files, declaration=declaration)
    commit_verdict(t, verdict_row(fid=fid, sha=hashlib.sha256(text.encode("utf-8")).hexdigest()))
    for x in (t / LEDGER).read_text(encoding="utf-8").splitlines():
        if is_seed(json.loads(x)):
            return json.loads(x)
    raise AssertionError("no seeded line")


def settle(t: Path, files, *, market: str = "NQ", verdict: bool = True, start: str = "2024-01-02",
           end: str = "2026-07-16") -> dict:
    """In the committed git tree `t` (at `<runs>/<name>`, as a clean run's checkout is): declare F-98 with its
    finalists' token, make its `heldout_test` read of `start`..`end` of `market` (`joint_read`), then, if `verdict`,
    commit its verdict row together with the ledger (`commit_verdict`). Returns the read's ledger line."""
    declare(t)
    joint_read(t, files, market=market, start=start, end=end)
    if verdict:
        commit_verdict(t, verdict_row(market=market))
    line = seed_line(t)
    assert line is not None
    return line
