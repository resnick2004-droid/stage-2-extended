"""Q-16 section 2: the P comparison's statistics (`extended/p_bound.py`), beside the pass line, never it.

What is asserted:
- a start's ahead average and the judged block, by hand;
- the batch-means t and the overlapping-batch-means (OBM) t by hand; OBM at batch 1 is the iid t;
- the OBM critical values are seeded, cached and above the normal's;
- Stage 2 D-621 (3)(i)'s line as re-implemented here (non-circular moving blocks of 63 starts, 2,000 draws, seed
  20261700, the `level` percentile) equals the vendored `user_journey.block_indices` (in a child process: the vendored
  code is never imported into the test runner) and reproduces `user_journey.csv`'s paired row (P-14 against P-16, the
  share ahead at 63 sessions, all starts: lo and hi) -- the identity of the reference statistic;
- P-14's judged-block P equals every family file's `judged` reference value (`u_budget.csv`, 0.719328);
- the shipped statistic's size on a fixed null (a Gaussian moving average over 21 starts, seed 20261910; 20,000
  replications) at one-sided 1 % and 5 % is inside or below its 99.9 % interval;
- the module offers no conjunction of lines: one statistic, read beside.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extended import p_bound as PB  # noqa: E402
from extended.lift_bound import clopper_pearson  # noqa: E402


def test_ahead_average_by_hand():
    st = pd.DataFrame({"start_date": ["2024-01-02", "2024-01-03", "2024-01-04", "2023-12-29"],
                       "observed": [63, 63, 40, 63],
                       "net_month_1": [10.0, -5.0, 3.0, 1.0], "net_month_2": [0.0, 5.0, 3.0, 1.0],
                       "net_month_3": [1.0, 5.0, 3.0, -1.0]})
    a = PB.ahead_average(st)
    assert a.to_dict() == {"2023-12-29": pytest.approx(2 / 3), "2024-01-02": pytest.approx(2 / 3),
                           "2024-01-03": pytest.approx(2 / 3)}                 # the 40-session start is not eligible
    assert list(PB.judged(a).index) == ["2024-01-02", "2024-01-03"]


def test_batch_t_by_hand():
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 9.0])
    est, se, df = PB.batch_t(x, batches=4)
    m = np.array([1.5, 3.5, 5.5, 8.0])
    assert est == pytest.approx(m.mean()) and se == pytest.approx(m.std(ddof=1) / 2) and df == 3
    X = np.vstack([x, x[::-1]]).T                                            # vectorised over replications
    e2, s2, _ = PB.batch_t(X, batches=4)
    assert e2[0] == pytest.approx(est) and s2[1] == pytest.approx(se)


def test_obm_by_hand_and_at_batch_one():
    rng = np.random.default_rng(20261910)
    x = rng.standard_normal(50)
    m = 7
    est, se = PB.obm(x, m)
    B = np.array([x[j:j + m].mean() for j in range(50 - m + 1)])
    var = 50 * m / ((50 - m + 1) * (50 - m)) * ((B - x.mean()) ** 2).sum()
    assert est == pytest.approx(x.mean()) and se == pytest.approx(math.sqrt(var / 50))
    e1, s1 = PB.obm(x, 1)
    assert s1 == pytest.approx(x.std(ddof=1) / math.sqrt(50))


def test_obm_critical_values():
    c = PB.obm_critical(595, 63, 0.01)
    assert c == PB.obm_critical(595, 63, 0.01)
    assert c > stats.norm.ppf(0.99) and PB.obm_critical(595, 126, 0.01) > c
    assert PB.obm_critical(595, 63, 0.001) > c


def test_stage2_line_indices_equal_the_vendored_ones():
    code = ("import sys; sys.path.insert(0, r'%s'); from extended import use_vendored_stage2; use_vendored_stage2();"
            "import numpy as np; from propedge.research import user_journey as U;"
            "i = U.block_indices(130, 63, draws=50, seed=20261700); print(int(i.sum()), i.shape[0], i.shape[1])"
            % str(ROOT))
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert r.returncode == 0, r.stderr[-2000:]
    mine = PB.stage2_block_indices(130, 63, draws=50, seed=20261700)
    assert r.stdout.split() == [str(int(mine.sum())), "50", "130"]


@pytest.fixture(scope="module")
def starts():
    return PB.load_starts(PB.JOURNEY_FILE)


def test_stage2_line_reproduces_the_registered_paired_row(starts):
    """user_journey.csv section `paired`: P-14 against P-16, verdict arm, `periodic` `share_positive` at 63 sessions,
    all starts: the interval re-derived by this module's re-implementation of the bootstrap."""
    lo, hi, n = PB.paired_row_identity(starts)
    row = PB.registered_paired_row()
    assert n == int(row["n"])
    assert lo == pytest.approx(float(row["lo"]), abs=1e-9) and hi == pytest.approx(float(row["hi"]), abs=1e-9)


def test_p14_judged_p_equals_the_family_files(starts):
    a = PB.judged(starts[("p14", "verdict")])
    assert len(a) == 595 and a.index[0] == "2024-01-02" and a.index[-1] == "2026-04-21"
    assert float(a.mean()) == pytest.approx(PB.registered_p14_judged(), abs=5e-7)


def _ma_null(rng, reps, n=595, q=21):
    e = rng.standard_normal((n + q - 1, reps))
    c = np.cumsum(np.vstack([np.zeros((1, reps)), e]), axis=0)
    return (c[q:] - c[:-q])[:n] / math.sqrt(q)


def test_shipped_statistic_holds_its_size_on_a_fixed_null():
    rng = np.random.default_rng(20261910)
    reps = 20000
    D = _ma_null(rng, reps)
    for a in (0.01, 0.05):
        k = int(PB.rejects(PB.SHIPPED, D, level=a).sum())
        lo, hi = clopper_pearson(int(round(a * reps)), reps, conf=0.999)
        assert k / reps <= hi, f"{PB.SHIPPED} at {a}: {k}/{reps}"


def test_mdd_draws_match_the_power_definition():
    rng = np.random.default_rng(20261911)
    D = _ma_null(rng, 4000) * 0.4
    m = PB.mdd_draws(PB.SHIPPED, D, level=0.01)
    q = float(np.quantile(m, 0.8))
    assert 0.79 <= PB.rejects(PB.SHIPPED, D + q + 1e-12, level=0.01).mean() <= 0.81


def test_flat_top_by_hand():
    rng = np.random.default_rng(20261910)
    x = rng.standard_normal(300)
    est, se = PB.flat_top(x, flat=5, taper=10)
    xc = x - x.mean()
    g = [np.dot(xc[: 300 - k], xc[k:]) / 300 for k in range(10)]
    w = [1.0] * 5 + [(10 - k) / 5 for k in range(6, 10)]                       # lags 1..5 weight 1, 6..9 tapering
    lrv = g[0] + 2 * sum(wk * gk for wk, gk in zip(w, g[1:]))
    assert est == pytest.approx(x.mean()) and se == pytest.approx(math.sqrt(lrv / 300))
    X = np.vstack([x, -x]).T
    e2, s2 = PB.flat_top(X, flat=5, taper=10)
    assert s2[0] == pytest.approx(se) and s2[1] == pytest.approx(se) and e2[1] == pytest.approx(-est)


def test_conservative_fallback_is_the_intersection():
    rng = np.random.default_rng(20261911)
    D = _ma_null(rng, 3000) * 0.4 + 0.12
    for a in (0.01, 0.05):
        both = np.logical_and.reduce([PB.rejects(m, D, level=a) for m in PB.PCONS])
        assert np.array_equal(PB.rejects("pcons", D, level=a), both)


def test_many_levels_equals_the_per_level_functions():
    rng = np.random.default_rng(20261911)
    D = _ma_null(rng, 300) * 0.4 + 0.05
    levels = (0.05 / 132, 0.01, 0.05)
    for m in PB.METHODS:
        rej, mdd = PB.many_levels(m, D, levels)
        for i, a in enumerate(levels):
            assert np.array_equal(rej[i], PB.rejects(m, D, level=a)), m
            assert np.allclose(mdd[i], PB.mdd_draws(m, D, level=a)), m


def test_no_conjunction_is_offered():
    assert not any("conj" in name for name in PB.METHODS)
    assert "d621" in PB.METHODS                                               # the old line, kept as the reference


@pytest.mark.slow
def test_p_calibration_script_runs_small(tmp_path):
    """The P part of the calibration end to end at a tiny size (synthetic nulls; the identities run first)."""
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "q16_calibrate.py"), "--out", str(tmp_path), "--part",
                        "p", "--synthetic-only", "--reps", "2000", "--d621-reps", "1000"],
                       capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    s = pd.read_csv(tmp_path / "p_size.csv")
    assert set(s["method"]) == set(PB.METHODS) | {"bm63c"} and (tmp_path / "p_power.csv").is_file()
    assert (tmp_path / "p_bm63c_critical.csv").is_file()
    meta = json.loads((tmp_path / "calibrate_p.json").read_text(encoding="utf-8"))
    assert meta["p"]["identity"].startswith("HOLDS")


def test_the_shipped_statistic_is_the_conservative_fallback():
    """The calibration's choice (docs/research/calibration_2026-11-15.md section 5.2): `pcons` stands alone; `bm63c` is
    recommended but needs its critical-value table pinned under a decision row."""
    assert PB.SHIPPED == "pcons" and PB.RECOMMENDED == "bm63c"


def test_bm63c_reads_its_critical_values_from_the_calibrations_table(tmp_path):
    p = tmp_path / "p_bm63c_critical.csv"
    pd.DataFrame({"level": [0.01, 0.05], "critical": [4.0, 2.5]}).to_csv(p, index=False)
    table = PB.load_bm63c_critical(p)
    rng = np.random.default_rng([20261911, 9])
    D = _ma_null(rng, 500) * 0.4 + 0.1
    est, se, _ = PB.batch_t(D, batches=595 // 63)
    assert np.array_equal(PB.bm63c_rejects(D, level=0.01, table=table), (est > 0) & (est - 4.0 * se > 0))
    with pytest.raises(KeyError):
        PB.bm63c_rejects(D, level=0.02, table=table)                         # a level the table does not hold
    with pytest.raises(ValueError):
        PB.rejects("bm63c", D, level=0.01)                                    # never without its table
