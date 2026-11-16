"""Write the BLS 08:30 ET release days into `propedge/outcomes/fv3_core.py` as per-year bitmasks (`NEWS`), from
`data/release_days_0830_2009_2025.csv` (its provenance beside it, `data/releases_bls_0830_2009_2025.provenance.json`;
the data-integrity check before it entered). The literal is data in code so the kit, the parser and the tests read one
source; `tests/test_fv3_kit.py` checks the literal against the file.

    python scripts/make_fv3_news.py           # rewrites the NEWS block in fv3_core.py
    python scripts/make_fv3_news.py --check   # exit 1 if the block differs from the file
"""
from __future__ import annotations

import csv
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "release_days_0830_2009_2025.csv"
CORE = ROOT / "propedge" / "outcomes" / "fv3_core.py"
BLOCK = re.compile(r"NEWS = \{[^}]*\}", re.S)


def masks(path: Path = DATA) -> dict[int, int]:
    out: dict[int, int] = {}
    with path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            d = date.fromisoformat(r["date"])
            out[d.year] = out.get(d.year, 0) | (1 << (d - date(d.year, 1, 1)).days)
    return out


def literal(m: dict[int, int]) -> str:
    return "NEWS = {\n" + "".join(f"    {y}: 0x{m[y]:x},\n" for y in sorted(m)) + "}"


def main(argv: list[str]) -> int:
    text = CORE.read_text(encoding="utf-8")
    want = literal(masks())
    found = BLOCK.search(text)
    if found is None:
        print("REFUSED: no NEWS block in fv3_core.py")
        return 2
    if "--check" in argv:
        same = found.group(0) == want
        print("NEWS block matches the data file" if same else "NEWS block DIFFERS from the data file")
        return 0 if same else 1
    CORE.write_text(text[:found.start()] + want + text[found.end():], encoding="utf-8", newline="\n")
    print(f"wrote {sum(bin(v).count('1') for v in masks().values())} release days into {CORE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
