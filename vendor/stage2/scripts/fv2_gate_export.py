"""EXPLORATORY (D-288): the campaign FV2's verdict was read from -- the D-145 gate's own day blocks -- as Campaign Studio
trade logs, so the operator can replay it and look for errors (the operator, 2026-10-05: "give me the final run that
you made the "failed" decesion from I want to visualise it and see if there are any errors"; the Studio is an
inspection view, never a verdict -- D-155's step 7).

    python scripts/fv2_gate_export.py

It rebuilds the gate exactly as `scripts/score_fv2_grid.py` built it, from the same records and seeds:

* **the trades** (`gate_trades`): each test year 2013 to June 2025 traded by the configuration the walk-forward selected
  on the years before it (results/fv2_grid.csv, `walkforward` -- not the final selection), both legs, each at its move
  less its cell's median cost of 2020 to June 2025, kept one at a time by the later of the two legs' exits;
* **the stops** (`gate_blocks`): each trade paired with a stop drawn (seed `stops`) from 2020 to June 2025's session
  stops in its cell's sessions, and left out unless sizeable at the Combine's and the funded risk; the MAE at the stop
  for every trade (D-284, the verdict's reading);
* **the day set**: every non-FOMC session of the test years, days without a trade included.

Every block is checked equal to the scorer's own `gate_blocks` output, and the edge and bound to results/fv2_grid.csv's
`gate_inputs`, before anything is written. Two logs:

* `fv2_gate_point` -- the outcomes as traded: the gate's `point` arm;
* `fv2_gate_verdict` -- every outcome shifted down to its leg's one-sided 95 % lower bound (`gate.shifted_blocks`): the
  arm the verdict was read on (`is_gate_row`, 0 % denial, D-234).

A Studio run of each at the manifest's `mirror` (the gate's campaign, policy and seed) should reproduce that arm's row
at 0 % denial in results/fv2_grid.csv; the Studio replays outcomes as they are, so the verdict arm needs its own log.

Each trade is one micro (MNQ): `dollars_risked` its drawn stop's risk per micro; `pnl_net` the block's own P&L (the
funded leg's net R times it), `pnl_gross` the same before the leg's median cost; `mae` the block's. The per-R columns
are exactly the outcomes the gate's policy reads: the Combine leg at `r_net_1.5` / `mae_r_1.5`, the funded leg at
`r_net_1.500001` / `mae_r_1.500001` -- the funded leg's outcome keyed by a label of its own
(`score_fv2_grid.FUNDED_KEY`) so the policy can tell the legs apart; the engine reads the key only to pick the series.
Times are bar starts: the entry at its bar's open (two minutes after the signal bar's close, D-282) and the exit at the
start of the bar it happened in, so the flat-account routing compares exactly the gate's bars (D-159). Prices are
constructed from the drawn stop (risk and P&L exact); `exit_reason` is the funded leg's. Beside the canonical columns,
each trade's session, configuration, signal time and both stops, for reading. It reads no new data and selects
nothing -- no new variant.

Writes results/fv2_studio_gate_point_trades.csv, results/fv2_studio_gate_verdict_trades.csv and
results/fv2_studio_gate_days.csv with manifests.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import orb_trades_export as ox  # noqa: E402
import score_fv2_grid as gf  # noqa: E402
import score_orb5_grid as g5  # noqa: E402

SCRIPT = "scripts/fv2_gate_export.py"
TICK_POINTS = 0.25                                   # MNQ's tick, in points


def rr_label(x: float) -> str:
    """A per-R column's label: 1.5 -> '1.5', 1.5 + 1e-6 -> '1.500001'."""
    return f"{x:.6f}".rstrip("0").rstrip(".")


def gate_rows(S: gf.Signals, ev: gf.EvaluatedFV, selections: dict, final: dict) -> pd.DataFrame:
    """`gf.gate_trades`, with what a reader needs beside it: the signal, its side, the funded leg's gross move, target
    and exit kind, the traded stop and the configuration (checked equal to `gate_trades` on its own columns)."""
    out = []
    for y, k in selections.items():
        if k is None:
            continue
        c = ev.cells[k]
        cand = S.candidates(c)
        legs = {}
        for leg in ("combine", "funded"):
            spec = gf.leg_spec(ev.cfg, ev.frisk, c, leg)
            o = S.outcome(spec[0], spec[1], spec[2], spec[3])
            legs[leg] = (o, S.today_cost(cand, spec[2], spec[3]))
        of = legs["funded"][0]
        kept = S.kept(cand, np.maximum(legs["combine"][0]["exit"], of["exit"])) & (S.year == y)
        key = gf._key(c)
        cfg_text = f"{key['sessions']} | {key['trigger']} | continuation {'on' if key['continuation'] else 'off'} | " \
                   f"Combine {key['combine']} | funded {key['funded_target']}"
        for i in np.nonzero(kept)[0]:
            row = {"date": S.df["date"].iat[i], "year": y, "sessions": c["sessions"], "entry_t": float(S.bar[i]),
                   "exit_t": float(of["exit"][i]), "flat_f": bool(of["flat"][i])}
            for leg, (o, tc) in legs.items():
                row[f"r_{leg[0]}"] = float(o["gross"][i] - tc)
                row[f"stopped_{leg[0]}"] = bool(o["stopped"][i])
            row.update({"dir": float(S.dir[i]), "session": str(S.session[i]), "signal_slot": int(S.slot[i]),
                        "gross_f": float(of["gross"][i]), "rr_f": float(of["rr"][i]),
                        "kind_f": "stop" if of["stopped"][i] else ("target" if of["target"][i] else "flatten"),
                        "stop_traded": float(S.st[i]), "config": cfg_text})
            out.append(row)
    return pd.DataFrame(out)


def drawn(t: pd.DataFrame, ses: pd.DataFrame, c_risk: float, frisk: float, band: pd.DataFrame, seed: int) -> pd.DataFrame:
    """`gf.gate_blocks`'s draw, kept per trade: the same seeded stops in the same order, the same stand-aside."""
    from orb5_prep import sizeable

    rng = np.random.default_rng(seed)
    cb = band[(band["state"] == "combine") & (band["market"] == "NQ")].iloc[0]
    fb = band[(band["state"] == "funded_below_2000") & (band["market"] == "NQ")].iloc[0]
    tv = float(cb["tick_value"])
    yr = pd.to_datetime(ses["date"]).dt.year
    pools: dict[tuple, np.ndarray] = {}
    st = np.empty(len(t))
    for n in range(len(t)):
        key = tuple(t["sessions"].iat[n])
        if key not in pools:
            pools[key] = ses[(yr >= gf.TODAY_FROM) & (ses["present"] == 1)
                             & ses["session"].isin(key)]["stop_ticks"].to_numpy(float)
        st[n] = float(rng.choice(pools[key]))
    ok = (sizeable(st, c_risk, int(cb["cap_micros"]), tv, int(cb["cost_drag_floor_ticks"]))
          & sizeable(st, frisk, int(fb["cap_micros"]), tv, int(fb["cost_drag_floor_ticks"])))
    return t.assign(stop_drawn=st, rpc=st * tv)[ok]


def ordered(td: pd.DataFrame, days: list[str]) -> list[pd.DataFrame | None]:
    """The trades of each day of `days` in the gate's block order (entry time, stable)."""
    by = {d: g.sort_values("entry_t", kind="stable") for d, g in td.groupby("date")} if len(td) else {}
    return [by.get(d) for d in days]


def check_blocks(rows: list, blocks: list, ckey: float, fkey: float) -> None:
    """Each day's rows against the scorer's block: same trades, same order, same values."""
    if len(rows) != len(blocks):
        raise SystemExit("REFUSED: the day set differs from the gate's.")
    for g, b in zip(rows, blocks):
        n = 0 if g is None else len(g)
        if n != len(b):
            raise SystemExit("REFUSED: a day's trades differ from the gate's block.")
        if not n:
            continue
        for mine, theirs in ((g["rpc"], b.risked), (g["entry_t"], b.entry_t), (g["exit_t"], b.exit_t),
                             (g["r_c"], b.r_by_rr[ckey]), (g["r_f"], b.r_by_rr[fkey]), (g["r_f"] * g["rpc"], b.pnl)):
            if not np.allclose(np.asarray(mine, float), np.asarray(theirs, float), rtol=0, atol=1e-9):
                raise SystemExit("REFUSED: a trade's values differ from the gate's block.")


def trade_log(rows: list, blocks: list, days: list[str], ckey: float, fkey: float) -> pd.DataFrame:
    """The Studio log of one arm's blocks (point or shifted), the rows giving each trade's side and reading."""
    cl, fl = rr_label(ckey), rr_label(fkey)
    out = []
    for d, g, b in zip(days, rows, blocks):
        if g is None or not len(b):
            continue
        for j, (_, r) in enumerate(g.iterrows()):
            side = 1.0 if r["dir"] > 0 else -1.0
            rpc, st = float(b.risked[j]), float(r["stop_drawn"])
            rf = float(b.r_by_rr[fkey][j])
            cost_f = float(r["gross_f"] - r["r_f"])                         # the leg's median cost, in R
            out.append({
                "timestamp_in": ox.stamp(d, int(r["entry_t"]) - 1),
                "timestamp_out": ox.stamp(d, int(r["exit_t"]) - 1),
                "symbol": "MNQ", "side": "long" if side > 0 else "short",
                "entry_price": ox.NOMINAL_ENTRY,
                "exit_price": ox.NOMINAL_ENTRY + side * (rf + cost_f) * st * TICK_POINTS,
                "stop": ox.NOMINAL_ENTRY - side * st * TICK_POINTS,
                "target": ox.NOMINAL_ENTRY + side * float(r["rr_f"]) * st * TICK_POINTS,
                "contracts": 1,
                "pnl_gross": float(b.pnl[j]) + cost_f * rpc,
                "pnl_net": float(b.pnl[j]),
                "exit_reason": r["kind_f"],
                "dollars_risked": rpc,
                "mae": float(b.mae[j]),
                f"r_net_{cl}": float(b.r_by_rr[ckey][j]), f"mae_r_{cl}": float(b.mae_by_rr[ckey][j]),
                f"r_net_{fl}": rf, f"mae_r_{fl}": float(b.mae_by_rr[fkey][j]),
                "fv2_session": r["session"], "fv2_config": r["config"],
                "signal_time": ox.stamp(d, int(r["signal_slot"])),
                "stop_ticks_traded": float(r["stop_traded"]), "stop_ticks_drawn": st,
            })
    log = pd.DataFrame(out)
    if not np.allclose(log["pnl_net"] / log["dollars_risked"], log[f"r_net_{fl}"], atol=1e-9):
        raise SystemExit("REFUSED: the log's own outcome is not the funded leg's.")
    return log


def main(results_dir: Path | None = None, runs_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.campaign.gate import shifted_blocks
    from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result
    from propedge.research.model_card import BAND_FILE, setups_minimum

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = gf.config()
    grid = read_result(rd / "fv2_grid.csv")
    need = {(float(c["rr"]), float(c["risk"])): float(setups_minimum(float(c["rr"]), float(c["risk"]), 0.0))
            for c in cfg["search"]["combine"]}
    sig, ses, _, sessions = gf.load(rd, Path(runs_dir) if runs_dir is not None else ROOT / "runs", cfg)
    fm = FillModel.load("assumed")
    q = params("NQ")
    S = gf.Signals(sig, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]),
                   q["micro_tick"] * q["micro_point_value"])
    band = read_result(BAND_FILE)
    print("evaluating the grid (the scorer's own selection)...")
    ev = gf.EvaluatedFV(S, ses, cfg, sessions, band, need)
    years = list(ev.years)
    sels = {T: ev.select(ev.years < T)[0] for T in years if T >= gf.WF_FIRST}
    kf, _ = ev.select(np.ones(len(years), bool))
    final = ev.cells[kf]
    frisk = float(ev.frisk[tuple(final["sessions"])])
    ckey, fkey = final["combine"]["rr"], gf.FUNDED_KEY[final["funded_target"]]
    c_risk = float(final["combine"]["risk"])

    t = gf.gate_trades(S, ev, sels, final)
    mine = gate_rows(S, ev, sels, final)
    if not mine[t.columns].reset_index(drop=True).equals(t.reset_index(drop=True)):
        raise SystemExit("REFUSED: the trades differ from the scorer's gate_trades.")
    stats = {}
    for leg, col in (("combine", "r_c"), ("funded", "r_f")):
        stats[leg] = {"e": float(t[col].mean()), "lb": g5.bound(t.groupby("year")[col].mean())}
    gi = grid[grid["section"] == "gate_inputs"].iloc[0]
    for leg in ("combine", "funded"):
        for x in ("e", "lb"):
            if not np.isclose(stats[leg][x], float(gi[f"{x}_{leg}"]), rtol=0, atol=1e-9):
                raise SystemExit(f"REFUSED: {x} of the {leg} leg differs from results/fv2_grid.csv.")
    days = sorted(d for d in set(ses["date"]) if int(d[:4]) >= gf.WF_FIRST)
    seed_stops = int(cfg["seeds"]["stops"])
    blocks, n_used = gf.gate_blocks(t, ses, days, c_risk, frisk, ckey, fkey, band, seed_stops, mae_unstopped=1.0)
    if n_used != int(gi["trades_used"]):
        raise SystemExit("REFUSED: the trades used differ from results/fv2_grid.csv.")
    rows = ordered(drawn(mine, ses, c_risk, frisk, band, seed_stops), days)
    check_blocks(rows, blocks, ckey, fkey)
    e_by = {ckey: stats["combine"]["e"], fkey: stats["funded"]["e"]}
    lb_by = {ckey: stats["combine"]["lb"], fkey: stats["funded"]["lb"]}
    shifted = shifted_blocks(blocks, lb_by[fkey] - e_by[fkey], {k: lb_by[k] - e_by[k] for k in e_by})

    camp = cfg["gate"]["campaign"]
    fkey_studio = float(rr_label(fkey))
    policy = RiskPolicy(id="fv2_gate", description="FV2's gate policy (scripts/score_fv2_grid.py run_gate)", root=Phase(
        combine=Leaf(f"combine {ckey:g}:1 ${c_risk:,.0f}", risk=c_risk, rr=ckey, max_trades=1),
        funded=Leaf(f"funded {final['funded_target']} ${frisk:,.0f}", risk=frisk, rr=fkey_studio, max_trades=1)))
    gate_rows_csv = grid[grid["section"] == "gate"]
    for arm, blk, shift in (("point", blocks, "point"), ("verdict", shifted, "lower_bound")):
        log = trade_log(rows, blk, days, ckey, fkey)
        want = gate_rows_csv[(gate_rows_csv["shift"] == shift) & (gate_rows_csv["enforcement_p"].astype(float) == 0.0)]
        if not np.isclose(float((log["pnl_net"] / log["dollars_risked"]).mean()), float(want["mean_r_used"].iloc[0]),
                          rtol=0, atol=1e-9):
            raise SystemExit(f"REFUSED: the {arm} log's mean R differs from the gate's {shift} row.")
        mirror = {"reproduces": f"results/fv2_grid.csv, section gate, shift {shift}, enforcement_p 0"
                                + (" -- the verdict's row (is_gate_row)" if shift == "lower_bound" else ""),
                  "allocation": camp["mode"], "accounts": int(camp["accounts"]), "bankroll": float(camp["bankroll"]),
                  "combine_rr": float(ckey), "combine_risk": c_risk, "funded_rr": fkey_studio, "funded_risk": frisk,
                  "payout_path": "standard", "sizing_mode": camp["sizing"], "headroom": float(camp["headroom"]),
                  "payout_method": camp["payout_method"], "max_concurrent_combines": int(camp["combines"]),
                  "max_total_accounts": int(camp["accounts"]), "enforcement_p": 0.0, "rtp": True,
                  "resample_paths": int(camp["n_paths"]), "resample_horizon_days": int(camp["horizon_days"]),
                  "seed": int(cfg["seeds"]["gate"]), "settlement": camp["settlement"],
                  "risk_policy": policy.as_dict()}
        params_ = {"arm": arm, "shift": shift, "seed_stops": seed_stops, "mae_unstopped": "the stop (D-284)",
                   "e_by_leg": {"combine": e_by[ckey], "funded": e_by[fkey]},
                   "lb_by_leg": {"combine": lb_by[ckey], "funded": lb_by[fkey]},
                   "walkforward": "results/fv2_grid.csv, walkforward", "mirror": mirror, "decision": "D-288"}
        write_result(log, f"fv2_studio_gate_{arm}_trades", script=SCRIPT, seed=seed_stops, exploratory=True,
                     results_dir=results_dir, parameters=params_,
                     notes={"status": "EXPLORATORY: the gate's own blocks re-presented for the Campaign Studio; the "
                                      "verdict is D-286's"},
                     description=f"EXPLORATORY: FV2's gate campaign, the {shift} arm, as a Campaign Studio trade log "
                                 "(the walk-forward's out-of-sample trades, the drawn stops, both legs' outcomes as the "
                                 "gate's policy reads them).")
        print(f"fv2_studio_gate_{arm}: {len(log)} trades; mean R {log['pnl_net'].sum() / log['dollars_risked'].sum():.4f} "
              f"(dollar-weighted); {log['exit_reason'].value_counts().to_dict()}")
    counts = pd.Series([0 if g is None else len(g) for g in rows], index=days)
    dayset = pd.DataFrame({"date": days, "entries": counts.to_numpy(int)})
    write_result(dayset, "fv2_studio_gate_days", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, parameters={"rule": "every non-FOMC session of the test years (the gate's "
                                                               "day blocks)", "decision": "D-288"},
                 notes={"status": "EXPLORATORY: the gate's day set, days without a trade included"},
                 description="EXPLORATORY: FV2's gate day set -- one row per session the gate laid a block on.")
    print(f"day set: {len(days)} sessions, {int((dayset['entries'] == 0).sum())} without a trade; busiest day "
          f"{int(dayset['entries'].max())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
