"""EXPLORATORY: P-13's gate campaign -- A3-BRK30's registered development test (D-494, D-500) -- as Campaign Studio
trade logs, so the operator can replay it and look (the operator, 2026-10-31: "Can you please import the P-13 results
into the campaign backtester?"; the Studio is an inspection view, never a verdict -- D-155's step 7; P-13's verdict is
D-500's). Read-only on results: it rebuilds what `scripts/a3_brk30.py` built and writes nothing into `results/`.

    python scripts/a3_brk30_export.py --out <folder outside results/>

It rebuilds the gate's blocks exactly as `scripts/a3_brk30.py` built them, from the same records:

* **the trades**: A3-BRK30's, from A1's events walked on FV3-C's rungs into A3's rung cache (`data/atlas/A3`, read
  only; `a3_brk30.cell_trades`, i.e. `atlas_a3.cell_trades` at the rung rule, padded to every R the policy asks for),
  checked to be the screen's cell (`a3_brk30.identity_with_screen`: `results/atlas_screen_a3.csv` at its registered
  sha256, the rung walk's inputs, the rung rule, the policy, the row's facts, the edge and era rows);
* **the bounds** the gate read (`atlas_a3.bounds`: each R's one-sided 95 % bound over 21-session blocks, the lower
  era's where the eras are flagged), checked equal to `results/a3_brk30_gate.csv`'s `edge` rows (`e`, `lb_gate`);
* **the blocks** (`score_fv3_grid.gate_blocks`, sides and per-R exits required, as P-13's run) and the lower-bound arm's
  (`gate.shifted_blocks` at the funded R's gap and each R's own), checked against the gate rows' `mean_r_used`;
* **the day set**: every day record of A1's walk, days without a trade included.

Two logs, in Stage 2's canonical schema, each with the day set and a `mirror` block in its manifest:

* `<prefix>_point` -- the outcomes as traded: the gate's point arm;
* `<prefix>_verdict` -- every R's outcomes shifted down to the bound the gate row read (the lower era's 0.05 bound):
  the arm P-13's verdict was read on (`is_gate_row`, 0 % denial, the placement off, D-234, D-289).

A Studio run of each at its `mirror` -- FV3-C's exported v12 policy at its own cell, FV3-C's protocol switches, the
day capacity at the cell's busiest day, the operator's strict one-at-a-time rule with five minutes (D-496), 500 paths
over 504 sessions at P-13's campaign seed -- should reproduce that arm's gate row at 0 % denial with the placement off.

Each trade is one micro (MNQ): `dollars_risked` its rung's stop per micro; `pnl_net` its 1R outcome times it (the
gate's block P&L on the point arm; on the verdict arm the 1R outcome at the 1R bound -- the gate's own block P&L there
carries the funded R's shift, a number the engine never reads under a policy that sets R); `pnl_gross` the same before
the 1R cost; `mae` the 1R excursion. `timestamp_out` and `exit_reason` are the fresh Combine R's (1.5R), the exit the
gate's flat routing reads; every R's own exit rides beside (`t_out_<R>`, `exit_kind_<R>`). Times are bar starts (the
kit's slot minus one), as `scripts/fv3_gate_export.py` writes them; the mirror's `router_clock_offset_min` 1 puts them
back on the engine's clock. Prices are constructed (risk and P&L exact). It reads no new data and selects nothing --
no new variant.
"""
from __future__ import annotations

import argparse
import hashlib
import math
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

SCRIPT = "scripts/a3_brk30_export.py"
DECISION = "D-500"                          # P-13's verdict, read on the gate rows this export mirrors
PREFIX = "a3_brk30_p13"
GATE = "a3_brk30_gate.csv"
TICK_POINTS = 0.25                          # MNQ's tick, in points
KIND_WORD = {"t": "target", "s": "stop", "b": "breakeven", "f": "flatten"}   # atlas_a3.KIND_CODE's codes
REASON = {"t": "target", "s": "stop", "b": "other", "f": "flatten"}          # the log's exit_reason (a breakeven: other)
TOL = 1e-12


def rr_label(x: float) -> str:
    """A per-R column's label: 1.0 -> '1', 2.5 -> '2.5'."""
    return f"{x:.6f}".rstrip("0").rstrip(".")


def text_sha256(path: Path) -> str:
    """A text file's sha256 with its line endings normalised (D-503: a Windows checkout's CRLF changes the bytes, not a
    value)."""
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def gate_rows(rd: Path) -> pd.DataFrame:
    """P-13's gate rows at 0 % denial with the placement off (the point arm and the bound arm the verdict read)."""
    import a3_brk30 as B

    g = B._exact(Path(rd) / GATE)
    s = g[(g["section"] == "gate") & np.isclose(g["enforcement_p"].astype(float), 0.0) & (g["placement"] == "off")]
    if sorted(s["shift"]) != ["lower_bound", "point"]:
        raise SystemExit(f"REFUSED: {GATE} holds no single point and bound row at 0 % denial, placement off.")
    return s.set_index("shift")


def check_edges(rd: Path, keys, e_by: dict, lb_by: dict, st: dict) -> None:
    """Each R's e, the bound the gate read and the trade count equal `results/a3_brk30_gate.csv`'s `edge` rows."""
    import a3_brk30 as B

    g = B._exact(Path(rd) / GATE)
    er = g[g["section"] == "edge"].copy()
    er["rr"] = er["rr"].astype(float)
    er = er.set_index("rr")
    if set(er.index) != {float(k) for k in keys}:
        raise SystemExit(f"REFUSED: the gate's edge rows are at R {sorted(er.index)}, the trades' at {sorted(keys)}.")
    for R in keys:
        for mine, col in ((e_by[R], "e"), (lb_by[R], "lb_gate"), (st[R]["n"], "n")):
            if not B._same(mine, er.loc[float(R), col]):
                raise SystemExit(f"REFUSED: R {R:g} {col}: {mine!r} against the gate's {er.loc[float(R), col]!r}.")


def trade_log(t: pd.DataFrame, days: list[str], blocks: list, keys, combine_rr: float) -> pd.DataFrame:
    """The Studio log of one arm's blocks (point or shifted): the rows give each trade's side, times, rung and exits,
    the blocks its outcomes at every R (blank where the hour offers no trade at that R). Rows walk the days in order,
    each day's trades in the blocks' order (entry time, stable -- `gate_blocks`' sort)."""
    import orb_trades_export as ox

    by = {d: g.sort_values("entry_t", kind="stable") for d, g in t.groupby("date")}
    ob = f"o_{combine_rr:g}"
    out = []
    for d, b in zip(days, blocks):
        g = by.get(d)
        if g is None or not len(g):
            if len(b):
                raise SystemExit("REFUSED: a day's trades differ from the gate's block.")
            continue
        if len(g) != len(b):
            raise SystemExit("REFUSED: a day's trades differ from the gate's block.")
        for j, (_, r) in enumerate(g.iterrows()):
            side = 1.0 if str(r["side"]) == "long" else -1.0
            if int(b.sides[j]) != int(side) or float(b.entry_t[j]) != float(r["entry_t"]):
                raise SystemExit("REFUSED: a trade's side or entry differs from the gate's block.")
            st, rpc = float(r["stop_ticks"]), float(b.risked[j])
            r1, m1, c1 = float(b.r_by_rr[1.0][j]), float(b.mae_by_rr[1.0][j]), float(r["c_1"])
            if not (np.isfinite(r1) and np.isfinite(m1) and np.isfinite(c1) and rpc > 0):
                raise SystemExit("REFUSED: a trade without its 1R outcome, or without a risk.")
            code = str(r[ob])
            if code not in REASON:
                raise SystemExit(f"REFUSED: a trade without its fresh Combine R's exit ({combine_rr:g}R).")
            row = {
                "timestamp_in": ox.stamp(d, int(r["entry_t"]) - 1),
                "timestamp_out": ox.stamp(d, int(r["exit_t"]) - 1),
                "symbol": "MNQ", "side": "long" if side > 0 else "short",
                "entry_price": ox.NOMINAL_ENTRY,
                "exit_price": ox.NOMINAL_ENTRY + side * (r1 + c1) * st * TICK_POINTS,
                "stop": ox.NOMINAL_ENTRY - side * st * TICK_POINTS,
                "target": ox.NOMINAL_ENTRY + side * math.floor(st + 1e-9) * TICK_POINTS,
                "contracts": 1,
                "pnl_gross": (r1 + c1) * rpc,
                "pnl_net": r1 * rpc,
                "exit_reason": REASON[code],
                "dollars_risked": rpc,
                "mae": m1 * rpc,
            }
            for k in keys:
                lab = rr_label(k)
                rv, mv = float(b.r_by_rr[k][j]), float(b.mae_by_rr[k][j])
                has = bool(np.isfinite(rv))
                if has != bool(np.isfinite(mv)) or has != bool(str(r[f"o_{k:g}"]) in KIND_WORD):
                    raise SystemExit(f"REFUSED: a trade's outcome, excursion and exit at R = {k:g} disagree.")
                if has and float(b.exit_by_rr[k][j]) != float(r[f"exit_t_{k:g}"]):
                    raise SystemExit(f"REFUSED: a trade's exit at R = {k:g} differs from the gate's block.")
                row[f"r_net_{lab}"] = rv if has else float("nan")
                row[f"mae_r_{lab}"] = mv if has else float("nan")
                row[f"t_out_{lab}"] = ox.stamp(d, int(r[f"exit_t_{k:g}"]) - 1) if has else None
                row[f"exit_kind_{lab}"] = KIND_WORD[str(r[f"o_{k:g}"])] if has else None
            row.update({"fee_per_micro": float(r["fee_micro_eq"]), "a3_hour_ct": str(r["decision_ct"]),
                        "a3_rung_points": float(r["S"]) * TICK_POINTS, "a3_day_kind": str(r["day_kind"]),
                        "signal_time": ox.stamp(d, int(r["decision_slot_minutes"])), "stop_ticks": st,
                        "a3_trading_day": d})
            out.append(row)
    log = pd.DataFrame(out)
    if not np.allclose(log["pnl_net"] / log["dollars_risked"], log["r_net_1"], rtol=0, atol=1e-12):
        raise SystemExit("REFUSED: the log's own outcome is not the 1R one.")
    return log


def mirror_base(L: dict, pol, cap: int, tv: float) -> dict:
    """The engine switches a Studio run must pass to reproduce P-13's gate rows: `atlas_a3.gate_kwargs`' call under
    FV3-C's config (`config/fv3_corrected_portfolio.yaml`), with P-13's day capacity, strict rule, paths and seed."""
    import a3_brk30 as B
    import fv3_gate_export as fx
    import score_fv3_grid as gf

    cfg, fcfg = L["cfg"], L["fcfg"]
    camp, fresh = fcfg["gate"]["campaign"], fcfg["state_policy"]["fresh"]
    sa = fcfg["state_policy"]["stand_aside"]
    pfile = ROOT / cfg["policy"]["policies_json"]
    edge = float(pol.id.split("_e")[1].split("_lam")[0])
    return {"allocation": camp["mode"], "accounts": int(camp["accounts"]), "bankroll": 5000.0,
            "bankroll_mode": "unconstrained" if gf.bankroll_output(fcfg) else "stated",
            "combine_rr": float(fresh["combine_rr"]), "combine_risk": float(fresh["combine_risk"]),
            "funded_rr": float(fresh["funded_rr"]), "funded_risk": float(fresh["funded_risk"]), "payout_path": "standard",
            "sizing_mode": camp["sizing"], "headroom": float(camp["headroom"]), "payout_method": camp["payout_method"],
            "max_concurrent_combines": int(camp["combines"]), "max_total_accounts": int(camp["accounts"]),
            "enforcement_p": 0.0, "rtp": False,
            "rtp_note": "the gate row's placement (D-289's base case, off)",
            "resample_paths": int(B.N_PATHS), "resample_horizon_days": int(camp["horizon_days"]), "seed": int(B.SEED),
            "settlement": camp["settlement"], "risk_policy": pol.as_dict(), "policy_id": pol.id, "policy_edge": edge,
            "policy_file": cfg["policy"]["policies_json"], "policy_file_sha256": text_sha256(pfile),
            "stand_aside": {kind: {"min_risk_share": float(v["min_risk_share"]),
                                   "floor_risk_per_contract": float(v["floor_ticks"]) * tv} for kind, v in sa.items()},
            **fx.mirror_switches(fcfg, tick_value=tv),
            # P-13's own: the operator's strict rule (R2, D-409, D-429, D-496) and the day capacity at the busiest day
            # (D-469); the Studio's protocol takes the log's busiest day, which is this capacity (checked at export)
            "one_at_a_time": float(B.STRICT_GAP), "trades_per_day": int(cap)}


def main(out: Path, prefix: str = PREFIX, results_dir: Path | None = None) -> int:
    import a3_brk30 as B
    import atlas_a3 as A
    import score_fv3_grid as gf

    from propedge import RESULTS_DIR
    from propedge.campaign.gate import mean_r, shifted_blocks
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    out = Path(out).resolve()
    if out == rd.resolve() or rd.resolve() in out.parents:
        raise SystemExit(f"REFUSED: {out} is inside {rd}; the export never writes into results/.")
    out.mkdir(parents=True, exist_ok=True)

    print("A3-BRK30's trades from the rung cache...")
    L = B.inputs()
    t, days = B.cell_trades(L)
    problems = B.identity_with_screen(rd, t, days, L)
    if problems:
        raise SystemExit("REFUSED: A3-BRK30's trades are not the screen's cell -- " + "; ".join(problems))
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    pol = B.policy(L)
    keys = B.rrs(t)
    cap = B.capacity(t, fcfg)
    if B.busiest(t) != cap:
        raise SystemExit(f"REFUSED: the day capacity {cap} is not the busiest day {B.busiest(t)}; the Studio's protocol "
                         "takes the log's busiest day.")
    st, e_by, lb_by, _, flagged = A.bounds(t, days, keys, cfg)
    check_edges(rd, keys, e_by, lb_by, st)
    crr, fr = B.fresh_rr(L)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    shifted = shifted_blocks(blocks, lb_by[fr] - e_by[fr], {k: lb_by[k] - e_by[k] for k in keys})
    rows = gate_rows(rd)
    for shift, blk in (("point", blocks), ("lower_bound", shifted)):
        r = rows.loc[shift]
        if not B._same(mean_r(blk), r["mean_r_used"]):
            raise SystemExit(f"REFUSED: the {shift} blocks' mean R {mean_r(blk)!r} is not the gate row's {r['mean_r_used']!r}.")
        if str(r["risk_policy"]) != pol.id or not B._same(r["one_at_a_time"], B.STRICT_GAP) \
                or int(float(r["paths"])) != int(B.N_PATHS):
            raise SystemExit(f"REFUSED: the {shift} gate row's policy, strict rule or paths are not P-13's.")
    base = mirror_base(L, pol, cap, tv)
    for k, col in (("settlement", "settlement"), ("routing", "routing"), ("seat_frees", "seat_frees"),
                   ("allocation", "mode"), ("accounts", "accounts"), ("max_concurrent_combines", "combines"),
                   ("resample_horizon_days", "horizon_days"), ("cross_account_rule", "cross_account_rule"),
                   ("hold_to_own_exit", "hold_to_own_exit")):
        if not B._same(base[k], rows.loc["point", col]):
            raise SystemExit(f"REFUSED: the mirror's {k} {base[k]!r} is not the gate row's {col} {rows.loc['point', col]!r}.")

    dayset = pd.DataFrame({"date": days, "entries": [len(b) for b in blocks]})
    days_name = f"{prefix}_days"
    for arm, blk, shift in (("point", blocks, "point"), ("verdict", shifted, "lower_bound")):
        log = trade_log(t, days, blk, keys, crr)
        want = e_by if arm == "point" else lb_by
        got = {k: float(np.nanmean(log[f"r_net_{rr_label(k)}"])) for k in keys}
        if not np.allclose([got[k] for k in keys], [want[k] for k in keys], rtol=0, atol=1e-12):
            raise SystemExit(f"REFUSED: the {arm} log's mean R by R is not the gate's "
                             + ("edges." if arm == "point" else "bounds."))
        if arm == "point":
            pnl = np.concatenate([b.pnl for b in blk if len(b)])
            if not np.array_equal(log["pnl_net"].to_numpy(), pnl):
                raise SystemExit("REFUSED: the point log's P&L differs from the gate's blocks.")
        mirror = {"reproduces": f"results/{GATE}, section gate, shift {shift}, enforcement_p 0, placement off"
                                + (" -- the verdict's row (is_gate_row)" if shift == "lower_bound" else ""),
                  **base, "logs": {"trades": f"{prefix}_{arm}_trades.csv", "days": f"{days_name}.csv"}}
        params_ = {"arm": arm, "shift": shift, "e_by_rr": {k: e_by[k] for k in keys}, "lb_by_rr": {k: lb_by[k] for k in keys},
                   "trades_by_rr": {k: int(st[k]["n"]) for k in keys}, "era_flagged": bool(flagged),
                   "bounds_read": "the lower era's" if flagged else "pooled", "prereg": "P-13",
                   "verdict": f"results/{GATE}", "verdict_sha256": text_sha256(rd / GATE),
                   "screen": f"results/{B.SCREEN}", "model": B.MODEL, "cell": B.cell_label(),
                   "trades": int(len(t)), "days": int(len(days)), "busiest_day": int(B.busiest(t)),
                   "mae": "the rung walk's adverse excursion at each R (fv3_rung_walk)", "mirror": mirror,
                   "decision": f"{DECISION} (P-13's verdict); the export EXPLORATORY, no new variant"}
        write_result(log, f"{prefix}_{arm}_trades", script=SCRIPT, seed=int(B.SEED), exploratory=True, results_dir=out,
                     parameters=params_,
                     notes={"status": "EXPLORATORY: P-13's gate blocks re-presented for the Campaign Studio; the verdict "
                                      "is D-500's"},
                     description=f"EXPLORATORY: A3-BRK30's gate campaign (P-13), the {shift} arm, as a Campaign Studio "
                                 "trade log (the cell's trades on FV3-C's rungs, every R's outcome as the state policy "
                                 "reads them, blank where the hour offers no trade at that R).")
        blanks = {rr_label(k): int(log[f"r_net_{rr_label(k)}"].isna().sum()) for k in keys}
        print(f"{prefix}_{arm}: {len(log)} trades; mean 1R {float(log['r_net_1'].mean()):.6f}; "
              f"{log['exit_reason'].value_counts().to_dict()}; no trade at R: {blanks}")
    write_result(dayset, days_name, script=SCRIPT, seed=None, require_seed=False, exploratory=True, results_dir=out,
                 parameters={"rule": "every day record of A1's walk (the gate's day blocks)", "decision": DECISION,
                             "verdict": f"results/{GATE}"},
                 notes={"status": "EXPLORATORY: P-13's gate day set, days without a trade included"},
                 description="EXPLORATORY: A3-BRK30's gate day set -- one row per session the gate laid a block on.")
    print(f"day set: {len(days)} sessions, {int((dayset['entries'] == 0).sum())} without a trade; busiest day "
          f"{int(dayset['entries'].max())}; written to {out}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", required=True, help="the folder the logs and their manifests go to (never results/)")
    ap.add_argument("--prefix", default=PREFIX, help=f"the files' prefix ({PREFIX})")
    a = ap.parse_args()
    raise SystemExit(main(Path(a.out), prefix=a.prefix))
