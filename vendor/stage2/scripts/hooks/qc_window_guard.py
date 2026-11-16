"""PreToolUse hook: refuse a QuantConnect cloud run that reaches the confirmation window.

Matches the MCP tools that upload algorithm code or launch a backtest. It reads the tool input,
finds the algorithm source or the file contents inside it, and applies the same check an API
script applies -- `propedge.data.cloud_guard.assert_cloud_run_allowed` -- so the agent route and
the scripted route cannot drift apart.

Fails closed in both directions: if the payload holds no code it can inspect, or the code has no
declared dates, the call is denied. A backtest with no `SetStartDate` runs from the beginning of
the dataset.

Exit codes follow the Claude Code hook convention: 0 allows, 2 denies with the message on stderr.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from propedge.data.cloud_guard import CloudRunRefused, assert_cloud_run_allowed  # noqa: E402

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
    payload = event.get("tool_input", {}) or {}
    code = _collect_code(payload)
    prereg_id = None
    for key in ("prereg_id", "preregId", "prereg"):
        if isinstance(payload.get(key), str):
            prereg_id = payload[key]
            break
    if not code.strip():
        print(
            f"DENIED: {name} carries no algorithm source this hook can inspect, so its data "
            f"span cannot be checked. Generate the algorithm from the repository template "
            f"(dates from propedge/data/window.py) and pass its contents in the call.",
            file=sys.stderr,
        )
        return 2
    try:
        assert_cloud_run_allowed(code, prereg_id=prereg_id, what=name)
    except CloudRunRefused as exc:
        print(f"DENIED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
