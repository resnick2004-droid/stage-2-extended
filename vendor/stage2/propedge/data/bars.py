"""The local bar store (R3, D-458): the operator's Databento 1-minute bars, git-ignored, read through the window guard.

D-39 and D-120 kept raw bars in QuantConnect's cloud; D-458 reopens that for the operator's own licensed Databento
files with these safeguards: the bars live under `data/bars/<ROOT>/` (git-ignored: the vendor's licence is private
use, no redistribution, so they never reach a remote or a result file); `tests/test_no_raw_bars_in_results.py` still
refuses any bar series in `results/`; only trade logs and summary rows are written there; every read goes through
`propedge.data.windows.assert_readable`, so a read past a market's declared window raises; a day in a reserved window
is never stored at all. The registered record of a run names which source it read (QuantConnect's AlgoSeek bars or
these).

The store holds one parquet file of the charted contract's bars per root -- each trading day the outright with the
most volume on the previous trading day, the rule the kits trade by (D-98); a day's bars are never stitched to another
contract's -- and a manifest of what was imported. Trading days are Chicago time: a session opens at 17:00 the
evening before (the bar's Chicago time plus seven hours, its date).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from propedge import REPO_ROOT
from propedge.data.windows import WINDOWS_PATH, assert_readable

STORE = REPO_ROOT / "data" / "bars"
LICENCE = "Databento historical data under the operator's licence: private use, no redistribution"
COLUMNS = ["ts", "day", "contract", "open", "high", "low", "close", "volume"]


class BarStoreError(ValueError):
    """The store has no bars for the root, or a file in it does not match its manifest."""


def root_dir(root: str, store: Path | None = None) -> Path:
    return Path(store or STORE) / root


def manifest(root: str, store: Path | None = None) -> dict[str, Any] | None:
    p = root_dir(root, store) / "manifest.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def trading_days(root: str, store: Path | None = None) -> list[str]:
    """Every trading day in the store for `root` (no bar is read)."""
    m = manifest(root, store)
    return list(m["day_list"]) if m else []


def read_bars(root: str, start: Any, end: Any, purpose: str, *, prereg: str | None = None,
              store: Path | None = None, windows: Path | str = WINDOWS_PATH, what: str = "bar read") -> pd.DataFrame:
    """The charted contract's 1-minute bars for trading days `start` to `end` (inclusive), after the window guard.

    Raises `ConfirmationWindowLeak` before anything is read when the span reaches a window `purpose` may not read
    (`propedge.data.windows`), and `BarStoreError` when the root has no store.
    """
    assert_readable(root, start, end, purpose, prereg=prereg, path=windows, what=what)
    p = root_dir(root, store) / "bars.parquet"
    if not p.is_file():
        raise BarStoreError(f"no bar store for {root} at {p}: import the operator's Databento file with "
                            "scripts/import_bars.py")
    s, e = str(pd.Timestamp(start).date()), str(pd.Timestamp(end).date())
    df = pd.read_parquet(p, filters=[("day", ">=", s), ("day", "<=", e)])
    return df.sort_values("ts", kind="stable").reset_index(drop=True)
