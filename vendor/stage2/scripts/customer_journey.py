"""EXPLORATORY (D-518): the customer-journey study -- the chance a customer reaches each milestone within a period, and
the money it takes -- on the configurations on file. The frontier is reported; NOTHING IS CHOSEN until the operator
gives the selection rule (D-518 (8)).

    python scripts/customer_journey.py --check --paths 4 --starts 6        # quick identities; nothing written
    python scripts/customer_journey.py --workers 4                         # the study (from a clean checkout, D-474)

**Two sources** (D-518 (1)): `replay` -- every trading day of the configuration's development window as a fresh start,
its trades in historical order (D-508's engine call, `customer_slices.engine_args` / `replay`; D-514's and D-515's
`run_joint` with `replay=True` for the two-firm rows), each start run for min(126, sessions left) sessions, plus runs of
exactly 21, 63 and 90 sessions where the start has them (a replay's last evening differs from a longer one's by the
purchases made after its final close, so a reading AT a day comes from a run of exactly that length; the event days
before it are the long run's -- checked start for start); `resampled` -- the 500 paths of the configuration's recorded
run, re-run and equal to its per-path file on every recorded column, read on their first 126 sessions. **Arms:**
`verdict` (`lower_bound`, every R at the bound its gate read) and `point`; best is marked on `verdict` only.

**The configurations** (D-518 (4)) and what each must reproduce before anything is read:

=====================  =======  ==========================================  ===========================================
config                 pool     built as                                    reproduced from
=====================  =======  ==========================================  ===========================================
fv3c                   topstep  FV3-C's development campaign                 fv3_corrected_v1_paths (gate placement off)
fv3c_noclose_b20       topstep  the same, no closure, budget 20 (D-505)      fv3c_compliance_paths (fv3c_dev)
p13                    topstep  P-13's campaign (D-500)                      a3_brk30_gate_paths (gate)
p13_noclose            topstep  no closure (D-501)                           a3_compliance_paths (a_noclose)
p13_noclose_b20        topstep  no closure, budget 20                        a3_compliance_paths (c_noclose_budget20)
p13_noclose_b30        topstep  no closure, budget 30                        a3_compliance_paths (c_noclose_budget30)
p14                    topstep  P-14 (D-513; seed 20261131)                  a3_brk30_cb20_gate_paths (gate)
two_firm_unhedged      assumed  D-514's a_unhedged                           hypo_hedge_a3_paths (a_unhedged)
hedged                 hypo     D-514's b_hedged                             hypo_hedge_a3_paths (b_hedged)
hedged_combines        hypo     D-514's c_hedged_combines                    hypo_hedge_a3_paths (c_hedged_combines)
mirror                 hypo     D-515's b_mirror                             hypo_mirror_paths (b_mirror)
=====================  =======  ==========================================  ===========================================

The replays' identities: each start's 21 / 63 / 126-session slice equals D-508's (`customer_slices.csv`) where it
holds the configuration and arm, P-14's own (`a3_brk30_cb20_gate_slices.csv`) and P-13-without-closure-budget-20's for
P-14; the slice summaries equal D-514's and D-515's (`hypo_hedge_a3.csv`, `hypo_mirror.csv`) for their arms.

**Pools** (D-518 (6)): `topstep` (eligible), `assumed_second_firm` (eligible only in the wider pool: its second firm is
Topstep's contract under Firm H's convention, not a verified firm's rules), `hypothetical_hedge` (never eligible; the
prohibition unchanged -- Topstep 13747047, Lucid 11404734; tier 1).

Writes `results/customer_journey.csv` (sections `identity`, `metric`, `frontier`, `curve`, `start`) and
`results/customer_journey_paths.csv` (each resampled path's journey); variants under `D-518:customer_journey` and
`D-518:hypothetical_hedge`. EXPLORATORY: beside the verdicts, never a gate; no selection.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.research import customer_journey as cj  # noqa: E402

SCRIPT = "scripts/customer_journey.py"
DECISION = "D-518"
RESULT = "customer_journey"
FAMILY_ID = f"{DECISION}:customer_journey"
HYPO_FAMILY_ID = f"{DECISION}:hypothetical_hedge"
N_PATHS = 500
ARMS = ("verdict", "point")
SHIFT_OF = {"verdict": "lower_bound", "point": "point"}
TOPSTEP, ASSUMED, HYPO = "topstep", "assumed_second_firm", "hypothetical_hedge"
LABEL_OF = {TOPSTEP: "", ASSUMED: ASSUMED, HYPO: HYPO}
BUDGET20, BUDGET30 = (20, 21), (30, 21)
P13_SEED, P14_SEED, FV3C_SEED, HEDGE_SEED, MIRROR_SEED = 20261028, 20261131, 20261019, 20261131, 20261201
TOL = 1e-6
READING = "EXPLORATORY (D-518): beside the verdicts, never a gate (D-234); no selection until the operator's rule"
CHUNK_STARTS = 40
CHUNK_PATHS = 25
WORKER_GB = 0.6

#: (config, pool, kind, table, budget, seed, (paths file, filter, run), slice references {arm: [(file, config)]},
#:  summary reference (file, arm) or None, decision)
CONFIGS: tuple[dict[str, Any], ...] = (
    dict(config="fv3c", pool=TOPSTEP, kind="fv3c", table="v12", budget=None, seed=FV3C_SEED,
         ref=("fv3_corrected_v1_paths.csv", {}, "gate placement off"),
         slices={"verdict": [("customer_slices.csv", "fv3c")]}, summary=None, decision="D-505"),
    dict(config="fv3c_noclose_b20", pool=TOPSTEP, kind="fv3c", table="noclose", budget=BUDGET20, seed=FV3C_SEED,
         ref=("fv3c_compliance_paths.csv", {"study_campaign": "fv3c_dev"}, "c_noclose_budget20"),
         slices={"verdict": [("customer_slices.csv", "fv3c_noclose_b20")]}, summary=None, decision="D-505"),
    dict(config="p13", pool=TOPSTEP, kind="p13", table="v12", budget=None, seed=P13_SEED,
         ref=("a3_brk30_gate_paths.csv", {}, "gate"),
         slices={"verdict": [("customer_slices.csv", "p13")], "point": [("customer_slices.csv", "p13")]},
         summary=None, decision="D-500"),
    dict(config="p13_noclose", pool=TOPSTEP, kind="p13", table="noclose", budget=None, seed=P13_SEED,
         ref=("a3_compliance_paths.csv", {}, "a_noclose"),
         slices={"verdict": [("customer_slices.csv", "p13_noclose")]}, summary=None, decision="D-501"),
    dict(config="p13_noclose_b20", pool=TOPSTEP, kind="p13", table="noclose", budget=BUDGET20, seed=P13_SEED,
         ref=("a3_compliance_paths.csv", {}, "c_noclose_budget20"),
         slices={"verdict": [("customer_slices.csv", "p13_noclose_b20")]}, summary=None, decision="D-501"),
    dict(config="p13_noclose_b30", pool=TOPSTEP, kind="p13", table="noclose", budget=BUDGET30, seed=P13_SEED,
         ref=("a3_compliance_paths.csv", {}, "c_noclose_budget30"),
         slices={"verdict": [("customer_slices.csv", "p13_noclose_b30")]}, summary=None, decision="D-501"),
    dict(config="p14", pool=TOPSTEP, kind="p13", table="noclose", budget=BUDGET20, seed=P14_SEED,
         ref=("a3_brk30_cb20_gate_paths.csv", {}, "gate"),
         slices={"verdict": [("a3_brk30_cb20_gate_slices.csv", "a3_brk30_cb20"),
                             ("customer_slices.csv", "p13_noclose_b20")]}, summary=None, decision="D-513"),
    dict(config="two_firm_unhedged", pool=ASSUMED, kind="hedge", arm="a_unhedged", seed=HEDGE_SEED,
         ref=("hypo_hedge_a3_paths.csv", {}, "a_unhedged"), slices={}, summary=("hypo_hedge_a3.csv", "a_unhedged"),
         decision="D-514"),
    dict(config="hedged", pool=HYPO, kind="hedge", arm="b_hedged", seed=HEDGE_SEED,
         ref=("hypo_hedge_a3_paths.csv", {}, "b_hedged"), slices={}, summary=("hypo_hedge_a3.csv", "b_hedged"),
         decision="D-514"),
    dict(config="hedged_combines", pool=HYPO, kind="hedge", arm="c_hedged_combines", seed=HEDGE_SEED,
         ref=("hypo_hedge_a3_paths.csv", {}, "c_hedged_combines"), slices={},
         summary=("hypo_hedge_a3.csv", "c_hedged_combines"), decision="D-514"),
    dict(config="mirror", pool=HYPO, kind="mirror", arm="b_mirror", seed=MIRROR_SEED,
         ref=("hypo_mirror_paths.csv", {}, "b_mirror"), slices={}, summary=("hypo_mirror.csv", "b_mirror"),
         decision="D-515"),
)


# ------------------------------------------------------------------------------------------------ journeys from records


def _single_pay_days(p) -> list[int]:
    if p.days_to_first_payout is None:
        return []
    out = [int(p.days_to_first_payout)]
    for g in p.payout_gaps:
        out.append(out[-1] + int(g))
    return out


def single_events(lp) -> tuple[np.ndarray, float, list[int], list[int], list[int]]:
    """(cash closes, initial, pass days, funded activation days, payout days) of one `LockstepPath`."""
    p = lp.path
    passes = [int(c.resolved_on) for c in lp.combines if c.passed and c.resolved_on is not None]
    funded = [int(f.activation_day) for f in lp.funded]
    return np.asarray(p.cash_series, float), float(p.initial_bankroll), passes, funded, _single_pay_days(p)


def joint_events(jp) -> tuple[np.ndarray, float, list[int], list[int], list[int]]:
    """The same for a two-firm `JointPath`: the pooled wallet's cash (the last firm's series), every firm's events."""
    from propedge.research import hypo_hedge as hh

    last = jp.paths[-1].path
    passes = [int(c.resolved_on) for lp in jp.paths for c in lp.combines if c.passed and c.resolved_on is not None]
    funded = [int(f.activation_day) for lp in jp.paths for f in lp.funded]
    pays = sorted(d for lp in jp.paths for d in hh._pay_days(lp.path))
    return np.asarray(last.cash_series, float), float(last.initial_bankroll), passes, funded, pays


def _join(xs) -> str:
    return " ".join(str(int(x)) for x in sorted(xs))


def journey_of(ev, window: int = cj.WINDOW) -> dict[str, Any]:
    """A resampled path's journey on its first `window` sessions, with its event days (all of them) as text."""
    cash, init, passes, funded, pays = ev
    u = cj.unit(cash[:window + 1], init, passes, funded, pays)
    u.update({"pass_days": _join(d for d in passes if d <= window), "funded_days": _join(d for d in funded if d <= window),
              "pay_days": _join(d for d in pays if d <= window)})
    return u


# ------------------------------------------------------------------------------------------------ the replay tasks


def _events_upto(ev, h: int) -> tuple:
    _, _, passes, funded, pays = ev
    return (sorted(d for d in passes if d <= h), sorted(d for d in funded if d <= h), sorted(d for d in pays if d <= h))


def _start_rows(config: str, arm: str, s: int, date: str, long_ev, exact_ev: dict[int, Any], sub: float,
                slice_fn) -> tuple[dict, list[dict], int]:
    """One start: its unit and start row, its D-508 slices at 21 / 63 / 126 (for the identities), and the count of
    exact runs whose event days differ from the long run's (must be 0)."""
    cash, init = long_ev[0], long_ev[1]
    L = len(cash) - 1
    exact = {h: e[0] for h, e in exact_ev.items()}
    if L in cj.EXACT:
        exact[L] = cash
    u = cj.unit(cash, init, long_ev[2], long_ev[3], long_ev[4], exact=exact)
    bad = sum(1 for h, e in exact_ev.items() if _events_upto(e, h) != _events_upto(long_ev, h))
    passes, funded, pays = _events_upto(long_ev, L)
    row = {"section": "start", "config": config, "arm": arm, "start_day": int(s), "start_date": date, **u,
           "pass_days": _join(passes), "funded_days": _join(funded), "pay_days": _join(pays),
           **{f"net_month_{k}": float(cash[cj.MONTH * k] - init) if cj.MONTH * k <= L else float("nan")
              for k in range(1, cj.WINDOW // cj.MONTH + 1)}}
    slices = []
    for h in (21, 63, 126):
        if h == L:
            slices.append({"horizon": h, "start_day": int(s), "start_date": date, **slice_fn(None, h)})
        elif h in exact_ev:
            slices.append({"horizon": h, "start_day": int(s), "start_date": date, **slice_fn(h, h)})
    return row, slices, bad


def _single_replay_task(task: tuple) -> dict[str, Any]:
    """(config, arm, blocks, dates, args, starts) -> start rows, slices and the event-day mismatches (one firm)."""
    import warnings

    import customer_slices as cs

    warnings.filterwarnings("ignore")
    config, arm, blocks, dates, args, starts = task
    sub = float(args["path"]["subscription"])
    n = len(blocks)
    rows, slices, bad = [], [], 0
    for s in starts:
        L = min(cj.WINDOW, n - s)
        lp_long = cs.replay(blocks[s:s + L], args)
        lps = {h: cs.replay(blocks[s:s + h], args) for h in cj.EXACT if h < L}
        r, sl, b = _start_rows(config, arm, s, dates[s], single_events(lp_long),
                               {h: single_events(x) for h, x in lps.items()}, sub,
                               lambda h, hh_, _l=lp_long, _x=lps: cs.slice_measures(_l if h is None else _x[h], hh_, sub))
        rows.append(r)
        slices += sl
        bad += b
    return {"arm": arm, "rows": rows, "slices": slices, "bad": bad}


def _joint_replay_task(task: tuple) -> dict[str, Any]:
    """(arm, config, kind, firms, mode, blocks, dates, setup, seed, starts) -> the same for a two-firm arm."""
    import warnings

    from propedge.research import hypo_hedge as hh
    from propedge.research import hypo_mirror as hm

    warnings.filterwarnings("ignore")
    arm, config, kind, firms, mode, blocks, dates, setup, seed, starts = task
    sub = float(setup.path["subscription"])
    n = len(blocks)
    want = []
    for s in starts:
        L = min(cj.WINDOW, n - s)
        want.append((s, L))
        want += [(s, h) for h in cj.EXACT if h < L]
    specs = [hh.PathSpec(seed=int(seed), blocks=blocks[s:s + h], horizon_days=int(h) + 1, replay=True) for s, h in want]
    if kind == "mirror":
        jps = hm.run_joint(specs, setup, n_firms=int(firms), mode=mode)
    else:
        jps = hh.run_joint(specs, setup, n_firms=int(firms), mode=mode, doubled=True)
    got = {k: jp for k, jp in zip(want, jps)}
    rows, slices, bad = [], [], 0
    for s in starts:
        L = min(cj.WINDOW, n - s)
        lp_long = got[(s, L)]
        lps = {h: got[(s, h)] for h in cj.EXACT if h < L}
        r, sl, b = _start_rows(config, arm, s, dates[s], joint_events(lp_long),
                               {h: joint_events(x) for h, x in lps.items()}, sub,
                               lambda h, hh_, _l=lp_long, _x=lps: hh.slice_measures(_l if h is None else _x[h], hh_, sub))
        rows.append(r)
        slices += sl
        bad += b
    return {"arm": arm, "rows": rows, "slices": slices, "bad": bad}


# ------------------------------------------------------------------------------------------------ the resampled tasks


def _joint_paths_task(task: tuple) -> list[dict]:
    """(config, kind, firms, mode, shift, blocks, setup, [(index, seed)], margin, horizon, fees) -> per path: the
    recorded file's row (as its writer built it) and the journey."""
    import warnings

    from propedge.research import hypo_hedge as hh
    from propedge.research import hypo_mirror as hm

    warnings.filterwarnings("ignore")
    config, kind, firms, mode, shift, blocks, setup, items, margin, horizon, fees = task
    specs = [hh.PathSpec(seed=int(s), blocks=blocks, horizon_days=int(horizon)) for _, s in items]
    if kind == "mirror":
        jps = hm.run_joint(specs, setup, n_firms=int(firms), mode=mode)
    else:
        jps = hh.run_joint(specs, setup, n_firms=int(firms), mode=mode, doubled=True)
    out = []
    for (i, s), jp in zip(items, jps):
        if kind == "mirror":
            r = hm.path_record(jp, margin=margin, subscription=fees[0], activation=fees[1])
            rec = {"net": r["net"], "fees": r["fees"], "combine_fees": r["combine_fees"],
                   "activation_fees": r["activation_fees"], "payouts_dollars": r["payouts_dollars"],
                   "needed": r["needed"], "combines_started": r["combines_started"],
                   "combines_resolved": len(r["resolved"]), "passes": len(r["pass_days"]),
                   "payouts": len(r["pay_days"]), "funded_accounts": r["funded_accounts"],
                   "funded_breached": r["funded_breached"], "pairs": r["pairs"], "funded_pairs": r["funded_pairs"],
                   **{f"combine_pairs_{k}": v for k, v in r["combine_pair_outcomes"].items()},
                   "pass_days": " ".join(str(d) for d in r["pass_days"]),
                   "pay_days": " ".join(str(d) for d in r["pay_days"]),
                   **{f"deal_{k}": (v if not isinstance(v, list) else " ".join(str(x) for x in v))
                      for k, v in r["deal"].items()}}
        else:
            r = hh.path_record(jp, margin=margin)
            rec = {"initial": r["initial"], "net": r["net"], "fees": r["fees"], "payouts_dollars": r["payouts_dollars"],
                   "deepest_loss_from_start": r["deepest_loss_from_start"], "needed": r["needed"],
                   "combines_started": r["combines_started"], "combines_resolved": len(r["resolved"]),
                   "passes": len(r["pass_days"]), "payouts": len(r["pay_days"]),
                   "pass_days": " ".join(str(d) for d in r["pass_days"]),
                   "pay_days": " ".join(str(d) for d in r["pay_days"]),
                   "resolved_passed": "".join("1" if ok else "0" for _, ok in r["resolved"]),
                   "pairs": r["pairs"], "pairs_with_pass": r["pairs_with_pass"],
                   "pairs_both_pass": r["pairs_both_pass"], "pair_passes": r["pair_passes"],
                   **{f"deal_{k}": (v if not isinstance(v, list) else " ".join(str(x) for x in v))
                      for k, v in r["deal"].items()}}
        out.append({"config": config, "shift": shift, "path": int(i), "seed": int(s), "record": rec,
                    "growth_record": r,
                    "journey": journey_of(joint_events(jp))})
    return out


def _pool_run(tasks: list[tuple], fn, workers: int, what: str) -> list:
    from propedge.campaign.lockstep import _WorkerEnvironment, path_pool

    pool, n = (path_pool(int(workers), n_tasks=len(tasks), memory_per_worker_gb=WORKER_GB)
               if int(workers) > 1 and len(tasks) > 1 else (None, 1))
    print(f"  {what}: {len(tasks)} tasks on {n} process(es)", flush=True)
    t0 = time.time()
    out = []
    step = max(1, len(tasks) // 10)
    if pool is None:
        for i, t in enumerate(tasks):
            out.append(fn(t))
            if (i + 1) % step == 0:
                print(f"    {i + 1}/{len(tasks)} tasks, {time.time() - t0:.0f} s", flush=True)
        return out
    try:
        with _WorkerEnvironment():
            futures = [pool.submit(fn, t) for t in tasks]
        for i, f in enumerate(futures):
            out.append(f.result())
            if (i + 1) % step == 0:
                print(f"    {i + 1}/{len(tasks)} tasks, {time.time() - t0:.0f} s", flush=True)
        return out
    finally:
        pool.shutdown()


# ------------------------------------------------------------------------------------------------ the identities


def _truth(v) -> bool:
    return str(v).strip().lower() in ("true", "1", "1.0")


def _same(x, y) -> bool:
    """Two recorded values equal: flags as flags, blanks as blanks, numbers to `TOL` (or 1e-12 relative), text as text."""
    if isinstance(x, (bool, np.bool_)) or isinstance(y, (bool, np.bool_)) or str(x) in ("True", "False")             or str(y) in ("True", "False"):
        return _truth(x) == _truth(y)
    xs, ys = ("" if x is None else str(x)), ("" if y is None else str(y))
    if xs.strip() == ys.strip():                   # the same text (a digit string such as `resolved_passed` too)
        return True
    if xs in ("", "nan", "None") and ys in ("", "nan", "None"):
        return True
    try:
        a, b = float(xs), float(ys)
    except ValueError:
        return xs.strip() == ys.strip()
    if np.isnan(a) and np.isnan(b):
        return True
    return bool(abs(a - b) <= max(TOL, 1e-12 * max(abs(a), abs(b))))


def _read_paths(rd: Path, name: str) -> pd.DataFrame:
    """A per-path file as text (its digit strings, e.g. `resolved_passed`, stay text), after its manifest check."""
    from propedge.reporting.results import verify_result

    ok, msg = verify_result(rd / name)
    if not ok:
        raise SystemExit(f"REFUSED ({DECISION}): {name}: {msg}")
    return pd.read_csv(rd / name, dtype=str, keep_default_na=False)


def records_problems(mine: list[dict], ref: pd.DataFrame, cols: list[str], what: str) -> list[str]:
    """Our records (path order) against the reference's rows (path order) on `cols`."""
    ref = ref.assign(_p=ref["path"].astype(float).astype(int)).sort_values("_p").reset_index(drop=True)
    mine = sorted(mine, key=lambda r: int(r["path"]))
    if len(mine) > len(ref):
        return [f"{what}: {len(mine)} paths against the reference's {len(ref)}"]
    out = []
    for c in cols:
        bad = [i for i, r in enumerate(mine) if not _same(r.get(c), ref[c].iloc[i])]
        if bad:
            i = bad[0]
            out.append(f"{what} {c}: path {i} {mine[i].get(c)!r} against {ref[c].iloc[i]!r} ({len(bad)} differ)")
    return out


def slice_problems(mine: pd.DataFrame, ref_file: Path, config: str, arm: str) -> list[str]:
    """Our slices (one arm) against a slice file's rows of `config` at `arm`, start for start at each horizon, on
    `a3_brk30_cb20.SLICE_ID_COLS`."""
    import a3_brk30_cb20 as C

    from propedge.reporting.results import read_result

    ref = read_result(ref_file)
    ref = ref[(ref["section"] == "slice") & (ref["config"].astype(str) == config) & (ref["arm"].astype(str) == arm)]
    out = []
    for h in (21, 63, 126):
        a = mine[mine["horizon"].astype(int) == h].sort_values("start_day").reset_index(drop=True)
        b = ref[ref["horizon"].astype(int) == h]
        b = b[b["start_day"].astype(int).isin(set(a["start_day"].astype(int)))].sort_values("start_day")
        b = b.reset_index(drop=True)
        if len(a) == 0 or len(a) != len(b):
            out.append(f"{config} {arm} horizon {h}: {len(a)} slices against {len(b)} in {ref_file.name}")
            continue
        for c in C.SLICE_ID_COLS:
            bad = [i for i in range(len(a)) if not C._slice_same(a[c].iloc[i], b[c].iloc[i])]
            if bad:
                i = bad[0]
                out.append(f"{config} {arm} h{h} start {int(a['start_day'].iloc[i])} {c}: {a[c].iloc[i]!r} against "
                           f"{b[c].iloc[i]!r} in {ref_file.name} ({len(bad)} differ)")
    return out


def summary_problems(mine: pd.DataFrame, ref_file: Path, arm: str) -> list[str]:
    """Our slices' summary (`customer_slices.summarise`) against a hypothetical study's `slices` rows for `arm`."""
    import customer_slices as cs

    from propedge.reporting.results import read_result

    ref = read_result(ref_file)
    ref = ref[(ref["section"] == "slices") & (ref["arm"].astype(str) == arm)]
    s = cs.summarise(mine.assign(config=arm, arm="verdict"))
    out = []
    for h in (21, 63, 126):
        a, b = s[s["horizon"].astype(int) == h], ref[ref["horizon"].astype(float).astype(int) == h]
        if len(a) != 1 or len(b) != 1:
            out.append(f"{arm} horizon {h}: {len(a)} summaries against {len(b)} in {ref_file.name}")
            continue
        for c in cs.SUMMARY_COLS:
            if not _same(a[c].iloc[0], b[c].iloc[0]):
                out.append(f"{arm} h{h} {c}: {a[c].iloc[0]!r} against {b[c].iloc[0]!r} in {ref_file.name}")
    return out


# ------------------------------------------------------------------------------------------------ the campaigns


class Inputs:
    """Everything built once: the single-firm campaigns (replay and resampled), the plans, D-514's and D-515's."""

    def __init__(self, rd: Path, configs: list[dict]):
        self.rd = rd
        kinds = {c["kind"] for c in configs}
        self.single: dict[str, Any] = {}
        if kinds & {"p13", "fv3c"}:
            import a3_compliance as a3
            import customer_slices as cs

            self.noclose = a3.noclose_policy(rd)
            if "p13" in kinds:
                print("P-13's campaign from the A3 rung cache...", flush=True)
                self.single["p13"] = cs.p13_campaign()
                self._p13_gate_inputs()
            if "fv3c" in kinds:
                print("FV3-C's development campaign...", flush=True)
                import fv3c_compliance as fvc

                self.single["fv3c"] = cs.fv3c_campaign(rd)
                self.fv3c_gate = fvc.fv3c_dev_campaign(rd)
        if "hedge" in kinds:
            print("D-514's campaign and the opposite walk...", flush=True)
            import hypo_hedge_a3 as ha

            self.ha = ha
            self.hI = ha.inputs(rd)
            self.h_camp, self.h_rep = ha.setups(self.hI)
            self.h_blocks = {s: ha.arm_blocks(self.hI, s) for s in ("point", "lower_bound")}
            self.h_dates = [str(d) for d in self.hI["days"]]
        if "mirror" in kinds:
            print("D-515's resolution reading, choice and campaign...", flush=True)
            import hypo_mirror as hmS

            from propedge.research import hypo_mirror as hm

            fee_rt = hmS.fee()
            days = hmS.day_set()
            pairs = hmS.walk_all(days, fee_rt)
            table = hm.resolution_table(pairs)
            choice = hm.choose(table, sorted({int(d[:4]) for d in days}), fee_rt)
            sz = hm.sizing(choice["stop_points"], fee_rt)
            t = hmS.trade_set(pairs, choice)
            st = hmS.cell_stats(t)
            cell, opp = hm.blocks(t, days)
            self.mS = hmS
            self.m_blocks = {s: hmS.arm_blocks(cell, opp, s, st["delta_r"]) for s in ("point", "lower_bound")}
            self.m_camp, self.m_rep = hmS.setups(sz, len(choice["slots"]))
            self.m_dates = list(days)
            self.m_choice = {"stop_points": float(choice["stop_points"]), "slots": [hmS.ct(s) for s in choice["slots"]]}

    def _p13_gate_inputs(self) -> None:
        import a3_brk30 as B
        import a3_compliance as a3

        L = B.inputs()
        t, days = B.cell_trades(L)
        self.p13_L, self.p13_ci = L, a3.campaign_inputs(L, t, days)

    def subscription(self, c: dict) -> float:
        """One subscription of the configuration's firm (the bankroll reading's margin, D-508)."""
        if c["kind"] in ("p13", "fv3c"):
            return float(self.single[c["kind"]].kw["rules"].subscription)
        return float((self.m_rep if c["kind"] == "mirror" else self.h_rep).path["subscription"])

    def plan(self, kind: str, table: str):
        if table == "noclose":
            return self.noclose
        return self.p13_ci["policy"] if kind == "p13" else self.fv3c_gate.kw["risk_policy"]


# ------------------------------------------------------------------------------------------------ step 1: resampled


def resampled_single(I: Inputs, c: dict, n_paths: int, workers: int) -> tuple[dict, dict, list[str]]:
    """One single-firm configuration's recorded run re-run: {shift: [journey]}, {shift: gate row}, the problems against
    its per-path file (every column the file and our record share)."""
    import a3_brk30 as B
    import atlas_a3 as A
    import fv3c_compliance as fvc
    import fv3d_lever_test as lt
    import portfolio_stage as ps

    from propedge.campaign import gate

    sink: list[dict] = []
    journeys: dict[str, list[dict]] = {}
    if c["kind"] == "p13":
        fcfg = I.p13_L["fcfg"]
        inner = ps.composed_hook({"margin": float(fcfg["portfolio"]["margin"]),
                                  "block_days": int(fcfg["portfolio"]["block_days"])}, sink=sink)
        base = lt.lever_hook(inner)
    else:
        base, inner = fvc.hook_of(I.fv3c_gate, sink)

    def hook(shift, p, paths):
        out = base(shift, p, paths)
        if float(p) == 0.0:
            journeys[shift] = [journey_of(single_events(x)) for x in paths]
        return out

    ps._label(inner, c["config"])
    if c["kind"] == "p13":
        ci, L = I.p13_ci, I.p13_L
        kw = A.gate_kwargs(ci["blocks"], L["fcfg"], float(L["tv"]), I.plan("p13", c["table"]), ci["e_by"],
                           ci["lb_by"], hook, seed=int(c["seed"]), n_paths=int(n_paths),
                           horizon=int(L["fcfg"]["gate"]["campaign"]["horizon_days"]), capacity=ci["cap"],
                           levels=(0.0,), rtp=False, one_at_a_time=B.STRICT_GAP, purchase_budget=c["budget"])
        df, _ = gate.run_gate(kw.pop("blocks"), workers=int(workers), **kw)
    else:
        g = I.fv3c_gate
        df, _ = gate.run_gate(g.blocks, path_hook=hook, workers=int(workers),
                              **fvc.run_kwargs(g, I.plan("fv3c", c["table"]), c["budget"], n_paths))
    file, filt, run = c["ref"]
    ref = _read_paths(I.rd, file)
    for k, v in filt.items():
        ref = ref[ref[k] == v]
    problems = []
    for shift in ("point", "lower_bound"):
        r = ref[(ref["run"] == run) & (ref["shift"] == shift) & (ref["enforcement_p"].astype(float) == 0.0)]
        mine = [x for x in sink if x["run"] == c["config"] and x["shift"] == shift and float(x["enforcement_p"]) == 0]
        cols = [k for k in r.columns if k in mine[0] and k not in ("run", "shift", "enforcement_p", "path")] if mine else []
        if int(n_paths) != N_PATHS:            # the base (the run's required p90) and its measures need every path
            import zero_edge_decomposition as zd

            cols = [k for k in cols if k in zd.PATH_COLS]
        problems += records_problems(mine, r, cols, f"{c['config']} {shift}")
        if len(mine) != int(n_paths):
            problems.append(f"{c['config']} {shift}: {len(mine)} paths run, not {n_paths}")
        nets = [float(x["final_cash"]) - float(x["initial_bankroll"]) for x in sorted(mine, key=lambda x: x["path"])]
        jnet = [j["net_126"] for j in journeys.get(shift, [])]
        if len(jnet) != len(nets):
            problems.append(f"{c['config']} {shift}: {len(jnet)} journeys against {len(nets)} paths")
    rows = {s: df[(df["shift"] == s) & np.isclose(df["enforcement_p"].astype(float), 0.0)].iloc[0].to_dict()
            for s in ("point", "lower_bound")}
    return journeys, rows, problems


def resampled_joint(I: Inputs, c: dict, n_paths: int, workers: int) -> tuple[dict, dict, list[str]]:
    """One two-firm arm's recorded run re-run: {shift: [journey]}, {shift: readings}, the problems against its file."""
    from propedge.campaign.lockstep import path_seeds
    from propedge.research import hypo_hedge as hh
    from propedge.research import hypo_mirror as hm

    if c["kind"] == "mirror":
        S = I.mS
        arm_def = next(a for a in S.ARMS if a[0] == c["arm"])
        blocks, setup, seed, margin, horizon = I.m_blocks, I.m_camp, S.SEED, S.MARGIN, S.HORIZON
        fees = (float(setup.path["subscription"]), float(setup.path["activation"]))
    else:
        S = I.ha
        arm_def = next(a for a in S.ARMS if a[0] == c["arm"])
        blocks, setup, seed, margin, horizon = I.h_blocks, I.h_camp, S.SEED, I.hI["margin"], I.hI["horizon"]
        fees = (0.0, 0.0)
    _, firms, mode = arm_def
    seeds = list(enumerate(path_seeds(int(seed), int(n_paths))))
    tasks = [(c["config"], c["kind"], firms, mode, s, blocks[s], setup, seeds[j:j + CHUNK_PATHS], margin, horizon, fees)
             for s in ("point", "lower_bound") for j in range(0, len(seeds), CHUNK_PATHS)]
    res = [r for chunk in _pool_run(tasks, _joint_paths_task, workers, f"{c['config']} resampled") for r in chunk]
    file, _, run = c["ref"]
    ref = _read_paths(I.rd, file)
    journeys, readings, problems = {}, {}, []
    for s in ("point", "lower_bound"):
        mine = sorted([r for r in res if r["shift"] == s], key=lambda r: r["path"])
        rr = ref[(ref["arm"] == run) & (ref["shift"] == s)]
        recs = [{**r["record"], "path": r["path"], "seed": r["seed"]} for r in mine]
        cols = [k for k in rr.columns if k in recs[0] and k not in ("path",)] if recs else []
        problems += records_problems(recs, rr, cols, f"{c['config']} {s}")
        journeys[s] = [r["journey"] for r in mine]
        gr = [r["growth_record"] for r in mine]
        readings[s] = (hm.readings(gr, margin=margin) if c["kind"] == "mirror" else hh.readings(gr, margin=margin))
    return journeys, readings, problems


# ------------------------------------------------------------------------------------------------ step 2: replays


def replay_jobs(I: Inputs, c: dict, starts: int | None) -> list[tuple]:
    import customer_slices as cs

    tasks = []
    if c["kind"] in ("p13", "fv3c"):
        camp = I.single[c["kind"]]
        for arm in ARMS:
            blk = cs.arm_blocks(camp, arm)
            args = cs.engine_args(camp.kw, arm, camp.blocks, risk_policy=I.plan(c["kind"], c["table"]),
                                  purchase_budget=c["budget"])
            if c["kind"] == "p13":
                args = {**args, "seed": int(c["seed"])}
            elif int(args["seed"]) != int(c["seed"]):
                raise SystemExit(f"REFUSED ({DECISION}): {c['config']}'s replay seed {args['seed']} is not {c['seed']}.")
            n = len(blk) if starts is None else min(int(starts), len(blk))
            for j in range(0, n, CHUNK_STARTS):
                tasks.append(("single", (c["config"], arm, blk, camp.dates, args, list(range(j, min(n, j + CHUNK_STARTS))))))
        return tasks
    if c["kind"] == "mirror":
        S, blocks, dates, setup, seed = I.mS, I.m_blocks, I.m_dates, I.m_rep, I.mS.SEED
    else:
        S, blocks, dates, setup, seed = I.ha, I.h_blocks, I.h_dates, I.h_rep, I.ha.SLICE_SEED
    _, firms, mode = next(a for a in S.ARMS if a[0] == c["arm"])
    for arm in ARMS:
        blk = blocks[SHIFT_OF[arm]]
        n = len(blk) if starts is None else min(int(starts), len(blk))
        for j in range(0, n, CHUNK_STARTS):
            tasks.append(("joint", (arm, c["config"], c["kind"], firms, mode, blk, dates, setup, seed,
                                    list(range(j, min(n, j + CHUNK_STARTS))))))
    return tasks


def _replay_dispatch(task: tuple) -> dict[str, Any]:
    kind, t = task
    return _single_replay_task(t) if kind == "single" else _joint_replay_task(t)


def replay_problems(I: Inputs, c: dict, sl: pd.DataFrame, *, all_starts: bool = True) -> list[str]:
    """The replay's slices against the files on record; a summary (over every start) only when every start ran."""
    out = []
    for arm, refs in c["slices"].items():
        mine = sl[sl["arm"] == arm]
        for file, cfg in refs:
            out += slice_problems(mine, I.rd / file, cfg, arm)
    if c["summary"] is not None and all_starts:
        file, arm = c["summary"]
        out += summary_problems(sl[sl["arm"] == "verdict"], I.rd / file, arm)
    return out


# ------------------------------------------------------------------------------------------------ step 3: the tables


def metric_rows(units: pd.DataFrame, config: str, arm: str, source: str, pool: str, sub: float) -> list[dict]:
    rows = []
    for m in cj.metrics(units, sub):
        rows.append({"section": "metric", "config": config, "arm": arm, "source": source, "pool": pool,
                     "label": LABEL_OF[pool], "key": cj.metric_key(m["milestone"], m["measure"], m["at_days"]), **m})
    return rows


def tables(metric: pd.DataFrame, beside: dict[tuple[str, str, str], float]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The metric table with its best flags, and the frontier rows, per source on the verdict arm."""
    metric = metric.copy()
    metric["best"] = False
    metric["best_incl_assumed"] = False
    pools = {"best": (TOPSTEP,), "best_incl_assumed": (TOPSTEP, ASSUMED)}
    fr = []
    for source, g in metric[metric["arm"] == "verdict"].groupby("source", sort=False):
        for flag, allowed in pools.items():
            el = sorted({c for c, p in zip(g["config"], g["pool"]) if p in allowed},
                        key=list(dict.fromkeys(g["config"])).index)
            metric.loc[g.index, flag] = cj.best_flags(g, el).to_numpy()
            for r in cj.frontier(g, el):
                fr.append({"section": "frontier", "source": source, "arm": "verdict",
                           "frontier_pool": "topstep" if flag == "best" else "topstep_and_assumed_second_firm", **r})
    frontier = pd.DataFrame(fr)
    pool_of = dict(zip(metric["config"], metric["pool"]))
    frontier["pool"] = frontier["config"].map(pool_of)
    frontier["label"] = frontier["pool"].map(LABEL_OF)
    frontier["growth_on_required_beside"] = [beside.get((c, "verdict", s), float("nan"))
                                             for c, s in zip(frontier["config"], frontier["source"])]
    return metric, frontier


# ------------------------------------------------------------------------------------------------ the study


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="the identities only; nothing written")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--paths", type=int, default=N_PATHS, help="resampled paths (500 for the study)")
    ap.add_argument("--starts", type=int, default=None, help="test seam: only the first replay starts")
    ap.add_argument("--configs", default=None, help="test seam: a comma-separated subset")
    ap.add_argument("--out", default=None, help="test seam: write a partial run to this folder outside results/")
    a = ap.parse_args(argv)
    if a.out is not None:
        out = Path(a.out).resolve()
        if out == RESULTS_DIR.resolve() or RESULTS_DIR.resolve() in out.parents:
            print(f"REFUSED ({DECISION}): --out must be outside results/.")
            return 2
        out.mkdir(parents=True, exist_ok=True)
        results_dir = out
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    full = a.paths == N_PATHS and a.starts is None and a.configs is None
    if not a.check and not full and a.out is None:
        print(f"REFUSED ({DECISION}): a partial run (--paths / --starts / --configs) writes nothing; use --check.")
        return 2
    configs = [c for c in CONFIGS if a.configs is None or c["config"] in a.configs.split(",")]
    t_all = time.time()
    I = Inputs(RESULTS_DIR, configs)
    idents: list[dict] = []
    units: dict[tuple[str, str, str], list[dict]] = {}
    beside: dict[tuple[str, str, str], float] = {}
    starts_rows: list[dict] = []
    path_rows: list[dict] = []

    # 1. the resampled runs, each reproduced from its per-path file before anything is read
    for c in configs:
        t0 = time.time()
        if c["kind"] in ("p13", "fv3c"):
            js, rows, bad = resampled_single(I, c, a.paths, a.workers)
            g = {s: float(rows[s]["pf_growth_on_base_p50"]) for s in rows}
        else:
            js, rows, bad = resampled_joint(I, c, a.paths, a.workers)
            g = {s: float(rows[s]["growth_on_required"]) for s in rows}
        if bad:
            print(f"REFUSED ({DECISION}): {c['config']} does not reproduce {c['ref'][0]} -- " + "; ".join(bad[:8]))
            return 3
        print(f"identity HOLDS: {c['config']} = {c['ref'][0]} ({c['ref'][2]}), {a.paths} paths, point and bound "
              f"({time.time() - t0:.0f} s)", flush=True)
        idents.append({"section": "identity", "config": c["config"], "source": "resampled", "holds": True,
                       "check": f"the configuration's {a.paths} paths at both arms re-run equal results/{c['ref'][0]}'s "
                                f"'{c['ref'][2]}' rows on every column both hold"})
        for arm in ARMS:
            s = SHIFT_OF[arm]
            units[(c["config"], arm, "resampled")] = js[s]
            beside[(c["config"], arm, "resampled")] = g[s]
            for i, j in enumerate(js[s]):
                path_rows.append({"config": c["config"], "arm": arm, "path": i, "label": LABEL_OF[c["pool"]], **j})

    # 2. the replays, each identical to the slices on file before anything is read
    for c in configs:
        t0 = time.time()
        res = _pool_run(replay_jobs(I, c, a.starts), _replay_dispatch, a.workers, f"{c['config']} replay")
        rows = [r for x in res for r in x["rows"]]
        sl = pd.DataFrame([{**s, "arm": x["arm"]} for x in res for s in x["slices"]])
        mism = int(sum(x["bad"] for x in res))
        bad = ([f"{mism} exact runs whose event days differ from the long run's"] if mism else []) \
            + replay_problems(I, c, sl, all_starts=a.starts is None)
        if bad:
            print(f"REFUSED ({DECISION}): {c['config']}'s replay is not the slices on file -- " + "; ".join(bad[:8]))
            return 3
        print(f"identity HOLDS: {c['config']} replay, {len(rows)} starts x arms, slices equal "
              + (", ".join(f"{f}:{k}" for refs in c["slices"].values() for f, k in refs) or
                 f"{c['summary'][0]}'s summary") + f" ({time.time() - t0:.0f} s)", flush=True)
        idents.append({"section": "identity", "config": c["config"], "source": "replay", "holds": True,
                       "check": "every start's 21/63/126-session slice equals "
                                + ("; ".join(f"results/{f} '{k}' ({arm})" for arm, refs in c["slices"].items()
                                             for f, k in refs) if c["slices"] else
                                   f"results/{c['summary'][0]}'s slice summary for '{c['summary'][1]}'")
                                + "; the long run's event days equal every exact run's"})
        for arm in ARMS:
            units[(c["config"], arm, "replay")] = [r for r in rows if r["arm"] == arm]
            beside[(c["config"], arm, "replay")] = float("nan")
        for r in rows:
            r["label"] = LABEL_OF[c["pool"]]
            r["pool"] = c["pool"]
        starts_rows += rows
    if "p14" in [c["config"] for c in configs] and "p13_noclose_b20" in [c["config"] for c in configs]:
        bad = []
        for arm in ARMS:
            x = pd.DataFrame(units[("p14", arm, "replay")])[list(cj.UNIT_COLS)]
            y = pd.DataFrame(units[("p13_noclose_b20", arm, "replay")])[list(cj.UNIT_COLS)]
            if not all(_same(p, q) for p, q in zip(x.to_numpy().ravel(), y.to_numpy().ravel())) or len(x) != len(y):
                bad.append(arm)
        if bad:
            print(f"REFUSED ({DECISION}): P-14's replay is not P-13-without-closure-budget-20's ({bad}).")
            return 3
        idents.append({"section": "identity", "config": "p14", "source": "replay", "holds": True,
                       "check": "P-14's replay equals p13_noclose_b20's start for start at both arms (a replay draws "
                                "nothing; only the seed differs)"})
        print("identity HOLDS: P-14's replay = p13_noclose_b20's, start for start", flush=True)
    if a.check:
        print(f"every identity holds; nothing written (--check). {time.time() - t_all:.0f} s")
        return 0

    # 3. the readings (only now)
    sub_of = {c["config"]: I.subscription(c) for c in configs}
    metric, curves = [], []
    pool_of = {c["config"]: c["pool"] for c in configs}
    for (config, arm, source), us in units.items():
        u = pd.DataFrame(us)
        metric += metric_rows(u, config, arm, source, pool_of[config], sub_of[config])
        for r in cj.curve(u):
            curves.append({"section": "curve", "config": config, "arm": arm, "source": source, "pool": pool_of[config],
                           "label": LABEL_OF[pool_of[config]], **r})
    mdf, fdf = tables(pd.DataFrame(metric), beside)
    res = pd.concat([pd.DataFrame(idents), mdf, fdf, pd.DataFrame(curves), pd.DataFrame(starts_rows)],
                    ignore_index=True)
    res.insert(1, "reading", READING)
    if (res.loc[res["pool"] == HYPO, ["best", "best_incl_assumed"]].fillna(False).astype(bool).any().any()
            or res.loc[(res["section"] == "frontier") & (res["pool"] == HYPO)].shape[0]):
        raise SystemExit(f"REFUSED ({DECISION}): a hypothetical_hedge row is marked best or on a frontier.")
    seconds = time.time() - t_all
    counter = VariantCounter(path=rd / "variants.jsonl")
    for c in configs:
        for arm in ARMS:
            hypo = c["pool"] == HYPO
            counter.record(prereg_id=HYPO_FAMILY_ID if hypo else FAMILY_ID, seed=int(c["seed"]), exploratory=True,
                           params={"study": "customer journey (D-518)", "config": c["config"], "arm": arm,
                                   "pool": c["pool"], "sources": ["replay", "resampled"]},
                           label=f"D-518's customer journey: {c['config']} ({arm})" + (f" -- {HYPO}" if hypo else ""))
    params = {"decision": DECISION, "configs": [{k: (list(v) if isinstance(v, tuple) else v)
                                                 for k, v in c.items() if k not in ("slices",)} for c in configs],
              "arms": {a_: SHIFT_OF[a_] for a_ in ARMS}, "best_arm": "verdict", "n_paths": a.paths,
              "window": cj.WINDOW, "month": cj.MONTH, "pass_days": list(cj.PASS_DAYS),
              "funded_days": list(cj.FUNDED_DAYS), "payout_days": list(cj.PAYOUT_DAYS), "ahead": list(cj.AHEAD),
              "bankroll": list(cj.BANKROLL), "deep_loss_day": cj.DEEP_LOSS_DAY, "exact_runs": list(cj.EXACT),
              "pools": {"best": [TOPSTEP], "best_incl_assumed": [TOPSTEP, ASSUMED], "never": [HYPO]},
              "mirror_choice": getattr(I, "m_choice", None), "percentiles": "numpy linear",
              "placement": "off", "enforcement_p": 0.0, "workers": int(a.workers), "seconds": round(seconds, 1)}
    write_result(res, RESULT, script=SCRIPT, seed=P13_SEED, exploratory=True, results_dir=results_dir,
                 variant_count=2 * len(configs), parameters=params,
                 notes={"status": READING, "labels": "hypothetical_hedge rows are never eligible (tier 1, prohibited "
                        "at Topstep 13747047 and Lucid 11404734); assumed_second_firm rows only in the wider pool",
                        "ties": "a measure's ties are all best (to 1e-9); a measure equal for every eligible configuration, "
                                "or blank for all, marks none (it distinguishes nothing) -- an implementation rule set "
                                "before the full run's reading",
                        "variant_count_rule": f"one reading per configuration and arm, under {FAMILY_ID} or "
                                              f"{HYPO_FAMILY_ID}"},
                 description="EXPLORATORY (D-518): the customer journey -- chance by day of a first pass, funded "
                             "account and payout, the cash spent before them, net at 1/3/6 months, payout rhythm and the "
                             "bad-case bankroll -- per configuration, arm and source (replay of every start in historical "
                             "order; the recorded run's 500 resampled paths), each measure's best eligible configuration "
                             "and the frontier; curves and every start's journey for the Studio. No selection.")
    write_result(pd.DataFrame(path_rows), f"{RESULT}_paths", script=SCRIPT, seed=P13_SEED, exploratory=True,
                 results_dir=results_dir, parameters={"result": f"{RESULT}.csv", "window": cj.WINDOW},
                 notes={"status": READING, "companion_of": f"{RESULT}.csv"},
                 description="EXPLORATORY (D-518): each resampled path's journey on its first 126 sessions.")
    pd.set_option("display.width", 250)
    print(fdf.to_string(index=False))
    print(f"written: {RESULT}.csv and {RESULT}_paths.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
