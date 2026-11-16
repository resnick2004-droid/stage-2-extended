"""EXPLORATORY (D-416 (4), (6)): T23's choice from its per-trade capture (R147, R148) -- first the identity against the
collect map (R145), then, for each configuration (d20, d25, d30, d40: the Combine at 1:1 and the big funded trade at
1.5:1 on one stop distance, the 20-point flip after the big win), the five-a-day schedule and stage one's contract fit
at the brackets' measured net edges, on CHOICE (2021-2023), at the seated delay, A3's side.

    python scripts/t23_choose.py

Writes results/t23_choice.csv (`identity`, `slot`, `config` and `verdict` rows) with its manifest.
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

SCRIPT = "scripts/t23_choose.py"
DECISION = "D-416"
CAPTURES = ("results/manual_R147_t23_NQ_2022.csv", "results/manual_R148_t23_NQ_2025.csv")
R145 = "results/manual_R145_collect_NQ.csv"
R137 = "results/manual_R137_flipmap_NQ.csv"
SEED = 20261023
IDENTITY = {"slot": "08:30", "bracket": (20.0, 20.0), "box": 10, "delay": 0, "contracts": 5, "multiple": 1.0, "tol": 0.02}
FLAT = 22 * 60 + 10
TICK, MPV = 0.25, 2.0
COMBINE_ANCHOR, COMBINE_MICROS = 1500.0, 50      # propsim D-08; D-289
BIG_ANCHOR, BIG_MICROS = 1000.0, 20              # propsim D-36; D-289 (an XFA under $1,500 of profit)
FLIP = {"risk": 200.0, "rr": 1.0}                # the 20/20 flip at five micros
GRID = 50.0
MIN_SIGNALS = 5


def stake(per_micro: float, anchor: float, cap: int, multiple: float) -> tuple[int, float]:
    """The most whole micros within the anchor and the allowance whose stake and win (stake x the bracket's R) both
    land on the $50 grid (D-412's rule)."""
    n = min(int(math.floor(anchor / per_micro + 1e-9)), cap)

    def on(x: float) -> bool:
        return abs(x / GRID - round(x / GRID)) < 1e-9

    while n > 0 and not (on(n * per_micro) and on(n * per_micro * multiple)):
        n -= 1
    return n, n * per_micro


def bracket_index(cfg: dict) -> dict[tuple[float, float], int]:
    return {(float(a), float(b)): i for i, (a, b) in enumerate(cfg["brackets"])}


def load(rd: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    from propedge.reporting.results import read_result

    parts = [read_result(rd / Path(p).name) for p in CAPTURES]
    t = pd.concat(parts, ignore_index=True)
    walks = t[t["kind"] == "walk"].copy()
    days = t[t["kind"] == "day"].copy()
    walks["year"] = walks["date"].astype(str).str[:4].astype(int)
    return walks, days


def identity(walks: pd.DataFrame, r145: pd.DataFrame, bi: int) -> dict:
    """D-416 (4): the 20/20 bracket on time at 08:30 read in the collect map's 10-minute box, against R145's cell."""
    w = walks[(walks["decision_ct"].astype(str) == IDENTITY["slot"]) & (walks["delay"].astype(int) == IDENTITY["delay"])]
    o, m = w[f"o{bi}"].astype(str), w[f"m{bi}"].astype(float)
    n = len(w)
    ours = {"target": float(((o == "t") & (m <= IDENTITY["box"])).sum()) / n,
            "stop": float(((o == "s") & (m <= IDENTITY["box"])).sum()) / n}
    ours["scratch"] = 1.0 - ours["target"] - ours["stop"]
    c = r145[(r145["kind"] == "count") & (r145["decision_ct"].astype(str) == IDENTITY["slot"])
             & (r145["contracts"].astype(float) == IDENTITY["contracts"])
             & ((r145["stop_multiple"].astype(float) - IDENTITY["multiple"]).abs() < 1e-9)
             & (r145["box_minutes"].astype(float) == IDENTITY["box"]) & (r145["delay_min"].astype(float) == IDENTITY["delay"])]
    N = float(c["n"].sum())
    theirs = {k: float(c[k].sum()) / N for k in ("target", "stop", "scratch")}
    diffs = {k: ours[k] - theirs[k] for k in ours}
    return {"section": "identity", "walks_ours": n, "walks_r145": int(N),
            **{f"{k}_share": ours[k] for k in ours}, **{f"r145_{k}_share": theirs[k] for k in ours},
            **{f"{k}_diff": diffs[k] for k in ours}, "tolerance": IDENTITY["tol"],
            "identity_holds": bool(all(abs(v) <= IDENTITY["tol"] for v in diffs.values()))}


def sides(walks: pd.DataFrame, days: pd.DataFrame, slots: list[int], rule: str) -> pd.Series:
    """Each walk's side under the rule -- A3's sign at its slot that day (0 or missing: no trade), or a seeded coin."""
    if rule == "coin":
        rng = np.random.default_rng(SEED)
        keys = sorted(set(zip(walks["date"].astype(str), walks["decision_slot_minutes"].astype(int))))
        coin = dict(zip(keys, rng.choice([1, -1], size=len(keys))))
        return pd.Series([coin[(d, s)] for d, s in zip(walks["date"].astype(str), walks["decision_slot_minutes"].astype(int))],
                         index=walks.index)
    idx = {s: i for i, s in enumerate(slots)}
    a3 = {}
    for r in days.itertuples(index=False):
        for s, i in idx.items():
            v = getattr(r, f"a3_{i}")
            a3[(str(r.date), s)] = 0 if (v is None or v != v) else int(v)
    return pd.Series([a3.get((d, int(s)), 0) for d, s in zip(walks["date"].astype(str), walks["decision_slot_minutes"])],
                     index=walks.index)


def trade_r(t: pd.DataFrame, bi: int, T: float, S: float, spread: dict, fee: float) -> pd.Series:
    """Each trade's net R at bracket `bi` (target T, stop S points) per micro: the target T/S, the stop -1 less its
    recorded gap, an end its recorded ticks; less the collect map's costs -- the round turn, the entry spread beyond the
    walk's tick (R137, the slot's year), a tick and the gap on a stop -- over the stop's dollars (D-416 (6))."""
    tick_d = TICK * MPV
    risk = S * MPV
    o, g, x = t[f"o{bi}"].astype(str), t[f"g{bi}"].astype(float), t[f"x{bi}"].astype(float)
    gross = np.where(o == "t", T * MPV, np.where(o == "s", -(S * MPV + g * tick_d), x * tick_d))
    sp = np.array([spread.get((str(c), int(y)), 1.0) for c, y in zip(t["decision_ct"], t["year"])], float)
    cost = fee + np.maximum(0.0, sp - 1.0) * tick_d + np.where(o == "s", tick_d, 0.0)
    return pd.Series((gross - cost) / risk, index=t.index)


def trade_parts(t: pd.DataFrame, bi: int, T: float, S: float, spread: dict, fee: float) -> tuple[pd.Series, pd.Series]:
    """`trade_r`'s two parts, each over the stop's dollars per micro: the gross R and the cost in R (D-419: the cost
    drag beside the verdict); gross less cost is `trade_r`."""
    tick_d = TICK * MPV
    risk = S * MPV
    o, g, x = t[f"o{bi}"].astype(str), t[f"g{bi}"].astype(float), t[f"x{bi}"].astype(float)
    gross = np.where(o == "t", T * MPV, np.where(o == "s", -(S * MPV + g * tick_d), x * tick_d))
    sp = np.array([spread.get((str(c), int(y)), 1.0) for c, y in zip(t["decision_ct"], t["year"])], float)
    cost = fee + np.maximum(0.0, sp - 1.0) * tick_d + np.where(o == "s", tick_d, 0.0)
    return pd.Series(gross / risk, index=t.index), pd.Series(cost / risk, index=t.index)


def largest_schedule(dur: dict[int, float]) -> list[int]:
    """The largest set of slots each ending (slot + its duration) at or before the next chosen slot and by 15:10 CT."""
    ok = sorted((s + d, s) for s, d in dur.items() if np.isfinite(d) and s + d <= FLAT)
    chosen, free = [], -1.0
    for end, s in ok:
        if s >= free:
            chosen.append(s)
            free = end
    return sorted(chosen)


def funded_and_combine(cfg_dp: dict, rules, e_combine: float, e_big: float, e_flip: float, combine_risk: float,
                       big_risk: float) -> dict:
    """D-414's model at these edges: stage one's Combine at 1:1, the funded table with the big 1.5:1 trade at or below
    the start and the flip (a menu bracket at its own edge) above it."""
    import state_policy_dp as dp
    from propedge.campaign import state_policy as sp

    T = int(cfg_dp["horizon_days"])
    step = float(cfg_dp["menu"]["step"])
    menu = sp.Menu(risks=(float(big_risk),), rrs=(1.5,), skip=False, step=step,
                   flips=((FLIP["risk"], FLIP["rr"], float(e_flip), 0.0),))
    f = sp.FundedDP(rules, menu, float(e_big), T, 0.0, balance_cap=float(cfg_dp["funded"]["balance_cap"]),
                    payout_grid_step=float(cfg_dp["funded"]["payout_grid_step"]), payout_choice="max")
    bi, fi = f.actions.index((float(big_risk), 1.5)), f.actions.index((FLIP["risk"], FLIP["rr"]))
    above = f.B > 1e-9
    allowed = np.zeros((len(f.actions), f.nS), bool)
    allowed[bi], allowed[fi] = ~above, above
    f.allowed = allowed
    fsol = f.solve()
    ff = f.forward(fsol)
    c = sp.CombineDP(rules, sp.Menu.fixed(float(combine_risk), 1.0, step), float(e_combine), T, 0.0)
    csol = c.solve(fsol.fresh_value[1:T + 1] - rules.activation)
    cf = c.forward(csol)
    row = dp.row_of("config", e_combine, 0.0, "t23", rules, fsol, ff, csol, cf)
    cash, days, rate = dp.cycle_rate(rules, ff, cf)
    return {"p_pass": row["p_pass"], "combine_mean_days": row["combine_mean_days"], "xfa_mean_cash": row["xfa_mean_cash"],
            "xfa_mean_days": row["xfa_mean_days"], "xfa_p_paid": row["xfa_p_paid"],
            "chain_cash_no_rent": row["chain_cash_no_rent"], "cash_per_slot_day": rate}


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import score_collect_map as scm
    import state_policy_dp as dp

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.campaign.payout_method import rules_for_method
    from propedge.data import t23_kit as tk
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = tk.config_t23()
    q = tk.params_t23(str(cfg["runs"][0]["run"]), cfg)
    slots, labels = q["slots"], q["slot_labels"]
    bix = bracket_index(cfg)
    walks, days = load(rd)
    rows = [identity(walks, read_result(rd / Path(R145).name), bix[IDENTITY["bracket"]])]
    if not rows[0]["identity_holds"]:
        rows.append({"section": "verdict", "verdict": "none: the identity fails -- nothing is chosen (D-416 (4))"})
    else:
        sp_rows = read_result(rd / Path(R137).name)
        sp_rows = sp_rows[sp_rows["kind"] == "spread"]
        spread = {(str(r.decision_ct), int(r.year)): float(r.spread_ticks_mean) for r in sp_rows.itertuples()
                  if float(r.quotes) > 0}
        fee = float(FillModel.load("assumed").round_turn_by_instrument[str(cfg["contract"]["micro"])])
        per = {k: tuple(int(x[:4]) for x in v) for k, v in cfg["periods"].items()}
        choice_years = list(range(per["choice"][0], per["choice"][1] + 1))
        check_years = list(range(per["check"][0], per["check"][1] + 1))
        dly = int(cfg["delay_rule"])
        base = walks[walks["delay"].astype(int) == dly].copy()
        base["a3"] = sides(base, days, slots, "a3")
        base["coin"] = sides(base, days, slots, "coin")
        dp_cfg = dp.config(dp.config_for(12))
        rules = rules_for_method(dp_cfg["campaign_check"]["payout_method"])
        configs = []
        for c in cfg["configurations"]:
            legs = {"combine": tuple(map(float, c["combine"])), "big": tuple(map(float, c["big"])),
                    "flip": tuple(map(float, c["flip"]))}
            tr = base[(base["side"].astype(int) == base["a3"]) & (base["a3"] != 0)]
            ch = tr[tr["year"].isin(choice_years)]
            # (a) each slot's duration: the slowest of the three brackets, its yearly p90, the worst year
            dur_cols = []
            for leg, (T, S) in legs.items():
                b = bix[(T, S)]
                ch = ch.assign(**{f"d_{leg}": ch["entry_slot"].astype(float) + ch[f"m{b}"].astype(float)
                                  - ch["decision_slot_minutes"].astype(float)})
                dur_cols.append(f"d_{leg}")
            ch = ch.assign(slowest=ch[dur_cols].max(axis=1))
            dur = {}
            for s, g in ch.groupby("decision_slot_minutes"):
                dur[int(s)] = float(g.groupby("year")["slowest"].quantile(0.90).max())
            sched = largest_schedule(dur)
            for s in sorted(dur):
                rows.append({"section": "slot", "config": c["name"], "decision_slot_minutes": s,
                             "decision_ct": labels[slots.index(s)], "duration_p90_worst_year": dur[s],
                             "in_schedule": s in sched})
            r = {"section": "config", "config": c["name"], "schedule": " ".join(labels[slots.index(s)] for s in sched),
                 "schedule_size": len(sched), "meets_r1": len(sched) >= MIN_SIGNALS}
            # (c) each bracket's measured net edge over the schedule's slots, A3's side, its bound; CHECK, 2020, coin beside
            for leg, (T, S) in legs.items():
                b = bix[(T, S)]
                x = tr[tr["decision_slot_minutes"].astype(int).isin(sched)]
                rr = trade_r(x, b, T, S, spread, fee)
                yr = rr.groupby(x["year"]).mean()
                r[f"e_{leg}"] = float(rr[x["year"].isin(choice_years)].mean()) if len(rr) else float("nan")
                r[f"lb_{leg}"] = scm.bound([yr[y] for y in choice_years if y in yr.index])
                r[f"e_{leg}_check"] = float(rr[x["year"].isin(check_years)].mean()) if len(rr) else float("nan")
                r[f"e_{leg}_2020"] = float(rr[x["year"] == 2020].mean()) if len(rr) else float("nan")
                xc = base[(base["side"].astype(int) == base["coin"]) & base["decision_slot_minutes"].astype(int).isin(sched)
                          & base["year"].isin(choice_years)]
                r[f"e_{leg}_coin"] = float(trade_r(xc, b, T, S, spread, fee).mean()) if len(xc) else float("nan")
                r[f"n_{leg}"] = int(x["year"].isin(choice_years).sum())
            nc, rc = stake(legs["combine"][1] * MPV, COMBINE_ANCHOR, COMBINE_MICROS, 1.0)
            nb, rb = stake(legs["big"][1] * MPV, BIG_ANCHOR, BIG_MICROS, 1.5)
            r.update({"combine_micros": nc, "combine_risk": rc, "big_micros": nb, "big_risk": rb})
            if r["meets_r1"] and rc > 0 and rb > 0:
                for arm, key in (("point", "e"), ("lower_bound", "lb"), ("zero", None)):
                    e = (lambda leg: 0.0) if key is None else (lambda leg, k=key: r[f"{k}_{leg}"])
                    out = funded_and_combine(dp_cfg, rules, e("combine"), e("big"), e("flip"), rc, rb)
                    r.update({f"{k}_{arm}": v for k, v in out.items()})
                r["passes"] = bool(r["chain_cash_no_rent_point"] > 0.0)
            else:
                r["passes"] = False
            configs.append(r)
            rows.append(r)
            print(f"{c['name']}: schedule {r['schedule']} ({len(sched)}); e combine {r['e_combine']:+.4f}, big "
                  f"{r['e_big']:+.4f}, flip {r['e_flip']:+.4f}; cash/attempt {r.get('chain_cash_no_rent_point', float('nan')):+.1f}",
                  flush=True)
        cf = pd.DataFrame(configs)
        passing = cf[cf["passes"]].sort_values("cash_per_slot_day_point", ascending=False)
        first = passing.iloc[0] if len(passing) else None
        plateau = ([x.config for x in passing.itertuples()
                    if x.cash_per_slot_day_point >= first["cash_per_slot_day_point"] * 0.9 - 1e-12] if first is not None else [])
        rows.append({"section": "verdict", "verdict": (f"{first['config']}" if first is not None
                                                       else "none: T23's fixed-time route closes (D-416 (6))"),
                     "passing": ",".join(passing["config"]), "plateau": ",".join(plateau)})
    res = pd.DataFrame(rows)
    write_result(res, "t23_choice", script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 parameters={"decision": DECISION, "captures": list(CAPTURES), "r145": R145, "r137": R137,
                             "identity": {k: (list(v) if isinstance(v, tuple) else v) for k, v in IDENTITY.items()},
                             "delay_rule": "two bars", "side_rule": "A3 (coin beside, seed 20261023)",
                             "model": "D-414's (stage one's Combine at 1:1; the funded table's state rule, big 1.5:1 then "
                                      "the 20/20 flip at its own edge); no rent"},
                 notes={"status": "EXPLORATORY: T23's choice of stop distance from its capture (D-416 (6))"},
                 description="EXPLORATORY: T23's choice (D-416 (6)) -- the identity against R145, then per configuration "
                             "the five-a-day schedule and stage one's contract fit at the brackets' measured net edges.")
    vc = VariantCounter(path=rd / "variants.jsonl")
    for c in cfg["configurations"]:
        vc.record(prereg_id=f"{DECISION}:t23_capture", seed=SEED, exploratory=True,
                  params={"study": "T23 choice", "config": c["name"]}, label=f"T23's choice (D-416): {c['name']}")
    print(res[res["section"].isin(["identity", "verdict"])].dropna(axis=1, how="all").to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
