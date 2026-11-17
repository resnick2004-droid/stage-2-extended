"""Q-108 (E-115): the one-sample pass line's re-calibration -- one heavy run, on the calibration seeds only, from the
pinned plan `docs/calibration/Q-108_one_sample_plan.md` (sha256 c8e7424b..., E-115). It measures every candidate of
`extended/lift_one_sample.py` on the plan's 2,293 nulls in both scopes, applies the plan's choice rule (its 4.2) by
code, never by hand, and writes what the plan declares (its 6.2).

    python scripts/run_clean.py --name q108-calibrate --task Q-108 --hours <from the build's measurement> --mem-gb 1.5 -- python scripts/q108_calibrate.py
    python scripts/q108_calibrate.py --check-read      # the reader's verdict on the calendar read; reads and writes nothing

**What it computes** (the plan's sections 2-5; the choice is the plan's, coded here):
- C8's reference table first (2,000,000 draws, the calibration's `sn_table` seed);
- the nulls in the rule -- every candidate C0..C9, both scopes, on shared draws:
  - the fixed-data streams `offered` and `taken` (Q-16's), and 115 fresh subsets of P-16's judged offers (23 at each
    of 200, 500, 1,000, 2,000 and 5,000 trades), each at `win1` and `net3`, under the twelve side models of the plan's
    3.1 -- flips at 1, 5, 21 sessions, the coin and Markov switching (dwell 30, 50, 80) by Monte Carlo; flips at 42,
    55, 63 and the alternating models (45, 55) by exact enumeration; the flips at 1 and 5 and the coin on the first 5
    subsets of each size;
  - Q-16's 25 realistic synthetic nulls (`syn_batch` unchanged), always admitted in scope D;
- beside, deciding nothing: Q-82's 54 count-persistent one-sample nulls and the `flat` form at flips of 21, 42, 63;
- scope D per replication (per cell on an exact null): a rejection counts where the replication's own non-tie side
  series is admitted (R >= 13, E >= 4, both sides);
- the scalar re-decision (E-115 (R1)): every Monte Carlo rejection at a family level, and each null's first 3
  replications, re-decided by the scalar form a family calls (`lift_one_sample.bound_1s`, and `admission` in scope D);
  on an exact null the first 100 cells rejecting at k = 13 per candidate and scope, plus 20 cells drawn uniformly from
  all the null's cells (the same 20 for every candidate). **A disagreement is a failed check: the run stops, writes no
  result and prints no choice** (E-115 (R1)); the work folder and the log keep the record;
- the nesting assertion (the plan's 4.2, m6): every candidate's counts on every Monte Carlo null, and its exact sizes,
  non-increasing in k -- else the run stops with no choice;
- the power (the plan's 5): MDL50 and MDL80 at k = 13, 15 and 20 on the toys (subset j = 0 of each size, coin and
  persist1 sides, `win1`; the same for `net3`; Q-16's `cluster` at 1,000 trades), from each toy's first 20,000
  replications; P(c) the geometric mean of the ten `win1` toys' MDL80 at k = 13;
- the choice: level-eligible in a scope when (1) no Monte Carlo null's point rate and no exact null's exact size is
  above nominal at any k = 13..20, (2) P_MC >= 0.9 (the dynamic program over nested binomials), (3) the worst exact
  ratio <= 1/4; the most powerful (smallest P) eligible candidate in scope Q (C1..C9), else in scope D (C0..C9), else
  NONE; ties to fewer members, then the earlier row.

**Reads**, as Q-83's: the judged calendar through `extended.reader.read_walks` (purpose `registered_design`, E-035,
P-16), its count and sha256 asserted against E-094 (2); P-16's pairs through `scripts/q16_p16_pairs.py`. No bar is
opened by this script.

**Writes** (`extended.results.write_result`, each with its manifest and seeds; only inside a clean run):
`q108_cal_size.csv`, `q108_cal_power.csv`, `q108_sn_table.csv`, `q108_choice.csv`.

**Refusals (exit 3, before any step):** outside a clean run; a result file that exists; `lift_bound.py` other than its
pinned blob or the plan other than its pin; a seed map other than the calibration block's (the plan's 4.1); either
seed block named or derived outside the allow-list (the guard, below); a work folder inside the tree; a calendar other
than E-094's. **A failed check (exit 5):** a scalar disagreement, a nesting violation, a missing null.

**The seed guard** (the plan's 4.1): refuses a literal seed of either block, word-bounded, on any branch, remote or tag
or in the working tree, outside the allow-list (a document's mention outside `prereg/` is printed; this run's own
result files, their manifests naming a Q-108 runner, are printed); refuses an integer expression NAME + constants
(NAME an integer constant of the same file; a loop index bounded by `range` with constant bounds or `enumerate` over a
literal sequence) whose folded value lands in a block; prints, never refuses, an expression whose loop index cannot be
bounded, with the reach it would need (against the hand-check record `HAND_CHECKED`). Imported names are not folded:
their offsets are in the record `HAND_CHECKED_IMPORTED`.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import math
import os
import platform
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from extended import CLEAN_RUN_ENV, RESULTS_DIR, RUNS_DIR  # noqa: E402
from extended import count_nulls as CN  # noqa: E402
from extended import lift_bound as LB  # noqa: E402
from extended import lift_one_sample as O  # noqa: E402
from extended.procmem import working_set_mb  # noqa: E402


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


#: Q-82's runner, imported (never edited): its pairs loader, offers, count-persistent grid and engine data
Q82 = _load("q82_validation_for_q108", "scripts/q82_validation.py")
#: Q-16's calibration script (through Q-82): `_flip_signs`, `syn_batch`, `syn_specs`, the re-entry rule's constants
Q16 = Q82.Q16

SCRIPT = "scripts/q108_calibrate.py"
VALIDATE_SCRIPT = "scripts/q108_validate.py"
MODULE = "extended/lift_one_sample.py"
DECISION = "E-115"
PLAN = "docs/calibration/Q-108_one_sample_plan.md"
PLAN_SHA256 = "c8e7424b46ff0c60ecb5b3ea875ac3b77e70f090a52f0cc0d999d7e416486d7e"
#: lift_bound.py's pinned blob (F-03 pins it; the plan's 2.1)
VALIDATED_BLOBS = {"extended/lift_bound.py": "984f3467a4a05aa790d3ea43e94ac7761f0725b2"}
READ_ROW, READ_DESIGN = "E-035", "P-16"
JUDGED_FIRST, JUDGED_LAST = "2024-01-02", "2026-07-16"
#: the judged block's session list, E-094 (2): its count and the sha256 of its ISO dates joined by LF
N_SESSIONS = 657
JUDGED_SHA256 = "d1e4524b15dc6a69c2f66865462a5fe30527c6a56b4c7cc7aaccc1436a30f3bd"
DAYS_REL = Q82.DAYS_REL
RUN_CMD = ("python scripts/run_clean.py --name q108-calibrate --task Q-108 --hours <measured> --mem-gb 1.5 -- "
           "python scripts/q108_calibrate.py")

# ---- the seed blocks (the plan's 4.1) ----
#: the calibration block and the validation block, verified unused before the run (`seed_block_problems`)
CAL_BLOCK = tuple(range(20262110, 20262119 + 1))
VAL_BLOCK = tuple(range(20262120, 20262129 + 1))
#: the calibration block's map (the plan's 4.1 table)
SEEDS = {
    "tests": 20262110,           # the calibration build's tests
    "fixed_mc": 20262111,        # the fixed-data streams' Monte Carlo side draws: [s, i]
    "subsets": 20262112,         # the thinned subsets: subset (z, j) by [s, z_index, j]
    "subset_mc": 20262113,       # the subsets' Monte Carlo side draws: [s, z_index, j, value_index, model_index]
    "synthetic": 20262114,       # the realistic synthetic nulls: [s, i], i the null's index in Q-16's list
    "sn_table": 20262115,        # C8's reference: [s, 0], 200 batches of 10,000 drawn in turn
    "beside_cp": 20262116,       # the count-persistent nulls beside: [s, i], i the null's position in Q-82's CP_ONE
    "beside_flat": 20262117,     # the `flat` form beside: [s, i], i = (L, z_index, value_index) outermost first
    "exact_sample": 20262118,    # the exact nulls' sample of cells for the scalar re-decision: [s, null index]
}
#: drawn by nothing
SPARE = (20262119,)
# ---- end of the seed blocks ----

#: the roles a run draws, by runner (the validation's map has no C8 table: the statistic's definition is calibrated)
DRAW_ROLES = ("fixed_mc", "subsets", "subset_mc", "synthetic", "beside_cp", "beside_flat", "exact_sample")
CAL_ROLES = DRAW_ROLES + ("sn_table",)

# ---- the nulls (the plan's 3) ----
#: the side models in the plan's 3.1 order: `model_index` 0..11
MODELS = ("flip1", "flip5", "flip21", "flip42", "flip55", "flip63", "coin", "alt45", "alt55", "markov30", "markov50",
          "markov80")
EXACT_MODELS = ("flip42", "flip55", "flip63", "alt45", "alt55")
PERSISTENT = ("flip21", "flip42", "flip55", "flip63", "alt45", "alt55", "markov30", "markov50", "markov80")
NONPERSISTENT = ("flip1", "flip5", "coin")
#: the fixed-data streams' Monte Carlo models, in the order that indexes them
FIXED_MC_MODELS = ("flip1", "flip5", "flip21", "coin", "markov30", "markov50", "markov80")
STREAMS = ("offered", "taken")
VALUES = ("win1", "net3")
SIZES = (200, 500, 1000, 2000, 5000)
N_SUBSETS = 23
N_SUBSETS_NONPERSISTENT = 5
REALISTIC = ("iid", "cluster", "cluster_ar1", "regime01", "volclust")
FLAT_L = (21, 42, 63)
#: Q-82's one-sample count-persistent grid (its (ii)), the nulls beside
CP_ONE = tuple(Q82.CP_ONE)
#: replications and batches
REPS = 200_000
REPS_BESIDE = 100_000
BATCH = 10_000
#: (a builder's reading, E-115 hand-back) the beside nulls' batch: Q-82's 5,000 for its count-persistent nulls
BATCH_BESIDE = 5_000
SUB_PER_OFFER = Q82.SUB_PER_OFFER
#: the scalar re-decision (as Q-82: each null's first replications too)
SCALAR_FIRST = 3
SAMPLE_FIRST = 100
SAMPLE_UNIFORM = 20
#: power (the plan's 5)
POWER_REPS = 20_000
POWER_KS = (13, 15, 20)
#: the choice (the plan's 4.2)
P_MC_MIN = 0.9
RATIO_MAX = Fraction(1, 4)
LEVELS = O.LEVELS_1S
FAMILY = O.FAMILY_LEVELS_1S
NF = len(FAMILY)
LABELS = tuple([f"k{k}" for k in O.K_RANGE_1S] + [f"a{a:g}" for a in O.EXTRA_LEVELS_1S])
SCOPES = ("Q", "D")
#: the null counts the plan declares (its 3.5); `expected_counts` computes them from the grid above, and a test holds
#: the two equal
EXPECTED = {"rule": 2293, "rule_exact": 1170, "rule_mc": 1123, "beside_cp": 54, "beside_flat": 30}
RESULT_FILES = ("q108_cal_size", "q108_cal_power", "q108_sn_table", "q108_choice")
PARTS = ("fixed", "sub0", "sub1", "sub2", "sub3", "sub4", "syn", "cp", "flat")

#: exit codes
REFUSED, FAILED_CHECK = 3, 5


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S', time.gmtime())} UTC] {msg}", flush=True)


# ================================================================================================ the failure counts


def failure_count(level: float, reps: int = REPS) -> int:
    """The smallest count whose 95 % Clopper-Pearson lower limit lies above `level` (E-052's "wholly above")."""
    c = max(1, int(level * reps))
    while stats.beta.ppf(0.025, c, reps - c + 1) <= level:
        c += 1
    return c


#: 71, 63, 56, 50, 45, 41, 38, 35 at k = 13..20 (the plan's 4.2, `q108_arith.py`)
FAIL = {k: failure_count(LB.family_level(k)) for k in O.K_RANGE_1S}
_FAIL_BY_REPS = {REPS: FAIL}


def fail_counts(reps: int) -> dict[int, int]:
    """The failure counts at `reps` replications (200,000 in both runs; a test's toy run takes its own)."""
    if int(reps) not in _FAIL_BY_REPS:
        _FAIL_BY_REPS[int(reps)] = {k: failure_count(LB.family_level(k), int(reps)) for k in O.K_RANGE_1S}
    return _FAIL_BY_REPS[int(reps)]


def p_holds(rates, fail=None, reps: int = REPS) -> float:
    """P(X_k < fail_k at every k = 13..20) for X_13 ~ Bin(reps, rates[0]) and X_{k+1} | X_k ~ Bin(X_k, rates[i+1] /
    rates[i]), zero once a rate is zero -- by dynamic programming over the counts (exact; `q108_arith.p_holds`'s
    computation as matrices)."""
    fail = FAIL if fail is None else fail
    f = [int(fail[k]) for k in O.K_RANGE_1S]
    r = [float(x) for x in rates]
    if len(r) != len(f):
        raise ValueError("one rate a family level")
    if any(b > a for a, b in zip(r, r[1:])):
        raise ValueError("rates must be non-increasing in k (nested rejections)")
    if r[0] <= 0.0:
        return 1.0
    prob = stats.binom.pmf(np.arange(f[0]), reps, r[0])
    for i in range(1, len(f)):
        q = r[i] / r[i - 1] if r[i - 1] > 0 else 0.0
        x = np.arange(prob.size)
        y = np.arange(f[i])
        T = stats.binom.pmf(y[:, None], x[None, :], q)
        prob = T @ prob
    return float(prob.sum())


# ================================================================================================ the seed guard


SEED_PATTERN = r"2026211[0-9]|2026212[0-9]"
#: the files that may name either block (the plan's 4.1 allow-list)
SEED_ALLOW = frozenset({PLAN, MODULE, SCRIPT, VALIDATE_SCRIPT, "tests/test_lift_one_sample.py",
                        "tests/test_q108_calibrate.py", "tests/test_q108_validate.py",
                        "DECISIONS.md", "TASK_QUEUE.md", "STATUS.md", "PROGRESS.md"})
SEED_ALLOW_PREFIXES = ("docs/calibration/scripts/q108/", "docs/briefs/Q-108")
#: this run's own results (Q-82b's pattern): they record their seeds; allowed where the manifest names a Q-108 runner
OWN_RESULT = re.compile(r"results/(q108_[A-Za-z0-9_]+)\.csv(?:\.manifest\.json)?")
OWN_SCRIPTS = (SCRIPT, VALIDATE_SCRIPT)
#: (a builder's reading, E-115 hand-back) an unbounded expression is printed for a hand check when its anchor -- its
#: fold with every unbounded index at its least value (0 for `enumerate` and `range`) -- lies within this many seeds
#: of a block; the others are counted in one line with the least reach among them. Printing never refuses.
PRINT_REACH = 1_000_000

#: the hand-check record of the loop-index expressions the guard cannot bound (the plan's 4.1, E-115): file, the
#: expression as `ast.unparse` writes it, and the reach and reason of the hand check
HAND_CHECKED = (
    {"file": "tests/test_features_lookahead.py", "expr": "SEED_REPLACE + i",
     "reach": "i runs over the cuts of a test's synthetic bars (tens); it would need to reach 978 to land in the "
              "calibration block",
     "reason": "the plan's 4.1 hand check: the cuts are tens, far below the blocks"},
    {"file": "tests/test_features_lookahead.py", "expr": "SEED_REPLACE + 200 + i",
     "reach": "i runs over the fixed days (a handful); it would need to reach 778 to land in the calibration block",
     "reason": "the plan's 4.1 hand check: the fixed days are a handful, far below the blocks"},
    {"file": "tests/test_features_lookahead.py", "expr": "SEED_REPLACE + 1000 + i",
     "reach": "i < 790 (the alerts of ten days); its least value is three above the validation block's last seed",
     "reason": "the plan's 4.1 hand check: an enumerate index is never negative, so it lands in neither block"},
)
#: imported names plus an offset, not folded by the guard: checked by hand (the plan's 4.1; E-115 adds the nested
#: planted-effect offset; the third read adds lift_bound's runtime offset)
HAND_CHECKED_IMPORTED = (
    {"where": "scripts/rd01_reading.py (wt-firms)", "expr": "R.F.LADDER_SEED + i",
     "reason": "the firms reading's first block seed plus i over a short literal sequence; RD-01's undeclared draws "
               "end below the calibration block (docs/reviews/BUILD_RD-01_2026-11-16.md)"},
    {"where": "vendor/stage2/scripts/hypo_firm_h.py, hypo_firm_h_edge.py", "expr": "fh.SEED + 1, fh.SEED + 2",
     "reason": "Stage 2's firm_h seed plus one or two, far below the blocks"},
    {"where": "vendor/stage2/scripts/score_im2.py", "expr": "sc.SEED + 1",
     "reason": "Stage 2's im2_score seed plus one, far below the blocks"},
    {"where": "vendor/stage2/scripts/l5_planted_effect.py", "expr": "pe.SEED + 100_000 * i + 1_000 * j",
     "reason": "Stage 2's planted_effect seed is 202 modulo 1,000 and the blocks lie at 110-129 modulo 1,000, so no "
               "multiple of 1,000 lands it in a block"},
    {"where": "vendor/stage2/propedge/research/planted_effect.py (power_cell)", "expr": "seed + 1 + i",
     "reason": "E-115: the nested offset on top of the planted-effect seeds above, i < 200 replications: residues "
               "203-402 modulo 1,000, in neither block"},
    {"where": "Stage 1's frozen propsim scripts", "expr": "a.seed + ...",
     "reason": "runtime arguments of Stage 1's frozen scripts, not run here"},
    {"where": "extended/lift_bound.py (fixed_b_critical)", "expr": "seed + 1000 * G + lags",
     "reason": "the third read: its fixed-b seed plus 1,000 G plus 2 cannot land in a block for any integer G"},
)


def _git(repo: Path, *a: str, binary: bool = False) -> subprocess.CompletedProcess:
    if binary:
        return subprocess.run(["git", *a], cwd=repo, capture_output=True)
    return subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace")


def _refs(repo: Path) -> list[str]:
    r = _git(repo, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", "refs/tags")
    if r.returncode:
        raise RuntimeError(f"cannot list the refs of {repo}: {r.stderr.strip()[:200]}")
    return [x for x in r.stdout.split() if x and not x.endswith("/HEAD")]


def _own_result(repo: Path, where: str, path: str) -> bool:
    m = OWN_RESULT.fullmatch(path)
    if not m:
        return False
    man = f"results/{m.group(1)}.csv.manifest.json"
    if where == "working tree":
        p = repo / man
        text = p.read_text(encoding="utf-8", errors="replace") if p.is_file() else None
    else:
        r = _git(repo, "show", f"{where}:{man}")
        text = r.stdout if r.returncode == 0 else None
    try:
        rec = json.loads(text) if text else None
    except ValueError:
        return False
    return isinstance(rec, dict) and rec.get("script") in OWN_SCRIPTS and rec.get("result_file") == f"{m.group(1)}.csv"


def literal_problems(repo: Path | str = ROOT) -> tuple[list[str], list[str]]:
    """(problems, notes): files naming a seed of either block, word-bounded, on any branch, remote or tag or in the
    working tree (tracked or untracked, not ignored), outside the allow-list. A document's mention outside `prereg/`,
    or this run's own result file, is a note; anything else a problem."""
    repo = Path(repo)
    hits: dict[tuple[str, str], int] = {}
    r = _git(repo, "grep", "--untracked", "-n", "-I", "-w", "-E", SEED_PATTERN)
    if r.returncode not in (0, 1):
        return [f"git grep failed in the working tree: {r.stderr.strip()[:200]}"], []
    for line in r.stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) == 3:
            hits[("working tree", parts[0])] = 1
    names = _refs(repo)
    for i in range(0, len(names), 40):
        r = _git(repo, "grep", "-n", "-I", "-w", "-E", SEED_PATTERN, *names[i:i + 40], "--")
        if r.returncode not in (0, 1):
            return [f"git grep failed on {names[i:i + 40][:3]}: {r.stderr.strip()[:200]}"], []
        for line in r.stdout.splitlines():
            parts = line.split(":", 3)
            if len(parts) == 4:
                hits[(parts[0], parts[1])] = 1
    problems, notes = set(), set()
    for (where, path) in hits:
        path = path.replace("\\", "/")
        if path in SEED_ALLOW or path.startswith(SEED_ALLOW_PREFIXES):
            continue
        if _own_result(repo, where, path):
            notes.add(f"{path} ({where}): this run's own result, its manifest naming a Q-108 runner")
            continue
        if path.lower().endswith(".md") and not path.startswith("prereg/"):
            notes.add(f"{path} ({where}): a document's mention")
            continue
        problems.add(f"{path} ({where})")
    return sorted(problems), sorted(notes)


# ---- the AST fold ----

INF = math.inf


def _ival_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _ival_sub(a, b):
    return (a[0] - b[1], a[1] - b[0])


def _ival_mul(a, b):
    xs = []
    for x in a:
        for y in b:
            if (x == 0 and math.isinf(y)) or (y == 0 and math.isinf(x)):
                xs.append(0.0)
            else:
                xs.append(x * y)
    return (min(xs), max(xs))


def _int_constants(tree: ast.AST) -> dict[str, set[int]]:
    """Every NAME assigned an integer literal anywhere in the file (`X = 5`, `A, B = 1, 2`, `X: int = 5`)."""
    out: dict[str, set[int]] = {}

    def put(t, v):
        if isinstance(t, ast.Name) and isinstance(v, ast.Constant) and type(v.value) is int:
            out.setdefault(t.id, set()).add(int(v.value))

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, (ast.Tuple, ast.List)) and isinstance(node.value, (ast.Tuple, ast.List)) \
                        and len(t.elts) == len(node.value.elts):
                    for a, b in zip(t.elts, node.value.elts):
                        put(a, b)
                else:
                    put(t, node.value)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            put(node.target, node.value)
    return out


def _const_int(node) -> int | None:
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return int(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _const_int(node.operand)
        return None if v is None else -v
    return None


def _loop_bounds(target, it) -> dict[str, tuple[float, float]]:
    """The literal extent of a loop's index names: `range` with constant bounds -> [lo, hi]; `range` with a constant
    start (or none) and a positive or absent step -> [start, inf); `enumerate(seq)` -> its index [start, start + len -
    1] over a written-out list, tuple or string, [start, inf) otherwise. Names it cannot bound: (-inf, inf)."""
    out: dict[str, tuple[float, float]] = {}
    names = [n.id for n in ast.walk(target) if isinstance(n, ast.Name)]
    for nm in names:
        out[nm] = (-INF, INF)
    if isinstance(it, ast.Call) and isinstance(it.func, ast.Name):
        fn, args = it.func.id, it.args
        if fn == "range" and isinstance(target, ast.Name) and 1 <= len(args) <= 3:
            vals = [_const_int(a) for a in args]
            step = vals[2] if len(args) == 3 else 1
            start = 0 if len(args) == 1 else vals[0]
            stop = vals[0] if len(args) == 1 else vals[1]
            if step is not None and step > 0 and start is not None:
                out[target.id] = (start, stop - 1) if stop is not None else (start, INF)
        elif fn == "enumerate" and isinstance(target, ast.Tuple) and target.elts \
                and isinstance(target.elts[0], ast.Name) and args:
            start = 0
            for kw in it.keywords:
                if kw.arg == "start":
                    start = _const_int(kw.value)
            if len(args) > 1:
                start = _const_int(args[1])
            if start is not None:
                seq = args[0]
                ln = None
                if isinstance(seq, (ast.List, ast.Tuple)):
                    ln = len(seq.elts)
                elif isinstance(seq, ast.Constant) and isinstance(seq.value, str):
                    ln = len(seq.value)
                out[target.elts[0].id] = (start, start + ln - 1) if ln is not None else (start, INF)
    return out


@dataclass(frozen=True)
class Folded:
    file: str
    line: int
    expr: str
    lo: float
    hi: float
    anchor: float


class _Folder(ast.NodeVisitor):
    def __init__(self, consts: dict[str, set[int]]):
        self.consts = consts
        self.scopes: list[dict[str, tuple[float, float]]] = []
        self.found: list[tuple[ast.AST, tuple[float, float], float]] = []

    def _lookup(self, nm: str):
        for sc in reversed(self.scopes):
            if nm in sc:
                return sc[nm]
        return None

    def _fold(self, node, uses: list):
        """(interval, anchor interval) or None when a leaf is opaque."""
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
            a = self._fold(node.left, uses)
            b = self._fold(node.right, uses)
            if a is None or b is None:
                return None
            f = {ast.Add: _ival_add, ast.Sub: _ival_sub, ast.Mult: _ival_mul}[type(node.op)]
            return f(a[0], b[0]), f(a[1], b[1])
        v = _const_int(node)
        if v is not None:
            return (v, v), (v, v)
        if isinstance(node, ast.Name):
            b = self._lookup(node.id)
            if b is not None:                                   # a loop index
                lo = b[0] if math.isfinite(b[0]) else 0.0
                return b, (lo, lo)
            if node.id in self.consts:                          # an integer constant of the file
                vals = self.consts[node.id]
                uses.append(node.id)
                return (min(vals), max(vals)), (min(vals), max(vals))
            return (-INF, INF), (0.0, 0.0)                      # another name: unbounded
        return None                                             # an attribute, call, subscript: not folded

    def visit_BinOp(self, node):
        uses: list = []
        res = self._fold(node, uses)
        if res is not None and uses:
            self.found.append((node, res[0], res[1][0]))
            return                                              # the maximal expression only
        self.generic_visit(node)

    def _loop(self, target, it, body_nodes):
        self.visit(it)
        self.scopes.append(_loop_bounds(target, it))
        for b in body_nodes:
            self.visit(b)
        self.scopes.pop()

    def visit_For(self, node):
        self._loop(node.target, node.iter, node.body + node.orelse)

    visit_AsyncFor = visit_For

    def _comp(self, node, elts):
        def rec(gens):
            if not gens:
                for e in elts:
                    self.visit(e)
                return
            g = gens[0]
            self.visit(g.iter)
            self.scopes.append(_loop_bounds(g.target, g.iter))
            for c in g.ifs:
                self.visit(c)
            rec(gens[1:])
            self.scopes.pop()
        rec(node.generators)

    def visit_ListComp(self, node):
        self._comp(node, [node.elt])

    visit_SetComp = visit_GeneratorExp = visit_ListComp

    def visit_DictComp(self, node):
        self._comp(node, [node.key, node.value])


def fold_file(text: str, path: str) -> list[Folded]:
    """Every maximal integer expression of NAME + constants (and loop indices) in one file, folded."""
    import warnings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return []
    fo = _Folder(_int_constants(tree))
    fo.visit(tree)
    out = []
    for node, (lo, hi), anchor in fo.found:
        out.append(Folded(path, int(getattr(node, "lineno", 0)), ast.unparse(node), float(lo), float(hi),
                          float(anchor)))
    return out


def _blocks_span():
    return [(min(CAL_BLOCK), max(CAL_BLOCK), "calibration"), (min(VAL_BLOCK), max(VAL_BLOCK), "validation")]


def classify_folded(f: Folded) -> tuple[str, str]:
    """('refuse' | 'print' | 'ok', why)."""
    spans = _blocks_span()
    if math.isfinite(f.lo) and math.isfinite(f.hi):
        for a, b, name in spans:
            if f.lo <= b and f.hi >= a:
                return "refuse", f"its folded value{'s' if f.hi > f.lo else ''} [{f.lo:.0f}, {f.hi:.0f}] reach the {name} block"
        return "ok", ""
    near = min(min(abs(f.anchor - a), abs(f.anchor - b)) if not (a <= f.anchor <= b) else 0 for a, b, _ in spans)
    if near > PRINT_REACH:
        return "ok", f"far: {near:.0f}"
    lands = [(a, b, nm) for a, b, nm in spans if f.lo <= b and f.hi >= a]
    if not lands:
        return "print", "its loop index cannot be bounded above, but its least value lies beyond both blocks: it cannot land"
    reach = min(max(0.0, a - f.anchor) if f.hi == INF else max(0.0, f.anchor - b) for a, b, _ in lands)
    return "print", f"its loop index cannot be bounded; it would need a reach of {reach:.0f} to land in a block"


def _py_sources(repo: Path) -> dict[str, tuple[str, str]]:
    """{blob or path key: (where, path)} of every .py file in the working tree (tracked and untracked, not ignored)
    and on every branch, remote and tag, each distinct blob once."""
    out: dict[str, tuple[str, str]] = {}
    changed = set(_git(repo, "ls-files", "-m", "-o", "--exclude-standard", "--", "*.py").stdout.splitlines())
    for line in _git(repo, "ls-files", "-s", "--", "*.py").stdout.splitlines():
        meta, _, path = line.partition("	")
        bits = meta.split()
        if len(bits) >= 2 and path not in changed and (repo / path).is_file():
            out.setdefault(bits[1], ("working tree", path))       # unmodified: its index blob, read once
    for path in changed:
        if (repo / path).is_file():
            out[f"wt:{path}"] = ("working tree", path)
    for ref in _refs(repo):
        r = _git(repo, "ls-tree", "-r", ref)
        for line in r.stdout.splitlines():
            meta, _, path = line.partition("\t")
            bits = meta.split()
            if len(bits) == 3 and bits[1] == "blob" and path.endswith(".py"):
                out.setdefault(bits[2], (ref, path))
    return out


def derived_problems(repo: Path | str = ROOT) -> tuple[list[str], list[str]]:
    """(problems, prints): the AST fold over every .py of the working tree and every ref (distinct blobs once),
    outside the allow-list. A folded value landing in a block is a problem; an unbounded loop index near a block is
    printed for a hand check (against `HAND_CHECKED`), never refused."""
    repo = Path(repo)
    srcs = _py_sources(repo)
    blobs = [k for k in srcs if not k.startswith("wt:")]
    texts: dict[str, str] = {}
    if blobs:
        r = subprocess.run(["git", "cat-file", "--batch"], cwd=repo, input="\n".join(blobs).encode() + b"\n",
                           capture_output=True)
        data, pos = r.stdout, 0
        while pos < len(data):
            nl = data.index(b"\n", pos)
            head = data[pos:nl].decode().split()
            pos = nl + 1
            if len(head) < 3 or head[1] != "blob":
                continue
            size = int(head[2])
            texts[head[0]] = data[pos:pos + size].decode("utf-8", errors="replace")
            pos += size + 1
    problems, prints, far = set(), set(), []
    hand = {(h["file"], h["expr"]): h for h in HAND_CHECKED}
    spans = _blocks_span()
    for key, (where, path) in srcs.items():
        path = path.replace("\\", "/")
        if path in SEED_ALLOW or path.startswith(SEED_ALLOW_PREFIXES):
            continue
        text = (repo / path).read_text(encoding="utf-8", errors="replace") if key.startswith("wt:") \
            else texts.get(key, "")
        for f in fold_file(text, path):
            kind, why = classify_folded(f)
            if kind == "refuse":
                problems.add(f"{path}:{f.line} ({where}): `{f.expr}` -- {why}")
            elif kind == "print":
                h = hand.get((path, f.expr))
                rec = f"hand-checked: {h['reach']} ({h['reason']})" if h else "NOT in the hand-check record"
                prints.add(f"{path}:{f.line}: `{f.expr}` -- {why}; {rec}")
            elif why.startswith("far"):
                d = min(abs(f.anchor - a) if f.anchor < a else abs(f.anchor - b) for a, b, _ in spans)
                far.append((d, f"{path}:{f.line}"))
    out = sorted(prints)
    if far:
        d, at = min(far)
        out.append(f"{len(far)} more unbounded expression(s) lie over {PRINT_REACH:,} seeds from both blocks (not "
                   f"listed); the nearest, {at}, at {d:,.0f}")
    return sorted(problems), out


def seed_block_problems(repo: Path | str = ROOT) -> tuple[list[str], list[str]]:
    """(problems, notes) of both checks."""
    p1, n1 = literal_problems(repo)
    p2, n2 = derived_problems(repo)
    return p1 + p2, n1 + [f"derived seed, printed for a hand check: {x}" for x in n2]


def seed_map_problems(seeds: dict, block, roles) -> list[str]:
    """A runner draws only its own block: every role of `roles` mapped, each in `block`, all distinct."""
    out = []
    block = set(int(x) for x in block)
    for r in roles:
        if r not in seeds:
            out.append(f"the seed map has no {r!r}")
        elif int(seeds[r]) not in block:
            out.append(f"seed role {r!r} is {seeds[r]}, outside this runner's block")
    vals = [int(seeds[r]) for r in roles if r in seeds]
    if len(set(vals)) != len(vals):
        out.append("two roles share a seed")
    return out


# ================================================================================================ reads and data


def blob_id(path: Path) -> str:
    return Q82.blob_id(path)


def file_sha_lf(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def pin_problems() -> list[str]:
    out = Q82.module_blob_problems({rel: (ROOT / rel, want) for rel, want in VALIDATED_BLOBS.items()})
    if file_sha_lf(ROOT / PLAN) != PLAN_SHA256:
        out.append(f"{PLAN} does not hash to its pin in {DECISION}")
    return out


def judged_sessions(dates) -> tuple[list[str], str]:
    """Q-82's session list (657 sessions, the sha256 of the ISO dates joined by LF)."""
    return Q82.judged_sessions(dates)


def calendar_problems(cal: list[str], sha: str) -> list[str]:
    if len(cal) != N_SESSIONS or sha != JUDGED_SHA256:
        return [f"the judged calendar has {len(cal)} sessions and sha256 {sha[:12]}..., not E-094 (2)'s "
                f"{N_SESSIONS} and {JUDGED_SHA256[:12]}..."]
    return []


def read_calendar() -> tuple[list[str], str, dict]:
    from extended import reader

    df = reader.read_walks("A1", "days", JUDGED_FIRST, JUDGED_LAST, purpose=reader.REGISTERED_DESIGN,
                           declaration=READ_ROW, design=READ_DESIGN, columns=["date"],
                           what=f"{DECISION} (Q-108): the judged block's session list -- A1's stored days, dates only")
    cal, sha = judged_sessions(df["date"].astype(str).tolist())
    return cal, sha, {"file": DAYS_REL, "columns": ["date"], "purpose": "registered_design", "declaration": READ_ROW,
                      "design": READ_DESIGN}


def fixed_streams(p: pd.DataFrame) -> dict:
    """Q-16's `offered` and `taken` streams (`real_streams`), as (session, win1, net3, coin) -- the re-entry rule as
    Q-82's `lift_streams` writes it, without its thinned subsets."""
    s = p["session"].to_numpy(np.int64)
    win1 = 0.5 * ((p["kl_1"] == 1).astype(float) - (p["ks_1"] == 1).astype(float)).to_numpy()
    net3 = 0.5 * (p["rl_3"].astype(float) - p["rs_3"].astype(float)).to_numpy()
    coin = p["coin"].astype(int).to_numpy()
    xl = p[f"xl_{Q16.R_SCHED:g}"].to_numpy(int)
    xs = p[f"xs_{Q16.R_SCHED:g}"].to_numpy(int)
    slot = p["slot"].to_numpy(int)
    take = np.zeros(len(p), dtype=bool)
    free, cur = -1, -1
    for i in range(len(p)):
        if s[i] != cur:
            cur, free = s[i], -1
        if slot[i] >= free:
            take[i] = True
            free = (xl[i] if coin[i] > 0 else xs[i]) + Q16.STRICT_GAP
    return {"offered": (s, win1, net3, coin), "taken": tuple(a[take] for a in (s, win1, net3, coin))}


def subset_index(n_offers: int, z: int, entropy) -> np.ndarray:
    """A fresh subset of z of the judged offers, without replacement (`default_rng(entropy)`), in offer order."""
    rng = np.random.default_rng(entropy)
    return np.sort(rng.choice(int(n_offers), size=int(z), replace=False))


@dataclass
class DataSet:
    """One trade set's per-session arrays at one value."""
    name: str
    s: np.ndarray                               # each trade's session
    coin: np.ndarray                            # each trade's coin side
    V: np.ndarray                               # (n,) the value's session sums
    Vcoin: np.ndarray                           # (n,) the coin side times the value, summed
    N: np.ndarray                               # (n,) counts
    Cnet: np.ndarray                            # (n,) the coin sides summed (the coin null's net side)

    @property
    def traded(self) -> np.ndarray:
        return self.N > 0


def dataset(name: str, arrs, value: str, n: int) -> DataSet:
    s, win1, net3, coin = arrs
    v = win1 if value == "win1" else net3
    return DataSet(name, s, coin, np.bincount(s, weights=v, minlength=n), np.bincount(s, weights=coin * v,
                   minlength=n), np.bincount(s, minlength=n).astype(float),
                   np.bincount(s, weights=coin.astype(float), minlength=n))


# ================================================================================================ the null plan


def null_plan(seeds: dict | None = None) -> list[dict]:
    """Every null of the run, in order, with its part and entropy (no data read)."""
    seeds = SEEDS if seeds is None else seeds
    plan: list[dict] = []

    def add(**kw):
        base = {"null": None, "part": None, "kind": None, "group": None, "in_rule": True, "data": None, "stream": None,
                "size": None, "z_index": None, "j": None, "value": None, "value_index": None, "model": None,
                "model_index": None, "entropy": None, "subset_entropy": None, "exact_index": None,
                "sample_entropy": None, "toy": None, "q16": None, "profile": None, "L": None, "engine": None}
        base.update(kw)
        plan.append(base)

    def exact_index(data_pos, vi, model):
        return (data_pos * 2 + vi) * 5 + EXACT_MODELS.index(model)

    for si, st in enumerate(STREAMS):
        for vi, v in enumerate(VALUES):
            for pos, m in enumerate(FIXED_MC_MODELS):
                i = (si * 2 + vi) * 7 + pos
                add(null=f"fixed:{st}:{v}:{m}", part="fixed", kind="mc", group="fixed", data=st, stream=st, value=v,
                    value_index=vi, model=m, model_index=MODELS.index(m), entropy=[int(seeds["fixed_mc"]), i])
            for m in EXACT_MODELS:
                xi = exact_index(si, vi, m)
                add(null=f"fixed:{st}:{v}:{m}", part="fixed", kind="exact", group="fixed", data=st, stream=st,
                    value=v, value_index=vi, model=m, model_index=MODELS.index(m), exact_index=xi,
                    sample_entropy=[int(seeds["exact_sample"]), xi])
    for zi, z in enumerate(SIZES):
        for j in range(N_SUBSETS):
            sub_e = [int(seeds["subsets"]), zi, j]
            for vi, v in enumerate(VALUES):
                for mi, m in enumerate(MODELS):
                    if m in NONPERSISTENT and j >= N_SUBSETS_NONPERSISTENT:
                        continue
                    toy = None
                    if j == 0 and m in ("coin", "flip1"):
                        toy = "P" if v == "win1" else "net3"
                    common = dict(null=f"sub:{z}:{j:02d}:{v}:{m}", part=f"sub{zi}", group="subset", data="sub",
                                  size=z, z_index=zi, j=j, value=v, value_index=vi, model=m, model_index=mi,
                                  subset_entropy=sub_e, toy=toy)
                    if m in EXACT_MODELS:
                        xi = exact_index(2 + zi * N_SUBSETS + j, vi, m)
                        add(kind="exact", exact_index=xi, sample_entropy=[int(seeds["exact_sample"]), xi], **common)
                    else:
                        add(kind="mc", entropy=[int(seeds["subset_mc"]), zi, j, vi, mi], **common)
    for ni, sp in enumerate(Q16.syn_specs()):
        if sp["model"] in REALISTIC:
            add(null=sp["null"], part="syn", kind="mc", group="synthetic", data="syn", size=int(sp["trades"]),
                model=sp["model"], entropy=[int(seeds["synthetic"]), ni], q16=sp,
                toy="cluster" if sp["model"] == "cluster" and int(sp["trades"]) == 1000 else None)
    for i, (prof, T, v, L) in enumerate(CP_ONE):
        add(null=f"cp:{prof}:{T}:{v}:persist{L}", part="cp", kind="mc", group="beside_cp", in_rule=False, data="cp",
            size=int(T), value=v, profile=prof, L=int(L), entropy=[int(seeds["beside_cp"]), i],
            engine="hypergeometric" if v == "win1" else "per-offer")
    for Li, L in enumerate(FLAT_L):
        for zi, z in enumerate(SIZES):
            for vi, v in enumerate(VALUES):
                i = (Li * len(SIZES) + zi) * len(VALUES) + vi
                add(null=f"flat:{z}:{v}:flip{L}", part="flat", kind="mc", group="beside_flat", in_rule=False,
                    data="flat", size=z, z_index=zi, value=v, value_index=vi, profile="flat", L=L,
                    entropy=[int(seeds["beside_flat"]), i], engine="hypergeometric" if v == "win1" else "per-offer")
    return plan


# ================================================================================================ the generators


@dataclass
class Batch:
    S: np.ndarray                               # (n, r)
    N: np.ndarray                               # (n, 1) or (n, r)
    g: np.ndarray | None                        # (n, r) the session sides; None: always admitted (daily sides)
    kind: str                                   # "uniform" (every trade on g_j), "coin" (coin_i g_j), "daily"


class Inputs:
    """What the generators read: the judged calendar's length and P-16's judged offers (streams, subsets and Q-82's
    count-persistent engine data, each built when first asked)."""

    def __init__(self, p: pd.DataFrame | None, n: int, seeds: dict):
        self.p, self.n, self.seeds = p, int(n), dict(seeds)
        self._cache: dict = {}

    def _need(self):
        if self.p is None:
            raise ValueError("this null reads P-16's pairs; none were given")

    @property
    def offers(self):
        self._need()
        if "O" not in self._cache:
            O_ = Q82.judged_offers(self.p, self.n)
            self._cache["O"] = (O_["s"], O_["v_win1"], O_["v_net3"], O_["coin"])
        return self._cache["O"]

    @property
    def streams(self) -> dict:
        self._need()
        if "streams" not in self._cache:
            self._cache["streams"] = fixed_streams(self.p)
        return self._cache["streams"]

    def data_for(self, e: dict) -> DataSet:
        key = ("ds", e["data"], e["size"], e["j"], e["value"])
        if key in self._cache:
            return self._cache[key]
        if e["data"] in STREAMS:
            arrs = self.streams[e["data"]]
        else:
            ak = ("subarrs", e["size"], e["j"])
            if ak not in self._cache:
                full = self.offers
                idx = subset_index(len(full[0]), int(e["size"]), e["subset_entropy"])
                self._cache[ak] = tuple(a[idx] for a in full)
            arrs = self._cache[ak]
        ds = dataset(e["null"].rsplit(":", 1)[0], arrs, e["value"], self.n)
        self._cache[key] = ds
        return ds

    @property
    def engine82(self):
        self._need()
        if "q82" not in self._cache:
            self._cache["q82"] = Q82.Data(self.p, [None] * self.n, seeds={})
        return self._cache["q82"]

    def drop(self, prefix) -> None:
        for k in [k for k in self._cache if isinstance(k, tuple) and k[0] in prefix]:
            del self._cache[k]


def _flip_L(model: str) -> int:
    return int(model[4:])


def mc_generator(e: dict, inp: Inputs):
    """The null's batch generator `gen(rng, r) -> Batch` (side draws before anything that reads an outcome)."""
    n = inp.n
    if e["group"] in ("fixed", "subset"):
        ds = inp.data_for(e)
        m = e["model"]
        Nf = ds.N[:, None]
        if m.startswith("flip"):
            L = _flip_L(m)

            def gen(rng, r):
                g = Q16._flip_signs(rng, n, L, r)
                return Batch(ds.V[:, None] * g, Nf, g, "uniform")
            return gen
        if m == "coin":
            def gen(rng, r):
                g = Q16._flip_signs(rng, n, 1, r)
                return Batch(ds.Vcoin[:, None] * g, Nf, g, "coin")
            return gen
        if m.startswith("markov"):
            D = float(m[6:])

            def gen(rng, r):
                g = O.markov_sides(rng, n, D, r)
                return Batch(ds.V[:, None] * g, Nf, g, "uniform")
            return gen
        raise ValueError(f"no Monte Carlo generator for {m!r}")
    if e["group"] == "synthetic":
        spec = e["q16"]

        def gen(rng, r):
            S, N = Q16.syn_batch(spec, n, rng, r)
            return Batch(S, N, None, "daily")
        return gen
    if e["group"] in ("beside_cp", "beside_flat"):
        d = inp.engine82
        c, prof, L = float(e["size"]) / d.n_off, e["profile"], int(e["L"])
        if e["engine"] == "hypergeometric":
            def gen(rng, r):                                    # Q-82's cp_one, its draws in its order, g returned
                K = CN.thin_counts(d.offers, CN.keep_rates(CN.intensity(prof, n, r, rng), c), rng)
                g = Q16._flip_signs(rng, n, L, r)
                S = CN.subset_sums(d.cats_v, (0.5, 0.0, -0.5), [K], rng)[0]
                return Batch(S * g, K.astype(float), g, "uniform")
            return gen

        def gen(rng, r):                                        # net R: offer by offer (Q-82's per-offer engine)
            rate = CN.keep_rates(CN.intensity(prof, n, r, rng), c)
            g = Q16._flip_signs(rng, n, L, r)
            ind, v = d.indicator, d.v_net3
            S, N = np.empty((n, r)), np.empty((n, r))
            for a0 in range(0, r, SUB_PER_OFFER):
                b0 = min(r, a0 + SUB_PER_OFFER)
                keep = CN.bernoulli_keep(d.s, rate[:, a0:b0], rng)
                N[:, a0:b0] = ind @ keep.astype(float)
                S[:, a0:b0] = ind @ np.where(keep, v[:, None], 0.0)
            return Batch(S * g, N, g, "uniform")
        return gen
    raise ValueError(f"unknown null group {e['group']!r}")


def side_matrix(b: Batch, ds: DataSet | None) -> np.ndarray | None:
    """The replications' net-side signs (n, r), or None (always admitted)."""
    if b.g is None:
        return None
    if b.kind == "coin":
        return O.session_side_matrix(b.g, None, coin_net=ds.Cnet)
    traded = (np.broadcast_to(b.N, b.g.shape) > 0)
    return np.where(traded, np.sign(b.g), 0).astype(np.int8)


# ================================================================================================ the scalar re-decision


def _col(X, j: int) -> np.ndarray:
    X = np.asarray(X)
    return X[:, j] if X.shape[1] > 1 else X[:, 0]


def pseudo_trades(S: np.ndarray, N: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Trades with the same session sums: N_j trades of S_j / N_j on session j (the statistics read nothing else)."""
    return Q82._pseudo(S, N)


def trade_sides(b: Batch, ds: DataSet | None, j: int) -> tuple[np.ndarray, np.ndarray]:
    """(sides, sessions) of replication j's trades, for the scalar admission check."""
    g = b.g[:, j]
    if b.kind == "coin":
        return ds.coin.astype(float) * g[ds.s], ds.s
    Nj = np.rint(_col(b.N, j)).astype(np.int64)
    if ds is not None and b.N.shape[1] == 1:
        return g[ds.s], ds.s
    ses = np.repeat(np.arange(len(Nj)), Nj)
    return g[ses], ses


def redecide(cands, S, N, n, levels, sn_crit) -> dict[str, list[bool]]:
    """{candidate: its scalar decisions at `levels`} on one replication's session sums."""
    x, s = pseudo_trades(S, N)
    return {c: [b.rejects for b in O.bound_1s_levels(c, x, s, n, levels=levels, sn_crit=sn_crit)] for c in cands}


# ================================================================================================ running a null


def _new_counts(cands):
    return {(c, s): np.zeros(len(LEVELS), dtype=np.int64) for c in cands for s in SCOPES}


def run_mc(e: dict, gen, ds: DataSet | None, reps: int, batch: int, n: int, cands, sn_crit, *,
           power: bool = False) -> dict:
    """One Monte Carlo null: rejections per candidate, scope and level; the scalar re-decision; the toys' MDLs."""
    rng = np.random.default_rng(e["entropy"])
    counts = _new_counts(cands)
    admitted = 0
    done = 0
    checked, mism = 0, []
    trades, nontie = [], []
    mdls = {(c, s, k): [] for c in cands for s in SCOPES for k in POWER_KS} if power else None
    kidx = {k: O.K_RANGE_1S.index(k) for k in POWER_KS}
    while done < reps:
        r = min(batch, reps - done)
        b = gen(rng, r)
        low = O.evaluate(b.S, b.N, LEVELS, sn_crit=sn_crit, cands=[O.candidate(c) for c in cands])
        m = side_matrix(b, ds)
        if m is None:
            adm = np.ones(r, dtype=bool)
        else:
            R, E = O.runs_and_effective(m)
            adm = O.admits(R, E, n)
            nontie.append((m != 0).sum(axis=0))
        admitted += int(adm.sum())
        trades.append(np.broadcast_to(b.N, b.S.shape).sum(axis=0))
        for c in cands:
            rej = low[c] > 0.0
            counts[(c, "Q")] += rej.sum(axis=1)
            counts[(c, "D")] += (rej & adm[None, :]).sum(axis=1)
            if power and done < POWER_REPS:
                take = min(r, POWER_REPS - done)
                for k, i in kidx.items():
                    md = -low[c][i, :take]
                    mdls[(c, "Q", k)].append(md)
                    mdls[(c, "D", k)].append(np.where(adm[:take], md, np.inf))
        # the scalar re-decision: each candidate's rejections at a family level, and the null's first replications
        adm_s = {}
        for c in cands:
            rej = low[c][:NF] > 0.0
            idx = np.flatnonzero(rej.any(axis=0))
            if done == 0:
                idx = np.union1d(idx, np.arange(min(SCALAR_FIRST, r)))
            for j in idx:
                j = int(j)
                Sj, Nj = _col(b.S, j), _col(b.N, j)
                if m is not None and j not in adm_s:
                    sd, ses = trade_sides(b, ds, j)
                    a_ = O.admission(sd, ses, n).admitted
                    adm_s[j] = a_
                    checked += 1
                    if a_ != bool(adm[j]):
                        mism.append({"null": e["null"], "candidate": "(admission)", "scope": "D", "replication":
                                     done + j, "k": None, "vectorised": bool(adm[j]), "scalar": a_})
                sc = redecide([c], Sj, Nj, n, FAMILY, sn_crit)[c]
                a_s = adm_s.get(j, True)
                for i, k in enumerate(O.K_RANGE_1S):
                    for s_, vec, scal in (("Q", bool(rej[i, j]), sc[i]),
                                          ("D", bool(rej[i, j] and adm[j]), sc[i] and a_s)):
                        checked += 1
                        if vec != scal:
                            mism.append({"null": e["null"], "candidate": c, "scope": s_, "replication": done + j,
                                         "k": k, "vectorised": vec, "scalar": scal})
        done += r
        del b, low
    out = {"counts": counts, "den": reps, "admitted": admitted, "checked": checked, "mismatches": mism,
           "trades_mean": float(np.concatenate(trades).mean()),
           "nontie_mean": float(np.concatenate(nontie).mean()) if nontie else None}
    if power:
        out["mdl"] = {key: np.concatenate(v) for key, v in mdls.items()}
    return out


def _uniform_cells(entropy, n_cells: int) -> list[int]:
    """The exact null's 20 cells drawn uniformly from all its cells, without replacement (the same for every
    candidate), from `default_rng(entropy)`."""
    rng = np.random.default_rng(entropy)
    return sorted(int(x) for x in rng.choice(int(n_cells), size=min(SAMPLE_UNIFORM, int(n_cells)), replace=False))


def run_exact(e: dict, ds: DataSet, n: int, cands, sn_crit) -> dict:
    """One exact null (flips at 42, 55, 63 or the alternating models): exact sizes per candidate, scope and level;
    the scalar re-decision of the declared sample of cells."""
    m = e["model"]
    checked, mism = 0, []
    cobjs = [O.candidate(c) for c in cands]
    if m.startswith("flip"):
        L = _flip_L(m)
        Bs, _ = O.flip_cells(n, L)
        ncell = sum(2 ** b for b in Bs)
        uni = _uniform_cells(e["sample_entropy"], ncell)
        ex = O.exact_flip(ds.V, ds.N, L, LEVELS, sn_crit=sn_crit, cands=cobjs, n_first=SAMPLE_FIRST,
                          uniform_cells=uni)
        num, den, adm_w = ex.num, ex.den, ex.admitted

        def cell_sides(p, q):
            return O.flip_cell_sides(n, L, p, q)
        sampled = []
        for (c, s_), lst in ex.samples.items():
            for cell, p, q, dec in lst:
                sampled.append((c, s_, cell, p, q, dec))
        for cell, p, q, dec, _a in ex.uniform:
            for (c, s_), d in dec.items():
                sampled.append((c, s_, cell, p, q, d))
    else:
        L = int(m[3:])
        sides = O.alternating_sides(n, L)
        low = O.evaluate(sides * ds.V[:, None], ds.N[:, None], LEVELS, sn_crit=sn_crit, cands=cobjs)
        mm = np.where(ds.traded[:, None], sides, 0).astype(np.int8)
        R, E = O.runs_and_effective(mm)
        adm = O.admits(R, E, n)
        den = 2 * L
        adm_w = int(adm.sum())
        num = {}
        uni = _uniform_cells(e["sample_entropy"], den)
        sampled = []
        for c in cands:
            rej = low[c] > 0.0
            for s_, rr in (("Q", rej), ("D", rej & adm[None, :])):
                num[(c, s_)] = [int(x) for x in rr.sum(axis=1)]
                first = [int(x) for x in np.flatnonzero(rr[0])[:SAMPLE_FIRST]]
                for cell in sorted(set(first) | set(uni)):
                    sampled.append((c, s_, cell, cell // 2, cell % 2, tuple(bool(v) for v in rr[:NF, cell])))

        def cell_sides(p, q):
            return sides[:, 2 * p + q]
    # the scalar re-decision of the sampled cells
    stat_cache: dict = {}
    adm_cache: dict = {}
    for c, s_, cell, p, q, dec in sampled:
        sd = cell_sides(p, q)
        if (c, cell) not in stat_cache:
            stat_cache[(c, cell)] = redecide([c], sd * ds.V, ds.N, n, FAMILY, sn_crit)[c]
        sc = stat_cache[(c, cell)]
        if s_ == "D":
            if cell not in adm_cache:
                adm_cache[cell] = O.admission(sd[ds.s], ds.s, n).admitted
            sc = [x and adm_cache[cell] for x in sc]
        for i, k in enumerate(O.K_RANGE_1S):
            checked += 1
            if bool(dec[i]) != bool(sc[i]):
                mism.append({"null": e["null"], "candidate": c, "scope": s_, "replication": cell, "k": k,
                             "vectorised": bool(dec[i]), "scalar": bool(sc[i])})
    return {"counts": {key: np.asarray(v, dtype=np.int64) for key, v in num.items()}, "den": int(den),
            "admitted": int(adm_w), "checked": checked, "mismatches": mism, "trades_mean": float(ds.N.sum()),
            "nontie_mean": float(ds.traded.sum())}


def nesting_problems(e: dict, res: dict, cands) -> list[str]:
    out = []
    for c in cands:
        for s_ in SCOPES:
            v = np.asarray(res["counts"][(c, s_)][:NF])
            if np.any(np.diff(v) > 0):
                out.append(f"{e['null']} {c} scope {s_}: counts {list(map(int, v))} rise with k")
    return out


# ================================================================================================ rows


def _null_desc(e: dict) -> dict:
    return {"null": e["null"], "part": e["part"], "kind": e["kind"], "group": e["group"], "in_rule": e["in_rule"],
            "data": e["data"], "size": e["size"], "j": e["j"], "value": e["value"], "model": e["model"] or e["profile"],
            "L": e["L"], "toy": e["toy"], "entropy": json.dumps(e["entropy"]) if e["entropy"] else None,
            "subset_entropy": json.dumps(e["subset_entropy"]) if e["subset_entropy"] else None,
            "exact_index": e["exact_index"],
            "sample_entropy": json.dumps(e["sample_entropy"]) if e["sample_entropy"] else None}


def _g6(x: float) -> float:
    return float(f"{x:.6g}") if math.isfinite(x) else x


def size_rows(e: dict, res: dict, cands) -> list[dict]:
    desc = _null_desc(e)
    den = int(res["den"])
    rows = []
    for c in cands:
        cand = O.candidate(c)
        for s_ in SCOPES:
            cnt = res["counts"][(c, s_)]
            row = {**desc, "candidate": c, "cid": cand.cid, "scope": s_, "denominator": den,
                   "admitted_share": res["admitted"] / den, "trades_mean": res["trades_mean"],
                   "nontie_sessions_mean": res["nontie_mean"]}
            for lab, a, x in zip(LABELS, LEVELS, cnt):
                x = int(x)
                row[f"count_{lab}"] = x
                row[f"rate_{lab}"] = x / den
                if e["kind"] == "mc":
                    lo, hi = LB.clopper_pearson(x, den)
                    row[f"ci_lo_{lab}"], row[f"ci_hi_{lab}"] = _g6(lo), _g6(hi)
                else:
                    row[f"ci_lo_{lab}"], row[f"ci_hi_{lab}"] = None, None
                row[f"ratio_{lab}"] = _g6((x / den) / a)
            rows.append(row)
    return rows


def _q(v: np.ndarray, p: float) -> float:
    """The p-quantile by numpy's default (linear) rule, an infinite neighbour giving infinity (a builder's reading:
    numpy alone would give NaN between two infinities)."""
    v = np.sort(np.asarray(v, dtype=float))
    if v.size == 0:
        return math.nan
    h = (v.size - 1) * p
    lo, hi = int(math.floor(h)), int(math.ceil(h))
    if not math.isfinite(v[hi]) or not math.isfinite(v[lo]):
        return math.inf if (v[hi] == math.inf or v[lo] == math.inf) else math.nan
    return float(v[lo] + (v[hi] - v[lo]) * (h - lo))


def power_rows(e: dict, res: dict, cands) -> list[dict]:
    rows = []
    for c in cands:
        for s_ in SCOPES:
            for k in POWER_KS:
                v = res["mdl"][(c, s_, k)]
                rows.append({"row": "toy", "null": e["null"], "toy": e["toy"], "size": e["size"], "value": e["value"],
                             "model": e["model"], "candidate": c, "cid": O.candidate(c).cid, "scope": s_, "k": k,
                             "reps_used": int(v.size), "mdl50": _q(v, 0.5), "mdl80": _q(v, 0.8),
                             "infinite_share": float(np.mean(~np.isfinite(v)))})
    return rows


# ================================================================================================ a part


def compute_part(part: str, p: pd.DataFrame | None, n: int, reps: int, seeds: dict, cands, sn_crit, *,
                 reps_beside: int | None = None, only=None, log=_log) -> dict:
    """Every null of `part`, in plan order: size rows, power rows, the re-decision's mismatches, the nesting check
    and the part's meta. Stops after the first null with a scalar disagreement or a nesting violation (E-115 (R1);
    the plan's 4.2): the failed check is recorded, nothing after it is computed."""
    t0 = time.time()
    reps_beside = REPS_BESIDE if reps_beside is None else int(reps_beside)
    inp = Inputs(p, n, seeds)
    plan = [x for x in null_plan(seeds) if x["part"] == part and (only is None or x["null"] in only)]
    size, power, mism, nest, timing = [], [], [], [], []
    checked = 0
    stopped = None
    last_sub = None
    for e in plan:
        t1 = time.time()
        if e["group"] == "subset" and last_sub != (e["size"], e["j"]):
            inp.drop(("ds", "subarrs"))
            last_sub = (e["size"], e["j"])
        if e["kind"] == "exact":
            res = run_exact(e, inp.data_for(e), n, cands, sn_crit)
        else:
            ds = inp.data_for(e) if e["group"] in ("fixed", "subset") else None
            rr = reps if e["in_rule"] else reps_beside
            bb = BATCH if e["in_rule"] else BATCH_BESIDE
            res = run_mc(e, mc_generator(e, inp), ds, rr, min(bb, rr), n, cands, sn_crit, power=bool(e["toy"]))
            if e["toy"]:
                power += power_rows(e, res, cands)
        size += size_rows(e, res, cands)
        checked += res["checked"]
        mism += res["mismatches"]
        nest += nesting_problems(e, res, cands)
        dt = time.time() - t1
        timing.append({"null": e["null"], "kind": e["kind"], "model": e["model"] or e["profile"], "seconds": dt})
        c0 = cands[0]
        log(f"  {e['null']}: {c0} at k=13 Q {int(res['counts'][(c0, 'Q')][0])} D {int(res['counts'][(c0, 'D')][0])}"
            f" of {res['den']}; {dt:.1f} s, ws {working_set_mb():.0f} MB"
            + (f"; DIFFERS in {len(res['mismatches'])} of {res['checked']}" if res["mismatches"] else ""))
        if res["mismatches"] or nest:
            stopped = e["null"]
            break
    meta = {"part": part, "nulls": len(plan), "nulls_done": len(timing), "reps": reps, "reps_beside": reps_beside,
            "seconds": round(time.time() - t0, 1), "peak_working_set_mb": round(working_set_mb(peak=True), 1),
            "scalar_checked": checked, "scalar_mismatched": len(mism), "nesting_violations": nest,
            "stopped_after": stopped, "candidates": list(cands), "n_sessions": n, "timing": timing}
    return {"size": size, "power": power, "mismatches": mism, "meta": meta}


# ================================================================================================ the choice


def _frac_level(lab: str) -> Fraction:
    return O.level_fraction(LEVELS[LABELS.index(lab)])


FAM_LABELS = LABELS[:NF]


def eligibility(size: pd.DataFrame, cands, scopes=SCOPES) -> pd.DataFrame:
    """Per candidate and scope, from the rule's nulls: the floors, P_MC, the worst exact ratio overall and per exact
    model (with the null and k attaining it), and the three conditions."""
    d = size[size["in_rule"].astype(str).str.lower().isin(["true", "1"])]
    out = []
    for c in cands:
        cand = O.candidate(c)
        for s_ in scopes:
            g = d[(d["candidate"] == c) & (d["scope"] == s_)]
            mc, ex = g[g["kind"] == "mc"], g[g["kind"] == "exact"]
            row = {"row": "candidate", "candidate": c, "cid": cand.cid, "scope": s_, "members": cand.n_members,
                   "table_row": cand.row, "in_scope_set": bool(cand.scope_q or s_ == "D"), "mc_nulls": len(mc),
                   "exact_nulls": len(ex)}
            worst_mc, worst_mc_at = -1.0, (None, None)
            mc_floor = True
            pmc = 1.0
            for _, r in mc.iterrows():
                den = int(r["denominator"])
                rates = []
                for lab, k in zip(FAM_LABELS, O.K_RANGE_1S):
                    x = int(r[f"count_{lab}"])
                    if Fraction(x, den) > _frac_level(lab):
                        mc_floor = False
                    ratio = (x / den) / LB.family_level(k)
                    if ratio > worst_mc:
                        worst_mc, worst_mc_at = ratio, (r["null"], k)
                    rates.append(x / den)
                pmc *= p_holds(rates, fail_counts(den), reps=den)
            exact_floor = True
            worst = Fraction(-1)
            worst_at = (None, None)
            per_model = {m: (Fraction(-1), None, None) for m in EXACT_MODELS}
            for _, r in ex.iterrows():
                den = int(r["denominator"])
                for lab, k in zip(FAM_LABELS, O.K_RANGE_1S):
                    sz = Fraction(int(r[f"count_{lab}"]), den)
                    ratio = sz / _frac_level(lab)
                    if sz > _frac_level(lab):
                        exact_floor = False
                    if ratio > worst:
                        worst, worst_at = ratio, (r["null"], k)
                    if ratio > per_model[r["model"]][0]:
                        per_model[r["model"]] = (ratio, r["null"], k)
            row.update({"mc_floor_ok": mc_floor, "mc_worst_ratio": worst_mc, "mc_worst_null": worst_mc_at[0],
                        "mc_worst_k": worst_mc_at[1], "exact_floor_ok": exact_floor, "p_mc": pmc,
                        "worst_exact_ratio": float(worst) if worst >= 0 else math.nan,
                        "worst_exact_null": worst_at[0], "worst_exact_k": worst_at[1],
                        "cond1_floors": bool(mc_floor and exact_floor), "cond2_p_mc": bool(pmc >= P_MC_MIN),
                        "cond3_ratio": bool(worst <= RATIO_MAX) if worst >= 0 else False})
            for m in EXACT_MODELS:
                rr, nn, kk = per_model[m]
                row[f"worst_ratio_{m}"] = float(rr) if rr >= 0 else math.nan
                row[f"worst_null_{m}"] = nn
                row[f"worst_k_{m}"] = kk
            row["eligible"] = bool(row["in_scope_set"] and row["cond1_floors"] and row["cond2_p_mc"]
                                   and row["cond3_ratio"])
            row["refused_by_cond3_alone"] = bool(row["in_scope_set"] and row["cond1_floors"] and row["cond2_p_mc"]
                                                 and not row["cond3_ratio"])
            out.append(row)
    return pd.DataFrame(out)


def power_summary(power: pd.DataFrame, cands, scopes=SCOPES) -> pd.DataFrame:
    """P(c) per candidate and scope: the geometric mean over the ten `win1` toys of their MDL80 at k = 13 (infinite
    when any toy's is); beside, the same geometric means of MDL50 and MDL80 at k = 13, 15 and 20, and P relative to
    C0's in the same scope."""
    t = power[(power["row"] == "toy") & (power["toy"] == "P")]
    out = []
    for c in cands:
        for s_ in scopes:
            g = t[(t["candidate"] == c) & (t["scope"] == s_)]
            row = {"row": "P", "candidate": c, "cid": O.candidate(c).cid, "scope": s_,
                   "toys": int(g[g["k"] == 13].shape[0])}
            for k in POWER_KS:
                for q in ("mdl50", "mdl80"):
                    v = g[g["k"] == k][q].astype(float).to_numpy()
                    row[f"{q}_k{k}_geomean"] = _geomean(v)
            row["P"] = row["mdl80_k13_geomean"]
            out.append(row)
    df = pd.DataFrame(out)
    for s_ in scopes:
        base = df[(df["candidate"] == "cons") & (df["scope"] == s_)]["P"]
        b = float(base.iloc[0]) if len(base) else math.nan
        sel = df["scope"] == s_
        df.loc[sel, "P_rel_C0"] = df.loc[sel, "P"].astype(float) / b if (b and math.isfinite(b)) else math.nan
    return df


def _geomean(v) -> float:
    v = np.asarray(v, dtype=float)
    if v.size == 0 or np.isnan(v).any():
        return math.nan
    if (v == np.inf).any():
        return math.inf
    if (v <= 0).any():
        return math.nan                                        # an MDL at or below zero has no geometric mean
    return float(np.exp(np.log(v).mean()))


def _rank_key(r) -> tuple:
    P = float(r["P"]) if r["P"] is not None and not (isinstance(r["P"], float) and math.isnan(r["P"])) else math.inf
    return (P, int(r["members"]), int(r["table_row"]))


def choose(elig: pd.DataFrame, psum: pd.DataFrame) -> dict:
    """The plan's 4.2: the most powerful eligible candidate in scope Q, else in scope D, else NONE; ties to fewer
    members, then the earlier row. Beside, per scope, the most powerful candidate refused by condition 3 alone."""
    t = elig.merge(psum[["candidate", "scope", "P", "P_rel_C0"] + [c for c in psum.columns if "geomean" in c]],
                   on=["candidate", "scope"], how="left")
    chosen = None
    for s_ in SCOPES:
        g = t[(t["scope"] == s_) & t["eligible"]]
        if len(g):
            best = min((r for _, r in g.iterrows()), key=_rank_key)
            chosen = {"candidate": best["candidate"], "cid": best["cid"], "scope": s_}
            break
    refused = {}
    for s_ in SCOPES:
        g = t[(t["scope"] == s_) & t["refused_by_cond3_alone"]]
        if len(g):
            r = min((r for _, r in g.iterrows()), key=_rank_key)
            refused[s_] = {"candidate": r["candidate"], "cid": r["cid"], "scope": s_, "P": r["P"],
                           **{c: r[c] for c in t.columns if "geomean" in c}}
    t["chosen"] = False
    if chosen is not None:
        t.loc[(t["candidate"] == chosen["candidate"]) & (t["scope"] == chosen["scope"]), "chosen"] = True
    line = f"CHOSEN {chosen['candidate']} (scope {chosen['scope']})" if chosen else "NONE"
    return {"table": t, "chosen": chosen, "line": line, "refused": refused}


def choice_frame(ch: dict) -> pd.DataFrame:
    """q108_choice.csv: every candidate in both scopes, then the decision row and the refused-candidate rows."""
    t = ch["table"].copy()
    rows = [t]
    dec = {"row": "decision", "decision": ch["line"], "candidate": ch["chosen"]["candidate"] if ch["chosen"] else None,
           "cid": ch["chosen"]["cid"] if ch["chosen"] else None,
           "scope": ch["chosen"]["scope"] if ch["chosen"] else None}
    rows.append(pd.DataFrame([dec]))
    ref = []
    for s_, r in ch["refused"].items():
        ref.append({"row": "refused_by_cond3_alone", **r,
                    "decision": "the most powerful candidate refused by condition 3 alone in scope " + s_})
    if ref:
        rows.append(pd.DataFrame(ref))
    return pd.concat(rows, ignore_index=True, sort=False)


def spread_rows(size: pd.DataFrame) -> list[dict]:
    """Each subset construction's spread across its subsets (per model, value and size, and pooled over sizes): how
    many subsets sit above nominal, and the median, 90th percentile and largest ratio to nominal, at each level."""
    d = size[(size["group"] == "subset")]
    out = []
    for (m, v, c, s_), g in d.groupby(["model", "value", "candidate", "scope"], sort=True):
        for z, gz in [(zz, g[g["size"] == zz]) for zz in sorted(g["size"].unique())] + [("all", g)]:
            row = {"row": "spread", "null": f"spread:{z}:{v}:{m}", "group": "subset", "model": m, "value": v,
                   "size": z, "candidate": c, "cid": O.candidate(c).cid, "scope": s_, "subsets": int(len(gz))}
            for lab in LABELS:
                r = gz[f"ratio_{lab}"].astype(float).to_numpy()
                row[f"above_{lab}"] = int((r > 1.0).sum())
                row[f"median_ratio_{lab}"] = _g6(float(np.median(r)))
                row[f"p90_ratio_{lab}"] = _g6(float(np.quantile(r, 0.9)))
                row[f"max_ratio_{lab}"] = _g6(float(r.max()))
            out.append(row)
    return out


def expected_counts(seeds: dict | None = None) -> dict[str, int]:
    """The null counts of `null_plan` (2,293 in the rule, 1,170 of them exact; 54 and 30 beside, at the plan's grid)."""
    plan = null_plan(seeds or SEEDS)
    rule = [x for x in plan if x["in_rule"]]
    return {"rule": len(rule), "rule_exact": sum(x["kind"] == "exact" for x in rule),
            "rule_mc": sum(x["kind"] == "mc" for x in rule),
            "beside_cp": sum(x["group"] == "beside_cp" for x in plan),
            "beside_flat": sum(x["group"] == "beside_flat" for x in plan)}


def completeness_problems(size: pd.DataFrame, cands, want: dict | None = None) -> list[str]:
    """Every candidate, both scopes, on all 2,293 nulls in the rule and the 84 beside."""
    out = []
    want = EXPECTED if want is None else want
    for c in cands:
        for s_ in SCOPES:
            g = size[(size["candidate"] == c) & (size["scope"] == s_)]
            rule = g[g["in_rule"].astype(str).str.lower().isin(["true", "1"])]
            got = {"rule": rule["null"].nunique(), "rule_exact": int((rule["kind"] == "exact").sum()),
                   "rule_mc": int((rule["kind"] == "mc").sum()),
                   "beside_cp": int((g["group"] == "beside_cp").sum()),
                   "beside_flat": int((g["group"] == "beside_flat").sum())}
            if got != want:
                out.append(f"{c} scope {s_}: {got}, not {want}")
    return out


def calibrate_tables(parts_out: list[dict], cands, want: dict | None = None) -> dict:
    """From the parts' outputs: the checks (R1, nesting, completeness), and when they pass the size, power and choice
    tables. Writes nothing."""
    size = pd.DataFrame([r for p in parts_out for r in p["size"]])
    power = pd.DataFrame([r for p in parts_out for r in p["power"]])
    mism = [m for p in parts_out for m in p["mismatches"]]
    nest = [x for p in parts_out for x in p["meta"]["nesting_violations"]]
    failed = []
    if mism:
        failed.append(f"the scalar re-decision DIFFERS in {len(mism)} decisions (E-115 (R1)): first "
                      f"{mism[0]}")
    if nest:
        failed.append(f"the nesting assertion fails on {len(nest)} (the plan's 4.2): first {nest[0]}")
    out = {"size": size, "power": power, "mismatches": mism, "failed": failed}
    if failed:
        return out
    inc = completeness_problems(size, cands, want)
    if inc:
        out["failed"] = [f"nulls missing: {inc[:3]}"]
        return out
    elig = eligibility(size, cands)
    psum = power_summary(power, cands)
    ch = choose(elig, psum)
    out.update({"elig": elig, "psum": psum, "choice": ch,
                "size_out": pd.concat([size, pd.DataFrame(spread_rows(size))], ignore_index=True, sort=False)
                if len(size) else size,
                "power_out": pd.concat([power, psum], ignore_index=True, sort=False)})
    return out


# ================================================================================================ the commands


def _outside_tree(work: Path) -> bool:
    w = Path(work).resolve()
    return ROOT.resolve() not in [w, *w.parents]


def _check_read() -> int:
    from extended import reader

    print(f"reader: purpose=registered_design declaration={READ_ROW} design={READ_DESIGN} span {JUDGED_FIRST} to "
          f"{JUDGED_LAST} files {DAYS_REL} (columns date)", flush=True)
    try:
        reader.authorise(JUDGED_FIRST, JUDGED_LAST, purpose=reader.REGISTERED_DESIGN, declaration=READ_ROW,
                         design=READ_DESIGN, what=f"{DECISION}: the judged session list (check only)")
    except (reader.ReadRefused, ValueError) as exc:
        text = str(exc)
        print(text if text.startswith("REFUSED") else f"REFUSED: {type(exc).__name__}: {text}", flush=True)
        return REFUSED
    print("reader: AUTHORISED (nothing read)", flush=True)
    return 0


def load_sn_table(path: Path) -> dict[float, float]:
    t = pd.read_csv(path, float_precision="round_trip")
    return {float(a): float(c) for a, c in zip(t["level"], t["critical"])}


def sn_table_frame(table: dict[float, float]) -> pd.DataFrame:
    return pd.DataFrame([{"level": a, "k": O.k_of(a), "label": LABELS[LEVELS.index(a)], "draws": O.SN_DRAWS,
                          "rank": O.sn_rank(a), "critical": c} for a, c in table.items()])


def compute_main(a, script: str, seeds: dict) -> int:
    """`--compute <part>`: one part in its own process, its tables into the work folder."""
    work = Path(a.work)
    if not _outside_tree(work):
        print(f"REFUSED: the work folder {work} must lie outside this tree", flush=True)
        return REFUSED
    cal, sha = judged_sessions(pd.read_csv(a.calendar, dtype=str)["date"].tolist())
    d = work / a.compute
    d.mkdir(parents=True, exist_ok=True)
    if a.compute == "sn":
        t = O.sn_reference([int(seeds["sn_table"]), 0])
        sn_table_frame(t).to_csv(d / "table.csv", index=False)
        (d / "meta.json").write_text(json.dumps({"part": "sn", "peak_working_set_mb": working_set_mb(peak=True),
                                                 "calendar_sha256": sha}), encoding="utf-8")
        return 0
    p = None
    if a.compute != "syn":
        p, _ = Q82.load_pairs(Path(a.pairs_file), cal)
    sn = load_sn_table(Path(a.sn_table))
    cands = a.candidates.split(",")
    out = compute_part(a.compute, p, len(cal), a.reps, seeds, cands, sn, reps_beside=a.reps_beside)
    pd.DataFrame(out["size"]).to_csv(d / "size.csv", index=False)
    pd.DataFrame(out["power"]).to_csv(d / "power.csv", index=False)
    pd.DataFrame(out["mismatches"]).to_csv(d / "mismatches.csv", index=False)
    out["meta"]["calendar_sha256"] = sha
    (d / "meta.json").write_text(json.dumps(out["meta"], indent=1, default=str), encoding="utf-8")
    return FAILED_CHECK if (out["mismatches"] or out["meta"]["nesting_violations"]) else 0


def _step(name: str, args: list[str]) -> int:
    _log(f"step {name}: {' '.join(args)}")
    t0 = time.time()
    r = subprocess.run([sys.executable, *args], cwd=str(ROOT))
    _log(f"step {name}: exit {r.returncode}, {time.time() - t0:.0f} s")
    return r.returncode


def read_part(work: Path, part: str) -> dict:
    d = work / part

    def rd(f):
        p = d / f
        if not p.is_file() or p.stat().st_size <= 1:
            return []
        try:
            return pd.read_csv(p, low_memory=False, float_precision="round_trip").to_dict("records")
        except pd.errors.EmptyDataError:
            return []
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    return {"size": rd("size.csv"), "power": rd("power.csv"), "mismatches": rd("mismatches.csv"), "meta": meta}


def _versions() -> dict:
    import scipy

    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "pandas": pd.__version__}


def preflight(target: Path) -> list[str]:
    """The refusals before any step, in order (each a reason; empty when the run may start)."""
    from extended import results as XR

    bad = XR.clean_run_problem()                         # each runner refuses outside a clean run (the plan's 6.1)
    if bad:
        return [f"this process is not a clean run -- {bad}. Run it as: {RUN_CMD}"]
    clash = [x for x in RESULT_FILES if (target / f"{x}.csv").exists() or (target / f"{x}.csv.manifest.json").exists()]
    if clash:
        return [f"{clash} exist in {target}; a result file is never overwritten"]
    probs = pin_problems()
    probs += seed_map_problems(SEEDS, CAL_BLOCK, CAL_ROLES + ("tests",))
    return probs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check-read", action="store_true")
    ap.add_argument("--compute", default=None, help=argparse.SUPPRESS)
    ap.add_argument("--work", type=Path, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--calendar", type=Path, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--pairs-file", type=Path, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--sn-table", type=Path, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--candidates", default=",".join(O.NAMES), help=argparse.SUPPRESS)
    ap.add_argument("--reps", type=int, default=REPS, help=argparse.SUPPRESS)
    ap.add_argument("--reps-beside", type=int, default=REPS_BESIDE, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.check_read:
        return _check_read()
    if a.compute is not None:
        from extended import results as XR

        if XR.clean_run_problem():
            print("REFUSED: a part runs only inside the clean run that started it", flush=True)
            return REFUSED
        return compute_main(a, SCRIPT, SEEDS)
    t0 = time.time()
    from extended import results as XR

    target = RESULTS_DIR
    probs = preflight(target)
    if probs:
        print("REFUSED: " + "; ".join(probs), flush=True)
        return REFUSED
    seed_probs, seed_notes = seed_block_problems(ROOT)
    for x in seed_notes:
        _log(f"seed blocks: {x}")
    if seed_probs:
        print("REFUSED: the plan's seed blocks are not unused -- " + "; ".join(seed_probs[:10]) + ". The run stops "
              "here; no other seeds are picked: report it to the lead.", flush=True)
        return REFUSED
    _log(f"seed blocks: unused outside the allow-list; the map {SEEDS}, spare {list(SPARE)}")
    name = os.environ.get(CLEAN_RUN_ENV)
    work = Path(RUNS_DIR) / f"{name}.work" if name else Path(tempfile.mkdtemp(prefix="q108_"))
    work.mkdir(parents=True, exist_ok=True)
    if not _outside_tree(work):
        print(f"REFUSED: the work folder {work} must lie outside this tree", flush=True)
        return REFUSED
    cal, cal_sha, cal_src = read_calendar()
    bad = calendar_problems(cal, cal_sha)
    if bad:
        print("REFUSED: " + "; ".join(bad), flush=True)
        return REFUSED
    calf = work / "judged_sessions.csv"
    pd.DataFrame({"date": cal}).to_csv(calf, index=False)
    _log(f"judged sessions: {len(cal)}, {cal[0]} to {cal[-1]}, sha256 {cal_sha} (E-094 (2))")
    pairs = work / "pairs"
    if _step("pairs", ["scripts/q16_p16_pairs.py", "--out", str(pairs)]):
        return 1
    pq = pairs / "p16_pairs.parquet"
    pairs_meta = json.loads((pairs / "p16_pairs.json").read_text(encoding="utf-8"))
    common = ["--work", str(work), "--calendar", str(calf)]
    if _step("sn", [SCRIPT, "--compute", "sn", *common]):
        return 1
    snf = work / "sn" / "table.csv"
    rc_all = {}
    for part in PARTS:
        rc = _step(part, [SCRIPT, "--compute", part, *common, "--pairs-file", str(pq), "--sn-table", str(snf)])
        rc_all[part] = rc
        if rc == FAILED_CHECK:
            break
        if rc:
            return 1
    outs = [read_part(work, p) for p in PARTS if (work / p / "meta.json").is_file()]
    res = calibrate_tables(outs, list(O.NAMES))
    if res["failed"] or any(v == FAILED_CHECK for v in rc_all.values()):
        for f in res["failed"] or ["a part stopped on a failed check"]:
            print(f"FAILED CHECK: {f}", flush=True)
        print("FAILED CHECK: no result is written and no choice is made; the record is in " + str(work), flush=True)
        _log(f"EXIT {FAILED_CHECK} ({time.time() - t0:.0f} s)")
        print(f"EXIT {FAILED_CHECK}", flush=True)
        return FAILED_CHECK
    ch = res["choice"]
    _log(f"read ledger: {XR.note_ledger_appends()}")
    blobs = {rel: blob_id(ROOT / rel) for rel in ("extended/lift_bound.py", MODULE, "extended/count_nulls.py",
                                                  "scripts/q16_calibrate.py", "scripts/q82_validation.py", SCRIPT,
                                                  "scripts/q16_p16_pairs.py")}
    metas = {m["meta"]["part"]: {x: m["meta"].get(x) for x in ("nulls", "seconds", "peak_working_set_mb",
                                                                "scalar_checked", "scalar_mismatched")} for m in outs}
    common_p = {
        "decision": DECISION, "plan": PLAN, "plan_sha256": PLAN_SHA256, "task": "Q-108", "argv": sys.argv[1:],
        "reps": REPS, "reps_beside": REPS_BESIDE, "batch": BATCH, "batch_beside": BATCH_BESIDE,
        "levels": list(LEVELS), "k_range": list(O.K_RANGE_1S), "candidates": list(O.NAMES),
        "n_sessions": len(cal), "calendar_sha256": cal_sha, "calendar_source": cal_src,
        "pairs_sha256": pairs_meta.get("parquet_sha256"), "pairs_identity": pairs_meta.get("identity"),
        "blobs": blobs, "versions": _versions(), "seed_map": {k: int(v) for k, v in SEEDS.items()},
        "spare_seeds": list(SPARE), "seed_block": list(CAL_BLOCK),
        "seed_check": "unused outside the allow-list; notes: " + ("; ".join(seed_notes) or "none"),
        "scalar_redecision": {"checked": sum(m["meta"]["scalar_checked"] for m in outs), "mismatched": 0},
        "parts": metas, "fail_counts": FAIL, "p_mc_min": P_MC_MIN, "ratio_max": str(RATIO_MAX),
        "choice": ch["line"]}
    sn_t = pd.read_csv(snf, float_precision="round_trip")
    out = {
        "q108_cal_size": (res["size_out"], SEEDS["fixed_mc"], ("fixed_mc", "subsets", "subset_mc", "synthetic",
                                                               "beside_cp", "beside_flat", "exact_sample"),
                          "Q-108 (E-115): every null x candidate x scope x level -- Monte Carlo rejections with their "
                          "95 % interval, or the exact size -- and each subset construction's spread"),
        "q108_cal_power": (res["power_out"], SEEDS["subset_mc"], ("subsets", "subset_mc", "synthetic"),
                           "Q-108 (E-115): the toys' MDL50 and MDL80 at k = 13, 15, 20 (first 20,000 replications) "
                           "and P(c) per candidate and scope"),
        "q108_sn_table": (sn_t, SEEDS["sn_table"], ("sn_table",),
                          "Q-108 (E-115): C8's reference -- the ceil(a D)-th largest T of 2,000,000 iid normal draws"),
        "q108_choice": (choice_frame(ch), None, (),
                        f"Q-108 (E-115): the plan's 4.2 applied by code -- {ch['line']}; computed from the size and "
                        "power tables beside, no randomness of its own"),
    }
    for nm, (df, seed, roles, desc) in out.items():
        params = {**common_p, "seeds": {r: int(SEEDS[r]) for r in roles}}
        csv, man = XR.write_result(df, nm, script=SCRIPT, seed=seed, parameters=params, description=desc,
                                   exploratory=False, require_seed=seed is not None)
        _log(f"wrote {csv} ({len(df)} rows) and {man.name}")
    for s_, r in ch["refused"].items():
        print(f"refused by condition 3 alone (scope {s_}): {r['candidate']} P {r['P']}", flush=True)
    print(ch["line"], flush=True)
    _log(f"EXIT 0 ({time.time() - t0:.0f} s)")
    print("EXIT 0", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
