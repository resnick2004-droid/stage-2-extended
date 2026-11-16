"""Q-82 (E-052; the red team's M2 and M1, `docs/reviews/PASS_LINE_CODE_2026-11-16.md`): the pass line's fresh-seed
validation -- one command for a clean run, built ready to run (TASK_QUEUE Q-83 runs it, under the lock).

    python scripts/run_clean.py --name q83-validation --task Q-83 --hours 5 --mem-gb 1.2 -- python scripts/q82_validation.py
    python scripts/q82_validation.py --check-read      # the reader's verdict on the calendar read; reads and writes nothing
    python scripts/q82_validation.py --results-dir <tmp> --work <tmp> --pairs <dir> --days <csv> --reps 300   # a test

**Why.** Q-55 replays Q-16's own replications (the same seeds, pairs and code), so it checks provenance, not the
choices made on those draws: `cons` picked from seven candidates, and the two-sample form's treated block count devised
after its first form failed (M2). This run applies the shipped statistics to the same null constructions drawn afresh,
on seeds no file had used (E-052's block; the seed map below), with the criterion fixed in E-052 before the run.

**The statistics** (`extended/lift_bound.py`, refused unless its blob is the one E-052 and F-02 name): `SHIPPED`
(`cons`: `t21w`, `t42w` and `t63w` all reject) in its three uses -- `bound` (C1, the lift over the coin twin),
`two_sample_bound` (F-02's C1') and `placebo_selection_bound` (E-023's twin), the two-sample ones with the treated
block count (`DIFF_DF_RULE`). They are computed as the calibration computed them (`many_levels`, `diff_many_levels`),
and every replication that `cons` rejects at a family level -- and the first few of each null -- is decided again by
the scalar function F-02 calls, on trades rebuilt from the session sums (the statistic reads nothing else); a
disagreement prints DIFFERS and is counted in every table. The members are reported beside; they are not the test.

**(i) The criterion's nulls: Q-16's, drawn afresh** (`scripts/q16_calibrate.py`'s constructions, imported, never
edited; a test proves that on Q-16's own seeds this script reproduces Q-16's rejection counts exactly):
- the lift's 70 real nulls -- P-16's registered pairs (`scripts/q16_p16_pairs.py`, its three identities refusing) on
  the judged block, sign-flipped by blocks of 1, 5, 21 and 63 sessions or on the coin's side, on the `offered`, `taken`
  and five `thinN` streams (the thinnings drawn anew) -- and its 25 realistic synthetic nulls (`iid`, `cluster`,
  `cluster_ar1`, `regime01`, `volclust` at 200 to 5,000 trades; the stress nulls are not in the criterion and not run);
- the 55 placebo-selection nulls and the 56 C1' nulls on P-16's judged offers (the C1' subsets drawn anew).

**(ii) Beside, never the criterion: count-persistent nulls** (`extended/count_nulls.py`; F-02's K0 addresses them):
- P-16's judged offers thinned at a persistent, outcome-independent rate -- a fresh thinning each replication, every
  offer of session j kept with probability min(1, c m_j), m_j one of the profiles `flat`, `trend2x`, `trend3x`,
  `ar98s07`, `ar98s10`, `ar98s15`, `ar995s10`, `burst10x` -- to 200 to 5,000 trades, sides flipped by session (and by
  21 sessions for the two strongest profiles), in win probability at 1R (net R at 3R for the two strongest, offer by
  offer); C1' with level and placebo fills (five times as many) thinned together, sides shared; the placebo-selection
  twin with a filter firing at the persistent rate;
- the red team's synthetic count-persistent nulls (Appendix A): Q-16's `cluster` outcome on iid, trend, AR and
  one-quarter-at-10x counts at 0.3 and 2 trades a session; C1' on the AR and burst profiles at 0.3 and 1.

**The criterion (E-052, fixed before the run).** For each statistic, at every k in 11..15 (level 0.05/(k(k+1))): no
null of (i) has its 95 % Clopper-Pearson interval (recomputed from its counts) wholly above nominal. The script prints
`criterion (E-052) <statistic>: HOLDS | FAILS | NOT CHECKED` -- NOT CHECKED when a statistic's nulls are not all there
(95, 56, 55), never a pass. (ii) is reported beside, with no verdict.

**Replications.** 200,000 a null (`--reps`), as Q-16 ran every t-type, selection and C1' null; batches of 10,000 for
(i) (Q-16's layout) and 5,000 for (ii). At 0.05/240 that is about 42 expected rejections at nominal.

**Reads** (each through `extended/reader.py`): the judged block's session list from A1's stored days
(`read_walks("A1", "days", ..., columns=["date"])`, purpose `registered_design`, declaration E-035, design P-16, as
the red team's m3 asked), and P-16's pairs rebuilt by `scripts/q16_p16_pairs.py`, whose engine read is authorised
the same way (as Q-55's). The pairs file is this repository's own derived output, read in the compute steps under
E-035's exemption, as Q-16's script reads it. Nothing else is read; no bar is opened by this script.

**What it writes** (`extended.results.write_result`, each with its manifest and its own seeds in `parameters.seeds`;
into this tree's `results/` only inside the clean run `scripts/run_clean.py` made -- refused at once otherwise):

| file | rows |
|---|---|
| `q82_validation_one_sample.csv` | (i) the lift's 95 nulls x `t21w`, `t42w`, `t63w`, `cons` x levels: rejections, rate, interval, ratio |
| `q82_validation_two_sample.csv` | (i) the 55 placebo-selection and 56 C1' nulls, the same columns |
| `q82_count_persistent.csv` | (ii) every count-persistent null, the same columns, with the busiest quarter's share of the trades |
| `q82_criterion.csv` | the criterion per statistic and k (`section` `criterion`, with the verdicts) and (ii)'s summary (`beside`) |
| `q82_judged_sessions.csv` | the judged block's session list as the calibration uses it: ordinal, date; its count and the sha256 of the ISO dates joined by "\\n" (no trailing newline) in the manifest's parameters |

Every result file is built before the first is written; a write that fails leaves the earlier files, each whole with
its manifest, and the log names them. The run's own read-ledger lines are recorded as this run's writes (D-207) once
checked to be appended ledger records, so they do not stamp the manifests `-dirty` (`extended.results.
note_ledger_appends`, Q-97; the writer applies it to every write inside a clean run).

**Refusals (exit 3, before any step):** this tree's `results/` outside a clean run; a result file that exists; a
`lift_bound.py` other than the validated blob; any seed of E-052's block named elsewhere -- in code, data, a result or
a declaration, on any branch or in the working tree (a document's mention, or a declaration's line that cites this run
by Q-82, Q-83 or E-052, is printed, not refused) -- in which case the run stops and no other seeds are picked; a work
folder inside the tree; a calendar of other than 657 sessions.
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
import subprocess
import sys
import tempfile
import time
from pathlib import Path

for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import CLEAN_RUN_ENV, RESULTS_DIR, RUNS_DIR  # noqa: E402
from extended import count_nulls as CN  # noqa: E402
from extended import lift_bound as LB  # noqa: E402
from extended.procmem import working_set_mb  # noqa: E402


def _load_q16():
    """Q-16's calibration script, imported (never edited): its null constructions are (i)'s."""
    spec = importlib.util.spec_from_file_location("q16_calibrate_for_q82", ROOT / "scripts" / "q16_calibrate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


Q16 = _load_q16()

SCRIPT = "scripts/q82_validation.py"
DECISION = "E-052"
#: the reader's row for P-16's registered pairs and the judged calendar (E-035, as Q-55's pairs step names it)
READ_ROW = "E-035"
READ_DESIGN = "P-16"
DAYS_REL = "vendor/stage2/data/atlas/A1/days.parquet"
RUN_CMD = ("python scripts/run_clean.py --name q83-validation --task Q-83 --hours 5 --mem-gb 1.2 -- "
           "python scripts/q82_validation.py")

# ---- the seed map (E-052) ----
#: E-052's block, verified unused before the run (`seed_block_problems`, refusing)
SEED_BLOCK = tuple(range(20262010, 20262019 + 1))
SEEDS = {
    "tests": 20262010,           # the tests' synthetic inputs (tests/test_q82_validation.py, tests/test_count_nulls.py)
    "lift_real": 20262011,       # (i) the lift's real nulls: the thinN subsets [s, 999], null i's flips [s, i]
    "lift_syn": 20262012,        # (i) the realistic synthetic nulls [s, i], i the null's index in Q-16's list
    "selection": 20262013,       # (i) the placebo-selection nulls [s, 5000 + i]
    "c1p": 20262014,             # (i) the C1' nulls: the level/placebo subsets [s, 9000], null i's flips [s, 7000 + i]
    "count_real_one": 20262015,  # (ii) P-16's offers thinned at a persistent rate, one-sample [s, i]
    "count_real_two": 20262016,  # (ii) the same for C1' and the placebo-selection twin [s, i]
    "count_syn": 20262017,       # (ii) the red team's synthetic count-persistent nulls [s, i]
}
#: reserved by E-052's block, drawn by nothing in this run
SPARE = (20262018, 20262019)
# ---- end of the seed map ----

#: Q-16's own seeds in this layout -- only for the test that proves (i)'s constructions are Q-16's
Q16_LAYOUT_SEEDS = {**SEEDS, "lift_real": Q16.SEED_LIFT_REAL, "lift_syn": Q16.SEED_LIFT_SYN,
                    "selection": Q16.SEED_LIFT_REAL, "c1p": Q16.SEED_LIFT_REAL}
#: each part's seed keys, by the null family's name
PART_SEED = {"i_lift": {"real": "lift_real", "syn": "lift_syn"}, "i_two": {"selection": "selection", "c1p": "c1p"},
             "ii_real": {"one": "count_real_one", "two": "count_real_two"}, "ii_syn": {"syn": "count_syn"}}
PARTS = ("i_lift", "i_two", "ii_real", "ii_syn")

#: the code this validation is of: E-052 and F-02 name this blob (git's, of the LF text)
VALIDATED_BLOBS = {"extended/lift_bound.py": "984f3467a4a05aa790d3ea43e94ac7761f0725b2"}

JUDGED_FIRST, JUDGED_LAST = "2024-01-02", "2026-07-16"
N_SESSIONS = 657
REPS = 200_000
BATCH = Q16.BATCH                # 10,000: Q-16's batch, so (i)'s draws follow its layout
BATCH_II = 5_000
SUB_PER_OFFER = 128              # replications a sub-batch in the offer-by-offer engine (memory)
SCALAR_FIRST = 3                 # each null's first replications re-decided by the scalar function, rejecting or not
FAMILY_LEVELS = tuple(LB.family_level(k) for k in LB.K_RANGE)
EXTRA_LEVELS = (0.001, 0.005, 0.01, 0.025)
LEVELS = FAMILY_LEVELS + EXTRA_LEVELS
MEMBERS = ("t21w", "t42w", "t63w")
STAT = LB.SHIPPED
DF_RULE = "treated"

#: Q-16's realistic synthetic nulls (the note's 2.2); the stress nulls are outside the criterion and not run
REALISTIC = ("iid", "cluster", "cluster_ar1", "regime01", "volclust")
STREAMS = ("offered", "taken") + tuple(f"thin{n}" for n in Q16.SIZES)
C1P_SIZES = (200, 500, 1000, 2000)
C1P_SIDES = (("shared", 1), ("shared", 21), ("shared", 63), ("indep", 1), ("indep", 21), ("indep", 63), ("coin", 1))
#: (ii): the count-persistent grids
CP_STRONG = ("ar98s15", "burst10x")
CP_TWO_PROFILES = ("ar98s07", "ar98s10", "ar98s15", "burst10x")
CP_ONE = ([(p, T, "win1", 1) for p in CN.PROFILES for T in Q16.SIZES]
          + [(p, T, "win1", 21) for p in CP_STRONG for T in Q16.SIZES]
          + [(p, T, "net3", 1) for p in CP_STRONG for T in (200, 2000)])
CP_C1P = [(p, n1) for p in CP_TWO_PROFILES for n1 in C1P_SIZES]
CP_SEL = [(p, sh) for p in CP_TWO_PROFILES for sh in (0.02, 0.05, 0.10, 0.25)]
CPSYN_ONE = [(p, m) for p in CN.SYNTHETIC_PROFILES for m in (0.3, 2.0)]
CPSYN_C1P = [(p, m1) for p in CP_TWO_PROFILES for m1 in (0.3, 1.0)]

#: the criterion's statistics and how many (i) nulls each must have
EXPECTED_NULLS = {"bound": 95, "two_sample_bound": 56, "placebo_selection_bound": 55}
STAT_LABELS = {"bound": "cons by lift_bound.bound (C1: the lift over the coin twin)",
               "two_sample_bound": "cons by lift_bound.two_sample_bound (C1', treated block count)",
               "placebo_selection_bound": "cons by lift_bound.placebo_selection_bound (E-023's twin, treated count)"}
BESIDE = "beside (E-052): not the criterion; F-02's K0 addresses it"
RESULT_FILES = ("q82_validation_one_sample", "q82_validation_two_sample", "q82_count_persistent", "q82_criterion",
                "q82_judged_sessions")
PAIR_COLS = ["date", "slot", "coin", "kl_1", "ks_1", "rl_3", "rs_3", f"xl_{Q16.R_SCHED:g}", f"xs_{Q16.R_SCHED:g}"]

#: the seed check: files that may name the block (this item's own, and the lead's record of it)
SEED_PATTERN = r"2026201[0-9]"
SEED_ALLOW = frozenset({SCRIPT, "extended/count_nulls.py", "tests/test_q82_validation.py", "tests/test_count_nulls.py",
                        "DECISIONS.md", "TASK_QUEUE.md", "STATUS.md", "PROGRESS.md"})
SEED_ALLOW_PREFIXES = ("docs/briefs/Q-82_", "docs/briefs/Q-83_")


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S', time.gmtime())} UTC] {msg}", flush=True)


def _kk(level: float):
    return next((k for k in LB.K_RANGE if abs(LB.family_level(k) - level) < 1e-15), None)


# ================================================================================================ refusals


#: a line of a declaration that names the block together with one of these cites this run; it reserves nothing
CITES_THIS_RUN = re.compile(r"\b(?:Q-82|Q-83|E-052)\b")


def _is_use(path: str, lines: list[str]) -> bool:
    """Whether a file's mentions of the block can draw or reserve a seed: any in code, data or a result; in a
    declaration (`prereg/`) unless every such line cites this run (Q-82, Q-83 or E-052); never a document's (another
    `.md`)."""
    if not path.lower().endswith(".md"):
        return True
    if path.startswith("prereg/"):
        return not all(CITES_THIS_RUN.search(x) for x in lines)
    return False


def seed_block_problems(repo: Path | str = ROOT) -> tuple[list[str], list[str]]:
    """(problems, notes): every file naming a seed of E-052's block (word-bounded) on any branch, remote or tag, or in
    the working tree (tracked or untracked, not ignored), outside this item's files. A use is a problem; a document's
    mention, or a declaration's line citing this run, a note."""
    repo = Path(repo)

    def git(*a: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, encoding="utf-8",
                              errors="replace")

    refs = git("for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", "refs/tags")
    if refs.returncode:
        return [f"cannot list the refs of {repo}: {refs.stderr.strip()[:200]}"], []
    hits: dict[tuple[str, str], list[str]] = {}
    r = git("grep", "--untracked", "-n", "-I", "-w", "-E", SEED_PATTERN)
    if r.returncode not in (0, 1):
        return [f"git grep failed in the working tree: {r.stderr.strip()[:200]}"], []
    for line in r.stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) == 3:
            hits.setdefault(("working tree", parts[0]), []).append(parts[2])
    names = [x for x in refs.stdout.split() if x and not x.endswith("/HEAD")]
    for i in range(0, len(names), 40):
        r = git("grep", "-n", "-I", "-w", "-E", SEED_PATTERN, *names[i:i + 40], "--")
        if r.returncode not in (0, 1):
            return [f"git grep failed on {names[i:i + 40][:3]}...: {r.stderr.strip()[:200]}"], []
        for line in r.stdout.splitlines():
            parts = line.split(":", 3)
            if len(parts) == 4:
                hits.setdefault((parts[0], parts[1]), []).append(parts[3])
    problems, notes = set(), set()
    for (where, path), lines in hits.items():
        path = path.replace("\\", "/")
        if path in SEED_ALLOW or path.startswith(SEED_ALLOW_PREFIXES):
            continue
        (problems if _is_use(path, lines) else notes).add(f"{path} ({where})")
    return sorted(problems), sorted(notes)


def blob_id(path: Path) -> str:
    """git's blob id of a file's LF text (the id `git hash-object` gives under `* text=auto`)."""
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def module_blob_problems(overrides: dict | None = None) -> list[str]:
    """The validated modules' blobs, refusing any other (the validation is of that code)."""
    checks = {rel: (ROOT / rel, want) for rel, want in VALIDATED_BLOBS.items()}
    checks.update(overrides or {})
    out = []
    for rel, (path, want) in checks.items():
        got = blob_id(Path(path))
        if got != want:
            out.append(f"{rel} is blob {got[:12]}, not the validated {want[:12]} (E-052; a new module version is "
                       "validated under its own row)")
    return out


# ================================================================================================ inputs


def judged_sessions(dates) -> tuple[list[str], str]:
    """(the judged block's sessions, the sha256 of their ISO dates joined by "\\n", no trailing newline): every stored
    day from 2024-01-02 to 2026-07-16, as Q-16's `judged_calendar` takes them; refusing a date that is not ISO, a
    repeated day, or a count other than 657."""
    ds = sorted(str(x) for x in dates)
    bad = [x for x in ds if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", x)]
    if bad:
        raise SystemExit(f"REFUSED: the calendar holds dates that are not ISO (YYYY-MM-DD): {bad[:3]}")
    if len(set(ds)) != len(ds):
        raise SystemExit("REFUSED: the calendar repeats a day")
    cal = [x for x in ds if JUDGED_FIRST <= x <= JUDGED_LAST]
    if len(cal) != N_SESSIONS:
        raise SystemExit(f"REFUSED: the judged calendar has {len(cal)} sessions, not {N_SESSIONS} (Q-16's)")
    return cal, hashlib.sha256("\n".join(cal).encode("ascii")).hexdigest()


def read_calendar(days_csv: Path | None) -> tuple[list[str], str, dict]:
    """The judged session list: A1's stored days through the reader (a ledgered `registered_design` read inside a
    clean run), or a test's CSV with a `date` column."""
    if days_csv is not None:
        d = pd.read_csv(days_csv, dtype=str)["date"].tolist()
        src = {"seam": str(days_csv)}
    else:
        from extended import reader

        df = reader.read_walks("A1", "days", JUDGED_FIRST, JUDGED_LAST, purpose=reader.REGISTERED_DESIGN,
                               declaration=READ_ROW, design=READ_DESIGN, columns=["date"],
                               what=f"{DECISION} (Q-82/Q-83): the judged block's session list -- A1's stored days, "
                                    "dates only, as Q-16's calibration used them")
        d = df["date"].astype(str).tolist()
        src = {"file": DAYS_REL, "columns": ["date"], "purpose": "registered_design", "declaration": READ_ROW,
               "design": READ_DESIGN, "data_manifest_sha256": _data_manifest_sha(DAYS_REL)}
    cal, sha = judged_sessions(d)
    return cal, sha, src


def _data_manifest_sha(rel: str) -> str | None:
    p = ROOT / "vendor" / "DATA_MANIFEST_stage2.sha256"
    if not p.is_file():
        return None
    want = rel.removeprefix("vendor/stage2/")
    for line in p.read_text(encoding="utf-8").splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[1].strip().lstrip("*") == want:
            return parts[0].lower()
    return None


def load_pairs(pq: Path, cal: list[str]) -> tuple[pd.DataFrame, dict]:
    """P-16's judged pairs in (date, slot) order with their session ordinal -- refusing pairs whose identity did not
    hold, and a judged pair whose date is not in the calendar (as `scripts/q16_calibrate.py` does)."""
    pq = Path(pq)
    meta = json.loads(pq.with_suffix(".json").read_text(encoding="utf-8"))
    sha = hashlib.sha256(pq.read_bytes()).hexdigest()
    if not str(meta.get("identity", "")).startswith("HOLDS") or meta.get("parquet_sha256") != sha:
        raise SystemExit(f"REFUSED: {pq} is not the identity-checked output of scripts/q16_p16_pairs.py")
    p = pd.read_parquet(pq, columns=PAIR_COLS)  # one-door-exempt: E-056 -- p16_pairs.parquet, this repository's own derived file (P-16's registered pairs, scripts/q16_p16_pairs.py's identity-checked output), not Stage 2's bars or walks
    p["date"] = p["date"].astype(str)
    p = p[(p["date"] >= JUDGED_FIRST) & (p["date"] <= JUDGED_LAST)]
    pos = {d: i for i, d in enumerate(cal)}
    if not p["date"].isin(pos).all():
        raise SystemExit("REFUSED: a judged pair's date is not in the judged calendar")
    p = p.sort_values(["date", "slot"], kind="stable").reset_index(drop=True)
    p["session"] = p["date"].map(pos).astype(np.int64)
    return p, {**meta, "parquet_sha256_checked": sha}


def lift_streams(p: pd.DataFrame, thin_seed: int) -> dict:
    """Q-16's streams (`real_streams`): `offered`, `taken` (re-entry when flat at 1.5R, the next mark at least 5
    minutes after the coin side's exit) and the `thinN` subsets, drawn with `default_rng([thin_seed, 999])`."""
    s = p["session"].to_numpy(np.int64)
    win1 = 0.5 * ((p["kl_1"] == 1).astype(float) - (p["ks_1"] == 1).astype(float)).to_numpy()
    net3 = 0.5 * (p["rl_3"].astype(float) - p["rs_3"].astype(float)).to_numpy()
    coin = p["coin"].astype(int).to_numpy()
    out = {"offered": (s, win1, net3, coin)}
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
    out["taken"] = tuple(a[take] for a in (s, win1, net3, coin))
    rng = np.random.default_rng([int(thin_seed), 999])
    for n in Q16.SIZES:
        idx = np.sort(rng.choice(len(p), size=n, replace=False))
        out[f"thin{n}"] = tuple(a[idx] for a in (s, win1, net3, coin))
    return out


def judged_offers(p: pd.DataFrame, n: int) -> dict:
    """Q-16's `judged_offers`: every judged offer's session, the coin side's own win at 1R and net R at 3R, the pair
    differences at those, the coin."""
    s = p["session"].to_numpy(np.int64)
    c = p["coin"].astype(int).to_numpy()
    wl, ws = (p["kl_1"] == 1).to_numpy(float), (p["ks_1"] == 1).to_numpy(float)
    rl, rs = p["rl_3"].to_numpy(float), p["rs_3"].to_numpy(float)
    return {"s": s, "y_win1": np.where(c > 0, wl, ws), "y_net3": np.where(c > 0, rl, rs),
            "v_win1": 0.5 * (wl - ws), "v_net3": 0.5 * (rl - rs), "coin": c, "n": int(n)}


class Data:
    """What the generators read: the calendar's length and, given pairs, P-16's judged offers -- their sessions, the
    offers a session, the outcome categories (counts only) and Q-16's streams and subsets, built when first asked."""

    def __init__(self, p: pd.DataFrame | None, cal: list[str], seeds: dict | None = None):
        self.n = len(cal)
        self.seeds = dict(SEEDS if seeds is None else seeds)
        self.p = p
        self._cache: dict = {}
        if p is not None:
            self.s = p["session"].to_numpy(np.int64)
            self.n_off = int(len(self.s))
            self.offers = np.bincount(self.s, minlength=self.n).astype(np.int64)
            wl, ws = (p["kl_1"] == 1).to_numpy(), (p["ks_1"] == 1).to_numpy()
            v = 0.5 * (wl.astype(float) - ws.astype(float))
            self.cats_v = CN.category_counts(self.s, np.where(v > 0, 0, np.where(v < 0, 2, 1)), self.n, 3)
            y = np.where(p["coin"].astype(int).to_numpy() > 0, wl, ws)
            self.cats_y = CN.category_counts(self.s, np.where(y, 0, 1), self.n, 2)
            self.wins_y = self.cats_y[:, 0].astype(float)
            self.v_net3 = 0.5 * (p["rl_3"].astype(float) - p["rs_3"].astype(float)).to_numpy()

    def _need(self):
        if self.p is None:
            raise ValueError("this null reads P-16's pairs; none were given")

    @property
    def streams(self) -> dict:
        self._need()
        if "streams" not in self._cache:
            self._cache["streams"] = lift_streams(self.p, self.seeds["lift_real"])
        return self._cache["streams"]

    @property
    def O(self) -> dict:                                       # noqa: N802 (Q-16's name)
        self._need()
        if "O" not in self._cache:
            self._cache["O"] = judged_offers(self.p, self.n)
        return self._cache["O"]

    @property
    def c1p_subsets(self) -> dict:
        """Q-16's C1' level and placebo subsets (five times as many), drawn with `default_rng([c1p seed, 9000])`."""
        if "c1p" not in self._cache:
            rng0 = np.random.default_rng([int(self.seeds["c1p"]), 9000])
            sub = {}
            for n1 in C1P_SIZES:
                idx = rng0.permutation(len(self.O["s"]))[: 6 * n1]
                sub[n1] = (np.sort(idx[:n1]), np.sort(idx[n1:]))
            self._cache["c1p"] = sub
        return self._cache["c1p"]

    @property
    def indicator(self):
        """(sessions, offers) sparse: each offer's session (the offer-by-offer engine's sums)."""
        self._need()
        if "ind" not in self._cache:
            from scipy import sparse

            self._cache["ind"] = sparse.csr_matrix((np.ones(self.n_off), (self.s, np.arange(self.n_off))),
                                                   shape=(self.n, self.n_off))
        return self._cache["ind"]


# ================================================================================================ the nulls


def null_plan(seeds: dict | None = None) -> list[dict]:
    """Every null of the run, in order, with its generator entropy `[seed, index]` (no data read)."""
    seeds = SEEDS if seeds is None else seeds
    plan: list[dict] = []

    def add(part, family, idx, **kw):
        plan.append({"part": part, "family": family, "entropy": [int(seeds[PART_SEED[part][family]]), int(idx)],
                     "stream": None, "value": None, "side": None, "L": None, "model": None, "profile": None,
                     "size": None, "share": None, "m": None, "engine": None, "q16": None, **kw})

    for ni, sp in enumerate(Q16.real_null_specs(dict.fromkeys(STREAMS))):
        add("i_lift", "real", ni, null=sp["null"], kind="lift_real", group="real", form="one-sample",
            function="bound", in_criterion=True, stream=sp["stream"], value=sp["value"], side=sp["side"], L=sp["L"],
            q16=sp)
    for ni, sp in enumerate(Q16.syn_specs()):
        if sp["model"] in REALISTIC:
            add("i_lift", "syn", ni, null=sp["null"], kind="lift_syn", group="realistic synthetic", form="one-sample",
                function="bound", in_criterion=True, model=sp["model"], size=sp["trades"], q16=sp)
    sel = [(m, sh, v) for m in Q16.SEL_MODELS for sh in Q16.SHARES for v in ("win1", "net3")
           if not (m == "offer" and v == "net3")]
    for ni, (m, sh, v) in enumerate(sel):
        add("i_two", "selection", 5000 + ni, null=f"select:{m}:{sh:g}:{v}", kind="selection", group="real",
            form="placebo-selection", function="placebo_selection_bound", in_criterion=True, model=m, share=sh,
            value=v)
    c1 = [(n1, v, side, L) for n1 in C1P_SIZES for v in ("win1", "net3") for side, L in C1P_SIDES]
    for ni, (n1, v, side, L) in enumerate(c1):
        add("i_two", "c1p", 7000 + ni, null=f"c1p:{n1}:{v}:{side}{L if side != 'coin' else ''}", kind="c1p",
            group="real", form="two-sample (C1')", function="two_sample_bound", in_criterion=True, size=n1, value=v,
            side=side, L=L)
    for i, (p, T, v, L) in enumerate(CP_ONE):
        add("ii_real", "one", i, null=f"cp:{p}:{T}:{v}:persist{L}", kind="cp_one", group="count-persistent real",
            form="one-sample", function="bound", in_criterion=False, profile=p, size=T, value=v, side="persist", L=L,
            engine="hypergeometric" if v == "win1" else "per-offer")
    i = 0
    for p, n1 in CP_C1P:
        add("ii_real", "two", i, null=f"cp_c1p:{p}:{n1}:win1:shared1", kind="cp_c1p", group="count-persistent real",
            form="two-sample (C1')", function="two_sample_bound", in_criterion=False, profile=p, size=n1,
            value="win1", side="shared", L=1, engine="hypergeometric")
        i += 1
    for p, sh in CP_SEL:
        add("ii_real", "two", i, null=f"cp_select:{p}:{sh:g}:win1", kind="cp_select", group="count-persistent real",
            form="placebo-selection", function="placebo_selection_bound", in_criterion=False, profile=p, share=sh,
            value="win1", engine="hypergeometric")
        i += 1
    i = 0
    for p, m in CPSYN_ONE:
        add("ii_syn", "syn", i, null=f"cpsyn:{p}:{m:g}", kind="cpsyn_one", group="count-persistent synthetic",
            form="one-sample", function="bound", in_criterion=False, profile=p, m=m)
        i += 1
    for p, m1 in CPSYN_C1P:
        add("ii_syn", "syn", i, null=f"cpsyn_c1p:{p}:{m1:g}", kind="cpsyn_c1p", group="count-persistent synthetic",
            form="two-sample (C1')", function="two_sample_bound", in_criterion=False, profile=p, m=m1)
        i += 1
    return plan


def generator(e: dict, data: Data):
    """The null's batch generator `gen(rng, r)`: one-sample `(S, N)`; two-sample `(S1, N1, S2, N2)`; the
    placebo-selection twin `(A, B, C, M)` -- each (sessions, r) or (sessions, 1). For (ii) the counts (and the sides)
    are drawn before anything that reads an outcome."""
    k, n = e["kind"], data.n
    if k == "lift_real":
        spec, streams = e["q16"], data.streams
        return lambda rng, r: Q16.real_batch(spec, streams, n, rng, r)
    if k == "lift_syn":
        spec = e["q16"]
        return lambda rng, r: Q16.syn_batch(spec, n, rng, r)
    if k == "selection":
        O, v = data.O, e["value"]
        Cr = np.bincount(O["s"], weights=O[f"y_{v}"], minlength=n)[:, None]
        Mr = np.bincount(O["s"], minlength=n).astype(float)[:, None]

        def gen(rng, r):
            A, B = Q16._sel_batch(e["model"], e["share"], O, f"y_{v}", rng, r)
            return A, B, Cr, Mr
        return gen
    if k == "c1p":
        O, v, side, L = data.O, e["value"], e["side"], int(e["L"])
        i1, i2 = data.c1p_subsets[int(e["size"])]
        x = O[f"v_{v}"] * (O["coin"] if side == "coin" else 1)
        V1 = np.bincount(O["s"][i1], weights=x[i1], minlength=n)
        V2 = np.bincount(O["s"][i2], weights=x[i2], minlength=n)
        N1 = np.bincount(O["s"][i1], minlength=n).astype(float)[:, None]
        N2 = np.bincount(O["s"][i2], minlength=n).astype(float)[:, None]

        def gen(rng, r):
            g1 = Q16._flip_signs(rng, n, L, r)
            g2 = g1 if side in ("shared", "coin") else Q16._flip_signs(rng, n, L, r)
            return V1[:, None] * g1, N1, V2[:, None] * g2, N2
        return gen
    if k == "cp_one":
        c, prof, L = float(e["size"]) / data.n_off, e["profile"], int(e["L"])
        if e["engine"] == "hypergeometric":
            def gen(rng, r):
                K = CN.thin_counts(data.offers, CN.keep_rates(CN.intensity(prof, n, r, rng), c), rng)
                g = Q16._flip_signs(rng, n, L, r)
                S = CN.subset_sums(data.cats_v, (0.5, 0.0, -0.5), [K], rng)[0]
                return S * g, K.astype(float)
            return gen

        def gen(rng, r):                                          # net R: offer by offer
            rate = CN.keep_rates(CN.intensity(prof, n, r, rng), c)
            g = Q16._flip_signs(rng, n, L, r)
            ind, v = data.indicator, data.v_net3
            S, N = np.empty((n, r)), np.empty((n, r))
            for a0 in range(0, r, SUB_PER_OFFER):
                b0 = min(r, a0 + SUB_PER_OFFER)
                keep = CN.bernoulli_keep(data.s, rate[:, a0:b0], rng)
                N[:, a0:b0] = ind @ keep.astype(float)
                S[:, a0:b0] = ind @ np.where(keep, v[:, None], 0.0)
            return S * g, N
        return gen
    if k == "cp_c1p":
        c, prof = 6.0 * float(e["size"]) / data.n_off, e["profile"]

        def gen(rng, r):
            q = CN.keep_rates(CN.intensity(prof, n, r, rng), c)
            K1, K2 = CN.split_counts(data.offers, q, 1.0 / 6.0, rng)
            g = Q16._flip_signs(rng, n, 1, r)
            S1, S2 = CN.subset_sums(data.cats_v, (0.5, 0.0, -0.5), [K1, K2], rng)
            return S1 * g, K1.astype(float), S2 * g, K2.astype(float)
        return gen
    if k == "cp_select":
        share, prof = float(e["share"]), e["profile"]
        Cr, Mr = data.wins_y[:, None], data.offers.astype(float)[:, None]

        def gen(rng, r):
            B = CN.thin_counts(data.offers, CN.keep_rates(CN.intensity(prof, n, r, rng), share), rng)
            A = CN.subset_sums(data.cats_y, (1.0, 0.0), [B], rng)[0]
            return A, B.astype(float), Cr, Mr
        return gen
    if k == "cpsyn_one":
        prof, m = e["profile"], float(e["m"])

        def gen(rng, r):
            N = CN.synthetic_counts(prof, m, n, r, rng)
            return CN.cluster_sums(N, rng), N
        return gen
    if k == "cpsyn_c1p":
        prof, m1 = e["profile"], float(e["m"])

        def gen(rng, r):
            mult = CN.intensity(prof, n, r, rng)
            N1 = rng.poisson(mult * m1).astype(float)
            N2 = rng.poisson(mult * 5.0 * m1).astype(float)
            S1, S2 = CN.cluster_two_sample(N1, N2, rng)
            return S1, N1, S2, N2
        return gen
    raise ValueError(f"unknown null kind {k!r}")


# ================================================================================================ the scalar functions


def _col(X, j: int) -> np.ndarray:
    X = np.asarray(X)
    if X.ndim == 1:
        return X
    return X[:, j] if X.shape[1] > 1 else X[:, 0]


def _pseudo(S: np.ndarray, N: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Trades with the same session sums: N_j trades of S_j / N_j on session j (the statistic reads nothing else)."""
    Ni = np.rint(N).astype(np.int64)
    x = np.divide(S, N, out=np.zeros(len(N)), where=Ni > 0)
    return np.repeat(x, Ni), np.repeat(np.arange(len(Ni)), Ni)


def redecide_one(S, N, j: int, n: int, level: float) -> bool:
    x, s = _pseudo(_col(S, j), _col(N, j))
    return LB.bound(STAT, x, s, n, level=level).rejects


def redecide_two(S1, N1, S2, N2, j: int, n: int, level: float) -> bool:
    x1, s1 = _pseudo(_col(S1, j), _col(N1, j))
    x2, s2 = _pseudo(_col(S2, j), _col(N2, j))
    return LB.two_sample_bound(x1, s1, x2, s2, n, level=level).rejects


def redecide_sel(A, B, C, M, j: int, n: int, level: float) -> bool:
    """The placebo-selection twin: each session's M_j offers, the first B_j selected; the selected carry A_j / B_j each,
    the rest (C_j - A_j) / (M_j - B_j) -- the same selected and population sums."""
    a, b, c, m = _col(A, j), _col(B, j), _col(C, j), _col(M, j)
    mi, bi = np.rint(m).astype(np.int64), np.rint(b).astype(np.int64)
    if (bi > mi).any() or ((bi == mi) & ~np.isclose(a, c)).any():
        raise ValueError("not a selection of the offers")
    session = np.repeat(np.arange(n), mi)
    start = np.r_[0, np.cumsum(mi)[:-1]]
    selected = (np.arange(int(mi.sum())) - np.repeat(start, mi)) < np.repeat(bi, mi)
    ysel = np.divide(a, b, out=np.zeros(n), where=bi > 0)
    yoth = np.divide(c - a, m - b, out=np.zeros(n), where=(mi - bi) > 0)
    y = np.where(selected, np.repeat(ysel, mi), np.repeat(yoth, mi))
    return LB.placebo_selection_bound(y, session, selected, n, level=level).rejects


REDECIDE = {"one-sample": redecide_one, "two-sample (C1')": redecide_two, "two-sample": redecide_two,
            "placebo-selection": redecide_sel}


def scalar_check(form: str, arrs, cons_family: np.ndarray, n: int, first: int = 0) -> tuple[int, int]:
    """(decisions checked, decisions that differ): every replication `cons` rejects at a family level (rows of
    `cons_family`, in `FAMILY_LEVELS`' order), and the first `first`, decided again by the scalar function."""
    cons_family = np.asarray(cons_family, dtype=bool)
    idx = np.flatnonzero(cons_family.any(axis=0))
    if first:
        idx = np.union1d(idx, np.arange(min(int(first), cons_family.shape[1])))
    fn = REDECIDE[form]
    checked = bad = 0
    for j in idx:
        for li, a in enumerate(FAMILY_LEVELS[: cons_family.shape[0]]):
            checked += 1
            bad += int(fn(*arrs, int(j), n, a) != bool(cons_family[li, j]))
    return checked, bad


# ================================================================================================ the run


def run_null(e: dict, gen, reps: int, batch: int, n: int) -> tuple[list[dict], dict]:
    rng = np.random.default_rng(e["entropy"])
    rej = {m: np.zeros(len(LEVELS), dtype=np.int64) for m in MEMBERS + (STAT,)}
    t1, t2, tops = [], [], []
    checked = bad = done = 0
    nf = len(FAMILY_LEVELS)
    one = e["form"] == "one-sample"
    while done < reps:
        r = min(batch, reps - done)
        arrs = gen(rng, r)
        if one:
            dec = {m: LB.many_levels(m, arrs[0], arrs[1], LEVELS)[0] for m in MEMBERS}
        else:
            dec = {m: LB.diff_many_levels(m, *arrs, LEVELS, df_rule=DF_RULE)[0] for m in MEMBERS}
        cons = dec[MEMBERS[0]] & dec[MEMBERS[1]] & dec[MEMBERS[2]]
        for m in MEMBERS:
            rej[m] += dec[m].sum(axis=1)
        rej[STAT] += cons.sum(axis=1)
        N1 = np.broadcast_to(arrs[1], (n, r))
        t1.append(N1.sum(axis=0))
        tops.append(CN.top_share(N1))
        if not one:
            t2.append(np.broadcast_to(arrs[3], (n, r)).sum(axis=0))
        c_, b_ = scalar_check(e["form"], arrs, cons[:nf], n, first=SCALAR_FIRST if done == 0 else 0)
        checked += c_
        bad += b_
        done += r
        del arrs, dec, cons
    t1, tops = np.concatenate(t1), np.concatenate(tops)
    desc = {k: e[k] for k in ("null", "part", "group", "form", "function", "in_criterion", "stream", "value", "side",
                              "L", "model", "profile", "size", "share", "m", "engine")}
    desc.update({"seed": e["entropy"][0], "entropy": json.dumps(e["entropy"]),
                 "subset_entropy": json.dumps([e["entropy"][0], 9000]) if e["kind"] == "c1p" else None,
                 "trades_mean": float(t1.mean()), "trades2_mean": float(np.concatenate(t2).mean()) if t2 else None,
                 "top_share_p50": float(np.median(tops)), "top_share_p90": float(np.quantile(tops, 0.9)),
                 "scalar_checked": checked, "scalar_mismatched": bad})
    rows = []
    for m in MEMBERS + (STAT,):
        for li, a in enumerate(LEVELS):
            k = int(rej[m][li])
            lo, hi = LB.clopper_pearson(k, reps)
            rows.append({**desc, "method": m, "level": a, "k": _kk(a), "reps": reps, "rejections": k,
                         "rate": k / reps, "ci_lo": lo, "ci_hi": hi, "ratio": (k / reps) / a,
                         "above_nominal": bool(lo > a)})
    return rows, {"checked": checked, "mismatched": bad, "cons_k11": int(rej[STAT][0])}


def compute_part(part: str, p: pd.DataFrame | None, cal: list[str], reps: int, seeds: dict | None = None,
                 log=_log) -> tuple[list[dict], dict]:
    """Every null of `part`: its size rows and the part's meta."""
    seeds = SEEDS if seeds is None else seeds
    t0 = time.time()
    data = Data(p, cal, seeds)
    plan = [x for x in null_plan(seeds) if x["part"] == part]
    batch = BATCH if part.startswith("i_") else BATCH_II
    rows, checked, bad = [], 0, 0
    for e in plan:
        t1 = time.time()
        r_, info = run_null(e, generator(e, data), reps, batch, data.n)
        rows += r_
        checked += info["checked"]
        bad += info["mismatched"]
        flag = f"; DIFFERS from the scalar function in {info['mismatched']} of {info['checked']}" if info["mismatched"] \
            else ""
        log(f"  {e['null']}: cons at 0.05/132 {info['cons_k11']} of {reps}; {time.time() - t1:.0f} s, "
            f"ws {working_set_mb():.0f} MB{flag}")
    meta = {"part": part, "nulls": len(plan), "reps": reps, "batch": batch, "seconds": round(time.time() - t0, 1),
            "peak_working_set_mb": round(working_set_mb(peak=True), 1), "scalar_checked": checked,
            "scalar_mismatched": bad, "seeds": {kk: int(seeds[kk]) for kk in PART_SEED[part].values()},
            "n_sessions": len(cal)}
    return rows, meta


# ================================================================================================ the criterion


def _summary(gk: pd.DataFrame, a: float) -> dict:
    if gk.empty:
        return {"nulls": 0, "rows": 0, "nulls_above": 0, "above_nulls": "", "worst_null": None,
                "worst_rejections": None, "worst_reps": None, "worst_rate": math.nan, "worst_ratio": math.nan,
                "worst_ci_lo": math.nan, "worst_ci_hi": math.nan}
    rj = gk["rejections"].astype(int).to_numpy()
    rp = gk["reps"].astype(int).to_numpy()
    ci = [LB.clopper_pearson(int(x), int(y)) for x, y in zip(rj, rp)]
    lo = np.array([c[0] for c in ci])
    hi = np.array([c[1] for c in ci])
    rate = rj / rp
    above = lo > a
    i = int(np.argmax(rate / a))
    nulls = gk["null"].astype(str).to_numpy()
    return {"nulls": int(len(set(nulls))), "rows": int(len(gk)), "nulls_above": int(above.sum()),
            "above_nulls": ";".join(nulls[above]), "worst_null": nulls[i] if rj[i] > 0 else "(none rejected)",
            "worst_rejections": int(rj[i]),
            "worst_reps": int(rp[i]), "worst_rate": float(rate[i]), "worst_ratio": float(rate[i] / a),
            "worst_ci_lo": float(lo[i]), "worst_ci_hi": float(hi[i])}


def _flag(x) -> bool:
    return str(x).strip().lower() in ("true", "1")


def criterion(size: pd.DataFrame, expected: dict | None = None) -> pd.DataFrame:
    """E-052's criterion, per statistic and k, from the counts (each interval recomputed): `section` `criterion` --
    HOLDS at a k when every one of the statistic's (i) nulls is there and none has its 95 % interval wholly above the
    nominal rate, FAILS when one has, NOT CHECKED when a null is missing; the row `k` = "11-15" is the statistic's
    verdict (FAILS if any k fails, else NOT CHECKED if any k was not checked, else HOLDS). `section` `beside`: (ii)'s
    count-persistent nulls summarised the same way, with no verdict."""
    expected = EXPECTED_NULLS if expected is None else expected
    d = size[size["method"] == STAT].copy()
    d["_in"] = d["in_criterion"].map(_flag)
    d["_k"] = pd.to_numeric(d["k"], errors="coerce")
    out = []
    for fn in EXPECTED_NULLS:
        g = d[d["_in"] & (d["function"] == fn)]
        per = []
        for k in LB.K_RANGE:
            a = LB.family_level(k)
            row = {"section": "criterion", "statistic": fn, "label": STAT_LABELS[fn], "group": "real and realistic",
                   "k": k, "level": a, "expected_nulls": expected[fn], **_summary(g[g["_k"] == k], a)}
            complete = row["nulls"] == expected[fn] and row["rows"] == row["nulls"]
            row["verdict"] = "NOT CHECKED" if not complete else ("FAILS" if row["nulls_above"] else "HOLDS")
            per.append(row)
        vs = [r["verdict"] for r in per]
        worst = max(per, key=lambda r: (-1.0 if math.isnan(r["worst_ratio"]) else r["worst_ratio"]))
        out += per + [{"section": "criterion", "statistic": fn, "label": STAT_LABELS[fn], "group": "real and realistic",
                       "k": "11-15", "level": math.nan, "expected_nulls": expected[fn],
                       "nulls": min(r["nulls"] for r in per), "rows": sum(r["rows"] for r in per),
                       "nulls_above": sum(r["nulls_above"] for r in per),
                       "above_nulls": ";".join(f"k{r['k']}:{r['above_nulls']}" for r in per if r["above_nulls"]),
                       **{x: worst[x] for x in ("worst_null", "worst_rejections", "worst_reps", "worst_rate",
                                                "worst_ratio", "worst_ci_lo", "worst_ci_hi")},
                       "worst_k": worst["k"],
                       "verdict": "FAILS" if "FAILS" in vs else ("NOT CHECKED" if "NOT CHECKED" in vs else "HOLDS")}]
    for fn in EXPECTED_NULLS:
        for grp in sorted(set(d.loc[~d["_in"], "group"].astype(str))):
            g = d[~d["_in"] & (d["function"] == fn) & (d["group"].astype(str) == grp)]
            if g.empty:
                continue
            for k in LB.K_RANGE:
                a = LB.family_level(k)
                out.append({"section": "beside", "statistic": fn, "label": STAT_LABELS[fn], "group": grp, "k": k,
                            "level": a, "expected_nulls": None, **_summary(g[g["_k"] == k], a), "verdict": BESIDE})
    return pd.DataFrame(out)


def verdicts(crit: pd.DataFrame) -> dict:
    """{statistic: its verdict over k = 11..15}."""
    c = crit[(crit["section"] == "criterion") & (crit["k"].astype(str) == "11-15")]
    return {str(r["statistic"]): str(r["verdict"]) for _, r in c.iterrows()}


# ================================================================================================ the commands


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
        return 3
    print("reader: AUTHORISED (nothing read)", flush=True)
    return 0


def _outside_tree(work: Path) -> bool:
    w = work.resolve()
    return ROOT.resolve() not in [w, *w.parents]


def _compute_main(a) -> int:
    work = Path(a.work)
    if not _outside_tree(work):
        print(f"REFUSED: the work folder {work} must lie outside this tree", flush=True)
        return 3
    cal, sha = judged_sessions(pd.read_csv(a.calendar, dtype=str)["date"].tolist())
    p, pmeta = (None, {})
    if a.compute != "ii_syn":
        if a.pairs_file is None:
            print("REFUSED: --pairs-file is needed for this part", flush=True)
            return 3
        p, pmeta = load_pairs(Path(a.pairs_file), cal)
    t0 = time.time()
    _log(f"part {a.compute}: {len([x for x in null_plan() if x['part'] == a.compute])} nulls x {a.reps} replications; "
         f"{len(p) if p is not None else 0} judged offers")
    rows, meta = compute_part(a.compute, p, cal, a.reps)
    d = work / a.compute
    d.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(d / "size.csv", index=False)
    meta.update({"calendar_sha256": sha, "pairs_sha256": pmeta.get("parquet_sha256_checked"),
                 "offers": int(len(p)) if p is not None else None})
    (d / "meta.json").write_text(json.dumps(meta, indent=1, default=str), encoding="utf-8")
    _log(f"part {a.compute} done: {time.time() - t0:.0f} s, peak working set {meta['peak_working_set_mb']} MB; "
         f"scalar re-decision {meta['scalar_checked']} checked, {meta['scalar_mismatched']} mismatched")
    return 0


def _step(name: str, args: list[str]) -> None:
    _log(f"step {name}: {' '.join(args)}")
    t0 = time.time()
    r = subprocess.run([sys.executable, *args], cwd=str(ROOT))
    if r.returncode != 0:
        _log(f"step {name} FAILED (exit {r.returncode}); nothing written")
        raise SystemExit(r.returncode if r.returncode in (2, 3) else 1)
    _log(f"step {name}: done, {time.time() - t0:.0f} s")


def _versions() -> dict:
    import scipy

    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "pandas": pd.__version__}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--results-dir", type=Path, default=None, help="default: this tree's results/ (clean run only)")
    ap.add_argument("--work", type=Path, default=None)
    ap.add_argument("--pairs", type=Path, default=None, help="a pairs folder already made (a test's seam)")
    ap.add_argument("--days", type=Path, default=None, help="a CSV of stored days, column `date` (a test's seam)")
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--check-read", action="store_true", help="the reader's verdict on the calendar read; nothing read")
    ap.add_argument("--compute", choices=PARTS, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--calendar", type=Path, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--pairs-file", type=Path, default=None, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.compute is not None:
        return _compute_main(a)
    if a.check_read:
        return _check_read()
    t0 = time.time()

    from extended import results as XR                  # the vendored writer: this process only

    target = Path(a.results_dir) if a.results_dir is not None else RESULTS_DIR
    if XR.protected(target):                             # refuse at once, never after hours of work
        bad = XR.clean_run_problem()
        if bad:
            print(f"REFUSED: {target} is a results/ folder of this repository and this process is not a clean run "
                  f"-- {bad}. Run it as: {RUN_CMD}", flush=True)
            return 3
    clash = [x for x in RESULT_FILES if (target / f"{x}.csv").exists() or (target / f"{x}.csv.manifest.json").exists()]
    if clash:
        print(f"REFUSED: {clash} exist in {target}; a result file is never overwritten", flush=True)
        return 3
    blob = module_blob_problems()
    if blob:
        print("REFUSED: " + "; ".join(blob), flush=True)
        return 3
    seed_probs, seed_notes = seed_block_problems(ROOT)
    for x in seed_notes:
        _log(f"seed block named in a document (a mention, not a use): {x}")
    if seed_probs:
        print("REFUSED: E-052's seed block 20262010-20262019 is not unused -- named in " + "; ".join(seed_probs[:10])
              + ". The run stops here; no other seeds are picked (E-052): report it to the lead.", flush=True)
        return 3
    _log(f"seed block: unused outside this item's files (all branches, remotes, tags and the working tree); "
         f"seed map {SEEDS}, spare {list(SPARE)}")
    name = os.environ.get(CLEAN_RUN_ENV)
    work = Path(a.work) if a.work is not None else (Path(RUNS_DIR) / f"{name}.work" if name
                                                     else Path(tempfile.mkdtemp(prefix="q82_")))
    work.mkdir(parents=True, exist_ok=True)
    if not _outside_tree(work):
        print(f"REFUSED: the work folder {work} must lie outside this tree (the checkout stays clean)", flush=True)
        return 3
    _log(f"Q-82: target {target}, work {work}, clean run {name or 'none'}, {a.reps} replications a null")

    cal, cal_sha, cal_src = read_calendar(a.days)
    calf = work / "judged_sessions.csv"
    pd.DataFrame({"date": cal}).to_csv(calf, index=False)
    _log(f"judged sessions: {len(cal)}, {cal[0]} to {cal[-1]}, sha256 of the dates joined by LF {cal_sha}")

    pairs = Path(a.pairs) if a.pairs is not None else work / "pairs"
    if a.pairs is None:
        _step("pairs", ["scripts/q16_p16_pairs.py", "--out", str(pairs)])
    pq = pairs / "p16_pairs.parquet"
    pairs_meta = json.loads((pairs / "p16_pairs.json").read_text(encoding="utf-8"))
    for part in PARTS:
        _step(part, [SCRIPT, "--compute", part, "--work", str(work), "--calendar", str(calf), "--reps", str(a.reps)]
              + ([] if part == "ii_syn" else ["--pairs-file", str(pq)]))

    frames, metas = {}, {}
    for part in PARTS:
        frames[part] = pd.read_csv(work / part / "size.csv", low_memory=False, float_precision="round_trip")
        metas[part] = json.loads((work / part / "meta.json").read_text(encoding="utf-8"))
        if metas[part]["calendar_sha256"] != cal_sha:
            print(f"REFUSED: part {part} ran on another calendar", flush=True)
            return 3
        if part != "ii_syn" and metas[part]["pairs_sha256"] != pairs_meta.get("parquet_sha256"):
            print(f"REFUSED: part {part} ran on other pairs", flush=True)
            return 3
    size_i = pd.concat([frames["i_lift"], frames["i_two"]], ignore_index=True)
    cp = pd.concat([frames["ii_real"], frames["ii_syn"]], ignore_index=True)
    crit = criterion(pd.concat([size_i, cp], ignore_index=True))
    verd = verdicts(crit)
    checked = sum(m["scalar_checked"] for m in metas.values())
    mism = sum(m["scalar_mismatched"] for m in metas.values())
    _log(f"scalar re-decision: {checked} decisions checked against lift_bound's scalar functions, {mism} mismatched"
         + (" -- DIFFERS" if mism else ""))

    _log(f"read ledger: {XR.note_ledger_appends()}")             # Q-97's shared helper (the writer repeats it)
    blobs = {rel: blob_id(ROOT / rel) for rel in ("extended/lift_bound.py", "extended/count_nulls.py",
                                                  "scripts/q16_calibrate.py", SCRIPT, "scripts/q16_p16_pairs.py")}
    common = {
        "decision": DECISION, "task": "Q-82 built it; Q-83 runs it", "argv": sys.argv[1:], "reps": a.reps,
        "batch_i": BATCH, "batch_ii": BATCH_II, "levels": list(LEVELS),
        "family_levels": {str(k): LB.family_level(k) for k in LB.K_RANGE}, "statistic": STAT,
        "members": list(MEMBERS), "df_rule": DF_RULE, "n_sessions": len(cal), "calendar_sha256": cal_sha,
        "calendar_source": cal_src, "pairs_supplied": a.pairs is not None, "days_supplied": a.days is not None,
        "pairs_sha256": pairs_meta.get("parquet_sha256"), "trades_sha256": pairs_meta.get("trades_sha256"),
        "pairs_identity": pairs_meta.get("identity"), "blobs": blobs, "versions": _versions(),
        "read": {"purpose": "registered_design", "declaration": READ_ROW, "design": READ_DESIGN,
                 "files": [DAYS_REL, "vendor/stage2/data/atlas/A1/events.parquet",
                           "vendor/stage2/data/bars/NQ/bars.parquet"],
                 "by": {"calendar": SCRIPT, "pairs": "scripts/q16_p16_pairs.py"}},
        "seed_map": {k: int(v) for k, v in SEEDS.items()}, "spare_seeds": list(SPARE), "seed_block": list(SEED_BLOCK),
        "seed_check": "unused outside this item's files; documents' mentions: " + ("; ".join(seed_notes) or "none"),
        "scalar_redecision": {"checked": checked, "mismatched": mism},
        "parts": {k: {x: m.get(x) for x in ("nulls", "seconds", "peak_working_set_mb", "scalar_checked",
                                            "scalar_mismatched", "batch")} for k, m in metas.items()},
        "criterion": "E-052: at every k in 11..15 no real or realistic null's 95 % interval lies wholly above nominal; "
                     "(ii) beside, never folded in"}
    notes = {"why": "E-052 (M2): Q-55 replays Q-16's replications; this run draws the same constructions afresh",
             "criterion_fixed": "in E-052, before the run",
             "beside": "the count-persistent tables are reported beside; F-02's K0 addresses them"}
    seeds_of = {"q82_validation_one_sample": ("lift_real", "lift_syn"), "q82_validation_two_sample": ("selection", "c1p"),
                "q82_count_persistent": ("count_real_one", "count_real_two", "count_syn")}
    out = {
        "q82_validation_one_sample": (frames["i_lift"], SEEDS["lift_real"],
                                      "Q-82 (E-052) (i): cons and its members on Q-16's 70 real lift nulls (P-16's "
                                      "pairs, sign-flipped) and 25 realistic synthetic nulls, drawn on fresh seeds"),
        "q82_validation_two_sample": (frames["i_two"], SEEDS["selection"],
                                      "Q-82 (E-052) (i): the treated two-sample cons on Q-16's 55 placebo-selection "
                                      "and 56 C1' nulls on P-16's judged offers, drawn on fresh seeds"),
        "q82_count_persistent": (cp, SEEDS["count_real_one"],
                                 "Q-82 (E-052) (ii), beside the criterion: cons and the two-sample cons on "
                                 "count-persistent nulls (P-16's offers thinned at a persistent outcome-independent "
                                 "rate; the red team's synthetic ones)"),
        "q82_criterion": (crit, None,
                          "Q-82 (E-052): the criterion per statistic and k from the (i) tables' counts (section "
                          "criterion, with HOLDS / FAILS / NOT CHECKED) and (ii)'s summary (section beside, no "
                          "verdict); no randomness of its own -- computed from the tables beside"),
        "q82_judged_sessions": (pd.DataFrame({"ordinal": range(len(cal)), "date": cal}), None,
                                "Q-82 (E-052): the judged block's session list as the calibration uses it (A1's "
                                "stored days 2024-01-02..2026-07-16); no randomness"),
    }
    params = {}
    for nm in out:
        if nm in seeds_of:
            s = {k: int(SEEDS[k]) for k in seeds_of[nm]}
        elif nm == "q82_criterion":
            s = {k: int(SEEDS[k]) for k in ("lift_real", "lift_syn", "selection", "c1p", "count_real_one",
                                             "count_real_two", "count_syn")}
        else:
            s = {}
        params[nm] = {**common, "seeds": s}
    params["q82_judged_sessions"].update({"count": len(cal), "first": cal[0], "last": cal[-1],
                                          "sha256_dates_joined_lf": cal_sha,
                                          "joined": "ISO dates joined by a single LF, no trailing newline"})
    for nm, (df, seed, desc) in out.items():                     # every frame is built before the first write
        csv, man = XR.write_result(df, nm, script=SCRIPT, seed=seed, parameters=params[nm], results_dir=target,
                                   description=desc, exploratory=False, notes=notes, require_seed=seed is not None)
        _log(f"wrote {csv} ({len(df)} rows) and {man.name}")
    for fn, v in verd.items():
        print(f"criterion (E-052) {fn}: {v} -- {STAT_LABELS[fn]}", flush=True)
    _log(f"EXIT 0 ({time.time() - t0:.0f} s)")
    print("EXIT 0", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
