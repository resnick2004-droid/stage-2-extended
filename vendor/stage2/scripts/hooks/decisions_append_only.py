"""PreToolUse hook: warn when an edit to DECISIONS.md would remove or change an existing line.

`DECISIONS.md` is append-only. Its value is that it records what was believed **at the time**;
an entry corrected in place is a lost record, and a reversal that overwrites the decision it
reverses hides the fact that anyone changed their mind.

This **warns** rather than denies, because there are legitimate edits to the file: appending a
row, fixing the header prose, adding a link. Denying all of them would make the log unmaintainable
and would push people to edit it outside the tool. So the hook allows the edit and says clearly
what is about to be lost -- both to the user (`systemMessage`) and to Claude
(`additionalContext`).

Detection: for an `Edit`, an `old_string` that contains a decision row (`| D-nn |`) means an
existing entry is being rewritten or removed. For a `Write`, the whole file is being replaced, so
every existing row is at risk and the warning names how many.

Fails open on any unexpected input.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROW = re.compile(r"\|\s*D-\d+\s*\|")

EDIT_WARNING = """\
WARNING -- append-only log: this edit to DECISIONS.md rewrites {n} existing decision {word}
({ids}).

DECISIONS.md is append-only (see its header): an entry is never edited after the fact, and a
reversal is a NEW entry that cites the old one by number. Editing an entry in place destroys the
record of what was believed when the decision was taken -- which is the only thing the log is for.

The edit has been allowed. If you meant to append, use `/decide <text>`, which numbers and dates
a new row for you. If you meant to reverse D-nn, add a new entry citing it instead.
"""

WRITE_WARNING = """\
WARNING -- append-only log: this rewrites DECISIONS.md wholesale, and the current file contains
{n} decision {word}.

DECISIONS.md is append-only: entries are never edited after the fact, and a reversal is a NEW
entry citing the old one. A whole-file write cannot be checked line by line, so confirm that every
existing entry survives unchanged.

The write has been allowed. Prefer `/decide <text>` to append a single numbered, dated row.
"""


def emit(message: str) -> None:
    """Allow the call, but surface the warning to both the user and Claude."""
    json.dump(
        {
            "systemMessage": message,
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": message,
            },
        },
        sys.stdout,
    )
    sys.stdout.write("\n")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    try:
        tool = payload.get("tool_name") or ""
        if tool not in {"Write", "Edit", "MultiEdit"}:
            return 0

        tool_input = payload.get("tool_input") or {}
        raw = tool_input.get("file_path") or tool_input.get("path") or ""
        if not raw:
            return 0

        cwd = Path(payload.get("cwd") or ".")
        target = Path(raw)
        if not target.is_absolute():
            target = cwd / target
        try:
            target = target.resolve(strict=False)
        except (OSError, RuntimeError):
            pass

        if target.name != "DECISIONS.md":
            return 0

        # The vendored stage-one DECISIONS.md is protected outright by protect_vendor.py.
        if "propsim" in target.parts:
            return 0

        if tool == "Edit":
            old = tool_input.get("old_string") or ""
            ids = re.findall(r"D-\d+", old)
            touched = [line for line in old.splitlines() if ROW.search(line)]
            if touched:
                n = len(touched)
                emit(
                    EDIT_WARNING.format(
                        n=n,
                        word="entry" if n == 1 else "entries",
                        ids=", ".join(dict.fromkeys(ids)) or "unnumbered",
                    )
                )
            return 0

        if tool == "MultiEdit":
            edits = tool_input.get("edits") or []
            ids: list[str] = []
            count = 0
            for e in edits:
                old = (e or {}).get("old_string") or ""
                rows = [line for line in old.splitlines() if ROW.search(line)]
                count += len(rows)
                ids += re.findall(r"D-\d+", old)
            if count:
                emit(
                    EDIT_WARNING.format(
                        n=count,
                        word="entry" if count == 1 else "entries",
                        ids=", ".join(dict.fromkeys(ids)) or "unnumbered",
                    )
                )
            return 0

        # Write: the whole file is replaced.
        if target.is_file():
            existing = sum(
                1 for line in target.read_text(encoding="utf-8", errors="replace").splitlines()
                if ROW.search(line)
            )
            if existing:
                emit(
                    WRITE_WARNING.format(
                        n=existing, word="entry" if existing == 1 else "entries"
                    )
                )
    except Exception:
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
