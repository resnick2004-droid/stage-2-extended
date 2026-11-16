"""PreToolUse hook: deny any write or edit under a vendored tree (E-002).

Stage 2 is vendored read-only at `vendor/stage2/` -- one unmodified snapshot of commit f1b42e2, pinned by
`vendor/MANIFEST_stage2.sha256` -- and imported, never edited. This hook is the fast feedback;
`tests/test_vendor_integrity.py` and `python scripts/vendor_stage2.py --verify` are the proof that survives outside a
Claude session.

**Which `vendor/`.** The hooks run from this repository's `scripts/hooks/` whatever the target, and the target may lie in
a worktree (`%LOCALAPPDATA%\\stage2-extended-wt\\<name>`) or a clean checkout (`%LOCALAPPDATA%\\stage2-extended-runs\\
<name>`). So a target is denied when it lies under a directory named `vendor` that sits directly in a tree root -- a
directory holding `.git`, a directory in the main repository, a file in a worktree or checkout -- or under this
repository's own `vendor/` (`_trees.py`). The licensed bars and atlas under `vendor/stage2/data/` are covered too:
they are never written, and in a worktree they are a junction into this tree.

Deny = exit 2 with the reason on stderr. Fails open on any unexpected input (the hash test is the real guarantee).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
MESSAGE = """DENIED: {path}

{vendor} is READ-ONLY (DECISIONS.md E-002). Stage 2's engine, rules, results and the licensed data are vendored as one
unmodified snapshot of commit f1b42e2, pinned by vendor/MANIFEST_stage2.sha256 (the data by
vendor/DATA_MANIFEST_stage2.sha256), and this holds in every worktree and clean checkout of the repository too.
Import it; write adapters in this repository's own package (extended/). A newer Stage 2 is a new snapshot under a new
decision row (scripts/vendor_stage2.py). Something learned about Stage 2 belongs in this repository's docs/ or a
proposed E-row, never in the vendored tree.
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
            vendor = T.protected_dir(target, "vendor")
            if vendor is not None:
                sys.stderr.write(MESSAGE.format(path=target, vendor=vendor))
                return 2
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
