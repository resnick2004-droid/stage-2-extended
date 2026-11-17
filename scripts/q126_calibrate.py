"""Q-126 (E-187): the one-sample pass line's second calibration -- heavy, on the calibration seeds only, from the pinned
plan `docs/calibration/Q-126_one_sample_plan_2.md` (sha256 117f5eb3..., E-187). It measures every candidate of
`extended/lift_one_sample2.py` in both scopes on the plan's nulls, applies the plan's choice rule (its 4.2) by code,
never by hand, and writes what the plan declares (its 6.2).

    python scripts/run_clean.py --name q126-calibrate --task Q-126 --hours <from the build's measurement> --mem-gb 1.5 -- python scripts/q126_calibrate.py
    python scripts/q126_calibrate.py --check-read      # the reader's verdict on the calendar read; reads and writes nothing

**The declared parts (the plan's 6.2, B-27), in order, all under the one lock and from the same clean commit:**
`core` (the pairs step and Q-108's class), `sizing200` ... `sizing5000` (the sizing subsets, one part a size), `probe`
(it needs the sizing parts' rankings), `drift` (beside), `choice`. With no `--parts` the command runs them all in turn,
each in its own process; `--parts a,b` runs those only (a crash's rerun). Each part writes all its output or none:
into a temporary folder of the run's work folder (`%LOCALAPPDATA%/stage2-extended-runs/q126-calibrate.work`), with its
own manifest (the commit, the seed map, the part, the package versions, each data file's sha256), renamed into place
when it is whole; a partial folder is deleted and counts as no output.

**The crash rule (6.2).** A part that exits non-zero with no failed check and no output may be run again from scratch
(its output is fixed by the commit and the seeds). A part already whole at this commit is not run again. **A failed
check** -- the nesting assertion, a scalar mismatch, the provenance assertion -- leaves its record in `<part>.failed`
and is never rerun: the command refuses while one is there. After a code fix (a new commit) every whole part of the
earlier commit is moved to `<part>.prev-<commit>` and rerun, and must reproduce each of its data files' sha256, or the
run stops.

**The choice** reads every part's manifest and refuses a missing part, another commit, another seed map or other
package versions; it alone writes the result files, through `extended.results`, all or none (every frame and name
checked before the first write): `q126_cal_size.csv` (the core and the probe, every null x candidate x scope x level,
and each subset construction's spread), `q126_cal_sizing.csv` and `q126_cal_drift.csv` (the sizing and drift nulls, one
row a null, every candidate x scope x level as columns -- a builder's reading: in Q-108's long form the sizing alone
would be about 0.4 GB, past the remote's file limit), `q126_cal_power.csv`, `q126_cal_cells.csv`, `q126_choice.csv`.

**Refusals (exit 3), before any read:** outside a clean run; `run.lock` not held by this run's own job; a result file
that exists; a pinned file other than its pin (the plan's sha256 and its E-187 row, `lift_bound.py`, `lift_one_sample.py`
and the Q-108/Q-16/Q-82 runners imported); a seed map other than the plan's 4.1 table as parsed from the pinned plan;
**the seed-provenance assertion** (every generator entropy, in full, the plan's 4.1 entropy for that null); either seed
block named or derived outside the allow-list (Q-108's guard, re-pointed); a work folder inside the tree; a failed
part on record; a calendar other than E-094 (2)'s. **A failed check (exit 5):** a scalar disagreement, a nesting
violation (in k, or in m on rows 1-7), a missing null, a reproduction that differs.

**Reads**, as Q-108's 6.1: the judged calendar through `extended.reader.read_walks` (purpose `registered_design`,
E-035, P-16), its count and sha256 asserted; P-16's pairs through `scripts/q16_p16_pairs.py`. Both in the core part
only; the later parts read them from the core part's output, its sha256 checked. No other bar is opened.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Mapping
from fractions import Fraction
from pathlib import Path

for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import CLEAN_RUN_ENV, RESULTS_DIR, RUNS_DIR  # noqa: E402
from extended import lift_bound as LB  # noqa: E402
from extended import lift_one_sample as O  # noqa: E402
from extended import lift_one_sample2 as L2  # noqa: E402
from extended.procmem import working_set_mb  # noqa: E402


class ProvenanceRefused(RuntimeError):
    """A draw would take a seed the plan's 4.1 does not declare for it (Q-108's retired maps included)."""


class RetiredSeedMap(Mapping):
    """Q-108's retired seed map, replaced in this runner's private copy of Q-108's code: any read of it -- a Q-108
    construction called without a seed map falls back to it -- refuses (the plan's 4.1, B-28)."""

    def __init__(self, what: str):
        self.what = what

    def _refuse(self, *a):
        raise ProvenanceRefused(f"REFUSED: {self.what} is retired (the plan's 4.1): a Q-108 construction was called "
                                "without this run's own seed map")

    __getitem__ = __iter__ = __len__ = __contains__ = get = keys = items = values = _refuse


def _load(name: str, rel: str):
    """A private copy of a script as a module, registered under `name` (its dataclasses resolve through it)."""
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


#: Q-108's calibration runner, a private copy (its file is never edited): its streams, subsets, side generators,
#: failure counts and P_MC's dynamic program, and its seed guard re-pointed at this plan's blocks below. Its retired
#: seed map is replaced by a refusal, so a construction called without this run's map cannot draw it.
CAL = _load(f"q108_calibrate_for_{__name__}", "scripts/q108_calibrate.py")
CAL.SEEDS = RetiredSeedMap("Q-108's calibration seed map")


def _not_this_run(*a, **k):
    raise ProvenanceRefused("REFUSED: Q-108's part runner builds Q-108's null plan; this run builds its own (4.1)")


#: Q-108's part runner and command are never this run's: their null plan is Q-108's
CAL.compute_part = CAL.main = CAL.preflight = _not_this_run
Q82 = CAL.Q82
Q16 = CAL.Q16

SCRIPT = "scripts/q126_calibrate.py"
VALIDATE_SCRIPT = "scripts/q126_validate.py"
MODULE = "extended/lift_one_sample2.py"
DECISION = "E-187"
TASK = "Q-126"
PLAN_NAMES = ("docs/calibration/Q-126_one_sample_plan_2.md", "docs/calibration/DRAFT_Q-126_one_sample_plan_2.md")
PLAN_SHA256 = "117f5eb36dfd8312b24db35d1e6898167397fe374ae47a1feab94b5a2ebfcdc6"
#: the files this runner imports and must not have changed: `lift_bound.py` (F-03's pin), `lift_one_sample.py` as built
#: (E-126), and the Q-108, Q-16 and Q-82 code it reuses -- each the blob Q-108's calibration ran
#: (`results/q108_cal_size.csv.manifest.json`)
VALIDATED_BLOBS = {
    "extended/lift_bound.py": "984f3467a4a05aa790d3ea43e94ac7761f0725b2",
    "extended/lift_one_sample.py": "36df2c6f82a60b63213528d5907db082b23c9d6e",
    "extended/count_nulls.py": "c4ceee8ffb243bb8dc07cb51be5397daae906c02",
    "scripts/q108_calibrate.py": "30ce697f04010b802b93d0685386d8fdc17141ee",
    "scripts/q16_calibrate.py": "677d6a738283a2c44d3ffa6b6650e131d99088f4",
    "scripts/q16_p16_pairs.py": "1bdd21a3b654ea01b1e7a9d0d0bea142a6aa0db6",
    "scripts/q82_validation.py": "9490fc57f855be5d61ee8d4ddb62c7b63e05a282",
}
READ_ROW, READ_DESIGN = "E-035", "P-16"
JUDGED_FIRST, JUDGED_LAST = CAL.JUDGED_FIRST, CAL.JUDGED_LAST
N_SESSIONS = CAL.N_SESSIONS
JUDGED_SHA256 = CAL.JUDGED_SHA256
DAYS_REL = CAL.DAYS_REL
WORK_NAME = "q126-calibrate.work"
RUN_CMD = ("python scripts/run_clean.py --name q126-calibrate --task Q-126 --hours <measured> --mem-gb 1.5 -- "
           "python scripts/q126_calibrate.py")

# ---- the seed blocks (the plan's 4.1) ----
CAL_BLOCK = tuple(range(20263010, 20263020))
VAL_BLOCK = tuple(range(20263020, 20263030))
#: the calibration block's map; `seed_map_problems` holds it to the plan's table as parsed from the pinned file
SEEDS = {
    "tests": 20263010,          # the calibration build's tests
    "fixed_mc": 20263011,       # the fixed-data streams' Monte Carlo side draws: [s, i]
    "subsets": 20263012,        # the thinned subsets: (z, j) by [s, z_index, j], j = 0..659
    "subset_mc": 20263013,      # the core subsets' Monte Carlo side draws: [s, z_index, j, value_index, model_index]
    "synthetic": 20263014,      # the realistic synthetic nulls: [s, i], i the null's index in Q-16's list
    "beside_cp": 20263015,      # the count-persistent nulls beside: [s, i]
    "beside_flat": 20263016,    # the `flat` form beside: [s, i]
    "exact_sample": 20263017,   # the exact nulls' seeded sample of cells: [s, exact null index]
    "drift": 20263018,          # the drift populations beside: [s, c, r]
    "probe": 20263019,          # the probe's Monte Carlo side draws: [s, z_index, j, value_index, model_index]
}
SPARE: tuple[int, ...] = ()
# ---- end of the seed blocks ----

#: each role's use as the plan's 4.1 table words it (its first words): the parse maps the table's rows to roles by them
ROLE_TEXT = {
    "tests": "the calibration build's tests",
    "fixed_mc": "the fixed-data streams' Monte Carlo side draws",
    "subsets": "the thinned subsets",
    "subset_mc": "the core subsets' Monte Carlo side draws",
    "synthetic": "the realistic synthetic nulls",
    "beside_cp": "the count-persistent nulls beside",
    "beside_flat": "the `flat` form beside",
    "exact_sample": "the exact nulls' seeded sample of cells",
    "drift": "the drift populations beside",
    "probe": "the probe's Monte Carlo side draws",
}
#: the roles a calibration draws (the tests' seed is drawn by the build's tests only)
DRAW_ROLES = ("fixed_mc", "subsets", "subset_mc", "synthetic", "beside_cp", "beside_flat", "exact_sample", "drift",
              "probe")

# ---- the nulls (the plan's 3) ----
MODELS = CAL.MODELS
EXACT_MODELS = CAL.EXACT_MODELS
PERSISTENT = CAL.PERSISTENT
NONPERSISTENT = CAL.NONPERSISTENT
FIXED_MC_MODELS = CAL.FIXED_MC_MODELS
STREAMS = CAL.STREAMS
VALUES = CAL.VALUES
SIZES = CAL.SIZES
REALISTIC = CAL.REALISTIC
FLAT_L = CAL.FLAT_L
CP_ONE = CAL.CP_ONE
#: the core subsets j = 0..22 at each size; the persistent models on all, the flips at 1 and 5 and the coin on 0..4
N_CORE = 23
N_NONPERSISTENT = 5
#: the calibration's subsets at each size, j = 0..659 (the plan's 3.2): j >= 23 are the sizing subsets
N_SUBSETS = 660
#: the probe: the 23 largest-exact-size sizing subsets at each size carry the four persistent Monte Carlo models
PROBE_PER_SIZE = 23
PROBE_MODELS = ("flip21", "markov30", "markov50", "markov80")
#: the drift nulls (3.3): Appendix A's eight scenarios, 150 populations each, exact at the five exact models
DRIFT_SCENARIOS = L2.DRIFT_SCENARIOS
DRIFT_POPULATIONS = L2.DRIFT_POPULATIONS
#: replications and batches (Q-108's)
REPS = CAL.REPS
REPS_BESIDE = CAL.REPS_BESIDE
BATCH = CAL.BATCH
BATCH_BESIDE = CAL.BATCH_BESIDE
#: the scalar re-decision (4.1): each MC null's first replications and every MC rejection at a family level; on the
#: core's exact nulls the first 100 cells rejecting at k = 13 per candidate and scope plus the same 20 uniform cells,
#: on the sizing nulls the first 5 and no uniform cells
SCALAR_FIRST = CAL.SCALAR_FIRST
SAMPLE_FIRST_CORE = 100
SAMPLE_FIRST_SIZING = 5
POWER_REPS = CAL.POWER_REPS
POWER_KS = CAL.POWER_KS
P_MC_MIN = 0.9
RATIO_MAX = Fraction(1, 4)
LEVELS = O.LEVELS_1S
FAMILY = O.FAMILY_LEVELS_1S
NF = len(FAMILY)
KS = O.K_RANGE_1S
LABELS = CAL.LABELS
FAM_LABELS = LABELS[:NF]
SCOPES = L2.SCOPES
CANDS = L2.NAMES
#: the reference P is stated against (the plan's 5)
REFERENCE = "cons_m1.25"
#: the counts the plan declares (its 3.2 and 3.5); `expected_counts` computes them from the grid and a test holds them
EXPECTED = {"core_rule": 2293, "core_exact": 1170, "core_mc": 1123, "beside_cp": 54, "beside_flat": 30,
            "sizing": 31850, "probe": 920, "drift": 6000, "rule": 35063, "exact_index_max": 33019}
RESULT_FILES = ("q126_cal_size", "q126_cal_sizing", "q126_cal_drift", "q126_cal_power", "q126_cal_cells",
                "q126_choice")
PARTS = ("core", *(f"sizing{z}" for z in SIZES), "probe", "drift", "choice")
#: exit codes
REFUSED, FAILED_CHECK = 3, 5


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S', time.gmtime())} UTC] {msg}", flush=True)


# ================================================================================================ the pinned plan


def plan_path(repo: Path = ROOT) -> Path:
    """The pinned plan under either of its names (exactly one present)."""
    found = [Path(repo) / p for p in PLAN_NAMES if (Path(repo) / p).is_file()]
    if len(found) != 1:
        raise ProvenanceRefused(f"REFUSED: exactly one Q-126 plan is expected ({PLAN_NAMES}); found {found}")
    return found[0]


def file_sha_lf(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


SEED_ROW = re.compile(r"^\|\s*(\d{8})\s*\|\s*([^|]+?)\s*\|\s*$", re.MULTILINE)


def plan_seed_tables(text: str) -> dict[str, list[tuple[int, str]]]:
    """The plan's 4.1 tables, parsed: {"calibration": [(seed, use)], "validation": [(seed, use)]}."""
    text = text.replace("\r\n", "\n")
    i = text.index("### 4.1")
    j = text.index("### 4.2", i)
    s = text[i:j]
    c = s.index("**Calibration block,")
    v = s.index("**Validation block,")
    return {"calibration": [(int(a), b) for a, b in SEED_ROW.findall(s[c:v])],
            "validation": [(int(a), b) for a, b in SEED_ROW.findall(s[v:])]}


def parsed_seed_map(text: str, block: str, role_text: dict) -> tuple[dict[str, int], list[int]]:
    """(role -> seed, spare seeds) from the plan's table for `block`, each role found by its use's first words."""
    rows = plan_seed_tables(text)[block]
    out, spare, used = {}, [], set()
    for seed, use in rows:
        if use.startswith("spare, drawn by nothing"):
            spare.append(seed)
            continue
        hit = [r for r, t in role_text.items() if use.startswith(t)]
        if len(hit) != 1:
            raise ProvenanceRefused(f"REFUSED: the plan's 4.1 row {seed} ({use[:60]}...) names {len(hit)} roles")
        if hit[0] in used:
            raise ProvenanceRefused(f"REFUSED: the plan's 4.1 names role {hit[0]!r} twice")
        used.add(hit[0])
        out[hit[0]] = seed
    return out, spare


def seed_map_problems(seeds: dict, block, roles, *, plan_block: str = "calibration", role_text: dict | None = None,
                      spare=(), repo: Path = ROOT) -> list[str]:
    """The seed map is the plan's: every role mapped, in the block, distinct, and the whole map (spare included) equal
    to the 4.1 table **as parsed from the pinned plan**, its sha256 checked (the plan's 4.1, the red team's n5)."""
    out = CAL.seed_map_problems(seeds, block, roles)
    try:
        p = plan_path(repo)
    except ProvenanceRefused as exc:
        return out + [str(exc)]
    if file_sha_lf(p) != PLAN_SHA256:
        return out + [f"{p.name} does not hash to its pin in {DECISION}"]
    want, want_spare = parsed_seed_map(p.read_text(encoding="utf-8"), plan_block, role_text or ROLE_TEXT)
    got = {k: int(v) for k, v in seeds.items()}
    if got != want:
        out.append(f"the seed map {got} is not the plan's 4.1 {plan_block} table {want}")
    if sorted(int(x) for x in spare) != sorted(want_spare):
        out.append(f"the spare seeds {list(spare)} are not the plan's {want_spare}")
    return out


def pin_problems(repo: Path = ROOT) -> list[str]:
    """The pinned files: the plan (sha256 and its pinning row in DECISIONS.md) and every imported module's blob."""
    repo = Path(repo)
    out = []
    for rel, want in VALIDATED_BLOBS.items():
        got = CAL.blob_id(repo / rel) if (repo / rel).is_file() else None
        if got != want:
            out.append(f"{rel} is blob {str(got)[:12]}, not the pinned {want[:12]} (its code is what this run imports)")
    try:
        p = plan_path(repo)
    except ProvenanceRefused as exc:
        return out + [str(exc)]
    if file_sha_lf(p) != PLAN_SHA256:
        out.append(f"{p.name} does not hash to its pin in {DECISION}")
    dec = (repo / "DECISIONS.md").read_text(encoding="utf-8") if (repo / "DECISIONS.md").is_file() else ""
    row = f"`{PLAN_NAMES[0]}` sha256 `{PLAN_SHA256}`"
    if not any(line.startswith(f"| {DECISION} |") and row in line for line in dec.splitlines()):
        out.append(f"no {DECISION} row in DECISIONS.md pins {row}: the plan is not pinned")
    return out


# ================================================================================================ the seed guard


#: the files allowed to name either block (the plan's 4.1 allow-list); the lookahead test's hand-checked expressions
#: below; this plan's own result files where their manifest names a Q-126 runner
SEED_ALLOW = frozenset({*PLAN_NAMES, MODULE, SCRIPT, VALIDATE_SCRIPT, "tests/test_lift_one_sample2.py",
                        "tests/test_q126_calibrate.py", "tests/test_q126_validate.py", "tests/test_q126_draft.py",
                        "DECISIONS.md", "TASK_QUEUE.md", "STATUS.md", "PROGRESS.md"})
SEED_ALLOW_PREFIXES = ("docs/calibration/scripts/q126/",)
HAND_CHECKED = (
    {"file": "tests/test_features_lookahead.py", "expr": "SEED_REPLACE + i",
     "reach": "i runs over the cuts of a test's synthetic bars (tens), far below the blocks",
     "reason": "the plan's 4.1: the cut loops, on refs before Q-128 (E-178) made the walks SeedSequence children"},
    {"file": "tests/test_features_lookahead.py", "expr": "SEED_REPLACE + 200 + i",
     "reach": "i runs over the fixed days (a handful), far below the blocks",
     "reason": "the plan's 4.1, as above"},
    {"file": "tests/test_features_lookahead.py", "expr": "SEED_REPLACE + 1000 + i",
     "reach": "i < 790 (its len(rows) == 790): its last value is 89 below the calibration block's first seed",
     "reason": "the plan's 4.1, held by tests/test_q126_draft.py at the search's commit ec6905a"},
)


def _point_guard() -> None:
    """Q-108's guard (literal and AST-folded) pointed at this plan's two blocks and allow-list, in the private copy."""
    CAL.CAL_BLOCK, CAL.VAL_BLOCK = CAL_BLOCK, VAL_BLOCK
    CAL.SEED_PATTERN = "|".join(str(s) for s in CAL_BLOCK + VAL_BLOCK)
    CAL.SEED_ALLOW, CAL.SEED_ALLOW_PREFIXES = SEED_ALLOW, SEED_ALLOW_PREFIXES
    CAL.OWN_RESULT = re.compile(r"results/(q126_[A-Za-z0-9_]+)\.csv(?:\.manifest\.json)?")
    CAL.OWN_SCRIPTS = (SCRIPT, VALIDATE_SCRIPT)
    CAL.HAND_CHECKED = HAND_CHECKED


_point_guard()


def seed_block_problems(repo: Path | str = ROOT) -> tuple[list[str], list[str]]:
    """(problems, notes): Q-108's guard on this plan's blocks; a mention in another calibration plan or in a
    declaration is a problem (T-0's rule), a document's mention elsewhere a note."""
    _point_guard()
    probs, notes = CAL.seed_block_problems(repo)
    keep = []
    for n_ in notes:
        path = n_.split(" (", 1)[0]
        if n_.endswith("a document's mention") and path.startswith("docs/calibration/"):
            probs.append(f"{n_}: another calibration plan may not name this plan's blocks")
        else:
            keep.append(n_)
    return probs, keep


# ================================================================================================ the null plan


def exact_index(data_pos: int, vi: int, model: str) -> int:
    """The exact null index (4.1): data (offered, taken, then the subsets by z_index then j), then value, then exact
    model, outermost first."""
    return (int(data_pos) * len(VALUES) + int(vi)) * len(EXACT_MODELS) + EXACT_MODELS.index(model)


def subset_pos(zi: int, j: int, n_subsets: int | None = None) -> int:
    return len(STREAMS) + int(zi) * (N_SUBSETS if n_subsets is None else int(n_subsets)) + int(j)


def _base(**kw) -> dict:
    e = {"null": None, "part": None, "kind": None, "group": None, "in_rule": True, "data": None, "stream": None,
         "size": None, "z_index": None, "j": None, "value": None, "value_index": None, "model": None,
         "model_index": None, "entropy": None, "subset_entropy": None, "exact_index": None, "sample_entropy": None,
         "toy": None, "q16": None, "profile": None, "L": None, "engine": None, "scenario": None, "population": None}
    e.update(kw)
    return e


def core_plan(seeds: dict, *, n_subsets: int | None = None) -> list[dict]:
    """The core (Q-108's class, the plan's 3.1) on this run's seeds: the fixed streams, the 23 core subsets at each size,
    the realistic synthetic nulls, and the count-persistent and `flat` nulls beside. `n_subsets` (the run's subsets a
    size: 660 at the calibration, 23 at the validation) sets the exact null index."""
    ns = N_SUBSETS if n_subsets is None else int(n_subsets)
    plan: list[dict] = []
    for si, st in enumerate(STREAMS):
        for vi, v in enumerate(VALUES):
            for pos, m in enumerate(FIXED_MC_MODELS):
                plan.append(_base(null=f"fixed:{st}:{v}:{m}", part="core", kind="mc", group="fixed", data=st,
                                  stream=st, value=v, value_index=vi, model=m, model_index=MODELS.index(m),
                                  entropy=[int(seeds["fixed_mc"]), (si * 2 + vi) * 7 + pos]))
            for m in EXACT_MODELS:
                xi = exact_index(si, vi, m)
                plan.append(_base(null=f"fixed:{st}:{v}:{m}", part="core", kind="exact", group="fixed", data=st,
                                  stream=st, value=v, value_index=vi, model=m, model_index=MODELS.index(m),
                                  exact_index=xi, sample_entropy=[int(seeds["exact_sample"]), xi]))
    for zi, z in enumerate(SIZES):
        for j in range(N_CORE):
            sub_e = [int(seeds["subsets"]), zi, j]
            for vi, v in enumerate(VALUES):
                for mi, m in enumerate(MODELS):
                    if m in NONPERSISTENT and j >= N_NONPERSISTENT:
                        continue
                    toy = ("P" if v == "win1" else "net3") if (j == 0 and m in ("coin", "flip1")) else None
                    common = dict(null=f"sub:{z}:{j:03d}:{v}:{m}", part="core", group="subset", data="sub", size=z,
                                  z_index=zi, j=j, value=v, value_index=vi, model=m, model_index=mi,
                                  subset_entropy=list(sub_e), toy=toy)
                    if m in EXACT_MODELS:
                        xi = exact_index(subset_pos(zi, j, ns), vi, m)
                        plan.append(_base(kind="exact", exact_index=xi,
                                          sample_entropy=[int(seeds["exact_sample"]), xi], **common))
                    else:
                        plan.append(_base(kind="mc", entropy=[int(seeds["subset_mc"]), zi, j, vi, mi], **common))
    for ni, sp in enumerate(Q16.syn_specs()):
        if sp["model"] in REALISTIC:
            plan.append(_base(null=sp["null"], part="core", kind="mc", group="synthetic", data="syn",
                              size=int(sp["trades"]), model=sp["model"], entropy=[int(seeds["synthetic"]), ni], q16=sp,
                              toy="cluster" if sp["model"] == "cluster" and int(sp["trades"]) == 1000 else None))
    for i, (prof, T, v, L) in enumerate(CP_ONE):
        plan.append(_base(null=f"cp:{prof}:{T}:{v}:persist{L}", part="core", kind="mc", group="beside_cp",
                          in_rule=False, data="cp", size=int(T), value=v, profile=prof, L=int(L),
                          entropy=[int(seeds["beside_cp"]), i], engine="hypergeometric" if v == "win1" else "per-offer"))
    for Li, L in enumerate(FLAT_L):
        for zi, z in enumerate(SIZES):
            for vi, v in enumerate(VALUES):
                plan.append(_base(null=f"flat:{z}:{v}:flip{L}", part="core", kind="mc", group="beside_flat",
                                  in_rule=False, data="flat", size=z, z_index=zi, value=v, value_index=vi,
                                  profile="flat", L=L, entropy=[int(seeds["beside_flat"]),
                                                                (Li * len(SIZES) + zi) * len(VALUES) + vi],
                                  engine="hypergeometric" if v == "win1" else "per-offer"))
    return plan


def sizing_plan(seeds: dict, z: int) -> list[dict]:
    """The sizing subsets at size z (3.2): j = 23..659, both values, the five exact models; no draw but the subset."""
    zi = SIZES.index(z)
    plan = []
    for j in range(N_CORE, N_SUBSETS):
        for vi, v in enumerate(VALUES):
            for m in EXACT_MODELS:
                plan.append(_base(null=f"sub:{z}:{j:03d}:{v}:{m}", part=f"sizing{z}", kind="exact", group="sizing",
                                  data="sub", size=z, z_index=zi, j=j, value=v, value_index=vi, model=m,
                                  model_index=MODELS.index(m), subset_entropy=[int(seeds["subsets"]), zi, j],
                                  exact_index=exact_index(subset_pos(zi, j), vi, m)))
    return plan


def probe_plan(seeds: dict, ranking: dict) -> list[dict]:
    """The probe (3.2): at each size the ranked sizing subsets, both values, the four persistent Monte Carlo models,
    seeded by the probe's role with the subset's own j (B-24) and Q-108's model_index."""
    plan = []
    for zi, z in enumerate(SIZES):
        for j, _score in ranking.get(z, []):
            for vi, v in enumerate(VALUES):
                for m in PROBE_MODELS:
                    mi = MODELS.index(m)
                    plan.append(_base(null=f"probe:{z}:{j:03d}:{v}:{m}", part="probe", kind="mc", group="probe",
                                      data="sub", size=z, z_index=zi, j=j, value=v, value_index=vi, model=m,
                                      model_index=mi, entropy=[int(seeds["probe"]), zi, j, vi, mi],
                                      subset_entropy=[int(seeds["subsets"]), zi, j]))
    return plan


def drift_plan(seeds: dict, *, part: str = "drift") -> list[dict]:
    """The drift nulls beside (3.3): population r of scenario c by [s, c, r], at every exact model."""
    plan = []
    for c, lab, z, T, d, varying in DRIFT_SCENARIOS:
        for r in range(DRIFT_POPULATIONS):
            for m in EXACT_MODELS:
                plan.append(_base(null=f"drift:{lab}:{r:03d}:{m}", part=part, kind="exact", group="drift",
                                  in_rule=False, data="drift", size=int(z), model=m, model_index=MODELS.index(m),
                                  entropy=[int(seeds["drift"]), int(c), int(r)], scenario=int(c), population=int(r),
                                  profile=f"{lab}:T{T}:d{d:g}:{'varying' if varying else 'constant'}"))
    return plan


def deterministic_plan(seeds: dict) -> list[dict]:
    """Every null whose entropy is fixed before the run: the core, the sizing parts and the drift (the probe's subsets
    follow the sizing parts' ranking)."""
    out = core_plan(seeds)
    for z in SIZES:
        out += sizing_plan(seeds, z)
    return out + drift_plan(seeds)


def expected_counts(seeds: dict) -> dict[str, int]:
    plan = core_plan(seeds)
    rule = [x for x in plan if x["in_rule"]]
    sizing = sum(len(sizing_plan(seeds, z)) for z in SIZES)
    probe = PROBE_PER_SIZE * len(SIZES) * len(VALUES) * len(PROBE_MODELS)
    core_exact = sum(x["kind"] == "exact" for x in rule)
    return {"core_rule": len(rule), "core_exact": core_exact, "core_mc": sum(x["kind"] == "mc" for x in rule),
            "beside_cp": sum(x["group"] == "beside_cp" for x in plan),
            "beside_flat": sum(x["group"] == "beside_flat" for x in plan), "sizing": sizing, "probe": probe,
            "drift": len(drift_plan(seeds)), "rule": len(rule) + sizing + probe,
            "exact_index_max": max(x["exact_index"] for x in [*plan, *sizing_plan(seeds, SIZES[-1])]
                                   if x["exact_index"] is not None)}


# ================================================================================================ the provenance assertion


def declared_entropies(e: dict, seeds: dict, *, n_subsets: int | None = None) -> dict:
    """The entropies the plan's 4.1 declares for null `e`, recomputed from its declared fields alone (its stream,
    value, model, size, j, scenario and population), never from the entropies it carries."""
    ns = N_SUBSETS if n_subsets is None else int(n_subsets)
    g = e["group"]
    vi = VALUES.index(e["value"]) if e.get("value") in VALUES else None
    want = {"entropy": None, "subset_entropy": None, "sample_entropy": None, "exact_index": None}
    if g == "fixed":
        si = STREAMS.index(e["stream"])
        if e["kind"] == "mc":
            want["entropy"] = [int(seeds["fixed_mc"]), (si * 2 + vi) * 7 + FIXED_MC_MODELS.index(e["model"])]
        else:
            xi = exact_index(si, vi, e["model"])
            want.update(exact_index=xi, sample_entropy=[int(seeds["exact_sample"]), xi])
    elif g in ("subset", "sizing", "probe"):
        zi, j = SIZES.index(int(e["size"])), int(e["j"])
        want["subset_entropy"] = [int(seeds["subsets"]), zi, j]
        if g == "probe":
            want["entropy"] = [int(seeds["probe"]), zi, j, vi, MODELS.index(e["model"])]
        elif e["kind"] == "mc":
            want["entropy"] = [int(seeds["subset_mc"]), zi, j, vi, MODELS.index(e["model"])]
        else:
            xi = exact_index(subset_pos(zi, j, ns), vi, e["model"])
            want["exact_index"] = xi
            if g == "subset":
                want["sample_entropy"] = [int(seeds["exact_sample"]), xi]
    elif g == "synthetic":
        names = [sp["null"] for sp in Q16.syn_specs()]
        want["entropy"] = [int(seeds["synthetic"]), names.index(e["null"])]
    elif g == "beside_cp":
        key = (e["profile"], int(e["size"]), e["value"], int(e["L"]))
        want["entropy"] = [int(seeds["beside_cp"]), [tuple(x) for x in CP_ONE].index(key)]
    elif g == "beside_flat":
        Li, zi = FLAT_L.index(int(e["L"])), SIZES.index(int(e["size"]))
        want["entropy"] = [int(seeds["beside_flat"]), (Li * len(SIZES) + zi) * len(VALUES) + vi]
    elif g == "drift":
        want["entropy"] = [int(seeds["drift"]), int(e["scenario"]), int(e["population"])]
    else:
        raise ProvenanceRefused(f"REFUSED: null {e.get('null')!r} is of no group the plan declares ({g!r})")
    return want


def provenance_problems(plan: list[dict], seeds: dict, block, *, n_subsets: int | None = None,
                        max_j: int | None = None) -> list[str]:
    """The seed-provenance assertion (the plan's 4.1, B-28), before any draw: every generator entropy of every null --
    `entropy`, `subset_entropy`, `sample_entropy` and the exact index -- is, in full, the one 4.1 declares for that null,
    its first element a seed of this run's own block; no two nulls share a draw they should not."""
    out = []
    block = {int(x) for x in block}
    lim = (N_SUBSETS if n_subsets is None else int(n_subsets)) if max_j is None else int(max_j)
    seen: dict = {}
    for e in plan:
        try:
            want = declared_entropies(e, seeds, n_subsets=n_subsets)
        except (ValueError, KeyError, TypeError) as exc:
            out.append(f"{e.get('null')}: its declared fields do not fix an entropy ({type(exc).__name__}: {exc})")
            continue
        except ProvenanceRefused as exc:
            out.append(str(exc))
            continue
        for k in ("entropy", "subset_entropy", "sample_entropy"):
            got = e.get(k)
            got = [int(x) for x in got] if got is not None else None
            if got != want[k]:
                out.append(f"{e['null']}: {k} {got} is not the plan's {want[k]}")
            elif got is not None and got[0] not in block:
                out.append(f"{e['null']}: {k} starts with {got[0]}, outside this run's block")
        if e.get("exact_index") != want["exact_index"]:
            out.append(f"{e['null']}: exact index {e.get('exact_index')} is not the plan's {want['exact_index']}")
        if e.get("j") is not None and not (0 <= int(e["j"]) < lim):
            out.append(f"{e['null']}: subset j = {e['j']} outside 0..{lim - 1}")
        if e.get("entropy") is not None and e["group"] != "drift":            # a drift population feeds 5 models
            key = tuple(e["entropy"])
            if key in seen:
                out.append(f"{e['null']} shares its entropy with {seen[key]}")
            seen[key] = e["null"]
    return out


# ================================================================================================ inputs


def judged_sessions(dates):
    return CAL.judged_sessions(dates)


def calendar_problems(cal, sha) -> list[str]:
    return CAL.calendar_problems(cal, sha)


def read_calendar(decision: str = DECISION, task: str = TASK) -> tuple[list[str], str, dict]:
    """The judged block's session list: A1's stored days, dates only, through the reader (a ledgered
    `registered_design` read under E-035 for P-16, as Q-108's 6.1)."""
    from extended import reader

    df = reader.read_walks("A1", "days", JUDGED_FIRST, JUDGED_LAST, purpose=reader.REGISTERED_DESIGN,
                           declaration=READ_ROW, design=READ_DESIGN, columns=["date"],
                           what=f"{decision} ({task}): the judged block's session list -- A1's stored days, dates only")
    cal, sha = judged_sessions(df["date"].astype(str).tolist())
    return cal, sha, {"file": DAYS_REL, "columns": ["date"], "purpose": "registered_design", "declaration": READ_ROW,
                      "design": READ_DESIGN}


def _versions() -> dict:
    return CAL._versions()


def blob_id(path: Path) -> str:
    return CAL.blob_id(path)


# ================================================================================================ running a null


def _new_counts(cands):
    return {(c, s): np.zeros(len(LEVELS), dtype=np.int64) for c in cands for s in SCOPES}


def redecide(cands, S, N, n, levels) -> dict[str, list[bool]]:
    """{candidate: its scalar decisions at `levels`} on one replication's (or cell's) session sums."""
    x, s = CAL.pseudo_trades(S, N)
    return {c: [b.rejects for b in L2.bound_1s_levels(c, x, s, n, levels=levels)] for c in cands}


def run_mc(e: dict, gen, ds, reps: int, batch: int, n: int, cands, *, power: bool = False) -> dict:
    """One Monte Carlo null: rejections per candidate, scope and level (scope D with the balance limit); the scalar
    re-decision (every rejection at a family level and the null's first replications, `admission2` for scope D); the
    toys' MDLs. Q-108's `run_mc`, on this module's candidates and admission."""
    rng = np.random.default_rng(e["entropy"])
    counts = _new_counts(cands)
    admitted = done = checked = 0
    mism, trades, nontie = [], [], []
    mdls = {(c, s, k): [] for c in cands for s in SCOPES for k in POWER_KS} if power else None
    kidx = {k: KS.index(k) for k in POWER_KS}
    while done < reps:
        r = min(batch, reps - done)
        b = gen(rng, r)
        low = L2.evaluate(b.S, b.N, LEVELS, cands=cands)
        m = CAL.side_matrix(b, ds)
        if m is None:
            adm = np.ones(r, dtype=bool)
        else:
            adm = L2.admitted_matrix(m, n)
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
        adm_s: dict = {}
        for c in cands:
            rej = low[c][:NF] > 0.0
            idx = np.flatnonzero(rej.any(axis=0))
            if done == 0:
                idx = np.union1d(idx, np.arange(min(SCALAR_FIRST, r)))
            for j in idx:
                j = int(j)
                Sj, Nj = CAL._col(b.S, j), CAL._col(b.N, j)
                if m is not None and j not in adm_s:
                    sd, ses = CAL.trade_sides(b, ds, j)
                    a_ = L2.admission2(sd, ses, n).admitted
                    adm_s[j] = a_
                    checked += 1
                    if a_ != bool(adm[j]):
                        mism.append({"null": e["null"], "candidate": "(admission)", "scope": "D",
                                     "replication": done + j, "k": None, "vectorised": bool(adm[j]), "scalar": a_})
                sc = redecide([c], Sj, Nj, n, FAMILY)[c]
                a_s = adm_s.get(j, True)
                for i, k in enumerate(KS):
                    for s_, vec, scal in (("Q", bool(rej[i, j]), sc[i]), ("D", bool(rej[i, j] and adm[j]), sc[i] and a_s)):
                        checked += 1
                        if vec != scal:
                            mism.append({"null": e["null"], "candidate": c, "scope": s_, "replication": done + j,
                                         "k": k, "vectorised": vec, "scalar": scal})
        done += r
        del b, low
    out = {"counts": counts, "den": reps, "admitted": admitted, "checked": checked, "mismatches": mism,
           "trades_mean": float(np.concatenate(trades).mean()),
           "nontie_mean": float(np.concatenate(nontie).mean()) if nontie else None, "records": {}}
    if power:
        out["mdl"] = {key: np.concatenate(v) for key, v in mdls.items()}
    return out


def run_exact(e: dict, V, N, n: int, cands, *, ds=None, n_first: int = SAMPLE_FIRST_CORE, uniform: bool = True,
              redecide_cells: bool = True, record=None) -> dict:
    """One exact null (flips at 42, 55, 63 or the alternating models) on fixed session sums V and counts N: exact sizes
    per candidate, scope and level (scope D with the balance limit); the scalar re-decision of the declared sample of
    cells (`ds` the trade set, for the per-trade admission); the rejecting cells of the pairs in `record`."""
    m = e["model"]
    record = sorted(L2.IN_RULE & {(c, s) for c in cands for s in SCOPES}) if record is None else record
    checked, mism = 0, []
    V = np.asarray(V, dtype=float)
    N = np.asarray(N, dtype=float)
    if m.startswith("flip"):
        L = int(m[4:])
        Bs, _ = O.flip_cells(n, L)
        ncell = sum(2 ** b for b in Bs)
        uni = CAL._uniform_cells(e["sample_entropy"], ncell) if uniform else []
        ex = L2.exact_flip2(V, N, L, LEVELS, cands=cands, n_first=n_first, uniform_cells=uni, record=record)
        num, den, adm_w, records = ex.num, ex.den, ex.admitted, ex.records
        sampled = [(c, s_, cell, p, q, dec) for (c, s_), lst in ex.samples.items() for cell, p, q, dec in lst]
        sampled += [(c, s_, cell, p, q, d) for cell, p, q, dec, _a in ex.uniform for (c, s_), d in dec.items()]

        def cell_sides(p, q):
            return O.flip_cell_sides(n, L, p, q)
    else:
        L = int(m[3:])
        alt = L2.exact_alternating(V, N, L, LEVELS, cands=cands, record=record)
        num, den, adm_w, records = alt.num, alt.den, alt.admitted, alt.records
        uni = CAL._uniform_cells(e["sample_entropy"], den) if uniform else []
        sampled = []
        for (c, s_), rr in alt.rej.items():
            first = [int(x) for x in np.flatnonzero(rr[0])[:n_first]]
            for cell in sorted(set(first) | set(uni)):
                sampled.append((c, s_, cell, cell // 2, cell % 2, tuple(bool(v) for v in rr[:NF, cell])))
        sides_all = O.alternating_sides(n, L)

        def cell_sides(p, q):
            return sides_all[:, 2 * p + q]
    if redecide_cells:
        stat_cache: dict = {}
        adm_cache: dict = {}
        for c, s_, cell, p, q, dec in sampled:
            sd = cell_sides(p, q)
            if (c, cell) not in stat_cache:
                stat_cache[(c, cell)] = redecide([c], sd * V, N, n, FAMILY)[c]
            sc = stat_cache[(c, cell)]
            if s_ == "D":
                if cell not in adm_cache:
                    adm_cache[cell] = L2.admission2(sd[ds.s], ds.s, n).admitted
                sc = [x and adm_cache[cell] for x in sc]
            for i, k in enumerate(KS):
                checked += 1
                if bool(dec[i]) != bool(sc[i]):
                    mism.append({"null": e["null"], "candidate": c, "scope": s_, "replication": cell, "k": k,
                                 "vectorised": bool(dec[i]), "scalar": bool(sc[i])})
    return {"counts": {key: np.asarray(v, dtype=np.int64) for key, v in num.items()}, "den": int(den),
            "admitted": int(adm_w), "checked": checked, "mismatches": mism, "trades_mean": float(N.sum()),
            "nontie_mean": float((N > 0).sum()), "records": records}


def nesting_problems(e: dict, res: dict, cands) -> list[str]:
    """The plan's 4.2: counts non-increasing in k for every candidate and scope; and (B-17) non-increasing in m on
    rows 1-7 at every level and in each scope, on these shared draws."""
    out = []
    for c in cands:
        for s_ in SCOPES:
            v = np.asarray(res["counts"][(c, s_)][:NF])
            if np.any(np.diff(v) > 0):
                out.append(f"{e['null']} {c} scope {s_}: counts {list(map(int, v))} rise with k")
    nest = [c for c in L2.NESTED if c in cands]
    for s_ in SCOPES:
        for a, b in zip(nest, nest[1:]):
            va, vb = np.asarray(res["counts"][(a, s_)]), np.asarray(res["counts"][(b, s_)])
            if np.any(vb > va):
                out.append(f"{e['null']} scope {s_}: {b}'s counts {list(map(int, vb))} exceed {a}'s "
                           f"{list(map(int, va))} (not nested in m)")
    return out


# ================================================================================================ rows


def _cid(c: str) -> str:
    return L2.candidate(c).cid


def size_rows(e: dict, res: dict, cands, *, long: bool = True) -> list[dict]:
    """One row per candidate and scope. `long` (the core and the probe): Q-108's columns -- every level's count, rate,
    95 % Clopper-Pearson interval (Monte Carlo) and ratio to nominal; otherwise the counts and the denominator only."""
    den = int(res["den"])
    desc = {"null": e["null"], "part": e["part"], "kind": e["kind"], "group": e["group"], "in_rule": e["in_rule"],
            "data": e["data"], "size": e["size"], "j": e["j"], "value": e["value"], "model": e["model"] or e["profile"],
            "L": e["L"], "toy": e["toy"], "exact_index": e["exact_index"], "scenario": e["scenario"],
            "population": e["population"]}
    if long:
        desc.update({"entropy": json.dumps(e["entropy"]) if e["entropy"] else None,
                     "subset_entropy": json.dumps(e["subset_entropy"]) if e["subset_entropy"] else None,
                     "sample_entropy": json.dumps(e["sample_entropy"]) if e["sample_entropy"] else None})
    rows = []
    for c in cands:
        for s_ in SCOPES:
            cnt = res["counts"][(c, s_)]
            row = {**desc, "candidate": c, "cid": _cid(c), "scope": s_, "pair_in_rule": L2.in_rule(c, s_),
                   "denominator": den, "admitted": int(res["admitted"]), "admitted_share": res["admitted"] / den}
            if long:
                row.update({"trades_mean": res["trades_mean"], "nontie_sessions_mean": res["nontie_mean"]})
            for lab, a, x in zip(LABELS, LEVELS, cnt):
                x = int(x)
                row[f"count_{lab}"] = x
                if long:
                    row[f"rate_{lab}"] = x / den
                    if e["kind"] == "mc":
                        lo, hi = LB.clopper_pearson(x, den)
                        row[f"ci_lo_{lab}"], row[f"ci_hi_{lab}"] = CAL._g6(lo), CAL._g6(hi)
                    else:
                        row[f"ci_lo_{lab}"], row[f"ci_hi_{lab}"] = None, None
                    row[f"ratio_{lab}"] = CAL._g6((x / den) / a)
            rows.append(row)
    return rows


def _quarter_exceeded(cnt, den: int) -> bool:
    """An exact size above a quarter of nominal at some k in 13..20 (exactly: 4 x count x 20 k (k + 1) > den)."""
    return any(4 * int(x) * 20 * k * (k + 1) > int(den) for x, k in zip(cnt[:NF], KS))


def cell_rows(e: dict, res: dict) -> list[dict]:
    """The plan's 4.5: for each pair in the rule whose exact size is above a quarter of nominal at any k in 13..20, one
    row per cell rejecting at k = 13 (in scope D, rejecting and admitted)."""
    rows = []
    alt = e["model"].startswith("alt")
    for (c, s_), rec in sorted(res["records"].items()):
        if not _quarter_exceeded(res["counts"][(c, s_)], res["den"]):
            continue
        for i in range(len(rec["cell"])):
            rows.append({"null": e["null"], "part": e["part"], "group": e["group"], "model": e["model"],
                         "candidate": c, "cid": _cid(c), "scope": s_, "cell": int(rec["cell"][i]),
                         "phase": int(rec["p"][i]), "pattern": int(rec["q"][i]),
                         "first": ("short" if int(rec["q"][i]) else "long") if alt else None,
                         "blocks": None if alt else int(rec["B"][i]), "weight": int(rec["weight"][i]),
                         "admitted": bool(rec["admitted"][i]), "k_max": int(rec["kmax"][i])})
    return rows


def power_rows(e: dict, res: dict, cands) -> list[dict]:
    rows = []
    for c in cands:
        for s_ in SCOPES:
            for k in POWER_KS:
                v = res["mdl"][(c, s_, k)]
                rows.append({"row": "toy", "null": e["null"], "toy": e["toy"], "size": e["size"], "value": e["value"],
                             "model": e["model"], "candidate": c, "cid": _cid(c), "scope": s_, "k": k,
                             "reps_used": int(v.size), "mdl50": CAL._q(v, 0.5), "mdl80": CAL._q(v, 0.8),
                             "infinite_share": float(np.mean(~np.isfinite(v)))})
    return rows


# ================================================================================================ the parts' computation


def _empty_out(part: str) -> dict:
    return {"size": [], "power": [], "cells": [], "mismatches": [], "nesting": [], "ranking": [],
            "meta": {"part": part}, "timing": []}


def compute_nulls(part: str, plan: list[dict], inp, n: int, reps: int, cands, *, reps_beside: int | None = None,
                  drift_inputs=None, record=None, log=_log) -> dict:
    """Every null of `plan`, in order: size rows, power rows, cells rows, the re-decision's mismatches and the nesting
    checks. Stops after the first null with a scalar disagreement or a nesting violation (the plan's 4.1, 4.2): the
    failed check is recorded, nothing after it is computed."""
    t0 = time.time()
    reps_beside = REPS_BESIDE if reps_beside is None else int(reps_beside)
    out = _empty_out(part)
    checked = 0
    stopped = None
    last_sub = None
    pop_cache: dict = {}
    for e in plan:
        t1 = time.time()
        if e["data"] == "sub" and last_sub != (e["size"], e["j"]):
            inp.drop(("ds", "subarrs"))
            last_sub = (e["size"], e["j"])
        long = e["group"] in ("fixed", "subset", "synthetic", "beside_cp", "beside_flat", "probe")
        if e["kind"] == "exact":
            if e["group"] == "drift":
                key = tuple(e["entropy"])
                if key not in pop_cache:
                    pop_cache.clear()
                    pop_cache[key] = drift_inputs(e)
                V, N = pop_cache[key]
                res = run_exact(e, V, N, n, cands, uniform=False, redecide_cells=False, record=record)
            else:
                ds = inp.data_for(e)
                core = e["group"] in ("fixed", "subset")
                res = run_exact(e, ds.V, ds.N, n, cands, ds=ds, n_first=SAMPLE_FIRST_CORE if core else
                                SAMPLE_FIRST_SIZING, uniform=core, record=record)
            out["cells"] += cell_rows(e, res)
        else:
            ds = inp.data_for(e) if e["data"] == "sub" or e["group"] == "fixed" else None
            rr = reps if e["in_rule"] else reps_beside
            bb = BATCH if e["in_rule"] else BATCH_BESIDE
            gen = CAL.mc_generator(dict(e, group="subset") if e["group"] == "probe" else e, inp)
            res = run_mc(e, gen, ds, rr, min(bb, rr), n, cands, power=bool(e["toy"]))
            if e["toy"]:
                out["power"] += power_rows(e, res, cands)
        out["size"] += size_rows(e, res, cands, long=long)
        checked += res["checked"]
        out["mismatches"] += res["mismatches"]
        nest = nesting_problems(e, res, cands)
        out["nesting"] += nest
        dt = time.time() - t1
        out["timing"].append({"null": e["null"], "kind": e["kind"], "model": e["model"] or e["profile"],
                              "seconds": round(dt, 3)})
        c0 = cands[0]
        log(f"  {e['null']}: {c0} at k=13 Q {int(res['counts'][(c0, 'Q')][0])} D {int(res['counts'][(c0, 'D')][0])}"
            f" of {res['den']}; {dt:.1f} s, ws {working_set_mb():.0f} MB"
            + (f"; DIFFERS in {len(res['mismatches'])} of {res['checked']}" if res["mismatches"] else ""))
        if res["mismatches"] or nest:
            stopped = e["null"]
            break
    out["meta"].update({"nulls": len(plan), "nulls_done": len(out["timing"]), "reps": reps,
                        "reps_beside": reps_beside, "scalar_checked": checked,
                        "scalar_mismatched": len(out["mismatches"]), "nesting_violations": out["nesting"],
                        "stopped_after": stopped, "candidates": list(cands), "n_sessions": n})
    out["seconds"] = round(time.time() - t0, 1)
    return out


def failed(out: dict) -> bool:
    return bool(out["mismatches"] or out["nesting"] or out["meta"].get("failed"))


def drift_inputs_for(n: int):
    def f(e):
        c, lab, z, T, d, varying = DRIFT_SCENARIOS[int(e["scenario"])]
        return L2.drift_draw(np.random.default_rng(e["entropy"]), int(z), int(T), float(d), bool(varying), n=n)
    return f


def ranking_scores(sizing_rows: pd.DataFrame) -> dict:
    """The probe's ranking score of each sizing subset (B-23): the sum over both values and the flips at 42, 55 and 63
    of `cons`'s scope-Q exact size over the level at k = 13, exactly (a Fraction)."""
    d = sizing_rows[(sizing_rows["candidate"] == "cons") & (sizing_rows["scope"] == "Q")
                    & sizing_rows["model"].isin(["flip42", "flip55", "flip63"])]
    k13 = Fraction(20 * 13 * 14)
    out: dict = {}
    for z, j, x, den in zip(d["size"].astype(int), d["j"].astype(int), d["count_k13"].astype(int),
                            d["denominator"].astype(int)):
        out[(z, j)] = out.get((z, j), Fraction(0)) + Fraction(int(x), int(den)) * k13
    return out


def ranking_frame(ranking: dict) -> pd.DataFrame:
    rows = []
    for z in SIZES:
        for rank, (j, s) in enumerate(ranking.get(z, [])):
            rows.append({"row": "probe_ranking", "size": z, "rank": rank, "j": j, "score": float(s), "score_exact": str(s)})
    return pd.DataFrame(rows)


# ================================================================================================ the choice


def _truthy(s: pd.Series) -> pd.Series:
    return s.astype(str).str.lower().isin(["true", "1"])


#: 1 / level at k = 13..20: 20 k (k + 1)
INV_LEVEL = np.array([20 * k * (k + 1) for k in KS], dtype=np.int64)


def _above(counts: np.ndarray, den: np.ndarray, mult: int = 1) -> np.ndarray:
    """(rows, NF) exactly, in integers: mult x count / den > level, i.e. mult x count x 20 k (k + 1) > den (a count is
    at most its denominator, at most 63 x 2^11 or 42 x 2^17 cells or 200,000 replications, so int64 holds it)."""
    c = np.asarray(counts, dtype=np.int64)
    if c.size and int(c.max()) > (1 << 40):
        raise OverflowError("a count too large for the exact comparison")
    return (c * int(mult) * INV_LEVEL[None, :]) > np.asarray(den, dtype=np.int64)[:, None]


def _fam(d: pd.DataFrame) -> np.ndarray:
    return d[[f"count_{lab}" for lab in FAM_LABELS]].to_numpy(dtype=np.int64)


def eligibility(size: pd.DataFrame, cands=CANDS) -> pd.DataFrame:
    """Per candidate and scope, the plan's four conditions (4.2) on the calibration's nulls: (1) the floors -- no core
    Monte Carlo null's point rate above nominal, no fixed-stream exact size above nominal, **no subset of the 3,300 bad**
    (at either value and any exact model, its exact size above nominal at some k); (2) P_MC >= 0.9 over the core's
    Monte Carlo nulls; (3) the worst exact ratio over the core's exact nulls at most 1/4; (4) no probed null reaching
    its failure count. Beside: the worst exact ratio overall and per model, the bad-subset counts per size and model,
    the probe's worst share of its failure count."""
    d = size[_truthy(size["in_rule"])]
    out = []
    for c in cands:
        cand = L2.candidate(c)
        for s_ in SCOPES:
            g = d[(d["candidate"] == c) & (d["scope"] == s_)]
            core_mc = g[(g["kind"] == "mc") & g["group"].isin(["fixed", "subset", "synthetic"])]
            fixed_ex = g[(g["kind"] == "exact") & (g["group"] == "fixed")]
            core_ex = g[(g["kind"] == "exact") & g["group"].isin(["fixed", "subset"])]
            sub_ex = g[(g["kind"] == "exact") & g["group"].isin(["subset", "sizing"])]
            all_ex = g[(g["kind"] == "exact")]
            probe = g[g["group"] == "probe"]
            row = {"row": "candidate", "candidate": c, "cid": cand.cid, "scope": s_, "margin": L2.margin_of(c),
                   "members": cand.n_members, "table_row": cand.row, "in_rule": L2.in_rule(c, s_),
                   "core_mc_nulls": len(core_mc), "core_exact_nulls": len(core_ex), "sizing_exact_nulls":
                   int((g["group"] == "sizing").sum()), "probe_nulls": len(probe)}
            # (1a) the core MC point rate
            if len(core_mc):
                ab = _above(_fam(core_mc), core_mc["denominator"].to_numpy(np.int64))
                row["mc_floor_ok"] = not bool(ab.any())
                rates = _fam(core_mc) / core_mc["denominator"].to_numpy(float)[:, None]
                ratio = rates / np.array(FAMILY)[None, :]
                i, kk = np.unravel_index(int(np.argmax(ratio)), ratio.shape)
                row.update({"mc_worst_ratio": float(ratio[i, kk]), "mc_worst_null": core_mc["null"].iloc[i],
                            "mc_worst_k": KS[kk]})
            else:
                row.update({"mc_floor_ok": True, "mc_worst_ratio": math.nan, "mc_worst_null": None, "mc_worst_k": None})
            # (1b) the fixed streams' exact sizes
            row["fixed_exact_floor_ok"] = not bool(_above(_fam(fixed_ex), fixed_ex["denominator"].to_numpy(np.int64))
                                                   .any()) if len(fixed_ex) else True
            # (1c) the bad subsets: union over values and exact models
            if len(sub_ex):
                bad_row = _above(_fam(sub_ex), sub_ex["denominator"].to_numpy(np.int64)).any(axis=1)
                alt = sub_ex["model"].str.startswith("alt").to_numpy()
                if not np.array_equal(bad_row[alt], (_fam(sub_ex)[alt] > 0).any(axis=1)):
                    raise AssertionError("on an alternating model a rejecting configuration is not above nominal")
                bs = sub_ex.assign(_bad=bad_row)
                per_sub = bs.groupby(["size", "j"])["_bad"].any()
                row["subsets"] = int(per_sub.size)
                row["bad_subsets"] = int(per_sub.sum())
                core_bad = per_sub[per_sub.index.get_level_values("j") < N_CORE]
                row["bad_core_subsets"] = int(core_bad.sum())
                row["bad_sizing_subsets"] = int(per_sub.sum() - core_bad.sum())
                for z in SIZES:
                    row[f"bad_subsets_{z}"] = int(per_sub[per_sub.index.get_level_values("size") == z].sum())
                for m in EXACT_MODELS:
                    row[f"bad_subsets_{m}"] = int(bs[bs["model"] == m].groupby(["size", "j"])["_bad"].any().sum())
            else:
                row.update({"subsets": 0, "bad_subsets": 0, "bad_core_subsets": 0, "bad_sizing_subsets": 0})
            row["subset_floor_ok"] = row["bad_subsets"] == 0
            # (2) P_MC over the core's Monte Carlo nulls
            pmc = 1.0
            for x, den in zip(_fam(core_mc), core_mc["denominator"].to_numpy(np.int64)):
                if x.any():
                    pmc *= CAL.p_holds(list(x / den), CAL.fail_counts(int(den)), reps=int(den))
            row["p_mc"] = pmc
            # (3) the worst exact ratio over the core's exact nulls (exactly: 4 x count x level^-1 <= den)
            row["cond3_ratio"] = not bool(_above(_fam(core_ex), core_ex["denominator"].to_numpy(np.int64), 4).any()) \
                if len(core_ex) else False
            for lab_, dd in (("core", core_ex), ("all", all_ex)):
                if len(dd):
                    ratio = (_fam(dd) / dd["denominator"].to_numpy(float)[:, None]) / np.array(FAMILY)[None, :]
                    i, kk = np.unravel_index(int(np.argmax(ratio)), ratio.shape)
                    row.update({f"worst_exact_ratio_{lab_}": float(ratio[i, kk]),
                                f"worst_exact_null_{lab_}": dd["null"].iloc[i], f"worst_exact_k_{lab_}": KS[kk]})
            for m in EXACT_MODELS:
                dm = all_ex[all_ex["model"] == m]
                if len(dm):
                    ratio = (_fam(dm) / dm["denominator"].to_numpy(float)[:, None]) / np.array(FAMILY)[None, :]
                    i, kk = np.unravel_index(int(np.argmax(ratio)), ratio.shape)
                    row.update({f"worst_ratio_{m}": float(ratio[i, kk]), f"worst_null_{m}": dm["null"].iloc[i],
                                f"worst_k_{m}": KS[kk]})
            # (4) the probe
            if len(probe):
                dens = probe["denominator"].to_numpy(np.int64)
                fail = np.array([[CAL.fail_counts(int(dn))[k] for k in KS] for dn in dens])
                share = _fam(probe) / fail
                i, kk = np.unravel_index(int(np.argmax(share)), share.shape)
                row.update({"probe_ok": not bool((_fam(probe) >= fail).any()), "probe_worst_share": float(share[i, kk]),
                            "probe_worst_null": probe["null"].iloc[i], "probe_worst_k": KS[kk],
                            "probe_worst_count": int(_fam(probe)[i, kk])})
            else:
                row.update({"probe_ok": True, "probe_worst_share": math.nan, "probe_worst_null": None,
                            "probe_worst_k": None, "probe_worst_count": None})
            row["cond1_floors"] = bool(row["mc_floor_ok"] and row["fixed_exact_floor_ok"] and row["subset_floor_ok"])
            row["cond2_p_mc"] = bool(pmc >= P_MC_MIN)
            row["cond4_probe"] = bool(row["probe_ok"])
            others = {"c1_other": bool(row["mc_floor_ok"] and row["fixed_exact_floor_ok"]), "c1_sized":
                      bool(row["subset_floor_ok"]), "c2": row["cond2_p_mc"], "c3": bool(row["cond3_ratio"]),
                      "c4": row["cond4_probe"]}
            row["eligible"] = bool(row["in_rule"] and all(others.values()))
            for name, key in (("refused_by_cond1_sized_alone", "c1_sized"), ("refused_by_cond3_alone", "c3"),
                              ("refused_by_cond4_alone", "c4")):
                row[name] = bool(row["in_rule"] and not others[key] and all(v for k_, v in others.items() if k_ != key))
            row["eligible_without_floor"] = bool(row["in_rule"] and all(v for k_, v in others.items() if k_ != "c1_sized"))
            out.append(row)
    return pd.DataFrame(out)


def power_summary(power: pd.DataFrame, cands=CANDS) -> pd.DataFrame:
    """P per candidate and scope: the geometric mean over the ten `win1` toys of their MDL80 at k = 13 (infinite when
    any toy's is); the geometric means of MDL50 and MDL80 at k = 13, 15 and 20 beside, and P relative to
    `cons_m1.25`'s in the same scope (the plan's 5)."""
    t = power[(power["row"] == "toy") & (power["toy"] == "P")]
    out = []
    for c in cands:
        for s_ in SCOPES:
            g = t[(t["candidate"] == c) & (t["scope"] == s_)]
            row = {"row": "P", "candidate": c, "cid": _cid(c), "scope": s_, "toys": int(g[g["k"] == 13].shape[0])}
            for k in POWER_KS:
                for q in ("mdl50", "mdl80"):
                    row[f"{q}_k{k}_geomean"] = CAL._geomean(g[g["k"] == k][q].astype(float).to_numpy())
            row["P"] = row["mdl80_k13_geomean"]
            out.append(row)
    df = pd.DataFrame(out)
    for s_ in SCOPES:
        base = df[(df["candidate"] == REFERENCE) & (df["scope"] == s_)]["P"]
        b = float(base.iloc[0]) if len(base) else math.nan
        sel = df["scope"] == s_
        df.loc[sel, "P_rel_cons_m1.25"] = df.loc[sel, "P"].astype(float) / b if (b and math.isfinite(b)) else math.nan
    return df


def _rank_key(r) -> tuple:
    P = float(r["P"]) if r["P"] is not None and not (isinstance(r["P"], float) and math.isnan(r["P"])) else math.inf
    return (P, int(r["members"]), int(r["table_row"]))


def choose(elig: pd.DataFrame, psum: pd.DataFrame) -> dict:
    """The plan's 4.2 order: (1) the primary in scope D -- among rows 1-8 the eligible candidate with the smallest P,
    ties to fewer members, then the earlier row; (2) the scope-Q branch -- among rows 5-7 in scope Q, by the same rule:
    the second statistic when scope D chose, the primary when it did not; (3) NONE when neither has one."""
    t = elig.merge(psum[["candidate", "scope", "P", "P_rel_cons_m1.25"] + [c for c in psum.columns if "geomean" in c]],
                   on=["candidate", "scope"], how="left")

    def best(scope, names):
        g = t[(t["scope"] == scope) & t["eligible"] & t["candidate"].isin(names)]
        return min((r for _, r in g.iterrows()), key=_rank_key) if len(g) else None

    d = best("D", list(L2.NAMES))
    q = best("Q", list(L2.Q_BRANCH))
    primary = second = None
    if d is not None:
        primary = {"candidate": d["candidate"], "cid": d["cid"], "scope": "D", "P": d["P"]}
        if q is not None:
            second = {"candidate": q["candidate"], "cid": q["cid"], "scope": "Q", "P": q["P"]}
        line = f"CHOSEN {d['candidate']} (scope D)\n" + (f"SECOND {q['candidate']} (scope Q)" if q is not None
                                                          else "SECOND NONE")
    elif q is not None:
        primary = {"candidate": q["candidate"], "cid": q["cid"], "scope": "Q", "P": q["P"]}
        line = f"CHOSEN {q['candidate']} (scope Q)"
    else:
        line = "NONE"
    cost = []
    for s_, names in (("D", list(L2.NAMES)), ("Q", list(L2.Q_BRANCH))):
        g = t[(t["scope"] == s_) & t["candidate"].isin(names)]
        for col, what, count in (("refused_by_cond1_sized_alone", "condition 1's sized part alone (a bad subset)",
                                  "bad_subsets"),
                                 ("refused_by_cond3_alone", "condition 3 alone (the core's worst exact ratio)",
                                  "worst_exact_ratio_core"),
                                 ("refused_by_cond4_alone", "condition 4 alone (a probed null at its failure count)",
                                  "probe_worst_count")):
            h = g[g[col]]
            if len(h):
                r = min((r for _, r in h.iterrows()), key=_rank_key)
                cost.append({"row": "cost", "decision": f"the most powerful candidate refused by {what} in scope {s_}",
                             "candidate": r["candidate"], "cid": r["cid"], "scope": s_, "P": r["P"],
                             "refusing_count": r.get(count), "refusing_column": count})
        empty = not bool(g["eligible"].any())
        emptied = bool(empty and g["eligible_without_floor"].any())
        cost.append({"row": "floor_emptied_branch", "scope": s_, "branch": "scope D (rows 1-8)" if s_ == "D" else
                     "scope Q (rows 5-7)", "branch_empty": empty, "floor_alone_emptied": emptied,
                     "decision": f"whether the floor alone emptied the {'scope-D' if s_ == 'D' else 'scope-Q'} branch: "
                                 + ("yes" if emptied else "no")})
    t["chosen"] = None
    if primary is not None:
        t.loc[(t["candidate"] == primary["candidate"]) & (t["scope"] == primary["scope"]), "chosen"] = "primary"
    if second is not None:
        t.loc[(t["candidate"] == second["candidate"]) & (t["scope"] == "Q"), "chosen"] = "second"
    return {"table": t, "primary": primary, "second": second, "line": line, "cost": cost}


def choice_frame(ch: dict, ranking: pd.DataFrame | None = None) -> pd.DataFrame:
    """q126_choice.csv: every candidate in both scopes, the decision row, the cost rows, the probe's ranking."""
    rows = [ch["table"].copy()]
    p, s = ch["primary"], ch["second"]
    rows.append(pd.DataFrame([{"row": "decision", "decision": ch["line"].replace("\n", "; "),
                               "candidate": p["candidate"] if p else None, "scope": p["scope"] if p else None,
                               "second_candidate": s["candidate"] if s else None, "second_scope": s["scope"] if s
                               else None}]))
    if ch["cost"]:
        rows.append(pd.DataFrame(ch["cost"]))
    if ranking is not None and len(ranking):
        rows.append(ranking)
    return pd.concat(rows, ignore_index=True, sort=False)


def spread_rows(long: pd.DataFrame) -> list[dict]:
    """Each subset construction's spread across its subsets (per model, value, candidate and scope; per size and
    pooled): subsets above nominal, and the median, 90th percentile and largest ratio to nominal at each level."""
    d = long[long["group"].isin(["subset", "sizing"])]
    out = []
    lev = np.array(LEVELS)
    for (m, v, c, s_), g in d.groupby(["model", "value", "candidate", "scope"], sort=True):
        r_all = (g[[f"count_{lab}" for lab in LABELS]].to_numpy(float) / g["denominator"].to_numpy(float)[:, None]) \
            / lev[None, :]
        sizes = g["size"].to_numpy()
        for z in [*sorted(set(sizes)), "all"]:
            r = r_all if z == "all" else r_all[sizes == z]
            row = {"row": "spread", "null": f"spread:{z}:{v}:{m}", "group": "subset", "model": m, "value": v,
                   "size": z, "candidate": c, "cid": _cid(c), "scope": s_, "subsets": int(r.shape[0])}
            for i, lab in enumerate(LABELS):
                row[f"above_{lab}"] = int((r[:, i] > 1.0).sum())
                row[f"median_ratio_{lab}"] = CAL._g6(float(np.median(r[:, i])))
                row[f"p90_ratio_{lab}"] = CAL._g6(float(np.quantile(r[:, i], 0.9)))
                row[f"max_ratio_{lab}"] = CAL._g6(float(r[:, i].max()))
            out.append(row)
    return out


def wide(long: pd.DataFrame, cands=CANDS) -> pd.DataFrame:
    """The sizing and drift nulls in one row a null: the null's fields, the denominator and admitted weight, and each
    candidate x scope x level's count as a column `count|<candidate>|<scope>|<level>`."""
    if long.empty:
        return long
    keys = ["null", "part", "kind", "group", "in_rule", "data", "size", "j", "value", "model", "exact_index",
            "scenario", "population", "denominator", "admitted"]
    base = long.drop_duplicates("null")[keys].set_index("null")
    cols = {}
    for c in cands:
        for s_ in SCOPES:
            g = long[(long["candidate"] == c) & (long["scope"] == s_)].set_index("null")
            for lab in LABELS:
                cols[f"count|{c}|{s_}|{lab}"] = g[f"count_{lab}"]
    return base.join(pd.DataFrame(cols)).reset_index()


def completeness_problems(parts: dict[str, dict], seeds: dict, cands=CANDS) -> list[str]:
    """Every candidate, both scopes, on every declared null of every part."""
    out = []
    want = {"core": core_plan(seeds), "drift": drift_plan(seeds),
            **{f"sizing{z}": sizing_plan(seeds, z) for z in SIZES}}
    for part, plan in want.items():
        if part not in parts:
            out.append(f"the part {part} is missing")
            continue
        size = parts[part]["size"]
        names = {e["null"] for e in plan}
        for c in cands:
            for s_ in SCOPES:
                got = set(size[(size["candidate"] == c) & (size["scope"] == s_)]["null"])
                if got != names:
                    out.append(f"{part}: {c} scope {s_} has {len(got)} of its {len(names)} nulls")
                    break
    if "probe" in parts:
        size = parts["probe"]["size"]
        n_probe = PROBE_PER_SIZE * len(SIZES) * len(VALUES) * len(PROBE_MODELS)
        for c in cands:
            for s_ in SCOPES:
                k = size[(size["candidate"] == c) & (size["scope"] == s_)]["null"].nunique()
                if k != n_probe:
                    out.append(f"probe: {c} scope {s_} has {k} of its {n_probe} nulls")
    else:
        out.append("the part probe is missing")
    return out


def nesting_in_m_table(size: pd.DataFrame) -> list[str]:
    """B-17 over the whole table: on every null, rows 1-7's counts non-increasing in m at every level and scope; and
    their bad-subset counts non-increasing in m in each scope."""
    out = []
    cols = [f"count_{lab}" for lab in LABELS]
    for s_ in SCOPES:
        g = size[(size["scope"] == s_) & size["candidate"].isin(L2.NESTED)]
        if g.empty:
            continue
        wide_ = g.set_index(["null", "candidate"])[cols].unstack("candidate")
        for col, lab in zip(cols, LABELS):
            pv = wide_[col]
            pv = pv[[c for c in L2.NESTED if c in pv.columns]]
            bad = (pv.diff(axis=1).iloc[:, 1:] > 0).any(axis=1)
            if bad.any():
                out.append(f"scope {s_}, {lab}: {int(bad.sum())} nulls not nested in m, first {bad.idxmax()}")
    return out


def choice_tables(parts: dict[str, dict], seeds: dict, cands=CANDS) -> dict:
    """From the parts' outputs (each {"size", "power", "cells", "ranking"} frames): the checks, then the eligibility,
    the power summary, the choice and the result frames. Writes nothing."""
    out = {"failed": []}
    inc = completeness_problems(parts, seeds, cands)
    if inc:
        out["failed"] = [f"NOT CHECKED: nulls missing -- {inc[:3]}"]
        return out
    size = pd.concat([parts[p]["size"] for p in PARTS if p in parts and p != "choice"], ignore_index=True, sort=False)
    nest = []
    fam = _fam(size)
    rise = np.flatnonzero((np.diff(fam, axis=1) > 0).any(axis=1))
    if rise.size:
        nest.append(f"counts rise with k on {rise.size} rows, first {size['null'].iloc[rise[0]]}")
    nest += nesting_in_m_table(size)
    elig = eligibility(size, cands)
    for s_ in SCOPES:
        g = elig[elig["scope"] == s_].set_index("candidate")
        b = [int(g.loc[c, "bad_subsets"]) for c in L2.NESTED if c in g.index]
        if any(y > x for x, y in zip(b, b[1:])):
            nest.append(f"scope {s_}: the bad-subset counts {b} rise with m")
    if nest:
        out["failed"] = [f"the nesting assertion fails (the plan's 4.2, B-17): {nest[:3]}"]
        return out
    ranking = parts["probe"].get("ranking", pd.DataFrame())
    want = ranking_frame(L2.probe_ranking(ranking_scores(size[size["group"] == "sizing"]), per_size=PROBE_PER_SIZE,
                                          core=N_CORE))
    got = ranking[["size", "rank", "j", "score_exact"]].astype(str).reset_index(drop=True) if len(ranking) else None
    if got is None or not got.equals(want[["size", "rank", "j", "score_exact"]].astype(str).reset_index(drop=True)):
        out["failed"] = ["the probe's ranking is not the one the sizing parts give (the plan's 3.2, B-23)"]
        return out
    probed = {(int(z), int(j)) for z, j in zip(ranking["size"], ranking["j"])}
    got_probe = {(int(z), int(j)) for z, j in zip(parts["probe"]["size"]["size"], parts["probe"]["size"]["j"])}
    if probed != got_probe:
        out["failed"] = ["the probed nulls are not the ranked subsets'"]
        return out
    power = parts["core"]["power"]
    psum = power_summary(power, cands)
    ch = choose(elig, psum)
    core_probe = size[size["group"] != "sizing"]
    core_probe = core_probe[core_probe["group"] != "drift"]
    long_out = pd.concat([core_probe, pd.DataFrame(spread_rows(size))], ignore_index=True, sort=False)
    sizing = wide(size[size["group"] == "sizing"], cands)
    drift = wide(size[size["group"] == "drift"], cands)
    cells = pd.concat([parts[p]["cells"] for p in PARTS if p in parts and p != "choice"
                       and len(parts[p]["cells"])], ignore_index=True, sort=False) \
        if any(len(parts[p]["cells"]) for p in parts if p != "choice") else pd.DataFrame(
            columns=["null", "candidate", "scope", "cell", "phase", "pattern", "first", "blocks", "weight", "admitted",
                     "k_max"])
    out.update({"size": size, "elig": elig, "psum": psum, "choice": ch, "frames": {
        "q126_cal_size": long_out, "q126_cal_sizing": sizing, "q126_cal_drift": drift,
        "q126_cal_power": pd.concat([power, psum], ignore_index=True, sort=False), "q126_cal_cells": cells,
        "q126_choice": choice_frame(ch, ranking)}})
    return out


# ================================================================================================ the work folder


def git_head(repo: Path = ROOT) -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "unknown"


def _sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def work_dir() -> Path:
    return Path(RUNS_DIR) / WORK_NAME


def _outside_tree(work: Path, repo: Path = ROOT) -> bool:
    w = Path(work).resolve()
    return Path(repo).resolve() not in [w, *w.parents]


DATA_FILES = ("size.csv", "power.csv", "cells.csv", "mismatches.csv", "ranking.csv", "judged_sessions.csv")


def write_part(work: Path, part: str, out: dict, manifest: dict, extra_dirs: dict | None = None) -> Path:
    """All or none (the plan's 6.2): the part's files into a temporary folder of the work folder, then renamed into
    place whole -- `<part>/`, or `<part>.failed/` when a check failed (kept for the diagnosis, never output). Its
    manifest records each data file's sha256; times and host are its only run-dependent fields."""
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    tmp = work / f".{part}.tmp-{os.getpid()}"
    if tmp.exists():
        shutil.rmtree(tmp)
    try:
        tmp.mkdir()
        for name, rows in (("size.csv", out["size"]), ("power.csv", out["power"]), ("cells.csv", out["cells"]),
                           ("mismatches.csv", out["mismatches"]), ("ranking.csv", out.get("ranking", []))):
            df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
            df.to_csv(tmp / name, index=False, lineterminator="\n")
        for name, src in (extra_dirs or {}).items():
            if Path(src).is_dir():
                shutil.copytree(src, tmp / name)
            else:
                shutil.copy2(src, tmp / name)
        files = {}
        for p in sorted(tmp.rglob("*")):
            if p.is_file():
                files[p.relative_to(tmp).as_posix()] = _sha(p)
        man = {**manifest, "part": part, "files": files, "meta": out["meta"], "failed": failed(out)}
        (tmp / "manifest.json").write_text(json.dumps(man, indent=1, default=str), encoding="utf-8")
        dest = work / (f"{part}.failed" if failed(out) else part)
        if dest.exists():
            raise FileExistsError(f"{dest} exists: a part's output is never overwritten")
        os.replace(tmp, dest)
        return dest
    finally:
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)


def read_manifest(d: Path) -> dict:
    return json.loads((Path(d) / "manifest.json").read_text(encoding="utf-8"))


def part_problems(work: Path, part: str, *, commit: str, seeds: dict, versions: dict | None = None) -> list[str]:
    """A part's output is whole, of this commit and seed map (and package versions when given), and each file's
    sha256 is its manifest's."""
    d = Path(work) / part
    if not (d / "manifest.json").is_file():
        return [f"the part {part} has no output"]
    man = read_manifest(d)
    out = []
    if man.get("commit") != commit:
        out.append(f"the part {part} is of commit {str(man.get('commit'))[:12]}, not {commit[:12]}")
    if man.get("seed_map") != {k: int(v) for k, v in seeds.items()}:
        out.append(f"the part {part} ran another seed map")
    if versions is not None and man.get("versions") != versions:
        out.append(f"the part {part} ran other package versions ({man.get('versions')} against {versions})")
    if man.get("failed"):
        out.append(f"the part {part} holds a failed check")
    for rel, sha in man.get("files", {}).items():
        p = d / rel
        if not p.is_file() or _sha(p) != sha:
            out.append(f"the part {part}'s {rel} does not hash to its manifest")
    return out


def versions_problems(work: Path, parts) -> list[str]:
    """The choice refuses a part whose recorded package versions differ from the others' (the plan's 6.2)."""
    vs = {p: read_manifest(Path(work) / p).get("versions") for p in parts if (Path(work) / p / "manifest.json").is_file()}
    distinct = {json.dumps(v, sort_keys=True) for v in vs.values()}
    if len(distinct) > 1:
        return [f"the parts ran different package versions: {vs}"]
    return []


def reproduction_problems(work: Path, part: str) -> list[str]:
    """After a code fix: every data file of the earlier commit's whole part (`<part>.prev-*`) has the same sha256 in
    the rerun (the plan's 6.2, the red team's m-1)."""
    out = []
    new = read_manifest(Path(work) / part)["files"]
    for prev in sorted(Path(work).glob(f"{part}.prev-*")):
        old = read_manifest(prev)["files"]
        for rel, sha in old.items():
            if rel == "manifest.json":
                continue
            if new.get(rel) != sha:
                out.append(f"{part}: {rel} differs from {prev.name}'s (sha256 {sha[:12]} against "
                           f"{str(new.get(rel))[:12]})")
        for rel in set(new) - set(old):
            out.append(f"{part}: {rel} is new against {prev.name}")
    return out


def read_part_frames(work: Path, part: str) -> dict:
    d = Path(work) / part

    def rd(f):
        p = d / f
        if not p.is_file() or p.stat().st_size <= 1:
            return pd.DataFrame()
        try:
            return pd.read_csv(p, low_memory=False, float_precision="round_trip")
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
    return {"size": rd("size.csv"), "power": rd("power.csv"), "cells": rd("cells.csv"), "ranking": rd("ranking.csv"),
            "manifest": read_manifest(d)}


# ================================================================================================ the refusals


def lock_problem(env: Mapping | None = None) -> str | None:
    """The run lock is held by this run's own job: `S2X_LOCK_HOLDER` (set by `scripts/run_clean.py` under the lock)
    names the clean run, and `run.lock` at the main root names the same job."""
    from extended.lock_guard import LOCK_HOLDER_ENV, LOCK_NAME, main_root

    env = os.environ if env is None else env
    holder, name = env.get(LOCK_HOLDER_ENV), env.get(CLEAN_RUN_ENV)
    if not holder or holder != name:
        return (f"the run lock is not held by this run ({LOCK_HOLDER_ENV}={holder!r}, the clean run {name!r}): run it "
                f"under scripts/run_clean.py with --hours and --mem-gb")
    root = main_root(ROOT)
    lock = root / LOCK_NAME if root else None
    try:
        job = json.loads(lock.read_text(encoding="utf-8")).get("job") if lock and lock.is_file() else None
    except (OSError, ValueError):
        job = None
    if job != holder:
        return f"run.lock names job {job!r}, not this run's {holder!r}"
    return None


def preflight(target: Path, part: str | None, *, seeds: dict | None = None, guard: bool = True,
              repo: Path = ROOT) -> list[str]:
    """The refusals before any read, in order (each a reason; empty when the run may start)."""
    from extended import results as XR

    seeds = SEEDS if seeds is None else seeds
    bad = XR.clean_run_problem()
    if bad:
        return [f"this process is not a clean run -- {bad}. Run it as: {RUN_CMD}"]
    bad = lock_problem()
    if bad:
        return [bad]
    if part in (None, "choice"):
        clash = [x for x in RESULT_FILES if (target / f"{x}.csv").exists()
                 or (target / f"{x}.csv.manifest.json").exists()]
        if clash:
            return [f"{clash} exist in {target}; a result file is never overwritten"]
    probs = pin_problems(repo)
    probs += seed_map_problems(seeds, CAL_BLOCK, DRAW_ROLES + ("tests",), spare=SPARE, repo=repo)
    if probs:
        return probs
    probs = provenance_problems(deterministic_plan(seeds), seeds, CAL_BLOCK)
    if probs:
        return [f"the seed-provenance assertion refuses: {probs[:5]}"]
    work = work_dir()
    if not _outside_tree(work, repo):
        return [f"the work folder {work} must lie outside this tree"]
    fails = sorted(p.name for p in work.glob("*.failed")) if work.is_dir() else []
    if fails:
        return [f"a failed check is on record ({fails}): it is diagnosed under the failure protocol, never rerun"]
    if guard:
        sp, notes = seed_block_problems(repo)
        for x in notes:
            _log(f"seed blocks: {x}")
        if sp:
            return ["the plan's seed blocks are not unused -- " + "; ".join(sp[:10]) + ". No other seeds are picked: "
                    "report it to the lead."]
    return []


# ================================================================================================ the commands


#: the validation table's roles (the plan's 4.1 words), for `manifest_seed_problems`
VAL_ROLE_TEXT = {
    "tests": "the validation build's tests", "fixed_mc": "the fixed-data streams' Monte Carlo side draws",
    "subsets": "the thinned subsets", "subset_mc": "the core subsets' Monte Carlo side draws",
    "synthetic": "the realistic synthetic nulls", "beside_cp": "the count-persistent nulls beside",
    "beside_flat": "the `flat` form beside", "exact_sample": "the exact nulls' seeded sample of cells",
    "drift": "the drift populations beside"}


def manifest_seed_problems(seeds: dict) -> list[str]:
    """The seed map a manifest is about to record equals the plan's 4.1 table of its block, as parsed from the pinned
    plan (the red team's n5): checked where every manifest is written, not only at the start."""
    t = int(seeds.get("tests", -1))
    if t in CAL_BLOCK:
        return seed_map_problems(seeds, CAL_BLOCK, DRAW_ROLES + ("tests",), spare=SPARE)
    if t in VAL_BLOCK:
        text = plan_path().read_text(encoding="utf-8")
        _, spare = parsed_seed_map(text, "validation", VAL_ROLE_TEXT)
        return seed_map_problems(seeds, VAL_BLOCK, tuple(VAL_ROLE_TEXT), plan_block="validation",
                                 role_text=VAL_ROLE_TEXT, spare=spare)
    return [f"the seed map's tests seed {t} is in neither of the plan's blocks"]


def _manifest_base(seeds: dict, extra: dict | None = None) -> dict:
    probs = manifest_seed_problems(seeds)
    if probs:
        raise ProvenanceRefused(f"REFUSED: the seed map to be recorded is not the plan's: {probs[:3]}")
    blobs = {rel: blob_id(ROOT / rel) for rel in (*VALIDATED_BLOBS, MODULE, SCRIPT, VALIDATE_SCRIPT)
             if (ROOT / rel).is_file()}
    p = plan_path()
    return {"decision": DECISION, "task": TASK, "plan": p.relative_to(ROOT).as_posix(), "plan_sha256": file_sha_lf(p),
            "commit": git_head(), "seed_map": {k: int(v) for k, v in seeds.items()}, "spare_seeds": list(SPARE),
            "versions": _versions(), "blobs": blobs, **(extra or {})}


def _time_fields(t0: float) -> dict:
    return {"time": {"finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                     "seconds": round(time.time() - t0, 1),
                     "peak_working_set_mb": round(working_set_mb(peak=True), 1)}, "host": platform.node()}


def load_core_inputs(work: Path) -> tuple[list[str], str, pd.DataFrame]:
    """The calendar and P-16's pairs from the core part's output, each checked against its manifest and E-094 (2)."""
    d = Path(work) / "core"
    man = read_manifest(d)
    cal, sha = judged_sessions(pd.read_csv(d / "judged_sessions.csv", dtype=str)["date"].tolist())
    bad = calendar_problems(cal, sha)
    if bad or sha != man.get("calendar_sha256"):
        raise ProvenanceRefused("REFUSED: the core part's calendar is not E-094 (2)'s or not its manifest's")
    pq = d / "pairs" / "p16_pairs.parquet"
    if man["files"].get("pairs/p16_pairs.parquet") != _sha(pq):
        raise ProvenanceRefused("REFUSED: the core part's pairs do not hash to its manifest")
    p, _ = Q82.load_pairs(pq, cal)
    return cal, sha, p


def compute_part_main(part: str, work: Path, *, seeds: dict, reps: int = REPS, reps_beside: int = REPS_BESIDE,
                      cands=CANDS) -> int:
    """One part in its own process: its plan, the provenance assertion before any draw, its computation, its output
    written all or none."""
    t0 = time.time()
    extra: dict = {}
    extra_dirs: dict = {}
    if part == "core":
        plan = core_plan(seeds)
        probs = provenance_problems(plan, seeds, CAL_BLOCK)              # before any read and any draw
        if probs:
            print(f"REFUSED: the seed-provenance assertion refuses: {probs[:5]}", flush=True)
            return REFUSED
        cal, sha, src = read_calendar()
        bad = calendar_problems(cal, sha)
        if bad:
            print("REFUSED: " + "; ".join(bad), flush=True)
            return REFUSED
        _log(f"judged sessions: {len(cal)}, {cal[0]} to {cal[-1]}, sha256 {sha} (E-094 (2))")
        scratch = Path(work) / f".core.inputs-{os.getpid()}"
        if scratch.exists():
            shutil.rmtree(scratch)
        scratch.mkdir(parents=True)
        try:
            calf = scratch / "judged_sessions.csv"
            pd.DataFrame({"date": cal}).to_csv(calf, index=False, lineterminator="\n")
            r = subprocess.run([sys.executable, "scripts/q16_p16_pairs.py", "--out", str(scratch / "pairs")],
                               cwd=str(ROOT))
            if r.returncode:
                _log(f"the pairs step exited {r.returncode}")
                return 1
            p, pinfo = Q82.load_pairs(scratch / "pairs" / "p16_pairs.parquet", cal)
            inp = CAL.Inputs(p, len(cal), seeds)
            out = compute_nulls(part, plan, inp, len(cal), reps, list(cands), reps_beside=reps_beside)
            extra = {"calendar_sha256": sha, "calendar_source": src, "pairs_identity": pinfo.get("identity"),
                     "pairs_sha256": pinfo.get("parquet_sha256")}
            extra_dirs = {"judged_sessions.csv": calf, "pairs": scratch / "pairs"}
            dest = write_part(work, part, out, {**_manifest_base(seeds, extra), **_time_fields(t0),
                                                "timing": out["timing"]}, extra_dirs)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
        _log(f"part core written to {dest}")
        return FAILED_CHECK if failed(out) else 0
    if part.startswith("sizing") or part == "probe":
        if part == "probe":
            sz = []
            for z in SIZES:
                bad = part_problems(work, f"sizing{z}", commit=git_head(), seeds=seeds)
                if bad:
                    print("REFUSED: " + "; ".join(bad), flush=True)
                    return REFUSED
                sz.append(read_part_frames(work, f"sizing{z}")["size"])
            ranking = L2.probe_ranking(ranking_scores(pd.concat(sz, ignore_index=True)), per_size=PROBE_PER_SIZE,
                                       core=N_CORE)
            plan = probe_plan(seeds, ranking)
        else:
            plan = sizing_plan(seeds, int(part[len("sizing"):]))
            ranking = None
        probs = provenance_problems(plan, seeds, CAL_BLOCK)              # before the pairs are read, before any draw
        if probs:
            print(f"REFUSED: the seed-provenance assertion refuses: {probs[:5]}", flush=True)
            return REFUSED
        cal, sha, p = load_core_inputs(work)
        n = len(cal)
        inp = CAL.Inputs(p, n, seeds)
        out = compute_nulls(part, plan, inp, n, reps, list(cands), reps_beside=reps_beside)
        if ranking is not None:
            out["ranking"] = ranking_frame(ranking)
        extra = {"calendar_sha256": sha}
    elif part == "drift":
        plan = drift_plan(seeds)
        probs = provenance_problems(plan, seeds, CAL_BLOCK)
        if probs:
            print(f"REFUSED: the seed-provenance assertion refuses: {probs[:5]}", flush=True)
            return REFUSED
        out = compute_nulls(part, plan, None, N_SESSIONS, reps, list(cands), drift_inputs=drift_inputs_for(N_SESSIONS))
    else:
        raise ValueError(f"no part {part!r}")
    dest = write_part(work, part, out, {**_manifest_base(seeds, extra), **_time_fields(t0), "timing": out["timing"]})
    _log(f"part {part} written to {dest}")
    return FAILED_CHECK if failed(out) else 0


def choice_main(work: Path, *, seeds: dict) -> int:
    """The choice: every part's manifest checked; the tables; the result files written through `extended.results`,
    all or none -- every frame and name checked before the first write."""
    from extended import results as XR

    t0 = time.time()
    commit = git_head()
    need = [p for p in PARTS if p != "choice"]
    probs = []
    for p in need:
        probs += part_problems(work, p, commit=commit, seeds=seeds)
    probs += versions_problems(work, need)
    if probs:
        print("REFUSED: " + "; ".join(probs[:8]), flush=True)
        return REFUSED
    parts = {p: read_part_frames(work, p) for p in need}
    res = choice_tables(parts, seeds)
    if res["failed"]:
        for f in res["failed"]:
            print(f"FAILED CHECK: {f}", flush=True)
        print("FAILED CHECK: no result is written and no choice is made; the record is in " + str(work), flush=True)
        return FAILED_CHECK
    ch = res["choice"]
    probs = manifest_seed_problems(seeds)
    if probs:
        print(f"REFUSED: the seed map to be recorded is not the plan's: {probs[:3]}", flush=True)
        return REFUSED
    _log(f"read ledger: {XR.note_ledger_appends()}")
    man0 = parts["core"]["manifest"]
    common = {"decision": DECISION, "plan": man0["plan"], "plan_sha256": PLAN_SHA256, "task": TASK,
              "argv": sys.argv[1:], "reps": REPS, "reps_beside": REPS_BESIDE, "levels": list(LEVELS),
              "k_range": list(KS), "candidates": list(CANDS), "in_rule": sorted(map(list, L2.IN_RULE)),
              "n_sessions": N_SESSIONS, "calendar_sha256": man0.get("calendar_sha256"),
              "calendar_source": man0.get("calendar_source"), "pairs_sha256": man0.get("pairs_sha256"),
              "pairs_identity": man0.get("pairs_identity"), "blobs": man0["blobs"], "versions": man0["versions"],
              "seed_map": {k: int(v) for k, v in seeds.items()}, "spare_seeds": list(SPARE),
              "seed_block": list(CAL_BLOCK), "admission_b": str(L2.admission_b(N_SESSIONS)),
              "subsets_a_size": N_SUBSETS, "core_subsets": N_CORE, "probe_per_size": PROBE_PER_SIZE,
              "drift_populations": DRIFT_POPULATIONS, "p_mc_min": P_MC_MIN, "ratio_max": str(RATIO_MAX),
              "fail_counts": CAL.FAIL, "parts": {p: {"files": parts[p]["manifest"]["files"],
                                                     "time": parts[p]["manifest"].get("time"),
                                                     "scalar_checked": parts[p]["manifest"]["meta"].get("scalar_checked")}
                                                 for p in need},
              "choice": ch["line"].replace("\n", "; ")}
    roles = {"q126_cal_size": ("fixed_mc", ("fixed_mc", "subsets", "subset_mc", "synthetic", "beside_cp", "beside_flat",
                                            "exact_sample", "probe")),
             "q126_cal_sizing": ("subsets", ("subsets",)), "q126_cal_drift": ("drift", ("drift",)),
             "q126_cal_power": ("subset_mc", ("subsets", "subset_mc", "synthetic")),
             "q126_cal_cells": ("subsets", ("subsets", "exact_sample", "drift")), "q126_choice": (None, ())}
    desc = {"q126_cal_size": "every core and probed null x candidate x scope x level, and each subset construction's "
                             "spread (core and sizing subsets)",
            "q126_cal_sizing": "the 31,850 sizing nulls, one row a null: every candidate x scope x level's exact count",
            "q126_cal_drift": "the 6,000 drift nulls beside, one row a null (they decide nothing)",
            "q126_cal_power": "the toys' MDL50 and MDL80 at k = 13, 15, 20 and P per candidate and scope",
            "q126_cal_cells": "the rejecting cells (4.5) of every exact null above a quarter of nominal, pairs in the rule",
            "q126_choice": f"the plan's 4.2 applied by code -- {ch['line'].replace(chr(10), '; ')}; from the tables "
                           "beside, no randomness of its own"}
    target = RESULTS_DIR
    clash = [nm for nm in roles if (target / f"{nm}.csv").exists() or (target / f"{nm}.csv.manifest.json").exists()]
    if clash or set(roles) != set(RESULT_FILES) or set(res["frames"]) != set(RESULT_FILES):
        print(f"REFUSED: the result files {clash} exist, or the frames are not the declared files", flush=True)
        return REFUSED
    written = []
    try:
        for nm in RESULT_FILES:
            seed, rr = roles[nm]
            params = {**common, "seeds": {r: int(seeds[r]) for r in rr}}
            csv, mp = XR.write_result(res["frames"][nm], nm, script=SCRIPT, seed=None if seed is None else
                                      int(seeds[seed]), parameters=params, description=f"Q-126 ({DECISION}): {desc[nm]}",
                                      exploratory=False, require_seed=seed is not None)
            written.append(nm)
            _log(f"wrote {csv} ({len(res['frames'][nm])} rows) and {mp.name}")
    except Exception as exc:                                              # a partial write is a failed run
        print(f"FAILED CHECK: the result files were written in part ({written}) -- {type(exc).__name__}: {exc}. A "
              "partial write to results/ is a failed run, diagnosed; nothing is deleted", flush=True)
        return FAILED_CHECK
    for row in ch["cost"]:
        print(f"cost: {row['decision']}" + (f": {row['candidate']} P {row['P']}" if row.get("candidate") else ""),
              flush=True)
    print(ch["line"], flush=True)
    _log(f"the choice in {time.time() - t0:.0f} s")
    return 0


def _step(name: str, args: list[str], log_file: Path | None = None) -> int:
    _log(f"step {name}: {' '.join(args)}")
    t0 = time.time()
    r = subprocess.run([sys.executable, *args], cwd=str(ROOT))
    msg = f"step {name}: exit {r.returncode}, {time.time() - t0:.0f} s"
    _log(msg)
    if log_file is not None:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {git_head()[:12]} {msg}\n")
    return r.returncode


def prepare_part(work: Path, part: str, commit: str) -> str:
    """Before a part runs: "done" when it is whole at this commit; else any partial folder is deleted and a whole part
    of another commit moved to `<part>.prev-<commit>` (its rerun must reproduce it); "run"."""
    work = Path(work)
    for tmp in work.glob(f".{part}.tmp-*"):
        shutil.rmtree(tmp, ignore_errors=True)                   # partial: no output
    d = work / part
    if (d / "manifest.json").is_file():
        man = read_manifest(d)
        if man.get("commit") == commit:
            return "done"
        prev = work / f"{part}.prev-{str(man.get('commit'))[:12]}"
        if prev.exists():
            raise FileExistsError(f"{prev} exists already")
        os.replace(d, prev)
    elif d.exists():
        shutil.rmtree(d)
    return "run"


def driver(parts, work: Path, script: str = SCRIPT, *, step=_step) -> int:
    """The parts in their declared order, each in its own process; a failed check stops the run, a crash stops it too
    (to be rerun from scratch), a reproduction that differs is a failed check."""
    commit = git_head()
    log_file = Path(work) / "driver.log"
    for part in parts:
        state = prepare_part(work, part, commit)
        if state == "done":
            _log(f"part {part}: whole at this commit, not rerun")
            continue
        rc = step(part, [script, "--part", part, "--work", str(work)], log_file)
        if rc == FAILED_CHECK:
            print(f"FAILED CHECK: the part {part} stopped on a failed check; its record is in {work}", flush=True)
            return FAILED_CHECK
        if rc:
            return rc
        if part != "choice" and list(Path(work).glob(f"{part}.prev-*")):
            bad = reproduction_problems(work, part)
            if bad:
                print("FAILED CHECK: a part rerun at a new commit does not reproduce its earlier output -- "
                      + "; ".join(bad[:5]), flush=True)
                return FAILED_CHECK
            _log(f"part {part}: reproduces its earlier commit's output, file for file")
    return 0


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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check-read", action="store_true")
    ap.add_argument("--parts", default=None, help="a comma list of declared parts to run, in the declared order")
    ap.add_argument("--part", default=None, help=argparse.SUPPRESS)
    ap.add_argument("--work", type=Path, default=None, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.check_read:
        return _check_read()
    t0 = time.time()
    part = a.part
    try:
        probs = preflight(RESULTS_DIR, part, guard=True)
    except ProvenanceRefused as exc:
        probs = [str(exc)]
    if probs:
        print("REFUSED: " + "; ".join(probs), flush=True)
        return REFUSED
    work = work_dir() if a.work is None else Path(a.work)
    if not _outside_tree(work):
        print(f"REFUSED: the work folder {work} must lie outside this tree", flush=True)
        return REFUSED
    work.mkdir(parents=True, exist_ok=True)
    try:
        if part is not None:
            if part not in PARTS:
                print(f"REFUSED: no part {part!r}; the parts are {PARTS}", flush=True)
                return REFUSED
            rc = choice_main(work, seeds=SEEDS) if part == "choice" else compute_part_main(part, work, seeds=SEEDS)
            return rc
        parts = PARTS if a.parts is None else tuple(x for x in PARTS if x in a.parts.split(","))
        if a.parts is not None and set(a.parts.split(",")) - set(PARTS):
            print(f"REFUSED: unknown parts {sorted(set(a.parts.split(',')) - set(PARTS))}", flush=True)
            return REFUSED
        _log(f"the seed map {SEEDS}; the parts {parts}; the work folder {work}")
        rc = driver(parts, work)
        _log(f"EXIT {rc} ({time.time() - t0:.0f} s)")
        return rc
    except ProvenanceRefused as exc:
        print(str(exc), flush=True)
        return REFUSED


if __name__ == "__main__":
    sys.exit(main())
