"""EXPLORATORY (D-299): the campaign FV3's verdict was read from -- the D-145 gate's own day blocks under the state
policy -- as Campaign Studio trade logs, so the operator can replay it and look (the operator, 2026-10-05: "Can you
share the results in the campaign studio so I can visualize results"; the Studio is an inspection view, never a
verdict -- D-155's step 7; FV3's verdict is D-298's).

    python scripts/fv3_gate_export.py

It rebuilds the gate's blocks as `scripts/score_fv3_grid.py` built them, from the same records:

* **the trades** (`gate_trades`'s rule): each test year 2013 to June 2025 traded by the configuration the walk-forward
  selected on the years before it (results/fv3_grid.csv, `walkforward`), kept one at a time by the fresh Combine
  geometry's exits (1R at $1,500), each trade carrying its outcome and true MAE at every R of the menu (1, 1.5, 2,
  2.5, 3), net of the cell's today-cost at that R -- blank where the room rule permits no trade at that R (D-162:
  the engine takes no trade for an account whose state calls for it);
* **the stops**: each trade's own ladder stop (no draw -- FV3's stops are the capture's);
* **the day set**: every non-FOMC session of the test years, days without a trade included.

The per-R edge, bound and trade count of every R are checked equal to results/fv3_grid.csv's `gate_inputs`, and the
policy cell to its `gate` rows, before anything is written. Two logs:

* `fv3_gate_point` -- the outcomes as traded: the gate's `point` arm;
* `fv3_gate_verdict` -- every R's outcomes shifted down to that R's one-sided 95 % lower bound (`gate.shifted_blocks`):
  the arm the verdict's gate row was read on (`is_gate_row`, 0 % denial, D-234).

A Studio run of each at the manifest's `mirror` (the gate's campaign, the exported state policy at the edge nearest
the funded leg's bound, the seed) should reproduce that arm's row at 0 % denial in results/fv3_grid.csv -- **with the
Responsible Trading Program's placement ON, as the gate ran it** (the audit's finding 1, D-298: the engine's default,
not D-289's base case); the Studio's own counterfactual shows the same paths with the placement off.

Each trade is one micro (MNQ): `dollars_risked` its stop's risk per micro; `pnl_net` its 1R outcome times it (the
Combine's fresh geometry; in the verdict arm the 1R outcome at the 1R bound -- the gate's own block P&L there carries
the funded R's shift instead, a number the engine never reads under a policy that sets R), `pnl_gross` the same before
the cell's today-cost at 1R; `mae` the 1R excursion. `exit_reason` is the 1R outcome's (a breakeven exit is `other`).
Times are bar starts: the entry at its bar's open (two minutes after the signal bar's close, D-282) and the exit at the
start of the bar it happened in, so the flat-account routing compares exactly the gate's bars (D-159). Prices are
constructed (risk and P&L exact). Beside the canonical columns: the session, the phase, the rung, the signal time and
the configuration. It reads no new data and selects nothing -- no new variant.

Writes results/fv3_studio_gate_point_trades.csv, results/fv3_studio_gate_verdict_trades.csv and
results/fv3_studio_gate_days.csv with manifests.

    python scripts/fv3_gate_export.py --grid fv3_grid_corrected --prefix fv3_studio_gate_corrected

exports the corrected run's gate (D-301, D-302) the same way: its mirror carries the placement the gate row ran under
(off, D-289), D-272's stand-aside per leg as the Studio's spec takes it (SD-03), the version-2 policy and the stated
bankroll (the Studio's SD-04 runs bankroll-free by default).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import orb_trades_export as ox  # noqa: E402
import score_fv3_grid as gf  # noqa: E402
import score_orb5_grid as g5  # noqa: E402

SCRIPT = "scripts/fv3_gate_export.py"
TICK_POINTS = 0.25                                   # MNQ's tick, in points
RUNG_NAMES = {gf.RUNG_HALF: "half", gf.RUNG_FULL: "full", gf.RUNG_DOUBLE: "double"}
KEYS = [float(R) for R in gf.RR_MENU]                # the R menu; `main` re-reads it from the declaration's config (D-306)


def rr_label(x: float) -> str:
    """A per-R column's label: 1.0 -> '1', 2.5 -> '2.5'."""
    return f"{x:.6f}".rstrip("0").rstrip(".")


def cell_key(row) -> dict:
    """A result row's cell as `gf._key` writes it (a CSV reads the booleans back as strings or bools)."""
    def b(v) -> bool:
        return str(v).strip().lower() == "true"
    return {"sessions": str(row["sessions"]), "continuation": b(row["continuation"]),
            "displacement": str(row["displacement"]), "double_rung_reversions": b(row["double_rung_reversions"])}


def selections(grid: pd.DataFrame, cfg: dict) -> tuple[dict[int, int], int]:
    """(test year -> the walk-forward's selected cell index, the final cell's index), from results/fv3_grid.csv."""
    keys = [gf._key(c) for c in gf.cells(cfg)]

    def idx(row) -> int:
        k = cell_key(row)
        m = [i for i, kk in enumerate(keys) if kk == k]
        if len(m) != 1:
            raise SystemExit(f"REFUSED: the selection {k} is not one of the declared cells.")
        return m[0]
    wf = grid[grid["section"] == "walkforward"]
    # a test year without a selection (D-308's run: 2021, one development year giving no bound) contributes no gate
    # trades, exactly as the scorer's gate_trades skips it; a run with no selected year at all is refused
    with_sel = wf[wf["sessions"].notna()] if len(wf) else wf
    if not len(with_sel):
        raise SystemExit("REFUSED: the screen result has no walk-forward year with a selection.")
    sels = {int(float(r["test_year"])): idx(r) for _, r in with_sel.iterrows()}
    f = grid[grid["section"] == "final"]
    if len(f) != 1:
        raise SystemExit("REFUSED: results/fv3_grid.csv holds no single final selection.")
    return sels, idx(f.iloc[0])


def gate_rows(S: gf.Signals3, cfg: dict, sels: dict[int, int]) -> pd.DataFrame:
    """`gf.gate_trades`'s rule with what a reader needs beside it: the side, the session, the phase, the rung, the
    signal's bar, the 1R exit kind and the cell's today-cost at 1R. The outcomes are computed once per selected
    cell (the walk-forward picks the same cell in several years)."""
    cells = gf.cells(cfg)
    c_spec = gf.leg_spec(cfg, "combine")
    costs = gf.fidelity_of(cfg)["costs"]
    per_trade = costs in ("per_trade", "per_trade_at_size")   # D-321: each trade's own cost, as the scorer charges it
    at_size = costs == "per_trade_at_size"                     # D-324: the fee in it, re-priced in the engine
    cache: dict[int, tuple] = {}
    out = []
    for y, k in sels.items():
        if k not in cache:
            c = cells[k]
            cand = S.candidates(c)
            rung = S.rung(bool(c["double_rung_reversions"]))
            per_r = {R: S.outcome(rung, "r", R, c_spec[2], c_spec[3]) for R in KEYS}
            base = per_r[c_spec[1]] if c_spec[1] in per_r else S.outcome(rung, "r", c_spec[1], c_spec[2], c_spec[3])
            tcs = {R: S.today_cost(cand, per_r[R]["stop"], c_spec[2], c_spec[3]) for R in KEYS}
            kept_all = S.kept(cand & base["permitted"], base["exit"], base["stopped"],
                              two_losses_bos_only=(c["displacement"] == "rule"))
            cache[k] = (c, rung, per_r, base, tcs, kept_all)
        c, rung, per_r, base, tcs, kept_all = cache[k]
        kept = kept_all & (S.year == y)
        key = gf._key(c)
        cfg_text = (f"{key['sessions']} | continuation {'on' if key['continuation'] else 'off'} | displacement "
                    f"{key['displacement']} | double-rung reversions {'on' if key['double_rung_reversions'] else 'off'}")
        for i in np.nonzero(kept)[0]:
            row = {"date": S.df["date"].iat[i], "year": y, "entry_t": float(S.bar[i]), "exit_t": float(base["exit"][i]),
                   "flat": bool(base["flat"][i]), "stop_ticks": float(base["stop"][i])}
            for R in KEYS:
                o = per_r[R]
                ok = bool(o["permitted"][i])
                cost = float(o["cost"][i]) if per_trade else float(tcs[R])            # D-321, as the scorer's
                row[f"r_{R:g}"] = float(o["gross"][i] - cost) if ok else float("nan")
                row[f"mae_{R:g}"] = float(o["mae_r"][i]) if ok else float("nan")
                # for the Studio's trade chart (SD-09): each R's own exit -- the slot its stop, target or breakeven was
                # reached (the flatten's at 15:08) -- and its kind; display only, no number reads them
                row[f"xexit_{R:g}"] = float(o["exit"][i]) if ok else float("nan")
                row[f"xkind_{R:g}"] = (("stop" if o["stopped"][i] else "target" if o["target"][i]
                                        else "breakeven" if o["breakeven"][i] else "flatten") if ok else "")
                # D-349: the engine's own column for the same exit, so the mirror's blocks carry exit_by_rr and the
                # cross-account rule holds a position to its exit at the R the account trades, as the gate run did
                row[f"exit_t_{R:g}"] = float(o["exit"][i]) if ok else float("nan")
            kind = ("stop" if base["stopped"][i] else "target" if base["target"][i]
                    else "other" if base["breakeven"][i] else "flatten")
            row.update({"dir": float(S.dir[i]), "session": str(S.session[i]), "signal_slot": int(S.slot[i]),
                        "phase": "continuation" if S.cont[i] else "reversion", "rung": RUNG_NAMES[int(rung[i])],
                        "kind_1": kind, "cost_1": float(per_r[1.0]["cost"][i]) if per_trade else float(tcs[1.0]),
                        "config": cfg_text})
            if at_size:                                         # D-324: as the scorer's gate rows carry it
                st = float(base["stop"][i])
                row["fee_micro_eq"] = float(S.fee(np.array([st if np.isfinite(st) and st > 0 else 1.0]),
                                                  c_spec[2], c_spec[3])[0])
            out.append(row)
    return pd.DataFrame(out)


def check_inputs(t: pd.DataFrame, grid: pd.DataFrame) -> dict[float, dict[str, float]]:
    """Each R's edge, bound and trade count against results/fv3_grid.csv's `gate_inputs`; the stats, keyed by R."""
    gi = grid[grid["section"] == "gate_inputs"]
    stats = {}
    for R in KEYS:
        col = f"r_{R:g}"
        v = t[col].dropna() if len(t) else pd.Series(dtype=float)
        by = v.groupby(t.loc[v.index, "year"]).mean() if len(v) else pd.Series(dtype=float)
        s = {"e": float(v.mean()) if len(v) else float("nan"), "lb": g5.bound(by), "n": int(len(v))}
        row = gi[gi["rr"].astype(float) == R]
        if len(row) != 1:
            raise SystemExit(f"REFUSED: results/fv3_grid.csv has no single gate_inputs row at R = {R:g}.")
        r = row.iloc[0]
        if s["n"] != int(float(r["oos_trades"])) or not np.isclose(s["e"], float(r["e"]), rtol=0, atol=1e-9, equal_nan=True) \
                or not np.isclose(s["lb"], float(r["lb"]), rtol=0, atol=1e-9, equal_nan=True):
            raise SystemExit(f"REFUSED: the trades at R = {R:g} differ from results/fv3_grid.csv's gate inputs.")
        stats[R] = s
    return stats


def ordered(rows: pd.DataFrame, days: list[str]) -> list[pd.DataFrame | None]:
    """The trades of each day of `days` in the gate's block order (entry time, stable)."""
    by = {d: g.sort_values("entry_t", kind="stable") for d, g in rows.groupby("date")} if len(rows) else {}
    return [by.get(d) for d in days]


def trade_log(rows: list, blocks: list, days: list[str]) -> pd.DataFrame:
    """The Studio log of one arm's blocks (point or shifted), the rows giving each trade's side and reading. The
    log's own outcome is the 1R one (`r_net_1`); every R of the menu rides beside it, blank where no trade -- with,
    where the rows carry them, each R's own exit time and kind (`t_out_<R>`, `exit_kind_<R>`: stop, target,
    breakeven, flatten) for the Studio's trade chart. `timestamp_out` and `exit_reason` stay the fresh Combine R's:
    the exit the gate's flat routing reads."""
    out = []
    for d, g, b in zip(days, rows, blocks):
        if g is None or not len(b):
            if (g is None) != (not len(b)):
                raise SystemExit("REFUSED: a day's trades differ from the gate's block.")
            continue
        if len(g) != len(b):
            raise SystemExit("REFUSED: a day's trades differ from the gate's block.")
        for j, (_, r) in enumerate(g.iterrows()):
            side = 1.0 if r["dir"] > 0 else -1.0
            st, rpc = float(r["stop_ticks"]), float(b.risked[j])
            r1, m1, cost = float(b.r_by_rr[1.0][j]), float(b.mae_by_rr[1.0][j]), float(r["cost_1"])
            if not np.isfinite(r1) or not np.isfinite(m1) or not rpc > 0:
                raise SystemExit("REFUSED: a trade without its 1R outcome, or without a risk.")
            won = math.floor(st + 1e-9)
            row = {
                "timestamp_in": ox.stamp(d, int(r["entry_t"]) - 1),
                "timestamp_out": ox.stamp(d, int(r["exit_t"]) - 1),
                "symbol": "MNQ", "side": "long" if side > 0 else "short",
                "entry_price": ox.NOMINAL_ENTRY,
                "exit_price": ox.NOMINAL_ENTRY + side * (r1 + cost) * st * TICK_POINTS,
                "stop": ox.NOMINAL_ENTRY - side * st * TICK_POINTS,
                "target": ox.NOMINAL_ENTRY + side * won * TICK_POINTS,
                "contracts": 1,
                "pnl_gross": (r1 + cost) * rpc,
                "pnl_net": r1 * rpc,
                "exit_reason": r["kind_1"],
                "dollars_risked": rpc,
                "mae": m1 * rpc,
            }
            for k in KEYS:
                lab = rr_label(k)
                row[f"r_net_{lab}"] = float(b.r_by_rr[k][j])
                row[f"mae_r_{lab}"] = float(b.mae_by_rr[k][j])
                if f"xexit_{k:g}" in r.index:
                    # the Studio's trade chart (SD-09): each R's own exit time and kind, blank exactly where the R's
                    # outcome is; `timestamp_out` stays the exit the gate's routing reads (the fresh Combine R's), so
                    # the mirror lays back the same blocks
                    has = np.isfinite(row[f"r_net_{lab}"])
                    if has != np.isfinite(float(r[f"xexit_{k:g}"])):
                        raise SystemExit(f"REFUSED: a trade's exit time at R = {k:g} disagrees with its outcome.")
                    row[f"t_out_{lab}"] = ox.stamp(d, int(r[f"xexit_{k:g}"]) - 1) if has else None
                    row[f"exit_kind_{lab}"] = str(r[f"xkind_{k:g}"]) if has else None
            if "fee_micro_eq" in r.index:                       # D-324: the fee a micro-equivalent priced in
                row["fee_per_micro"] = float(r["fee_micro_eq"])
            row.update({"fv3_session": r["session"], "fv3_phase": r["phase"], "fv3_rung": r["rung"],
                        "fv3_config": r["config"], "signal_time": ox.stamp(d, int(r["signal_slot"])),
                        "stop_ticks": st})
            out.append(row)
    log = pd.DataFrame(out)
    if not np.allclose(log["pnl_net"] / log["dollars_risked"], log["r_net_1"], atol=1e-9):
        raise SystemExit("REFUSED: the log's own outcome is not the 1R one.")
    return log


def mirror_switches(cfg: dict, arm: str = "point", tick_value: float = 0.5) -> dict:
    """The engine switches a Studio run must pass to reproduce a gate row of this config -- every fidelity rule since
    D-306 as the scorer reads it, and (D-339) the firm's cross-account rule, the seat switch and the flip stream's spec
    (None without one; on the `verdict` arm the spec at the bracket's own lower bound, as the gate's lower-bound arm ran
    it)."""
    f = gf.fidelity_of(cfg)
    spec = gf.flip_spec_of(cfg)
    if spec is not None and arm == "verdict" and np.isfinite(float(spec.edge_lower_bound)):
        spec = spec.shifted(float(spec.edge_lower_bound))
    rule = gf.sizing_rule(cfg, tick_value)
    return {
        # D-306: the gate's Combine trades close at what the account needs to pass (the smallest carried R at or above
        # it); a Studio without that rule reproduces the gate row only when it is off
        "need_aware_exits": bool(f["need_aware_exits"]),
        # D-313: the Combine's consistency-capped exits and the room cap -- engine rules the Studio must pass
        "consistency_cap_exits": bool(f["consistency_cap_exits"]),
        "room_cap": list(f["room_cap"]),
        # D-318: the router hands a trade only to an account that can take it, and a room-capped Combine out of room
        # ends (the room cap carries it); the Studio must pass `routing` to reproduce the row
        "routing": f["routing"],
        # D-324: the fee re-priced at each trade's contracts (with the log's `fee_per_micro`), and no-trade states for
        # Standard-path accounts only -- engine rules the Studio must pass
        "fee_schedule": None if rule.fee_schedule is None else list(rule.fee_schedule),
        "no_trade_standard_path_only": bool(f.get("no_trade_standard_path_only", False)),
        "decision_inputs_cents": bool(f.get("decision_inputs_cents", False)),            # D-328
        # D-339: the firm's cross-account rule (no signal opposite to any open position), when a funded seat is freed,
        # and the flip stream (its spec as the engine's FlipDraw takes it; the log's `side` column feeds the rule)
        "cross_account_rule": bool(f.get("cross_account_rule", False)),
        "seat_frees": str(f.get("seat_frees", "next_session")),
        "flip": None if spec is None else spec.as_dict(),
        # D-351: a routed position held to its exit at the R its account trades (the rule implies it)
        "hold_to_own_exit": bool(f.get("hold_to_own_exit", False)) or bool(f.get("cross_account_rule", False)),
        # D-354 (the Studio's SD-27): the export's trade times are bar STARTS, one minute before the engine's bar-end clock;
        # the router must be fed the engine's clock (a position held to t_end is flat at t_end; a signal in a flip box's
        # last minute is routed), so the mirror adds this offset to every block time before it routes
        "router_clock_offset_min": 1,
    }


def main(results_dir: Path | None = None, runs_dir: Path | None = None, grid_name: str = "fv3_grid",
         prefix: str = "fv3_studio_gate", config_path: str | None = None) -> int:
    global KEYS
    from propedge import RESULTS_DIR
    from propedge.campaign.gate import shifted_blocks
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = gf.config(config_path)
    KEYS = [float(R) for R in gf.rr_menu(cfg)]              # D-306: the declaration's own R menu
    grid = read_result(rd / f"{grid_name}.csv")
    sels, kf = selections(grid, cfg)
    final = gf.cells(cfg)[kf]
    fresh = cfg["state_policy"]["fresh"]
    fr = float(fresh["funded_rr"])
    print("loading the captures...")
    sig, ses, _, _ = gf.load(rd, Path(runs_dir) if runs_dir is not None else ROOT / "runs", cfg)
    fm = FillModel.load("assumed")
    q = params("NQ")
    S = gf.Signals3(sig, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]),
                    q["micro_tick"] * q["micro_point_value"], cfg["ladder"])
    print("the walk-forward's out-of-sample trades...")
    mine = gate_rows(S, cfg, sels)
    stats = check_inputs(mine, grid)
    wf_first = int(cfg["selection"]["walkforward"].get("first_test_year", gf.WF_FIRST))
    days = sorted(d for d in set(ses["date"]) if int(d[:4]) >= wf_first)
    blocks, n_used = gf.gate_blocks(mine, days, S.td, KEYS,
                                    require_sides=bool(gf.fidelity_of(cfg).get("cross_account_rule", False)),   # D-348: the rows' dir
                                    require_exits=bool(gf.fidelity_of(cfg).get("hold_to_own_exit", False)))     # D-351
    if n_used != len(mine):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    e_by = {k: stats[k]["e"] for k in KEYS}
    lb_by = {k: stats[k]["lb"] for k in KEYS}
    shifted = shifted_blocks(blocks, lb_by[fr] - e_by[fr], {k: lb_by[k] - e_by[k] for k in KEYS})
    policy, e_used, pid = gf.policy_for_edge(cfg, lb_by[fr])
    gate_rows_csv = grid[grid["section"] == "gate"]
    if not len(gate_rows_csv) or set(gate_rows_csv["policy_id"].astype(str)) != {pid}:
        raise SystemExit(f"REFUSED: the policy cell {pid} is not the gate rows' ({set(gate_rows_csv['policy_id'])}).")
    rows = ordered(mine, days)

    camp = cfg["gate"]["campaign"]
    # the placement the gate row ran under: the corrected run (D-301) records it per row; the first run (D-295) ran
    # the engine's default, placement on (D-298's audit, finding 1)
    corrected = "placement" in gate_rows_csv.columns
    if corrected:
        row0 = gate_rows_csv[gate_rows_csv["is_gate_row"].astype(str) == "True"].iloc[0]
        rtp = str(row0["placement"]) == "on"
    else:
        rtp = True
    out_mode = gf.bankroll_output(cfg)                        # D-312: the bankroll an output of the run
    mirror_base = {"allocation": camp["mode"], "accounts": int(camp["accounts"]),
                   "bankroll": float(camp["bankroll"]) if camp.get("bankroll") is not None else 5000.0,
                   "bankroll_mode": "unconstrained" if out_mode else "stated",   # the Studio's SD-04
                   "combine_rr": float(fresh["combine_rr"]), "combine_risk": float(fresh["combine_risk"]),
                   "funded_rr": fr, "funded_risk": float(fresh["funded_risk"]), "payout_path": "standard",
                   "sizing_mode": camp["sizing"], "headroom": float(camp["headroom"]),
                   "payout_method": camp["payout_method"], "max_concurrent_combines": int(camp["combines"]),
                   "max_total_accounts": int(camp["accounts"]), "enforcement_p": 0.0, "rtp": rtp,
                   "rtp_note": ("the gate row's placement (D-289's base case, off; D-301)" if corrected else
                                "as the gate ran it -- the engine's default (D-298's audit, finding 1), not D-289's "
                                "base case; the Studio's counterfactual shows the same paths with the placement off"),
                   "resample_paths": int(camp["n_paths"]), "resample_horizon_days": int(camp["horizon_days"]),
                   "seed": int(cfg["seeds"]["gate"]), "settlement": camp["settlement"],
                   "risk_policy": policy.as_dict(), "policy_id": pid, "policy_edge": e_used,
                   **mirror_switches(cfg, tick_value=S.td)}
    if corrected:                                             # D-272's stand-aside per leg, as the Studio's spec takes it (SD-03)
        sa = cfg["state_policy"]["stand_aside"]
        mirror_base["stand_aside"] = {kind: {"min_risk_share": float(v["min_risk_share"]),
                                             "floor_risk_per_contract": float(v["floor_ticks"]) * S.td}
                                      for kind, v in sa.items()}
    for arm, blk, shift in (("point", blocks, "point"), ("verdict", shifted, "lower_bound")):
        log = trade_log(rows, blk, days)
        if arm == "point":
            want = {k: e_by[k] for k in KEYS}
            if not np.allclose([float(np.nanmean(log[f"r_net_{rr_label(k)}"])) for k in KEYS],
                               [want[k] for k in KEYS], rtol=0, atol=1e-9):
                raise SystemExit("REFUSED: the point log's mean R by R differs from the gate inputs.")
            pnl = np.concatenate([b.pnl for b in blk if len(b)])
            if not np.allclose(log["pnl_net"].to_numpy(), pnl, rtol=0, atol=1e-9):
                raise SystemExit("REFUSED: the point log's P&L differs from the gate's blocks.")
        else:
            if not np.allclose([float(np.nanmean(log[f"r_net_{rr_label(k)}"])) for k in KEYS],
                               [lb_by[k] for k in KEYS], rtol=0, atol=1e-9):
                raise SystemExit("REFUSED: the verdict log's mean R by R is not each R's lower bound.")
        mirror = {"reproduces": f"results/{grid_name}.csv, section gate, shift {shift}, enforcement_p 0"
                                + (f", placement {'on' if rtp else 'off'}" if corrected else "")
                                + (" -- the verdict's row (is_gate_row)" if shift == "lower_bound" else ""),
                  **mirror_base,
                  # D-339: the verdict arm's flips run at the bracket's own lower bound, as the gate ran them
                  "flip": mirror_switches(cfg, arm=arm, tick_value=S.td)["flip"]}
        params_ = {"arm": arm, "shift": shift, "e_by_rr": e_by, "lb_by_rr": lb_by, "oos_trades_by_rr": {k: stats[k]["n"] for k in KEYS},
                   "walkforward": f"results/{grid_name}.csv, walkforward", "final": gf._key(final), "mae": "the capture's true "
                   "adverse excursion (D-293)", "mirror": mirror, "decision": "D-299" + (", D-301, D-302" if corrected else "")}
        write_result(log, f"{prefix}_{arm}_trades", script=SCRIPT, seed=int(cfg["seeds"]["gate"]),
                     exploratory=True, results_dir=results_dir, parameters=params_,
                     notes={"status": "EXPLORATORY: the gate's own blocks re-presented for the Campaign Studio; the "
                                      "verdict is D-298's"},
                     description=f"EXPLORATORY: FV3's gate campaign, the {shift} arm, as a Campaign Studio trade log "
                                 "(the walk-forward's out-of-sample trades, the ladder's stops, every R's outcome as "
                                 "the state policy reads them, blank where the room permits no trade).")
        blanks = {rr_label(k): int(log[f"r_net_{rr_label(k)}"].isna().sum()) for k in KEYS}
        print(f"{prefix}_{arm}: {len(log)} trades; mean 1R {float(log['r_net_1'].mean()):.4f}; "
              f"{log['exit_reason'].value_counts().to_dict()}; no trade at R: {blanks}")
    dayset = pd.DataFrame({"date": days, "entries": [len(b) for b in blocks]})
    write_result(dayset, f"{prefix}_days", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, parameters={"rule": "every non-FOMC session of the test years (the gate's "
                                                               "day blocks)", "decision": "D-299", "grid": grid_name},
                 notes={"status": "EXPLORATORY: the gate's day set, days without a trade included"},
                 description="EXPLORATORY: FV3's gate day set -- one row per session the gate laid a block on.")
    print(f"day set: {len(days)} sessions, {int((dayset['entries'] == 0).sum())} without a trade; busiest day "
          f"{int(dayset['entries'].max())}")
    return 0


def confirmation_main(results_dir: Path | None = None, runs_dir: Path | None = None,
                      prefix: str = "fv3_studio_confirmation", conf_path: Path | None = None) -> int:
    """EXPLORATORY (D-362): P-06's verdict campaign -- FV3-C's gate on NQ's held-back window, the run
    `results/fv3_confirmation.csv` was read from (D-361) -- as Campaign Studio trade logs, for the operator to replay and
    look (the operator, 2026-10-13: "Can we fully update the campaign replay so I can visualise the results and
    executions"). The window's records are read exactly as the verdict read them (`confirm_fv3.load_window`, each
    period's label in the year slot; the saved runs `period_state` accepts), the frozen cell's trades rebuilt by
    `gate_rows`, and each R's edge, block bound and trade count checked equal to the verdict file's `gate_inputs`, the
    policy cell to its `gate` rows, before anything is written. Two logs (the point arm; the verdict arm, every R shifted
    to its own bound) and the day set (every window session the gate laid a block on), with the mirror the verdict's
    gate row ran under. The Studio is an inspection view: nothing here is a reading of the window beyond P-06's."""
    global KEYS
    saved = KEYS
    try:
        return _confirmation_export(results_dir, runs_dir, prefix, conf_path)
    finally:
        KEYS = saved                                     # the module's menu as it was (the helpers read it)


def _confirmation_export(results_dir, runs_dir, prefix, conf_path) -> int:
    global KEYS
    import confirm_fv3 as cf

    from propedge import RESULTS_DIR
    from propedge.campaign.gate import shifted_blocks
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    rund = Path(runs_dir) if runs_dir is not None else ROOT / "runs"
    conf = cf.config(conf_path)
    cfg = cf.candidate(conf)
    KEYS = [float(R) for R in gf.rr_menu(cfg)]
    verdict = read_result(rd / "fv3_confirmation.csv")
    states = {str(p["id"]): cf.period_state(p, rd, rund) for p in conf["periods"]}
    if any(s != "ingested" for s, _, _ in states.values()):
        raise SystemExit("REFUSED: every period's run must be saved as the verdict read it: "
                         + "; ".join(why for s, _, why in states.values() if s != "ingested"))
    chosen = {k: run for k, (_, run, _) in states.items()}
    sig, ses, _, _, days, label_of_day = cf.load_window(conf, cfg, chosen, rd, rund)
    fm, q = FillModel.load("assumed"), params("NQ")
    S = gf.Signals3(sig, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]),
                    q["micro_tick"] * q["micro_point_value"], cfg["ladder"])
    S.year = np.array([label_of_day[str(d)] for d in S.df["date"]], dtype=int)
    labels = sorted({int(p["label"]) for p in conf["periods"]})
    mine = gate_rows(S, cfg, {lab: 0 for lab in labels})
    period_of = {int(p["label"]): str(p["id"]) for p in conf["periods"]}
    stats = cf.edge_stats(mine, KEYS, days, int(conf["block_days"]), None)
    gi = verdict[verdict["section"] == "gate_inputs"]
    for R in KEYS:
        r = gi[gi["rr"].astype(float) == R].iloc[0]
        s = stats[R]
        if s["n"] != int(float(r["oos_trades"])) or not np.isclose(s["e"], float(r["e"]), rtol=0, atol=1e-9) \
                or not np.isclose(s["lb"], float(r["lb"]), rtol=0, atol=1e-9, equal_nan=True):
            raise SystemExit(f"REFUSED: the trades at R = {R:g} differ from results/fv3_confirmation.csv's gate inputs.")
    fresh = cfg["state_policy"]["fresh"]
    fr = float(fresh["funded_rr"])
    blocks, n_used = gf.gate_blocks(mine, days, S.td, KEYS, require_sides=True, require_exits=True)
    if n_used != len(mine):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    e_by = {k: stats[k]["e"] for k in KEYS}
    lb_by = {k: stats[k]["lb"] for k in KEYS}
    shifted = shifted_blocks(blocks, lb_by[fr] - e_by[fr], {k: lb_by[k] - e_by[k] for k in KEYS})
    policy, e_used, pid = gf.policy_for_edge(cfg, lb_by[fr])
    gate_csv = verdict[verdict["section"] == "gate"]
    if not len(gate_csv) or set(gate_csv["policy_id"].astype(str)) != {pid}:
        raise SystemExit(f"REFUSED: the policy cell {pid} is not the verdict's gate rows'.")
    row0 = gate_csv[gate_csv["is_gate_row"].astype(str) == "True"].iloc[0]
    rtp = str(row0["placement"]) == "on"
    rows = ordered(mine, days)
    camp = cfg["gate"]["campaign"]
    sa = cfg["state_policy"]["stand_aside"]
    mirror_base = {"allocation": camp["mode"], "accounts": int(camp["accounts"]), "bankroll": 5000.0,
                   "bankroll_mode": "unconstrained" if gf.bankroll_output(cfg) else "stated",
                   "combine_rr": float(fresh["combine_rr"]), "combine_risk": float(fresh["combine_risk"]),
                   "funded_rr": fr, "funded_risk": float(fresh["funded_risk"]), "payout_path": "standard",
                   "sizing_mode": camp["sizing"], "headroom": float(camp["headroom"]),
                   "payout_method": camp["payout_method"], "max_concurrent_combines": int(camp["combines"]),
                   "max_total_accounts": int(camp["accounts"]), "enforcement_p": 0.0, "rtp": rtp,
                   "rtp_note": "the gate row's placement (D-289's base case, off)",
                   "resample_paths": int(camp["n_paths"]), "resample_horizon_days": int(camp["horizon_days"]),
                   "seed": int(cfg["seeds"]["gate"]), "settlement": camp["settlement"],
                   "risk_policy": policy.as_dict(), "policy_id": pid, "policy_edge": e_used,
                   "stand_aside": {kind: {"min_risk_share": float(v["min_risk_share"]),
                                          "floor_risk_per_contract": float(v["floor_ticks"]) * S.td}
                                   for kind, v in sa.items()},
                   **mirror_switches(cfg, tick_value=S.td)}
    for arm, blk, shift in (("point", blocks, "point"), ("verdict", shifted, "lower_bound")):
        log = trade_log(rows, blk, days)
        # each trade's trading day in the log's order (trade_log walks the days, each day's trades in block order); an
        # evening trade's stamp carries the calendar date before its trading day, so the period is read from the day
        trade_days = [d for d, g in zip(days, rows) if g is not None for _ in range(len(g))]
        if len(trade_days) != len(log):
            raise SystemExit("REFUSED: the log's trades differ from the days' trades.")
        log["fv3_trading_day"] = trade_days
        log["fv3_period"] = [period_of[label_of_day[d]] for d in trade_days]
        want = e_by if arm == "point" else lb_by
        if not np.allclose([float(np.nanmean(log[f"r_net_{rr_label(k)}"])) for k in KEYS], [want[k] for k in KEYS],
                           rtol=0, atol=1e-9):
            raise SystemExit(f"REFUSED: the {arm} log's mean R by R differs from the verdict's "
                             + ("edges" if arm == "point" else "bounds") + ".")
        if arm == "point":
            pnl = np.concatenate([b.pnl for b in blk if len(b)])
            if not np.allclose(log["pnl_net"].to_numpy(), pnl, rtol=0, atol=1e-9):
                raise SystemExit("REFUSED: the point log's P&L differs from the gate's blocks.")
        mirror = {"reproduces": "results/fv3_confirmation.csv, section gate, shift " + shift
                                + f", enforcement_p 0, placement {'on' if rtp else 'off'}"
                                + (" -- the verdict's row (is_gate_row)" if shift == "lower_bound" else ""),
                  **mirror_base, "flip": None}
        params_ = {"arm": arm, "shift": shift, "e_by_rr": e_by, "lb_by_rr": lb_by,
                   "oos_trades_by_rr": {k: stats[k]["n"] for k in KEYS}, "prereg": str(conf["prereg_id"]),
                   "verdict": "results/fv3_confirmation.csv", "runs": chosen, "block_days": int(conf["block_days"]),
                   "mae": "the capture's true adverse excursion (D-293)", "mirror": mirror, "decision": "D-362"}
        write_result(log, f"{prefix}_{arm}_trades", script=SCRIPT, seed=int(cfg["seeds"]["gate"]),
                     exploratory=True, results_dir=results_dir, parameters=params_,
                     notes={"status": "EXPLORATORY: P-06's gate blocks re-presented for the Campaign Studio; the verdict "
                                      "is P-06's (D-361)"},
                     description=f"EXPLORATORY: FV3-C's confirmation campaign on NQ's held-back window, the {shift} arm, "
                                 "as a Campaign Studio trade log (the frozen cell's trades, the ladder's stops, every "
                                 "R's outcome as the state policy reads them, blank where the room permits no trade).")
        print(f"{prefix}_{arm}: {len(log)} trades; mean 1R {float(log['r_net_1'].mean()):.4f}")
    dayset = pd.DataFrame({"date": days, "entries": [len(b) for b in blocks],
                           "period": [period_of[label_of_day[d]] for d in days]})
    write_result(dayset, f"{prefix}_days", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, parameters={"rule": "every non-FOMC session of the held-back window the gate "
                                                               "laid a block on", "decision": "D-362",
                                                               "verdict": "results/fv3_confirmation.csv"},
                 notes={"status": "EXPLORATORY: P-06's gate day set, days without a trade included"},
                 description="EXPLORATORY: FV3-C's confirmation day set -- one row per window session.")
    print(f"day set: {len(days)} sessions, {int((dayset['entries'] == 0).sum())} without a trade")
    return 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--grid", default="fv3_grid", help="the screen result to export (fv3_grid, or fv3_grid_corrected)")
    ap.add_argument("--prefix", default=None, help="the result files' prefix (fv3_studio_gate_corrected for the corrected run)")
    ap.add_argument("--config", default=None, help="the declaration's config (config/fv3_grid.yaml; D-306: config/fv3_portfolio.yaml)")
    ap.add_argument("--confirmation", action="store_true",
                    help="D-362: export P-06's verdict campaign (results/fv3_confirmation.csv) instead of a development run")
    a = ap.parse_args()
    if a.confirmation:
        raise SystemExit(confirmation_main(prefix=a.prefix or "fv3_studio_confirmation"))
    raise SystemExit(main(grid_name=a.grid, prefix=a.prefix or "fv3_studio_gate", config_path=a.config))
