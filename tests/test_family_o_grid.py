"""F-03 (family O): the states' inputs read with less memory and fitted never in the judge -- `opening_states.grid_by_year`
(the build read's memory note: the choice block's bars read one calendar year at a time; not wired into `Ctx.grid`
unless a measurement needs it, E-122) is bit for bit the
one-shot read's grid; `compute(frozen=..., frozen_folds=...)` gives the choice block's u3 out of fold from the pinned fold
fits without fitting anything (13's choice-block beside; T-9). Synthetic bars only (`extended/synthetic_bars.py`, seeds
`[SEED_TESTS, 1200, ...]`, section 16's test block); the reader-and-store version and the memory measurement are
`tests/fo_grid_memory.py` (slow).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from extended import features as F
from extended import opening_states as OS
from extended import opening_stats as ST
from extended import synthetic_bars as sb

ROOT = Path(__file__).resolve().parent.parent


def _bars() -> pd.DataFrame:
    parts = []
    for k, (a, b) in enumerate(((date(2020, 12, 21), date(2021, 1, 8)), (date(2021, 12, 20), date(2022, 1, 7)))):
        parts.append(sb.generate(sb.Spec(a, b, seed=[ST.SEED_TESTS, 1200, k], vol_scale=10.0)))
    return pd.concat(parts, ignore_index=True).sort_values("ts", kind="stable").reset_index(drop=True)


BARS = _bars()
DAYS = sorted(BARS["day"].astype(str).unique())
WALKED = {d for i, d in enumerate(DAYS) if i % 4 != 1}


def _read(calls):
    def read(s, e):
        calls.append((s, e))
        b = BARS[(BARS["day"].astype(str) >= s) & (BARS["day"].astype(str) <= e)]
        return b.reset_index(drop=True)
    return read


def _same(a: F.Grid, b: F.Grid) -> bool:
    return (a.days == b.days and a.contract.dtype == b.contract.dtype and np.array_equal(a.contract, b.contract)
            and all(x.dtype == y.dtype and x.shape == y.shape and np.array_equal(x, y, equal_nan=True)
                    for x, y in ((a.O, b.O), (a.H, b.H), (a.L, b.L), (a.C, b.C), (a.V, b.V))))


def test_the_grid_read_by_year_is_the_one_shot_grid_bit_for_bit():
    one = F.grid(BARS[BARS["day"].astype(str).isin(WALKED)].reset_index(drop=True))
    calls: list = []
    got = OS.grid_by_year(_read(calls), "2020-01-02", "2023-12-29", WALKED)
    assert _same(one, got)
    assert calls == [("2020-01-02", "2020-12-31"), ("2021-01-01", "2021-12-31"), ("2022-01-01", "2022-12-31"),
                     ("2023-01-01", "2023-12-29")]                   # one calendar year at a time, the span's ends kept
    assert len({d.year for d in got.days}) == 3


def test_a_year_with_no_walked_session_is_skipped_and_none_at_all_refuses():
    calls: list = []
    w = {d for d in WALKED if not d.startswith("2022")}
    got = OS.grid_by_year(_read(calls), "2020-01-02", "2023-12-29", w)
    assert _same(got, F.grid(BARS[BARS["day"].astype(str).isin(w)].reset_index(drop=True)))
    with pytest.raises(ValueError):
        OS.grid_by_year(_read([]), "2020-01-02", "2023-12-29", set())


def test_concatenated_grids_refuse_days_out_of_order():
    a = F.grid(BARS[BARS["day"].astype(str) < "2021-06-01"].reset_index(drop=True))
    b = F.grid(BARS[BARS["day"].astype(str) >= "2021-06-01"].reset_index(drop=True))
    assert _same(OS.concat_grids([a, b]), F.grid(BARS))
    with pytest.raises(ValueError):
        OS.concat_grids([b, a])


SPEC = sb.Spec(date(2020, 6, 1), date(2021, 3, 31), seed=[ST.SEED_TESTS, 1200, 9], rolls=((date(2021, 3, 12), "NQM1"),),
               first_contract="NQH1", holidays=frozenset(), early_closes=frozenset(), vol_scale=10.0)


def test_the_choice_blocks_u3_out_of_fold_from_the_pinned_folds_fits_nothing(monkeypatch):
    g = F.grid(sb.generate(SPEC))
    st = OS.compute(g)
    assert st.forecast.folds, "the synthetic frame holds a test year"
    folds = {Y: OS.coefficients_from_json(OS.canonical_json(cf)) for Y, cf in st.forecast.folds.items()}
    final = OS.coefficients_from_json(OS.canonical_json(st.forecast.final))

    def no_fit(*a, **k):
        raise AssertionError("the judge fitted")

    monkeypatch.setattr(OS, "fit", no_fit)
    got = OS.compute(g, frozen=final, frozen_folds=folds, test_years=())
    for c in OS.BUILT:
        assert np.array_equal(got.share(c), st.share(c), equal_nan=True), c
    assert got.forecast.coefficients_sha256 == st.forecast.coefficients_sha256
    assert {Y: OS.coefficients_sha256(v) for Y, v in got.forecast.folds.items()} == \
        {Y: OS.coefficients_sha256(v) for Y, v in st.forecast.folds.items()}
    with pytest.raises(ValueError):
        OS.compute(g, frozen_folds=folds, test_years=())                # pinned folds only with the pinned final fit
    with pytest.raises(ValueError):
        OS.compute(g, frozen=final, frozen_folds=folds)                  # and never with folds to fit


@pytest.mark.slow
def test_the_reader_grid_by_year_on_a_store_is_the_one_shot_grid(tmp_path):
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    script = str(ROOT / "tests" / "fo_grid_memory.py")
    r = subprocess.run([sys.executable, script, str(ROOT), "make", str(tmp_path), "2020-11-02", "2022-02-25"],
                       capture_output=True, text=True, timeout=900, env=env, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    got = {}
    for mode in ("oneshot", "byyear"):
        r = subprocess.run([sys.executable, script, str(ROOT), "measure", str(tmp_path), mode, "2020-11-02",
                            "2022-02-25"], capture_output=True, text=True, timeout=900, env=env, cwd=str(ROOT))
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
        got[mode] = json.loads(r.stdout.strip().splitlines()[-1])
    assert got["oneshot"]["grid_sha256"] == got["byyear"]["grid_sha256"]
    assert got["oneshot"]["sessions"] == got["byyear"]["sessions"] > 250
