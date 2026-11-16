"""EXPLORATORY (D-593): Lucid seats ADDED to P-16's five Topstep seats -- 5+1, 5+2, 5+3, 5+5 against P-16's own call
(5+0), unhedged, on the full development history and on D-578 (2)'s two spans alone.

    python scripts/rc150_added_lucid.py --check --paths 4 --starts 6     # every identity, every cell, both spans at 4
                                                                         #   paths; no reading printed, nothing written
    python scripts/rc150_added_lucid.py                                  # the screen (a clean checkout, D-474; workers 1)

**The design** (`propedge.research.rc150_added_lucid`, D-593's row pinned by its sha256 and phrase by phrase): firm 0
Topstep with P-16's five seats and 20-in-21 budget, firm 1 Lucid with k seats (1, 2, 3, 5) and floor(20 x k / 5) in 21
trading days, inside Lucid's household caps (5 funded, 10 evaluations, 10 in total: k <= 5, refused above). Everything
else is D-575's Lucid screen, by import from `scripts/rc150_firm_split.py`: `inputs("lucid")` (P-16's cell
`rc_s150_all` by its content hash, the opposite side aligned one for one, P-16's engine arguments, Lucid's verified
contract through `lucid_setup` with `lucid_upper_bound`'s two unpriced fees at zero and the household rule's
conservative reading `HOUSEHOLD_CLOSES_AT_LIVE`), `arm_blocks` (point, bound through `mirror_shift`, zero-edge twin),
`firm_setups` (each firm's seats and budget; Lucid's caps), `readings_of`, `run_journey` (D-518's journey on the bound
arm's replay, every start; the margin one evaluation of the dearest firm), the resume file (D-540). Campaign seed
20261131, coin seed 20261102, 500 paths; the unhedged deal of `hypo_hedge.run_joint` (each signal to one account at one
firm, one position at a time per firm with D-429's gap, one pooled wallet, D-206).

**Readings** per cell (D-593 (3)): growth on the required bankroll at the bound and the point, the required bankroll,
trades taken a session per firm (`trades_taken_per_session_topstep` / `_lucid`) and pooled, payouts a month pooled and
per firm, the share of paths where the household rule closed every Lucid seat (`household_closed_share`), the zero-edge
twin, D-518's journey and D-508's slices (as D-575). **The spans** (D-578 (2), `rc150_routing`'s G3 construction): each
cell on 2020-01-01 .. 2023-12-31 and on 2024-01-01 .. 2026-07-16 alone -- the span's cell built by
`rc_stop_walkforward.cell` on the span's days (its own cutoff), its opposite side the same walk with every coin side
negated (aligned one for one), its own pooled 0.05 bound (`a3_brk30.check_bounds`), the day capacity its own busiest day,
the engine arguments rebuilt on the span (`span_inputs`, `rc150_firm_split.inputs`' construction); the same seeds; the
bound and the point (no twin, no journey on a span).

**Identities, each refusing:** (a) the declaration (D-593's row's sha256 and phrases); Lucid's caps as `lucid_terms`
reads them; (b) the cell's content hash is P-16's (`rc150_firm_split.inputs`); (c) 5+0 through the joint engine
reproduces P-16's single-firm engine call (`rc_screen.Runner`) path for path on `PATH_COLS` for the first
`IDENTITY_PATHS` paths at both shifts, with its growth and required bankroll there; (d) the span construction's walk
rebuilds P-16's cell (content hash) and the full-history opposite side `rc150_firm_split.inputs` built; (e) on each span,
5+0 through the joint engine reproduces `rc_screen.Runner` with the span's bounds path for path (as (c)); (f) the full
run only: 5+0 at 500 paths reproduces `rc_width_screen.csv`'s `rc_s150_all` (growth at the bound and the point, the
required bankroll) and, on each span, `rc150_routing.csv`'s G3 row for R0 (the same computation: `rc_screen.Runner` on
the span's cell with its bounds, rule None).

**The rule** (D-593 (4), `rc150_added_lucid.verdict`): a cell is a candidate only if its growth at the bound exceeds
5+0's by more than 0.05, P-16's trades resolve every offered R (`atlas_a3.resolution`, as `rc150_routing`), and it is not
below 5+0 at the bound on either span alone. Every figure is an upper bound on Lucid's two unpriced fees.

Writes `results/rc150_added_lucid.csv` (EXPLORATORY; sections declaration, identity, cell, twin, journey, slices, span,
resolution, verdict) with its manifest; four variants under `D-593:rc150_added_lucid` (5+1, 5+2, 5+3, 5+5).
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

import rc150_firm_split as F  # noqa: E402
from propedge.research import customer_journey as cj  # noqa: E402
from propedge.research import hypo_hedge as hh  # noqa: E402
from propedge.research import rc150_added_lucid as M  # noqa: E402

SCRIPT = M.SCRIPT
DECISION = M.DECISION
STOP = 150
IDENTITY_PATHS = F.IDENTITY_PATHS
TOL = F.TOL
FIRM_NAMES = ("topstep", F.LUCID)
ROUTING_FILE = "rc150_routing.csv"
ROUTING_REF = "R0_longest_waiting"
MONTH = 21


# ------------------------------------------------------------------------------------------------ the span inputs


def span_inputs(I: dict, t: pd.DataFrame, fa: pd.DataFrame, days: list[str], e_by: dict, lb_by: dict) -> dict[str, Any]:
    """`rc150_firm_split.inputs`' construction on one span: the span's cell `t` and its aligned opposite side `fa` on
    the span's `days`, with the span's own bounds (`a3_brk30.check_bounds`, as `rc_screen.Runner` takes them from
    `rc150_routing`'s G3), the span's capacity, P-16's engine arguments rebuilt on the span and Lucid as firm 1."""
    import a3_brk30 as B
    import atlas_a3 as A
    import customer_slices as cs
    import rc_screen as S
    import score_fv3_grid as gf

    L = I["L"]
    fcfg, tv = L["fcfg"], float(L["tv"])
    keys = B.rrs(t)
    if B.rrs(fa) != keys:
        raise SystemExit(f"REFUSED ({DECISION}): a span's opposite side carries other R values.")
    e_opp, _ = B.check_bounds(fa, days, keys)
    cell, n1 = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    opp, n2 = gf.gate_blocks(fa, days, tv, keys, require_sides=True, require_exits=True)
    if n1 != len(t) or n2 != len(t):
        raise SystemExit(f"REFUSED ({DECISION}): a span's blocks hold a different number of trades.")
    cap = B.capacity(t, fcfg)
    horizon = int(fcfg["gate"]["campaign"]["horizon_days"])
    kw = A.gate_kwargs(cell, fcfg, tv, I["plan"], dict(e_by), dict(lb_by), None, seed=S.SEED, n_paths=M.N_PATHS,
                       horizon=horizon, capacity=cap, levels=(0.0,), rtp=False, one_at_a_time=S.STRICT_GAP,
                       purchase_budget=S.BUDGET)
    kw.pop("blocks")
    args = cs.engine_args(kw, "point", cell, purchase_budget=S.BUDGET)
    camp = hh.with_capacity(hh.setup_from_engine_args(args, funded_horizon_days=horizon, combine_max_days=2000),
                            2 * cap)
    rep = hh.with_capacity(hh.setup_from_engine_args(args), 2 * cap)
    p = camp.path
    if (int(p["max_concurrent_accounts"]), int(p["max_concurrent_combines"]), int(p["max_total_accounts"] or 0),
            tuple(p.get("purchase_budget") or ())) != (F.FULL_SEATS, F.FULL_SEATS, F.FULL_SEATS,
                                                       (F.FULL_BUDGET, F.BUDGET_WINDOW)):
        raise SystemExit(f"REFUSED ({DECISION}): a span's engine call is not five seats with the 20-in-21 budget.")
    return {"I": I, "t": t, "fa": fa, "cell": cell, "opp": opp, "days": list(days), "e_by": dict(e_by),
            "lb_by": dict(lb_by), "camp1": F.lucid_setup(camp), "rep1": F.lucid_setup(rep), "second_firm": F.LUCID,
            "e_opp": e_opp, "delta_r": float(kw["lb"]) - float(kw["e"]),
            "delta_by_rr": {float(k): float(lb_by[k]) - float(e_by[k]) for k in e_by},
            "fresh_rr": float(fcfg["state_policy"]["fresh"]["funded_rr"]), "cap": int(cap), "horizon": horizon,
            "camp": camp, "rep": rep, "margin": float(fcfg["portfolio"]["margin"]),
            "subscription": float(rep.path["subscription"])}


def build_spans(I: dict, X: dict) -> tuple[dict[str, dict], list[dict], list[str]]:
    """The walk (`rc_stop_walkforward.walk_stop`, `rc150_routing`'s), identity (d), and each span's inputs; with each
    span's resolution beside. Returns (span inputs, resolution rows, problems)."""
    import a3_brk30 as B
    import atlas_a3 as A
    import hypo_hedge_a3 as ha
    import rc150_dev_test as R150
    import rc_dev_test as D
    import rc_stop_walkforward as WF

    if {k: tuple(v) for k, v in WF.SPANS.items()} != {k: tuple(v) for k, v in M.SPANS.items()}:
        return {}, [], [f"rc_stop_walkforward.SPANS {WF.SPANS} are not D-578 (2)'s {M.SPANS}"]
    W = WF.walk_stop(I, STOP)
    Wn = {**W, "coins": {k: -int(v) for k, v in W["coins"].items()}}     # the same walk, every coin side the other way
    days = list(W["days"])
    bad = []
    if days != list(X["days"]):
        bad.append("the walk's development days are not rc150_firm_split.inputs' days")
    full = WF.cell(W, STOP, days)["trades"]
    if full is None or D.trades_hash(full) != R150.TRADES_SHA256:
        bad.append("the span construction's walk does not rebuild P-16's cell (content hash)")
    else:
        fo = WF.cell(Wn, STOP, days)["trades"]
        if fo is None or D.trades_hash(ha.align_opposite(full, fo)) != D.trades_hash(X["fa"]):
            bad.append("the span construction's opposite side is not rc150_firm_split.inputs' (content hash)")
    if bad:
        return {}, [], bad
    out = {}
    res_full, ok_full = A.resolution(X["t"], W["rr_grid"])
    res_rows = [{"section": "resolution", "span": "full", "span_first": days[0], "span_last": days[-1],
                 "sessions": len(days), "candidates": int(len(X["t"])), "every_r_resolves": bool(ok_full),
                 "decides": True, **res_full}]
    for span, (lo, hi) in M.SPANS.items():
        sd = WF.span_days(days, lo, hi)
        ts = WF.cell(W, STOP, sd)["trades"]
        fs = WF.cell(Wn, STOP, sd)["trades"]
        if ts is None or fs is None:
            return {}, [], [f"{span}: no mark the span's cutoff admits"]
        fa = ha.align_opposite(ts, fs)
        e_by, lb_by = B.check_bounds(ts, sd, B.rrs(ts))
        out[span] = span_inputs(I, ts, fa, sd, e_by, lb_by)
        res, ok = A.resolution(ts, W["rr_grid"])
        res_rows.append({"section": "resolution", "span": span, "span_first": sd[0], "span_last": sd[-1],
                         "sessions": len(sd), "candidates": int(len(ts)), "every_r_resolves": bool(ok),
                         "decides": False, **res})
        print(f"  span {span}: {len(sd)} sessions, {len(ts)} candidates, opposite aligned", flush=True)
    del W, Wn
    return out, res_rows, []


# ------------------------------------------------------------------------------------------------ the runs


def _paths_task(task: tuple) -> list[dict]:
    """`rc150_firm_split._paths_task`'s record (unhedged), plus each firm's trades a session and payouts."""
    import warnings

    warnings.filterwarnings("ignore")
    cell, shift, blocks, setups, items, margin, horizon = task
    specs = [hh.PathSpec(seed=int(s), blocks=blocks, horizon_days=int(horizon)) for _, s in items]
    jps = hh.run_joint(specs, setups[0], n_firms=len(setups), mode=hh.UNHEDGED, doubled=True, firm_setups=setups)
    out = []
    for (i, s), jp in zip(items, jps):
        r = hh.path_record(jp, margin=margin)
        r.update({"cell": cell, "shift": shift, "path": int(i), "seed": int(s)})
        hold = [lp.household for lp in jp.paths if lp.household]
        if hold:
            r["household_closed_on"] = int(max(int(h["closed_on"]) for h in hold))
        tps = []
        for lp in jp.paths:
            x = np.asarray(lp.path.trades_by_day, float)
            tps.append(float(x[1:].mean()) if len(x) > 1 else float("nan"))
        r["firm_trades_per_session"] = tps
        r["firm_payouts"] = [len(hh._pay_days(lp.path)) for lp in jp.paths]
        out.append(r)
    return out


def run_paths(X: dict, cell: str, seats: tuple[int, ...], blocks: list, shift: str, n_paths: int,
              workers: int) -> list[dict]:
    from propedge.campaign.lockstep import path_seeds

    import rc_screen as S

    setups = F.firm_setups(X, "camp", seats)
    seeds = list(enumerate(path_seeds(int(S.SEED), int(n_paths))))
    tasks = [(cell, shift, blocks, setups, seeds[j:j + F.CHUNK_PATHS], X["margin"], X["horizon"])
             for j in range(0, len(seeds), F.CHUNK_PATHS)]
    recs = [r for chunk in F._pool(tasks, _paths_task, workers, f"{cell} {shift}") for r in chunk]
    return sorted(recs, key=lambda r: r["path"])


def readings(recs: list[dict], X: dict) -> dict[str, Any]:
    """`rc150_firm_split.readings_of` (pooled; the household rule's share) and each firm's trades a session and
    payouts a month."""
    out = F.readings_of(recs, X)
    n_firms = len(recs[0]["firm_payouts"]) if recs else 0
    days = int(recs[0]["days"]) if recs else 0
    months = (days - 1) / float(MONTH) if days > 1 else float("nan")
    for f in range(n_firms):
        nm = FIRM_NAMES[f]
        out[f"trades_taken_per_session_{nm}"] = float(np.mean([r["firm_trades_per_session"][f] for r in recs]))
        out[f"payouts_per_month_mean_{nm}"] = (float(np.mean([r["firm_payouts"][f] for r in recs]) / months)
                                               if months > 0 else float("nan"))
    return out


def run_cell(X: dict, name: str, seats: tuple[int, ...], shift: str, n_paths: int, workers: int, *,
             twin: bool = False) -> dict[str, Any]:
    blocks = F.arm_blocks(X, "point", twin=True) if twin else F.arm_blocks(X, shift)
    return readings(run_paths(X, name, seats, blocks, "point" if twin else shift, n_paths, workers), X)


# ------------------------------------------------------------------------------------------------ the identities


def runner_identity(X: dict, n: int, workers: int, *, bounds: tuple[dict, dict] | None = None,
                    label: str = "p16_single") -> list[str]:
    """(c) / (e): 5+0 through the joint engine (this script's path task) against P-16's single-firm engine call
    (`rc_screen.Runner`, with `bounds` on a span) for the first `n` paths, both shifts, on PATH_COLS; and its growth and
    required bankroll at `n`."""
    import rc_screen as S
    import zero_edge_decomposition as zd

    R = S.Runner(X["I"], workers)
    df = R.run(label, X["t"], X["days"], int(n), bounds=bounds)
    ref = pd.DataFrame(R.sink)
    seats = dict(M.CELLS)[M.REFERENCE]
    mine, problems = [], []
    for shift in M.SHIFTS:
        recs = run_paths(X, M.REFERENCE, seats, F.arm_blocks(X, shift), shift, n, workers)
        mine += [{"run": "joint", "shift": shift, "enforcement_p": 0.0, "path": r["path"], **r["firm0"]} for r in recs]
        g = readings(recs, X)
        row = df[(df["shift"] == shift) & np.isclose(df["enforcement_p"].astype(float), 0.0)].iloc[0]
        for mine_col, theirs in (("growth_on_required", "pf_growth_on_base_p50"), ("required_p90", "pf_required_p90")):
            a, b = float(g[mine_col]), float(row[theirs])
            if not (abs(a - b) <= TOL or (np.isnan(a) and np.isnan(b))):
                problems.append(f"{label} {shift} {mine_col}: joint {a!r} against the single-firm call's {b!r}")
    problems += zd.path_problems(mine, ref, [("joint", s, label, s) for s in M.SHIFTS], int(n))
    return problems


def routing_identity(span: str, rows: dict[str, dict], rd: Path) -> list[str]:
    """(f) on a span: 5+0 at 500 paths against `rc150_routing.csv`'s G3 row for R0 on that span."""
    from propedge.reporting.results import read_result

    ref = read_result(Path(rd) / ROUTING_FILE)
    r = ref[(ref["section"].astype(str) == "g3") & (ref["rule"].astype(str) == ROUTING_REF)
            & (ref["span"].astype(str) == span)]
    if len(r) != 1:
        return [f"{ROUTING_FILE} holds {len(r)} G3 {ROUTING_REF} rows on {span}, not one"]
    r = r.iloc[0]
    out = []
    for what, mine, theirs in (("growth at the bound", rows["lower_bound"]["growth_on_required"],
                                r["growth_on_required"]),
                               ("growth at the point", rows["point"]["growth_on_required"],
                                r["growth_on_required_point"]),
                               ("required bankroll", rows["lower_bound"]["required_p90"], r["required_p90"])):
        if not abs(float(mine) - float(theirs)) <= TOL:
            out.append(f"5+0 on {span}, {what}: {float(mine)!r} against {ROUTING_FILE}'s {float(theirs)!r}")
    return out


def caps_problems() -> list[str]:
    from propedge.contract.lucid import lucid_terms

    t = lucid_terms()
    got = {"max_funded": int(t.max_funded), "eval_count_limit": int(t.eval_count_limit),
           "max_total_accounts": int(t.max_total_accounts)}
    out = [] if got == M.LUCID_CAPS else [f"Lucid's caps read {got}, not D-575's {M.LUCID_CAPS}"]
    try:
        M.check_caps(M.CELLS, got)
    except ValueError as exc:
        out.append(str(exc))
    return out


# ------------------------------------------------------------------------------------------------ the study


def _flat(d: dict) -> dict:
    return {k: v for k, v in d.items() if not isinstance(v, (list, dict))}


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import subprocess

    import customer_slices as cs

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="every identity, cell and span at --paths; nothing written")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--paths", type=int, default=None, help="test seam (with --check): paths a run")
    ap.add_argument("--starts", type=int, default=None, help="test seam (with --check): replay starts a cell")
    ap.add_argument("--only", default=None, help="test seam (with --check): a comma-separated subset of cells")
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--resume-dir", default=None)
    a = ap.parse_args(argv)
    if not a.check and (a.paths is not None or a.starts is not None or a.only is not None):
        print(f"REFUSED ({DECISION}): a reading runs every cell at {M.N_PATHS} paths and every start; use --check.")
        return 2
    if not a.check and int(a.workers) != 1:
        print(f"REFUSED ({DECISION}): the reading runs with workers 1 (D-593).")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    n_paths = M.N_PATHS if a.paths is None else int(a.paths)
    id_paths = IDENTITY_PATHS if not a.check else min(IDENTITY_PATHS, n_paths)
    cells = [c for c in M.CELLS if a.only is None or c[0] in a.only.split(",")]
    if a.only is not None and M.REFERENCE not in [c for c, _ in cells]:
        cells.insert(0, (M.REFERENCE, dict(M.CELLS)[M.REFERENCE]))      # the reference always runs
    t_all = time.time()

    # ---- (a) the declaration and Lucid's caps
    decl = M.declaration()
    bad = M.declaration_problems(decl) + caps_problems()
    if bad:
        print(f"REFUSED ({DECISION}): the build is not D-593's declaration -- " + "; ".join(bad[:8]))
        return 3
    print(f"the declaration HOLDS: {DECISION}'s row (sha256 {decl['sha256'][:16]}); Lucid's caps "
          f"{M.LUCID_CAPS} (at most {M.lucid_seat_limit()} Lucid seats)", flush=True)
    idents = [{"section": "declaration", "holds": True,
               "check": f"DECISIONS.md's {DECISION} row (sha256 {decl['sha256']}) and every phrase this build's "
                        f"constants rest on; Lucid's household caps {M.LUCID_CAPS} as lucid_terms reads them, every "
                        "cell inside them"}]

    # ---- (b) P-16's cell, (c) the joint engine's 5+0 = P-16's call
    print("P-16's cell, the opposite side, the blocks and the engine's arguments (rc150_firm_split.inputs, Lucid)...",
          flush=True)
    X = F.inputs(F.LUCID)
    print(f"identity HOLDS: the cell = P-16's rc_s150_all ({len(X['t'])} candidates); the opposite side aligned "
          f"({len(X['fa'])} rows)", flush=True)
    bad = runner_identity(X, id_paths, a.workers)
    if bad:
        print(f"REFUSED ({DECISION}): the joint engine's 5+0 is not P-16's single-firm call -- " + "; ".join(bad[:8]))
        return 3
    print(f"identity HOLDS: 5+0 through the joint engine = P-16's single-firm call, the first {id_paths} paths at both "
          "shifts (PATH_COLS), growth and required bankroll", flush=True)
    idents += [{"section": "identity", "holds": True,
                "check": "the cell's content hash is P-16's (rc150_dev_test.TRADES_SHA256); the opposite side aligned "
                         "one for one on the other side (rc150_firm_split.inputs)"},
               {"section": "identity", "holds": True,
                "check": f"5+0 through the joint engine reproduces P-16's single-firm engine call (rc_screen.Runner) "
                         f"path for path on PATH_COLS for the first {id_paths} paths at both shifts, and its growth "
                         "and required bankroll there"}]

    # ---- (d) the spans' construction, (e) the joint engine's 5+0 on each span = rc_screen.Runner with its bounds
    print("the spans: rc_stop_walkforward's walk, each span's cell, opposite side and bounds...", flush=True)
    XS, res_rows, bad = build_spans(X["I"], X)
    if bad:
        print(f"REFUSED ({DECISION}): " + "; ".join(bad))
        return 3
    idents.append({"section": "identity", "holds": True,
                   "check": "the span construction's walk (rc_stop_walkforward.walk_stop / cell, rc150_routing's G3) "
                            "rebuilds P-16's cell on every development day (content hash) and, with every coin side "
                            "negated, rc150_firm_split.inputs' opposite side (content hash)"})
    for span, XSp in XS.items():
        bad = runner_identity(XSp, id_paths, a.workers, bounds=(XSp["e_by"], XSp["lb_by"]), label=f"p16_{span}")
        if bad:
            print(f"REFUSED ({DECISION}): on {span}, the joint engine's 5+0 is not rc_screen.Runner's -- "
                  + "; ".join(bad[:8]))
            return 3
        idents.append({"section": "identity", "holds": True,
                       "check": f"on {span} ({XSp['days'][0]} .. {XSp['days'][-1]}) 5+0 through the joint engine "
                                f"reproduces rc_screen.Runner with the span's check_bounds path for path on PATH_COLS "
                                f"for the first {id_paths} paths at both shifts, and its growth and required bankroll"})
    print(f"identity HOLDS: on each span 5+0 through the joint engine = rc_screen.Runner with the span's bounds "
          f"({id_paths} paths)", flush=True)

    resume = None
    if not a.check and not a.no_resume:
        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = F.Resume(folder, f"{commit}_{n_paths}_{a.starts or 'all'}", M.RESULT)

    rows: list[dict] = []
    journeys: list[dict] = []
    slice_rows: list[dict] = []
    span_rows: list[dict] = []
    growth: dict[str, float] = {}
    span_growth: dict[str, dict[str, float]] = {s: {} for s in M.SPANS}
    lucid_traded = False
    for name, seats in cells:
        t0 = time.time()
        lab = M.label_of(seats)
        head = {"cell": name, "label": lab, "mode": hh.UNHEDGED, "firms": len(seats), "seats": M.seats_text(seats),
                "seats_total": int(sum(seats)), "budgets": "+".join(str(M.budget_for(s)[0]) for s in seats)}
        per = {}
        for shift in M.SHIFTS:
            per[shift] = F._cached(resume, f"{name}|{shift}", lambda name=name, seats=seats, shift=shift:
                                   run_cell(X, name, seats, shift, n_paths, a.workers))
        tw = F._cached(resume, f"{name}|twin", lambda name=name, seats=seats:
                       run_cell(X, name, seats, "point", n_paths, a.workers, twin=True))
        if name == M.REFERENCE and not a.check:
            badc = F.screen_identity(per, rd)
            if badc:
                print(f"REFUSED ({DECISION}): " + "; ".join(badc))
                return 3
            idents.append({"section": "identity", "holds": True,
                           "check": f"5+0 at {M.N_PATHS} paths reproduces results/rc_width_screen.csv's rc_s150_all "
                                    "(growth at the bound and the point, required bankroll)"})
            print(f"identity HOLDS: 5+0 at {M.N_PATHS} paths = rc_width_screen.csv's rc_s150_all", flush=True)
        jv = F._cached(resume, f"{name}|journey", lambda name=name, seats=seats:
                       dict(zip(("rows", "slices", "bad"), F.run_journey(X, name, seats, hh.UNHEDGED, a.starts,
                                                                         a.workers))))
        if int(jv["bad"]):
            print(f"REFUSED ({DECISION}): {name}: {jv['bad']} exact replays whose event days differ from the long run's")
            return 3
        u = pd.DataFrame(jv["rows"])
        cell_sub = max(float(s.path["subscription"]) for s in F.firm_setups(X, "rep", seats))
        for m in cj.metrics(u, cell_sub):
            journeys.append({"section": "journey", "cell": name, "label": lab, "arm": "verdict",
                             "key": cj.metric_key(m["milestone"], m["measure"], m["at_days"]), **m})
        sl = pd.DataFrame(jv["slices"])
        if len(sl):
            for r in cs.summarise(sl.assign(config=name, arm="verdict")).to_dict("records"):
                slice_rows.append({**r, "section": "slices", "cell": name, "label": lab})
        for shift in M.SHIFTS:
            rows.append({"section": "cell", **head, "shift": shift, **_flat(per[shift])})
        rows.append({"section": "twin", **head, "shift": "point", **_flat(tw)})
        growth[name] = float(per["lower_bound"]["growth_on_required"])
        if len(seats) > 1 and float(per["point"].get(f"trades_taken_per_session_{F.LUCID}", 0.0) or 0.0) > 0:
            lucid_traded = True
        # ---- the spans
        for span, XSp in XS.items():
            sp = {}
            for shift in M.SHIFTS:
                sp[shift] = F._cached(resume, f"{span}|{name}|{shift}", lambda XSp=XSp, name=name, seats=seats,
                                      shift=shift: run_cell(XSp, name, seats, shift, n_paths, a.workers))
            if name == M.REFERENCE and not a.check:
                badr = routing_identity(span, sp, rd)
                if badr:
                    print(f"REFUSED ({DECISION}): " + "; ".join(badr))
                    return 3
                idents.append({"section": "identity", "holds": True,
                               "check": f"5+0 on {span} at {M.N_PATHS} paths reproduces results/{ROUTING_FILE}'s G3 "
                                        f"{ROUTING_REF} row (growth at the bound and the point, required bankroll)"})
                print(f"identity HOLDS: 5+0 on {span} = {ROUTING_FILE}'s G3 {ROUTING_REF}", flush=True)
            for shift in M.SHIFTS:
                span_rows.append({"section": "span", **head, "span": span, "span_first": XSp["days"][0],
                                  "span_last": XSp["days"][-1], "sessions": len(XSp["days"]), "shift": shift,
                                  **_flat(sp[shift])})
            span_growth[span][name] = float(sp["lower_bound"]["growth_on_required"])
        print(f"  {name}: done ({time.time() - t0:.0f} s)", flush=True)
    secs = time.time() - t_all
    if a.check:
        if any(len(s) > 1 for _, s in cells) and not lucid_traded:
            print(f"REFUSED ({DECISION}): no Lucid trade was taken in the check.")
            return 3
        print(f"every identity holds; cells {[c for c, _ in cells]} ran at {n_paths} paths (full history and both "
              f"spans) and {'every' if a.starts is None else a.starts} start(s); nothing written, no reading printed "
              f"(--check). {secs:.0f} s")
        return 0
    resolves = bool(res_rows[0]["every_r_resolves"])
    verd = M.verdict(growth, span_growth, resolves)
    res = pd.DataFrame(idents + rows + journeys + slice_rows + span_rows + res_rows + verd)
    res.insert(1, "reading", M.READING)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for name, seats in M.CELLS:
        if name == M.REFERENCE:
            continue
        counter.record(prereg_id=M.FAMILY_ID, seed=M.CAMPAIGN_SEED, exploratory=True,
                       params={"study": f"{DECISION}'s added Lucid seats on P-16's cell", "cell": name,
                               "seats": list(seats), "mode": hh.UNHEDGED,
                               "budgets": [M.budget_for(s)[0] for s in seats], "paths": n_paths,
                               "second_firm": F.LUCID, "spans": {k: list(v) for k, v in M.SPANS.items()}},
                       label=f"{DECISION}'s added Lucid seats: {name} ({M.LUCID_LABEL})")
    from propedge.contract.lucid import STANDARD_40, lucid_provenance

    params = {"decision": DECISION, "declaration_sha256": decl["sha256"],
              "cells": [{"cell": c, "seats": list(s), "label": M.label_of(s), "budgets": [M.budget_for(x)[0] for x in s]}
                        for c, s in M.CELLS],
              "reference": M.REFERENCE, "campaign_seed": M.CAMPAIGN_SEED, "coin_seed": M.COIN_SEED,
              "n_paths": n_paths, "identity_paths": id_paths, "margin": M.MARGIN,
              "spans": {k: list(v) for k, v in M.SPANS.items()},
              "span_construction": "rc_stop_walkforward.cell on the span's days (its own cutoff), the opposite side "
                                   "with every coin side negated, a3_brk30.check_bounds, the span's own capacity "
                                   "(rc150_routing's G3)",
              "budget_rule": "floor(20 x seats / 5) purchases and resets in 21 trading days, per firm",
              "lucid_caps": M.LUCID_CAPS, "second_firm": F.SECOND_FIRM_NOTE[F.LUCID], "lucid": lucid_provenance(STANDARD_40),
              "deal": "unhedged (hypo_hedge.run_joint): each signal to one account at one firm",
              "bound": "the cell at its 0.05 bound, the opposite side mirrored (hypo_hedge.mirror_shift)",
              "journey": "customer_journey's units and metrics on the bound arm's replay, every start (full history)",
              "journey_margin": "one evaluation of the dearest firm in the cell",
              "every_r_resolves": resolves, "seconds": round(secs, 1), "workers": int(a.workers)}
    write_result(res, M.RESULT, script=SCRIPT, seed=M.CAMPAIGN_SEED, exploratory=True, results_dir=results_dir,
                 variant_count=M.N_VARIANTS, parameters=params,
                 notes={"status": M.READING, "labels": F.LABEL_NOTE[F.LUCID],
                        "selection": "D-593 (4): a candidate would get its own registered development test (N counting "
                                     "this grid, D-567's, D-575's and the RC pool) and the confirmation on unread data"},
                 description="EXPLORATORY (D-593): P-16's five Topstep seats with Lucid seats added (5+1, 5+2, 5+3, "
                             "5+5) against P-16's own call (5+0), unhedged; growth on the required bankroll, trades a "
                             "session and payouts a month per firm, the household rule's closures, D-518's journey; "
                             "the same cells on 2020-2023 and 2024-2026-07-16 alone; the verdict per D-593 (4); an "
                             "upper bound on Lucid's two unpriced fees.")
    print(pd.DataFrame(verd)[["cell", "growth_minus_reference", "early_growth_minus_reference",
                              "late_growth_minus_reference", "candidate"]].to_string(index=False))
    print(f"written: {M.RESULT}.csv ({secs:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
