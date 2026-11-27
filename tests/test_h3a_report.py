"""Unit tests for H3-A's report and laxity-stop code (`extended/h3a_report.py`; E-279)."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import binom

from extended import h3a_report as R
from extended import three_way_stats as ST


def _make_clean_54(n: int = 2000) -> list[R.SizeCount]:
    rows = []
    for part, nc, comp, b, lvl in sorted(R.expected_pooled_keys()):
        k = int(round(lvl * n))
        rows.append(R.SizeCount(part=part, null_class=nc, composite=comp, bound=b, level=lvl, rejections=k, n=n))
    return rows


def _k_crit(n: int, level: float, alpha: float = R.STOP_ALPHA_PER_COUNT) -> int:
    """Smallest integer k in 1..n whose exact one-sided binomial tail at p=level is < alpha."""
    for k in range(1, n + 1):
        if float(binom.sf(k - 1, n, level)) < alpha:
            return k
    raise AssertionError("no critical k found")


def test_exact_one_sided_clopper_pearson_matches_binomial_tail_and_exact_boundary() -> None:
    alpha = R.STOP_ALPHA_PER_COUNT
    assert math.isclose(alpha, 0.05 / 54, rel_tol=0.0, abs_tol=1e-15)
    assert R.one_sided_cp_lower(0, 1000, alpha) == 0.0
    for n, k in ((2000, 1), (2000, 20), (2000, 120), (2000, 2000)):
        lo = R.one_sided_cp_lower(k, n, alpha)
        assert 0.0 < lo <= 1.0
        tail = float(binom.sf(k - 1, n, lo))
        assert math.isclose(tail, alpha, rel_tol=1e-9, abs_tol=1e-12), (n, k, lo, tail)

    # Exact boundary kills two-sided (alpha/2), denominator 53, and denominator 1080 mutants!
    for n, lvl in ((1000, 0.05), (2000, 0.05), (2000, 0.01), (2000, 0.001)):
        kc = _k_crit(n, lvl, alpha)
        # k_crit - 1 must NOT be lax; k_crit MUST be lax
        lo_below = R.one_sided_cp_lower(kc - 1, n, alpha)
        lo_at = R.one_sided_cp_lower(kc, n, alpha)
        assert lo_below <= lvl < lo_at, (n, lvl, kc, lo_below, lo_at)
        # Also verify through the stop (stop_on_pooled) (kills denominator 53 and 1080 mutants on evaluate_laxity_stop)
        rows_below = _make_clean_54(n)
        idx = next(i for i, r in enumerate(rows_below) if r.part == "A1" and r.level == lvl)
        c = rows_below[idx]
        rows_below[idx] = R.SizeCount(c.part, c.null_class, c.composite, c.bound, c.level, kc - 1, n)
        assert R.stop_on_pooled(rows_below)["stop_h3d"] is False
        rows_at = list(rows_below)
        rows_at[idx] = R.SizeCount(c.part, c.null_class, c.composite, c.bound, c.level, kc, n)
        res_at = R.stop_on_pooled(rows_at)
        assert res_at["stop_h3d"] is True and res_at["lax_count"] == 1 and res_at["lax_cells"][0]["part"] == "A1"

    # Specifically verify exact boundary between 0.05/54 and 0.05/53 (and two-sided 0.05/108)
    # Find an (n, lvl) where k_crit(0.05/54) != k_crit(0.05/53) or k_crit(0.05/108)
    n_s, lvl_s = 2000, 0.05
    kc_54 = _k_crit(n_s, lvl_s, 0.05 / 54)
    kc_twosided = _k_crit(n_s, lvl_s, 0.05 / 108)
    assert kc_twosided > kc_54, "two-sided critical k must be strictly larger"
    # At kc_54, one-sided 0.05/54 rejects while two-sided 0.05/108 would NOT
    rows = _make_clean_54(n_s)
    idx = next(i for i, r in enumerate(rows) if r.part == "A2" and r.level == lvl_s)
    c = rows[idx]
    rows[idx] = R.SizeCount(c.part, c.null_class, c.composite, c.bound, c.level, kc_54, n_s)
    res = R.stop_on_pooled(rows)
    assert res["stop_h3d"] is True and res["lax_cells"][0]["part"] == "A2"
    # Find an n where denominator 53 differs from 54 (kills denom-53 mutant)
    for n_probe in range(500, 5000):
        k53 = _k_crit(n_probe, 0.05, 0.05 / 53)
        k54 = _k_crit(n_probe, 0.05, 0.05 / 54)
        if k54 > k53:
            rows53 = _make_clean_54(n_probe)
            i53 = next(i for i, r in enumerate(rows53) if r.part == "A1" and r.level == 0.05)
            c53 = rows53[i53]
            rows53[i53] = R.SizeCount(c53.part, c53.null_class, c53.composite, c53.bound, c53.level, k53, n_probe)
            assert R.stop_on_pooled(rows53)["stop_h3d"] is False
            break
    else:
        pytest.fail("no n found distinguishing denom 53 from 54")

    # Find an n where denominator 55 differs from 54 (kills denom-55 mutant M32)
    for n_probe in range(500, 5000):
        k54 = _k_crit(n_probe, 0.05, 0.05 / 54)
        k55 = _k_crit(n_probe, 0.05, 0.05 / 55)
        if k55 > k54:
            rows55 = _make_clean_54(n_probe)
            i55 = next(i for i, r in enumerate(rows55) if r.part == "A1" and r.level == 0.05)
            c55 = rows55[i55]
            rows55[i55] = R.SizeCount(c55.part, c55.null_class, c55.composite, c55.bound, c55.level, k54, n_probe)
            assert R.stop_on_pooled(rows55)["stop_h3d"] is True
            break
    else:
        pytest.fail("no n found distinguishing denom 54 from 55")


def test_clean_54_passes_and_generator_inputs_do_not_exhaust() -> None:
    rows = _make_clean_54(2000)
    res = R.stop_on_pooled(r for r in rows)  # generator input!
    assert res["pooled_total"] == 54
    assert res["a1_pooled"] == 36
    assert res["a2_pooled"] == 18
    assert res["stop_h3d"] is False
    assert res["lax_count"] == 0
    assert res["verdict"] == "PASS_NO_LAXITY"
    assert len(res["pooled_rows"]) == 54

    # 100%-lax generator MUST fail (kills double-iteration exhaustion bug!)
    all_lax = (R.SizeCount(r.part, r.null_class, r.composite, r.bound, r.level, 2000, 2000) for r in rows)
    res_lax = R.stop_on_pooled(all_lax)
    assert res_lax["stop_h3d"] is True and res_lax["lax_count"] == 54 and res_lax["verdict"] == "FAIL_LAXITY_STOP_H3D"


def test_a1_and_a2_single_lax_cells_each_stop_h3d() -> None:
    for target_part in ("A1", "A2"):
        rows = _make_clean_54(2000)
        idx = next(i for i, r in enumerate(rows) if r.part == target_part and r.level == 0.01)
        bad = rows[idx]
        rows[idx] = R.SizeCount(bad.part, bad.null_class, bad.composite, bad.bound, bad.level, 60, 2000)
        res = R.stop_on_pooled(rows)
        assert res["stop_h3d"] is True
        assert res["lax_count"] == 1
        assert res["lax_cells"][0]["part"] == target_part


def test_e052_size_label_is_beside_only_and_never_decides() -> None:
    n, lvl = 2000, 0.05
    k_border = next(
        k for k in range(100, 160)
        if ST.size_label(k, n, lvl)["label"] == "lax" and R.one_sided_cp_lower(k, n, R.STOP_ALPHA_PER_COUNT) <= lvl
    )
    rows = _make_clean_54(n)
    idx = next(i for i, r in enumerate(rows) if r.level == lvl)
    c = rows[idx]
    rows[idx] = R.SizeCount(c.part, c.null_class, c.composite, c.bound, c.level, k_border, n)
    res = R.stop_on_pooled(rows)
    assert res["stop_h3d"] is False
    cell = next(r for r in res["pooled_rows"] if (r["part"], r["null_class"], r["composite"], r["bound"], r["level"])
                == (c.part, c.null_class, c.composite, c.bound, c.level))
    assert cell["beside_e052_label"] == "lax" and cell["stop_lax"] is False


def _declared_inputs(rate_of=None):
    """1080 per-history counts at the declared per-history n (each cell at its level's rate, or `rate_of(cell,
    history, n)` rejections), and the 54 pooled counts their sums."""
    per_n = R.declared_per_history_n()
    hs = R.declared_histories()
    per = []
    for part, nc, comp, b, lvl in sorted(R.expected_pooled_keys()):
        n = per_n[(part, nc)]
        for h in hs[part]:
            k = int(round(lvl * n)) if rate_of is None else rate_of((part, nc, comp, b, lvl), h, n)
            per.append(R.SizeCount(part, nc, comp, b, lvl, k, n, history=h))
    return R.pool_counts(per), per


def test_the_declared_n_and_histories_are_the_declarations_arithmetic() -> None:
    """B-4: the pooled n is R x floor(seeds a side / J') -- 20 x floor(10000 / 100) for the antithetic and exact-centred
    cells, 20 x floor(5000 / 100) for the disjoint cells (the red team's arithmetic) -- and R is Appendix A's."""
    import importlib.util
    from extended import ROOT as repo
    from extended import three_way_h3a as H
    spec = importlib.util.spec_from_file_location("arith_for_h3a_report_test",
                                                  repo / "docs/plans/scripts/three_way/three_way_arith.py")
    A = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(A)
    parts = {name.split()[0]: r_ for name, r_, *_ in A.parts() if name.split()[0] in ("A1", "A2", "A3", "A4")}
    assert parts == R.DECLARED_R == {"A1": 20, "A2": 20, "A3": 200, "A4": 10}
    assert R.declared_pooled_n() == {("A1", "antithetic"): 2000, ("A1", "disjoint"): 1000,
                                     ("A2", "exact_centred"): 2000}
    assert R.declared_pooled_n()[("A1", "antithetic")] == 20 * (H.SEEDS // H.J_PRIME)
    assert R.declared_histories() == {"A1": tuple(range(20)), "A2": tuple(range(20))}
    pooled, per = _declared_inputs()
    assert len(pooled) == 54 and len(per) == 1080 == 36 * 20 + 18 * 20


def test_the_stop_reads_declared_inputs_only_and_per_history_laxity_never_stops() -> None:
    pooled, per = _declared_inputs()
    res = R.evaluate_laxity_stop(pooled, (h for h in per))
    assert res["stop_h3d"] is False and res["per_history_count"] == 1080 and res["verdict"] == "PASS_NO_LAXITY"

    # lax per-history-only cells: one history at 30/100 at level 0.05 in every A1 antithetic cell, the rest at 5/100;
    # each such history cell is labelled lax beside, the pooled 125/2000 is not lax: nothing stops
    def one_lax(cell, h, n):
        part, nc, comp, b, lvl = cell
        if part == "A1" and nc == "antithetic" and lvl == 0.05:
            return 30 if h == 0 else 5
        return int(round(lvl * n))
    pooled1, per1 = _declared_inputs(one_lax)
    res1 = R.evaluate_laxity_stop(pooled1, per1)
    assert res1["stop_h3d"] is False
    lab = [r for r in res1["per_history_beside"] if r["history"] == 0 and r["level"] == 0.05
           and r["null_class"] == "antithetic" and r["part"] == "A1"]
    assert len(lab) == 6 and all(r["beside_e052_label"] == "lax" and r["decides"] is False for r in lab)

    # a lax pooled cell (every history lax in one cell): the stop fires
    def lax_cell(cell, h, n):
        if cell == ("A2", "exact_centred", "toy_composite", "betting", 0.001):
            return 1
        return int(round(cell[4] * n))
    pooled2, per2 = _declared_inputs(lax_cell)
    res2 = R.evaluate_laxity_stop(pooled2, per2)
    assert res2["stop_h3d"] is True and res2["lax_count"] == 1


def test_the_stop_refuses_inputs_not_tied_to_the_declaration() -> None:
    """B-4: mismatched n, mismatched sums, missing or extra per-history rows, a history outside 0 .. R - 1, a
    per-history n off its declared value even with consistent sums, no per-history rows at all, and the red team's
    check 1c (54 pooled cells of n = 5) all refuse."""
    pooled, per = _declared_inputs()
    i = next(j for j, c in enumerate(pooled) if c.null_class == "disjoint")
    c = pooled[i]
    bad_n = list(pooled)
    bad_n[i] = R.SizeCount(c.part, c.null_class, c.composite, c.bound, c.level, c.rejections, c.n + 1)
    with pytest.raises(R.H3ReportRefused, match="declared n"):
        R.evaluate_laxity_stop(bad_n, per)
    bad_k = list(pooled)
    bad_k[i] = R.SizeCount(c.part, c.null_class, c.composite, c.bound, c.level, c.rejections + 1, c.n)
    with pytest.raises(R.H3ReportRefused, match="sum of its"):
        R.evaluate_laxity_stop(bad_k, per)
    with pytest.raises(R.H3ReportRefused, match="every declared cell"):
        R.evaluate_laxity_stop(pooled, per[:-1])
    with pytest.raises(R.H3ReportRefused, match="every declared cell"):
        R.evaluate_laxity_stop(pooled, [])
    x = per[0]
    with pytest.raises(R.H3ReportRefused, match="declared histories"):
        R.evaluate_laxity_stop(pooled, per + [R.SizeCount(x.part, x.null_class, x.composite, x.bound, x.level,
                                                          x.rejections, x.n, history=20)])
    # per-history n off by one in two histories, sums kept
    j0 = next(j for j, h in enumerate(per) if h.history == 0)
    j1 = next(j for j, h in enumerate(per) if h.history == 1 and h.key() == per[j0].key())
    shifted = list(per)
    a, b = per[j0], per[j1]
    shifted[j0] = R.SizeCount(a.part, a.null_class, a.composite, a.bound, a.level, a.rejections, a.n + 1, history=0)
    shifted[j1] = R.SizeCount(b.part, b.null_class, b.composite, b.bound, b.level, b.rejections, b.n - 1, history=1)
    with pytest.raises(R.H3ReportRefused, match="per-history n"):
        R.evaluate_laxity_stop(pooled, shifted)
    tiny = [R.SizeCount(*k, 0, 5) for k in sorted(R.expected_pooled_keys())]
    with pytest.raises(R.H3ReportRefused, match="declared n"):
        R.evaluate_laxity_stop(tiny, per)
    # duplicates and undeclared keys
    with pytest.raises(R.H3ReportRefused, match="duplicate per-history"):
        R.evaluate_laxity_stop(pooled, per + [per[0]])
    bogus = R.SizeCount("A9", "antithetic", "p_b", "bound_22a", 0.05, 5, 100, history=0)
    with pytest.raises(R.H3ReportRefused, match="undeclared per-history"):
        R.evaluate_laxity_stop(pooled, per + [bogus])
    # history=None and invalid per-history counts/bools refused (kills M28)
    with pytest.raises(R.H3ReportRefused, match="history index"):
        R.score_per_history_beside(pooled[0])
    for bad_ph in (
        R.SizeCount("A1", "antithetic", "p_b", "bound_22a", 0.05, -1, 100, history=0),
        R.SizeCount("A1", "antithetic", "p_b", "bound_22a", 0.05, 101, 100, history=0),
        R.SizeCount("A1", "antithetic", "p_b", "bound_22a", 0.05, 0, 0, history=0),
        R.SizeCount("A1", "antithetic", "p_b", "bound_22a", 0.05, 5, 100, history=True),  # type: ignore[arg-type]
    ):
        with pytest.raises(R.H3ReportRefused):
            R.score_per_history_beside(bad_ph)


def test_pool_counts_sums_planted_counts_over_histories() -> None:
    """The one pooling: planted counts on two histories sum exactly (kills `n = n_s` and `k = rej` mutants);
    duplicates and pooled rows refused."""
    rows = [R.SizeCount("A1", "antithetic", "p_b", "eb", 0.05, 3, 100, history=0),
            R.SizeCount("A1", "antithetic", "p_b", "eb", 0.05, 7, 100, history=1),
            R.SizeCount("A1", "disjoint", "p_b", "eb", 0.05, 2, 50, history=1),
            R.SizeCount("A1", "disjoint", "p_b", "eb", 0.05, 0, 50, history=0)]
    got = {c.key(): (c.rejections, c.n) for c in R.pool_counts(rows)}
    assert got == {("A1", "antithetic", "p_b", "eb", 0.05): (10, 200), ("A1", "disjoint", "p_b", "eb", 0.05): (2, 100)}
    with pytest.raises(R.H3ReportRefused, match="duplicate"):
        R.pool_counts(rows + [rows[0]])
    with pytest.raises(R.H3ReportRefused, match="per-history rows only"):
        R.pool_counts([R.SizeCount("A1", "antithetic", "p_b", "eb", 0.05, 3, 100)])


def test_the_eb_range_term_is_printed_beside_the_eb_counts() -> None:
    """m-7: (7 ln(2/alpha) / 3) x 2 / (J' - 1) beside every pooled EB count, nothing beside the other bounds."""
    from extended import three_way_h3a as H
    for lv in R.LEVELS:
        want = (7.0 * math.log(2.0 / lv) / 3.0) * 2.0 / (H.J_PRIME - 1)
        assert math.isclose(R.eb_range_term(H.J_PRIME, lv), want, rel_tol=1e-12)
        row = R.score_pooled_cell(R.SizeCount("A1", "antithetic", "p_b", "eb", lv, 0, 2000))
        assert math.isclose(row["beside_eb_range_term_at_j_prime"], want, rel_tol=1e-12)
        other = R.score_pooled_cell(R.SizeCount("A1", "antithetic", "p_b", "betting", lv, 0, 2000))
        assert math.isnan(other["beside_eb_range_term_at_j_prime"])


def test_the_asymmetric_twin_kill_fires_on_a_centred_skewed_pool() -> None:
    """B-8: a pool centred exactly in mean but skewed (exponential quantiles less their mean) passes centring and
    fires the symmetry kill; a symmetric pool passes both; a pool of mostly zeros is read on its nonzero terms."""
    n = 2000
    q = -np.log(1.0 - (np.arange(n) + 0.5) / n)
    skew = q - q.mean()
    assert R.check_centring(skew)["ok"] is True
    s = R.check_symmetry(skew)
    assert s["ok"] is False and s["abs_z"] > R.H.CENTRING_Z
    sym = np.concatenate([skew, -skew])
    assert R.check_symmetry(sym)["ok"] is True and R.check_centring(sym)["ok"] is True
    assert R.check_symmetry(np.array([0.0, 0.0, 1.0, -1.0]))["n_nonzero"] == 2
    with pytest.raises(R.H3ReportRefused, match="all-zero"):
        R.check_symmetry(np.zeros(5))


def _brute_clipped(dim, p, m):
    """E[clip((K/n - lo)/(hi - lo), 0, 1)] by enumerating every outcome of the m x len(p) indicator units."""
    import itertools
    tot = 0.0
    units = [pt for pt in p for _ in range(m)]
    for bits in itertools.product((0, 1), repeat=len(units)):
        pr = 1.0
        for b_, pt in zip(bits, units):
            pr *= pt if b_ else 1.0 - pt
        tot += pr * min(1.0, max(0.0, (sum(bits) / len(units) - dim.lo) / (dim.hi - dim.lo)))
    return tot


def test_the_clipped_composite_centre_is_exact() -> None:
    """B-2 (c): the indicator's clipped expectation by its Poisson-binomial law equals brute-force enumeration where
    the cap binds (and differs from the clip of the mean there); a dimension whose range lies in its caps is linear; a
    non-indicator whose cap can bind refuses; the composite's centre is the weighted sum of the dimensions'."""
    paid = next(d for d in R.H.TOY_COMPOSITE if d.name == "paid_by_63")
    p = [0.9, 0.5, 0.2]
    for m in (1, 2, 3):
        got = R.clipped_indicator_expectation(paid, p, m)
        assert math.isclose(got, _brute_clipped(paid, p, m), abs_tol=1e-12)
    naive = min(1.0, float(np.mean(p)) / paid.hi)
    assert not math.isclose(R.clipped_indicator_expectation(paid, p, 2), naive, abs_tol=1e-3)
    pb = next(d for d in R.H.TOY_COMPOSITE if d.name == "P_B")
    assert math.isclose(R.clipped_dimension_expectation(pb, [0.2, 0.4], 5), 0.3, abs_tol=1e-15)
    bad = ST.Dimension("y", "mean", 63, a=0.0, r=2.0, source="arithmetic", lo=0.0, hi=1.0)
    with pytest.raises(R.H3ReportRefused, match="no exact centre"):
        R.clipped_dimension_expectation(bad, [0.5], 3)
    sv = next(d for d in R.H.TOY_COMPOSITE if d.name == "sessions_saved_to_payout")
    ef = {"P_B": [0.5, 0.5], "paid_by_63": [0.9, 0.5], "sessions_saved_to_payout": [10.0, 20.0]}
    eb = {"P_B": [0.4, 0.2], "paid_by_63": [0.1, 0.1], "sessions_saved_to_payout": [5.0, 5.0]}
    want = (pb.weight * (0.5 - 0.3) + paid.weight * (R.clipped_indicator_expectation(paid, ef["paid_by_63"], 2)
                                                     - R.clipped_indicator_expectation(paid, eb["paid_by_63"], 2))
            + sv.weight * (15.0 - 5.0) / 64.0)
    assert math.isclose(R.exact_composite_centre(R.H.TOY_COMPOSITE, ef, eb, 2), want, abs_tol=1e-12)


def _toy_values(shift_pb=0.0, shift_saved=0.0, n_starts=4, n_cols=40, saved_mod=30):
    """Deterministic per-unit values on the toy composite's ranges (a lattice, no random draw)."""
    i = np.arange(n_starts)[:, None]
    j = np.arange(n_cols)[None, :]
    pb = ((i + j) % 4) / 3.0
    paid = ((i * 3 + j) % 5 == 0).astype(float)
    saved = ((i * 7 + j * 3) % saved_mod).astype(float)
    xb = {"P_B": pb * 0.5, "paid_by_63": paid, "sessions_saved_to_payout": saved}
    xf = {"P_B": pb * 0.5 + shift_pb, "paid_by_63": paid, "sessions_saved_to_payout": saved + shift_saved}
    return xf, xb


def test_size_counts_count_against_the_centre_and_each_bound_and_composite_apart() -> None:
    """B-2's counting: a rejection is the lower limit above the centre -- f = beta + 0.45 on P_B rejects in every
    2.2 (a) set against zero and nowhere against the centre 0.45; at J' = 100 the EB range term lies below 0.45, so
    EB (and the betting bound) reject against zero and not against the centre; a shift in
    `sessions_saved_to_payout` alone leaves P_B's counts at zero and moves the toy composite's, where the betting
    bound and 2.2 (a)'s reject and EB's range term keeps it from rejecting (each bound's own count: kills a swapped
    key and a composite read from the other's pool)."""
    starts = tuple(range(4))
    xf, xb = _toy_values(shift_pb=0.45)
    c0, _ = R.size_counts(xf, xb, starts, j_prime=20)
    assert all(c0[("p_b", "bound_22a", lv)] == (2, 2) for lv in R.LEVELS)
    cen = {"p_b": {"set": 0.45, "seed": 0.45}, "toy_composite": {"set": 0.225, "seed": 0.225}}
    c1, pools = R.size_counts(xf, xb, starts, j_prime=20, centres=cen)
    assert all(v == (0, 2) for k, v in c1.items() if k[0] == "p_b")
    assert np.allclose(pools["p_b"]["seed"], 0.0)
    xf3, xb3 = _toy_values(shift_pb=0.45, n_cols=200)
    c3, _ = R.size_counts(xf3, xb3, starts, j_prime=100)
    c4, _ = R.size_counts(xf3, xb3, starts, j_prime=100, centres=cen)
    for b in ("eb", "betting"):
        assert c3[("p_b", b, 0.05)] == (2, 2) and c4[("p_b", b, 0.05)] == (0, 2), b
    s16 = tuple(range(16))
    xf2, xb2 = _toy_values(shift_saved=54.0, n_starts=16, n_cols=200, saved_mod=10)
    c2, _ = R.size_counts(xf2, xb2, s16, j_prime=100)
    assert all(c2[("p_b", b, lv)] == (0, 2) for b in R.BOUNDS for lv in R.LEVELS)
    assert c2[("toy_composite", "betting", 0.05)] == (2, 2)
    assert c2[("toy_composite", "eb", 0.05)] == (0, 2)
    assert c2[("toy_composite", "bound_22a", 0.05)] == (2, 2)


def test_size_counts_read_each_bound_at_its_own_centre() -> None:
    """c2 m-1 (C8 to C10): with the set centre and the replicate centre different, 2.2 (a) moves only with the set
    centre and EB and betting only with the replicate centre, and each pool is centred at its own: a constant
    difference of 0.45 at J' = 100 rejects against 0 and not against 0.45."""
    starts = tuple(range(4))
    xf, xb = _toy_values(shift_pb=0.45, n_cols=200)
    c1, p1 = R.size_counts(xf, xb, starts, j_prime=100,
                           centres={"p_b": {"set": 0.0, "seed": 0.45}, "toy_composite": {"set": 0.0, "seed": 0.225}})
    assert c1[("p_b", "bound_22a", 0.05)] == (2, 2)
    assert c1[("p_b", "eb", 0.05)] == (0, 2) and c1[("p_b", "betting", 0.05)] == (0, 2)
    assert np.allclose(p1["p_b"]["seed"], 0.0) and np.allclose(p1["p_b"]["set"], 0.45)
    c2, p2 = R.size_counts(xf, xb, starts, j_prime=100,
                           centres={"p_b": {"set": 0.45, "seed": 0.0}, "toy_composite": {"set": 0.225, "seed": 0.0}})
    assert c2[("p_b", "bound_22a", 0.05)] == (0, 2)
    assert c2[("p_b", "eb", 0.05)] == (2, 2) and c2[("p_b", "betting", 0.05)] == (2, 2)
    assert np.allclose(p2["p_b"]["seed"], 0.45) and np.allclose(p2["p_b"]["set"], 0.0)


def test_the_lag1_autocorrelation_beside() -> None:
    """c2 m-10: alternating signs give lag-1 autocorrelation near -1, a slow ramp near +1, a constant pool NaN."""
    alt = np.tile([1.0, -1.0], 50)
    assert R.lag1_autocorrelation(alt) < -0.95
    assert R.lag1_autocorrelation(np.linspace(-1, 1, 100)) > 0.95
    assert math.isnan(R.lag1_autocorrelation(np.ones(10))) and math.isnan(R.lag1_autocorrelation([1.0, 2.0]))


def test_a4_and_a3_counts_and_summaries() -> None:
    """Section 8's 426 pass-rate cells and 60 MDL lines are derived from the declared grids; A4's summary pools
    every cell under every history and gives the known MDL; A3's gives 6 rates; both refuse a missing history."""
    from extended import three_way_h3a as H
    cells = R.a4_cells()
    assert len(cells) == 426 and len(R.a4_mdl_lines()) == 60
    assert sum(c[0] == "P1" for c in cells) == 30 and sum(c[0] == "P2" for c in cells) == 54
    assert sum(c[0] == "P3" for c in cells) == 72 and sum(c[0] == "P4" for c in cells) == 270
    hs = (0, 1)
    draws = 4
    lowers = [{"history": h, "draw": d, "bound": b, "level": lv, "lower0": -0.006}
              for h in hs for d in range(draws) for b in ("bound_22a", "eb") for lv in R.LEVELS]

    def passes(cell):
        plant, param = cell[0], cell[1]
        d = float(param.split("=")[-1]) if plant in ("P1", "P4") else 0.0
        return draws if (plant in ("P1", "P4") and d > 0.006) else 0
    rows = [{"history": h, "plant": c[0], "param": c[1], "composite": c[2], "bound": c[3], "level": c[4],
             "passes": passes(c), "draws": draws, "true_delta": 0.0} for h in hs for c in cells]
    rates, mdls = R.summarise_a4(rows, lowers, histories=hs)
    assert len(rates) == 426 and len(mdls) == 60
    assert all(m["mdl_grid"] == 0.01 for m in mdls)
    with pytest.raises(R.H3ReportRefused, match="every cell under every history"):
        R.summarise_a4(rows[:-1], lowers, histories=hs)
    with pytest.raises(R.H3ReportRefused, match="linear form"):
        R.summarise_a4(rows, [dict(x, lower0=-0.001) for x in lowers], histories=hs)

    a3 = [{"history": h, "composite": c, "level": lv, "pass_prob": 0.1 * (h + 1), "full_passes": 1, "full_draws": 4}
          for h in hs for c in R.COMPOSITES for lv in R.LEVELS]
    out = R.summarise_a3(a3, histories=hs, shortcut=(0,))
    assert len(out) == 6 and all(math.isclose(o["fpr_hist"], 0.15) and o["pair"] == "stylised" for o in out)
    assert all(math.isclose(o["shortcut_error_mean_beside"], 0.1 - 0.25) for o in out)
    with pytest.raises(R.H3ReportRefused, match="histories"):
        R.summarise_a3(a3[:-1], histories=hs, shortcut=(0,))
    assert len(H.SHORTCUT_HISTORIES) == 5


def test_verify_inputs_refuses_dirty_mixed_unverified_and_stale_inputs(tmp_path: Path) -> None:
    """m-5: an input that does not verify, one written dirty, inputs from two commits, and a commit whose build or
    report files differ from HEAD's all refuse; clean inputs of HEAD's commit pass (when this tree's files are
    HEAD's)."""
    import subprocess
    from extended import ROOT as repo
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()
    files = []
    for i in range(2):
        f = tmp_path / f"x{i}.csv"
        f.write_text("a\n1\n", encoding="utf-8")
        files.append(f)
    man = {f: {"git_commit": head, "git_dirty": False} for f in files}

    def ok(p):
        return True, "ok"
    same_as_head = subprocess.run(["git", "-C", str(repo), "diff", "--quiet", head, "HEAD", "--", *R.H3_BUILD_FILES,
                                   *R.REPORT_FILES]).returncode == 0
    assert same_as_head
    assert R.verify_inputs(files, verify=ok, root=repo, read_manifest=lambda p: man[p]) == head
    with pytest.raises(R.H3ReportRefused, match="does not verify"):
        R.verify_inputs(files, verify=lambda p: (False, "sha"), root=repo, read_manifest=lambda p: man[p])
    with pytest.raises(R.H3ReportRefused, match="clean tree"):
        R.verify_inputs(files, verify=ok, root=repo, read_manifest=lambda p: {**man[p], "git_dirty": True})
    two = {files[0]: man[files[0]], files[1]: {"git_commit": R.H3_BUILD_COMMIT, "git_dirty": False}}
    with pytest.raises(R.H3ReportRefused, match="2 commits"):
        R.verify_inputs(files, verify=ok, root=repo, read_manifest=lambda p: two[p])
    old = {f: {"git_commit": R.H3_BUILD_COMMIT, "git_dirty": False} for f in files}
    with pytest.raises(R.H3ReportRefused, match="differ"):
        R.verify_inputs(files, verify=ok, root=repo, read_manifest=lambda p: old[p])


def test_refuses_missing_extra_duplicate_and_invalid_inputs() -> None:
    rows = _make_clean_54(2000)
    with pytest.raises(R.H3ReportRefused, match="exact 54"):
        R.stop_on_pooled(rows[:-1])
    extra = R.SizeCount("A2", "antithetic", "p_b", "bound_22a", 0.05, 5, 100)
    with pytest.raises(R.H3ReportRefused, match="exact 54"):
        R.stop_on_pooled(rows + [extra])
    with pytest.raises(R.H3ReportRefused, match="duplicate"):
        R.stop_on_pooled(rows + [rows[0]])
    with pytest.raises(R.H3ReportRefused, match="per-history"):
        R.stop_on_pooled([R.SizeCount("A1", "antithetic", "p_b", "bound_22a", 0.05, 5, 100, history=0)])

    # Invalid counts, bools, floats, NaN level, bad alpha
    for args in ((-1, 100), (101, 100), (0, 0), (True, 100), (10, False), (10.5, 100)):
        with pytest.raises(R.H3ReportRefused):
            R.one_sided_cp_lower(args[0], args[1])  # type: ignore[arg-type]
    for bad_a in (0.0, 1.0, -0.1, float("nan"), float("inf")):
        with pytest.raises(R.H3ReportRefused):
            R.one_sided_cp_lower(5, 100, bad_a)
    with pytest.raises(R.H3ReportRefused):
        R.score_pooled_cell(R.SizeCount("A1", "antithetic", "p_b", "bound_22a", float("nan"), 100, 100))


def test_centring_and_null_pool_guards_two_sided_and_degenerate() -> None:
    # Deterministic centred pool with exact mean=0, sd=1
    base = np.tile(np.array([-1.0, 1.0]), 50)
    assert R.check_null_pool(base)["ok"] is True

    # Two-sided boundary around CENTRING_Z = 4.0 (positive AND negative!)
    n = base.size
    sd = float(base.std(ddof=1))
    se = sd / math.sqrt(n)
    assert R.check_null_pool(base + 3.9 * se)["ok"] is True
    assert R.check_null_pool(base - 3.9 * se)["ok"] is True
    assert R.check_null_pool(base + 4.1 * se)["ok"] is False
    assert R.check_null_pool(base - 4.1 * se)["ok"] is False

    # Degenerate / non-finite / bad variance pools refused
    with pytest.raises(R.H3ReportRefused, match="zero"):
        R.check_null_pool(np.zeros(20))
    with pytest.raises(R.H3ReportRefused, match="zero-variance"):
        R.check_null_pool(np.ones(20))
    with pytest.raises(R.H3ReportRefused, match="finite"):
        R.check_null_pool(np.array([1.0, float("nan"), -1.0]))
    with pytest.raises(R.H3ReportRefused, match="tolerance"):
        R.check_null_pool(base, single_arm_var=10.0, var_tol=0.5)
    with pytest.raises(R.H3ReportRefused, match="z_max"):
        R.check_centring(base, z_max=0.0)
    for bad_vt in (float("nan"), -0.1, True):
        with pytest.raises(R.H3ReportRefused, match="var_tol"):
            R.check_null_pool(base, single_arm_var=0.5, var_tol=bad_vt)  # type: ignore[arg-type]


def test_preconditions_positive_and_negative_controls(tmp_path: Path) -> None:
    from extended import ROOT as repo

    # Build a valid synthetic repo with H3's real bytes + valid pinned template v3
    (tmp_path / "prereg").mkdir()
    h3_bytes = (repo / R.H3_DECL_PATH).read_bytes()
    (tmp_path / R.H3_DECL_PATH).write_bytes(h3_bytes)
    tpl_body = (
        "# Template v3\n\n"
        "## 5. The zero-edge convention\n\n"
        "**R-10: the redraw for a trade that ends at a time limit**\n"
        + "\n".join(R.R10_CLAUSES) + "\n\n"
        "## 6. Next section\n"
    )
    tpl_path = tmp_path / "prereg" / "TEMPLATE_design_search.md"
    tpl_path.write_text(tpl_body, encoding="utf-8", newline="\n")
    tpl_sha = hashlib.sha256(tpl_body.encode("utf-8")).hexdigest()
    dec = tmp_path / "DECISIONS.md"
    good_dec = (
        f"| E-279 | 2026-11-22 | `{R.H3_DECL_PATH}` sha256 `{R.H3_PIN_SHA256}` | b |\n"
        f"| E-284 | 2026-11-23 | `prereg/TEMPLATE_design_search.md` sha256 `{tpl_sha}` | b |\n"
    )
    dec.write_text(good_dec, encoding="utf-8", newline="\n")

    # Positive control passes
    info = R.assert_h3_preconditions(tmp_path)
    assert info["h3_sha256"] == R.H3_PIN_SHA256 and info["template_sha256"] == tpl_sha

    # Negative 1: H3 pin missing from DECISIONS.md
    dec.write_text(f"| E-284 | 2026-11-23 | `prereg/TEMPLATE_design_search.md` sha256 `{tpl_sha}` | b |\n",
                   encoding="utf-8")
    with pytest.raises(R.H3ReportRefused, match="H3 pin"):
        R.assert_h3_preconditions(tmp_path)

    # Negative 2: template pin missing from DECISIONS.md
    dec.write_text(f"| E-279 | 2026-11-22 | `{R.H3_DECL_PATH}` sha256 `{R.H3_PIN_SHA256}` | b |\n",
                   encoding="utf-8")
    with pytest.raises(R.H3ReportRefused, match="template v3 hash row"):
        R.assert_h3_preconditions(tmp_path)

    # Negative 3: template sha256 mismatch
    dec.write_text(good_dec.replace(tpl_sha, "0" * 64), encoding="utf-8")
    with pytest.raises(R.H3ReportRefused, match="LF sha256"):
        R.assert_h3_preconditions(tmp_path)

    # Negative 4: missing R-10 clause (even when hash matches!)
    bad_tpl = tpl_body.replace(R.R10_CLAUSES[0], "removed clause")
    tpl_path.write_text(bad_tpl, encoding="utf-8", newline="\n")
    bad_tpl_sha = hashlib.sha256(bad_tpl.encode("utf-8")).hexdigest()
    dec.write_text(good_dec.replace(tpl_sha, bad_tpl_sha), encoding="utf-8")
    with pytest.raises(R.H3ReportRefused, match="pinned R-10 disagrees"):
        R.assert_h3_preconditions(tmp_path)

    # Negative 5: section 6 before section 5 (kills M22)
    flipped_tpl = (
        "# Template v3\n\n## 6. Early\n\n## 5. The zero-edge convention\n\n"
        "**R-10: the redraw for a trade that ends at a time limit**\n" + "\n".join(R.R10_CLAUSES) + "\n"
    )
    tpl_path.write_text(flipped_tpl, encoding="utf-8", newline="\n")
    fl_sha = hashlib.sha256(flipped_tpl.encode("utf-8")).hexdigest()
    dec.write_text(good_dec.replace(tpl_sha, fl_sha), encoding="utf-8")
    with pytest.raises(R.H3ReportRefused, match="section 6 heading after section 5"):
        R.assert_h3_preconditions(tmp_path)

    # Negative 6: check_build_commit=True fails in non-git / missing-ancestor repo (kills M23)
    tpl_path.write_text(tpl_body, encoding="utf-8", newline="\n")
    dec.write_text(good_dec, encoding="utf-8")
    with pytest.raises(R.H3ReportRefused, match="ancestor"):
        R.assert_h3_preconditions(tmp_path, check_build_commit=True)

    # Negative 7: H3 file tampered
    (tmp_path / R.H3_DECL_PATH).write_text("tampered\n", encoding="utf-8")
    with pytest.raises(R.H3ReportRefused, match="LF sha256"):
        R.assert_h3_preconditions(tmp_path)


def test_h3_probe_runtime_gates(tmp_path: Path) -> None:
    """Run h3_probe._check_runtime_gates in a child process (avoids importing extended.results in the test runner, Q-204)."""
    import os
    import subprocess
    import sys
    import textwrap
    from extended import ROOT as repo

    probe_path = Path(__file__).resolve().parent / "h3_probe.py"
    if not probe_path.is_file():
        probe_path = repo / "scripts" / "h3_probe.py"
    h3a_path = Path(__file__).resolve().parent / "h3a_report.py"
    code = textwrap.dedent(f"""
        import importlib.util, json, os, sys
        from pathlib import Path
        sys.path.insert(0, {str(repo)!r})
        if {str(h3a_path)!r} and Path({str(h3a_path)!r}).is_file() and not (Path({str(repo)!r}) / "extended" / "h3a_report.py").is_file():
            s = importlib.util.spec_from_file_location("extended.h3a_report", {str(h3a_path)!r})
            m = importlib.util.module_from_spec(s)
            sys.modules["extended.h3a_report"] = m
            s.loader.exec_module(m)
            import extended; extended.h3a_report = m
        from extended import h3a_report as R, lock_guard as LG, results as RES
        spec = importlib.util.spec_from_file_location("h3_probe_gate_test", {str(probe_path)!r})
        P = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(P)

        tmp = Path({str(tmp_path)!r})
        mroot, rdir = tmp / "main", tmp / "results"
        mroot.mkdir(); rdir.mkdir()
        LG.main_root = lambda _start=None: mroot
        RES.clean_run_problem = lambda: None
        os.environ["S2X_LOCK_HOLDER"] = "h3-0-probe"

        def expect_refuse(pat):
            try:
                P._check_runtime_gates(root=mroot, results_dir=rdir)
            except R.H3ReportRefused as exc:
                assert pat in str(exc), f"expected {{pat!r}} in {{exc}}"
                return
            raise AssertionError(f"expected H3ReportRefused matching {{pat!r}}")

        expect_refuse("run.lock not found")
        (mroot / LG.LOCK_NAME).write_text("[1, 2, 3]\\n", encoding="utf-8")
        expect_refuse("malformed")
        (mroot / LG.LOCK_NAME).write_text(json.dumps({{"job": "other-job"}}), encoding="utf-8")
        expect_refuse("S2X_LOCK_HOLDER")
        (mroot / LG.LOCK_NAME).write_text(json.dumps({{"job": "h3-0-probe"}}), encoding="utf-8")
        P._check_runtime_gates(root=mroot, results_dir=rdir)
        (rdir / f"{{P.OUTPUT_NAME}}.csv").write_text("x\\n", encoding="utf-8")
        expect_refuse("already exists")
        RES.clean_run_problem = lambda: "dirty tree"
        expect_refuse("clean run")
        print("OK")
    """)
    env = dict(os.environ, OMP_NUM_THREADS="1")
    r = subprocess.run([sys.executable, "-c", code], cwd=repo, capture_output=True, text=True, env=env, timeout=60)
    assert r.returncode == 0 and r.stdout.strip().endswith("OK"), (r.returncode, r.stdout, r.stderr)
