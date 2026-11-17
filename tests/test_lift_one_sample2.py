"""Q-126 (E-187): `extended/lift_one_sample2.py` -- the grid, scope D's admission with the balance limit, the band check,
the drift generator and the probe's ranking. Synthetic data only; the plan's build seed 20263010 (its 4.1), sub-streams
by test. Fast tier.

What is asserted (the plan's 6.1):
- **the grid**: the members equal `lift_one_sample`'s at m = 1.0, 1.25, 1.5, 1.75 and 2.0 (and C6's), the margin
  multiplies the critical value only, the scalar and vectorised forms agree, `lift_one_sample.py` is unchanged;
- **the nesting in m** on planted samples, at every level and in both scopes;
- **the balance limit**: `admission_b` and `band_b` and the runs intervals equal the plan's arithmetic
  (`q126_arith.py`) at 657 and 1,006 sessions; an exact cell's mean side against a direct count; the enumeration's
  admitted weight against the scalar admission cell by cell; with the limit off, the enumeration is
  `lift_one_sample.exact_flip` exactly; the red team's dominated side admitted without it and refused with it, in the
  scalar, the vectorised and the procedure's counts;
- **the rejecting cells**: they sum, with their weights, to the exact count at k = 13, and their k_max is nested;
- **the band check**: the regime filter's four conditions against `regime_filter_check` (the three gamed sides refused,
  an honest filter passed, the edge-reversal side refused by its spacing) -- and the kind barred by E-187 in
  `band_check`; the dominated side refused in every band; a judged-block mismatch "not claimed"; 2.5's table;
- **the drift generator** equals the plan's Appendix A `draw`, call for call;
- **the probe's ranking**: the 23 largest per size, ties to the smaller j, the core excluded.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

from extended import lift_one_sample as O
from extended import lift_one_sample2 as L2

ROOT = Path(__file__).resolve().parent.parent
SEED = 20263010
ARITH = ROOT / "docs" / "calibration" / "scripts" / "q126" / "q126_arith.py"


def arith():
    name = "q126_arith_for_l2"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ARITH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def plan_text() -> str:
    found = [p for p in (ROOT / "docs" / "calibration").glob("*Q-126_one_sample_plan_2.md")]
    assert len(found) == 1
    return found[0].read_text(encoding="utf-8").replace("\r\n", "\n")


def sample(sub: int, n: int = 657, trades: int = 2000, drift: float = 0.0):
    g = np.random.default_rng([SEED, sub])
    s = np.sort(g.integers(0, n, trades))
    x = np.round(g.choice([-0.5, 0.0, 0.5], trades, p=[0.25 - drift, 0.5, 0.25 + drift]) * 2) / 2
    return x, s


def session_data(sub: int, n: int, *, trades: int = 1500, drift: float = 0.0, traded: float = 0.8):
    g = np.random.default_rng([SEED, sub])
    w = (g.random(n) < traded) * g.gamma(2.0, 1.0, n)
    N = g.multinomial(trades, w / w.sum()).astype(float)
    V = np.zeros(n)
    for j in np.flatnonzero(N):
        u = g.random(int(N[j]))
        V[j] = 0.5 * ((u < 0.25 + drift).sum() - ((u >= 0.25 + drift) & (u < 0.5)).sum())
    return V, N


# ------------------------------------------------------------------------------------------------ the grid


def test_the_grid_and_its_members():
    assert L2.GRID == (1.0, 1.125, 1.25, 1.375, 1.5, 1.75, 2.0)
    assert L2.NAMES == ("cons", "cons_m1.125", "cons_m1.25", "cons_m1.375", "cons_m1.5", "cons_m1.75", "cons_m2",
                        "cons_bm_m1.25")
    assert [c.row for c in L2.CANDIDATES] == list(range(1, 9))
    for name in ("cons", "cons_m1.25", "cons_m1.5", "cons_m1.75", "cons_m2", "cons_bm_m1.25"):
        assert L2.candidate(name).members == O.candidate(name).members, name
    for name, m in (("cons_m1.125", 1.125), ("cons_m1.375", 1.375)):
        assert L2.candidate(name).members == tuple(O.Member("cr1", b, m) for b in (21, 42, 63))
    assert L2.Q_BRANCH == ("cons_m1.5", "cons_m1.75", "cons_m2")
    assert L2.IN_RULE == {(c, "D") for c in L2.NAMES} | {(c, "Q") for c in L2.Q_BRANCH}
    assert L2.NESTED == L2.NAMES[:7]
    assert all(L2.candidate(c).n_members == 3 for c in L2.NAMES)


def test_lift_one_sample_is_unchanged():
    import hashlib

    data = (ROOT / "extended" / "lift_one_sample.py").read_bytes().replace(b"\r\n", b"\n")
    blob = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
    assert blob == "36df2c6f82a60b63213528d5907db082b23c9d6e"          # E-126's build, the blob Q-108's runs ran
    assert O.NAMES == ("cons", "cons_m1.25", "cons_m1.5", "cons_m1.75", "cons_m2", "cons_bm", "cons_bm_m1.25",
                       "cons_im", "sn", "cons_sn")


def test_the_margin_multiplies_the_critical_value_only():
    x, s = sample(1, drift=0.03)
    lv = list(O.FAMILY_LEVELS_1S)
    base = L2.bound_1s_levels("cons", x, s, 657, levels=lv)
    for name in L2.NESTED[1:]:
        m = L2.margin_of(name)
        got = L2.bound_1s_levels(name, x, s, 657, levels=lv)
        for b0, b1 in zip(base, got):
            for m0, m1 in zip(b0.members, b1.members):
                assert (m1.estimate, m1.se, m1.critical, m1.df) == (m0.estimate, m0.se, m0.critical, m0.df)
                assert m1.lower == m1.estimate - (m * m1.critical) * m1.se
    # and the vectorised form agrees with the scalar form, and with lift_one_sample's where the two share a candidate
    from extended import lift_bound as LB

    S, N = LB.session_sums(x, s, 657)
    low = L2.evaluate(S[:, None], N[:, None], O.LEVELS_1S)
    low_o = O.evaluate(S[:, None], N[:, None], O.LEVELS_1S, cands=[O.candidate(c) for c in ("cons", "cons_m1.5",
                                                                                           "cons_bm_m1.25")])
    for name in L2.NAMES:
        sc = L2.bound_1s_levels(name, x, s, 657, levels=O.LEVELS_1S)
        assert np.allclose(low[name][:, 0], [b.lower for b in sc], rtol=0, atol=1e-12), name
    for name in low_o:
        assert np.array_equal(low[name], low_o[name]), name


def test_the_nesting_in_m_on_planted_samples():
    for sub in range(2, 8):
        x, s = sample(sub, trades=800 + 300 * sub, drift=0.01 * sub)
        from extended import lift_bound as LB

        S, N = LB.session_sums(x, s, 657)
        g = np.random.default_rng([SEED, 100 + sub])
        sides = np.where(g.random((657, 400)) < 0.5, -1.0, 1.0)
        low = L2.evaluate(S[:, None] * sides, N[:, None], O.LEVELS_1S)
        adm = L2.admitted_matrix(np.where(N[:, None] > 0, sides, 0), 657)
        for a, b in zip(L2.NESTED, L2.NESTED[1:]):
            ra, rb = low[a] > 0, low[b] > 0
            assert not (rb & ~ra).any(), (a, b)
            assert not ((rb & adm) & ~(ra & adm)).any()
        assert (low["cons"] > 0).any(), "a nesting check with no rejection checks nothing"


# ------------------------------------------------------------------------------------------------ the balance limit


def test_the_balance_limits_and_runs_intervals_are_the_plans():
    A = arith()
    for n in (657, 1006):
        assert float(L2.admission_b(n)) == A.admission_b(n)
        assert L2.admission_b(n).denominator * A.admission_b(n) == pytest.approx(L2.admission_b(n).numerator)
        for band in L2.BANDS:
            assert float(L2.band_b(n, band)) == A.band_b(n, band), (n, band)
            assert L2.runs_interval(n, band) == A.runs_interval(n, band), (n, band)
    assert L2.admission_b(657) == Fraction(437, 657)                  # 0.6651, the plan's 4.4
    assert L2.ADMISSION_RANGE == A.ADMISSION_RANGE and L2.BANDS == A.BANDS and L2.BALANCE_Q == A.BALANCE_Q
    assert float(L2.admission_b(130)) <= 1.0                          # a toy span takes its own n


def test_the_exact_cells_mean_side_against_a_direct_count():
    n = 140
    V, N = session_data(10, n, trades=600, traded=0.6)
    tr = N > 0
    for L in (12, 42, 55):
        Bs, _ = O.flip_cells(n, L)
        g = np.random.default_rng([SEED, 11 + L])
        for p in range(L):
            for q in g.integers(0, 2 ** Bs[p], 5):
                sd = O.flip_cell_sides(n, L, p, int(q))
                s, m = L2.flip_cell_balance(N, L, p, int(q))
                assert s == int(sd[tr].sum()) and m == int(tr.sum())
    # hand-built: three blocks of 5 sessions, traded sessions 3, 0 and 4; pattern q = 0b101 (+, -, +)
    N = np.array([1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 1, 1], dtype=float)
    assert L2.flip_cell_balance(N, 5, 0, 0b101) == (3 + 4, 7)
    assert L2.flip_cell_balance(N, 5, 0, 0b010) == (-7, 7)
    assert L2.flip_cell_balance(N, 5, 0, 0b001) == (3 - 4, 7)


def _brute_admitted(V, N, L, n, balance=True):
    Bs, _ = O.flip_cells(n, L)
    Bmax = max(Bs)
    s = np.repeat(np.arange(n), N.astype(int))
    w = 0
    for p in range(L):
        for q in range(2 ** Bs[p]):
            sd = O.flip_cell_sides(n, L, p, q)
            w += 2 ** (Bmax - Bs[p]) * int(L2.admission2(sd[s], s, n, balance=balance).admitted)
    return w


def test_the_enumerations_admission_against_the_scalar_cell_by_cell(monkeypatch):
    n = 100
    V, N = session_data(12, n, trades=500, traded=0.9)
    assert L2.admission_b(n) > Fraction(9, 10)                        # on a short span the limit barely binds
    for L in (10, 12):
        ex = L2.exact_flip2(V, N, L, cands=["cons"])
        ex0 = L2.exact_flip2(V, N, L, cands=["cons"], balance=False)
        assert ex.admitted == _brute_admitted(V, N, L, n)
        assert ex0.admitted == _brute_admitted(V, N, L, n, balance=False)
    # a planted tighter limit, so that it refuses cells the runs admission admits: both forms still agree
    monkeypatch.setattr(L2, "admission_b", lambda n_: Fraction(1, 4))
    for L in (10, 12):
        ex = L2.exact_flip2(V, N, L, cands=["cons"])
        ex0 = L2.exact_flip2(V, N, L, cands=["cons"], balance=False)
        assert ex.admitted == _brute_admitted(V, N, L, n)
        assert 0 < ex.admitted < ex0.admitted, "the planted limit should refuse some admitted cells"


def test_without_the_limit_the_enumeration_is_q108s():
    for n, L, sub in ((300, 42, 13), (657, 63, 14), (657, 55, 15)):
        V, N = session_data(sub, n, trades=3000, drift=0.03)
        cands_o = [O.candidate(c) for c in ("cons", "cons_m1.25", "cons_m1.5", "cons_bm_m1.25")]
        uni = [0, 7, 100, 513]
        a = O.exact_flip(V, N, L, cands=cands_o, uniform_cells=uni)
        b = L2.exact_flip2(V, N, L, cands=[c.name for c in cands_o], uniform_cells=uni, balance=False)
        assert (a.num, a.den, a.admitted, a.cells, a.samples, a.uniform) == \
            (b.num, b.den, b.admitted, b.cells, b.samples, b.uniform)
        assert sum(a.num[("cons", "Q")]) > 0, "no rejection: the comparison checks nothing"


def dominated_side(n: int = 657, shorts: int = 8) -> np.ndarray:
    s = np.ones(n)
    for i in range(shorts):
        s[int((i + 0.5) * n / shorts)] = -1.0
    return s


def test_the_dominated_side_with_and_without_the_limit():
    s = dominated_side()
    ses = np.arange(657)
    a0 = O.admission(s, ses, 657)
    a1 = L2.admission2(s, ses, 657)
    # the red team's F-1 side (its exact spacing unstated, so E depends on it: the plan cites 9.02 for its own)
    assert a0.runs == 17 and a0.effective >= O.E_MIN and a0.admitted
    assert a1.runs == 17 and not a1.admitted and not a1.balanced and a1.mean_side == pytest.approx(0.9756, abs=1e-4)
    assert L2.admission2(s, ses, 657, balance=False).admitted
    # vectorised, and the procedure's counts on a planted null whose every replication takes that side
    m = np.repeat(s[:, None], 50, axis=1).astype(np.int8)
    assert L2.admitted_matrix(m, 657, balance=False).all() and not L2.admitted_matrix(m, 657).any()
    x, ses_t = sample(20, trades=3000, drift=0.05)
    from extended import lift_bound as LB

    S, N = LB.session_sums(x, ses_t, 657)
    low = L2.evaluate(S[:, None] * np.repeat(s[:, None], 50, axis=1), N[:, None], O.LEVELS_1S)
    rej = low["cons"] > 0
    mm = np.where(N[:, None] > 0, m, 0)
    without = (rej & L2.admitted_matrix(mm, 657, balance=False)[None, :]).sum(axis=1)
    with_ = (rej & L2.admitted_matrix(mm, 657)[None, :]).sum(axis=1)
    assert without[0] == rej[0].sum() > 0 and (with_ == 0).all()
    # an honest switching side (dwell 45) is admitted with the limit
    h = np.array([1.0 if (j // 45) % 2 == 0 else -1.0 for j in range(657)])
    assert L2.admission2(h, ses, 657).admitted


# ------------------------------------------------------------------------------------------------ the rejecting cells


def test_the_rejecting_cells_sum_to_the_exact_count():
    n = 300
    V, N = session_data(30, n, trades=4000, drift=0.08)
    rec = [(c, s) for c in ("cons", "cons_m1.5") for s in ("Q", "D")]
    for L in (42, 55):
        ex = L2.exact_flip2(V, N, L, cands=["cons", "cons_m1.5"], record=rec)
        for key in rec:
            r = ex.records[key]
            assert int((r["weight"]).sum()) == ex.num[key][0], (L, key)
            for i, k in enumerate(O.K_RANGE_1S):
                assert int(r["weight"][r["kmax"] >= k].sum()) == ex.num[key][i], (L, key, k)
            if key[1] == "D":
                assert r["admitted"].all()
        assert ex.num[("cons", "Q")][0] > 0
    for L in (45, 55):
        alt = L2.exact_alternating(V, N, L, cands=["cons", "cons_m1.5"], record=rec)
        for key in rec:
            r = alt.records[key]
            assert len(r["cell"]) == alt.num[key][0] and (r["p"] == r["cell"] // 2).all()
            for i, k in enumerate(O.K_RANGE_1S):
                assert int((r["kmax"] >= k).sum()) == alt.num[key][i]


# ------------------------------------------------------------------------------------------------ the band check


def test_the_regime_filter_conditions_are_the_plans_and_the_kind_is_barred():
    A = arith()
    want = {"one switch, unused points": ["runs floor"], "three fixed regimes": ["runs floor"],
            "two halves with a burst": ["spacing"], "an honest 44-session filter": []}
    for name, (sd, pts) in A.gamed_sides().items():
        got = L2.regime_filter_conditions(sd, pts, "42 to 50")
        assert got == A.regime_filter_check(sd, pts, "42 to 50") == ((not want[name]), want[name]), name
    # the edge-reversal side as a regime filter: refused by its spacing
    n, s = 657, []
    for k in range(3):
        blk = [1 if k % 2 == 0 else -1] * 219
        blk[1] = -blk[0]
        s += blk
    s = np.array(s)
    ch = [j for j in range(1, n) if s[j] != s[j - 1]]
    pts = sorted(set(ch) | set(range(44, n, 44)))
    assert L2.regime_filter_conditions(s, pts, "42 to 50") == (False, ["spacing"])
    for B in range(11, 18):
        assert L2.regime_floor(B) == A.regime_floor(B)
    # E-187: the kind is barred from any family's use, whatever its sides
    honest, hp = A.gamed_sides()["an honest 44-session filter"]
    bc = L2.band_check("regime_filter", "42 to 50", block="choice", n_sessions=657, sides=honest,
                       session=np.arange(657))
    assert not bc.passes and bc.outcome == "barred" and "E-187" in bc.reasons[0]


def test_the_switching_side_check():
    ses = np.arange(657)
    dom = dominated_side()
    for band in L2.BANDS:
        for block in ("judged", "choice"):
            bc = L2.band_check("switching", band, block=block, n_sessions=657, sides=dom, session=ses)
            assert not bc.passes and "balance" in bc.reasons
    bc = L2.band_check("switching", "42 to 50", block="judged", n_sessions=657, sides=dom, session=ses)
    assert bc.outcome == "not claimed"
    bc = L2.band_check("switching", "42 to 50", block="choice", n_sessions=657, sides=dom, session=ses)
    assert bc.outcome == "re-declare before the pin"
    h = np.array([1.0 if (j // 45) % 2 == 0 else -1.0 for j in range(657)])          # 15 runs, balanced
    assert L2.band_check("switching", "42 to 50", block="judged", n_sessions=657, sides=h, session=ses).passes
    bc = L2.band_check("switching", "51 to 62", block="judged", n_sessions=657, sides=h, session=ses)
    assert bc.passes                                                                  # 5 <= 15 <= 22
    bc = L2.band_check("switching", "below 42", block="judged", n_sessions=657, sides=h, session=ses)
    assert bc.passes and bc.details["interval"] == (9, None)
    fast = np.array([1.0 if (j // 10) % 2 == 0 else -1.0 for j in range(657)])       # 66 runs: above 26
    bc = L2.band_check("switching", "42 to 50", block="judged", n_sessions=657, sides=fast, session=ses)
    assert not bc.passes and bc.reasons == ("runs interval",) and bc.outcome == "not claimed"
    # the edge-reversal residual (2.5's F-3): it passes as a switching side in 42 to 50, as the plan states
    s = []
    for k in range(3):
        blk = [1.0 if k % 2 == 0 else -1.0] * 219
        blk[1] = -blk[0]
        s += blk
    assert L2.band_check("switching", "42 to 50", block="judged", n_sessions=657, sides=np.array(s), session=ses).passes
    with pytest.raises(ValueError):
        L2.band_check("switching", "63 or more", block="judged", n_sessions=657, sides=h, session=ses)


def test_which_statistic_a_family_uses():
    S = L2.statistic_for
    assert L2.band_of(30) == "below 42" and L2.band_of(42) == "42 to 50" and L2.band_of(50) == "42 to 50"
    assert L2.band_of(51) == "51 to 62" and L2.band_of(62) == "51 to 62" and L2.band_of(63) is None
    # scope D chose the primary
    assert S(30, "D", second_holds=True) == ("primary", "D")
    assert S(45, "D", second_holds=True) == ("second", "Q")
    assert S(45, "D", second_holds=False) is None                     # never the primary: no switch after a read
    assert S(55, "D", second_holds=True) == ("primary", "D")
    assert S(70, "D", second_holds=True) is None
    assert S(30, "D", primary_holds=False, second_holds=True) is None  # a FAILS is not covered by the other
    # the scope-Q branch is the primary (scope D chose none)
    for p in (10, 45, 60):
        assert S(p, "Q") == ("primary", "Q")
    assert S(63, "Q") is None and S(45, None) is None and S(45, "Q", primary_holds=False) is None


# ------------------------------------------------------------------------------------------------ the drift generator


def appendix_draw():
    body = plan_text()
    app = body[body.index("## Appendix A"):body.index("## Appendix B")]
    code = re.search(r"```python\n(.*?)```", app, re.S).group(1)
    ns = {"np": np, "n": 657}
    exec(compile(code, "appendix_a", "exec"), ns)
    return ns["draw"]


def test_the_drift_generator_is_appendix_as_draw_call_for_call():
    draw = appendix_draw()
    assert L2.DRIFT_SCENARIOS == ((0, "A", 5000, 560, 0.0, False), (1, "B", 5000, 560, 0.01, False),
                                  (2, "C", 5000, 560, 0.02, False), (3, "D", 5000, 560, 0.03, False),
                                  (4, "E", 500, 300, 0.02, False), (5, "F", 5000, 150, 0.0, False),
                                  (6, "G", 5000, 150, 0.02, False), (7, "H", 5000, 560, 0.02, True))
    assert L2.DRIFT_POPULATIONS == 150
    for c, _lab, z, T, d, varying in L2.DRIFT_SCENARIOS:
        for r in (0, 1):
            g1, g2 = np.random.default_rng([SEED, 40, c, r]), np.random.default_rng([SEED, 40, c, r])
            V1, N1 = draw(g1, z, T, d, varying)
            V2, N2 = L2.drift_draw(g2, z, T, d, varying)
            assert np.array_equal(V1, V2) and np.array_equal(N1, N2)
            assert g1.bit_generator.state == g2.bit_generator.state       # the same draws, call for call
            assert N2.sum() == z and (N2 > 0).sum() <= T


# ------------------------------------------------------------------------------------------------ the probe's ranking


def test_the_probe_ranking():
    g = np.random.default_rng([SEED, 50])
    scores = {}
    for z in (200, 5000):
        for j in range(0, 60):
            scores[(z, j)] = Fraction(int(g.integers(0, 6)), 7)
        scores[(z, 3)] = Fraction(99)                                  # a core subset: never ranked
    rk = L2.probe_ranking(scores, per_size=23, core=23)
    for z in (200, 5000):
        js = [j for j, _ in rk[z]]
        assert len(js) == 23 and min(js) >= 23 and 3 not in js
        want = sorted((j for j in range(23, 60)), key=lambda j: (-scores[(z, j)], j))[:23]
        assert js == want
        sc = [s for _, s in rk[z]]
        assert sc == sorted(sc, reverse=True)
        # ties: equal scores in increasing j
        for (j1, s1), (j2, s2) in zip(rk[z], rk[z][1:]):
            assert s1 > s2 or (s1 == s2 and j1 < j2)
