"""PreToolUse hook: deny any write or edit whose target is under vendor/propsim/ or vendor/propfirms/ (D-463).

D-01: stage one is vendored read-only and is imported, never edited. This hook is the fast
feedback; `tests/test_vendor_integrity.py` and `tests/test_no_writes_to_vendor.py` are the
proof that survives outside a Claude session.

Deny is signalled by exit code 2 with the reason on stderr, which Claude reads.

Fails open: any unexpected input, missing field or internal error exits 0. A hook that crashes
must not make the repository unusable, and the hash checks in the test suite are the real
guarantee.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
#: the vendored trees: stage one (D-01) and the multi-firm repository's Lucid subset (D-463,
#: pinned by vendor/MANIFEST_propfirms.sha256)
PROTECTED = ("propsim", "propfirms")

MESSAGE = """\
DENIED: {path}

vendor/propsim/ and vendor/propfirms/ are READ-ONLY (DECISIONS.md D-01, D-463).

Stage one is vendored as a single unmodified copy so that every stage-two result is
attributable to stage-two code. It is pinned by vendor/MANIFEST.sha256 (114 files) and
verified before and after every test run.

Import it; do not edit it:

    from propedge.contract.adapter import Policy, Rules, run_combine, run_xfa

If the engine needs to behave differently, write an adapter or subclass in propedge/ --
propedge/contract/adapter.py is the seam. If you are recording something you have learned
about stage one, it belongs in this repository's DECISIONS.md or docs/, not in the vendored
tree.
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

        # Resolve without requiring existence (the file may be about to be created).
        try:
            target = target.resolve(strict=False)
        except (OSError, RuntimeError):
            pass

        for name in PROTECTED:
            protected = (cwd / "vendor" / name).resolve(strict=False)
            if target == protected or protected in target.parents:
                sys.stderr.write(MESSAGE.format(path=target))
                return 2
    except Exception:
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
