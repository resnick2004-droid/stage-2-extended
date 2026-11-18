"""Q-82 (E-052): `scripts/q82_validation.py`, the pass line's fresh-seed validation -- built ready to run; never run on
the real pairs here. Synthetic inputs only.

What is asserted:
- **the seed map** is E-052's block 20262010-20262019 and nothing else: every null's generator entropy starts with its
  part's seed, no two nulls share an entropy, the tests' seed and the two spares are drawn by no null, no Q-16 seed is
  in the map, and no seed literal of the block appears in the script outside its seed map;
- **the block is unused elsewhere**: the run's own check refuses a file that names a seed of the block outside the
  item's files (code, data, results or a declaration, on any branch), not a document's mention; and it holds on this
  repository as it stands; after the run (Q-82b, E-093) its own results (`results/q82_*`, the manifest naming the
  script) may name the block, and a stray use in code, tests or another result file is still refused;
- **the criterion** (fixed in E-052): per statistic, HOLDS only if at every k in 11..15 no real or realistic null's 95 %
  interval (recomputed from the counts) lies wholly above nominal; FAILS on one such null; NOT CHECKED when a null is
  missing; the count-persistent rows and the members never move it;
- the judged session list's count and sha256 (ISO dates joined by "\\n"), refusing any count but 657;
- (i)'s null constructions are Q-16's: the streams, the offers and -- on Q-16's own seeds -- every rejection count of
  `t21w`, `t42w`, `t63w` and `cons` on every real and realistic null equal Q-16's code's (slow);
- (ii)'s thinning never reads the outcome: the kept counts are the same, draw for draw, whatever the outcomes;
- the vectorised decisions are the scalar functions F-02 calls (`bound`, `two_sample_bound`, `placebo_selection_bound`),
  and a planted disagreement is caught;
- the script refuses this tree's `results/` outside a clean run before any step, refuses a `lift_bound.py` other than
  the validated blob, asks the reader before the calendar read, and end to end at a tiny size writes its five result
  files with manifests, each with its seeds (slow).
Seeds: 20262010 (the map's tests seed), sub-streams by test.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
ENTRY = ROOT / "scripts" / "q82_validation.py"
SEED = 20262010
RESULTS = ("q82_validation_one_sample", "q82_validation_two_sample", "q82_count_persistent", "q82_criterion",
           "q82_judged_sessions")


def load_q82():
    spec = importlib.util.spec_from_file_location("q82_validation_t", ENTRY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def q82():
    return load_q82()


def _env():
    e = {k: v for k, v in os.environ.items() if k not in ("S2X_CLEAN_RUN", "S2X_RUN_ID")}
    e.setdefault("OMP_NUM_THREADS", "1")
    return e


def _run(args, timeout=900):
    return subprocess.run([sys.executable, *map(str, args)], cwd=str(ROOT), capture_output=True, text=True,
                          timeout=timeout, env=_env())


def synthetic_inputs(d: Path, per_session: int = 20):
    """657 judged weekdays from 2024-01-02 (and 255 before), `per_session` offers a judged session with both sides
    walked at 1, 1.5 and 3R (a session effect on the long side's chance), a few offers before the block (filtered out);
    the pairs folder as `scripts/q16_p16_pairs.py` writes it. Returns (pairs dir, days CSV, days parquet, calendar)."""
    rng = np.random.default_rng([SEED, 1])
    days = pd.bdate_range("2023-01-02", periods=262 + 657).strftime("%Y-%m-%d")
    before = [x for x in days if x < "2024-01-02"][:255]
    judged = [x for x in days if x >= "2024-01-02"][:657]
    allc = before + judged
    csv = d / "days.csv"
    pd.DataFrame({"date": allc}).to_csv(csv, index=False)
    pq_days = d / "days.parquet"
    pd.DataFrame({"date": allc, "day_kind": "n"}).to_parquet(pq_days, index=False)
    rows = []
    for dt in before[-3:] + judged:
        a = rng.standard_normal() * 0.5
        for j in range(per_session):
            slot = 15 * j
            r = {"date": dt, "day_kind": "n", "slot": slot, "entry_slot": slot + 1, "coin": int(rng.choice([-1, 1]))}
            for R in (1.0, 1.5, 3.0):
                kl = int(rng.random() < 1 / (1 + np.exp(-a)) * 0.9)
                ks = int(rng.random() < 1 / (1 + np.exp(a)) * 0.9)
                if not kl and rng.random() < 0.2:
                    kl = 2
                if not ks and rng.random() < 0.2:
                    ks = 2
                r[f"kl_{R:g}"], r[f"ks_{R:g}"] = kl, ks
                r[f"rl_{R:g}"] = float(R - 0.05) if kl == 1 else (float(rng.uniform(-1, R)) if kl == 2 else -1.05)
                r[f"rs_{R:g}"] = float(R - 0.05) if ks == 1 else (float(rng.uniform(-1, R)) if ks == 2 else -1.05)
                r[f"xl_{R:g}"] = slot + 1 + int(rng.integers(5, 60))
                r[f"xs_{R:g}"] = slot + 1 + int(rng.integers(5, 60))
            rows.append(r)
    pairs = pd.DataFrame(rows)
    pdir = d / "pairs"
    pdir.mkdir()
    pq = pdir / "p16_pairs.parquet"
    pairs.to_parquet(pq, index=False)
    (pdir / "p16_pairs.json").write_text(json.dumps({
        "identity": "HOLDS: synthetic (test)", "parquet_sha256": hashlib.sha256(pq.read_bytes()).hexdigest(),
        "trades_sha256": "synthetic"}), encoding="utf-8")
    return pdir, csv, pq_days, judged


# ------------------------------------------------------------------------------------------------ the seed map


def test_the_seed_map_is_e052s_block(q82):
    block = tuple(range(20262010, 20262020))
    assert q82.SEED_BLOCK == block
    used = list(q82.SEEDS.values())
    assert len(set(used)) == len(used) and set(used) | set(q82.SPARE) == set(block)
    assert not set(used) & set(q82.SPARE)
    assert not set(used) & set(range(20261910, 20261920))          # none of Q-16's
    plan = q82.null_plan()
    ent = [tuple(x["entropy"]) for x in plan]
    assert len(set(ent)) == len(ent), "two nulls share a generator entropy"
    first = {e[0] for e in ent}
    assert SEED not in first and not first & set(q82.SPARE)
    for x in plan:
        assert x["entropy"][0] == q82.SEEDS[q82.PART_SEED[x["part"]][x["family"]]], x["null"]
    src = ENTRY.read_text(encoding="utf-8")
    lines = src.splitlines()
    first = next(i for i, x in enumerate(lines, 1) if x.startswith("# ---- the seed map (E-052) ----"))
    last = next(i for i, x in enumerate(lines, 1) if x.startswith("# ---- end of the seed map ----"))
    lits = [(node.lineno, node.value) for node in ast.walk(ast.parse(src)) if isinstance(node, ast.Constant)
            and isinstance(node.value, int) and 20262000 <= node.value <= 20262099]
    assert lits and all(first < ln < last for ln, _ in lits), f"a seed literal outside the seed map: {lits}"
    assert {v for _, v in lits} == set(block)


def test_the_null_plan_counts(q82):
    plan = q82.null_plan()
    crit = [x for x in plan if x["in_criterion"]]
    by = {}
    for x in crit:
        by[x["function"]] = by.get(x["function"], 0) + 1
    assert by == {"bound": 95, "two_sample_bound": 56, "placebo_selection_bound": 55} == q82.EXPECTED_NULLS
    one = [x for x in crit if x["function"] == "bound"]
    assert sum(x["group"] == "real" for x in one) == 70 and sum(x["group"] == "realistic synthetic" for x in one) == 25
    assert {x["q16"]["model"] for x in one if x["group"] != "real"} == {"iid", "cluster", "cluster_ar1", "regime01",
                                                                         "volclust"}
    beside = [x for x in plan if not x["in_criterion"]]
    assert beside and all(x["group"].startswith("count-persistent") for x in beside)
    names = {x["null"] for x in beside}
    for need in ("cp:ar98s15:200:win1:persist1", "cp:burst10x:5000:win1:persist1", "cpsyn:ar98s15:2",
                 "cpsyn:burst10x:0.3", "cpsyn_c1p:ar98s15:1", "cp_c1p:ar98s15:1000:win1:shared1",
                 "cp_select:burst10x:0.05:win1"):
        assert need in names, need


def _git(repo, *a):
    r = subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


def test_the_seed_block_check(q82, tmp_path):
    t = tmp_path / "repo"
    t.mkdir()
    _git(t, "init", "-q", "-b", "master")
    _git(t, "config", "user.email", "t@example.invalid")
    _git(t, "config", "user.name", "t")
    (t / "scripts").mkdir()
    (t / "scripts" / "q82_validation.py").write_text("SEEDS = {'a': 20262011}\n", encoding="utf-8")
    (t / "notes.md").write_text("the block 20262010-20262019 is reserved\n", encoding="utf-8")
    (t / "other.py").write_text("SEED = 202620111\n", encoding="utf-8")       # not word-bounded: not a use
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "c")
    probs, notes = q82.seed_block_problems(t)
    assert probs == [] and any("notes.md" in n for n in notes)
    (t / "prereg").mkdir()
    (t / "prereg" / "F-98_y.md").write_text("the pin waits for Q-83 (seeds 20262010-20262019)\n", encoding="utf-8")
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "a declaration citing the run")
    probs, notes = q82.seed_block_problems(t)
    assert probs == [] and any("F-98_y.md" in n for n in notes)       # a citation of this run reserves nothing
    _git(t, "checkout", "-q", "-b", "side")
    (t / "prereg" / "F-99_x.md").write_text("seeds 20262016\n", encoding="utf-8")
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "a declaration reserving one")
    _git(t, "checkout", "-q", "master")
    probs, _ = q82.seed_block_problems(t)
    assert any("F-99_x.md" in p and "side" in p for p in probs)
    assert not any("F-98_y.md" in p for p in probs)
    (t / "uses.py").write_text("rng = default_rng(20262014)\n", encoding="utf-8")   # uncommitted, untracked
    probs, _ = q82.seed_block_problems(t)
    assert any(p.startswith("uses.py") or "uses.py" in p for p in probs)


def _result(d: Path, name: str, script: str, result_file: str | None = None) -> None:
    """A result file and its manifest as the writer leaves them, its seed recorded."""
    (d / "results").mkdir(exist_ok=True)
    (d / "results" / f"{name}.csv").write_text("null,seed\nx,20262011\n", encoding="utf-8")
    (d / "results" / f"{name}.csv.manifest.json").write_text(json.dumps(
        {"result_file": result_file or f"{name}.csv", "script": script, "seed": 20262011,
         "parameters": {"seeds": {"lift_real": 20262011}}}, indent=2), encoding="utf-8")


def test_after_the_run_its_results_may_name_the_block_and_nothing_else_may(q82, tmp_path):
    """Q-82b (E-093): once Q-83 has run, its results (`results/q82_*`, the manifest naming the script) and the audits'
    and reviews' documents name the block; a stray use in code or tests, or any other result file, is still refused --
    in the working tree or on a branch."""
    t = tmp_path / "repo"
    t.mkdir()
    _git(t, "init", "-q", "-b", "master")
    _git(t, "config", "user.email", "t@example.invalid")
    _git(t, "config", "user.name", "t")
    _result(t, "q82_validation_one_sample", "scripts/q82_validation.py")
    for sub in ("audits", "reviews"):
        (t / "docs" / sub).mkdir(parents=True)
        (t / "docs" / sub / "Q-83.md").write_text("Q-83 drew seeds 20262011-20262017\n", encoding="utf-8")
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "the run's results and their audit")
    probs, notes = q82.seed_block_problems(t)
    assert probs == [], probs
    assert any("q82_validation_one_sample.csv (" in n for n in notes)
    assert any("q82_validation_one_sample.csv.manifest.json" in n for n in notes)
    # a stray code use and a test that draws from the block: refused, though the run's results stay allowed
    (t / "extended").mkdir()
    (t / "extended" / "stray.py").write_text("rng = default_rng([20262013, 1])\n", encoding="utf-8")
    (t / "tests").mkdir()
    (t / "tests" / "test_other.py").write_text("SEED = 20262019\n", encoding="utf-8")
    probs, _ = q82.seed_block_problems(t)
    assert any("extended/stray.py" in p for p in probs) and any("tests/test_other.py" in p for p in probs)
    assert not any("q82_validation_one_sample" in p for p in probs)
    for f in ("extended/stray.py", "tests/test_other.py"):
        (t / f).unlink()
    # another result naming the block, a q82_ name written by another script, a q82_ file with no manifest: refused
    _git(t, "checkout", "-q", "-b", "side")
    _result(t, "f02_stage_a", "scripts/f02.py")
    _result(t, "q82_impostor", "scripts/other.py")
    _result(t, "q82_mislabelled", "scripts/q82_validation.py", result_file="something_else.csv")
    (t / "results" / "q82_orphan.csv").write_text("seed\n20262012\n", encoding="utf-8")
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "second uses")
    _git(t, "checkout", "-q", "master")
    probs, _ = q82.seed_block_problems(t)
    for bad in ("f02_stage_a.csv", "q82_impostor.csv", "q82_mislabelled.csv", "q82_orphan.csv"):
        assert any(bad in p and "side" in p for p in probs), (bad, probs)
    assert not any("q82_validation_one_sample" in p for p in probs)


def test_the_seed_block_is_unused_in_this_repository(q82):
    probs, _ = q82.seed_block_problems(ROOT)
    assert probs == [], probs


# ------------------------------------------------------------------------------------------------ the criterion


def _rows(q82, nulls_by_fn, k_above=None, drop=None, members_lax=False, beside_lax=False):
    rows = []
    for fn, n in nulls_by_fn.items():
        for i in range(n):
            null = f"{fn}:{i}"
            if drop and null == drop:
                continue
            for k in (11, 12, 13, 14, 15):
                a = 0.05 / (k * (k + 1))
                rej = 200 if (k_above and (fn, i, k) == k_above) else 0      # 1e-3: wholly above every family level
                for m in ("t21w", "t42w", "t63w", "cons"):
                    r = rej if m == "cons" else (200 if members_lax else 0)
                    rows.append({"null": null, "function": fn, "in_criterion": True, "method": m, "level": a, "k": k,
                                 "reps": 200_000, "rejections": r, "ci_lo": 0.0, "group": "real"})
    if beside_lax:
        for k in (11, 12, 13, 14, 15):
            rows.append({"null": "cp:x", "function": "bound", "in_criterion": False, "method": "cons",
                         "level": 0.05 / (k * (k + 1)), "k": k, "reps": 200_000, "rejections": 500, "ci_lo": 0.9,
                         "group": "count-persistent real"})
    return pd.DataFrame(rows)


def test_the_criterion(q82):
    full = dict(q82.EXPECTED_NULLS)
    v = q82.verdicts(q82.criterion(_rows(q82, full, members_lax=True, beside_lax=True)))
    assert v == {"bound": "HOLDS", "two_sample_bound": "HOLDS", "placebo_selection_bound": "HOLDS"}
    v = q82.verdicts(q82.criterion(_rows(q82, full, k_above=("two_sample_bound", 7, 13))))
    assert v == {"bound": "HOLDS", "two_sample_bound": "FAILS", "placebo_selection_bound": "HOLDS"}
    v = q82.verdicts(q82.criterion(_rows(q82, full, drop="bound:3")))
    assert v["bound"] == "NOT CHECKED" and v["two_sample_bound"] == "HOLDS"
    c = q82.criterion(_rows(q82, full, k_above=("bound", 0, 15), beside_lax=True))
    row = c[(c["statistic"] == "bound") & (c["k"].astype(str) == "15")].iloc[0]
    assert row["verdict"] == "FAILS" and row["nulls_above"] == 1 and row["worst_null"] == "bound:0"
    assert row["nulls"] == 95
    ok = c[(c["statistic"] == "bound") & (c["k"].astype(str) == "14")].iloc[0]
    assert ok["verdict"] == "HOLDS"
    assert c[(c["statistic"] == "bound") & (c["k"].astype(str) == "11-15")].iloc[0]["verdict"] == "FAILS"
    # 30 of 200,000 at 0.05/240 (nominal 41.7 expected) is not above: the counts decide, not a planted ci_lo column
    df = _rows(q82, full)
    df.loc[df["method"] == "cons", "rejections"] = 30
    df.loc[df["method"] == "cons", "ci_lo"] = 1.0
    assert set(q82.verdicts(q82.criterion(df)).values()) == {"HOLDS"}
    beside = c[c["section"] == "beside"]
    assert len(beside) and (beside["verdict"].isin(["HOLDS", "FAILS"])).sum() == 0   # the beside rows carry no verdict
    assert (beside["nulls_above"] > 0).all()


# ------------------------------------------------------------------------------------------------ the session list


def test_the_judged_session_list(q82):
    before = pd.bdate_range("2023-06-01", "2023-12-29").strftime("%Y-%m-%d").tolist()
    judged = pd.bdate_range("2024-01-02", periods=657).strftime("%Y-%m-%d").tolist()
    assert judged[-1] <= "2026-07-16"
    cal, sha = q82.judged_sessions(list(reversed(before + judged)))
    assert cal == judged and sha == hashlib.sha256("\n".join(judged).encode("ascii")).hexdigest()
    assert len(sha) == 64
    for bad in (before + judged[:-1], judged + [judged[5]], [d.replace("-", "/") for d in judged]):
        with pytest.raises(SystemExit):
            q82.judged_sessions(bad)


# ------------------------------------------------------------------------------------------------ (i) is Q-16's


def test_streams_and_offers_are_q16s(q82, tmp_path):
    pdir, csv, pq_days, cal = synthetic_inputs(tmp_path)
    Q16 = q82.Q16
    Q16.DAYS_FILE = pq_days
    ref, n, _ = Q16.real_streams(pdir / "p16_pairs.parquet")
    p, _ = q82.load_pairs(pdir / "p16_pairs.parquet", cal)
    mine = q82.lift_streams(p, Q16.SEED_LIFT_REAL)
    assert n == len(cal) == 657 and list(mine) == list(ref)
    for k in ref:
        for a, b in zip(ref[k], mine[k]):
            assert np.array_equal(a, b), k
    O = Q16.judged_offers(pdir / "p16_pairs.parquet")
    O2 = q82.judged_offers(p, len(cal))
    assert set(O) == set(O2)
    for k in O:
        assert np.array_equal(np.asarray(O[k]), np.asarray(O2[k])), k


@pytest.mark.slow
def test_same_nulls_as_q16_on_q16s_seeds(q82, tmp_path):
    """On Q-16's seeds, this script's real and realistic nulls give Q-16's code's rejection counts exactly -- so on
    E-052's seeds they are the same constructions, freshly drawn."""
    pdir, csv, pq_days, cal = synthetic_inputs(tmp_path)
    Q16 = q82.Q16
    Q16.DAYS_FILE = pq_days
    reps = 300
    out = tmp_path / "q16"
    out.mkdir()
    pq = pdir / "p16_pairs.parquet"
    a = argparse.Namespace(out=str(out), pairs=str(pq), synthetic_only=False, reps=reps, boot_reps=0)
    Q16.lift_part(a, lambda m: None)
    a2 = argparse.Namespace(out=str(out), pairs=str(pq), reps=reps, diff_df="treated", power_reps=40)
    Q16.select_part(a2, lambda m: None)
    p, _ = q82.load_pairs(pq, cal)
    key = ["null", "method", "lv"]
    for part, ref_file in (("i_lift", "lift_size.csv"), ("i_two", "diff_size.csv")):
        rows, meta = q82.compute_part(part, p, cal, reps, seeds=q82.Q16_LAYOUT_SEEDS, log=lambda m: None)
        mine = pd.DataFrame(rows)
        ref = pd.read_csv(out / ref_file, float_precision="round_trip")
        ref = ref[ref["method"].isin(["t21w", "t42w", "t63w", "cons"])]
        for df in (mine, ref):
            df["lv"] = df["level"].map(lambda x: f"{x:.12g}")
        mine = mine[mine["lv"].isin(set(ref["lv"]))]                   # Q-16 has no 0.01 level; this script adds it
        assert mine["lv"].nunique() == 8
        j = mine.merge(ref[key + ["rejections"]], on=key, how="left", suffixes=("", "_q16"))
        assert j["rejections_q16"].notna().all(), j[j["rejections_q16"].isna()]["null"].unique()[:5]
        assert (j["rejections"] == j["rejections_q16"]).all(), j[j["rejections"] != j["rejections_q16"]].head()
        assert j["null"].nunique() == (95 if part == "i_lift" else 111)
        assert j["rejections"].sum() > 0                               # the comparison is not of zeros only
        assert meta["scalar_mismatched"] == 0 and meta["scalar_checked"] > 0
        assert len(mine) == len(mine.drop_duplicates(key))


# ------------------------------------------------------------------------------------------------ (ii) outcome-free


def test_count_persistent_thinning_never_reads_the_outcome(q82, tmp_path):
    pdir, csv, pq_days, cal = synthetic_inputs(tmp_path, per_session=12)
    p, _ = q82.load_pairs(pdir / "p16_pairs.parquet", cal)
    p2 = p.copy()
    g = np.random.default_rng([SEED, 2])
    for c in ("kl_1", "ks_1", "kl_3", "ks_3"):
        p2[c] = g.integers(0, 3, size=len(p2))                       # unrelated outcomes, the same offers
    for c in ("rl_3", "rs_3"):
        p2[c] = g.normal(size=len(p2)).astype(np.float32)
    plan = {x["null"]: x for x in q82.null_plan()}
    for name in ("cp:ar98s15:1000:win1:persist1", "cp:burst10x:200:net3:persist1", "cp_c1p:ar98s10:500:win1:shared1",
                 "cp_select:ar98s15:0.1:win1"):
        outs = []
        for frame in (p, p2):
            data = q82.Data(frame, cal)
            gen = q82.generator(plan[name], data)
            outs.append(gen(np.random.default_rng(plan[name]["entropy"]), 64))
        if len(outs[0]) == 2:
            (S_a, N_a), (S_b, N_b) = outs
            assert np.array_equal(N_a, N_b), name
            assert not np.array_equal(S_a, S_b), name
        else:
            (A1, B1, C1, D1), (A2, B2, C2, D2) = outs
            assert np.array_equal(B1, B2), name                       # sample 1's counts
            if "c1p" in name:
                assert np.array_equal(D1, D2), name                   # the placebo's counts
            assert not np.array_equal(A1, A2), name


# ------------------------------------------------------------------------------------------------ the scalar functions


def test_the_vectorised_decisions_are_the_scalar_functions(q82):
    import extended.lift_bound as LB

    n = 657
    g = np.random.default_rng([SEED, 3])
    reps = 40
    N = g.poisson(0.8, size=(n, reps)).astype(float)
    S = 0.5 * (2 * g.binomial(N.astype(int), 0.5) - N) + 0.12 * N * (np.arange(reps) % 2)[None, :]
    lev = LB.family_level(11)
    fam = list(q82.FAMILY_LEVELS)
    rj = np.vstack([LB.many_levels(m, S, N, [lev])[0] for m in q82.MEMBERS])
    cons = rj.all(axis=0)
    assert 0 < cons.sum() < reps
    for j in range(reps):
        assert q82.redecide_one(S, N, j, n, lev) == bool(cons[j])
    cons5 = LB.many_levels(q82.MEMBERS[0], S, N, fam)[0]
    for m in q82.MEMBERS[1:]:
        cons5 = cons5 & LB.many_levels(m, S, N, fam)[0]
    assert np.array_equal(cons5, LB.many_levels("cons", S, N, fam)[0])
    N2 = g.poisson(4.0, size=(n, reps)).astype(float)
    S2 = 0.5 * (2 * g.binomial(N2.astype(int), 0.5) - N2)
    rj2 = np.vstack([LB.diff_many_levels(m, S, N, S2, N2, [lev], df_rule="treated")[0] for m in q82.MEMBERS]).all(0)
    for j in range(reps):
        assert q82.redecide_two(S, N, S2, N2, j, n, lev) == bool(rj2[j])
    M = g.integers(5, 40, size=n)
    C = g.binomial(M, 0.5).astype(float)[:, None]
    B = np.minimum(g.binomial(np.repeat(M[:, None], reps, 1), 0.2), M[:, None] - 1)   # a session never all selected
    A = g.hypergeometric(np.repeat(C.astype(int), reps, 1), np.repeat((M[:, None] - C).astype(int), reps, 1), B)
    A = A + (B * 0.25 * (np.arange(reps) % 2)[None, :]).round()
    A = np.minimum(A, B).astype(float)
    Mf = M[:, None].astype(float)
    rj3 = np.vstack([LB.diff_many_levels(m, A, B.astype(float), C, Mf, [lev], df_rule="treated")[0]
                     for m in q82.MEMBERS]).all(0)
    assert rj3.any()
    for j in range(reps):
        assert q82.redecide_sel(A, B.astype(float), C, Mf, j, n, lev) == bool(rj3[j])
    # a planted disagreement is counted: the vectorised side flipped for one replication at one level
    checked, bad = q82.scalar_check("one-sample", (S, N), cons5, n, first=reps)
    assert checked == 5 * reps and bad == 0
    flipped = cons5.copy()
    flipped[2, 0] = not flipped[2, 0]
    checked, bad = q82.scalar_check("one-sample", (S, N), flipped, n, first=reps)
    assert bad == 1
    # only the replications that reject at a family level are re-decided after the first few
    checked, bad = q82.scalar_check("one-sample", (S, N), cons5, n, first=0)
    assert checked == 5 * int(cons5.any(axis=0).sum()) and bad == 0
    for form, arrs in (("two-sample", (S, N, S2, N2)), ("placebo-selection", (A, B.astype(float), C, Mf))):
        dec = np.ones((5, reps), dtype=bool)
        for m in q82.MEMBERS:
            dec &= LB.diff_many_levels(m, *arrs, fam, df_rule="treated")[0]
        checked, bad = q82.scalar_check(form, arrs, dec, n, first=reps)
        assert checked == 5 * reps and bad == 0, form


# ------------------------------------------------------------------------------------------------ refusals and reads


def test_refuses_this_trees_results_outside_a_clean_run():
    r = _run([ENTRY], timeout=300)
    assert r.returncode == 3 and "REFUSED" in r.stdout and "clean" in r.stdout, r.stdout[-2000:] + r.stderr[-2000:]
    assert "step" not in r.stdout.lower().split("refused")[0]


def test_refuses_a_lift_bound_other_than_the_validated_blob(q82, tmp_path):
    assert q82.module_blob_problems() == []
    f = tmp_path / "lift_bound.py"
    f.write_bytes((ROOT / "extended" / "lift_bound.py").read_bytes() + b"\n# changed\n")
    probs = q82.module_blob_problems({"extended/lift_bound.py": (f, q82.VALIDATED_BLOBS["extended/lift_bound.py"])})
    assert probs and "lift_bound" in probs[0]


def test_asks_the_reader_before_the_calendar_read():
    """Q-158 (the reader's held-out rule 3): the judged calendar read under E-035, a row without a read token, is now
    refused by the reader before anything is read; a row whose token is `heldout-read: P-16 by
    scripts/q82_validation.py` (the lead's) would admit one run of it, inside a clean run."""
    r = _run([ENTRY, "--check-read"], timeout=300)
    out = r.stdout + r.stderr
    assert "reader: purpose=registered_design declaration=E-035 design=P-16" in out, out[-2000:]
    assert "data/atlas/A1/days.parquet" in out
    assert r.returncode == 3 and "REFUSED (held-out rule 3" in out and "AUTHORISED" not in out, out[-2000:]


@pytest.mark.slow
def test_end_to_end_at_a_tiny_size(tmp_path):
    pdir, csv, pq_days, cal = synthetic_inputs(tmp_path)
    res = tmp_path / "results"
    r = _run([ENTRY, "--results-dir", res, "--work", tmp_path / "work", "--pairs", pdir, "--days", csv,
              "--reps", "300"], timeout=1800)
    assert r.returncode == 0, r.stdout[-4000:] + r.stderr[-3000:]
    assert "EXIT 0" in r.stdout
    for label in ("bound", "two_sample_bound", "placebo_selection_bound"):
        assert re.search(rf"criterion \(E-052\) {label}: (HOLDS|FAILS|NOT CHECKED)", r.stdout), label
    seeds_seen = {}
    for name in RESULTS:
        csvp, man = res / f"{name}.csv", res / f"{name}.csv.manifest.json"
        assert csvp.is_file() and man.is_file(), name
        m = json.loads(man.read_text(encoding="utf-8"))
        assert m["sha256"] == hashlib.sha256(csvp.read_bytes()).hexdigest(), name
        assert "seeds" in m["parameters"], name
        seeds_seen[name] = m["parameters"]["seeds"]
        assert m["parameters"]["pairs_supplied"] is True and m["parameters"]["days_supplied"] is True
    assert set(seeds_seen["q82_validation_one_sample"].values()) == {20262011, 20262012}
    assert set(seeds_seen["q82_validation_two_sample"].values()) == {20262013, 20262014}
    assert set(seeds_seen["q82_count_persistent"].values()) == {20262015, 20262016, 20262017}
    sess = pd.read_csv(res / "q82_judged_sessions.csv", dtype=str)
    assert sess["date"].tolist() == cal
    pm = json.loads((res / "q82_judged_sessions.csv.manifest.json").read_text(encoding="utf-8"))["parameters"]
    assert pm["count"] == 657 and pm["sha256_dates_joined_lf"] == hashlib.sha256("\n".join(cal).encode()).hexdigest()
    one = pd.read_csv(res / "q82_validation_one_sample.csv", low_memory=False)
    assert one["null"].nunique() == 95 and set(one["method"]) == {"t21w", "t42w", "t63w", "cons"}
    two = pd.read_csv(res / "q82_validation_two_sample.csv", low_memory=False)
    assert two["null"].nunique() == 111
    cp = pd.read_csv(res / "q82_count_persistent.csv", low_memory=False)
    assert not cp["in_criterion"].any() and cp["null"].nunique() == len([x for x in load_q82().null_plan()
                                                                         if not x["in_criterion"]])
    crit = pd.read_csv(res / "q82_criterion.csv", low_memory=False)
    main_rows = crit[crit["section"] == "criterion"]
    assert set(main_rows["statistic"]) == {"bound", "two_sample_bound", "placebo_selection_bound"}
    assert len(main_rows) == 3 * 6                                      # k = 11..15 and the overall row
