"""Q-108 (E-115): `scripts/q108_validate.py`, the validation runner -- built ready to run, never run on the real
pairs here; it refuses until a decision row records the calibration's choice. Synthetic inputs only. Seeds: 20262120
(the validation build's tests, the plan's 4.1).

What is asserted:
- **the seed map** is the validation block's table and nothing else (the plan's 4.1): every null of the validation's
  plan draws a validation seed, the tests' seed and the two spares by no null, no calibration seed anywhere in it, no
  literal of the calibration block in the script and the validation block's only in its seed-map section; the
  validation's nulls are the calibration's, null for null; it draws no reference table of its own;
- **the choosing row**: refused with no row, with a row whose pin does not match, with a choice file that is not the
  calibration's own from a clean run, with a `lift_one_sample.py` other than the one the calibration ran, and with the
  choice NONE (the validation block retired); accepted when every condition holds;
- **the criterion** (the plan's 4.3) on planted tables: HOLDS; FAILS on a Monte Carlo null at the failure count (and
  not one below it), on an exact size above nominal, on one rejecting alternating configuration; NOT CHECKED with a
  null missing; C0's, the other scope's and the beside nulls' laxity never moves it;
- **a scalar disagreement** stops the validation with no verdict (E-115 (R1));
- **the refusals** before any step: outside a clean run; without the choosing row.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
ENTRY = ROOT / "scripts" / "q108_validate.py"
SEED = 20262120


def load_val():
    name = "q108_validate_t"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ENTRY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def V():
    return load_val()


def _env():
    e = {k: v for k, v in os.environ.items() if k not in ("S2X_CLEAN_RUN", "S2X_RUN_ID")}
    e.setdefault("OMP_NUM_THREADS", "1")
    return e


# ------------------------------------------------------------------------------------------------ the seed map


def test_the_seed_map_is_the_validation_block(V):
    C = V.CAL
    assert V.SEEDS == {"tests": 20262120, "fixed_mc": 20262121, "subsets": 20262122, "subset_mc": 20262123,
                       "synthetic": 20262124, "beside_cp": 20262125, "beside_flat": 20262126, "exact_sample": 20262127}
    assert V.SPARE == (20262128, 20262129)
    assert set(V.SEEDS.values()) | set(V.SPARE) == set(C.VAL_BLOCK)
    assert "sn_table" not in V.SEEDS                                          # C8's table is the calibration's
    assert C.seed_map_problems(V.SEEDS, C.VAL_BLOCK, V.VAL_ROLES + ("tests",)) == []
    plan = C.null_plan(V.SEEDS)
    firsts = set()
    for x in plan:
        for key in ("entropy", "subset_entropy", "sample_entropy"):
            if x[key]:
                firsts.add(x[key][0])
    assert firsts <= set(C.VAL_BLOCK) and SEED not in firsts and not firsts & set(V.SPARE)
    assert not firsts & set(C.CAL_BLOCK)
    assert [x["null"] for x in plan] == [x["null"] for x in C.null_plan()]   # the same nulls, null for null
    ents = [tuple(x["entropy"]) for x in plan if x["entropy"]]
    assert len(set(ents)) == len(ents)
    src = ENTRY.read_text(encoding="utf-8")
    lines = src.splitlines()
    first = next(i for i, x in enumerate(lines, 1) if x.startswith("# ---- the validation seed map"))
    last = next(i for i, x in enumerate(lines, 1) if x.startswith("# ---- end of the validation seed map"))
    lits = [(node.lineno, node.value) for node in ast.walk(ast.parse(src)) if isinstance(node, ast.Constant)
            and isinstance(node.value, int) and 20262000 <= node.value <= 20262199]
    assert lits and all(first < ln < last for ln, _ in lits), lits
    assert {v for _, v in lits} == set(C.VAL_BLOCK)                          # no calibration seed in the script


def test_the_validation_draws_no_reference_table(V, monkeypatch, capsys):
    from extended import results as XR

    monkeypatch.setattr(XR, "clean_run_problem", lambda: None)
    assert V.main(["--compute", "sn", "--work", str(ROOT.parent / "nowhere")]) == 3
    assert "REFUSED" in capsys.readouterr().out


# ------------------------------------------------------------------------------------------------ the choosing row


def _calibration_files(V, repo: Path, decision: str, *, script=None, clean=True, exploratory=False):
    from extended import results as XR

    C = V.CAL
    res = repo / "results"
    choice = pd.DataFrame([{"row": "candidate", "candidate": "cons_m1.5", "scope": "Q", "decision": None},
                           {"row": "decision", "decision": decision, "candidate": None, "scope": None}])
    table = pd.DataFrame([{"level": a, "critical": 10.0 + i} for i, a in enumerate(C.LEVELS)])
    blob = C.blob_id(ROOT / C.MODULE)
    prov = {"clean_run": {"name": "q108-calibrate"}} if clean else None
    for df, nm in ((choice, "q108_choice"), (table, "q108_sn_table")):
        XR.write_result(df, nm, script=script or C.SCRIPT, seed=None, require_seed=False, results_dir=res,
                        parameters={"blobs": {C.MODULE: blob}}, provenance=prov, exploratory=exploratory)
    (repo / "extended").mkdir(exist_ok=True)
    shutil.copy(ROOT / C.MODULE, repo / C.MODULE)
    return {nm: hashlib.sha256((res / f"{nm}.csv").read_bytes()).hexdigest() for nm in ("q108_choice", "q108_sn_table")}


def _row(sha_c, sha_s):
    return (f"| E-999 | 2026-11-17 | **The choice:** `results/q108_choice.csv` sha256 `{sha_c}` and C8's reference "
            f"`results/q108_sn_table.csv` sha256 `{sha_s}`. | the calibration |\n")


def test_the_choosing_row(V, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    sha = _calibration_files(V, repo, "CHOSEN cons_m1.5 (scope Q)")
    (repo / "DECISIONS.md").write_text("| E-115 | 2026-11-16 | the plan pinned | x |\n", encoding="utf-8")
    probs, _ = V.choice_problems(repo)
    assert probs and "no decision row records the choice" in probs[0]
    (repo / "DECISIONS.md").write_text(_row("0" * 64, sha["q108_sn_table"]), encoding="utf-8")
    probs, _ = V.choice_problems(repo)
    assert any("does not hash to E-999's pin" in p for p in probs)
    (repo / "DECISIONS.md").write_text(_row(sha["q108_choice"], sha["q108_sn_table"]), encoding="utf-8")
    probs, info = V.choice_problems(repo)
    assert probs == [] and info["chosen"] == "cons_m1.5" and info["scope"] == "Q" and info["row"] == "E-999"
    # the statistic is the code the calibration ran
    (repo / "extended" / "lift_one_sample.py").write_text("# changed\n", encoding="utf-8")
    probs, _ = V.choice_problems(repo)
    assert any("the calibration ran" in p for p in probs)


@pytest.mark.parametrize("kw,why", [({"script": "scripts/other.py"}, "not scripts/q108_calibrate.py"),
                                    ({"clean": False}, "not written inside a clean run"),
                                    ({"exploratory": True}, "exploratory")])
def test_a_choice_not_the_calibrations_own_is_refused(V, tmp_path, kw, why):
    repo = tmp_path / "repo"
    repo.mkdir()
    sha = _calibration_files(V, repo, "CHOSEN cons_m1.5 (scope Q)", **kw)
    (repo / "DECISIONS.md").write_text(_row(sha["q108_choice"], sha["q108_sn_table"]), encoding="utf-8")
    probs, _ = V.choice_problems(repo)
    assert any(why in p for p in probs), probs


def test_none_retires_the_validation_block(V, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    sha = _calibration_files(V, repo, "NONE")
    (repo / "DECISIONS.md").write_text(_row(sha["q108_choice"], sha["q108_sn_table"]), encoding="utf-8")
    probs, _ = V.choice_problems(repo)
    assert probs and "retired, never drawn" in probs[0]


# ------------------------------------------------------------------------------------------------ the criterion


def _planted(V, cands=("cons_m1.5", "cons"), mc=3, exact=("flip42", "alt55")):
    C = V.CAL
    rows = []

    def add(**kw):
        r = dict(kw)
        r.update({f"count_{lab}": 0 for lab in C.LABELS})
        r.update({f"ratio_{lab}": 0.0 for lab in C.LABELS})
        rows.append(r)

    for c in cands:
        for s_ in C.SCOPES:
            for i in range(mc):
                add(null=f"mc{i}", kind="mc", group="subset", in_rule=True, model="markov80", candidate=c, scope=s_,
                    denominator=200_000)
            for m in exact:
                add(null=f"ex:{m}", kind="exact", group="subset", in_rule=True, model=m, candidate=c, scope=s_,
                    denominator=42 * 2 ** 17 if m.startswith("flip") else 110)
            add(null="cp:x", kind="mc", group="beside_cp", in_rule=False, model="ar98s15", candidate=c, scope=s_,
                denominator=100_000)
    return pd.DataFrame(rows)


def _set(df, c, s_, null, lab, x):
    df.loc[(df["candidate"] == c) & (df["scope"] == s_) & (df["null"] == null), f"count_{lab}"] = x


def _verdict(V, df, want):
    crit = V.criterion(df, "cons_m1.5", "Q", want)
    return str(crit[crit["k"].astype(str) == "13-20"]["verdict"].iloc[0]), crit


def test_the_criterion(V):
    C = V.CAL
    want = {"rule": 5}
    df = _planted(V)
    v, crit = _verdict(V, df, want)
    assert v == "HOLDS" and len(crit) == 9
    # C0 lax on every null, a beside null lax, the other scope lax: none of them moves it
    for null in ("mc0", "mc1", "ex:flip42"):
        _set(df, "cons", "Q", null, "k13", 500)
    _set(df, "cons_m1.5", "Q", "cp:x", "k13", 900)
    _set(df, "cons_m1.5", "D", "mc0", "k13", 900)
    assert _verdict(V, df, want)[0] == "HOLDS"
    # a Monte Carlo null at the failure count fails; one below it does not
    _set(df, "cons_m1.5", "Q", "mc2", "k17", C.FAIL[17] - 1)
    assert _verdict(V, df, want)[0] == "HOLDS"
    _set(df, "cons_m1.5", "Q", "mc2", "k17", C.FAIL[17])
    v, crit = _verdict(V, df, want)
    assert v == "FAILS" and crit[crit["k"].astype(str) == "17"]["failing_nulls"].iloc[0] == "mc2"
    assert crit[crit["k"].astype(str) == "16"]["verdict"].iloc[0] == "HOLDS"
    _set(df, "cons_m1.5", "Q", "mc2", "k17", 0)
    # an exact size above nominal fails: 700 of 42 x 2^17 is 1.27e-4 > 1.19e-4 at k = 20
    _set(df, "cons_m1.5", "Q", "ex:flip42", "k20", 700)
    v, crit = _verdict(V, df, want)
    assert v == "FAILS" and crit[crit["k"].astype(str) == "20"]["failing_nulls"].iloc[0] == "ex:flip42"
    _set(df, "cons_m1.5", "Q", "ex:flip42", "k20", 600)                       # 1.09e-4: at or below nominal
    assert _verdict(V, df, want)[0] == "HOLDS"
    # one rejecting configuration of an alternating model fails
    _set(df, "cons_m1.5", "Q", "ex:alt55", "k13", 1)
    assert _verdict(V, df, want)[0] == "FAILS"
    _set(df, "cons_m1.5", "Q", "ex:alt55", "k13", 0)
    # a missing null: NOT CHECKED, never a pass
    short = df[~((df["candidate"] == "cons_m1.5") & (df["scope"] == "Q") & (df["null"] == "mc1"))]
    assert _verdict(V, short, want)[0] == "NOT CHECKED"
    assert _verdict(V, df, {"rule": 6})[0] == "NOT CHECKED"


def test_a_scalar_disagreement_stops_the_validation(V):
    part = {"size": [], "power": [], "mismatches": [{"null": "x", "candidate": "cons_m1.5", "scope": "Q",
                                                     "replication": 3, "k": 13, "vectorised": True, "scalar": False}],
            "meta": {"nesting_violations": []}}
    out = V.validate_tables([part], "cons_m1.5", "Q", ["cons_m1.5", "cons"])
    assert out["failed"] and "R1" in out["failed"][0] and "verdict" not in out


# ------------------------------------------------------------------------------------------------ the refusals


def test_refuses_outside_a_clean_run_before_any_step():
    r = subprocess.run([sys.executable, str(ENTRY)], cwd=str(ROOT), capture_output=True, text=True, timeout=300,
                       env=_env())
    assert r.returncode == 3 and "REFUSED" in r.stdout and "clean run" in r.stdout, r.stdout[-2000:] + r.stderr
    assert "step" not in r.stdout.lower()


def test_refuses_until_the_choosing_row_exists(V, monkeypatch, capsys):
    from extended import results as XR

    monkeypatch.setattr(XR, "clean_run_problem", lambda: None)
    # state-independent (E-151, as Q-113): the log as it would be with no choosing row, whatever the real log now records
    monkeypatch.setattr(V, "choosing_row", lambda text: (None, None, None))
    assert V.main([]) == 3
    out = capsys.readouterr().out
    assert "REFUSED" in out and "no decision row records the choice" in out and "step" not in out
