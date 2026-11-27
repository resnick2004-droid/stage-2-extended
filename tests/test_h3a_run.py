"""Synthetic unit tests for `scripts/h3a_run.py` (E-279, E-285; the red team's BUILD_H3A_REPORT_2026-11-27).

**Seeds (B-3):** every draw here is the tests' seed in the tests' part (`three_way_seeds.issue("tests")`,
`PARTS["tests"]`), passed to the runner as its role and part; H3-A's declared roles appear only in the test that shows
they are refused outside a clean run, before any draw. Tiny S1 toys only; never reads bars or writes `results/`
(records go to an in-memory sink or a temporary folder). The clean-run gate test runs in a subprocess so
`extended.results` is never imported in the fast-tier process (Q-204).
"""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from extended import CLEAN_RUN_ENV
from extended import h3a_report as REP
from extended import three_way_h3a as H
from extended import three_way_journey as J
from extended import three_way_runner as R
from extended import three_way_s1 as S1
from extended import three_way_seeds as S
from scripts import h3a_run as HR

ROOT = Path(__file__).resolve().parent.parent
TP = S.PARTS["tests"]
ROLES = ("tests", "tests")
#: A1, A3, A4's tiny S1 (a regime, a stream rate high enough for trades on every start) and A2's (the exact program's
#: settings, as `S1_PARAMS_EXACT`: no regime, the low rate that keeps its states few)
TINY = S1.S1Params(n_sessions=75, vol_mean=6.0, phi=0.9, vol_sd=0.15, regime_amp=0.2, rate=1.0, rate_beta=1.0,
                   hold_mean=25.0, hold_stop=40.0, time_limit=90.0)
TINY_X = S1.S1Params(n_sessions=75, vol_mean=6.0, phi=0.9, vol_sd=0.15, regime_amp=0.0, rate=0.3, rate_beta=1.0,
                     hold_mean=30.0, hold_stop=40.0, time_limit=90.0)
STARTS = (0, 1, 2, 3)
M, JP = 400, 20
DISJ = ((0, 200), (200, 400))
BIG = 1e9                      # the memory cap in these tests: the pytest process's own peak is not a worker's


class Store:
    def __init__(self):
        self.files: dict[str, tuple[pd.DataFrame, dict]] = {}

    def __call__(self, df, name, description, parameters):
        assert name not in self.files, f"{name} written twice"
        self.files[name] = (df.copy(), dict(parameters))

    def to_dir(self, d: Path) -> None:
        for name, (df, _) in self.files.items():
            df.to_csv(d / f"{name}.csv", index=False)


@pytest.fixture(scope="module")
def a1():
    st = Store()
    res = HR.run_a1(part_id=TP, roles=ROLES, sink=st, histories=(0, 1), M=M, starts=STARTS, j_prime=JP, disjoint=DISJ,
                    s1_params=TINY, rules=H.TOY_RULES_EXACT, workers=1, cap_mb=BIG)
    return st, res


@pytest.fixture(scope="module")
def a2():
    st = Store()
    res = HR.run_a2(part_id=TP, roles=ROLES, sink=st, histories=(0, 1), M=M, starts=STARTS, j_prime=JP,
                    s1_params=TINY_X, workers=1, cap_mb=BIG)
    return st, res


def _sum_per_history(st: Store, prefix: str, hs) -> dict:
    """The pooled counts recomputed here, independently of the runner: each cell's per-history sums."""
    df = pd.concat([st.files[f"{prefix}_h{h:03d}"][0] for h in hs])
    g = df.groupby(["part", "null_class", "composite", "bound", "level"])[["rejections", "n"]].sum()
    return {k: (int(v["rejections"]), int(v["n"])) for k, v in g.iterrows()}


def test_a1_writes_each_history_and_pools_their_sums(a1) -> None:
    """B-1 and B-4: one file a history, the premise table and the pooled file; 36 cells a history at its own n
    (floor(400 / 20) antithetic, floor(200 / 20) disjoint); every pooled count the sum of the two histories' (kills
    a pooled n of one history, `acc[1] = n_s`, and `acc[0] = rej`); the failures at the fill of both arms (m-6); the
    worker's peak recorded; every premise holding."""
    st, res = a1
    assert set(st.files) == {"h3a_a1_h000", "h3a_a1_h001", "h3a_a1_premises", "h3a_a1"}
    for h in (0, 1):
        df = st.files[f"h3a_a1_h{h:03d}"][0]
        assert len(df) == 36 and set(df["history"]) == {h}
        assert set(df.loc[df["null_class"] == "antithetic", "n"]) == {M // JP}
        assert set(df.loc[df["null_class"] == "disjoint", "n"]) == {(DISJ[0][1] - DISJ[0][0]) // JP}
        assert "beside_eb_range_term_at_j_prime" in df.columns
    pooled = st.files["h3a_a1"][0]
    assert len(pooled) == 36 == REP.A1_POOLED_TOTAL
    want = _sum_per_history(st, "h3a_a1", (0, 1))
    got = {(r["part"], r["null_class"], r["composite"], r["bound"], float(r["level"])): (int(r["rejections"]),
                                                                                          int(r["n"]))
           for _, r in pooled.iterrows()}
    assert got == want
    assert all(n == 2 * (M // JP if k[1] == "antithetic" else 200 // JP) for k, (_, n) in got.items())
    prem = st.files["h3a_a1_premises"][0]
    assert len(prem) == 2 * (1 + 2 * 8) and prem["ok"].all()
    assert set(prem["check"]) == {"twin_uniforms", "centring", "centring_beside", "symmetry", "centring_and_variance",
                                  "symmetry_beside", "serial_lag1_beside"}
    # E-295 (e): per-set centring decides for the clipped composite only; P_B's is beside
    sets = prem[prem["pool"] == "set"]
    assert not sets.loc[sets["composite"] == "p_b", "decides"].astype(bool).any()
    assert sets.loc[sets["composite"] == "toy_composite", "decides"].astype(bool).all()
    # E-295 (d): the twin's uniforms, deciding, read on the guards' sampled keys
    tw = prem[prem["check"] == "twin_uniforms"]
    assert len(tw) == 2 and tw["decides"].astype(bool).all() and (tw["n"] > 0).all()
    # c2 m-10: the lag-1 autocorrelation beside, deciding nothing
    ser = prem[prem["check"] == "serial_lag1_beside"]
    assert len(ser) == 2 * 2 * 2 and not ser["decides"].astype(bool).any() and np.isfinite(ser["stat"]).all()
    meta = st.files["h3a_a1"][1]
    assert set(meta["fill_failures"][0]) == {"base", "twin"}
    assert meta["smaller_j_report"].startswith("not run") and meta["stress"] == HR.STRESS_NOTE
    assert "OMP_NUM_THREADS" in meta and meta["workers"] == 1
    assert all(math.isfinite(r["mem_peak_mb"]) for r in res["records"]) or sys.platform != "win32"


def test_the_report_reads_every_input_and_refuses_the_tiny_sizes_at_the_declared_n(a1, a2, tmp_path) -> None:
    """The report part on the two parts' files: 54 pooled rows and 108 per-history rows at the tests' own sizes; at
    the declared sizes (the default) the same files refuse (B-4: their n is not the declared n); a missing
    per-history file refuses."""
    for st, _ in (a1, a2):
        st.to_dir(tmp_path)
    hs = {"A1": (0, 1), "A2": (0, 1)}
    pn = {("A1", "antithetic"): 2 * (M // JP), ("A1", "disjoint"): 2 * (200 // JP),
          ("A2", "exact_centred"): 2 * (M // JP)}
    df, hdf, meta = HR.build_final_report(tmp_path, pooled_n=pn, histories=hs)
    assert len(df) == 54 and len(hdf) == 108 and meta["pooled_total"] == 54
    assert meta["verdict"] in ("PASS_NO_LAXITY", "FAIL_LAXITY_STOP_H3D")
    with pytest.raises(REP.H3ReportRefused):
        HR.build_final_report(tmp_path, histories=hs)
    # c2 m-6 (R1, R2): a premise table holding one failed deciding premise refuses the report
    pf = tmp_path / "h3a_a1_premises.csv"
    prem = pd.read_csv(pf)
    i = prem.index[prem["decides"].astype(bool)][0]
    prem.loc[i, "ok"] = False
    prem.to_csv(pf, index=False)
    with pytest.raises(REP.H3ReportRefused, match="premise"):
        HR.build_final_report(tmp_path, pooled_n=pn, histories=hs)
    a1[0].to_dir(tmp_path)
    (tmp_path / "h3a_a2_h001.csv").unlink()
    with pytest.raises(REP.H3ReportRefused, match="missing"):
        HR.build_final_report(tmp_path, pooled_n=pn, histories=hs)


def test_a2_is_centred_exactly_and_its_premises_read_the_counted_pools(a2) -> None:
    """B-2: 18 cells a history; the centres are the exact program's (P_B's equal at the set and the seed, the clipped
    composite's at J' and at one seed); every centring premise on the counted pools (per seed and per set, both
    composites) holds; both arms' failures at the fill are recorded."""
    st, res = a2
    assert len(st.files["h3a_a2"][0]) == 18 == REP.A2_POOLED_TOTAL
    want = _sum_per_history(st, "h3a_a2", (0, 1))
    pooled = st.files["h3a_a2"][0]
    assert {(r["part"], r["null_class"], r["composite"], r["bound"], float(r["level"])): (int(r["rejections"]),
                                                                                          int(r["n"]))
            for _, r in pooled.iterrows()} == want
    seed = S.issue("tests")
    for rec in res["records"]:
        c = rec["beside"]["centres"]
        assert c["p_b"]["set"] == c["p_b"]["seed"]
        assert set(rec["fill"]) == {"a2_x1", "a2_x2"}
        hist = S1.generate(seed, TP, rec["history"], TINY_X)
        f, b = (S1.schedule(sp, hist) for sp in H.A2_PAIR)
        plan = R.Plan(seed=seed, part=TP, history=rec["history"], starts=STARTS, seed_indices=range(M), horizon=63,
                      block_sessions=TINY_X.n_sessions, budget=H.BUDGET)
        ef, eb = HR.exact_arm(f, H.TOY_RULES_EXACT, plan), HR.exact_arm(b, H.TOY_RULES_EXACT, plan)
        assert math.isclose(c["p_b"]["set"], float(R.exact_centres(f, b, H.TOY_RULES_EXACT, plan).mean()),
                            abs_tol=1e-12)
        assert math.isclose(c["toy_composite"]["set"], REP.exact_composite_centre(H.TOY_COMPOSITE, ef, eb, JP),
                            abs_tol=1e-12)
        assert math.isclose(c["toy_composite"]["seed"], REP.exact_composite_centre(H.TOY_COMPOSITE, ef, eb, 1),
                            abs_tol=1e-12)
    prem = st.files["h3a_a2_premises"][0]
    assert len(prem) == 2 * 2 * 3 and prem["ok"].all() and set(prem["pool"]) == {"seed", "set"}
    assert prem.loc[prem["check"] == "centring", "decides"].astype(bool).all()        # A2's set-level stays deciding
    assert not prem.loc[prem["check"] == "serial_lag1_beside", "decides"].astype(bool).any()


# --------------------------------------------------------------------------------------------- the exact program


def _pay_rules() -> J.ToyRules:
    """A toy account whose first payout can arrive within a few trades (one win passes, the next pays)."""
    return J.ToyRules(combine_fee=10.0, billing=21, target=100.0, mll=150.0, dll=None, activation_fee=10.0,
                      funded_mll=150.0, win_day=50.0, payout_days=1, payout_share=0.5, payout_cap=1000.0, split=1.0,
                      payout_lag=1)


def _pay_schedule(n: int = 8) -> J.Schedule:
    """n race trades, one a session from session 0, then none (so the program with no merge stays small)."""
    return J.Schedule("pay_toy", tuple(J.Trade(session=s, decision=960, entry=965, exit=1000, exit_reason="target",
                                               g=20, l=20, tick_value=5.0) for s in range(n)))


def test_the_first_payout_program_is_exact_against_no_merge_and_monte_carlo() -> None:
    """B-2 (b): the merge with the payout bit gives the same law of the first payout, P_B and sessions saved as the
    program with no merge at all (exact by construction); P_B equals the build's `three_way_journey.expect`; and a
    Monte Carlo of 20000 units (the tests' seed) lies within 4 standard errors of each exact moment."""
    rules, sch, h = _pay_rules(), _pay_schedule(), H.HORIZON
    got = HR.exact_moments(sch, rules, 0, h, block_sessions=h, budget=H.BUDGET)
    brute = HR.exact_moments(sch, rules, 0, h, block_sessions=h, budget=H.BUDGET, merge=lambda L, r, b: L)
    for k in HR.DIM_NAMES:
        assert math.isclose(got[k], brute[k], abs_tol=1e-12), k
    assert 0.05 < got["paid_by_63"] < 0.95
    assert math.isclose(got["P_B"], J.expect(sch, rules, 0, h, block_sessions=h, budget=H.BUDGET)["p_b"],
                        abs_tol=1e-12)
    plan = R.Plan(seed=S.issue("tests"), part=TP, history=0, starts=(0,), seed_indices=range(20000), horizon=h,
                  block_sessions=h, budget=H.BUDGET)
    X, _ = HR.unit_values(sch, rules, plan, J.ArmSpec(), None)
    for k in HR.DIM_NAMES:
        x = X[k].ravel()
        assert abs(x.mean() - got[k]) <= 4 * x.std(ddof=1) / math.sqrt(x.size) + 1e-12, k


def test_the_builds_merge_joins_paid_and_unpaid_states_and_the_payout_merge_does_not() -> None:
    """B-2 (b)'s defect shown on the build's own merge (unedited): two states equal in every field the build's key
    reads, one paid and one not, are joined by `three_way_journey._merge` (keeping one's `first_pay`), and kept apart
    by `_merge_paid` (the positive control for dropping the payout bit)."""
    rules = _pay_rules()
    L = J.Lanes.concat([J.fresh(1, rules), J.fresh(1, rules)])
    L.first_pay = np.array([-1, 5])
    L.w = np.array([0.5, 0.5])
    assert len(J._merge(L, rules, H.BUDGET)) == 1
    out = HR._merge_paid(L, rules, H.BUDGET)
    assert len(out) == 2 and sorted(out.first_pay.tolist()) == [-1, 5]


def test_unit_values_equal_the_builds_runner() -> None:
    """B-7's streaming changes nothing: `unit_values` equals `three_way_runner.run` + `matrix` for P_B, and the
    payout dimensions are the build's definitions on the same records."""
    seed = S.issue("tests")
    hist = S1.generate(seed, TP, 0, TINY)
    sch = S1.schedule(H.A1_DESIGN, hist)
    plan = R.Plan(seed=seed, part=TP, history=0, starts=(0, 2), seed_indices=range(64), horizon=63,
                  block_sessions=TINY.n_sessions, budget=H.BUDGET)
    X, ff = HR.unit_values(sch, H.TOY_RULES, plan, J.ArmSpec(), None)
    recs = R.run(sch, H.TOY_RULES, plan)
    assert np.array_equal(X["P_B"], R.matrix(recs, R.p_b))
    assert np.array_equal(X["paid_by_63"], R.matrix(recs, lambda r: ((r.first_pay > 0) & (r.first_pay <= 63)) * 1.0))
    assert np.array_equal(X["sessions_saved_to_payout"],
                          R.matrix(recs, lambda r: 64.0 - J.days_to_first_payout(r, 63)))
    assert HR.fill_summary(ff) == R.fill_failures(recs)


# --------------------------------------------------------------------------------------------- the kills


def test_a_planted_asymmetric_twin_stops_the_part_after_writing_its_records() -> None:
    """B-8 and m-8: a twin whose race is tilted (P3's plant on the twin's arm) is asymmetric; the symmetry kill
    fires, the history's record and the premise table are written first, the part refuses and no pooled file is
    written."""
    st = Store()
    with pytest.raises(REP.H3ReportRefused, match="premise failed"):
        HR.run_a1(part_id=TP, roles=ROLES, sink=st, histories=(0,), M=M, starts=STARTS, j_prime=JP, disjoint=DISJ,
                  s1_params=TINY, rules=H.TOY_RULES_EXACT, workers=1, cap_mb=BIG,
                  twin_arm=J.ArmSpec(twin=True, plant_eps=0.3))
    assert "h3a_a1_h000" in st.files and "h3a_a1_premises" in st.files and "h3a_a1" not in st.files
    prem = st.files["h3a_a1_premises"][0]
    bad = prem[~prem["ok"].astype(bool)]
    assert "symmetry" in set(bad["check"])
    assert bad.loc[bad["check"] == "symmetry", "decides"].astype(bool).all()
    assert st.files["h3a_a1_premises"][1]["refused"] is True


def test_the_disjoint_sets_are_checked_exactly() -> None:
    """m-3: two equal halves, sharing no index, covering every index; anything else refused."""
    HR.check_disjoint_sets(((0, 5), (5, 10)), 10)
    for bad in (((0, 6), (5, 10)), ((0, 4), (4, 10)), ((0, 5), (6, 11))):
        with pytest.raises(REP.H3ReportRefused):
            HR.check_disjoint_sets(bad, 10)
    assert HR.check_disjoint_sets(H.DISJOINT, H.SEEDS) is None


def test_memory_is_measured_projected_and_refused_above_the_cap() -> None:
    """B-7: the guard refuses a peak above its cap; a slot whose projection breaches the cap refuses before any draw;
    a record whose worker peaked above the cap is written, then refused; the declared slots' projections fit the
    declared cap at Appendix A's assumed base."""
    if not math.isfinite(HR.procmem.working_set_mb(peak=True)):
        pytest.skip("no working-set reading on this platform")
    with pytest.raises(HR.MemoryRefused):
        HR.MemoryGuard(1.0).check()
    st = Store()
    with pytest.raises(HR.MemoryRefused, match="projected"):
        HR.run_a1(part_id=TP, roles=ROLES, sink=st, histories=(0,), M=M, starts=STARTS, j_prime=JP, disjoint=DISJ,
                  s1_params=TINY, workers=1, cap_mb=1.0)
    assert not st.files
    P = HR._Part("A1", "t_a1", st, {"histories": [0], "j": JP}, cap_mb=10.0)
    with pytest.raises(HR.MemoryRefused):
        P.take({"part": "A1", "history": 0, "rows": [], "premise": [], "fill": {}, "beside": {}, "refused": False,
                "mem_peak_mb": 11.0})
    assert "t_a1_premises" in st.files
    base_mb = HR._A.BASE_GB * 1e9 / 2 ** 20
    for part, m in (("A1", H.SEEDS), ("A2", H.SEEDS), ("A3", 2000), ("A4", H.SEEDS)):
        assert HR.project_worker_mb(part, m, len(H.STARTS), H.HORIZON, H.TOY_RULES.payout_lag, base_mb) \
            <= HR.WORKER_CAP_MB


# --------------------------------------------------------------------------------------------- seeds, workers, rulings


def test_h3a_roles_are_refused_outside_a_clean_run_before_any_draw(monkeypatch) -> None:
    """B-3: the runner refuses H3-A's declared roles unless the clean-run marker is set, before any history is drawn;
    the tests' role is refused outside the tests' part."""
    monkeypatch.delenv(CLEAN_RUN_ENV, raising=False)

    def no_draw(*a, **k):
        raise AssertionError("a history was drawn")
    monkeypatch.setattr(HR.S1, "generate", no_draw)
    for runner, part in ((HR.run_a1, "A1"), (HR.run_a2, "A2")):
        with pytest.raises(S.ProvenanceRefused, match="clean run"):
            runner(part_id=S.PARTS[part], roles=HR.PART_ROLES[part], sink=Store(), histories=(0,), M=M,
                   starts=STARTS, workers=1)
    with pytest.raises(S.ProvenanceRefused, match="tests' part"):
        HR.run_a1(part_id=S.PARTS["A1"], roles=ROLES, sink=Store(), histories=(0,), M=M, starts=STARTS, workers=1)
    with pytest.raises(S.ProvenanceRefused):
        HR.check_seed_use("A1", S.PARTS["A1"], ("h3a3_history_null",))


def test_workers_are_refused_above_two_and_undeclared_slots_refuse() -> None:
    """m-4: --workers 1 or 2, never clamped; the slots a row must size first (A3, A4) refuse; main refuses before
    its gates."""
    assert HR.check_workers(1) == 1 and HR.check_workers(2) == 2
    for bad in (0, 3, True, 2.0, "2"):
        with pytest.raises(REP.H3ReportRefused, match="workers"):
            HR.check_workers(bad)
    with pytest.raises(REP.H3ReportRefused, match="workers"):
        HR.main(["--part", "A1", "--workers", "3", "--commit", "HEAD"])
    for part in ("A3_1", "A3_2", "report_a3"):
        with pytest.raises(REP.H3ReportRefused, match=r"deferred to H3-D \(E-295\)"):
            HR.check_rulings(part)
    for part in ("A1", "A2", "A4_1", "A4_2", "report", "report_a4"):
        HR.check_rulings(part)
    assert HR.A4_DRAW_J == H.J_PRIME and HR.PART_ROLES["A3"] == ()


def test_the_stress_is_fifteen_runs_when_a_size_is_given() -> None:
    """Section 8's stress: 3 arms x 5 schedules = 15 runs (`three_way_runner.stress_cells`), at a size the tests give
    (m-2: H3-A's is undeclared, so A1 does not run it)."""
    quick = S1.S1Params(n_sessions=70, regime_amp=0.0, rate=1.0, hold_mean=5.0, time_limit=500.0)
    out = HR.run_stress(0, 2, part_id=TP, roles=ROLES, part="A1", starts=(0,), s1_params=quick)
    assert sum(len(v) for v in out.values()) == 15 == R.stress_cells()
    assert HR.STRESS_NOTE.startswith("not run: deferred to H3-D")


# --------------------------------------------------------------------------------------------- A3 and A4


def test_a3_and_a4_slices_produce_their_declared_counts(tmp_path) -> None:
    """A3: 6 rows a history (2 composites x 3 levels), a shortcut history's full run, the summary's 6 rates; A4: 426
    rows a history and the summary's 426 rates and 60 MDLs; P1's null on an independent coin field (its draws' 2.2
    (a) lower limits vary: a null of the base against itself would not)."""
    st = Store()
    HR.run_a3_slice((0, 1), part_id=TP, roles=("tests",), sink=st, test_j=JP, time_conditions="regime", n_min=1, M=M,
                    starts=STARTS, s1_params=TINY, workers=1, shortcut=(0,), out="h3a_a3_1", block=2, cap_mb=BIG)
    rows = st.files["h3a_a3_1_h000"][0]
    assert len(rows) == 2 * 6 and rows.loc[rows["history"] == 0, "full_draws"].eq(M // JP).all()
    out = REP.summarise_a3(rows.to_dict("records"), histories=(0, 1), shortcut=(0,))
    assert len(out) == 6
    st4 = Store()
    HR.run_a4_slice((0, 1), part_id=TP, roles=ROLES, sink=st4, draw_j=JP, M=M, starts=STARTS, disjoint=DISJ,
                    s1_params=TINY, rules=H.TOY_RULES_EXACT, workers=1, cap_mb=BIG, out="h3a_a4_1")
    for h in (0, 1):
        assert len(st4.files[f"h3a_a4_1_h{h:03d}"][0]) == 426
    low = st4.files["h3a_a4_1_h000_p1"][0]
    assert len(low) == (200 // JP) * 2 * 3
    assert low.loc[low["bound"] == "bound_22a", "lower0"].std() > 0
    st4.to_dir(tmp_path)
    rates, mdls, _ = HR.build_a4_report(tmp_path, histories=(0, 1))
    assert len(rates) == 426 and len(mdls) == 60


def test_h3a_run_refuses_outside_clean_run_in_subprocess():
    code = (
        "import os; os.environ.pop('S2X_CLEAN_RUN', None); "
        "from scripts import h3a_run as HR; "
        "HR.check_runtime_gates('A1')"
    )
    proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    assert proc.returncode != 0
    assert "clean run" in (proc.stderr + proc.stdout).lower()


# --------------------------------------------------------------------------------------------- c2's minors (E-295)


def _fine_merge(L, rules):
    """The oracle's merge: the build's state key and the first payout's own session (never joins two states whose
    first payouts differ), so its program is exact for the first payout's law by construction."""
    key = np.column_stack([J._state_key(L, rules, H.BUDGET), np.asarray(L.first_pay, float)])
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    w = np.zeros(len(first))
    np.add.at(w, inv.ravel(), L.w)
    out = L.take(first)
    out.w = w
    return out


def _oracle(sch, rules, start, h, block):
    """P_B, paid and sessions saved from the final states of the fine-merged program, by `days_to_first_payout`'s
    rule (W + 1 less the first payout's session, 0 unpaid) -- not from the runner's per-close law."""
    L = J.fresh(1, rules)
    for k in range(1, h + 1):
        L = J._session(L, sch.by_session.get(start + k - 1, ()), k, rules, J.ArmSpec(), H.BUDGET, None, dp=True)
        L.day = L.dead = L.stopped = None
        L = _fine_merge(L, rules)
    fp = np.asarray(L.first_pay, float)
    paid = (fp > 0) & (fp <= h)
    return {"P_B": float((L.w * L.ahead).sum() / 3.0), "paid_by_63": float((L.w * paid).sum()),
            "sessions_saved_to_payout": float((L.w * np.where(paid, h + 1 - fp, 0.0)).sum())}


def test_sessions_saved_and_the_payout_law_against_an_independent_oracle() -> None:
    """c2 m-2: on a toy where the build's merge misstates the first payout's law (A2's pair on a `TINY_X` history of
    the tests' seed, start 3), the runner's program equals the oracle -- its own merge keyed by the first payout's
    session and the sessions saved read from the final states -- and the build's merge does not (so the oracle sees
    the payout bit, and an off-by-one in sessions saved, mutant P2, fails)."""
    hist = S1.generate(S.issue("tests"), TP, 0, TINY_X)
    sch = S1.schedule(H.A2_PAIR[0], hist)
    rules, h, block = H.TOY_RULES_EXACT, H.HORIZON, TINY_X.n_sessions
    want = _oracle(sch, rules, 3, h, block)
    got = HR.exact_moments(sch, rules, 3, h, block_sessions=block, budget=H.BUDGET)
    for k in HR.DIM_NAMES:
        assert math.isclose(got[k], want[k], abs_tol=1e-12), k
    built = HR.exact_moments(sch, rules, 3, h, block_sessions=block, budget=H.BUDGET,
                             merge=lambda L, r, b: J._merge(L, r, b))
    assert abs(built["paid_by_63"] - want["paid_by_63"]) > 1e-6
    assert want["paid_by_63"] > 0.01


def test_check_seed_use_refuses_a_declared_role_elsewhere_and_a_foreign_role(monkeypatch) -> None:
    """c2 m-3 (D1, D4), inside a clean run: H3-A's declared role at another part's id, a foreign role, and A3's role
    (drawn by nothing until H3-D's text, E-295 (b)) all refuse; the declared roles in their own part pass."""
    monkeypatch.setenv(CLEAN_RUN_ENV, "a-clean-run")
    with pytest.raises(S.ProvenanceRefused, match="draws in part A1 only"):
        HR.check_seed_use("A1", S.PARTS["A2"], ("h3a_histories",))
    with pytest.raises(S.ProvenanceRefused, match="not a seed role of part A1"):
        HR.check_seed_use("A1", S.PARTS["A1"], ("h3d_coins",))
    with pytest.raises(S.ProvenanceRefused, match="not a seed role of part A3"):
        HR.check_seed_use("A3", S.PARTS["A3"], ("h3a3_history_null",))
    HR.check_seed_use("A1", S.PARTS["A1"], HR.PART_ROLES["A1"])


def test_a_refusal_inside_a_worker_writes_the_records_first(monkeypatch) -> None:
    """c2 m-4: a memory breach inside a worker, and a `BoundRefused` whose message is not a "REFUSED" one, are
    returned as refused records: the history's record and the premise table are written, then the part refuses."""
    calls = {"n": 0}

    def breach(self):
        calls["n"] += 1
        if calls["n"] > 2:
            raise HR.MemoryRefused("REFUSED (B-7): planted breach")
    monkeypatch.setattr(HR.MemoryGuard, "check", breach)
    st = Store()
    with pytest.raises(HR.MemoryRefused):
        HR.run_a1(part_id=TP, roles=ROLES, sink=st, histories=(0,), M=M, starts=STARTS, j_prime=JP, disjoint=DISJ,
                  s1_params=TINY, rules=H.TOY_RULES_EXACT, workers=1, cap_mb=BIG)
    assert "h3a_a1_h000" in st.files and "h3a_a1" not in st.files
    assert "memory" in set(st.files["h3a_a1_premises"][0]["check"])
    monkeypatch.undo()

    def blank(*a, **k):
        raise HR.ST.BoundRefused("P_B: a blank or infinite per-unit value")
    monkeypatch.setattr(HR.REP, "size_counts", blank)
    st2 = Store()
    with pytest.raises(REP.H3ReportRefused, match="premise failed"):
        HR.run_a1(part_id=TP, roles=ROLES, sink=st2, histories=(0,), M=M, starts=STARTS, j_prime=JP, disjoint=DISJ,
                  s1_params=TINY, rules=H.TOY_RULES_EXACT, workers=1, cap_mb=BIG)
    assert "h3a_a1_h000" in st2.files
    assert "term_out_of_range" in set(st2.files["h3a_a1_premises"][0]["check"])


def test_the_memory_projection_guard_and_total_have_their_declared_sizes() -> None:
    """c2 m-5 (Y1, Y2): the projection is its arithmetic, written out here; the caps are Appendix A's (2.5 GB in all,
    half a worker); the guard refuses just below a known allocation's peak and passes above it; the total counts
    the parent beside each worker; a part and a projection over the cap in all refuse."""
    if not math.isfinite(HR.procmem.working_set_mb(peak=True)):
        pytest.skip("no working-set reading on this platform")
    lag = H.TOY_RULES.payout_lag
    kept = 2 * 4 * 120 * 10000 * 8
    one = 5000 * ((20 + lag + 1) * 8 + 64 * 8 + 200 + 32 * 8)
    assert math.isclose(HR.project_worker_mb("A1", 10000, 120, 63, lag, 0.0), (kept + one) / 2 ** 20, rel_tol=1e-12)
    one4 = 10000 * ((20 + lag + 1) * 8 + 64 * 8 + 200 + 32 * 8)
    assert math.isclose(HR.project_worker_mb("A4", 10000, 120, 63, lag, 7.0), 7.0 + (kept + one4) / 2 ** 20,
                        rel_tol=1e-12)
    assert math.isclose(HR.TOTAL_CAP_MB, 2.5e9 / 2 ** 20) and math.isclose(HR.WORKER_CAP_MB, HR.TOTAL_CAP_MB / 2)
    block = np.ones(200 * 2 ** 20 // 8)                     # a known allocation, touched
    peak = HR.procmem.working_set_mb(peak=True)
    assert block.sum() > 0
    with pytest.raises(HR.MemoryRefused):
        HR.MemoryGuard(peak - 20.0).check()
    HR.MemoryGuard(peak + 150.0).check()
    del block
    assert HR.total_mb(300.0, 400.0, 2) == 1100.0 and HR.total_mb(300.0, 400.0, 1) == 400.0
    with pytest.raises(HR.MemoryRefused, match="in all"):
        HR._projection_check("A1", M, len(STARTS), 63, H.TOY_RULES, cap_mb=BIG, workers=2, total_cap_mb=1.0)
    st = Store()
    P = HR._Part("A1", "t_a1", st, {"histories": [0], "j": JP}, cap_mb=BIG, workers=2, total_cap_mb=1.0)
    with pytest.raises(HR.MemoryRefused, match="in all"):
        P.take({"part": "A1", "history": 0, "rows": [], "premise": [], "fill": {}, "beside": {}, "refused": False,
                "mem_peak_mb": 1.0})
    assert "t_a1_premises" in st.files


def test_the_runner_runs_from_one_named_commit(tmp_path) -> None:
    """c2 m-6: HEAD must be the named commit; an H3-A output already in results/ written from another commit, or
    dirty, refuses at the start; one from the named commit, clean, passes; `--commit` is required; a premise table
    with one failed deciding premise refuses (`_premises_hold`), a failed premise beside does not."""
    head = HR.check_commit("HEAD", results_dir=tmp_path)
    assert len(head) == 40
    with pytest.raises(REP.H3ReportRefused, match="not the named commit"):
        HR.check_commit(REP.H3_BUILD_COMMIT, results_dir=tmp_path)
    (tmp_path / "h3a_a1.csv").write_text("a\n1\n", encoding="utf-8")
    (tmp_path / "other.csv").write_text("a\n1\n", encoding="utf-8")
    seen = []

    def man(commit, dirty):
        return lambda f: (seen.append(f.name), {"git_commit": commit, "git_dirty": dirty})[1]
    assert HR.check_commit("HEAD", results_dir=tmp_path, read_manifest=man(head, False)) == head
    assert seen == ["h3a_a1.csv"]
    with pytest.raises(REP.H3ReportRefused, match="written from"):
        HR.check_commit("HEAD", results_dir=tmp_path, read_manifest=man("0" * 40, False))
    with pytest.raises(REP.H3ReportRefused, match="written from"):
        HR.check_commit("HEAD", results_dir=tmp_path, read_manifest=man(head, True))
    with pytest.raises(SystemExit):
        HR.main(["--part", "A1", "--workers", "2"])
    cols = ["part", "history", "null_class", "composite", "pool", "check", "decides", "ok"]
    with pytest.raises(REP.H3ReportRefused, match="premise"):
        HR._premises_hold(pd.DataFrame([["A1", 0, "antithetic", "p_b", "seed", "centring", True, False]],
                                       columns=cols), "t")
    HR._premises_hold(pd.DataFrame([["A1", 0, "antithetic", "p_b", "set", "centring_beside", False, False],
                                    ["A1", 0, "antithetic", "p_b", "seed", "centring", True, True]], columns=cols), "t")


def test_omp_threads_are_refused_above_two_and_unset(monkeypatch) -> None:
    """c2 m-7: OMP_NUM_THREADS 1 or 2; unset, 0, 3 or text refuse; main refuses before its gates."""
    assert HR.check_threads({"OMP_NUM_THREADS": "1"}) == 1 and HR.check_threads({"OMP_NUM_THREADS": "2"}) == 2
    for bad in ({}, {"OMP_NUM_THREADS": "0"}, {"OMP_NUM_THREADS": "3"}, {"OMP_NUM_THREADS": "many"}):
        with pytest.raises(REP.H3ReportRefused, match="OMP_NUM_THREADS"):
            HR.check_threads(bad)
    monkeypatch.setenv("OMP_NUM_THREADS", "3")
    with pytest.raises(REP.H3ReportRefused, match="OMP_NUM_THREADS"):
        HR.main(["--part", "A1", "--workers", "2", "--commit", "HEAD"])


def test_the_twin_uniforms_are_the_complements_bit_for_bit_and_a_defect_kills_the_part(monkeypatch) -> None:
    """E-295 (d): on a guard's sampled keys every twin uniform is 1 minus the base's, bit for bit; a reader that
    hands the twin the base's uniforms mismatches on every key; planted in A1, it kills the part."""
    seed = S.issue("tests")
    sch = S1.schedule(H.A1_DESIGN, S1.generate(seed, TP, 0, TINY))
    plan = R.Plan(seed=seed, part=TP, history=0, starts=(0,), seed_indices=range(16), horizon=63,
                  block_sessions=TINY.n_sessions, budget=H.BUDGET)
    g = HR.K.KeyGuard.sampled(plan.starts, plan.seed_indices)
    HR.unit_values(sch, H.TOY_RULES, plan, J.ArmSpec(), g)
    ok = HR.check_twin_uniforms([g], seed)
    assert ok["ok"] is True and ok["n"] > 0 and ok["mismatches"] == 0

    def same(Mx, n):
        return HR.F.uniforms(Mx, n, False)
    bad = HR.check_twin_uniforms([g], seed, twin_read=same)
    assert bad["ok"] is False and bad["mismatches"] == bad["n"] == ok["n"]
    real = HR.check_twin_uniforms
    monkeypatch.setattr(HR, "check_twin_uniforms", lambda guards, sd: real(guards, sd, twin_read=same))
    st = Store()
    with pytest.raises(REP.H3ReportRefused, match="twin_uniforms"):
        HR.run_a1(part_id=TP, roles=ROLES, sink=st, histories=(0,), M=M, starts=STARTS, j_prime=JP, disjoint=DISJ,
                  s1_params=TINY, rules=H.TOY_RULES_EXACT, workers=1, cap_mb=BIG)
    assert "h3a_a1_premises" in st.files and "h3a_a1" not in st.files


def test_a4_prints_its_j_and_its_null_beside(tmp_path) -> None:
    """E-295 (a) and c2 m-9: A4's manifest, rates and MDLs carry the J = J' note, and P1's and P4's rows the reading
    that their null is the disjoint same-design null and that P4 is P1 at d mean(1 + a rho_t) in H3-A."""
    rows = [{"history": 0, "plant": c[0], "param": c[1], "composite": c[2], "bound": c[3], "level": c[4], "passes": 0,
             "draws": 2, "true_delta": 0.0} for c in REP.a4_cells()]
    low = [{"history": 0, "draw": d, "bound": b, "level": lv, "lower0": -1.0} for d in range(2)
           for b in ("bound_22a", "eb") for lv in REP.LEVELS]
    rates, mdls = REP.summarise_a4(rows, low, histories=(0,))
    assert all(r["j_beside"] == REP.A4_J_NOTE for r in rates) and all(m["j_beside"] == REP.A4_J_NOTE for m in mdls)
    assert all(r["reading_beside"] == REP.A4_NULL_NOTE for r in rates if r["plant"] in ("P1", "P4"))
    assert all(r["reading_beside"] == "" for r in rates if r["plant"] in ("P2", "P3"))
    assert all(m["reading_beside"] == REP.A4_NULL_NOTE for m in mdls)
    assert "J = J_PRIME = 100" in REP.A4_J_NOTE and "d mean(1 + a rho_t)" in REP.A4_NULL_NOTE
