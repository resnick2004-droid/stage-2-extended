"""EXPLORATORY (D-373): the any-time direction atlas's screen, by the rules fixed in config/flip_anytime.yaml before its
data was read.

    python scripts/score_flip_anytime.py          # reads results/manual_R143_flipany_NQ.csv

Per slot-day a signal per measure (+1, -1, 0); on the slot-days with a signal and both primary brackets entered on
time, z = 1 when the rule's side reached its target first, -1 when the other side did; the effect is mean z, its
standard error clustered by day (the day's summed residuals, Newey-West over days, lag 5).

* **A, the hint (k = 1):** FOLLOW the last minute's candle at every slot but 08:30, 2022-01-03 to 2025-06-30; it holds
  when the effect is above zero with a one-sided p below 0.05 and the 60-second-late entry's effect is above zero too.
* **B, the atlas (k = 7):** each measure pooled over the thirteen slots; on CHOICE (2020-2022) two-sided p and
  Benjamini-Hochberg at q = 0.10, the side by the sign; on CHECK (2023 to June 2025) a survivor holds when its side's
  effect is above zero, one-sided p below 0.05, at least half the CHOICE size, and the late entry's effect the same sign.
* **The money:** the rule's side at the primary width, on time, per attempt in units of the risk (+1, -1, a scratch's
  ticks over the width) less the cost (the MNQ round turn from config/fills.yaml and one tick of spread, over the width
  in ticks at $0.50 a tick); TRADABLE when its clustered one-sided 95 % lower bound is above zero.

Beside: every measure at every slot on both spans with the Benjamini-Hochberg listing over the 91 on CHOICE, per year,
the 0.40 width and the late entry, the long and short baseline per slot. Writes results/flip_anytime_nq.csv with its
manifest; the eight tests are recorded in results/variants.jsonl (family flip_anytime, D-373).
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from score_flip_direction import _p_one, _p_two, _sign, _thirds, bh  # noqa: E402

SCRIPT = "scripts/score_flip_anytime.py"
CONFIG = ROOT / "config" / "flip_anytime.yaml"
RUN = "R143-flipany-NQ"
MEASURES = ("A1_last1", "A2_last15", "A3_last60", "A4_since_rth_open", "A5_since_day_open", "A6_range_position",
            "A7_prior_rth")
Q_FDR = 0.10
P_ONE = 0.05
NW_LAG = 5
Z95 = 1.6448536269514722


def signals(df: pd.DataFrame) -> pd.DataFrame:
    """Each measure's signal per slot-day (+1, -1, 0), by config/flip_anytime.yaml's definitions."""
    out = pd.DataFrame(index=df.index)
    for m, col in (("A1_last1", "a1_last1"), ("A2_last15", "a2_last15"), ("A3_last60", "a3_last60"),
                   ("A4_since_rth_open", "a4_since_rth_open"), ("A5_since_day_open", "a5_since_day_open"),
                   ("A7_prior_rth", "a7_prior_rth")):
        out[m] = [_sign(x) for x in df[col].astype(float)]
    out["A6_range_position"] = [_thirds(lo, hi) for lo, hi in zip(df["rlo"].astype(float), df["rhi"].astype(float))]
    return out[list(MEASURES)]


def clustered(values: np.ndarray, days: np.ndarray, lag: int = NW_LAG) -> tuple[float, float]:
    """(mean, standard error) of `values`, the error clustered by day: the day's summed residuals, Newey-West over the
    days in date order (Bartlett weights, `lag` days)."""
    n = len(values)
    if n < 2:
        return (float(values.mean()) if n else float("nan")), float("nan")
    mu = float(values.mean())
    e = pd.Series(values - mu).groupby(days).sum().sort_index().to_numpy()
    v = float(e @ e)
    for k in range(1, min(lag, len(e) - 1) + 1):
        v += 2.0 * (1.0 - k / (lag + 1.0)) * float(e[k:] @ e[:-k])
    return mu, math.sqrt(max(v, 0.0)) / n


def _sides(df: pd.DataFrame, sig: pd.Series, col_l: str, col_s: str):
    ok = ((sig != 0) & (df[col_l] != "-") & (df[col_s] != "-")).to_numpy()
    s = sig.to_numpy()[ok]
    lo, so = df[col_l].to_numpy()[ok], df[col_s].to_numpy()[ok]
    return ok, np.where(s > 0, lo, so), np.where(s > 0, so, lo)


def effect(df: pd.DataFrame, sig: pd.Series, col_l: str, col_s: str) -> dict:
    """On the slot-days with a signal and both brackets entered: n, the signal side's and the other side's win shares,
    the effect (mean z), its day-clustered standard error and t."""
    ok, fol, fad = _sides(df, sig, col_l, col_s)
    z = (fol == "t").astype(float) - (fad == "t").astype(float)
    if not len(z):
        return {"n": 0, "follow_win": float("nan"), "fade_win": float("nan"), "effect": float("nan"),
                "se": float("nan"), "t": float("nan")}
    mu, se = clustered(z, df["date"].to_numpy()[ok])
    return {"n": int(len(z)), "follow_win": float((fol == "t").mean()), "fade_win": float((fad == "t").mean()),
            "effect": mu, "se": se, "t": mu / se if (se == se and se > 0) else float("nan")}


def money(df: pd.DataFrame, sig: pd.Series, side: int, label: str, fee_micro: float) -> dict:
    """The rule's side (`side` +1 with the signal, -1 against it) at the primary width, on time: per attempt in units of
    the risk -- +1, -1, or a scratch's ticks over the width -- less the cost (the round turn a micro over $0.50 a tick,
    plus one tick, over the width in ticks); its mean, clustered one-sided 95 % lower bound and win share."""
    cl, cs = f"o_{label}_d0_L", f"o_{label}_d0_S"
    ok = ((sig != 0) & (df[cl] != "-") & (df[cs] != "-")).to_numpy()
    d = df[ok]
    trade = sig.to_numpy()[ok] * side
    kind = np.where(trade > 0, d[cl].to_numpy(), d[cs].to_numpy())
    xs = np.where(trade > 0, d["xs_L"].astype(float).to_numpy(), d["xs_S"].astype(float).to_numpy())
    w = d[f"w_{label}"].astype(float).to_numpy()
    cost = (fee_micro / 0.5 + 1.0) / w
    r = np.where(kind == "t", 1.0, np.where(kind == "s", -1.0, np.nan_to_num(xs) / w)) - cost
    if not len(r):
        return {"money_n": 0, "money_win": float("nan"), "money_mean_r": float("nan"), "money_lb_r": float("nan"),
                "money_cost_r": float("nan")}
    mu, se = clustered(r, d["date"].to_numpy())
    return {"money_n": int(len(r)), "money_win": float((kind == "t").mean()), "money_mean_r": mu,
            "money_lb_r": mu - Z95 * se if se == se else float("nan"), "money_cost_r": float(cost.mean())}


def _in(df: pd.DataFrame, span) -> np.ndarray:
    return ((df["date"] >= span[0]) & (df["date"] <= span[1])).to_numpy()


def score(df: pd.DataFrame, cfg: dict, fee_micro: float) -> pd.DataFrame:
    from propedge.data import flip_kit as fk

    q = fk.params_anytime(cfg)
    prim, wide = q["width_labels"][0], q["width_labels"][1]
    pl, ps, ll, ls = f"o_{prim}_d0_L", f"o_{prim}_d0_S", f"o_{prim}_d60_L", f"o_{prim}_d60_S"
    df = df.sort_values(["date", "slot_index"]).reset_index(drop=True)
    sig = signals(df)
    rows: list[dict] = []
    # ---- A: the hint at the slots it was not seen at
    a = cfg["A_hint"]
    sel = _in(df, a["period"]) & (df["slot"] != "08:30").to_numpy()
    d, s = df[sel], sig.loc[sel, "A1_last1"]
    e, late = effect(d, s, pl, ps), effect(d, s, ll, ls)
    pa = _p_one(e["t"])
    held_a = bool(e["effect"] == e["effect"] and e["effect"] > 0 and pa < P_ONE and late["effect"] > 0)
    mon_a = money(d, s, 1, prim, fee_micro)
    rows.append({"section": "A_hint", "measure": "A1_last1", "side": "follow", "period": "2022-2025", **e,
                 "p_one": pa, "late_effect": late["effect"], "holds": held_a, **mon_a,
                 "tradable": bool(held_a and mon_a["money_lb_r"] > 0)})
    for slot in [x for x in q["slot_labels"] if x != "08:30"]:
        ss = sel & (df["slot"] == slot).to_numpy()
        rows.append({"section": "A_slot", "measure": "A1_last1", "side": "follow", "slot": slot,
                     **effect(df[ss], sig.loc[ss, "A1_last1"], pl, ps)})
    # ---- B: each measure pooled over the slots
    b = cfg["B_atlas"]
    ch, ck = _in(df, b["choice"]), _in(df, b["check"])
    stats = {m: (effect(df[ch], sig.loc[ch, m], pl, ps), effect(df[ck], sig.loc[ck, m], pl, ps),
                 effect(df[ck], sig.loc[ck, m], ll, ls)) for m in MEASURES}
    p_choice = [_p_two(stats[m][0]["t"]) for m in MEASURES]
    disc = bh(p_choice, Q_FDR)
    surv, holds, trad = [], [], []
    for i, m in enumerate(MEASURES):
        c, k, kl = stats[m]
        side = 1 if (c["effect"] == c["effect"] and c["effect"] > 0) else -1
        kc, klc = side * k["effect"], side * kl["effect"]
        p1 = _p_one(kc / k["se"]) if (k["se"] == k["se"] and k["se"] > 0) else float("nan")
        held = bool(disc[i] and kc > 0 and p1 < P_ONE and kc >= 0.5 * abs(c["effect"]) - 1e-12 and klc > 0)
        mon = money(df[ck], sig.loc[ck, m], side, prim, fee_micro)
        tradable = bool(held and mon["money_lb_r"] > 0)
        rows.append({"section": "B_test", "measure": m, "period": "choice", "side": "follow" if side > 0 else "fade",
                     **c, "p_two_choice": p_choice[i], "survives_choice": bool(disc[i])})
        rows.append({"section": "B_test", "measure": m, "period": "check", "side": "follow" if side > 0 else "fade",
                     **k, "check_effect_chosen": kc, "check_p_one": p1, "late_effect_chosen": klc, "holds": held,
                     **mon, "tradable": tradable})
        surv += [m] if disc[i] else []
        holds += [m] if held else []
        trad += [m] if tradable else []
    # ---- beside: every measure at every slot (the Benjamini-Hochberg listing over all of them on CHOICE), per year,
    # the wider width and the late entry, and each slot's long and short baseline
    cells = []
    for m in MEASURES:
        for slot in q["slot_labels"]:
            sl = (df["slot"] == slot).to_numpy()
            ce = effect(df[ch & sl], sig.loc[ch & sl, m], pl, ps)
            ke = effect(df[ck & sl], sig.loc[ck & sl, m], pl, ps)
            cells.append((m, slot, ce, ke))
    listing = bh([_p_two(c[2]["t"]) for c in cells], Q_FDR)
    for (m, slot, ce, ke), hit in zip(cells, listing):
        rows.append({"section": "slot", "measure": m, "slot": slot, "period": "choice", **ce, "bh_listed": bool(hit)})
        rows.append({"section": "slot", "measure": m, "slot": slot, "period": "check", **ke})
    for m in MEASURES:
        for y in sorted(df["year"].unique()):
            sy = (df["year"] == y).to_numpy()
            rows.append({"section": "year", "measure": m, "year": int(y), **effect(df[sy], sig.loc[sy, m], pl, ps)})
        for lab, dl in ((wide, 0), (prim, 60), (wide, 60)):
            for per, mask in (("choice", ch), ("check", ck)):
                rows.append({"section": "sensitivity", "measure": m, "period": per, "width": lab, "delay": dl,
                             **effect(df[mask], sig.loc[mask, m], f"o_{lab}_d{dl}_L", f"o_{lab}_d{dl}_S")})
    for slot in q["slot_labels"]:
        sl = (df["slot"] == slot).to_numpy()
        d = df[sl]
        ok = (d[pl] != "-") & (d[ps] != "-")
        rows.append({"section": "baseline", "slot": slot, "n": int(ok.sum()), "slot_days": int(len(d)),
                     "follow_win": float((d.loc[ok, pl] == "t").mean()) if ok.any() else float("nan"),
                     "fade_win": float((d.loc[ok, ps] == "t").mean()) if ok.any() else float("nan"),
                     "width_ticks_median": float(d[f"w_{prim}"].median())})
    rows.append({"section": "verdict", "q_fdr": Q_FDR, "fee_micro": fee_micro, "A_holds": held_a,
                 "A_tradable": bool(held_a and mon_a["money_lb_r"] > 0), "survivors": ";".join(surv) or "none",
                 "holds": ";".join(holds) or "none", "tradable": ";".join(trad) or "none"})
    return pd.DataFrame(rows)


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import yaml

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    if cfg.get("status") != "fixed":
        print("REFUSED: config/flip_anytime.yaml is not fixed.")
        return 2
    src = rd / f"manual_{RUN.replace('-', '_')}.csv"
    if not src.exists():
        print(f"REFUSED: {src.name} is not ingested; run the kit and scripts/ingest_flip_run.py first.")
        return 2
    fee = float(FillModel.load("assumed").round_turn_by_instrument["MNQ"])
    out = score(read_result(src), cfg, fee)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for m in ("A_hint:A1_last1_follow",) + tuple(f"B:{x}" for x in MEASURES):
        counter.record(prereg_id="D-373:flip_anytime", seed=0, exploratory=True,
                       params={"test": m, "config": "config/flip_anytime.yaml", "run": RUN},
                       label=f"any-time direction atlas: {m} (D-373)")
    n_var = len({r["variant_id"] for r in counter.all() if r.get("prereg_id") == "D-373:flip_anytime"})
    write_result(out, "flip_anytime_nq", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, variant_count=n_var,
                 parameters={"config": "config/flip_anytime.yaml", "run": RUN, "measures": list(MEASURES),
                             "q_fdr": Q_FDR, "p_one": P_ONE, "nw_lag": NW_LAG, "fee_micro": fee,
                             "fee_source": "config/fills.yaml round_turn_by_instrument MNQ", "decision": "D-373"},
                 notes={"status": "EXPLORATORY: a screen, not a strategy; a rule that holds becomes a candidate record "
                                  "(D-191) by its own row"},
                 description="EXPLORATORY: the any-time direction atlas -- whether a measure known at a moment tells the "
                             "side of the next move at every half hour of NQ's regular session (2020 to June 2025): "
                             "the 2022 hint at the slots it was not seen at, each measure pooled over the slots on "
                             "CHOICE and CHECK, the money, per slot, per year and sensitivities.")
    v = out[out["section"] == "verdict"].iloc[0]
    print(f"A (the hint at the other slots): holds {v['A_holds']}, tradable {v['A_tradable']}; B survivors on CHOICE: "
          f"{v['survivors']}; hold on CHECK: {v['holds']}; tradable: {v['tradable']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
