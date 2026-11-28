"""Synthetic unit tests for `scripts/h3a_a2_diag.py` (Q-187: the failure protocol's component in isolation for
H3-A's slot A2).

**Seeds (B-3):** every draw is the tests' seed in the tests' part (`three_way_seeds.issue("tests")`), passed as the
roles; tiny S1 toys only (`test_h3a_run`'s `TINY_X`, A2's settings). Never reads bars or writes `results/`; the CLI's
refusal runs in a subprocess, so `extended.results` is never imported in the fast-tier process (Q-204).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from extended import h3a_report as REP
from extended import three_way_h3a as H
from extended import three_way_journey as J
from extended import three_way_redraw as RD
from extended import three_way_runner as R
from extended import three_way_s1 as S1
from extended import three_way_seeds as S
from scripts import h3a_a2_diag as DIAG
from scripts import h3a_run as HR

ROOT = Path(__file__).resolve().parent.parent
TP = S.PARTS["tests"]
ROLES = ("tests", "tests")
TINY_X = S1.S1Params(n_sessions=75, vol_mean=6.0, phi=0.9, vol_sd=0.15, regime_amp=0.0, rate=0.3, rate_beta=1.0,
                     hold_mean=30.0, hold_stop=40.0, time_limit=90.0)
STARTS = (0, 1)
M, JP = 200, 20


def _history_with_a_walk() -> int:
    """The first tests' history whose A2 schedules hold an R-10 walk inside a start's window (the program's branching
    beyond the race's two outcomes is then exercised)."""
    seed = S.issue("tests")
    for h in range(60):
        hist = S1.generate(seed, TP, h, TINY_X)
        for spec in H.A2_PAIR:
            sch = S1.schedule(spec, hist)
            if any(t.law == "walk" and t.session < STARTS[-1] + H.HORIZON for t in sch.trades):
                return h
    raise AssertionError("no tests' history with a walk in its windows")


@pytest.fixture(scope="module")
def walk_history() -> int:
    return _history_with_a_walk()


def _task(h: int, cap: float = 1e9, starts=STARTS) -> HR.HistoryTask:
    return DIAG.a2_task(h, part_id=TP, roles=ROLES, M=M, starts=starts, j_prime=JP, s1_params=TINY_X, cap_mb=cap)


def _originals():
    return (HR.unit_values, HR.exact_arm, HR.exact_moments, HR._merge_paid, REP.size_counts, R.exact_centres,
            J.simulate, J.expect, J._trade_dp, J._merge, J.Lanes.__dict__["concat"], RD.walk_law)


@pytest.fixture(scope="module")
def traced(walk_history):
    lines: list[dict] = []
    before = _originals()
    rec, trace = DIAG.diagnose(_task(walk_history), abort_mb=1e9, emit=lines.append)
    return rec, trace, lines, before


def test_the_traced_path_is_the_runs_path_and_every_hook_is_restored(traced, walk_history) -> None:
    """Outcome-neutral instrumentation: `a2_history` under the trace gives the record the plain call gives (rows,
    premises, centres, failures at the fill), and every wrapped function is the original again afterwards."""
    rec, _, _, before = traced
    after = _originals()
    assert all(a is b for a, b in zip(after, before))
    plain = HR.a2_history(_task(walk_history))
    assert rec["rows"] == plain["rows"] and len(rec["rows"]) == 18
    assert [repr(p) for p in rec["premise"]] == [repr(p) for p in plain["premise"]]      # NaN-aware
    assert rec["beside"] == plain["beside"] and rec["fill"] == plain["fill"]


def test_the_lines_carry_sizes_only_in_the_paths_order(traced) -> None:
    """Every printed line's keys are in `SIZE_KEYS` (no value, centre, count or premise result); the stages come in
    `a2_history`'s order; a start line a start of each simulation and each exact program (both arms in the centres)."""
    _, _, lines, _ = traced
    for ln in lines:
        assert set(ln) <= DIAG.SIZE_KEYS, set(ln) - DIAG.SIZE_KEYS
        for t in ln.get("top", []):
            assert set(t) <= DIAG.SIZE_KEYS
    stages = [(ln["stage"], ln["schedule"]) for ln in lines if ln["kind"] == "stage"]
    assert stages == [("mc", "a2_x1"), ("mc", "a2_x2"), ("exact", "a2_x1"), ("exact", "a2_x2"),
                      ("centres", "a2_x1-a2_x2"), ("counts", "")]
    starts = [ln for ln in lines if ln["kind"] == "start"]
    by = {}
    for ln in starts:
        by.setdefault(ln["stage"], []).append(ln["start"])
    assert by["mc"] == list(STARTS) * 2 and by["exact"] == list(STARTS) * 2
    assert sorted(by["centres"]) == sorted(list(STARTS) * 2)
    assert all(ln["lanes"] == M for ln in starts if ln["stage"] == "mc")
    hist = [ln for ln in lines if ln["kind"] == "history"]
    assert len(hist) == 1 and hist[0]["rows_n"] == 18 and hist[0]["run_refusal"] == "" and not hist[0]["aborted"]


def test_the_state_counts_are_the_programs_own(traced, walk_history) -> None:
    """Each centres start's largest merged state count equals `three_way_journey.expect`'s own `states` (computed
    apart, untraced); the states before a merge are at least those after; the walks in a window are counted from the
    schedule apart; a window with a walk reads a walk law with more outcomes than the race's two."""
    _, _, lines, _ = traced
    seed = S.issue("tests")
    hist = S1.generate(seed, TP, walk_history, TINY_X)
    sch = {s.name: S1.schedule(s, hist) for s in H.A2_PAIR}
    seen_walk = False
    for ln in (x for x in lines if x["kind"] == "start" and x["stage"] in ("exact", "centres")):
        assert ln["max_states_pre_merge"] >= ln["max_states_post_merge"] >= 1
        sc = sch[ln["schedule"]]
        walks = sum(1 for t in sc.trades if t.law == "walk" and ln["start"] <= t.session < ln["start"] + H.HORIZON)
        assert ln["walks_in_window"] == walks
        if walks:
            seen_walk = True
            assert ln["max_walk_outcomes"] > 2 and ln["max_walk_laws_a_trade"] >= 1
        if ln["stage"] == "centres":
            want = J.expect(sc, H.TOY_RULES_EXACT, ln["start"], H.HORIZON, block_sessions=TINY_X.n_sessions,
                            budget=H.BUDGET)["states"]
            assert ln["max_states_post_merge"] == want
    assert seen_walk


def test_the_diagnostic_stop_refuses_at_its_first_sample_and_names_the_stage(walk_history) -> None:
    """A positive control of the stop: at 1 MB the first sample (the first simulated start) refuses, recorded as
    `a2_history` records a memory refusal (no rows), the stage printed as aborted and the history's line naming where."""
    lines: list[dict] = []
    before = _originals()
    rec, trace = DIAG.diagnose(_task(walk_history, cap=1.0), abort_mb=1.0, emit=lines.append, trace_malloc=False)
    summ = DIAG.history_summary(rec)
    assert trace.aborted == "mc/simulate"
    assert summ["run_refusal"] == "memory" and summ["rows_n"] == 0 and "diagnostic's stop" in summ["memory_detail"]
    st = [ln for ln in lines if ln["kind"] == "stage"]
    assert len(st) == 1 and st[0]["aborted"] and st[0]["abort_where"] == "mc/simulate"
    assert all(a is b for a, b in zip(_originals(), before))


def test_retention_after_a_history_is_measured_and_a_planted_leak_is_seen(walk_history, monkeypatch) -> None:
    """The diagnosis's claim that nothing outlives a history: after a warm-up, a second history's traced memory after
    it is within a fraction of a megabyte of before; with a planted leak (a 4 MB array kept by a hook across the
    history) the same reading sees it."""
    one = (STARTS[0],)
    DIAG.diagnose(_task(walk_history, starts=one), abort_mb=1e9, emit=lambda r: None, exact=True, frames=1)
    lines: list[dict] = []
    DIAG.diagnose(_task(walk_history, starts=one), abort_mb=1e9, emit=lines.append, exact=True, frames=1)
    clean = [ln for ln in lines if ln["kind"] == "history"][0]
    assert abs(clean["retained_traced_mb"]) < 0.5
    kept: list[np.ndarray] = []
    orig = HR.exact_arm

    def leaky(*a, **kw):
        kept.append(np.ones(2 ** 19))                       # 4 MB that outlive the history
        return orig(*a, **kw)
    monkeypatch.setattr(HR, "exact_arm", leaky)
    lines = []
    DIAG.diagnose(_task(walk_history, starts=one), abort_mb=1e9, emit=lines.append, exact=True, frames=1)
    leak = [ln for ln in lines if ln["kind"] == "history"][0]
    assert leak["retained_traced_mb"] > 7.5                 # two arms, 4 MB each
    assert [ln["stage"] for ln in lines if ln["kind"] == "stage"] == ["exact", "exact", "centres"]


def test_schedule_sizes_count_the_walks() -> None:
    seed = S.issue("tests")
    rows = DIAG.schedule_sizes(0, part_id=TP, role="tests", s1_params=TINY_X, starts=STARTS)
    hist = S1.generate(seed, TP, 0, TINY_X)
    assert [r["schedule"] for r in rows] == [s.name for s in H.A2_PAIR]
    for r, spec in zip(rows, H.A2_PAIR):
        assert set(r) <= DIAG.SIZE_KEYS
        sch = S1.schedule(spec, hist)
        walks = [t for t in sch.trades if t.law == "walk"]
        assert r["trades"] == len(sch.trades) and r["walks"] == len(walks)
        per = [sum(1 for t in walks if s <= t.session < s + H.HORIZON) for s in STARTS]
        assert r["walks_window_max"] == max(per) and r["windows_with_walks"] == sum(p > 0 for p in per)


def test_a_report_is_never_written_inside_the_checkout(tmp_path) -> None:
    for bad in (ROOT / "results" / "h3a_a2_diag.jsonl", ROOT / "diag.jsonl", ROOT):
        with pytest.raises(REP.H3ReportRefused, match="outside the checkout"):
            DIAG.check_report_path(bad)
    ok = tmp_path / "diag.jsonl"
    assert DIAG.check_report_path(ok) == ok.resolve()
    ok.write_text("x", encoding="utf-8")
    with pytest.raises(REP.H3ReportRefused, match="never replaces"):
        DIAG.check_report_path(ok)
    assert DIAG.check_report_path(None) is None


def test_the_reached_files_are_the_paths_own() -> None:
    files = DIAG.reached_files()
    for f in ("scripts/h3a_run.py", "extended/three_way_journey.py", "extended/three_way_runner.py",
              "extended/h3a_report.py", "docs/plans/scripts/three_way/three_way_arith.py",
              "extended/journey_measures.py"):
        assert f in files
    assert DIAG.SCRIPT not in files and DIAG.READER_FILE not in files                  # the reader is the mode's
    assert not any(f.startswith("vendor/") for f in files)


def test_the_cli_refuses_outside_a_clean_run_before_any_draw() -> None:
    """The gates come before any draw: outside a clean run (or at a path that is not the run's) the CLI refuses and
    prints no `DIAG ` line."""
    env = {k: v for k, v in os.environ.items() if k not in ("S2X_CLEAN_RUN", "S2X_LOCK_HOLDER")}
    env["OMP_NUM_THREADS"] = "1"
    proc = subprocess.run([sys.executable, str(ROOT / DIAG.SCRIPT), "--commit", "HEAD", "--sizes", ""], cwd=str(ROOT),
                          env=env, capture_output=True, text=True, timeout=120)
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0 and "REFUSED (Q-187)" in out
    assert DIAG.PREFIX not in proc.stdout


def test_the_file_hash_is_the_runners_own_file(walk_history, tmp_path) -> None:
    """`rows_sha256` is the sha256 of the file the runner writes for the history: `run_a2` with a sink that writes
    each frame by the vendored writer's call (`to_csv(..., index=False)`) into a temporary folder gives the same hash."""
    import hashlib

    def sink(df, name, description, parameters):
        df.to_csv(tmp_path / f"{name}.csv", index=False)
    HR.run_a2(part_id=TP, roles=ROLES, sink=sink, histories=(walk_history,), M=M, starts=STARTS, j_prime=JP,
              s1_params=TINY_X, workers=1, cap_mb=1e9)
    want = hashlib.sha256((tmp_path / f"h3a_a2_h{walk_history:03d}.csv").read_bytes()).hexdigest()
    lines: list[dict] = []
    DIAG.diagnose(_task(walk_history), abort_mb=1e9, emit=lines.append, trace_malloc=False, start_lines=False)
    hist = [ln for ln in lines if ln["kind"] == "history"][0]
    assert hist["rows_sha256"] == want
    assert not [ln for ln in lines if ln["kind"] == "start"]


def test_a_reused_process_reproduces_each_history_bit_for_bit(walk_history) -> None:
    """The replication's premise: a history run after another in one process gives the file it gives alone (its
    sha256), and each line names its sequence and place."""
    lines: list[dict] = []
    code = DIAG.replicate((walk_history, walk_history + 1, walk_history), mode="fixed", make_task=_task,
                          abort_mb=1e9, emit=lines.append)
    hs = [ln for ln in lines if ln["kind"] == "history"]
    assert code == 0 and [ln["position"] for ln in hs] == [0, 1, 2]
    assert hs[0]["rows_sha256"] == hs[2]["rows_sha256"] != hs[1]["rows_sha256"]
    assert all(set(ln) <= DIAG.SIZE_KEYS for ln in lines)


def test_the_run_reader_is_called_at_every_guard_reading_and_leaves_its_classes_behind(walk_history, traced) -> None:
    """The mechanism, on the run's own reader (git's copy at the run's commit): the path reads memory once a simulated
    start, once a close of the exact program and once at the end -- 2 T + 2 T h + 1 for T starts and horizon h (the
    full path, untraced), 2 T h + 1 for the exact stages alone --, and with the run's reader every such reading stays
    traced after the history; with this commit's it does not."""
    try:
        run_read = DIAG.run_reader()
    except REP.H3ReportRefused:
        pytest.skip("the run's commit is not in this clone")
    if not np.isfinite(run_read()):
        pytest.skip("psapi is Windows'")
    lines: list[dict] = []
    DIAG.diagnose(_task(walk_history), abort_mb=1e9, emit=lines.append, mode="run", trace_malloc=False,
                  start_lines=False)
    full = [ln for ln in lines if ln["kind"] == "history"][0]
    assert full["procmem_calls"] == 2 * len(STARTS) + 2 * len(STARTS) * H.HORIZON + 1
    one = (STARTS[0],)
    calls = 2 * H.HORIZON + 1
    out = {}
    for mode in ("fixed", "run", "fixed"):
        lines = []
        DIAG.diagnose(_task(walk_history, starts=one), abort_mb=1e9, emit=lines.append, mode=mode, exact=True,
                      frames=1, start_lines=False)
        out[mode] = [ln for ln in lines if ln["kind"] == "history"][0]
    assert out["run"]["procmem_calls"] == out["fixed"]["procmem_calls"] == calls
    assert out["run"]["retained_traced_mb"] * 2 ** 20 > calls * 1024
    assert abs(out["fixed"]["retained_traced_mb"]) < 0.5
    fixed_full = [ln for ln in traced[2] if ln["kind"] == "history"][0]                # the fixture: this reader
    assert full["rows_sha256"] == fixed_full["rows_sha256"] != ""                      # the reader moves no record


def test_the_cli_children_print_sizes_only(walk_history, monkeypatch, capsys) -> None:
    """The CLI's two child kinds in-process, the gates and the task replaced by the tests' (the declared roles never
    drawn here): each prints `DIAG ` lines of `SIZE_KEYS` only and exits 0; the parent's setup line too."""
    import json
    monkeypatch.setattr(DIAG, "check_gates", lambda commit, root=ROOT: "0" * 40)
    task = _task(walk_history)                              # built before the patch (`_task` calls `a2_task`)
    monkeypatch.setattr(DIAG, "a2_task", lambda h, **kw: task)
    base = ["--commit", "x", "--history", str(walk_history), "--sizes", ""]
    assert DIAG.main(base + ["--child", "isolate:fixed", "--exact-only", "--frames", "1"]) == 0
    assert DIAG.main(base + ["--child", f"replicate:fixed:{walk_history}"]) == 0
    assert DIAG.main(base + ["--plan", "", "--modes", "fixed"]) == 0
    out = [ln for ln in capsys.readouterr().out.splitlines() if ln.startswith(DIAG.PREFIX)]
    recs = [json.loads(ln[len(DIAG.PREFIX):]) for ln in out]
    assert {r["kind"] for r in recs} == {"stage", "start", "history", "setup"}
    assert all(set(r) <= DIAG.SIZE_KEYS for r in recs)
    assert [r["plan"] for r in recs if r["kind"] == "history" and "plan" in r] == ["replicate"]
