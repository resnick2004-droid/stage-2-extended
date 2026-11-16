"""PreToolUse hook: warn when a write to DECISIONS.md would change an existing row, or comes from a worktree.

`DECISIONS.md` is append-only: a row is never edited; a correction is a new row that names the one it corrects (its
header). Its value is that it records what was believed **at the time**. And it has one writer: only the lead, on
`master`, appends to it (the single-writer rule, E-005); a worker proposes a row as one finished line `| E-NNN | ... |`
in its hand-back and the lead numbers and commits it.

This **warns** rather than denies, because there are legitimate edits (appending a row, the header prose). It allows the
call and says what is at stake -- to the user (`systemMessage`) and to Claude (`additionalContext`):

* an `Edit` or `MultiEdit` whose `old_string` holds a decision row (`| E-nnn |`) that does not survive verbatim in its
  `new_string` -- an existing entry rewritten or removed (an append anchored on the last row keeps it, and is silent);
* a `Write` over an existing file that holds rows -- every row is at risk and the warning names how many;
* any write to a `DECISIONS.md` inside a worktree or detached checkout (its tree's `.git` is a file): only the lead
  writes the decision log.

Stage 2's log under `vendor/stage2/` is refused outright by `protect_vendor.py` and not commented on here.
Fails open on any unexpected input.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

ROW = re.compile(r"\|\s*E-\d+\s*\|")
ROW_ID = re.compile(r"\|\s*(E-\d+)\s*\|")

EDIT_WARNING = """\
WARNING -- append-only log: this edit to DECISIONS.md rewrites or removes {n} existing decision {word} ({ids}).

DECISIONS.md is append-only (its header): a row is never edited after the fact, and a correction or reversal is a NEW
row that cites the old one by number. Editing a row in place destroys the record of what was believed when the
decision was taken -- the only thing the log is for.

The edit has been allowed. If you meant to append, use `/decide <text>` (the lead's command), which numbers and dates a
new row. If you meant to reverse {first}, add a new row citing it instead.
"""

WRITE_WARNING = """\
WARNING -- append-only log: this rewrites DECISIONS.md wholesale, and the current file holds {n} decision {word}.

DECISIONS.md is append-only: rows are never edited after the fact, and a correction is a NEW row citing the old one.
A whole-file write cannot be checked row by row, so confirm that every existing row survives unchanged.

The write has been allowed. Prefer `/decide <text>` to append a single numbered, dated row.
"""

WORKTREE_WARNING = """\
WARNING -- single writer: {path} is inside a worktree or checkout ({root}), and only the lead writes the decision log
(E-005). A worker never appends to DECISIONS.md: end the hand-back with the proposed row as one finished line
`| E-NNN | <date> | **<decision>** ... | <basis> |`, and the lead numbers it and commits it on master.

The write has been allowed; it will not merge as written.
"""


def emit(messages: list[str]) -> None:
    """Allow the call, but surface the warnings to both the user and Claude."""
    message = "\n".join(messages)
    json.dump({"systemMessage": message,
               "hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": message}}, sys.stdout)
    sys.stdout.write("\n")


def rewritten_rows(old: str, new: str) -> list[str]:
    """Rows of `old` that do not appear verbatim (ignoring trailing whitespace) among the lines of `new`."""
    kept = {line.rstrip() for line in (new or "").splitlines()}
    return [line for line in (old or "").splitlines() if ROW.search(line) and line.rstrip() not in kept]


def edit_warning(rows: list[str]) -> str:
    ids = list(dict.fromkeys(m.group(1) for line in rows for m in [ROW_ID.search(line)] if m))
    n = len(rows)
    return EDIT_WARNING.format(n=n, word="row" if n == 1 else "rows", ids=", ".join(ids) or "unnumbered",
                               first=ids[0] if ids else "a row")


def main() -> int:
    try:
        import _trees as T

        payload = json.load(sys.stdin)
        tool = payload.get("tool_name") or ""
        if tool not in {"Write", "Edit", "MultiEdit"}:
            return 0
        raw = T.target_of(payload)
        if not raw:
            return 0
        found = T.candidates(raw, payload.get("cwd"))
        target = found[-1]
        if target.name.lower() != "decisions.md":
            return 0
        if any(T.protected_dir(c, "vendor") is not None for c in found):
            return 0  # the vendored log: protect_vendor.py denies it outright

        ti = payload.get("tool_input") or {}
        messages: list[str] = []
        if tool == "Edit":
            rows = rewritten_rows(ti.get("old_string") or "", ti.get("new_string") or "")
            if rows:
                messages.append(edit_warning(rows))
        elif tool == "MultiEdit":
            rows = []
            for e in ti.get("edits") or []:
                rows += rewritten_rows((e or {}).get("old_string") or "", (e or {}).get("new_string") or "")
            if rows:
                messages.append(edit_warning(rows))
        elif target.is_file():
            existing = sum(1 for line in target.read_text(encoding="utf-8", errors="replace").splitlines()
                           if ROW.search(line))
            if existing:
                messages.append(WRITE_WARNING.format(n=existing, word="row" if existing == 1 else "rows"))

        root = T.tree_root(target)
        if root is not None and T.is_worktree(root):
            messages.append(WORKTREE_WARNING.format(path=target, root=root))
        if messages:
            emit(messages)
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
