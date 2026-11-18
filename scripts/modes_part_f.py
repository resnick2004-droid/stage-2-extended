"""RD-05 steps 3 to 5 (`prereg/RD-05_firm_modes.md` 18 steps 3-5; 12): the registered scorecard, the beside readings
and the gates -- the shared refusing entry point of `scripts/modes_reading.py`, `scripts/modes_beside.py` and
`scripts/modes_gate.py`. Each prints its step's refusals (`extended.modes_steps.step_problems`) and refuses (exit 3)
while any stands; part F's adapters are not built at this commit, so every one of them refuses with `NOT BUILT`.
Nothing is read: no purpose is authorised, no bar opened, no result written.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main(step: int, argv: list[str] | None = None) -> int:
    from extended import modes_steps as S

    probs = S.step_problems(int(step))
    for p in probs:
        print(f"REFUSED (step {step}): {p}")
    if probs:
        return 3
    raise RuntimeError(f"step {step} passed its refusals but its body is not built")   # unreachable while NOT_BUILT


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1])))
