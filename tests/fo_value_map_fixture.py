"""A synthetic `u_value_map.csv` in the vendored file's **long** schema (Q-117f), for F-03's tests.

F-03's run 1 crashed at `scripts/fo_opening.py`'s `mean_dv_c` (`KeyError: 'place'`): the reader assumed a wide file
(columns `place`, `mean_dv`), while Stage 2's `vendor/stage2/results/u_value_map.csv` is long -- one value a row, its
place in `state`, its measure's name in `measure`, its number in `value`. The synthetic runs had stubbed `Ctx.mean_dv`
with a constant, so the reader itself never ran on any file. This module builds the file the reader meets: **the
columns are read from the vendored file's header line** (the header only -- no row, no value of the vendored file is
read), the rows synthetic, the manifest written by `extended.results.write_result` into a temporary folder (never a
`results/` folder of this repository; `write_result` refuses one outside a clean run).

The rows: the target (`place_values`, `p16`, `funded`, `c_funded_opening`, `mean_dv`) at the caller's value, and one
decoy for each key it is selected by -- another section, another base, another place, another measure -- each at its
own value, so a reader that drops any one key reads a decoy (or two rows) and is caught.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

VALUE_MAP = "u_value_map.csv"
TARGET = {"section": "place_values", "base": "p16", "phase": "funded", "state": "c_funded_opening",
          "measure": "mean_dv"}
#: (the key changed, its decoy value, the synthetic value written)
DECOYS = (("section", "records_leaf", -1.0), ("base", "p14", -2.0), ("state", "b_evaluation", -3.0),
          ("measure", "dollars_per_trade", -4.0))


def vendored_header(root: Path | str) -> list[str]:
    """The vendored `u_value_map.csv`'s header line, as a list of column names (nothing below it is read)."""
    with open(Path(root) / "vendor" / "stage2" / "results" / VALUE_MAP, newline="", encoding="utf-8") as fh:
        return next(csv.reader(fh))


def rows(value: Any = 1000.0, *, target: bool = True, duplicate: bool = False) -> list[dict[str, Any]]:
    """The synthetic rows: the decoys, the target at `value` (absent with `target=False`, twice with
    `duplicate=True`)."""
    out = []
    for key, other, v in DECOYS:
        out.append({**TARGET, key: other, "value": v, "n": "", "unit": "dollars", "note": f"synthetic decoy ({key})"})
    if target:
        out += [{**TARGET, "value": value, "n": "", "unit": "dollars", "note": "synthetic target"}] * (2 if duplicate
                                                                                                    else 1)
    return out


def write(root: Path | str, results_dir: Path | str, records: list[dict[str, Any]] | None = None,
          columns: list[str] | None = None) -> Path:
    """Write the synthetic value map (default `rows()`) with the vendored header's columns (or `columns`) and its
    manifest into `results_dir` (a temporary folder); returns the CSV's path."""
    import pandas as pd

    from extended.results import write_result

    cols = list(columns) if columns is not None else vendored_header(root)
    df = pd.DataFrame(records if records is not None else rows(), columns=cols)
    csv_path, _ = write_result(df, VALUE_MAP, script="tests/fo_value_map_fixture.py", seed=None,
                               parameters={"synthetic": True, "q": "Q-117f"}, results_dir=Path(results_dir),
                               require_seed=False, description="SYNTHETIC: a value map in the vendored long schema "
                               "for F-03's tests; no randomness (fixed synthetic rows)")
    return Path(csv_path)
