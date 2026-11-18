"""RD-05 step 0 (`prereg/RD-05_firm_modes.md` 18 step 0; 7, 8, 11 item 1, 16): the rules arithmetic -- parts A, B and
E item 1 and the oracle count N -- from the record by key. No seed, no bar, no engine run, no trade, no result read.

    python scripts/modes_rules.py --plan        # light: the refusals, the counts step 0 would fix; writes nothing
    python scripts/run_clean.py --name rd05-step0 --task <Q> --hours 1 --mem-gb 0.5 -- python scripts/modes_rules.py

**Refusing first** (13.2; 18's waits; `extended.modes_steps.step_problems(0)`): the declaration at its pin; no
`e015-limits:` row; every Appendix R key at its stated status; every role of every mode-corner resolving (the loaders
refusing a non-verified value; A-19's parses); every shared identity held at a commit containing the record (Q-05,
Q-80, Q-93, Q-101, Q-104). Then **the stated-fewest check, refusing** (7): a computed `k_E` that differs from the
firm's own statement stops step 0. Then **the boundary cells' exactness, refusing** (7 item 8 against 9.6): a declared
boundary cell at which a pass cannot end at exactly `T` would stop step 2 on a correct engine, so step 0 refuses until
the lead rules (see `extended.modes_rules.boundary_exact`).

**Writes** `results/modes_rules.csv` (sections `terms`, `flip_days`, `stated_check`, `flip_sizes`, `implied_days`,
`boundary_cells`, `sizing`, `allowed`, `size_binding`, `oracle_count`, and `coin_cells` -- the coin runs step 2 runs,
fixed here) with its manifest through `extended.results`, only from a clean checkout.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import pandas as pd  # noqa: E402

from extended import modes_rules as R  # noqa: E402
from extended import modes_steps as S  # noqa: E402
from extended import modes_terms as M  # noqa: E402

SCRIPT = "scripts/modes_rules.py"


class BoundaryDefect(RuntimeError):
    """A declared boundary cell at which every pass cannot end at exactly T (7 item 8 against 9.6)."""


def tables() -> pd.DataFrame:
    """Every section of step 0's file as one frame (`section` first); refusing on the stated-fewest check and on an
    inexact boundary cell."""
    a = R.part_a_rows()
    inexact = [b for b in a["boundary_cells"] if not b["exact_by_lattice"]]
    if inexact:
        cells = ", ".join(f"{b['mode']} w={b['w']:g} r={b['r']:g}" for b in inexact)
        raise BoundaryDefect(f"7 item 8's declared conditions list {len(inexact)} boundary cells at which a pass "
                             f"overshoots T ({cells}); 9.6 would stop step 2 there on a correct engine -- the lead's "
                             "ruling is needed before step 0 writes (a declaration defect, reported)")
    b = R.part_b_rows()
    cells = R.coin_cells()
    count = R.oracle_count(cells, a["boundary_cells"])
    parts = {"terms": R.terms_rows(), **a, **b, "oracle_count": [count], "coin_cells": cells}
    frames = []
    for sec, rows in parts.items():
        if rows:
            df = pd.DataFrame(rows)
            df.insert(0, "section", sec)
            frames.append(df)
    out = pd.concat(frames, ignore_index=True, sort=False)
    out["described"] = "described, not carried"
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--plan", action="store_true", help="print the refusals and the counts; write nothing")
    args = ap.parse_args(argv)
    t0 = time.time()
    probs = S.step_problems(0)
    for p in probs:
        print(f"REFUSED: {p}")
    if args.plan:
        try:
            a = R.part_a_rows()
            print(f"stated-fewest rows: {len(a['stated_check'])}; boundary cells: {len(a['boundary_cells'])} "
                  f"({sum(not b['exact_by_lattice'] for b in a['boundary_cells'])} inexact)")
            print(f"oracle count: {R.oracle_count()}")
        except Exception as exc:                                   # noqa: BLE001
            print(f"REFUSED: {type(exc).__name__}: {exc}")
        return 3 if probs else 0
    if probs:
        return 3
    try:
        df = tables()
    except (R.StatedFewestMismatch, BoundaryDefect) as exc:
        print(f"REFUSED: {exc}")
        return 3
    from extended import results

    params = {"prereg": M.DECLARATION, "prereg_sha256": M.DECLARATION_SHA256, "pinning_row": M.PINNING_ROW,
              "declared": {k: str(v.value) for k, v in M.DECLARED.items()}, "u_rules": {k: v.cite for k, v in
                                                                                     M.U_RULES.items()},
              "record_keys": M.RECORD_KEYS, "head": S.head_sha(), "e015_limits": "none approved before the run's commit"}
    results.write_result(df, "modes_rules", script=SCRIPT, seed=None, require_seed=False, parameters=params,
                         prereg_id=M.PREREG_ID, exploratory=False,
                         description="RD-05 step 0: flip days, the sizing grid, the binding size, N (described, not "
                                     "carried)")
    print(f"step 0 written in {time.time() - t0:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
