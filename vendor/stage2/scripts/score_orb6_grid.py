"""ORB6's declared grid (T16 item 9; D-278): config/orb6_grid.yaml scored on NQ's development years -- the plateau
selection, its walk-forward, the era rule, the per-side drift benchmark and the D-145 gate on the walk-forward's
out-of-sample trades -- all fixed in that file before this script read an outcome.

    python scripts/score_orb6_grid.py --declaration D-278

ORB6's cheap screen (step 3 of `docs/RESEARCH_PROTOCOL.md`), declared by D-278 under D-277's stopping rule: it refuses
to run unless its declaring decision is in DECISIONS.md. Reads ORB3's day records R102-R104, ORB5's captures R105-R107
and ORB6's R108-R110 (the same days, joined and checked at ingest), drops FOMC days, refuses any record before
2009-06-01 or on or after 2025-07-01 (the held-back window, D-237).

**A trade** (`Grid6.outcome`): an entry -- the retest (the hypothesis: a limit at the broken edge working from the
breakout's bar + 5 minutes, filled at the level or at a gapped bar's open plus a tick; a retest filled at or beyond the
range's far side is in no cell) or, reported beside it, the D-266 hand-traded stop entry -- with a bracket at R on the
cell's stop (the range's far side one tick beyond, or a width of the 14-day ATR): stopped if the stop's passage comes no
later than R x the stop's (equal slots the stop's) or, the fill inside its bar, the bar's adverse excursion reaches the
stop (the strict reading, D-254); else the target at R x the stop rounded down to a whole tick (D-257); else the
flatten at the worst of 15:07-15:10 (D-263), the 15:08 close where no bar was recorded. Its move before any cost in R
is from the recorded fill for the retest (its entry carries no further cost) and, for the baseline, from the price
before the entry's tick, as ORB5's. Its costs: the baseline's entry max(1 tick, the recorded spread); the fee of NQ
minis with MNQ micros at the trade's micro-equivalent size (D-276's mix; the Combine's $1,500 under 37, the funded risk
under 15); the exit 1 tick on a stop, none at a target, 2 on the flatten. Its metric: the move less the cell's median
round-trip cost in R over its filled trades of 2020 to June 2025, priced as a stop exit (no outcome).

**The drift benchmark (kill line B)**: each kept trade's move less the year's mean move of R108-R110's unconditional
entries of the same side, at the latest benchmark slot before the trade's fill bar, with the same stop (its ATR width
that day, or its range's own stop: that range plus a tick) and the same R, read strictly and priced alike -- the cost
cancels, the costs being the cell's.

Writes results/orb6_grid.csv: `grid`, `walkforward`, `final`, `final_leg`, `era_leg`, `eras`, `drift`, `baseline`, `flatten`,
`retest`, `locked_added`, `gate_inputs`, `gate`, `spa`, `dsr`, `kline`, `summary` rows. L = 0 is not reported: the
capture records the retest only from the alert + 5 minutes, the operator's rule (D-278).
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
import score_orb5_grid as g5  # noqa: E402
from orb5_exploratory import CAPS, mini_mix_fee  # noqa: E402
from propedge.outcomes.orb6_core import BENCH_SLOTS, MISSING6  # noqa: E402
from propedge.outcomes.orb_core import FLAT_ENTRY, OR_MINS  # noqa: E402

SCRIPT = "scripts/score_orb6_grid.py"
DECLARATION = "D-278"
CONFIG = ROOT / "config" / "orb6_grid.yaml"
CAPTURES6 = ("R108-orb6-NQ-0914", "R109-orb6-NQ-1519", "R110-orb6-NQ-2025")
WF_FIRST, TODAY_FROM = g5.WF_FIRST, g5.TODAY_FROM
RS = (1.0, 1.5, 2.0, 3.0)
RNAME = {1.0: "f1", 1.5: "f15", 2.0: "f2", 3.0: "f3"}
AXES = ("ranges", "stop", "state", "last_fill_ct", "coordination", "funded_rr")
STATES = ("none", "vwap_with", "gap_with", "overnight_with")
FLATTEN_SLIP_TICKS, STOP_SLIP_TICKS = g5.FLATTEN_SLIP_TICKS, g5.STOP_SLIP_TICKS
FLAT_MAX = g5.FLAT_MAX
POLICIES = ("chase", "skip", "rest")                       # the baseline's, D-266; chase the reported one


def config(path: Path | None = None) -> dict:
    return yaml.safe_load(Path(path or CONFIG).read_text(encoding="utf-8"))


# ------------------------------------------------------------------------------------------------- the records

def load(rd: Path, runs_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[int, float]]:
    """ORB3's records joined to ORB5's and ORB6's captures, FOMC days out; the unconditional entries of those days;
    the trading days a year."""
    m, sessions = g5.load(rd, runs_dir)
    days, bench = [], []
    for run in CAPTURES6:
        f = rd / f"manual_{run.replace('-', '_')}.csv"
        if not f.is_file():
            raise SystemExit(f"REFUSED: {run} is not ingested.")
        t = pd.read_csv(f, low_memory=False)
        days.append(t[t["kind"] == "day"])
        bench.append(t[t["kind"] == "bench"])
    c = pd.concat(days, ignore_index=True)
    b = pd.concat(bench, ignore_index=True)
    c["or_minutes"] = c["or_minutes"].astype(int)
    c["date"], b["date"] = c["date"].astype(str), b["date"].astype(str)
    for x in (c, b):
        dt = pd.to_datetime(x["date"]).dt.date
        if (dt >= s3.HELD_BACK).any() or (dt < s3.START).any():
            raise SystemExit("REFUSED: an ORB6 record outside 2009-06-01 to 2025-06-30 -- the held-back window is never "
                             "read here (D-237).")
    shared = [x for x in c.columns if x in m.columns and x not in ("date", "or_minutes")]
    j = m.merge(c, on=["date", "or_minutes"], how="left", suffixes=("", "_6"), validate="one_to_one")
    if j["rt_kind"].isna().any():
        raise SystemExit("REFUSED: ORB6's captures do not cover every day and range of ORB3's and ORB5's records.")
    for x in ("dir", "fill_slot", "atr_ticks"):
        if x in shared and not (j[x] == j[f"{x}_6"]).all():
            raise SystemExit(f"REFUSED: ORB6's {x} disagrees with ORB3's -- the runs do not describe the same trades.")
    j = j.drop(columns=[f"{x}_6" for x in shared])
    b = b[b["date"].isin(set(j["date"]))].copy()
    return j, b, sessions


def _broadcast(col: np.ndarray) -> np.ndarray:
    return np.repeat(col[:, None], len(OR_MINS), axis=1)


class Grid6:
    """The records as (days x ranges) arrays: the retest's view and the baseline's per policy, each with its stops'
    distances and passages (option 0 the range stop, then the declared ATR widths)."""

    def __init__(self, m: pd.DataFrame, bench: pd.DataFrame, cfg: dict, fee_micro: float, fee_mini: float,
                 tick_dollars: float):
        from propedge.data.orb6_kit import params

        self.cfg, self.fm, self.fM, self.td = cfg, float(fee_micro), float(fee_mini), float(tick_dollars)
        cap = [float(x) for x in params()["stops"]]
        self.K = len(cap)
        self.opt_i: list[int | None] = [None]
        for s in cfg["search"]["stop"][1:]:
            hit = [i for i, x in enumerate(cap) if abs(x - float(s)) < 1e-9]
            if not hit:
                raise SystemExit(f"REFUSED: the declared width {s} is not one of the capture's {cap}.")
            self.opt_i.append(hit[0])
        if cfg["search"]["stop"][0] != "range":
            raise SystemExit("REFUSED: the declaration's first stop is the range stop.")
        first = m[m["or_minutes"] == OR_MINS[0]].sort_values("date").set_index("date")
        self.dates = first.index.to_numpy()
        self.row = {d: r for r, d in enumerate(self.dates)}
        self.year = pd.to_datetime(pd.Series(self.dates)).dt.year.to_numpy()
        self.stop = np.stack([first[f"stop_ticks_{i}"].to_numpy(float) for i in range(self.K)], axis=1)

        def piv(col):
            return (m.pivot(index="date", columns="or_minutes", values=col).reindex(index=self.dates, columns=OR_MINS)
                    .to_numpy(float))
        self.dir, self.fill, self.range_ticks = piv("dir"), piv("fill_slot"), piv("range_ticks")
        vw = piv("vwap_offset_ticks")
        gap, ov = _broadcast(first["gap_ticks"].to_numpy(float)), _broadcast(first["overnight_ticks"].to_numpy(float))
        self.state = {"none": np.ones(self.dir.shape, bool),
                      "vwap_with": (vw != MISSING6) & (self.dir * vw > 0),
                      "gap_with": (gap != MISSING6) & (self.dir * gap > 0),
                      "overnight_with": (ov != MISSING6) & (self.dir * ov > 0)}
        rt_kind, rt_dist = piv("rt_kind"), piv("rt_range_dist_ticks")
        self.rt_ok = (rt_kind == 1) & (rt_dist != -1)
        self.left_out = (rt_kind == 1) & (rt_dist == -1)                 # at or beyond the far side: no cell
        self.rt_slot_all = piv("rt_slot")
        wid = {o: _broadcast(self.stop[:, i]) for o, i in enumerate(self.opt_i) if i is not None}
        rt = {"slot": np.where(self.rt_ok, self.rt_slot_all, -1.0), "at_open": piv("rt_at_open"),
              "fba": piv("rt_fill_bar_against_ticks"), "close": piv("rt_close_ticks"), "worst": piv("rt_worst_ticks"),
              "entry": np.zeros(self.dir.shape), "offset": 0.0,
              "stops": {0: rt_dist, **wid}, "A": {0: piv("rt_range_a")},
              "F": {(0, R): piv(f"rt_range_{RNAME[R]}") for R in RS},
              "ladder": [piv(f"rt_a_{k}") for k in range(self.K)]}
        for o, i in enumerate(self.opt_i):
            if i is not None:
                rt["A"][o] = piv(f"rt_a_{i}")
                rt["F"].update({(o, R): piv(f"rt_{RNAME[R]}_{i}") for R in RS})
        self.views = {"retest": rt}
        kind, lslot = piv("lat_kind"), piv("lat_slot")
        sp = piv("lat_spread_fill_tenths")

        def shift(col):
            x = piv(col)
            return np.where((x != -1) & (lslot != -1), lslot + x, -1.0)
        hd = piv("hand_range_dist_ticks")
        hand = {"at_open": piv("lat_at_open"), "fba": piv("lat_fill_bar_against_ticks"), "close": piv("lat_close_ticks"),
                "worst": piv("lat_worst_ticks"), "entry": np.where(sp >= 0, np.maximum(1.0, sp / 10.0), 1.0),
                "offset": 1.0, "stops": {0: hd, **wid}, "A": {0: shift("hand_range_a")},
                "F": {(0, R): shift(f"hand_range_{RNAME[R]}") for R in RS},
                "ladder": [piv(f"lat_a_{k}") for k in range(self.K)]}
        for o, i in enumerate(self.opt_i):
            if i is not None:
                hand["A"][o] = piv(f"lat_a_{i}")
                hand["F"].update({(o, R): piv(f"lat_{RNAME[R]}_{i}") for R in RS})
        for pol in POLICIES:
            self.views[pol] = {**hand, "slot": np.where(np.isin(kind, g5.KINDS[pol]), lslot, -1.0)}
        self.bench = bench.reset_index(drop=True)
        self.bench_row = self.bench["date"].map(self.row).to_numpy()
        self._bench_cache: dict[tuple, pd.Series] = {}

    # -- trades
    @staticmethod
    def st(v: dict, o: int) -> np.ndarray:
        x = np.asarray(v["stops"][o], dtype=float)
        return np.where(x > 0, x, np.nan)

    def fee(self, st: np.ndarray, risk: float, cap: int) -> np.ndarray:
        return mini_mix_fee(np.where(np.isfinite(st), st, 1.0), risk, cap, self.td, self.fm, self.fM)

    def valid(self, v: dict, c: dict) -> np.ndarray:
        cols = np.array([n in tuple(c["ranges"]) for n in OR_MINS])[None, :]
        return ((self.dir != 0) & (v["slot"] != -1) & (v["slot"] <= c["last_fill_slot"]) & cols
                & self.state[c["state"]] & np.isfinite(self.st(v, c["o"])))

    def today_cost(self, v: dict, o: int, valid: np.ndarray, risk: float, cap: int) -> float:
        """The median round-trip cost in R over the cell's filled records of 2020 to June 2025, priced as a stop
        exit -- before coordination, so no outcome enters (D-257)."""
        st = self.st(v, o)
        sel = valid & (self.year >= TODAY_FROM)[:, None]
        c = (v["entry"][sel] * self.td + self.fee(st, risk, cap)[sel] + STOP_SLIP_TICKS * self.td) / (st[sel] * self.td)
        return float(np.median(c)) if len(c) else float("nan")

    def outcome(self, v: dict, o: int, R: float, risk: float, cap: int, mae: bool = False) -> dict[str, np.ndarray]:
        """Every record's outcome at R on stop option `o`, before coordination; the MAE bound when `mae`."""
        st = self.st(v, o)
        inside = v["at_open"] == 0
        fbs = inside & (v["fba"] >= st)
        A, F = v["A"][o], v["F"][(o, R)]
        stopped = fbs | ((A != -1) & ((F == -1) | (A <= F)))
        target = ~stopped & (F != -1)
        flat = ~stopped & ~target
        exit_slot = np.where(fbs, v["slot"], np.where(stopped, A, np.where(target, F, FLAT_ENTRY)))
        won = np.floor(R * st + 1e-9)
        flat_move = np.where(v["worst"] != MISSING6, v["worst"], v["close"])
        move = np.where(stopped, -st, np.where(target, won, flat_move))
        gross = (move + v["offset"]) / st
        exit_ticks = np.where(stopped, STOP_SLIP_TICKS, np.where(target, 0.0, FLATTEN_SLIP_TICKS))
        cost = (v["entry"] * self.td + self.fee(st, risk, cap) + exit_ticks * self.td) / (st * self.td)
        out = {"gross": gross, "cost": cost, "net": gross - cost, "flat": flat, "stopped": stopped,
               "target": target, "exit": exit_slot}
        if not mae:
            return out
        # the MAE's upper bound in R: a stopped trade's is its stop; any other's the narrowest ATR width not reached
        # before its exit (the capture's ladder), never above its own stop, never below its fill bar's own excursion
        unreached = np.full(st.shape, np.inf)
        for k in range(self.K):
            stk = _broadcast(self.stop[:, k])
            hit = (v["ladder"][k] != -1) & (v["ladder"][k] <= exit_slot)
            unreached = np.where(~hit, np.minimum(unreached, stk), unreached)
        bnd = np.minimum(np.maximum(np.minimum(unreached, st), np.where(inside, v["fba"], 0.0)), st)
        return {**out, "mae": np.clip(np.where(stopped, 1.0, bnd / st), 0.0, 1.0)}

    def kept(self, v: dict, valid: np.ndarray, exit_slot: np.ndarray, coordination: str) -> np.ndarray:
        if coordination == "one_at_a_time":
            return s3.sequential_mask(np.where(valid, v["slot"], np.inf), np.where(valid, exit_slot, -1), valid)
        if coordination != "ranges_locked":
            raise ValueError(coordination)
        order = np.where(valid, v["slot"] * 10 + np.arange(len(OR_MINS))[None, :], np.inf)
        first = np.argmin(order, axis=1)
        side = self.dir[np.arange(len(self.dates)), first]
        return valid & (self.dir == side[:, None])

    # -- the benchmark
    def bench_means(self, o: int, col: int, R: float) -> pd.Series:
        """The unconditional entries' mean move in R per (year, side, slot) on stop option `o` (column `col`'s range
        for the range stop) at R, read strictly; codes 9 (no bracket) and days outside the records left out."""
        key = (o, col if o == 0 else None, R)
        if key in self._bench_cache:
            return self._bench_cache[key]
        b = self.bench
        ok = ~np.isnan(self.bench_row.astype(float))
        r = np.where(ok, self.bench_row, 0).astype(int)
        rn = RNAME[R][1:]
        if o == 0:
            n = OR_MINS[col]
            code = b[f"c_r{n}_{rn}"].to_numpy(float)
            st = self.range_ticks[r, col] + 1.0
        else:
            i = self.opt_i[o]
            code = b[f"c_w{i}_{rn}"].to_numpy(float)
            st = self.stop[r, i]
        worst, close = b["bench_worst_ticks"].to_numpy(float), b["bench_close_ticks"].to_numpy(float)
        flat_move = np.where(worst != MISSING6, worst, close)
        gross = np.where(code == 1, np.floor(R * st + 1e-9) / st, np.where(code == 0, -1.0, flat_move / st))
        use = ok & (code != 9) & (st > 0)
        t = pd.DataFrame({"year": b["year"].to_numpy(int)[use], "side": b["side"].to_numpy(int)[use],
                          "slot": b["bench_after"].to_numpy(int)[use], "gross": gross[use]})
        out = t.groupby(["year", "side", "slot"])["gross"].mean()
        self._bench_cache[key] = out
        return out


def bench_slot(slot: np.ndarray) -> np.ndarray:
    """The latest benchmark slot before each fill bar (-1 if none)."""
    bs = np.array(BENCH_SLOTS)
    idx = np.searchsorted(bs, slot, side="left") - 1
    return np.where(idx >= 0, bs[np.clip(idx, 0, None)], -1)


# ------------------------------------------------------------------------------------------ the grid's statistics

def cells(cfg: dict) -> list[dict]:
    s = cfg["search"]
    out = []
    for a, ranges in enumerate(s["ranges"]):
        for o, stop in enumerate(s["stop"]):
            for t, state in enumerate(s["state"]):
                for j, cut in enumerate(s["last_fill_ct"]):
                    for q, co in enumerate(s["coordination"]):
                        for r, R in enumerate(s["funded_rr"]):
                            out.append({"idx": (a, o, t, j, q, r), "ranges": tuple(ranges), "o": o, "stop": stop,
                                        "state": state, "j": j, "last_fill_ct": cut,
                                        "last_fill_slot": s3._ct_slot(cut), "coordination": co,
                                        "funded_rr": float(R)})
    return out


def funded_risks(grid: Grid6, band: pd.DataFrame, cfg: dict) -> dict[tuple, float]:
    """D-273 per stop: of the funded candidates the one deploying the most risk a day -- the risk times the share of
    2020 to June 2025's stops sizeable at it -- ties to the larger; nan if none is ever sizeable. Keyed (option,
    ranges): an ATR width's stops are its days', the range stop's the retests' range-stop distances in those ranges."""
    from orb5_prep import FUNDED_RISKS, sizeable

    b = band[(band["state"] == "funded_below_2000") & (band["market"] == "NQ")].iloc[0]
    today = grid.year >= TODAY_FROM

    def best(st: np.ndarray) -> float:
        out, val = float("nan"), 0.0
        for r in sorted(FUNDED_RISKS, reverse=True):
            share = float(sizeable(st, r, int(b["cap_micros"]), float(b["tick_value"]),
                                   int(b["cost_drag_floor_ticks"])).mean()) if len(st) else 0.0
            if r * share > val + 1e-9:
                out, val = float(r), r * share
        return out
    res = {}
    for ranges in cfg["search"]["ranges"]:
        cols = np.array([n in tuple(ranges) for n in OR_MINS])[None, :]
        d = grid.views["retest"]["stops"][0][today[:, None] & grid.rt_ok & cols]
        res[(0, tuple(ranges))] = best(d.astype(float))
        for o, i in enumerate(grid.opt_i):
            if i is not None:
                res[(o, tuple(ranges))] = best(grid.stop[today, i])
    return res


def leg_risk(cfg: dict, frisk: dict, c: dict, leg: str) -> tuple[float, int]:
    if leg == "combine":
        return float(cfg["fixed"]["combine"]["risk"]), CAPS["combine"]
    r = frisk[(c["o"], tuple(c["ranges"]))]
    return (r if np.isfinite(r) else float(cfg["fixed"]["combine"]["risk"])), CAPS["funded"]


def leg_stats(grid: Grid6, v: dict, c: dict, R: float, risk: float, cap: int, years: np.ndarray) -> tuple[dict, dict]:
    """(per-year arrays, the trades) of one leg of a cell."""
    valid = grid.valid(v, c)
    o = grid.outcome(v, c["o"], R, risk, cap)
    kept = grid.kept(v, valid, o["exit"], c["coordination"])
    tc = grid.today_cost(v, c["o"], valid, risk, cap)
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
    trades = {"rows": rows, "cols": cols, "metric": metric, "kept": kept, "o": o, "valid": valid, "tc": tc}
    return stats, trades


class Evaluated6(g5.Evaluated):
    """Every cell's two legs' per-year statistics, as matrices (cells x years), and the static feasibility."""

    def __init__(self, grid: Grid6, cfg: dict, sessions: dict[int, float], band: pd.DataFrame, need: float):
        from orb5_prep import sizeable

        self.cfg, self.grid = cfg, grid
        self.cells = cells(cfg)
        self.years = np.array(sorted(sessions))
        ny, nc = len(self.years), len(self.cells)
        self.frisk = funded_risks(grid, band, cfg)
        cb = band[(band["state"] == "combine") & (band["market"] == "NQ")].iloc[0]
        crisk = float(cfg["fixed"]["combine"]["risk"])
        today_days = sum(v for y, v in sessions.items() if y >= TODAY_FROM)
        accounts = int(cfg["gate"]["campaign"]["accounts"])
        self.mat = {leg: {k: np.zeros((nc, ny)) for k in ("n", "metric", "gross", "net", "flat", "n_long",
                                                           "metric_long", "n_short", "metric_short")}
                    for leg in ("combine", "funded")}
        self.tc = {leg: np.full(nc, np.nan) for leg in ("combine", "funded")}
        self.static_ok = np.zeros(nc, bool)
        self.freq = np.zeros(nc)
        v = grid.views["retest"]
        cache: dict[tuple, tuple[dict, dict]] = {}
        for k, c in enumerate(self.cells):
            key = (c["ranges"], c["o"], c["state"], c["j"], c["coordination"])
            if key not in cache:
                cache[key] = leg_stats(grid, v, c, float(cfg["fixed"]["combine"]["rr"]), *leg_risk(cfg, self.frisk,
                                                                                                   c, "combine"),
                                       self.years)
            cs, ct = cache[key]
            fs, _ = leg_stats(grid, v, c, c["funded_rr"], *leg_risk(cfg, self.frisk, c, "funded"), self.years)
            for leg, s in (("combine", cs), ("funded", fs)):
                for name, m in self.mat[leg].items():
                    m[k] = s[name]
                self.tc[leg][k] = s["today_cost"]
            today = grid.year[ct["rows"]] >= TODAY_FROM
            st = grid.st(v, c["o"])[ct["rows"], ct["cols"]]
            sized = sizeable(np.where(np.isfinite(st), st, 0.0), crisk, int(cb["cap_micros"]), float(cb["tick_value"]),
                             int(cb["cost_drag_floor_ticks"]))
            self.freq[k] = (float((today & sized).sum()) / today_days / accounts) if today_days else 0.0
            self.static_ok[k] = bool(self.freq[k] + 1e-9 >= need
                                     and np.isfinite(self.frisk[(c["o"], tuple(c["ranges"]))]))
        self.shape = tuple(len(cfg["search"][a]) for a in AXES)

    def select(self, ymask: np.ndarray) -> tuple[int | None, float]:
        """The plateau rule: the feasible cell maximising min(own value, the median of every configuration one step or
        fewer away in stop -- along the ATR widths; the range stop's neighbours in last_fill only -- and in last fill,
        the rest equal, every neighbour counted, no value the lowest); ties to the earlier cell."""
        ok, v = self.values(ymask)
        V = np.where(np.isnan(v), -np.inf, v).reshape(self.shape)
        med = np.empty(self.shape)
        for idx in np.ndindex(self.shape):
            a, s, t, j, q, r = idx
            ss = [s] if s == 0 else [x for x in (s - 1, s, s + 1) if 1 <= x < self.shape[1]]
            jj = [x for x in (j - 1, j, j + 1) if 0 <= x < self.shape[3]]
            med[idx] = np.median([V[a, x, t, y, q, r] for x in ss for y in jj])
        score = np.where(ok, np.fmin(V.reshape(-1), med.reshape(-1)), -np.inf)
        if not ok.any():
            return None, float("nan")
        best = int(np.argmax(score))                 # every feasible cell at -inf: the earliest feasible (the rule)
        if not np.isfinite(score[best]):
            best = int(np.argmax(ok))
        return best, float(score[best])


# ------------------------------------------------------------------------------------------- the final's readings

def drift_value(grid: Grid6, ev: Evaluated6, k: int) -> tuple[list[dict], float]:
    """D-277 (2): per leg, each kept trade's move less its benchmark's -- the year's mean unconditional entry of the
    same side, at the latest slot before its fill, same stop and R; the yearly-means bound of that excess, and long,
    short and combined beside it. (rows, the smaller leg's bound)."""
    c = ev.cells[k]
    v = grid.views["retest"]
    rows, vals = [], []
    for leg, R in (("combine", float(ev.cfg["fixed"]["combine"]["rr"])), ("funded", c["funded_rr"])):
        _, tr = leg_stats(grid, v, c, R, *leg_risk(ev.cfg, ev.frisk, c, leg), ev.years)
        r, cl = tr["rows"], tr["cols"]
        gross = tr["o"]["gross"][r, cl]
        side = grid.dir[r, cl].astype(int)
        slot = bench_slot(v["slot"][r, cl])
        bm = np.full(len(r), np.nan)
        for col in range(len(OR_MINS)):
            sel = cl == col
            if not sel.any():
                continue
            means = grid.bench_means(c["o"], col, R)
            keys = list(zip(grid.year[r[sel]], side[sel], slot[sel]))
            bm[sel] = [means.get(x, np.nan) for x in keys]
        ex = gross - bm
        by = pd.Series(ex).groupby(grid.year[r]).mean()
        b = g5.bound(by)
        vals.append(b)
        for name, mk in (("long", side > 0), ("short", side < 0), ("combined", np.ones(len(r), bool))):
            rows.append({"section": "drift", "leg": leg, "side": name, "trades": int(mk.sum()),
                         "e_metric": float(tr["metric"][mk].mean()) if mk.any() else float("nan"),
                         "benchmark_gross": float(np.nanmean(bm[mk])) if mk.any() else float("nan"),
                         "excess": float(np.nanmean(ex[mk])) if mk.any() else float("nan"),
                         "excess_bound": g5.bound(pd.Series(ex[mk]).groupby(grid.year[r][mk]).mean()) if mk.any()
                         else float("nan"),
                         "unmatched": int(np.isnan(bm[mk]).sum())})
    value = float(np.fmin(vals[0], vals[1])) if not any(np.isnan(vals)) else float("nan")
    rows.append({"section": "drift", "leg": "value", "excess_bound": value})
    return rows, value


def final_details(grid: Grid6, ev: Evaluated6, k: int, sessions: dict[int, float]) -> list[dict]:
    """The legs (with the skew of R and minutes to resolution), the flatten detail, the retest's fill rate and its
    gapped and left-out shares, and the baseline (the hand-traded stop entry) at the same cell."""
    from scipy import stats as sps

    c = ev.cells[k]
    v = grid.views["retest"]
    out = []
    for leg, R in (("combine", float(ev.cfg["fixed"]["combine"]["rr"])), ("funded", c["funded_rr"])):
        risk, cap = leg_risk(ev.cfg, ev.frisk, c, leg)
        _, tr = leg_stats(grid, v, c, R, risk, cap, ev.years)
        r, cl = tr["rows"], tr["cols"]
        o = tr["o"]
        g = o["gross"][r, cl]
        fl = o["flat"][r, cl]
        res = ~fl
        mins = (o["exit"][r, cl] - v["slot"][r, cl])[res]
        hit = o["target"][r, cl]
        out.append({"section": "final_leg", **g5.leg_summary(ev, k, leg, sessions), "today_cost": float(tr["tc"]),
                    "hit_rate": float(hit.mean()) if len(hit) else float("nan"),
                    "efr": float(g.mean() / tr["tc"]) if len(g) and tr["tc"] > 0 else float("nan"),
                    "skew_gross": float(sps.skew(g)) if len(g) > 2 else float("nan"),
                    "median_minutes_to_resolution": float(np.median(mins)) if len(mins) else float("nan")})
        # per era and pooled (D-271 (1)): e, its bound, gross and net, hit rate, trades a day, the flatten share
        yr = grid.year[r]
        for era, (lo_y, hi_y) in [("pooled", (min(ev.years), max(ev.years)))] + [
                (f"{a}-{b}", (a, b)) for a, b in ev.cfg["selection"]["eras"]["split"]]:
            mk = (yr >= lo_y) & (yr <= hi_y)
            days = sum(n for y, n in sessions.items() if lo_y <= y <= hi_y)
            met = tr["metric"][mk]
            out.append({"section": "era_leg", "leg": leg, "era": era, "trades": int(mk.sum()),
                        "per_day": float(mk.sum() / days) if days else float("nan"),
                        "e_metric": float(met.mean()) if mk.any() else float("nan"),
                        "bound": g5.bound(pd.Series(met).groupby(yr[mk]).mean()) if mk.any() else float("nan"),
                        "gross": float(g[mk].mean()) if mk.any() else float("nan"),
                        "net": float(o["net"][r, cl][mk].mean()) if mk.any() else float("nan"),
                        "hit_rate": float(hit[mk].mean()) if mk.any() else float("nan"),
                        "flat_share": float(fl[mk].mean()) if mk.any() else float("nan")})
        out.append({"section": "flatten", "leg": leg, "trades": int(len(g)), "flat_share": float(fl.mean())
                    if len(g) else float("nan"), "flat_mean_gross": float(g[fl].mean()) if fl.any() else float("nan")})
        for pol in POLICIES:
            st_b, tb = leg_stats(grid, grid.views[pol], c, R, risk, cap, ev.years)
            n = st_b["n"]
            means = pd.Series(np.where(n > 0, st_b["metric"] / np.maximum(n, 1), np.nan))
            out.append({"section": "baseline", "leg": leg, "policy": pol, "trades": int(n.sum()),
                        "e_metric": float(st_b["metric"].sum() / max(n.sum(), 1)), "bound": g5.bound(means),
                        "gross": float(st_b["gross"].sum() / max(n.sum(), 1)),
                        "net": float(st_b["net"].sum() / max(n.sum(), 1)), "today_cost": float(tb["tc"]),
                        "hit_rate": float(tb["o"]["target"][tb["rows"], tb["cols"]].mean()) if len(tb["rows"])
                        else float("nan")})
    for pol in POLICIES:                                     # the baseline's value: the smaller leg's bound
        legs = [x["bound"] for x in out if x.get("section") == "baseline" and x.get("policy") == pol]
        out.append({"section": "baseline", "leg": "value", "policy": pol,
                    "bound": float(np.fmin(legs[0], legs[1])) if not any(np.isnan(legs)) else float("nan")})
    cols = np.array([n in tuple(c["ranges"]) for n in OR_MINS])[None, :]
    brk = (grid.dir != 0) & (grid.fill != -1) & cols & grid.state[c["state"]]
    filled = brk & grid.rt_ok & (grid.rt_slot_all <= c["last_fill_slot"])
    left = brk & grid.left_out & (grid.rt_slot_all <= c["last_fill_slot"])
    out.append({"section": "retest", "breakouts": int(brk.sum()), "retests_by_last_fill": int(filled.sum()),
                "fill_rate": float(filled.sum() / max(brk.sum(), 1)),
                "gapped_open_share": float(v["at_open"][filled].mean()) if filled.any() else float("nan"),
                "left_out_beyond_far_side": int(left.sum())})
    return out


def locked_added(grid: Grid6, ev: Evaluated6, k: int) -> list[dict]:
    """D-269 (2): the trades ranges_locked takes beyond one_at_a_time for the final cell, each leg."""
    c = ev.cells[k]
    v = grid.views["retest"]
    out = []
    for leg, R in (("combine", float(ev.cfg["fixed"]["combine"]["rr"])), ("funded", c["funded_rr"])):
        risk, cap = leg_risk(ev.cfg, ev.frisk, c, leg)
        _, seq = leg_stats(grid, v, {**c, "coordination": "one_at_a_time"}, R, risk, cap, ev.years)
        _, lock = leg_stats(grid, v, {**c, "coordination": "ranges_locked"}, R, risk, cap, ev.years)
        add = lock["kept"] & ~seq["kept"]
        rows, cols = np.nonzero(add)
        met = lock["o"]["gross"][rows, cols] - lock["tc"]
        y = pd.Series(met).groupby(grid.year[rows]).mean()
        out.append({"section": "locked_added", "leg": leg, "added": int(len(rows)),
                    "e_metric": float(met.mean()) if len(met) else float("nan"), "bound": g5.bound(y),
                    "cost": float(lock["o"]["cost"][rows, cols].mean()) if len(rows) else float("nan")})
    return out


# ------------------------------------------------------------------------------------------------------ the gate

def gate_trades(grid: Grid6, ev: Evaluated6, selections: dict[int, int | None]) -> pd.DataFrame:
    """Each test year's out-of-sample trades: the selection made on the years before it, both legs' outcomes -- each
    leg's R its move less its cell's median cost of 2020 to June 2025 (D-271, D-276) -- on the trades the funded leg's
    coordination keeps."""
    v = grid.views["retest"]
    out = []
    for y, k in selections.items():
        if k is None:
            continue
        c = ev.cells[k]
        valid = grid.valid(v, c)
        legs = {}
        for leg, R in (("c", float(ev.cfg["fixed"]["combine"]["rr"])), ("f", c["funded_rr"])):
            risk, cap = leg_risk(ev.cfg, ev.frisk, c, "combine" if leg == "c" else "funded")
            legs[leg] = (grid.outcome(v, c["o"], R, risk, cap, mae=True), grid.today_cost(v, c["o"], valid, risk, cap))
        of = legs["f"][0]
        kept = grid.kept(v, valid, of["exit"], c["coordination"]) & (grid.year == y)[:, None]
        for r, col in zip(*np.nonzero(kept)):
            row = {"date": grid.dates[r], "year": y, "o": c["o"], "col": int(col), "ranges": c["ranges"],
                   "entry_t": float(v["slot"][r, col]), "exit_t": float(of["exit"][r, col]),
                   "flat_f": bool(of["flat"][r, col])}
            for leg, (oo, tc) in legs.items():
                row[f"r_{leg}"] = float(oo["gross"][r, col] - tc)
                row[f"mae_{leg}"] = float(oo["mae"][r, col])
            out.append(row)
    return pd.DataFrame(out)


def gate_blocks(grid: Grid6, t: pd.DataFrame, days: list[str], frisk: float, final_rr: float, band: pd.DataFrame,
                seed: int):
    """D-271 (4): each trade's stop a micro drawn (seeded) from 2020 to June 2025 at its stop -- an ATR width's from
    the days, the range stop's from its range's retests -- left out unless sizeable in both states. One block a
    trading day, trades in entry order."""
    from orb5_prep import sizeable
    from propedge.outcomes.distribution import DayBlock

    rng = np.random.default_rng(seed)
    today = grid.year >= TODAY_FROM
    cb = band[(band["state"] == "combine") & (band["market"] == "NQ")].iloc[0]
    fb = band[(band["state"] == "funded_below_2000") & (band["market"] == "NQ")].iloc[0]
    tv = float(cb["tick_value"])
    if len(t):
        st = np.empty(len(t))
        for n in range(len(t)):
            o, col = int(t["o"].iat[n]), int(t["col"].iat[n])
            if o == 0:
                pool = grid.views["retest"]["stops"][0][today & grid.rt_ok[:, col], col]
            else:
                pool = grid.stop[today, grid.opt_i[o]]
            if not len(pool):
                raise SystemExit(f"REFUSED: no 2020 to June 2025 stop to draw for option {o}, range column {col}.")
            st[n] = float(rng.choice(pool))
        ok = (sizeable(st, 1500.0, int(cb["cap_micros"]), tv, int(cb["cost_drag_floor_ticks"]))
              & sizeable(st, frisk, int(fb["cap_micros"]), tv, int(fb["cost_drag_floor_ticks"])))
        t = t.assign(rpc=st * tv)[ok]
    by = {d: g.sort_values("entry_t", kind="stable") for d, g in t.groupby("date")} if len(t) else {}
    blocks = []
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
    protocol = Protocol(name="orb6", combine_rr=1.0, combine_risk=1500.0, funded_rr=final_rr, funded_risk=frisk,
                        trades_per_day=max(1, int(busiest)), payout_path="standard", keep_balance=0.0,
                        payout_frac=1.0, max_concurrent_accounts=int(camp["accounts"]), family="orb6",
                        source="config/orb6_grid.yaml", note="ORB6's gate (D-278)")
    policy = RiskPolicy(id="orb6_gate", root=Phase(
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


# --------------------------------------------------------------------------------------------------------- main

def _key(c: dict | None) -> dict:
    if c is None:
        return {"ranges": None}
    return {"ranges": "+".join(map(str, c["ranges"])), "stop": str(c["stop"]), "state": c["state"],
            "last_fill_ct": c["last_fill_ct"], "coordination": c["coordination"], "funded_rr": c["funded_rr"]}


def main(argv: list[str] | None = None, *, results_dir: Path | None = None, runs_dir: Path | None = None,
         record: bool = True, data: tuple | None = None) -> int:
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
        print(f"REFUSED: ORB6 is declared by {DECLARATION} (DECISIONS.md); got {a.declaration!r} or the row is missing.")
        return 2
    cfg = config()
    k_total = math.prod(len(cfg["search"][x]) for x in AXES)
    if k_total != int(cfg["k"]):
        print(f"REFUSED: the grid holds {k_total} configurations, the config declares {cfg['k']}.")
        return 2
    if tuple(cfg["search"]["state"]) != STATES:
        print(f"REFUSED: the declared states {cfg['search']['state']} are not {STATES}.")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    m, bench, sessions = data if data is not None else load(rd, Path(runs_dir) if runs_dir is not None else ROOT / "runs")
    fm = FillModel.load("assumed")
    q = params("NQ")
    grid = Grid6(m, bench, cfg, float(fm.round_turn_by_instrument[q["micro"]]),
                 float(fm.round_turn_by_instrument["NQ"]), q["micro_tick"] * q["micro_point_value"])
    band = read_result(BAND_FILE)
    need = setups_minimum(float(cfg["fixed"]["combine"]["rr"]), float(cfg["fixed"]["combine"]["risk"]), 0.0)
    ev = Evaluated6(grid, cfg, sessions, band, float(need))
    years = list(ev.years)
    rows = []
    ok_all, v_all = ev.values(np.ones(len(years), bool))
    for k, c in enumerate(ev.cells):
        r = {"section": "grid", **_key(c), "feasible": bool(ok_all[k]), "value": float(v_all[k]),
             "freq_per_account_today": float(ev.freq[k]), "funded_risk": ev.frisk[(c["o"], tuple(c["ranges"]))]}
        for leg in ("combine", "funded"):
            n = ev.mat[leg]["n"][k].sum()
            g = float(ev.mat[leg]["gross"][k].sum() / max(n, 1))
            r[f"{leg}_n"] = int(n)
            r[f"{leg}_metric"] = float(ev.mat[leg]["metric"][k].sum() / max(n, 1))
            r[f"{leg}_gross"] = g
            r[f"{leg}_net"] = float(ev.mat[leg]["net"][k].sum() / max(n, 1))
            r[f"{leg}_flat"] = float(ev.mat[leg]["flat"][k].sum() / max(n, 1))
            r[f"{leg}_today_cost"] = float(ev.tc[leg][k])
            r[f"{leg}_efr"] = float(g / ev.tc[leg][k]) if n and ev.tc[leg][k] > 0 else float("nan")
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
    w1_lb = g5.bound(wf_s)
    w1 = bool(wf_s.isna().any() or not (w1_lb > 0))
    # the final selection
    kf, score = ev.select(np.ones(len(years), bool))
    final = ev.cells[kf] if kf is not None else None
    w2, b_kill, g_kill, gate_passed = True, True, True, False
    if final is not None:
        fv = float(v_all[kf])
        era_rows, flagged, low = g5.era_reading(ev, kf, cfg["selection"]["eras"]["split"], 2000, cfg["seeds"]["eras"])
        fv_used = min(fv, low) if flagged else fv
        w2 = bool(not ok_all[kf] or not (fv_used > 0))
        frisk = float(ev.frisk[(final["o"], tuple(final["ranges"]))])
        rows.append({"section": "final", **_key(final), "plateau_score": score, "value": fv, "value_used": fv_used,
                     "era_flagged": flagged, "funded_risk": frisk, "freq_per_account_today": float(ev.freq[kf])})
        rows += final_details(grid, ev, kf, sessions)
        rows += [{"section": "eras", **r} for r in era_rows.values()]
        drift_rows, dv = drift_value(grid, ev, kf)
        rows += drift_rows
        b_kill = bool(not (dv > 0))
        rows += locked_added(grid, ev, kf)
        # the gate on the walk-forward's out-of-sample trades
        t = gate_trades(grid, ev, sels)
        stats = {}
        for leg, col in (("combine", "r_c"), ("funded", "r_f")):
            by = t.groupby("year")[col].mean() if len(t) else pd.Series(dtype=float)
            stats[leg] = {"e": float(t[col].mean()) if len(t) else float("nan"), "lb": g5.bound(by)}
        test_days = [d for d, y in zip(grid.dates, grid.year) if y >= WF_FIRST]
        n_used = 0
        if np.isfinite(frisk):
            blocks, n_used = gate_blocks(grid, t, test_days, frisk, final["funded_rr"], band, cfg["seeds"]["stops"])
            if np.isfinite([stats[x]["lb"] for x in stats]).all() and n_used:
                gdf, gate_passed = run_gate(blocks, stats, final["funded_rr"], frisk, cfg["gate"], cfg["seeds"]["gate"])
                for _, gr in gdf.iterrows():
                    rows.append({"section": "gate",
                                 **{kk: vv for kk, vv in gr.items() if not isinstance(vv, (list, dict))}})
        rows.append({"section": "gate_inputs", "oos_trades": int(len(t)), "trades_used": n_used,
                     "e_combine": stats["combine"]["e"], "lb_combine": stats["combine"]["lb"],
                     "e_funded": stats["funded"]["e"], "lb_funded": stats["funded"]["lb"], "funded_risk": frisk})
        g_kill = not gate_passed
    # SPA and the deflated Sharpe ratio, reported
    feas = np.nonzero(ok_all)[0]
    Y = np.array([[ev.year_value(int(k), y) for y in years] for k in feas]) if len(feas) else np.zeros((0, len(years)))
    rows.append({"section": "spa", "cells": int(len(feas)), "p_value": g5.spa_pvalue(Y, 2000, cfg["seeds"]["spa"])})
    if kf is not None and len(Y):
        srs = Y.mean(axis=1) / np.where(Y.std(axis=1, ddof=1) > 0, Y.std(axis=1, ddof=1), np.nan)
        yf = np.array([ev.year_value(kf, y) for y in years])
        rows.append({"section": "dsr", "n_trials": k_total, "dsr": g5.deflated_sharpe(yf, srs, k_total)})
    lines = {"W1": w1, "W2": w2, "B": b_kill, "G": g_kill}
    for ln, x in lines.items():
        rows.append({"section": "kline", "line": ln, "killed": bool(x), "value": w1_lb if ln == "W1" else None})
    killed = [ln for ln, x in lines.items() if x]
    # D-277's stopping points: W1 failing closes the branch; a later line closes the specification
    stop_point = ("W1: the execution model invalidated, the 08:30 NQ breakout branch closed" if w1 else
                  "a later gate: this specification closed" if killed else
                  "continue: one confirmation on the held-back window")
    rows.append({"section": "summary", "verdict": "kill" if killed else "continue", "killed_by": ",".join(killed),
                 "stopping_point": stop_point, "k": k_total, "years": f"{years[0]}-{years[-1]}",
                 "declaration": DECLARATION, "configurations_feasible_all_years": int(ok_all.sum())})
    out = pd.DataFrame(rows)
    write_result(out, "orb6_grid", script=SCRIPT, seed=int(cfg["seeds"]["gate"]), exploratory=True,
                 results_dir=results_dir,
                 notes={"status": "ORB6's screen, declared before it ran (D-278); EXPLORATORY in that its design is not "
                                  "blind to ORB5's results; only the held-back confirmation can decide"},
                 parameters={"config": "config/orb6_grid.yaml", "runs": cfg["runs"], "k": k_total,
                             "fill_profile": "assumed", "fee": "NQ minis with MNQ micros (D-276, D-278)",
                             "seeds": cfg["seeds"], "decision": DECLARATION},
                 description="ORB6's declared grid on NQ 2009 to June 2025: every configuration, the plateau "
                             "selection, its walk-forward from 2013, the era rule, the per-side drift benchmark, the "
                             "D-145 gate on the walk-forward's out-of-sample trades, and the kill lines W1, W2, B and "
                             "G with D-277's stopping points, all fixed in config/orb6_grid.yaml before the run.")
    if record:
        VariantCounter().record(prereg_id=f"{DECLARATION}:orb6_grid", seed=int(cfg["seeds"]["gate"]), exploratory=True,
                                params={"study": "ORB6 grid", "k": k_total, "market": "NQ"},
                                label=f"ORB6's declared grid: {k_total} configurations (D-278)")
    pd.set_option("display.width", 250)
    print(out[out["section"].isin(["final", "final_leg", "eras", "drift", "baseline", "flatten", "retest",
                                   "locked_added", "gate_inputs", "spa", "dsr", "kline", "summary"])]
          .dropna(axis=1, how="all").round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
