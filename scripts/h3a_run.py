"""H3-A: the three-way test's design checks (`prereg/H3_three_way.md` sections 8, 10, 11, 15-17; E-279, E-285, E-295).

Runs one declared H3-A slot at a time from a clean checkout of ONE named commit under `run.lock` (`OMP_NUM_THREADS`
1, refused above 2; at most 2 workers; the lock reserves the declared memory cap, 2.5 GB in all -- Appendix A's
`memory: cap 2.5 GB over 2 workers` -- the parent process counted inside it). Every line names the same `<sha>`
twice: `run_clean.py` checks it out, and the runner refuses at its start unless HEAD is that commit and every H3-A
output already in `results/` was written from it (`check_commit`; the red team's c2 m-6):

    python scripts/run_clean.py --name h3a-a1   --commit <sha> --hours 7.5 --mem-gb 2.5 --task Q-187 -- python scripts/h3a_run.py --part A1   --workers 2 --commit <sha>
    python scripts/run_clean.py --name h3a-a2   --commit <sha> --hours 5.5 --mem-gb 2.5 --task Q-187 -- python scripts/h3a_run.py --part A2   --workers 2 --commit <sha>
    python scripts/run_clean.py --name h3a-a4-1 --commit <sha> --hours 5.5 --mem-gb 2.5 --task Q-187 -- python scripts/h3a_run.py --part A4_1 --workers 2 --commit <sha>
    python scripts/run_clean.py --name h3a-a4-2 --commit <sha> --hours 5.5 --mem-gb 2.5 --task Q-187 -- python scripts/h3a_run.py --part A4_2 --workers 2 --commit <sha>
    python scripts/run_clean.py --name h3a-rep  --commit <sha> -- python scripts/h3a_run.py --part report    --commit <sha>  (A1 + A2: the stop)
    python scripts/run_clean.py --name h3a-rep4 --commit <sha> -- python scripts/h3a_run.py --part report_a4 --commit <sha>  (A4's 426 + 60)

**Refuses before any draw** unless the commit check holds (`check_commit`), `OMP_NUM_THREADS` is set and at most 2
(`check_threads`), `extended.h3a_report.assert_h3_preconditions(ROOT, check_build_commit=True)` holds (H3 pinned at
E-279, template v3 pinned at E-284 with matching R-10 clauses, all 9 build files unchanged since `4c07026`), the
checkout is clean (`S2X_CLEAN_RUN`), `run.lock` is held by this job (compute parts), no output of the slot exists,
`--workers` is 1 or 2, and the slot's projected memory -- the parent and each worker -- is inside the declared cap
(`project_worker_mb`, `TOTAL_CAP_MB`; B-7, c2 m-5).

**Seeds (B-3).** Every per-history worker takes its seed **roles** and its part id as arguments (`HistoryTask`); only
`main()` passes H3-A's declared roles (`h3a_histories`, `h3a_coins`) with their declared parts, and the workers refuse
those roles outside a clean run, at another part's id, and any role not the part's (`check_seed_use`). The tests pass
the tests' role in the tests' part. No seed value appears here; every seed is issued by role through
`extended.three_way_seeds.issue`.

**Memory (B-7, c2 m-5).** A start's `Records` is reduced to its per-unit values as soon as it is made (`unit_values`),
so no start's `rel` or arrival lists outlive it; each worker reads its peak working set after every start and every
close of the exact program and refuses above the declared cap a worker (`WORKER_CAP_MB`); the parent refuses when its
own peak plus the workers' exceeds the cap in all (`TOTAL_CAP_MB`); every record and manifest carries the peaks.

**Records written as they arrive (B-1, m-8; c2 m-4).** Each history's counts and premise table are written (`sink`)
the moment its worker returns, before the next is awaited; a premise failure, a key-guard or range refusal, a refused
term inside a worker (`BoundRefused`) or a memory breach inside a worker is returned as a refused record, and the part
writes that history's record and its premise table first and then refuses -- so a late failure loses nothing.

**The premises (section 11; the lead's rulings E-295 (d), (e)).** Deciding: centring of every counted per-seed pool;
centring of the counted per-set pools of the clipped toy composite in A1 and of both composites in A2 (P_B's per-set
pool in A1 is printed beside: the sets partition the seeds and P_B's clip never binds, so it tests the per-seed
pool's mean again); the disjoint pool's variance tolerance; the twin's symmetry (a sign test at `CENTRING_Z`); the
twin's uniforms, every one exactly 1 minus the base's on the guard's sampled keys, bit for bit (`check_twin_uniforms`);
a key-guard refusal; a term out of range. Beside, deciding nothing: the disjoint pool's symmetry and each per-seed
pool's lag-1 autocorrelation in seed order (the note's 2.6 "no serial dependence", not in section 11's kill list).

**A4 at J' (E-295 (a), a reading).** One draw is `A4_DRAW_J = J_PRIME` seeds (Appendix C's), read from the
declaration's l.143 ("H3-A's size tests take Appendix C's `J_PRIME`") and the note's l.693 ("a pool of at least a
hundred times J", with `SEEDS` a history); its manifest and report print beside the MDLs that they hold at J = J'
only. P1's and P4's null is the disjoint same-design null of A4's base arm (2.3 (b)), and in H3-A, with no time
condition, P4 is P1 at the size d mean(1 + a rho_t) (printed beside P4's rates and MDLs).

**What is not run here, and why:**
- **The smaller-J report** (section 7's row "the smaller-J rule's inputs", prereg l.145) is **not run in H3-A**: its
  delta is undeclared -- the declaration's l.132 "delta\\* ... H3-A uses none (its plants' grid is Appendix C's)", the
  note's l.783 only "at placeholder values of delta" -- and so is its level (l.145 names a grid, draws, a model and a
  key, no alpha). It belongs to H3-D's text (E-290); `three_way_h3a.smaller_j_rng` stays unused.
- **The stress** (section 8, l.185: "3 arms ... x 5 schedules ... = 15 runs") is **deferred to H3-D's text (E-295
  (c))**: it decides nothing and no size is declared. `run_stress` builds it (tested at 15 runs); A1 does not run it
  and its manifest says so.
- **A3** (the history null) is **deferred to H3-D's text (E-295 (b))**: "the test's J" and the time conditions (the
  note's l.547, l.549) are H3-D's inputs. Its 6 rates move there, and A3's role seed stays drawn by nothing until
  then; the A3 slots and A3's report refuse (`check_rulings`). The code (`a3_history`, `run_a3_slice`) is kept for
  H3-D's text to declare.
- **The copy-against-stagger check**: 0 until the template defines overlap (section 11).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
import math
import os
import sys
import time
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import norm as _norm  # noqa: E402

from extended import CLEAN_RUN_ENV, RESULTS_DIR  # noqa: E402
from extended import family_stats as FS  # noqa: E402
from extended import h3a_report as REP  # noqa: E402
from extended import lock_guard as LG  # noqa: E402
from extended import procmem  # noqa: E402
from extended import three_way_fastkeys as F  # noqa: E402
from extended import three_way_h3a as H  # noqa: E402
from extended import three_way_journey as J  # noqa: E402
from extended import three_way_keys as K  # noqa: E402
from extended import three_way_runner as R  # noqa: E402
from extended import three_way_s1 as S1  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402
from extended import three_way_stats as ST  # noqa: E402

SCRIPT = "scripts/h3a_run.py"


def _arith():
    spec = importlib.util.spec_from_file_location(
        "three_way_arith_for_h3a_run", ROOT / "docs" / "plans" / "scripts" / "three_way" / "three_way_arith.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_A = _arith()
#: the declared workers and memory cap (Appendix A: "memory: cap 2.5 GB over 2 workers"; `three_way_arith`)
MAX_WORKERS: int = int(_A.WORKERS)
WORKER_CAP_MB: float = float(_A.MEM_CAP_GB) * 1e9 / int(_A.WORKERS) / 2 ** 20

#: the cap in all, the parent process counted inside it (the note's 6.2: "under 2.5 GB in all"; c2 m-5)
TOTAL_CAP_MB: float = float(_A.MEM_CAP_GB) * 1e9 / 2 ** 20
#: the most BLAS threads a process may run (CLAUDE.md; c2 m-7)
MAX_THREADS = 2

#: A3 is deferred to H3-D's text (E-295 (b)): None refuses its slots and its report
A3_TEST_J: int | None = None
A3_TIME_CONDITIONS: str | None = None
A3_N_MIN: int | None = None
#: A4's seeds a draw: Appendix C's J' (E-295 (a), a reading of l.143 and the note's l.693)
A4_DRAW_J: int = H.J_PRIME
STRESS_NOTE = "not run: deferred to H3-D's text (E-295 (c)): it decides nothing and no size is declared"
A3_NOTE = "deferred to H3-D (E-295): A3's test's J and time conditions are H3-D's inputs; its 6 rates move there"

#: E-285 declared H3-A slot splits (histories range, seed count M)
SLOT_SPEC: dict[str, dict[str, Any]] = {
    "A1": {"part": "A1", "histories": (0, 20), "M": H.SEEDS, "out": "h3a_a1"},
    "A2": {"part": "A2", "histories": (0, 20), "M": H.SEEDS, "out": "h3a_a2"},
    "A3_1": {"part": "A3", "histories": (0, 100), "M": 2000, "out": "h3a_a3_1"},
    "A3_2": {"part": "A3", "histories": (100, 200), "M": 2000, "out": "h3a_a3_2"},
    "A4_1": {"part": "A4", "histories": (0, 5), "M": H.SEEDS, "out": "h3a_a4_1"},
    "A4_2": {"part": "A4", "histories": (5, 10), "M": H.SEEDS, "out": "h3a_a4_2"},
    "report": {"part": "report", "out": "h3a_summary"},
    "report_a3": {"part": "report", "out": "h3a_a3_summary"},
    "report_a4": {"part": "report", "out": "h3a_a4_rates"},
}
#: each part's declared seed roles (section 15's table)
#: (A3's role, `h3a3_history_null`, is drawn by nothing until H3-D's text: E-295 (b))
PART_ROLES: dict[str, tuple[str, ...]] = {"A1": ("h3a_histories", "h3a_coins"), "A2": ("h3a_histories", "h3a_coins"),
                                          "A3": (), "A4": ("h3a_histories", "h3a_coins")}
DIM_NAMES: tuple[str, ...] = ("P_B", "paid_by_63", "sessions_saved_to_payout")
#: A3's per-history files hold this many consecutive histories each (A1, A2 and A4 write one a history)
A3_BLOCK = 10


class MemoryRefused(RuntimeError):
    """A worker's measured (or a slot's projected) memory is above the declared cap a worker."""


# ----------------------------------------------------------------------------------------- seeds (B-3)


def check_seed_use(part: str, part_id: int, roles: Sequence[str]) -> None:
    """B-3: the tests' role only in the tests' part; H3-A's declared roles only in their own part, and only inside a
    clean run (`S2X_CLEAN_RUN` set); any other role refused. Checked before any draw."""
    for role in roles:
        if role == "tests":
            if int(part_id) != S.PARTS["tests"]:
                raise S.ProvenanceRefused("REFUSED (B-3): the tests' seed draws only in the tests' part")
        elif role in PART_ROLES.get(part, ()):
            if int(part_id) != S.PARTS[part]:
                raise S.ProvenanceRefused(f"REFUSED (B-3): {role} draws in part {part} only")
            if not os.environ.get(CLEAN_RUN_ENV):
                raise S.ProvenanceRefused(f"REFUSED (B-3): H3-A's declared seed {role} draws only in a clean run "
                                          f"({CLEAN_RUN_ENV} unset): a test uses the tests' seed")
        else:
            raise S.ProvenanceRefused(f"REFUSED (B-3): {role!r} is not a seed role of part {part}")


# ----------------------------------------------------------------------------------------- per-unit values (B-7)


class MemoryGuard:
    """Reads this process's peak working set and refuses above the cap (B-7)."""

    def __init__(self, cap_mb: float):
        self.cap_mb = float(cap_mb)

    def peak(self) -> float:
        return float(procmem.working_set_mb(peak=True))

    def check(self) -> None:
        p = self.peak()
        if math.isfinite(p) and p > self.cap_mb:
            raise MemoryRefused(f"REFUSED (B-7): a worker's peak working set {p:.0f} MB is above the declared cap "
                                f"{self.cap_mb:.0f} MB a worker")


def unit_values(schedule: J.Schedule, rules: J.ToyRules, plan: R.Plan, arm: J.ArmSpec, guard: K.KeyGuard | None,
                on_start: Callable[[], None] | None = None) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """The toy composite's per-unit values x[s, c] for every start and seed of the plan -- `P_B` (`three_way_runner.p_b`),
    `paid_by_63` (an indicator: a first payout by the horizon) and `sessions_saved_to_payout` (W + 1 less the
    censored sessions to the first payout, `three_way_journey.days_to_first_payout`) -- and the failures at the fill;
    each start simulated exactly as `three_way_runner.run` does and reduced at once, so its `Records` is dropped before
    the next start (B-7)."""
    n_s, n_c, h = len(plan.starts), len(plan.seed_indices), int(plan.horizon)
    X = {k: np.empty((n_s, n_c)) for k in DIM_NAMES}
    ff = np.empty((n_s, n_c))
    for i, s in enumerate(plan.starts):
        rec = J.simulate(schedule, rules, s, plan.seed_indices, h, seed=plan.seed, part=plan.part,
                         history=plan.history, block_sessions=plan.block_sessions, arm=arm, budget=plan.budget,
                         guard=guard)
        X["P_B"][i] = R.p_b(rec)
        fp = rec.first_pay
        X["paid_by_63"][i] = ((fp > 0) & (fp <= h)).astype(float)
        X["sessions_saved_to_payout"][i] = float(h + 1) - J.days_to_first_payout(rec, h)
        ff[i] = np.asarray(rec.fill_failures, float)
        del rec
        if on_start is not None:
            on_start()
    return X, ff


def fill_summary(ff: np.ndarray) -> dict[str, float]:
    """`three_way_runner.fill_failures`' three readings on a matrix of failures at the fill (m-6: for every arm)."""
    f = np.asarray(ff, float).ravel()
    return {"fill_failures_per_unit": float(f.mean()) if f.size else 0.0,
            "share_of_units_with_one": float((f > 0).mean()) if f.size else 0.0, "fill_failures": float(f.sum())}


def check_twin_uniforms(guards: Sequence[K.KeyGuard], seed: S.RoleSeed, n: int = J.WALK_CHUNK,
                        twin_read: Callable[[np.ndarray, int], np.ndarray] | None = None) -> dict:
    """E-295 (d): the twin is the complement of every uniform -- on every coin and enforce key the guards stored (their
    declared sample, the run's own keys), the first `n` uniforms the journey's reader gives the twin
    (`three_way_fastkeys.uniforms(..., twin=True)`, or `twin_read`, a test's planted reader) equal 1 minus the base's,
    bit for bit. Deciding: one mismatch kills the part. Returns the premise's result (`ok`, the keys read, the
    mismatches)."""
    read = twin_read if twin_read is not None else (lambda M, k: F.uniforms(M, k, True))
    keys = sorted({k for g in guards for k in g.keys()})
    names_of = {K.KEY_KINDS[kind][0]: (kind, K.KEY_KINDS[kind][1]) for kind in K.UNIT_KINDS}
    n_keys, bad = 0, 0
    rows: dict[int, list] = {}
    for k in keys:
        if int(k[1]) not in names_of:
            continue
        if int(k[0]) != int(seed):
            bad += 1
            continue
        rows.setdefault(int(k[1]), []).append([int(x) for x in k[2:]])
    for tag, rs in rows.items():                            # one key matrix a kind: every sampled key at once
        kind, names = names_of[tag]
        cols = np.asarray(rs, dtype=np.int64)
        M = F.key_matrix(seed, kind, **{nm: cols[:, i] for i, nm in enumerate(names)})
        base = F.uniforms(M, n, False)
        tw = np.asarray(read(M, n), dtype=np.float64)
        n_keys += len(rs)
        if tw.shape != base.shape:
            bad += len(rs)
            continue
        bad += int((tw.view(np.uint64) != (1.0 - base).view(np.uint64)).any(axis=1).sum())
    return {"ok": bool(n_keys > 0 and bad == 0), "n": n_keys, "mismatches": bad, "abs_z": float(bad)}


def _cols(X: Mapping[str, np.ndarray], lo: int, hi: int) -> dict[str, np.ndarray]:
    return {k: v[:, lo:hi] for k, v in X.items()}


# ----------------------------------------------------------------------------------------- the exact program (B-2)


def _merge_paid(L: J.Lanes, rules: J.ToyRules, budget: float | None) -> J.Lanes:
    """`three_way_journey._merge` with one more column in the state key: whether the first payout has arrived
    (`first_pay > 0`). The build's key (`three_way_journey._state_key`, a build file, unedited) holds every field the
    future reads but not that one, so its merge joins states with and without a payout and keeps one's `first_pay`
    (the red team's B-2 (b)). With the bit in the key, two states merged here have identical futures in every field
    the toy composite reads (the journey reads `first_pay` only as `first_pay < 0`, `_close_cash`), so the program
    stays exact for the first payout's law; the failures at the fill are carried as `_merge` carries them."""
    if len(L) <= 1:
        return L
    M = np.column_stack([J._state_key(L, rules, budget), (np.asarray(L.first_pay) > 0).astype(float)])
    _, first, inv = np.unique(M, axis=0, return_index=True, return_inverse=True)
    w = np.zeros(len(first))
    np.add.at(w, inv.ravel(), L.w)
    wf = np.zeros(len(first))
    np.add.at(wf, inv.ravel(), L.w * np.asarray(L.ffail, float))
    out = L.take(first)
    out.w = w
    out.ffail = np.where(w > 0, wf / np.where(w > 0, w, 1.0), 0.0)
    return out


def exact_moments(schedule: J.Schedule, rules: J.ToyRules, start: int, horizon: int, *, block_sessions: int,
                  budget: float | None, arm: J.ArmSpec = J.ArmSpec(), merge: Callable | None = None,
                  on_step: Callable[[], None] | None = None) -> dict[str, float]:
    """One start's exact expectations of the toy composite's per-unit values (the note's 2.4): the forward program of
    `three_way_journey.expect` (its `_session` step, unedited) with the merge `_merge_paid`, reading the probability of
    the first payout at each close k as the mass whose `first_pay` became k at that close, before the merge. Returns
    E[P_B's value], P(paid by h) (the indicator's probability), E[sessions saved] = sum over k of P(first payout at
    k) (h + 1 - k), and the total probability. `merge` replaces the merge (a test's control only)."""
    J.check_window(start, horizon, block_sessions)
    J.check_costs(schedule, rules, arm)
    mg = _merge_paid if merge is None else merge
    L = J.fresh(1, rules)
    pay = np.zeros(horizon + 1)
    for k in range(1, horizon + 1):
        L = J._session(L, schedule.by_session.get(start + k - 1, ()), k, rules, arm, budget, None, dp=True)
        L.day = L.dead = L.stopped = None
        pay[k] = float(L.w[np.asarray(L.first_pay) == k].sum())
        L = mg(L, rules, budget)
        if on_step is not None:
            on_step()
    tot = float(L.w.sum())
    paid = float(pay.sum())
    if abs(tot - 1.0) > 1e-9:
        raise REP.H3ReportRefused(f"the exact program's total probability is {tot}, not 1, at start {start}")
    if merge is None and abs(float(L.w[np.asarray(L.first_pay) > 0].sum()) - paid) > 1e-9:
        raise REP.H3ReportRefused(f"the exact program's paid mass disagrees with its first-payout law at start {start}")
    saved = float(sum(pay[k] * (horizon + 1 - k) for k in range(1, horizon + 1)))
    return {"P_B": float((L.w * L.ahead).sum() / 3.0), "paid_by_63": paid, "sessions_saved_to_payout": saved,
            "total": tot}


def exact_arm(schedule: J.Schedule, rules: J.ToyRules, plan: R.Plan,
              on_step: Callable[[], None] | None = None) -> dict[str, np.ndarray]:
    """Each start's exact moments for one arm (`exact_moments`), as arrays over the plan's starts; `on_step` (the
    memory guard) after every close, since the program's states are memory too."""
    rows = [exact_moments(schedule, rules, s, plan.horizon, block_sessions=plan.block_sessions, budget=plan.budget,
                          on_step=on_step) for s in plan.starts]
    return {k: np.array([r[k] for r in rows]) for k in DIM_NAMES}


# ----------------------------------------------------------------------------------------- the tasks


@dataclass(frozen=True)
class HistoryTask:
    """One history of one part: its seed roles and part id (B-3), its sizes, and its inputs."""
    part: str
    part_id: int
    roles: tuple[str, ...]
    history: int
    M: int
    starts: tuple[int, ...]
    horizon: int
    j: int
    disjoint: tuple[tuple[int, int], tuple[int, int]]
    s1_params: S1.S1Params
    rules: J.ToyRules
    cap_mb: float
    twin_arm: J.ArmSpec = J.ArmSpec(twin=True)
    time_conditions: str | None = None
    n_min: int | None = None
    shortcut: tuple[int, ...] = ()


def _caught(exc: BaseException) -> bool:
    """A refusal inside a worker that the part records before stopping (m-8; c2 m-4): a memory breach, a term out of
    range (`BoundRefused`, whatever its message), a report refusal, a key-guard refusal."""
    if isinstance(exc, (MemoryRefused, ST.BoundRefused, REP.H3ReportRefused)):
        return True
    return isinstance(exc, ValueError) and str(exc).startswith("REFUSED")


def _refusal_kind(exc: BaseException) -> str:
    if isinstance(exc, MemoryRefused):
        return "memory"
    if isinstance(exc, ST.BoundRefused):
        return "term_out_of_range"
    msg = str(exc)
    if "(2.3)" in msg or "(N-2)" in msg:
        return "key_guard"
    return "refusal"


def _premise(task: HistoryTask, null_class: str, comp: str, pool: str, check: str, decides: bool, res: dict | None,
             detail: str = "") -> dict:
    return {"part": task.part, "history": task.history, "null_class": null_class, "composite": comp, "pool": pool,
            "check": check, "decides": bool(decides), "ok": bool(res["ok"]) if res is not None else False,
            "abs_z": float(res.get("abs_z", float("nan"))) if res is not None else float("nan"),
            "n": int(res.get("n", res.get("n_nonzero", 0))) if res is not None else 0,
            "stat": float(res.get("stat", float("nan"))) if res is not None else float("nan"), "detail": detail}


def _serial_beside(task: HistoryTask, null_class: str, comp: str, pool) -> dict:
    """c2 m-10: a per-seed pool's lag-1 autocorrelation in seed order, beside the 2.6 premises, deciding nothing."""
    r = REP.lag1_autocorrelation(pool)
    return _premise(task, null_class, comp, "seed", "serial_lag1_beside", False, {"ok": True, "stat": r,
                                                                                  "n": int(np.size(pool))})


def _guarded(task: HistoryTask, null_class: str, comp: str, pool: str, check: str, decides: bool,
             fn: Callable[[], dict]) -> dict:
    """A premise check as a record: a refusal of the pool (all zero, zero variance, outside the variance tolerance)
    is a failed premise, recorded, never an exception (m-8)."""
    try:
        return _premise(task, null_class, comp, pool, check, decides, fn())
    except REP.H3ReportRefused as exc:
        return _premise(task, null_class, comp, pool, check, decides, None, str(exc))


def _plan(task: HistoryTask, seed: S.RoleSeed, lo: int, hi: int) -> R.Plan:
    return R.Plan(seed=seed, part=task.part_id, history=task.history, starts=task.starts, seed_indices=range(lo, hi),
                  horizon=task.horizon, block_sessions=task.s1_params.n_sessions, budget=H.BUDGET)


def check_disjoint_sets(disjoint, M: int) -> None:
    """m-3: the disjoint null's two seed-index sets checked exactly -- two equal halves, sharing no index, together
    every index 0 .. M - 1."""
    (a0, a1), (b0, b1) = disjoint
    s1, s2 = set(range(a0, a1)), set(range(b0, b1))
    if s1 & s2 or s1 | s2 != set(range(int(M))) or len(s1) != len(s2):
        raise REP.H3ReportRefused(f"REFUSED (2.3 (b)): the disjoint sets {disjoint} are not two equal, disjoint halves "
                                  f"of the {M} seed indices")


def _base(task: HistoryTask) -> dict:
    return {"part": task.part, "history": task.history, "rows": [], "premise": [], "fill": {}, "beside": {},
            "refused": False}


def _finish(rec: dict, guard: MemoryGuard) -> dict:
    rec["mem_peak_mb"] = guard.peak()
    rec["refused"] = rec["refused"] or any(p["decides"] and not p["ok"] for p in rec["premise"])
    return rec


def a1_history(task: HistoryTask) -> dict:
    """A1 on one history: A1's design on its S1 history, its base arm and its antithetic twin, each on the two
    `DISJOINT` seed sets with one sampled key guard a set (m-3: the run's own keys at both sets' first 64 seed
    indices; the guards' states disjoint), so the antithetic pool pairs every seed's base with its twin and the
    disjoint pool pairs the first set's seeds with the second's. The counts (36) and the premises: centring on every
    counted pool (per seed and per set, both classes and composites), the twin's symmetry (`check_symmetry`, deciding),
    the disjoint pool's variance tolerance; a key-guard or range refusal is a failed premise, recorded."""
    mem = MemoryGuard(task.cap_mb)
    check_seed_use(task.part, task.part_id, task.roles)
    rec = _base(task)
    check_disjoint_sets(task.disjoint, task.M)
    h_seed, c_seed = (S.issue(r) for r in task.roles)
    hist = S1.generate(h_seed, task.part_id, task.history, task.s1_params)
    sched = S1.schedule(H.A1_DESIGN, hist)
    plans = [_plan(task, c_seed, lo, hi) for lo, hi in task.disjoint]
    guards = [K.KeyGuard.sampled(p.starts, p.seed_indices) for p in plans]
    try:
        base = [unit_values(sched, task.rules, p, J.ArmSpec(), g, mem.check) for p, g in zip(plans, guards)]
        twin = [unit_values(sched, task.rules, p, task.twin_arm, g, mem.check) for p, g in zip(plans, guards)]
        K.disjoint(*guards)
        Xb = {k: np.hstack([base[0][0][k], base[1][0][k]]) for k in DIM_NAMES}
        Xt = {k: np.hstack([twin[0][0][k], twin[1][0][k]]) for k in DIM_NAMES}
        anti, anti_pools = REP.size_counts(Xb, Xt, task.starts, j_prime=task.j)
        disj, disj_pools = REP.size_counts(base[0][0], base[1][0], task.starts, j_prime=task.j)
    except Exception as exc:                                # noqa: BLE001 -- only the recorded refusals (_caught)
        if not _caught(exc):
            raise
        rec["premise"].append(_premise(task, "run", "all", "run", _refusal_kind(exc), True, None, str(exc)))
        return _finish(rec, mem)
    rec["rows"] = REP.counts_to_rows("A1", "antithetic", task.history, anti) + \
        REP.counts_to_rows("A1", "disjoint", task.history, disj)
    rec["premise"].append(_premise(task, "antithetic", "all", "sample", "twin_uniforms", True,
                                   check_twin_uniforms(guards, c_seed)))
    for comp in REP.COMPOSITES:
        dims = REP.composite_dims(comp)
        set_decides = comp == "toy_composite"               # E-295 (e): P_B's per-set centring is beside
        for pool, dec in (("seed", True), ("set", set_decides)):
            rec["premise"].append(_guarded(task, "antithetic", comp, pool, "centring" if dec else "centring_beside",
                                           dec, lambda: REP.check_null_pool(anti_pools[comp][pool])))
        rec["premise"].append(_guarded(task, "antithetic", comp, "seed", "symmetry", True,
                                       lambda: REP.check_symmetry(anti_pools[comp]["seed"])))
        single = float(REP.composite_per_seed(base[0][0], dims).var(ddof=1))
        rec["premise"].append(_guarded(task, "disjoint", comp, "seed", "centring_and_variance", True,
                                       lambda: REP.check_null_pool(disj_pools[comp]["seed"], single_arm_var=single)))
        rec["premise"].append(_guarded(task, "disjoint", comp, "set", "centring" if set_decides else
                                       "centring_beside", set_decides,
                                       lambda: REP.check_null_pool(disj_pools[comp]["set"])))
        rec["premise"].append(_guarded(task, "disjoint", comp, "seed", "symmetry_beside", False,
                                       lambda: REP.check_symmetry(disj_pools[comp]["seed"])))
        rec["premise"].append(_serial_beside(task, "antithetic", comp, anti_pools[comp]["seed"]))
        rec["premise"].append(_serial_beside(task, "disjoint", comp, disj_pools[comp]["seed"]))
        rec["beside"][f"at_cap_share_{comp}"] = {"antithetic": anti_pools[comp]["at_cap"],
                                                 "disjoint": disj_pools[comp]["at_cap"]}
        rec["beside"][f"sd_per_seed_{comp}"] = {"antithetic": float(anti_pools[comp]["seed"].std(ddof=1)),
                                                "disjoint": float(disj_pools[comp]["seed"].std(ddof=1))}
    rec["fill"] = {"base": fill_summary(np.hstack([base[0][1], base[1][1]])),
                   "twin": fill_summary(np.hstack([twin[0][1], twin[1][1]]))}
    rec["beside"]["key_guard_checked"] = int(sum(g.checked for g in guards))
    return _finish(rec, mem)


def a2_history(task: HistoryTask) -> dict:
    """A2 on one history: A2's pair on its S1 history (`S1_PARAMS_EXACT`, `TOY_RULES_EXACT`), both arms on one coin
    field; each start's exact moments for both arms (`exact_arm`), P_B's centre from `three_way_runner.exact_centres`
    (the build's exact program) and held equal to this program's; the clipped composite's centre exactly
    (`h3a_report.exact_composite_centre`) at a set of J' seeds (the 2.2 (a) bound's estimate) and at one seed (the
    2.2 (b) bounds' replicate); a rejection is the lower limit above its centre (`size_counts`), and the centring
    premise reads the counted pools."""
    mem = MemoryGuard(task.cap_mb)
    check_seed_use(task.part, task.part_id, task.roles)
    rec = _base(task)
    h_seed, c_seed = (S.issue(r) for r in task.roles)
    hist = S1.generate(h_seed, task.part_id, task.history, task.s1_params)
    f_sch, b_sch = (S1.schedule(spec, hist) for spec in H.A2_PAIR)
    plan = _plan(task, c_seed, 0, task.M)
    guard = K.KeyGuard.sampled(plan.starts, plan.seed_indices)
    try:
        Xf, fff = unit_values(f_sch, task.rules, plan, J.ArmSpec(), guard, mem.check)
        Xb, ffb = unit_values(b_sch, task.rules, plan, J.ArmSpec(), guard, mem.check)
        ef, eb = exact_arm(f_sch, task.rules, plan, mem.check), exact_arm(b_sch, task.rules, plan, mem.check)
        theta_pb_t = R.exact_centres(f_sch, b_sch, task.rules, plan)
        if np.max(np.abs(theta_pb_t - (ef["P_B"] - eb["P_B"]))) > 1e-9:
            raise REP.H3ReportRefused("the first-payout program's P_B disagrees with three_way_runner.exact_centres")
        toy = tuple(H.TOY_COMPOSITE)
        centres = {"p_b": {"set": float(theta_pb_t.mean()), "seed": float(theta_pb_t.mean())},
                   "toy_composite": {"set": REP.exact_composite_centre(toy, ef, eb, task.j),
                                     "seed": REP.exact_composite_centre(toy, ef, eb, 1)}}
        counts, pools = REP.size_counts(Xf, Xb, task.starts, j_prime=task.j, centres=centres)
    except Exception as exc:                                # noqa: BLE001 -- only the recorded refusals (_caught)
        if not _caught(exc):
            raise
        rec["premise"].append(_premise(task, "run", "all", "run", _refusal_kind(exc), True, None, str(exc)))
        return _finish(rec, mem)
    rec["rows"] = REP.counts_to_rows("A2", "exact_centred", task.history, counts)
    for comp in REP.COMPOSITES:
        for pool in ("seed", "set"):
            rec["premise"].append(_guarded(task, "exact_centred", comp, pool, "centring", True,
                                           lambda: REP.check_null_pool(pools[comp][pool])))
        rec["premise"].append(_serial_beside(task, "exact_centred", comp, pools[comp]["seed"]))
        rec["beside"][f"at_cap_share_{comp}"] = pools[comp]["at_cap"]
    rec["beside"]["centres"] = centres
    rec["fill"] = {"a2_x1": fill_summary(fff), "a2_x2": fill_summary(ffb)}
    return _finish(rec, mem)


def _regime_condition(hist: S1.S1History, starts: Sequence[int], Xf, Xb, dims, cols, n_min: int) -> bool:
    """(R) on S1: every regime (the history's slow sign at the start's session) of at least n_min starts has its
    composite difference over the given seed columns positive (`three_way_stats.condition`)."""
    reg = np.array([float(hist.regime[s]) for s in starts])
    dh, cnt = {}, {}
    for g in np.unique(reg):
        rows = np.flatnonzero(reg == g)
        xf = {d.name: Xf[d.name][rows][:, cols] for d in dims}
        xb = {d.name: Xb[d.name][rows][:, cols] for d in dims}
        dh[float(g)] = ST.composite(dims, xf) - ST.composite(dims, xb)
        cnt[float(g)] = rows.size
    return bool(ST.condition(dh, cnt, n_min)["holds"])


def a3_history(task: HistoryTask) -> dict:
    """A3 on one history (the note's 2.7): the stream pair (D on stream A, D' on stream B), one coin field; on the
    pool of M seeds, theta-hat at the test's J (the mean of the sets' 2.2 (a) estimates) and its standard error (the
    per-seed linear composite difference's sd over sqrt(J)); the pass probability Phi((theta-hat - margin) / se) at
    each level, 2.5's formula with the bound's own margin, times the time conditions' indicator; on a shortcut
    history, the full run at the test's J (each set's bound, its time conditions on its own units)."""
    mem = MemoryGuard(task.cap_mb)
    check_seed_use(task.part, task.part_id, task.roles)
    if task.time_conditions not in (None, "regime") or (task.time_conditions == "regime" and task.n_min is None):
        raise REP.H3ReportRefused("A3's time conditions are None (the coin leg alone) or 'regime' with an n_min")
    rec = _base(task)
    (seed,) = (S.issue(r) for r in task.roles)
    hist = S1.generate(seed, task.part_id, task.history, task.s1_params)
    d_sch, dp_sch = (S1.schedule(spec, hist) for spec in H.A3_PAIR)
    plan = _plan(task, seed, 0, task.M)
    guard = K.KeyGuard.sampled(plan.starts, plan.seed_indices)
    try:
        Xd, ffd = unit_values(d_sch, task.rules, plan, J.ArmSpec(), guard, mem.check)
        Xp, ffp = unit_values(dp_sch, task.rules, plan, J.ArmSpec(), guard, mem.check)
    except Exception as exc:                                # noqa: BLE001 -- only the recorded refusals (_caught)
        if not _caught(exc):
            raise
        rec["premise"].append(_premise(task, "run", "all", "run", _refusal_kind(exc), True, None, str(exc)))
        return _finish(rec, mem)
    jt = int(task.j)
    if task.M < jt:
        raise REP.H3ReportRefused(f"A3's pool of {task.M} seeds holds no set of the test's J = {jt}")
    sets = [np.arange(i * jt, (i + 1) * jt) for i in range(task.M // jt)]
    for comp in REP.COMPOSITES:
        dims = REP.composite_dims(comp)
        smap = {d.name: task.starts for d in dims}
        lin = sum(d.weight * (d.values(Xp[d.name]).mean(axis=0) - d.values(Xd[d.name]).mean(axis=0))
                  / (d.hi - d.lo) for d in dims)
        se = float(np.std(lin, ddof=1)) / math.sqrt(jt)
        regime = task.time_conditions == "regime"
        time_ok = _regime_condition(hist, task.starts, Xp, Xd, dims, np.arange(task.M), int(task.n_min)) \
            if regime else True
        set_ok = [_regime_condition(hist, task.starts, Xp, Xd, dims, c, int(task.n_min)) if regime else True
                  for c in sets] if task.history in task.shortcut else []
        for lv in REP.LEVELS:
            bnds = [ST.mcdiarmid(dims, {k: Xp[k][:, c] for k in smap}, {k: Xd[k][:, c] for k in smap}, smap, lv)
                    for c in sets]
            theta = float(np.mean([b.estimate for b in bnds]))
            margin = float(bnds[0].estimate - bnds[0].lower)
            if se > 0:
                pp = float(_norm.cdf((theta - margin) / se))
            else:
                pp = float(theta > margin)
            row = {"history": task.history, "composite": comp, "bound": "bound_22a", "level": lv,
                   "pass_prob": pp * float(time_ok), "pass_prob_coin_leg": pp, "time_ok": bool(time_ok),
                   "theta_hat": theta, "se_hat": se, "margin": margin, "test_j": jt,
                   "time_conditions": task.time_conditions or "none", "full_passes": 0, "full_draws": 0}
            if task.history in task.shortcut:
                row["full_passes"] = int(sum(int(b.lower > 0 and ok_t) for b, ok_t in zip(bnds, set_ok)))
                row["full_draws"] = len(sets)
            rec["rows"].append(row)
    rec["fill"] = {"a3_D": fill_summary(ffd), "a3_D'": fill_summary(ffp)}
    return _finish(rec, mem)


def _plant_passes(lower: Callable[[np.ndarray], float], samples: Sequence[np.ndarray], size: float) -> int:
    """The draws, of `samples`, on which `lower` passes the plant of `size` run through the bound itself
    (`three_way_stats.planted_rates`), as a count."""
    return int(round(float(ST.planted_rates(lower, samples, [float(size)])[0]) * len(samples)))


def a4_history(task: HistoryTask) -> dict:
    """A4 on one history: A1's design on its S1 history (`S1_PARAMS`, `TOY_RULES`); its base arm on every seed,
    retained; each plant arm on the same coin field, reduced and dropped (B-7).
    - **P1 and P4 against a null on an independent coin field** (B-5): the null terms are the base arm's on the first
      `DISJOINT` set against its second (the disjoint same-design null of 2.3 (b)), in draws of J seeds a side; P1 the
      null plus delta (2.2 (a)'s and EB's lower limits at no plant recorded per draw for `planted_mdl`; its rates by
      `planted_rates`), P4 the null plus delta_t = d (1 + a rho_t) on the composite's scale, rho_t a slow sign over
      the starts (`family_stats.slow_sign` of the `plant` key), its rates by `planted_rates` -- the clip to [-1, 1]
      and the betting bound included.
    - **P2 and P3 paired with the base on one coin field** (the design against its baseline), in draws of J seeds; a
      pass is the lower limit above zero; the pool's estimate beside (M seeds, the note's "a pool of at least a hundred
      times J")."""
    mem = MemoryGuard(task.cap_mb)
    check_seed_use(task.part, task.part_id, task.roles)
    check_disjoint_sets(task.disjoint, task.M)
    rec = _base(task)
    rec["p1_lowers"] = []
    h_seed, c_seed = (S.issue(r) for r in task.roles)
    hist = S1.generate(h_seed, task.part_id, task.history, task.s1_params)
    sched = S1.schedule(H.A1_DESIGN, hist)
    plan = _plan(task, c_seed, 0, task.M)
    guard = K.KeyGuard.sampled(plan.starts, plan.seed_indices)
    jd = int(task.j)
    (a0, a1), (b0, b1) = task.disjoint
    try:
        Xb, ffb = unit_values(sched, task.rules, plan, J.ArmSpec(), guard, mem.check)
        rec["fill"]["base"] = fill_summary(ffb)
        X1, X2 = _cols(Xb, a0, a1), _cols(Xb, b0, b1)
        n_draws = (a1 - a0) // jd
        if n_draws < 1:
            raise REP.H3ReportRefused(f"A4: no draw of {jd} seeds a side in a set of {a1 - a0}")
        rho = FS.slow_sign(np.random.default_rng(K.seed_key(h_seed, "plant", part=task.part_id,
                                                            history=task.history, plant=4, replicate=0)),
                           len(task.starts), H.P4_SWITCH)
        null = {}
        for comp in REP.COMPOSITES:
            dims = REP.composite_dims(comp)
            smap = {d.name: task.starts for d in dims}
            d_seed = REP.composite_per_seed_diffs(X1, X2, dims)
            reps, est, margin = [], [], {}
            for i in range(n_draws):
                c = np.arange(i * jd, (i + 1) * jd)
                reps.append(d_seed[c])
                b0_ = ST.mcdiarmid(dims, _cols(X1, c[0], c[-1] + 1), _cols(X2, c[0], c[-1] + 1), smap, REP.LEVELS[0])
                est.append(b0_.estimate)
            for lv in REP.LEVELS:
                b = ST.mcdiarmid(dims, _cols(X1, 0, jd), _cols(X2, 0, jd), smap, lv)
                margin[lv] = float(b.estimate - b.lower)
            null[comp] = {"reps": reps, "est": np.asarray(est), "margin": margin}
            single = float(REP.composite_per_seed(X1, dims).var(ddof=1))
            rec["premise"].append(_guarded(task, "a4_disjoint_null", comp, "seed", "centring_and_variance", True,
                                           lambda: REP.check_null_pool(d_seed, single_arm_var=single)))
            rec["premise"].append(_serial_beside(task, "a4_disjoint_null", comp, d_seed))

        def lowers(comp, b, lv):
            n = null[comp]
            if b == "bound_22a":
                return (lambda x, _m=n["margin"][lv]: float(x[0]) - _m), [np.array([e]) for e in n["est"]]
            f = ST.eb_lower if b == "eb" else ST.betting_lower
            return (lambda x, _f=f, _l=lv: float(_f(x, _l))), n["reps"]

        # P1: P_B alone, 2.2 (a)'s and EB (the linear form's bounds), the null plus delta
        for b in ("bound_22a", "eb"):
            for lv in REP.LEVELS:
                fn, smp = lowers("p_b", b, lv)
                for i, x in enumerate(smp):
                    rec["p1_lowers"].append({"history": task.history, "draw": i, "bound": b, "level": lv,
                                             "lower0": fn(x)})
                for d in H.SIZE_GRID:
                    rec["rows"].append({"history": task.history, "plant": "P1", "param": f"delta={d:g}",
                                        "composite": "p_b", "bound": b, "level": lv,
                                        "passes": _plant_passes(fn, smp, d), "draws": len(smp),
                                        "true_delta": float(d)})
        # P4: delta_t = d (1 + a rho_t), on the composite's scale, its mean over the starts the plant
        for a in H.P4_A:
            for d in H.SIZE_GRID:
                size = float(d) * float(np.mean(1.0 + float(a) * rho))
                for comp in REP.COMPOSITES:
                    for b in REP.BOUNDS:
                        for lv in REP.LEVELS:
                            fn, smp = lowers(comp, b, lv)
                            rec["rows"].append({"history": task.history, "plant": "P4", "param": f"a={a:g},d={d:g}",
                                                "composite": comp, "bound": b, "level": lv,
                                                "passes": _plant_passes(fn, smp, size), "draws": len(smp),
                                                "true_delta": size})
        # P2 and P3: each arm against the base on one coin field
        arms = [("P2", name, replace(task.rules, **patch), J.ArmSpec()) for name, patch in H.P2_LEVERS.items()]
        arms += [("P3", f"eps={e:g}", task.rules, J.ArmSpec(plant_eps=float(e))) for e in H.P3_EPS]
        for plant, param, rules, arm in arms:
            Xf, fff = unit_values(sched, rules, plan, arm, guard, mem.check)
            rec["fill"][f"{plant}:{param}"] = fill_summary(fff)
            counts, pools = REP.size_counts(Xf, Xb, task.starts, j_prime=jd)
            for comp in REP.COMPOSITES:
                td = float(np.mean(pools[comp]["set"]))
                for b in REP.BOUNDS:
                    for lv in REP.LEVELS:
                        k, n = counts[(comp, b, float(lv))]
                        rec["rows"].append({"history": task.history, "plant": plant, "param": param,
                                            "composite": comp, "bound": b, "level": float(lv), "passes": int(k),
                                            "draws": int(n), "true_delta": td})
            del Xf
    except Exception as exc:                                # noqa: BLE001 -- only the recorded refusals (_caught)
        if not _caught(exc):
            raise
        rec["premise"].append(_premise(task, "run", "all", "run", _refusal_kind(exc), True, None, str(exc)))
        return _finish(rec, mem)
    return _finish(rec, mem)


# ----------------------------------------------------------------------------------------- the stress (m-2)


def run_stress(history: int, n_seeds: int, *, part_id: int, roles: Sequence[str], part: str = "A1",
               starts: Sequence[int] = H.STARTS, horizon: int = H.HORIZON, s1_params: S1.S1Params = H.S1_PARAMS,
               rules: J.ToyRules = H.TOY_RULES) -> dict[str, dict[str, float]]:
    """Section 8's stress beside: the 3 declared stress arms x 5 schedules (A1's design and the four baselines' toys)
    = 15 runs (`three_way_runner.stress`) on one history and `n_seeds` seed indices -- a size the declaration does not
    state (m-2): called only with a size a row sets."""
    check_seed_use(part, part_id, roles)
    h_seed, c_seed = (S.issue(r) for r in roles)
    hist = S1.generate(h_seed, part_id, int(history), s1_params)
    plan = R.Plan(seed=c_seed, part=part_id, history=int(history), starts=starts, seed_indices=range(int(n_seeds)),
                  horizon=horizon, block_sessions=s1_params.n_sessions, budget=H.BUDGET)
    out = R.stress(S1.schedule(H.A1_DESIGN, hist), {n: S1.schedule(sp, hist) for n, sp in H.BASELINES.items()},
                   rules, plan, R.p_b)
    return {arm: {k: float(v.mean()) for k, v in mats.items()} for arm, mats in out.items()}


# ----------------------------------------------------------------------------------------- orchestration


Sink = Callable[[pd.DataFrame, str, str, dict], None]


def _jsonable(x):
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        v = float(x)
        return v if math.isfinite(v) else None
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


def check_workers(workers: Any) -> int:
    """m-4: 1 or 2 workers (the declared at most 2), refused otherwise -- never clamped."""
    if isinstance(workers, bool) or not isinstance(workers, (int, np.integer)) or not 1 <= int(workers) <= MAX_WORKERS:
        raise REP.H3ReportRefused(f"REFUSED (m-4): --workers is 1 .. {MAX_WORKERS}, not {workers!r}")
    return int(workers)


def project_worker_mb(part: str, M: int, n_starts: int, horizon: int, payout_lag: int, base_mb: float) -> float:
    """B-7's projection a worker: the process base (`base_mb`, measured) plus the values a worker keeps (A1: two arms
    of two sets; A2, A3 and A4: two arms at once) -- three dimensions and the failures at the fill, float64, a start a
    row, a seed a column -- plus one start's simulation (its lanes' state, `rel` over the horizon, the arrivals' lists
    at a conservative 200 bytes a lane, and the 32-step walk chunk), at the widest plan of the part."""
    lanes = int(M) // 2 if part == "A1" else int(M)
    kept = 2 * 4 * int(n_starts) * int(M) * 8
    one_start = lanes * ((20 + payout_lag + 1) * 8 + (horizon + 1) * 8 + 200 + J.WALK_CHUNK * 8)
    return float(base_mb) + (kept + one_start) / 2 ** 20


def _execute(fn: Callable[[HistoryTask], dict], tasks: Sequence[HistoryTask], workers: int,
             on_result: Callable[[dict], None]) -> None:
    """Run the tasks, handing each record to `on_result` the moment it returns (B-1: nothing waits for the last); a
    refusal in `on_result` cancels the tasks not started."""
    if workers == 1 or len(tasks) <= 1:
        for t in tasks:
            on_result(fn(t))
        return
    ex = cf.ProcessPoolExecutor(max_workers=workers)
    try:
        futs = [ex.submit(fn, t) for t in tasks]
        for f in cf.as_completed(futs):
            on_result(f.result())
    except BaseException:
        ex.shutdown(wait=True, cancel_futures=True)
        raise
    ex.shutdown(wait=True)


def _premise_df(records: Sequence[dict]) -> pd.DataFrame:
    rows = [p for r in records for p in r["premise"]]
    cols = ["part", "history", "null_class", "composite", "pool", "check", "decides", "ok", "abs_z", "n", "stat",
            "detail"]
    return pd.DataFrame(rows, columns=cols)


def _env_meta(workers: int) -> dict:
    return {"workers": int(workers), "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
            "worker_cap_mb": WORKER_CAP_MB, "total_cap_mb": TOTAL_CAP_MB}


def total_mb(parent_peak_mb: float, worker_peak_mb: float, workers: int) -> float:
    """c2 m-5: the memory in all -- the parent's peak plus each worker's (one worker runs in the parent's process, so
    the parent's peak is then the total)."""
    if int(workers) == 1:
        return float(max(parent_peak_mb, worker_peak_mb))
    return float(parent_peak_mb) + int(workers) * float(worker_peak_mb)


class _Part:
    """One part's run: records written as they arrive, the premise table written before any refusal (m-8)."""

    def __init__(self, part: str, out: str, sink: Sink, meta: dict, block: int = 1, cap_mb: float = WORKER_CAP_MB,
                 workers: int = 1, total_cap_mb: float = TOTAL_CAP_MB):
        self.part, self.out, self.sink, self.meta, self.block = part, out, sink, meta, int(block)
        self.cap_mb, self.workers, self.total_cap_mb = float(cap_mb), int(workers), float(total_cap_mb)
        self.worker_peak = 0.0
        self.records: list[dict] = []
        self.pending: dict[int, list[dict]] = {}

    def _write_block(self, recs: list[dict]) -> None:
        recs = sorted(recs, key=lambda r: r["history"])
        first = recs[0]["history"]
        name = f"{self.out}_h{first:03d}"
        params = {"part": self.part, "histories": [r["history"] for r in recs],
                  "premise": [p for r in recs for p in r["premise"]], "fill_failures": {r["history"]: r["fill"]
                                                                                         for r in recs},
                  "beside": {r["history"]: r["beside"] for r in recs},
                  "mem_peak_mb": {r["history"]: r["mem_peak_mb"] for r in recs}, **self.meta}
        rows = [x for r in recs for x in r["rows"]]
        if rows and isinstance(rows[0], REP.SizeCount):
            df = pd.DataFrame([{**REP.score_per_history_beside(c),
                                "beside_eb_range_term_at_j_prime": REP.eb_range_term(int(self.meta["j"]), c.level)
                                if c.bound == "eb" else float("nan")} for c in rows])
        else:
            df = pd.DataFrame(rows)
        params["parent_peak_mb"] = {r["history"]: r.get("parent_peak_mb") for r in recs}
        params["total_mb"] = {r["history"]: r.get("total_mb") for r in recs}
        self.sink(df, name, f"H3-{self.part} per-history records (histories {params['histories']}), beside",
                  params)
        if any("p1_lowers" in r for r in recs):
            self.sink(pd.DataFrame([x for r in recs for x in r.get("p1_lowers", [])]), f"{name}_p1",
                      f"H3-{self.part} P1's per-draw lower limits at no plant (histories {params['histories']})",
                      {"part": self.part, "histories": params["histories"], **self.meta})

    def take(self, rec: dict) -> None:
        rec["parent_peak_mb"] = float(procmem.working_set_mb(peak=True))
        if math.isfinite(rec["mem_peak_mb"]):
            self.worker_peak = max(self.worker_peak, rec["mem_peak_mb"])
        rec["total_mb"] = total_mb(rec["parent_peak_mb"], self.worker_peak, self.workers)
        self.records.append(rec)
        b = rec["history"] // self.block
        self.pending.setdefault(b, []).append(rec)
        lo = b * self.block
        want = set(range(lo, lo + self.block)) & set(self.meta["histories"])
        if {r["history"] for r in self.pending[b]} == want:
            self._write_block(self.pending.pop(b))
        bad = [p for p in rec["premise"] if p["decides"] and not p["ok"]]
        over = (math.isfinite(rec["mem_peak_mb"]) and rec["mem_peak_mb"] > self.cap_mb) \
            or any(p["check"] == "memory" for p in bad)
        over_all = math.isfinite(rec["total_mb"]) and rec["total_mb"] > self.total_cap_mb
        if bad or over or over_all or rec["refused"]:
            for blk in list(self.pending):
                self._write_block(self.pending.pop(blk))
            self.write_premises(refused=True)
            if over:
                raise MemoryRefused(f"REFUSED (B-7): history {rec['history']}'s worker peaked at "
                                    f"{rec['mem_peak_mb']:.0f} MB, above {self.cap_mb:.0f} MB, or refused inside")
            if over_all:
                raise MemoryRefused(f"REFUSED (c2 m-5): the parent and {self.workers} worker(s) reach "
                                    f"{rec['total_mb']:.0f} MB in all, above the cap {self.total_cap_mb:.0f} MB")
            raise REP.H3ReportRefused(f"H3-{self.part} premise failed on history {rec['history']} (section 11; "
                                      f"the failure protocol): {[(p['null_class'], p['composite'], p['pool'], p['check'], p['detail'][:80]) for p in bad][:5]}")

    def write_premises(self, refused: bool = False) -> None:
        self.sink(_premise_df(self.records), f"{self.out}_premises",
                  f"H3-{self.part} premise table ({'REFUSED' if refused else 'every premise holds'})",
                  {"part": self.part, "refused": refused, **self.meta})


def _projection_check(part: str, M: int, n_starts: int, horizon: int, rules: J.ToyRules,
                      cap_mb: float = WORKER_CAP_MB, workers: int = 1, total_cap_mb: float = TOTAL_CAP_MB) -> float:
    """B-7 and c2 m-5 before any draw: the projected worker inside the cap a worker, and the parent (its working set
    now) with the projected workers inside the cap in all."""
    now = procmem.working_set_mb()
    proj = project_worker_mb(part, M, n_starts, horizon, rules.payout_lag, now)
    if math.isfinite(proj) and proj > cap_mb:
        raise MemoryRefused(f"REFUSED (B-7): the projected memory a worker, {proj:.0f} MB, is above the declared cap "
                            f"{cap_mb:.0f} MB")
    tot = total_mb(now, proj, workers)
    if math.isfinite(tot) and tot > total_cap_mb:
        raise MemoryRefused(f"REFUSED (c2 m-5): the projected memory in all, {tot:.0f} MB, is above the declared cap "
                            f"{total_cap_mb:.0f} MB")
    return proj


def _tasks(part: str, part_id: int, roles, histories, M, starts, horizon, j, disjoint, s1_params, rules, cap_mb,
           **kw):
    return [HistoryTask(part=part, part_id=int(part_id), roles=tuple(roles), history=int(r), M=int(M),
                        starts=tuple(int(s) for s in starts), horizon=int(horizon), j=int(j),
                        disjoint=tuple(tuple(int(x) for x in d) for d in disjoint), s1_params=s1_params, rules=rules,
                        cap_mb=float(cap_mb), **kw) for r in histories]


def run_a1(*, part_id: int, roles: Sequence[str], sink: Sink, histories: Sequence[int] = range(20), M: int = H.SEEDS,
           starts: Sequence[int] = H.STARTS, horizon: int = H.HORIZON, j_prime: int = H.J_PRIME,
           disjoint=H.DISJOINT, s1_params: S1.S1Params = H.S1_PARAMS, rules: J.ToyRules = H.TOY_RULES,
           workers: int = 2, twin_arm: J.ArmSpec = J.ArmSpec(twin=True), stress: tuple[int, int] | None = None,
           cap_mb: float = WORKER_CAP_MB, out: str = "h3a_a1") -> dict:
    """A1 (section 8's 36 pooled counts and the 720 per-history beside): every history's record written as it
    arrives; the pooled counts are `h3a_report.pool_counts` of the per-history ones; the stress beside at `stress` =
    (history, seeds) only when given (m-2)."""
    w = check_workers(workers)
    check_seed_use("A1", part_id, roles)
    check_disjoint_sets(disjoint, M)
    proj = _projection_check("A1", M, len(starts), horizon, rules, cap_mb, w)
    meta = {"histories": [int(r) for r in histories], "M": int(M), "j": int(j_prime), "disjoint": disjoint,
            "seed_roles": list(roles), "key_kinds": ["history", "coin"], "projected_worker_mb": proj, **_env_meta(w)}
    P = _Part("A1", out, sink, meta, cap_mb=cap_mb, workers=w)
    _execute(a1_history, _tasks("A1", part_id, roles, histories, M, starts, horizon, j_prime, disjoint, s1_params,
                                rules, cap_mb, twin_arm=twin_arm), w, P.take)
    pooled = REP.pool_counts([c for r in P.records for c in r["rows"]])
    stress_out = None if stress is None else run_stress(stress[0], stress[1], part_id=part_id, roles=roles,
                                                        starts=starts, horizon=horizon, s1_params=s1_params,
                                                        rules=rules)
    meta2 = {**meta, "mem_peak_mb_max": max(r["mem_peak_mb"] for r in P.records),
             "fill_failures": {r["history"]: r["fill"] for r in P.records},
             "stress": stress_out if stress_out is not None else STRESS_NOTE,
             "smaller_j_report": "not run in H3-A: its delta and level are undeclared (B-1); H3-D's text's (E-290)",
             "premise_forms": "E-295 (d): the twin's sign test at CENTRING_Z and its uniforms 1 - u bit for bit, "
                              "deciding; (e): per-set centring deciding for the toy composite only, P_B's beside",
             "parent_peak_mb_max": max(r["parent_peak_mb"] for r in P.records)}
    P.write_premises()
    df = pd.DataFrame([REP.score_pooled_cell(c) for c in pooled])
    sink(df, out, "H3-A1 same-design nulls (36 pooled counts = the sums of the per-history counts; E-279/E-285)",
         meta2)
    return {"pooled": pooled, "records": P.records, "meta": meta2, "stress": stress_out}


def run_a2(*, part_id: int, roles: Sequence[str], sink: Sink, histories: Sequence[int] = range(20), M: int = H.SEEDS,
           starts: Sequence[int] = H.STARTS, horizon: int = H.HORIZON, j_prime: int = H.J_PRIME,
           s1_params: S1.S1Params = H.S1_PARAMS_EXACT, rules: J.ToyRules = H.TOY_RULES_EXACT, workers: int = 2,
           cap_mb: float = WORKER_CAP_MB, out: str = "h3a_a2") -> dict:
    """A2 (section 8's 18 pooled counts and the 360 per-history beside), records written as they arrive."""
    w = check_workers(workers)
    check_seed_use("A2", part_id, roles)
    proj = _projection_check("A2", M, len(starts), horizon, rules, cap_mb, w)
    meta = {"histories": [int(r) for r in histories], "M": int(M), "j": int(j_prime), "seed_roles": list(roles),
            "key_kinds": ["history", "coin"], "projected_worker_mb": proj, **_env_meta(w)}
    P = _Part("A2", out, sink, meta, cap_mb=cap_mb, workers=w)
    half = ((0, int(M)), (0, int(M)))                     # unused by A2 (one coin field), carried for the task's form
    _execute(a2_history, _tasks("A2", part_id, roles, histories, M, starts, horizon, j_prime, half, s1_params, rules, cap_mb),
             w, P.take)
    pooled = REP.pool_counts([c for r in P.records for c in r["rows"]])
    meta2 = {**meta, "mem_peak_mb_max": max(r["mem_peak_mb"] for r in P.records),
             "fill_failures": {r["history"]: r["fill"] for r in P.records}}
    P.write_premises()
    df = pd.DataFrame([REP.score_pooled_cell(c) for c in pooled])
    sink(df, out, "H3-A2 exact-centred toy null (18 pooled counts = the sums of the per-history counts; E-279/E-285)",
         meta2)
    return {"pooled": pooled, "records": P.records, "meta": meta2}


def run_a3_slice(histories: Sequence[int], *, part_id: int, roles: Sequence[str], sink: Sink, test_j: int,
                 time_conditions: str | None, n_min: int | None = None, M: int = 2000,
                 starts: Sequence[int] = H.STARTS, horizon: int = H.HORIZON, s1_params: S1.S1Params = H.S1_PARAMS,
                 rules: J.ToyRules = H.TOY_RULES, workers: int = 2, shortcut: Sequence[int] = H.SHORTCUT_HISTORIES,
                 cap_mb: float = WORKER_CAP_MB, out: str = "h3a_a3_1", block: int = A3_BLOCK) -> dict:
    """A3 on a slice of its histories (the note's 2.7), at the test's J and time conditions given (a row's)."""
    w = check_workers(workers)
    check_seed_use("A3", part_id, roles)
    proj = _projection_check("A3", M, len(starts), horizon, rules, cap_mb, w)
    meta = {"histories": [int(r) for r in histories], "M": int(M), "j": int(test_j), "seed_roles": list(roles),
            "key_kinds": ["history", "coin"], "time_conditions": time_conditions or "none", "n_min": n_min,
            "pair_label": REP.A3_PAIR_LABEL, "projected_worker_mb": proj, **_env_meta(w)}
    P = _Part("A3", out, sink, meta, block=block, cap_mb=cap_mb, workers=w)
    none = ((0, int(M)), (0, int(M)))
    _execute(a3_history, _tasks("A3", part_id, roles, histories, M, starts, horizon, test_j, none, s1_params, rules,
                                cap_mb, time_conditions=time_conditions, n_min=n_min, shortcut=tuple(shortcut)), w, P.take)
    P.meta = {**meta, "mem_peak_mb_max": max(r["mem_peak_mb"] for r in P.records)}
    P.write_premises()
    return {"records": P.records, "meta": P.meta}


def run_a4_slice(histories: Sequence[int], *, part_id: int, roles: Sequence[str], sink: Sink, draw_j: int,
                 M: int = H.SEEDS, starts: Sequence[int] = H.STARTS, horizon: int = H.HORIZON, disjoint=H.DISJOINT,
                 s1_params: S1.S1Params = H.S1_PARAMS, rules: J.ToyRules = H.TOY_RULES, workers: int = 2,
                 cap_mb: float = WORKER_CAP_MB, out: str = "h3a_a4_1") -> dict:
    """A4 on a slice of its histories: 426 rows a history (section 8's pass-rate cells) and P1's per-draw lowers."""
    w = check_workers(workers)
    check_seed_use("A4", part_id, roles)
    check_disjoint_sets(disjoint, M)
    proj = _projection_check("A4", M, len(starts), horizon, rules, cap_mb, w)
    meta = {"histories": [int(r) for r in histories], "M": int(M), "j": int(draw_j), "disjoint": disjoint,
            "seed_roles": list(roles), "key_kinds": ["history", "coin", "plant"], "projected_worker_mb": proj,
            "copy_against_stagger": "not run in H3-A (the template does not define overlap yet; section 11)",
            "j_note": REP.A4_J_NOTE, "null_note": REP.A4_NULL_NOTE,
            **_env_meta(w)}
    P = _Part("A4", out, sink, meta, cap_mb=cap_mb, workers=w)
    _execute(a4_history, _tasks("A4", part_id, roles, histories, M, starts, horizon, draw_j, disjoint, s1_params,
                                rules, cap_mb), w, P.take)
    for r in P.records:
        if len(r["rows"]) != len(REP.a4_cells()):
            raise REP.H3ReportRefused(f"A4 history {r['history']} produced {len(r['rows'])} cells, not 426")
    P.meta = {**meta, "mem_peak_mb_max": max(r["mem_peak_mb"] for r in P.records)}
    P.write_premises()
    return {"records": P.records, "meta": P.meta}


# ----------------------------------------------------------------------------------------- the reports


def _premises_hold(df: pd.DataFrame, label: str) -> None:
    bad = df[(df["decides"].astype(str).str.lower() == "true") & (df["ok"].astype(str).str.lower() != "true")]
    if len(df) == 0 or len(bad):
        raise REP.H3ReportRefused(f"{label}: {len(bad)} deciding premise(s) failed or no premise table")


def _size_rows(df: pd.DataFrame, per_history: bool) -> list[REP.SizeCount]:
    return [REP.SizeCount(str(r["part"]), str(r["null_class"]), str(r["composite"]), str(r["bound"]),
                          float(r["level"]), int(r["rejections"]), int(r["n"]),
                          history=int(r["history"]) if per_history else None) for _, r in df.iterrows()]


def build_final_report(results_dir: Path = RESULTS_DIR, *, read: Callable[[Path], pd.DataFrame] = pd.read_csv,
                       check_inputs: Callable[[Sequence[Path]], Any] | None = None,
                       pooled_n=None, histories=None) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """The stop (A1 + A2): the 54 pooled counts and the 1080 per-history counts read from their files (every one
    required), their premise tables (every deciding premise holding), the inputs checked (`check_inputs`, m-5), then
    `h3a_report.evaluate_laxity_stop`, which ties them to the declared n and to each other (B-4)."""
    d = Path(results_dir)
    hs = REP.declared_histories() if histories is None else histories
    paths = {"A1": d / "h3a_a1.csv", "A2": d / "h3a_a2.csv"}
    ph = {p: [d / f"{SLOT_SPEC[p]['out']}_h{int(h):03d}.csv" for h in hs[p]] for p in ("A1", "A2")}
    prem = {p: d / f"{SLOT_SPEC[p]['out']}_premises.csv" for p in ("A1", "A2")}
    every = [*paths.values(), *ph["A1"], *ph["A2"], *prem.values()]
    missing = [str(p) for p in every if not p.is_file()]
    if missing:
        raise REP.H3ReportRefused(f"the stop needs every input; missing {len(missing)}: {missing[:3]}")
    commit = check_inputs(every) if check_inputs is not None else None
    for p in ("A1", "A2"):
        _premises_hold(read(prem[p]), f"H3-{p}'s premises")
    pooled = [c for p in ("A1", "A2") for c in _size_rows(read(paths[p]), False)]
    per = [c for p in ("A1", "A2") for f in ph[p] for c in _size_rows(read(f), True)]
    ev = REP.evaluate_laxity_stop(pooled, per, pooled_n=pooled_n, histories=histories)
    meta = {k: ev[k] for k in ("verdict", "stop_h3d", "lax_count", "pooled_total", "per_history_count",
                               "family_stop_alpha", "stop_alpha_per_count")}
    meta["inputs_commit"] = commit
    meta["declared_pooled_n"] = {f"{a}/{b}": v for (a, b), v in (pooled_n or REP.declared_pooled_n()).items()}
    return pd.DataFrame(ev["pooled_rows"]), pd.DataFrame(ev["per_history_beside"]), meta


def build_a4_report(results_dir: Path = RESULTS_DIR, *, read: Callable[[Path], pd.DataFrame] = pd.read_csv,
                    check_inputs: Callable[[Sequence[Path]], Any] | None = None,
                    histories: Sequence[int] | None = None) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """A4 pooled over its histories: the 426 rates and the 60 MDLs (`h3a_report.summarise_a4`)."""
    d = Path(results_dir)
    hs = tuple(range(REP.DECLARED_R["A4"])) if histories is None else tuple(histories)
    slot_of = {h: s for s in ("A4_1", "A4_2") for h in range(*SLOT_SPEC[s]["histories"])}
    files = [d / f"{SLOT_SPEC[slot_of.get(h, 'A4_1')]['out']}_h{h:03d}.csv" for h in hs]
    p1 = [Path(str(f)[:-4] + "_p1.csv") for f in files]
    prem = sorted({d / f"{SLOT_SPEC[slot_of.get(h, 'A4_1')]['out']}_premises.csv" for h in hs})
    every = [*files, *p1, *prem]
    missing = [str(p) for p in every if not p.is_file()]
    if missing:
        raise REP.H3ReportRefused(f"A4's report needs every input; missing {len(missing)}: {missing[:3]}")
    commit = check_inputs(every) if check_inputs is not None else None
    for p in prem:
        _premises_hold(read(p), f"A4 ({p.name})")
    rows = [r for f in files for r in read(f).to_dict("records")]
    lows = [r for f in p1 for r in read(f).to_dict("records")]
    rates, mdls = REP.summarise_a4(rows, lows, histories=hs)
    return pd.DataFrame(rates), pd.DataFrame(mdls), {"inputs_commit": commit, "histories": list(hs)}


def build_a3_report(results_dir: Path = RESULTS_DIR, *, read: Callable[[Path], pd.DataFrame] = pd.read_csv,
                    check_inputs: Callable[[Sequence[Path]], Any] | None = None,
                    histories: Sequence[int] | None = None, shortcut: Sequence[int] | None = None,
                    block: int = A3_BLOCK) -> tuple[pd.DataFrame, dict]:
    """A3 pooled over its histories: the 6 rates (`h3a_report.summarise_a3`)."""
    d = Path(results_dir)
    hs = tuple(range(H.A3_HISTORIES)) if histories is None else tuple(histories)
    slot_of = {h: s for s in ("A3_1", "A3_2") for h in range(*SLOT_SPEC[s]["histories"])}
    firsts = sorted({(slot_of.get(h, "A3_1"), (h // block) * block) for h in hs})
    files = [d / f"{SLOT_SPEC[s]['out']}_h{f:03d}.csv" for s, f in firsts]
    prem = sorted({d / f"{SLOT_SPEC[slot_of.get(h, 'A3_1')]['out']}_premises.csv" for h in hs})
    every = [*files, *prem]
    missing = [str(p) for p in every if not p.is_file()]
    if missing:
        raise REP.H3ReportRefused(f"A3's report needs every input; missing {len(missing)}: {missing[:3]}")
    commit = check_inputs(every) if check_inputs is not None else None
    for p in prem:
        _premises_hold(read(p), f"A3 ({p.name})")
    rows = [r for f in files for r in read(f).to_dict("records")]
    out = REP.summarise_a3(rows, histories=hs, shortcut=shortcut)
    return pd.DataFrame(out), {"inputs_commit": commit, "histories": len(hs)}


# ----------------------------------------------------------------------------------------- the gates and main


def check_runtime_gates(part: str, *, root: Path = ROOT, results_dir: Path = RESULTS_DIR,
                        require_lock: bool = True) -> dict[str, str]:
    """Section 16 item 1: H3 pin + template v3 + `4c07026` build files + clean run + run.lock + no output of the slot."""
    from extended import results as RES

    pre = REP.assert_h3_preconditions(root, check_build_commit=True)
    bad_clean = RES.clean_run_problem()
    if bad_clean:
        raise REP.H3ReportRefused(f"H3-A requires a clean run (scripts/run_clean.py): {bad_clean}")
    if require_lock:
        holder = os.environ.get(LG.LOCK_HOLDER_ENV, "").strip()
        if not holder:
            raise REP.H3ReportRefused(f"H3-A {part} requires run.lock ({LG.LOCK_HOLDER_ENV} unset)")
        mroot = LG.main_root(root)
        if mroot is None:
            raise REP.H3ReportRefused(f"cannot resolve main root for run.lock from {root}")
        lock_file = mroot / LG.LOCK_NAME
        if not lock_file.is_file():
            raise REP.H3ReportRefused(f"run.lock not found at {lock_file}")
        lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
        if not isinstance(lock_data, dict) or lock_data.get("job") != holder:
            raise REP.H3ReportRefused(f"run.lock job != {LG.LOCK_HOLDER_ENV} ({holder!r})")
    out = SLOT_SPEC[part]["out"]
    clash = sorted(p.name for p in Path(results_dir).glob(f"{out}*")
                   if p.name.startswith(f"{out}.") or p.name.startswith(f"{out}_"))
    if clash:
        raise REP.H3ReportRefused(f"output already exists: {clash[:3]} (refusing to overwrite)")
    return pre


def check_rulings(part: str) -> None:
    """E-295: A3 (its slots and its report) is deferred to H3-D's text and refuses; A4 runs at `A4_DRAW_J`."""
    if part.startswith("A3") or part == "report_a3":
        raise REP.H3ReportRefused(f"REFUSED (B-6): A3 is {A3_NOTE}")
    if part.startswith("A4") and A4_DRAW_J != H.J_PRIME:
        raise REP.H3ReportRefused("REFUSED (E-295 (a)): A4's seeds a draw are J_PRIME")


def check_threads(env: Mapping[str, str] | None = None) -> int:
    """c2 m-7: OMP_NUM_THREADS set to an integer 1 .. MAX_THREADS, refused otherwise."""
    v = (os.environ if env is None else env).get("OMP_NUM_THREADS")
    try:
        n = int(str(v).strip())
    except (TypeError, ValueError):
        raise REP.H3ReportRefused(f"REFUSED (c2 m-7): OMP_NUM_THREADS must be set to 1 .. {MAX_THREADS}, not {v!r}")
    if not 1 <= n <= MAX_THREADS:
        raise REP.H3ReportRefused(f"REFUSED (c2 m-7): OMP_NUM_THREADS is 1 .. {MAX_THREADS}, not {n}")
    return n


#: every H3-A output this runner writes (the outputs a later slot finds already in results/)
H3A_OUTPUTS = ("h3a_a1", "h3a_a2", "h3a_a3", "h3a_a4", "h3a_summary")


def check_commit(commit: str, *, root: Path = ROOT, results_dir: Path = RESULTS_DIR,
                 read_manifest: Callable[[Path], Mapping] | None = None) -> str:
    """c2 m-6, at the runner's start: HEAD is the named commit, and every H3-A output already in `results_dir` was
    written from it, clean -- so the slots of H3-A all run from one commit and a mixed set refuses at its first slot,
    not at the report. Returns the full sha."""
    import subprocess

    def sha(ref: str) -> str:
        r = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", f"{ref}^{{commit}}"], capture_output=True,
                           text=True, encoding="utf-8")
        if r.returncode:
            raise REP.H3ReportRefused(f"REFUSED (c2 m-6): {ref!r} is not a commit")
        return r.stdout.strip()
    want, head = sha(str(commit)), sha("HEAD")
    if head != want:
        raise REP.H3ReportRefused(f"REFUSED (c2 m-6): HEAD {head[:7]} is not the named commit {want[:7]}")
    rd = read_manifest or REP.manifest_of
    for f in sorted(Path(results_dir).glob("h3a_*.csv")):
        if not f.name.startswith(H3A_OUTPUTS):
            continue
        m = rd(f)
        if str(m.get("git_commit", "")) != want or m.get("git_dirty") is not False:
            raise REP.H3ReportRefused(f"REFUSED (c2 m-6): {f.name} was written from {str(m.get('git_commit'))[:7]} "
                                      f"(dirty={m.get('git_dirty')!r}), not the named commit {want[:7]}")
    return want


def _result_sink() -> Sink:
    from extended import results as RES

    def sink(df: pd.DataFrame, name: str, description: str, parameters: dict) -> None:
        RES.write_result(df, name, script=SCRIPT, seed=None, require_seed=False, exploratory=False, prereg_id="H3",
                         description=description, parameters=_jsonable(parameters))
    return sink


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--part", required=True, choices=tuple(SLOT_SPEC.keys()))
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--commit", required=True, help="the one commit every H3-A slot runs from (c2 m-6)")
    args = ap.parse_args(argv)
    w = check_workers(args.workers)
    part = args.part
    check_rulings(part)
    threads = check_threads()
    commit = check_commit(args.commit)
    is_report = part.startswith("report")
    pre = check_runtime_gates(part, require_lock=not is_report)
    t0 = time.perf_counter()
    from extended import results as RES

    sink = _result_sink()
    spec = SLOT_SPEC[part]
    if not is_report:
        lo, hi = spec["histories"]
        base = dict(part_id=S.PARTS[spec["part"]], roles=PART_ROLES[spec["part"]],
                    sink=lambda df, name, d, prm: sink(df, name, d, {**prm, "named_commit": commit,
                                                                     "omp_threads_checked": threads}),
                    histories=range(lo, hi), M=spec["M"], workers=w, out=spec["out"])
        if part == "A1":
            res = run_a1(stress=None, **base)
        elif part == "A2":
            res = run_a2(**base)
        elif part.startswith("A3"):
            res = run_a3_slice(test_j=A3_TEST_J, time_conditions=A3_TIME_CONDITIONS, n_min=A3_N_MIN,
                               **{k: v for k, v in base.items() if k != "histories"}, histories=range(lo, hi))
        else:
            res = run_a4_slice(draw_j=A4_DRAW_J, **{k: v for k, v in base.items() if k != "histories"},
                               histories=range(lo, hi))
        print(f"H3-{part}: {len(res['records'])} histories written; preconditions {pre['h3_sha256'][:12]}; "
              f"{time.perf_counter() - t0:.0f} s")
        return 0

    def check(paths):
        c = REP.verify_inputs(paths, verify=RES.verify_result, root=ROOT)
        if c != commit:
            raise REP.H3ReportRefused(f"REFUSED (c2 m-6): the inputs come from {c[:7]}, not the named {commit[:7]}")
        return c

    if part == "report":
        df, hdf, meta = build_final_report(RESULTS_DIR, read=RES.read_result, check_inputs=check)
        meta.update(preconditions=pre, elapsed_s=time.perf_counter() - t0)
        sink(df, "h3a_summary", "H3-A laxity stop (54 pooled counts, one-sided 0.05/54, E-279)", meta)
        sink(hdf, "h3a_summary_per_history", "H3-A per-history counts beside (1080, never deciding)", meta)
        print(f"H3-A verdict: {meta['verdict']} (lax_count={meta['lax_count']}/{meta['pooled_total']})")
    elif part == "report_a4":
        rates, mdls, meta = build_a4_report(RESULTS_DIR, read=RES.read_result, check_inputs=check)
        meta.update(preconditions=pre)
        sink(rates, "h3a_a4_rates", "H3-A4 the 426 pass rates, pooled over A4's histories", meta)
        sink(mdls, "h3a_a4_mdl", "H3-A4 the 60 MDLs at pi* over SIZE_GRID", meta)
    else:
        df, meta = build_a3_report(RESULTS_DIR, read=RES.read_result, check_inputs=check)
        meta.update(preconditions=pre)
        sink(df, "h3a_a3_summary", "H3-A3 the history null's 6 rates (FPR_hist, stylised pair)", meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
