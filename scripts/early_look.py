"""Q-213: an early look -- ONE trading design on the user-journey scorecard on the search years.

**EXPLORATORY. It decides nothing and cannot be cited for a verdict.** It spends no k, is no registration, reads no
held-out date (nothing from 2024-01-02) and never NQ from 2026-07-17. Every output carries `exploratory: true` and
the sentence `LABEL` below.

    python scripts/early_look.py plan                      # prints the declaration below; reads nothing
    python scripts/early_look.py synthetic --out <dir>     # the toy end-to-end (no bar): result + page in <dir>
    python scripts/run_clean.py --name q213-early-look --hours 3 --mem-gb 3 --task Q-213 -- python scripts/early_look.py run
    python scripts/early_look.py summary                   # after --collect: docs/plans/EARLY_LOOK.md from the files

**The route** (the lead's ruling (A) on the Q-213 hand-back): the design's own trigger becomes a trade table
(`extended.design_trades`), which feeds the vendored `rc_campaign` job (P-16's money side: the no-closure table, the
20/21 budget, five seats, the strict five-minute gap -- the job H4's naive coin is run on), the firm path's baseline mode
`three_way_baseline.simulate(..., outcome="race")` (every outcome redrawn at its bracket's driftless odds, R-10's walk
for a flatten; CHARTER 3.2) and H4's `summarise_baseline_readings` -- one convention with H4-B. The bars are read only
inside `extended.search_cut` (cut at 2023-12-29), after `search_cut.authorise` (the reader's door for the engine's
read, `extended.reader`), as H4's builders read them.

**The design, fixed here before any run** (the lead's ruling (C): RL3's draft's declared base cell, nothing chosen
after an outcome). The draft is `prereg/DRAFT_F-RL3_resting_levels.md` (third text, 2026-11-18, never pinned, never
run; LF sha256 `DRAFT_SHA256`, checked at the run). Line numbers are that text's:
- level kind `pd`, the prior regular session's high and low (searched; line 552 lists `pd`, `on`, `pdc`, `rn100`, `pd`
  first; line 463 numbers the cells with `fade` `pd` first, g = 0; line 321 defines the level);
- side rule `fade` at both levels: a sell limit at the high, a buy limit at the low (searched; line 553, `fade` first;
  line 463);
- stop 50 ticks, 12.5 points (searched; line 554, the first of 50, 100, 150; line 464, s = 0);
- R: the money side's menu (line 987: the journey reads "the pick's own rule-side trades at every R of the base's
  carried menu"); the trades are walked at all twelve R of FV3's grid as the naive coin's are, and the job's state
  policy picks each account's R. R's first grid value (line 555: 1, 1.5, 3; line 465, r = 0) is the cell of the
  draft's lift readings (stages A to C), which this look does not make;
- cutoff 14:30 CT (line 574: "the latest of 14:30, 14:00, ..., 10:00 CT passing 7.2 item 2", the first listed; line
  218: "14:30 at the latest"). **Interpretation, said:** the draft reads the cutoff on the choice block (its 7.2 item
  2, a resolution count); this look reads nothing to choose it and takes the first listed value;
- latency-free (line 556): the information from bars stamped at or before 08:29 (line 557), the alert 08:30 (line
  558), live from the bar stamped 09:00 (line 559), `P_ref` the 08:29 bar's close, a day without it void (line 560),
  void if already through at 09:00 (line 561);
- fills: a limit only on a trade through by a tick, at its price (line 566); costs Stage 2's at the stop, exit ticks
  1 / 0 / 2, no entry tick on a resting fill (line 573); the walk to the bar ending 15:08 CT, flattened at the worst
  of 15:08-15:10 less two ticks, no stop move (line 572; `triggers.JOURNEY`);
- the two tickets of the kind one-cancels-other (line 967);
- news windows: those the record verifies (line 563), none added beyond H4's calendar convention (`day_calendar`:
  BLS, FOMC, the voids; the closed 08:30-08:59 window), as the draft states the record's windows all fall before
  09:00 on a non-void day (line 280).
**Interpretation, said:** the draft's own journey (its 11.2, line 940) adds the tickets to a base (P-14 for a 50-tick
pick); the lead's route runs the tickets alone on the naive coin's job, P-16's money side. The look is that design.

**The seeds** (the lead's ruling 3): one new exploratory block, code-owned here and nowhere else (`SEED_BLOCK`,
held by `tests/test_early_look.py`'s guard: found in no other file of this tree or any ref), each seed one role
(`ROLES`), the spares drawn by nothing. Searched before it was written: no token of the block on any ref, worktree or
the main tree. Parts: `PART`, one field value for every key of this look (the seeds are this look's own).

**The units** (declared here, before any run): every start day of the search calendar (H4-B's starts), `J_SEEDS` seed
indices `0 .. J_SEEDS - 1` each, the horizon min(252, the sessions left) (H4-B's `JM.YEAR`), the deciding arm only (`off`,
the martingale-outcome reading; no stress arm, no exact-run re-check), the 1 % audit sample re-derived by H4's
independent oracle (`h4_audit.verify_race_trade_row`). At most `WORKERS` processes, one BLAS thread each.

**Expected cost** (an estimate, not a result): about 33,000 units (every start of the search calendar, `J_SEEDS`
seeds), H4-B's unit cost on P-14 (its logs: about a quarter of a second a full-horizon unit a worker) at two workers,
about 70 minutes, plus the build (the cut's inputs, the bars as arrays, the trades, the job) of some minutes: about
1.5 hours, run.lock asked for 3; peak memory estimated below 3 GB (the parent's bars as arrays and units, two
workers each holding the job). The synthetic mode times a unit on toys.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Mapping, Sequence

if __name__ == "__main__":
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import design_trades as DT  # noqa: E402
from extended import h4_audit as HA  # noqa: E402
from extended import h4_coin_source as CS  # noqa: E402
from extended import journey_measures as JM  # noqa: E402
from extended import reader as RDR  # noqa: E402
from extended import three_way_baseline as TB  # noqa: E402
from extended import three_way_journey as J  # noqa: E402
from extended import three_way_keys as K  # noqa: E402
from extended import triggers as T  # noqa: E402
from extended import walker as W  # noqa: E402
from extended import wave42 as W42  # noqa: E402

SCRIPT = "scripts/early_look.py"
TASK = "Q-213"
LABEL = ("EXPLORATORY (Q-213): an early look at one design on the search years; it decides nothing, spends no k "
         "and cannot be cited for a verdict")

# ------------------------------------------------------------------------------------------------ the declaration
DESIGN = "rl3_pd_fade"
DRAFT = "prereg/DRAFT_F-RL3_resting_levels.md"
DRAFT_SHA256 = "a09c1e1fd3887e7ce559e72e47e48bae8f5a38263abfe8539a3ffc401992d431"
KIND = "pd"
RULE = {"hi": "fade", "lo": "fade"}
STOP_TICKS = 50
CUTOFF = W.slot(14, 30)
LAST = "2023-12-29"                       # the search years' last day (E-208); nothing later is read
LATENCY = 0.0                            # latency-free: (30)'s screen hours read no wait (H4's P-16 / P-15 value)

# ------------------------------------------------------------------------------------------------ the seeds
#: the early look's own block (Q-213; searched 2026-11-27 on every ref, worktree and the main tree: no token of it)
SEED_BLOCK = (20267130, 20267131, 20267132, 20267133, 20267134, 20267135, 20267136, 20267137, 20267138, 20267139)
ROLES = {"el_coins": SEED_BLOCK[0], "el_sample": SEED_BLOCK[1], "el_tests": SEED_BLOCK[2]}
STATUS = {"el_coins": "exploratory reading: the coin field of every unit (the race, R-10's walk, the missed draw)",
          "el_sample": "exploratory audit: the 1 % sample of units re-derived by H4's oracle",
          "el_tests": "tests: the synthetic toys' bars and starts",
          **{f"el_spare_{k}": "spare, drawn by nothing" for k in range(3, 10)}}
PART = 0                                 # the key field of every draw of this look (its seeds are its own)

# ------------------------------------------------------------------------------------------------ the units
J_SEEDS = 32
START_STEP = 1                           # every start of the search calendar
HORIZON = JM.YEAR                        # 252 sessions, cut to the sessions left
WORKERS = 2
BATCH = 21

RESULT = f"early_look_{DESIGN}"
SUMMARY = "docs/plans/EARLY_LOOK.md"
H4B_P14 = "results/h4_readings_p14_p*.csv"
BESIDE_LABEL = "H4-B, pending its exact-run treatment (B-2)"


class EarlyLookRefused(RuntimeError):
    """A refusal of this look (a held-out date, a dirty tree, a seed outside its role, a file that does not verify)."""


def issue(role: str) -> int:
    """The block's seed for `role`; refused for an unknown role and for a spare."""
    if role not in STATUS:
        raise EarlyLookRefused(f"REFUSED: {role!r} is no role of the early look's block")
    if role not in ROLES:
        raise EarlyLookRefused(f"REFUSED: {role!r} is a spare, drawn by nothing")
    return int(ROLES[role])


def check_last(last: Any) -> date:
    """Refuse a last day after the search years' (E-208) -- the held-out years begin 2024-01-02."""
    d = date.fromisoformat(str(last)[:10])
    if d > RDR.CHOICE_END:
        raise EarlyLookRefused(f"REFUSED (E-208): the early look reads the search years only; {d} is after "
                               f"{RDR.CHOICE_END}")
    return d


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def git_dirty(repo: Path) -> list[str]:
    """The tree's uncommitted changes (tracked or untracked, not ignored), `git status --porcelain`."""
    r = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=repo, capture_output=True,
                       text=True, encoding="utf-8")
    if r.returncode:
        raise EarlyLookRefused(f"REFUSED: git status failed in {repo}: {r.stderr.strip()[:200]}")
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def require_clean(repo: Path) -> None:
    """Refuse to write from a dirty tree: a result is written only from a committed state."""
    bad = git_dirty(repo)
    if bad:
        raise EarlyLookRefused(f"REFUSED: the tree {repo} is dirty ({len(bad)} change(s), first {bad[0]!r}); a result "
                               "is written only from a clean checkout of a committed commit")


def _h4() -> Any:
    """H4's runner as a module (its `summarise_baseline_readings` and its audit row formatter: one convention)."""
    name = "h4_rebaseline_for_early_look"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / "h4_rebaseline.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------------------------------------ the units


_CTX: dict[str, Any] = {}


def _init(ctx: dict[str, Any]) -> None:
    from extended import use_vendored_stage2

    use_vendored_stage2()
    _CTX.clear()
    _CTX.update(ctx)


def subs_of(facts: Mapping[tuple[int, int], TB.TradeFacts]) -> dict[tuple[int, int], int]:
    subs: dict[tuple[int, int], int] = {}
    at: dict[tuple[int, int], int] = {}
    for i, j in sorted(facts):
        m = (int(i), int(facts[(i, j)].decision))
        subs[(int(i), int(j))] = at.get(m, 0)
        at[m] = at.get(m, 0) + 1
    return subs


def run_chunk(starts: list[int]) -> dict[str, Any]:
    """Every unit (start, seed index) of `starts` on the deciding arm: H4-B's chunk, its `off` arm only."""
    c = _CTX
    dates, blocks, args, facts = c["dates"], c["blocks"], c["args"], c["facts"]
    coin, sample = int(c["coin_seed"]), int(c["sample_seed"])
    seeds = tuple(c["seed_indices"])
    n = len(dates)
    units, trades, oracle = [], [], 0
    guard = K.KeyGuard.sampled(starts, seeds)
    for s in starts:
        sl = n - int(s)
        obs = min(int(c["horizon"]), sl)
        rec = TB.simulate(blocks, args, facts, int(s), seeds, obs, seed=coin, part=PART, history=0, block_sessions=n,
                          dates=dates, arm=J.ArmSpec(), guard=guard, outcome="race", keep_paths=True, log=True,
                          calendar=c["calendar"])
        for jl, ci in enumerate(seeds):
            lg = rec.logs[jl]
            taken = [{"day_idx": int(r["i"]), "fill_bar": int(facts[(int(r["i"]), int(r["j"]))].entry),
                      "exit_bar_at_R": _exit_at(blocks, r), "law": r.get("law")}
                     for r in lg if r.get("law") not in ("missed", "day_end")]
            ov = HA.assert_zero_strict_overlaps(taken, what=f"{DESIGN}/start={dates[s]}/seed={ci}")
            beside = {"move_trades": int(rec.move_trades[jl]), "b_redrawn": int(rec.b_redrawn[jl]),
                      "b_historical": int(rec.b_historical[jl]), "be_differs": int(rec.be_differs[jl]),
                      "be_unrecorded": int(rec.be_unrecorded[jl]), "tb_overlaps": int(rec.overlaps[jl])}
            units.append(HA.extract_unit_measures(
                baseline=DESIGN, arm="off", reading=W42.READING, start=int(s), start_date=dates[s], seed_index=ci,
                sessions_left=sl, rel=rec.rel[jl], first_pass=int(rec.first_pass[jl]), first_pay=int(rec.first_pay[jl]),
                arrivals=rec.arrivals[jl], path=rec.paths[jl], log_rows=lg, blocks=blocks, latency=LATENCY,
                strict_overlaps=ov, beside_counts=beside, payout_lag=int(args["path"]["payout_lag_days"])))
            if c.get("sample_all") or HA.is_sampled_unit(int(s), int(ci), seed=sample, part=PART):
                rows = _h4()._format_sampled_trade_rows(DESIGN, "off", W42.READING, int(s), dates[s], int(ci), dates,
                                                        blocks, facts, c["subs"], J.ArmSpec(), lg)
                for tr in rows:
                    HA.verify_race_trade_row(tr, seed=coin, part=PART, history=0)
                    oracle += 1
                trades.extend(rows)
    return {"units": units, "trades": trades, "oracle": oracle, "keys": guard.checked}


def _exit_at(blocks: Sequence[Any], r: Mapping[str, Any]) -> float:
    b, j, R = blocks[int(r["i"])], int(r["j"]), float(r["R"])
    ex = getattr(b, "exit_by_rr", None)
    if ex is not None and R in ex and math.isfinite(float(ex[R][j])):
        return float(ex[R][j])
    return float(b.exit_t[j])


def run_units(ctx: dict[str, Any], starts: Sequence[int], workers: int) -> dict[str, Any]:
    chunks = [list(starts[k:k + BATCH]) for k in range(0, len(starts), BATCH)]
    t0 = time.perf_counter()
    out: list[dict[str, Any]] = []
    w = max(1, min(int(workers), WORKERS))
    if w == 1 or len(chunks) <= 1:
        _init(ctx)
        for ch in chunks:
            out.append(run_chunk(ch))
    else:
        with cf.ProcessPoolExecutor(max_workers=w, initializer=_init, initargs=(ctx,)) as ex:
            futs = [ex.submit(run_chunk, ch) for ch in chunks]
            for k, f in enumerate(futs, 1):
                out.append(f.result())
                print(f"  [{DESIGN}] batch {k}/{len(chunks)}, {time.perf_counter() - t0:.1f}s", flush=True)
    return {"units": pd.DataFrame([u for o in out for u in o["units"]]),
            "oracle": int(sum(o["oracle"] for o in out)), "keys": int(sum(o["keys"] for o in out)),
            "seconds": time.perf_counter() - t0}


def readings(units: pd.DataFrame, dates: Sequence[str]) -> pd.DataFrame:
    """H4's readings of the units (MEASURES 1.4), each row labelled exploratory."""
    df = _h4().summarise_baseline_readings(units, dates, DESIGN)
    df["comparator_label"] = "exploratory design (Q-213), not a comparator"     # H4 labels its baselines here
    df.insert(0, "exploratory", True)
    df.insert(1, "label", LABEL)
    return df


def write(df: pd.DataFrame, results_dir: Path | None, params: dict[str, Any], repo: Path) -> Path:
    """The result file and its manifest through `extended.results` (refusing a dirty tree first)."""
    from extended import results as RES

    require_clean(repo)
    p, _ = RES.write_result(df, RESULT, script=SCRIPT, seed=issue("el_coins"), parameters=params,
                            results_dir=results_dir, exploratory=True, prereg_id=None,
                            description=f"{LABEL}. RL3's draft base cell ({DESIGN}) through the firm path's baseline "
                                        "mode (race), H4-B's readings beside in the summary.")
    return Path(p)


# ------------------------------------------------------------------------------------------------ the real run


def build(root: Path = ROOT) -> dict[str, Any]:
    """The design's search-year trade table, job and facts (inside `search_cut`, cut at `LAST`)."""
    from extended import VENDOR_STAGE2, use_vendored_stage2
    from extended import day_calendar as DC
    from extended import search_cut as SC
    from extended import three_way_firm as TF

    check_last(LAST)
    if lf_sha256(root / DRAFT) != DRAFT_SHA256:
        raise EarlyLookRefused(f"REFUSED: {DRAFT} is not the text this look's header cites")
    use_vendored_stage2()
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import rc150_dev_test as R150
    import rc_dev_test as D
    import rc_screen as RS
    import user_journey as UJ
    import zero_edge_decomposition as zd

    reg = SC.load_constants(root / HA.H4_REG_CONSTANTS_REL, expected_sha256=HA.H4_REG_CONSTANTS_SHA256)
    cal_src = DC.load_sources(flags=root / "results" / "h2_overnight_flags.csv", manifest=TF.MANIFEST,
                              calendar=root / "config" / "calendar_early_closes.csv")
    SC.authorise(purpose="early_look_search_years", declaration=None,
                 what=f"Q-213 early look {DESIGN} through search_cut up to {LAST}", last=LAST, bars=True,
                 root=VENDOR_STAGE2)
    spec = DT.rl3_spec(KIND, CUTOFF, RULE, STOP_TICKS, name=DESIGN)
    with SC.cut(last=LAST, root=VENDOR_STAGE2) as cut_log:
        I_in = RS.inputs()
        L = I_in["L"]
        cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
        days_df = L["days"].copy()
        days_df["date"] = days_df["date"].astype(str)
        days_df = days_df.sort_values("date", kind="stable").reset_index(drop=True)
        days = days_df["date"].tolist()
        SC.check_calendar(days, calendar_path=root / HA.H4_SEARCH_CALENDAR_REL, last=LAST)
        day_kinds = dict(zip(days_df["date"], days_df["day_kind"].astype(str)))
        arr_fn = A.bar_arrays(dict(cfg), list(days))
        arrays = {str(d): arr_fn(str(d)) for d in days}
        fees = A.fee_by_stop(fcfg, (STOP_TICKS,), tv)
        crr = float(fcfg["state_policy"]["fresh"]["combine_rr"])
        rr_grid = A.rrs(cfg)
        keys = sorted(set(float(R) for R in rr_grid) | set(zd.policy_rrs(I_in["plan"])))
        problems = cut_log.problems()
        if problems:
            raise EarlyLookRefused(f"REFUSED (search_cut): {problems}")
        cut_summary = cut_log.manifest_summary()
    HA.check_job_ends_search_window(days, f"Q-213 {DESIGN}")
    hist = DT.history_from_arrays(days, arrays)
    del arrays
    ctxs = {i: T.context_for(spec.source, cal_src, date.fromisoformat(d), i, rules=spec.rules)
            for i, d in enumerate(days)}
    out = DT.build_trades(spec, hist, lambda i: ctxs[i], day_kinds=day_kinds, rr_grid=rr_grid, fresh_rr=crr,
                          fee_micro_eq=float(fees[STOP_TICKS]), tick_value=tv,
                          market_entry_ticks=float(cfg["slip_ticks"]), tick=float(cfg["contract"]["tick"]))
    t_pad = zd.pad(out.trades, keys) if len(out.trades) else out.trades
    _, e_by, lb_by, _, _ = A.bounds(t_pad, days, B.rrs(t_pad), cfg)
    cap = max(int(reg["p16"]["capacity"]), int(B.capacity(t_pad, fcfg)))
    camp = D.rc_campaign(I_in, t_pad, days, e_by, lb_by, cap, R150.SPEC)
    job = UJ._single_jobs(camp, I_in["plan"], C.BUDGET)["point"]
    facts = DT.facts_for(out.trades, out.aux, days, tick_value=tv, rr_cols=tuple(float(R) for R in rr_grid),
                         entry_ticks=float(out.counts["entry_ticks"]))
    blocks = list(job["blocks"])
    check_alignment(blocks, facts)
    return {"dates": tuple(days), "blocks": blocks, "args": dict(job["args"]), "facts": facts,
            "trades_sha256": SC.trades_subhash(t_pad, last=LAST), "counts": out.counts, "capacity": cap,
            "cut": cut_summary, "trades": int(len(out.trades))}


def check_alignment(blocks: Sequence[Any], facts: Mapping[tuple[int, int], TB.TradeFacts]) -> None:
    """Every fact is its block's trade (day, index, fill bar), and every block trade has its fact."""
    n_blk = sum(len(b.entry_t) for b in blocks)
    if n_blk != len(facts):
        raise EarlyLookRefused(f"REFUSED: the blocks hold {n_blk} trades, the facts {len(facts)}")
    for (i, j), f in facts.items():
        if int(round(float(blocks[i].entry_t[j]))) != int(f.entry):
            raise EarlyLookRefused(f"REFUSED: block {i} trade {j} fills at {blocks[i].entry_t[j]}, its fact at {f.entry}")


def run(root: Path = ROOT, results_dir: Path | None = None) -> Path:
    from extended import RESULTS_DIR
    from extended import results as RES

    bad = RES.clean_run_problem()
    if bad:
        raise EarlyLookRefused(f"REFUSED: the early look runs only from a clean run (scripts/run_clean.py): {bad}")
    holder = HA.check_run_lock(root)
    require_clean(root)
    t0 = time.perf_counter()
    b = build(root)
    starts = list(range(0, len(b["dates"]), START_STEP))
    ctx = {"dates": b["dates"], "blocks": b["blocks"], "args": b["args"], "facts": b["facts"],
           "subs": subs_of(b["facts"]), "seed_indices": tuple(range(J_SEEDS)), "coin_seed": issue("el_coins"),
           "sample_seed": issue("el_sample"), "horizon": HORIZON,
           "calendar": frozenset(date.fromisoformat(d) for d in b["dates"])}
    res = run_units(ctx, starts, WORKERS)
    df = readings(res["units"], b["dates"])
    params = params_of(b["dates"], starts, res, b, holder, time.perf_counter() - t0)
    return write(df, results_dir if results_dir is not None else RESULTS_DIR, params, root)


def params_of(dates: Sequence[str], starts: Sequence[int], res: Mapping[str, Any], b: Mapping[str, Any],
              holder: str | None, seconds: float) -> dict[str, Any]:
    if max(dates) > LAST:
        raise EarlyLookRefused("REFUSED: a date past the search years reached the result")
    return {"task": TASK, "exploratory": True, "label": LABEL, "design": DESIGN, "draft": DRAFT,
            "draft_lf_sha256": DRAFT_SHA256, "kind": KIND, "rule": RULE, "stop_ticks": STOP_TICKS,
            "cutoff_slot": CUTOFF, "first_date": min(dates), "last_date": max(dates),
            "seed_roles": {k: v for k, v in ROLES.items() if k != "el_tests"}, "part": PART, "J": J_SEEDS,
            "starts": len(starts), "start_step": START_STEP, "horizon": HORIZON, "arm": "off",
            "reading": W42.READING, "units": int(len(res["units"])), "oracle_checked_trades": res["oracle"],
            "keys_checked": res["keys"], "unit_seconds": round(float(res["seconds"]), 2),
            "seconds": round(float(seconds), 2), "trades": b.get("trades"), "trades_sha256": b.get("trades_sha256"),
            "capacity": b.get("capacity"), "counts": b.get("counts"), "lock_holder": holder,
            "convention": "zero_edge: three_way_baseline race on rc_campaign (P-16's money side), H4-B's readings"}


# ------------------------------------------------------------------------------------------------ the toy run


def toy_bars(n_days: int, seed: int) -> tuple[list[str], dict[str, tuple[np.ndarray, ...]]]:
    """A toy history in the walker's layout: business days from 2021-01-04, a driftless random walk on the tick grid
    from 17:00 to 15:10 CT each day, seeded by the tests' role (`SeedSequence(seed, spawn_key=(0,))`)."""
    rng = np.random.default_rng(np.random.SeedSequence(int(seed), spawn_key=(0,)))
    days, d = [], date(2021, 1, 4)
    while len(days) < n_days:
        if d.weekday() < 5:
            days.append(d.isoformat())
        d += timedelta(days=1)
    arrays: dict[str, tuple[np.ndarray, ...]] = {}
    px = 13000.0
    for ds in days:
        o, h, l, c = (np.full(1441, np.nan) for _ in range(4))
        for j in range(1, W.C_FLAT + 1):
            steps = rng.integers(-6, 7, size=4) * W.TICK
            op = px
            path = op + np.cumsum(steps)
            o[j], c[j] = op, float(path[-1])
            h[j], l[j] = float(max(op, path.max())), float(min(op, path.min()))
            px = float(path[-1])
        arrays[ds] = (o, h, l, c)
    return days, arrays


def toy_args() -> dict[str, Any]:
    """A synthetic job's arguments on the verified ledger's rules (H4-0's synthetic probe's form)."""
    import dataclasses as dc

    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.campaign.lockstep import ConductModel
    from propedge.campaign.payout_method import payout_method_terms
    from propedge.campaign.protocols import Protocol
    from propedge.campaign.risk_policy import RiskPolicy
    from propedge.campaign.sizing import SizingRule
    from propedge.contract.adapter import rules_from_ledger
    from propedge.contract.rules import load_rules

    rules = rules_from_ledger()
    proto = Protocol(name="q213_toy", combine_rr=1.5, combine_risk=500.0, funded_rr=2.0, funded_risk=400.0,
                     trades_per_day=1, max_concurrent_accounts=5,
                     params={"need_aware_exits": True, "consistency_cap_exits": True})
    lag = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
    return {"seed": 1,
            "draws": {"protocol": proto, "mode": "rotation", "flip": None,
                      "sizing": dc.replace(SizingRule.from_ledger(), fee_schedule=(1.22, 3.78)), "route_able": True,
                      "one_at_a_time": 5.0, "hold_to_own_exit": True},
            "path": {"edge": 0.0, "rules": rules, "initial_bankroll": 1_000_000.0, "max_concurrent_accounts": 5,
                     "subscription": float(rules.subscription), "billing_days": int(rules.billing_days),
                     "activation": float(rules.activation), "payout_lag_days": lag, "max_concurrent_combines": 2,
                     "max_total_accounts": 5, "conduct": ConductModel(rtp=False, enforcement_p=0.0),
                     "combine_max_days": 2000, "funded_horizon_days": 100_000, "record_trades": True,
                     "risk_policy": RiskPolicy.from_protocol(proto, with_rr=True)}}


def synthetic(out_dir: Path, n_days: int = 300, starts: Sequence[int] = (0, 3, 7), j: int = 4) -> dict[str, Any]:
    """The toy end-to-end: toy bars -> RL3's trades by `design_trades` -> the vendored blocks (`gate_blocks`) -> the
    race units -> H4's readings -> the result file in `out_dir` (never `results/`) -> the page beside it. No bar of
    the store is read; returns the paths and the unit timing (the dry run's cost measure)."""
    from extended import use_vendored_stage2

    use_vendored_stage2()
    import score_fv3_grid as gf

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    days, arrays = toy_bars(n_days, issue("el_tests"))
    hist = DT.history_from_arrays(days, arrays)
    spec = DT.rl3_spec(KIND, CUTOFF, RULE, STOP_TICKS, name=DESIGN)
    ctxs = {i: T.DayContext(i, d) for i, d in enumerate(days)}
    tv, fee = 0.5, 1.22
    built = DT.build_trades(spec, hist, lambda i: ctxs[i], day_kinds={d: "n" for d in days}, rr_grid=CS.RR_GRID,
                            fresh_rr=1.5, fee_micro_eq=fee, tick_value=tv, market_entry_ticks=1.0)
    if built.trades.empty:
        raise EarlyLookRefused("REFUSED: the toy history gave no trade")
    blocks, n_used = gf.gate_blocks(built.trades, days, tv, list(CS.RR_GRID), require_sides=True, require_exits=True)
    if n_used != len(built.trades):
        raise EarlyLookRefused("REFUSED: the toy blocks hold a different number of trades")
    facts = DT.facts_for(built.trades, built.aux, days, tick_value=tv, rr_cols=CS.RR_GRID, entry_ticks=0.0)
    check_alignment(list(blocks), facts)
    ctx = {"dates": tuple(days), "blocks": list(blocks), "args": toy_args(), "facts": facts, "subs": subs_of(facts),
           "seed_indices": tuple(range(int(j))), "coin_seed": issue("el_coins"), "sample_seed": issue("el_sample"),
           "horizon": HORIZON, "calendar": frozenset(date.fromisoformat(d) for d in days), "sample_all": True}
    res = run_units(ctx, list(starts), 1)
    df = readings(res["units"], days)
    b = {"trades": int(len(built.trades)), "counts": built.counts}
    params = params_of(days, list(starts), res, b, None, res["seconds"])
    params["toy"] = True
    from extended import results as RES

    p, _ = RES.write_result(df, RESULT, script=SCRIPT, seed=issue("el_coins"), parameters=params, results_dir=out_dir,
                            exploratory=True, prereg_id=None, description=f"{LABEL}. A synthetic toy run (no bar).")
    page = summary(Path(p), [], out_dir / "EARLY_LOOK.md")
    n_units = max(1, int(len(res["units"])))
    return {"result": str(p), "page": str(page), "units": n_units, "unit_seconds": res["seconds"] / n_units,
            "trades": int(len(built.trades)), "oracle": res["oracle"], "counts": built.counts,
            "page_problems": page_problems(page, {Path(p).name: Path(p)})}


# ------------------------------------------------------------------------------------------------ the page


#: (measure, horizon, plain words, kind of figure, the reading's column)
PAGE_ROWS: tuple[tuple[str, int, str, str, str], ...] = (
    ("first_pass_days", 126, "Sessions to the first pass (within six months)", "days", "r1_p50"),
    ("cash_to_first_pass", 126, "Cash spent to reach the first pass", "usd", "r1_p50"),
    ("first_payout_days", 126, "Sessions to the first payout (within six months)", "days", "r1_p50"),
    ("spent_before_first_payout", 126, "Cash spent before the first payout", "usd", "r1_p50"),
    ("paid_by_21", 21, "Share of users paid within the first month", "share", "r1_share"),
    ("payouts_per_month", 252, "Payouts a month, over the first year", "rate", "r1_p50"),
    ("monthly_net_4_12_median", 252, "Monthly income, months four to twelve (the median month)", "usd", "r1_p50"),
    ("net_month_12", 252, "Net after twelve months, a typical user", "usd", "r1_p50"),
    ("net_month_12", 252, "Net after twelve months, a bad case (one user in ten does worse)", "usd", "r1_p10"),
    ("peak_oop_12_months", 252, "Bankroll: the most money out of pocket in the first year", "usd", "r1_p50"),
)


def fmt(v: float, kind: str, horizon: int | None = None) -> str:
    """A figure as the page prints it; a count of sessions past its window (MEASURES' censored code, the window plus
    one) is "not reached"."""
    if v is None or not math.isfinite(float(v)):
        return "n/a"
    v = float(v)
    if kind == "days" and horizon is not None and v > int(horizon):
        return "not reached"
    if kind == "usd":
        return ("-" if v < 0 else "") + f"${abs(v):,.0f}"
    if kind == "share":
        return f"{100.0 * v:.1f} %"
    if kind == "days":
        return f"{v:.1f}"
    return f"{v:.2f}"


def _row(df: pd.DataFrame, measure: str, horizon: int) -> pd.Series | None:
    sel = df[(df["measure"].astype(str) == measure) & (df["horizon"].astype(int) == int(horizon))
             & (df["arm"].astype(str) == "off") & (df["reading"].astype(str) == W42.READING)]
    return None if sel.empty else sel.iloc[0]


def _verified(path: Path) -> pd.DataFrame:
    from extended import results as RES

    ok, why = RES.verify_result(path)
    if not ok:
        raise EarlyLookRefused(f"REFUSED: {path} does not verify against its manifest: {why}")
    return pd.read_csv(path)


def summary(result: Path, beside: Sequence[Path], page: Path) -> Path:
    """The one-page plain-language summary, every figure computed from `result` (and `beside`, H4-B's readings of
    P-14 by start-range part), each figure's source written in `<page>.trace.json` beside it."""
    from extended import results as RES

    df = _verified(Path(result))
    man = RES.read_manifest(Path(result)).as_dict()
    if not (bool(man.get("exploratory")) and df["exploratory"].astype(bool).all()):
        raise EarlyLookRefused("REFUSED: the early look's file is not labelled exploratory")
    par = man.get("parameters", {}) or {}
    if str(par.get("last_date", LAST)) > LAST:
        raise EarlyLookRefused("REFUSED: the early look's file reaches past the search years")
    parts = [(Path(p), _verified(Path(p)), RES.read_manifest(Path(p)).parameters or {}) for p in sorted(beside)]
    trace: list[dict[str, Any]] = []

    def cite(text: str, src: Path, measure: str, horizon: int, col: str, v: float, kind: str) -> str:
        trace.append({"text": text, "file": Path(src).name, "measure": measure, "horizon": int(horizon),
                      "column": col, "value": None if not math.isfinite(float(v)) else float(v), "kind": kind})
        return text

    lines = [f"# Early look: {DESIGN} (Q-213)", "", f"**{LABEL}.**", "",
             "This page is generated by `scripts/early_look.py summary` from the result file named below; every "
             "figure is read from that file (or from the H4-B files named beside it), never typed.", "",
             f"- **The design:** RL3's resting orders at the prior regular session's high and low, faded (a sell "
             f"limit at the high, a buy limit at the low), from `{DRAFT}`'s first declared cell, live from 09:00 CT, "
             f"one trade a day at most, cancelled at 14:30 CT.",
             f"- **How it was read:** every trade's direction removed and each outcome redrawn at its bracket's "
             f"driftless odds (zero edge), on Topstep's verified 50K rules through the firm path, over the search "
             f"years only (to {LAST}).",
             f"- **The file:** `results/{Path(result).name}`.", ""]
    p14_names = ", ".join(f"`results/{p.name}`" for p, _, _ in parts) or "none found"
    lines += ["| what a user sees | this design | P-14 (" + BESIDE_LABEL + "; low to high across its start-range "
              "parts) |", "|---|---|---|"]
    for measure, hz, words, kind, col in PAGE_ROWS:
        r = _row(df, measure, hz)
        v = float(r[col]) if (r is not None and col in r and pd.notna(r[col])) else float("nan")
        mine = cite(fmt(v, kind, hz), Path(result), measure, hz, col, v, kind)
        vals = []
        for p, pdf, _ in parts:
            pr = _row(pdf, measure, hz)
            if pr is not None and col in pr and pd.notna(pr[col]):
                vals.append((float(pr[col]), p))
        if vals:
            lo, hi = min(vals, key=lambda x: x[0]), max(vals, key=lambda x: x[0])
            p14 = (cite(fmt(lo[0], kind, hz), lo[1], measure, hz, col, lo[0], kind) + " to "
                   + cite(fmt(hi[0], kind, hz), hi[1], measure, hz, col, hi[0], kind))
        else:
            p14 = "not read"
        lines.append(f"| {words} | {mine} | {p14} |")
    lines += ["", "**Ruin** (the chance of running out of money before a first payout, MEASURES (24)) needs the "
              "bankroll budget W42-R1 sets from H4's readings (Q-189), not yet pinned: not shown here. The bad-case "
              "row and the bankroll row above are the nearest readings.", "",
              f"- **P-14** beside: {p14_names} -- {BESIDE_LABEL}; its parts cover different start days from each "
              "other, so its column is the range of their readings, not one figure.",
              "- **P-15:** pending (the F-3 drops). **P-16 and the naive coin:** not yet read in H4-B.",
              "- The design and P-14 are not paired: different coin fields (this look's own seeds), the design on "
              "every start day with fewer seeds. Read them side by side, not as a test.", "",
              "Not modelled: a user who stops when their own money runs out; the user's time; taxes; the denial "
              "of payouts (0 % here)."]
    text = "\n".join(lines) + "\n"
    page = Path(page)
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(text, encoding="utf-8", newline="\n")
    Path(str(page) + ".trace.json").write_text(json.dumps(trace, indent=1, sort_keys=True), encoding="utf-8",
                                                newline="\n")
    return page


#: what in the page may carry a digit without a trace (the design's id, dates, file names, section ids)
UNTRACED = re.compile(re.escape(DESIGN) + r"|Q-213|W42-R1|Q-189|H4-B|H4|B-2|F-3|P-1[456]|P-14|\(24\)|50K|RL3|09:00|14:30|"
                      r"\d{4}-\d{2}-\d{2}|`[^`]*`|\b(?:four|twelve|six)\b|0 %")


def page_problems(page: Path, files: Mapping[str, Path]) -> list[str]:
    """Every figure of the page that its trace does not hold; every traced value that is not its file's cell (the
    file re-read here, by name from `files`) or does not format to the printed text."""
    text = Path(page).read_text(encoding="utf-8")
    trace = json.loads(Path(str(page) + ".trace.json").read_text(encoding="utf-8"))
    probs = []
    frames: dict[str, pd.DataFrame] = {}
    for t in trace:
        if t["file"] not in files:
            probs.append(f"trace names {t['file']!r}, which is not one of the page's files")
            continue
        if t["file"] not in frames:
            frames[t["file"]] = pd.read_csv(files[t["file"]])
        r = _row(frames[t["file"]], t["measure"], t["horizon"])
        cell = float(r[t["column"]]) if (r is not None and t["column"] in r and pd.notna(r[t["column"]])) \
            else float("nan")
        got = float("nan") if t["value"] is None else float(t["value"])
        if not ((math.isnan(cell) and math.isnan(got)) or cell == got):
            probs.append(f"trace {t['measure']}/{t['column']} holds {got}, its file {cell}")
        want = fmt(got, t["kind"], t["horizon"])
        if want != t["text"]:
            probs.append(f"trace {t['measure']} formats to {want!r}, not {t['text']!r}")
    rest = text
    for t in sorted({t["text"] for t in trace}, key=len, reverse=True):
        rest = rest.replace(t, " ")
    rest = UNTRACED.sub(" ", rest)
    for m in re.finditer(r"\d", rest):
        probs.append(f"an untraced figure near {rest[max(0, m.start() - 20):m.end() + 20]!r}")
        break
    return probs


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    sub.add_parser("plan")
    sp = sub.add_parser("synthetic")
    sp.add_argument("--out", required=True)
    sub.add_parser("run")
    sm = sub.add_parser("summary")
    sm.add_argument("--result", default=f"results/{RESULT}.csv")
    sm.add_argument("--page", default=SUMMARY)
    cp = sub.add_parser("check-page")
    cp.add_argument("--page", required=True)
    cp.add_argument("--files", nargs="+", required=True)
    a = ap.parse_args(argv)
    if a.mode == "check-page":
        print(json.dumps({"problems": page_problems(Path(a.page), {Path(f).name: Path(f) for f in a.files})}))
        return 0
    if a.mode == "plan":
        print(json.dumps({"label": LABEL, "design": DESIGN, "draft": DRAFT, "kind": KIND, "rule": RULE,
                          "stop_ticks": STOP_TICKS, "cutoff_slot": CUTOFF, "last": LAST, "roles": sorted(ROLES),
                          "J": J_SEEDS, "start_step": START_STEP, "horizon": HORIZON, "workers": WORKERS},
                         sort_keys=True))
        return 0
    if a.mode == "synthetic":
        print(json.dumps(synthetic(Path(a.out)), sort_keys=True))
        return 0
    if a.mode == "run":
        print(json.dumps({"result": str(run())}))
        return 0
    beside = sorted(ROOT.glob(H4B_P14))
    page = summary(ROOT / a.result, beside, ROOT / a.page)
    probs = page_problems(page, {p.name: p for p in [ROOT / a.result, *beside]})
    if probs:
        raise EarlyLookRefused(f"REFUSED: the page holds untraced figures: {probs[:3]}")
    print(json.dumps({"page": str(page), "beside": [p.name for p in beside]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
