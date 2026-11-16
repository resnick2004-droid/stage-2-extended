"""EXPLORATORY (D-533 (2)): `rc_s100_all_nr` -- P-15's coin (`rc_s100_all`) with no entry offered on a BLS report day
before 07:35 CT, the release bar closed -- read on development data beside P-15, before its confirmation is registered.

    python scripts/rc_nr_dev.py --check --paths 4 --starts 6    # identities and every arm at 4 paths; nothing written,
                                                                 #   no reading printed
    python scripts/rc_nr_dev.py --count                         # the candidates the change removes (no P&L); nothing
                                                                 #   written
    python scripts/rc_nr_dev.py --workers 4                     # the reading (500 paths, every start), from a clean
                                                                 #   checkout (D-474)

**Why** (D-533, P-15's audit finding 1): a report day's marks before the 07:30 CT cut are dropped, but the 07:30 mark is
offered and enters at the open of the release bar at most of the maximum size -- tier 1 (D-145; Topstep 10305426). D-533
(2): the confirmed candidate offers no report-day entry before 07:35 CT (`resolved_coin.drop_release_minute` at
`RELEASE_CLEAR_CT`). A post-gate change, so a variant counted in N (`D-533:rc_nr`), read here EXPLORATORY.

**The variant is P-15's cell minus those rows, nothing else:** the cell is built exactly as P-15 built it
(`rc_dev_test.build_cells`) and must first pass P-15's identity (b) -- the screen's row and the pinned content hash
(`rc_dev_test.trade_problems`) -- then `drop_release_minute` removes the report-day entries before 07:35 CT. Every other
choice is P-15's: P-14's engine call (`atlas_a3.gate_kwargs`: the no-closure table, 20 purchases in 21 trading days, the
strict rule at 5 minutes, the day capacity at the variant's busiest day, the placement off, 0 % denial), P-15's registered
campaign seed (`rc_dev_test.SEED`), 500 paths, each R's 0.05 bound by the era rule (`a3_brk30.bounds_at_n`) and at 0.05/N at P-15's N
(the ledger's count for model RC; a registration of the variant counts it on top).

**Arms read:** the gate (point and bound, 0 %), the bound at 0.05/N, the zero-edge twin; D-509's four slice lines at 63
trading days against FV3-C's development configuration, the variant's slices from D-518's journey replay
(`rc_dev_test.journey_and_slices`) and FV3-C's read from P-15's own slices file (`results/rc_s100_all_gate_slices.csv`,
its manifest verified -- never rerun). **Beside, never rerun:** P-15's gate rows, bound at 0.05/N, zero-edge twin and slice
lines, read from `results/rc_s100_all_gate.csv`.

Writes `results/rc_nr_dev.csv` with its manifest (EXPLORATORY; the variant recorded under `D-533:rc_nr`). Not a verdict:
the variant's registered reading is its confirmation's pre-registration.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

if __name__ == "__main__":                 # one BLAS thread (D-464 (5)), before numpy loads
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/rc_nr_dev.py"
DECISION = "D-533"
RESULT = "rc_nr_dev"
VARIANT = "rc_s100_all_nr"
FAMILY_ID = f"{DECISION}:rc_nr"
P15_RESULT = "rc_s100_all_gate.csv"
P15_SLICES = "rc_s100_all_gate_slices.csv"
READING = "EXPLORATORY (D-533 (2)): the conduct-fixed variant beside P-15, never a verdict"


def removed_rows(t: pd.DataFrame, clear: int) -> pd.DataFrame:
    """The rows `drop_release_minute` removes (report-day entries before `clear`)."""
    from propedge.research import resolved_coin as rc

    keep = rc.drop_release_minute(t, clear)
    return t.loc[~t.index.isin(t.index[:0])].iloc[0:0] if len(keep) == len(t) else \
        t[(t["day_kind"].astype(str) == rc.REPORT_DAY_KIND) & (t["decision_slot_minutes"].astype(int) < int(clear))]


def p15_beside(rd: Path) -> pd.DataFrame:
    """P-15's own rows, read (manifest verified), never rerun: its gate rows at 0 %, its bound at 0.05/N, its zero-edge
    twin and its slice lines."""
    from propedge.reporting.results import read_result

    d = read_result(Path(rd) / P15_RESULT)
    sec = d["section"].astype(str)
    zero = pd.to_numeric(d.get("enforcement_p"), errors="coerce").fillna(0.0) == 0.0
    keep = ((sec == "gate") & zero) | sec.isin(["gate_at_ledger_n", "zero_edge_twin", "slice_lines"])
    out = d[keep].copy()
    out.insert(0, "beside", "P-15 (read from results/rc_s100_all_gate.csv, never rerun)")
    out["section"] = "p15_" + out["section"].astype(str)
    return out


def fv3c_slices_from_p15(rd: Path) -> pd.DataFrame:
    """FV3-C's slices as P-15 recorded them (its slices file's `fv3c` rows; the manifest verified by `read_result`)."""
    import customer_slices as cs

    from propedge.reporting.results import read_result

    d = read_result(Path(rd) / P15_SLICES)
    d = d[d["config"].astype(str) == "fv3c"]
    if d.empty:
        raise SystemExit(f"REFUSED ({DECISION}): {P15_SLICES} holds no fv3c slices.")
    return d[list(cs.SLICE_COLS)].reset_index(drop=True)


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import customer_slices as cs
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc_dev_test as D
    import rc_screen as S
    import score_fv3_grid as gf

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.campaign import gate
    from propedge.outcomes.collect_core import c_slot
    from propedge.reporting.results import write_result
    from propedge.research import ledger as lg
    from propedge.research import resolved_coin as rc

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="identities and every arm; no reading, nothing written")
    ap.add_argument("--count", action="store_true", help="the candidates the change removes (no P&L); nothing written")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--paths", type=int, default=D.N_PATHS)
    ap.add_argument("--starts", type=int, default=None, help="test seam: the first replay starts only")
    a = ap.parse_args(argv)
    if not (a.check or a.count) and (a.paths != D.N_PATHS or a.starts is not None):
        print(f"REFUSED ({DECISION}): a reading needs {D.N_PATHS} paths and every start; use --check for a smoke.")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    print("P-15's cell (P-14's inputs, the walk, the cutoff)...", flush=True)
    I, b = D.build_cells()
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    t15 = b["cells"][D.CELL]["trades"]
    days = b["days"]
    bad = D.trade_problems(RESULTS_DIR, b, fcfg)
    if bad:
        print(f"REFUSED ({DECISION}): the cell is not P-15's {D.CELL} -- " + "; ".join(bad[:8]))
        return 3
    print(f"identity HOLDS: the cell = P-15's {D.CELL} ({len(t15)} candidates, content hash {D.trades_hash(t15)[:16]})",
          flush=True)
    cut = c_slot(*(int(x) for x in str(cfg["news"]["bls_cut_ct"]).split(":")))
    clear = c_slot(*rc.RELEASE_CLEAR_CT)
    if len(rc.drop_release_minute(t15, cut)) != len(t15):
        print(f"REFUSED ({DECISION}): P-15's cell holds report-day entries before its own cut.")
        return 3
    t = rc.drop_release_minute(t15, clear)
    gone = removed_rows(t15, clear)
    counts = {"candidates_p15": int(len(t15)), "candidates_variant": int(len(t)), "removed": int(len(gone)),
              "removed_report_days": int(gone["date"].nunique()) if len(gone) else 0,
              "report_days_in_cell": int(t15.loc[t15["day_kind"].astype(str) == rc.REPORT_DAY_KIND, "date"].nunique()),
              "removed_marks_ct": sorted({rc.ct(int(x)) for x in gone["decision_slot_minutes"]}) if len(gone) else [],
              "clear_ct": f"{rc.RELEASE_CLEAR_CT[0]:02d}:{rc.RELEASE_CLEAR_CT[1]:02d}", "cut_ct": cfg["news"]["bls_cut_ct"]}
    print(f"  the change: {counts['removed']} candidates removed on {counts['removed_report_days']} of "
          f"{counts['report_days_in_cell']} report days (marks {counts['removed_marks_ct']}); {len(t)} remain", flush=True)
    if a.count:
        print(f"nothing written (--count). {time.time() - t_all:.0f} s")
        return 0
    # (a) P-14's trades through this engine call (P-15's identity (a))
    R = S.Runner(I, a.workers)
    bad = S.identity_problems(R, a.paths)
    if bad:
        print(f"REFUSED ({DECISION}): P-14's trades are not {S.P14_PATHS} -- " + "; ".join(bad[:8]))
        return 3
    print(f"identity HOLDS: P-14's trades = the first {a.paths} paths of {S.P14_PATHS}", flush=True)
    horizon = int(fcfg["gate"]["campaign"]["horizon_days"])
    keys = B.rrs(t)
    cap = B.capacity(t, fcfg)
    n_led = lg.count_n(lg.load_ledger(), model=D.MODEL, k=D.K, markets=["NQ"], window=D.WINDOW)["N"]
    st, e_by, lb_by, lbn_by, era_rows, flagged = B.bounds_at_n(t, days, cfg, n_led)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    nc = I["plan"]
    pcfg = fcfg["portfolio"]
    paths_rows: list[dict] = []
    inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])}, sink=paths_rows)
    hook = lt.lever_hook(inner)

    def go(section: str, blk, eb, lbb) -> pd.DataFrame:
        ps._label(inner, section)
        kw = A.gate_kwargs(blk, fcfg, tv, nc, eb, lbb, hook, seed=int(D.SEED), n_paths=int(a.paths), horizon=horizon,
                           capacity=cap, levels=(0.0,), rtp=False, one_at_a_time=C.STRICT_GAP,
                           purchase_budget=C.BUDGET)
        df, _ = gate.run_gate(kw.pop("blocks"), workers=int(a.workers), **kw)
        df["placement"] = "off"
        df.insert(0, "section", section)
        return df

    gate_df = go("gate", blocks, e_by, lb_by)
    n_df = go("gate_at_ledger_n", blocks, e_by, lbn_by)
    n_df = n_df[n_df["shift"] == "lower_bound"]
    fr = B.fresh_rr(L)[1]
    zero = {k: 0.0 for k in e_by}
    z_df = go("zero_edge_twin", ps.zero_edge_blocks(blocks, e_by, fr), zero, zero)
    z_df = z_df[z_df["shift"] == "point"]
    rcamp = D.rc_campaign(I, t, days, e_by, lb_by, cap)
    units, rsl = D.journey_and_slices(rcamp, nc, C.BUDGET, a.workers, a.starts)
    rsl["config"] = VARIANT
    fsl = fv3c_slices_from_p15(rd)
    if a.starts is not None:
        fsl = fsl[fsl["start_day"].astype(int) < int(a.starts)]
    sl = pd.concat([rsl, fsl], ignore_index=True)
    summ = cs.summarise(sl)
    lines = C.slice_lines(summ, candidate=VARIANT, reference="fv3c")
    if a.check:
        print(f"every identity holds and every arm ran at {a.paths} paths; the slices on "
              f"{'every' if a.starts is None else a.starts} start(s); nothing written, no reading printed (--check). "
              f"{time.time() - t_all:.0f} s")
        return 0
    row = gate_df[(gate_df["shift"] == "lower_bound") & np.isclose(gate_df["enforcement_p"].astype(float), 0.0)].iloc[0]
    g = float(row["pf_growth_on_base_p50"])
    g_n = float(n_df.iloc[0]["pf_growth_on_base_p50"])
    res_rows = B.resolution_rows(t, keys)
    resolves = all(r["resolves"] for r in res_rows)
    realised = float(row.get("realised_to_intended_capped_risk", float("nan")))
    lines_hold = all(r["holds"] for r in lines)
    summary = pd.DataFrame([{"section": "reading", "variant": VARIANT, "growth_bound": g, "growth_bound_at_ledger_n": g_n,
                             "ledger_n": n_led, "resolves": resolves, "realised_to_intended_capped_risk": realised,
                             "slice_lines_hold": lines_hold, "era_flagged": flagged, **{k: v for k, v in counts.items()
                                                                                         if not isinstance(v, list)},
                             "removed_marks_ct": " ".join(counts["removed_marks_ct"]),
                             "trades_sha256_p15": D.trades_hash(t15), "trades_sha256_variant": D.trades_hash(t),
                             "reading": READING}])
    summ_out = summ.copy()
    summ_out["section"] = "slices"
    res = pd.concat([summary, gate_df, n_df, z_df, pd.DataFrame(res_rows), pd.DataFrame(lines).assign(section="slice_lines"),
                     summ_out, p15_beside(rd)], ignore_index=True)
    res["reading"] = res["reading"].fillna(READING) if "reading" in res else READING
    VariantCounter(path=rd / "variants.jsonl").record(
        prereg_id=FAMILY_ID, seed=int(D.SEED), exploratory=True,
        params={"study": "D-533 (2): the release bar closed", "variant": VARIANT, "base": D.CELL,
                "clear_ct": counts["clear_ct"], "paths": int(a.paths)},
        label=f"{DECISION}'s {VARIANT}: P-15's coin without report-day entries before {counts['clear_ct']} CT")
    params = {"decision": DECISION, "variant": VARIANT, "base_cell": D.CELL, "seed": int(D.SEED), "n_paths": int(a.paths),
              "horizon": horizon, "ledger_n": n_led, "ledger_n_note": "P-15's N (model RC); a registration of the "
              "variant counts it on top", "one_at_a_time": C.STRICT_GAP, "budget": list(C.BUDGET), "policy_id": nc.id,
              "capacity": cap, "change": counts, "fv3c_slices": f"results/{P15_SLICES} (P-15's, never rerun)",
              "beside": f"results/{P15_RESULT} (P-15's rows, never rerun)", "workers": int(a.workers),
              "seconds": round(time.time() - t_all, 1)}
    write_result(res, RESULT, script=SCRIPT, seed=int(D.SEED), exploratory=True, results_dir=results_dir,
                 variant_count=1, parameters=params, notes={"status": READING, "variant_label": FAMILY_ID},
                 description="EXPLORATORY (D-533 (2)): P-15's coin without report-day entries before 07:35 CT (the "
                             "release bar closed) -- the gate at 0.05 and 0.05/N, the zero-edge twin and D-509's slice "
                             "lines through P-15's engine call and seed, beside P-15's own rows; never a verdict.")
    print(f"written: {RESULT}.csv ({time.time() - t_all:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
