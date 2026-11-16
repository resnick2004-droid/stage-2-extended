"""T24 (D-426): the cheapest coin -- an EXPLORATORY screen of sizing families on coin-flip trades from the T23 captures,
strictly one trade at a time, in the campaign engine at the point and at the bound.

    python scripts/t24_screen.py

The trades: the six fixed times and the 20-point stop of the captures (D-416, D-417; reused by a new protocol under
D-426 (2)), entered two bars late, each side chosen by a coin seeded here (COIN_SEED), filtered strictly one at a time
(D-160, `t23_d20.strict`), each trade's costs inside its R and its fee re-priced in the engine at the contracts it holds
-- as many NQ minis as fit, the rest MNQ micros (D-324). Every family closes a funded account left with less room than
one micro at the stop (D-336's reading of closing at the trader's request); a Combine out of room is ended as before
(D-318). The families:

    f0_reference   T23-D20's legs (the Combine 1:1 $1,400; funded 1.5:1 $800 at or below the start, the $200 flip above)
                   -- a diagnostic of what the closure and the fees change, never a candidate (D-423 (4))
    f1_two_shot    the operator's Combine (2026-10-24): 1:1 at $1,600, one trade a session, so two wins net the $3,000
                   target after costs inside the consistency rule; closed once the room cannot carry another $1,600;
                   funded as f0

The kill line (D-426 (4)): a family continues if its campaign's median growth on the required bankroll is above zero at
each R's one-sided 95 % bound over 21-session blocks, 0 % denial, the placement off. Exploratory, never a verdict.
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

SCRIPT = "scripts/t24_screen.py"
DECISION = "D-426"
COIN_SEED = 20261025                       # the coin's sides, fixed before the screen reads them
SEED = 20261026                            # the campaign's resampling
N_PATHS, HORIZON, ACCOUNTS = 500, 504, 5
MARGIN, BLOCK = 49.0, 21
FEE_MICRO, FEE_MINI = 1.22, 3.78           # config/fills.yaml `assumed` (the published schedule)
TWO_SHOT = 1600.0                          # 40 micros at the 20-point stop: a win nets at least half the target
FAMILIES = ("f0_reference", "f1_two_shot")


def coin(walks: pd.DataFrame, seed: int = COIN_SEED) -> pd.Series:
    """Each walk's side by a seeded coin, one draw a (date, slot), the same for both of its sides' walks."""
    rng = np.random.default_rng(seed)
    keys = sorted(set(zip(walks["date"].astype(str), walks["decision_slot_minutes"].astype(int))))
    draw = dict(zip(keys, rng.choice([1, -1], size=len(keys))))
    return pd.Series([draw[(d, s)] for d, s in zip(walks["date"].astype(str), walks["decision_slot_minutes"].astype(int))],
                     index=walks.index)


def trades(rd: Path) -> tuple[pd.DataFrame, list[str], int]:
    """The coin's trades at the schedule, as `t23_d20.trades` builds A3's: each with its net R, outcome and exit time at
    R 1 and 1.5 and the fee a micro priced into it; the strict filter; the day set."""
    import t23_choose as tc
    import t23_d20 as td

    from propedge.data import t23_kit as tk
    from propedge.reporting.results import read_result

    cfg = tk.config_t23()
    q = tk.params_t23(str(cfg["runs"][0]["run"]), cfg)
    slots, labels = q["slots"], q["slot_labels"]
    bix = tc.bracket_index(cfg)
    walks, days = tc.load(rd)
    sched = [slots[labels.index(x)] for x in td.chosen_schedule(rd)]
    base = walks[(walks["delay"].astype(int) == td.DELAY) & walks["decision_slot_minutes"].astype(int).isin(sched)].copy()
    base["coin"] = coin(base)
    t = base[base["side"].astype(int) == base["coin"]].copy()
    sp = read_result(rd / Path(tc.R137).name)
    sp = sp[sp["kind"] == "spread"]
    spread = {(str(r.decision_ct), int(r.year)): float(r.spread_ticks_mean) for r in sp.itertuples() if float(r.quotes) > 0}
    t["entry_t"] = t["entry_slot"].astype(float)
    for R, (T, S) in td.BRACKETS.items():
        b = bix[(T, S)]
        t[f"r_{R:g}"] = tc.trade_r(t, b, T, S, spread, FEE_MICRO)
        t[f"g_{R:g}"], t[f"c_{R:g}"] = tc.trade_parts(t, b, T, S, spread, FEE_MICRO)
        t[f"o_{R:g}"] = t[f"o{b}"].astype(str)
        t[f"exit_t_{R:g}"] = t["entry_t"] + t[f"m{b}"].astype(float)
        t[f"mae_{R:g}"] = np.nan
    t["exit_t"] = t["exit_t_1.5"]
    t["flat"] = t["o_1.5"] == "f"
    t["stop_ticks"] = td.STOP_TICKS
    t["fee_micro_eq"] = FEE_MICRO                                  # D-324: the fee a micro priced into each R
    t["side"] = np.where(t["side"].astype(int) > 0, "long", "short")
    t["date"] = t["date"].astype(str)
    cols = ["date", "year", "decision_ct", "entry_t", "exit_t", "side", "stop_ticks", "flat", "fee_micro_eq",
            *[c for R in td.BRACKETS for c in (f"r_{R:g}", f"g_{R:g}", f"c_{R:g}", f"o_{R:g}", f"exit_t_{R:g}",
                                               f"mae_{R:g}")]]
    kept, skipped = td.strict(t[cols])
    return kept, sorted(days["date"].astype(str)), skipped


def _closing(node, floor: float):
    """`node` wrapped so an account whose room above the floor is below `floor` dollars is closed (D-336's reading)."""
    from propedge.campaign.risk_policy import Leaf, Tiers

    return Tiers(on="cushion", name="the room", tiers=((-1e12, Leaf("closed: no room", 0.0, None, max_trades=0,
                                                                     abandon=True)),
                                                      (float(floor), node)))


def policy(family: str):
    """The family's phase and balance tree (module docstring), each funded account closed below one micro's room."""
    import t23_d20 as td

    from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy, Tiers

    (cr, cR), (br, bR), (fr, fR) = td.LEGS["combine"], td.LEGS["big"], td.LEGS["flip"]
    micro = td.STOP_TICKS * 0.5                                   # one micro's risk at the stop
    funded = _closing(Tiers(on="balance", name="the start",
                            tiers=((-1e12, Leaf("big 1.5:1", br, bR, max_trades=td.MAX_TRADES)),
                                   (0.01, Leaf("flip 1:1", fr, fR, max_trades=td.MAX_TRADES)))), micro)
    if family == "f0_reference":
        combine = Leaf("combine 1:1", cr, cR, max_trades=td.MAX_TRADES)
    elif family == "f1_two_shot":
        combine = _closing(Leaf("two-shot 1:1", TWO_SHOT, 1.0, max_trades=1), TWO_SHOT)
    else:
        raise ValueError(f"unknown family {family!r}")
    p = RiskPolicy(id=f"t24_{family}", root=Phase(combine=combine, funded=funded),
                   description=f"T24 (D-426): {family}")
    p.validate()
    return p


def sizing():
    from dataclasses import replace

    import t23_d20 as td

    return replace(td.sizing(), fee_schedule=(FEE_MICRO, FEE_MINI))


def run_family(blocks, e_by, lb_by, hook, family: str) -> pd.DataFrame:
    import score_fv3_grid as gf
    import t23_d20 as td

    from propedge.campaign import gate
    from propedge.campaign.payout_method import rules_for_method

    df, _ = gate.run_gate(list(blocks), e=e_by[1.5], lb=lb_by[1.5], protocol=td.protocol(), bankroll=gf.UNBOUND_BANKROLL,
                          horizon_days=HORIZON, n_paths=N_PATHS, seed=SEED, accounts=ACCOUNTS, sizing=sizing(),
                          rules=rules_for_method("aeropay"), mode="rotation", settlement="pessimistic",
                          combines=ACCOUNTS, total_accounts=ACCOUNTS, risk_policy=policy(family), e_by_rr=e_by,
                          lb_by_rr=lb_by, levels=(0.0,), path_hook=hook, rtp=False, routing="able",
                          cross_account=True, hold_to_own_exit=True)
    df.insert(0, "family", family)
    df.insert(0, "section", "campaign")
    return df


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import confirm_fv3 as cf
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import score_fv3_grid as gf
    import t23_d20 as td

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t, days, skipped = trades(rd)
    menu = sorted(td.BRACKETS)
    stats = cf.edge_stats(t, menu, days, BLOCK, None)
    e_by, lb_by = ps._by(stats, "e"), ps._by(stats, "lb")
    blocks, n_used = gf.gate_blocks(t, days, td.TICK * td.MPV, menu, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    hook = lt.lever_hook(ps.composed_hook({"margin": MARGIN, "block_days": BLOCK}))
    rows = [pd.DataFrame([{"section": "edge", "rr": R, "e": stats[R]["e"], "lb": stats[R]["lb"], "n": stats[R]["n"],
                           "gross_r": float(t[f"g_{R:g}"].mean()), "cost_r": float(t[f"c_{R:g}"].mean())} for R in menu])]
    out = {}
    for fam in FAMILIES:
        df = run_family(blocks, e_by, lb_by, hook, fam)
        rows.append(df)
        b = df[df["shift"] == "lower_bound"].iloc[0]
        out[fam] = float(b["pf_growth_on_base_p50"])
    rows.append(pd.DataFrame([{"section": "screen", "family": f, "growth_at_bound": g,
                               "continues": bool(g > 0)} for f, g in out.items()]))
    res = pd.concat(rows, ignore_index=True)
    vc = VariantCounter(path=rd / "variants.jsonl")
    for fam in FAMILIES:
        vc.record(prereg_id=f"{DECISION}:t24_screen", seed=SEED, exploratory=True,
                  params={"study": "T24 screen", "family": fam, "coin_seed": COIN_SEED}, label=f"T24 screen {fam}")
    write_result(res, "t24_screen", script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 parameters={"decision": DECISION, "families": list(FAMILIES), "coin_seed": COIN_SEED,
                             "schedule": list(td.SCHEDULE), "stop_ticks": td.STOP_TICKS, "two_shot": TWO_SHOT,
                             "fees": [FEE_MICRO, FEE_MINI], "n_paths": N_PATHS, "horizon": HORIZON, "trades": len(t),
                             "skipped": skipped},
                 notes={"status": "EXPLORATORY screen (D-426); the kill line at the bound, never a verdict"},
                 description="T24's screen (D-426): coin-flip trades at the T23 schedule, strictly one at a time, "
                             "through five accounts under two sizing families, at the point and the bound.")
    for f, g in out.items():
        print(f"{f}: growth at the bound {g:+.4f} -> {'continues' if g > 0 else 'stops'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
