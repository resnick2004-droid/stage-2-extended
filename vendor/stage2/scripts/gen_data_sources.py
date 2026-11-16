"""Generate docs/DATA_SOURCES.md from config/data_sources.yaml (D-78).

The Markdown is a generated artefact, entirely: no hand-written section survives regeneration, so
`tests/test_data_sources_agreement.py` can require the file to equal `render()` byte for byte and
also compare it field by field in both directions for a readable failure.

Run: python scripts/gen_data_sources.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from propedge.data.sources import DataSources  # noqa: E402  (validates provenance on load)

YAML = ROOT / "config" / "data_sources.yaml"
MD = ROOT / "docs" / "DATA_SOURCES.md"

HEAD = (
    "| key | fact | value | status | requires | method | identifier | what was read | date read | read by |\n"
    "|---|---|---|---|---|---|---|---|---|---|"
)


def canonical(value) -> str:
    """The yaml value as the Markdown value cell shows it. Shared with the agreement test."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(canonical(v) for v in value) + "]"
    return str(value)


def cell(value) -> str:
    """One table cell: pipes escaped, newlines flattened, empty shown as an em dash."""
    if value is None or value == "":
        return "—"
    text = " ".join(str(value).split())
    return text.replace("|", "\\|")


def row(e) -> str:
    return "| " + " | ".join([
        f"`{e.key}`",
        cell(e.question),
        cell(canonical(e.value)),
        e.status,
        " or ".join(e.requires),
        cell(e.method),
        cell(e.identifier),
        cell(e.what_read),
        cell(e.date_read),
        cell(e.read_by),
    ]) + " |"


def render(yaml_path: Path = YAML) -> str:
    record = DataSources.load(yaml_path)
    facts = list(record)
    read = [e for e in facts if e.is_read]
    unread = [e for e in facts if not e.is_read]
    notes = [e for e in facts if e.note]

    out = [
        "# Data sources — QuantConnect facts and their provenance",
        "",
        "> **Generated from [`config/data_sources.yaml`](../config/data_sources.yaml) by",
        "> `python scripts/gen_data_sources.py`. Do not edit by hand** —",
        "> `tests/test_data_sources_agreement.py` fails if this file and the yaml differ.",
        "",
        "Facts about the vendor's data and server: dataset membership, start dates, the continuous-contract",
        "roll rule, resolution and the MCP server version. **Not firm rules** — those are in",
        "[`RULES_LEDGER.md`](../RULES_LEDGER.md), read on the Topstep help centre (D-78).",
        "",
        "Every `read` fact records what was read, how (`mcp_tool`, `api_script` or `manual_run`, with its",
        "identifier), the date and the reader. `requires` fixes the route before the fact is read: dataset",
        "facts accept a committed API script or a committed manual-run kit (D-82), never an agent",
        "conversation, which has no manifest (D-77). `propedge/data/sources.py` refuses to hand out an",
        "`unread` fact.",
        "",
        f"## A. Read — {len(read)} of {len(facts)}",
        "",
        HEAD,
        *[row(e) for e in read],
        "",
        f"## B. Not yet read — {len(unread)} of {len(facts)}",
        "",
        HEAD,
        *[row(e) for e in unread],
        "",
        "## C. Notes",
        "",
    ]
    if notes:
        for e in notes:
            out.append(f"- **`{e.key}`** — {' '.join(str(e.note).split())}")
    else:
        out.append("None.")
    out.append("")
    return "\n".join(out)


def main() -> int:
    MD.write_text(render(), encoding="utf-8", newline="\n")
    record = DataSources.load(YAML)
    print(f"docs/DATA_SOURCES.md regenerated: {len(record) - len(record.unread())} read, "
          f"{len(record.unread())} not")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
