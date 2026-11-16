"""EXPLORATORY development reading (T15 item 9; D-249, D-250): ORB1's fingerprints and trades on NQ and ES, 2009-2019,
by rules fixed in config/orb_model.yaml before any record was read.

    python scripts/score_orb_dev.py

Reads the development runs R099 (NQ) and R100 (ES) (`propedge/data/orb_parser.py`'s table, a row per day and range),
drops FOMC days (`config/im2_release_calendar.csv`, code FOMC), and refuses any record dated 2020 or later -- the check
years are a separate run, read only under a registration.

* **Fingerprints**, per range (5, 15, 30, 60 minutes), on every day with a direction (doji days have none), in units of
  the ATR so years compare: P1 the signed drift after the range at 30, 60, 120 minutes and at 15:08 -- present if its
  lower bound is above zero at all four; P2 the paper exit's edge in R and the drift at 15:08 by relative volume, at or
  above 100 % against below -- present if both rise and the edge's difference has its lower bound above zero (the
  paper's own claim is about the edge, its Fig. 4); P3 the drift per minute in each interval -- has its sign if it falls
  interval by interval; P4 the drift by the overnight gap's size against the ATR, top third against bottom (higher); P5
  by the pre-open's relative volume, top third against bottom (higher); P6 by the ATR against its own past year, top
  third against bottom (higher). P4-P6 split the whole sample into thirds: descriptive, never a selection. P7 (D-250)
  the 5-minute range's paper-exit edge less each longer range's, filtered trades, both markets (higher). Each with the
  yearly estimates' one-sided 95 % lower bound and whether it has the predicted sign. The ladder reads the 5-minute
  range's P1 and P2; the others are reported.
* **Trades**, the paper's filter (each range's relative volume at least 100 %), net of costs in R (the micro's round
  turn and D-95's tick on a stop exit and on the flatten over the stop's dollars per micro; the entry tick is in the
  fill): the paper's exit (stop, or the 15:08 close) and the bracket exit at each R (target first, else stop, else the
  15:08 close; D-212's finish share beside). Five entry sets: each range alone, and the COMBO -- every range's trade, NQ
  and ES one group (D-55), an entry opposite a position still open in either market skipped (D-250). Per market and both
  together: trades, trades per day, the net edge, its yearly lower bound at 95 % and at one-sided 0.05 / 35 (the
  ladder's: 5 entry sets x 7 exits).
* **The ladder** (D-249, D-250): the 5-minute range's P1 and P2 present -> the mechanism lives; then, on both markets
  together, an entry set and exit with at least `min_trades` trades, a lower bound above zero at 0.05 / 35 and (a
  bracket) D-212's finish -> pre-register the check; P1 or P2 absent -> stop. Both markets must be ingested.

Writes results/orb_dev_score.csv: `fingerprint`, `trade` and `summary` rows. k = 2 markets x 5 entry sets x 7 exits,
reported.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.outcomes.orb_core import FLAT_ENTRY, MISSING, OR_MINS  # noqa: E402

SCRIPT = "scripts/score_orb_dev.py"
DEV_END = 2019
HZ = {"drift_30": 30, "drift_60": 60, "drift_120": 120}
COMBO = "combo"
ENTRY_SETS = tuple(OR_MINS) + (COMBO,)


def entry_set(es) -> str:
    """The trade rows' label: '5m', '15m', '30m', '60m' or 'combo' (a string column, never mixed with numbers)."""
    return COMBO if es == COMBO else f"{int(es)}m"


def load(results_dir: Path) -> tuple[pd.DataFrame, list[str]]:
    from propedge.data.orb_kit import ORB_RUNS

    frames, have = [], []
    for market, run in ORB_RUNS.items():
        f = results_dir / f"manual_{run.replace('-', '_')}.csv"
        if f.exists():
            frames.append(pd.read_csv(f, low_memory=False))
            have.append(market)
    if not frames:
        return pd.DataFrame(), have
    d = pd.concat(frames, ignore_index=True)
    d = d[d["kind"] == "day"].copy()
    d["or_minutes"] = d["or_minutes"].astype(int)
    return d, have


def fomc_dates(path: Path | None = None) -> set[str]:
    cal = pd.read_csv(path or ROOT / "config" / "im2_release_calendar.csv")
    return set(cal.loc[cal["code"] == "FOMC", "date"].astype(str))


def bound(by_year: pd.Series, alpha: float = 0.05) -> float:
    """The yearly estimates' mean less the one-sided (1 - alpha) t quantile times their standard error."""
    from scipy import stats

    y = by_year.dropna().astype(float)
    if len(y) < 2:
        return float("nan")
    return float(y.mean() - stats.t.ppf(1 - alpha, len(y) - 1) * y.std(ddof=1) / math.sqrt(len(y)))


def _diff_rows(d: pd.DataFrame, value: str, split: pd.Series, name: str, label: str) -> dict:
    """The mean of `value` where `split` is True less where it is False, overall and its yearly bound."""
    hi, lo = d[split], d[~split]
    by = hi.groupby("year")[value].mean() - lo.groupby("year")[value].mean()
    diff = float(hi[value].mean() - lo[value].mean()) if len(hi) and len(lo) else float("nan")
    lb = bound(by)
    return {"section": "fingerprint", "test": name, "label": label, "n_high": len(hi), "n_low": len(lo),
            "estimate": diff, "lower_bound": lb, "predicted_sign": "+", "has_sign": bool(diff > 0),
            "present": bool(lb > 0)}


def _tercile_split(x: pd.Series) -> pd.Series:
    """True for the top third, False for the bottom third, NaN for the middle (dropped)."""
    q1, q2 = x.quantile(1 / 3), x.quantile(2 / 3)
    return pd.Series(np.where(x >= q2, 1.0, np.where(x <= q1, 0.0, np.nan)), index=x.index)


def trade_r(d: pd.DataFrame, tick_dollars: float, fee: float, slip_ticks: float, R: float | None,
            rr: tuple[float, ...], flat_slip_ticks: float | None = None) -> pd.DataFrame:
    """Each filled row's trade in R, net: R None the paper's exit, else the bracket at R. Columns r, finished and
    exit_slot (the bar it ends on: the target's, the stop's, or the flatten's)."""
    f = d[d["fill_slot"] != -1].copy()
    stop_d = f["stop_ticks"] * tick_dollars
    stop_cost = (fee + slip_ticks * tick_dollars) / stop_d
    flat_cost = (fee + (slip_ticks if flat_slip_ticks is None else flat_slip_ticks) * tick_dollars) / stop_d
    stopped = f["stop_slot"] != -1
    loss = -1.0 - f["overshoot_tenths"] / 10.0 / f["stop_ticks"] - stop_cost
    flat = f["close_ticks"] / f["stop_ticks"] - flat_cost
    unstopped = np.where(stopped, f["stop_slot"], FLAT_ENTRY)
    if R is None:
        f["r"] = np.where(stopped, loss, flat)
        f["finished"] = stopped
        f["exit_slot"] = unstopped
    else:
        tgt = f[f"target_{R:g}_slot"]
        hit = tgt != -1
        f["r"] = np.where(hit, R - fee / stop_d, np.where(stopped, loss, flat))
        f["finished"] = hit | stopped
        f["exit_slot"] = np.where(hit, tgt, unstopped)
    return f


def combo(t: pd.DataFrame, markets: tuple[str, ...]) -> tuple[pd.DataFrame, int]:
    """The COMBO's trades from every range's (`t`: trade_r rows with or_minutes and market), NQ and ES one group: taken
    in fill-bar order (then the shorter range, then the markets' order), an entry skipped when a position in the
    opposite direction is open on its fill bar (from that position's fill bar to its exit bar, both counted). Returns
    (the trades kept, the number skipped)."""
    rank = {m: i for i, m in enumerate(markets)}
    t = t.assign(_m=t["market"].map(rank)).sort_values(["date", "fill_slot", "or_minutes", "_m"], kind="stable")
    keep, skipped = [], 0
    for _, g in t.groupby("date", sort=False):
        open_ = []
        for idx, d, fs, xs in zip(g.index, g["dir"], g["fill_slot"], g["exit_slot"]):
            if any(od == -d and ox >= fs for od, ox in open_):
                skipped += 1
                continue
            open_.append((d, xs))
            keep.append(idx)
    return t.loc[keep].drop(columns="_m"), skipped


def fingerprints(d: pd.DataFrame, paper_r: pd.Series | None = None) -> list[dict]:
    """`d`: one range's rows. `paper_r`: each filled row's paper-exit trade in R (index of `d`), for P2's edge."""
    rows = []
    x = d[d["dir"] != 0].copy()
    for c in list(HZ) + ["drift_flat"]:
        x[c + "_atr"] = x[c] / x["atr_ticks"]
    for c in list(HZ) + ["drift_flat"]:                                         # P1
        m = float(x[c + "_atr"].mean())
        lb = bound(x.groupby("year")[c + "_atr"].mean())
        rows.append({"section": "fingerprint", "test": "P1", "label": f"signed drift, {c}", "n_high": len(x),
                     "estimate": m, "lower_bound": lb, "predicted_sign": "+", "has_sign": bool(m > 0),
                     "present": bool(lb > 0)})
    x["rv_high"] = x["rv100"] >= 100                                             # P2
    p2d = _diff_rows(x, "drift_flat_atr", x["rv_high"], "P2", "drift at 15:08, relative volume >= 100 % vs below")
    p2d["test"] = "P2_drift"
    rows.append(p2d)
    if paper_r is not None:
        y = x.join(paper_r.rename("paper_r"), how="inner")
        p2 = _diff_rows(y, "paper_r", y["rv_high"], "P2", "paper exit edge (R), relative volume >= 100 % vs below")
        p2["present"] = bool(p2["present"] and p2d["has_sign"])
        rows.append(p2)
    prev, prev_m, per_min = 0.0, 0, []                                         # P3
    for c, m in HZ.items():
        per = (x[c + "_atr"] - (x[prev] / x["atr_ticks"] if prev else 0.0)) / (m - prev_m)
        per_min.append(float(per.mean()))
        rows.append({"section": "fingerprint", "test": "P3", "label": f"drift per minute, {prev_m}-{m} min",
                     "n_high": len(x), "estimate": per_min[-1], "lower_bound": bound(per.groupby(x["year"]).mean()),
                     "predicted_sign": "falling", "has_sign": pd.NA, "present": pd.NA})
        prev, prev_m = c, m
    falling = all(a > b for a, b in zip(per_min, per_min[1:]))
    for r in rows:
        if r["test"] == "P3":
            r["has_sign"] = falling
    for test, raw, label in (("P4", (x["gap_ticks"].where(x["gap_ticks"] != MISSING).abs() / x["atr_ticks"]),
                              "overnight gap / ATR, top third vs bottom"),
                             ("P5", x["pre_rv100"].where(x["pre_rv100"] != -1).astype(float),
                              "pre-open relative volume, top third vs bottom"),
                             ("P6", _atr_state(x), "ATR against its past year, top third vs bottom")):
        s = _tercile_split(raw)
        keep = s.notna()
        rows.append(_diff_rows(x[keep], "drift_flat_atr", s[keep] == 1.0, test, label))
    return rows


def p7(paper: dict[int, pd.DataFrame]) -> list[dict]:
    """P7 (D-250): the 5-minute range's paper-exit edge less each longer range's, filtered trades on both markets."""
    rows, base = [], paper[OR_MINS[0]]
    for n in OR_MINS[1:]:
        o = paper[n]
        by = base.groupby("year")["r"].mean() - o.groupby("year")["r"].mean()
        est = float(base["r"].mean() - o["r"].mean()) if len(base) and len(o) else float("nan")
        lb = bound(by)
        rows.append({"section": "fingerprint", "test": "P7", "or_minutes": n,
                     "label": f"paper exit edge (R), 5-minute range less the {n}-minute", "n_high": len(base),
                     "n_low": len(o), "estimate": est, "lower_bound": lb, "predicted_sign": "+",
                     "has_sign": bool(est > 0), "present": bool(lb > 0)})
    return rows


def _atr_state(x: pd.DataFrame) -> pd.Series:
    """Each day's ATR over the median ATR of the market's previous 250 records (past only)."""
    out = pd.Series(np.nan, index=x.index)
    for _, g in x.sort_values("date").groupby("market"):
        med = g["atr_ticks"].rolling(250, min_periods=60).median().shift(1)
        out.loc[g.index] = g["atr_ticks"] / med
    return out


def trades(d: pd.DataFrame, cfg: dict, fees: dict, slip_ticks: float, flat_slip_ticks: float | None = None
           ) -> list[dict]:
    from propedge.data.orb_kit import MARKETS, params

    rows = []
    rr = tuple(float(r) for r in cfg["exits"]["bracket"]["rr"])
    family = len(ENTRY_SETS) * (1 + len(rr))
    if family != int(cfg["screen"]["edge_alpha_over"]):
        raise ValueError(f"the ladder's family is {family}, the config says {cfg['screen']['edge_alpha_over']}")
    min_trades = int(cfg["screen"]["min_trades"])
    rv_min = float(cfg["fixed"]["relative_volume"]["min"])
    finish_min = float(cfg["exits"]["bracket"]["finish_min"])
    x = d[(d["dir"] != 0) & (d["rv100"] >= 100 * rv_min)]
    days = {m: d.loc[d["market"] == m, "date"].nunique() for m in d["market"].unique()}
    days["both"] = d["date"].nunique()
    per = {}                                       # (entry set, R) -> every market's trades
    for R in (None, *rr):
        by_n = []
        for market, g in x.groupby("market"):
            q = params(market, cfg)
            by_n.append(trade_r(g, q["micro_tick"] * q["micro_point_value"], float(fees[q["micro"]]), slip_ticks,
                                R, rr, flat_slip_ticks))
        allr = pd.concat(by_n) if by_n else x.iloc[0:0]
        for n in OR_MINS:
            per[(n, R)] = (allr[allr["or_minutes"] == n], 0)
        per[(COMBO, R)] = combo(allr, tuple(m for m in MARKETS if m in days))
    for es in ENTRY_SETS:
        for scope in sorted(m for m in days if m != "both") + ["both"]:
            for R in (None, *rr):
                t_all, skipped = per[(es, R)]
                t = t_all if scope == "both" else t_all[t_all["market"] == scope]
                by = t.groupby("year")
                fin = by["finished"].mean()
                ym = by["r"].mean()
                rows.append({"section": "trade", "entry_set": entry_set(es), "market": scope,
                             "exit": "paper" if R is None else "bracket", "R": R, "n": len(t),
                             "per_day": len(t) / days[scope] if days[scope] else float("nan"),
                             "skipped_by_lock": skipped if (es == COMBO and scope == "both") else pd.NA,
                             "e_net": float(t["r"].mean()) if len(t) else float("nan"),
                             "lower_bound": bound(ym), "lower_bound_family": bound(ym, 0.05 / family),
                             "enough_trades": len(t) >= min_trades,
                             "worst_year_e_net": float(ym.min()) if len(ym) else float("nan"),
                             "finished_share": float(t["finished"].mean()) if len(t) else float("nan"),
                             "worst_year_finished": float(fin.min()) if len(fin) else float("nan"),
                             "meets_d212": bool(R is not None and len(t) and t["finished"].mean() >= finish_min
                                                and fin.min() >= finish_min)})
    return rows


def main(results_dir: Path | None = None, record: bool = True) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.data.orb_kit import MARKETS, ORB_RUNS, config, params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    d, have = load(rd)
    if d.empty:
        print("REFUSED: no ORB1 development run is ingested yet (R099, R100).")
        return 2
    if (d["year"] > DEV_END).any():
        print("REFUSED: a record dated after 2019 -- the check years are read only under a registration (D-249).")
        return 2
    if set(have) != set(MARKETS):
        print(f"REFUSED: both markets' development runs are needed, ingested: {have} (D-249).")
        return 2
    cfg = config()
    if tuple(cfg["ranges"]["minutes"]) != tuple(OR_MINS):
        print(f"REFUSED: the config's ranges {cfg['ranges']['minutes']} are not the kit's {OR_MINS}.")
        return 2
    d = d[~d["date"].astype(str).isin(fomc_dates())]
    fm = FillModel.load("assumed")
    fees, slip, flat_slip = dict(fm.round_turn_by_instrument), float(fm.stop_slippage_ticks), float(
        fm.flatten_slippage_ticks)

    def paper_of(rows: pd.DataFrame) -> pd.DataFrame:
        return pd.concat([trade_r(g, params(m, cfg)["micro_tick"] * params(m, cfg)["micro_point_value"],
                                  float(fees[params(m, cfg)["micro"]]), slip, None, (), flat_slip)
                          for m, g in rows.groupby("market")])

    fp = []
    rv_min = float(cfg["fixed"]["relative_volume"]["min"])
    filtered = {}
    for n in OR_MINS:
        dn = d[d["or_minutes"] == n]
        fp += [{**r, "or_minutes": n} for r in fingerprints(dn, paper_of(dn[dn["dir"] != 0])["r"])]
        filtered[n] = paper_of(dn[(dn["dir"] != 0) & (dn["rv100"] >= 100 * rv_min)])
    fp += p7(filtered)
    tr = trades(d, cfg, fees, slip, flat_slip)
    f = pd.DataFrame(fp)
    five = f["or_minutes"] == OR_MINS[0]
    p1 = bool(f[five & (f["test"] == "P1")]["present"].astype(bool).all())   # all four horizons, the 5-minute range
    p2 = bool(f[five & (f["test"] == "P2")]["present"].iloc[0])
    t = pd.DataFrame(tr)
    both = t[t["market"] == "both"]
    edge = bool((both["enough_trades"] & (both["lower_bound_family"] > 0)
                 & ((both["exit"] == "paper") | both["meets_d212"])).any())
    k = len(MARKETS) * len(ENTRY_SETS) * (1 + len(cfg["exits"]["bracket"]["rr"]))
    rung = ("stop: the mechanism leaves no fingerprint" if not (p1 and p2) else
            "pre-register the check" if edge else "alive without a net edge: the geometry is the problem")
    raw = pd.concat([pd.read_csv(rd / f"manual_{ORB_RUNS[m].replace('-', '_')}.csv", low_memory=False) for m in have])
    recs = raw[(raw["kind"] == "day") & (raw["or_minutes"] == OR_MINS[0])] if "or_minutes" in raw else raw.iloc[0:0]
    summary = {"section": "summary", "k": k, "markets": ",".join(have), "p1_present": p1, "p2_present": p2,
               "net_edge": edge, "ladder": rung, "days": int((d["or_minutes"] == OR_MINS[0]).sum()),
               # a day with the histories but no opening-range bar writes no record (the pre-run review)
               "history_days_without_record": (int(raw.loc[raw["kind"] == "session", "history_days"].sum())
                                               - len(recs)) if "history_days" in raw else pd.NA}
    out = pd.concat([f, t, pd.DataFrame([summary])], ignore_index=True)
    write_result(out, "orb_dev_score", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"config": "config/orb_model.yaml", "years": [2009, DEV_END], "k": k,
                             "ranges": list(OR_MINS), "entry_sets": [str(e) for e in ENTRY_SETS],
                             "family": int(cfg["screen"]["edge_alpha_over"]),
                             "fomc_excluded": True, "fees": dict(fm.round_turn_by_instrument),
                             "exit_slippage_ticks": float(fm.stop_slippage_ticks),
                             "runs": {m: ORB_RUNS[m] for m in have}, "decision": "D-249, D-250"},
                 notes={"status": "EXPLORATORY: ORB1's development reading by rules fixed before any record "
                                  "(D-249, D-250); the check years are a separate, registered run"},
                 description="EXPLORATORY: ORB1 on NQ and ES, 2009-2019 -- the fingerprints P1-P7 per range with their "
                             "predicted signs, the paper's exit and the bracket exits net of costs for the 5-, 15-, 30- "
                             "and 60-minute ranges and their COMBO, and the ladder's rung. No seed: a deterministic "
                             "reading of day records.")
    if record:
        VariantCounter().record(prereg_id="D-250:orb_dev", seed=0, exploratory=True,
                                params={"study": "ORB1 development reading", "k": k, "markets": have},
                                label="EXPLORATORY: ORB1, four ranges and their COMBO, the paper's exit and six "
                                      "bracket exits per market (deterministic records; the seed is nominal)")
    pd.set_option("display.width", 250)
    print(f[["or_minutes", "test", "label", "estimate", "lower_bound", "has_sign", "present"]].round(4)
          .to_string(index=False))
    print(t[["entry_set", "market", "exit", "R", "n", "per_day", "e_net", "lower_bound", "lower_bound_family",
             "finished_share", "meets_d212"]].round(4).to_string(index=False))
    print(pd.DataFrame([summary]).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
