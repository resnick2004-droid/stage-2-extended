"""F-03's T-3 (18.2; the second build read's V1): every judged-block row replaced **below every loader**, so that no path
-- `extended/reader.py`, a vendored loader (`propedge.data.bars.read_bars`, `atlas_a3`'s walk tables), an atlas table,
a cache -- can reach the judged block unseen while run 1 is recomputed.

    with opening_t3.JudgedReplacement(roots=[VENDOR_STAGE2 / "data"]) as jr:
        run1(...)
    jr.entered, jr.rows_replaced, jr.reads

The licensed store cannot be copied (E-002), so the replacement is in memory: while the context is open,
`pandas.read_parquet` and `pyarrow.parquet.read_table` are wrapped; a read of a file under one of `roots` (the bars and
the atlas, by path) is counted (`entered`), and every row of it dated from 2024-01-02 (its `day` or `date` column) has
its prices replaced by the test key's seeded walk and every other float column by seeded draws, and is counted
(`rows_replaced`). **T-3 refuses unless the wrapper was entered** (it is wired), and **holds only with no judged row
replaced** (run 1 reaches none) **and** its sections byte-identical. Seeds: the test block's T-3 key `[SEED_TESTS, 100]`
(section 16).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

JUDGED_FIRST = "2024-01-02"
PRICES = ("open", "high", "low", "close")


def _norm(p: Any) -> str:
    return os.path.normcase(os.path.abspath(str(p)))


class JudgedReplacement:
    """The context manager of the module docstring."""

    def __init__(self, roots: Sequence[Path | str], key: Sequence[int] | None = None):
        from extended import opening_stats as ST

        self.roots = [_norm(r) for r in roots] + [_norm(Path(r).resolve()) for r in roots]
        self.rng = np.random.default_rng(list(key) if key is not None else [ST.SEED_TESTS, 100])
        self.entered = 0
        self.rows_replaced = 0
        self.reads: list[tuple[str, int, int]] = []
        self._saved: list[tuple[Any, str, Any]] = []

    def covers(self, path: Any) -> bool:
        if not isinstance(path, (str, os.PathLike)):
            return False
        a, b = _norm(path), _norm(Path(path).resolve())
        return any(x == r or x.startswith(r + os.sep) for x in (a, b) for r in self.roots)

    def replace(self, df: pd.DataFrame, path: Any) -> pd.DataFrame:
        col = "day" if "day" in df.columns else "date" if "date" in df.columns else None
        self.entered += 1
        if col is None or not len(df):
            self.reads.append((str(path), len(df), 0))
            return df
        m = df[col].astype(str).str[:10].to_numpy() >= JUDGED_FIRST
        k = int(m.sum())
        self.reads.append((str(path), len(df), k))
        if not k:
            return df
        df = df.copy()
        walk = 9000.0 + 0.25 * np.cumsum(np.rint(self.rng.normal(0.0, 40.0, k)))
        for c in df.columns:
            if c in PRICES:
                df.loc[m, c] = walk
            elif c not in ("ts",) and pd.api.types.is_float_dtype(df[c]):
                df.loc[m, c] = self.rng.normal(size=k)
        self.rows_replaced += k
        return df

    def __enter__(self) -> "JudgedReplacement":
        import pyarrow as pa
        import pyarrow.parquet as pq

        orig_pd, orig_pq = pd.read_parquet, pq.read_table

        def read_parquet(path, *a, **k):
            df = orig_pd(path, *a, **k)
            return self.replace(df, path) if self.covers(path) else df

        def read_table(source, *a, **k):
            t = orig_pq(source, *a, **k)
            if not self.covers(source):
                return t
            df = self.replace(t.to_pandas(), source)
            return pa.Table.from_pandas(df, schema=t.schema, preserve_index=False)

        self._saved = [(pd, "read_parquet", orig_pd), (pq, "read_table", orig_pq)]
        pd.read_parquet = read_parquet
        pq.read_table = read_table
        return self

    def __exit__(self, *exc: Any) -> None:
        for mod, name, fn in self._saved:
            setattr(mod, name, fn)
        self._saved = []

    def verdict(self) -> list[str]:
        """T-3's refusals beside the byte comparison: the wrapper entered, no judged row replaced."""
        out = []
        if not self.entered:
            out.append("T-3's replacement was never entered: it is not wired below the loaders")
        if self.rows_replaced:
            first = next(r for r in self.reads if r[2])
            out.append(f"run 1 read {self.rows_replaced} judged-block rows (first {first[0]}: {first[2]} rows)")
        return out


__all__ = ["JUDGED_FIRST", "JudgedReplacement"]
