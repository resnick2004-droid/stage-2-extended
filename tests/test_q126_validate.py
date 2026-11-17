"""Q-126 (E-187): `scripts/q126_validate.py`, the validation runner -- built ready to run, never run here. Synthetic
inputs only. Seeds: 20263020 (the validation build's tests, the plan's 4.1), sub-streams by test; the toy runs' seed
maps lie outside the 2026 space (81260210 and up), named by role.

What is asserted (the plan's 4.3, 6.1 and 6.3):
- **the seed map** is the plan's validation table as parsed from the pinned file, its spare drawn by nothing; a map
  of another block refused; no literal outside the seed-block section;
- **the validation's nulls**: Q-108's class on the validation seeds, j = 0..22, the exact null index 0..1,169, the
  provenance assertion passing them and refusing the calibration's index and Q-108's validation construction;
- **the choosing row and the decision line**: only the lines the plan's 4.2 prints; NONE retires the block before any
  read; the choice file refused unless it matches its pinning row and its manifest (the calibration's script, a clean
  run, not exploratory) and the module is the blob the calibration ran;
- **the criterion**: Q-108's validation code's verdicts reproduced on planted tables, for each of two statistics, each
  on its own -- HOLDS, FAILS on a Monte Carlo null at its failure count and on an exact size above nominal, NOT
  CHECKED with a null missing;
- **a small end-to-end validation on toy streams** (the core and the drift, two statistics and `cons` beside, the
  criterion) that writes nothing.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
ENTRY = ROOT / "scripts" / "q126_validate.py"
SEED = 20263020
TOY = 81260210


def load(name="q126_validate_t"):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ENTRY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def V():
    return load()


def toy_seeds(V):
    s = {r: TOY + i for i, r in enumerate(V.DRAW_ROLES)}
    s["tests"] = TOY + 40
    return s


# ------------------------------------------------------------------------------------------------ the seed map


def test_the_seed_map_is_the_plans_validation_table(V):
    C = V.CALQ
    text = C.plan_path().read_text(encoding="utf-8")
    want, spare = C.parsed_seed_map(text, "validation", V.ROLE_TEXT)
    assert V.SEEDS == want and list(V.SPARE) == spare and V.SEEDS["tests"] == SEED
    assert set(V.SEEDS.values()) | set(V.SPARE) == set(C.VAL_BLOCK)
    assert C.seed_map_problems(V.SEEDS, C.VAL_BLOCK, V.DRAW_ROLES + ("tests",), plan_block="validation",
                               role_text=V.ROLE_TEXT, spare=V.SPARE) == []
    # the calibration's map, or a validation map without its spare, is refused
    assert C.seed_map_problems(C.SEEDS, C.VAL_BLOCK, V.DRAW_ROLES + ("tests",), plan_block="validation",
                               role_text=V.ROLE_TEXT, spare=V.SPARE)
    assert C.seed_map_problems(V.SEEDS, C.VAL_BLOCK, V.DRAW_ROLES + ("tests",), plan_block="validation",
                               role_text=V.ROLE_TEXT, spare=())
    swap = dict(V.SEEDS, drift=V.SEEDS["exact_sample"], exact_sample=V.SEEDS["drift"])
    assert C.seed_map_problems(swap, C.VAL_BLOCK, V.DRAW_ROLES + ("tests",), plan_block="validation",
                               role_text=V.ROLE_TEXT, spare=V.SPARE)
    src = ENTRY.read_text(encoding="utf-8")
    lines = src.splitlines()
    first = next(i for i, x in enumerate(lines, 1) if x.startswith("# ---- the validation seed map"))
    last = next(i for i, x in enumerate(lines, 1) if x.startswith("# ---- end of the validation seed map"))
    lits = [(node.lineno, node.value) for node in ast.walk(ast.parse(src)) if isinstance(node, ast.Constant)
            and isinstance(node.value, int) and 20263000 <= node.value <= 20263099]
    assert lits and all(first < ln < last for ln, _ in lits) and {v for _, v in lits} == set(C.VAL_BLOCK)


def test_the_validations_nulls(V):
    C = V.CALQ
    s = V.SEEDS
    plan = V.core_plan(s)
    rule = [x for x in plan if x["in_rule"]]
    assert len(rule) == 2293 and sum(x["kind"] == "exact" for x in rule) == 1170
    assert sum(x["group"] == "beside_cp" for x in plan) == 54 and sum(x["group"] == "beside_flat" for x in plan) == 30
    ex = sorted(x["exact_index"] for x in plan if x["kind"] == "exact")
    assert ex == list(range(1170))
    by = {x["null"]: x for x in plan}
    assert by["sub:5000:022:net3:alt55"]["exact_index"] == 1169
    assert by["sub:500:000:win1:flip42"]["exact_index"] == (2 + 23) * 10              # Q-108's validation form
    assert by["sub:500:000:win1:flip42"]["sample_entropy"] == [s["exact_sample"], 250]
    assert max(x["j"] for x in plan if x["j"] is not None) == 22
    assert all(x["subset_entropy"][0] == s["subsets"] for x in plan if x["subset_entropy"])
    assert V.provenance(plan + V.drift_plan(s), s) == []
    # the calibration's exact index (660 subsets a size) on these seeds is refused, as is any j past 22
    cal_form = C.core_plan(s)
    assert any("exact index" in p for p in V.provenance(cal_form, s))
    extra = dict(by["sub:200:000:win1:alt45"], j=23, null="sub:200:023:win1:alt45")
    assert V.provenance([extra], s)
    # Q-108's validation construction (its retired map) is refused in full
    spec = importlib.util.spec_from_file_location("q108_validate_pristine_t", ROOT / "scripts" / "q108_validate.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    old = mod.CAL.null_plan(mod.SEEDS)
    probs = V.provenance([dict(C._base(), **x) for x in old], s)
    assert probs and sum("is not the plan's" in p for p in probs) >= len(old) * 0.9
    assert all(e[0] != V.SPARE[0] for x in plan for e in (x["entropy"], x["subset_entropy"], x["sample_entropy"]) if e)
    with pytest.raises(C.ProvenanceRefused):
        V.VAL108.SEEDS["fixed_mc"]


# ------------------------------------------------------------------------------------------------ the choice


def test_the_decision_lines(V):
    P = V.parse_decision
    assert P("NONE") is None
    assert P("CHOSEN cons_m1.25 (scope D); SECOND cons_m1.5 (scope Q)") == \
        {"primary": ("cons_m1.25", "D"), "second": ("cons_m1.5", "Q")}
    assert P("CHOSEN cons_bm_m1.25 (scope D); SECOND NONE") == {"primary": ("cons_bm_m1.25", "D"), "second": None}
    assert P("CHOSEN cons_m2 (scope Q)") == {"primary": ("cons_m2", "Q"), "second": None}
    for bad in ("CHOSEN cons (scope Q)",                              # not a pair in the rule
                "CHOSEN cons_m1.5 (scope Q); SECOND cons_m2 (scope Q)",   # a scope-Q primary has no second
                "CHOSEN cons (scope D); SECOND cons_m1.25 (scope Q)",     # the second from the branch only
                "CHOSEN cons (scope D)",                                  # the SECOND line is printed
                "CHOSEN cons_m3 (scope D); SECOND NONE", "chosen cons"):
        with pytest.raises(ValueError):
            P(bad)
    st = V.statistics({"primary": ("cons_m1.25", "D"), "second": ("cons_m1.5", "Q")})
    assert st == [("cons_m1.25", "D"), ("cons_m1.5", "Q")]
    assert V.candidates_for(st) == ["cons_m1.25", "cons_m1.5", "cons"]
    assert V.candidates_for([("cons", "D")]) == ["cons"]
    text = "| E-190 | x | `results/q126_choice.csv` sha256 `" + "a" * 64 + "` |\n| E-191 | y |\n"
    assert V.choosing_row(text) == ("E-190", "a" * 64)
    assert V.choosing_row("| E-1 | nothing |") == (None, None)


def _choice_repo(tmp_path, V, line, *, script=None, clean=True, exploratory=False, blob=None):
    from extended import results as XR

    repo = tmp_path / "repo"
    (repo / "results").mkdir(parents=True)
    (repo / "extended").mkdir()
    (repo / "extended" / "lift_one_sample2.py").write_bytes((ROOT / "extended" / "lift_one_sample2.py").read_bytes())
    df = pd.DataFrame([{"row": "candidate", "candidate": "cons", "decision": None},
                       {"row": "decision", "candidate": None, "decision": line}])
    csv, man = XR.write_result(df, "q126_choice", script=script or V.CALQ.SCRIPT, seed=None, require_seed=False,
                               parameters={"blobs": {V.CALQ.MODULE: blob or V.CALQ.blob_id(
                                   repo / "extended" / "lift_one_sample2.py")}},
                               results_dir=repo / "results", exploratory=exploratory,
                               provenance={"clean_run": {"name": "t"}} if clean else None)
    sha = V.CALQ._sha(csv)
    (repo / "DECISIONS.md").write_text(f"| E-190 | 2026-11-18 | **the choice: `results/q126_choice.csv` sha256 "
                                       f"`{sha}`** | basis |\n", encoding="utf-8")
    return repo


def test_the_choice_file_and_its_row(V, tmp_path):
    ok_line = "CHOSEN cons_m1.25 (scope D); SECOND cons_m1.5 (scope Q)"
    probs, info = V.choice_problems(_choice_repo(tmp_path / "a", V, ok_line))
    assert probs == [] and info["primary"] == ("cons_m1.25", "D") and info["second"] == ("cons_m1.5", "Q")
    probs, _ = V.choice_problems(_choice_repo(tmp_path / "b", V, "NONE"))
    assert probs and "retired" in probs[0]
    assert V.choice_problems(_choice_repo(tmp_path / "c", V, ok_line, script="scripts/other.py"))[0]
    assert V.choice_problems(_choice_repo(tmp_path / "d", V, ok_line, clean=False))[0]
    assert V.choice_problems(_choice_repo(tmp_path / "e", V, ok_line, exploratory=True))[0]
    probs, _ = V.choice_problems(_choice_repo(tmp_path / "f", V, ok_line, blob="0" * 40))
    assert any("the calibration ran" in p for p in probs)
    repo = _choice_repo(tmp_path / "g", V, ok_line)
    (repo / "DECISIONS.md").write_text("| E-190 | `results/q126_choice.csv` sha256 `" + "0" * 64 + "` |\n",
                                       encoding="utf-8")
    assert any("does not hash" in p for p in V.choice_problems(repo)[0])
    (repo / "DECISIONS.md").write_text("| E-190 | no row |\n", encoding="utf-8")
    assert "no decision row" in V.choice_problems(repo)[0][0]


def test_none_is_refused_before_any_read(V, tmp_path, monkeypatch, capsys):
    from extended import results as XR

    monkeypatch.setattr(XR, "clean_run_problem", lambda: None)
    monkeypatch.setattr(V.CALQ, "lock_problem", lambda env=None: None)
    repo = _choice_repo(tmp_path, V, "NONE")
    reads = []
    monkeypatch.setattr(V.CALQ, "read_calendar", lambda *a, **k: reads.append(1))
    probs, _ = V.preflight(tmp_path / "results_target", None, repo=repo, guard=False)
    assert probs and "retired" in probs[0] and reads == []
    monkeypatch.setattr(V, "preflight", lambda *a, **k: (["the calibration chose NONE: retired"], {}))
    assert V.main([]) == 3 and "REFUSED" in capsys.readouterr().out and reads == []


def test_refuses_outside_a_clean_run():
    env = {k: v for k, v in __import__("os").environ.items() if k not in ("S2X_CLEAN_RUN", "S2X_RUN_ID",
                                                                          "S2X_LOCK_HOLDER")}
    r = subprocess.run([sys.executable, str(ENTRY)], cwd=str(ROOT), capture_output=True, text=True, timeout=600,
                       env=env)
    assert r.returncode == 3 and "clean run" in r.stdout, r.stdout[-2000:] + r.stderr


# ------------------------------------------------------------------------------------------------ the criterion


def _crit_size(V, stats_, nulls=6):
    C = V.CALQ
    rows = []
    for c in V.candidates_for(stats_):
        for s_ in C.SCOPES:
            for i in range(nulls):
                kind = "mc" if i % 2 == 0 else "exact"
                den = 200_000 if kind == "mc" else 42 * 2 ** 17
                r = {"null": f"n{i}", "kind": kind, "group": "subset", "in_rule": True, "candidate": c, "scope": s_,
                     "denominator": den, "model": "markov50" if kind == "mc" else "flip42"}
                for lab in C.LABELS:
                    r[f"count_{lab}"] = 0
                r[f"ratio_{C.LABELS[0]}"] = 0.0
                for lab in C.LABELS:
                    r[f"ratio_{lab}"] = 0.0
                rows.append(r)
    return pd.DataFrame(rows)


def _set(V, df, c, s_, null, counts):
    """Plant counts for `c` -- and for every smaller margin of rows 1-7 present, so the table stays nested in m."""
    nest = list(V.L2.NESTED)
    who = [x for x in nest[:nest.index(c) + 1]] if c in nest else [c]
    sel = df["candidate"].isin(who) & (df["scope"] == s_) & (df["null"] == null)
    for lab, x in zip(V.CALQ.FAM_LABELS, counts):
        df.loc[sel, f"count_{lab}"] = x


def test_the_criterion_is_q108s_for_each_of_two_statistics(V):
    stats_ = [("cons_m1.25", "D"), ("cons_m1.5", "Q")]
    want = {"rule": 6}
    size = _crit_size(V, stats_)
    res = V.criterion_tables(size, stats_, V.candidates_for(stats_), want)
    assert res["failed"] == [] and res["verdicts"] == {("cons_m1.25", "D"): "HOLDS", ("cons_m1.5", "Q"): "HOLDS"}
    for c, s_ in stats_:
        ref = V.VAL108.criterion(size, c, s_, want)
        got = res["criterion"][(res["criterion"]["candidate"] == c) & (res["criterion"]["scope"] == s_)]
        assert list(got["verdict"]) == list(ref["verdict"])
    # a Monte Carlo null at its failure count at k = 20 (35 of 200,000): the primary FAILS, the second HOLDS
    _set(V, size, "cons_m1.25", "D", "n0", [35] * 8)
    res = V.criterion_tables(size, stats_, V.candidates_for(stats_), want)
    assert res["verdicts"] == {("cons_m1.25", "D"): "FAILS", ("cons_m1.5", "Q"): "HOLDS"}
    k20 = res["criterion"][(res["criterion"]["candidate"] == "cons_m1.25") & (res["criterion"]["k"].astype(str) == "20")]
    assert k20["failing_nulls"].iloc[0] == "n0"
    _set(V, size, "cons_m1.25", "D", "n0", [34] * 8)                                   # one below: holds
    assert V.criterion_tables(size, stats_, V.candidates_for(stats_), want)["verdicts"][("cons_m1.25", "D")] == "HOLDS"
    # an exact size above nominal at k = 20 for the second: it FAILS on its own
    x = (42 * 2 ** 17) // (20 * 20 * 21) + 1
    _set(V, size, "cons_m1.5", "Q", "n1", [x] * 8)
    res = V.criterion_tables(size, stats_, V.candidates_for(stats_), want)
    assert res["verdicts"] == {("cons_m1.25", "D"): "HOLDS", ("cons_m1.5", "Q"): "FAILS"}
    for c, s_ in stats_:
        ref = V.VAL108.criterion(size, c, s_, want)
        got = res["criterion"][(res["criterion"]["candidate"] == c) & (res["criterion"]["scope"] == s_)]
        assert list(got["verdict"]) == list(ref["verdict"])
    # a table not nested in m is a failed check, with no verdict
    bad = size.copy()
    sel = (bad["candidate"] == "cons_m1.5") & (bad["scope"] == "D") & (bad["null"] == "n2")
    bad.loc[sel, "count_k13"] = 1
    assert V.criterion_tables(bad, stats_, V.candidates_for(stats_), want)["failed"]
    # a null missing: NOT CHECKED, never a pass
    res = V.criterion_tables(size[size["null"] != "n4"], stats_, V.candidates_for(stats_), want)
    assert res["verdicts"][("cons_m1.25", "D")] == "NOT CHECKED"
    # beside: cons in both scopes, never a verdict
    assert set(res["beside"]["candidate"]) == {"cons_m1.25", "cons_m1.5", "cons"}
    assert set(res["beside"]["verdict"]) == {"beside: not the criterion"}


# ------------------------------------------------------------------------------------------------ end to end


def test_a_small_end_to_end_validation_writes_nothing(V, monkeypatch, tmp_path):
    C = V.CALQ
    before = {p for p in (ROOT / "results").rglob("*")} if (ROOT / "results").is_dir() else set()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(C, "SIZES", (200, 1000))
    monkeypatch.setattr(C, "N_CORE", 1)
    monkeypatch.setattr(C, "N_NONPERSISTENT", 1)
    monkeypatch.setattr(C, "CP_ONE", C.CP_ONE[:1])
    monkeypatch.setattr(C, "FLAT_L", (21,))
    monkeypatch.setattr(C, "DRIFT_SCENARIOS", ((0, "A", 500, 100, 0.02, False),))
    monkeypatch.setattr(C, "DRIFT_POPULATIONS", 1)
    monkeypatch.setattr(V, "N_SUBSETS_VAL", 1)
    tc = importlib.util.spec_from_file_location("q126_cal_tests_for_val", ROOT / "tests" / "test_q126_calibrate.py")
    T = importlib.util.module_from_spec(tc)
    sys.modules[tc.name] = T
    tc.loader.exec_module(T)
    p, days = T.synthetic_pairs(n_judged=130, per_session=10, sub=80)
    n = len(days)
    seeds = toy_seeds(V)
    stats_ = [("cons_m1.25", "D"), ("cons_m1.5", "Q")]
    cands = V.candidates_for(stats_)
    plan = V.core_plan(seeds)
    probs = C.provenance_problems(plan, seeds, set(seeds.values()), n_subsets=1, max_j=1)
    assert probs == [], probs[:3]
    inp = C.CAL.Inputs(p, n, seeds)
    out = C.compute_nulls("core", plan, inp, n, 200, cands, reps_beside=150, record=stats_, log=lambda m: None)
    assert not C.failed(out) and out["meta"]["scalar_checked"] > 500
    dr = C.compute_nulls("drift", V.drift_plan(seeds), None, n, 200, cands, drift_inputs=C.drift_inputs_for(n),
                         record=stats_, log=lambda m: None)
    size = pd.concat([pd.DataFrame(out["size"]), pd.DataFrame(dr["size"])], ignore_index=True)
    want = {"rule": sum(x["in_rule"] for x in plan)}
    res = V.criterion_tables(size, stats_, cands, want)
    assert res["failed"] == [] and set(res["verdicts"]) == set(stats_)
    assert all(v in V.VERDICTS for v in res["verdicts"].values())
    assert {r["candidate"] for r in out["cells"]} <= {"cons_m1.25", "cons_m1.5"}
    after = {p for p in (ROOT / "results").rglob("*")} if (ROOT / "results").is_dir() else set()
    assert after == before and list(tmp_path.iterdir()) == []
