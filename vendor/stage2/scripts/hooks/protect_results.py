"""PreToolUse hook: deny direct edits to result files under results/.

Result CSVs and their sidecar manifests are written only by
`propedge.reporting.results.write_result`, which writes the data and its provenance together
and records the CSV's sha256. A hand-edited result breaks that link: the manifest's hash no
longer matches, `read_result` raises, and the number can no longer be cited anywhere.

The remedy for a wrong number is never to fix the file. It is to fix the code and regenerate,
so that the correction is itself reproducible.

What is allowed under results/: documentation (`README.md`), the append-only variant log
(`variants.jsonl`, written by `VariantCounter`), and the test-run record. What is denied:
`*.csv` and `*.manifest.json`.

Deny is exit code 2 with the reason on stderr. Fails open on any unexpected input.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

#: Files under results/ that a tool call may legitimately write.
ALLOWED_NAMES = {"README.md", ".gitkeep", "variants.jsonl", ".last_test_run.json"}

MESSAGE = """\
DENIED: {path}

Result files are never hand-edited (results/README.md; CLAUDE.md "result numbers are never
typed into documents").

Every result CSV is written by propedge.reporting.results.write_result together with a sidecar
manifest recording the script, git commit, seed, parameters, timestamp and the CSV's sha256.
Editing the CSV breaks that link: verify_result() will fail, read_result() will raise, and the
number can no longer be cited in any document.

To change a result, change the code and regenerate it:

    from propedge.reporting.results import write_result
    write_result(df, "{stem}", script="scripts/<script>.py", seed=<seed>, parameters={{...}})

If you are trying to correct a number in a report, the number is wrong in the code or the
document, not in the evidence.
"""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    try:
        tool = payload.get("tool_name") or ""
        if tool not in WRITE_TOOLS:
            return 0

        tool_input = payload.get("tool_input") or {}
        raw = (
            tool_input.get("file_path")
            or tool_input.get("notebook_path")
            or tool_input.get("path")
        )
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

        results_dir = (cwd / "results").resolve(strict=False)
        if results_dir not in target.parents:
            return 0

        if target.name in ALLOWED_NAMES:
            return 0

        if target.suffix == ".csv" or target.name.endswith(".manifest.json"):
            sys.stderr.write(MESSAGE.format(path=target, stem=target.stem))
            return 2
    except Exception:
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
