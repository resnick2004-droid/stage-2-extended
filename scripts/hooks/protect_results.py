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

Allowed under `results/`: `README.md`, `.gitkeep`, the append-only variant log `variants.jsonl`, and the test-run record
`.last_test_run.json`. Denied: `*.csv` and `*.manifest.json`.

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
ALLOWED_NAMES = {"readme.md", ".gitkeep", "variants.jsonl", ".last_test_run.json"}

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
