"""Move the done rows of `TASK_QUEUE.md` to `docs/archive/TASK_QUEUE_ARCHIVE.md` (Q-147, E-205). The lead runs it.

    python scripts/archive_queue.py --dry-run     # say what would move; write nothing
    python scripts/archive_queue.py               # move them

**What moves:** every queue row whose `state` cell begins with `done` (`done`, `done: ...`, `done; ...`), as
`scripts/status.py`'s own parser (`queue_rows`) reads the row -- so what this calls done is what the board calls done.
Nothing else in the queue changes: the headings, the table headers, every other row, the prose and the checklists stay
byte for byte, line endings included. Once, before the first section, the queue gains one line saying where its done
rows went.

**Where they go:** appended to the archive, never rewriting what is there: one block per run and per section the rows
stood in (`## <section> -- moved <date>`), the queue's table header above them, each row verbatim. The archive is made
with a short heading on the first run.

**Refusals (exit 1, nothing written):** a row to move whose id is already in the archive (a double move, or two rows
with one id); a moved row that would not read back from the archive as it read from the queue; any row lost or doubled
between the two files. The archive is written before the queue, each by a temporary file and a rename, so an
interrupted run can leave a row in both files, never in neither.

Only the lead writes `TASK_QUEUE.md` (E-005): a worker never runs this on its tree's queue except in a test, on a copy.
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

QUEUE = ROOT / "TASK_QUEUE.md"
ARCHIVE = ROOT / "docs" / "archive" / "TASK_QUEUE_ARCHIVE.md"
ARCHIVE_REL = "docs/archive/TASK_QUEUE_ARCHIVE.md"
POINTER = (f"Rows whose state begins with `done` are moved, verbatim and under their section, to "
           f"[`{ARCHIVE_REL}`]({ARCHIVE_REL}) by `scripts/archive_queue.py` (Q-147).")
ARCHIVE_HEAD = ("# Task queue archive\n\nThe rows of `TASK_QUEUE.md` whose state begins with `done`, moved here "
                "verbatim by `scripts/archive_queue.py` (Q-147), one block per run and per section they stood in.\n"
                "Append-only: a row is never edited here; a correction is made in the decision log.\n")
TABLE_HEAD = ("| id | task | owner | state | depends on | weight | retries | row |",
              "|---|---|---|---|---|---|---|---|")


#: the sibling `scripts/status.py`, loaded once by its path (Q-204); see `_status`
STATUS_FILE = HERE / "status.py"
_STATUS_MODULE_NAME = "s2x_archive_queue_status"
_S = None


def _status():
    """This tree's `scripts/status.py`, loaded by its path under a name of its own, once.

    Never `import status`: that bare name is ambiguous in a process that has imported the vendored engine
    (`extended.use_vendored_stage2()` puts `vendor/stage2/scripts`, which holds a `status.py` of its own, first on
    `sys.path`), so the parser would depend on what ran before in the process -- under pytest-xdist, on the files an
    earlier test put on the same worker (Q-204). `status.py` still puts the repository on `sys.path` for its own
    imports when it loads."""
    global _S
    if _S is None:
        import importlib.util  # noqa: PLC0415

        spec = importlib.util.spec_from_file_location(_STATUS_MODULE_NAME, STATUS_FILE)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _S = mod
    return _S


def _is_done_row(line: str) -> bool:
    rows = _status().queue_rows(line)
    return len(rows) == 1 and rows[0]["state"].startswith("done")


def _eol(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def plan(queue_text: str, archive_text: str, today: str) -> tuple[str, str, list[str]]:
    """The queue and archive texts after the move, and the ids moved, in queue order. Raises ValueError on a refusal."""
    S = _status()
    eol = _eol(queue_text)
    lines = queue_text.splitlines(keepends=True)
    keep: list[str] = []
    moved: dict[str, list[str]] = {}               # section heading -> moved row lines (without their line end)
    section = "(before any section)"
    for line in lines:
        bare = line.rstrip("\r\n")
        if bare.startswith("## "):
            section = bare[3:].strip()
        if _is_done_row(bare):
            moved.setdefault(section, []).append(bare)
        else:
            keep.append(line)
    ids = [S.queue_rows(r)[0]["id"] for rows in moved.values() for r in rows]
    if not ids:
        return queue_text, archive_text, []

    archived = Counter(r["id"] for r in S.queue_rows(archive_text))
    clash = sorted({i for i in ids if archived[i]} | {i for i, n in Counter(ids).items() if n > 1})
    if clash:
        raise ValueError(f"refused: id(s) already in the archive or moved twice: {', '.join(clash)}")

    a_eol = _eol(archive_text) if archive_text else eol
    out = archive_text if archive_text else ARCHIVE_HEAD.replace("\n", a_eol)
    if not out.endswith(a_eol):
        out += a_eol
    for sec, rows in moved.items():
        out += a_eol + f"## {sec} -- moved {today}" + a_eol + a_eol + a_eol.join((*TABLE_HEAD, *rows)) + a_eol

    new_queue = "".join(keep)
    if "TASK_QUEUE_ARCHIVE.md" not in new_queue:
        k = next((i for i, ln in enumerate(keep) if ln.startswith("## ")), len(keep))
        keep[k:k] = [POINTER + eol, eol]
        new_queue = "".join(keep)

    # Read back: no row lost or doubled, none done left, each moved row read exactly as it was.
    before = S.queue_rows(queue_text) + S.queue_rows(archive_text)
    after_q, after_a = S.queue_rows(new_queue), S.queue_rows(out)
    if sorted(map(repr, before)) != sorted(map(repr, after_q + after_a)):
        raise ValueError("refused: the rows read from the two files after the move differ from those before it")
    if any(r["state"].startswith("done") for r in after_q):
        raise ValueError("refused: a done row would stay in the queue")
    return new_queue, out, ids


def _replace(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(text.encode("utf-8"))
    os.replace(tmp, path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--queue", type=Path, default=QUEUE)
    ap.add_argument("--archive", type=Path, default=ARCHIVE)
    ap.add_argument("--date", default=date.today().isoformat(), help="the date written in the archive's block heading")
    ap.add_argument("--dry-run", action="store_true", help="say what would move; write nothing")
    args = ap.parse_args(argv)

    queue_text = args.queue.read_bytes().decode("utf-8")
    archive_text = args.archive.read_bytes().decode("utf-8") if args.archive.is_file() else ""
    try:
        new_queue, new_archive, ids = plan(queue_text, archive_text, args.date)
    except ValueError as e:
        print(f"archive_queue: {e}", file=sys.stderr)
        return 1
    if not ids:
        print(f"archive_queue: no done row in {args.queue}; nothing written")
        return 0
    left = len(_status().queue_rows(new_queue))
    verb = "would move" if args.dry_run else "moved"
    print(f"archive_queue: {verb} {len(ids)} done row(s) from {args.queue} to {args.archive}; {left} row(s) stay")
    print("  " + ", ".join(ids))
    if args.dry_run:
        return 0
    _replace(args.archive, new_archive)
    _replace(args.queue, new_queue)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
