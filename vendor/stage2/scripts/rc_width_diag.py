"""EXPLORATORY (D-542): the stop-width screen's funded-risk diagnostic -- `rc_s150_all` (the news-safe coin at 37.5
points, all-day) with the funded leg's realised risk held to the 25-point reference's, so the cost-share effect of the
wider stop and the funded-risk effect it brings with it (D-539 (2)) are read apart.

    python scripts/rc_width_diag.py --check --paths 4      # the cell and its hash, the sizing table, both runs at 4
                                                            # paths; nothing written, no growth printed
    python scripts/rc_width_diag.py --workers 2             # the reading (500 paths); writes the file

**The cap** (`resolved_coin.funded_cap_rule`): the gate's own `SizingRule` with the funded leg's micro cap scaled by
100 / 150 (floor) -- every sizing path of the engine reads the cap through `cap_micros`, so it holds wherever the
engine sizes; the Combine's sizing, the table, the allowance, the stand-aside, the room cap and the fees unchanged.
Section `funded_sizing` (`funded_cap_sizing`, sizing only): for every funded leaf and allowance tier, the realised
dollars at 25 points, at 37.5 as the engine sizes it, and at 37.5 under the cap -- the cap changes only the states whose
dollars rose at the wider stop (the funded cap binding at 25 points), and leaves no state above its 25-point dollars.

**The runs**, through `rc_screen.Runner` (P-14's engine call) at the screen's seeds (campaign 20261131, coin
20261102), 500 paths: the cell with the cap (`rc_s150_all_fcap`), its zero-edge twin under the same cap; the gate rows
(point, bound, 0 %) and the trades taken a session. Beside, never rerun: `results/rc_width_screen.csv`'s `rc_s150_all`
cell row and its 25-point reference row.

**Identities first, each refusing:** the cell's trades as `rc_width_screen.build` builds them, their content hash
pinned here and their count equal to the screen's `rc_s150_all` row; at 500 paths the cell WITHOUT the cap reproduces
the screen's `rc_s150_all` growth at the bound and point and its required bankroll.

Writes `results/rc_width_diag.csv` with its manifest (EXPLORATORY; variants under `D-538:rc_width_diag`).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import rc_screen as S  # noqa: E402
import rc_width_screen as W  # noqa: E402
from propedge.research import resolved_coin as rc  # noqa: E402

SCRIPT = "scripts/rc_width_diag.py"
DECISION = rc.DECISION_WIDTH_DIAG
RESULT = "rc_width_diag"
FAMILY_ID = f"{rc.DECISION_WIDTH}:rc_width_diag"
CELL = "rc_s150_all"
STOP = 150
LABEL = f"{CELL}_fcap"
N_PATHS = S.N_PATHS
SCREEN_FILE = "rc_width_screen.csv"
#: the cell's trades (D-538's build, D-533's cut) -- pinned from the build's check run, refusing any other
CELL_TRADES_SHA256 = "17bcc29bc0c61296c872eaf04c3d49942649dcddca782836916bebdf29c9635f"
READING = "EXPLORATORY (D-542): the 37.5-point coin's funded-risk diagnostic; beside D-538's screen, never a gate"
IDENT_COLS = (("growth_on_required", "lower_bound", "pf_growth_on_base_p50"),
              ("growth_on_required_point", "point", "pf_growth_on_base_p50"),
              ("required_p90", "lower_bound", "pf_required_p90"))


def screen_rows(rd: Path) -> tuple[pd.Series, pd.Series]:
    """The screen's `rc_s150_all` cell row and its reference row (manifest verified)."""
    from propedge.reporting.results import read_result

    d = read_result(Path(rd) / SCREEN_FILE)
    sec, cell = d["section"].astype(str), d["cell"].astype(str)
    c, r = d[(sec == "cell") & (cell == CELL)], d[sec == "reference"]
    if len(c) != 1 or len(r) != 1:
        raise SystemExit(f"REFUSED ({DECISION}): {SCREEN_FILE} holds {len(c)} {CELL} rows and {len(r)} reference rows.")
    return c.iloc[0], r.iloc[0]


def growth_problems(df: pd.DataFrame, row: pd.Series) -> list[str]:
    """The uncapped run's gate rows against the screen's `rc_s150_all` row."""
    out = []
    for col, shift, src in IDENT_COLS:
        g = df[(df["shift"] == shift) & np.isclose(df["enforcement_p"].astype(float), 0.0)]
        mine, want = float(g[src].iloc[0]), float(row[col])
        if not np.isclose(mine, want, rtol=0, atol=1e-9):
            out.append(f"{col}: {mine!r} against {SCREEN_FILE}'s {want!r}")
    return out


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import rc_dev_test as D
    import rc_reentry_screen as RS
    import score_fv3_grid as gf

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="the cell, its hash, the sizing and both runs; nothing written")
    ap.add_argument("--paths", type=int, default=N_PATHS)
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    if not a.check and int(a.paths) != N_PATHS:
        print(f"REFUSED ({DECISION}): the reading runs {N_PATHS} paths; a smaller run is --check (writes nothing).")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    srow, rrow = screen_rows(RESULTS_DIR)
    print("P-14's inputs, the no-closure plan and the 37.5-point walk...", flush=True)
    I = S.inputs()
    L = I["L"]
    fcfg, tv = L["fcfg"], float(L["tv"])
    b = W.build(I, (STOP,))
    c = b["cells"][CELL]
    t, days = c["trades"], b["days"]
    h = D.trades_hash(t)
    bad = []
    if int(len(t)) != int(srow["candidates"]):
        bad.append(f"{len(t)} candidates against the screen's {int(srow['candidates'])}")
    if CELL_TRADES_SHA256 is not None and h != CELL_TRADES_SHA256:
        bad.append(f"content hash {h[:16]} against the pinned {CELL_TRADES_SHA256[:16]}")
    if bad:
        print(f"REFUSED ({DECISION}): the cell is not the screen's {CELL} -- " + "; ".join(bad))
        return 3
    print(f"identity HOLDS: the cell = {SCREEN_FILE}'s {CELL} ({len(t)} candidates; content hash {h[:16]}"
          f"{'' if CELL_TRADES_SHA256 else ' -- not yet pinned'})", flush=True)
    base = gf.sizing_rule(fcfg, tv)                       # the gate's own (atlas_a3.gate_kwargs's)
    capped = rc.funded_cap_rule(base, rc.REFERENCE_STOP, STOP)
    sizing = rc.funded_cap_sizing(base, W.policy_leaves(I["plan"]), rc.REFERENCE_STOP, STOP, tv)
    if bool(sizing["capped_above_ref"].any()) or bool(sizing["cannot_size_capped"].any()):
        print(f"REFUSED ({DECISION}): under the cap a funded state still realises more than at 25 points, or cannot "
              "size -- the cap does not do what D-542 declared.")
        return 3
    print(f"  funded sizing: {len(sizing)} (leaf, tier) rows; {int(sizing['above_ref'].sum())} above their 25-point "
          f"dollars as the engine sizes 37.5 points, {int(sizing['cap_changes'].sum())} changed by the cap, none above "
          "under it", flush=True)
    R = S.Runner(I, a.workers)
    idents = [{"section": "identity", "cell": CELL, "holds": True,
               "check": f"the cell's trades as rc_width_screen.build builds them: {len(t)} candidates as the screen's "
                        f"{CELL} row; content hash {h}"}]
    df_off = R.run(f"{CELL} cap off", t, days, a.paths)
    if int(a.paths) == N_PATHS:
        bad = growth_problems(df_off, srow)
        if bad:
            print(f"REFUSED ({DECISION}): {CELL} without the cap is not the screen's -- " + "; ".join(bad))
            return 3
        print(f"identity HOLDS: {CELL} without the cap at {N_PATHS} paths = {SCREEN_FILE}'s growth and required "
              "bankroll", flush=True)
        idents.append({"section": "identity", "cell": CELL, "holds": True,
                       "check": f"{CELL} without the cap, seed {S.SEED}, {N_PATHS} paths, reproduces results/"
                                f"{SCREEN_FILE}'s growth at the bound and point and its required bankroll"})
    else:
        print(f"  the cap-off identity needs {N_PATHS} paths; not compared at {a.paths}", flush=True)
    df = R.run(LABEL, t, days, a.paths, sizing=capped)
    tw = R.run(f"{LABEL} twin", t, days, a.paths, twin=True, sizing=capped)
    if a.check:
        print(f"every identity run held; the capped cell and its twin ran at {a.paths} paths; trades taken a session "
              f"{RS.taken_per_session(R.sink, LABEL, 'lower_bound'):.2f} (bound) -- no growth printed; nothing written "
              f"(--check). {time.time() - t_all:.0f} s")
        return 0
    row = RS.cell_row(LABEL, c, df, tw, R.sink, days, b["rr_grid"], fcfg)
    row.update({"section": "cell", "cell": LABEL, "funded_cap": f"funded micro cap x {rc.REFERENCE_STOP}/{STOP} (floor)",
                "reading": READING})
    beside = [{"section": "beside", "cell": str(r["cell"]), "source": f"results/{SCREEN_FILE} (never rerun)",
               "growth_on_required": float(r["growth_on_required"]),
               "growth_on_required_point": float(r["growth_on_required_point"]),
               "required_p90": float(r["required_p90"]), "growth_zero_edge_twin": float(r["growth_zero_edge_twin"]),
               "trades_taken_per_session": float(r["trades_taken_per_session"])} for r in (srow, rrow)]
    seconds = time.time() - t_all
    res = pd.DataFrame(idents + [row] + beside + sizing.to_dict("records"))
    res["reading"] = res["reading"].fillna(READING) if "reading" in res else READING
    VariantCounter(path=rd / "variants.jsonl").record(
        prereg_id=FAMILY_ID, seed=S.SEED, exploratory=True,
        params={"study": "D-542's funded-risk diagnostic", "cell": CELL, "stop_ticks": STOP,
                "funded_scale": float(rc.REFERENCE_STOP) / STOP, "coin_seed": rc.COIN_SEED, "paths": N_PATHS},
        label=f"D-542's diagnostic: {CELL} with the funded risk held to the 25-point cell's")
    write_result(res, RESULT, script=SCRIPT, seed=S.SEED, exploratory=True, results_dir=results_dir, variant_count=1,
                 parameters={"decision": DECISION, "cell": CELL, "stop_ticks": STOP, "reference_stop": rc.REFERENCE_STOP,
                             "funded_scale": float(rc.REFERENCE_STOP) / STOP, "seed": S.SEED, "coin_seed": rc.COIN_SEED,
                             "paths": N_PATHS, "cell_trades_sha256": h, "workers": int(a.workers),
                             "seconds": round(seconds, 1)},
                 notes={"status": READING, "cap": "resolved_coin.funded_cap_rule: the funded leg's micro cap scaled "
                        "by the stop ratio (floor) through SizingRule.cap_micros; the Combine's sizing and the table "
                        "unchanged"},
                 description="EXPLORATORY (D-542): the 37.5-point news-safe coin (all-day) with the funded leg's "
                             "realised risk held to the 25-point cell's, beside D-538's uncapped cell and reference; "
                             "the funded sizing at both stops with and without the cap.")
    print(pd.DataFrame([row] + beside)[["cell", "growth_on_required", "growth_on_required_point", "required_p90",
                                        "growth_zero_edge_twin", "trades_taken_per_session"]].to_string(index=False))
    print(f"written: {RESULT}.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
