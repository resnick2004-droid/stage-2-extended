"""PreToolUse hook: deny any write or edit under vendor/ (E-002). Stage 2 is vendored read-only and imported, never
edited; tests/test_vendor_integrity.py is the proof that survives outside a Claude session. Deny = exit 2 with the
reason on stderr. Fails open on any unexpected input (the hash test is the real guarantee)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
MESSAGE = """DENIED: {path}

vendor/ is READ-ONLY (DECISIONS.md E-002). Stage 2's engine, rules and results are vendored as one unmodified snapshot
of commit f1b42e2, pinned by vendor/MANIFEST_stage2.sha256. Import it; write adapters in this repository's own package.
A newer Stage 2 is a new snapshot under a new decision row (scripts/vendor_stage2.py).
"""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if (payload.get("tool_name") or "") not in WRITE_TOOLS:
            return 0
        ti = payload.get("tool_input") or {}
        raw = ti.get("file_path") or ti.get("notebook_path") or ti.get("path")
        if not raw:
            return 0
        cwd = Path(payload.get("cwd") or ".")
        target = Path(raw)
        if not target.is_absolute():
            target = cwd / target
        target = target.resolve(strict=False)
        root = Path(__file__).resolve().parent.parent.parent
        protected = (root / "vendor").resolve(strict=False)
        if target == protected or protected in target.parents:
            sys.stderr.write(MESSAGE.format(path=target))
            return 2
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
