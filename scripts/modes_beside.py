"""RD-05 step 4 (`prereg/RD-05_firm_modes.md` 18 step 4): the denial ladder and the placement beside (purpose modes_ladder_beside). Refusing: see `scripts/modes_part_f.py`
and `extended.modes_steps.step_problems(4)` -- part F is not built at this commit, so this step refuses.

    python scripts/modes_beside.py            # prints the refusals; exit 3
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from modes_part_f import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(4, sys.argv[1:]))
