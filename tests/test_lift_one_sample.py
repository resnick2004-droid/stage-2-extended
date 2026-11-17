"""Q-108 (E-115): `extended/lift_one_sample.py` -- the candidates, the admission and the exact enumeration, on synthetic
data only (the plan's 6.1 list). Seeds: 20262110 (the calibration build's tests, the plan's 4.1), sub-streams by test.

What is asserted:
- the constants: k = 13..20 in the module's own `K_RANGE_1S`, `lift_bound.K_RANGE` and its blob untouched; the
  candidates' ids, names, members, margins and table order, C0 outside scope Q;
- each candidate's statistic on a hand-computed toy (two blocks, four trades: every member's estimate, se, df, the
  CR2/BM values and C8's T worked out by hand);
- CR2/BM: CR1 and G' - 1 on equal blocks; the df formula against a direct trace computation (tr A)^2 / tr A^2 on the
  trade-level matrix; the CR2 variance against its trade-level definition;
- the MDL identities: a constant lift moves every bound by itself (so the MDL is minus the bound and the test rejects
  exactly above it), C8's partial sums unchanged by it, an intersection's MDL its members' largest;
- the scalar forms (`bound_1s`, the form a family calls) against the vectorised ones (`evaluate`) on every candidate
  and family level, C0 against the shipped `lift_bound` (vectorised `many_levels` and scalar `bound`);
- exact enumeration: against explicit evaluation of every cell (counts equal, both scopes, at L = 63 and 55), and
  against Monte Carlo on Q-16's `_flip_signs` within the 99.9 % Monte Carlo interval at L = 42, 55 and 63;
- the pattern encoding (bit f set is +1), the flip blocks' phase, the cell order and offsets, the alternating
  convention ((-1)^b on block b, long before short), against hand-built cases;
- C8's reference against a direct order statistic on the same iid draws, and its level on fresh iid data;
- the admission: ties and empty sessions dropped; a single-side series never admitted; a 63-session block-constant
  side never admitted on 657 sessions (every phase, every pattern) nor on 1,006; E >= 4 refusing a run over half the
  non-tie sessions; the re-read's constructed cases (a long side tied on alternate sessions; a long side with a dozen
  brief reversals) refused; the vectorised runs equal the scalar ones; the thresholds 13 and 18;
- the Markov sides' mean dwell and fair first side; the generators take no outcome.
"""
from __future__ import annotations

import importlib.util
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extended import lift_bound as LB  # noqa: E402
from extended import lift_one_sample as O  # noqa: E402

SEED = 20262110


def _rng(i: int) -> np.random.Generator:
    return np.random.default_rng([SEED, i])


def _pseudo(S, N):
    Ni = np.rint(N).astype(np.int64)
    x = np.divide(S, N, out=np.zeros(len(N)), where=Ni > 0)
    return np.repeat(x, Ni), np.repeat(np.arange(len(Ni)), Ni)


def _q16():
    spec = importlib.util.spec_from_file_location("q16_for_t108", ROOT / "scripts" / "q16_calibrate.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["q16_for_t108"] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------------------------------------ the constants


def test_the_range_and_the_candidates():
    assert O.K_RANGE_1S == tuple(range(13, 21))
    assert O.FAMILY_LEVELS_1S == tuple(0.05 / (k * (k + 1)) for k in range(13, 21))
    assert O.EXTRA_LEVELS_1S == (0.001, 0.005, 0.01, 0.025)
    assert LB.K_RANGE == (11, 12, 13, 14, 15)                                  # lift_bound's untouched
    blob = subprocess.run(["git", "hash-object", "extended/lift_bound.py"], cwd=ROOT, capture_output=True,
                          text=True).stdout.strip()
    assert blob == "984f3467a4a05aa790d3ea43e94ac7761f0725b2"
    ids = [c.cid for c in O.CANDIDATES]
    assert ids == [f"C{i}" for i in range(10)]
    assert [c.row for c in O.CANDIDATES] == list(range(10))
    assert O.NAMES == ("cons", "cons_m1.25", "cons_m1.5", "cons_m1.75", "cons_m2", "cons_bm", "cons_bm_m1.25",
                       "cons_im", "sn", "cons_sn")
    assert [c.scope_q for c in O.CANDIDATES] == [False] + [True] * 9               # C0 in scope D only
    mem = {c.name: [m.name for m in c.members] for c in O.CANDIDATES}
    assert mem["cons"] == ["t21w", "t42w", "t63w"]
    assert mem["cons_m1.75"] == ["t21w*1.75", "t42w*1.75", "t63w*1.75"]
    assert mem["cons_bm"] == ["t21bm", "t42bm", "t63bm"]
    assert mem["cons_bm_m1.25"] == ["t21bm*1.25", "t42bm*1.25", "t63bm*1.25"]
    assert mem["cons_im"] == ["t21w", "t42w", "t63w", "t63e"]
    assert mem["sn"] == ["sn"] and mem["cons_sn"] == ["t21w", "t42w", "t63w", "sn"]
    assert [O.candidate(f"C{i}").n_members for i in range(10)] == [3, 3, 3, 3, 3, 3, 3, 4, 1, 4]
    assert O.runs_threshold(657) == 13 and O.runs_threshold(1006) == 18 and O.E_MIN == 4.0


# ------------------------------------------------------------------------------------------------ hand-computed toys


def _toy():
    """126 sessions (21-session blocks: 6; 42: 3; 63: 2). Three trades 0.5, 0.5, -0.5 in sessions 0-2 and one of 0.5
    in session 100: every block scale sees two non-empty blocks with sums 0.5 / 3 trades and 0.5 / 1 trade."""
    x = np.array([0.5, 0.5, -0.5, 0.5])
    s = np.array([0, 1, 2, 100])
    return x, s, 126


def test_each_candidate_on_a_hand_computed_toy():
    x, s, n = _toy()
    a = 0.025
    # by hand: N = 4, est = 1 / 4; u = (0.5 - 0.75, 0.5 - 0.25) = (-0.25, 0.25)
    est = 0.25
    se1 = math.sqrt(2 / 1 * (0.0625 + 0.0625)) / 4                              # CR1: 0.125, df 1
    assert se1 == 0.125
    # CR2: p = (3/4, 1/4), w = (4, 4/3): se^2 = (4 x 0.0625 + 4/3 x 0.0625) / 16
    se2 = math.sqrt((4 * 0.0625 + 4 / 3 * 0.0625) / 16)
    # df_BM = 16 / [(9 + 1) + ((4 x 9 + 4/3 x 1) / 4)^2 - ((4 x 9)^2 + (4/3)^2) / 16] = 16 / 16 = 1
    dfbm = 16 / ((9 + 1) + ((4 * 9 + 4 / 3) / 4) ** 2 - ((4 * 9) ** 2 + (4 / 3) ** 2) / 16)
    assert abs(dfbm - 1.0) < 1e-12
    # t63e: block means 1/6 and 1/2, est 1/3, sd = sqrt(2 (1/6)^2), se = sd / sqrt 2 = 1/6, df 1
    est_e, se_e = 1 / 3, math.sqrt(2 * (1 / 6) ** 2) / math.sqrt(2)
    # C8: U = 0.25, 0.5, -0.25 (x 98 sessions to 99), 0 after; sum U^2 = 0.0625 + 0.25 + 98 x 0.0625
    q = 0.0625 + 0.25 + 98 * 0.0625
    scale = math.sqrt(q / n)
    assert abs(O.sn_statistic(*[v[:, None] for v in LB.session_sums(x, s, n)])[0] - 1.0 / scale) < 1e-12
    c1 = stats.t.ppf(1 - a, 1)
    for name, m in (("cons", 1.0), ("cons_m1.5", 1.5), ("cons_m2", 2.0)):
        b = O.bound_1s(name, x, s, n, level=a)
        for mb in b.members:
            assert abs(mb.estimate - est) < 1e-15 and abs(mb.se - se1) < 1e-15 and mb.df == 1
            assert abs(mb.lower - (est - m * c1 * se1)) < 1e-12
        assert not b.rejects and abs(b.mdl - (m * c1 * se1 - est)) < 1e-12
    for name, m in (("cons_bm", 1.0), ("cons_bm_m1.25", 1.25)):
        b = O.bound_1s(name, x, s, n, level=a)
        for mb in b.members:
            assert abs(mb.se - se2) < 1e-15 and abs(mb.df - dfbm) < 1e-12
            assert abs(mb.lower - (est - m * stats.t.ppf(1 - a, dfbm) * se2)) < 1e-9
    b = O.bound_1s("cons_im", x, s, n, level=a)
    e = [mb for mb in b.members if mb.member == "t63e"][0]
    assert abs(e.estimate - est_e) < 1e-15 and abs(e.se - se_e) < 1e-15 and e.df == 1
    assert abs(b.lower - min(est - c1 * se1, est_e - c1 * se_e)) < 1e-12
    for crit, rejects in ((4.0, True), (5.0, False)):
        sn = {a: crit}
        b = O.bound_1s("sn", x, s, n, level=a, sn_crit=sn)
        assert abs(b.lower - (1.0 - crit * scale) / 4) < 1e-12 and b.rejects is rejects
        b9 = O.bound_1s("cons_sn", x, s, n, level=a, sn_crit=sn)
        assert abs(b9.lower - min(est - c1 * se1, (1.0 - crit * scale) / 4)) < 1e-12 and not b9.rejects


def test_cr2_and_bell_mccaffrey_reduce_to_cr1_on_equal_blocks():
    g = _rng(1)
    for G in (3, 5, 10, 31):
        BN = np.full((G, 1), 7.0)
        BS = g.normal(size=(G, 400))
        est, se1, df1, se2, df2 = O.cr_parts(BS, BN)
        assert np.allclose(se1, se2, rtol=1e-12) and np.all(df1 == G - 1) and np.allclose(df2, G - 1, rtol=1e-12)


def test_bell_mccaffrey_df_and_cr2_against_the_trade_level_definitions():
    """(tr A)^2 / tr A^2 with A = M W M (M centres the trades, W = sum_g w_g c_g c_g'), and se^2 = x' A x / N^2."""
    g = _rng(2)
    for counts in ((5, 1, 3), (2, 2, 9, 1), (1, 8), (4, 4, 4, 4, 1)):
        Nt = sum(counts)
        grp = np.repeat(np.arange(len(counts)), counts)
        x = g.normal(size=Nt)
        M = np.eye(Nt) - np.ones((Nt, Nt)) / Nt
        W = np.zeros((Nt, Nt))
        for k, nk in enumerate(counts):
            c = (grp == k).astype(float)
            W += 1.0 / (1.0 - nk / Nt) * np.outer(c, c)
        A = M @ W @ M
        df_direct = np.trace(A) ** 2 / np.trace(A @ A)
        BS = np.array([[x[grp == k].sum()] for k in range(len(counts))])
        BN = np.array([[float(nk)] for nk in counts])
        _, _, _, se2, df2 = O.cr_parts(BS, BN)
        assert abs(float(df2[0]) - df_direct) < 1e-9 * df_direct, counts
        assert abs(float(se2[0]) ** 2 - x @ A @ x / Nt ** 2) < 1e-12, counts


# ------------------------------------------------------------------------------------------------ MDLs, scalar vs vectorised


def _sample(g, n=657, reps=40, rate=0.8, lift=0.12):
    N = g.poisson(rate, size=(n, reps)).astype(float)
    S = 0.5 * (2 * g.binomial(N.astype(int), 0.5) - N) + lift * N * (np.arange(reps) % 2)[None, :]
    return S, N


def test_the_mdl_identities():
    g = _rng(3)
    S, N = _sample(g, reps=6, rate=2.0, lift=0.03)
    sn = {a: 6.0 + 100 * a for a in O.LEVELS_1S}
    a = O.FAMILY_LEVELS_1S[0]
    for j in range(S.shape[1]):
        x, s = _pseudo(S[:, j], N[:, j])
        for name in O.NAMES:
            b = O.bound_1s(name, x, s, 657, level=a, sn_crit=sn)
            assert math.isfinite(b.mdl)
            for d in (b.mdl + 1e-9, b.mdl - 1e-9):                       # it rejects exactly above its MDL
                b2 = O.bound_1s(name, x + d, s, 657, level=a, sn_crit=sn)
                assert b2.rejects is (d > b.mdl), (name, j)
                assert abs(b2.lower - (b.lower + d)) < 1e-9                # the bound moves by the lift
            assert abs(b.mdl - max(-m.lower for m in b.members)) < 1e-15   # an intersection: its members' largest
        # C8's partial sums are unchanged by a constant lift
        _, _, sc0 = O.sn_parts(S[:, j:j + 1], N[:, j:j + 1])
        _, _, sc1 = O.sn_parts(S[:, j:j + 1] + 0.37 * N[:, j:j + 1], N[:, j:j + 1])
        assert abs(sc0[0] - sc1[0]) < 1e-9


def test_the_scalar_forms_are_the_vectorised_ones():
    g = _rng(4)
    S, N = _sample(g)
    sn = {a: 6.0 + 100 * a for a in O.LEVELS_1S}
    low = O.evaluate(S, N, O.LEVELS_1S, sn_crit=sn)
    some = 0
    for j in range(S.shape[1]):
        x, s = _pseudo(S[:, j], N[:, j])
        for name in O.NAMES:
            bs = O.bound_1s_levels(name, x, s, 657, levels=O.FAMILY_LEVELS_1S, sn_crit=sn)
            for i, b in enumerate(bs):
                v = low[name][i, j]
                assert b.rejects == bool(v > 0), (name, j, i)
                assert (math.isfinite(b.lower) and abs(b.lower - v) < 1e-10) or (not math.isfinite(b.lower)
                                                                                 and v == -np.inf)
                assert b.rejects == O.bound_1s(name, x, s, 657, level=O.FAMILY_LEVELS_1S[i], sn_crit=sn).rejects
                some += b.rejects
    assert 0 < some < 40 * 10 * 8                                             # the comparison is not of one value


def test_c0_is_lift_bounds_cons():
    g = _rng(5)
    S, N = _sample(g, reps=60)
    low = O.evaluate(S, N, O.LEVELS_1S, cands=[O.candidate("cons")])
    rj, md = LB.many_levels("cons", S, N, O.LEVELS_1S)
    assert np.array_equal(rj, low["cons"] > 0) and rj.any()
    fin = np.isfinite(md)
    assert np.array_equal(fin, np.isfinite(low["cons"])) and np.array_equal(md[fin], -low["cons"][fin])
    for j in range(20):
        x, s = _pseudo(S[:, j], N[:, j])
        for a in O.FAMILY_LEVELS_1S[:3]:
            ref = LB.bound("cons", x, s, 657, level=a)
            b = O.bound_1s("cons", x, s, 657, level=a)
            assert ref.rejects == b.rejects and abs(ref.lower - b.lower) < 1e-12
    est, se, df = LB.t_stats(S, N, block=63, weight="equal")
    e2 = O.eq_parts(*O.block_sums(S, N, 63))
    assert np.allclose(est, e2[0], equal_nan=True) and np.allclose(se, e2[1], equal_nan=True)


# ------------------------------------------------------------------------------------------------ the encodings


def test_the_pattern_encoding_cell_order_and_alternating_convention():
    assert O.pattern_signs([5], 3).tolist() == [[1.0, -1.0, 1.0]]               # bit f of q set -> +1
    assert O.pattern_signs([0, 7], 3).tolist() == [[-1, -1, -1], [1, 1, 1]]
    fid, B = O.flip_blocks(10, 4, 2)                                            # (j + p) // L
    assert fid.tolist() == [0, 0, 1, 1, 1, 1, 2, 2, 2, 2] and B == 3
    assert O.flip_cell_sides(10, 4, 2, 5).tolist() == [1, 1, -1, -1, -1, -1, 1, 1, 1, 1]
    Bs, offs = O.flip_cells(10, 4)                                              # phases 0..3: B = 3, 3, 3, 4
    assert Bs == [3, 3, 3, 4] and offs == [0, 8, 16, 24]
    alt = O.alternating_sides(8, 3)                                             # p ascending, long before short
    assert alt.shape == (8, 6)
    assert alt[:, 0].tolist() == [1, 1, 1, -1, -1, -1, 1, 1] and alt[:, 1].tolist() == (-alt[:, 0]).tolist()
    assert alt[:, 2].tolist() == [1, 1, -1, -1, -1, 1, 1, 1]
    assert alt[:, 4].tolist() == [1, -1, -1, -1, 1, 1, 1, -1]
    # Q-16's `_flip_signs` blocks are these: every session of a block shares its sign, B(p) blocks at phase p
    Q16 = _q16()
    g = _rng(6)
    sg = Q16._flip_signs(g, 657, 63, 200)
    for r in range(200):
        diffs = np.flatnonzero(sg[1:, r] != sg[:-1, r]) + 1             # sessions where a new sign starts
        if diffs.size:
            p = (-int(diffs[0])) % 63                                    # the phase that puts a boundary there
            assert all((int(d) + p) % 63 == 0 for d in diffs), r         # every change on a (j + p) // 63 boundary
    Bs63, _ = O.flip_cells(657, 63)
    assert sorted(set(Bs63)) == [11, 12] and Bs63.count(11) == 37 and Bs63.count(12) == 26   # the plan's table


def test_the_exact_sample_records_cells_in_order():
    g = _rng(7)
    n = 300
    N = np.bincount(g.integers(0, n, 900), minlength=n).astype(float)
    V = 0.5 * (2 * g.binomial(N.astype(int), 0.6) - N)
    Bs, offs = O.flip_cells(n, 63)
    total = sum(2 ** b for b in Bs)
    uni = [3, total // 2, total - 1]
    ex = O.exact_flip(V, N, 63, (0.05,), cands=[O.candidate("cons")], n_first=5, uniform_cells=uni, family=1)
    lst = ex.samples[("cons", "Q")]
    assert 0 < len(lst) <= 5 and [c[0] for c in lst] == sorted(c[0] for c in lst)
    for cell, p, q, dec in lst:
        assert cell == offs[p] + q and dec == (True,)
    assert [u[0] for u in ex.uniform] == sorted(uni)
    assert ex.cells == total and ex.den == 63 * 2 ** max(Bs)


# ------------------------------------------------------------------------------------------------ exact enumeration


def test_exact_enumeration_equals_explicit_evaluation():
    """Cell for cell (summed by phase): L = 63 on the judged block's 657 sessions; L = 55 and 42 on a 400-session
    calendar (fewer patterns, the same code)."""
    g = _rng(8)
    sn = {a: 3.0 + 10 * a for a in O.LEVELS_1S}
    for n, L in ((657, 63), (400, 55), (400, 42)):
        N = np.bincount(g.integers(0, n, 2000), minlength=n).astype(float)
        V = 0.5 * (2 * g.binomial(N.astype(int), 0.54) - N)
        ex = O.exact_flip(V, N, L, O.LEVELS_1S, sn_crit=sn)
        Bs, _ = O.flip_cells(n, L)
        Bmax = max(Bs)
        num = {(c, s): np.zeros(len(O.LEVELS_1S), dtype=np.int64) for c in O.NAMES for s in "QD"}
        adm_w = 0
        for p in range(L):
            fid, B = O.flip_blocks(n, L, p)
            sides = O.pattern_signs(np.arange(2 ** B), B)[:, fid].T
            low = O.evaluate(sides * V[:, None], N[:, None], O.LEVELS_1S, sn_crit=sn)
            R, E = O.runs_and_effective(O.session_side_matrix(sides, N > 0))
            adm = O.admits(R, E, n)
            adm_w += 2 ** (Bmax - B) * int(adm.sum())
            for c in O.NAMES:
                r = low[c] > 0
                num[(c, "Q")] += 2 ** (Bmax - B) * r.sum(1)
                num[(c, "D")] += 2 ** (Bmax - B) * (r & adm[None, :]).sum(1)
        for k in num:
            assert list(num[k]) == ex.num[k], (L, k)
        assert adm_w == ex.admitted
        assert any(sum(v) for v in ex.num.values())                          # not a comparison of zeros
        if n == 657 and L == 63:
            assert ex.admitted == 0                                           # 12 blocks at most: never admitted


def test_exact_enumeration_agrees_with_monte_carlo():
    """The plan's 6.1: on the same synthetic subset (drifted, so the sizes are not zero), the exact size lies inside
    the Monte Carlo interval (99.9 %) of Q-16's `_flip_signs` draws, at L = 42, 55 and 63."""
    Q16 = _q16()
    g = _rng(9)
    n = 657
    N = np.bincount(g.integers(0, n, 5000), minlength=n).astype(float)
    V = 0.5 * (2 * g.binomial(N.astype(int), 0.56) - N)                      # long-minus-short drift
    cands = [O.candidate("cons"), O.candidate("cons_m1.25")]
    levels = (0.025, 0.01)
    for i, L in enumerate((42, 55, 63)):
        ex = O.exact_flip(V, N, L, levels, cands=cands, family=1)
        rng = np.random.default_rng([SEED, 100 + i])
        reps, done = 40_000, 0
        cnt = {c.name: np.zeros(len(levels), dtype=np.int64) for c in cands}
        while done < reps:
            sg = Q16._flip_signs(rng, n, L, 10_000)
            low = O.evaluate(V[:, None] * sg, N[:, None], levels, cands=cands)
            for c in cands:
                cnt[c.name] += (low[c.name] > 0).sum(axis=1)
            done += 10_000
        seen = 0
        for c in cands:
            for li in range(len(levels)):
                exact = float(ex.size(c.name, "Q", li))
                lo, hi = LB.clopper_pearson(int(cnt[c.name][li]), reps, conf=0.999)
                assert lo <= exact <= hi, (L, c.name, levels[li], exact, cnt[c.name][li] / reps)
                seen += exact > 0
        assert seen, L


# ------------------------------------------------------------------------------------------------ C8's reference


def test_the_sn_reference_is_its_order_statistic_and_holds_its_level():
    ent = [SEED, 10]
    levels = (0.05, 0.01, 0.001)
    D, batch, n = 100_000, 10_000, 657
    t = O.sn_reference(ent, levels, draws=D, batch=batch, n=n)
    rng = np.random.default_rng(ent)
    T = []
    for _ in range(D // batch):
        Z = rng.standard_normal((n, batch))
        tot = Z.sum(axis=0)
        U = np.cumsum(Z, axis=0) - np.arange(1, n + 1)[:, None] * (tot / n)[None, :]   # a direct form of U_t
        T.append(tot / np.sqrt((U ** 2).mean(axis=0)))
    T = np.sort(np.concatenate(T))
    for a in levels:
        r = int(math.ceil(a * D))
        assert abs(t[a] - T[D - r]) < 1e-9 * abs(T[D - r]), a                 # the ceil(a D)-th largest
    assert O.sn_rank(0.001) == 2000 and O.sn_rank(0.025) == 50000 and O.sn_rank(O.FAMILY_LEVELS_1S[0]) == 550
    # fresh iid data: the rejection rate is the level
    g = _rng(11)
    rej = {a: 0 for a in levels[:2]}
    for _ in range(10):
        Z = g.standard_normal((n, 10_000))
        Tz = O.sn_statistic(Z, np.ones((n, 1)))
        for a in rej:
            rej[a] += int((Tz > t[a]).sum())
    for a, x in rej.items():
        # two binomial errors: the reference's own D draws and the 100,000 fresh ones (4 sd of their difference)
        assert abs(x / 100_000 - a) < 4 * math.sqrt(a * (1 - a) * (1 / D + 1 / 100_000)), (a, x)


# ------------------------------------------------------------------------------------------------ the admission


def test_ties_and_empty_sessions_are_dropped():
    sides = np.array([1, 1, -1, 1, -1, -1, -1, 1])
    session = np.array([0, 0, 1, 1, 3, 3, 5, 5])          # s0 net +2, s1 tie, s2 empty, s3 net -2, s4 empty, s5 tie
    assert O.nontie_series(sides, session, 6).tolist() == [1, -1]
    a = O.admission(sides, session, 6)
    assert a.runs == 2 and a.nontie == 2 and not a.admitted


def test_a_single_side_series_is_never_admitted():
    for n in (657, 1006):
        s = np.arange(n)
        a = O.admission(np.ones(n), s, n)
        assert a.runs == 1 and not a.admitted
        assert not O.admission(-np.ones(n), s, n).admitted
    assert not O.admits(1, 1.0, 657) and not O.admits(0, float("nan"), 657)


def test_a_quarter_constant_side_is_never_admitted():
    """On 657 sessions: every phase, every pattern of a 63-session block-constant side, every session traded."""
    n = 657
    nf_all = np.ones(n)
    for p in range(63):
        fid, B = O.flip_blocks(n, 63, p)
        P = O.pattern_signs(np.arange(2 ** B), B)
        nf = np.bincount(fid, weights=nf_all, minlength=B)
        assert not O._admit_patterns(P, nf, n).any(), p
    # on 1,006 sessions R <= B <= floor(1005 / 63) + 2 = 17 < 18 at every phase; the most runs (alternating) refused
    for p in range(63):
        fid, B = O.flip_blocks(1006, 63, p)
        assert B <= O.runs_threshold(1006) - 1
        alt = np.where(np.arange(B) % 2 == 0, 1.0, -1.0)[fid]
        assert not O.admission(alt, np.arange(1006), 1006).admitted


def test_e_refuses_a_run_over_half_the_sessions():
    # 40 alternating one-session runs (the last short), then one long run of 50: 90 sessions, s = 50/90 > 1/2, R = 41
    m = np.r_[np.where(np.arange(40) % 2 == 0, 1, -1), np.ones(50)]
    R, E = O.runs_of(m)
    assert R == 41 and E < 4 and not O.admits(R, E, 657)
    m2 = np.r_[np.where(np.arange(40) % 2 == 0, 1, -1), np.ones(30)]           # s = 30/70 < 1/2
    R2, E2 = O.runs_of(m2)
    assert E2 >= 4 and O.admits(R2, E2, 657)


def test_the_re_reads_constructed_cases_are_refused():
    n = 657
    # (1) long on every odd session; one long and one short on every even session: never short, ties dropped
    sides, session = [], []
    for j in range(n):
        if j % 2:
            sides.append(1)
            session.append(j)
        else:
            sides += [1, -1]
            session += [j, j]
    a = O.admission(np.array(sides), np.array(session), n)
    assert a.runs == 1 and not a.admitted
    # (2) long for 600 sessions, then twelve one-session reversals: R = 25 (passes 13), E about 1.2 (refused)
    m = np.r_[np.ones(600), np.tile([-1, 1], 12)]
    a = O.admission(m, np.arange(m.size), n)
    assert a.runs == 25 and a.runs >= O.runs_threshold(n) and a.effective < 1.3 and not a.admitted


def test_the_vectorised_runs_are_the_scalar_ones():
    g = _rng(12)
    m = g.choice([-1, 0, 0, 1], size=(300, 400)).astype(np.int8)
    m[:, 0] = 0
    m[:, 1] = 1
    m[:150, 2] = -1
    m[150:, 2] = 1
    R, E = O.runs_and_effective(m)
    for r in range(m.shape[1]):
        R1, E1 = O.runs_of(m[:, r][m[:, r] != 0])
        assert R[r] == R1 and ((math.isnan(E1) and math.isnan(E[r])) or abs(E[r] - E1) < 1e-12), r
    assert R[0] == 0 and R[1] == 1 and R[2] == 2


# ------------------------------------------------------------------------------------------------ the side models


def test_the_markov_and_alternating_sides():
    g = _rng(13)
    for D in (30, 50, 80):
        s = O.markov_sides(g, 657, D, 3000)
        assert set(np.unique(s)) == {-1.0, 1.0}
        assert abs(s[0].mean()) < 4 / math.sqrt(3000)                           # a fair first side (4 sd)
        # the mean dwell D: a reversal at each session boundary with probability 1 / D (4 sd of the binomial rate)
        sw = (s[1:] != s[:-1]).mean()
        assert abs(sw - 1 / D) < 4 * math.sqrt((1 / D) * (1 - 1 / D) / (656 * 3000)), (D, 1 / sw)
    # the generators take no data: the same generator state gives the same sides, whatever is traded
    a = O.markov_sides(np.random.default_rng([SEED, 14]), 657, 50, 10)
    b = O.markov_sides(np.random.default_rng([SEED, 14]), 657, 50, 10)
    assert np.array_equal(a, b)
    alt = O.alternating_sides(657, 55)
    assert alt.shape == (657, 110) and np.array_equal(alt[:, 1::2], -alt[:, 0::2])
