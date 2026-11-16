"""PreToolUse hook: refuse every QuantConnect live-trading tool.

`.claude/settings.json` denies these by permission rule. This hook is the second layer, and it exists because a
permission list is matched by name: a tool added to the server later, or named slightly differently by a different
server build, would slip a name-based deny list and would not slip a pattern.

Nothing in this repository's question (`CHARTER.md`) requires deploying an algorithm, connecting a brokerage, or sending
a command to a running one, and the operator's hard limit forbids it: no live orders and no automated or API order
entry (DIRECTIVE Part 1; it gets prop accounts banned). So the whole live surface is denied -- including the read-only
tools, because a `read_live_*` call that succeeds means a deployment exists, and there should be none.

Ported unchanged from Stage 2's `scripts/hooks/qc_no_live_trading.py` (the tool list and the patterns).

Exit codes: 0 allows, 2 denies with the message on stderr.
"""
from __future__ import annotations

import json
import re
import sys

#: The Live Trading group of the official server's published tool list (README, 64 tools, read 2026-09-23 by
#: Stage 2). Denied by exact name.
LIVE_TOOLS = (
    "authorize_connection",
    "create_live_algorithm",
    "read_live_algorithm",
    "list_live_algorithms",
    "read_live_chart",
    "read_live_logs",
    "read_live_portfolio",
    "read_live_orders",
    "read_live_insights",
    "stop_live_algorithm",
    "liquidate_live_algorithm",
    "create_live_command",
    "broadcast_live_command",
    # named in the docs pages but not in the README's list; denied so a build difference cannot open a gap
    "read_live_holdings",
    "search_live_logs",
)

#: Denied by shape, so a tool added later is covered without this file being edited.
LIVE_PATTERNS = (
    re.compile(r"_live(_|$)"),
    re.compile(r"(^|_)live_"),
    re.compile(r"brokerage"),
    re.compile(r"authorize_connection"),
    re.compile(r"broadcast"),
    re.compile(r"deploy"),
)


def is_live_tool(name: str) -> bool:
    n = (name or "").lower().rsplit("__", 1)[-1].rsplit(".", 1)[-1]
    if n in LIVE_TOOLS:
        return True
    return any(p.search(n) for p in LIVE_PATTERNS)


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    name = event.get("tool_name", "")
    if is_live_tool(name):
        print(
            f"DENIED: {name} is a live-trading tool. This project never deploys an algorithm, connects a brokerage, "
            f"or commands a running one: no live orders and no automated or API order entry (DIRECTIVE Part 1; the "
            f"operator's hard limit). Read-only live tools are denied too: a successful read means a deployment "
            f"exists, and there should be none.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
