"""PreToolUse hook: refuse a QuantConnect cloud run that reaches a confirmation window.

Matches the MCP tools that upload algorithm code or launch a backtest. It reads the tool input, finds the algorithm
source or the file contents inside it, and applies Stage 2's own check -- the vendored
`propedge.data.cloud_guard.assert_cloud_run_allowed` (imported from `vendor/stage2/`, never edited) -- so the agent
route and any scripted route cannot drift apart.

**Fails closed** for every guarded tool: if the vendored guard cannot be imported, if the payload holds no code it can
inspect, or if the code declares no dates, the call is denied. A backtest with no `SetStartDate` runs from the
beginning of the dataset.

**Two readings, recorded here (proposed for the lead's row with the port):**

* The vendored guard's boundary is Stage 2's `DEVELOPMENT_END` (2025-07-01, Stage 2 D-237), **earlier** than this
  repository's NQ boundary (development to 2026-07-16; NQ from 2026-07-17 is the declared confirmation window, Stage 2's
  `vendor/stage2/config/windows.yaml`, reserved). So this hook is stricter than the repository's windows -- it refuses
  any cloud run reaching 2025-07-01 -- and never laxer, on every market (ES, CL and GC's confirmation windows start
  on or after 2023-01-01 but are declared per market in that file; a cloud run's market is not read here). A cloud
  development read of 2025-07-01 to 2026-07-16 needs its own adapter under its own decision row.
* A `prereg_id` in the payload is **not** passed on: the vendored guard would look it up in Stage 2's
  `vendor/stage2/prereg/REGISTRY.md`, which authorises nothing in this repository. Until this repository registers a
  carried candidate under its own row, no cloud run may reach a confirmation window -- and that window is a purchase.

Exit codes follow the Claude Code hook convention: 0 allows, 2 denies with the message on stderr.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
VENDORED = ROOT / "vendor" / "stage2"

#: Tools that put code on QuantConnect or start a run against it.
GUARDED_SUFFIXES = (
    "create_backtest",
    "create_compile",
    "create_file",
    "update_file_contents",
    "patch_file",
    "create_optimization",
    "estimate_optimization_time",
)

#: Keys in a tool payload that may carry algorithm source.
CODE_KEYS = ("content", "contents", "code", "source", "file_contents", "patch", "body")


def _tool_is_guarded(name: str) -> bool:
    # Matched by suffix on any MCP server, as Stage 2 did: a QuantConnect server registered under another name is still
    # caught. The price, kept knowingly: another server's `create_file` (a drive, a document store) is held to the same
    # rule and refused unless its contents declare development-only dates.
    n = (name or "").lower()
    return any(n.endswith(s) or f"__{s}" in n or f".{s}" in n for s in GUARDED_SUFFIXES)


def _collect_code(payload) -> str:
    """Gather every string that might be algorithm source, from anywhere in the payload."""
    found: list[str] = []

    def walk(node, key=None):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, k)
        elif isinstance(node, list):
            for v in node:
                walk(v, key)
        elif isinstance(node, str):
            if key in CODE_KEYS or "date" in (key or "").lower() or len(node) > 200:
                found.append(node)

    walk(payload)
    return "\n".join(found)


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0                                   # not a payload we understand; other hooks run
    name = event.get("tool_name", "")
    if not _tool_is_guarded(name):
        return 0
    try:
        sys.path.insert(0, str(VENDORED))
        from propedge.data.cloud_guard import CloudRunRefused, assert_cloud_run_allowed
    except Exception as exc:                       # fail closed: an unguarded cloud run is never waved through
        print(f"DENIED: {name}: the vendored window guard (vendor/stage2/propedge/data/cloud_guard.py) could not be "
              f"imported ({type(exc).__name__}: {exc}), so the run's data span cannot be checked. Restore the snapshot "
              f"(python scripts/vendor_stage2.py --verify) before any cloud run.", file=sys.stderr)
        return 2
    payload = event.get("tool_input", {}) or {}
    code = _collect_code(payload)
    if not code.strip():
        print(f"DENIED: {name} carries no algorithm source this hook can inspect, so its data span cannot be checked. "
              f"Pass the algorithm's contents, with its SetStartDate and SetEndDate, in the call.", file=sys.stderr)
        return 2
    try:
        assert_cloud_run_allowed(code, prereg_id=None, what=name)
    except CloudRunRefused as exc:
        print(f"DENIED: {exc}\n\nThis repository: NQ development ends 2026-07-16 and NQ from 2026-07-17 is the "
              f"declared confirmation window, never read until a carried candidate is registered (a purchase); this "
              f"hook applies Stage 2's earlier boundary unchanged, so it refuses more than the windows require, never "
              f"less, and no prereg id authorises a confirmation run here yet (qc_window_guard.py's docstring).",
              file=sys.stderr)
        return 2
    except Exception as exc:                       # fail closed
        print(f"DENIED: {name}: the window guard failed ({type(exc).__name__}: {exc}).", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
