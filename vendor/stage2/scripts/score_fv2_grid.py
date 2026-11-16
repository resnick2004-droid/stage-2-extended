"""FV2's declared grid (T16 item 11; D-283): config/fv2_grid.yaml scored on NQ's development years -- the selection,
its walk-forward, the era rule, the per-side drift benchmark and the D-145 gate on the walk-forward's out-of-sample
trades -- all fixed in that file before this script read an outcome.

    python scripts/score_fv2_grid.py --declaration D-283

FV2's cheap screen (step 3 of `docs/RESEARCH_PROTOCOL.md`), declared by D-283 under D-277's stopping rule: it refuses
to run unless its declaring decision is in DECISIONS.md. Reads FV2's captures R111-R116, drops FOMC days, refuses any
record before 2009-06-01 or on or after 2025-07-01 (the held-back window, D-237).

**A trade** (`trades`): a recorded signal in the cell's sessions with the cell's trigger, a reversion -- or a
continuation where the cell takes them -- whose entry at two minutes filled, a reversion only with at least 0.8 x the
Combine's target of room. Its bracket on the session's stop at R (or, the funded leg's `fair_value`, at fair value's near
edge from the entry; a continuation, or a trade with fair value behind its entry, at 1.5R): stopped if the stop's
passage comes no later than the target's (equal slots the stop's; every entry is at a bar's open, so its bar is walked);
else the target at R x the stop rounded down to a whole tick (fair value at its whole-tick distance); else the flatten
at the worst of 15:07-15:10 (D-263), the 15:08 close where none was recorded. Its move in R from the entry bar's open;
its costs: the entry max(1 tick, the recorded spread), the fee of NQ minis with MNQ micros at the trade's
micro-equivalent size (D-276; the Combine at its risk under 37, the funded risk under 15), the exit 1 tick on a stop,
none at a target, 2 on the flatten. Its metric: the move less the cell's median round-trip cost in R over its candidate
trades of 2020 to June 2025, priced as a stop exit (no outcome). **Coordination**: per day in signal order, a trade
taken only after the previous one's exit bar, at most five (one an account, five accounts).

**The drift benchmark (kill line B)**: each kept trade's move less the year's mean move of the capture's unconditional
entries of the same side, in its session at the latest benchmark slot before its entry bar, on the session's stop with
the same target, read strictly and priced alike (the cost cancels).

**The gate**: the MAE a trade's settlement reads (D-156) is its stop for a stopped trade and, the capture recording no
path below the stop, its stop for any other too -- the bound that never flatters (D-284); the gate with the MAE at
zero for unstopped trades is reported beside it, never as the verdict. Each leg's outcomes are keyed by its R, the
funded leg's by a label of its own (the engine reads the key only to pick the series).

Writes results/fv2_grid.csv: `capped`, `grid`, `walkforward`, `final`, `final_leg`, `era_leg`, `eras`, `by_session`,
`latency`, `drift`, `gate_inputs`, `gate`, `gate_mae0`, `spa`, `dsr`, `kline`, `summary` rows.
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
from propedge.outcomes.fv2_core import BENCH, MISSING_FV, ROOM_MIN, SESSIONS  # noqa: E402
from propedge.outcomes.orb_core import FLAT_ENTRY  # noqa: E402

SCRIPT = "scripts/score_fv2_grid.py"
DECLARATION = "D-283"
CONFIG = ROOT / "config" / "fv2_grid.yaml"
WF_FIRST, TODAY_FROM = g5.WF_FIRST, g5.TODAY_FROM
AXES = ("sessions", "trigger", "continuation", "combine", "funded_target")
SESSION_NAMES = tuple(s[0] for s in SESSIONS)
SESSION_OPEN = {s[0]: s[1] for s in SESSIONS}
MAX_PER_DAY = 5
FLAT_MAX = g5.FLAT_MAX
CAP_MAX = 0.02
STOP_SLIP_TICKS, FLATTEN_SLIP_TICKS = g5.STOP_SLIP_TICKS, g5.FLATTEN_SLIP_TICKS
FUNDED_KEY = {"r1.5": 1.5 + 1e-6, "fair_value": 2.0}      # labels for the funded leg's outcome series in the gate


def config(path: Path | None = None) -> dict:
    return yaml.safe_load(Path(path or CONFIG).read_text(encoding="utf-8"))


# ------------------------------------------------------------------------------------------------- the records

def load(rd: Path, runs_dir: Path, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[int, float]]:
    """(signals, sessions, bench, trading days a year): FOMC days out, the held-back window never read."""
    frames, cells = [], []
    for run in cfg["runs"]:
        f = rd / f"manual_{run.replace('-', '_')}.csv"
        if not f.is_file():
            raise SystemExit(f"REFUSED: {run} is not ingested.")
        t = pd.read_csv(f, low_memory=False)
        cells.append(t[t["kind"] == "session"].assign(run=run))
        frames.append(t[t["kind"] != "session"])
    a = pd.concat(frames, ignore_index=True)
    a["date"] = a["date"].astype(str)
    dt = pd.to_datetime(a["date"]).dt.date
    if (dt >= s3.HELD_BACK).any() or (dt < s3.START).any():
        raise SystemExit("REFUSED: a record outside 2009-06-01 to 2025-06-30 -- the held-back window is never read "
                         "here (D-237).")
    if a[a["kind"] == "day"]["date"].duplicated().any():
        raise SystemExit("REFUSED: a day recorded twice across the runs.")
    sessions = s3.trading_days(pd.concat(cells, ignore_index=True), runs_dir, cfg)
    if sessions is None:
        raise SystemExit("REFUSED: a run record (runs/<run>/ingested.json) is missing: the trading days need it.")
    a = a[~a["date"].isin(s3.fomc_dates(cfg))]
    ses = a[a["kind"] == "fvsession"].copy()
    stops = ses[["date", "session", "stop_ticks"]]
    sig = a[a["kind"] == "signal"].drop(columns=["stop_ticks"], errors="ignore").merge(
        stops, on=["date", "session"], how="left", validate="many_to_one")
    bench = a[a["kind"] == "bench"].drop(columns=["stop_ticks"], errors="ignore").merge(
        stops, on=["date", "session"], how="left", validate="many_to_one")
    if sig["stop_ticks"].isna().any() or bench["stop_ticks"].isna().any():
        raise SystemExit("REFUSED: a signal or benchmark row without its session's stop.")
    return sig, ses, bench, sessions


class Signals:
    """Every recorded signal as arrays, in day and time order."""

    def __init__(self, sig: pd.DataFrame, fee_micro: float, fee_mini: float, tick_dollars: float):
        s = sig.sort_values(["date", "slot"], kind="stable").reset_index(drop=True)
        self.df = s
        self.fm, self.fM, self.td = float(fee_micro), float(fee_mini), float(tick_dollars)
        self.year = pd.to_datetime(s["date"]).dt.year.to_numpy()
        self.day = pd.factorize(s["date"])[0]
        self.session = s["session"].to_numpy()
        f = lambda c: s[c].to_numpy(float)                                       # noqa: E731
        self.slot, self.phase, self.dir, self.bits = f("slot"), f("phase"), f("dir"), f("trigger_bits").astype(int)
        self.room, self.st, self.bar = f("fv_ticks"), f("stop_ticks"), f("bar")
        self.a, self.f1, self.f15, self.ffv = f("a"), f("f1"), f("f15"), f("ffv")
        self.dfe, self.close, self.worst = f("fv_from_entry_ticks"), f("close_ticks"), f("worst_ticks")
        self.entry2 = f("entry_ticks")
        sp = f("spread_tenths")
        self.entry_cost = np.where(sp >= 0, np.maximum(1.0, sp / 10.0), 1.0)
        self.alt = {}
        for L in (0, 5):                     # a CSV reads the codes as numbers: 012 -> 12.0; back to three digits
            codes = s[f"codes_l{L}"].map(lambda x: f"{int(float(x)):03d}").to_numpy()
            if not all(len(c) == 3 and set(c) <= set("0129") for c in codes):
                raise SystemExit(f"REFUSED: a malformed latency-{L} outcome code.")
            self.alt[L] = (f(f"entry_ticks_l{L}"), codes)

    def fee(self, risk: float, cap: int) -> np.ndarray:
        return mini_mix_fee(np.where(self.st > 0, self.st, 1.0), risk, cap, self.td, self.fm, self.fM)

    def candidates(self, c: dict) -> np.ndarray:
        trig = {"bos": (self.bits & 1) > 0, "displacement": (self.bits & 2) > 0,
                "either": self.bits > 0}[c["trigger"]]
        rc = float(c["combine"]["rr"])
        room_ok = (self.phase == 0) | (self.room + 1e-9 >= ROOM_MIN * rc * self.st)
        cont_ok = (self.phase == 1) | bool(c["continuation"])
        return (np.isin(self.session, list(c["sessions"])) & trig & room_ok & cont_ok & (self.bar != -1)
                & (self.st > 0))

    def outcome(self, target: str, R: float | None, risk: float, cap: int) -> dict[str, np.ndarray]:
        """Every signal's outcome: `target` 'r' at R, or 'fv' (fair value; a continuation or fair value behind the
        entry at 1.5R)."""
        st = self.st
        if target == "r":
            F = self.f1 if R == 1.0 else self.f15
            won = np.floor(R * st + 1e-9)
            rr = np.full(st.shape, R)
        else:
            to_fv = (self.phase == 1) & (self.dfe > 0)
            F = np.where(to_fv, self.ffv, self.f15)
            won = np.where(to_fv, self.dfe, np.floor(1.5 * st + 1e-9))
            rr = np.where(to_fv, self.dfe / np.where(st > 0, st, 1.0), 1.5)
        A = self.a
        stopped = (A != -1) & ((F == -1) | (A <= F))
        target_hit = ~stopped & (F != -1)
        flat = ~stopped & ~target_hit
        exit_slot = np.where(stopped, A, np.where(target_hit, F, FLAT_ENTRY))
        flat_move = np.where(self.worst != MISSING_FV, self.worst, self.close)
        move = np.where(stopped, -st, np.where(target_hit, won, flat_move))
        safe = np.where(st > 0, st, 1.0)
        gross = move / safe
        exit_ticks = np.where(stopped, STOP_SLIP_TICKS, np.where(target_hit, 0.0, FLATTEN_SLIP_TICKS))
        cost = (self.entry_cost * self.td + self.fee(risk, cap) + exit_ticks * self.td) / (safe * self.td)
        return {"gross": gross, "cost": cost, "net": gross - cost, "flat": flat, "stopped": stopped,
                "target": target_hit, "exit": exit_slot, "rr": rr, "flat_move": flat_move}

    def today_cost(self, cand: np.ndarray, risk: float, cap: int) -> float:
        sel = cand & (self.year >= TODAY_FROM)
        safe = np.where(self.st > 0, self.st, 1.0)
        c = (self.entry_cost * self.td + self.fee(risk, cap) + STOP_SLIP_TICKS * self.td) / (safe * self.td)
        return float(np.median(c[sel])) if sel.any() else float("nan")

    def kept(self, cand: np.ndarray, exit_slot: np.ndarray) -> np.ndarray:
        """Per day in signal order: a trade only after the previous one's exit bar, at most five a day."""
        out = np.zeros(len(cand), bool)
        idx = np.nonzero(cand)[0]
        day, bar, ex = self.day[idx], self.bar[idx], exit_slot[idx]
        cur, busy, n = -1, -1.0, 0
        for k in range(len(idx)):
            if day[k] != cur:
                cur, busy, n = day[k], -1.0, 0
            if n < MAX_PER_DAY and bar[k] > busy:
                out[idx[k]] = True
                busy, n = ex[k], n + 1
        return out


# ------------------------------------------------------------------------------------------ the grid's statistics

def cells(cfg: dict) -> list[dict]:
    s = cfg["search"]
    out = []
    for a, ses in enumerate(s["sessions"]):
        for b, trig in enumerate(s["trigger"]):
            for c_, cont in enumerate(s["continuation"]):
                for d, comb in enumerate(s["combine"]):
                    for e, ft in enumerate(s["funded_target"]):
                        out.append({"idx": (a, b, c_, d, e), "sessions": tuple(ses), "trigger": trig,
                                    "continuation": bool(cont), "combine": {"rr": float(comb["rr"]),
                                                                            "risk": float(comb["risk"])},
                                    "funded_target": ft})
    return out


def funded_risks(ses: pd.DataFrame, band: pd.DataFrame, cfg: dict) -> dict[tuple, float]:
    """D-273 per session set: of the funded candidates the one deploying the most risk a day -- risk times the share of
    2020 to June 2025's session stops sizeable at it -- ties to the larger."""
    from orb5_prep import FUNDED_RISKS, sizeable

    b = band[(band["state"] == "funded_below_2000") & (band["market"] == "NQ")].iloc[0]
    yr = pd.to_datetime(ses["date"]).dt.year
    out = {}
    for sset in cfg["search"]["sessions"]:
        st = ses[(yr >= TODAY_FROM) & (ses["present"] == 1) & ses["session"].isin(sset)]["stop_ticks"].to_numpy(float)
        best, val = float("nan"), 0.0
        for r in sorted(FUNDED_RISKS, reverse=True):
            share = float(sizeable(st, r, int(b["cap_micros"]), float(b["tick_value"]),
                                   int(b["cost_drag_floor_ticks"])).mean()) if len(st) else 0.0
            if r * share > val + 1e-9:
                best, val = float(r), r * share
        out[tuple(sset)] = best
    return out


def cap_shares(ses: pd.DataFrame, cfg: dict) -> dict[tuple, float]:
    """Per session set, the share of 2020 to June 2025's present sessions whose signals ran past the capture's cap."""
    yr = pd.to_datetime(ses["date"]).dt.year
    out = {}
    for sset in cfg["search"]["sessions"]:
        x = ses[(yr >= TODAY_FROM) & (ses["present"] == 1) & ses["session"].isin(sset)]
        out[tuple(sset)] = float((x["signals_beyond_cap"] > 0).mean()) if len(x) else 1.0
    return out


def leg_spec(cfg: dict, frisk: dict, c: dict, leg: str) -> tuple[str, float | None, float, int]:
    if leg == "combine":
        return "r", c["combine"]["rr"], c["combine"]["risk"], CAPS["combine"]
    r = frisk[tuple(c["sessions"])]
    risk = r if np.isfinite(r) else float(cfg["fixed"].get("fallback_risk", 1000.0))
    return ("r", 1.5, risk, CAPS["funded"]) if c["funded_target"] == "r1.5" else ("fv", None, risk, CAPS["funded"])


def leg_stats(S: Signals, cand: np.ndarray, spec: tuple, years: np.ndarray) -> tuple[dict, dict]:
    target, R, risk, cap = spec
    o = S.outcome(target, R, risk, cap)
    kept = S.kept(cand, o["exit"])
    tc = S.today_cost(cand, risk, cap)
    k = np.nonzero(kept)[0]
    yi = np.searchsorted(years, S.year[k])
    metric = o["gross"][k] - tc
    dirs = S.dir[k]
    ny = len(years)

    def bc(w=None, mask=None):
        idx, ww = (yi, w) if mask is None else (yi[mask], None if w is None else w[mask])
        return np.bincount(idx, weights=ww, minlength=ny).astype(float)
    stats = {"n": bc(), "metric": bc(metric), "gross": bc(o["gross"][k]), "net": bc(o["net"][k]),
             "flat": bc(o["flat"][k].astype(float)), "n_long": bc(mask=dirs > 0), "metric_long": bc(metric, dirs > 0),
             "n_short": bc(mask=dirs < 0), "metric_short": bc(metric, dirs < 0), "today_cost": tc}
    return stats, {"k": k, "metric": metric, "o": o, "tc": tc, "kept": kept}


class EvaluatedFV(g5.Evaluated):
    """Every cell's two legs' per-year statistics (cells x years) and the static feasibility."""

    def __init__(self, S: Signals, ses: pd.DataFrame, cfg: dict, sessions: dict[int, float], band: pd.DataFrame,
                 need: dict[tuple, float]):
        from orb5_prep import sizeable

        self.cfg, self.S = cfg, S
        self.cells = cells(cfg)
        self.years = np.array(sorted(sessions))
        ny, nc = len(self.years), len(self.cells)
        self.frisk = funded_risks(ses, band, cfg)
        self.capped = cap_shares(ses, cfg)
        cb = band[(band["state"] == "combine") & (band["market"] == "NQ")].iloc[0]
        today_days = sum(v for y, v in sessions.items() if y >= TODAY_FROM)
        accounts = int(cfg["gate"]["campaign"]["accounts"])
        self.mat = {leg: {k: np.zeros((nc, ny)) for k in ("n", "metric", "gross", "net", "flat", "n_long",
                                                           "metric_long", "n_short", "metric_short")}
                    for leg in ("combine", "funded")}
        self.tc = {leg: np.full(nc, np.nan) for leg in ("combine", "funded")}
        self.static_ok = np.zeros(nc, bool)
        self.freq = np.zeros(nc)
        cache: dict[tuple, tuple[dict, dict]] = {}
        for k, c in enumerate(self.cells):
            cand = S.candidates(c)
            key = (c["sessions"], c["trigger"], c["continuation"], c["combine"]["rr"], c["combine"]["risk"])
            if key not in cache:
                cache[key] = leg_stats(S, cand, leg_spec(cfg, self.frisk, c, "combine"), self.years)
            cs, ct = cache[key]
            fs, _ = leg_stats(S, cand, leg_spec(cfg, self.frisk, c, "funded"), self.years)
            for leg, s in (("combine", cs), ("funded", fs)):
                for name, m in self.mat[leg].items():
                    m[k] = s[name]
                self.tc[leg][k] = s["today_cost"]
            kk = ct["k"]
            today = S.year[kk] >= TODAY_FROM
            sized = sizeable(S.st[kk], c["combine"]["risk"], int(cb["cap_micros"]), float(cb["tick_value"]),
                             int(cb["cost_drag_floor_ticks"]))
            self.freq[k] = float((today & sized).sum()) / today_days / accounts if today_days else 0.0
            nd = need[(c["combine"]["rr"], c["combine"]["risk"])]
            self.static_ok[k] = bool(self.freq[k] + 1e-9 >= nd and np.isfinite(self.frisk[tuple(c["sessions"])])
                                     and self.capped[tuple(c["sessions"])] <= CAP_MAX + 1e-12)
        self.shape = tuple(len(cfg["search"][a]) for a in AXES)

    def select(self, ymask: np.ndarray) -> tuple[int | None, float]:
        """No axis is ordered: the feasible cell with the highest value; ties to the earlier."""
        ok, v = self.values(ymask)
        score = np.where(ok, v, -np.inf)
        if not ok.any():
            return None, float("nan")
        best = int(np.argmax(score))
        return best, float(score[best])


# ------------------------------------------------------------------------------------------- the final's readings

def final_details(S: Signals, ev: EvaluatedFV, k: int, sessions: dict[int, float]) -> list[dict]:
    from scipy import stats as sps

    c = ev.cells[k]
    cand = S.candidates(c)
    out = []
    for leg in ("combine", "funded"):
        spec = leg_spec(ev.cfg, ev.frisk, c, leg)
        _, tr = leg_stats(S, cand, spec, ev.years)
        kk, o = tr["k"], tr["o"]
        g, fl, hit = o["gross"][kk], o["flat"][kk], o["target"][kk]
        mins = (o["exit"][kk] - S.bar[kk])[~fl]
        out.append({"section": "final_leg", **g5.leg_summary(ev, k, leg, sessions), "today_cost": tr["tc"],
                    "hit_rate": float(hit.mean()) if len(kk) else float("nan"),
                    "efr": float(g.mean() / tr["tc"]) if len(kk) and tr["tc"] > 0 else float("nan"),
                    "skew_gross": float(sps.skew(g)) if len(kk) > 2 else float("nan"),
                    "median_minutes_to_resolution": float(np.median(mins)) if len(mins) else float("nan"),
                    "flat_mean_gross": float(g[fl].mean()) if fl.any() else float("nan")})
        yr = S.year[kk]
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
                        "net": float(o["net"][kk][mk].mean()) if mk.any() else float("nan"),
                        "hit_rate": float(hit[mk].mean()) if mk.any() else float("nan"),
                        "flat_share": float(fl[mk].mean()) if mk.any() else float("nan"),
                        "flat_mean_gross": float(g[mk & fl].mean()) if (mk & fl).any() else float("nan")})
        for ses in sorted(set(S.session[kk])):
            for ph in (0, 1):
                mk = (S.session[kk] == ses) & (S.phase[kk] == ph)
                if mk.any():
                    out.append({"section": "by_session", "leg": leg, "session": ses,
                                "phase": "continuation" if ph == 0 else "reversion", "trades": int(mk.sum()),
                                "e_metric": float(tr["metric"][mk].mean()), "gross": float(g[mk].mean())})
        out += latency_rows(S, tr, spec, leg)
    return out


def latency_rows(S: Signals, tr: dict, spec: tuple, leg: str) -> list[dict]:
    """The kept trades re-entered at L = 0 and 5 (reported): each outcome from its code, a target at the leg's R or
    fair value's distance from that entry, an open trade valued from the two-minute trade's flatten move shifted by the
    entries' difference."""
    target, R, risk, cap = spec
    kk, o = tr["k"], tr["o"]
    out = []
    for L, (ent, codes) in S.alt.items():
        st = S.st[kk]
        shift = S.entry2[kk] - ent[kk]                          # d x (e2 - eL): the later entry's worse price
        col = {1.0: 0, 1.5: 1}.get(R, None)
        if target == "fv":
            dfe_l = S.dfe[kk] + shift                           # fair value's distance from this latency's entry
            to_fv = (S.phase[kk] == 1) & (dfe_l > 0)
            col_arr = np.where(to_fv, 2, 1)
            won = np.where(to_fv, dfe_l, np.floor(1.5 * st + 1e-9))
        else:
            col_arr = np.full(len(kk), col)
            won = np.floor(R * st + 1e-9)
        code = np.array([cd[i] for cd, i in zip(codes[kk], col_arr)])
        move = np.where(code == "1", won, np.where(code == "0", -st, o["flat_move"][kk] + shift))
        usable = code != "9"                                    # a never-filled entry codes 9: left out
        gross = move / st
        cost = (S.entry_cost[kk] * S.td + S.fee(risk, cap)[kk]
                + np.where(code == "0", STOP_SLIP_TICKS, np.where(code == "1", 0.0, FLATTEN_SLIP_TICKS)) * S.td
                ) / (st * S.td)
        met = gross[usable] - tr["tc"]
        yr = S.year[kk][usable]
        out.append({"section": "latency", "leg": leg, "latency": L, "trades": int(usable.sum()),
                    "e_metric": float(met.mean()) if len(met) else float("nan"),
                    "bound": g5.bound(pd.Series(met).groupby(yr).mean()) if len(met) else float("nan"),
                    "gross": float(gross[usable].mean()) if usable.any() else float("nan"),
                    "net": float((gross - cost)[usable].mean()) if usable.any() else float("nan")})
    return out


def bench_means(bench: pd.DataFrame) -> dict[str, pd.Series]:
    """The unconditional entries' mean move in R per (year, side, session, slot) at the target, read strictly."""
    st = bench["stop_ticks"].to_numpy(float)
    ok = st > 0
    safe = np.where(ok, st, 1.0)
    flat = np.where(bench["bench_worst_ticks"].to_numpy(float) != MISSING_FV,
                    bench["bench_worst_ticks"].to_numpy(float), bench["bench_close_ticks"].to_numpy(float))
    out = {}
    for name, code, won in (("r1", bench["c_1"].to_numpy(int), np.floor(1.0 * safe + 1e-9)),
                            ("r15", bench["c_15"].to_numpy(int), np.floor(1.5 * safe + 1e-9)),
                            ("fv", bench["c_fv"].to_numpy(int), bench["bench_fv_ticks"].to_numpy(float))):
        g = np.where(code == 1, won / safe, np.where(code == 0, -1.0, flat / safe))
        use = ok & (code != 9)
        t = pd.DataFrame({"year": pd.to_datetime(bench["date"]).dt.year.to_numpy()[use],
                          "side": bench["side"].to_numpy(int)[use], "session": bench["session"].to_numpy()[use],
                          "slot": bench["bench_after"].to_numpy(int)[use], "gross": g[use]})
        out[name] = t.groupby(["year", "side", "session", "slot"])["gross"].mean()
    return out


def bench_slot(session: np.ndarray, bar: np.ndarray) -> np.ndarray:
    """The latest benchmark slot of each trade's session before its entry bar (-1 if none)."""
    out = np.full(len(bar), -1)
    for i, (s, b) in enumerate(zip(session, bar)):
        prior = [x for x in BENCH[s] if x < b]
        out[i] = max(prior) if prior else -1
    return out


def drift_value(S: Signals, bench: pd.DataFrame, ev: EvaluatedFV, k: int) -> tuple[list[dict], float]:
    c = ev.cells[k]
    cand = S.candidates(c)
    means = bench_means(bench)
    rows, vals = [], []
    for leg in ("combine", "funded"):
        spec = leg_spec(ev.cfg, ev.frisk, c, leg)
        _, tr = leg_stats(S, cand, spec, ev.years)
        kk, o = tr["k"], tr["o"]
        target, R = spec[0], spec[1]
        if target == "r":
            which = np.full(len(kk), "r1" if R == 1.0 else "r15", dtype=object)
        else:
            which = np.where((S.phase[kk] == 1) & (S.dfe[kk] > 0), "fv", "r15").astype(object)
        slot = bench_slot(S.session[kk], S.bar[kk])
        side = S.dir[kk].astype(int)
        bm = np.array([means[w].get((y, sd, ses, sl), np.nan) for w, y, sd, ses, sl in
                       zip(which, S.year[kk], side, S.session[kk], slot)], dtype=float)
        ex = o["gross"][kk] - bm
        b = g5.bound(pd.Series(ex).groupby(S.year[kk]).mean())
        vals.append(b)
        for name, mk in (("long", side > 0), ("short", side < 0), ("combined", np.ones(len(kk), bool))):
            rows.append({"section": "drift", "leg": leg, "side": name, "trades": int(mk.sum()),
                         "e_metric": float(tr["metric"][mk].mean()) if mk.any() else float("nan"),
                         "benchmark_gross": float(np.nanmean(bm[mk])) if mk.any() else float("nan"),
                         "excess": float(np.nanmean(ex[mk])) if mk.any() else float("nan"),
                         "excess_bound": g5.bound(pd.Series(ex[mk]).groupby(S.year[kk][mk]).mean()) if mk.any()
                         else float("nan"),
                         "unmatched": int(np.isnan(bm[mk]).sum())})
    value = float(np.fmin(vals[0], vals[1])) if not any(np.isnan(vals)) else float("nan")
    rows.append({"section": "drift", "leg": "value", "excess_bound": value})
    return rows, value


# ------------------------------------------------------------------------------------------------------ the gate

def gate_trades(S: Signals, ev: EvaluatedFV, selections: dict[int, int | None], final: dict) -> pd.DataFrame:
    """Each test year's out-of-sample trades of the selection made on the years before it, both legs at their moves
    less their cells' median costs of 2020 to June 2025 (D-271, D-276), on the trades one-at-a-time coordination keeps
    when each position closes at the later of its two legs' exits -- either leg's account is then flat before the next
    entry, the conservative reading (D-285); the MAE at the stop (D-284)."""
    out = []
    for y, k in selections.items():
        if k is None:
            continue
        c = ev.cells[k]
        cand = S.candidates(c)
        legs = {}
        for leg in ("combine", "funded"):
            spec = leg_spec(ev.cfg, ev.frisk, c, leg)
            o = S.outcome(spec[0], spec[1], spec[2], spec[3])
            legs[leg] = (o, S.today_cost(cand, spec[2], spec[3]))
        of = legs["funded"][0]
        kept = S.kept(cand, np.maximum(legs["combine"][0]["exit"], of["exit"])) & (S.year == y)
        for i in np.nonzero(kept)[0]:
            row = {"date": S.df["date"].iat[i], "year": y, "sessions": c["sessions"], "entry_t": float(S.bar[i]),
                   "exit_t": float(of["exit"][i]), "flat_f": bool(of["flat"][i])}
            for leg, (o, tc) in legs.items():
                row[f"r_{leg[0]}"] = float(o["gross"][i] - tc)
                row[f"stopped_{leg[0]}"] = bool(o["stopped"][i])
            out.append(row)
    return pd.DataFrame(out)


def gate_blocks(t: pd.DataFrame, ses: pd.DataFrame, days: list[str], c_risk: float, frisk: float, ckey: float,
                fkey: float, band: pd.DataFrame, seed: int, mae_unstopped: float = 1.0):
    """D-271 (4): each trade's stop a micro drawn (seeded) from 2020 to June 2025's session stops in its cell's sessions;
    left out unless sizeable in both states. One block a trading day, trades in entry order."""
    from orb5_prep import sizeable
    from propedge.outcomes.distribution import DayBlock

    rng = np.random.default_rng(seed)
    cb = band[(band["state"] == "combine") & (band["market"] == "NQ")].iloc[0]
    fb = band[(band["state"] == "funded_below_2000") & (band["market"] == "NQ")].iloc[0]
    tv = float(cb["tick_value"])
    yr = pd.to_datetime(ses["date"]).dt.year
    pools = {}
    if len(t):
        st = np.empty(len(t))
        for n in range(len(t)):
            key = tuple(t["sessions"].iat[n])
            if key not in pools:
                pools[key] = ses[(yr >= TODAY_FROM) & (ses["present"] == 1)
                                 & ses["session"].isin(key)]["stop_ticks"].to_numpy(float)
            if not len(pools[key]):
                raise SystemExit(f"REFUSED: no 2020 to June 2025 session stop to draw for {key}.")
            st[n] = float(rng.choice(pools[key]))
        ok = (sizeable(st, c_risk, int(cb["cap_micros"]), tv, int(cb["cost_drag_floor_ticks"]))
              & sizeable(st, frisk, int(fb["cap_micros"]), tv, int(fb["cost_drag_floor_ticks"])))
        t = t.assign(rpc=st * tv)[ok]
    by = {d: g.sort_values("entry_t", kind="stable") for d, g in t.groupby("date")} if len(t) else {}
    blocks = []
    for d in days:
        g = by.get(d)
        if g is None or not len(g):
            z = np.zeros(0)
            blocks.append(DayBlock(pnl=z, risked=z, exit_reasons=(), risk_per_contract=z, mae=z, entry_t=z,
                                   exit_t=z, r_by_rr={ckey: z, fkey: z}, mae_by_rr={ckey: z, fkey: z}))
            continue
        rpc = g["rpc"].to_numpy(float)
        rc, rf = g["r_c"].to_numpy(float), g["r_f"].to_numpy(float)
        mc = np.where(g["stopped_c"].to_numpy(bool), 1.0, mae_unstopped)
        mf = np.where(g["stopped_f"].to_numpy(bool), 1.0, mae_unstopped)
        mc, mf = np.maximum(mc, -rc), np.maximum(mf, -rf)
        blocks.append(DayBlock(pnl=rf * rpc, risked=rpc.copy(),
                               exit_reasons=tuple("flatten" if x else "bracket" for x in g["flat_f"]),
                               risk_per_contract=rpc.copy(), mae=mf * rpc, entry_t=g["entry_t"].to_numpy(float),
                               exit_t=g["exit_t"].to_numpy(float), r_by_rr={ckey: rc, fkey: rf},
                               mae_by_rr={ckey: mc, fkey: mf}))
    return blocks, int(len(t))


def run_gate(blocks, stats: dict, final: dict, frisk: float, gcfg: dict, seed: int):
    from propedge.campaign import gate
    from propedge.campaign.payout_method import rules_for_method
    from propedge.campaign.protocols import Protocol
    from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy
    from propedge.campaign.sizing import CURRENT_TIER, SizingRule

    camp = gcfg["campaign"]
    ckey, fkey = final["combine"]["rr"], FUNDED_KEY[final["funded_target"]]
    protocol = Protocol(name="fv2", combine_rr=ckey, combine_risk=final["combine"]["risk"], funded_rr=fkey,
                        funded_risk=frisk, trades_per_day=MAX_PER_DAY, payout_path="standard", keep_balance=0.0,
                        payout_frac=1.0, max_concurrent_accounts=int(camp["accounts"]), family="fv2",
                        source="config/fv2_grid.yaml", note="FV2's gate (D-283)")
    policy = RiskPolicy(id="fv2_gate", root=Phase(
        combine=Leaf(f"combine {ckey:g}:1 ${final['combine']['risk']:,.0f}", risk=final["combine"]["risk"], rr=ckey,
                     max_trades=1),
        funded=Leaf(f"funded {final['funded_target']} ${frisk:,.0f}", risk=float(frisk), rr=fkey, max_trades=1)))
    e_by = {ckey: stats["combine"]["e"], fkey: stats["funded"]["e"]}
    lb_by = {ckey: stats["combine"]["lb"], fkey: stats["funded"]["lb"]}
    return gate.run_gate(
        blocks, e=e_by[fkey], lb=lb_by[fkey], protocol=protocol, bankroll=float(camp["bankroll"]),
        horizon_days=int(camp["horizon_days"]), n_paths=int(camp["n_paths"]), seed=seed,
        accounts=int(camp["accounts"]), sizing=SizingRule.from_ledger(CURRENT_TIER, headroom_frac=float(camp["headroom"])),
        rules=rules_for_method(camp["payout_method"]), mode=camp["mode"], settlement=camp["settlement"],
        combines=int(camp["combines"]), total_accounts=int(camp["accounts"]), risk_policy=policy,
        e_by_rr=e_by, lb_by_rr=lb_by)


# --------------------------------------------------------------------------------------------------------- main

def _key(c: dict | None) -> dict:
    if c is None:
        return {"sessions": None}
    return {"sessions": "+".join(c["sessions"]), "trigger": c["trigger"], "continuation": c["continuation"],
            "combine": f"{c['combine']['rr']:g}:1 ${c['combine']['risk']:,.0f}", "funded_target": c["funded_target"]}


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
        print(f"REFUSED: FV2 is declared by {DECLARATION} (DECISIONS.md); got {a.declaration!r} or the row is missing.")
        return 2
    cfg = config()
    k_total = math.prod(len(cfg["search"][x]) for x in AXES)
    if k_total != int(cfg["k"]):
        print(f"REFUSED: the grid holds {k_total} configurations, the config declares {cfg['k']}.")
        return 2
    need = {}
    for comb in cfg["search"]["combine"]:
        n = setups_minimum(float(comb["rr"]), float(comb["risk"]), 0.0)
        if n is None or n != n:
            print(f"REFUSED: D-154's minimum for the {comb['rr']}:1 ${comb['risk']} Combine is not tabulated "
                  "(results/setups_per_day.csv).")
            return 2
        need[(float(comb["rr"]), float(comb["risk"]))] = float(n)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    sig, ses, bench, sessions = data if data is not None else load(
        rd, Path(runs_dir) if runs_dir is not None else ROOT / "runs", cfg)
    fm = FillModel.load("assumed")
    q = params("NQ")
    S = Signals(sig, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]),
                q["micro_tick"] * q["micro_point_value"])
    band = read_result(BAND_FILE)
    ev = EvaluatedFV(S, ses, cfg, sessions, band, need)
    years = list(ev.years)
    rows = []
    # sessions at the capture's cap, per year and session (capture counts, no outcome)
    yr_s = pd.to_datetime(ses["date"]).dt.year
    for (y, name), g in ses[ses["present"] == 1].groupby([yr_s[ses["present"] == 1], "session"]):
        rows.append({"section": "capped", "year": int(y), "session": name, "sessions_present": int(len(g)),
                     "sessions_capped": int((g["signals_beyond_cap"] > 0).sum())})
    ok_all, v_all = ev.values(np.ones(len(years), bool))
    for k, c in enumerate(ev.cells):
        r = {"section": "grid", **_key(c), "feasible": bool(ok_all[k]), "value": float(v_all[k]),
             "freq_per_account_today": float(ev.freq[k]), "funded_risk": ev.frisk[tuple(c["sessions"])],
             "capped_share": ev.capped[tuple(c["sessions"])]}
        for leg in ("combine", "funded"):
            n = ev.mat[leg]["n"][k].sum()
            g = float(ev.mat[leg]["gross"][k].sum() / max(n, 1))
            r.update({f"{leg}_n": int(n), f"{leg}_metric": float(ev.mat[leg]["metric"][k].sum() / max(n, 1)),
                      f"{leg}_gross": g, f"{leg}_net": float(ev.mat[leg]["net"][k].sum() / max(n, 1)),
                      f"{leg}_flat": float(ev.mat[leg]["flat"][k].sum() / max(n, 1)),
                      f"{leg}_today_cost": float(ev.tc[leg][k]),
                      f"{leg}_efr": float(g / ev.tc[leg][k]) if n and ev.tc[leg][k] > 0 else float("nan")})
        rows.append(r)
    sels, wf = {}, []
    for T in [y for y in years if y >= WF_FIRST]:
        k, score = ev.select(ev.years < T)
        sels[T] = k
        val = ev.year_value(k, T) if k is not None else float("nan")
        wf.append(val)
        rows.append({"section": "walkforward", "test_year": T, **_key(ev.cells[k] if k is not None else None),
                     "score": score, "oos_value": val})
    wf_s = pd.Series(wf, index=[y for y in years if y >= WF_FIRST])
    w1_lb = g5.bound(wf_s)
    w1 = bool(wf_s.isna().any() or not (w1_lb > 0))
    kf, score = ev.select(np.ones(len(years), bool))
    final = ev.cells[kf] if kf is not None else None
    w2, b_kill, g_kill, gate_passed = True, True, True, False
    if final is not None:
        fv = float(v_all[kf])
        era_rows, flagged, low = g5.era_reading(ev, kf, cfg["selection"]["eras"]["split"], 2000, cfg["seeds"]["eras"])
        fv_used = min(fv, low) if flagged else fv
        w2 = bool(not ok_all[kf] or not (fv_used > 0))
        frisk = float(ev.frisk[tuple(final["sessions"])])
        rows.append({"section": "final", **_key(final), "score": score, "value": fv, "value_used": fv_used,
                     "era_flagged": flagged, "funded_risk": frisk, "freq_per_account_today": float(ev.freq[kf])})
        rows += final_details(S, ev, kf, sessions)
        rows += [{"section": "eras", **r} for r in era_rows.values()]
        drift_rows, dv = drift_value(S, bench, ev, kf)
        rows += drift_rows
        b_kill = bool(not (dv > 0))
        t = gate_trades(S, ev, sels, final)
        stats = {}
        for leg, col in (("combine", "r_c"), ("funded", "r_f")):
            by = t.groupby("year")[col].mean() if len(t) else pd.Series(dtype=float)
            stats[leg] = {"e": float(t[col].mean()) if len(t) else float("nan"), "lb": g5.bound(by)}
        test_days = sorted(d for d in set(ses["date"]) if int(d[:4]) >= WF_FIRST)
        n_used = 0
        ckey, fkey = final["combine"]["rr"], FUNDED_KEY[final["funded_target"]]
        if np.isfinite(frisk):
            for section, mae0 in (("gate", 1.0), ("gate_mae0", 0.0)):
                blocks, n_used = gate_blocks(t, ses, test_days, final["combine"]["risk"], frisk, ckey, fkey, band,
                                             cfg["seeds"]["stops"], mae_unstopped=mae0)
                if np.isfinite([stats[x]["lb"] for x in stats]).all() and n_used:
                    gdf, passed = run_gate(blocks, stats, final, frisk, cfg["gate"], cfg["seeds"]["gate"])
                    if section == "gate":
                        gate_passed = passed
                    for _, gr in gdf.iterrows():
                        rows.append({"section": section,
                                     **{kk: vv for kk, vv in gr.items() if not isinstance(vv, (list, dict))}})
        rows.append({"section": "gate_inputs", "oos_trades": int(len(t)), "trades_used": n_used,
                     "e_combine": stats["combine"]["e"], "lb_combine": stats["combine"]["lb"],
                     "e_funded": stats["funded"]["e"], "lb_funded": stats["funded"]["lb"], "funded_risk": frisk})
        g_kill = not gate_passed
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
    stop_point = ("W1: the execution model invalidated, the fair-value branch on NQ closed" if w1 else
                  "a later gate: this specification closed" if killed else
                  "continue: one confirmation on the held-back window")
    rows.append({"section": "summary", "verdict": "kill" if killed else "continue", "killed_by": ",".join(killed),
                 "stopping_point": stop_point, "k": k_total, "years": f"{years[0]}-{years[-1]}",
                 "declaration": DECLARATION, "configurations_feasible_all_years": int(ok_all.sum())})
    out = pd.DataFrame(rows)
    write_result(out, "fv2_grid", script=SCRIPT, seed=int(cfg["seeds"]["gate"]), exploratory=True,
                 results_dir=results_dir,
                 notes={"status": "FV2's screen, declared before it ran (D-283); EXPLORATORY in that its design is not "
                                  "blind to FV1's results; only the held-back confirmation can decide"},
                 parameters={"config": "config/fv2_grid.yaml", "runs": cfg["runs"], "k": k_total,
                             "fill_profile": "assumed", "fee": "NQ minis with MNQ micros (D-276)",
                             "seeds": cfg["seeds"], "decision": DECLARATION},
                 description="FV2's declared grid on NQ 2009 to June 2025: every configuration, the selection, its "
                             "walk-forward from 2013, the era rule, the per-side drift benchmark, the D-145 gate on "
                             "the walk-forward's out-of-sample trades, and the kill lines W1, W2, B and G with D-277's "
                             "stopping points, all fixed in config/fv2_grid.yaml before the run.")
    if record:
        VariantCounter().record(prereg_id=f"{DECLARATION}:fv2_grid", seed=int(cfg["seeds"]["gate"]), exploratory=True,
                                params={"study": "FV2 grid", "k": k_total, "market": "NQ"},
                                label=f"FV2's declared grid: {k_total} configurations (D-283)")
    pd.set_option("display.width", 250)
    print(out[out["section"].isin(["final", "final_leg", "eras", "drift", "latency", "gate_inputs", "spa", "dsr",
                                   "kline", "summary"])].dropna(axis=1, how="all").round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
