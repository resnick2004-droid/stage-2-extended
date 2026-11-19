"""Wave 3.2: the three-way test's statistics (`extended/three_way_stats.py`) on synthetic terms and toys with known
answers -- no engine, no bar, no result; fast. Seeds: the tests' role seed of H3's block, `test` keys with this build's
test ids (`three_way_seeds.TEST_IDS`), never the note's own test id.

- **the clips bind** -- a source-(ii) value outside its clip is clipped by the definition; a source-(i) value outside
  its arithmetic bound refuses the whole run before any statistic (M-1); a censored session count's range is
  [0, W + 1] (M-2); the composite's caps clip;
- **admission** -- only unconditional means with an a priori bound are admitted to 2.2 (a); a conditional share, a
  ratio, a tail mean, a quantile and a dimension with neither bound nor clip (M-3) are not;
- **the bound's arithmetic** -- McDiarmid's c_u through the clip and the caps, with nested E_h; for the fallback it is
  Hoeffding's Delta-bar - sqrt(2 ln(1/alpha) / (J |E_63|)); the empirical-Bernstein bound is the note's script's;
- **coverage at a feasible level** -- by seeded simulation at alpha = 0.05: McDiarmid's on independent non-identical
  bounded terms, the empirical-Bernstein and the betting bounds on skewed replicates;
- **a planted edge is detected at the stated power and none is found under the null at the stated size** -- at the
  plant 2.5's formula says has power 0.8 (sd taken at its bound 1), the rejection rate is at least 0.8; under the null
  at most alpha (a binomial allowance);
- **the smaller-J rule** reports both bounds' J and names the one that decides;
- **the nulls' guards**, **the time legs' stated sizes** and vacuity, the **search-years-only** refusal, **the gate at
  H_g = 504** over coin seeds, **O-5's limit check**, and **the history null on S1** (exact on the toys: the swapped
  history's pair is the pair's negative).
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pytest

from extended import three_way_journey as J
from extended import three_way_keys as K
from extended import three_way_s1 as S1
from extended import three_way_seeds as S
from extended import three_way_stats as ST

ROOT = Path(__file__).resolve().parent.parent
ARITH = ROOT / "docs" / "plans" / "scripts" / "three_way" / "three_way_arith.py"
SEED = S.issue("tests")


def rng_for(name: str, replicate: int = 0) -> np.random.Generator:
    return np.random.default_rng(K.seed_key(SEED, "test", test=S.TEST_IDS[name], replicate=replicate))


# ------------------------------------------------------------------------------------------------ the clips


def check_clips_bind() -> None:
    clip = ST.Dimension("net", "mean", 63, a=-500.0, r=1500.0, source="clip", lo=-100.0, hi=400.0, weight=1.0)
    v = clip.values([-2000.0, 0.0, 5000.0])
    assert v.tolist() == [-500.0, 0.0, 1000.0], v
    assert ST.composite([clip], {"net": [-2000.0, -2000.0]}) == 0.0          # the cap clips the normaliser too
    assert ST.composite([clip], {"net": [5000.0, 5000.0]}) == 1.0
    arith = ST.Dimension("share", "mean", 63, a=0.0, r=1.0, source="arithmetic")
    assert arith.values([0.0, 1.0]).tolist() == [0.0, 1.0]
    with pytest.raises(ST.BoundRefused, match="never re-run"):
        arith.values([0.0, 1.5])
    days = ST.session_count("days_to_payout", 126, 126, lo=0.0, hi=127.0)
    assert (days.a, days.r) == (0.0, 127.0)
    assert days.values([127.0]).tolist() == [127.0]                          # the censored value W + 1 admitted
    with pytest.raises(ST.BoundRefused):
        days.values([128.0])


def test_the_clips_bind() -> None:
    check_clips_bind()


def test_admission() -> None:
    assert ST.admission([ST.fallback()])[0]
    for kind in ("conditional", "ratio", "tail", "quantile"):
        ok, why = ST.admission([ST.Dimension("d", kind, 63, a=0, r=1, source="arithmetic")])
        assert not ok and "2.2 (b)" in why[0]
    ok, why = ST.admission([ST.Dimension("dollars", "mean", 63)])
    assert not ok and "M-3" in why[0]
    with pytest.raises(ValueError, match="not admitted"):
        ST.mcdiarmid([ST.Dimension("q", "quantile", 63, a=0, r=1, source="clip")], {"q": np.zeros((2, 2))},
                     {"q": np.zeros((2, 2))}, {"q": [0, 1]}, 0.05)


# ------------------------------------------------------------------------------------------------ the bound's arithmetic


def check_fallback_is_hoeffding() -> None:
    rng = rng_for("bounds_cover")
    xf = rng.integers(0, 4, (50, 8)) / 3.0
    xb = rng.integers(0, 4, (50, 8)) / 3.0
    a = ST.level(13)
    b = ST.mcdiarmid([ST.fallback()], {"P_B": xf}, {"P_B": xb}, {"P_B": range(50)}, a)
    d = xf - xb
    assert b.estimate == pytest.approx(d.mean(), abs=1e-12)
    assert b.lower == pytest.approx(d.mean() - math.sqrt(2 * math.log(1 / a) / d.size), abs=1e-12)
    assert b.lower == pytest.approx(ST.hoeffding_terms(d, a), abs=1e-12)


def test_the_fallback_is_hoeffdings_bound() -> None:
    check_fallback_is_hoeffding()


def test_mcdiarmids_c_u_with_nested_horizons() -> None:
    d1 = ST.Dimension("p", "mean", 63, a=0.0, r=1.0, source="arithmetic", lo=0.1, hi=0.6, weight=0.7)
    d2 = ST.session_count("days", 126, 126, lo=20.0, hi=127.0, weight=0.3)
    J_, s63, s126 = 6, list(range(40)), list(range(25))
    X = {"p": np.full((40, J_), 0.5), "days": np.full((25, J_), 60.0)}
    b = ST.mcdiarmid([d1, d2], X, X, {"p": s63, "days": s126}, 0.01)
    c63 = 0.7 * 2 * 1.0 / (0.5 * J_ * 40)
    c126 = 0.3 * 2 * 127.0 / (107.0 * J_ * 25)
    want = J_ * (25 * (c63 + c126) ** 2 + 15 * c63 ** 2)
    assert b.detail["sum_c2"] == pytest.approx(want, rel=1e-12) and b.estimate == 0.0
    assert b.lower == pytest.approx(-math.sqrt(math.log(100) * want / 2), rel=1e-12)


def test_the_empirical_bernstein_bound_is_the_notes_script() -> None:
    spec = importlib.util.spec_from_file_location("three_way_arith_for_stats", ARITH)
    arith = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arith)
    rng = rng_for("bounds_cover", 1)
    for J_ in (5, 30, 300):
        x = np.clip(rng.normal(0.05, 0.3, J_), -1, 1)
        assert ST.eb_lower(x, 0.01) == pytest.approx(arith.eb_lower(x, 0.01), abs=1e-12)


def check_coverage(reps: int = 2000) -> dict[str, int]:
    """At alpha = 0.05: McDiarmid's bound (the fallback form) on independent non-identical terms; the
    empirical-Bernstein and the betting bounds on heavily skewed replicates. Returns the misses."""
    alpha = 0.05
    rng = rng_for("bounds_cover", 2)
    p = np.linspace(0.05, 0.95, 120).reshape(40, 3)
    mu = float((p - p[::-1]).mean())
    miss = {"mcdiarmid": 0, "eb": 0, "betting": 0}
    for _ in range(reps):
        xf = (rng.random(p.shape) < p).astype(float)
        xb = (rng.random(p.shape) < p[::-1]).astype(float)
        b = ST.mcdiarmid([ST.fallback()], {"P_B": xf}, {"P_B": xb}, {"P_B": range(40)}, alpha)
        miss["mcdiarmid"] += b.lower > mu
    for _ in range(reps // 4):
        D = (rng.random(40) < 0.04).astype(float) * 2.0 - 1.0                # mean -0.92
        miss["eb"] += ST.eb_lower(D, alpha) > -0.92
        miss["betting"] += ST.betting_lower(D, alpha, grid=801) > -0.92
    return miss


def test_the_bounds_cover_at_a_feasible_level() -> None:
    miss = check_coverage()
    assert miss["mcdiarmid"] <= 2000 * 0.05 and miss["eb"] <= 500 * 0.05 and miss["betting"] <= 500 * 0.05, miss


# ------------------------------------------------------------------------------------------------ power


def check_power(reps: int = 300) -> tuple[float, float]:
    """The planted shift 2.5's formula gives power 0.8 at sd 1 (its bound), on terms in [-1, 1] with sd below one:
    (the rejection rate at the plant, the rejection rate under the null), Hoeffding's bound at alpha = 0.05."""
    alpha, n = 0.05, 400
    delta = (math.sqrt(2 * math.log(1 / alpha)) + 0.8416212335729143) / math.sqrt(n)
    rng = rng_for("power")
    rej_plant = rej_null = 0
    for _ in range(reps):
        base = rng.choice([-0.5, 0.5], n)                                     # a symmetric null, sd 0.5
        rej_null += ST.hoeffding_terms(base, alpha) > 0
        rej_plant += ST.hoeffding_terms(np.clip(base + delta, -1, 1), alpha) > 0
    assert ST.hoeffding_units(delta, alpha) <= n
    return rej_plant / reps, rej_null / reps


def test_a_planted_edge_is_found_at_the_stated_power_and_none_under_the_null() -> None:
    power, size = check_power()
    assert power >= 0.8, power
    assert size <= 0.05, size


def test_the_planted_mdl_and_the_smaller_j_rule() -> None:
    rng = rng_for("plant")
    lowers0 = np.array([ST.hoeffding_terms(rng.choice([-0.5, 0.5], 400), 0.05) for _ in range(200)])
    mdl = ST.planted_mdl(lowers0, grid=np.linspace(0.01, 0.5, 50))
    assert 0 < mdl.mdl < 0.5
    out = ST.smaller_j(0.3, 0.3, 0.05, 0.8, (10, 20, 40, 80), rng_for("betting"), reps=60)
    assert set(out["J"]) == {"eb", "betting"} and out["decides"] in ("eb", "betting")
    assert out["J"][out["decides"]] == min(v for v in out["J"].values() if v is not None)


# ------------------------------------------------------------------------------------------------ the nulls' guards


def test_the_null_guards() -> None:
    with pytest.raises(ValueError, match="all zero"):
        ST.null_pool_guards(np.zeros(10))
    rng = rng_for("resample")
    a, b = rng.normal(0, 1, 400), rng.normal(0, 1, 400)
    ST.null_pool_guards(a - b, single_arm_var=1.0)
    with pytest.raises(ValueError, match="tolerance"):
        ST.null_pool_guards(a - b, single_arm_var=0.2)
    lab = ST.size_label(12, 59, 0.05)
    assert lab["label"] == "lax" and ST.size_label(2, 59, 0.05)["label"] == "no laxity detected"


# ------------------------------------------------------------------------------------------------ the time legs


def test_the_time_legs_sizes_and_vacuity() -> None:
    assert ST.white_noise_size([range(0, 10)], 5, 40) == 0.5 and ST.label(0.5) == "VACUOUS"
    assert ST.white_noise_size([range(0, 10), range(20, 30)], 5, 40) == pytest.approx(0.25)
    overlap = ST.white_noise_size([range(0, 10), range(8, 18)], 5, 40)
    assert 0.25 < overlap < 0.5 and ST.label(overlap) == "not vacuous at this bound"
    c = ST.condition({2024: 0.1, 2025: 0.2, 2026: -0.3}, {2024: 252, 2025: 252, 2026: 15}, 21)
    assert c["ok"] == [2024, 2025] and c["holds"]
    assert not ST.condition({2024: 0.1, 2025: -0.2}, {2024: 252, 2025: 252}, 21)["holds"]
    assert ST.regimes([1.0, 3.0], 2.0).tolist() == ["calm", "volatile"]


def test_the_resampled_size_reads_the_search_years_only() -> None:
    days = np.arange(np.datetime64("2020-01-02"), np.datetime64("2020-01-02") + np.timedelta64(600, "D"))
    rng = rng_for("resample", 1)
    contrib = rng.normal(0, 1, 600)
    groups = lambda n: [np.arange(0, 200), np.arange(250, 450)]               # noqa: E731
    out = ST.resampled_size(contrib, days, groups, 63, 63.0, rng, 200)
    assert 0.0 < out["size"] < 1.0 and out["label"] in ("VACUOUS", "not vacuous at this bound")
    assert out["distinct_blocks_median"] >= 2
    with pytest.raises(ValueError, match="held-out"):
        ST.resampled_size(contrib, days + np.timedelta64(1500, "D"), groups, 63, 63.0, rng, 10)
    with pytest.raises(ValueError, match="h\\*"):
        ST.resampled_size(contrib, days, groups, 63, 21.0, rng, 10)


def test_the_gate_at_h_g_and_the_limit_check() -> None:
    spec = importlib.util.spec_from_file_location("three_way_arith_for_gate", ARITH)
    arith = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arith)
    assert ST.H_GATE == arith.H_GATE == 504
    assert ST.complete_starts(663) == arith.complete_starts(663, 504)
    rng = rng_for("gate")
    g = rng.normal(0.05, 0.02, (160, 50))
    out = ST.long_run_gate(g, 0.1, min_starts=100)
    assert out["passes"] and out["starts"] == 160
    assert not ST.long_run_gate(g, 0.1, min_starts=200)["passes"]
    assert not ST.long_run_gate(g - 0.1, 0.1, min_starts=100)["passes"]
    assert ST.limit_check(0.9, 1.0, 0.2)["passes"]                           # inside at the point estimate
    assert not ST.limit_check(1.05, 1.0, 0.2)["passes"]                      # outside at the point estimate
    assert ST.limit_check(1.05, 1.0, 0.2)["evidence_crosses"] is False
    assert not ST.limit_check(1.5, 1.0, 0.2)["passes"]


# ------------------------------------------------------------------------------------------------ the history null


def test_the_history_null_on_s1_is_exact_on_the_toys() -> None:
    rules = J.ToyRules(combine_fee=20, billing=21, target=150, mll=150, dll=None, activation_fee=20, funded_mll=150,
                       win_day=50, payout_days=2, payout_share=0.5, payout_cap=400, split=1.0, payout_lag=1)
    params = S1.S1Params(n_sessions=80, rate=0.4)
    spec = S1.DesignSpec("D", stream="A", fixed_stop=10, rr=1.0, per_session=1)
    passes, thetas = [], []
    for h in range(3):
        hist = S1.generate(SEED, S.PARTS["tests"], h, params)
        D = S1.schedule(spec, hist)
        Dp = S1.schedule(S1.DesignSpec("D'", stream="B", fixed_stop=10, rr=1.0, per_session=1), hist)
        e = lambda sch: J.expect(sch, rules, 0, 63, block_sessions=80, budget=60.0)["p_b"]   # noqa: E731
        theta = e(Dp) - e(D)
        sw = hist.swap()
        theta_sw = e(S1.schedule(S1.DesignSpec("D'", stream="B", fixed_stop=10, rr=1.0, per_session=1), sw)) \
            - e(S1.schedule(spec, sw))
        assert theta_sw == pytest.approx(-theta, abs=1e-12)
        passes.append(theta > 0)
        thetas.append(theta)
    assert any(abs(t) > 1e-6 for t in thetas)                                # the pair differs on a history
    out = ST.fpr_hist(passes, "stylised")
    assert out["pair"] == "stylised" and out["n"] == 3
