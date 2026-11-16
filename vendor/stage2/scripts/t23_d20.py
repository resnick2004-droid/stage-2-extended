"""T23-D20 (D-418): the captured trades of d20's six fixed times through five accounts, strictly one trade at a time,
under the firm's rules, judged by the D-145 gate at the bound.

    python scripts/t23_d20.py --stop-distribution        # the card's stop distribution (no campaign)
    python scripts/t23_d20.py --prereg P-xx              # the registered test; refused without a runnable id

The protocol, frozen as D-416's rule chose it (D-417): at 19:00, 03:00, 08:00, 09:00, 10:00 and 12:00 CT a market entry
two bars after the time on A3's side (no trade on a zero or missing sign); the 20-point stop; the Combine the 1:1
bracket at $1,400, a funded account at or below its start the 1.5:1 bracket at $800, above it the 1:1 bracket at $200
(the flip). A fixed time's trade is taken only when the previous trade taken, read at the slower of its two possible
brackets, ended at least five minutes before (D-160): no two accounts ever hold positions at once.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/t23_d20.py"
DECISION = "D-418"
SCHEDULE = ("19:00", "03:00", "08:00", "09:00", "10:00", "12:00")
DELAY = 2
STOP_POINTS, TICK, MPV = 20.0, 0.25, 2.0
STOP_TICKS = int(round(STOP_POINTS / TICK))                # 80 micro ticks
BRACKETS = {1.0: (20.0, 20.0), 1.5: (30.0, 20.0)}           # R: (target, stop) in points
GAP_MIN = 5                                                 # D-160's flat gap
LEGS = {"combine": (1400.0, 1.0), "big": (800.0, 1.5), "flip": (200.0, 1.0)}
MAX_TRADES = 2                                              # an account's trades a session at most
SEED = 20261019
N_PATHS, HORIZON, ACCOUNTS = 500, 504, 5
LEVELS = (0.0, 0.10, 0.25, 0.50)
MARGIN, BLOCK = 49.0, 21
CHECK = ("2024-01-01", "2025-06-30")
K, WINDOW = 4, ("2020-01-01", "2025-06-30")                 # the registration's k and development period (D-419)
ERAS = ((2020, 2022), (2023, 2025))                         # the card's per-era report (D-271)
SEED_BOOT, REPS = 20261017, 2000                            # the eras' whole-year bootstrap and the day bootstrap
REPLICATION_SEED = 20261024                                 # D-423: the failure protocol's replication, fixed first


def chosen_schedule(rd: Path) -> tuple[str, ...]:
    """d20's schedule as the chooser recorded it (`results/t23_choice.csv`); refused if it is not SCHEDULE."""
    from propedge.reporting.results import read_result

    ch = read_result(rd / "t23_choice.csv")
    v = ch[ch["section"] == "verdict"].iloc[0]
    c = ch[(ch["section"] == "config") & (ch["config"].astype(str) == "d20")].iloc[0]
    if str(v["verdict"]) != "d20" or tuple(str(c["schedule"]).split()) != SCHEDULE:
        raise SystemExit("REFUSED: results/t23_choice.csv does not hold d20 with the frozen schedule (D-417).")
    return SCHEDULE


def strict(t: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """D-418 (3): per day in entry order, a trade kept only when the previous kept trade's slower exit (the larger of
    its exits at R 1 and R 1.5) is at least GAP_MIN minutes before its entry. Returns (kept, skipped)."""
    keep, skipped = [], 0
    for _, g in t.sort_values(["date", "entry_t"], kind="stable").groupby("date", sort=False):
        free = -np.inf
        for i, r in g.iterrows():
            if r["entry_t"] >= free + GAP_MIN:
                keep.append(i)
                free = max(r["exit_t_1"], r["exit_t_1.5"])
            else:
                skipped += 1
    return t.loc[keep].sort_values(["date", "entry_t"], kind="stable").reset_index(drop=True), skipped


def trades(rd: Path) -> tuple[pd.DataFrame, list[str], int]:
    """The protocol's trades from the captures: the schedule's walks two bars late on A3's side, each with its net R,
    outcome and exit time at R 1 and 1.5 (the collect map's costs, D-416 (6)); the strict filter; the day set."""
    import t23_choose as tc

    from propedge.data import t23_kit as tk
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result

    cfg = tk.config_t23()
    q = tk.params_t23(str(cfg["runs"][0]["run"]), cfg)
    slots, labels = q["slots"], q["slot_labels"]
    bix = tc.bracket_index(cfg)
    walks, days = tc.load(rd)
    sched = [slots[labels.index(x)] for x in chosen_schedule(rd)]
    base = walks[(walks["delay"].astype(int) == DELAY) & walks["decision_slot_minutes"].astype(int).isin(sched)].copy()
    base["a3"] = tc.sides(base, days, slots, "a3")
    t = base[(base["side"].astype(int) == base["a3"]) & (base["a3"] != 0)].copy()
    sp = read_result(rd / Path(tc.R137).name)
    sp = sp[sp["kind"] == "spread"]
    spread = {(str(r.decision_ct), int(r.year)): float(r.spread_ticks_mean) for r in sp.itertuples() if float(r.quotes) > 0}
    fee = float(FillModel.load("assumed").round_turn_by_instrument[str(cfg["contract"]["micro"])])
    t["entry_t"] = t["entry_slot"].astype(float)
    for R, (T, S) in BRACKETS.items():
        b = bix[(T, S)]
        t[f"r_{R:g}"] = tc.trade_r(t, b, T, S, spread, fee)
        t[f"g_{R:g}"], t[f"c_{R:g}"] = tc.trade_parts(t, b, T, S, spread, fee)     # D-419: gross and cost in R
        t[f"o_{R:g}"] = t[f"o{b}"].astype(str)
        t[f"exit_t_{R:g}"] = t["entry_t"] + t[f"m{b}"].astype(float)
        t[f"mae_{R:g}"] = np.nan                                 # not captured: the room cap keeps every trade inside it
    t["exit_t"] = t["exit_t_1.5"]
    t["flat"] = t["o_1.5"] == "f"
    t["stop_ticks"] = STOP_TICKS
    t["side"] = np.where(t["side"].astype(int) > 0, "long", "short")
    t["date"] = t["date"].astype(str)
    kept, skipped = strict(t[["date", "year", "decision_ct", "entry_t", "exit_t", "side", "stop_ticks", "flat",
                              *[c for R in BRACKETS for c in (f"r_{R:g}", f"g_{R:g}", f"c_{R:g}", f"o_{R:g}",
                                                              f"exit_t_{R:g}", f"mae_{R:g}")]]])
    day_set = sorted(days["date"].astype(str))
    return kept, day_set, skipped


def stop_distribution(t: pd.DataFrame) -> pd.DataFrame:
    """The card's stops (D-191, D-212): one row per trade and state -- its stop in micro ticks, the exit its state's
    bracket took (the Combine and the flip the 1:1, the big funded trade the 1.5:1) and its date."""
    kinds = {"t": "target", "s": "stop", "f": "flatten"}
    rows = []
    for state, R in (("combine", 1.0), ("funded", 1.5)):
        rows.append(pd.DataFrame({"market": "NQ", "stop_ticks": t["stop_ticks"].astype(int), "state": state,
                                  "exit": t[f"o_{R:g}"].map(kinds), "date": t["date"]}))
    return pd.concat(rows, ignore_index=True)


def policy():
    """D-418 (2): the phase and balance tree -- the Combine 1:1 $1,400; funded at or below the start 1.5:1 $800, above
    it the 1:1 $200 flip."""
    from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy, Tiers

    (cr, cR), (br, bR), (fr, fR) = LEGS["combine"], LEGS["big"], LEGS["flip"]
    root = Phase(combine=Leaf("combine 1:1", cr, cR, max_trades=MAX_TRADES),
                 funded=Tiers(on="balance", name="the start",
                              tiers=((-1e12, Leaf("big 1.5:1", br, bR, max_trades=MAX_TRADES)),
                                     (0.01, Leaf("flip 1:1", fr, fR, max_trades=MAX_TRADES)))))
    p = RiskPolicy(id="t23_d20", root=root, description="T23-D20 (D-418): big trade first, then flips")
    p.validate()
    return p


def protocol():
    from propedge.campaign.protocols import Protocol

    return Protocol(name="t23_d20", combine_rr=1.0, combine_risk=LEGS["combine"][0], funded_rr=1.5,
                    # D-422: the day log's capacity (the schedule's six); each account's two a session is the policy's
                    # `max_trades` (D-162's `session_slots`)
                    funded_risk=LEGS["big"][0], trades_per_day=len(SCHEDULE), payout_path="standard", keep_balance=0.0,
                    payout_frac=1.0, max_concurrent_accounts=ACCOUNTS, family="t23", source="config/t23_capture.yaml",
                    note="D-418", params={"seat_frees": "same_evening"})


def sizing():
    from dataclasses import replace

    from propedge.campaign.sizing import CURRENT_TIER, SizingRule

    return replace(SizingRule.from_ledger(CURRENT_TIER, headroom_frac=1.0), room_cap=("combine", "funded"))


def period_rows(t: pd.DataFrame, days: list[str], menu: list[float], n_led: int) -> list[dict]:
    """D-419 (the card's per-era report and the cost drag): per period and R, e and its bounds over 21-session blocks
    at 0.05 and 0.05/N, the gross R, the cost in R and the net -- gross less cost checked equal to the net -- the target
    share and trades a day."""
    import confirm_fv3 as cf
    import fv3d_lever_test as lt

    periods = {"all": WINDOW, **{f"{a}-{b}": (f"{a}-01-01", f"{b}-12-31") for a, b in ERAS}, "check": CHECK}
    rows = []
    for name, (lo, hi) in periods.items():
        tp, dp = lt.in_period(t, days, lo, hi)
        st = cf.edge_stats(tp, menu, dp, BLOCK, n_led)
        for R in menu:
            g, c, r = (tp[f"{x}_{R:g}"].astype(float) for x in ("g", "c", "r"))
            if len(tp) and not np.allclose(g - c, r, atol=1e-9):
                raise SystemExit(f"REFUSED: gross less cost is not the net at R {R:g} ({name}).")
            rows.append({"section": "period", "period": name, "rr": R, "e": st[R]["e"], "lb": st[R]["lb"],
                         "lb_at_ledger_n": st[R]["lb_at_n"], "blocks": st[R]["blocks"], "n": st[R]["n"],
                         "gross_r": float(g.mean()) if len(tp) else np.nan,
                         "cost_r": float(c.mean()) if len(tp) else np.nan,
                         "net_r": float(r.mean()) if len(tp) else np.nan,
                         "target_share": float((tp[f"o_{R:g}"] == "t").mean()) if len(tp) else np.nan,
                         "trades_per_day": len(tp) / len(dp) if dp else np.nan, "days": len(dp)})
    return rows


def eras(t: pd.DataFrame, days: list[str], menu: list[float], n_led: int, *, reps: int = REPS,
         seed: int = SEED_BOOT) -> tuple[list[dict], bool, dict, dict]:
    """The card's rule (D-271): per R, the difference in the two eras' mean gross R from a bootstrap resampling whole
    years within each era; the eras flagged when either R's 95 % interval excludes zero. Returns (rows, flagged, each R's
    lower era bound at 0.05, at 0.05/N) -- the bounds the gate reads when flagged, never the pooled ones."""
    import confirm_fv3 as cf
    import fv3d_lever_test as lt

    rng = np.random.default_rng(seed)
    yr = t["date"].astype(str).str[:4].astype(int)
    split = [lt.in_period(t, days, f"{a}-01-01", f"{b}-12-31") for a, b in ERAS]
    rows, flagged, low, low_n = [], False, {}, {}
    for R in menu:
        g = t[f"g_{R:g}"].astype(float)
        by_year = {int(y): (float(g[yr == y].sum()), int((yr == y).sum())) for y in sorted(yr.unique())}
        pools = [[y for y in by_year if a <= y <= b] for a, b in ERAS]
        diffs = np.empty(reps)
        for i in range(reps):
            m = []
            for pool in pools:
                pick = rng.choice(pool, size=len(pool), replace=True)
                m.append(sum(by_year[int(y)][0] for y in pick) / max(sum(by_year[int(y)][1] for y in pick), 1))
            diffs[i] = m[1] - m[0]
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        fl = bool(lo > 0 or hi < 0)
        flagged |= fl
        st = [cf.edge_stats(te, [R], de, BLOCK, n_led)[float(R)] for te, de in split]
        low[float(R)], low_n[float(R)] = min(s["lb"] for s in st), min(s["lb_at_n"] for s in st)
        rows.append({"section": "eras", "rr": R, "diff_lo": float(lo), "diff_hi": float(hi), "flagged": fl,
                     "era1_lb": st[0]["lb"], "era2_lb": st[1]["lb"], "era1_lb_at_ledger_n": st[0]["lb_at_n"],
                     "era2_lb_at_ledger_n": st[1]["lb_at_n"], "seed": seed, "reps": reps})
    return rows, flagged, low, low_n


def sharpe_rows(t: pd.DataFrame, days: list[str], menu: list[float], n_led: int) -> list[dict]:
    """Beside the verdict (D-189, the template): per R, the deflated Sharpe ratio of the 21-session block means at the
    ledger's N, and `haircut.widened`'s day-bootstrap and normal bounds at 0.05/N (the deciding bound stays P-06's
    21-session t-bound, D-237 (4), D-418 (6))."""
    import confirm_fv3 as cf

    from propedge.research.haircut import deflated_sharpe, widened

    blk = cf.block_of(t["date"], days, BLOCK)
    pos = {d: i for i, d in enumerate(days)}
    idx = t["date"].astype(str).map(pos).to_numpy(int)
    rows = []
    for R in menu:
        r = t[f"r_{R:g}"].astype(float)
        d = deflated_sharpe(r.groupby(blk).mean().dropna().to_numpy(), int(n_led))
        w = widened(r.to_numpy(), idx, len(days), int(n_led), block=BLOCK, reps=REPS, seed=SEED_BOOT)
        rows.append({"section": "sharpe", "rr": R, "block_sr": d["sr"], "block_T": d["T"], "block_sr0": d["sr0"],
                     "deflated_sharpe_blocks": d["dsr"], "lb_bootstrap_widened": w["lb_bootstrap_widened"],
                     "lb_normal_widened": w["lb_normal_widened"], "lb_widened": w["lb_widened"],
                     "deflated_sharpe_daily": w["daily_dsr"], "ledger_n": int(n_led)})
    return rows


def verdict_of(g: float, g_n: float) -> str:
    """D-419: PASS -- the gate's growth above zero at e's bound at 0.05/N (D-189, D-230); CONTINUE -- above zero only at
    the one-sided 95 % bound, exploratory, to one confirmation on unread data; FAIL -- not above zero at 95 %."""
    if g_n > 0 and g > 0:
        return "PASS"
    return "CONTINUE" if g > 0 else "FAIL"


def run(blocks, e_by, lb_by, hook, *, rtp: bool, levels=LEVELS, seed: int = SEED) -> pd.DataFrame:
    import score_fv3_grid as gf

    from propedge.campaign import gate
    from propedge.campaign.payout_method import rules_for_method

    df, _ = gate.run_gate(list(blocks), e=e_by[1.5], lb=lb_by[1.5], protocol=protocol(), bankroll=gf.UNBOUND_BANKROLL,
                          horizon_days=HORIZON, n_paths=N_PATHS, seed=seed, accounts=ACCOUNTS, sizing=sizing(),
                          rules=rules_for_method("aeropay"), mode="rotation", settlement="pessimistic",
                          combines=ACCOUNTS, total_accounts=ACCOUNTS, risk_policy=policy(), e_by_rr=e_by, lb_by_rr=lb_by,
                          levels=tuple(levels), path_hook=hook, rtp=rtp, routing="able", cross_account=True,
                          hold_to_own_exit=True)
    df["placement"] = "on" if rtp else "off"
    return df


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stop-distribution", action="store_true")
    ap.add_argument("--prereg", default=None)
    ap.add_argument("--replicate", action="store_true", help="D-423: the failure protocol's replication (exploratory)")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if a.replicate:
        return _replicate(rd, results_dir)
    if a.stop_distribution:
        t, days, skipped = trades(rd)
        write_result(stop_distribution(t), "t23_d20_stop_distribution", script=SCRIPT, seed=None, require_seed=False,
                     exploratory=True, results_dir=results_dir,
                     parameters={"decision": DECISION, "schedule": list(SCHEDULE), "delay_bars": DELAY,
                                 "stop_ticks": STOP_TICKS, "brackets": {str(k): list(v) for k, v in BRACKETS.items()},
                                 "gap_minutes": GAP_MIN, "skipped": skipped, "trades": len(t)},
                     notes={"status": "the card's stop distribution (D-418 (7)); no campaign",
                            "seed": "none: a reading of the captures"},
                     description="T23-D20's stops (D-418 (7)): one row per scheduled trade after the strict filter and "
                                 "state, its stop in micro ticks, the exit its state's bracket took and its date.")
        print(f"stop distribution: {len(t)} trades, {skipped} skipped by the strict filter")
        return 0
    from propedge.backtest.harness import PreregRegistry, UnregisteredRunError

    try:
        PreregRegistry.load().require_runnable(a.prereg)
    except UnregisteredRunError as exc:
        print(f"REFUSED (D-418): {exc}")
        return 2
    return _registered_run(a.prereg, rd, results_dir)


def _inputs(rd: Path) -> dict:
    """The registered run's inputs (D-418, D-419): the trades, the ledger's N, each R's edge and bounds, the era rule's
    reading and the bounds the gate reads, the day blocks and the path hook."""
    import confirm_fv3 as cf
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import score_fv3_grid as gf

    from propedge.research import ledger as lg

    t, days, skipped = trades(rd)
    tv = TICK * MPV
    menu = sorted(BRACKETS)
    # D-419: e's bound at one-sided 0.05/N (D-189, the ledger's N) binds the verdict; 0.05/k beside
    n_led = lg.count_n(lg.load_ledger(), model="T23-D20", k=K, markets=["NQ"], window=WINDOW)["N"]
    stats = cf.edge_stats(t, menu, days, BLOCK, n_led)
    by_k = cf.edge_stats(t, menu, days, BLOCK, K)
    # the card's era rule (D-271): when the eras are flagged, every bound the gate reads is the lower era's
    era_rows, flagged, low, low_n = eras(t, days, menu, n_led)
    blocks, n_used = gf.gate_blocks(t, days, tv, menu, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    return {"t": t, "days": days, "skipped": skipped, "menu": menu, "n_led": n_led, "stats": stats, "by_k": by_k,
            "era_rows": era_rows, "flagged": flagged, "e_by": ps._by(stats, "e"),
            "lb_by": low if flagged else ps._by(stats, "lb"), "lbn_by": low_n if flagged else ps._by(stats, "lb_at_n"),
            "blocks": blocks, "hook": lt.lever_hook(ps.composed_hook({"margin": MARGIN, "block_days": BLOCK}))}


def _replicate(rd: Path, results_dir: Path | None) -> int:
    """D-423 (the failure protocol's last step): P-07's two deciding arms -- each R's bound at 0.05 and at 0.05/N, 0 %
    denial, the placement off -- again on REPLICATION_SEED, fixed in D-423 before this ran; exploratory, never the
    verdict, which stands as P-07 recorded it."""
    from propedge.reporting.results import read_result, write_result

    v = read_result(rd / "t23_d20_gate.csv")
    v = v[v["section"] == "verdict"].iloc[0]
    if str(v["prereg"]) != "P-07":
        raise SystemExit("REFUSED: results/t23_d20_gate.csv does not hold P-07's verdict.")
    x = _inputs(rd)
    out = []
    for name, lb in (("gate", x["lb_by"]), ("gate_at_ledger_n", x["lbn_by"])):
        df = run(x["blocks"], x["e_by"], lb, x["hook"], rtp=False, levels=(0.0,), seed=REPLICATION_SEED)
        df.insert(0, "section", name)
        out.append(df if name == "gate" else df[df["shift"] == "lower_bound"])
    res = pd.concat(out, ignore_index=True)
    g = float(res[(res["section"] == "gate") & (res["shift"] == "lower_bound")].iloc[0]["pf_growth_on_base_p50"])
    g_n = float(res[res["section"] == "gate_at_ledger_n"].iloc[0]["pf_growth_on_base_p50"])
    res = pd.concat([res, pd.DataFrame([{"section": "replication", "prereg": "P-07", "verdict_recorded": str(v["verdict"]),
                                         "verdict_on_this_seed": verdict_of(g, g_n), "gate_growth_on_base_p50": g,
                                         "gate_at_ledger_n_growth_on_base_p50": g_n}])], ignore_index=True)
    write_result(res, "t23_d20_replication", script=SCRIPT, seed=REPLICATION_SEED, exploratory=True,
                 results_dir=results_dir,
                 parameters={"decision": "D-423", "prereg": "P-07", "seed": REPLICATION_SEED, "n_paths": N_PATHS,
                             "horizon": HORIZON, "levels": [0.0], "arms": ["0.05", "0.05/N"]},
                 notes={"status": "the failure protocol's replication of P-07's deciding arms (D-423); exploratory, "
                                  "never the verdict"},
                 description="T23-D20's P-07 deciding arms again on a seed fixed before the run (D-423): the gate at 0 % "
                             "denial, the placement off, at each R's bound at 0.05 and at 0.05/N.")
    print(f"REPLICATION (D-423, seed {REPLICATION_SEED}): {verdict_of(g, g_n)} -- {g:+.4f} at the 95 % bound, "
          f"{g_n:+.4f} at 0.05/N (P-07 recorded {v['verdict']})")
    return 0


def _registered_run(pid: str, rd: Path, results_dir: Path | None) -> int:
    import confirm_fv3 as cf
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import score_fv3_grid as gf

    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    x = _inputs(rd)
    t, days, skipped, menu, n_led, stats, by_k = x["t"], x["days"], x["skipped"], x["menu"], x["n_led"], x["stats"], x["by_k"]
    era_rows, flagged, e_by, lb_by, lbn_by = x["era_rows"], x["flagged"], x["e_by"], x["lb_by"], x["lbn_by"]
    blocks, hook, tv = x["blocks"], x["hook"], TICK * MPV
    gate_df = run(blocks, e_by, lb_by, hook, rtp=False)
    gate_df.insert(0, "section", "gate")
    # D-419 (D-189, D-230): a verdict read on development data is at e's bound at one-sided 0.05/N
    n_df = run(blocks, e_by, lbn_by, hook, rtp=False, levels=(0.0,))
    n_df = n_df[n_df["shift"] == "lower_bound"]
    n_df.insert(0, "section", "gate_at_ledger_n")
    on_df = run(blocks, e_by, lb_by, hook, rtp=True, levels=(0.0,))
    on_df.insert(0, "section", "placement_on")
    zero = {k: 0.0 for k in e_by}
    z_df = run(ps.zero_edge_blocks(blocks, e_by, 1.5), zero, zero, hook, rtp=False, levels=(0.0,))
    z_df = z_df[z_df["shift"] == "point"]
    z_df.insert(0, "section", "zero_edge_twin")
    tc_, dc = lt.in_period(t, days, *CHECK)
    st_c = cf.edge_stats(tc_, menu, dc, BLOCK, None)
    bc, _ = gf.gate_blocks(tc_, dc, tv, menu, require_sides=True, require_exits=True)
    c_df = run(bc, ps._by(st_c, "e"), ps._by(st_c, "lb"), hook, rtp=False, levels=(0.0,))
    c_df.insert(0, "section", "check_years")
    g_n = float(n_df.iloc[0]["pf_growth_on_base_p50"])
    row = gate_df[(gate_df["shift"] == "lower_bound") & np.isclose(gate_df["enforcement_p"].astype(float), 0.0)].iloc[0]
    g = float(row["pf_growth_on_base_p50"])
    word = verdict_of(g, g_n)
    edges = pd.DataFrame([{"section": "edge", "rr": R, "e": stats[R]["e"], "lb": stats[R]["lb"], "n": stats[R]["n"],
                           "sd": stats[R]["sd"], "lb_at_ledger_n": stats[R]["lb_at_n"], "ledger_n": n_led,
                           "lb_at_k": by_k[R]["lb_at_n"], "k": K, "lb_gate": lb_by[float(R)],
                           "lb_gate_at_ledger_n": lbn_by[float(R)],
                           "d47_met": bool(stats[R]["e"] >= 0.10 and stats[R]["lb"] >= 0.05)} for R in menu])
    verdict = pd.DataFrame([{"section": "verdict", "prereg": pid, "gate_growth_on_base_p50": g,
                             "gate_at_ledger_n_growth_on_base_p50": g_n, "verdict": word, "era_flagged": flagged,
                             "bounds_read": "the lower era's" if flagged else "pooled", "trades": len(t),
                             "skipped": skipped, "days": len(days)}])
    beside = pd.DataFrame(period_rows(t, days, menu, n_led) + era_rows + sharpe_rows(t, days, menu, n_led))
    res = pd.concat([gate_df, n_df, on_df, z_df, c_df, edges, beside, verdict], ignore_index=True)
    # D-424 (the audit's D1): the variant recorded first, so the manifest carries the id and the count
    counter = VariantCounter(path=rd / "variants.jsonl")
    counter.record(prereg_id=pid, seed=SEED, exploratory=False, params={"study": "T23-D20 gate", "decision": DECISION},
                   label=f"T23-D20's registered test ({pid})")
    write_result(res, "t23_d20_gate", script=SCRIPT, seed=SEED, exploratory=False, results_dir=results_dir,
                 prereg_id=pid, variant_count=counter.count(pid),
                 parameters={"decision": DECISION, "prereg": pid, "schedule": list(SCHEDULE), "delay_bars": DELAY,
                             "legs": {k: list(v) for k, v in LEGS.items()}, "gap_minutes": GAP_MIN,
                             "n_paths": N_PATHS, "horizon": HORIZON, "accounts": ACCOUNTS, "levels": list(LEVELS),
                             "bound_rule": "21-session blocks (P-06)", "check": list(CHECK), "k": K,
                             "window": list(WINDOW), "ledger_n": n_led, "eras": [list(x) for x in ERAS],
                             "seed_bootstrap": SEED_BOOT, "reps": REPS, "payout_method": "aeropay"},
                 notes={"status": f"the registered test of T23-D20 ({pid}, D-418, D-419)"},
                 description="T23-D20's registered test (D-418): the captured trades through five accounts, strictly one "
                             "at a time; the D-145 gate at the bound; the placement, the zero-edge twin and the CHECK "
                             "years beside.")
    print(f"VERDICT ({pid}): {word} -- the gate's growth on the required bankroll {g:+.4f} at the 95 % bound, "
          f"{g_n:+.4f} at 0.05/N")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
