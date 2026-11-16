"""PreToolUse hook: deny direct edits to result files under `results/`.

Result CSVs and their sidecar manifests are written only through `extended.results.write_result` (the vendored
`propedge.reporting.results.write_result` underneath, with this repository's `results/` and git state), which writes
the data and its provenance together and records the CSV's sha256. A hand-edited result breaks that link: the
manifest's hash no longer matches, `read_result` raises, and the number can no longer be cited anywhere. The remedy for
a wrong number is never to fix the file: fix the code and regenerate it from a clean checkout, under its own decision
row, as a new file (a result file is never deleted or overwritten; DIRECTIVE Part 1).

**Which `results/`.** As `protect_vendor.py`: a directory named `results` that sits directly in a tree root (the main
repository, a worktree under `%LOCALAPPDATA%\\stage2-extended-wt\\`, a clean checkout under
`%LOCALAPPDATA%\\stage2-extended-runs\\`), or this repository's own `results/` (`_trees.py`). Stage 2's results under
`vendor/stage2/results/` are refused outright by `protect_vendor.py`.

Allowed under `results/`: `README.md`, `.gitkeep`, the append-only variant log `variants.jsonl`, the judged block's
append-only read ledger `read_ledger.jsonl` (Q-32; written by `extended.reader`), and the test-run record
`.last_test_run.json`. Denied: `*.csv` and `*.manifest.json`.

**The read ledger is append-only.** A tool call that would change or remove an existing line of a `read_ledger.jsonl`
(a `Write` whose content drops a current line, an `Edit` or `MultiEdit` whose `new_string` drops a line of its
`old_string`) is allowed and **warned** -- to the user (`systemMessage`) and to Claude (`additionalContext`), as
`decisions_append_only.py` warns; an append is silent. The proof is `tests/test_reader.py`'s history check, which
reports any committed line no longer in HEAD.

Deny = exit 2 with the reason on stderr. Fails open on any unexpected input.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

#: Files under results/ that a tool call may legitimately write.
ALLOWED_NAMES = {"readme.md", ".gitkeep", "variants.jsonl", ".last_test_run.json", "read_ledger.jsonl"}
#: Of those, the append-only ones whose existing lines a write is warned for changing (Q-32).
APPEND_ONLY_NAMES = {"read_ledger.jsonl"}

LEDGER_WARNING = """\
WARNING -- append-only: this {tool} changes or removes {n} existing line(s) of {path}, the judged block's read
ledger (Q-32; extended/reader.py), e.g. {example}

Every read of the judged block appends one line there (who, what, which dates, which declaration and purpose, when),
and a line is never edited or removed: the ledger is the record that the judged block was read once, by a pinned
declaration, for a declared purpose. tests/test_reader.py's history check reports any committed line that is no
longer in HEAD, and the reader refuses the next judged read while a line does not parse.

The write has been allowed. If a merge needs the lines of two branches, keep every line of both.
"""

MESSAGE = """\
DENIED: {path}

Result files are never hand-edited (CLAUDE.md "Results"; DIRECTIVE Part 1: no result file deleted or overwritten).

Every result CSV is written by extended.results.write_result (the vendored propedge.reporting.results.write_result
underneath, results_dir = this repository's results/) together with a sidecar manifest recording the script, git
commit, seed, parameters, timestamp and the CSV's sha256. Editing the CSV or its manifest breaks that link:
verify_result() fails, read_result() raises, and the number can no longer be cited in any document.

To change a result, change the code and regenerate it from a clean checkout of a named commit
(python scripts/run_clean.py), as a new file under its own decision row:

    from extended.results import write_result
    write_result(df, "{stem}_<new reading>", script="scripts/<script>.py", seed=<seed>, parameters={{...}})

If you are trying to correct a number in a report, the number is wrong in the code or the document, not in the
evidence.
"""


def _missing(old: str, new: str) -> list[str]:
    """Non-blank lines of `old` not in `new`, with multiplicity (the reader's `missing_lines`)."""
    have: dict[str, int] = {}
    for line in (new or "").splitlines():
        have[line] = have.get(line, 0) + 1
    out = []
    for line in (old or "").splitlines():
        if not line.strip():
            continue
        if have.get(line, 0) > 0:
            have[line] -= 1
        else:
            out.append(line)
    return out


def ledger_rewrites(payload: dict, target: Path) -> list[str]:
    """The existing lines of an append-only ledger that this tool call would change or remove."""
    tool = payload.get("tool_name") or ""
    ti = payload.get("tool_input") or {}
    if tool == "Write":
        current = target.read_text(encoding="utf-8") if target.is_file() else ""
        return _missing(current, ti.get("content") or "")
    if tool == "Edit":
        return _missing(ti.get("old_string") or "", ti.get("new_string") or "")
    if tool == "MultiEdit":
        return [x for e in (ti.get("edits") or []) for x in _missing(e.get("old_string") or "",
                                                                     e.get("new_string") or "")]
    return []


def warn(message: str) -> None:
    """Allow the call, and say so to the user and to Claude."""
    json.dump({"systemMessage": message,
               "hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": message}}, sys.stdout)
    sys.stdout.write("\n")


def main() -> int:
    try:
        import _trees as T

        payload = json.load(sys.stdin)
        if (payload.get("tool_name") or "") not in WRITE_TOOLS:
            return 0
        raw = T.target_of(payload)
        if not raw:
            return 0
        for target in T.candidates(raw, payload.get("cwd")):
            results = T.protected_dir(target, "results")
            if results is None or T.norm(results) == T.norm(target):
                continue
            name = target.name.lower()
            if name in APPEND_ONLY_NAMES:
                lost = ledger_rewrites(payload, target)
                if lost:
                    warn(LEDGER_WARNING.format(tool=payload.get("tool_name"), n=len(lost), path=target,
                                               example=lost[0][:160]))
                    return 0
            if name in ALLOWED_NAMES:
                continue
            if name.endswith(".csv") or name.endswith(".manifest.json"):
                stem = target.name.split(".csv")[0]
                sys.stderr.write(MESSAGE.format(path=target, stem=stem))
                return 2
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
