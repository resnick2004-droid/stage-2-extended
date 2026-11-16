"""ORB3's declared search (T15 item 9; D-256): config/orb3_search.yaml's grid scored on NQ's development years, the
plateau selection, its walk-forward and the kill line W1-W2, all fixed before R102-R104 were read.

    python scripts/score_orb3_search.py

Reads R102-R104 (`propedge/data/orb3_parser.py`'s table) and their run records (`runs/<run>/ingested.json`), drops
FOMC days, refuses any record before 2009-06-01 or on or after 2025-07-01 (the held-back window, D-237).

**A configuration** -- stop width (x the 14-day ATR), exit mode, latest fill, ranges, relative-volume filter -- is
traded one position at a time (`sequential`: fill-bar order, the shorter range first; an entry skipped while a
position is open, its fill bar to its exit bar). Each filled record's outcome, from the grid's first passages:

* the fill bar, when the fill is inside it: the kit's reading stops it there if the bar closes beyond the stop, the
  strict reading if its adverse excursion reaches the stop (D-254); a fill at the bar's open is walked from that bar;
* `bracket` (a leg at R): the stop if reached no later than R x the stop is traded through (equal slots the stop's),
  else the target, else the 15:08 close; `direction`: the stop if reached by 15:08, else the 15:08 close.

The move before any cost in R: -1, the target (R x the stop rounded down to a whole tick, where its limit sits, D-257)
or the 15:08 close over the stop, plus the entry's tick (the kit's fill is one tick beyond the level). The costs (the
`assumed` profile, D-95): the entry's tick, the round-turn fee, the exit's slippage on a stop or the flatten. **The
selection metric** of a trade is its move before any cost less its configuration's median round-trip cost in R over
every filled record of 2020 to June 2025, priced as a stop exit -- the behaviour from every year, the costs of the
market the confirmation trades in, and no outcome in the cost (D-257). A configuration's value on a set of years is
the yearly means' one-sided 95 % lower bound (in bracket mode the smaller of its two legs' bounds, 2R and 1.5R), under
the strict reading.

**Feasible** on a set of years: trades per trading day (every session; a run's early closes shared over its years by
their full sessions) at or above D-154's minimum in each leg; in bracket mode at most 2 % reaching the 15:08 bar,
overall and in every year, in each leg (D-212); and the contract fit on the stops of every filled record of 2020 to
June 2025 -- the Combine at $750 and at least one of $1,000, $750 and $500 funded pass D-201's band, D-190's unsizeable
share and D-212's consistent risk (`score_orb2_screen.fit`). **The plateau**: of the feasible configurations, the one
maximising the smaller of its own value and the median value of every configuration one step from it or fewer in stop
width and in latest fill (same mode, ranges and filter), feasible or not, one with no value counting as the lowest --
neither a lone peak nor a poor cell among good ones (D-257); ties to the earlier configuration in the order mode,
ranges, filter, stop width, latest fill. **Walk-forward**: each test year 2013-2025 scored with the selection made on
every earlier year, the year's value its trades' mean metric (in bracket mode the smaller leg's). **W1** kills if the
test years' values have their one-sided 95 % lower bound at or below zero, or a test year has no feasible selection or
no value; **W2** if the selection on every year is infeasible or its value at or below zero.

Writes results/orb3_search.csv: `grid` (every configuration on every year), `walkforward`, `final`, `kline` and
`summary` rows.
"""
from __future__ import annotations

import io
import json
import math
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from propedge.outcomes.orb_core import FLAT_ENTRY, OR_MINS  # noqa: E402

SCRIPT = "scripts/score_orb3_search.py"
CONFIG = ROOT / "config" / "orb3_search.yaml"
START, HELD_BACK = date(2009, 6, 1), date(2025, 7, 1)
TODAY_FROM = 2020
WF_FIRST = 2013


def config(path: Path | None = None) -> dict:
    return yaml.safe_load(Path(path or CONFIG).read_text(encoding="utf-8"))


def _ct_slot(hhmm: str) -> int:
    from propedge.outcomes.regime_core import slot_of

    h, m = map(int, hhmm.split(":"))
    return slot_of(h, m)


def fomc_dates(cfg: dict) -> set[str]:
    out = set()
    for rel in cfg["fomc"]:
        lines = [ln for ln in (ROOT / rel).read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
        t = pd.read_csv(io.StringIO("\n".join(lines)))
        if "code" in t.columns:
            t = t[t["code"] == "FOMC"]
        out |= set(t["date"].astype(str))
    return out


def load(results_dir: Path, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    days, sessions, have = [], [], []
    for run in cfg["runs"]:
        f = results_dir / f"manual_{run.replace('-', '_')}.csv"
        if f.exists():
            t = pd.read_csv(f, low_memory=False)
            days.append(t[t["kind"] == "day"])
            sessions.append(t[t["kind"] == "session"].assign(run=run))
            have.append(run)
    if not days:
        return pd.DataFrame(), pd.DataFrame(), have
    d = pd.concat(days, ignore_index=True)
    d["or_minutes"] = d["or_minutes"].astype(int)
    return d, pd.concat(sessions, ignore_index=True), have


def trading_days(sessions: pd.DataFrame, runs_dir: Path, cfg: dict) -> dict[int, float] | None:
    """{year: sessions}: each year's full sessions plus its share of its run's early closes (by full sessions)."""
    out: dict[int, float] = {}
    for run, g in sessions.groupby("run"):
        f = runs_dir / run / "ingested.json"
        if not f.exists():
            return None
        early = int(json.loads(f.read_text(encoding="utf-8"))["summary"]["early"])
        full = g.groupby("year")["days"].sum()
        for y, n in full.items():
            out[int(y)] = out.get(int(y), 0.0) + float(n) * (1 + early / float(full.sum()))
    return out


class Grid:
    """The day records as (days x ranges) arrays, and every configuration's one-at-a-time trades."""

    def __init__(self, d: pd.DataFrame, cfg: dict, fee: float, slip: float, flat_slip: float, tick_dollars: float):
        self.cfg, self.fee, self.slip, self.flat_slip, self.td = cfg, fee, slip, flat_slip, tick_dollars
        self.K = len(cfg["search"]["stop_atr"])
        first = d[d["or_minutes"] == OR_MINS[0]].sort_values("date").set_index("date")
        self.dates = first.index.to_numpy()
        self.year = first["year"].to_numpy().astype(int)
        self.stop = np.stack([first[f"stop_ticks_{i}"].to_numpy() for i in range(self.K)], axis=1).astype(float)

        def piv(col):
            return (d.pivot(index="date", columns="or_minutes", values=col).reindex(index=self.dates, columns=OR_MINS)
                    .to_numpy())
        self.f = {c: piv(c) for c in ("dir", "rv100", "fill_slot", "at_open", "fill_bar_close_ticks",
                                      "fill_bar_against_ticks", "close_ticks")}
        self.a = [piv(f"a_{i}") for i in range(self.K)]
        self.f15 = [piv(f"f15_{i}") for i in range(self.K)]
        self.f2 = [piv(f"f2_{i}") for i in range(self.K)]

    def valid(self, last_fill: int, ranges: tuple, rv_min) -> np.ndarray:
        """(days x ranges): a direction, a fill no later than `last_fill`, a range of the set, the filter."""
        f = self.f
        cols = np.array([n in ranges for n in OR_MINS])[None, :]
        out = (f["dir"] != 0) & (f["fill_slot"] != -1) & (f["fill_slot"] <= last_fill) & cols
        if rv_min is not None:
            out &= f["rv100"] >= 100 * float(rv_min)
        return out

    def today(self, i: int, last_fill: int, ranges: tuple, rv_min) -> tuple[float, np.ndarray]:
        """(the median round-trip cost in R, the stops in ticks) of every filled record of 2020 to June 2025 -- before
        one-at-a-time, priced as a stop exit (the entry's tick, the fee, the exit's tick): no outcome enters (D-257)."""
        v = self.valid(last_fill, ranges, rv_min) & (self.year >= TODAY_FROM)[:, None]
        st = np.repeat(self.stop[:, i][:, None], len(OR_MINS), axis=1)[v]
        cost = 1.0 / st + (self.fee + self.slip * self.td) / (st * self.td)
        return (float(np.median(cost)) if len(cost) else float("nan")), st

    def trades(self, i: int, mode: str, last_fill: int, ranges: tuple, rv_min, reading: str, R: float | None):
        """The kept trades of one configuration and leg: a dict of 1-D arrays (year, gross, cost, flat, stop, date)."""
        f = self.f
        valid = self.valid(last_fill, ranges, rv_min)
        st = np.repeat(self.stop[:, i][:, None], len(OR_MINS), axis=1)
        inside = f["at_open"] == 0
        fbs = inside & ((f["fill_bar_close_ticks"] <= -st) if reading == "lenient" else
                        (f["fill_bar_against_ticks"] >= st))
        A = self.a[i]
        if mode == "bracket":
            Fa = (self.f15 if R == 1.5 else self.f2)[i]
            stopped = fbs | ((A != -1) & ((Fa == -1) | (A <= Fa)))
            target = ~stopped & (Fa != -1)
            exit_slot = np.where(fbs, f["fill_slot"], np.where(stopped, A, np.where(target, Fa, FLAT_ENTRY)))
        else:
            stopped = fbs | (A != -1)
            target = np.zeros_like(stopped)
            exit_slot = np.where(fbs, f["fill_slot"], np.where(stopped, A, FLAT_ENTRY))
        flat = ~stopped & ~target
        entry = 1.0 / st
        # the target's limit sits on a whole tick: R x the stop rounded down, which the recorded trade-through of
        # R x the stop also fills (D-257)
        won = np.floor((R or 0.0) * st + 1e-9) / st
        gross = np.where(stopped, -1.0, np.where(target, won, f["close_ticks"] / st)) + entry
        exit_cost = np.where(stopped, self.fee + self.slip * self.td,
                             np.where(target, self.fee, self.fee + self.flat_slip * self.td)) / (st * self.td)
        cost = entry + exit_cost
        kept = sequential_mask(np.where(valid, f["fill_slot"], np.inf), np.where(valid, exit_slot, -1), valid)
        rows, cols_ = np.nonzero(kept)
        return {"year": self.year[rows], "gross": gross[rows, cols_], "cost": cost[rows, cols_],
                "flat": flat[rows, cols_], "stop": st[rows, cols_], "date": self.dates[rows],
                "or_minutes": np.array(OR_MINS)[cols_]}


def sequential_mask(fill: np.ndarray, exit_slot: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """One position at a time, day by day: (days x ranges) -> kept. Fill-bar order, the shorter range (the earlier
    column) first on the same bar; an entry kept only if its fill bar is after the kept position's exit bar."""
    order = np.argsort(fill, axis=1, kind="stable")
    busy = np.full(fill.shape[0], -1.0)
    kept = np.zeros_like(valid, dtype=bool)
    rows = np.arange(fill.shape[0])
    for p in range(fill.shape[1]):
        c = order[:, p]
        fs, xs, ok = fill[rows, c], exit_slot[rows, c], valid[rows, c]
        take = ok & (fs > busy)
        kept[rows[take], c[take]] = True
        busy = np.where(take, xs, busy)
    return kept


def bound(by_year: pd.Series) -> float:
    from scipy import stats

    y = by_year.dropna().astype(float)
    if len(y) < 2:
        return float("nan")
    return float(y.mean() - stats.t.ppf(0.95, len(y) - 1) * y.std(ddof=1) / math.sqrt(len(y)))


def configurations(cfg: dict) -> list[dict]:
    s = cfg["search"]
    out = []
    for mode in s["exit_mode"]:
        for ranges in s["ranges"]:
            for rv in s["relative_volume_min"]:
                for i, sa in enumerate(s["stop_atr"]):
                    for j, cut in enumerate(s["last_fill_ct"]):
                        out.append({"mode": mode, "ranges": tuple(ranges), "rv_min": rv, "i": i, "stop_atr": sa,
                                    "j": j, "last_fill_ct": cut, "last_fill_slot": _ct_slot(cut)})
    return out


def legs_of(c: dict, cfg: dict) -> list[tuple[str, float | None]]:
    if c["mode"] == "direction":
        return [("direction", None)]
    return [("combine", float(cfg["fixed"]["combine"]["rr"])), ("funded", float(cfg["fixed"]["funded"]["rr"]))]


def leg_frame(grid: Grid, c: dict, R, reading: str) -> pd.DataFrame:
    t = pd.DataFrame(grid.trades(c["i"], c["mode"], c["last_fill_slot"], c["ranges"], c["rv_min"], reading, R))
    t["metric"] = t["gross"] - grid.today(c["i"], c["last_fill_slot"], c["ranges"], c["rv_min"])[0]
    t["net"] = t["gross"] - t["cost"]
    return t


def evaluate(grid: Grid, cfg: dict, sessions: dict[int, float], band: pd.DataFrame, fit_fn, need: float):
    """Every configuration's legs under the strict reading, per year, and its contract fit on the stops of every
    filled record of 2020-2025 (D-257: before one-at-a-time, so no outcome enters)."""
    out = []
    for c in configurations(cfg):
        legs = {}
        for name, R in legs_of(c, cfg):
            t = leg_frame(grid, c, R, "strict")
            by = t.groupby("year")
            legs[name] = pd.DataFrame({"n": by.size(), "metric": by["metric"].mean(), "net": by["net"].mean(),
                                       "flat": by["flat"].mean(), "flat_n": by["flat"].sum()})
        st = pd.DataFrame({"market": "NQ", "stop_ticks": grid.today(c["i"], c["last_fill_slot"], c["ranges"],
                                                                    c["rv_min"])[1]})
        stops = pd.concat([st.assign(state="combine"), st.assign(state="funded")], ignore_index=True)
        fit = fit_fn(stops, float(cfg["fixed"]["combine"]["risk"]),
                     [float(r) for r in cfg["fixed"]["funded"]["risk_candidates"]], band)
        comb = next(r for r in fit if r["state"] == "combine")
        funded = next((r for r in fit if r["state"] == "funded" and r["passes"]), None)
        out.append({**c, "legs": legs, "fit_ok": bool(comb["passes"] and funded is not None),
                    "funded_risk": funded["risk"] if funded else float("nan"), "need": need,
                    "sessions": sessions})
    return out


def value_on(e: dict, years: list[int]) -> tuple[bool, float]:
    """(feasible, value) of an evaluated configuration on `years`; the value whether feasible or not (the plateau
    counts every neighbour, D-257). In bracket mode the value is the smaller leg's bound."""
    vals, ok = [], bool(e["fit_ok"])
    days = sum(e["sessions"].get(y, 0.0) for y in years)
    for name, t in e["legs"].items():
        t = t[t.index.isin(years)]
        if not days or t["n"].sum() / days + 1e-9 < e["need"]:
            ok = False
        if e["mode"] == "bracket" and (t["flat_n"].sum() / max(t["n"].sum(), 1) > 0.02 + 1e-12
                                       or (t["flat"] > 0.02 + 1e-12).any()):
            ok = False
        vals.append(bound(t["metric"]))
    v = min(vals) if vals else float("nan")
    return ok and v == v, v


def select(evals: list[dict], years: list[int]) -> tuple[dict | None, float]:
    """The plateau rule on `years`: (the selected configuration, its plateau score) or (None, nan). Only a feasible
    cell is chosen; its plateau is the median of every cell of its 3 x 3 neighbourhood's values, feasible or not, a
    cell with no value counting as the lowest (D-257); its score the smaller of its own value and that median."""
    scored = {}
    for k, e in enumerate(evals):
        ok, v = value_on(e, years)
        scored[k] = (ok, v)
    index = {(e["mode"], e["ranges"], e["rv_min"], e["i"], e["j"]): k for k, e in enumerate(evals)}
    best, best_score = None, -math.inf
    for k, e in enumerate(evals):
        if not scored[k][0]:
            continue
        near = [scored[index[(e["mode"], e["ranges"], e["rv_min"], e["i"] + di, e["j"] + dj)]][1]
                for di in (-1, 0, 1) for dj in (-1, 0, 1)
                if (e["mode"], e["ranges"], e["rv_min"], e["i"] + di, e["j"] + dj) in index]
        near = [x if x == x else -math.inf for x in near]
        score = min(scored[k][1], float(np.median(near)))                       # the cell itself and its plateau
        if score > best_score + 1e-12:
            best, best_score = k, score
    return (evals[best], best_score) if best is not None else (None, float("nan"))


def year_value(e: dict, year: int) -> float:
    vals = [float(t.loc[year, "metric"]) if year in t.index else float("nan") for t in e["legs"].values()]
    return min(vals) if vals else float("nan")


def _key(e: dict | None) -> dict:
    if e is None:
        return {"mode": None}
    return {"mode": e["mode"], "ranges": "+".join(map(str, e["ranges"])), "rv_min": e["rv_min"],
            "stop_atr": e["stop_atr"], "last_fill_ct": e["last_fill_ct"]}


def main(results_dir: Path | None = None, record: bool = True, runs_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result
    from propedge.research.model_card import BAND_FILE, setups_minimum
    from score_orb2_screen import fit as fit_fn

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = config()
    d, sess, have = load(rd, cfg)
    if set(have) != set(cfg["runs"]):
        print(f"REFUSED: ORB3's three runs are needed, ingested: {have}.")
        return 2
    dt = pd.to_datetime(d["date"]).dt.date
    if (dt >= HELD_BACK).any() or (dt < START).any():
        print("REFUSED: a record outside 2009-06-01 to 2025-06-30 -- the held-back window is never read here (D-237).")
        return 2
    sessions = trading_days(sess, Path(runs_dir) if runs_dir is not None else ROOT / "runs", cfg)
    if sessions is None:
        print("REFUSED: a run record (runs/<run>/ingested.json) is missing: the trading days need it.")
        return 2
    k = math.prod(len(v) for v in cfg["search"].values())
    if k != int(cfg["k"]):
        print(f"REFUSED: the grid holds {k} configurations, the config declares {cfg['k']}.")
        return 2
    d = d[~d["date"].astype(str).isin(fomc_dates(cfg))]
    fm = FillModel.load("assumed")
    q = params("NQ")
    grid = Grid(d, cfg, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.stop_slippage_ticks),
                float(fm.flatten_slippage_ticks), q["micro_tick"] * q["micro_point_value"])
    need = setups_minimum(float(cfg["fixed"]["combine"]["rr"]), float(cfg["fixed"]["combine"]["risk"]), 0.0)
    evals = evaluate(grid, cfg, sessions, read_result(BAND_FILE), fit_fn, need)
    years = sorted(sessions)
    rows = []
    for e in evals:
        ok, v = value_on(e, years)
        r = {"section": "grid", **_key(e), "feasible": ok, "value": v, "fit_ok": e["fit_ok"],
             "funded_risk": e["funded_risk"]}
        for name, t in e["legs"].items():
            days = sum(sessions.values())
            r.update({f"{name}_n": int(t["n"].sum()), f"{name}_per_day": t["n"].sum() / days,
                      f"{name}_metric": float((t["metric"] * t["n"]).sum() / max(t["n"].sum(), 1)),
                      f"{name}_net": float((t["net"] * t["n"]).sum() / max(t["n"].sum(), 1)),
                      f"{name}_flat_worst_year": float(t["flat"].max()) if len(t) else float("nan")})
        rows.append(r)
    wf = []
    for T in [y for y in years if y >= WF_FIRST]:
        sel, score = select(evals, [y for y in years if y < T])
        val = year_value(sel, T) if sel is not None else float("nan")
        wf.append(val)
        rows.append({"section": "walkforward", "test_year": T, **_key(sel), "plateau_score": score, "oos_value": val})
    wf_s = pd.Series(wf, index=[y for y in years if y >= WF_FIRST])
    w1_lb = bound(wf_s)
    w1 = bool(wf_s.isna().any() or not (w1_lb > 0))
    final, score = select(evals, years)
    fv = value_on(final, years)[1] if final is not None else float("nan")
    w2 = bool(final is None or not (fv > 0))
    rows.append({"section": "final", **_key(final), "plateau_score": score, "value": fv,
                 "funded_risk": final["funded_risk"] if final is not None else float("nan")})
    if final is not None:                                                        # the kit's reading, reported
        for name, R in legs_of(final, cfg):
            t = leg_frame(grid, final, R, "lenient")
            rows.append({"section": "final_lenient", "leg": name, "n": len(t),
                         "value": bound(t.groupby("year")["metric"].mean()),
                         "net": float(t["net"].mean()) if len(t) else float("nan")})
    rows.append({"section": "kline", "line": "W1", "value": w1_lb, "killed": w1})
    rows.append({"section": "kline", "line": "W2", "value": fv, "killed": w2})
    killed = [ln for ln, x in (("W1", w1), ("W2", w2)) if x]
    rows.append({"section": "summary", "verdict": "kill" if killed else "continue", "killed_by": ",".join(killed),
                 "k": k, "years": f"{years[0]}-{years[-1]}", "configurations_feasible_all_years":
                     int(sum(r.get("feasible", False) for r in rows if r["section"] == "grid"))})
    out = pd.DataFrame(rows)
    write_result(out, "orb3_search", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"config": "config/orb3_search.yaml", "runs": list(cfg["runs"]), "k": k,
                             "fill_profile": "assumed", "fees": dict(fm.round_turn_by_instrument),
                             "exit_slippage_ticks": float(fm.stop_slippage_ticks),
                             "flatten_slippage_ticks": float(fm.flatten_slippage_ticks), "decision": "D-256"},
                 description="ORB3's declared search on NQ 2009 to June 2025: every configuration of the grid, the "
                             "plateau selection, its walk-forward from 2013 and the kill line W1-W2 fixed in "
                             "config/orb3_search.yaml before the runs. Deterministic, no seed.")
    if record:
        VariantCounter().record(prereg_id="D-256:orb3_search", seed=0, exploratory=True,
                                params={"study": "ORB3 search", "k": k, "market": "NQ"},
                                label="ORB3's declared search: NQ, the stop grid x exit modes x latest fill x ranges x "
                                      "filter (deterministic records; the seed is nominal)")
    pd.set_option("display.width", 250)
    print(out[out["section"] != "grid"].dropna(axis=1, how="all").round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
