"""F-03 (family O, `prereg/F-03_opening_timing.md`) T-2 and T-7: the states read only bars closed by the alert, and
u3's forecast is ordinary least squares (sections 6, A3; build item 18.1 item 1). Synthetic bars only
(`extended/synthetic_bars.py`); the replacement walks are seeded `[SEED_SHIFT, j]` (section 16).

T-2 (A3): every bar stamped at or after the alert m - 5 is replaced by a seeded random walk, and separately deleted;
every state's share and flag and every y_hat at (d, m) -- and at every earlier (session, mark) -- is unchanged, at 200
(session, mark) cuts including the first marks after 17:00, the 17:30 mark, the `asia` band's first marks 18:00 and
18:05, a roll day and a DST change; replacing the alert day's 08:30-08:59 bars changes no state of that day; x3 is
2 x the library's `rv_tod` at every RTH alert where the library computes it; no window wraps at an overnight slot; no
state is all-undefined or constant. The replacement is applied to the day grid (`features.grid`'s arrays: every slot
at or after the cut on the cut's day, and every later day), which is what replacing the bars stamped at or after the
cut does to them (the stamps, and so the slots, are unchanged).
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pytest

from extended import features as F
from extended import opening_states as OS
from extended import synthetic_bars as sb

SEED_SHIFT = 20261981
SPEC = sb.Spec(date(2020, 6, 1), date(2021, 3, 31), seed=20261988, rolls=((date(2021, 3, 12), "NQM1"),),
               first_contract="NQH1", holidays=frozenset(), early_closes=frozenset())


@pytest.fixture(scope="module")
def base():
    bars = sb.generate(SPEC)
    g = F.grid(bars)
    return bars, g, OS.compute(g)


def _copy(g: F.Grid) -> F.Grid:
    return F.Grid(list(g.days), g.contract.copy(), g.O.copy(), g.H.copy(), g.L.copy(), g.C.copy(), g.V.copy())


def replaced(g: F.Grid, d: int, cut: int, j: int) -> F.Grid:
    """Every bar at or after slot `cut` of day d, and every bar of a later day, replaced by a seeded walk."""
    h = _copy(g)
    rng = np.random.default_rng([SEED_SHIFT, j])
    mask = np.zeros(g.O.shape, dtype=bool)
    mask[d, max(cut, 0):] = True
    mask[d + 1:, :] = True
    mask &= ~np.isnan(g.O)
    k = int(mask.sum())
    walk = 9000.0 + 0.25 * np.cumsum(np.rint(rng.normal(0.0, 40.0, k)))
    o = walk + 0.25 * np.rint(rng.normal(0.0, 10.0, k))
    wid = 0.25 * np.rint(np.abs(rng.normal(0.0, 30.0, (k, 2))))
    h.O[mask], h.C[mask] = o, walk
    h.H[mask] = np.maximum(o, walk) + wid[:, 0]
    h.L[mask] = np.minimum(o, walk) - wid[:, 1]
    h.V[mask] = rng.integers(1, 50_000, k)
    return h


def deleted(g: F.Grid, d: int, cut: int) -> F.Grid:
    """Every bar at or after the cut deleted: day d's from the cut, and every later day (which then has no bar, so is
    not in the frame -- as `features.grid` builds a frame from the bars that remain)."""
    h = F.Grid(list(g.days[:d + 1]), g.contract[:d + 1].copy(), *(X[:d + 1].copy() for X in (g.O, g.H, g.L, g.C, g.V)))
    for X in (h.O, h.H, h.L, h.C, h.V):
        X[d, max(cut, 0):] = np.nan
    return h


def _same(a: np.ndarray, b: np.ndarray) -> bool:
    return bool(np.array_equal(a, b, equal_nan=True))


def visible_mask(st: OS.States, d: int, m_cut: int) -> np.ndarray:
    """Every (session, mark) whose alert is at or before the cut's: every earlier session, and day d's marks <= m."""
    vis = np.zeros((len(st.days), len(st.marks)), dtype=bool)
    vis[:d] = True
    vis[d, [k for k, m in enumerate(st.marks) if m <= m_cut]] = True
    return vis


def _cuts(st: OS.States) -> list[tuple[int, int]]:
    days = [x.isoformat() for x in st.days]
    roll = days.index("2021-03-12")
    dst = days.index("2021-03-15")                      # the first session after the March change (opens 2021-03-14)
    dst_nov = days.index("2020-11-02")
    defined = [i for i in range(len(days)) if np.isfinite(st.share("s1")[i]).any()]
    rng = np.random.default_rng([SEED_SHIFT, 10 ** 6])
    pool = [i for i in defined if i not in (roll, dst)]
    picked = sorted(set(rng.choice(pool, size=min(60, len(pool)), replace=False).tolist())
                    | {roll, dst, dst_nov, defined[0]})
    marks = [0, 5, 30, 60, 65, 535, 540, 880, 925]
    cuts = [(d, m) for d in picked[:30] for m in marks[:5]]          # the first marks, 17:30, 18:00 and 18:05
    rest = [d for d in picked if d not in picked[:30]]
    for i, d in enumerate(rest):
        for m in (marks[5 + (i % 4)], int(rng.choice(OS.POPULATION_MARKS))):
            cuts.append((d, m))
    for d in (roll, dst, dst_nov):
        cuts += [(d, 30), (d, 60), (d, 925)]
    return sorted(set(cuts))


def test_t2_states_and_yhat_read_no_bar_at_or_after_the_alert(base):
    _, g, st = base
    cuts = _cuts(st)
    assert len(cuts) >= 200
    marks = list(st.marks)
    for j, (d, m) in enumerate(cuts):
        alert = m - 5
        vis = visible_mask(st, d, m)
        for variant in (replaced(g, d, alert, j), deleted(g, d, alert)):
            got = OS.compute(variant)
            v = vis[: len(got.days)]
            for c in OS.BUILT:
                assert _same(got.share(c)[v], st.share(c)[: len(got.days)][v]), (c, st.days[d], F.slot_label(m))
                assert np.array_equal(got.in_state(c)[v], st.in_state(c)[: len(got.days)][v]), (c, st.days[d], m)
            assert _same(got.y_hat[v], st.y_hat[: len(got.days)][v]), ("y_hat", st.days[d], m)
        assert m in marks


def test_t2_the_alert_days_opening_window_changes_no_state(base):
    _, g, st = base
    days = [x for x in range(len(st.days)) if np.isfinite(st.share("s1")[x]).any()][:30]
    for d in days:
        h = _copy(g)
        rng = np.random.default_rng([SEED_SHIFT, 2 * 10 ** 6 + d])
        sl = slice(F.slot(8, 30), F.slot(9, 0))
        for X in (h.O, h.H, h.L, h.C):
            X[d, sl] = X[d, sl] + 0.25 * np.rint(rng.normal(0, 400, X[d, sl].shape))
        h.H[d, sl] = np.fmax.reduce([h.O[d, sl], h.C[d, sl], h.H[d, sl]])
        h.L[d, sl] = np.fmin.reduce([h.O[d, sl], h.C[d, sl], h.L[d, sl]])
        got = OS.compute(h)
        for c in OS.BUILT:
            assert _same(got.share(c)[d], st.share(c)[d]), (c, st.days[d])
        assert _same(got.y_hat[d], st.y_hat[d])


def test_t2_x3_is_twice_the_librarys_rv_tod_at_rth_alerts(base):
    bars, g, _ = base
    alerts = list(F.ALERT_MARKS[::6])
    cal = F.Calendars(frozenset(), frozenset(), (), ())
    X = F.compute(bars, alerts, cal)
    lib = X["rv_tod"].to_numpy().reshape(len(g.days), len(alerts))
    RV = OS.rv60(g.C, alerts)
    mine = 2.0 * np.log(RV / OS.prior_median(RV))
    ok = np.isfinite(lib)
    assert ok.mean() > 0.8
    assert np.allclose(mine[ok], 2.0 * lib[ok], rtol=0, atol=1e-12)
    assert np.array_equal(np.isfinite(mine), ok)


def test_t2_no_window_wraps_at_an_overnight_slot(base):
    _, g, _ = base
    alerts = [1, 2, 5, 25, 59, 60, 61, 62, 120]
    RV = OS.rv60(g.C, alerts)
    for d in range(0, len(g.days), 17):
        C = g.C[d]
        for k, t in enumerate(alerts):
            lo = max(0, t - 60)
            idx = [i for i in range(0, t) if np.isfinite(C[i])]
            ch = [C[b] - C[a] for a, b in zip(idx, idx[1:]) if b >= lo]      # each change ends inside the window
            want = np.sqrt(np.mean(np.square(ch))) if len(ch) >= 2 else np.nan
            assert _same(np.array([RV[d, k]]), np.array([want])) or np.isclose(RV[d, k], want, rtol=1e-12), (d, t)


def test_t2_no_state_is_all_undefined_or_constant(base):
    _, _, st = base
    for c in OS.BUILT:
        sh = st.share(c)
        on = st.in_state(c)[np.isfinite(sh)]
        assert np.isfinite(sh).any(), c
        assert 0.0 < on.mean() < 1.0, c
    with pytest.raises(OS.CellDropped):
        st.share("s3")


def test_the_states_follow_the_declared_clock(base):
    _, _, st = base
    assert st.marks == OS.POPULATION_MARKS and len(st.marks) == 186
    early = [k for k, m in enumerate(st.marks) if m < OS.NIGHT_FIRST_MARK]
    assert not st.in_state("s1")[:, early].any() and not st.in_state("s2")[:, early].any()
    assert OS.N_COEFFICIENTS == 11 and OS.CELLS == ("s1", "s2", "s3", "u3") and OS.BUILT == ("s1", "s2", "u3")
    assert OS.band_of(F.slot(17, 55)) == "evening" and OS.band_of(F.slot(18, 0)) == "asia"
    assert OS.band_of(F.slot(1, 55)) == "asia" and OS.band_of(F.slot(2, 0)) == "london"


def test_the_rolling_share_is_t1s_mid_rank_rule():
    from tests.test_family_o_persistence import mid_rank_share

    x = np.random.default_rng([20261988, 7]).normal(size=900)
    x[::37] = np.nan
    assert _same(OS.rolling_share(x), mid_rank_share(x))


def test_har_needs_all_22_prior_values():
    x = np.arange(60, dtype=float)
    h = OS.har(x)
    assert np.isnan(h[:22]).all()
    d = 30
    assert np.isclose(h[d], (x[d - 1] + x[d - 5:d].mean() + x[d - 22:d].mean()) / 3.0)
    x[40] = np.nan
    assert np.isnan(OS.har(x)[41:63]).all()


# ------------------------------------------------------------------------------------------------ T-7


def _planted(rng, n: int = 400, marks=(0, 30, 60, 300, 540, 700)):
    shape = (n, len(marks))
    x1, x2, x3 = rng.normal(size=shape), rng.normal(size=shape), rng.normal(size=shape)
    beta = {"evening": (0.1, 0.5, 0.3), "asia": (-0.2, 0.4, 0.2, 0.6), "london": (0.05, 0.3, 0.25, 0.7)}
    y = np.empty(shape)
    for k, m in enumerate(marks):
        b = beta[OS.band_of(m)]
        y[:, k] = b[0] + b[1] * x1[:, k] + b[2] * x2[:, k] + (b[3] * x3[:, k] if len(b) > 3 else 0.0)
    y += rng.normal(scale=0.5, size=shape)
    return OS.Regressors(y, x1, x2, x3), list(marks), beta


def test_t7_the_fit_is_the_normal_equations_solve():
    R, marks, _ = _planted(np.random.default_rng([20261988, 30]))
    rows = np.ones(R.y.shape[0], dtype=bool)
    coef = OS.fit(R, marks, rows)
    for band in OS.BANDS:
        X, y = OS._design(R, marks, band, rows)
        direct = np.linalg.solve(X.T @ X, X.T @ y)
        assert np.allclose(coef[band], direct, rtol=0, atol=1e-8), band
    assert sum(len(v) for v in coef.values()) == OS.N_COEFFICIENTS


def test_t7_a_planted_har_process_is_recovered_with_its_signs():
    R, marks, beta = _planted(np.random.default_rng([20261988, 31]), n=1500)
    coef = OS.fit(R, marks, np.ones(R.y.shape[0], dtype=bool))
    for band, b in beta.items():
        assert np.all(np.sign(coef[band][1:]) == np.sign(b[1:])), band
        assert np.allclose(coef[band], b, atol=0.08), band


def test_t7_a_rank_deficient_band_is_refused_and_the_hash_is_canonical():
    R, marks, _ = _planted(np.random.default_rng([20261988, 32]))
    R2 = OS.Regressors(R.y, R.x1, R.x1.copy(), R.x3)             # x2 = x1: rank-deficient
    with pytest.raises(OS.RankDeficient):
        OS.fit(R2, marks, np.ones(R.y.shape[0], dtype=bool))
    coef = OS.fit(R, marks, np.ones(R.y.shape[0], dtype=bool))
    text = OS.canonical_json(coef)
    assert OS.coefficients_from_json(text) == coef
    assert OS.coefficients_sha256(coef) == OS.coefficients_sha256(OS.coefficients_from_json(text))


def test_t7_the_walk_forward_fits_inside_the_choice_block_less_22(base):
    _, g, st = base
    fc = st.forecast
    assert set(fc.folds) == {2021}                               # the synthetic frame holds 2020 and 2021 only
    n2020 = sum(1 for d in st.days if d.year == 2020)
    assert fc.fold_rows[2021] == n2020 - OS.FOLD_GAP
    with pytest.raises(ValueError, match="nothing is fitted"):
        OS.compute(g, frozen=fc.final)                               # the judge never refits (M5)
    frozen = OS.compute(g, frozen=fc.final, test_years=())
    assert frozen.forecast.coefficients_sha256 == fc.coefficients_sha256 and frozen.forecast.final == fc.final
    assert frozen.forecast.folds == {}


def test_t7_family_rs_forecast_is_not_pinned_so_no_shared_code_is_owed():
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    pinned = [p.name for p in (root / "prereg").glob("F-*.md")]
    assert not any("band" in n or "fast" in n or "family_r" in n.lower() for n in pinned), pinned
