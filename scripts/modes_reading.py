"""RD-05 step 3 (`prereg/RD-05_firm_modes.md` 18 step 3): the registered scorecard (purpose modes_scorecard). Refusing: see `scripts/modes_part_f.py`
and `extended.modes_steps.step_problems(3)` -- part F is not built at this commit, so this step refuses.

    python scripts/modes_reading.py            # prints the refusals; exit 3
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from modes_part_f import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(3, sys.argv[1:]))
