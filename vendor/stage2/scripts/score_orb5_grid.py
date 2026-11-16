"""ORB5's declared grid (T16 item 4; D-273): config/orb5_grid.yaml scored on NQ's development years -- the plateau
selection, its walk-forward, the era and drift rules, and the D-145 gate on the walk-forward's out-of-sample trades --
all fixed in that file before this script read an outcome.

    python scripts/score_orb5_grid.py --declaration D-273

ORB5's cheap screen (step 3 of `docs/RESEARCH_PROTOCOL.md`), declared as ORB3's search was (D-256): it refuses to run
unless its declaring decision is in DECISIONS.md; the pre-registration is the held-back confirmation's, if no kill
line is met. Reads ORB3's day records R102-R104 and
ORB5's captures R105-R107 (the same days, joined at ingest, D-265), drops FOMC days, refuses any record before
2009-06-01 or on or after 2025-07-01 (the held-back window, D-237).

**A trade** (`Grid5.leg`): an entry -- the original fill (`l0`, reported only) or the hand-traded entry at five minutes
under the cell's missed-trigger policy (D-266) -- with a bracket at R: stopped if the stop's passage comes no later than
R x the stop's (equal slots the stop's) or, the fill inside its bar, the bar's adverse excursion reaches the stop (the
strict reading, D-254); else the target at R x the stop rounded down to a whole tick (D-257); else the flatten at the
worst of 15:07-15:10 (D-263). Its move before any cost in R adds back the entry's tick (the record's fill is one tick
beyond the price the move is measured from). Its costs: the entry max(1 tick, the recorded spread at its fill minute),
the fee, the exit 1 tick on a stop, none at a target, 2 on the flatten. Its metric: the move less the cell's median
round-trip cost in R over its filled trades of 2020 to June 2025, priced as a stop exit (no outcome).

Writes results/orb5_grid.csv: `grid`, `walkforward`, `final`, `final_l0`, `eras`, `drift`, `locked_added`, `gate`,
`spa`, `dsr`, `kline`, `summary` rows.
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
import yaml  # noqa: E402

import score_orb3_search as s3  # noqa: E402
from propedge.outcomes.orb5_core import MISSING5  # noqa: E402
from propedge.outcomes.orb_core import FLAT_ENTRY, OR_MINS  # noqa: E402

SCRIPT = "scripts/score_orb5_grid.py"
DECLARATION = "D-273"
CONFIG = ROOT / "config" / "orb5_grid.yaml"
CAPTURES = ("R105-orb5-NQ-0914", "R106-orb5-NQ-1519", "R107-orb5-NQ-2025")
WF_FIRST, TODAY_FROM = 2013, 2020
RS = (1.0, 1.5, 2.0, 3.0, 5.0)
RNAME = {1.0: "f1", 1.5: "f15", 2.0: "f2", 3.0: "f3", 5.0: "f5"}
KINDS = {"skip": (0,), "rest": (0, 2), "chase": (0, 1, 2)}
AXES = ("ranges", "relative_volume_min", "stop_atr", "last_fill_ct", "missed_trigger", "coordination", "funded_rr")
FLATTEN_SLIP_TICKS, STOP_SLIP_TICKS = 2.0, 1.0
FLAT_MAX = 0.05                                                  # D-212 (2) as amended by D-308 (2 % before 2026-10-06; the records stand)


def config(path: Path | None = None) -> dict:
    return yaml.safe_load(Path(path or CONFIG).read_text(encoding="utf-8"))


# ------------------------------------------------------------------------------------------------- the records

def load(rd: Path, runs_dir: Path) -> tuple[pd.DataFrame, dict[int, float]]:
    """ORB3's records joined to the captures, FOMC days out; and the trading days a year."""
    c3 = s3.config()
    d, sess, have = s3.load(rd, c3)
    if set(have) != set(c3["runs"]):
        raise SystemExit(f"REFUSED: ORB3's three runs are needed, ingested: {have}.")
    caps = []
    for run in CAPTURES:
        f = rd / f"manual_{run.replace('-', '_')}.csv"
        if not f.is_file():
            raise SystemExit(f"REFUSED: {run} is not ingested.")
        t = pd.read_csv(f, low_memory=False)
        caps.append(t[t["kind"] == "day"])
    c = pd.concat(caps, ignore_index=True)
    c["or_minutes"] = c["or_minutes"].astype(int)
    d["date"], c["date"] = d["date"].astype(str), c["date"].astype(str)
    drop = [x for x in c.columns if x in d.columns and x not in ("date", "or_minutes")]
    m = d.merge(c.drop(columns=drop), on=["date", "or_minutes"], how="inner", validate="one_to_one")
    if len(m) != len(d) or len(m) != len(c):
        raise SystemExit("REFUSED: ORB3's records and the captures do not cover the same days and ranges.")
    dt = pd.to_datetime(m["date"]).dt.date
    if (dt >= s3.HELD_BACK).any() or (dt < s3.START).any():
        raise SystemExit("REFUSED: a record outside 2009-06-01 to 2025-06-30 -- the held-back window is never read "
                         "here (D-237).")
    sessions = s3.trading_days(sess, runs_dir, c3)
    if sessions is None:
        raise SystemExit("REFUSED: a run record (runs/<run>/ingested.json) is missing: the trading days need it.")
    m = m[~m["date"].isin(s3.fomc_dates(c3))].copy()
    return m, sessions


class Grid5:
    """The records as (days x ranges) arrays, an entry view per policy, and each leg's trades."""

    def __init__(self, m: pd.DataFrame, cfg: dict, fee: float, tick_dollars: float):
        self.cfg, self.fee, self.td = cfg, float(fee), float(tick_dollars)
        self.K = len(cfg["search"]["stop_atr"])
        first = m[m["or_minutes"] == OR_MINS[0]].sort_values("date").set_index("date")
        self.dates = first.index.to_numpy()
        self.year = pd.to_datetime(pd.Series(self.dates)).dt.year.to_numpy()
        self.stop = np.stack([first[f"stop_ticks_{i}"].to_numpy(float) for i in range(self.K)], axis=1)

        def piv(col):
            return (m.pivot(index="date", columns="or_minutes", values=col).reindex(index=self.dates, columns=OR_MINS)
                    .to_numpy(float))
        self.dir, self.rv = piv("dir"), piv("rv100")
        self.views = {"l0": {"slot": piv("fill_slot"), "at_open": piv("at_open"), "fbc": piv("fill_bar_close_ticks"),
                             "fba": piv("fill_bar_against_ticks"), "close": piv("close_ticks"),
                             "worst": piv("worst_flat_ticks"), "spread": piv("spread_fill_tenths"),
                             "A": [piv(f"a_{i}") for i in range(self.K)],
                             "F": {R: [piv(f"{RNAME[R]}_{i}") for i in range(self.K)] for R in RS}}}
        kind = piv("lat_kind")
        hand = {"slot": piv("lat_slot"), "at_open": piv("lat_at_open"), "fbc": piv("lat_fill_bar_close_ticks"),
                "fba": piv("lat_fill_bar_against_ticks"), "close": piv("lat_close_ticks"),
                "worst": piv("lat_worst_ticks"), "spread": piv("lat_spread_fill_tenths"),
                "A": [piv(f"lat_a_{i}") for i in range(self.K)],
                "F": {R: [piv(f"lat_{RNAME[R]}_{i}") for i in range(self.K)] for R in RS}}
        for pol, kinds in KINDS.items():
            self.views[pol] = {**hand, "slot": np.where(np.isin(kind, kinds), hand["slot"], -1.0)}

    def valid(self, v: dict, last_fill: int, ranges, rv_min) -> np.ndarray:
        cols = np.array([n in tuple(ranges) for n in OR_MINS])[None, :]
        out = (self.dir != 0) & (v["slot"] != -1) & (v["slot"] <= last_fill) & cols
        if rv_min is not None:
            out &= self.rv >= 100 * float(rv_min)
        return out

    def today_cost(self, v: dict, i: int, valid: np.ndarray) -> float:
        """The median round-trip cost in R over the cell's filled records of 2020 to June 2025, priced as a stop
        exit -- before coordination, so no outcome enters (D-257)."""
        st = np.repeat(self.stop[:, i][:, None], len(OR_MINS), axis=1)
        sel = valid & (self.year >= TODAY_FROM)[:, None]
        c = (self.entry_ticks(v)[sel] * self.td + self.fee + STOP_SLIP_TICKS * self.td) / (st[sel] * self.td)
        return float(np.median(c)) if len(c) else float("nan")

    @staticmethod
    def entry_ticks(v: dict) -> np.ndarray:
        sp = v["spread"]
        return np.where(sp >= 0, np.maximum(1.0, sp / 10.0), 1.0)

    def outcome(self, v: dict, i: int, R: float, mae: bool = False) -> dict[str, np.ndarray]:
        """Every record's outcome at R, before coordination: (days x ranges) arrays; the MAE bound when `mae`."""
        st = np.repeat(self.stop[:, i][:, None], len(OR_MINS), axis=1)
        inside = v["at_open"] == 0
        fbs = inside & (v["fba"] >= st)
        A, F = v["A"][i], v["F"][R][i]
        stopped = fbs | ((A != -1) & ((F == -1) | (A <= F)))
        target = ~stopped & (F != -1)
        flat = ~stopped & ~target
        exit_slot = np.where(fbs, v["slot"], np.where(stopped, A, np.where(target, F, FLAT_ENTRY)))
        won = np.floor(R * st + 1e-9)
        flat_move = np.where(v["worst"] != MISSING5, v["worst"], v["close"])
        move = np.where(stopped, -st, np.where(target, won, flat_move))
        gross = (move + 1.0) / st
        exit_ticks = np.where(stopped, STOP_SLIP_TICKS, np.where(target, 0.0, FLATTEN_SLIP_TICKS))
        cost = (self.entry_ticks(v) * self.td + self.fee + exit_ticks * self.td) / (st * self.td)
        out = {"gross": gross, "cost": cost, "net": gross - cost, "flat": flat, "stopped": stopped,
               "target": target, "exit": exit_slot}
        if not mae:
            return out
        # the MAE's upper bound in R (orb_trades_export's rule): a stopped trade's is its stop; any other's the
        # narrowest grid stop not reached before its exit, never below its fill bar's own excursion when inside
        unreached = np.full(st.shape, np.inf)
        for k in range(i + 1):
            stk = np.repeat(self.stop[:, k][:, None], len(OR_MINS), axis=1)
            hit = (v["A"][k] != -1) & (v["A"][k] <= exit_slot)
            unreached = np.where(~hit, np.minimum(unreached, stk), unreached)
        mae = np.where(stopped, st, np.minimum(unreached, st))
        mae = np.where(stopped, st, np.minimum(np.maximum(mae, np.where(inside, v["fba"], 0.0)), st))
        return {**out, "mae": np.clip(mae / st, 0.0, 1.0)}

    def kept(self, v: dict, valid: np.ndarray, exit_slot: np.ndarray, coordination: str) -> np.ndarray:
        if coordination == "one_at_a_time":
            return s3.sequential_mask(np.where(valid, v["slot"], np.inf), np.where(valid, exit_slot, -1), valid)
        if coordination != "ranges_locked":
            raise ValueError(coordination)
        # D-269: every entry on the side of the day's first entry (fill-bar order, the shorter range first)
        order = np.where(valid, v["slot"] * 10 + np.arange(len(OR_MINS))[None, :], np.inf)
        first = np.argmin(order, axis=1)
        side = self.dir[np.arange(len(self.dates)), first]
        return valid & (self.dir == side[:, None])


# ------------------------------------------------------------------------------------------ the grid's statistics

def cells(cfg: dict) -> list[dict]:
    s = cfg["search"]
    out = []
    for a, ranges in enumerate(s["ranges"]):
        for b, rv in enumerate(s["relative_volume_min"]):
            for i, sa in enumerate(s["stop_atr"]):
                for j, cut in enumerate(s["last_fill_ct"]):
                    for p, pol in enumerate(s["missed_trigger"]):
                        for q, co in enumerate(s["coordination"]):
                            for r, R in enumerate(s["funded_rr"]):
                                out.append({"idx": (a, b, i, j, p, q, r), "ranges": tuple(ranges), "rv_min": rv,
                                            "i": i, "stop_atr": sa, "j": j, "last_fill_ct": cut,
                                            "last_fill_slot": s3._ct_slot(cut), "policy": pol,
                                            "coordination": co, "funded_rr": float(R)})
    return out


def funded_risks(grid: Grid5, band: pd.DataFrame) -> dict[int, float]:
    """D-273: per stop width, of the funded candidates the one deploying the most risk a day -- the risk times the
    share of 2020 to June 2025's days sizeable at it -- ties to the larger; nan if none is ever sizeable."""
    from orb5_prep import FUNDED_RISKS, sizeable

    b = band[(band["state"] == "funded_below_2000") & (band["market"] == "NQ")].iloc[0]
    today = grid.year >= TODAY_FROM
    out = {}
    for i in range(grid.K):
        st = grid.stop[today, i]
        best, best_val = float("nan"), 0.0
        for r in sorted(FUNDED_RISKS, reverse=True):                     # the larger first, so a tie keeps it
            share = float(sizeable(st, r, int(b["cap_micros"]), float(b["tick_value"]),
                                   int(b["cost_drag_floor_ticks"])).mean()) if len(st) else 0.0
            if r * share > best_val + 1e-9:
                best, best_val = float(r), r * share
        out[i] = best
    return out


def combine_sizeable(grid: Grid5, band: pd.DataFrame, risk: float) -> np.ndarray:
    """(days x widths): the day's stop sizeable for the Combine at `risk` under 37 micros (D-272 (1))."""
    from orb5_prep import sizeable

    b = band[(band["state"] == "combine") & (band["market"] == "NQ")].iloc[0]
    return np.stack([sizeable(grid.stop[:, i], risk, int(b["cap_micros"]), float(b["tick_value"]),
                              int(b["cost_drag_floor_ticks"])) for i in range(grid.K)], axis=1)


def leg_stats(grid: Grid5, v: dict, c: dict, R: float, years: np.ndarray) -> tuple[dict, dict]:
    """(per-year arrays, the trades) of one leg of a cell."""
    valid = grid.valid(v, c["last_fill_slot"], c["ranges"], c["rv_min"])
    o = grid.outcome(v, c["i"], R)
    kept = grid.kept(v, valid, o["exit"], c["coordination"])
    tc = grid.today_cost(v, c["i"], valid)
    rows, cols = np.nonzero(kept)
    yi = np.searchsorted(years, grid.year[rows])
    metric = o["gross"][rows, cols] - tc
    dirs = grid.dir[rows, cols]
    ny = len(years)

    def bc(w=None, mask=None):
        idx, ww = (yi, w) if mask is None else (yi[mask], None if w is None else w[mask])
        return np.bincount(idx, weights=ww, minlength=ny).astype(float)
    flat = o["flat"][rows, cols].astype(float)
    stats = {"n": bc(), "metric": bc(metric), "gross": bc(o["gross"][rows, cols]), "net": bc(o["net"][rows, cols]),
             "flat": bc(flat), "n_long": bc(mask=dirs > 0), "metric_long": bc(metric, dirs > 0),
             "n_short": bc(mask=dirs < 0), "metric_short": bc(metric, dirs < 0), "today_cost": tc}
    trades = {"rows": rows, "cols": cols, "metric": metric, "kept": kept, "o": o, "valid": valid}
    return stats, trades


def bound_rows(means: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Row-wise one-sided 95 % lower bound of the yearly means where `mask` (at least two years), else nan."""
    from scipy import stats

    n = mask.sum(axis=1)
    x = np.where(mask, means, 0.0)
    mu = x.sum(axis=1) / np.maximum(n, 1)
    var = (np.where(mask, (means - mu[:, None]) ** 2, 0.0)).sum(axis=1) / np.maximum(n - 1, 1)
    t = stats.t.ppf(0.95, np.maximum(n - 1, 1))
    out = mu - t * np.sqrt(var) / np.sqrt(np.maximum(n, 1))
    return np.where(n >= 2, out, np.nan)


def bound(y: pd.Series) -> float:
    return s3.bound(y)


class Evaluated:
    """Every cell's two legs' per-year statistics, as matrices (cells x years), and the static feasibility."""

    def __init__(self, grid: Grid5, cfg: dict, sessions: dict[int, float], band: pd.DataFrame, need: float):
        self.cfg, self.grid = cfg, grid
        self.cells = cells(cfg)
        self.years = np.array(sorted(sessions))
        ny, nc = len(self.years), len(self.cells)
        self.frisk = funded_risks(grid, band)
        csz = combine_sizeable(grid, band, float(cfg["fixed"]["combine"]["risk"]))
        today_days = sum(v for y, v in sessions.items() if y >= TODAY_FROM)
        accounts = int(cfg["gate"]["campaign"]["accounts"])                    # D-154 per account, as validate_card
        self.mat = {leg: {k: np.zeros((nc, ny)) for k in ("n", "metric", "gross", "net", "flat", "n_long",
                                                           "metric_long", "n_short", "metric_short")}
                    for leg in ("combine", "funded")}
        self.static_ok = np.zeros(nc, bool)
        self.freq = np.zeros(nc)
        combine_cache: dict[tuple, tuple[dict, dict]] = {}
        for k, c in enumerate(self.cells):
            v = grid.views[c["policy"]]
            key = (c["ranges"], c["rv_min"], c["i"], c["j"], c["policy"], c["coordination"])
            if key not in combine_cache:
                combine_cache[key] = leg_stats(grid, v, c, float(cfg["fixed"]["combine"]["rr"]), self.years)
            cs, ct = combine_cache[key]
            fs, _ = leg_stats(grid, v, c, c["funded_rr"], self.years)
            for leg, s in (("combine", cs), ("funded", fs)):
                for name, m in self.mat[leg].items():
                    m[k] = s[name]
            today = grid.year[ct["rows"]] >= TODAY_FROM
            sized = csz[ct["rows"], c["i"]]
            self.freq[k] = (float((today & sized).sum()) / today_days / accounts) if today_days else 0.0   # per account
            self.static_ok[k] = bool(self.freq[k] + 1e-9 >= need and np.isfinite(self.frisk[c["i"]]))
        self.shape = tuple(len(cfg["search"][a]) for a in AXES)

    def values(self, ymask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(feasible, value) of every cell on the years of `ymask`."""
        ok = self.static_ok.copy()
        vals = []
        for leg in ("combine", "funded"):
            m = self.mat[leg]
            n = m["n"][:, ymask]
            has = n > 0
            fl = m["flat"][:, ymask]
            share = np.where(has, fl / np.maximum(n, 1), 0.0)
            overall = fl.sum(axis=1) / np.maximum(n.sum(axis=1), 1)
            ok &= (overall <= FLAT_MAX + 1e-12) & (share <= FLAT_MAX + 1e-12).all(axis=1)
            means = np.where(has, m["metric"][:, ymask] / np.maximum(n, 1), np.nan)
            vals.append(bound_rows(means, has))
        v = np.fmin(vals[0], vals[1])
        v = np.where(np.isnan(vals[0]) | np.isnan(vals[1]), np.nan, v)
        return ok & ~np.isnan(v), v

    def select(self, ymask: np.ndarray) -> tuple[int | None, float]:
        """The plateau rule: the feasible cell maximising min(own value, the median of its 3 x 3 neighbourhood in
        stop width and latest fill, every neighbour counted, no value the lowest); ties to the earlier cell."""
        ok, v = self.values(ymask)
        V = np.where(np.isnan(v), -np.inf, v).reshape(self.shape)
        pad = np.full(tuple(s + (2 if ax in (2, 3) else 0) for ax, s in enumerate(self.shape)), np.nan)
        sl = tuple(slice(1, -1) if ax in (2, 3) else slice(None) for ax in range(len(self.shape)))
        pad[sl] = V
        stack = []
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                s2 = tuple(slice(1 + di, pad.shape[2] - 1 + di) if ax == 2 else
                           slice(1 + dj, pad.shape[3] - 1 + dj) if ax == 3 else slice(None)
                           for ax in range(len(self.shape)))
                stack.append(pad[s2])
        med = np.nanmedian(np.stack(stack), axis=0).reshape(-1)
        score = np.where(ok, np.fmin(np.where(np.isnan(v), -np.inf, v), med), -np.inf)
        if not np.isfinite(score).any():
            return None, float("nan")
        best = int(np.argmax(score))
        return best, float(score[best])

    def year_value(self, k: int, y: int) -> float:
        """A selection's value in test year `y`: the smaller leg's mean metric; no trade there scores 0."""
        yi = int(np.searchsorted(self.years, y))
        out = []
        for leg in ("combine", "funded"):
            n = self.mat[leg]["n"][k, yi]
            out.append(self.mat[leg]["metric"][k, yi] / n if n > 0 else 0.0)
        return float(min(out))


# ------------------------------------------------------------------------------------------- the final's readings

def era_reading(ev: Evaluated, k: int, eras: list[list[int]], reps: int, seed: int) -> tuple[dict, bool, float]:
    """D-271 (1): per leg, the bootstrap of the eras' mean gross R per trade (whole years resampled within each era)
    and each era's yearly-means bound; (rows, flagged, the lower era's value)."""
    rng = np.random.default_rng(seed)
    rows, flagged, lows = {}, False, []
    for leg in ("combine", "funded"):
        m = ev.mat[leg]
        n, g, met = m["n"][k], m["gross"][k], m["metric"][k]
        masks = [(ev.years >= a) & (ev.years <= b) for a, b in eras]
        diffs = np.empty(reps)
        idx = [np.nonzero(mk & (n > 0))[0] for mk in masks]
        for r in range(reps):
            means = []
            for ix in idx:
                pick = rng.choice(ix, size=len(ix), replace=True) if len(ix) else ix
                means.append(g[pick].sum() / max(n[pick].sum(), 1))
            diffs[r] = means[1] - means[0]
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        fl = bool(lo > 0 or hi < 0)
        flagged |= fl
        era_b = [bound(pd.Series(np.where(n[mk] > 0, met[mk] / np.maximum(n[mk], 1), np.nan))) for mk in masks]
        lows.append(min(era_b))
        rows[leg] = {"leg": leg, "diff_lo": float(lo), "diff_hi": float(hi), "flagged": fl,
                     "era1_mean_gross": float(g[masks[0]].sum() / max(n[masks[0]].sum(), 1)),
                     "era2_mean_gross": float(g[masks[1]].sum() / max(n[masks[1]].sum(), 1)),
                     "era1_bound": era_b[0], "era2_bound": era_b[1]}
    return rows, flagged, float(min(lows))


def drift_value(ev: Evaluated, k: int) -> tuple[dict, float]:
    """D-271 (5): per leg, the yearly-means bound of the long/short-balanced metric."""
    out, vals = {}, []
    for leg in ("combine", "funded"):
        m = ev.mat[leg]
        ml = np.where(m["n_long"][k] > 0, m["metric_long"][k] / np.maximum(m["n_long"][k], 1), np.nan)
        ms = np.where(m["n_short"][k] > 0, m["metric_short"][k] / np.maximum(m["n_short"][k], 1), np.nan)
        bal = (ml + ms) / 2.0
        b = bound(pd.Series(bal))
        nl, nsh = m["n_long"][k].sum(), m["n_short"][k].sum()
        out[leg] = {"leg": leg, "long_share": float(nl / max(nl + nsh, 1)),
                    "long_mean": float(m["metric_long"][k].sum() / max(nl, 1)),
                    "short_mean": float(m["metric_short"][k].sum() / max(nsh, 1)), "balanced_bound": b}
        vals.append(b)
    return out, float(np.fmin(vals[0], vals[1])) if not any(np.isnan(vals)) else float("nan")


def leg_summary(ev: Evaluated, k: int, leg: str, sessions: dict[int, float]) -> dict:
    m = ev.mat[leg]
    n = m["n"][k]
    means = pd.Series(np.where(n > 0, m["metric"][k] / np.maximum(n, 1), np.nan))
    return {"leg": leg, "trades": int(n.sum()), "per_day": float(n.sum() / sum(sessions.values())),
            "e_metric": float(m["metric"][k].sum() / max(n.sum(), 1)), "bound": bound(means),
            "gross": float(m["gross"][k].sum() / max(n.sum(), 1)), "net": float(m["net"][k].sum() / max(n.sum(), 1)),
            "flat_share": float(m["flat"][k].sum() / max(n.sum(), 1))}


def locked_added(grid: Grid5, ev: Evaluated, k: int) -> list[dict]:
    """D-269 (2): the trades ranges_locked takes beyond one_at_a_time for the final cell, each leg: their own e,
    yearly-means bound and mean cost."""
    c = ev.cells[k]
    v = grid.views[c["policy"]]
    out = []
    for leg, R in (("combine", float(ev.cfg["fixed"]["combine"]["rr"])), ("funded", c["funded_rr"])):
        _, seq = leg_stats(grid, v, {**c, "coordination": "one_at_a_time"}, R, ev.years)
        _, lock = leg_stats(grid, v, {**c, "coordination": "ranges_locked"}, R, ev.years)
        add = lock["kept"] & ~seq["kept"]
        rows, cols = np.nonzero(add)
        tc = grid.today_cost(v, c["i"], lock["valid"])
        met = lock["o"]["gross"][rows, cols] - tc
        y = pd.Series(met).groupby(grid.year[rows]).mean()
        out.append({"section": "locked_added", "leg": leg, "added": int(len(rows)),
                    "e_metric": float(met.mean()) if len(met) else float("nan"), "bound": bound(y),
                    "cost": float(lock["o"]["cost"][rows, cols].mean()) if len(rows) else float("nan")})
    return out


# ------------------------------------------------------------------------------------------------------ the gate

def gate_trades(grid: Grid5, ev: Evaluated, selections: dict[int, int | None], final_rr: float) -> pd.DataFrame:
    """Each test year's out-of-sample trades: the selection made on the years before it, both legs' outcomes on the
    trades the funded leg's coordination keeps (fixed in config/orb5_grid.yaml's gate)."""
    out = []
    for y, k in selections.items():
        if k is None:
            continue
        c = ev.cells[k]
        v = grid.views[c["policy"]]
        valid = grid.valid(v, c["last_fill_slot"], c["ranges"], c["rv_min"])
        oc = grid.outcome(v, c["i"], float(ev.cfg["fixed"]["combine"]["rr"]), mae=True)
        of = grid.outcome(v, c["i"], c["funded_rr"], mae=True)
        kept = grid.kept(v, valid, of["exit"], c["coordination"]) & (grid.year == y)[:, None]
        rows, cols = np.nonzero(kept)
        for r, col in zip(rows, cols):
            out.append({"date": grid.dates[r], "year": y, "i": c["i"], "entry_t": float(v["slot"][r, col]),
                        "exit_t": float(of["exit"][r, col]),
                        "r_c": float(oc["net"][r, col]), "mae_c": float(oc["mae"][r, col]),
                        "r_f": float(of["net"][r, col]), "mae_f": float(of["mae"][r, col]),
                        "flat_f": bool(of["flat"][r, col])})
    return pd.DataFrame(out)


def gate_blocks(grid: Grid5, t: pd.DataFrame, days: list[str], frisk: float, final_rr: float, band: pd.DataFrame,
                seed: int):
    """D-271 (4): each trade's stop a micro drawn from 2020 to June 2025's days at its width; left out unless the
    drawn stop is sizeable in both states. One block a trading day, trades in entry order."""
    from orb5_prep import sizeable
    from propedge.outcomes.distribution import DayBlock

    rng = np.random.default_rng(seed)
    today = np.nonzero(grid.year >= TODAY_FROM)[0]
    cb = band[(band["state"] == "combine") & (band["market"] == "NQ")].iloc[0]
    fb = band[(band["state"] == "funded_below_2000") & (band["market"] == "NQ")].iloc[0]
    tv = float(cb["tick_value"])
    if len(t):
        draw = rng.choice(today, size=len(t), replace=True)
        st = grid.stop[draw, t["i"].to_numpy(int)]
        ok = (sizeable(st, 1500.0, int(cb["cap_micros"]), tv, int(cb["cost_drag_floor_ticks"]))
              & sizeable(st, frisk, int(fb["cap_micros"]), tv, int(fb["cost_drag_floor_ticks"])))
        t = t.assign(rpc=st * tv)[ok]
    by = {d: g.sort_values("entry_t", kind="stable") for d, g in t.groupby("date")} if len(t) else {}
    blocks, dropped = [], 0
    for d in days:
        g = by.get(d)
        if g is None or not len(g):
            z = np.zeros(0)
            blocks.append(DayBlock(pnl=z, risked=z, exit_reasons=(), risk_per_contract=z, mae=z, entry_t=z,
                                   exit_t=z, r_by_rr={1.0: z, final_rr: z}, mae_by_rr={1.0: z, final_rr: z}))
            continue
        rpc = g["rpc"].to_numpy(float)
        rc, rf = g["r_c"].to_numpy(float), g["r_f"].to_numpy(float)
        mc = np.maximum(g["mae_c"].to_numpy(float), -rc)
        mf = np.maximum(g["mae_f"].to_numpy(float), -rf)
        blocks.append(DayBlock(pnl=rf * rpc, risked=rpc.copy(),
                               exit_reasons=tuple("flatten" if x else "bracket" for x in g["flat_f"]),
                               risk_per_contract=rpc.copy(), mae=mf * rpc, entry_t=g["entry_t"].to_numpy(float),
                               exit_t=g["exit_t"].to_numpy(float), r_by_rr={1.0: rc, final_rr: rf},
                               mae_by_rr={1.0: mc, final_rr: mf}))
    return blocks, int(len(t))


def run_gate(blocks, stats: dict, final_rr: float, frisk: float, gcfg: dict, seed: int):
    from propedge.campaign import gate
    from propedge.campaign.payout_method import rules_for_method
    from propedge.campaign.protocols import Protocol
    from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy
    from propedge.campaign.sizing import CURRENT_TIER, SizingRule

    camp = gcfg["campaign"]
    busiest = max((len(b.pnl) for b in blocks), default=1)
    protocol = Protocol(name="orb5", combine_rr=1.0, combine_risk=1500.0, funded_rr=final_rr, funded_risk=frisk,
                        trades_per_day=max(1, int(busiest)), payout_path="standard", keep_balance=0.0,
                        payout_frac=1.0, max_concurrent_accounts=int(camp["accounts"]), family="orb5",
                        source="config/orb5_grid.yaml", note="ORB5's gate (D-273)")
    policy = RiskPolicy(id="orb5_gate", root=Phase(
        combine=Leaf("combine 1:1 $1,500", risk=1500.0, rr=1.0, max_trades=1),
        funded=Leaf(f"funded {final_rr:g}:1 ${frisk:,.0f}", risk=float(frisk), rr=float(final_rr))))
    e_by = {1.0: stats["combine"]["e"], final_rr: stats["funded"]["e"]}
    lb_by = {1.0: stats["combine"]["lb"], final_rr: stats["funded"]["lb"]}
    return gate.run_gate(
        blocks, e=e_by[final_rr], lb=lb_by[final_rr], protocol=protocol, bankroll=float(camp["bankroll"]),
        horizon_days=int(camp["horizon_days"]), n_paths=int(camp["n_paths"]), seed=seed,
        accounts=int(camp["accounts"]), sizing=SizingRule.from_ledger(CURRENT_TIER, headroom_frac=float(camp["headroom"])),
        rules=rules_for_method(camp["payout_method"]), mode=camp["mode"], settlement=camp["settlement"],
        combines=int(camp["combines"]), total_accounts=int(camp["accounts"]), risk_policy=policy,
        e_by_rr=e_by, lb_by_rr=lb_by)


# ------------------------------------------------------------------------------------------- SPA and deflated SR

def spa_pvalue(Y: np.ndarray, reps: int, seed: int, block: float = 2.0) -> float:
    """Hansen's SPA (consistent statistic) of H0 'no cell beats zero' on the cells' yearly values `Y` (cells x
    years, no nan), a stationary bootstrap of years with mean block `block`."""
    if Y.size == 0 or Y.shape[1] < 3:
        return float("nan")
    n = Y.shape[1]
    rng = np.random.default_rng(seed)
    mu, sd = Y.mean(axis=1), Y.std(axis=1, ddof=1)
    sd = np.where(sd > 0, sd, np.nan)
    t_obs = np.nanmax(np.sqrt(n) * mu / sd)
    keep = mu >= -sd * math.sqrt(2 * math.log(math.log(n))) / math.sqrt(n)        # the consistent recentring
    cmu = np.where(keep, mu, 0.0)
    count = 0
    p = 1.0 / block
    for _ in range(reps):
        idx = np.empty(n, int)
        idx[0] = rng.integers(n)
        for t in range(1, n):
            idx[t] = rng.integers(n) if rng.random() < p else (idx[t - 1] + 1) % n
        mb = Y[:, idx].mean(axis=1) - mu + cmu
        count += np.nanmax(np.sqrt(n) * (mb - cmu) / sd) >= t_obs
    return count / reps


def deflated_sharpe(y: np.ndarray, srs: np.ndarray, n_trials: int) -> float:
    """Bailey and Lopez de Prado's deflated Sharpe ratio of the yearly values `y`, the trials' Sharpe ratios `srs`."""
    from scipy import stats

    y = y[~np.isnan(y)]
    if len(y) < 3 or np.std(y, ddof=1) == 0:
        return float("nan")
    sr = y.mean() / y.std(ddof=1)
    v = np.nanvar(srs, ddof=1) if np.isfinite(srs).sum() > 1 else 0.0
    g = 0.5772156649
    sr0 = math.sqrt(v) * ((1 - g) * stats.norm.ppf(1 - 1 / n_trials) + g * stats.norm.ppf(1 - 1 / (n_trials * math.e)))
    sk, ku = stats.skew(y), stats.kurtosis(y, fisher=False)
    den = math.sqrt(max(1e-12, 1 - sk * sr + (ku - 1) / 4 * sr ** 2))
    return float(stats.norm.cdf((sr - sr0) * math.sqrt(len(y) - 1) / den))


# --------------------------------------------------------------------------------------------------------- main

def _key(c: dict | None) -> dict:
    if c is None:
        return {"ranges": None}
    return {"ranges": "+".join(map(str, c["ranges"])), "rv_min": c["rv_min"], "stop_atr": c["stop_atr"],
            "last_fill_ct": c["last_fill_ct"], "missed_trigger": c["policy"], "coordination": c["coordination"],
            "funded_rr": c["funded_rr"]}


def main(argv: list[str] | None = None, *, results_dir: Path | None = None, runs_dir: Path | None = None,
         record: bool = True) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result
    from propedge.research.model_card import BAND_FILE, setups_minimum

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--declaration", required=True)
    a = ap.parse_args(argv)
    if a.declaration != DECLARATION or f"| {DECLARATION} |" not in (ROOT / "DECISIONS.md").read_text(encoding="utf-8"):
        print(f"REFUSED: ORB5 is declared by {DECLARATION} (DECISIONS.md); got {a.declaration!r} or the row is missing.")
        return 2
    cfg = config()
    k_total = math.prod(len(cfg["search"][x]) for x in AXES)
    if k_total != int(cfg["k"]):
        print(f"REFUSED: the grid holds {k_total} configurations, the config declares {cfg['k']}.")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    m, sessions = load(rd, Path(runs_dir) if runs_dir is not None else ROOT / "runs")
    fm = FillModel.load("assumed")
    q = params("NQ")
    grid = Grid5(m, cfg, float(fm.round_turn_by_instrument[q["micro"]]), q["micro_tick"] * q["micro_point_value"])
    band = read_result(BAND_FILE)
    need = setups_minimum(float(cfg["fixed"]["combine"]["rr"]), float(cfg["fixed"]["combine"]["risk"]), 0.0)
    ev = Evaluated(grid, cfg, sessions, band, float(need))
    years = list(ev.years)
    rows = []
    ok_all, v_all = ev.values(np.ones(len(years), bool))
    for k, c in enumerate(ev.cells):
        r = {"section": "grid", **_key(c), "feasible": bool(ok_all[k]), "value": float(v_all[k]),
             "freq_per_account_today": float(ev.freq[k]), "funded_risk": ev.frisk[c["i"]]}
        for leg in ("combine", "funded"):
            n = ev.mat[leg]["n"][k].sum()
            r[f"{leg}_n"] = int(n)
            r[f"{leg}_metric"] = float(ev.mat[leg]["metric"][k].sum() / max(n, 1))
            r[f"{leg}_net"] = float(ev.mat[leg]["net"][k].sum() / max(n, 1))
            r[f"{leg}_flat"] = float(ev.mat[leg]["flat"][k].sum() / max(n, 1))
        rows.append(r)
    # the walk-forward
    sels, wf = {}, []
    for T in [y for y in years if y >= WF_FIRST]:
        k, score = ev.select(ev.years < T)
        sels[T] = k
        val = ev.year_value(k, T) if k is not None else float("nan")
        wf.append(val)
        rows.append({"section": "walkforward", "test_year": T, **_key(ev.cells[k] if k is not None else None),
                     "plateau_score": score, "oos_value": val})
    wf_s = pd.Series(wf, index=[y for y in years if y >= WF_FIRST])
    w1_lb = bound(wf_s)
    w1 = bool(wf_s.isna().any() or not (w1_lb > 0))
    # the final selection
    kf, score = ev.select(np.ones(len(years), bool))
    final = ev.cells[kf] if kf is not None else None
    w2, b_kill, g_kill, gate_passed = True, True, True, False
    if final is not None:
        fv = float(v_all[kf])
        era_rows, flagged, low = era_reading(ev, kf, cfg["selection"]["eras"]["split"], 2000, cfg["seeds"]["eras"])
        fv_used = min(fv, low) if flagged else fv
        w2 = bool(not ok_all[kf] or not (fv_used > 0))
        rows.append({"section": "final", **_key(final), "plateau_score": score, "value": fv, "value_used": fv_used,
                     "era_flagged": flagged, "funded_risk": ev.frisk[final["i"]],
                     "freq_per_account_today": float(ev.freq[kf])})
        for leg in ("combine", "funded"):
            rows.append({"section": "final_leg", **leg_summary(ev, kf, leg, sessions)})
        rows += [{"section": "eras", **r} for r in era_rows.values()]
        drift_rows, dv = drift_value(ev, kf)
        rows += [{"section": "drift", **r} for r in drift_rows.values()]
        b_kill = bool(not (dv > 0))
        rows.append({"section": "drift", "leg": "value", "balanced_bound": dv})
        # L = 0 beside it: the same cell on the original fill
        l0 = {**final, "policy": "l0"}
        for leg, R in (("combine", float(cfg["fixed"]["combine"]["rr"])), ("funded", final["funded_rr"])):
            st, _ = leg_stats(grid, grid.views["l0"], l0, R, ev.years)
            means = pd.Series(np.where(st["n"] > 0, st["metric"] / np.maximum(st["n"], 1), np.nan))
            rows.append({"section": "final_l0", "leg": leg, "trades": int(st["n"].sum()),
                         "e_metric": float(st["metric"].sum() / max(st["n"].sum(), 1)), "bound": bound(means),
                         "gross": float(st["gross"].sum() / max(st["n"].sum(), 1))})
        rows += locked_added(grid, ev, kf)
        # the gate on the walk-forward's out-of-sample trades
        frisk = float(ev.frisk[final["i"]])
        t = gate_trades(grid, ev, sels, final["funded_rr"])
        stats = {}
        for leg, col in (("combine", "r_c"), ("funded", "r_f")):
            by = t.groupby("year")[col].mean() if len(t) else pd.Series(dtype=float)
            stats[leg] = {"e": float(t[col].mean()) if len(t) else float("nan"), "lb": bound(by)}
        test_days = [d for d, y in zip(grid.dates, grid.year) if y >= WF_FIRST]
        blocks, n_used = gate_blocks(grid, t, test_days, frisk, final["funded_rr"], band, cfg["seeds"]["stops"])
        if np.isfinite([stats[x]["lb"] for x in stats]).all() and n_used:
            gdf, gate_passed = run_gate(blocks, stats, final["funded_rr"], frisk, cfg["gate"], cfg["seeds"]["gate"])
            for _, gr in gdf.iterrows():
                rows.append({"section": "gate", **{kk: vv for kk, vv in gr.items() if not isinstance(vv, (list, dict))}})
        rows.append({"section": "gate_inputs", "oos_trades": int(len(t)), "trades_used": n_used,
                     "e_combine": stats["combine"]["e"], "lb_combine": stats["combine"]["lb"],
                     "e_funded": stats["funded"]["e"], "lb_funded": stats["funded"]["lb"], "funded_risk": frisk})
        g_kill = not gate_passed
    # SPA and the deflated Sharpe ratio, reported
    feas = np.nonzero(ok_all)[0]
    Y = []
    for k in feas:
        Y.append([ev.year_value(int(k), y) for y in years])
    Y = np.array(Y) if len(Y) else np.zeros((0, len(years)))
    rows.append({"section": "spa", "cells": int(len(feas)), "p_value": spa_pvalue(Y, 2000, cfg["seeds"]["spa"])})
    if kf is not None and len(Y):
        srs = Y.mean(axis=1) / np.where(Y.std(axis=1, ddof=1) > 0, Y.std(axis=1, ddof=1), np.nan)
        yf = np.array([ev.year_value(kf, y) for y in years])
        rows.append({"section": "dsr", "n_trials": k_total, "dsr": deflated_sharpe(yf, srs, k_total)})
    lines = {"W1": w1, "W2": w2, "B": b_kill, "G": g_kill}
    for ln, x in lines.items():
        rows.append({"section": "kline", "line": ln, "killed": bool(x), "value": w1_lb if ln == "W1" else None})
    killed = [ln for ln, x in lines.items() if x]
    rows.append({"section": "summary", "verdict": "kill" if killed else "continue", "killed_by": ",".join(killed),
                 "k": k_total, "years": f"{years[0]}-{years[-1]}", "declaration": DECLARATION,
                 "configurations_feasible_all_years": int(ok_all.sum())})
    out = pd.DataFrame(rows)
    write_result(out, "orb5_grid", script=SCRIPT, seed=int(cfg["seeds"]["gate"]), exploratory=True,
                 results_dir=results_dir,
                 notes={"status": "ORB5's screen, declared before it ran (D-273); EXPLORATORY in that its design is not "
                                  "blind to the D-270 views; only the held-back confirmation can decide"},
                 parameters={"config": "config/orb5_grid.yaml", "runs": cfg["runs"], "k": k_total,
                             "fill_profile": "assumed", "seeds": cfg["seeds"], "decision": "D-273"},
                 description="ORB5's declared grid on NQ 2009 to June 2025: every configuration, the plateau "
                             "selection, its walk-forward from 2013, the era and drift rules, the D-145 gate on the "
                             "walk-forward's out-of-sample trades, and the kill lines W1, W2, B and G, all fixed in "
                             "config/orb5_grid.yaml before the run.")
    if record:
        VariantCounter().record(prereg_id=f"{DECLARATION}:orb5_grid", seed=int(cfg["seeds"]["gate"]), exploratory=True,
                                params={"study": "ORB5 grid", "k": k_total, "market": "NQ"},
                                label=f"ORB5's declared grid: {k_total} configurations (D-273)")
    pd.set_option("display.width", 250)
    print(out[out["section"].isin(["walkforward", "final", "final_leg", "eras", "drift", "final_l0", "locked_added",
                                   "gate_inputs", "spa", "dsr", "kline", "summary"])].dropna(axis=1, how="all")
          .round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
