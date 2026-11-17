"""RD-01's identity stage (`prereg/RD-01_firm_contracts.md` 9.1), refusing: written for the lead to run under the run
lock, as its own script under the purpose `identity` and the decision row that registers it (`--row`).

    python identity/firms_identity.py --plan                                   # light: prints what would run
    python identity/firms_identity.py --row E-NNN --starts 4 --paths 4         # slow (T-8; the run lock)
    python identity/firms_identity.py --row E-NNN --starts all --paths 500 --workers 1   # heavy, the run's first stage

**Item 1 -- TS through this reading's runner.** P-16 and P-14 as U1 built them (`user_beside_identity.build`), A-1 at
Topstep's contract (`firms.plan_args`: the arguments themselves), A-9's `off` arm through the runner
(`firms.run_plan`): U1's start rows (`vendor/stage2/results/user_journey.csv`, section `start`, configs `p16` and `p14`,
both arms, the starts chosen as `user_journey.start_choice` chooses them, every column by E-010's comparison:
`user_beside_identity.u1_compare_outs`, with U1's checks of every run's payouts and fees against the engine's totals).
And the registered gate paths through A-8 with A-1's Topstep arguments (`firms.gate_args` must return them unchanged):
`gate_identity.p16_problems` / `p14_problems` (`rc_s150_all_gate_paths.csv` at seed 20261206 after P-16's trades' hash;
`a3_brk30_cb20_gate_paths.csv` at seed 20261131), every `zero_edge_decomposition.PATH_COLS` column, point and bound,
the first N paths, to 1e-6.

**Item 2 -- every adapter at its Topstep setting** (`firm_accounts.TWINS`; A-11's Topstep setting is "not applied", so
its arm is item 1's), in three pairs, one evaluation class on the path and one funded class through A-9's keyword:
DayTraders (A-2 + A-3), Fast Pass (A-4 + A-5), Quick Pay (A-4 + A-7). Each pair's outputs equal item 1's runner outputs
bit for bit apart from the one key naming the funded class (`user_beside_identity.class_outs_problems`), and U1's rows
by E-010's comparison; and the gate's paths with the pair through A-8's seams, as item 1.

**Item 3 -- Lucid.** (a) The vendored joint engine reproduces U1's `p16_5+1` start rows (`stage2_identity.u1_problems`
on that configuration). (b) The runner with Lucid's contract (A-1 by `lucid_setup`, A-9's keywords) equals the
vendored joint engine's one-firm run of `rc150_firm_split.lucid_setup` at five seats (`hypo_hedge.run_joint`,
`n_firms=1`, through `user_journey.run_job`), start for start, both arms, every column of U1's start rows, at both
readings of Lucid's reach (the joint setup's own household rule, and `household_closure=False` on its path) -- P-16.

**Item 4 -- the trades are the base's.** On a sample of starts (labelled a sample: the reading's runner repeats items
4 and 5 on every replay of every run and writes their counts, `firm_reading.run_cell`) (`--trade-starts`, default 4) of every plan's strict
corner on both streams, each trade the replay's accounts take (`record_trades`) is a trade of the design's blocks at
that start (its day and index in range), its outcome the block's own at its R plus its fee re-pricing.

**Item 5 -- off where off.** On the same sample: at TS no adapter account exists; with the twins every adapter counter
is zero; at each plan every adapter account is of exactly the class `classes_for` names (m4: through the per-start
subclasses' bases, so Fast Pass's and Quick Pay's evaluation classes are told apart). Counted and printed.

**The reading's own route on the same sample** (the fourth read's n2 and V1, with items 4 and 5): on the sampled starts
of each stream and arm, the reading's cells as `scripts/rd01_reading.py` runs them (`firm_reading.run_cell`: one pass
through A-9 with its replays captured) -- TS held to U1's registered start rows by E-010's comparison on that route
(V1), then every plan's strict corner with every in-run refusal the reading makes: the capture guard, the recorder's
own checks (V5), 9.1 items 4 and 5, 9.2's oracles, 9.3's uncapped-ladder control, U1's consistency checks and M1's
lines. So a false refusal shows here, under the identity's read, before any purpose of the reading is ledgered.

**Timings (V3).** Every stage prints its seconds, its start-runs (or paths) and seconds a start-run, and the process's
peak memory so far -- item 1 at every start, T-8 at 4 -- for the lead to schedule the reading from.

E-010's negative control (`--control`): item 1's comparison with Fast Pass's strict corner in place of TS must be
refused (the comparison can tell a plan from TS).

**The read.** Before anything runs, `extended.reader.authorise_engine_read` (purpose `identity`, declaration `--row`,
the development window, the engine's files) -- refused: exit 3 before any read. Exit 0 when every item holds, 3 when one
is refused. Nothing is written. Peak memory printed last.

**Estimates** (not measured; the lead's run measures them): at `--starts 4 --paths 4` a few minutes; at every start and
500 paths, item 1 is about E-010's full U1 comparison plus the two registered gates, each pair of item 2 the same again,
item 3 two P-16 passes of the joint engine -- about ten U1-sized passes and eight gates in all, many hours at one worker;
peak memory as one U1 pass (about 3 GB at one worker, Stage 2's family runs).
"""
from __future__ import annotations

import argparse
import dataclasses
import gc
import sys
import time
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402

import gate_identity as GI  # noqa: E402
import stage2_identity as SI  # noqa: E402
import user_beside_identity as UBI  # noqa: E402

from extended import firm_accounts as A  # noqa: E402
from extended import firm_reading as RD  # noqa: E402
from extended import firm_terms as T  # noqa: E402
from extended import firms as F  # noqa: E402
from extended import reader  # noqa: E402
from extended import user_beside as B  # noqa: E402

VENDOR = ROOT / "vendor" / "stage2"
CONFIGS = ("p16", "p14")
TS = T.settings_for("TS", "reference")
#: item 2's pairs: (name, the evaluation twin, the funded twin)
PAIRS = (("DT", "A-2", "A-3"), ("FP", "A-4", "A-5"), ("QP", "A-4", "A-7"))
TWIN = {a: cls for a, _k, cls in A.TWINS}
LUCID_JOINT_CONFIG = "p16_5+1"
CHECKS = ("item 1: TS through the runner -- U1's start rows (p16, p14, both arms) and the registered gate paths",
          "item 2: the adapters at their Topstep setting, in pairs (A-2+A-3, A-4+A-5, A-4+A-7) -- the same",
          "item 3: Lucid -- (a) the vendored joint engine's p16_5+1 rows; (b) the runner against the joint one-firm run",
          "item 4: every trade taken is one of the design's offered trades; and, on the same sample, the reading's "
          "own route with every in-run refusal and TS held to U1's rows on it (n2, V1)",
          "item 5: off where off -- no adapter fires at TS, no other plan's rule in a plan")


def timing(label: str, seconds: float, runs: int, unit: str = "start-run") -> None:
    """V3: one stage's real timing and the process's peak memory so far, printed for the reading's schedule."""
    each = f", {seconds / runs:.3f} s a {unit}" if runs else ""
    mem = SI.peak_memory() or "peak memory not available"
    print(f"timing: {label}: {seconds:.1f} s, {runs} {unit}s{each}; {mem}", flush=True)


def _with_path(job: dict[str, Any], **kw: Any) -> dict[str, Any]:
    return {**job, "args": {**job["args"], "path": {**job["args"]["path"], **kw}}}


# ------------------------------------------------------------------------------------------------ items 1 and 2: U1


def u1_items(starts: int | None, workers: int, control: bool = False) -> dict[str, list[str]]:
    """Items 1 and 2 on U1's start rows; with `control`, item 1 at Fast Pass's strict corner (must be refused)."""
    import user_journey as UJ

    from propedge import RESULTS_DIR

    ref = UBI.u1_reference(RESULTS_DIR, CONFIGS)
    out: dict[str, list[str]] = {"item 1 U1": [], "item 2 U1": []}
    for name in CONFIGS:
        jobs, c, probs = UBI.build(RESULTS_DIR, name)
        out["item 1 U1"] += probs
        for arm in UJ.ARMS:
            job = jobs[arm]
            of = len(job["blocks"])
            chosen = UJ.start_choice(of, starts)
            s = T.settings_for("FP", T.STRICT) if control else TS
            args, kw = F.plan_args(job["args"], s, blocks=job["blocks"] if control else None)
            if not control and (args is not job["args"] or kw):
                out["item 1 U1"].append(f"{name} {arm}: A-1 at Topstep's contract changed the arguments")
            t0 = time.time()
            runs = F.run_plan(name, arm, B.BY_NAME["off"], {**job, "args": args}, s, chosen, kw, workers=workers)
            timing(f"item 1 {name} {arm} (A-9 through the runner, TS)", time.time() - t0, len(chosen))
            outs = [o for o, _ in runs]
            out["item 1 U1"] += UBI.u1_compare_outs(name, c, arm, outs, ref, of, starts)
            if control:
                continue
            for plan, ca, fa in PAIRS:
                j2 = _with_path(job, combine_account_cls=TWIN[ca])
                t0 = time.time()
                o2 = B.run_starts(name, arm, B.BY_NAME["off"], j2, chosen, workers, funded_account_cls=TWIN[fa])
                timing(f"item 2 {plan}'s twins {name} {arm}", time.time() - t0, len(chosen))
                what = f"{plan}'s twins ({ca}+{fa}) {name} {arm}"
                out["item 2 U1"] += [f"{what}: {p}" for p in UBI.u1_compare_outs(name, c, arm, o2, ref, of, starts)]
                out["item 2 U1"] += UBI.class_outs_problems(outs, o2, TWIN[fa], what)
                del o2
                gc.collect()
            del runs, outs
            gc.collect()
        del jobs
        gc.collect()
    return out


# ------------------------------------------------------------------------------------------------ items 1 and 2: gates


def gate_items(paths: int, workers: int) -> dict[str, list[str]]:
    """Items 1 and 2 on the registered gate paths, through `gate_identity`'s registered calls with this reading's arms:
    `ts` (A-1's Topstep arguments, which must be the call's own) and each pair's twins through A-8's seams."""
    arms = ("ts",) + tuple(f"twins_{p}" for p, _, _ in PAIRS)
    seen_ts: list[bool] = []

    def arm_kwargs(arm: str, ledger: Any | None = None) -> dict[str, Any]:
        if arm == "ts":
            probe = {"rules": object(), "sizing": object()}
            seen_ts.append(F.gate_args(probe, TS) is probe)
            return {}
        for plan, ca, fa in PAIRS:
            if arm == f"twins_{plan}":
                return {"combine_account_cls": TWIN[ca], "funded_account_cls": TWIN[fa]}
        raise ValueError(arm)

    saved = GI.arm_kwargs
    GI.arm_kwargs = arm_kwargs
    try:
        t0 = time.time()
        p16 = GI.p16_problems(int(paths), int(workers), arms)
        timing(f"items 1-2 gates P-16 ({len(arms)} arms, each two shifts)", time.time() - t0, int(paths) * len(arms),
               "arm-path")
        t0 = time.time()
        p14 = GI.p14_problems(int(paths), int(workers), arms)
        timing(f"items 1-2 gates P-14 ({len(arms)} arms, each two shifts)", time.time() - t0, int(paths) * len(arms),
               "arm-path")
    finally:
        GI.arm_kwargs = saved
    out = {"item 1 gate": [f"P-16 {p}" for p in p16["ts"]] + [f"P-14 {p}" for p in p14["ts"]],
           "item 2 gate": [f"{d} {a}: {p}" for d, r in (("P-16", p16), ("P-14", p14)) for a in arms[1:] for p in r[a]]}
    if not seen_ts or not all(seen_ts):
        out["item 1 gate"].append("A-1 at Topstep's contract changed the gate's arguments")
    return out


# ------------------------------------------------------------------------------------------------ item 3: Lucid


def lucid_items(starts: int | None, workers: int) -> dict[str, list[str]]:
    """(a) the vendored joint engine's p16_5+1 rows; (b) the runner with Lucid's contract against the vendored joint
    engine's one-firm Lucid run, both readings of the reach, both arms."""
    import customer_journey as CJ
    import rc150_firm_split as RS
    import rc_screen as S
    import user_journey as UJ

    from propedge import RESULTS_DIR
    from propedge.research import hypo_hedge as hh
    from propedge.research import user_journey as U

    out: dict[str, list[str]] = {"item 3a": [], "item 3b": []}
    defs = {d["config"]: d for d in UJ.CONFIG_DEFS}
    jl, idents = UJ.BUILDERS["joint"](RESULTS_DIR, [LUCID_JOINT_CONFIG])
    out["item 3a"] += [f"{LUCID_JOINT_CONFIG}: the study's identity fails: {r['check'][:120]} -- {r['problems']}"
                       for r in idents if not r["holds"] and r["refuses"]]
    ref = UBI.u1_reference(RESULTS_DIR, (LUCID_JOINT_CONFIG,))
    st = ref["start"]
    for arm in UJ.ARMS:
        got = UJ.run_job(jl[LUCID_JOINT_CONFIG][arm], LUCID_JOINT_CONFIG, arm, starts, int(workers))["starts"]
        mine = [{**r, "reading": U.READING} for r in UJ.start_rows(defs[LUCID_JOINT_CONFIG], arm, got)]
        theirs = st[(st["config"] == LUCID_JOINT_CONFIG) & (st["arm"] == arm)].to_dict("records")
        out["item 3a"] += SI.u1_compare(mine, theirs, ref["columns"], f"{LUCID_JOINT_CONFIG} {arm}",
                                        all_starts=starts is None)
    del jl
    gc.collect()
    X = RS.inputs(RS.LUCID)
    lu5 = RS.lucid_setup(hh.with_seats(X["rep"], 5, RS.budget_for(5)))
    jobs, c, probs = UBI.build(RESULTS_DIR, "p16")
    out["item 3b"] += probs
    cols = UBI.u1_reference(RESULTS_DIR, ("p16",))["columns"]
    for arm in UJ.ARMS:
        blocks = RS.arm_blocks(X, CJ.SHIFT_OF[arm])
        job = jobs[arm]
        chosen = UJ.start_choice(len(job["blocks"]), starts)
        for corner, setup in ((T.STRICT, lu5),
                              (T.LENIENT, dataclasses.replace(lu5, path={**lu5.path, "household_closure": False}))):
            s = T.settings_for("LU", corner)
            joint = {"engine": "joint", "blocks": blocks, "dates": list(X["days"]), "setups": [setup],
                     "seed": int(S.SEED)}
            theirs = [{**r, "reading": U.READING} for r in
                      UJ.start_rows(c, arm, UJ.run_job(joint, "p16_lu5", arm, starts, int(workers))["starts"])]
            args, kw = F.plan_args(job["args"], s, blocks=job["blocks"])
            mine = [{**r, "reading": U.READING} for r in
                    UJ.start_rows(c, arm, [o for o, _ in F.run_plan("p16", arm, B.BY_NAME["off"], {**job, "args": args},
                                                                    s, chosen, kw, workers=workers)])]
            out["item 3b"] += SI.u1_compare(mine, theirs, cols, f"Lucid {corner} p16 {arm}", all_starts=False)
            gc.collect()
    return out


# ------------------------------------------------------------------------------------------------ items 4 and 5


def trade_problems(lp: Any, blocks: Sequence[Any]) -> list[str]:
    """Item 4 on one replay: each trade's day and index are a trade of `blocks`, its outcome the block's own at its R
    plus its fee re-pricing (D-324)."""
    probs = []
    for r in lp.trades:
        h, j = int(r.get("historical_day", -1)), int(r.get("trade_index", -1))
        if not (0 <= h < len(blocks)) or not (0 <= j < len(blocks[h].pnl)):
            probs.append(f"a trade at day {h} index {j} is not in the design's blocks")
            continue
        R = r.get("rr_used", r.get("rr"))
        if R is None or blocks[h].r_by_rr is None or r.get("at_need") or r.get("stretch"):
            continue
        want = float(blocks[h].r_by_rr[float(R)][j]) + float(r.get("fee_adj_r", 0.0))
        if not np.isclose(float(r["u"]), want, atol=1e-9):
            probs.append(f"the trade at day {h} index {j} books {r['u']} at R {R}, the block's own is {want}")
    return probs


def sample_items(n_starts: int) -> dict[str, list[str]]:
    """Items 4 and 5 on `n_starts` starts of each stream and arm: TS, the twins, and every plan's strict corner."""
    import user_journey as UJ

    from propedge import RESULTS_DIR

    out: dict[str, list[str]] = {"item 4": [], "item 5": []}
    counts: dict[str, int] = {}
    for name in CONFIGS:
        jobs, _c, _p = UBI.build(RESULTS_DIR, name)
        for arm in UJ.ARMS:
            job = jobs[arm]
            delta_r, dby = F.arm_delta(jobs["point"]["blocks"], job["blocks"]) if arm != "point" else (0.0, None)
            for s0 in UJ.start_choice(len(job["blocks"]), n_starts):
                L = min(252, len(job["blocks"]) - s0)
                runs = [("TS", TS, None, None), ("twins", TS, TWIN["A-4"], TWIN["A-7"])]
                runs += [(p, T.settings_for(p, T.STRICT), None, None) for p in ("LU", "DT", "FP", "QP")]
                for tag, st, c_twin, f_twin in runs:
                    blocks, point_ref = job["blocks"], None
                    if st.plan in ("FP", "QP"):
                        blocks, _n = F.tier1_arm(jobs["point"]["blocks"], job["dates"], st.tier1, delta_r, dby)
                        point_ref, _n = F.tier1_arm(jobs["point"]["blocks"], job["dates"], st.tier1)   # M3
                    args, kw = F.plan_args(job["args"], st, blocks=blocks if st.plan not in ("TS", "LU") else None)
                    c_cls, f_cls = F.start_classes(st, job["dates"], s0, point_ref)
                    c_cls, f_cls = c_twin or c_cls, f_twin or f_cls or kw.get("funded_account_cls")
                    path = {**args["path"], "record_trades": True}
                    if c_cls is not None:
                        path["combine_account_cls"] = c_cls
                    if f_cls is not None:
                        path["funded_account_cls"] = f_cls
                    if "household_closure" in kw:
                        path["household_closure"] = kw["household_closure"]
                    A.TALLY.clear()
                    lp = B.replay(blocks[s0:s0 + L], {**args, "path": path}, B.start_seed(s0))
                    got = A.collect()
                    out["item 4"] += [f"{name} {arm} {tag} start {s0}: {p}" for p in
                                      trade_problems(lp, blocks[s0:s0 + L])[:3]]
                    if tag == "TS" and got:
                        out["item 5"].append(f"{name} {arm} start {s0}: {len(got)} adapter accounts at TS")
                    if tag == "twins":
                        fired = [g for g in got if any(v for k, v in g.items()
                                                       if k not in ("class", "family", "kind", "index", "day"))]
                        if fired:
                            out["item 5"].append(f"{name} {arm} start {s0}: a twin's switch fired ({fired[0]})")
                    if tag in ("LU", "DT", "FP", "QP"):           # m4: by the exact class classes_for names
                        out["item 5"] += [f"{name} {arm} {tag} start {s0}: {p}" for p in RD.class_problems(got, st)]
                        for g in got:
                            for k, v in g.items():
                                if k not in ("class", "family", "kind", "index", "day") and isinstance(v, (int, float)):
                                    counts[f"{tag}.{k}"] = counts.get(f"{tag}.{k}", 0) + int(v)
                    del lp
        del jobs
        gc.collect()
    print("item 5's counts (a sample of starts; the reading's runner repeats items 4 and 5 on every replay of every "
          "run and writes them): " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())), flush=True)
    return out


def reading_route_items(n_starts: int) -> dict[str, list[str]]:
    """n2 and V1 (the module's docstring): on `n_starts` starts of each stream and arm, the reading's own cells and
    every refusal it makes in the run, before any of its purposes is ledgered."""
    import user_journey as UJ

    from extended import user_readings as UR
    from propedge import RESULTS_DIR

    out: dict[str, list[str]] = {"n2 the reading's in-run refusals": [], "V1 TS on the reading's route": []}
    ref = UBI.u1_reference(RESULTS_DIR, CONFIGS)
    off = B.BY_NAME["off"]
    for name in CONFIGS:
        (jobs, c, probs), seen = RD.build_with_deltas(lambda name=name: UBI.build(RESULTS_DIR, name))
        out["n2 the reading's in-run refusals"] += probs
        uniq = {(float(dr), None if by is None else tuple(sorted(by.items()))) for dr, by in seen}
        if len(uniq) != 1:
            out["n2 the reading's in-run refusals"].append(f"{name}: {len(uniq)} registered verdict shifts, not one")
            continue
        delta = {"verdict": seen[0]}
        pt = jobs["point"]
        out["n2 the reading's in-run refusals"] += [f"{name} verdict: r6: {q}" for q in
                                                     RD.delta_problems(pt["blocks"], jobs["verdict"]["blocks"],
                                                                       delta["verdict"])]
        ctx = RD.stream_context(name, pt)
        for arm in UJ.ARMS:
            job = jobs[arm]
            chosen = UJ.start_choice(len(job["blocks"]), n_starts)
            ts = None
            for plan in ("TS", "LU", "DT", "FP", "QP"):
                st = TS if plan == "TS" else T.settings_for(plan, T.STRICT)
                what = f"{name} {arm} {plan}"
                t0 = time.time()
                try:
                    blocks, ref_pt, _ = RD.arm_inputs(pt, job, st, arm, delta.get(arm))
                    cjob, kw = RD.cell_job(job, st, blocks)
                    cell = RD.run_cell(name, arm, off, cjob, st, chosen, kw, ref_pt, direct=True, ctx=ctx,
                                       ts=None if ts is None else ts, keep_ts=plan == "TS",
                                       keep_directs=plan == "DT")
                    probs = list(cell["problems"])
                    if not probs:
                        outs = RD.reading_outs(cell, name, arm, off, st)
                        srows, _t = UR.summary(name, arm, off, outs, blocks=UR.READING_BLOCKS)
                        probs += UR.consistency_problems(srows, outs, what, blocks=UR.READING_BLOCKS)
                        RD.u1_reported_rows([o["rec"] for o in outs])
                    if plan == "TS" and not probs:
                        out["V1 TS on the reading's route"] += [
                            f"{what}: {q}" for q in UBI.u1_compare_outs(name, c, arm, cell["outs"], ref,
                                                                       len(job["blocks"]), n_starts)]
                        ts = cell["ts"]
                except RD.Refused as exc:
                    probs = [str(exc)]
                out["n2 the reading's in-run refusals"] += [f"{what}: {q}" for q in probs[:3]]
                timing(f"n2 {what} (the reading's single pass and its refusals)", time.time() - t0, len(chosen))
                gc.collect()
        del jobs
        gc.collect()
    return out


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--plan", action="store_true", help="print what would run, read nothing")
    ap.add_argument("--row", default=None, help="the decision row registering this identity (E-NNN)")
    ap.add_argument("--starts", default="4", help="N starts a configuration and arm, or 'all'")
    ap.add_argument("--paths", type=int, default=4)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--trade-starts", type=int, default=4)
    ap.add_argument("--only", default="1,2,3,4,5", help="the items to run, e.g. 1,2")
    ap.add_argument("--control", action="store_true", help="E-010's negative control: item 1 at FP's strict corner "
                    "must be refused (exit 0 when it is)")
    a = ap.parse_args(argv)
    items = {int(x) for x in a.only.split(",") if x}
    if a.plan:
        for k, line in enumerate(CHECKS, 1):
            print(("run  " if k in items else "skip ") + line)
        print(f"starts {a.starts}, paths {a.paths}, workers {a.workers}, trade starts {a.trade_starts}")
        return 0
    if not a.row or not a.row.startswith("E-"):
        ap.error("--row E-NNN: the decision row that registers this identity (9.1, section 6 item 6)")
    root = VENDOR / "data"
    if not ((root / "bars").is_dir() and (root / "atlas").is_dir()):
        print("REFUSED: no bars or atlas (scripts/vendor_stage2.py --data)")
        return 3
    try:                                            # the engine's read authorised (ledgered in a clean run only)
        reader.authorise_engine_read(reader.CHOICE_START, reader.JUDGED_END, purpose=reader.IDENTITY,
                                     declaration=a.row, files=SI.engine_files(VENDOR, bars=True),
                                     what=f"{a.row}'s identity (identity/firms_identity.py): RD-01's 9.1 items "
                                          f"{sorted(items)} at {a.starts} starts and {a.paths} paths"
                                          + (" -- the negative control" if a.control else ""))
    except (reader.ReadRefused, FileNotFoundError) as exc:
        print(SI.refusal(exc), flush=True)
        return 3
    starts = None if a.starts == "all" else int(a.starts)
    t0 = time.time()
    if a.control:
        r = u1_items(starts, a.workers, control=True)["item 1 U1"]
        print(("negative control HOLDS: Fast Pass's strict corner is refused by item 1's comparison "
               f"({len(r)} differences)") if r else "REFUSED: negative control: FP passes item 1's comparison", flush=True)
        mem = SI.peak_memory()
        if mem:
            print(mem, flush=True)
        return 0 if r else 3
    res: dict[str, list[str]] = {}
    if items & {1, 2}:
        t1 = time.time()
        res.update(u1_items(starts, a.workers))
        timing("items 1-2, U1's start rows", time.time() - t1, 0)
        t1 = time.time()
        res.update(gate_items(a.paths, a.workers))
        timing("items 1-2, the gates", time.time() - t1, 0)
        if 2 not in items:
            res.pop("item 2 U1"), res.pop("item 2 gate")
    if 3 in items:
        t1 = time.time()
        res.update(lucid_items(starts, a.workers))
        timing("item 3, Lucid", time.time() - t1, 0)
    if items & {4, 5}:
        t1 = time.time()
        res.update(sample_items(a.trade_starts))
        timing("items 4-5, the sample", time.time() - t1, 0)
        t1 = time.time()
        res.update(reading_route_items(a.trade_starts))
        timing("n2 and V1, the reading's route on the sample", time.time() - t1, 0)
    rc = 0
    for k, probs in res.items():
        if probs:
            rc = 3
            print(f"REFUSED: RD-01 9.1 {k} -- " + "; ".join(probs[:12]), flush=True)
        else:
            print(f"identity HOLDS: RD-01 9.1 {k}", flush=True)
    print(f"{time.time() - t0:.0f} s", flush=True)
    mem = SI.peak_memory()
    if mem:
        print(mem, flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
