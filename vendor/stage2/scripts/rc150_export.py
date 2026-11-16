"""EXPLORATORY: P-16's gate campaign -- RC150's registered development test (D-544, D-546, D-547) -- as Campaign Studio
trade logs, so the operator can replay it and look (the operator, 2026-11-14: "Please have the campaign terminal import
the new P-16 data for me to visualise ... I want to make sure there are no errors"; the Studio is an inspection view,
never a verdict -- D-155's step 7; P-16's verdict is D-547's). Read-only on results: it rebuilds what
`scripts/rc150_dev_test.py` built and writes nothing into `results/`.

    python scripts/rc150_export.py --out <folder outside results/>

`scripts/a3_brk30_export.py`'s form (P-13's export, D-507), with P-16's own inputs:

* **the trades**: the `rc_s150_all` cell (`rc150_dev_test.build_cells`: the walk at every five-minute mark from 17:00 CT
  at a 150-tick stop, the cutoff, the seeded coin, D-533's news-safe cut), checked to be the registered cell
  (`rc_dev_test.trade_problems`: `results/rc_width_screen.csv` at its pinned sha256 and the pinned content hash);
* **the bounds** the gate read (`a3_brk30.bounds_at_n` at the ledger's N, which must be the registered manifest's
  `ledger_n`): each R's e, its 0.05 bound and its bound at 0.05/N, checked equal to `results/rc_s150_all_gate.csv`'s
  `edge` rows (`e`, `lb_gate`, `lb_gate_at_ledger_n`, `n`);
* **the blocks** (`score_fv3_grid.gate_blocks`, as the run built them) and the verdict arm's (`gate.shifted_blocks` at
  the funded R's gap to its bound at 0.05/N and each R's own), checked against the gate rows' `mean_r_used`;
* **the day set**: every walked day, days without a trade included.

Two logs, in Stage 2's canonical schema, each with the day set and a `mirror` block in its manifest:

* `<prefix>_point` -- the outcomes as traded: section `gate`, shift `point`;
* `<prefix>_verdict` -- every R's outcomes shifted down to its bound at 0.05/N (N = 414): section `gate_at_ledger_n`,
  the row P-16's PASS was read on (D-189, D-419), 0 % denial, the placement off (D-234, D-289).

The mirror is P-13's (`a3_brk30_export.mirror_base`: FV3-C's protocol switches, the strict one-at-a-time rule at five
minutes, the day capacity at the cell's busiest day, 500 paths over 504 sessions) with P-16's differences: the
no-closure table (`state_dp_e-0.050_lamstar_noclose`, D-502), the purchase budget (20 Combine purchases and resets in any
21 trading days, D-501/D-502) and the registered campaign seed (`rc150_dev_test.SEED`). A Studio run of each arm at its mirror should reproduce
that arm's gate row and its 500 paths (`results/rc_s150_all_gate_paths.csv`, runs `gate` and `gate_at_ledger_n`).

Each trade is one micro (MNQ), as P-13's export writes it (`a3_brk30_export.trade_log`). It reads no new data and
selects nothing -- no new variant.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

if __name__ == "__main__":
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/rc150_export.py"
DECISION = "D-547"                          # P-16's verdict and audit, read on the gate rows this export mirrors
PREFIX = "rc150_p16"
GATE = "rc_s150_all_gate.csv"
#: (arm, the gate's section, its shift): the verdict arm is the 0.05/N row, the one the PASS was read on
ARMS = (("point", "gate", "point"), ("verdict", "gate_at_ledger_n", "lower_bound"))


def gate_rows(rd: Path) -> dict[str, pd.Series]:
    """P-16's two rows at 0 % denial with the placement off, by arm."""
    import a3_brk30 as B

    g = B._exact(Path(rd) / GATE)
    out = {}
    for arm, section, shift in ARMS:
        s = g[(g["section"] == section) & (g["shift"] == shift) & np.isclose(g["enforcement_p"].astype(float), 0.0)
              & (g["placement"] == "off")]
        if len(s) != 1:
            raise SystemExit(f"REFUSED: {GATE} holds {len(s)} rows for section {section}, shift {shift}, 0 % denial, "
                             "placement off.")
        out[arm] = s.iloc[0]
    return out


def check_edges(rd: Path, keys, e_by: dict, lb_by: dict, lbn_by: dict, st: dict) -> None:
    """Each R's e, its 0.05 bound, its 0.05/N bound and its trade count equal the gate's `edge` rows."""
    import a3_brk30 as B

    g = B._exact(Path(rd) / GATE)
    er = g[g["section"] == "edge"].copy()
    er["rr"] = er["rr"].astype(float)
    er = er.set_index("rr")
    if set(er.index) != {float(k) for k in keys}:
        raise SystemExit(f"REFUSED: the gate's edge rows are at R {sorted(er.index)}, the trades' at {sorted(keys)}.")
    for R in keys:
        for mine, col in ((e_by[R], "e"), (lb_by[R], "lb_gate"), (lbn_by[R], "lb_gate_at_ledger_n"),
                          (st[R]["n"], "n")):
            if not B._same(mine, er.loc[float(R), col]):
                raise SystemExit(f"REFUSED: R {R:g} {col}: {mine!r} against the gate's {er.loc[float(R), col]!r}.")


def main(out: Path, prefix: str = PREFIX, results_dir: Path | None = None) -> int:
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import a3_brk30_export as X
    import rc150_dev_test as P16
    import rc_dev_test as D
    import score_fv3_grid as gf

    from propedge import RESULTS_DIR
    from propedge.campaign.gate import mean_r, shifted_blocks
    from propedge.reporting.results import write_result
    from propedge.research import ledger as lg

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    out = Path(out).resolve()
    if out == rd.resolve() or rd.resolve() in out.parents:
        raise SystemExit(f"REFUSED: {out} is inside {rd}; the export never writes into results/.")
    man = json.loads((rd / f"{GATE}.manifest.json").read_text(encoding="utf-8"))
    mp = man["parameters"]
    if man.get("prereg_id") != "P-16" or int(man["seed"]) != int(P16.SEED):
        raise SystemExit(f"REFUSED: {GATE} is not P-16's registered file at seed {P16.SEED}.")

    print("RC150's cell (the walk, the cutoff, the coin, the news-safe cut)...", flush=True)
    I, b = P16.build_cells()
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    bad = D.trade_problems(rd, b, fcfg, spec=P16.SPEC)
    if bad:
        raise SystemExit(f"REFUSED: the trades are not {P16.SCREEN_FILE}'s {P16.CELL} -- " + "; ".join(bad[:6]))
    t, days = b["cells"][P16.CELL]["trades"], b["days"]
    if D.trades_hash(t) != mp["trades_sha256"]:
        raise SystemExit("REFUSED: the trades' content hash is not the registered manifest's.")
    pol = I["plan"]
    keys = B.rrs(t)
    cap = B.capacity(t, fcfg)
    if B.busiest(t) != cap:
        raise SystemExit(f"REFUSED: the day capacity {cap} is not the busiest day {B.busiest(t)}; the Studio's protocol "
                         "takes the log's busiest day.")
    n_led = lg.count_n(lg.load_ledger(), model=P16.MODEL, k=D.K, markets=["NQ"], window=D.WINDOW)["N"]
    if int(n_led) != int(mp["ledger_n"]):
        raise SystemExit(f"REFUSED: the ledger's N is {n_led}, the registered run's {mp['ledger_n']}.")
    st, e_by, lb_by, lbn_by, _, flagged = B.bounds_at_n(t, days, cfg, n_led)
    check_edges(rd, keys, e_by, lb_by, lbn_by, st)
    crr, fr = B.fresh_rr(L)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    shifted = shifted_blocks(blocks, lbn_by[fr] - e_by[fr], {k: lbn_by[k] - e_by[k] for k in keys})
    rows = gate_rows(rd)
    for arm, blk in (("point", blocks), ("verdict", shifted)):
        r = rows[arm]
        if not B._same(mean_r(blk), r["mean_r_used"]):
            raise SystemExit(f"REFUSED: the {arm} blocks' mean R {mean_r(blk)!r} is not the gate row's {r['mean_r_used']!r}.")
        if str(r["risk_policy"]) != pol.id or not B._same(r["one_at_a_time"], C.STRICT_GAP) \
                or int(float(r["paths"])) != int(mp["n_paths"]) \
                or [int(float(r["budget_k"])), int(float(r["budget_window_days"]))] != list(C.BUDGET):
            raise SystemExit(f"REFUSED: the {arm} gate row's policy, strict rule, paths or budget are not P-16's.")

    pfile = rd / f"{C.NOCLOSE_TABLE}_policies.json"
    base = X.mirror_base(L, pol, cap, tv)
    base.update({"seed": int(P16.SEED), "resample_paths": int(mp["n_paths"]), "one_at_a_time": float(C.STRICT_GAP),
                 "policy_file": f"results/{pfile.name}", "policy_file_sha256": X.text_sha256(pfile),
                 # D-501/D-502: the campaign's own restraint, (K, window in trading days)
                 "purchase_budget": [int(C.BUDGET[0]), int(C.BUDGET[1])]})
    for k, col in (("settlement", "settlement"), ("routing", "routing"), ("seat_frees", "seat_frees"),
                   ("allocation", "mode"), ("accounts", "accounts"), ("max_concurrent_combines", "combines"),
                   ("resample_horizon_days", "horizon_days"), ("cross_account_rule", "cross_account_rule"),
                   ("hold_to_own_exit", "hold_to_own_exit")):
        if not B._same(base[k], rows["point"][col]):
            raise SystemExit(f"REFUSED: the mirror's {k} {base[k]!r} is not the gate row's {col} {rows['point'][col]!r}.")

    out.mkdir(parents=True, exist_ok=True)
    dayset = pd.DataFrame({"date": days, "entries": [len(x) for x in blocks]})
    days_name = f"{prefix}_days"
    for (arm, section, shift), blk in zip(ARMS, (blocks, shifted)):
        log = X.trade_log(t, days, blk, keys, crr)
        want = e_by if arm == "point" else lbn_by
        got = {k: float(np.nanmean(log[f"r_net_{X.rr_label(k)}"])) for k in keys}
        if not np.allclose([got[k] for k in keys], [want[k] for k in keys], rtol=0, atol=1e-12):
            raise SystemExit(f"REFUSED: the {arm} log's mean R by R is not the gate's "
                             + ("edges." if arm == "point" else "bounds at 0.05/N."))
        if arm == "point":
            pnl = np.concatenate([x.pnl for x in blk if len(x)])
            if not np.array_equal(log["pnl_net"].to_numpy(), pnl):
                raise SystemExit("REFUSED: the point log's P&L differs from the gate's blocks.")
        mirror = {"reproduces": f"results/{GATE}, section {section}, shift {shift}, enforcement_p 0, placement off"
                                + (" -- the verdict's row, the bound at 0.05/N" if arm == "verdict" else ""),
                  "gate_section": section, **base,
                  "logs": {"trades": f"{prefix}_{arm}_trades.csv", "days": f"{days_name}.csv"}}
        params_ = {"arm": arm, "section": section, "shift": shift, "ledger_n": int(n_led),
                   "e_by_rr": {k: e_by[k] for k in keys}, "lb_by_rr": {k: lb_by[k] for k in keys},
                   "lb_at_ledger_n_by_rr": {k: lbn_by[k] for k in keys},
                   "trades_by_rr": {k: int(st[k]["n"]) for k in keys}, "era_flagged": bool(flagged),
                   "prereg": "P-16", "verdict": f"results/{GATE}", "verdict_sha256": X.text_sha256(rd / GATE),
                   "screen": f"results/{P16.SCREEN_FILE}", "model": P16.MODEL, "cell": P16.CELL,
                   "trades_sha256": D.trades_hash(t), "trades": int(len(t)), "days": int(len(days)),
                   "busiest_day": int(B.busiest(t)), "mirror": mirror,
                   "decision": f"{DECISION} (P-16's verdict and audit); the export EXPLORATORY, no new variant"}
        write_result(log, f"{prefix}_{arm}_trades", script=SCRIPT, seed=int(P16.SEED), exploratory=True,
                     results_dir=out, parameters=params_,
                     notes={"status": "EXPLORATORY: P-16's gate blocks re-presented for the Campaign Studio; the verdict "
                                      "is D-547's"},
                     description=f"EXPLORATORY: RC150's gate campaign (P-16), the {section} {shift} arm, as a Campaign "
                                 "Studio trade log (the 37.5-point news-safe coin's offered candidates, every R's outcome "
                                 "as the table reads them, blank where an R is not offered).")
        blanks = {X.rr_label(k): int(log[f"r_net_{X.rr_label(k)}"].isna().sum()) for k in keys}
        print(f"{prefix}_{arm}: {len(log)} trades; mean 1R {float(log['r_net_1'].mean()):.6f}; "
              f"{log['exit_reason'].value_counts().to_dict()}; no trade at R: {blanks}", flush=True)
    write_result(dayset, days_name, script=SCRIPT, seed=None, require_seed=False, exploratory=True, results_dir=out,
                 parameters={"rule": "every walked day (the gate's day blocks)", "decision": DECISION,
                             "verdict": f"results/{GATE}"},
                 notes={"status": "EXPLORATORY: P-16's gate day set, days without a trade included"},
                 description="EXPLORATORY: RC150's gate day set -- one row per session the gate laid a block on.")
    print(f"day set: {len(days)} sessions, {int((dayset['entries'] == 0).sum())} without a trade; busiest day "
          f"{int(dayset['entries'].max())}; written to {out}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", required=True, help="the folder the logs and their manifests go to (never results/)")
    ap.add_argument("--prefix", default=PREFIX, help=f"the files' prefix ({PREFIX})")
    a = ap.parse_args()
    raise SystemExit(main(Path(a.out), prefix=a.prefix))
