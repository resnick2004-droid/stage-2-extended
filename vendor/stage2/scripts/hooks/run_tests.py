"""PostToolUse hook: after a .py edit, run the suite's fast tier and report failures. Never blocks.

The tool call has already happened, so this cannot and should not undo anything. What it does
is make a break visible at the moment it is introduced rather than at the next manual run --
which matters most for the checks that keep the foundation honest (the stage-one reproduction,
the analytic ceilings, the pre-registration gate).

Reporting convention:
  * tests pass  -> exit 0, one-line summary on stdout.
  * tests fail  -> exit 2 with the failing output on stderr. For PostToolUse this surfaces the
    text to Claude without reverting anything, which is exactly "report, do not block".

Runs the fast tier only (R10): `-m "not slow and not heavy"`, about three minutes. The whole
suite took 25-60 minutes on this machine and always hit the timeout below, so the hook reported
nothing. The full suite runs in `make verify` and in CI (.github/workflows/verify.yml).

Also writes `results/.last_test_run.json` so `/status` can say when the suite last ran and what
it said (its summary names the fast tier).

`-o addopts=` clears the repository's own `-q` from pyproject.toml; without it the two combine
into `-qq` and the summary line with the count is suppressed. `PYTHONDONTWRITEBYTECODE=1` keeps
the subprocess from writing `__pycache__` into the read-only vendored tree.

Fails open: if pytest is missing or anything unexpected happens, exit 0.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WRITE_TOOLS = {"Write", "Edit", "MultiEdit"}
TIMEOUT_SECONDS = 600
#: The commit-time fast tier (R10), the same selection scripts/pre-commit runs.
FAST_TIER = "not slow and not heavy"


def summarise(output: str) -> str:
    """Pull pytest's own summary line out of its output."""
    for pattern in (
        r"\d+ failed[^\n]*",
        r"\d+ passed[^\n]*",
        r"no tests ran[^\n]*",
        r"ERROR[^\n]*",
    ):
        m = re.search(pattern, output)
        if m:
            return m.group(0).strip()
    return output.strip().splitlines()[-1] if output.strip() else "(no output)"


def record(repo: Path, exit_code: int, summary: str) -> None:
    try:
        path = repo / "results" / ".last_test_run.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "exit_code": exit_code,
                    "summary": summary,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
    except OSError:
        pass


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    try:
        if (payload.get("tool_name") or "") not in WRITE_TOOLS:
            return 0

        tool_input = payload.get("tool_input") or {}
        raw = tool_input.get("file_path") or tool_input.get("path") or ""
        if not str(raw).endswith(".py"):
            return 0

        repo = Path(payload.get("cwd") or ".").resolve(strict=False)

        # A .py edit outside this repository is not ours to test.
        target = Path(raw)
        if not target.is_absolute():
            target = repo / target
        try:
            target = target.resolve(strict=False)
        except (OSError, RuntimeError):
            return 0
        if repo not in target.parents and target != repo:
            return 0

        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-o", "addopts=", "-q", "--no-header", "-m", FAST_TIER],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            env=env,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        summary = f"fast tier: {summarise(out)}"
        record(repo, proc.returncode, summary)

        if proc.returncode == 0:
            sys.stdout.write(f"pytest after editing {Path(raw).name} ({summary})\n")
            return 0

        # Trim to the tail: the failure detail and the summary line are what matter.
        tail = "\n".join(out.splitlines()[-80:])
        sys.stderr.write(
            f"pytest FAILED after editing {Path(raw).name}: {summary}\n\n{tail}\n\n"
            "Reported, not blocked -- the edit stands. Fix the failure before building on it. "
            "If a stage-one reproduction test broke (tests/test_adapter_reproduces_stage_one.py) "
            "or an analytic ceiling was breached, that is an engine error and never a finding "
            "(CHARTER.md).\n"
        )
        return 2
    except subprocess.TimeoutExpired:
        sys.stderr.write(f"pytest (fast tier) timed out after {TIMEOUT_SECONDS}s; run it manually.\n")
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
