"""EXPLORATORY (D-371): the flip-direction atlas's screen -- does anything known before 08:30 CT tell the side of the
open's first move? -- by the rules fixed in config/flip_direction.yaml before its data was read.

    python scripts/score_flip_direction.py          # reads results/manual_R142_flipdir_NQ.csv

Per measure (F01 to F10) a signal +1, -1 or 0 per day; on the days with a signal and both primary brackets entered
(0.05 x ATR20, on time), z = 1 when the FOLLOW side reached its target first, -1 when the FADE side did, 0 otherwise;
the effect is mean z (follow's win share less fade's), its Newey-West standard error over the period's days (lag 5).
CHOICE (2010-2019): two-sided p per measure, Benjamini-Hochberg at q = 0.10 across the ten; a survivor's side is follow
when its effect is positive, else fade. CHECK (2020 to June 2025): a survivor holds when the chosen side's effect is
positive, its one-sided p below 0.05 and at least half the CHOICE size. The money, on CHECK, at the declared flip (20
points, on time): the chosen side's net outcome per attempt in units of the risk, less the flip's measured cost, and its
one-sided 95 % Newey-West lower bound -- TRADABLE when a measure holds and that bound is above zero. Every measure's rows
are written whatever it does; per-year rows and the sensitivities (the 0.03 and 0.08 widths, the late entry) beside,
and the share of days walked on minute bars (`res` 2) in the baseline rows.

Writes results/flip_direction_nq.csv with its manifest; the ten tests are recorded in results/variants.jsonl
(family flip_direction, D-371).
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/score_flip_direction.py"
CONFIG = ROOT / "config" / "flip_direction.yaml"
RUN = "R142-flipdir-NQ"
MEASURES = ("F01_gap", "F02_overnight", "F03_last60", "F04_last15", "F05_last1", "F06_range_position", "F07_prior_rth",
            "F08_prior_close_location", "F09_release_reaction", "F10_big_gap")
Q_FDR = 0.10
CHECK_P = 0.05
NW_LAG = 5


def _sign(x) -> int:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return 0
    return 1 if x > 0 else (-1 if x < 0 else 0)


def _thirds(a, b) -> int:
    """+1 when a / (a + b) is at or above two thirds, -1 at or below one third, else 0 (a, b the room below and above)."""
    if a is None or b is None or (isinstance(a, float) and math.isnan(a)) or (isinstance(b, float) and math.isnan(b)):
        return 0
    s = float(a) + float(b)
    if s <= 0:
        return 0
    pos = float(a) / s
    return 1 if pos >= 2.0 / 3.0 - 1e-12 else (-1 if pos <= 1.0 / 3.0 + 1e-12 else 0)


def big_gap_cut(df: pd.DataFrame, choice: tuple[str, str]) -> float:
    """F10's cut: the two-thirds quantile of |gap| / ATR20 over the CHOICE days that carry both."""
    d = df[(df["date"] >= choice[0]) & (df["date"] <= choice[1])]
    r = (d["gap"].abs() / d["atr"]).replace([np.inf, -np.inf], np.nan).dropna()
    return float(np.quantile(r, 2.0 / 3.0)) if len(r) else float("nan")


def signals(df: pd.DataFrame, release_days: set[str], cut: float) -> pd.DataFrame:
    """Each measure's signal per day (+1, -1, 0), by config/flip_direction.yaml's definitions."""
    g = df["gap"].astype(float)
    out = pd.DataFrame(index=df.index)
    out["F01_gap"] = [_sign(x) for x in g]
    out["F02_overnight"] = [_sign(x) for x in df["on"].astype(float)]
    out["F03_last60"] = [_sign(x) for x in df["m60"].astype(float)]
    out["F04_last15"] = [_sign(x) for x in df["m15"].astype(float)]
    out["F05_last1"] = [_sign(x) for x in df["b1"].astype(float)]
    out["F06_range_position"] = [_thirds(lo, hi) for lo, hi in zip(df["onlo"].astype(float), df["onhi"].astype(float))]
    out["F07_prior_rth"] = [_sign(x) for x in df["prth"].astype(float)]
    out["F08_prior_close_location"] = [_thirds(lo, hi) for lo, hi in zip(df["prlo"].astype(float), df["prhi"].astype(float))]
    out["F09_release_reaction"] = [(_sign(m) if d in release_days else 0) for d, m in zip(df["date"], df["m60"].astype(float))]
    ratio = (g.abs() / df["atr"].astype(float)).replace([np.inf, -np.inf], np.nan)
    out["F10_big_gap"] = [(_sign(x) if (r == r and cut == cut and r >= cut - 1e-12) else 0) for x, r in zip(g, ratio)]
    return out


def nw_se(z: np.ndarray, lag: int = NW_LAG) -> float:
    """Newey-West standard error of the mean of z (Bartlett weights, `lag` days)."""
    n = len(z)
    if n < 2:
        return float("nan")
    e = z - z.mean()
    v = float(e @ e) / n
    for k in range(1, min(lag, n - 1) + 1):
        v += 2.0 * (1.0 - k / (lag + 1.0)) * float(e[k:] @ e[:-k]) / n
    return math.sqrt(max(v, 0.0) / n)


def _p_two(t: float) -> float:
    return float(math.erfc(abs(t) / math.sqrt(2.0))) if t == t else float("nan")


def _p_one(t: float) -> float:
    return float(0.5 * math.erfc(t / math.sqrt(2.0))) if t == t else float("nan")


def effect(df: pd.DataFrame, sig: pd.Series, col_l: str, col_s: str) -> dict:
    """On the days with a signal and both brackets entered: n, follow's and fade's win shares, the effect (mean z), its
    Newey-West standard error and t."""
    ok = (sig != 0) & (df[col_l] != "-") & (df[col_s] != "-")
    s = sig[ok].to_numpy()
    lo, so = df.loc[ok, col_l].to_numpy(), df.loc[ok, col_s].to_numpy()
    fol = np.where(s > 0, lo, so)
    fad = np.where(s > 0, so, lo)
    z = (fol == "t").astype(float) - (fad == "t").astype(float)
    n = len(z)
    if not n:
        return {"n": 0, "follow_win": float("nan"), "fade_win": float("nan"), "effect": float("nan"), "se": float("nan"),
                "t": float("nan")}
    se = nw_se(z)
    eff = float(z.mean())
    return {"n": int(n), "follow_win": float((fol == "t").mean()), "fade_win": float((fad == "t").mean()),
            "effect": eff, "se": se, "t": eff / se if se and se > 0 else float("nan")}


def money(df: pd.DataFrame, sig: pd.Series, side: int, label: str, tick: float, width_points: float, cost_r: float) -> dict:
    """The chosen side's (`side` +1 follow, -1 fade) outcome at the declared flip, on time, per attempt in units of the
    risk: +1 at the target, -1 at the stop, the scratch's P&L over the width; less `cost_r`; its mean, Newey-West
    one-sided 95 % lower bound and win share, on the days with a signal and both brackets entered."""
    cl, cs = f"o_{label}_d0_L", f"o_{label}_d0_S"
    ok = (sig != 0) & (df[cl] != "-") & (df[cs] != "-")
    d = df[ok]
    trade = sig[ok].to_numpy() * side
    kind = np.where(trade > 0, d[cl].to_numpy(), d[cs].to_numpy())
    xs = np.where(trade > 0, d[f"xs_{label}_L"].astype(float).to_numpy(), d[f"xs_{label}_S"].astype(float).to_numpy())
    r = np.where(kind == "t", 1.0, np.where(kind == "s", -1.0, np.nan_to_num(xs) * tick / width_points)) - cost_r
    if not len(r):
        return {"money_n": 0, "money_win": float("nan"), "money_mean_r": float("nan"), "money_lb_r": float("nan")}
    se = nw_se(r)
    return {"money_n": int(len(r)), "money_win": float((kind == "t").mean()), "money_mean_r": float(r.mean()),
            "money_lb_r": float(r.mean() - 1.6448536269514722 * se) if se == se else float("nan")}


def bh(p: list[float], q: float) -> list[bool]:
    """Benjamini-Hochberg at q: which of the p-values are discoveries."""
    m = len(p)
    order = sorted(range(m), key=lambda i: (p[i] if p[i] == p[i] else 2.0))
    k = 0
    for rank, i in enumerate(order, start=1):
        if p[i] == p[i] and p[i] <= rank / m * q:
            k = rank
    keep = set(order[:k])
    return [i in keep for i in range(m)]


def score(df: pd.DataFrame, cfg: dict, release_days: set[str], cost_r: float) -> pd.DataFrame:
    """The screen's rows: per measure and period (`section` test), per measure, period and year (`year`), the
    sensitivities (`sensitivity`), and one verdict row."""
    from propedge.data import flip_kit as fk

    q = fk.params_direction(cfg)
    labels = q["width_labels"]
    prim = labels[q["primary"]]
    fixed = labels[len(q["fractions"])]
    tick = float(q["tick"])
    width_points = float(cfg["widths"]["fixed_points"][0])
    ch, ck = tuple(cfg["periods"]["choice"]), tuple(cfg["periods"]["check"])
    df = df.sort_values("date").reset_index(drop=True)
    cut = big_gap_cut(df, ch)
    sig = signals(df, release_days, cut)
    period = np.where((df["date"] >= ch[0]) & (df["date"] <= ch[1]), "choice",
                      np.where((df["date"] >= ck[0]) & (df["date"] <= ck[1]), "check", ""))
    pl, ps = f"o_{prim}_d0_L", f"o_{prim}_d0_S"
    rows = []
    stats = {}
    for m in MEASURES:
        for per in ("choice", "check"):
            sel = period == per
            d, s = df[sel], sig.loc[sel, m]
            entered = int(((d[pl] != "-") & (d[ps] != "-")).sum())
            e = effect(d, s, pl, ps)
            stats[(m, per)] = e
            rows.append({"section": "test", "measure": m, "period": per, **e,
                         "coverage": e["n"] / entered if entered else float("nan"), "days_entered": entered})
    p_choice = [_p_two(stats[(m, "choice")]["t"]) for m in MEASURES]
    disc = bh(p_choice, Q_FDR)
    verdict = {"section": "verdict", "q_fdr": Q_FDR, "big_gap_cut": cut, "cost_r": cost_r, "survivors": "", "holds": "",
               "tradable": ""}
    surv, holds, trad = [], [], []
    for i, m in enumerate(MEASURES):
        c, k = stats[(m, "choice")], stats[(m, "check")]
        side = 1 if (c["effect"] == c["effect"] and c["effect"] > 0) else -1
        kc = side * k["effect"] if k["effect"] == k["effect"] else float("nan")
        kt = kc / k["se"] if (k["se"] == k["se"] and k["se"] > 0) else float("nan")
        p1 = _p_one(kt)
        held = bool(disc[i] and kc == kc and kc > 0 and p1 < CHECK_P and kc >= 0.5 * abs(c["effect"]) - 1e-12)
        mon = money(df[period == "check"], sig.loc[period == "check", m], side, fixed, tick, width_points, cost_r)
        tradable = bool(held and mon["money_lb_r"] == mon["money_lb_r"] and mon["money_lb_r"] > 0)
        for r in rows:
            if r["section"] == "test" and r["measure"] == m:
                r.update({"p_two_choice": p_choice[i], "survives_choice": bool(disc[i]),
                          "side": "follow" if side > 0 else "fade"})
                if r["period"] == "check":
                    r.update({"check_effect_chosen": kc, "check_p_one": p1, "holds": held, **mon, "tradable": tradable})
        if disc[i]:
            surv.append(m)
        if held:
            holds.append(m)
        if tradable:
            trad.append(m)
    verdict.update({"survivors": ";".join(surv) or "none", "holds": ";".join(holds) or "none",
                    "tradable": ";".join(trad) or "none"})
    # beside: per year, and the sensitivities (descriptions, not tests)
    for m in MEASURES:
        for y in sorted(df["year"].unique()):
            sel = (df["year"] == y).to_numpy() & (period != "")
            e = effect(df[sel], sig.loc[sel, m], pl, ps)
            rows.append({"section": "year", "measure": m, "period": str(period[sel][0]) if sel.any() else "", "year": int(y), **e})
        for lab in labels[:len(q["fractions"])]:
            for dl in q["delays"]:
                if lab == prim and dl == 0:
                    continue
                for per in ("choice", "check"):
                    sel = period == per
                    e = effect(df[sel], sig.loc[sel, m], f"o_{lab}_d{dl}_L", f"o_{lab}_d{dl}_S")
                    rows.append({"section": "sensitivity", "measure": m, "period": per, "width": lab, "delay": dl, **e})
    # beside: the no-signal baseline -- the long and the short bracket on every entered day
    for per in ("choice", "check"):
        d = df[period == per]
        ok = (d[pl] != "-") & (d[ps] != "-")
        rows.append({"section": "baseline", "period": per, "n": int(ok.sum()),
                     "follow_win": float((d.loc[ok, pl] == "t").mean()) if ok.any() else float("nan"),
                     "fade_win": float((d.loc[ok, ps] == "t").mean()) if ok.any() else float("nan"),
                     # the share walked on minute bars (no second bar came): it can dilute an effect, never make one
                     "minute_share": float((d.loc[ok, "res"] == 2).mean()) if (ok.any() and "res" in d) else float("nan")})
    rows.append(verdict)
    return pd.DataFrame(rows)


def cost_of_flip(rd: Path) -> float:
    """The declared flip's measured cost per attempt in units of its risk: results/flip_map_nq_seconds_micros.csv, the
    08:30 CT, 20-point, on-time, pooled cell (D-346)."""
    from propedge.reporting.results import read_result

    t = read_result(rd / "flip_map_nq_seconds_micros.csv")
    c = t[(t["section"] == "cell") & (t["decision_ct"].astype(str) == "08:30") & np.isclose(t["width_points"].astype(float), 20.0)
          & np.isclose(t["delay_min"].astype(float), 0.0) & (t["year"].astype(str) == "pooled")]
    if len(c) != 1:
        raise SystemExit("REFUSED: no single 08:30 / 20-point / on-time pooled cell in flip_map_nq_seconds_micros.csv.")
    return float(c.iloc[0]["cost_r"])


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import yaml

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import read_result, write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    if cfg.get("status") != "fixed":
        print("REFUSED: config/flip_direction.yaml is not fixed.")
        return 2
    src = rd / f"manual_{RUN.replace('-', '_')}.csv"
    if not src.exists():
        print(f"REFUSED: {src.name} is not ingested; run the kit and scripts/ingest_flip_run.py first.")
        return 2
    df = read_result(src)
    cal = pd.read_csv(ROOT / "data" / "release_days_0830_2009_2025.csv")
    release_days = set(cal["date"].astype(str))
    cost_r = cost_of_flip(rd)
    out = score(df, cfg, release_days, cost_r)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for m in MEASURES:
        counter.record(prereg_id="D-371:flip_direction", seed=0, exploratory=True,
                       params={"measure": m, "config": "config/flip_direction.yaml", "run": RUN},
                       label=f"flip-direction atlas: {m} (D-371)")
    n_var = len({r["variant_id"] for r in counter.all() if r.get("prereg_id") == "D-371:flip_direction"})
    write_result(out, "flip_direction_nq", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, variant_count=n_var,
                 parameters={"config": "config/flip_direction.yaml", "run": RUN, "measures": list(MEASURES),
                             "q_fdr": Q_FDR, "check_p": CHECK_P, "nw_lag": NW_LAG, "periods": cfg["periods"],
                             "cost_source": "results/flip_map_nq_seconds_micros.csv (08:30, 20 points, on time, pooled)",
                             "release_days": "data/release_days_0830_2009_2025.csv", "decision": "D-371"},
                 notes={"status": "EXPLORATORY: a screen, not a strategy; a measure that holds becomes a candidate record "
                                  "(D-191) and enters the flip's table only by its own row"},
                 description="EXPLORATORY: the flip-direction atlas -- whether a measure known before 08:30 CT tells the "
                             "side of the open's first move (NQ, 2010 to June 2025): effects on CHOICE and CHECK, the "
                             "false-discovery correction, the money at the declared flip, per year and sensitivities.")
    v = out[out["section"] == "verdict"].iloc[0]
    print(f"survivors on CHOICE: {v['survivors']}; hold on CHECK: {v['holds']}; tradable: {v['tradable']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
