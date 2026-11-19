"""Q-171: S1's range -- the stop width as a multiple k of the trailing range, read on the search years only
(`extended/s1_range.py`, `scripts/s1_range.py`, and the S1 loader in `extended/lever_space.py`), on hand-built arrays and
synthetic bars only. No bar of the store is read here, and no outcome.

In this process (`extended.s1_range` imports no engine):

* `test_translation_on_known_ranges` -- the caps (floor and cap in ticks) translate into k on known trailing ranges by
  hand: the least and greatest k keeping the stop inside the caps on at least the share's count of days (a day at the
  cap's edge is inside), the joint set's contiguity (a gapped case is flagged), no k at all (blank), and a brute-force
  sweep over a fine grid agreeing;
* `test_quantiles_inverted_cdf` -- the k quantiles are the inverted empirical CDF (numpy's `inverted_cdf`), p = 0 the
  least;
* `test_trailing_reads_prior_days_only` -- the shift-invariance test of the trailing mean: every value from day i on
  replaced (seeded) leaves day i's trailing value and every earlier one unchanged, over every i; ineligible days never
  enter; fewer than 20 eligible priors give a blank; equal to Q-121's `trailing_means`; not all blank, not constant;
* `test_window_range_reads_its_own_bars` -- a session's range reads the bars stamped inside its window only (the
  arrays are indexed by bar END minute): a spike stamped just before the window or at its end is not read, one stamped
  at its first or last minute is;
* `test_session_windows_follow_the_anchors` -- the overnight windows are `day_calendar.anchored_starts` per date,
  DST-aware (a US-only and a UK-only daylight week differ), evening from the reopen, london ending at 08:30 CT;
* `test_day_table_shift_invariance` -- on 70 seeded days with a stubbed `day_arrays` and calendar: every bar from day
  i's 17:00 CT reopen on replaced leaves every session's trailing range at day i and before unchanged;
* `test_void_days_are_dropped` -- a day-wide void (a data-defect candidate) leaves every session's population, an
  overnight void (H2) leaves the overnight sessions' only and never enters their trailing means, while `ny`'s
  `trail20_range_pts` keeps Q-121's population; the day counts partition the stored days;
* `test_no_read_past_the_search_years` -- `check_span` and `check_days` refuse 2023-12-30, 2024-01-02 and 2026-07-17
  (the last as the reader's confirmation-window class) and a start before 2020-01-02; `day_table` refuses such a frame
  before it builds a single day's arrays;
* `test_summarise_output_problems_and_the_licence_check` -- the frame's sections and columns; `output_problems` refuses
  a per-day column, k_lo above k_hi, a share above one and broken counts; the written CSV passes the licence guard
  (`extended.price_levels`) with no finding;
* `test_q121_identity` -- `ny`'s trailing range by year equals Q-121's `range` rows rebuilt from it, and a changed
  median, count or missing year is a problem;
* `test_the_loader_refuses_before_the_file_and_loads_after` -- `lever_space.bounds("S1")` raises `NotComputed` while
  the file is absent; with a file and manifest it loads each session's k range (ny_am and ny_pm from ny) and opens only
  those two files; a changed byte, a manifest without a clean run, other caps, another share, a gapped range and a
  wrong span each refuse;
* `test_mutants_are_caught` -- nine source mutations of the core pieces (the trailing window, the window's bar index,
  the floor's and the cap's translation, the share count, the void filter, the span guard, the anchors, the loader's
  sha check), each caught by its check above.

In a child process (`tests/s1_synthetic.py`, the vendored tree on its path, `extended/synthetic_bars.py` toys):

* `test_child_shift_invariance_on_bars` -- with `synthetic_bars.replace_from` (seeded) from a day's 17:00 CT reopen on,
  every session's trailing range at that day and before is unchanged, at days around a roll and both daylight-saving
  changes (US and UK), through the vendored `day_arrays`;
* `test_child_script_end_to_end` -- `main` with the reader stood in by recorders: the identities hold, every read is
  inside the search years under the declared purpose and row, the file and manifest are written to a temporary folder
  only and verify, the frame passes `output_problems` and the licence guard, the loader parses the writer's manifest
  and refuses it for exactly the reasons a toy run must (no clean run, not the whole span);
* `test_child_script_refuses` -- `--end 2024-01-02` or `2026-07-17` exits 2 with no read; `results/` outside a clean run
  exits 2 with no read; a Q-121 file not at its pin exits 2 before any bar is read; a failed Q-121 or A1 identity exits
  4 with nothing written.

Seeds (named by role, outside the 2026xxxx range): `SEED_VALUES` 4711 (the trailing test's values and replacements),
`SEED_DAYS` 4712 (the stubbed days' random walks); the child's in `tests/s1_synthetic.py`.
"""
from __future__ import annotations

import builtins
import copy
import hashlib
import io
import json
import math
import subprocess
import sys
import types
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import day_calendar as DC  # noqa: E402
from extended import lever_space as LS  # noqa: E402
from extended import price_levels as pl  # noqa: E402
from extended import reader as R  # noqa: E402
from extended import s1_range as S  # noqa: E402
from extended import vol_descriptive as V  # noqa: E402

SEED_VALUES = 4711
SEED_DAYS = 4712
MOD_SRC = ROOT / "extended" / "s1_range.py"
N_ARR = V.SESSION_END + 1                      # the walker's arrays: index = a bar's END minute, 0 .. 1330


# ------------------------------------------------------------------------------------------------ helpers


def mutant(old: str, new: str, src: Path = MOD_SRC, name: str = "s1_range_mutant") -> types.ModuleType:
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


def flags_row(d: date, verdict: str = "OK", void: str = "", missing: int = 0, special: str = "") -> dict:
    return {"day": d.isoformat(), "verdict": verdict, "void": void, "missing_after_reopen": str(missing),
            "special": special}


def fake_sources(days: list[date], *, defect: tuple[date, ...] = (), h2_void: tuple[date, ...] = (),
                 last_bar: dict[date, str] | None = None) -> DC.Sources:
    """A void calendar for synthetic days: Q-40 defects and H2 voids as named; every other source empty."""
    cal = {d: {"date": d.isoformat(), "kind": "data_defect_candidate", "close_ct": ""} for d in defect}
    flags = {d: flags_row(d, "VOID" if d in h2_void else "OK", "gap" if d in h2_void else "") for d in days}
    lb = {d: "15:59" for d in days}
    lb.update(last_bar or {})
    return DC.Sources(list(days), cal, frozenset(), frozenset(), lb, frozenset(), frozenset(), flags, None)


def weekdays(start: date, n: int) -> list[date]:
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def toy_arrays(n_days: int, seed: int, vol: np.ndarray | None = None) -> dict[int, tuple[np.ndarray, ...]]:
    """Per day: (o, h, l) arrays indexed by bar END minute, a bar at every minute 1 .. 1330, a seeded walk."""
    rng = np.random.default_rng(seed)
    out = {}
    level = 13000.0
    for i in range(n_days):
        sd = 1.0 + (0.0 if vol is None else float(vol[i]))
        steps = np.rint(rng.normal(0.0, 4.0 * sd, N_ARR)) * V.TICK
        c = level + np.cumsum(steps)
        o = np.r_[level, c[:-1]]
        wid = np.abs(np.rint(rng.normal(0.0, 3.0, (N_ARR, 2)))) * V.TICK
        h = np.maximum(o, c) + wid[:, 0]
        l = np.minimum(o, c) - wid[:, 1]
        o, h, l = (np.where(np.arange(N_ARR) == 0, np.nan, x) for x in (o, h, l))
        out[i] = (o, h, l)
        level = float(c[-1])
    return out


def stub_bars(days: list[date]) -> pd.DataFrame:
    """A frame with one row per day (its `day` and its index): `day_table` groups it; the stub returns the arrays."""
    return pd.DataFrame({"day": [d.isoformat() for d in days], "i": range(len(days))})


def stub_arrays(arrays: dict[int, tuple[np.ndarray, ...]], calls: list | None = None):
    def day_arrays(g: pd.DataFrame):
        i = int(g["i"].iloc[0])
        if calls is not None:
            calls.append(i)
        o, h, l = arrays[i]
        return list(o), list(h), list(l), list(o)
    return day_arrays


def table(days, arrays, src, S_=S, calls=None) -> pd.DataFrame:
    t = S_.day_table(stub_bars(days), fomc=set(), bls=set(), src=src, day_arrays=stub_arrays(arrays, calls))
    return S_.add_trailing(t)


# ------------------------------------------------------------------------------------------------ the translation


def check_translation(S_) -> None:
    T = np.array([10.0, 20.0, 40.0, 80.0])                         # trailing ranges in points
    kmin, kmax = S_.k_bounds(T, floor_ticks=4, cap_ticks=400)       # floor 1 point, cap 100 points
    assert np.allclose(kmin, [0.1, 0.05, 0.025, 0.0125]) and np.allclose(kmax, [10.0, 5.0, 2.5, 1.25])
    for share, lo, hi in ((1.0, 0.1, 1.25), (0.75, 0.05, 2.5), (0.5, 0.025, 5.0), (0.25, 0.0125, 10.0)):
        r = S_.k_range(kmin, kmax, share)
        assert r["n_days"] == 4 and r["contiguous"] is True, (share, r)
        assert math.isclose(r["k_lo"], lo) and math.isclose(r["k_hi"], hi), (share, r)
        assert r["inside_at_lo"] >= share - 1e-12 and r["inside_at_hi"] >= share - 1e-12, (share, r)
    # the share's count is the ceiling: 0.9 of four days is four days
    r = S_.k_range(kmin, kmax, 0.9)
    assert math.isclose(r["k_lo"], 0.1) and math.isclose(r["k_hi"], 1.25), r
    # a gapped set: the cap only twice the floor, two clusters of days
    kmin2, kmax2 = S_.k_bounds(np.array([10.0, 10.0, 100.0, 100.0]), floor_ticks=4, cap_ticks=8)
    g = S_.k_range(kmin2, kmax2, 0.5)
    assert math.isclose(g["k_lo"], 0.01) and math.isclose(g["k_hi"], 0.2) and g["contiguous"] is False, g
    none = S_.k_range(kmin2, kmax2, 1.0)
    assert math.isnan(none["k_lo"]) and math.isnan(none["k_hi"]) and none["contiguous"] is False, none
    # a brute-force sweep on seeded ranges agrees with the exact ends
    rng = np.random.default_rng(SEED_VALUES)
    T3 = rng.uniform(50.0, 400.0, 300)
    a, b = S_.k_bounds(T3, floor_ticks=45, cap_ticks=4000)
    for share in (0.5, 0.95, 1.0):
        r = S_.k_range(a, b, share)
        grid = np.unique(np.r_[np.linspace(0.0, 100.0, 20001), a, b])
        inside = ((a[None, :] <= grid[:, None]) & (grid[:, None] <= b[None, :])).sum(axis=1)
        ok = grid[inside >= math.ceil(share * T3.size - 1e-9)]
        assert math.isclose(ok.min(), r["k_lo"]) and math.isclose(ok.max(), r["k_hi"]), (share, r)


def test_translation_on_known_ranges():
    check_translation(S)


def test_quantiles_inverted_cdf():
    rng = np.random.default_rng(SEED_VALUES)
    x = rng.uniform(0.0, 3.0, 101)
    for p in (0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0):
        assert S.quantile(x, p) == np.quantile(x, p, method="inverted_cdf"), p
    assert S.quantile(x, 0.0) == x.min() and S.quantile(x, 1.0) == x.max()
    assert math.isnan(S.quantile(np.array([]), 0.5))


# ------------------------------------------------------------------------------------------------ time


def check_trailing(S_) -> None:
    rng = np.random.default_rng(SEED_VALUES)
    n = 120
    v = rng.uniform(50.0, 300.0, n)
    v[[5, 40, 77]] = np.nan
    elig = rng.random(n) > 0.2
    base = S_.trailing_ranges(v, elig)
    ref = V.trailing_means(v, elig)
    assert np.array_equal(np.isnan(base), np.isnan(ref)) and np.allclose(base[~np.isnan(base)], ref[~np.isnan(ref)])
    ok = elig & np.isfinite(v)
    first = int(np.flatnonzero(np.cumsum(ok) == S_.TRAIL)[0]) + 1
    assert np.isnan(base[:first]).all() and np.isfinite(base[first:]).all()
    assert np.nanstd(base) > 0
    for i in range(n):
        w = v.copy()
        w[i:] = rng.uniform(1e4, 2e4, n - i)                        # arbitrary values from day i on
        e = elig.copy()
        e[i:] = rng.random(n - i) > 0.5
        got = S_.trailing_ranges(w, e)
        assert np.array_equal(np.isnan(got[: i + 1]), np.isnan(base[: i + 1])), i
        assert np.allclose(got[: i + 1][~np.isnan(base[: i + 1])], base[: i + 1][~np.isnan(base[: i + 1])]), i
    # an ineligible day never enters
    v2 = np.full(30, 100.0)
    v2[3] = 1e6
    e2 = np.ones(30, dtype=bool)
    e2[3] = False
    assert np.nanmax(S_.trailing_ranges(v2, e2)) == 100.0


def test_trailing_reads_prior_days_only():
    check_trailing(S)


def check_window(S_) -> None:
    a, b = 120, 600                                                  # stamps 120 .. 599
    o = np.full(N_ARR, 100.0)
    h = np.full(N_ARR, 101.0)
    l = np.full(N_ARR, 99.0)
    o[0] = h[0] = l[0] = np.nan
    assert S_.window_range(h, l, a, b) == 2.0
    for stamp, inside in ((a - 1, False), (a, True), (b - 1, True), (b, False)):
        hh = h.copy()
        hh[stamp + 1] = 150.0                                       # the bar stamped `stamp` ends at stamp + 1
        assert (S_.window_range(hh, l, a, b) == 51.0) is inside, stamp
    assert math.isnan(S_.window_range(np.full(N_ARR, np.nan), np.full(N_ARR, np.nan), a, b))


def test_window_range_reads_its_own_bars():
    check_window(S)


def check_anchors(S_) -> None:
    for d in (date(2021, 1, 15), date(2021, 3, 15), date(2021, 3, 30), date(2021, 7, 1), date(2021, 11, 2),
              date(2021, 11, 9)):
        w = S_.session_windows(d)
        a = DC.anchored_starts(d)
        assert w["evening"] == (0, a["asia"]) and w["asia"] == (a["asia"], a["london"]), d
        assert w["london"] == (a["london"], a["ny"]) and a["ny"] == 930, d
    # the US changed on 2021-03-14 and the UK on 2021-03-28: London's open moves an hour on the CT clock between them
    assert S_.session_windows(date(2021, 3, 15))["london"][0] != S_.session_windows(date(2021, 3, 30))["london"][0]
    assert S_.session_windows(date(2021, 1, 15))["asia"][0] != S_.session_windows(date(2021, 7, 1))["asia"][0]


def test_session_windows_follow_the_anchors():
    check_anchors(S)


def test_day_table_shift_invariance():
    days = weekdays(date(2021, 2, 1), 70)
    arrays = toy_arrays(len(days), SEED_DAYS, vol=np.sin(np.arange(len(days)) / 5.0) * 0.5)
    src = fake_sources(days)
    base = table(days, arrays, src)
    cols = [f"trail_{s}" for s in S.SESSIONS]
    assert all(base[c].notna().sum() >= 40 for c in cols) and all(base[c].std() > 0 for c in cols)
    rng = np.random.default_rng(SEED_VALUES)
    for i in (0, 19, 20, 21, 35, 69):
        arr = dict(arrays)
        for j in range(i, len(days)):                                # every bar from day i's reopen on
            o, h, l = (x.copy() for x in arrays[j])
            o[1:] = rng.uniform(5000.0, 9000.0, N_ARR - 1)
            h[1:] = o[1:] + rng.uniform(0.0, 900.0, N_ARR - 1)
            l[1:] = o[1:] - rng.uniform(0.0, 900.0, N_ARR - 1)
            arr[j] = (o, h, l)
        got = table(days, arr, src)
        for c in cols:
            pd.testing.assert_series_equal(got[c].iloc[: i + 1], base[c].iloc[: i + 1], check_names=False)


# ------------------------------------------------------------------------------------------------ voids


def check_voids(S_) -> None:
    days = weekdays(date(2021, 2, 1), 60)
    arrays = toy_arrays(len(days), SEED_DAYS)
    defect, h2 = days[30], days[40]
    src = fake_sources(days, defect=(defect,), h2_void=(h2,))
    t = table(days, arrays, src, S_)
    for s in S_.SESSIONS:
        pop = S_.population(t, s)
        assert not pop[t["date"] == defect.isoformat()].any(), s
        h2_in = bool(pop[t["date"] == h2.isoformat()].any())
        assert h2_in is (s == "ny"), (s, h2_in)
    # the overnight void never enters an overnight trailing mean; ny's trail20 keeps Q-121's population
    spike = dict(arrays)
    o, h, l = (x.copy() for x in arrays[40])
    h[1:] = h[1:] + 5000.0
    spike[40] = (o, h, l)
    t2 = table(days, spike, src, S_)
    for s in ("evening", "asia", "london"):
        assert np.allclose(t2[f"trail_{s}"].to_numpy()[41:], t[f"trail_{s}"].to_numpy()[41:], equal_nan=True), s
    assert not np.allclose(t2["trail_ny"].to_numpy()[41:61], t["trail_ny"].to_numpy()[41:61], equal_nan=True)
    counts = S_.day_counts(t)
    for s in S_.SESSIONS:
        c = counts[s]
        assert c["stored"] == len(days)
        assert c["kind_out"] + c["void"] + c["no_trail"] + c["population"] == c["stored"], (s, c)
        assert c["void"] == (1 if s == "ny" else 2), (s, c)


def test_void_days_are_dropped():
    check_voids(S)


# ------------------------------------------------------------------------------------------------ the search years only


def check_span(S_) -> None:
    assert S_.check_span("2020-01-02", "2023-12-29") == (date(2020, 1, 2), date(2023, 12, 29))
    for end in ("2023-12-30", "2024-01-02", "2025-06-30"):
        with pytest.raises(S_.BeyondSearchYears):
            S_.check_span("2020-01-02", end)
        with pytest.raises(S_.BeyondSearchYears):
            S_.check_span(end, end)
    for bad in ("2026-07-17", "2027-01-04"):
        with pytest.raises(R.ConfirmationWindowRefused):
            S_.check_span("2020-01-02", bad)
    with pytest.raises(ValueError):
        S_.check_span("2019-12-31", "2023-12-29")
    for late in ("2024-01-02", "2026-07-17"):
        with pytest.raises(S_.BeyondSearchYears):
            S_.check_days(["2023-12-28", late])


def test_no_read_past_the_search_years():
    check_span(S)
    days = weekdays(date(2023, 12, 1), 25)
    calls: list = []
    with pytest.raises(S.BeyondSearchYears):
        S.day_table(stub_bars(days), fomc=set(), bls=set(), src=None, day_arrays=stub_arrays({}, calls))
    assert calls == []
    with pytest.raises(R.ConfirmationWindowRefused):
        S.day_table(stub_bars([date(2026, 7, 17)]), fomc=set(), bls=set(), src=None, day_arrays=stub_arrays({}, calls))
    assert calls == []


# ------------------------------------------------------------------------------------------------ the frame


CAPS = {"floor_ticks": 45, "cap_ticks": 4000}


def _frame():
    days = weekdays(date(2021, 2, 1), 80)
    arrays = toy_arrays(len(days), SEED_DAYS, vol=np.cos(np.arange(len(days)) / 7.0) * 0.6)
    src = fake_sources(days, defect=(days[50],), h2_void=(days[60],))
    t = table(days, arrays, src)
    return t, S.summarise(t, CAPS)


def test_summarise_output_problems_and_the_licence_check(tmp_path):
    t, f = _frame()
    assert list(f.columns) == list(S.COLUMNS)
    assert set(f["section"]) == set(S.SECTIONS)
    assert S.output_problems(f) == []
    rk = f[f["section"] == "range_k"]
    assert len(rk) == len(S.SESSIONS) * len(S.SHARES)
    assert S.SHARE in set(rk["share"].astype(float))
    kq = f[f["section"] == "k_quantile"]
    assert len(kq) == len(S.SESSIONS) * len(S.PROBS)
    for s in S.SESSIONS:
        q = kq[kq["session"] == s].sort_values("prob")
        assert q["k_floor"].is_monotonic_increasing
        r = rk[(rk["session"] == s) & (rk["share"] == S.SHARE)].iloc[0]
        pop = S.population(t, s)
        T = t.loc[pop, f"trail_{s}"].to_numpy()
        want = S.k_range(*S.k_bounds(T, **CAPS), S.SHARE)
        assert r["k_lo"] == want["k_lo"] and r["k_hi"] == want["k_hi"] and want["n_days"] == pop.sum()
        n = f[(f["section"] == "days") & (f["session"] == s) & (f["count_kind"] == "population")]["count"]
        assert n.tolist() == [pop.sum()]
    bad = f.copy()
    bad["date"] = "2021-02-01"
    assert S.output_problems(bad)
    for col, val in (("share", 1.5), ("k_lo", 99.0)):
        b2 = f.copy()
        b2.loc[b2.index[b2["section"] == "range_k"][0], col] = val
        assert S.output_problems(b2), col
    b3 = f.copy()
    b3.loc[b3.index[(b3["section"] == "days") & (b3["count_kind"] == "population")][0], "count"] = 10**6
    assert S.output_problems(b3)
    p = tmp_path / "s1_range.csv"
    f.to_csv(p, index=False)
    assert pl.scan_path(p, name="results/s1_range.csv") == []
    g = S.summarise(t, {"floor_ticks": 40, "cap_ticks": 4000})        # 100 C / F on the tick grid
    g.to_csv(p, index=False)
    assert pl.scan_path(p, name="results/s1_range.csv") == []


def test_q121_identity():
    t, _ = _frame()
    rows = S.q121_like_rows(t)
    assert rows and S.q121_problems(t, rows) == []
    bad = copy.deepcopy(rows)
    bad[0]["median"] = str(float(bad[0]["median"]) + 0.25)
    assert S.q121_problems(t, bad)
    bad = copy.deepcopy(rows)
    bad[0]["n"] = str(int(bad[0]["n"]) + 1)
    assert S.q121_problems(t, bad)
    assert S.q121_problems(t, [])


# ------------------------------------------------------------------------------------------------ the loader


def _manifest(csv_path: Path, frame: pd.DataFrame, **over) -> Path:
    raw = csv_path.read_bytes()
    m = {"columns": list(frame.columns), "git_commit": "0" * 40, "git_dirty": False, "result_file": csv_path.name,
         "rows": len(frame), "script": S.SCRIPT, "seed": None, "sha256": hashlib.sha256(raw).hexdigest(),
         "provenance": {"clean_run": {"name": "q171-s1-range", "checkout": "x", "marker": "S2X_CLEAN_RUN"}},
         "parameters": S.manifest_parameters(LS.stop_caps(), identities={"q121": "HELD", "a1_days": "HELD"},
                                             span=(S.SEARCH_START, S.SEARCH_END))}
    for k, v in over.items():
        if k == "parameters":
            m["parameters"].update(v)
        else:
            m[k] = v
    mp = Path(str(csv_path) + ".manifest.json")
    mp.write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")
    return mp


def _written(tmp_path: Path, frame: pd.DataFrame | None = None, **over) -> Path:
    if frame is None:
        t, _ = _frame()
        frame = S.summarise(t, {k: LS.stop_caps()[k] for k in ("floor_ticks", "cap_ticks")})
    p = tmp_path / "s1_range.csv"
    frame.to_csv(p, index=False)
    _manifest(p, frame, **over)
    return p


def check_loader(S_, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(LS, "S1_PATH", tmp_path / "absent" / "s1_range.csv")
    with pytest.raises(LS.NotComputed):
        LS.bounds("S1")
    assert LS.refusals()["S1"] == "NotComputed"
    p = _written(tmp_path)
    caps = LS.stop_caps()
    got = S_.load_range(p, caps=caps)
    assert set(got["by_session"]) == set(S_.SESSIONS)
    p.write_bytes(p.read_bytes().replace(b"range_k", b"range_K", 1))
    with pytest.raises(S_.RangeRefused):
        S_.load_range(p, caps=caps)


def test_the_loader_refuses_before_the_file_and_loads_after(tmp_path, monkeypatch):
    check_loader(S, tmp_path, monkeypatch)
    p = _written(tmp_path)
    monkeypatch.setattr(LS, "S1_PATH", p)
    opened: list[str] = []
    real_open, real_io_open = builtins.open, io.open
    monkeypatch.setattr(builtins, "open", lambda f, *a, **k: (opened.append(str(f)), real_open(f, *a, **k))[1])
    monkeypatch.setattr(io, "open", lambda f, *a, **k: (opened.append(str(f)), real_io_open(f, *a, **k))[1])
    r = LS.bounds("S1")
    monkeypatch.setattr(builtins, "open", real_open)
    monkeypatch.setattr(io, "open", real_io_open)
    data = [x for x in opened if any(t in x.replace("\\", "/") for t in ("/results/", ".csv", "/data/", ".parquet"))
            and "s1_range" not in x]
    assert not data, data
    frame = pd.read_csv(p, float_precision="round_trip")
    rk = frame[(frame["section"] == "range_k") & (frame["share"] == S.SHARE)].set_index("session")
    by = r.detail["by_session"]
    assert set(by) == set(LS.declared("sessions"))
    for ls, s in S.LEVER_SESSIONS.items():
        assert by[ls] == (rk.loc[s, "k_lo"], rk.loc[s, "k_hi"]), ls
    assert r.lo == min(v[0] for v in by.values()) and r.hi == max(v[1] for v in by.values())
    assert r.detail["share"] == S.SHARE and r.detail["sha256"] == hashlib.sha256(p.read_bytes()).hexdigest()
    assert LS.stop_width("ny_pm").lo == rk.loc["ny", "k_lo"] and LS.stop_width("asia").hi == rk.loc["asia", "k_hi"]
    assert "S1" in LS.space() and "S1" not in LS.refusals()
    # each defect of the file refuses, loudly (not as "not computed")
    t, _ = _frame()
    caps = LS.stop_caps()
    frame0 = S.summarise(t, {k: caps[k] for k in ("floor_ticks", "cap_ticks")})
    cases = {
        "byte": None,
        "no clean run": {"provenance": {}},
        "dirty": {"git_dirty": True},
        "other script": {"script": "scripts/other.py"},
        "other caps": {"parameters": {"caps": {"floor_ticks": caps["floor_ticks"] + 1, "cap_ticks": caps["cap_ticks"]}}},
        "other share": {"parameters": {"share_declared": 0.9}},
        "a toy span": {"parameters": {"span": ["2021-01-04", "2021-05-28"]}},
        "an identity not held": {"parameters": {"identities": {"q121": "FAILED", "a1_days": "HELD"}}},
    }
    for why, over in cases.items():
        d = tmp_path / why.replace(" ", "_")
        d.mkdir()
        q = _written(d, frame0, **(over or {}))
        if over is None:
            q.write_bytes(q.read_bytes().replace(b"range_k", b"range_K", 1))
        monkeypatch.setattr(LS, "S1_PATH", q)
        with pytest.raises(LS.LeverRefused) as e:
            LS.bounds("S1")
        assert not isinstance(e.value, LS.NotComputed), why
    gapped = frame0.copy()
    gapped.loc[(gapped["section"] == "range_k") & (gapped["session"] == "asia"), "contiguous"] = False
    d = tmp_path / "gapped"
    d.mkdir()
    monkeypatch.setattr(LS, "S1_PATH", _written(d, gapped))
    with pytest.raises(LS.LeverRefused):
        LS.bounds("S1")


# ------------------------------------------------------------------------------------------------ mutants


_TRAIL_BLOCK = ("        if len(window) >= trail:\n            out[i] = float(np.mean(window[-trail:]))\n"
                "        if ok[i]:\n            window.append(float(v[i]))\n")
_TRAIL_MUTANT = ("        if ok[i]:\n            window.append(float(v[i]))\n"
                 "        if len(window) >= trail:\n            out[i] = float(np.mean(window[-trail:]))\n")
#: what a check raises on a mutant: an assertion, `pytest.raises`' "did not raise" (a BaseException), or a crash
CAUGHT = (AssertionError, Exception, pytest.fail.Exception)

MUTANTS = {
    "trailing includes the day itself": (_TRAIL_BLOCK, _TRAIL_MUTANT, check_trailing),
    "the window reads by stamp, not by end minute": (
        "hh, ll = h[a + 1: b + 1], l[a + 1: b + 1]", "hh, ll = h[a: b], l[a: b]", check_window),
    "the floor's translation off by a tick": (
        "kmin = floor_ticks * TICK / T", "kmin = (floor_ticks - 1) * TICK / T", check_translation),
    "the cap's translation scaled": (
        "kmax = cap_ticks * TICK / T", "kmax = cap_ticks * TICK / T * 1.01", check_translation),
    "the cap's edge exclusive": (
        'np.searchsorted(smax, v, "left")', 'np.searchsorted(smax, v, "right")', check_translation),
    "the share's count rounded down": (
        "math.ceil(float(share) * n - 1e-9)", "math.floor(float(share) * n + 1e-9)", check_translation),
    "the void filter dropped from the population": (
        'return walked & ~t[f"void_{session}"].to_numpy(bool) & np.isfinite(', "return walked & np.isfinite(",
        check_voids),
    "the void filter dropped from the overnight trailing": (
        '    return walked & ~t[f"void_{session}"].to_numpy(bool)\n', "    return walked\n", check_voids),
    "the span guard at the judged block's end": (
        "if max(s, e) > SEARCH_END:", "if max(s, e) > R.JUDGED_END:", check_span),
    "fixed CT session starts": (
        "a = DC.anchored_starts(d)", "a = {'asia': 60, 'london': 540, 'ny': 930}", check_anchors),
}


@pytest.mark.parametrize("name", list(MUTANTS))
def test_mutants_are_caught(name):
    old, new, check = MUTANTS[name]
    check(S)                                                        # the real module passes
    m = mutant(old, new)
    with pytest.raises(CAUGHT) as e:
        check(m)
    assert not isinstance(e.value, SyntaxError)


def test_mutant_loader_without_its_sha_check_is_caught(tmp_path, monkeypatch):
    (tmp_path / "real").mkdir()
    (tmp_path / "mutant").mkdir()
    check_loader(S, tmp_path / "real", monkeypatch)                 # the real loader passes
    m = mutant('if m.get("sha256") != sha:', "if False:")
    with pytest.raises(CAUGHT):
        check_loader(m, tmp_path / "mutant", monkeypatch)


def test_the_module_reads_nothing_and_imports_no_engine():
    src = MOD_SRC.read_text(encoding="utf-8")
    assert "propedge" not in src
    for call in ("read_bars(", "read_walks(", "read_parquet(", "authorise_engine_read("):
        assert call not in src, call


# ------------------------------------------------------------------------------------------------ the child


def _child(check: str) -> dict:
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "s1_synthetic.py"), check], capture_output=True,
                       text=True, timeout=900, cwd=str(ROOT))
    assert r.returncode == 0, (r.stdout[-3000:], r.stderr[-3000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_child_shift_invariance_on_bars():
    got = _child("shift")
    assert got["ok"], got
    assert got["checked_days"] >= 4 and got["sessions"] == list(S.SESSIONS)


def test_child_script_end_to_end():
    got = _child("script")
    assert got["ok"], got
    assert got["exit"] == 0 and got["verified"] and got["output_problems"] == [] and got["licence"] == []
    assert got["reads"] >= 2 and got["reads_inside"] and got["purposes"] == [S.PURPOSE]
    assert set(got["loader_refusals"]) == {"clean run", "span"}, got["loader_refusals"]


def test_child_script_refuses():
    got = _child("refuse")
    assert got["ok"], got
