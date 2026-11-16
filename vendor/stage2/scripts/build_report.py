"""Build stage two's exit (B) report and deck from the result files (T9, D-138).

    python scripts/build_report.py            # write docs/REPORT.md and docs/DECK.md
    python scripts/build_report.py --check    # exit 1 if the committed documents differ from a fresh build

Every number comes from `propedge.reporting.exit_report.evidence()`, which reads result CSVs through `read_result`
(manifests verified) and result manifests. Never edit the documents by hand: edit the renderer and rebuild.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from propedge.reporting.exit_report import (  # noqa: E402
    DECK_PATH, REPORT_PATH, evidence, render_deck, render_report,
)


def main(argv: list[str]) -> int:
    ev = evidence()
    docs = {REPORT_PATH: render_report(ev), DECK_PATH: render_deck(ev)}
    if "--check" in argv:
        stale = [p for p, text in docs.items()
                 if not (ROOT / p).is_file() or (ROOT / p).read_text(encoding="utf-8") != text]
        print("documents match a fresh build" if not stale else f"STALE: {', '.join(stale)}")
        return 1 if stale else 0
    for p, text in docs.items():
        (ROOT / p).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
