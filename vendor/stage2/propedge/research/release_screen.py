"""The pre-release drift family K (D-164; 2B F-032): three declared tests on the per-event records of the
release kits (R061 ES, R062 ZN), corrected on their own, each survivor checked once on the check half.
Definitions: `config/effect_atlas.yaml`, `amendment_d164`.

Test form: the slope of the release return (post, [t-1, t+5] minutes) on the pre-release return (prd,
[t-30, t-1] minutes), one-sided, expected positive (the drift is in the direction of the coming surprise).
Reported beside it: the sign-agreement rate of the two returns, the average sizes in percent and in ticks.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from propedge.research import atlas

NAN = float("nan")
BOOT_REPS = 2000
FAMILY = "K"


def prepare_events(df: pd.DataFrame, am: dict) -> pd.DataFrame:
    """One market's per-event rows: dates, the exclusion flag `ok`, and percent-per-tick for size conversion."""
    ex = am["exclusions"]
    d = df.copy()
    num = pd.to_numeric(d["d"], errors="coerce")
    d["date"] = pd.to_datetime(num.astype("int64").astype(str), format="%Y%m%d")
    offsets = d[["a", "b", "e"]].fillna(np.inf)
    d["ok"] = ((d["roll"].fillna(1) == 0) & (d["nb"] >= int(ex["min_bars"]))
               & (offsets <= int(ex["max_offset_min"])).all(axis=1)
               & d["prd"].notna() & d["post"].notna())
    return d


def _pct_per_tick(d: pd.DataFrame, tick: float) -> float:
    p = d["p"].to_numpy(float)
    p = p[np.isfinite(p) & (p > 0)]
    return float(np.mean(100.0 * tick / p)) if len(p) else NAN


def _test(tid: str, market: str, d: pd.DataFrame, tick: float, seed: int) -> dict:
    x, y = d["prd"].to_numpy(float), d["post"].to_numpy(float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    r = atlas.slope_test(x, y)
    p1 = float(stats.norm.sf(r["t"])) if np.isfinite(r["t"]) else NAN      # one-sided: slope > 0
    nz = (x != 0) & (y != 0)
    agree_n = int(nz.sum())
    agree = float((np.sign(x[nz]) == np.sign(y[nz])).mean()) if agree_n else NAN
    agree_p = float(stats.binomtest(int(round(agree * agree_n)), agree_n, 0.5, alternative="greater").pvalue) \
        if agree_n >= 10 else NAN
    fn = lambda a, b: np.polyfit(a, b, 1)[0] if len(a) > 2 else NAN      # noqa: E731
    pb = atlas.block_bootstrap_p(fn, [x, y], block=20, reps=BOOT_REPS, seed=seed) if len(x) >= 10 else NAN
    ppt = _pct_per_tick(d, tick)
    return {"family": FAMILY, "market": market, "test": tid, **r, "p1": p1, "p_boot": pb,
            "agree": agree, "agree_n": agree_n, "agree_p": agree_p,
            "mean_abs_prd_pct": float(np.mean(np.abs(x))) if len(x) else NAN,
            "mean_abs_post_pct": float(np.mean(np.abs(y))) if len(y) else NAN,
            "pct_per_tick": ppt,
            "size_ticks": float(r["size_pct"] / ppt) if np.isfinite(ppt) and ppt > 0 else NAN,
            "mean_abs_post_ticks": float(np.mean(np.abs(y)) / ppt) if len(y) and np.isfinite(ppt) and ppt > 0 else NAN}


def _check_row(r: pd.Series, c: dict) -> dict:
    sign = np.sign(r["est"])
    t_dir = sign * c["t"] if np.isfinite(c["t"]) else NAN
    p1 = float(stats.norm.sf(t_dir)) if np.isfinite(t_dir) else NAN
    passed = bool(np.sign(c["est"]) == sign and p1 < 0.05 and abs(c["est"]) >= 0.5 * abs(r["est"]))
    return {"check_est": c["est"], "check_se": c["se"], "check_n": c["n"], "check_p1": p1, "check_pass": passed,
            "check_size_pct": c["size_pct"], "check_size_ticks": c["size_ticks"], "check_agree": c["agree"]}


def _subsets(am: dict) -> list[tuple[str, str, str | None]]:
    """(test id, market, excluded code) for the three declared tests."""
    return [(t["id"], t["market"], t.get("exclude_code")) for t in am["tests"]]


def run_release_screen(frames: dict[str, pd.DataFrame], cfg: dict, *, seed: int = 20261014) -> pd.DataFrame:
    """Every K test on the screen half, Benjamini-Hochberg across the family, one check of each survivor."""
    am = cfg["amendment_d164"]
    dev = cfg["development"]
    s_end, c_start = pd.Timestamp(dev["screen_half_end"]), pd.Timestamp(dev["check_half_start"])
    prepared = {m: prepare_events(f, am) for m, f in frames.items()}
    rows = []
    for i, (tid, market, exclude) in enumerate(_subsets(am)):
        if market not in prepared:
            continue
        d = prepared[market]
        d = d[d["ok"]]
        if exclude:
            d = d[~d["k"].str.contains(exclude, regex=False)]
        tick = float(cfg["markets"][market]["tick"])
        screen, check = d[d["date"] <= s_end], d[d["date"] >= c_start]
        r = _test(tid, market, screen, tick, seed + i)
        r.update({"half": "screen", "n_excluded": int((~prepared[market]["ok"]).sum()),
                  "n_events_all": int(len(prepared[market]))})
        r["_check"] = _test(tid, market, check, tick, seed + 100 + i)
        rows.append(r)
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["family_size"] = len(out)
    p = out["p1"].to_numpy(float)
    finite = np.isfinite(p)
    surv = np.zeros(len(out), bool)
    if finite.any():
        surv[finite] = atlas.benjamini_hochberg(p[finite], float(am["fdr_q"]))
    out["survivor"] = surv
    checks = []
    for _, r in out.iterrows():
        c = r["_check"]
        checks.append(_check_row(r, c) if r["survivor"] else
                      {k: NAN for k in ("check_est", "check_se", "check_n", "check_p1", "check_size_pct",
                                        "check_size_ticks", "check_agree")} | {"check_pass": False})
    out = pd.concat([out.drop(columns=["_check"]), pd.DataFrame(checks, index=out.index)], axis=1)
    return out
