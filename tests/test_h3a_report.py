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
        # Also verify through evaluate_laxity_stop (kills denominator 53 and 1080 mutants on evaluate_laxity_stop)
        rows_below = _make_clean_54(n)
        idx = next(i for i, r in enumerate(rows_below) if r.part == "A1" and r.level == lvl)
        c = rows_below[idx]
        rows_below[idx] = R.SizeCount(c.part, c.null_class, c.composite, c.bound, c.level, kc - 1, n)
        assert R.evaluate_laxity_stop(rows_below)["stop_h3d"] is False
        rows_at = list(rows_below)
        rows_at[idx] = R.SizeCount(c.part, c.null_class, c.composite, c.bound, c.level, kc, n)
        res_at = R.evaluate_laxity_stop(rows_at)
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
    res = R.evaluate_laxity_stop(rows)
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
            assert R.evaluate_laxity_stop(rows53)["stop_h3d"] is False
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
            assert R.evaluate_laxity_stop(rows55)["stop_h3d"] is True
            break
    else:
        pytest.fail("no n found distinguishing denom 54 from 55")


def test_clean_54_passes_and_generator_inputs_do_not_exhaust() -> None:
    rows = _make_clean_54(2000)
    res = R.evaluate_laxity_stop(r for r in rows)  # generator input!
    assert res["pooled_total"] == 54
    assert res["a1_pooled"] == 36
    assert res["a2_pooled"] == 18
    assert res["stop_h3d"] is False
    assert res["lax_count"] == 0
    assert res["verdict"] == "PASS_NO_LAXITY"
    assert len(res["pooled_rows"]) == 54

    # 100%-lax generator MUST fail (kills double-iteration exhaustion bug!)
    all_lax = (R.SizeCount(r.part, r.null_class, r.composite, r.bound, r.level, 2000, 2000) for r in rows)
    res_lax = R.evaluate_laxity_stop(all_lax)
    assert res_lax["stop_h3d"] is True and res_lax["lax_count"] == 54 and res_lax["verdict"] == "FAIL_LAXITY_STOP_H3D"


def test_a1_and_a2_single_lax_cells_each_stop_h3d() -> None:
    for target_part in ("A1", "A2"):
        rows = _make_clean_54(2000)
        idx = next(i for i, r in enumerate(rows) if r.part == target_part and r.level == 0.01)
        bad = rows[idx]
        rows[idx] = R.SizeCount(bad.part, bad.null_class, bad.composite, bad.bound, bad.level, 60, 2000)
        res = R.evaluate_laxity_stop(rows)
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
    res = R.evaluate_laxity_stop(rows)
    assert res["stop_h3d"] is False
    cell = next(r for r in res["pooled_rows"] if (r["part"], r["null_class"], r["composite"], r["bound"], r["level"])
                == (c.part, c.null_class, c.composite, c.bound, c.level))
    assert cell["beside_e052_label"] == "lax" and cell["stop_lax"] is False


def test_per_history_laxity_never_stops_and_invalid_per_history_refused() -> None:
    pooled = _make_clean_54(2000)
    per_hist = [
        R.SizeCount(r.part, r.null_class, r.composite, r.bound, r.level, 100, 100, history=h)
        for r in pooled for h in range(20)
    ]
    assert len(per_hist) == 1080
    res = R.evaluate_laxity_stop(pooled, (h for h in per_hist))
    assert res["stop_h3d"] is False
    assert res["per_history_count"] == 1080
    assert all(h["beside_e052_label"] == "lax" and h["decides"] is False for h in res["per_history_beside"])

    # Duplicate per-history row refused
    with pytest.raises(R.H3ReportRefused, match="duplicate per-history"):
        R.evaluate_laxity_stop(pooled, [per_hist[0], per_hist[0]])
    # Bogus key per-history row refused
    bogus = R.SizeCount("A9", "antithetic", "p_b", "bound_22a", 0.05, 5, 100, history=0)
    with pytest.raises(R.H3ReportRefused, match="undeclared per-history"):
        R.evaluate_laxity_stop(pooled, [bogus])
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


def test_refuses_missing_extra_duplicate_and_invalid_inputs() -> None:
    rows = _make_clean_54(2000)
    with pytest.raises(R.H3ReportRefused, match="exact 54"):
        R.evaluate_laxity_stop(rows[:-1])
    extra = R.SizeCount("A2", "antithetic", "p_b", "bound_22a", 0.05, 5, 100)
    with pytest.raises(R.H3ReportRefused, match="exact 54"):
        R.evaluate_laxity_stop(rows + [extra])
    with pytest.raises(R.H3ReportRefused, match="duplicate"):
        R.evaluate_laxity_stop(rows + [rows[0]])
    with pytest.raises(R.H3ReportRefused, match="per-history"):
        R.evaluate_laxity_stop([R.SizeCount("A1", "antithetic", "p_b", "bound_22a", 0.05, 5, 100, history=0)])

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
