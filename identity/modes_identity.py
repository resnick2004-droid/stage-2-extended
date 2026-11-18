"""RD-05's replay identity (`prereg/RD-05_firm_modes.md` 13.1 item 2), before step 3; purpose `identity`.

Through A-14 at `TS` and every adapter at its Topstep setting: U1's start rows for P-14 and P-16 (both arms, every
start, every column as E-010 compared them), the registered gate paths (all 500, to 1e-6), and `LU50`'s composition
against the vendored joint engine's one-firm `lucid_setup` at `ADDON_50`. **NOT BUILT at this commit**: A-14's
composition and part F's account classes are not built, so this identity refuses (exit 3) and reads nothing.
"""
from __future__ import annotations

import sys


def main() -> int:
    print("NOT BUILT: RD-05's replay identity needs A-14's composition and part F's account classes; nothing is read")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
