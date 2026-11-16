"""T24 (D-429): the wide-bracket screen -- EXPLORATORY. Coin-flip trades from T24's capture (R149-R151, D-428), entered
five bars after each fixed time, at one stop width (20, 40 or 60 points) with targets at 1:1, 1.5:1, 2:1 and 3:1, through
five accounts under two sizing families and two routing rules, in the campaign engine at the point and at the bound.

    python scripts/t24_wide.py --identity          # first, and alone: the capture against R147/R148 (D-428 (4))
    python scripts/t24_wide.py --stop 40           # one width (20, 40, 60); refused until the identity holds

The families (D-429 (3)): `table` -- FV3-C's solver (D-329 to D-333) re-solved for this width's menu (one stop; R 1,
1.5, 2, 3; whole micros under the allowance; both legs may close the account), at the grid edge nearest the trades' lower
bound (FV3-C's convention, P-06); `two_shot` -- the operator's Combine (1:1 at $1,600, one a session, closed once the room
cannot carry another) with the table's funded and paid legs. The rules: `strict` -- the operator's R2, no trade while any
account holds a position or within five minutes of one closing (D-160, D-429); `firm` -- the firm's verified rule only, no
position opposite one open on any account (D-353). The kill line: a configuration continues if the campaign's median
growth on the required bankroll is above zero at each R's one-sided 95 % bound over 21-session blocks, 0 % denial, the
placement off.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/t24_wide.py"
DECISION = "D-429"
CAPTURES = ("results/manual_R149_t24_NQ_2021.csv", "results/manual_R150_t24_NQ_2023.csv",
            "results/manual_R151_t24_NQ_2025.csv")
T23_CAPTURES = ("results/manual_R147_t23_NQ_2022.csv", "results/manual_R148_t23_NQ_2025.csv")
COIN_SEED = 20261025                       # D-426's coin, one draw a (date, slot)
SEED = 20261027                            # the campaign's resampling
DELAY = 5                                  # the operator's entry for a coin side (D-428 (1))
STOPS = (20, 40, 60)
RRS = (1.0, 1.5, 2.0, 3.0)
GAP = 5.0                                  # D-160's flat gap, minutes
N_PATHS, HORIZON, ACCOUNTS = 500, 504, 5
MARGIN, BLOCK = 49.0, 21
FEE_MICRO, FEE_MINI = 1.22, 3.78           # config/fills.yaml `assumed` (the published schedule)
TWO_SHOT = 1600.0
GRID = (-0.05, -0.025, 0.0, 0.025, 0.05, 0.10)   # FV3-C's edge grid (config/state_policy_v12.yaml)
MICROS = (2, 4, 5, 10, 15, 20, 30, 40, 50)        # the menus' sizes in micros, each on the $50 grid
FAMILIES = ("table", "two_shot")
RULES = {"strict": GAP, "firm": None}
PARAMS = {"need_aware_exits": True, "consistency_cap_exits": True, "no_trade_standard_path_only": True,
          "decision_inputs_cents": True, "seat_frees": "same_evening"}   # FV3-C's fidelity switches (D-306 to D-353)


# ------------------------------------------------------------------------------------------------ the capture


def load(rd: Path, files=CAPTURES) -> tuple[pd.DataFrame, pd.DataFrame]:
    from propedge.reporting.results import read_result

    t = pd.concat([read_result(rd / Path(p).name) for p in files], ignore_index=True)
    walks = t[t["kind"] == "walk"].copy()
    days = t[t["kind"] == "day"].copy()
    walks["year"] = walks["date"].astype(str).str[:4].astype(int)
    return walks, days


def bracket_index(run: str) -> dict[tuple[float, float], int]:
    from propedge.data import t23_kit as tk

    return {(float(T), float(S)): i for i, (T, S) in enumerate(tk.params_t23(run)["brackets"])}


def identity(rd: Path) -> dict:
    """D-428 (4): the on-time walks of the four brackets both captures carry, walk for walk -- outcome, minutes, gap and
    end ticks -- against R147/R148."""
    from propedge.data import t23_kit as tk

    cfg = tk.config_for_run("R149-t24-NQ-2021")
    shared = [(float(T), float(S)) for T, S in cfg["identity"]["brackets"]]
    i24, i23 = bracket_index("R149-t24-NQ-2021"), bracket_index("R147-t23-NQ-2022")
    w24, _ = load(rd)
    w23, _ = load(rd, T23_CAPTURES)
    key = ["date", "decision_slot_minutes", "side"]
    a = w24[w24["delay"].astype(int) == int(cfg["identity"]["delay"])].copy()
    b = w23[w23["delay"].astype(int) == int(cfg["identity"]["delay"])].copy()
    for d in (a, b):
        d["date"] = d["date"].astype(str)
        d["decision_slot_minutes"] = d["decision_slot_minutes"].astype(int)
        d["side"] = d["side"].astype(int)
    m = a.merge(b, on=key, how="outer", suffixes=("_24", "_23"), indicator=True)
    only = int((m["_merge"] != "both").sum())
    both = m[m["_merge"] == "both"]
    diff = 0
    for br in shared:
        for f in ("o", "m", "g", "x"):
            x24, x23 = both[f"{f}{i24[br]}_24"].astype(str), both[f"{f}{i23[br]}_23"].astype(str)
            diff += int((x24 != x23).sum())
    return {"section": "identity", "walks_t24": len(a), "walks_t23": len(b), "unmatched": only,
            "fields_compared": int(len(both) * len(shared) * 4), "fields_differing": diff,
            "identity_holds": bool(only == 0 and diff == 0 and len(both) > 0)}


def coin(walks: pd.DataFrame, seed: int = COIN_SEED) -> pd.Series:
    import t24_screen as ts

    return ts.coin(walks, seed)


def trades(rd: Path, stop: int) -> tuple[pd.DataFrame, list[str]]:
    """The coin's trades five bars late at `stop` points: each with its net R, gross, cost, outcome and exit at every R
    of RRS, the fee a micro priced in; the day set."""
    import t23_choose as tc

    from propedge.reporting.results import read_result

    bix = bracket_index("R149-t24-NQ-2021")
    walks, days = load(rd)
    base = walks[walks["delay"].astype(int) == DELAY].copy()
    base["coin"] = coin(base)
    t = base[base["side"].astype(int) == base["coin"]].copy()
    sp = read_result(rd / Path(tc.R137).name)
    sp = sp[sp["kind"] == "spread"]
    spread = {(str(r.decision_ct), int(r.year)): float(r.spread_ticks_mean) for r in sp.itertuples() if float(r.quotes) > 0}
    t["entry_t"] = t["entry_slot"].astype(float)
    S = float(stop)
    for R in RRS:
        b = bix[(R * S, S)]
        t[f"r_{R:g}"] = tc.trade_r(t, b, R * S, S, spread, FEE_MICRO)
        t[f"g_{R:g}"], t[f"c_{R:g}"] = tc.trade_parts(t, b, R * S, S, spread, FEE_MICRO)
        t[f"o_{R:g}"] = t[f"o{b}"].astype(str)
        t[f"exit_t_{R:g}"] = t["entry_t"] + t[f"m{b}"].astype(float)
        t[f"mae_{R:g}"] = np.nan                                 # not captured: the room cap keeps every trade inside it
    t["exit_t"] = t[f"exit_t_{max(RRS):g}"]
    t["flat"] = t[f"o_{max(RRS):g}"] == "f"
    t["stop_ticks"] = int(round(S / 0.25))
    t["fee_micro_eq"] = FEE_MICRO
    t["side"] = np.where(t["side"].astype(int) > 0, "long", "short")
    t["date"] = t["date"].astype(str)
    t = t.sort_values(["date", "entry_t"], kind="stable").reset_index(drop=True)
    cols = ["date", "year", "decision_ct", "entry_t", "exit_t", "side", "stop_ticks", "flat", "fee_micro_eq",
            *[c for R in RRS for c in (f"r_{R:g}", f"g_{R:g}", f"c_{R:g}", f"o_{R:g}", f"exit_t_{R:g}", f"mae_{R:g}")]]
    return t[cols], sorted(days["date"].astype(str))


# ------------------------------------------------------------------------------------------------ the table


def rpc_of(stop: int) -> float:
    return float(stop) / 0.25 * 0.5                              # dollars a micro at the stop


def menu_risks(stop: int) -> list[float]:
    rpc = rpc_of(stop)
    return sorted({float(round(rpc * n / 50.0) * 50.0) for n in MICROS} - {0.0})


def table_config(stop: int) -> dict:
    """FV3-C's table config (`config/state_policy_v12.yaml`) with this width's menu: one stop, R 1 to 3, the sizes of
    MICROS on the $50 grid; its rules, rent, horizon and export unchanged."""
    import state_policy_dp as dp

    cfg = copy.deepcopy(dp.config(ROOT / "config" / "state_policy_v12.yaml"))
    cfg.pop("rungs", None)
    risks = menu_risks(stop)
    cfg["menu"] = {"step": 50.0, "risks": risks, "rrs": list(RRS), "skip": True}
    cfg["combine_menu"] = {"risks": risks, "rrs": list(RRS), "min_rr": 1.0}
    return cfg


def table_menu(stop: int):
    from propedge.campaign import state_policy as sp

    rungs = sp.Rungs(risk_per_contract=(rpc_of(stop),), shares=(1.0,), combine_cap=50,
                     funded_caps=((0.0, 20), (1500.0, 30), (2000.0, 50)), exit_grid=tuple(RRS))
    return sp.Menu(risks=tuple(menu_risks(stop)), rrs=tuple(RRS), skip=True, step=50.0, rungs=rungs, abandon=True)


def edge_cell(lb_by: dict[float, float]) -> float:
    """FV3-C's convention (P-06): the grid edge nearest the trades' lower bound -- the lowest of their R's -- clipped to
    the grid."""
    lb = min(lb_by.values())
    return min(GRID, key=lambda g: abs(g - (lb if np.isfinite(lb) else 0.0)))


class OracleRefused(SystemExit):
    """D-429: the table's oracles failed at a width -- a declared refusal, carrying the oracle rows for the record."""

    def __init__(self, message: str, rows: list[dict]):
        super().__init__(message)
        self.rows = rows


def solve_table(stop: int, e: float):
    """The table at edge `e` and its rent's fixed point; the oracles first. Returns (the exported RiskPolicy, rows)."""
    import state_policy_dp as dp

    from propedge.campaign import state_policy as sp
    from propedge.campaign.payout_method import rules_for_method

    cfg, menu = table_config(stop), table_menu(stop)
    rules = rules_for_method("aeropay")
    rows, ok = dp.oracles(cfg, rules, menu)
    rows = [{**r, "stop": stop} for r in rows]
    if not ok:
        raise OracleRefused("REFUSED: an oracle failed; the table is wrong, not the contract.", rows)
    lam, (f, fsol, ff, c, csol, cf), rounds = dp.solve_rent(cfg, rules, float(e), menu,
                                                            float(cfg["rent_fixed_point"]["start"]))
    cash, days, rate = dp.cycle_rate(rules, ff, cf)
    rows.append({"section": "table", "stop": stop, "edge": e, "rent": lam, "rate": rate, "cycle_cash": cash,
                 "cycle_slot_days": days, "value_attempt": csol.value - rules.subscription, "p_pass": cf["p_pass"],
                 "combine_p_abandon": cf.get("p_abandon", 0.0), "xfa_p_abandoned": ff.get("p_abandoned", 0.0),
                 "xfa_mean_cash": ff["mean_cash"], "rounds": len(rounds)})
    pid = f"t24_table_d{stop}_e{e:+.3f}_lamstar"
    pol, _ = sp.export_policy(pid, c, cf["visitation"], f, ff["visitation"], float(cfg["export"]["balance_band"]),
                              float(cfg["export"]["cushion_band"]), version=12, c_pol0=csol.policy[0],
                              f_pol0=fsol.policy[0],
                              description=f"T24 (D-429): FV3-C's table re-solved for the {stop}-point stop, R 1 to 3, at "
                                          f"edge {e:+.3f}, slot rent ${lam:.2f}/day")
    return pol, rows


def policies(table, stop: int) -> dict:
    """The families' policies from the exported table (module docstring)."""
    import t24_screen as ts

    from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy

    two = ts._closing(Leaf("two-shot 1:1", TWO_SHOT, 1.0, max_trades=1), TWO_SHOT)
    root = table.root
    p2 = RiskPolicy(id=f"t24_two_shot_d{stop}", root=Phase(combine=two, funded=root.funded, paid=root.paid),
                    description=f"T24 (D-429): the two-shot Combine with the {stop}-point table's funded legs")
    p2.validate()
    return {"table": table, "two_shot": p2}


# ------------------------------------------------------------------------------------------------ the campaign


def protocol():
    from propedge.campaign.protocols import Protocol

    return Protocol(name="t24_wide", combine_rr=1.0, combine_risk=TWO_SHOT, funded_rr=1.0, funded_risk=800.0,
                    trades_per_day=23, payout_path="standard", keep_balance=0.0, payout_frac=1.0,
                    max_concurrent_accounts=ACCOUNTS, family="t24", source="config/t24_capture.yaml", note=DECISION,
                    params=dict(PARAMS))


def sizing():
    from dataclasses import replace

    from propedge.campaign.sizing import CURRENT_TIER, SizingRule

    return replace(SizingRule.from_ledger(CURRENT_TIER, headroom_frac=1.0), room_cap=("combine", "funded"),
                   fee_schedule=(FEE_MICRO, FEE_MINI))


def run_config(blocks, e_by, lb_by, hook, policy, rule: str) -> pd.DataFrame:
    import score_fv3_grid as gf

    from propedge.campaign import gate
    from propedge.campaign.payout_method import rules_for_method

    df, _ = gate.run_gate(list(blocks), e=e_by[1.0], lb=lb_by[1.0], protocol=protocol(), bankroll=gf.UNBOUND_BANKROLL,
                          horizon_days=HORIZON, n_paths=N_PATHS, seed=SEED, accounts=ACCOUNTS, sizing=sizing(),
                          rules=rules_for_method("aeropay"), mode="rotation", settlement="pessimistic",
                          combines=ACCOUNTS, total_accounts=ACCOUNTS, risk_policy=policy, e_by_rr=e_by, lb_by_rr=lb_by,
                          levels=(0.0,), path_hook=hook, rtp=False, routing="able", cross_account=True,
                          hold_to_own_exit=True, one_at_a_time=RULES[rule])
    return df


def screen_width(rd: Path, stop: int) -> dict:
    """One width's screen, computed and returned, nothing written: the result's rows, the exported table, the screen
    rows, the trades and the table's edge cell. Workers run it; the parent writes (D-207: one process writes every
    result, so none reads another's file as dirt)."""
    import confirm_fv3 as cf
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import score_fv3_grid as gf

    t, days = trades(rd, stop)
    menu = list(RRS)
    stats = cf.edge_stats(t, menu, days, BLOCK, None)
    e_by, lb_by = ps._by(stats, "e"), ps._by(stats, "lb")
    blocks, n_used = gf.gate_blocks(t, days, 0.25 * 2.0, menu, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    e_tab = edge_cell(lb_by)
    pol, rows = solve_table(stop, e_tab)
    pols = policies(pol, stop)
    hook = lt.lever_hook(ps.composed_hook({"margin": MARGIN, "block_days": BLOCK}))
    out = [pd.DataFrame(rows),
           pd.DataFrame([{"section": "edge", "stop": stop, "rr": R, "e": stats[R]["e"], "lb": stats[R]["lb"],
                          "n": stats[R]["n"], "sd": stats[R]["sd"], "gross_r": float(t[f"g_{R:g}"].mean()),
                          "cost_r": float(t[f"c_{R:g}"].mean()), "flat_share": float((t[f"o_{R:g}"] == "f").mean())}
                         for R in menu])]
    screen = []
    for fam in FAMILIES:
        for rule in RULES:
            df = run_config(blocks, e_by, lb_by, hook, pols[fam], rule)
            df.insert(0, "rule", rule)
            df.insert(0, "family", fam)
            df.insert(0, "stop", stop)
            df.insert(0, "section", "campaign")
            out.append(df)
            g = float(df[df["shift"] == "lower_bound"].iloc[0]["pf_growth_on_base_p50"])
            gp = float(df[df["shift"] == "point"].iloc[0]["pf_growth_on_base_p50"])
            screen.append({"section": "screen", "stop": stop, "family": fam, "rule": rule, "growth_at_point": gp,
                           "growth_at_bound": g, "continues": bool(g > 0)})
            print(f"d{stop} {fam} {rule}: growth {gp:+.4f} at the point, {g:+.4f} at the bound", flush=True)
    out.append(pd.DataFrame(screen))
    return {"stop": stop, "res": pd.concat(out, ignore_index=True), "policy": pol.as_dict(), "screen": screen,
            "trades": len(t), "table_edge": e_tab}


def _screen_job(args: tuple) -> dict:
    """A width's screen in a worker. A declared refusal or an error comes back as a value: a pool worker that raises
    SystemExit is replaced and its task never returns, which deadlocked D-429's first run (D-430)."""
    rd, stop = args
    try:
        return screen_width(rd, stop)
    except OracleRefused as exc:
        return {"stop": stop, "refused": str(exc), "rows": exc.rows}
    except BaseException:                                        # noqa: B036 -- returned to the parent, never lost
        import traceback

        return {"stop": stop, "error": traceback.format_exc()}


def write_width(out: dict, rd: Path, results_dir: Path | None) -> None:
    """The parent's writes for one width: the variants, the result and the table's policy beside it; a refused width,
    its oracle rows and the refusal (no configuration ran, so no variant)."""
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import note_written, write_result

    stop = int(out["stop"])
    if "refused" in out:
        res = pd.DataFrame(list(out["rows"]) + [{"section": "screen", "stop": stop, "refused": out["refused"],
                                                 "continues": False}])
        write_result(res, f"t24_wide_d{stop}", script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                     parameters={"decision": DECISION, "stop": stop, "rrs": list(RRS), "menu_risks": menu_risks(stop)},
                     notes={"status": "EXPLORATORY screen (D-429): the width refused by its table's oracles"},
                     description=f"T24's wide screen (D-429) at the {stop}-point stop: refused -- the table's oracles "
                                 "failed, so no configuration ran.")
        return
    vc = VariantCounter(path=rd / "variants.jsonl")
    for r in out["screen"]:
        vc.record(prereg_id=f"{DECISION}:t24_wide", seed=SEED, exploratory=True,
                  params={"study": "T24 wide screen", "stop": stop, "family": r["family"], "rule": r["rule"],
                          "coin_seed": COIN_SEED}, label=f"T24 wide d{stop} {r['family']} {r['rule']}")
    name = f"t24_wide_d{stop}"
    write_result(out["res"], name, script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 parameters={"decision": DECISION, "stop": stop, "rrs": list(RRS), "delay": DELAY, "coin_seed": COIN_SEED,
                             "table_edge": out["table_edge"], "families": list(FAMILIES),
                             "rules": {k: v for k, v in RULES.items()}, "two_shot": TWO_SHOT,
                             "fees": [FEE_MICRO, FEE_MINI], "n_paths": N_PATHS, "horizon": HORIZON,
                             "trades": out["trades"]},
                 notes={"status": "EXPLORATORY screen (D-429); the kill line at the bound, never a verdict"},
                 description=f"T24's wide screen (D-429) at the {stop}-point stop: coin trades five bars late, two "
                             "families, two routing rules, at the point and the bound.")
    side = rd / f"{name}_policy.json"
    side.write_text(json.dumps(out["policy"]), encoding="utf-8")
    note_written(side)


WORKERS = 3


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result, write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--stop", type=int, choices=STOPS)
    ap.add_argument("--all", action="store_true", help="every width, in parallel workers, the parent writing each result")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if a.identity:
        row = identity(rd)
        write_result(pd.DataFrame([row]), "t24_identity", script=SCRIPT, seed=None, require_seed=False,
                     exploratory=True, results_dir=results_dir, parameters={"decision": DECISION},
                     notes={"seed": "none: a comparison of two captures"},
                     description="T24's capture against R147/R148 (D-428 (4)): the on-time walks of the four shared "
                                 "brackets, walk for walk.")
        print(f"identity: {'HOLDS' if row['identity_holds'] else 'FAILS'} -- {row['fields_differing']} of "
              f"{row['fields_compared']} fields differ, {row['unmatched']} walks unmatched")
        return 0 if row["identity_holds"] else 3
    if a.stop is None and not a.all:
        ap.error("--identity, --stop or --all")
    ident = read_result(rd / "t24_identity.csv")
    if not bool(ident.iloc[0]["identity_holds"]):
        print("REFUSED: the identity against R147/R148 does not hold (D-428 (4)); nothing of the capture is read.")
        return 3
    stops = list(STOPS) if a.all else [int(a.stop)]
    jobs = [(rd, s) for s in stops]
    if len(jobs) > 1 and WORKERS > 1:
        from multiprocessing import Pool

        with Pool(min(WORKERS, len(jobs))) as pool:
            outs = pool.map(_screen_job, jobs)
    else:
        outs = [_screen_job(j) for j in jobs]
    errors = [o for o in outs if "error" in o]
    for out in outs:
        if "error" not in out:
            write_width(out, rd, results_dir)
    for o in errors:
        print(f"ERROR at the {o['stop']}-point width (nothing written for it):\n{o['error']}", flush=True)
    return 4 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
