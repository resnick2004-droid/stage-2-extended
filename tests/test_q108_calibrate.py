"""Q-108 (E-115): `scripts/q108_calibrate.py`, the calibration runner -- built ready to run, never run on the real
pairs here. Synthetic inputs only. Seeds: 20262110 (the calibration build's tests, the plan's 4.1), sub-streams by
test; the toy runs' seed maps lie outside the 2026 space (81080110 and up).

What is asserted:
- **the seed map** is the calibration block's table and nothing else: each role's seed as the plan's 4.1, the spare
  and the tests' seed drawn by no null, every null's entropy starting with its role's seed, no two nulls sharing an
  entropy, every index order of 4.1 (the fixed streams' i, the subsets', the exact nulls' 0..1,169, the `flat` form's
  0..29, the count-persistent nulls' 0..53, the synthetic nulls' Q-16 index), and no literal of either block outside
  the script's seed-block section;
- **the null plan's counts** are the plan's 3.5 (2,293 in the rule, 1,170 exact, 1,123 Monte Carlo; 54 and 30
  beside) and its toys the plan's 5;
- **the seed guard** (the plan's 4.1, on Q-82b's pattern): a literal of either block refused outside the allow-list,
  on any branch or in the working tree; a document's mention printed; a declaration's refused; this run's own results
  printed, an impostor's refused; NAME + constants folded and refused when it lands in a block; a bounded `range` or
  `enumerate` over a literal refused when it reaches a block and passed when not; an unbounded loop index printed,
  never refused; an imported name not folded; and on this repository nothing refused, the cut loops still on a ref
  printed (three at most) and each matched to the hand-check record -- whose expressions are those of the calibration
  run's own commit, the working tree's file holding none since Q-128 made its walks children of their seed (E-171) --
  which also holds the imported offsets the plan and E-115 list, each checked;
- **the failure counts** (71, 63, 56, 50, 45, 41, 38, 35) and **P_MC's dynamic program**, against the plan's
  arithmetic script and against a nested-binomial simulation;
- **the choice rule on planted tables**: the most powerful eligible candidate in scope Q; ties to fewer members, then
  the earlier row; C0 never in scope Q; each of the three conditions refusing (an MC point rate above nominal, an exact
  size above nominal, an alternating configuration rejecting, P_MC below 0.9, the worst exact ratio above a quarter --
  with the refused-candidate report), the quarter on a fixed-stream exact null too (E-115 (R2)); scope D only when
  scope Q has none; NONE;
- **the refusals**: outside a clean run (before any step), a result that exists, a seed map off the block, a changed
  pinned file, a calendar other than E-094's; a scalar disagreement and a count rising with k stop the run with no
  choice;
- **the constructions**: the fixed streams are Q-16's; the side draws never read an outcome; the count-persistent
  generator is Q-82's, draw for draw; on Q-16's own seeds the fixed-stream and synthetic nulls give Q-16's rejection
  counts;
- **a small end-to-end calibration on toy streams** -- every part, every candidate, both scopes, the exact
  enumeration and its re-decision, the power, the choice -- that writes nothing.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from extended import git_scan as GS

ROOT = Path(__file__).resolve().parent.parent
ENTRY = ROOT / "scripts" / "q108_calibrate.py"
SEED = 20262110
TOY = 81080110


def load_cal():
    name = "q108_calibrate_t"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ENTRY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def C():
    # Q-156: the runner's seed scans (`git grep` over every ref) through `extended.git_scan` -- a time limit, the process
    # tree killed and an error on it, never a pass; the runner's file (pinned by blob) is not edited
    mod = load_cal()
    with pytest.MonkeyPatch.context() as mp:
        GS.route_scans(mp, mod)
        yield mod


def _env():
    e = {k: v for k, v in os.environ.items() if k not in ("S2X_CLEAN_RUN", "S2X_RUN_ID")}
    e.setdefault("OMP_NUM_THREADS", "1")
    return e


def _git(repo, *a):
    r = subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


def _repo(tmp_path):
    t = tmp_path / "repo"
    t.mkdir()
    _git(t, "init", "-q", "-b", "master")
    _git(t, "config", "user.email", "t@example.invalid")
    _git(t, "config", "user.name", "t")
    return t


def _write(t: Path, rel: str, text: str):
    p = t / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def toy_seeds(C):
    s = {r: TOY + i for i, r in enumerate(C.CAL_ROLES)}
    s["tests"] = TOY + 40
    return s


def synthetic_pairs(n_judged: int = 657, per_session: int = 6, sub: int = 1, before: int = 0):
    """Synthetic P-16 pairs on `n_judged` judged weekdays from 2024-01-02 (and `before` days before): `per_session`
    offers a session, both sides walked at 1, 1.5 and 3R with a session effect. Returns (pairs frame as Q-82's
    `load_pairs` gives it, judged calendar, the raw frame and the full calendar)."""
    rng = np.random.default_rng([SEED, sub])
    days = pd.bdate_range("2023-01-02", periods=262 + n_judged).strftime("%Y-%m-%d").tolist()
    pre = [x for x in days if x < "2024-01-02"][-before:] if before else []
    judged = [x for x in days if x >= "2024-01-02"][:n_judged]
    rows = []
    for dt in pre + judged:
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
    raw = pd.DataFrame(rows)
    p = raw[(raw["date"] >= "2024-01-02")].sort_values(["date", "slot"], kind="stable").reset_index(drop=True)
    pos = {d: i for i, d in enumerate(judged)}
    p["session"] = p["date"].map(pos).astype(np.int64)
    return p, judged, raw, pre + judged


# ------------------------------------------------------------------------------------------------ the seed map


def test_the_seed_map_is_the_calibration_block(C):
    assert C.CAL_BLOCK == tuple(range(20262110, 20262120)) and C.VAL_BLOCK == tuple(range(20262120, 20262130))
    assert C.SEEDS == {"tests": 20262110, "fixed_mc": 20262111, "subsets": 20262112, "subset_mc": 20262113,
                       "synthetic": 20262114, "sn_table": 20262115, "beside_cp": 20262116, "beside_flat": 20262117,
                       "exact_sample": 20262118}
    assert C.SPARE == (20262119,)
    assert set(C.SEEDS.values()) | set(C.SPARE) == set(C.CAL_BLOCK)
    assert C.seed_map_problems(C.SEEDS, C.CAL_BLOCK, C.CAL_ROLES + ("tests",)) == []
    plan = C.null_plan()
    ents = [tuple(x["entropy"]) for x in plan if x["entropy"]]
    assert len(set(ents)) == len(ents), "two nulls share a generator entropy"
    firsts = {e[0] for e in ents} | {x["subset_entropy"][0] for x in plan if x["subset_entropy"]} \
        | {x["sample_entropy"][0] for x in plan if x["sample_entropy"]}
    assert SEED not in firsts and not firsts & set(C.SPARE) and firsts <= set(C.CAL_BLOCK)
    assert C.SEEDS["sn_table"] not in firsts                                   # drawn by the reference only
    role = {"fixed": "fixed_mc", "subset": "subset_mc", "synthetic": "synthetic", "beside_cp": "beside_cp",
            "beside_flat": "beside_flat"}
    for x in plan:
        if x["entropy"]:
            assert x["entropy"][0] == C.SEEDS[role[x["group"]]], x["null"]
        if x["subset_entropy"]:
            assert x["subset_entropy"] == [C.SEEDS["subsets"], x["z_index"], x["j"]]
        if x["sample_entropy"]:
            assert x["sample_entropy"] == [C.SEEDS["exact_sample"], x["exact_index"]]
    src = ENTRY.read_text(encoding="utf-8")
    lines = src.splitlines()
    first = next(i for i, x in enumerate(lines, 1) if x.startswith("# ---- the seed blocks"))
    last = next(i for i, x in enumerate(lines, 1) if x.startswith("# ---- end of the seed blocks"))
    lits = [(node.lineno, node.value) for node in ast.walk(ast.parse(src)) if isinstance(node, ast.Constant)
            and isinstance(node.value, int) and 20262000 <= node.value <= 20262199]
    assert lits and all(first < ln < last for ln, _ in lits), f"a seed literal outside the seed blocks: {lits}"
    assert {v for _, v in lits} == set(C.CAL_BLOCK) | {20262120, 20262129}    # the validation block's extent only


def test_a_seed_map_off_the_block_is_refused(C):
    bad = dict(C.SEEDS, subset_mc=20262123)                                     # a validation seed
    assert any("subset_mc" in p for p in C.seed_map_problems(bad, C.CAL_BLOCK, C.CAL_ROLES))
    bad = dict(C.SEEDS, fixed_mc=C.SEEDS["subsets"])
    assert any("share" in p for p in C.seed_map_problems(bad, C.CAL_BLOCK, C.CAL_ROLES))
    bad = {k: v for k, v in C.SEEDS.items() if k != "beside_flat"}
    assert any("beside_flat" in p for p in C.seed_map_problems(bad, C.CAL_BLOCK, C.CAL_ROLES))


def test_the_index_orders(C):
    plan = {x["null"]: x for x in C.null_plan()}
    fx = [x for x in plan.values() if x["group"] == "fixed" and x["kind"] == "mc"]
    assert sorted(x["entropy"][1] for x in fx) == list(range(28))
    assert plan["fixed:offered:win1:flip1"]["entropy"] == [20262111, 0]
    assert plan["fixed:offered:win1:markov80"]["entropy"] == [20262111, 6]
    assert plan["fixed:taken:win1:flip1"]["entropy"] == [20262111, 14]
    assert plan["fixed:taken:net3:markov80"]["entropy"] == [20262111, 27]
    assert plan["sub:2000:03:net3:coin"]["entropy"] == [20262113, 3, 3, 1, 6]
    assert "sub:2000:17:net3:coin" not in plan and "sub:2000:17:net3:markov50" in plan   # coin: the first 5 only
    assert plan["sub:200:00:win1:markov30"]["entropy"] == [20262113, 0, 0, 0, 9]
    ex = [x for x in plan.values() if x["kind"] == "exact"]
    assert sorted(x["exact_index"] for x in ex) == list(range(1170))
    assert plan["fixed:offered:win1:flip42"]["exact_index"] == 0
    assert plan["fixed:offered:win1:alt55"]["exact_index"] == 4
    assert plan["fixed:offered:net3:flip42"]["exact_index"] == 5
    assert plan["fixed:taken:net3:alt55"]["exact_index"] == 19
    assert plan["sub:200:00:win1:flip42"]["exact_index"] == 20
    assert plan["sub:5000:22:net3:alt55"]["exact_index"] == 1169
    fl = sorted((x["entropy"][1], x["null"]) for x in plan.values() if x["group"] == "beside_flat")
    assert [i for i, _ in fl] == list(range(30)) and fl[0][1] == "flat:200:win1:flip21" \
        and fl[1][1] == "flat:200:net3:flip21" and fl[29][1] == "flat:5000:net3:flip63"
    cp = [x for x in C.null_plan() if x["group"] == "beside_cp"]
    assert [x["entropy"][1] for x in cp] == list(range(54))
    assert [x["null"] for x in cp] == [f"cp:{p}:{T}:{v}:persist{L}" for p, T, v, L in C.Q82.CP_ONE]
    syn = [x for x in C.null_plan() if x["group"] == "synthetic"]
    q16 = [sp["null"] for sp in C.Q16.syn_specs()]
    assert [x["entropy"][1] for x in syn] == [q16.index(x["null"]) for x in syn]
    assert C.MODELS == ("flip1", "flip5", "flip21", "flip42", "flip55", "flip63", "coin", "alt45", "alt55",
                        "markov30", "markov50", "markov80")


def test_the_null_plan_counts(C):
    want = {"rule": 2293, "rule_exact": 1170, "rule_mc": 1123, "beside_cp": 54, "beside_flat": 30}
    assert C.expected_counts() == want == C.EXPECTED
    plan = C.null_plan()
    rule = [x for x in plan if x["in_rule"]]
    for m in C.PERSISTENT:
        assert sum(x["model"] == m and x["group"] == "subset" for x in rule) == 115 * 2, m
        assert sum(x["model"] == m and x["group"] == "fixed" for x in rule) == 4, m
    for m in C.NONPERSISTENT:
        assert sum(x["model"] == m and x["group"] == "subset" for x in rule) == 25 * 2, m
    assert sum(x["group"] == "synthetic" for x in rule) == 25
    toys = [x for x in plan if x["toy"]]
    assert sum(x["toy"] == "P" for x in toys) == 10 and sum(x["toy"] == "net3" for x in toys) == 10
    assert [x["null"] for x in toys if x["toy"] == "cluster"] == ["syn:cluster:1000"]
    assert all(x["j"] == 0 and x["model"] in ("coin", "flip1") and x["value"] == "win1" for x in toys
               if x["toy"] == "P")
    assert {x["part"] for x in plan} == set(C.PARTS)


# ------------------------------------------------------------------------------------------------ the seed guard


def test_the_guard_on_literals(C, tmp_path):
    t = _repo(tmp_path)
    _write(t, "scripts/q108_calibrate.py", "SEEDS = {'a': 20262111}\n")             # allowed
    _write(t, "docs/notes.md", "the blocks 20262110-20262129 are reserved\n")       # a document's mention
    _write(t, "other.py", "SEED = 202621111\n")                                     # not word-bounded
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "c")
    probs, notes = C.literal_problems(t)
    assert probs == [] and any("notes.md" in n for n in notes)
    _write(t, "prereg/F-98_y.md", "seeds 20262125\n")                               # a declaration reserving one
    probs, _ = C.literal_problems(t)
    assert any("F-98_y.md" in p for p in probs)
    (t / "prereg" / "F-98_y.md").unlink()
    _git(t, "checkout", "-q", "-b", "side")
    _write(t, "extended/stray.py", "rng = default_rng([20262113, 1])\n")
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "a stray use")
    _git(t, "checkout", "-q", "master")
    probs, _ = C.literal_problems(t)
    assert any("extended/stray.py" in p and "side" in p for p in probs)
    _write(t, "uses.py", "rng = default_rng(20262127)\n")                           # untracked, the working tree
    probs, _ = C.literal_problems(t)
    assert any("uses.py" in p and "working tree" in p for p in probs)


def _result(d: Path, name: str, script: str, result_file: str | None = None) -> None:
    _write(d, f"results/{name}.csv", "null,seed\nx,20262111\n")
    _write(d, f"results/{name}.csv.manifest.json", json.dumps(
        {"result_file": result_file or f"{name}.csv", "script": script, "seed": 20262111,
         "parameters": {"seeds": {"fixed_mc": 20262111}}}, indent=2))


def test_the_runs_own_results_may_name_the_block_and_nothing_else_may(C, tmp_path):
    t = _repo(tmp_path)
    _result(t, "q108_cal_size", "scripts/q108_calibrate.py")
    _result(t, "q108_val_size", "scripts/q108_validate.py")
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "the runs' results")
    probs, notes = C.literal_problems(t)
    assert probs == [], probs
    assert any("q108_cal_size.csv (" in n for n in notes) and any("q108_val_size.csv.manifest" in n for n in notes)
    _git(t, "checkout", "-q", "-b", "side")
    _result(t, "f05_stage_a", "scripts/f05.py")
    _result(t, "q108_impostor", "scripts/other.py")
    _result(t, "q108_mislabelled", "scripts/q108_calibrate.py", result_file="else.csv")
    _write(t, "results/q108_orphan.csv", "seed\n20262112\n")
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "other uses")
    _git(t, "checkout", "-q", "master")
    probs, _ = C.literal_problems(t)
    for bad in ("f05_stage_a.csv", "q108_impostor.csv", "q108_mislabelled.csv", "q108_orphan.csv"):
        assert any(bad in p and "side" in p for p in probs), (bad, probs)
    assert not any("q108_cal_size" in p for p in probs)


def test_the_guard_folds_derived_seeds(C, tmp_path):
    t = _repo(tmp_path)
    code = "\n".join([
        "BASE = 20262100",
        "A, B = 20262090, 7",
        "lands = BASE + 15",                                       # 20262115: the calibration block -> refused
        "misses = BASE + 30",                                      # 20262130: above both -> nothing
        "also = A + 2 * 20",                                       # 20262130 -> nothing
        "for i in range(5):",
        "    f(BASE + 10 + i)",                                    # 20262110..14 -> refused
        "for i in range(3):",
        "    f(BASE + i)",                                         # ..00..02 -> nothing
        "for i, x in enumerate(stuff):",
        "    f(BASE + 2 + i)",                                     # unbounded, near -> printed, not refused
        "for i, d in enumerate(('a', 'b')):",
        "    f(BASE + 50 + i)",                                    # bounded ..150..151 -> nothing
        "for i, d in enumerate(['a', 'b', 'c']):",
        "    f(BASE + 18 + i)",                                    # bounded 20262118..120 -> refused
        "g = [BASE + 25 + k for k in range(4)]",                   # a comprehension: 20262125..128 -> refused
        "h = mod.SEED + 15",                                       # an imported name: not folded
        "w = seed + 1 + i",                                        # a runtime argument: not folded (no constant)
    ]) + "\n"
    _write(t, "x.py", code)
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "c")
    probs, prints = C.derived_problems(t)
    got = sorted(p.split("`")[1] for p in probs)                          # each blob read once: no repeats
    assert got == sorted(["BASE + 15", "BASE + 10 + i", "BASE + 18 + i", "BASE + 25 + k"]), probs
    assert len(prints) == 1 and "BASE + 2 + i" in prints[0] and "NOT in the hand-check record" in prints[0]
    assert "reach of 8" in prints[0]
    # on a branch only: still refused, naming the branch
    _git(t, "checkout", "-q", "-b", "side")
    _write(t, "y.py", "S = 20262000\nseed = S + 121\n")
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "side")
    _git(t, "checkout", "-q", "master")
    probs, _ = C.derived_problems(t)
    assert any("y.py" in p and "side" in p and "S + 121" in p for p in probs)


def test_the_guard_on_this_repository_and_the_hand_check_record(C):
    probs, notes = C.seed_block_problems(ROOT)
    assert probs == [], probs
    printed = [n for n in notes if n.startswith("derived seed") and "`" in n]
    # Q-128 (E-171): the walks are SeedSequence children now; an older blob on another ref may still print, never more
    # than the three recorded, each hand-checked
    assert len(printed) <= 3 and all("hand-checked" in n for n in printed), printed
    far = [n for n in notes if n.startswith("derived seed") and "more unbounded expression" in n]
    assert len(far) <= 1                                                  # the rest lie over PRINT_REACH away
    want = {("tests/test_features_lookahead.py", e) for e in ("SEED_REPLACE + i", "SEED_REPLACE + 200 + i",
                                                              "SEED_REPLACE + 1000 + i")}
    assert {(h["file"], h["expr"]) for h in C.HAND_CHECKED} == want
    # each recorded expression is in its file as the calibration ran it (the commit its result's manifest names); the
    # working tree's file has none of them since Q-128 (E-171)
    ran = json.loads((ROOT / "results" / "q108_cal_size.csv.manifest.json").read_text(encoding="utf-8"))["git_commit"]
    for f, e in want:
        r = subprocess.run(["git", "show", f"{ran}:{f}"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0, r.stderr
        assert any(x.expr == e for x in C.fold_file(r.stdout, f)), e
        assert not any(x.expr == e for x in C.fold_file((ROOT / f).read_text(encoding="utf-8"), f)), e
    # the imported offsets of the plan's 4.1 and E-115, each where the record says and each checked
    rec = {h["expr"]: h for h in C.HAND_CHECKED_IMPORTED}
    for e in ("R.F.LADDER_SEED + i", "fh.SEED + 1, fh.SEED + 2", "sc.SEED + 1", "pe.SEED + 100_000 * i + 1_000 * j",
              "seed + 1 + i", "a.seed + ...", "seed + 1000 * G + lags"):
        assert e in rec, e
    vend = ROOT / "vendor" / "stage2"
    assert "fh.SEED + 1, fh.SEED + 2" in (vend / "scripts" / "hypo_firm_h.py").read_text(encoding="utf-8")
    assert "sc.SEED + 1" in (vend / "scripts" / "score_im2.py").read_text(encoding="utf-8")
    assert "pe.SEED + 100_000 * i + 1_000 * j" in (vend / "scripts" / "l5_planted_effect.py").read_text(
        encoding="utf-8")
    pe_src = (vend / "propedge" / "research" / "planted_effect.py").read_text(encoding="utf-8")
    assert "seed=seed + 1 + i" in pe_src and "for i in range(replications)" in pe_src

    def const(path: Path, name: str) -> int:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        return next(int(n.value.value) for n in ast.walk(tree) if isinstance(n, ast.Assign)
                    and any(isinstance(x, ast.Name) and x.id == name for x in n.targets))

    res = {x % 1000 for x in C.CAL_BLOCK + C.VAL_BLOCK}                       # the blocks' residues mod 1,000
    pe = const(vend / "propedge" / "research" / "planted_effect.py", "SEED")
    assert pe % 1000 not in res                                               # + 100,000 i + 1,000 j never lands
    assert not ({(pe + 1 + i) % 1000 for i in range(200)} & res)              # E-115's nested offset
    for mod in ("firm_h", "im2_score"):
        s = const(vend / "propedge" / "research" / f"{mod}.py", "SEED")
        assert s + 2 < min(C.CAL_BLOCK)
    import extended.lift_bound as LB
    assert (LB.FIXED_B_SEED + 2) % 1000 not in res                            # + 1,000 G + lags, lags = 2
    r = subprocess.run(["git", "show", "refs/heads/wt/wt-firms:scripts/rd01_reading.py"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode == 0:
        assert "R.F.LADDER_SEED + i" in r.stdout


# ------------------------------------------------------------------------------------------------ the DP


def _arith():
    spec = importlib.util.spec_from_file_location("q108_arith_t", ROOT / "docs/calibration/scripts/q108/q108_arith.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_failure_counts_and_the_dynamic_program(C):
    assert [C.FAIL[k] for k in range(13, 21)] == [71, 63, 56, 50, 45, 41, 38, 35]
    A = _arith()
    nom = [0.05 / (k * (k + 1)) for k in range(13, 21)]
    profiles = [[r * a for a in nom] for r in (0.3, 0.7, 0.9, 1.0)]
    profiles.append([0.95 * a * (0.97 ** i) for i, a in enumerate(nom)])
    profiles.append([0.8 * a for a in nom[:4]] + [0.0] * 4)
    g = np.random.default_rng([SEED, 30])
    for i, rates in enumerate(profiles):
        dp = C.p_holds(rates)
        assert abs(dp - A.p_holds(rates, C.FAIL)) < 1e-12, i
        # a nested-binomial simulation of the validation criterion, count by count
        M = 400_000
        x = g.binomial(200_000, rates[0], size=M)
        ok = x < C.FAIL[13]
        for j, k in enumerate(range(14, 21), start=1):
            q = rates[j] / rates[j - 1] if rates[j - 1] > 0 else 0.0
            x = g.binomial(x, q)
            ok &= x < C.FAIL[k]
        sim = ok.mean()
        assert abs(sim - dp) < 4 * math.sqrt(max(dp * (1 - dp), 1e-9) / M) + 1e-6, (i, dp, sim)
    assert C.p_holds([0.0] * 8) == 1.0
    with pytest.raises(ValueError):
        C.p_holds([1e-4, 2e-4] + [1e-4] * 6)                                  # rising rates: not nested


# ------------------------------------------------------------------------------------------------ the choice rule


LABS = None


def _planted(C, mc_nulls=4, exact_models=("flip42", "alt45")):
    """A size table with every candidate at zero rejections on `mc_nulls` Monte Carlo nulls and one exact null per
    model, both scopes; and power rows giving each candidate a P."""
    rows = []
    for c in C.O.NAMES:
        for s_ in C.SCOPES:
            for i in range(mc_nulls):
                r = {"null": f"mc{i}", "kind": "mc", "group": "subset", "in_rule": True, "model": "markov50",
                     "candidate": c, "scope": s_, "denominator": 200_000}
                r.update({f"count_{lab}": 0 for lab in C.LABELS})
                rows.append(r)
            for m in exact_models:
                den = 42 * 2 ** 17 if m.startswith("flip") else 90
                r = {"null": f"ex:{m}", "kind": "exact", "group": "subset", "in_rule": True, "model": m,
                     "candidate": c, "scope": s_, "denominator": den}
                r.update({f"count_{lab}": 0 for lab in C.LABELS})
                rows.append(r)
    return pd.DataFrame(rows)


def _power(C, P: dict):
    rows = []
    for c in C.O.NAMES:
        for s_ in C.SCOPES:
            for t in range(10):
                for k in C.POWER_KS:
                    rows.append({"row": "toy", "null": f"toy{t}", "toy": "P", "candidate": c, "scope": s_, "k": k,
                                 "mdl50": P[c] / 2, "mdl80": P[c] * (1.1 if t % 2 else 1 / 1.1)})
    return pd.DataFrame(rows)


def _set(df, c, s_, null, counts):
    sel = (df["candidate"] == c) & (df["scope"] == s_) & (df["null"] == null)
    for lab, x in zip(load_cal().FAM_LABELS, counts):
        df.loc[sel, f"count_{lab}"] = x


BASE_P = {"cons": 1.0, "cons_m1.25": 1.25, "cons_m1.5": 1.5, "cons_m1.75": 1.75, "cons_m2": 2.0, "cons_bm": 1.01,
          "cons_bm_m1.25": 1.26, "cons_im": 1.02, "sn": 1.1, "cons_sn": 1.1}


def _choose(C, size, P):
    return C.choose(C.eligibility(size, C.O.NAMES), C.power_summary(_power(C, P), C.O.NAMES))


def test_the_choice_rule_picks_the_most_powerful_eligible_candidate(C):
    size = _planted(C)
    ch = _choose(C, size, BASE_P)
    assert ch["line"] == "CHOSEN cons_bm (scope Q)"                       # C0 (1.0) is not eligible in scope Q
    t = ch["table"]
    assert not t[(t["candidate"] == "cons") & (t["scope"] == "Q")]["eligible"].iloc[0]
    assert t[(t["candidate"] == "cons") & (t["scope"] == "D")]["eligible"].iloc[0]
    ps = C.power_summary(_power(C, BASE_P), C.O.NAMES)
    assert abs(float(ps[(ps["candidate"] == "sn") & (ps["scope"] == "Q")]["P"].iloc[0]) - 1.1) < 1e-12
    assert abs(float(ps[(ps["candidate"] == "cons_m2") & (ps["scope"] == "Q")]["P_rel_C0"].iloc[0]) - 2.0) < 1e-12
    # ties: fewer members first, then the earlier row
    P = dict(BASE_P, cons_bm=1.25, sn=1.25, cons_im=2.0, cons_sn=2.0)
    assert _choose(C, size, P)["line"] == "CHOSEN sn (scope Q)"           # 1 member against 3
    P = dict(BASE_P, cons_bm=1.25, sn=3.0, cons_im=3.0, cons_sn=3.0)
    assert _choose(C, size, P)["line"] == "CHOSEN cons_m1.25 (scope Q)"    # C1 before C5 at the same P and members


def test_each_condition_refuses(C):
    size = _planted(C)
    # (1) an MC point rate above nominal at k = 20 (24 > 23.8 of 200,000)
    _set(size, "cons_bm", "Q", "mc0", [24] * 8)
    # (1) an exact size above nominal: flip42, 1,000 of 42 x 2^17 is about 1.8e-4 > 1.19e-4 at k = 20
    _set(size, "cons_im", "Q", "ex:flip42", [1000] * 8)
    # (1) an alternating configuration rejecting: 1 / 90
    _set(size, "cons_m1.25", "Q", "ex:alt45", [1] * 8)
    # (3) the quarter: 270 of 42 x 2^17 is 4.9e-5 -- below nominal at every k, 0.41 x nominal at k = 20
    _set(size, "sn", "Q", "ex:flip42", [270] * 8)
    ch = _choose(C, size, BASE_P)
    t = ch["table"].set_index(["candidate", "scope"])
    assert not t.loc[("cons_bm", "Q"), "cond1_floors"] and t.loc[("cons_bm", "Q"), "mc_worst_k"] == 20
    assert not t.loc[("cons_im", "Q"), "cond1_floors"] and not t.loc[("cons_m1.25", "Q"), "cond1_floors"]
    assert t.loc[("sn", "Q"), "cond1_floors"] and t.loc[("sn", "Q"), "cond2_p_mc"]
    assert not t.loc[("sn", "Q"), "cond3_ratio"] and t.loc[("sn", "Q"), "refused_by_cond3_alone"]
    w = 270 / (42 * 2 ** 17) / (0.05 / 420)
    assert abs(t.loc[("sn", "Q"), "worst_exact_ratio"] - w) < 1e-12 and t.loc[("sn", "Q"), "worst_exact_k"] == 20
    assert t.loc[("sn", "Q"), "worst_null_flip42"] == "ex:flip42"
    assert ch["line"] == "CHOSEN cons_sn (scope Q)"                       # the next most powerful (1.1, 4 members)
    assert ch["refused"]["Q"]["candidate"] == "sn" and abs(ch["refused"]["Q"]["P"] - 1.1) < 1e-12
    assert "mdl50_k13_geomean" in ch["refused"]["Q"] and "mdl80_k20_geomean" in ch["refused"]["Q"]
    fr = C.choice_frame(ch)
    assert fr[fr["row"] == "decision"]["decision"].iloc[0] == "CHOSEN cons_sn (scope Q)"
    assert fr[fr["row"] == "refused_by_cond3_alone"]["candidate"].tolist() == ["sn"]
    # (2) P_MC below 0.9: five nulls each just below nominal at every k (none above it)
    size = _planted(C, mc_nulls=5)
    for i in range(5):
        _set(size, "cons_bm", "Q", f"mc{i}", [54, 47, 41, 36, 32, 29, 26, 23])
    ch = _choose(C, size, BASE_P)
    t = ch["table"].set_index(["candidate", "scope"])
    want = C.p_holds([x / 200_000 for x in (54, 47, 41, 36, 32, 29, 26, 23)]) ** 5
    assert abs(t.loc[("cons_bm", "Q"), "p_mc"] - want) < 1e-12 and want < 0.9
    assert t.loc[("cons_bm", "Q"), "cond1_floors"] and not t.loc[("cons_bm", "Q"), "cond2_p_mc"]
    assert ch["line"] == "CHOSEN cons_im (scope Q)"


def test_the_quarter_binds_on_the_fixed_stream_exact_nulls_too(C):
    """E-115 (R2): condition 3 is over every exactly enumerated calibration null, the fixed-data streams' included,
    though their sizes repeat at validation; its cost shows in the refused-candidate report."""
    size = _planted(C)
    fx = size[size["null"] == "ex:flip42"].copy()
    fx["null"], fx["group"] = "fixed:offered:win1:flip42", "fixed"
    size = pd.concat([size, fx], ignore_index=True)
    _set(size, "cons_bm", "Q", "fixed:offered:win1:flip42", [270] * 8)       # 0.41 x nominal at k = 20
    ch = _choose(C, size, BASE_P)
    t = ch["table"].set_index(["candidate", "scope"])
    assert t.loc[("cons_bm", "Q"), "refused_by_cond3_alone"]
    assert t.loc[("cons_bm", "Q"), "worst_exact_null"] == "fixed:offered:win1:flip42"
    assert ch["line"] == "CHOSEN cons_im (scope Q)" and ch["refused"]["Q"]["candidate"] == "cons_bm"


def test_scope_d_only_when_scope_q_has_none_and_none_at_all(C):
    size = _planted(C)
    for c in C.O.NAMES:
        _set(size, c, "Q", "ex:flip42", [5000] * 8)                         # every scope-Q statistic above nominal
    ch = _choose(C, size, BASE_P)
    assert ch["line"] == "CHOSEN cons (scope D)"                          # C0 is eligible in scope D
    for c in C.O.NAMES:
        _set(size, c, "D", "ex:alt45", [1] * 8)
    ch = _choose(C, size, BASE_P)
    assert ch["line"] == "NONE" and ch["chosen"] is None
    assert C.choice_frame(ch)[lambda d: d["row"] == "decision"]["decision"].iloc[0] == "NONE"


# ------------------------------------------------------------------------------------------------ the failed checks


def _toy_inputs(C, n=130, per=10):                                        # 1,300 offers: subsets up to 1,000
    p, judged, _, _ = synthetic_pairs(n_judged=n, per_session=per, sub=40)
    return p, len(judged)


def test_a_count_rising_with_k_stops_the_run(C):
    e = {"null": "x"}
    res = {"counts": {("cons", "Q"): np.array([3, 3, 4, 2, 2, 1, 0, 0, 9, 9, 9, 9]),
                      ("cons", "D"): np.array([3, 3, 3, 2, 2, 1, 0, 0, 9, 9, 9, 9])}}
    probs = C.nesting_problems(e, res, ["cons"])
    assert len(probs) == 1 and "scope Q" in probs[0]
    part = {"size": [], "power": [], "mismatches": [], "meta": {"nesting_violations": probs}}
    out = C.calibrate_tables([part], ["cons"])
    assert out["failed"] and "nesting" in out["failed"][0] and "choice" not in out


def test_a_scalar_disagreement_stops_the_run(C, monkeypatch):
    p, n = _toy_inputs(C)
    real = C.O.bound_1s_levels
    hits = {"n": 0}

    def wrong(name, *a, **kw):
        out = real(name, *a, **kw)
        hits["n"] += 1
        if hits["n"] == 1:                                                    # one planted disagreement
            b = out[0]
            out[0] = C.O.Bound1S(b.candidate, b.level, -1.0 if b.rejects else 1.0, b.members, b.trades)
        return out

    monkeypatch.setattr(C.O, "bound_1s_levels", wrong)
    seeds = toy_seeds(C)
    only = {"syn:iid:200", "syn:iid:500"}
    res = C.compute_part("syn", None, n, 200, seeds, ["cons", "cons_m1.5"], None, only=only, log=lambda m: None)
    mm = res["mismatches"]                                                # one flipped decision, seen in both
    assert len(mm) == 2 and {m["scope"] for m in mm} == {"Q", "D"}        # scopes (a synthetic null: admitted)
    assert len({(m["replication"], m["k"], m["candidate"]) for m in mm}) == 1
    assert res["meta"]["nulls_done"] == 1 and res["meta"]["stopped_after"] == "syn:iid:200"
    out = C.calibrate_tables([res], ["cons", "cons_m1.5"])
    assert out["failed"] and "R1" in out["failed"][0] and "choice" not in out


# ------------------------------------------------------------------------------------------------ the refusals


def test_refuses_outside_a_clean_run_before_any_step():
    r = subprocess.run([sys.executable, str(ENTRY)], cwd=str(ROOT), capture_output=True, text=True, timeout=300,
                       env=_env())
    assert r.returncode == 3 and "REFUSED" in r.stdout and "clean run" in r.stdout, r.stdout[-2000:] + r.stderr
    assert "step" not in r.stdout.lower()


def test_the_preflight_refusals(C, monkeypatch, tmp_path, capsys):
    from extended import results as XR

    monkeypatch.setattr(XR, "clean_run_problem", lambda: None)
    assert C.preflight(tmp_path) == []
    (tmp_path / "q108_choice.csv").write_text("x\n", encoding="utf-8")
    assert any("never overwritten" in p for p in C.preflight(tmp_path))
    (tmp_path / "q108_choice.csv").unlink()
    monkeypatch.setattr(C, "SEEDS", dict(C.SEEDS, exact_sample=20262127))
    assert any("exact_sample" in p for p in C.preflight(tmp_path))
    monkeypatch.setattr(C, "SEEDS", load_cal().SEEDS)
    monkeypatch.setattr(C, "VALIDATED_BLOBS", {"extended/lift_bound.py": "0" * 40})
    assert any("lift_bound" in p for p in C.preflight(tmp_path))
    monkeypatch.setattr(C, "VALIDATED_BLOBS", {"extended/lift_bound.py": "984f3467a4a05aa790d3ea43e94ac7761f0725b2"})
    monkeypatch.setattr(C, "PLAN_SHA256", "0" * 64)
    assert any("pin" in p for p in C.preflight(tmp_path))
    # main() stops at the first refusal, before any step
    monkeypatch.setattr(C, "SEEDS", dict(C.SEEDS, fixed_mc=20262121))
    assert C.main([]) == 3
    out = capsys.readouterr().out
    assert "REFUSED" in out and "step" not in out


def test_a_calendar_other_than_e094s_is_refused(C):
    cal = pd.bdate_range("2024-01-02", periods=657).strftime("%Y-%m-%d").tolist()
    sha = hashlib.sha256("\n".join(cal).encode("ascii")).hexdigest()
    assert C.calendar_problems(cal, sha)                                       # weekdays are not A1's stored days
    assert C.calendar_problems(cal[:-1], C.JUDGED_SHA256)
    assert C.calendar_problems(["x"] * 657, C.JUDGED_SHA256) == []             # the count and the hash decide


# ------------------------------------------------------------------------------------------------ the constructions


def test_the_fixed_streams_are_q16s(C):
    p, judged, _, _ = synthetic_pairs(n_judged=657, per_session=8, sub=41)   # 5,256 offers: thinN up to 5,000
    mine = C.fixed_streams(p)
    ref = C.Q82.lift_streams(p, SEED)                                          # its thinN draws are not compared
    for k in ("offered", "taken"):
        for a, b in zip(ref[k], mine[k]):
            assert np.array_equal(a, b), k
    O_ = C.Q82.judged_offers(p, 657)
    inp = C.Inputs(p, 657, toy_seeds(C))
    for a, b in zip(inp.offers, (O_["s"], O_["v_win1"], O_["v_net3"], O_["coin"])):
        assert np.array_equal(a, b)


def test_the_side_draws_never_read_an_outcome(C):
    p, judged, _, _ = synthetic_pairs(n_judged=200, per_session=8, sub=42)
    p2 = p.copy()
    g = np.random.default_rng([SEED, 43])
    for c in ("kl_1", "ks_1", "kl_3", "ks_3"):
        p2[c] = g.integers(0, 3, size=len(p2))
    for c in ("rl_3", "rs_3"):
        p2[c] = g.normal(size=len(p2))
    seeds = toy_seeds(C)
    plan = {x["null"]: x for x in C.null_plan(seeds)}
    n = 200
    for name in ("fixed:offered:win1:flip5", "fixed:taken:net3:coin", "sub:500:03:net3:markov50",
                 "sub:1000:00:win1:flip21", "cp:ar98s15:1000:win1:persist1", "cp:burst10x:200:net3:persist1",
                 "flat:1000:win1:flip42"):                                 # 1,600 offers: sizes up to 1,000
        e = plan[name]
        outs = []
        for frame in (p, p2):
            inp = C.Inputs(frame, n, seeds)
            gen = C.mc_generator(e, inp)
            outs.append(gen(np.random.default_rng(e["entropy"]), 40))
        a, b = outs
        assert np.array_equal(a.g, b.g) and np.array_equal(a.N, b.N), name     # sides and counts: outcome-free
        assert not np.array_equal(a.S, b.S), name
    # the subsets' draws are the offers' only
    e = plan["sub:1000:05:win1:alt45"]
    i1 = C.subset_index(len(p), 1000, e["subset_entropy"])
    i2 = C.subset_index(len(p2), 1000, e["subset_entropy"])
    assert np.array_equal(i1, i2) and len(set(i1)) == 1000


def test_the_count_persistent_generator_is_q82s(C):
    p, judged, _, _ = synthetic_pairs(n_judged=200, per_session=8, sub=44)
    seeds = toy_seeds(C)
    plan = {x["null"]: x for x in C.null_plan(seeds)}
    q82plan = {x["null"]: x for x in C.Q82.null_plan()}
    inp = C.Inputs(p, 200, seeds)
    d82 = C.Q82.Data(p, [None] * 200, seeds={})
    for name in ("cp:ar98s15:1000:win1:persist1", "cp:burst10x:200:net3:persist1", "cp:ar98s15:500:win1:persist21"):
        mine = C.mc_generator(plan[name], inp)(np.random.default_rng([SEED, 45]), 24)
        theirs = C.Q82.generator(q82plan[name], d82)(np.random.default_rng([SEED, 45]), 24)
        assert np.array_equal(mine.S, theirs[0]) and np.array_equal(mine.N, theirs[1]), name


def test_the_coin_nulls_side_series_drops_ties(C):
    p, judged, _, _ = synthetic_pairs(n_judged=130, per_session=2, sub=46)
    seeds = toy_seeds(C)
    e = {x["null"]: x for x in C.null_plan(seeds)}["fixed:offered:win1:coin"]
    inp = C.Inputs(p, 130, seeds)
    ds = inp.data_for(e)
    b = C.mc_generator(e, inp)(np.random.default_rng([SEED, 47]), 30)
    m = C.side_matrix(b, ds)
    tie = ds.Cnet == 0                                                         # one long and one short coin side
    assert tie.any() and (m[tie] == 0).all() and (m[~tie] != 0).all()
    for j in range(30):
        sd, ses = C.trade_sides(b, ds, j)
        assert C.O.admission(sd, ses, 130).runs == C.O.runs_of(m[:, j][m[:, j] != 0])[0]


def test_same_nulls_as_q16_on_q16s_seeds(C, tmp_path, monkeypatch):
    """On Q-16's own seeds, the fixed-stream nulls (flips at 1, 5, 21 and the coin) and the realistic synthetic nulls
    give Q-16's code's `cons` rejection counts exactly at every level the two share."""
    _, judged, raw, allc = synthetic_pairs(n_judged=657, per_session=8, sub=48, before=3)   # thin5000 needs 5,000
    pdir = tmp_path / "pairs"
    pdir.mkdir()
    pq = pdir / "p16_pairs.parquet"
    raw.to_parquet(pq, index=False)
    (pdir / "p16_pairs.json").write_text(json.dumps({"identity": "HOLDS: synthetic (test)", "parquet_sha256":
                                                     hashlib.sha256(pq.read_bytes()).hexdigest(),
                                                     "trades_sha256": "synthetic"}), encoding="utf-8")
    days = tmp_path / "days.parquet"
    pd.DataFrame({"date": allc, "day_kind": "n"}).to_parquet(days, index=False)
    Q16 = C.Q16
    monkeypatch.setattr(Q16, "DAYS_FILE", days)
    streams, n, _ = Q16.real_streams(pq)
    p, _ = C.Q82.load_pairs(pq, judged)
    reps = 300
    specs = Q16.real_null_specs(streams)
    rows, _ = Q16._calibrate(specs, lambda sp, rng, r: Q16.real_batch(sp, streams, n, rng, r), reps,
                             Q16.SEED_LIFT_REAL, ("cons",), lambda m: None)
    ref = {(r["null"], f"{r['level']:.12g}"): r["rejections"] for r in rows}
    sspecs = Q16.syn_specs()
    srows, _ = Q16._calibrate(sspecs, lambda sp, rng, r: Q16.syn_batch(sp, n, rng, r), reps, Q16.SEED_LIFT_SYN,
                              ("cons",), lambda m: None)
    ref.update({(r["null"], f"{r['level']:.12g}"): r["rejections"] for r in srows})
    shared = [a for a in C.LEVELS if any(abs(a - b) < 1e-15 for b in Q16.LEVELS)]
    assert len(shared) == 6                                                   # k = 13, 14, 15 and 0.001, .005, .025
    inp = C.Inputs(p, n, C.SEEDS)
    names = [sp["null"] for sp in specs]
    model_of = {"persist1": "flip1", "persist5": "flip5", "persist21": "flip21", "coin": "coin"}
    compared = 0
    for e in C.null_plan():
        if e["group"] == "fixed" and e["model"] in model_of.values():
            side = {v: k for k, v in model_of.items()}[e["model"]]
            q16 = f"real:{e['stream']}:{e['value']}:{side}"
            ee = dict(e, entropy=[Q16.SEED_LIFT_REAL, names.index(q16)])
            res = C.run_mc(ee, C.mc_generator(ee, inp), inp.data_for(ee), reps, C.BATCH, n, ["cons"], None)
        elif e["group"] == "synthetic":
            q16 = e["null"]
            ee = dict(e, entropy=[Q16.SEED_LIFT_SYN, [s["null"] for s in sspecs].index(q16)])
            res = C.run_mc(ee, C.mc_generator(ee, inp), None, reps, C.BATCH, n, ["cons"], None)
        else:
            continue
        for a in shared:
            i = C.LEVELS.index(a)
            assert int(res["counts"][("cons", "Q")][i]) == ref[(q16, f"{a:.12g}")], (q16, a)
            compared += 1
        assert res["mismatches"] == []
    assert compared == (16 + 25) * 6
    assert sum(ref.values()) > 0


# ------------------------------------------------------------------------------------------------ end to end


def test_a_small_end_to_end_calibration_writes_nothing(C, monkeypatch, tmp_path):
    """Toy streams on a 130-session calendar, the grid shrunk (two sizes, one subset each, three count-persistent and
    one `flat` null): every part, every candidate, both scopes, the exact nulls and their re-decision, the power and the
    choice -- and no file written anywhere."""
    before = {p for p in (ROOT / "results").rglob("*")} if (ROOT / "results").is_dir() else set()
    monkeypatch.chdir(tmp_path)
    p, n = _toy_inputs(C)
    monkeypatch.setattr(C, "SIZES", (200, 1000))
    monkeypatch.setattr(C, "N_SUBSETS", 1)
    monkeypatch.setattr(C, "N_SUBSETS_NONPERSISTENT", 1)
    monkeypatch.setattr(C, "CP_ONE", C.CP_ONE[:2] + C.CP_ONE[-1:])
    monkeypatch.setattr(C, "FLAT_L", (21,))
    seeds = toy_seeds(C)
    want = C.expected_counts(seeds)
    assert want == {"rule": 121, "rule_exact": 40, "rule_mc": 81, "beside_cp": 3, "beside_flat": 4}
    sn = C.O.sn_reference([seeds["sn_table"], 0], draws=100_000, n=n)
    outs = [C.compute_part(part, p, n, 200, seeds, list(C.O.NAMES), sn, reps_beside=150, log=lambda m: None)
            for part in C.PARTS]
    res = C.calibrate_tables(outs, list(C.O.NAMES), want)
    assert res["failed"] == [], res["failed"]
    assert sum(o["meta"]["scalar_checked"] for o in outs) > 1000
    size = res["size"]
    assert len(size) == (want["rule"] + want["beside_cp"] + want["beside_flat"]) * 10 * 2
    assert set(size["scope"]) == {"Q", "D"} and set(size["candidate"]) == set(C.O.NAMES)
    ex = size[size["kind"] == "exact"]
    assert set(ex["model"]) == set(C.EXACT_MODELS) and ex["ci_lo_k13"].isna().all()
    assert (ex[ex["model"] == "flip63"]["admitted_share"] == 0).all()           # never admitted at 63
    line = res["choice"]["line"]
    assert line == "NONE" or line.startswith("CHOSEN ")
    elig = res["elig"]
    assert len(elig) == 20 and {"p_mc", "worst_exact_ratio", "worst_ratio_alt55", "cond3_ratio"} <= set(elig)
    pw = res["power"]
    assert set(pw["toy"]) == {"P", "net3", "cluster"} and set(pw["k"]) == {13, 15, 20}
    ps = res["psum"]
    assert np.isfinite(ps["P"].astype(float)).all() and len(ps) == 20
    sp = res["size_out"][res["size_out"].get("row") == "spread"]
    assert len(sp) and {"above_k13", "max_ratio_k20", "p90_ratio_a0.025"} <= set(sp.columns)
    fr = C.choice_frame(res["choice"])
    assert (fr["row"] == "decision").sum() == 1
    assert list(tmp_path.iterdir()) == []                                      # nothing written
    after = {p for p in (ROOT / "results").rglob("*")} if (ROOT / "results").is_dir() else set()
    assert after == before
