"""Q-187, the failure protocol for H3-A's slot A2 (its run `h3a-a2` at `RUN_COMMIT` refused B-7 at history 5):
**the component in isolation** and **the replication with the seeds fixed beforehand** -- A2's per-history path
(`scripts/h3a_run.py`'s `a2_history`, called itself, unedited) with its seeds exactly the run's (H3-A's declared
roles in A2's part, `three_way_seeds.issue`), under a fine memory trace, and under each of two memory readers:

- **`run`**: the path's reader is the run's own `extended/procmem.py`, read from git at `RUN_COMMIT` and loaded as a
  module -- the reader that left a ctypes pointer type behind at every call (`tests/test_procmem.py`);
- **`fixed`**: the path's reader is this commit's `extended/procmem.py` (Q-187's fix, built once).

The trace's own readings always use this commit's reader (they leave nothing behind), so the two modes differ only in
the reader the path calls -- its memory guard after every start and every close of the exact program. Each line also
counts those calls (`procmem_calls`).

**The plan** (each item and mode in a child process of its own, one at a time):
- `isolate`: one history (default the refused one) alone, `tracemalloc` on: each stage's wall time, working set
  (sampled at every trade, walk law, lane concatenation and merge of the exact program, and after every simulated
  start), process peak, `tracemalloc` peak and top allocations, and each start's state counts (into a trade, before
  and after each merge) beside its schedule's sizes (trades and R-10 walks inside the start's window);
- `replicate`: the run's workers re-enacted -- each sequence of histories in one process, in order, as a reused
  worker ran them (`SEQUENCES`, read from the order the run's records were written), `tracemalloc` off: each
  history's process peak after it (the run's `mem_peak_mb` is that reading) and the sha256 of its records file as
  the runner writes it (`rows_sha256`: `h3a_run._Part._write_block`'s frame, `to_csv` into a temporary folder), to
  set against the failed run's manifests -- a hash, never a value.

**Sizes and memory only.** Nothing here prints, returns or writes a value of the per-unit matrices, a centre, a count,
a rate or a premise's result: the history's record is reduced to its row count, the sha256 of its file, and, for a
refusal of the run itself (`null_class == "run"`), its kind and, for a memory refusal, its message
(`history_summary`); every printed key is in `SIZE_KEYS`. It writes nothing under `results/`, never calls the
results sink, and refuses a `--report` path inside the checkout; its lines go to stdout (the log beside the clean
checkout), each prefixed `DIAG `.

**Heavy** (the run's histories at M = `three_way_h3a.SEEDS` and the exact program): only under `run.lock`, from a
clean checkout of a committed commit, through `scripts/run_clean.py`:

    python scripts/run_clean.py --name h3a-a2-diag --commit <sha> --hours 2 --mem-gb 3 --task Q-187 -- python scripts/h3a_a2_diag.py --commit <sha>

It refuses, before any draw, unless `OMP_NUM_THREADS` is 1 or 2, HEAD is the named commit, every file the path
reaches except `extended/procmem.py` (the reader, chosen by the mode) equals `RUN_COMMIT`'s, the checkout is a clean
run, `run.lock` is held by this job, and H3's preconditions hold (`h3a_report.assert_h3_preconditions`). The run's cap
a worker is replaced by the diagnostic's stop (`--abort-mb`, the cap in all by default): the point is each history's
own peak, and the stop keeps the machine safe -- at the stop the stage and the place are printed and the exit is 2.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import time
import tracemalloc
import types
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from extended import h3a_report as REP  # noqa: E402
from extended import procmem  # noqa: E402
from extended import three_way_h3a as H  # noqa: E402
from extended import three_way_journey as J  # noqa: E402
from extended import three_way_redraw as RD  # noqa: E402
from extended import three_way_runner as R  # noqa: E402
from extended import three_way_s1 as S1  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402
from scripts import h3a_run as RUN  # noqa: E402

SCRIPT = "scripts/h3a_a2_diag.py"
#: the failed run's commit (`h3a-a2`, run.lock's command line); every file the path reaches must equal it
RUN_COMMIT = "26e1a55f601c7931a41344602028ec84f5628015"
#: the reader the modes swap (excluded from the reached files' check)
READER_FILE = "extended/procmem.py"
#: the history the run refused at
REFUSED_HISTORY = 5
#: the run's two workers' sequences, read from the order its records were written (the manifests' timestamps: 1, 2,
#: 3 by one worker and 0, 4 by the other, then 5 by the first free) -- an inference; `replicate` tests it
SEQUENCES = ((1, 2, 3, 5), (0, 4))
MODES = ("run", "fixed")
PREFIX = "DIAG "
#: this commit's reader, kept before any mode swaps the module's: the trace's own readings
_READ = procmem.working_set_mb
#: the keys a printed line may carry (sizes, times, memory, names, hashes): the tests hold every line to this list
SIZE_KEYS = frozenset({
    "kind", "stage", "schedule", "history", "start", "seconds", "lanes", "ws_start_mb", "ws_max_mb",
    "ws_end_mb", "lifetime_peak_mb", "traced_peak_mb", "traced_end_mb", "top", "aborted", "abort_where",
    "walks_in_window", "trades_in_window", "max_states_into_trade", "max_states_out_of_trade",
    "max_states_pre_merge", "max_states_post_merge", "max_walk_laws_a_trade", "max_walk_outcomes", "trades", "walks",
    "walks_window_max", "walks_window_mean", "windows_with_walks", "walk_n_max", "walk_step_min", "rows_n",
    "rows_sha256", "run_refusal", "memory_detail", "mem_peak_mb", "retained_traced_mb", "ws_before_mb",
    "ws_after_mb", "M", "starts", "horizon", "projected_worker_mb", "worker_cap_mb", "total_cap_mb", "abort_mb",
    "commit", "run_commit", "exact_only", "part", "where", "mb", "count", "exit", "mode", "plan", "sequence",
    "position", "procmem_calls", "max_walks_in_window"})


def _mb(x: float) -> float:
    return float(x) / 2 ** 20


def _short(path: str) -> str:
    """A frame's file, its last three parts (no machine path in the log)."""
    return "/".join(Path(path).parts[-3:])


# ----------------------------------------------------------------------------------------- the readers


def run_reader(root: Path = ROOT) -> Callable[..., float]:
    """The run's own `extended/procmem.py` (git's copy at `RUN_COMMIT`), loaded as a module of its own: its reader."""
    r = subprocess.run(["git", "-C", str(root), "show", f"{RUN_COMMIT}:{READER_FILE}"], capture_output=True,
                       text=True, encoding="utf-8")
    if r.returncode:
        raise REP.H3ReportRefused(f"REFUSED (Q-187): git cannot show {READER_FILE} at {RUN_COMMIT[:7]}")
    mod = types.ModuleType("procmem_at_run_commit")
    exec(compile(r.stdout, f"{RUN_COMMIT[:7]}:{READER_FILE}", "exec"), mod.__dict__)
    return mod.working_set_mb


def reader_for(mode: str, root: Path = ROOT) -> Callable[..., float]:
    if mode == "run":
        return run_reader(root)
    if mode == "fixed":
        return _READ
    raise REP.H3ReportRefused(f"REFUSED (Q-187): the mode is one of {MODES}, not {mode!r}")


@contextmanager
def path_reader(read: Callable[..., float], trace: "Trace") -> Iterator[None]:
    """The path's reader (the memory guard's, `h3a_run`'s `procmem.working_set_mb`) replaced by `read`, its calls
    counted; restored on exit."""
    orig = procmem.working_set_mb

    def counted(peak: bool = False) -> float:
        trace.procmem_calls += 1
        return read(peak=peak)
    procmem.working_set_mb = counted
    try:
        yield
    finally:
        procmem.working_set_mb = orig


# ----------------------------------------------------------------------------------------- the trace


class Trace:
    """The memory trace of one history: stages, starts, samples, `tracemalloc` snapshots; `emit` prints a line."""

    def __init__(self, abort_mb: float, emit: Callable[[dict], None], top: int = 12, snapshots: int = 6,
                 snap_floor_mb: float = 64.0, start_lines: bool = True):
        self.abort_mb, self.emit, self.top = float(abort_mb), emit, int(top)
        self.snapshots, self.snap_floor_mb, self.start_lines = int(snapshots), float(snap_floor_mb), bool(start_lines)
        self.stage: dict | None = None
        self.start: dict | None = None
        self.trade: dict | None = None
        self.aborted: str | None = None
        self.procmem_calls = 0

    def sample(self, where: str) -> None:
        cur = _READ()
        for rec in (self.stage, self.start):
            if rec is not None and math.isfinite(cur):
                rec["ws_max_mb"] = max(rec.get("ws_max_mb", 0.0), cur)
        st = self.stage
        if st is not None and tracemalloc.is_tracing():
            tm = _mb(tracemalloc.get_traced_memory()[0])
            if tm > self.snap_floor_mb and tm > 1.25 * st["_snap_best"] and st["_snaps"] < self.snapshots:
                snap = tracemalloc.take_snapshot().filter_traces((tracemalloc.Filter(False, tracemalloc.__file__),))
                st["top"] = [{"where": f"{_short(s.traceback[0].filename)}:{s.traceback[0].lineno}",
                              "mb": round(_mb(s.size), 3), "count": int(s.count)}
                             for s in snap.statistics("lineno")[: self.top]]
                st["_snap_best"], st["_snaps"] = tm, st["_snaps"] + 1
        if math.isfinite(cur) and cur > self.abort_mb:
            self.aborted = f"{st['stage'] if st else '-'}/{where}"
            raise RUN.MemoryRefused(f"REFUSED (Q-187 diagnostic): working set {cur:.0f} MB above the diagnostic's "
                                    f"stop {self.abort_mb:.0f} MB at {self.aborted}")

    @contextmanager
    def in_stage(self, name: str, schedule: str = "") -> Iterator[dict]:
        if tracemalloc.is_tracing():
            tracemalloc.reset_peak()
        rec = {"kind": "stage", "stage": name, "schedule": schedule, "ws_start_mb": _READ(), "ws_max_mb": 0.0,
               "top": [], "max_states_pre_merge": 0, "max_states_post_merge": 0, "max_walks_in_window": 0,
               "_snap_best": 0.0, "_snaps": 0, "_peak": 0.0, "_t0": time.perf_counter()}
        outer, self.stage = self.stage, rec
        try:
            yield rec
        finally:
            rec["seconds"] = time.perf_counter() - rec.pop("_t0")
            rec["ws_end_mb"] = _READ()
            rec["lifetime_peak_mb"] = _READ(peak=True)
            if tracemalloc.is_tracing():
                cur, pk = tracemalloc.get_traced_memory()
                rec["traced_peak_mb"], rec["traced_end_mb"] = max(rec["_peak"], _mb(pk)), _mb(cur)
            rec["aborted"] = self.aborted is not None
            if self.aborted:
                rec["abort_where"] = self.aborted
            for k in ("_snap_best", "_snaps", "_peak"):
                rec.pop(k)
            self.stage = outer
            self.emit(rec)

    @contextmanager
    def in_start(self, schedule: J.Schedule, start: int, horizon: int, lanes: int | None = None) -> Iterator[dict]:
        st = self.stage
        if tracemalloc.is_tracing():
            if st is not None:
                st["_peak"] = max(st["_peak"], _mb(tracemalloc.get_traced_memory()[1]))
            tracemalloc.reset_peak()
        win = [t for t in schedule.trades if start <= t.session < start + horizon]
        rec = {"kind": "start", "stage": st["stage"] if st else "", "schedule": schedule.name, "start": int(start),
               "trades_in_window": len(win), "walks_in_window": sum(1 for t in win if t.law == "walk"),
               "max_states_into_trade": 0, "max_states_out_of_trade": 0, "max_states_pre_merge": 0,
               "max_states_post_merge": 0, "max_walk_laws_a_trade": 0, "max_walk_outcomes": 0, "ws_max_mb": 0.0,
               "_t0": time.perf_counter()}
        if lanes is not None:
            rec["lanes"] = int(lanes)
        self.start = rec
        try:
            yield rec
        finally:
            rec["seconds"] = time.perf_counter() - rec.pop("_t0")
            if tracemalloc.is_tracing():
                pk = _mb(tracemalloc.get_traced_memory()[1])
                rec["traced_peak_mb"] = pk
                if st is not None:
                    st["_peak"] = max(st["_peak"], pk)
            if st is not None:
                for k in ("max_states_pre_merge", "max_states_post_merge"):
                    st[k] = max(st[k], rec[k])
                st["max_walks_in_window"] = max(st["max_walks_in_window"], rec["walks_in_window"])
            self.start = None
            if self.start_lines:
                self.emit(rec)

    def note(self, key: str, value: int) -> None:
        if self.start is not None:
            self.start[key] = max(int(self.start.get(key, 0)), int(value))


@contextmanager
def instrumented(trace: Trace) -> Iterator[None]:
    """The hooks, each a wrapper that calls the original unchanged and records sizes and memory around it; every
    original restored on exit (the tests hold that the wrapped path's record equals the plain path's)."""
    orig = {"unit_values": RUN.unit_values, "exact_arm": RUN.exact_arm, "exact_moments": RUN.exact_moments,
            "merge_paid": RUN._merge_paid, "size_counts": REP.size_counts, "exact_centres": R.exact_centres,
            "simulate": J.simulate, "expect": J.expect, "trade_dp": J._trade_dp, "merge": J._merge,
            "concat": J.Lanes.__dict__["concat"], "walk_law": RD.walk_law}

    def unit_values(schedule, rules, plan, arm, guard, on_start=None):
        with trace.in_stage("mc", schedule.name):
            return orig["unit_values"](schedule, rules, plan, arm, guard, on_start)

    def simulate(schedule, rules, start, seed_indices, horizon, **kw):
        with trace.in_start(schedule, start, horizon, lanes=len(seed_indices)):
            out = orig["simulate"](schedule, rules, start, seed_indices, horizon, **kw)
            trace.sample("simulate")
            return out

    def exact_arm(schedule, rules, plan, on_step=None):
        with trace.in_stage("exact", schedule.name):
            return orig["exact_arm"](schedule, rules, plan, on_step)

    def exact_moments(schedule, rules, start, horizon, **kw):
        with trace.in_start(schedule, start, horizon):
            return orig["exact_moments"](schedule, rules, start, horizon, **kw)

    def exact_centres(f, b, rules, plan, arm=J.ArmSpec()):
        with trace.in_stage("centres", f"{f.name}-{b.name}"):
            return orig["exact_centres"](f, b, rules, plan, arm)

    def expect(schedule, rules, start, horizon, **kw):
        with trace.in_start(schedule, start, horizon):
            return orig["expect"](schedule, rules, start, horizon, **kw)

    def size_counts(*a, **kw):
        with trace.in_stage("counts"):
            return orig["size_counts"](*a, **kw)

    def trade_dp(L, t, rules, arm):
        trace.note("max_states_into_trade", len(L))
        trace.trade = {"laws": 0}
        out = orig["trade_dp"](L, t, rules, arm)
        trace.note("max_states_out_of_trade", len(out))
        trace.note("max_walk_laws_a_trade", trace.trade["laws"])
        trace.trade = None
        trace.sample("trade")
        return out

    def walk_law(G, L, s, n):
        out = orig["walk_law"](G, L, s, n)
        if trace.trade is not None:
            trace.trade["laws"] += 1
        trace.note("max_walk_outcomes", len(out))
        trace.sample("walk_law")
        return out

    def concat(parts):
        out = orig["concat"].__func__(parts)
        trace.sample("concat")
        return out

    def merged(fn):
        def merge(L, rules, budget):
            trace.note("max_states_pre_merge", len(L))
            trace.sample("pre_merge")
            out = fn(L, rules, budget)
            trace.note("max_states_post_merge", len(out))
            trace.sample("merge")
            return out
        return merge

    RUN.unit_values, RUN.exact_arm, RUN.exact_moments = unit_values, exact_arm, exact_moments
    RUN._merge_paid, REP.size_counts, R.exact_centres = merged(orig["merge_paid"]), size_counts, exact_centres
    J.simulate, J.expect, J._trade_dp, J._merge = simulate, expect, trade_dp, merged(orig["merge"])
    J.Lanes.concat, RD.walk_law = staticmethod(concat), walk_law
    try:
        yield
    finally:
        RUN.unit_values, RUN.exact_arm, RUN.exact_moments = orig["unit_values"], orig["exact_arm"], orig["exact_moments"]
        RUN._merge_paid, REP.size_counts, R.exact_centres = orig["merge_paid"], orig["size_counts"], orig["exact_centres"]
        J.simulate, J.expect, J._trade_dp, J._merge = orig["simulate"], orig["expect"], orig["trade_dp"], orig["merge"]
        J.Lanes.concat, RD.walk_law = orig["concat"], orig["walk_law"]


# ----------------------------------------------------------------------------------------- the history


def a2_task(history: int, *, part_id: int, roles: Sequence[str], M: int = H.SEEDS, starts: Sequence[int] = H.STARTS,
            horizon: int = H.HORIZON, j_prime: int = H.J_PRIME, s1_params: S1.S1Params = H.S1_PARAMS_EXACT,
            rules: J.ToyRules = H.TOY_RULES_EXACT, cap_mb: float = RUN.TOTAL_CAP_MB) -> RUN.HistoryTask:
    """A2's task for one history, as `run_a2` builds it (`h3a_run._tasks`, its `half`), the cap replaced by `cap_mb`."""
    half = ((0, int(M)), (0, int(M)))
    return RUN._tasks("A2", part_id, roles, [int(history)], M, starts, horizon, j_prime, half, s1_params, rules,
                      cap_mb)[0]


def exact_only(task: RUN.HistoryTask) -> dict:
    """The exact program's stages of `a2_history` alone, called as it calls them (both arms' `exact_arm` with the
    memory guard, then `three_way_runner.exact_centres`), with a placeholder of the bytes `a2_history` holds through
    them (both arms' four per-unit matrices, written so their pages are resident); the values dropped. Returns a record
    in `a2_history`'s form (no rows; a refusal recorded as `a2_history` records it)."""
    mem = RUN.MemoryGuard(task.cap_mb)
    RUN.check_seed_use(task.part, task.part_id, task.roles)
    rec = RUN._base(task)
    h_seed, c_seed = (S.issue(r) for r in task.roles)
    hist = S1.generate(h_seed, task.part_id, task.history, task.s1_params)
    f_sch, b_sch = (S1.schedule(spec, hist) for spec in H.A2_PAIR)
    plan = RUN._plan(task, c_seed, 0, task.M)
    held = np.ones((2, len(RUN.DIM_NAMES) + 1, len(task.starts), int(task.M)))
    try:
        RUN.exact_arm(f_sch, task.rules, plan, mem.check)
        RUN.exact_arm(b_sch, task.rules, plan, mem.check)
        R.exact_centres(f_sch, b_sch, task.rules, plan)
    except Exception as exc:                                # noqa: BLE001 -- only the recorded refusals
        if not RUN._caught(exc):
            raise
        rec["premise"].append(RUN._premise(task, "run", "all", "run", RUN._refusal_kind(exc), True, None, str(exc)))
    del held
    return RUN._finish(rec, mem)


def rows_sha256(rec: dict, j: int) -> str:
    """The sha256 of the history's records file as the runner writes it: `h3a_run._Part._write_block`'s frame,
    written by `to_csv(..., index=False)` (the vendored writer's call) into a temporary folder, hashed, removed."""
    got: list = []
    part = RUN._Part("A2", "h3a_a2", lambda df, name, d, prm: got.append(df), {"j": int(j),
                                                                               "histories": [rec["history"]]})
    part._write_block([rec])
    with tempfile.TemporaryDirectory(prefix="q187_") as d:
        p = Path(d) / "h.csv"
        got[0].to_csv(p, index=False)
        return hashlib.sha256(p.read_bytes()).hexdigest()


def history_summary(rec: dict) -> dict:
    """The record reduced to sizes: its row count, and a refusal of the run itself (`null_class == "run"`: memory,
    a term out of range, a key guard) by its kind, with its message only for memory. No premise's result."""
    run = [p for p in rec["premise"] if p["null_class"] == "run"]
    out = {"kind": "history", "history": int(rec["history"]), "rows_n": len(rec["rows"]),
           "mem_peak_mb": float(rec["mem_peak_mb"]), "run_refusal": run[0]["check"] if run else ""}
    if run and run[0]["check"] == "memory":
        out["memory_detail"] = run[0]["detail"]
    return out


def diagnose(task: RUN.HistoryTask, *, abort_mb: float, emit: Callable[[dict], None], exact: bool = False,
             top: int = 12, frames: int = 3, trace_malloc: bool = True, mode: str = "fixed",
             start_lines: bool = True, read: Callable[..., float] | None = None) -> tuple[dict, Trace]:
    """One history of A2 under the trace and the mode's reader: `a2_history(task)` itself (or `exact_only`), every
    hook outcome-neutral. Emits each stage's (and start's) line and the history's summary (`history_summary`, its
    file's sha256 beside), and returns the record (for the tests: the run's record, never printed) and the trace."""
    started = False
    if trace_malloc and not tracemalloc.is_tracing():
        tracemalloc.start(int(frames))
        started = True
    try:
        trace = Trace(abort_mb, emit, top=top, start_lines=start_lines)
        rd = read if read is not None else reader_for(mode)
        gc.collect()
        before_tm = _mb(tracemalloc.get_traced_memory()[0]) if tracemalloc.is_tracing() else float("nan")
        ws_before = _READ()
        t0 = time.perf_counter()
        with path_reader(rd, trace), instrumented(trace):
            rec = exact_only(task) if exact else RUN.a2_history(task)
        seconds = time.perf_counter() - t0
        gc.collect()
        after_tm = _mb(tracemalloc.get_traced_memory()[0]) if tracemalloc.is_tracing() else float("nan")
        summ = history_summary(rec)
        summ.update(seconds=seconds, ws_before_mb=ws_before, ws_after_mb=_READ(), mode=mode,
                    retained_traced_mb=after_tm - before_tm, aborted=trace.aborted is not None, exact_only=bool(exact),
                    lifetime_peak_mb=_READ(peak=True), procmem_calls=trace.procmem_calls,
                    rows_sha256=rows_sha256(rec, task.j) if rec["rows"] else "")
        if trace.aborted:
            summ["abort_where"] = trace.aborted
        emit(summ)
        return rec, trace
    finally:
        if started:
            tracemalloc.stop()


def refused(rec: dict, trace: Trace) -> bool:
    return trace.aborted is not None or history_summary(rec)["run_refusal"] == "memory"


def replicate(histories: Sequence[int], *, mode: str, make_task: Callable[[int], RUN.HistoryTask], abort_mb: float,
              emit: Callable[[dict], None], read: Callable[..., float] | None = None) -> int:
    """A reused worker re-enacted: the histories in order in this one process (no `tracemalloc`, no start lines),
    each history's line carrying the process peak after it. Stops at the first refusal; returns 2 then, else 0."""
    rd = read if read is not None else reader_for(mode)
    for i, h in enumerate(histories):
        lines: list[dict] = []
        rec, trace = diagnose(make_task(int(h)), abort_mb=abort_mb, emit=lines.append, trace_malloc=False, mode=mode,
                              start_lines=False, read=rd)
        for ln in lines:
            if ln["kind"] == "history":
                ln.update(plan="replicate", sequence=",".join(str(int(x)) for x in histories), position=i)
            emit(ln)
        if refused(rec, trace):
            return 2
    return 0


def schedule_sizes(history: int, *, part_id: int, role: str, s1_params: S1.S1Params = H.S1_PARAMS_EXACT,
                   starts: Sequence[int] = H.STARTS, horizon: int = H.HORIZON) -> list[dict]:
    """A history's A2 schedules' sizes (no simulation): trades, R-10 walks, walks inside a start's window (the most,
    the mean, the windows with one), the longest walk's steps and the finest lattice step."""
    hist = S1.generate(S.issue(role), part_id, int(history), s1_params)
    out = []
    for spec in H.A2_PAIR:
        sch = S1.schedule(spec, hist)
        walks = [t for t in sch.trades if t.law == "walk"]
        per = [sum(1 for t in walks if s <= t.session < s + horizon) for s in starts]
        out.append({"kind": "sizes", "history": int(history), "schedule": sch.name, "trades": len(sch.trades),
                    "walks": len(walks), "walks_window_max": max(per) if per else 0,
                    "walks_window_mean": float(np.mean(per)) if per else 0.0,
                    "windows_with_walks": int(sum(1 for p in per if p > 0)),
                    "walk_n_max": max((t.walk_n for t in walks), default=0),
                    "walk_step_min": min((t.walk_step for t in walks), default=0)})
    return out


# ----------------------------------------------------------------------------------------- the gates and main


def check_report_path(path: Path | None, root: Path = ROOT) -> Path | None:
    """A report file is never inside the checkout (`results/` included) and never replaces a file."""
    if path is None:
        return None
    p = Path(path).resolve()
    r = Path(root).resolve()
    if p == r or r in p.parents:
        raise REP.H3ReportRefused(f"REFUSED (Q-187): the diagnostic's report is written outside the checkout, not {p}")
    if p.exists():
        raise REP.H3ReportRefused(f"REFUSED (Q-187): {p} exists; the diagnostic never replaces a file")
    return p


def reached_files(root: Path = ROOT) -> list[str]:
    """Every file of this repository the path imports (the loaded modules under `root`, the declared arithmetic that
    `h3a_run` loads by path, and `journey_measures`, which P_B's values import late), relative and sorted -- this
    script and the reader (`READER_FILE`, chosen by the mode) left out."""
    r = Path(root).resolve()
    out = {"docs/plans/scripts/three_way/three_way_arith.py", "extended/journey_measures.py"}
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f:
            continue
        p = Path(f).resolve()
        if r in p.parents and "vendor" not in p.relative_to(r).parts and p.suffix == ".py":
            out.add(p.relative_to(r).as_posix())
    out.discard(SCRIPT)
    out.discard(READER_FILE)
    return sorted(out)


def check_gates(commit: str, root: Path = ROOT) -> str:
    """Before any draw: threads, HEAD the named commit, the reached files the run's, a clean run, run.lock held by this
    job, H3's preconditions. Returns the full sha."""
    import extended.journey_measures  # noqa: F401  -- loaded now so its file is checked with the rest

    files = reached_files(root)                             # before the gate's own imports: A2's path alone
    from extended import lock_guard as LG
    from extended import results as RES

    RUN.check_threads()

    def sha(ref: str) -> str:
        r = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", f"{ref}^{{commit}}"], capture_output=True,
                           text=True, encoding="utf-8")
        if r.returncode:
            raise REP.H3ReportRefused(f"REFUSED (Q-187): {ref!r} is not a commit")
        return r.stdout.strip()
    want = sha(commit)
    if sha("HEAD") != want:
        raise REP.H3ReportRefused(f"REFUSED (Q-187): HEAD is not the named commit {want[:7]}")
    d = subprocess.run(["git", "-C", str(root), "diff", "--quiet", RUN_COMMIT, "HEAD", "--", *files])
    if d.returncode != 0:
        raise REP.H3ReportRefused(f"REFUSED (Q-187): a file A2's path reaches differs from the run's {RUN_COMMIT[:7]}")
    bad = RES.clean_run_problem()
    if bad:
        raise REP.H3ReportRefused(f"REFUSED (Q-187): the diagnostic runs only in a clean run: {bad}")
    holder = os.environ.get(LG.LOCK_HOLDER_ENV, "").strip()
    mroot = LG.main_root(root)
    lock = (mroot / LG.LOCK_NAME) if mroot is not None else None
    if not holder or lock is None or not lock.is_file() or \
            json.loads(lock.read_text(encoding="utf-8")).get("job") != holder:
        raise REP.H3ReportRefused("REFUSED (Q-187): heavy: run.lock must be held by this job (scripts/run_clean.py)")
    REP.assert_h3_preconditions(root, check_build_commit=True)
    return want


def _parse_list(s: str) -> list[int]:
    out: list[int] = []
    for part in str(s).split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        elif part.strip():
            out.append(int(part))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--commit", required=True, help="the checked-out commit (HEAD must be it)")
    ap.add_argument("--plan", default="isolate,replicate", help="isolate, replicate, or both")
    ap.add_argument("--modes", default=",".join(MODES), help="the path's reader: run, fixed, or both")
    ap.add_argument("--history", type=int, default=REFUSED_HISTORY, help="isolate's history (default: the refused)")
    ap.add_argument("--sequences", default=";".join(",".join(str(h) for h in s) for s in SEQUENCES),
                    help="replicate's workers: histories in order, workers apart by ';'")
    ap.add_argument("--exact-only", action="store_true", help="isolate: the exact program's stages alone")
    ap.add_argument("--sizes", default="0-19", help="the schedules' sizes of these histories first ('' for none)")
    ap.add_argument("--abort-mb", type=float, default=RUN.TOTAL_CAP_MB, help="the diagnostic's stop (working set)")
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--frames", type=int, default=3)
    ap.add_argument("--report", default=None, help="also write the lines here (outside the checkout, a new file)")
    ap.add_argument("--child", default=None, help=argparse.SUPPRESS)      # "isolate:<mode>" or "replicate:<mode>:<seq>"
    args = ap.parse_args(argv)
    report = check_report_path(Path(args.report) if args.report else None)
    lines: list[dict] = []

    def emit(rec: dict) -> None:
        bad = set(rec) - SIZE_KEYS
        if bad:
            raise REP.H3ReportRefused(f"REFUSED (Q-187): a line would print a key outside the sizes {sorted(bad)}")
        lines.append(rec)
        print(PREFIX + json.dumps(RUN._jsonable(rec), sort_keys=True), flush=True)

    commit = check_gates(args.commit)
    part_id, roles = S.PARTS["A2"], RUN.PART_ROLES["A2"]

    def make_task(h: int) -> RUN.HistoryTask:
        return a2_task(h, part_id=part_id, roles=roles, cap_mb=args.abort_mb)

    if args.child:
        kind, mode, *rest = args.child.split(":")
        if kind == "isolate":
            rec, trace = diagnose(make_task(args.history), abort_mb=args.abort_mb, emit=emit, exact=args.exact_only,
                                  top=args.top, frames=args.frames, mode=mode)
            return 2 if refused(rec, trace) else 0
        return replicate(_parse_list(rest[0]), mode=mode, make_task=make_task, abort_mb=args.abort_mb, emit=emit)

    emit({"kind": "setup", "commit": commit, "run_commit": RUN_COMMIT, "part": "A2", "M": H.SEEDS,
          "starts": len(H.STARTS), "horizon": H.HORIZON, "worker_cap_mb": RUN.WORKER_CAP_MB,
          "total_cap_mb": RUN.TOTAL_CAP_MB, "abort_mb": args.abort_mb, "exact_only": bool(args.exact_only),
          "projected_worker_mb": RUN.project_worker_mb("A2", H.SEEDS, len(H.STARTS), H.HORIZON,
                                                       H.TOY_RULES_EXACT.payout_lag, _READ())})
    for h in _parse_list(args.sizes):
        for rec in schedule_sizes(h, part_id=part_id, role=roles[0]):
            emit(rec)
    modes = [m for m in args.modes.split(",") if m]
    for m in modes:
        reader_for(m)                                       # refuses an unknown mode, or a run reader git lacks
    children: list[tuple[str, str, str]] = []
    plan = [p for p in args.plan.split(",") if p]
    for m in modes:
        if "isolate" in plan:
            children.append(("isolate", m, f"isolate:{m}"))
        if "replicate" in plan:
            for seq in [s for s in args.sequences.split(";") if s]:
                children.append(("replicate", m, f"replicate:{m}:{seq}"))
    code = 0
    base = [sys.executable, str(Path(__file__).resolve()), "--commit", commit, "--history", str(args.history),
            "--abort-mb", str(args.abort_mb), "--top", str(args.top), "--frames", str(args.frames), "--sizes", ""]
    for kind, m, child in children:
        cmd = base + ["--child", child] + (["--exact-only"] if args.exact_only and kind == "isolate" else [])
        with subprocess.Popen(cmd, cwd=str(ROOT), stdout=subprocess.PIPE, text=True, encoding="utf-8") as proc:
            for raw in proc.stdout:                         # the child's lines relayed (and kept for --report)
                print(raw, end="", flush=True)
                if raw.startswith(PREFIX):
                    lines.append(json.loads(raw[len(PREFIX):]))
        rc = proc.returncode
        emit({"kind": "child", "plan": child, "mode": m, "exit": int(rc)})
        code = max(code, rc)
    if report is not None:
        report.write_text("".join(json.dumps(RUN._jsonable(x), sort_keys=True) + "\n" for x in lines),
                          encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
