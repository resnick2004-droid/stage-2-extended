"""Q-121 (E-157 (a1)): the bars-only, side-free volatility descriptive -- `extended/vol_descriptive.py` and
`scripts/vol_descriptive.py`, on hand-built arrays and synthetic bars only (no bar of the store is read here).

In this process (`extended.vol_descriptive` imports no engine):

* `test_refuses_the_judged_block` -- `check_span` refuses 2024-01-02 as an end and as a start (and 2023-12-30, the
  seal's first day), accepts 2023-12-29; `check_days` refuses a frame holding 2024-01-02; `describe` refuses such a
  frame before it builds a single day's arrays;
* `test_band_levels_reached_and_traded_through` -- one hand-built day: a level against the entry is reached at an
  excursion of S ticks, a level the other way only beyond T = floor(R S); the entry bar counts; a move after the bar
  ending 15:08 CT is never read (the walk stays open); the two directions are both walked and neither is labelled;
* `test_entries_follow_stage2s_rule` -- delay 0 and 5 over missing bars, a mark at or after the last bar, an entry bar
  at or after 15:08 CT, a report day's cut;
* `test_trailing_means_read_prior_sessions_only` -- the shift-invariance test for the trailing means: every value from
  session i on replaced (seeded) leaves the trailing mean at i and before unchanged, over every i; ineligible
  sessions never enter; fewer than 20 eligible priors give NaN; the result is not all-NaN and not constant;
* `test_a_wider_market_exits_no_later` -- a seeded day scaled about its first open by 2 (on the tick grid): every
  fixed-band walk exits no later (elementwise), the range doubles exactly, the percent range too;
* `test_quantiles_inverted_cdf` -- on finite samples equal to numpy's `inverted_cdf`; an open walk counts as later than
  every exit, a quantile on it is blank; `NONE` codes are not walks;
* `test_describe_and_summarise` -- `describe` with a stub `day_arrays` on 30 seeded sessions: day kinds, the trailing
  columns from session 21 on, the scaled bands, the walks' shape; `summarise`'s sections and counts; the frame passes
  `output_problems`, which refuses a side column, a share above one, a date in 2024 and a quantile out of order;
* `test_the_module_reads_nothing_and_imports_no_engine` -- the module's source names no reader call and no `propedge`
  import outside the one vendored `day_arrays` door.

In a child process (`tests/q121_synthetic.py`, named `vd_synthetic.py` before Q-121b: RD-04 reserves `vd_`; the
vendored tree on its path), on `extended/synthetic_bars.py` toys:

* `test_child_fv3_identity_and_day_kinds` -- the script's walk identity holds against `fv3_rung_walk` on 100 synthetic
  sessions (a roll and a DST change inside) and refuses a single tampered code; the day kinds equal `atlas_walk._kind`
  on every session (the early close included) and the days identity refuses a tampered table;
* `test_child_shift_invariance_on_bars` -- with `synthetic_bars.replace_from` (seeded) from a session's 17:00 CT on, the
  session table's trailing columns and scaled bands at that session and before are unchanged, at sessions around a
  roll and both DST changes; from 15:08 CT on, that session's walks are unchanged; from 15:10 CT on, its range;
* `test_child_script_end_to_end` -- `main` with the reader stood in by synthetic bars and a days table: the identities
  hold, the file and manifest are written to a temporary folder only and verify, the frame passes `output_problems`,
  no seed; the timing and peak memory printed (for the hand-back's estimate);
* `test_child_script_refuses_2024` -- `main` with `--end 2024-01-02` or `--start 2024-01-02` exits 2 and the reader is
  never called; `results/` outside a clean run exits 2 before any read; a failed identity exits 4, nothing written.

Seeds (named by role, outside the 2026xxxx range): `SEED_PATHS` 4213 (the hand-built days' random walks),
`SEED_VALUES` 4214 (the trailing test's replacements); the child's in `tests/q121_synthetic.py`.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import vol_descriptive as V  # noqa: E402

SEED_PATHS = 4213
SEED_VALUES = 4214
N = V.SESSION_END + 1


def flat_day(price: float = 1000.0, upto: int = V.SESSION_END) -> tuple[np.ndarray, ...]:
    o = np.full(N, np.nan)
    o[1: upto + 1] = price
    return o.copy(), o.copy(), o.copy(), o.copy()


def random_day(rng: np.random.Generator, start: float = 13000.0, sd_ticks: float = 6.0,
               missing: float = 0.02) -> tuple[np.ndarray, ...]:
    """A seeded day on the tick grid: o, h, l, c with a few minutes missing."""
    steps = np.rint(rng.normal(0.0, sd_ticks, (N, 3)))
    path = start / V.TICK + np.cumsum(steps.ravel()).reshape(N, 3)
    o, c = path[:, 0], path[:, 2]
    h, l = path.max(axis=1), path.min(axis=1)
    o, h, l, c = (x * V.TICK for x in (o, h, l, c))
    gone = rng.random(N) < missing
    gone[0] = True
    gone[1] = False
    for x in (o, h, l, c):
        x[gone] = np.nan
    return o, h, l, c


# ------------------------------------------------------------------------------------------------------ refusal


def test_refuses_the_judged_block():
    for s, e in (("2020-01-02", "2024-01-02"), ("2024-01-02", "2024-01-02"), ("2023-12-29", "2023-12-30"),
                 ("2020-01-02", "2026-07-16"), ("2024-01-02", "2024-03-01")):
        with pytest.raises(V.BeyondChoiceBlock):
            V.check_span(s, e)
    assert V.check_span("2020-01-02", "2023-12-29") == (V.FIRST_DAY, V.LAST_DAY)
    with pytest.raises(ValueError):
        V.check_span("2019-12-31", "2020-01-10")
    with pytest.raises(V.BeyondChoiceBlock):
        V.check_days(["2023-12-28", "2023-12-29", "2024-01-02"])
    V.check_days(["2023-12-28", "2023-12-29"])
    calls = []

    def stub(g):
        calls.append(1)
        return flat_day()

    bars = pd.DataFrame({"ts": [1, 2], "day": ["2023-12-29", "2024-01-02"], "open": 1.0, "high": 1.0, "low": 1.0,
                         "close": 1.0})
    with pytest.raises(V.BeyondChoiceBlock):
        V.describe(bars, fomc=[], bls=[], day_arrays=stub)
    assert calls == [], "nothing is computed for a frame reaching the judged block"


# ------------------------------------------------------------------------------------------------------ the walks


def test_band_levels_reached_and_traded_through():
    o, h, l, c = flat_day()
    je = 10                                   # the bar ending 17:10 CT; the entry at its open, 1000
    h[20] = 1000.0 + 50 * V.TICK              # +50 ticks at the bar ending 17:20
    bands = [50, None]
    rr = [0.75, 1.0]
    x = V.first_exits(o, h, l, [je], bands, rr)
    assert x.shape == (1, 2, 2, 2)
    # 'down' (index 0): its level e + S is reached at an excursion of exactly S -> exits at bar 20: 20 - 10 + 1 minutes
    assert x[0, 0, 0, 0] == 11 and x[0, 0, 0, 1] == 11
    # 'up' (index 1): its level e + T must be traded through: T = 37 (R 0.75) is, T = 50 (R 1) is not -> open
    assert x[0, 1, 0, 0] == 11 and x[0, 1, 0, 1] == V.OPEN
    assert (x[0, :, 1, :] == V.NONE).all(), "a band that is None walks nothing"
    # the entry bar counts
    o2, h2, l2, c2 = flat_day()
    l2[je] = 1000.0 - 50 * V.TICK
    y = V.first_exits(o2, h2, l2, [je], [50], [1.0])
    assert y[0, 1, 0, 0] == 1, "the walk 'up' reaches e - S on its entry bar"
    # nothing after the bar ending 15:08 CT is read
    o3, h3, l3, c3 = flat_day()
    h3[V.FLAT_ENTRY + 1:] = 2000.0
    l3[V.FLAT_ENTRY + 1:] = 0.0
    z = V.first_exits(o3, h3, l3, [je], [50], [1.0])
    assert (z == V.OPEN).all()
    h3[V.FLAT_ENTRY] = 2000.0
    z = V.first_exits(o3, h3, l3, [je], [50], [1.0])
    assert z[0, 0, 0, 0] == V.FLAT_ENTRY - je + 1 and z[0, 1, 0, 0] == V.FLAT_ENTRY - je + 1
    with pytest.raises(ValueError):
        V.first_exits(o3, h3, l3, [V.FLAT_ENTRY], [50], [1.0])


def test_entries_follow_stage2s_rule():
    o, h, l, c = flat_day()
    o[11:14] = np.nan                         # the bars ending 17:11-17:13 missing
    assert V.entries(o, [10], 0) == [(10, 14)]
    assert V.entries(o, [10], 5) == [(10, 19)]          # idx[5]: the sixth bar with an open (fast_walk.entry_bar)
    assert V.entries(o, [0], 0) == [(0, 1)]
    assert V.entries(o, [V.FLAT_ENTRY - 1], 0) == [], "an entry bar at 15:08 CT has no walk"
    assert V.entries(o, [V.FLAT_ENTRY - 2], 0) == [(V.FLAT_ENTRY - 2, V.FLAT_ENTRY - 1)]
    assert V.entries(o, [V.SESSION_END], 0) == [], "a mark at or after the last bar"
    assert V.entries(o, [V.BLS_CUT - 5, V.BLS_CUT], 0, cut=V.BLS_CUT) == [(V.BLS_CUT, V.BLS_CUT + 1)]
    early = flat_day(upto=12 * 60 + 15 + 420)[0]                          # an early close: the last bar ends 12:15 CT
    assert V.entries(early, [1000, 1200], 0) == [(1000, 1001)]
    assert V.P16_MARKS[0] == 0 and V.P16_MARKS[-1] == V.SESSION_END - 5 and len(V.P16_MARKS) == 266
    assert len(V.P14_SLOTS) == 22 and V.ct(V.P14_SLOTS[-1]) == "14:00" and V.ct(V.P14_SLOTS[0]) == "17:00"
    assert V.ct(V.BLS_CUT) == "07:30"
    assert V.RR_GRID == tuple(0.25 * k for k in range(1, 13))


def test_trailing_means_read_prior_sessions_only():
    rng = np.random.default_rng(SEED_VALUES)
    n = 80
    v = rng.gamma(4.0, 50.0, n)
    elig = rng.random(n) > 0.1
    base = V.trailing_means(v, elig)
    assert np.isnan(base[: int(np.flatnonzero(np.cumsum(elig) == 20)[0]) + 1]).all()
    assert np.isfinite(base).sum() > 40 and np.nanstd(base) > 0, "not all-NaN, not constant"
    for i in range(n):
        w = v.copy()
        w[i:] = rng.gamma(9.0, 300.0, n - i)                         # arbitrary values from session i on
        e2 = elig.copy()
        e2[i:] = rng.random(n - i) > 0.5
        got = V.trailing_means(w, e2)
        assert np.array_equal(got[: i + 1], base[: i + 1], equal_nan=True), f"session {i} read itself or later"
    # by hand: eligible priors only, the 20 most recent
    i = 60
    prior = [v[j] for j in range(i) if elig[j]][-20:]
    assert base[i] == pytest.approx(np.mean(prior), rel=0, abs=1e-12)
    assert V.band_ticks(101.0, 0.10) == 40 and V.band_ticks(101.25, 0.10) == 41      # 40.4 -> 40, 40.5 -> 41
    assert V.band_ticks(float("nan"), 0.25) is None and V.band_ticks(0.1, 0.10) == 1


def test_a_wider_market_exits_no_later():
    rng = np.random.default_rng(SEED_PATHS)
    o, h, l, c = random_day(rng)
    p0 = float(o[1])
    o2, h2, l2, c2 = (p0 + 2.0 * (x - p0) for x in (o, h, l, c))
    ent = V.entries(o, V.P16_MARKS, 0)
    assert ent == V.entries(o2, V.P16_MARKS, 0)
    bands = list(V.FIXED_BANDS_TICKS)
    a = V.first_exits(o, h, l, [j for _, j in ent], bands)
    b = V.first_exits(o2, h2, l2, [j for _, j in ent], bands)
    assert (b <= a).all(), "doubled excursions reach every fixed level no later"
    assert (b < a).any()
    m1, m2 = V.session_measures(o, h, l), V.session_measures(o2, h2, l2)
    assert m2["range_pts"] == 2 * m1["range_pts"] and m2["range_pct"] == pytest.approx(2 * m1["range_pct"])


def test_quantiles_inverted_cdf():
    rng = np.random.default_rng(SEED_PATHS + 0)
    for n in (1, 2, 3, 9, 10, 11, 57):
        x = rng.integers(1, 1300, n).astype(np.int16)
        got = V.quantiles(x[:, None])
        for q in (0.1, 0.5, 0.9):
            assert got[str(q)][0] == np.quantile(x, q, method="inverted_cdf"), (n, q)
        assert got["n"][0] == n and got["open_share"][0] == 0
        vq = V.value_quantiles(x.astype(float))
        assert vq["median"] == np.quantile(x, 0.5, method="inverted_cdf") and vq["n"] == n
    codes = np.array([[3], [5], [V.OPEN], [V.OPEN], [V.NONE], [7], [V.OPEN], [V.NONE]], dtype=np.int16)
    q = V.quantiles(codes)
    assert q["n"][0] == 6 and q["open_share"][0] == pytest.approx(0.5)
    assert q["0.1"][0] == 3 and q["0.5"][0] == 7 and np.isnan(q["0.9"][0])
    empty = V.quantiles(np.full((4, 1), V.NONE, dtype=np.int16))
    assert empty["n"][0] == 0 and np.isnan(empty["open_share"][0]) and np.isnan(empty["0.5"][0])


# ------------------------------------------------------------------------------------------------------ describe


def _sessions(n: int = 30):
    rng = np.random.default_rng(SEED_PATHS + 1)
    days = pd.bdate_range("2021-01-04", periods=n).strftime("%Y-%m-%d").tolist()
    arrays = {d: random_day(rng, sd_ticks=4.0 + (i % 5)) for i, d in enumerate(days)}
    arrays[days[3]] = flat_day(upto=12 * 60 + 15 + 420)                 # an early close
    bars = pd.DataFrame({"ts": range(n), "day": days, "open": 0.0, "high": 0.0, "low": 0.0, "close": 0.0})
    return days, arrays, bars


def test_describe_and_summarise():
    days, arrays, bars = _sessions()
    fomc, bls = [V.yymmdd(days[5])], [V.yymmdd(days[7]), V.yymmdd(days[25])]
    sessions, walks = V.describe(bars, fomc=fomc, bls=bls, day_arrays=lambda g: arrays[str(g["day"].iloc[0])])
    kinds = sessions.set_index("date")["day_kind"]
    assert kinds[days[3]] == "e" and kinds[days[5]] == "o" and kinds[days[7]] == "b" and kinds[days[0]] == "n"
    walked = sessions["walked"].to_numpy()
    assert walked.sum() == 28 and walks["dates"] == sessions.loc[walked, "date"].tolist()
    first = int(np.flatnonzero(np.cumsum(walked) == 20)[0]) + 1          # the first session with 20 walked priors
    assert sessions["trail20_range_pts"].iloc[:first].isna().all()
    assert sessions["trail20_range_pts"].iloc[first:].notna().all()
    i = first + 3
    prior = sessions.loc[: i - 1][walked[:i]]["range_pts"].tail(20)
    assert sessions["trail20_range_pts"].iloc[i] == pytest.approx(prior.mean())
    assert sessions["band_ticks_025"].iloc[i] == V.band_ticks(prior.mean(), 0.25)
    E = walks["p16_marks"]
    assert E.shape == (28, 266, 2, 5, 12) and walks["p14_slots"].shape == (28, 22, 2, 5, 12)
    pos = walks["dates"].index(days[0])
    assert (E[pos, :, :, 3:] == V.NONE).all(), "no scaled band before 20 prior sessions"
    assert (E[-1, :, :, :3] != V.NONE).any() and (E[-1, :, :, 3:] != V.NONE).any()
    b_pos = walks["dates"].index(days[7])
    cut_rows = [k for k, m in enumerate(V.P16_MARKS) if m < V.BLS_CUT]
    assert (E[b_pos, cut_rows] == V.NONE).all() and (E[b_pos, len(cut_rows)] != V.NONE).any()
    # P-14's slots: entered five bars late, the same walk as a five-minute mark entered at that bar
    o, h, l, c = arrays[days[0]]
    ent14 = V.entries(o, V.P14_SLOTS, 5)
    alone = V.first_exits(o, h, l, [j for _, j in ent14], list(V.FIXED_BANDS_TICKS) + [None, None])
    assert np.array_equal(walks["p14_slots"][pos, : len(ent14)], alone)

    frame = V.summarise(sessions, walks)
    assert V.output_problems(frame) == []
    assert list(frame.columns) == list(V.COLUMNS)
    sec = frame["section"].value_counts()
    assert sec["session"] == 30
    quarters = sorted({f"2021Q{(int(d[5:7]) - 1) // 3 + 1}" for d in walks["dates"]})
    n_per = 1 + 1 + len(quarters)                      # the block, 2021, each quarter
    assert sec["range"] == n_per * 4
    assert sec["band"] == 2 * n_per * 5 * 12
    assert sec["band_mark"] == (n_per - len(quarters)) * (266 + 22) * 5 * 12
    blk = frame[(frame["section"] == "band") & (frame["period_kind"] == "block") & (frame["set"] == "p16_marks")]
    one = blk[(blk["band"] == "25pt") & (blk["rr"] == 1.0)].iloc[0]
    codes = E[:, :, :, 1, 3].ravel()
    codes = codes[codes != V.NONE]
    assert one["n"] == codes.size and one["open_share"] == pytest.approx((codes == V.OPEN).mean())
    rng_row = frame[(frame["section"] == "range") & (frame["period_kind"] == "block") &
                    (frame["measure"] == "range_pts")].iloc[0]
    assert rng_row["n"] == 28 and rng_row["median"] == np.quantile(sessions.loc[walked, "range_pts"], 0.5,
                                                                    method="inverted_cdf")
    # output_problems refuses what this reading must never hold
    bad = frame.copy()
    bad["side"] = 1
    assert any("COLUMNS" in p for p in V.output_problems(bad)) and any("forbidden" in p for p in V.output_problems(bad))
    bad = frame.copy()
    bad.loc[bad.index[-1], "open_share"] = 1.5
    assert any("[0, 1]" in p for p in V.output_problems(bad))
    bad = frame.copy()
    bad.loc[bad.index[0], "date"] = "2024-01-02"
    assert any("choice block" in p for p in V.output_problems(bad))
    bad = frame.copy()
    k = bad.index[(bad["section"] == "band") & bad["p10"].notna() & bad["p90"].notna()][0]
    bad.loc[k, "p10"] = bad.loc[k, "p90"] + 1
    assert any("out of order" in p for p in V.output_problems(bad))
    assert any("missing sections" in p for p in V.output_problems(frame[frame["section"] != "band"]))


def test_the_module_reads_nothing_and_imports_no_engine():
    src = (ROOT / "extended" / "vol_descriptive.py").read_text(encoding="utf-8")
    assert not re.search(r"read_(bars|walks|parquet|csv)\(", src)
    imports = re.findall(r"^\s*(?:from|import)\s+(propedge[\w.]*)", src, re.MULTILINE)
    assert imports == ["propedge.research.atlas_local"], imports
    assert "use_vendored_stage2" not in src


# ------------------------------------------------------------------------------------------------------ the child


def _child(check: str) -> dict:
    env = {**os.environ, "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    env.pop("S2X_CLEAN_RUN", None)
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "q121_synthetic.py"), check], capture_output=True,
                       text=True, timeout=600, env=env)
    assert r.returncode == 0, r.stdout[-4000:] + r.stderr[-4000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_child_fv3_identity_and_day_kinds():
    out = _child("identity")
    assert out["walk_problems"] == [] and out["compared"] > 100_000, out
    assert out["compared_late"] > 1_000, "walks after 13:00 CT (no breakeven possible) are compared"
    assert out["sets_compared"] == ["p14_slots", "p16_marks"]
    assert out["tampered_walk"] and "differs from fv3_rung_walk.walk" in out["tampered_walk"][0]
    assert out["kinds_equal_atlas_walk"] and set(out["kinds_seen"]) >= {"n", "b", "e"}, out["kinds_seen"]
    assert out["kind_problems"] == [] and out["tampered_kinds"], out
    assert out["rr_grid_is_fv3s"] and out["marks_are_resolved_coins"] and out["cut_is_a1s"]


def test_child_shift_invariance_on_bars():
    out = _child("shift")
    assert out["cuts"] >= 8 and out["trail_changed"] == [] and out["walk_changed"] == [] and out["range_changed"] == []
    assert out["trail_finite"] > 0 and out["trail_distinct"] > 5


def test_child_script_end_to_end():
    out = _child("script")
    assert out["rc"] == 0, out["stdout"]
    assert "identity days" in out["stdout"] and "identity walk" in out["stdout"] and "FAILED" not in out["stdout"]
    assert out["written"] and out["verified"] and out["problems"] == [], out
    assert out["manifest_seed"] is None and out["exploratory"] is True
    assert out["sections"] == list(V.SECTIONS)
    assert out["read_spans"] == [["2021-01-04", "2021-06-30"]] and out["walk_reads"] == [["A1", "days"]]
    assert out["results_untouched"]


def test_child_script_refuses_2024():
    out = _child("refuse")
    for case in ("end_2024", "start_2024", "seal_day"):
        assert out[case]["rc"] == 2 and out[case]["reads"] == 0 and "REFUSED" in out[case]["stdout"], (case, out[case])
    assert out["results_outside_clean_run"]["rc"] == 2 and out["results_outside_clean_run"]["reads"] == 0
    assert out["identity_fails"]["rc"] == 4 and not out["identity_fails"]["written"]
