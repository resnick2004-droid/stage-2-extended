"""The effect atlas screen (D-126): every declared test, the false-discovery correction on the screen
half, and one check of the survivors on the check half. Definitions: `config/effect_atlas.yaml`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from propedge.research import atlas

WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    """One market's per-day rows: dates, calendar flags, the day filter, the previous day's rv_day."""
    d = df.copy()
    num = pd.to_numeric(d["d"], errors="coerce")
    d["date"] = pd.to_datetime(num.astype("int64").astype(str), format="%Y%m%d")
    d = atlas.calendar_flags(d)
    d["ok"] = atlas.scoreable(d).to_numpy()
    d["prev_rvd"] = d["rvd"].shift(1)
    return d


def _tests_for(d: pd.DataFrame, market: str, cfg: dict, screen_ref: pd.DataFrame, seed: int) -> list[dict]:
    """The 20 per-market tests on the rows `d` (already restricted to a half and to scoreable days).
    `screen_ref` supplies the screen-half cut-offs (median |r_on|, rv terciles)."""
    rows = []

    def add(tid, res, fn=None, arrays=None):
        pb = atlas.block_bootstrap_p(fn, arrays, seed=seed + len(rows)) if fn is not None else float("nan")
        rows.append({"market": market, "test": tid, **res, "p_boot": pb})

    slope = lambda xk, yk: (atlas.slope_test(d[xk], d[yk]),                              # noqa: E731
                            lambda x, y: np.polyfit(x, y, 1)[0] if len(x) > 2 else np.nan,
                            [d[xk].to_numpy(float), d[yk].to_numpy(float)])
    for tid, xk, yk in (("H01_overnight_reversal", "on", "day"), ("H02_first30_to_rest", "r30", "rr30"),
                        ("H03_first30_to_last30", "r30", "l30"), ("H04_overnight_to_last30", "on", "l30"),
                        ("H05_gap_toward_S0", "on", "r60"), ("H09_settlement_momentum", "mid", "l30")):
        r, fn, arrs = slope(xk, yk)
        ok = np.isfinite(arrs[0]) & np.isfinite(arrs[1])
        add(tid, r, fn, [a[ok] for a in arrs])
    med = float(screen_ref["on"].abs().median())
    big = d[d["on"].abs() > med]
    z = (big["gf"] - atlas.p_touch(big["on"].abs(), big["rvd"])).to_numpy(float)
    z = z[np.isfinite(z)]
    add("H06_gap_fill_rate", atlas.mean_test(z), lambda v: v.mean(), [z])
    br = d.loc[d["bd"] != 0, "br"].to_numpy(float)
    br = br[np.isfinite(br)]
    add("H07_range_break_follow", atlas.mean_test(br), lambda v: v.mean(), [br])
    l30 = d["l30"].to_numpy(float)
    l30 = l30[np.isfinite(l30)]
    add("H08_settlement_drift", atlas.mean_test(l30), lambda v: v.mean(), [l30])
    for wd in WEEKDAYS:
        v = d.loc[d["weekday"] == wd, "day"].to_numpy(float)
        add(f"H10_weekday_{wd}", atlas.mean_test(v[np.isfinite(v)]))
    for flag, tid in (("month_last", "H11_month_last"), ("month_first", "H11_month_first"),
                      ("third_friday", "H12_third_friday"), ("after_third_friday", "H12_after_third_friday"),
                      ("roll_window", "H13_roll_window")):
        v = d.loc[d[flag], "day"].to_numpy(float)
        add(tid, atlas.mean_test(v[np.isfinite(v)]))
    lo, hi = np.nanquantile(screen_ref["prev_rvd"], [1 / 3, 2 / 3])
    sub = d[(d["prev_rvd"] <= lo) | (d["prev_rvd"] >= hi)]
    add("H14_vol_state", atlas.interaction_test(sub["r30"], sub["rr30"], (sub["prev_rvd"] >= hi).astype(float)))
    return rows


def _cross(es: pd.DataFrame, other: pd.DataFrame, market: str) -> dict:
    m = es[["date", "r30"]].merge(other[["date", "rr30"]], on="date")
    return {"market": market, "test": "H15_es_leads", **atlas.slope_test(m["r30"], m["rr30"]), "p_boot": float("nan")}


def run_screen(frames: dict[str, pd.DataFrame], cfg: dict, *, seed: int = 20261012) -> pd.DataFrame:
    dev = cfg["development"]
    s_end, c_start = pd.Timestamp(dev["screen_half_end"]), pd.Timestamp(dev["check_half_start"])
    screened = list(cfg["screened_markets"])
    seen = {tid: set(spec.get("seen", [])) for tid, spec in cfg["statistics"].items()}
    prepared = {m: prepare(f) for m, f in frames.items()}
    halves = {m: {"screen": p[p["ok"] & (p["date"] <= s_end)], "check": p[p["ok"] & (p["date"] >= c_start)],
                  "all": p[p["ok"]]} for m, p in prepared.items()}
    rows = []
    for m in prepared:
        family = m in screened
        part = "screen" if family else "all"
        ref = halves[m][part]
        for r in _tests_for(ref, m, cfg, ref, seed):
            rows.append({**r, "family": family, "half": part})
    for m in ("NQ", "CL", "ZN", "GC"):
        if m in prepared and "ES" in prepared:
            part = "screen" if m in screened else "all"
            rows.append({**_cross(halves["ES"][part], halves[m][part], m), "family": m in screened, "half": part})
    out = pd.DataFrame(rows)
    out["seen"] = [any(tid.startswith(k) for k in seen if m in seen[k]) for tid, m in zip(out["test"], out["market"])]
    fam = out["family"].to_numpy()
    disc = np.zeros(len(out), bool)
    disc[fam] = atlas.benjamini_hochberg(out.loc[fam, "p"].to_numpy(float), float(cfg["screen"]["correction"]
                                                                                    .split("q = ")[1].split()[0]))
    out["survivor"] = disc
    out["family_size"] = int(fam.sum())
    # the check half, once, survivors only
    checks = []
    for i in np.flatnonzero(disc):
        r = out.iloc[i]
        m, tid = r["market"], r["test"]
        if tid == "H15_es_leads":
            c = _cross(halves["ES"]["check"], halves[m]["check"], m)
        else:
            c = next(x for x in _tests_for(halves[m]["check"], m, cfg, halves[m]["screen"], seed)
                     if x["test"] == tid)
        sign = np.sign(r["est"])
        t_dir = sign * c["t"] if np.isfinite(c["t"]) else float("nan")
        from scipy import stats as _st
        p1 = float(_st.norm.sf(t_dir)) if np.isfinite(t_dir) else float("nan")
        passed = bool(np.sign(c["est"]) == sign and p1 < 0.05 and abs(c["est"]) >= 0.5 * abs(r["est"]))
        checks.append({"i": i, "check_est": c["est"], "check_se": c["se"], "check_n": c["n"],
                       "check_p1": p1, "check_pass": passed, "check_size_pct": c["size_pct"]})
    for col in ("check_est", "check_se", "check_n", "check_p1", "check_pass", "check_size_pct"):
        out[col] = np.nan if col != "check_pass" else False
    for c in checks:
        for col, v in c.items():
            if col != "i":
                out.loc[c["i"], col] = v
    # size against the market's cost floor, for reading survivors (reporting only)
    floors = {}
    for m, p in prepared.items():
        mk = cfg["markets"][m]
        price = float(np.nanmedian(p["S"]))
        floors[m] = 100.0 * float(mk["floor_ticks"]) * float(mk["vehicle_tick"]) / price if price else np.nan
    out["cost_floor_pct"] = out["market"].map(floors)
    out["size_over_floor"] = out["size_pct"].abs() / out["cost_floor_pct"]
    return out
