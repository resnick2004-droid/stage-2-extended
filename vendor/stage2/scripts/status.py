"""Print the stage's status: open tasks, pre-registrations, unverified rules, last test run.

Backs the `/status` slash command. Reads the Markdown documents rather than a database,
because those documents are what a human reads and they must not diverge from what the tools
report.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from propedge.backtest.harness import PreregRegistry, VariantCounter  # noqa: E402
from propedge.contract.rules import load_rules  # noqa: E402
from propedge.reporting.results import list_results  # noqa: E402

LAST_TEST_RUN = ROOT / "results" / ".last_test_run.json"


def open_tasks() -> list[tuple[str, str]]:
    """Tasks in NEXT_STEPS.md (T-numbered, and the R reset list of D-454) whose status is not `closed` or `parked`."""
    path = ROOT / "NEXT_STEPS.md"
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+([TR]\d*)\s+—\s+(.*?)\s+·\s+`([^`]+)`", line)
        if not m:
            m = re.match(r"^##\s+([TR]\d*)\s+-\s+(.*?)\s+·\s+`([^`]+)`", line)
        if m:
            tid, title, status = m.group(1), m.group(2), m.group(3)
            if status.lower() not in {"closed"} and not status.lower().startswith("parked"):
                out.append((tid, f"{title} [{status}]"))
    return out


def closing_checklist() -> list[tuple[bool, str]]:
    """The checklist lines from NEXT_STEPS.md, with their checkbox state."""
    path = ROOT / "NEXT_STEPS.md"
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^- \[([ xX])\]\s+(.*)$", line.strip())
        if m:
            out.append((m.group(1).lower() == "x", m.group(2)))
    return out


def last_test_run() -> str:
    if not LAST_TEST_RUN.is_file():
        return "no recorded test run (run `make test`, or `.\\scripts\\make.ps1 test`)"
    try:
        data = json.loads(LAST_TEST_RUN.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "recorded test run is unreadable"
    return (
        f"{data.get('timestamp', '?')}: {data.get('summary', '?')} "
        f"(exit {data.get('exit_code', '?')})"
    )


def main() -> int:
    print("=" * 72)
    print("STAGE TWO STATUS")
    print("=" * 72)

    print("\n## Open tasks (NEXT_STEPS.md)")
    tasks = open_tasks()
    if not tasks:
        print("  (none open)")
    for tid, desc in tasks:
        print(f"  {tid}  {desc}")

    print("\n## Pre-registrations")
    reg = PreregRegistry.load()
    if len(reg) == 0:
        print("  none registered yet (create one with /prereg <title>)")
    else:
        for e in reg.all():
            outcome = e.outcome or "(no outcome recorded)"
            print(f"  {e.id}  [{e.status}]  {e.title} -> {outcome}")
        openents = reg.open_entries()
        if openents:
            print(f"  -> {len(openents)} with no recorded outcome: "
                  f"{', '.join(e.id for e in openents)}")

    print("\n## Rules ledger")
    try:
        ledger = load_rules()
        unver = ledger.unverified()
        print(f"  {len(ledger.verified())} verified, {len(unver)} not verified")
        if unver:
            print("  NOT VERIFIED (code cannot load these):")
            for e in unver:
                print(f"    - {e.name}: {e.status}")
    except Exception as exc:  # noqa: BLE001
        print(f"  could not read the rules ledger: {exc}")

    print("\n## Variants tried")
    try:
        counter = VariantCounter()
        print(f"  {counter.count()} distinct configurations recorded "
              f"({counter.count(distinct=False)} runs)")
    except Exception as exc:  # noqa: BLE001
        print(f"  could not read the variant counter: {exc}")

    print("\n## Result files")
    results = list_results()
    if not results:
        print("  none yet")
    for r in results:
        mark = "ok  " if r.get("verified") else "FAIL"
        print(f"  [{mark}] {r['file']}  {r.get('message', '')}")

    print("\n## Last test run")
    print(f"  {last_test_run()}")

    print("\n## Closing checklist")
    for done, text in closing_checklist():
        print(f"  [{'x' if done else ' '}] {text[:100]}")

    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
