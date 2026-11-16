"""EXPLORATORY (D-583): a fill-slippage stress test of P-16 (`rc_s150_all_nr`), beside P-16's registered verdict; decides
nothing, selects nothing.

    python scripts/p16_slip_stress.py --check                # a smoke: ~30 walked sessions, every arm at 4 paths with
                                                             #   its twin; no reading printed; nothing written
    python scripts/p16_slip_stress.py --workers 1            # the stress test (a clean checkout, D-474); writes the file

**The declaration** is DECISIONS.md's D-583 row, read as text, its sha256 pinned (`p16_slip_stress.DECLARATION_SHA256`)
and every constant of `propedge.research.p16_slip_stress` checked against its words; a mismatch refuses.

**The cell** (P-16, D-544, D-547): `rc_s150_all` -- the 37.5-point (150-tick) news-safe coin, all-day window, offered
every five minutes and re-entering when flat, its own coin seed 20261102 -- built by `rc_stop_walkforward.walk_stop` /
`cell` on every development day, at FV3's base costs (D-95's ASSUMED: one tick on entry, one on a stop or breakeven
exit, none on a target, two on the flatten; checked against `fv3_rung_walk.EXIT_TICKS` and the config's slip).

**The arms** (`propedge.research.p16_slip_stress`, whose docstring states every reading): the base; (A) exits only,
stop slip 2 / 3 / 5 / 8 / 12 ticks, the flatten one more, entry 1; (B) entry too, entry = stop slip 2 / 3 / 5, the
flatten one more. Targets stay at zero slip. Each arm's trades are P-16's with every offered R's net outcome lowered by
the arm's extra ticks over the base, by the exit's kind, over the stop (`p16_slip_stress.stress`); nothing else changes.

**The engine call, unchanged** (P-14's, `rc_screen.Runner` through `rc150_routing.run_rule`, the zero-edge twin with
it): the no-closure table (`a3_brk30_cb20.noclose_plan`: a solved file pinned by sha256, loaded once and handed to every
arm -- the engine re-solves nothing from the trades it is given, so the table is the one solved at the base costs), 20
purchases and resets in 21 trading days, the strict one-at-a-time rule, five Topstep seats, the placement off, 0 %
denial; campaign seed 20261131, 500 paths. What the stress flows through: each R's e and 0.05 bound (`atlas_a3.bounds`,
on the net `r_R`; the era rule's flag is read from the GROSS `g_R`, which no arm changes, so every arm reads the same
era), the blocks' outcomes and MAE floor (`score_fv3_grid.gate_blocks`: `r_R`; MAE floored at `-r_R`), the lower-bound
shift (lb - e by R), the zero-edge twin (each arm's own e removed), the need-aware exits (`r_by_rr`) and D-324's fee
re-pricing (the fee moved from the log's micro-equivalent to the contracts held: slippage stays in `r_R`).

**Readings per arm** (section `arms`): the ticks, growth on the required bankroll at the bound and the point, the
required bankroll, the zero-edge twin, payouts per path (median, mean), the share of accounts ever paid, trades taken a
session, e and the bound at the fresh legs' R, D-212's resolution (kind columns: unchanged by cost; reported), D-509's
four slice lines against FV3-C (FV3-C's slices read from `customer_slices.csv`, pinned, never rerun; not in --check)
and the arm's trades content hash. **The reading** (section `reading`, `p16_slip_stress.reading`): per family the lowest
level with growth at the bound at or below zero and the highest level at which all four slice lines hold.

**Identities, each refusing:** (i) the base arm's trades = P-16's (count against `rc_width_screen.csv`, content hash
against `rc150_dev_test.TRADES_SHA256`; every day only); (ii) every arm's added cost per trade = the declared extra
ticks over the stop in R, by kind, at every R, every other column unchanged; (iii) at the declared counts the base arm's
run reproduces `rc_width_screen.csv`'s `rc_s150_all` row (growth at the bound and point, the required bankroll) and
`results/rc150_routing.csv`'s R0 G1 row (with the zero-edge twin) -- S2's identity (iv).

**Resume** (D-540, `rc_robust.Resume`): each finished arm kept outside the checkout, keyed by commit and paths; off in
--check and with --no-resume.

Writes `results/p16_slip_stress.csv` (EXPLORATORY; sections declaration, identity, arms, journey, slice_lines, reading)
with its manifest; variants under `D-583` (the eight arms beyond the base).
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

import rc_robust as RR  # noqa: E402
import rc_screen as S  # noqa: E402
from propedge.research import p16_slip_stress as ps16  # noqa: E402

SCRIPT = "scripts/p16_slip_stress.py"
DECISION = ps16.DECISION
RESULT = ps16.RESULT
FAMILY_ID = DECISION
CELL = "rc_s150_all"
STOP = ps16.STOP
N_PATHS = ps16.N_PATHS
SPANS = {"early": ("2020-01-01", "2023-12-31"), "late": ("2024-01-01", "2026-07-16")}
CHECK_DAYS = 30                            # --check: N/2 walked sessions of each span
ROUTING_FILE = "rc150_routing.csv"         # identity (iii): its R0 G1 row (D-576)
ROUTING_REF = "R0_longest_waiting"
IDENT_COLS = ("growth_on_required", "growth_on_required_point", "required_p90")
READING = ("EXPLORATORY (D-583): a fill-slippage stress test of P-16 -- its cell, table and engine call unchanged, each "
           "trade's net R recomputed at more slippage by exit kind; beside P-16's registered verdict, selects nothing")


class Resume(RR.Resume):
    """`rc_robust.Resume` (D-540) under this test's own file name."""

    def __init__(self, folder: Path | None, key: str):
        import json

        self.path = None if folder is None else Path(folder) / f"{RESULT}_{key}.jsonl"
        self.rows = {}
        if self.path is not None and self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    self.rows[r["_label"]] = r["row"]
            print(f"  resume: {len(self.rows)} finished run(s) read from {self.path}", flush=True)


_cached = RR._cached


# ------------------------------------------------------------------------------------------------ pure parts (tested)


def smoke_pick(walked: list[str], n: int) -> list[str]:
    """--check: the first n/2 walked sessions of each span."""
    half = max(int(n) // 2, 1)
    return [d for lo, hi in SPANS.values() for d in sorted(x for x in walked if lo <= x <= hi)[:half]]


def routing_problems(routing: pd.DataFrame, row: dict, cols=IDENT_COLS + ("growth_zero_edge_twin",)) -> list[str]:
    """Identity (iii): the base arm's row against `rc150_routing.csv`'s R0 G1 row (exact to 1e-9)."""
    r = routing[(routing["section"].astype(str) == "g1") & (routing["rule"].astype(str) == ROUTING_REF)]
    if len(r) != 1:
        return [f"{len(r)} {ROUTING_REF} g1 rows in {ROUTING_FILE}"]
    out = []
    for c in cols:
        mine, want = float(row[c]), float(r.iloc[0][c])
        if not np.isclose(mine, want, rtol=0, atol=1e-9):
            out.append(f"g1 {c}: {mine!r} against {want!r}")
    return out


def plan_problems(plan: Any, noclose_id: str) -> list[str]:
    """The sizing table every arm is handed: the no-closure table solved at the base costs (`noclose_plan` has checked
    its file's sha256); by id."""
    pid = getattr(plan, "id", None)
    return [] if pid == noclose_id else [f"the table is {pid!r}, not {noclose_id!r}"]


def edge_beside(t: pd.DataFrame, days: list[str], cfg: dict, fcfg: dict) -> dict[str, Any]:
    """Beside: e and the bound read (`atlas_a3.bounds`, the era rule -- the engine call's own) at the fresh Combine's
    and the fresh funded account's R, and whether the eras are flagged."""
    import a3_brk30 as B
    import atlas_a3 as A

    _, e_by, lb_by, _, flagged = A.bounds(t, days, B.rrs(t), cfg)
    fr = fcfg["state_policy"]["fresh"]
    out = {"eras_flagged": bool(flagged)}
    for leg in ("combine", "funded"):
        R = float(fr[f"{leg}_rr"])
        out[f"e_fresh_{leg}_r"] = float(e_by.get(R, np.nan))
        out[f"lb_fresh_{leg}_r"] = float(lb_by.get(R, np.nan))
    return out


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import rc150_dev_test as R150
    import rc150_payout_screen as PS
    import rc150_routing as RT
    import rc_dev_test as D
    import rc_stop_walkforward as WF

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import read_result, write_result
    from propedge.research import fv3_rung_walk as FW
    from propedge.research import resolved_coin as rc

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="a smoke: ~30 walked sessions, every arm at a few paths with "
                                                         "its twin; no reading printed; nothing written")
    ap.add_argument("--days", type=int, default=None, help=f"--check: walked sessions, half in each span ({CHECK_DAYS})")
    ap.add_argument("--paths", type=int, default=None, help="--check: paths (4)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true", help="D-540: neither keep nor read finished runs' rows")
    ap.add_argument("--resume-dir", default=None, help="D-540: where finished runs' rows are kept (outside the checkout)")
    a = ap.parse_args(argv)
    if not a.check and any(x is not None for x in (a.days, a.paths)):
        print(f"REFUSED ({DECISION}): the stress test runs every day at {N_PATHS} paths; a smaller run is --check "
              "(writes nothing).")
        return 2
    n_paths = (a.paths or 4) if a.check else N_PATHS
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    ARMS = ps16.arms()

    # ---- the declaration and the constants it fixes
    decl = ps16.declaration()
    bad = ps16.declaration_problems(decl)
    fixed = {"campaign seed": (S.SEED, ps16.CAMPAIGN_SEED), "paths": (S.N_PATHS, N_PATHS),
             "coin seed": (rc.COIN_SEED, ps16.COIN_SEED), "stop": (RT.STOP, STOP), "cell": (RT.CELL, CELL)}
    bad += [f"{k}: the engine's {v[0]!r} against D-583's {v[1]!r}" for k, v in fixed.items() if v[0] != v[1]]
    if bad:
        print(f"REFUSED ({DECISION}): the build is not D-583's declaration -- " + "; ".join(bad))
        return 2
    print(f"the declaration HOLDS: DECISIONS.md's {DECISION} row (sha256 {decl['sha256'][:16]}); "
          f"{len(ARMS)} arms", flush=True)
    idents = [{"section": "declaration", "holds": True,
               "check": f"DECISIONS.md's {DECISION} row sha256 {decl['sha256']}, read as text; arms "
                        f"{[x['arm'] for x in ARMS]}, {ps16.N_VARIANTS} beyond the base; every constant agrees"}]

    # ---- the cell, its base costs and identity (i)
    srow = PS.screen_row(RESULTS_DIR)
    print("P-14's inputs, the no-closure plan and the 37.5-point walk...", flush=True)
    I = S.inputs()
    L = I["L"]
    bad = plan_problems(I["plan"], C.NOCLOSE_ID)
    if bad:
        print(f"REFUSED ({DECISION}): " + "; ".join(bad))
        return 3
    plan_id = id(I["plan"])
    idents.append({"section": "identity", "holds": True,
                   "check": f"the sizing table: {C.NOCLOSE_TABLE} ({C.NOCLOSE_ID}; file sha256 {C.NOCLOSE_TABLE_SHA256}, "
                            f"policies sha256 {C.NOCLOSE_POLICIES_SHA256}), solved at the base costs, loaded once and "
                            "handed unchanged to every arm's engine call (the engine re-solves nothing from trades)"})
    if a.check:
        dk = L["days"].copy()
        dk["date"] = dk["date"].astype(str)
        import a3_resolution_map as m0

        walked = sorted(dk.loc[dk["day_kind"].astype(str).isin(m0.WALK_DAY_KINDS), "date"])
        pick = set(smoke_pick(walked, a.days or CHECK_DAYS))
        I = {**I, "L": {**L, "days": dk[dk["date"].isin(pick)].reset_index(drop=True)}}
        L = I["L"]
    W = WF.walk_stop(I, STOP)
    bad = ps16.base_problems(FW.EXIT_TICKS, rc.KIND_CODE, W["slip"])
    if bad:
        print(f"REFUSED ({DECISION}): P-16's costs are not D-95's base -- " + "; ".join(bad))
        return 3
    idents.append({"section": "identity", "holds": True,
                   "check": "the base costs: fv3_rung_walk.EXIT_TICKS by resolved_coin.KIND_CODE "
                            f"{ps16.base_exit_ticks()} and the walk's entry slip {W['slip']:g} are D-95's ASSUMED"})
    days = list(W["days"])
    t = WF.cell(W, STOP, days)["trades"]
    if t is None or not len(t):
        print(f"REFUSED ({DECISION}): the cell has no trades on these days.")
        return 3
    h = D.trades_hash(t)
    if a.check:
        print(f"identity (i): the pinned count and content hash are not comparable on a --check subset ({len(days)} "
              f"days, {len(t)} candidates); identity (ii) runs on it", flush=True)
    else:
        bad = []
        if int(len(t)) != int(srow["candidates"]):
            bad.append(f"{len(t)} candidates against the screen's {int(srow['candidates'])}")
        if h != R150.TRADES_SHA256:
            bad.append(f"content hash {h[:16]} against the pinned {R150.TRADES_SHA256[:16]}")
        if bad:
            print(f"REFUSED ({DECISION}): the cell is not P-16's {CELL} -- " + "; ".join(bad))
            return 3

    # ---- the arms' trades and identity (ii); the base arm's hash is the cell's (identity (i) on every day)
    trades: dict[str, pd.DataFrame] = {}
    for x in ARMS:
        tx = ps16.stress(t, x)
        bad = ps16.cost_problems(t, tx, x)
        if bad:
            print(f"REFUSED ({DECISION}): identity (ii) -- " + "; ".join(bad))
            return 3
        trades[x["arm"]] = tx
    hb = D.trades_hash(trades["base"])
    if hb != h:
        print(f"REFUSED ({DECISION}): the base arm's trades hash {hb[:16]}, not the cell's {h[:16]}.")
        return 3
    if not a.check:
        idents.append({"section": "identity", "holds": True,
                       "check": f"(i) the base arm's trades (rc_stop_walkforward.cell on every development day, "
                                f"p16_slip_stress.stress at the base): {len(t)} candidates as {PS.SCREEN_FILE}'s {CELL}; "
                                f"content hash {hb} = rc150_dev_test.TRADES_SHA256 (P-16's)"})
        print(f"identity (i) HOLDS: the base arm = P-16's {CELL} ({len(t)} candidates; content hash {h[:16]})",
              flush=True)
    idents.append({"section": "identity", "holds": True,
                   "check": "(ii) every arm's added cost per trade equals its declared extra ticks over the base by exit "
                            f"kind over the stop ({STOP} ticks) in R, at every offered R (r - r' and c' - c within "
                            f"{ps16.COST_ATOL:g}); gross, MAE, exits, kinds and every other column unchanged"})
    print("identity (ii) HOLDS: every arm's added cost = its declared ticks / S by kind", flush=True)

    resume = None
    if not a.check and not a.no_resume:
        import subprocess

        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = Resume(folder, f"{commit}_{n_paths}")
    declared = not a.check
    routing = read_result(RESULTS_DIR / ROUTING_FILE) if declared else None
    fsl = PS.fv3c_slices(RESULTS_DIR) if declared else None

    # ---- the runs
    rows: dict[str, dict] = {}
    extra: list[dict] = []
    for x in ARMS:
        name = x["arm"]
        t0 = time.time()
        if id(I["plan"]) != plan_id:
            raise SystemExit(f"REFUSED ({DECISION}): arm {name} would not run on the base arm's table.")

        def make(name=name, x=x, tc=trades[name]):
            res_off, ok_off = A.resolution(tc, W["offered_rr"])
            _, ok_grid = A.resolution(tc, W["rr_grid"])
            add = ps16.added_ticks(x)
            head = {"section": "arms", "cell": CELL, **x, "candidates": int(len(tc)),
                    **{f"added_ticks_{k}": int(v) for k, v in add.items()},
                    **{f"added_r_{k}": float(v) / STOP for k, v in add.items()},
                    "arm_trades_sha256": D.trades_hash(tc), "table": C.NOCLOSE_ID, **res_off,
                    "every_offered_r_resolves": bool(ok_off), "every_grid_r_resolves": bool(ok_grid),
                    **edge_beside(tc, days, L["cfg"], L["fcfg"])}
            r = RT.run_rule(I, name, None, tc, days, n_paths, a.workers, twin=True)
            df = r.pop("df")
            if name == "base" and declared:
                prob = PS.growth_problems(df, srow)
                if prob:
                    raise SystemExit(f"REFUSED ({DECISION}): the base arm is not {PS.SCREEN_FILE}'s {CELL} -- "
                                     + "; ".join(prob))
            if declared:                           # beside; not in --check (a smoke has no 63- or 126-day horizon)
                jl = RT.journey_and_lines(I, tc, days, None, name, fsl, a.workers, None)
            else:
                jl = {"journey": [], "lines": [], "lines_hold": None}
            rn = lambda z: {**{("arm" if k == "rule" else k): v for k, v in z.items()}}   # noqa: E731
            return {"row": {**head, **r, "slice_lines_hold": jl["lines_hold"]},
                    "journey": [rn(z) for z in jl["journey"]], "lines": [rn(z) for z in jl["lines"]]}

        res = _cached(resume, f"arm {name}", make)
        rows[name] = res["row"]
        extra += res["journey"] + res["lines"]
        print(f"  arm {name}: done ({time.time() - t0:.0f} s)", flush=True)
        if name == "base" and declared:
            prob = routing_problems(routing, rows["base"])
            if prob:
                print(f"REFUSED ({DECISION}): the base arm's run is not {ROUTING_FILE}'s {ROUTING_REF} -- "
                      + "; ".join(prob))
                return 3
            idents.append({"section": "identity", "holds": True,
                           "check": f"(iii) the base arm at seed {S.SEED}, {N_PATHS} paths, reproduces results/"
                                    f"{PS.SCREEN_FILE}'s {CELL} growth at the bound and point and its required bankroll, "
                                    f"and results/{ROUTING_FILE}'s {ROUTING_REF} G1 row (with the zero-edge twin)"})
            print(f"identity (iii) HOLDS: the base arm at {N_PATHS} paths = {PS.SCREEN_FILE}'s {CELL} and "
                  f"{ROUTING_FILE}'s {ROUTING_REF}", flush=True)

    seconds = time.time() - t_all
    if a.check:
        hashes = len({r["arm_trades_sha256"] for r in rows.values()})
        print(f"--check done: the declaration, the base costs, identity (ii) on {len(days)} sessions ({len(t)} "
              f"candidates; {hashes} distinct arm hashes of {len(ARMS)}), every arm through run_rule with its twin at "
              f"{n_paths} paths; no reading printed; nothing written. {seconds:.0f} s")
        return 0
    arm_rows = [rows[x["arm"]] for x in ARMS]
    read = ps16.reading(arm_rows)
    out = pd.DataFrame(idents + arm_rows + extra + read)
    out.insert(1, "reading", READING)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for x in ARMS:
        if x["arm"] == "base":
            continue
        counter.record(prereg_id=FAMILY_ID, seed=S.SEED, exploratory=True,
                       params={"study": "D-583, a fill-slippage stress test of P-16", "reference": CELL,
                               "arm": x["arm"], "family": x["family"], "level": x["level"],
                               "entry_slip_ticks": x["entry_slip_ticks"], "stop_slip_ticks": x["stop_slip_ticks"],
                               "flatten_slip_ticks": x["flatten_slip_ticks"], "target_slip_ticks": 0,
                               "coin_seed": rc.COIN_SEED, "paths": N_PATHS, "table": C.NOCLOSE_ID},
                       label=f"D-583's slippage stress: {x['arm']}")
    write_result(out, RESULT, script=SCRIPT, seed=S.SEED, exploratory=True, results_dir=results_dir,
                 variant_count=ps16.N_VARIANTS,
                 parameters={"decision": DECISION, "declaration_sha256": decl["sha256"], "reference": f"P-16 ({CELL})",
                             "stop_ticks": STOP, "arms": ARMS, "base_ticks": dict(ps16.BASE),
                             "levels_a": list(ps16.LEVELS_A), "levels_b": list(ps16.LEVELS_B),
                             "campaign_seed": S.SEED, "coin_seed": rc.COIN_SEED, "paths": N_PATHS,
                             "bound": "0.05 by the era rule (atlas_a3.bounds)", "twin": True,
                             "table": {"id": C.NOCLOSE_ID, "file": C.NOCLOSE_TABLE, "sha256": C.NOCLOSE_TABLE_SHA256,
                                       "policies_sha256": C.NOCLOSE_POLICIES_SHA256,
                                       "frozen": "the table solved at the base costs, every arm"},
                             "cell_trades_sha256": h, "cost_atol": ps16.COST_ATOL,
                             "fv3c_slices": "results/customer_slices.csv (sha256 pinned), read, never rerun",
                             "workers": int(a.workers), "seconds": round(seconds, 1)},
                 notes={"status": READING, "selection": "none: beside P-16's registered verdict (D-583)",
                        "arm_readings": "propedge/research/p16_slip_stress.py's docstring"},
                 description="EXPLORATORY (D-583): P-16 (the 37.5-point news-safe coin) at more fill slippage -- exits "
                             "only (stop 2/3/5/8/12 ticks, the flatten one more) and entry too (entry = stop 2/3/5) -- "
                             "each trade's net R recomputed by exit kind, its table and engine call unchanged; 500 paths "
                             "with the zero-edge twin and D-509's slice lines; the lowest level at which growth at the "
                             "bound reaches zero and the highest at which the slice lines hold.")
    pd.set_option("display.width", 250)
    print(pd.DataFrame(read).to_string(index=False))
    print(f"written: {RESULT}.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
