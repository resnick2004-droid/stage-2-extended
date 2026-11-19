"""H3-A's declared inputs, printed from `extended/three_way_h3a.py` (the red team's B-3): the draft's Appendix C holds
this output line for line (`tests/test_h3_draft.py`). No draw, no bar, no result.

    python docs/plans/scripts/three_way/h3a_inputs.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import three_way_h3a as H  # noqa: E402


def report() -> str:
    return "\n".join(f"{name} = {value}" for name, value in H.declared())


def main() -> None:
    print(report())


if __name__ == "__main__":
    main()
