"""T7: the admission forecast (`extended/t7_forecast.py`, `scripts/t7_fit.py`, and the T7 loader in
`extended/lever_space.py`), on hand-built arrays and synthetic bars only. No bar of the store is read here, and no
outcome.

In this process (`extended.t7_forecast` imports no engine):

* `test_psi_series_equals_images` -- the series and the method of images agree to 1e-9 on every S2 w and u from 0.05
  to 5; Psi is 1 at u = 0, falls with u, rises with w;
* `test_window_stats_by_hand` -- on one hand-built day: the entry is the first bar stamped at or after the mark, IV is
  (C - O) of the entry bar plus the later close changes to the bar stamped 15:07, the excursions read the same bars,
  nothing stamped after 15:07 is read, and rv_60 reads the bars stamped a - 60 .. a - 1 only;
* `test_prior_means_read_earlier_rows_only` -- the trailing means skip missing values and never read their own row;
* `test_feature_shift_invariance` -- every bar stamped at or after a cut replaced (`synthetic_bars.replace_from`,
  seeded): every feature (x1, x2, x3, has_forecast, band, reach) of every earlier day and of every mark whose alert is
  at or after the cut is unchanged, and the opening bands' frozen x3 too for any cut at or after 08:25 -- at cuts
  across the day (the reopen, its third minute, asia, london, 08:25, 08:30, 10:05, 15:00) on days at a roll and both
  daylight-saving changes; the features are not all missing and not constant;
* `test_x3_is_twice_the_library_rv_tod` -- on the day band, x3 is 2 x `extended.features`' rv_tod at m - 5, missing
  where it is missing;
* `test_open_counts_by_hand` -- the stop on a touch, the target only through by a tick, the short mirrored;
* `test_planted_har_recovered` / `test_planted_calibration_recovered` -- coefficients planted in a synthetic table
  are recovered by `fit_har` and `fit_logistic`; a rank-deficient band is refused;
* `test_brownian_brackets_give_the_textbook_calibration` -- Brownian paths with a perfect variance forecast: the
  labels through `open_counts` and `psi` calibrate to alpha near 0 and beta near 1;
* `test_purge_and_embargo` -- each fold's training rows exclude the fold, the 22 sessions before it, the 22 after it,
  and any later row whose features read a day of the fold;
* `test_no_row_after_the_search_years` -- `check_span` refuses 2023-12-30, 2024-01-02 and 2026-07-17 (the last as the
  reader's confirmation-window class); `day_grid`, `feature_table`, `fit_har` and `run_fit` refuse a 2024 day before
  computing anything; a feature table holds no row after 2023-12-29;
* `test_run_fit_frame_and_licence` -- `run_fit` on synthetic bars of two search years: the sections, the final model
  complete, `output_problems` empty, a mutated frame refused, and the written CSV passing the licence guard with no
  finding; no date or clock column;
* `test_admission_line_is_d212` -- q is Stage 2's `selection.feasibility.flat_share_max` read independently; a config
  without the key, or whose note does not cite D-212, is refused;
* `test_the_loader_refuses_then_loads` -- `lever_space.bounds("T7")` is `NotComputed` while the file is absent; with
  the file and its manifest it loads `off` / `admit`, q and the final model, opening no other data file; each defect
  (a byte, no clean run, a dirty tree, another script, another q, a toy span, an identity not held, a non-positive
  beta) refuses loudly, never as `NotComputed`;
* `test_mutants_are_caught` -- source mutations of each core piece, each caught by its check.

In a child process (`tests/t7_synthetic.py`, synthetic bars, the reader stood in by recorders):

* `test_child_script_end_to_end` -- `main` writes the file and manifest to a temporary folder only, both identities
  hold, every read is inside the search years under the declared purpose and row, the frame passes `output_problems`
  and the licence guard, and the loader refuses it for exactly the toy's reasons (no clean run, not the whole span);
* `test_child_script_refuses` -- `--end 2024-01-02` or `2026-07-17` and `results/` outside a clean run exit 2 with no
  read; a failed a1_days identity exits 4 with nothing written.

Seeds (named by role, outside the 2026xxxx range): `SEED_BARS` 4731 (the synthetic bars), `SEED_SHIFT` 4732 (the
replacements; the k-th cut takes the k-th child), `SEED_PLANT` 4733 (the planted tables), `SEED_BM` 4734 (the
Brownian paths); the child's in `tests/t7_synthetic.py`.
"""
from __future__ import annotations

import builtins
import hashlib
import io
import json
import subprocess
import sys
import types
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import features as FL  # noqa: E402
from extended import lever_space as LS  # noqa: E402
from extended import price_levels as pl  # noqa: E402
from extended import reader as R  # noqa: E402
from extended import synthetic_bars as SB  # noqa: E402
from extended import t7_forecast as T  # noqa: E402

SEED_BARS = 4731
SEED_SHIFT = 4732
SEED_PLANT = 4733
SEED_BM = 4734
MOD_SRC = ROOT / "extended" / "t7_forecast.py"
FEATURES = ("x1", "x2", "x3", "has_forecast", "band", "reach")
CAUGHT = (AssertionError, Exception, pytest.fail.Exception)


def child_seed(root: int, k: int) -> int:
    return int(np.random.SeedSequence(root, spawn_key=(k,)).generate_state(1)[0])


def toy(start: str, end: str) -> pd.DataFrame:
    return SB.generate(SB.Spec(start=date.fromisoformat(start), end=date.fromisoformat(end), seed=SEED_BARS))


_BARS: dict[str, pd.DataFrame] = {}


def bars_2021() -> pd.DataFrame:
    if "b" not in _BARS:
        _BARS["b"] = toy("2021-01-04", "2021-04-09")
    return _BARS["b"]


def table(mod, bars: pd.DataFrame) -> pd.DataFrame:
    days, O, H, L, C = mod.day_grid(bars)
    return mod.feature_table(days, mod.window_stats(O, H, L, C))


def mutant(old: str, new: str, src: Path = MOD_SRC, name: str = "t7_forecast_mutant") -> types.ModuleType:
    """The module with `old` (found exactly once) replaced by `new`, loaded as a fresh module."""
    text = src.read_text(encoding="utf-8")
    assert text.count(old) == 1, f"the mutation's anchor occurs {text.count(old)} times: {old!r}"
    m = types.ModuleType(name)
    m.__file__ = str(src)
    sys.modules[name] = m
    try:
        exec(compile(text.replace(old, new), str(src), "exec"), m.__dict__)
    finally:
        sys.modules.pop(name, None)
    return m


# ------------------------------------------------------------------------------------------------ checks (module-generic)


def check_psi(mod) -> None:
    u = np.array([0.05, 0.1, 0.2, 0.5, 0.8, 1.0, 1.5, 2.0, 5.0])
    for w in mod.W_GRID:
        a = mod.psi_series(w, u, terms=400)
        b = mod.psi_images(w, u)
        assert np.max(np.abs(a - b)) < 1e-9, w
        p = mod.psi(w, u)
        assert np.max(np.abs(p - b)) < 1e-9 and np.all(np.diff(p) < 0)
    assert mod.psi(1.0, 0.0) == 1.0
    assert np.all(mod.psi(np.array(mod.W_GRID), 1.0)[1:] > mod.psi(np.array(mod.W_GRID), 1.0)[:-1])


def _one_day() -> tuple[np.ndarray, ...]:
    n = T.N_SLOTS
    O, H, L, C = (np.full((1, n), np.nan) for _ in range(4))
    for s in range(0, 1380):
        if s in (1030, 1031, 1032, 1033):           # no bar at 10:10-10:13
            continue
        base = 100.0 + 0.25 * ((s * 7) % 13)
        O[0, s], C[0, s] = base, base + 0.25 * ((s % 5) - 2)
        H[0, s], L[0, s] = max(O[0, s], C[0, s]) + 0.5, min(O[0, s], C[0, s]) - 0.5
    H[0, 1328], L[0, 1328] = 1e4, -1e4               # stamped 15:08: after the walk's last bar, never read
    return O, H, L, C


def check_window(mod) -> None:
    O, H, L, C = _one_day()
    st = mod.window_stats(O, H, L, C)
    k = list(mod.MARKS).index(1030)                  # mark 10:10: the entry bar is stamped 10:14 (1034)
    e, last = 1034, mod.WALK_LAST_STAMP
    pres = [s for s in range(e, last + 1) if np.isfinite(C[0, s])]
    iv = (C[0, e] - O[0, e]) ** 2 + sum((C[0, b] - C[0, a]) ** 2 for a, b in zip(pres, pres[1:]))
    assert abs(st["iv"][0, k] - iv) < 1e-9
    assert st["up"][0, k] == np.nanmax(H[0, e:last + 1]) - O[0, e]
    assert st["dn"][0, k] == O[0, e] - np.nanmin(L[0, e:last + 1])
    a = 1030 - mod.ALERT_LAG
    win = [s for s in range(a - 60, a) if np.isfinite(C[0, s]) and np.isfinite(C[0, s - 1])]
    rv = np.sqrt(np.mean([(C[0, s] - C[0, s - 1]) ** 2 for s in win]))
    assert abs(st["rv_live"][0, k] - rv) < 1e-12


def check_prior_means(mod) -> None:
    X = np.array([[1.0], [np.nan], [3.0], [5.0], [7.0]])
    m, first = mod.prior_means(X, 2)
    assert np.isnan(m[:3, 0]).all() and m[3, 0] == 2.0 and m[4, 0] == 4.0
    assert list(first[:, 0]) == [-1, -1, -1, 0, 2]


def check_shift(mod, cuts: list[tuple[str, int]] | None = None) -> int:
    bars = bars_2021()
    base = table(mod, bars)
    feats = [c for c in FEATURES]
    if cuts is None:
        cuts = [(d, s) for d in ("2021-03-12", "2021-03-15", "2021-03-29")
                for s in (0, 3, 120, 600, 925, 930, 1025, 1320)]
    checked = 0
    for i, (d, s) in enumerate(cuts):
        hh, mm = divmod((s + 17 * 60) % (24 * 60), 60)
        cut_ts = SB.ts_of(d, hh, mm)
        alt = table(mod, SB.replace_from(bars, cut_ts, child_seed(SEED_SHIFT, i)))
        keep = (base["date"] < d) | ((base["date"] == d) & (base["mark"] <= s + mod.ALERT_LAG))
        if s >= mod.FROZEN_ALERT:
            keep |= (base["date"] == d) & base["band"].isin(mod.FROZEN_BANDS)
        a, b = base.loc[keep, feats].reset_index(drop=True), alt.loc[keep, feats].reset_index(drop=True)
        pd.testing.assert_frame_equal(a, b, check_exact=True, obj=f"cut {d} slot {s}")
        checked += int(keep.sum())
    on = base[base["has_forecast"]]
    for c in ("x1", "x2", "x3"):
        assert on[c].notna().any() and on[c].nunique() > 10, c
    return checked


def check_open_counts(mod) -> None:
    up = np.array([0.0, 1.0, 2.0, 2.24, 2.26, 0.5])
    dn = np.array([0.0, 0.5, 0.5, 0.5, 0.5, 1.0])
    tk = np.full(6, 0.25)
    # c = 1, w = 2: a long is stopped at dn >= 1, through its target at up >= 2.25; a short stopped at up >= 1
    long_open = np.array([1, 1, 1, 1, 0, 0])
    short_open = np.array([1, 0, 0, 0, 0, 1])
    assert list(mod.open_counts(up, dn, tk, 1.0, 2.0)) == list(long_open + short_open)
    assert list(mod.open_counts(dn, up, tk, 1.0, 2.0)) == list(short_open + long_open)
    k = mod.open_counts(np.array([0.2]), np.array([2.25]), np.array([0.25]), 1.0, 2.0)
    assert k[0] == 0                                  # the long stopped, the short's target traded through
    k2 = mod.open_counts(np.array([0.2]), np.array([2.24]), np.array([0.25]), 1.0, 2.0)
    assert k2[0] == 1                                 # the short's target touched but not traded through: open


def _planted_table(mod, rng, n_per_band: int = 4000, coefs: dict | None = None) -> tuple[pd.DataFrame, dict]:
    coefs = coefs or {b: {"const": -0.2 + 0.05 * i, "x1": 0.3, "x2": 0.25, "x3": 0.4}
                      for i, b in enumerate(mod.BANDS)}
    rows = []
    for i, b in enumerate(mod.BANDS):
        x = rng.normal(0, 1, (n_per_band, 3))
        y = coefs[b]["const"] + 0.3 * x[:, 0] + 0.25 * x[:, 1] + (0.4 * x[:, 2] if b != "evening" else 0)
        y = y + rng.normal(0, 0.3, n_per_band)
        rows.append(pd.DataFrame({"date": "2021-06-01", "day_index": 0, "mark": 0, "band": b,
                                  "has_forecast": True, "y": y, "x1": x[:, 0], "x2": x[:, 1],
                                  "x3": x[:, 2] if b != "evening" else np.nan, "reach": 0,
                                  "up_n": 1.0, "dn_n": 1.0, "tick_n": 0.0}))
    return pd.concat(rows, ignore_index=True), coefs


def check_planted_har(mod) -> None:
    rng = np.random.default_rng(SEED_PLANT)
    t, coefs = _planted_table(mod, rng)
    har = mod.fit_har(t, np.ones(len(t), dtype=bool))
    for b in mod.BANDS:
        assert abs(har[b]["const"] - coefs[b]["const"]) < 0.02, b
        assert abs(har[b]["x1"] - 0.3) < 0.02 and abs(har[b]["x2"] - 0.25) < 0.02
        if b != "evening":
            assert abs(har[b]["x3"] - 0.4) < 0.02
        else:
            assert "x3" not in har[b]
    yh = mod.predict_y(har, t)
    assert np.corrcoef(yh, t["y"])[0, 1] > 0.8


def check_planted_calibration(mod) -> None:
    rng = np.random.default_rng(child_seed(SEED_PLANT, 1))
    z = rng.normal(-1.0, 2.0, 100_000)
    p = mod.sigmoid(-0.4 + 0.7 * z)
    k = rng.binomial(2, p)
    a, b = mod.fit_logistic(z, k)
    assert abs(a + 0.4) < 0.03 and abs(b - 0.7) < 0.03


def check_brownian(mod) -> tuple[float, float]:
    rng = np.random.default_rng(SEED_BM)
    n, steps = 3000, 1500
    var = np.exp(rng.normal(0, 0.5, n))               # each row's integrated variance (M = 1)
    inc = rng.normal(0, 1, (n, steps)) * np.sqrt(var / steps)[:, None]
    path = np.cumsum(inc, axis=1)
    up = np.maximum(path.max(axis=1), 0.0)
    dn = np.maximum(-path.min(axis=1), 0.0)
    t = pd.DataFrame({"date": "2021-06-01", "day_index": 0, "mark": 1030, "band": "day", "has_forecast": True,
                      "y": np.log(var), "x1": 0.0, "x2": 0.0, "x3": 0.0, "reach": 0, "up_n": up, "dn_n": dn,
                      "tick_n": 0.0})
    obs = mod.bracket_obs(t, np.log(var), np.ones(n, dtype=bool))
    a, b = mod.fit_logistic(obs["z"], obs["k"])
    assert abs(a) < 0.12 and abs(b - 1.0) < 0.08, (a, b)
    return a, b


def _split_table(mod) -> pd.DataFrame:
    days = [d for d in (date(2020, 1, 2) + timedelta(days=i) for i in range(4 * 366))
            if d.weekday() < 5 and d <= mod.SEARCH_END]
    t = pd.DataFrame({"date": [d.isoformat() for d in days], "day_index": np.arange(len(days))})
    t["reach"] = t["day_index"] - 5                     # short reaches: the embargo binds on its own
    return t


def check_splits(mod) -> None:
    t = _split_table(mod)
    di = t["day_index"].to_numpy()
    yr = pd.to_datetime(t["date"]).dt.year.to_numpy()
    lo, hi = di[yr == 2021].min(), di[yr == 2021].max()
    t.loc[t["day_index"] == hi + 30, "reach"] = hi       # a later row whose features read the fold's last day
    train, test = mod.fold_masks(t, 2021)
    assert test.sum() == (yr == 2021).sum() and not (train & test).any()
    tr = set(di[train])
    assert not tr & set(range(lo - 22, hi + 23)), "a training row within 22 sessions of the fold"
    assert lo - 23 in tr and hi + 23 in tr
    assert hi + 30 not in tr and hi + 31 in tr
    assert set(di[~train & ~test]) == set(range(lo - 22, lo)) | set(range(hi + 1, hi + 23)) | {hi + 30}


def check_span(mod) -> None:
    for bad in ("2023-12-30", "2024-01-02"):
        with pytest.raises(mod.BeyondSearchYears):
            mod.check_span("2023-01-03", bad)
    with pytest.raises(R.ConfirmationWindowRefused):
        mod.check_span("2023-01-03", "2026-07-17")
    with pytest.raises(ValueError):
        mod.check_span("2019-12-31", "2020-02-03")
    with pytest.raises(mod.BeyondSearchYears):
        mod.check_days(["2023-12-29", "2024-01-02"])


def _manifest(csv_path: Path, frame: pd.DataFrame, q: float, **over) -> Path:
    raw = csv_path.read_bytes()
    _, qs = T.admission_line()
    m = {"columns": list(frame.columns), "git_commit": "0" * 40, "git_dirty": False, "result_file": csv_path.name,
         "rows": len(frame), "script": T.SCRIPT, "seed": None, "sha256": hashlib.sha256(raw).hexdigest(),
         "provenance": {"clean_run": {"name": "t7-forecast", "checkout": "x", "marker": "S2X_CLEAN_RUN"}},
         "parameters": T.manifest_parameters(q, qs, identities={"rv_tod": "HELD", "a1_days": "HELD"},
                                             span=(T.SEARCH_START, T.SEARCH_END))}
    for k, v in over.items():
        if k == "parameters":
            m["parameters"].update(v)
        else:
            m[k] = v
    mp = Path(str(csv_path) + ".manifest.json")
    mp.write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")
    return mp


def _final_frame(mod, beta: float = 0.9) -> pd.DataFrame:
    rows = []
    for i, b in enumerate(mod.BANDS):
        for term, v in zip(("const",) + mod.TERMS[b], (-0.1 - 0.01 * i, 0.2, 0.3, 0.5)):
            rows.append(mod._r("coef", term, v, band=b, fold=mod.FINAL))
        rows += [mod._r("calib", "alpha", 0.1, band=b, fold=mod.FINAL),
                 mod._r("calib", "beta", beta if b == "day" else 0.9, band=b, fold=mod.FINAL),
                 mod._r("count", "rows_final", 1000, band=b, fold=mod.FINAL)]
    return pd.DataFrame(rows, columns=list(mod.COLUMNS))


def _written(folder: Path, frame: pd.DataFrame | None = None, **over) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    frame = _final_frame(T) if frame is None else frame
    p = folder / "t7_forecast.csv"
    frame.to_csv(p, index=False)
    _manifest(p, frame, T.admission_line()[0], **over)
    return p


def check_loader(mod, tmp_path: Path) -> None:
    q = T.admission_line()[0]
    with pytest.raises(mod.NotRead):
        mod.load_forecast(tmp_path / "absent" / "t7_forecast.csv", q=q)
    p = _written(tmp_path / "ok")
    got = mod.load_forecast(p, q=q)
    assert set(got["har"]) == set(mod.BANDS)
    raw = p.read_bytes()
    assert raw.count(b",0.2") >= 1
    p.write_bytes(raw.replace(b",0.2", b",0.7", 1))          # still complete and parseable: only the sha differs
    with pytest.raises(mod.ForecastRefused):
        mod.load_forecast(p, q=q)
    bad = _written(tmp_path / "beta", _final_frame(T, beta=-0.1))
    with pytest.raises(mod.ForecastRefused):
        mod.load_forecast(bad, q=q)


# ------------------------------------------------------------------------------------------------ the tests


def test_psi_series_equals_images():
    check_psi(T)


def test_window_stats_by_hand():
    check_window(T)


def test_prior_means_read_earlier_rows_only():
    check_prior_means(T)


def test_feature_shift_invariance():
    assert check_shift(T) > 1000


def test_x3_is_twice_the_library_rv_tod():
    bars = bars_2021()
    t = table(T, bars)
    marks = [int(m) for m in T.MARKS if m >= T.DAY1_LAST + T.MARK_STEP]
    lib = FL.compute(bars, marks=[m - T.ALERT_LAG for m in marks])
    lib = pd.DataFrame({"date": lib["day"].astype(str), "mark": lib["slot"] + T.ALERT_LAG, "rv": lib["rv_tod"]})
    got = t[t["mark"].isin(marks)].merge(lib, on=["date", "mark"], how="outer", indicator=True)
    assert (got["_merge"] == "both").all()
    a, b = got["x3"].to_numpy(float), 2.0 * got["rv"].to_numpy(float)
    assert (np.isnan(a) == np.isnan(b)).all() and np.isfinite(a).sum() > 1000
    assert np.allclose(a[np.isfinite(a)], b[np.isfinite(b)], rtol=1e-12, atol=0.0)


def test_open_counts_by_hand():
    check_open_counts(T)


def test_planted_har_recovered():
    check_planted_har(T)
    rng = np.random.default_rng(child_seed(SEED_PLANT, 2))
    t, _ = _planted_table(T, rng, n_per_band=200)
    t.loc[t["band"] == "day", "x2"] = t.loc[t["band"] == "day", "x1"]
    with pytest.raises(T.FitRefused):
        T.fit_har(t, np.ones(len(t), dtype=bool))


def test_planted_calibration_recovered():
    check_planted_calibration(T)


def test_brownian_brackets_give_the_textbook_calibration():
    check_brownian(T)


def test_purge_and_embargo():
    check_splits(T)


def test_no_row_after_the_search_years():
    check_span(T)
    late = toy("2023-12-18", "2024-01-05")
    with pytest.raises(T.BeyondSearchYears):
        T.day_grid(late)
    ok = late[late["day"] <= "2023-12-29"]
    days, O, H, L, C = T.day_grid(ok)
    st = T.window_stats(O, H, L, C)
    with pytest.raises(T.BeyondSearchYears):
        T.feature_table(days + [date(2024, 1, 2)], {k: np.concatenate([v, v[-1:]]) for k, v in st.items()})
    t = T.feature_table(days, st)
    assert t["date"].max() <= "2023-12-29"
    t2 = t.copy()
    t2.loc[t2.index[-1], "date"] = "2024-01-02"
    with pytest.raises(T.BeyondSearchYears):
        T.fit_har(t2, np.ones(len(t2), dtype=bool))
    with pytest.raises(T.BeyondSearchYears):
        T.run_fit(t2, 0.05)


def _two_years() -> pd.DataFrame:
    return pd.concat([toy("2021-01-04", "2021-04-30"), toy("2022-01-03", "2022-04-29")], ignore_index=True)


def test_run_fit_frame_and_licence(tmp_path):
    bars = _two_years()
    t = table(T, bars)
    frame, final = T.run_fit(t, 0.05)
    assert list(frame.columns) == list(T.COLUMNS) and set(frame["section"]) == set(T.SECTIONS)
    assert set(frame["fold"]) == {"y2021", "y2022", T.OOF, T.FINAL}
    assert T.output_problems(frame) == []
    assert set(final["har"]) == set(T.BANDS) and all(final["calibration"][b][1] > 0 for b in T.BANDS)
    bad = frame.copy()
    bad.loc[(bad["fold"] == T.FINAL) & (bad["section"] == "calib") & (bad["band"] == "asia")
            & (bad["stat"] == "beta"), "section"] = "coef"
    assert T.output_problems(bad)
    bad2 = frame.copy()
    bad2.loc[bad2["stat"] == "mean_p", "value"] = 1.5
    assert T.output_problems(bad2)
    p = tmp_path / "t7_forecast.csv"
    frame.to_csv(p, index=False)
    assert pl.scan_path(p, name="results/t7_forecast.csv") == []
    for c in frame.columns:
        assert not pl.is_level_name(c) and c not in ("date", "mark", "alert", "ts")


def test_admission_line_is_d212(tmp_path):
    doc = yaml.safe_load((ROOT / "vendor" / "stage2" / T.Q_CONFIG).read_text(encoding="utf-8"))
    want = doc["selection"]["feasibility"]["flat_share_max"]
    q, src = T.admission_line()
    assert q == float(want) and 0 < q < 1 and src["key"] == "selection.feasibility.flat_share_max"
    gone = tmp_path / "gone.yaml"
    gone.write_text("selection: {feasibility: {}}\n", encoding="utf-8")
    with pytest.raises(T.ForecastRefused):
        T.admission_line(gone)
    other = tmp_path / "other.yaml"
    other.write_text("selection: {feasibility: {flat_share_max: 0.05, flat_share_note: 'some rule'}}\n",
                     encoding="utf-8")
    with pytest.raises(T.ForecastRefused):
        T.admission_line(other)


def test_the_loader_refuses_then_loads(tmp_path, monkeypatch):
    check_loader(T, tmp_path / "direct")
    monkeypatch.setattr(LS, "T7_PATH", tmp_path / "absent" / "t7_forecast.csv")
    with pytest.raises(LS.NotComputed):
        LS.bounds("T7")
    assert LS.refusals()["T7"] == "NotComputed"
    p = _written(tmp_path / "good")
    monkeypatch.setattr(LS, "T7_PATH", p)
    opened: list[str] = []
    real_open, real_io_open = builtins.open, io.open
    monkeypatch.setattr(builtins, "open", lambda f, *a, **k: (opened.append(str(f)), real_open(f, *a, **k))[1])
    monkeypatch.setattr(io, "open", lambda f, *a, **k: (opened.append(str(f)), real_io_open(f, *a, **k))[1])
    r = LS.bounds("T7")
    monkeypatch.setattr(builtins, "open", real_open)
    monkeypatch.setattr(io, "open", real_io_open)
    data = [x for x in opened if any(s in x.replace("\\", "/") for s in ("/results/", ".csv", "/data/", ".parquet"))
            and "t7_forecast" not in x]
    assert not data, data
    q = T.admission_line()[0]
    assert r.kind == "choices" and r.values == ("off", "admit") and r.detail["q"] == q
    assert r.detail["sha256"] == hashlib.sha256(p.read_bytes()).hexdigest()
    frame = pd.read_csv(p)
    want = frame[(frame["section"] == "coef") & (frame["band"] == "day") & (frame["stat"] == "x3")]["value"].iloc[0]
    assert r.detail["model"]["har"]["day"]["x3"] == want
    assert "T7" in LS.space() and "T7" not in LS.refusals()
    pr = T.probability_open(r.detail["model"], "day", {"x1": 0.0, "x2": 0.0, "x3": 0.0}, 1.0, 1.0, 2.0)
    assert 0 < pr < 1 and T.admit(pr, 1.0) and not T.admit(float("nan"), q)
    cases = {
        "byte": None,
        "no clean run": {"provenance": {}},
        "dirty": {"git_dirty": True},
        "other script": {"script": "scripts/other.py"},
        "other q": {"parameters": {"q": q / 2}},
        "a toy span": {"parameters": {"span": ["2021-01-04", "2022-04-29"]}},
        "an identity not held": {"parameters": {"identities": {"rv_tod": "FAILED", "a1_days": "HELD"}}},
        "other purpose": {"parameters": {"purpose": "t7_other"}},
    }
    for why, over in cases.items():
        q_ = _written(tmp_path / why.replace(" ", "_"), **(over or {}))
        if over is None:
            q_.write_bytes(q_.read_bytes().replace(b",0.2", b",0.7", 1))
        monkeypatch.setattr(LS, "T7_PATH", q_)
        with pytest.raises(LS.LeverRefused) as e:
            LS.bounds("T7")
        assert not isinstance(e.value, LS.NotComputed), why
    monkeypatch.setattr(LS, "T7_PATH", _written(tmp_path / "negative_beta", _final_frame(T, beta=-0.2)))
    with pytest.raises(LS.LeverRefused):
        LS.bounds("T7")


_SHIFT_FAST = [("2021-03-15", 600), ("2021-03-15", 1025)]
_FREEZE = [("2021-03-15", 930)]

MUTANTS = {
    "the trailing mean reads its own row": (
        "c = np.cumsum(ok) - ok", "c = np.cumsum(ok)", check_prior_means),
    "rv_60 reads the alert's own bar": (
        "        a = int(a)\n        if a < 1:", "        a = int(a) + 1\n        if a < 1:",
        lambda m: check_shift(m, _SHIFT_FAST)),
    "x3 not frozen in the opening bands": (
        "x3 = np.where(frozen, x3_frozen[:, None], x3_live)", "x3 = x3_live", lambda m: check_shift(m, _FREEZE)),
    "the entry bar's own change dropped from IV": (
        "iv = (Cw[rows, ec] - entry) ** 2 + suf[rows, ec + 1]", "iv = suf[rows, ec + 1]", check_window),
    "the window read past 15:07": (
        "Hs = np.fmax.accumulate(Hw[:, ::-1], axis=1)[:, ::-1]",
        "Hs = np.fmax.accumulate(H[:, ::-1], axis=1)[:, ::-1][:, :E + 1]", check_window),
    "the embargo dropped": (
        "after = (di > hi + embargo) & (reach > hi)", "after = (di > hi) & (reach > hi)", check_splits),
    "the reach check dropped": (
        "after = (di > hi + embargo) & (reach > hi)", "after = di > hi + embargo", check_splits),
    "the purge dropped": ("before = di < lo - purge", "before = di < lo", check_splits),
    "the target fills on a touch": (
        "long_open = (dn_n < c) & (up_n < w * c + tick_n)", "long_open = (dn_n < c) & (up_n < w * c)",
        check_open_counts),
    "the short not mirrored": (
        "short_open = (up_n < c) & (dn_n < w * c + tick_n)", "short_open = (dn_n < c) & (up_n < w * c + tick_n)",
        check_open_counts),
    "the HAR without its intercept": (
        "cols = [np.ones(int(sel.sum()))] + [", "cols = [", check_planted_har),
    "the calibration's gradient ignores the trials": (
        "g = X.T @ (k - trials * p)", "g = X.T @ (k - p)", check_planted_calibration),
    "the images' sign": (
        "- ndtr((b + 2.0 + sh) / s) + ndtr((1.0 + sh) / s)", "+ ndtr((b + 2.0 + sh) / s) - ndtr((1.0 + sh) / s)",
        check_psi),
    "u not in stop units squared": (
        'parts["z"].append(logit(psi(w, eh / (c * c))))', 'parts["z"].append(logit(psi(w, eh / c)))',
        check_brownian),
    "the span guard": ("    if max(s, e) > SEARCH_END:\n", "    if False:\n", check_span),
}


@pytest.mark.parametrize("name", sorted(MUTANTS))
def test_mutants_are_caught(name):
    old, new, check = MUTANTS[name]
    check(T)                                                        # the real module passes
    m = mutant(old, new)
    with pytest.raises(CAUGHT) as e:
        check(m)
    assert not isinstance(e.value, SyntaxError)


@pytest.mark.parametrize("old,new", [('if m.get("sha256") != sha:', "if False:"),
                                     ('if not cc["beta"] > 0:', "if False:")])
def test_mutant_loader_checks_are_caught(tmp_path, old, new):
    check_loader(T, tmp_path / "real")
    m = mutant(old, new)
    with pytest.raises(CAUGHT):
        check_loader(m, tmp_path / "mutant")


def test_the_module_reads_nothing_and_imports_no_engine():
    src = MOD_SRC.read_text(encoding="utf-8")
    assert "propedge" not in src
    for call in ("read_bars(", "read_walks(", "read_parquet(", "authorise_engine_read("):
        assert call not in src, call


# ------------------------------------------------------------------------------------------------ the child


def _child(check: str) -> dict:
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "t7_synthetic.py"), check], capture_output=True,
                       text=True, timeout=900, cwd=str(ROOT))
    assert r.returncode == 0, (r.stdout[-3000:], r.stderr[-3000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_child_script_end_to_end():
    got = _child("script")
    assert got["ok"], got
    assert got["exit"] == 0 and got["verified"] and got["output_problems"] == [] and got["licence"] == []
    assert got["reads"] >= 2 and got["reads_inside"] and got["purposes"] == [T.PURPOSE]
    assert got["rows"] == [T.READ_ROW] and got["identities_held"]
    assert set(got["loader_refusals"]) == {"clean run", "span"}, got["loader_refusals"]


def test_child_script_refuses():
    got = _child("refuse")
    assert got["ok"], got
