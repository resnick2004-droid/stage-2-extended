"""Q-145: the shared statistics module (`extended/family_stats.py`) -- B2's conditional critical values, the conjoint
MDL, the screen rule and the pre-pin power gate -- held to their sources bit for bit, and to level and power on toys
with known truth (E-051's rule: a tightening is accepted only with its level and power shown).

**What is held bit for bit (the extraction; no covered file is edited).** `extended/opening_stats.py` (F-03's build) is
covered by F-03's A0 identity and the shared identities' covers (`extended.opening_run.cover`, `extended.identity_cover`),
so its functions were copied, not moved; every copied piece is compared here with the original on the same inputs and
the same generators, so the copy cannot drift from F-03's code unnoticed:
* the larger-of rule (`larger_of`), its two-sample members, B2's stationary bootstrap and slow sign, B2's replicate on
  the (session x mark) grid, B2's member t's and quantiles, the 63-block amplitude, and the screen rule's comparison in
  `scripts/fo_opening.py` (stage A's `screen = ...`, with `opening_stats.MDL_FACTOR`);
* family B's reference for its named wrapper (`tests/test_family_b_b2.py`'s `cons_bound_with_critical`), and
  `extended.lift_bound`'s MDL definition (`mdl_draws`: crit x se - estimate, the 80th percentile).

**Level and power on toys with known truth** (session-level grid toys: 600 judged sessions, 4 offers a session, the
choice block 1,000 sessions; a pair value d = a rho_t + eta_t + eps, rho a two-state sign switching 1/250 a session,
eta the session effect sd 0.30, eps the offer noise sd 0.35; the sides a regime switching 1/250 with long share 0.8 /
0.2 inside it, or a fair coin per offer). Under the null the realised lift's expectation is exactly zero given the sides
(rho starts at a fair random sign), so the truth is known; a planted lift L moves every pair value toward the side
(d -> d + L s), so the line's lift is L.
* **B2 holds the level where nominal `cons` does not**, at 0.01 (fast) and at the family level 0.05 / 210 (k = 14;
  `slow`), when its null spans the truth: nominal's 95 % Clopper-Pearson interval lies wholly above the level, B2's
  does not; B2 without its drift term does not hold either (the drift is what carries it).
* **A finding, kept on record** (a strict `xfail`; this file's first run asserted otherwise and failed): with the
  choice block's own slow drift resampled in 63-session blocks, B2 at the true amplitude, and family B's declared
  yearly-mean amplitude where its estimate falls below the true one, under-cover on a one-sided side series (mean side
  about -0.6). Diagnosed and replicated with seeds fixed beforehand (`test_b2_level_replication`, slow).
* **B2 has power** (by the null shown to hold): on the persistent toy its power rises with L and reaches 0.8 inside
  the grid; on the coin toy (no persistence, no drift) it is within 0.05 of nominal `cons`'s at every L.
* **The template** (`prereg/TEMPLATE_family.md`) carries the rules, matches no declaration glob, and holds no seed and
  no figure.
* **The conjoint MDL** equals the Gaussian truth on toys where it is known in closed form; at L = 0 the conjunction's
  pass rate is at most the level; on fresh draws its power at the MDL is at least 0.8 and one grid step below it is
  not above 0.8 (within the draws' error); it is no smaller than any line's own MDL.
* **The screen rule** flags only families whose power at their bar is small, and never one with power at its bar.
* **The power gate** refuses cleanly, naming the file, before Q-126 writes its power file; on planted tables it reads
  the declared rows, never passes a family whose true MDL is above the factor times its bar, and is exact at the
  calibrated points.

Seeds: `numpy.random.default_rng([14514500, j, ...])` -- this file's own seed (Q-145), outside the 2026 seed space the
declarations' blocks use, checked unused in the tree, the vendored snapshot and every branch's history before it was
written. Nothing here reads a bar, a walk or a result file of this repository.
"""
from __future__ import annotations

import fnmatch
import functools
import json
import math
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from extended import family_stats as FS
from extended import lift_bound as LB
from extended import opening_stats as OS

ROOT = Path(__file__).resolve().parent.parent
SEED = 14514500
NJ, NC, M = 600, 1000, 4
A_DRIFT, Q_DRIFT, Q_SIDE, P_IN, S_ETA, S_EPS = 0.05, 1 / 250, 1 / 250, 0.8, 0.30, 0.35
MEAN_BLOCK = 63
K_FAMILY = 14
LEVEL_FAMILY = LB.family_level(K_FAMILY)            # 0.05 / 210


def rng(*key: int) -> np.random.Generator:
    return np.random.default_rng([SEED, *key])


def same(a, b) -> bool:
    """Bit-equal floats (NaN equal to NaN)."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return a.shape == b.shape and bool(np.all((a == b) | (np.isnan(a) & np.isnan(b))))


# ================================================================================================ the toys


def markov(g: np.random.Generator, q: float, R: int, n: int) -> np.ndarray:
    """R independent two-state signs of length n switching with probability q a session, from a fair random start."""
    sw = g.random((R, n)) < q
    sw[:, 0] = g.random(R) < 0.5
    return np.where(np.cumsum(sw, axis=1) % 2 == 0, 1.0, -1.0)


def toy_sides(g: np.random.Generator, persistent: bool) -> np.ndarray:
    """The judged sides (NJ x M): a regime switching Q_SIDE with long share P_IN / 1 - P_IN inside it, or a fair coin."""
    if not persistent:
        return np.where(g.random((NJ, M)) < 0.5, 1.0, -1.0)
    reg = markov(g, Q_SIDE, 1, NJ)[0]
    return np.where(g.random((NJ, M)) < np.where(reg > 0, P_IN, 1 - P_IN)[:, None], 1.0, -1.0)


def toy_choice(g: np.random.Generator, a: float) -> np.ndarray:
    """The choice block's pair values (NC x M) by the same process as the truth's."""
    return (a * markov(g, Q_DRIFT, 1, NC)[0][:, None] + S_ETA * g.standard_normal((NC, 1))
            + S_EPS * g.standard_normal((NC, M)))


def truth_t(g: np.random.Generator, s: np.ndarray, a: float, R: int, L: float = 0.0, chunk: int = 2500) -> np.ndarray:
    """The truth's member t's (3 x R): fresh pair values given the sides, the lift L planted toward the side."""
    out = []
    done = 0
    while done < R:
        r = min(chunk, R - done)
        d = (a * markov(g, Q_DRIFT, r, NJ)[:, :, None] + S_ETA * g.standard_normal((r, NJ, 1))
             + S_EPS * g.standard_normal((r, NJ, M)))
        S = (s[None] * d).sum(2).T + L * M
        out.append(FS.member_t_one_sample(S, np.full_like(S, float(M))))
        done += r
    return np.concatenate(out, axis=1)


def b2_of(s: np.ndarray, choice: np.ndarray, a_star: float, level: float, replicates: int, stream: int) -> dict:
    """B2's quantiles for the one-sample line on the sides s: the pooled null (the choice block's sessions by a stationary
    bootstrap of mean block 63, centred, plus a* rho_t switching Q_DRIFT), replicate i from `[SEED, stream, i]`."""
    exists = np.ones((NJ, M), dtype=bool)

    def rep(g):
        V = FS.b2_null_pooled(g, choice, exists, a_star, mean_block=MEAN_BLOCK, switch=Q_DRIFT)
        return FS.grid_session_sums(s * V, exists.astype(float))

    T = FS.b2_member_t(rep, replicates, lambda i: rng(stream, i), form="one_sample")
    return FS.b2_quantiles(T, level)


def df_full() -> np.ndarray:
    return np.array([LB.block_index(NJ, b)[1] - 1 for b in FS.MEMBERS], dtype=float)


def rate_ci(T: np.ndarray, crit: np.ndarray) -> tuple[float, float, float]:
    k = int(FS.rejects_t(T, crit).sum())
    lo, hi = LB.clopper_pearson(k, T.shape[1])
    return k / T.shape[1], lo, hi


# ================================================================================================ A. the extraction


def _sums(g, n, empty_share=0.1):
    N1 = g.integers(0, 4, n).astype(float)
    N2 = N1 + g.integers(0, 6, n)
    N1[g.random(n) < empty_share] = 0.0
    S1 = 0.5 * (2 * g.binomial(N1.astype(int), 0.55) - N1)
    S2 = S1 + 0.5 * (2 * g.binomial((N2 - N1).astype(int), 0.5) - (N2 - N1))
    return S1, N1, S2, N2


@pytest.mark.parametrize("j", range(4))
def test_larger_of_two_sample_is_f03s_rule_bit_for_bit(j):
    g = rng(0, j)
    n = (300, 609, 657, 1006)[j]
    S1, N1, S2, N2 = _sums(g, n)
    for level in (0.01, 0.05, LB.family_level(12), LEVEL_FAMILY):
        for b2 in (None, {21: 1.0, 42: 9.0, 63: 2.5}, {21: float(g.normal(3, 1)), 42: 0.0, 63: 7.0}):
            old = OS.larger_of(S1, N1, S2, N2, level, b2)
            new = FS.larger_of_two_sample(S1, N1, S2, N2, level, b2)
            assert same(old.bound, new.bound) and old.passes == new.passes and old.level == new.level
            assert len(old.members) == len(new.members) == 3
            for mo, mn in zip(old.members, new.members):
                for f in ("block", "estimate", "se", "df", "t_crit", "b2_crit", "crit", "lower"):
                    assert same(getattr(mo, f), getattr(mn, f)), (f, level, b2)


def test_larger_of_one_sample_is_family_bs_reference_and_cons_at_nominal():
    import test_family_b_b2 as T

    for j, n in enumerate((300, 609, 657)):
        g = rng(1, j)
        session = np.sort(g.integers(0, n, 5 * n))
        x = 0.03 + g.standard_normal(session.size)
        for level in (0.01, LB.family_level(12), LEVEL_FAMILY):
            ref = LB.bound("cons", x, session, n, level=level)
            for crit in (None, {21: 2.0, 42: 8.0, 63: 3.0}):
                low, rej = T.cons_bound_with_critical(x, session, n, level, crit)
                line = FS.larger_of_one_sample(*LB.session_sums(x, session, n), level, crit)
                assert line.bound == low and line.passes == rej
                assert FS.cons_bound_with_critical(x, session, n, level, crit) == (low, rej)
                if crit is None:
                    assert line.bound == ref.lower and line.passes == ref.rejects


def test_the_bootstrap_and_the_slow_sign_draw_as_f03s():
    for j, (n_src, n_out, mb) in enumerate(((1000, 600, 63.0), (37, 250, 21.0), (5, 3, 63.0), (900, 0, 63.0))):
        g1, g2 = rng(2, j), rng(2, j)
        assert np.array_equal(OS.stationary_indices(g1, n_src, n_out, mb), FS.stationary_indices(g2, n_src, n_out, mb))
        assert g1.random() == g2.random()                          # the same number of draws taken
        g1, g2 = rng(3, j), rng(3, j)
        assert np.array_equal(OS.slow_sign(g1, n_out, 1 / 63), FS.slow_sign(g2, n_out, 1 / 63))
        assert g1.random() == g2.random()
    with pytest.raises(ValueError):
        FS.stationary_indices(rng(2, 9), 0, 5, 63.0)


def _b2_inputs(g):
    """A synthetic B2Inputs of F-03's form: choice values with gaps, day kinds b / n (and f, left empty, judged), the
    judged strata (kind, year), the judged offers and the two samples' weights."""
    nc, nj, m = 400, 300, 6
    cv = g.standard_normal((nc, m))
    cv[g.random((nc, m)) < 0.1] = np.nan
    ck = np.where(g.random(nc) < 0.2, "b", "n").astype(object)
    jk = np.where(g.random(nj) < 0.2, "b", np.where(g.random(nj) < 0.05, "f", "n")).astype(object)
    year = np.repeat([2024, 2025, 2026], [120, 120, 60])
    groups = sorted({(str(a), int(b)) for a, b in zip(jk, year)})
    pos = {gk: i for i, gk in enumerate(groups)}
    jg = np.array([pos[(str(a), int(b))] for a, b in zip(jk, year)], dtype=np.int64)
    ex = g.random((nj, m)) < 0.8
    W2 = ex.astype(float)
    W1 = (ex & (g.random((nj, m)) < 0.3)).astype(float)
    return OS.B2Inputs(cv, ck, jk, jg, ex, W1, W2)


def _strata_rep(inp, a_star):
    def rep(g):
        V = FS.b2_null_strata(g, inp.choice_values, inp.choice_kind, inp.judged_kind, inp.judged_group,
                              inp.judged_exists, a_star, kinds=OS.B2_KINDS, mean_block=OS.B2_MEAN_BLOCK,
                              switch=OS.SLOW_SWITCH)
        S1, N1 = FS.grid_session_sums(V, inp.W1)
        S2, N2 = FS.grid_session_sums(V, inp.W2)
        return S1, N1, S2, N2
    return rep


def test_b2_strata_replicate_is_f03s_bit_for_bit():
    inp = _b2_inputs(rng(4, 0))
    rep = _strata_rep(inp, 0.07)
    for i in range(25):
        old = OS.b2_replicate_sums(inp, 0.07, rng(4, 1, i))
        new = rep(rng(4, 1, i))
        assert all(same(o, n_) for o, n_ in zip(old, new))
    V = inp.choice_values[:300]
    assert all(same(a, b) for a, b in zip(FS.grid_session_sums(V, inp.W2), OS.session_sums(V, inp.W2)))


def test_b2_quantiles_are_f03s_bit_for_bit_and_chunking_changes_no_draw():
    inp = _b2_inputs(rng(5, 0))
    for level in (0.05, 0.01):
        old, T_old = OS.b2_quantiles(inp, 0.04, level, line=0, replicates=400, prefix=(SEED, 5, 1), keep=True)
        rep = _strata_rep(inp, 0.04)
        T = FS.b2_member_t(rep, 400, lambda i: rng(5, 1, i), form="two_sample")
        assert np.array_equal(T, T_old)
        assert FS.b2_quantiles(T, level) == old
        # the chunking changes no draw; it can change a t's last bit (numpy's reductions over a chunk's columns), so
        # bit-identity with F-03 holds at F-03's chunk (500), and another chunk agrees to rounding (first run: one t
        # of 1,200 differed, by 1.1e-16 -- the claim of bit equality across chunks was wrong and is corrected here)
        T7 = FS.b2_member_t(rep, 400, lambda i: rng(5, 1, i), form="two_sample", chunk=7)
        assert np.allclose(T7, T, rtol=1e-13, atol=1e-13)
        assert FS.b2_critical(rep, level=level, replicates=400, key=lambda i: rng(5, 1, i), form="two_sample") == old


def test_the_member_t_forms_are_f03s_and_lift_bounds():
    g = rng(6, 0)
    S1, N1, S2, N2 = (np.column_stack(c) for c in zip(*[_sums(g, 609) for _ in range(50)]))
    assert same(OS.member_t(S1, N1, S2, N2), FS.member_t_two_sample(S1, N1, S2, N2))
    T1 = FS.member_t_one_sample(S1, N1)
    for i, b in enumerate(FS.MEMBERS):
        est, se, _ = LB.t_stats(S1, N1, block=b, weight="trades")
        assert same(T1[i], np.where(np.isfinite(se) & (se > 0), est / se, np.nan))


def test_the_block_amplitude_is_f03s():
    g = rng(7, 0)
    for n in (657, 1006, 40):
        x = g.standard_normal(n) + 0.1
        x[g.random(n) < 0.2] = np.nan
        for b in (63, 21):
            assert OS.block_mean_amplitude(x, b) == FS.block_mean_amplitude(x, b)


def test_the_screen_rule_is_f03s_on_every_planted_case():
    """`scripts/fo_opening.py` (stage A): `screen = bool(surviving) and all(mdl > MDL_FACTOR x lambda_bar)`."""
    assert FS.MDL_FACTOR == OS.MDL_FACTOR == 3.0
    g = rng(8, 0)
    cases = [({}, {}), ({"a": 3.0}, {"a": 1.0}), ({"a": 3.0000001}, {"a": 1.0}), ({"a": math.inf}, {"a": 0.2})]
    for _ in range(300):
        cells = [f"c{i}" for i in range(int(g.integers(1, 5)))]
        bar = {c: float(g.uniform(0.001, 0.05)) for c in cells}
        mdl = {c: float(bar[c] * g.choice([0.5, 2.9, 3.0, 3.1, 10.0, math.inf])) for c in cells}
        cases.append((mdl, bar))
    for mdl, bar in cases:
        old = bool(list(mdl)) and all(mdl[c] > OS.MDL_FACTOR * bar[c] for c in mdl)
        assert FS.screen_rule(mdl, bar).screen == old


def test_the_mdl_is_lift_bounds_definition():
    """lift_bound.mdl_draws("cons"): per replication, the largest over members of crit x se - estimate; the MDL its 80th
    percentile. The module's need (minus the line's lower bound) and quantile give the same numbers."""
    g = rng(9, 0)
    S = 0.5 * (2 * g.binomial(4, 0.5, (609, 3000)) - 4.0)
    N = np.full_like(S, 4.0)
    for level in (0.01, LEVEL_FAMILY):
        ref = LB.mdl_draws("cons", S, N, level=level)
        est, se, df = FS.members_one_sample(S, N)
        crit = FS.critical(level, df[:, 0])
        need = FS.need_from_lowers(FS.lower_bounds(est, se, crit)[:, None])
        assert np.array_equal(need, ref)
        assert FS.mdl_from_need(need, 0.8) == float(np.quantile(ref, 0.8))


# ================================================================================================ B. B2: level and power


def test_b2_null_pooled_builds_the_declared_null():
    g = rng(10, 0)
    choice = g.standard_normal((50, 3))
    exists = g.random((40, 3)) < 0.7
    V = FS.b2_null_pooled(rng(10, 1), choice, exists, 0.2, mean_block=5.0, switch=0.1)
    g2 = rng(10, 1)
    pi = FS.stationary_indices(g2, 50, 40, 5.0)
    W = choice[pi]
    mu = W[exists].mean()
    drift = 0.2 * FS.slow_sign(g2, 40, 0.1)
    assert same(V, np.where(exists, W - mu + drift[:, None], np.nan))
    assert np.isnan(V[~exists]).all() and np.isfinite(V[exists]).all()
    V0 = FS.b2_null_pooled(rng(10, 1), choice, exists, 0.0, mean_block=5.0, switch=0.1)
    assert abs(float(V0[exists].mean())) < 1e-12            # centred over the judged offers before the drift


def test_the_two_amplitude_rules():
    x = np.r_[np.full(250, 0.1), np.full(250, -0.3), np.full(100, np.nan), np.full(57, 0.2)]
    years = np.repeat([2024, 2025, 2026], [250, 250, 157])
    assert FS.year_mean_amplitude(x, years) == pytest.approx(0.3, abs=1e-15)
    assert FS.block_mean_amplitude(x, 63) == pytest.approx(0.3, abs=1e-15)
    with pytest.raises(ValueError):
        FS.year_mean_amplitude(x, years[:-1])


def test_the_slow_two_state_and_the_centring():
    x = FS.slow_two_state(rng(11, 0), 500, 0.03, 1 / 50)
    assert set(np.unique(x)) <= {0.0, 0.06}
    v = rng(11, 1).standard_normal((20, 4))
    w = (rng(11, 2).random((20, 4)) < 0.6).astype(float)
    c = FS.centre_within(v, w)
    # one shift for every entry (to rounding: the first form asserted bit equality of c - v, which (v - m) - v is not)
    assert abs(float((c * w).sum())) < 1e-12 and np.allclose(c - v, c[0, 0] - v[0, 0], rtol=0, atol=1e-15)


def test_the_refusals():
    with pytest.raises(ValueError):
        FS.critical(0.5, [10.0, 10.0, 10.0])
    with pytest.raises(ValueError):
        FS.critical(0.0, [10.0, 10.0, 10.0])
    with pytest.raises(FS.NotFinite):
        FS.critical(0.01, [10.0, 10.0, 10.0], {21: math.nan, 42: 1.0, 63: 1.0})
    with pytest.raises(FS.NotFinite):
        FS.larger_of_two_sample(*_sums(rng(12, 0), 300), 0.01, {21: math.inf, 42: 1.0, 63: 1.0})
    with pytest.raises(FS.NotFinite):
        FS.b2_quantiles(np.full((3, 10), np.nan), 0.05)
    with pytest.raises(ValueError):
        FS.b2_member_t(lambda g: (np.ones(5),), 3, lambda i: rng(12, i), form="one_sample")
    with pytest.raises(ValueError):
        FS.b2_member_t(lambda g: (np.ones(5), np.ones(5)), 3, lambda i: rng(12, i), form="three_sample")


def toy_choice_exact(g: np.random.Generator) -> np.ndarray:
    """A choice block of the truth's noise only (its session effect and offer noise, no drift): with `a* = a` B2's null
    is then the truth's own process given the sides -- the null that spans the truth."""
    return S_ETA * g.standard_normal((NC, 1)) + S_EPS * g.standard_normal((NC, M))


YEARS_C = np.repeat(np.arange(4), NC // 4)


@functools.lru_cache(maxsize=None)
def _level_case(level: float, truths: int, replicates: int, stream: int) -> dict:
    """One persistent side series (`[SEED, stream, 0]`), its truth's t's (`[SEED, stream, 1]`) and B2 five ways, each
    from its own stream `[SEED, 10 stream + j, i]`: j = 4 the null spanning the truth (`toy_choice_exact`, a* = a, the
    exact choice block from `[SEED, 10 stream + 4, 0]`); 3 with no drift term (a* = 0); 2 the choice block with its own
    drift resampled and a* = a; 5 family B's declared amplitude (the choice block's largest calendar-year mean); 7 that
    choice block at a* = 2a. Returns {name: (rate, CI low, CI high)}."""
    g = rng(stream, 0)
    s = toy_sides(g, persistent=True)
    choice = toy_choice(g, A_DRIFT)
    exact = toy_choice_exact(rng(10 * stream + 4, 0))
    T = truth_t(rng(stream, 1), s, A_DRIFT, truths)
    df = df_full()
    a_year = FS.year_mean_amplitude(choice.mean(1), YEARS_C)
    out = {"nominal": rate_ci(T, FS.critical(level, df)), "mean_side": float(s.mean()), "a_year": a_year}
    for name, ch, a_star, j in (("exact", exact, A_DRIFT, 4), ("no_drift", choice, 0.0, 3),
                                ("a_true", choice, A_DRIFT, 2), ("declared", choice, a_year, 5),
                                ("a_twice", choice, 2 * A_DRIFT, 7)):
        out[name] = rate_ci(T, FS.critical(level, df, b2_of(s, ch, a_star, level, replicates, 10 * stream + j)))
    print(f"\n[B2 level at {level:.3g}, {truths} truths, {replicates} B2 replicates, stream {stream}; mean side "
          f"{out['mean_side']:.3f}, a_year {a_year:.4f}, a {A_DRIFT}] "
          + "; ".join(f"{k} {v[0]:.6f} ({v[1]:.6f}, {v[2]:.6f})" for k, v in out.items() if isinstance(v, tuple)))
    return out


def test_b2_holds_the_level_where_nominal_cons_does_not():
    """At 0.01 on stream 20: nominal `cons` is lax (the defect B2 answers); B2 whose null spans the truth holds the
    level; B2 with no drift term does not (the drift is what holds it); B2 at twice the drift holds."""
    level = 0.01
    out = _level_case(level, 40_000, 10_000, 20)
    assert out["nominal"][1] > level
    assert out["exact"][1] <= level and out["exact"][0] <= 1.25 * level
    assert out["no_drift"][1] > level
    assert out["a_twice"][1] <= level


@pytest.mark.xfail(strict=True, reason=(
    "Q-145's finding, kept on record (the failure protocol): this file's first run asserted that B2 at the true drift "
    "amplitude holds 0.01 on stream 20, and it did not. Diagnosed with seeds fixed beforehand (the docstring): the "
    "machinery holds when its null spans the truth (the test above); the choice block's own slow drift, resampled in "
    "63-session blocks, adds block-scale variance that dilutes the slow part, so on a one-sided side series B2 at a* = a "
    "under-covers, and family B's declared yearly-mean a* under-covers whenever its estimate falls below a. A family "
    "using the pooled form declares its amplitude with this in view; strict, so a pass here fails the suite."))
def test_b2_as_family_b_declares_it_holds_on_a_one_sided_side_series():
    """Expected to fail (the record): on stream 20 (mean side about -0.6), B2 with the choice block's own drift
    resampled, at a* = a and at family B's declared yearly-mean a* (below a on this draw), is lax at 0.01. The
    replication on streams 22-26 (`test_b2_level_replication`, slow): the null spanning the truth held on every one;
    a* = a held on all five; the declared rule was lax on one, where its estimate fell below a."""
    level = 0.01
    out = _level_case(level, 40_000, 10_000, 20)
    assert out["a_true"][1] <= level and out["declared"][1] <= level


@pytest.mark.slow
def test_b2_level_replication():
    """The diagnosis's replication (seeds fixed before it ran: streams 22-26, the same construction as stream 20): the
    null spanning the truth holds 0.01 on every side series; the other forms are printed, deciding nothing here."""
    for stream in (22, 23, 24, 25, 26):
        out = _level_case(0.01, 40_000, 10_000, stream)
        assert out["nominal"][0] > 0.01 and out["exact"][1] <= 0.01


@pytest.mark.slow
def test_b2_holds_the_level_at_the_family_level():
    """At 0.05 / 210 (k = 14) on stream 21: nominal lax, the null spanning the truth holds, no drift term lax; the other
    forms printed (decided before this ran, after the 0.01 finding)."""
    out = _level_case(LEVEL_FAMILY, 400_000, 200_000, 21)
    assert out["nominal"][1] > LEVEL_FAMILY
    assert out["exact"][1] <= LEVEL_FAMILY and out["exact"][0] <= 1.25 * LEVEL_FAMILY
    assert out["no_drift"][1] > LEVEL_FAMILY


def _power_case(level: float, persistent: bool, grid, truths: int, replicates: int, stream: int):
    """B2's power by the null that spans the truth (the form shown to hold the level), against nominal `cons`'s."""
    g = rng(stream, 0)
    a = A_DRIFT if persistent else 0.0
    s = toy_sides(g, persistent=persistent)
    choice = toy_choice_exact(rng(10 * stream + 4, 0))
    df = df_full()
    nom = FS.critical(level, df)
    rule = FS.critical(level, df, b2_of(s, choice, a, level, replicates, 10 * stream + 2))
    p_nom, p_rule = [], []
    for i, L in enumerate(grid):
        T = truth_t(rng(stream, 1, i), s, a, truths, L)
        p_nom.append(float(FS.rejects_t(T, nom).mean()))
        p_rule.append(float(FS.rejects_t(T, rule).mean()))
    print(f"\n[B2 power at {level:.3g}, {'persistent' if persistent else 'coin'} toy] L {list(grid)}; nominal "
          f"{np.round(p_nom, 4).tolist()}; B2 {np.round(p_rule, 4).tolist()}; crit nominal {nom.round(3)} B2 "
          f"{rule.round(3)}")
    return np.array(p_nom), np.array(p_rule)


def test_b2_has_power():
    """At 0.01: on the persistent toy B2's power rises with the lift and reaches 0.8 inside the grid, at no more than
    twice nominal's 80 % point (nominal's own level is lax there); on the coin toy it is within 0.05 of nominal's."""
    level = 0.01
    grid = (0.02, 0.04, 0.06, 0.08, 0.10)
    p_nom, p_rule = _power_case(level, True, grid, 10_000, 10_000, 30)
    assert np.all(np.diff(p_rule) >= -0.01) and p_rule[-1] >= 0.8
    mdl_nom = next(L for L, p in zip(grid, p_nom) if p >= 0.8)
    assert next(L for L, p in zip(grid, p_rule) if p >= 0.8) <= 2 * mdl_nom
    p_nom, p_rule = _power_case(level, False, (0.01, 0.02, 0.03, 0.04), 10_000, 10_000, 31)
    assert np.all(p_rule >= p_nom - 0.05)


@pytest.mark.slow
def test_b2_has_power_at_the_family_level():
    grid = (0.04, 0.08, 0.12, 0.16, 0.20)
    p_nom, p_rule = _power_case(LEVEL_FAMILY, True, grid, 20_000, 200_000, 32)
    assert np.all(np.diff(p_rule) >= -0.01) and p_rule[-1] >= 0.8
    mdl_nom = next(L for L, p in zip(grid, p_nom) if p >= 0.8)
    assert next(L for L, p in zip(grid, p_rule) if p >= 0.8) <= 2 * mdl_nom
    p_nom, p_rule = _power_case(LEVEL_FAMILY, False, (0.02, 0.04, 0.06, 0.08), 20_000, 200_000, 33)
    assert np.all(p_rule >= p_nom - 0.05)


# ================================================================================================ C. the conjoint MDL


def _gauss_lowers(g, draws, lines, c, se=1.0, rho=0.0):
    """Gaussian lines: est ~ N(0, se^2) with correlation rho between lines, lower = est - c se."""
    z = g.standard_normal((draws, lines))
    if rho:
        z = math.sqrt(1 - rho) * z + math.sqrt(rho) * g.standard_normal((draws, 1))
    return se * z - c * se


def test_the_conjoint_mdl_is_the_gaussian_truth():
    c, se, step = 3.5, 0.01, 0.00025
    grid = np.round(np.arange(1, 401) * step, 8)
    for lines, p_each in ((1, 0.8), (2, math.sqrt(0.8)), (3, 0.8 ** (1 / 3))):
        lw = _gauss_lowers(rng(40, lines), 200_000, lines, c, se)
        truth = (c + stats.norm.ppf(p_each)) * se
        res = FS.conjoint_mdl_linear(lw, np.ones(lines), grid)
        assert abs(res.mdl_continuous - truth) < 0.02 * se
        assert truth - step - 0.02 * se <= res.mdl <= truth + step + 0.02 * se
        assert all(res.mdl >= v for v in res.line_mdl)


def test_the_conjoint_mdl_level_and_power_on_fresh_draws():
    """Two cons lines on the coin toy (each at B2's larger-of critical values; the second a paired difference against a
    twin agreeing with the model on 70 % of offers, so its lift is L times the disagreement count): at L = 0 the
    conjunction passes at most the level; on fresh draws its power at the conjoint MDL is at least 0.8 and one grid
    step below it is not above 0.8, within the draws' error; it is no smaller than either line's own MDL."""
    level = 0.01
    g = rng(41, 0)
    s = toy_sides(g, persistent=False)
    f = np.where(g.random((NJ, M)) < 0.3, -s, s)
    dis = (1.0 - s * f)                                   # 0 or 2 per offer: the paired line's weight on the lift
    choice = toy_choice(g, 0.0)
    df = df_full()
    crit1 = FS.critical(level, df, b2_of(s, choice, 0.0, level, 5000, 412))
    exists = np.ones((NJ, M), dtype=bool)

    def rep2(gg):
        V = FS.b2_null_pooled(gg, choice, exists, 0.0, mean_block=MEAN_BLOCK, switch=Q_DRIFT)
        return FS.grid_session_sums((s - f) * V, exists.astype(float))

    crit2 = FS.critical(level, df, FS.b2_critical(rep2, level=level, replicates=5000, key=lambda i: rng(413, i),
                                                   form="one_sample"))

    def lowers(gg, draws):
        d = S_ETA * gg.standard_normal((draws, NJ, 1)) + S_EPS * gg.standard_normal((draws, NJ, M))
        S1 = (s[None] * d).sum(2).T
        S2 = ((s - f)[None] * d).sum(2).T
        N = np.full_like(S1, float(M))
        e1, se1, _ = FS.members_one_sample(S1, N)
        e2, se2, _ = FS.members_one_sample(S2, N)
        low = np.column_stack([FS.lower_bounds(e1, se1, crit1), FS.lower_bounds(e2, se2, crit2)])
        return low, np.array([1.0, dis.sum() / (NJ * M)])

    low0, slopes = lowers(rng(41, 1), 20_000)
    grid = np.round(np.arange(1, 201) * 0.0025, 6)
    res = FS.conjoint_mdl_linear(low0, slopes, grid)
    assert math.isfinite(res.mdl) and all(res.mdl >= v for v in res.line_mdl)
    lo, _ = LB.clopper_pearson(int(np.all(low0 > 0, axis=1).sum()), low0.shape[0])
    assert lo <= level
    fresh, _ = lowers(rng(41, 2), 20_000)
    p_at = float(np.all(fresh + res.mdl * slopes > 0, axis=1).mean())
    p_below = float(np.all(fresh + (res.mdl - 0.0025) * slopes > 0, axis=1).mean())
    print(f"\n[conjoint MDL, two lines at {level}] MDL {res.mdl}; lines' own {res.line_mdl}; fresh power at it "
          f"{p_at:.4f}, a step below {p_below:.4f}")
    assert p_at >= 0.8 - 0.01 and p_below <= 0.8 + 0.01


def test_the_grid_and_linear_forms_agree_and_the_edges():
    lw = _gauss_lowers(rng(42, 0), 5000, 3, 3.0, 0.02, rho=0.5)
    slopes = np.array([1.0, 0.6, 0.3])
    grid = np.round(np.arange(1, 101) * 0.005, 6)
    lin = FS.conjoint_mdl_linear(lw, slopes, grid)
    gr = FS.conjoint_mdl_grid(lambda L: lw + L * slopes[None, :] > 0, grid)
    assert lin.mdl == gr.mdl and np.array_equal(lin.conj_power, gr.conj_power) and lin.line_mdl == gr.line_mdl
    tiny = FS.conjoint_mdl_grid(lambda L: lw + L * slopes[None, :] > 0, grid[:3])
    assert tiny.mdl == math.inf                           # "above the grid"
    for bad in ([0.01, 0.005], [0.0, 0.01], [], [0.01, math.nan]):
        with pytest.raises(ValueError):
            FS.conjoint_mdl_grid(lambda L: lw > 0, bad)
    with pytest.raises(ValueError):
        FS.conjoint_mdl_linear(lw, np.array([1.0, 0.0, 1.0]), grid)
    with pytest.raises(ValueError):
        FS.mdl_from_need(np.ones(5), 1.0)
    need = np.array([1.0, 2.0, math.inf, math.inf, math.inf])
    assert FS.mdl_from_need(need, 0.25) == 2.0 and FS.mdl_from_need(need, 0.8) == math.inf
    assert FS.mdl_from_need(np.array([1.0, 2.0, 3.0]), 0.8) == float(np.quantile([1.0, 2.0, 3.0], 0.8))


# ================================================================================================ D. the screen rule


def test_the_screen_rule_flags_only_families_without_power_at_their_bar():
    """Gaussian single-line cells (crit c, se): the cell's 80 % MDL is (c + z_0.8) se. A family the rule declares a
    screen (every cell's MDL above three times its bar) has power at most 0.05 at its bar in every cell; a cell whose MDL
    is at or below its bar has power at least 0.8 there, and a family holding one is never a screen."""
    g = rng(50, 0)
    c = stats.t.ppf(1 - LEVEL_FAMILY, 8)
    for _ in range(40):
        cells = [f"c{i}" for i in range(int(g.integers(1, 4)))]
        se = {k: float(g.uniform(0.005, 0.03)) for k in cells}
        mdl = {k: (c + stats.norm.ppf(0.8)) * se[k] for k in cells}
        bar = {k: mdl[k] / float(g.choice([0.5, 1.0, 2.0, 2.9, 3.1, 6.0])) for k in cells}
        v = FS.screen_rule(mdl, bar)
        z = g.standard_normal(20_000)
        power = {k: float(np.mean(z * se[k] + bar[k] - c * se[k] > 0)) for k in cells}
        if v.screen:
            assert all(p <= 0.05 for p in power.values()), (mdl, bar, power)
        if any(mdl[k] <= bar[k] for k in cells):
            assert not v.screen and all(power[k] >= 0.8 - 0.01 for k in cells if mdl[k] <= bar[k])
        assert v.ratios == {k: mdl[k] / bar[k] for k in cells}


def test_the_screen_rule_refuses():
    for mdl, bar in (({"a": math.nan}, {"a": 1.0}), ({"a": 1.0}, {"a": 0.0}), ({"a": 1.0}, {"b": 1.0}),
                     ({"a": 1.0}, {"a": math.inf}), ({"a": -1.0}, {"a": 1.0})):
        with pytest.raises((ValueError, FS.NotFinite)):
            FS.screen_rule(mdl, bar)
    with pytest.raises(ValueError):
        FS.screen_rule({"a": 1.0}, {"a": 1.0}, factor=0.0)


# ================================================================================================ E. the power gate


def planted_power(mdl80) -> pd.DataFrame:
    """A power table in `q126_cal_power.csv`'s form (`scripts/q126_calibrate.py`'s `power_rows`, then the P rows):
    mdl80(value, size, model, candidate, scope, k) for the toys j = 0 at each size."""
    rows = []
    for value, toy in (("win1", "P"), ("net3", "net3")):
        for z in (200, 500, 1000, 2000, 5000):
            for model in ("coin", "flip1"):
                for cand in ("cons_m1.25", "cons_m1.5"):
                    for scope in ("D", "Q"):
                        for k in (13, 15, 20):
                            m80 = float(mdl80(value, z, model, cand, scope, k))
                            rows.append({"row": "toy", "null": f"sub:{z}:00:{value}:{model}", "toy": toy, "size": z,
                                         "value": value, "model": model, "candidate": cand, "cid": 0, "scope": scope,
                                         "k": k, "reps_used": 20000, "mdl50": m80 / 2, "mdl80": m80,
                                         "infinite_share": 0.0})
    rows.append({"row": "P", "candidate": "cons_m1.25", "scope": "D", "P": 0.5})
    return pd.DataFrame(rows)


def gauss_mdl(value, z, model, cand, scope, k):
    """A known-truth MDL: (z_{1 - level(k)} + z_0.8) sigma / sqrt(z), flip1 10 % above coin, cons_m1.5 a fifth above."""
    sig = 0.5 if value == "win1" else 1.4
    m = (stats.norm.ppf(1 - LB.family_level(k)) + stats.norm.ppf(0.8)) * sig / math.sqrt(z)
    return m * (1.1 if model == "flip1" else 1.0) * (1.2 if cand == "cons_m1.5" else 1.0)


def test_the_gate_refuses_cleanly_before_q126_writes_its_power_file(tmp_path):
    p = tmp_path / "q126_cal_power.csv"
    with pytest.raises(FS.PowerGateRefused) as e:
        FS.power_gate(k=14, candidate="cons_m1.25", scope="D", value="win1", supply=1500, bar=0.02, path=p)
    msg = str(e.value)
    assert str(p) in msg and "scripts/q126_calibrate.py" in msg and "REFUSED" in msg
    default = ROOT / "results" / FS.POWER_FILE
    if not default.exists():                              # until the calibration writes it, the default refuses too
        with pytest.raises(FS.PowerGateRefused) as e2:
            FS.power_gate(k=14, candidate="cons_m1.25", scope="D", value="win1", supply=1500, bar=0.02)
        assert FS.POWER_FILE in str(e2.value)


def test_the_gate_reads_the_declared_rows():
    t = planted_power(gauss_mdl)
    v = FS.power_gate_from_table(t, k=14, candidate="cons_m1.25", scope="D", value="win1", supply=1500, bar=0.01)
    assert (v.k_used, v.size_used) == (15, 1000)
    assert v.mdl80 == max(gauss_mdl("win1", 1000, m, "cons_m1.25", "D", 15) for m in ("coin", "flip1"))
    assert v.closes == (v.mdl80 > 3.0 * 0.01) and v.ratio == v.mdl80 / 0.01
    assert v.beside_scaled == v.mdl80 * math.sqrt(1000 / 1500)
    assert len(v.rows) == 2
    for k, ku in ((13, 13), (15, 15), (16, 20), (20, 20)):
        assert FS.power_gate_from_table(t, k=k, candidate="cons_m1.5", scope="Q", value="net3", supply=5000,
                                        bar=1.0).k_used == ku
    for sup, zu in ((200, 200), (499, 200), (10_000, 5000)):
        assert FS.power_gate_from_table(t, k=13, candidate="cons_m1.5", scope="Q", value="net3", supply=sup,
                                        bar=1.0).size_used == zu
    t2 = planted_power(lambda *a: math.inf if a[2] == "flip1" else 0.001)
    assert FS.power_gate_from_table(t2, k=13, candidate="cons_m1.25", scope="D", value="win1", supply=600,
                                    bar=1.0).closes


@pytest.mark.parametrize("kw", [dict(k=12), dict(k=21), dict(supply=199), dict(candidate="cons"), dict(scope="X"),
                                dict(value="net1"), dict(bar=0.0), dict(bar=math.nan), dict(bar=math.inf),
                                dict(factor=0.0), dict(supply=math.nan)])
def test_the_gate_refuses_outside_its_table(kw):
    base = dict(k=14, candidate="cons_m1.25", scope="D", value="win1", supply=1500, bar=0.01)
    with pytest.raises(FS.PowerGateRefused):
        FS.power_gate_from_table(planted_power(gauss_mdl), **{**base, **kw})


def test_the_gate_refuses_an_incomplete_table():
    t = planted_power(gauss_mdl)
    t = t[~((t["model"] == "flip1") & (t["size"] == 1000))]
    with pytest.raises(FS.PowerGateRefused):
        FS.power_gate_from_table(t, k=14, candidate="cons_m1.25", scope="D", value="win1", supply=1500, bar=0.01)
    t = planted_power(gauss_mdl)
    t.loc[t.index[0], "mdl80"] = math.nan
    with pytest.raises(FS.PowerGateRefused):
        FS.power_gate_from_table(t, k=13, candidate="cons_m1.25", scope="D", value="win1", supply=200, bar=0.01)


def test_the_gate_never_passes_a_family_without_power_and_is_exact_at_the_calibrated_points():
    """Known truth: the planted table's MDL is the Gaussian one at every (k, size); a family's true MDL at its own k and
    supply is the same formula there. The gate's lookup (the smallest calibrated k at or above the family's, the largest
    calibrated size at or below its supply, the larger of the two side models) only overstates the MDL, so no family
    whose true MDL is above the factor times its bar passes; at a calibrated (k, size) it decides exactly as the truth."""
    t = planted_power(gauss_mdl)
    g = rng(60, 0)
    for _ in range(400):
        k = int(g.integers(13, 21))
        supply = int(g.integers(200, 8000))
        cand, scope = str(g.choice(["cons_m1.25", "cons_m1.5"])), str(g.choice(["D", "Q"]))
        true = max(gauss_mdl("win1", supply, m, cand, scope, k) for m in ("coin", "flip1"))
        bar = true / 3.0 * float(g.uniform(0.5, 1.5))
        v = FS.power_gate_from_table(t, k=k, candidate=cand, scope=scope, value="win1", supply=supply, bar=bar)
        assert v.mdl80 >= true - 1e-15
        if true > 3.0 * bar:
            assert v.closes
        if k in (13, 15, 20) and supply in (200, 500, 1000, 2000, 5000):
            assert v.closes == (true > 3.0 * bar)


CHILD = """
import json, os, sys
from pathlib import Path
sys.path.insert(0, os.getcwd())
os.environ.setdefault("OMP_NUM_THREADS", "1")
"""


def child(code: str, tmp: Path) -> dict:
    e = {k: v for k, v in os.environ.items() if k != "S2X_CLEAN_RUN"}
    e["S2X_TMP"] = str(tmp)
    r = subprocess.run([sys.executable, "-c", CHILD + textwrap.dedent(code)], cwd=ROOT, capture_output=True, text=True,
                       timeout=300, env=e)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_the_gate_reads_a_manifested_file_and_refuses_one_not_from_a_clean_run(tmp_path):
    """In its own process (the results writer puts the vendored tree on sys.path): a planted power file written through
    `extended.results.write_result` with the calibration's script name, a clean run's provenance and exploratory False
    is read and decides as the table; the same file without the clean run's provenance, marked exploratory, from
    another script, or edited after its write, is refused."""
    t = planted_power(gauss_mdl)
    t.to_pickle(tmp_path / "table.pkl")
    out = child("""
        import math
        import pandas as pd
        from extended import family_stats as FS
        from extended import results as X
        d = Path(os.environ["S2X_TMP"])
        t = pd.read_pickle(d / "table.pkl")
        kw = dict(k=14, candidate="cons_m1.25", scope="D", value="win1", supply=1500, bar=0.01)
        got = {}
        for name, prov, expl, script in (("good", {"clean_run": {"name": "t"}}, False, FS.POWER_SCRIPT),
                                         ("noclean", None, False, FS.POWER_SCRIPT),
                                         ("explor", {"clean_run": {"name": "t"}}, True, FS.POWER_SCRIPT),
                                         ("script", {"clean_run": {"name": "t"}}, False, "scripts/other.py")):
            sub = d / name
            sub.mkdir()
            csv, mp = X.write_result(t, "q126_cal_power", script=script, seed=None, parameters={}, results_dir=sub,
                                     provenance=prov, exploratory=expl, require_seed=False)
            m = json.loads(Path(mp).read_text(encoding="utf-8"))      # a clean run's commit is not dirty; this
            m["git_commit"] = m["git_commit"].replace("-dirty", "")   # worktree may be, so the manifest is planted
            m["git_dirty"] = False
            Path(mp).write_text(json.dumps(m), encoding="utf-8")
            try:
                v = FS.power_gate(path=csv, **kw)
                got[name] = {"closes": v.closes, "mdl80": v.mdl80, "k_used": v.k_used, "size_used": v.size_used}
            except FS.PowerGateRefused as e:
                got[name] = "refused: " + str(e)[:200]
        mp = X.manifest_path_for(d / "good" / "q126_cal_power.csv")
        m = json.loads(Path(mp).read_text(encoding="utf-8"))
        m["git_dirty"] = True
        Path(mp).write_text(json.dumps(m), encoding="utf-8")
        try:
            FS.power_gate(path=d / "good" / "q126_cal_power.csv", **kw)
            got["dirty"] = "read"
        except FS.PowerGateRefused as e:
            got["dirty"] = "refused: " + str(e)[:200]
        m["git_dirty"] = False
        Path(mp).write_text(json.dumps(m), encoding="utf-8")
        csv = d / "good" / "q126_cal_power.csv"
        csv.write_text(csv.read_text(encoding="utf-8").replace("20000", "20001", 1), encoding="utf-8")
        try:
            FS.power_gate(path=csv, **kw)
            got["edited"] = "read"
        except FS.PowerGateRefused as e:
            got["edited"] = "refused: " + str(e)[:200]
        pure = FS.power_gate_from_table(t, **kw)
        got["pure"] = {"closes": pure.closes, "mdl80": pure.mdl80, "k_used": pure.k_used, "size_used": pure.size_used}
        print(json.dumps(got))
    """, tmp_path)
    assert out["good"] == out["pure"]
    for name in ("noclean", "explor", "script", "dirty", "edited"):
        assert str(out[name]).startswith("refused: REFUSED"), (name, out[name])


# ================================================================================================ F. the template


TEMPLATE = ROOT / "prereg" / "TEMPLATE_family.md"


def _test_globs() -> list[str]:
    """Every glob literal a test file applies (the prereg folder's scans among them)."""
    pats = set()
    for p in (ROOT / "tests").glob("*.py"):
        for m in re.finditer(r"\.r?glob\(\s*f?[\"']([^\"']+)[\"']", p.read_text(encoding="utf-8")):
            pats.add(m.group(1))
    return sorted(pats)


def test_the_template_matches_no_declaration_glob_and_is_no_declaration():
    """The template is no declaration: the reader's grammar (F- or RD-, a number) refuses it, the pin test's regex does
    not read it, and no test's glob for declarations matches it. The scans that read every `prereg/*.md` are seed scans
    (each looks for its own block in the other files); the template carries no seed, so it adds no hit to any."""
    from extended import reader as RD

    name = TEMPLATE.name
    assert TEMPLATE.is_file()
    assert not RD.F_ID.match(name) and not RD.DECLARATION_PATH.fullmatch(f"prereg/{name}")
    assert not re.search(r"(?:F|RD)-\d+", name)
    globs = _test_globs()
    assert "F-*.md" in globs and "*.md" in globs                   # the scan is not vacuous
    matching = [g for g in globs if fnmatch.fnmatch(name, g) or fnmatch.fnmatch(f"prereg/{name}", g)]
    assert set(matching) <= {"*.md", "*", "**/*.md"}, matching
    assert not re.search(r"\b\d{8}\b", TEMPLATE.read_text(encoding="utf-8"))


REQUIRED = (
    "Judged-block reads:", "Seeds -- by role", "by role", "nowhere else", "k_cells", "every cell", "counted",
    "refusals first", "Q-126", "adoption row", "power gate", "before the pin", "Kill", "what a fail means",
    "2026-07-17", "a purchase", "fixed / searched / dropped", "the choice block", "the judged block",
    "2020-01-02", "2023-12-29", "2024-01-02", "2026-07-16", "0.05 / (k (k + 1))", "R* = P-14",
    "E-031", "E-035 (6)", "E-051", "E-052", "E-094 (3)", "E-157 (b)", "E-161", "E-187",
    "K0", "B2", "conjoint MDL", "screen rule", "extended/family_stats.py", "band", "fill intensity",
    "walk-forward", "exploratory", "conduct tier 1", "never deciding",
)


def test_the_template_carries_the_rules():
    text = TEMPLATE.read_text(encoding="utf-8")
    missing = [r for r in REQUIRED if r not in text]
    assert not missing, missing
    assert "\r\n" not in text, "LF text (a pin hashes the LF bytes)"
    # the run order: refusals first, then A0, then run 1, the lead's row, run 2
    order = [text.find(s) for s in ("**Refusals first", "**A0", "**Run 1", "**The lead's row", "**Run 2")]
    assert all(i >= 0 for i in order) and order == sorted(order), order


def test_the_template_types_no_result_number():
    """No figure that could be a result: the only numbers are the declared dates, row ids, levels' formula, section
    numbers and the program's fixed constants named in the rows it cites."""
    text = TEMPLATE.read_text(encoding="utf-8")
    assert not re.search(r"\b0\.\d{3,}\b", text), re.findall(r"\b0\.\d{3,}\b", text)
    assert not re.search(r"\$\s?\d", text.replace("$500", "")), "no dollar figure but the program's bar"
