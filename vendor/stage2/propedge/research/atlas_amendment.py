"""The effect atlas amendment (D-128): three new families -- F (directional features), R (size features, for
sizing only) and O (options gamma, ES and NQ, from 2012) -- each corrected on its own, each survivor checked
once on its check half. Definitions: `config/effect_atlas.yaml`, `amendment_d128`. D-126's 103-test family is
untouched and still computed by `atlas_screen.run_screen`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from propedge.research import atlas
from propedge.research.atlas_screen import prepare

NAN = float("nan")
#: bootstrap replications, as D-126's screen; tests lower it for speed
BOOT_REPS = 2000


# ---------------------------------------------------------------- the repository features

def context_frame(ctx: pd.DataFrame, am: dict | None = None) -> pd.DataFrame:
    """The context kit's per-session rows, dated, with the previous session's VIX beside each and (D-129) the VIX
    relative to its own trailing median, known at each session's close."""
    lb = (am or {}).get("lookback", {"vix_rel_days": 120, "vix_rel_min": 60})
    c = ctx.copy()
    num = pd.to_numeric(c["d"], errors="coerce")
    c["cdate"] = pd.to_datetime(num.astype("int64").astype(str), format="%Y%m%d")
    c = c.sort_values("cdate").reset_index(drop=True)
    c["vix_lag"] = c["vix"].shift(1)
    med = c["vix"].rolling(lb["vix_rel_days"], min_periods=lb["vix_rel_min"]).median()
    c["vix_rel"] = np.log(c["vix"] / med)
    return c


def gamma_agreement(ctx: pd.DataFrame, key: str) -> tuple[float, int]:
    """Share of sessions on which the Black-Scholes and the platform's exposure agree in sign, and how many."""
    a, b = ctx[key].to_numpy(float), ctx[key + "l"].to_numpy(float)
    ok = np.isfinite(a) & np.isfinite(b) & (a != 0) & (b != 0)
    n = int(ok.sum())
    return (float(((a[ok] > 0) == (b[ok] > 0)).mean()) if n else NAN), n


def underlying_match(ctx: pd.DataFrame, key: str) -> tuple[float, int]:
    """D-129: share of sessions with an exposure whose option universe's index level equals that session's close
    (the kit's `g?u` flag), and how many; NaN when the context has no flag (R038)."""
    col = key + "u"
    if col not in ctx:
        return NAN, 0
    have = ctx[key].notna() & ctx[col].notna()
    n = int(have.sum())
    return (float((ctx.loc[have, col] == 1).mean()) if n else NAN), n


def features(d: pd.DataFrame, ctx: pd.DataFrame | None, market: str, am: dict) -> pd.DataFrame:
    """D-128's repository features on one market's prepared rows (`atlas_screen.prepare`)."""
    lb = am["lookback"]
    d = d.sort_values("date").reset_index(drop=True).copy()
    ok = d["ok"].astype(bool)
    O = d["S"] / np.exp(d["day"] / 100.0)                      # the open, from settlement and the day's return
    H, L = O * np.exp(d["hi"] / 100.0), O * np.exp(d["lo"] / 100.0)
    same = (d["sym"] == d["sym"].shift(1)) & ok.shift(1, fill_value=False)   # lagged prices comparable
    clv = ((d["S"] - L) / (H - L) - 0.5).where(H > L)
    d["clv_prev"] = clv.shift(1).where(same)
    hp, lp = H.shift(1), L.shift(1)
    outside = pd.Series(np.where(O > hp, 1.0, np.where(O < lp, -1.0, 0.0)), index=d.index)
    d["outside"] = outside.where(same & hp.notna() & lp.notna())
    rng = (d["hi"] - d["lo"]).where(ok & ((d["hi"] - d["lo"]) > 0))
    med = rng.shift(2).rolling(lb["range_days"], min_periods=lb["min_periods"]).median()
    d["comp"] = np.log(rng.shift(1)) - np.log(med)
    v30 = d["v30"].where(ok & (d["v30"] > 0))
    vmed = v30.shift(1).rolling(lb["volume_days"], min_periods=lb["min_periods"]).median()
    d["vsurge"] = np.log(v30) - np.log(vmed)
    oc = (d["on"] + d["day"]).where(ok)
    d["rev5"] = oc.shift(1).rolling(lb["reversal_days"], min_periods=lb["reversal_days"]).sum()
    d["r_rod"] = d["on"] + d["r30"] + d["mid"]
    rv_rest = d["rvd"] - d["rv30"]
    d["ln_rvd"] = np.log(d["rvd"].where(d["rvd"] > 0))
    d["ln_rvd_prev"] = d["ln_rvd"].shift(1)
    d["ln_rv_rest"] = np.log(rv_rest.where(rv_rest > 0))
    d["ln_rv30"] = np.log(d["rv30"].where(d["rv30"] > 0))
    d["cl30c"] = d["cl30"] - 0.5
    for col in ("vix_prev", "vix_rel_prev", "dvix", "ln_vix_prev", "nge_prev", "nge_neg"):
        d[col] = NAN
    if ctx is not None and len(ctx):
        key = am["options_markets"].get(market)
        cols = ["cdate", "vix", "vix_lag", "vix_rel"] + ([key] if key else [])
        m = pd.merge_asof(d[["date"]], ctx[cols], left_on="date", right_on="cdate",
                          allow_exact_matches=False, direction="backward")
        fresh = (d["date"] - m["cdate"]).dt.days <= int(am["context_max_age_days"])
        d["vix_prev"] = m["vix"].where(fresh)
        d["vix_rel_prev"] = m["vix_rel"].where(fresh)
        d["ln_vix_prev"] = np.log(d["vix_prev"].where(d["vix_prev"] > 0))
        d["dvix"] = np.log(m["vix"] / m["vix_lag"]).where(fresh)
        if key:
            g = m[key].where(fresh & (m[key] != 0))
            d["nge_prev"] = g
            d["nge_neg"] = (g < 0).astype(float).where(g.notna())
    return d


# ---------------------------------------------------------------- the tests of each family

def _tercile_flag(v: pd.Series, ref: pd.Series) -> pd.Series:
    """1 in ref's top tercile, 0 in its bottom tercile, NaN between (cuts from the screen half)."""
    lo, hi = np.nanquantile(ref.to_numpy(float), [1 / 3, 2 / 3])
    return pd.Series(np.where(v >= hi, 1.0, np.where(v <= lo, 0.0, NAN)), index=v.index).where(v.notna())


def _slope_row(tid, d, xk, yk, seed, where=None):
    s = d if where is None else d[where]
    x, y = s[xk].to_numpy(float), s[yk].to_numpy(float)
    r = atlas.slope_test(x, y)
    ok = np.isfinite(x) & np.isfinite(y)
    fn = lambda a, b: np.polyfit(a, b, 1)[0] if len(a) > 2 else NAN      # noqa: E731
    return {"test": tid, **r, "p_boot": atlas.block_bootstrap_p(fn, [x[ok], y[ok]], reps=BOOT_REPS, seed=seed)}


def f_tests(d: pd.DataFrame, ref: pd.DataFrame, seed: int) -> list[dict]:
    """The ten F tests on rows `d`; tercile cuts from `ref` (the screen half)."""
    rows = [_slope_row("F01_prev_close_location_day", d, "clv_prev", "day", seed + 1),
            _slope_row("F02_prev_close_location_on", d, "clv_prev", "on", seed + 2)]
    z = (d["outside"] * d["rr30"])[d["outside"].fillna(0) != 0].to_numpy(float)
    z = z[np.isfinite(z)]
    rows.append({"test": "F03_open_outside_range", **atlas.mean_test(z),
                 "p_boot": atlas.block_bootstrap_p(lambda v: v.mean(), [z], reps=BOOT_REPS, seed=seed + 3)})
    rows.append(_slope_row("F04_compression_breakout", d, "comp", "br", seed + 4, where=d["bd"].fillna(0) != 0))
    vol_hi = _tercile_flag(d["vsurge"], ref["vsurge"])
    rows.append({"test": "F05_volume_surge_continuation", **atlas.interaction_test(d["r30"], d["rr30"], vol_hi),
                 "p_boot": NAN})
    rows.append(_slope_row("F06_opening_close_location", d, "cl30c", "rr30", seed + 6))
    rows.append(_slope_row("F07_short_term_reversal", d, "rev5", "day", seed + 7))
    rows.append(_slope_row("F08_vix_change", d, "dvix", "day", seed + 8))
    vix_hi = _tercile_flag(d["vix_rel_prev"], ref["vix_rel_prev"])          # D-129: relative, not absolute
    rows.append({"test": "F09_vix_state_continuation", **atlas.interaction_test(d["r30"], d["rr30"], vix_hi),
                 "p_boot": NAN})
    rows.append(_slope_row("F10_opening_imbalance", d, "imb30", "rr30", seed + 10))
    return rows


def r_tests(d: pd.DataFrame, ref: pd.DataFrame, seed: int) -> list[dict]:
    """The three R (size) tests: partial slopes with the declared control."""
    return [{"test": tid, **atlas.partial_slope_test(d[x], d[z], d[y]), "p_boot": NAN}
            for tid, x, z, y in (("R01_vix_level_vol", "ln_vix_prev", "ln_rvd_prev", "ln_rvd"),
                                 ("R02_compression_vol", "comp", "ln_rvd_prev", "ln_rvd"),
                                 ("R03_volume_surge_vol", "vsurge", "ln_rv30", "ln_rv_rest"))]


def o_tests(d: pd.DataFrame, ref: pd.DataFrame, seed: int) -> list[dict]:
    """The three O tests: negative minus positive net gamma exposure of the session before."""
    return [{"test": "O01_gamma_intraday_momentum", **atlas.interaction_test(d["r_rod"], d["l30"], d["nge_neg"]),
             "p_boot": NAN},
            {"test": "O02_gamma_opening_continuation", **atlas.interaction_test(d["r30"], d["rr30"], d["nge_neg"]),
             "p_boot": NAN},
            {"test": "O03_gamma_vol", **atlas.partial_slope_test(d["nge_neg"], d["ln_rvd_prev"], d["ln_rv_rest"]),
             "p_boot": NAN}]


FAMILIES = {"F": f_tests, "R": r_tests, "O": o_tests}


# ---------------------------------------------------------------- the screen and the check

def _check_row(r: pd.Series, c: dict) -> dict:
    sign = np.sign(r["est"])
    t_dir = sign * c["t"] if np.isfinite(c["t"]) else NAN
    p1 = float(stats.norm.sf(t_dir)) if np.isfinite(t_dir) else NAN
    passed = bool(np.sign(c["est"]) == sign and p1 < 0.05 and abs(c["est"]) >= 0.5 * abs(r["est"]))
    return {"check_est": c["est"], "check_se": c["se"], "check_n": c["n"], "check_p1": p1, "check_pass": passed,
            "check_size_pct": c["size_pct"]}


def run_amendment(frames: dict[str, pd.DataFrame], cfg: dict, context: pd.DataFrame | None, *,
                  seed: int = 20261013) -> tuple[pd.DataFrame, dict]:
    """Every F, R and O test, the per-family correction on the screen half, one check of each survivor.
    Returns (rows, info); info records the context integrity and whether the O family ran."""
    am = cfg["amendment_d128"]
    dev = cfg["development"]
    s_end, c_start = pd.Timestamp(dev["screen_half_end"]), pd.Timestamp(dev["check_half_start"])
    oh = {k: pd.Timestamp(v) for k, v in am["o_halves"].items()}
    screened = list(cfg["screened_markets"])
    ctx = context_frame(context, am) if context is not None else None
    feats = {m: features(prepare(f), ctx, m, am) for m, f in frames.items()}
    info: dict = {"o_ran": False, "agreement": {}}
    halves: dict[tuple[str, str], dict[str, pd.DataFrame]] = {}
    for m, d in feats.items():
        ok = d["ok"].astype(bool)
        halves[("FR", m)] = {"screen": d[ok & (d["date"] <= s_end)], "check": d[ok & (d["date"] >= c_start)],
                             "all": d[ok]}
        halves[("O", m)] = {"screen": d[ok & (d["date"] >= oh["start"]) & (d["date"] <= oh["screen_end"])],
                            "check": d[ok & (d["date"] >= oh["check_start"])]}
    rows = []
    for fam in ("F", "R"):
        for m in feats:
            member = m in screened
            part = "screen" if member else "all"
            h = halves[("FR", m)]
            for r in FAMILIES[fam](h[part], h[part], seed):
                rows.append({"family": fam, "market": m, **r, "in_family": member, "half": part})
    if ctx is not None:
        keys = sorted(set(am["options_markets"].values()))
        agree = {k: gamma_agreement(ctx, k) for k in keys}
        match = {k: underlying_match(ctx, k) for k in keys}
        info["agreement"], info["underlying"] = agree, match
        info["o_ran"] = (all(np.isfinite(a) and a >= float(am["gamma_sign_agreement_min"]) for a, _ in agree.values())
                         and all(np.isfinite(a) and a >= float(am["underlying_match_min"]) for a, _ in match.values()))
    if info["o_ran"]:
        for m in am["options_markets"]:
            if m in feats:
                h = halves[("O", m)]
                for r in o_tests(h["screen"], h["screen"], seed):
                    rows.append({"family": "O", "market": m, **r, "in_family": True, "half": "screen"})
    out = pd.DataFrame(rows)
    q = float(am["fdr_q"])
    out["survivor"] = False
    out["family_size"] = 0
    for fam in ("F", "R", "O"):
        mask = ((out["family"] == fam) & out["in_family"]).to_numpy()
        if mask.any():
            out.loc[mask, "survivor"] = atlas.benjamini_hochberg(out.loc[mask, "p"].to_numpy(float), q)
        out.loc[(out["family"] == fam).to_numpy(), "family_size"] = int(mask.sum())
    for col in ("check_est", "check_se", "check_n", "check_p1", "check_size_pct"):
        out[col] = NAN
    out["check_pass"] = False
    for i in np.flatnonzero(out["survivor"].to_numpy()):
        r = out.iloc[i]
        key = ("O" if r["family"] == "O" else "FR", r["market"])
        h = halves[key]
        c = next(x for x in FAMILIES[r["family"]](h["check"], h["screen"], seed) if x["test"] == r["test"])
        for col, v in _check_row(r, c).items():
            out.loc[out.index[i], col] = v
    out["seen_in_literature"] = out["test"].isin(
        [t for fam in am["families"].values() for t, spec in fam.items() if spec.get("seen_in_literature")])
    return out, info


def spread_table(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Per market and year, on scoreable days: median daily spread, mean opening spread, mean share of
    minutes wider than a tick, mean quote coverage (a cost measurement for T2, not a test)."""
    rows = []
    for m, f in frames.items():
        d = prepare(f)
        d = d[d["ok"].astype(bool)]
        for y, g in d.groupby(d["date"].dt.year):
            rows.append({"market": m, "year": int(y), "days": len(g), "sp_median": float(g["sp"].median()),
                         "sp30_mean": float(g["sp30"].mean()), "spw_mean": float(g["spw"].mean()),
                         "qcov_mean": float(g["qcov"].mean())})
    return pd.DataFrame(rows)
