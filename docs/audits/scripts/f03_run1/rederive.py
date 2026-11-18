"""Independent re-derivation for the audit of results/fo_opening.csv. Reads the CSV and manifest only (and, for the
two cross-checks named, vendored *data* result files read as CSV). Imports nothing of extended/ or vendor/ code."""
import csv, hashlib, json, math, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import beta, norm

ROOT = Path(r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended")
csvp = ROOT / "results" / "fo_opening.csv"
man = json.loads((ROOT / "results" / "fo_opening.csv.manifest.json").read_text(encoding="utf-8"))
P = man["parameters"]
print("sha256 file", hashlib.sha256(csvp.read_bytes()).hexdigest(), "manifest", man["sha256"])
d = pd.read_csv(csvp, low_memory=False)
print("rows", len(d), "manifest rows", man["rows"], "columns equal", list(d.columns) == man["columns"])

level = 0.05 / (P["k"] * (P["k"] + 1))
print("k", P["k"], "level recomputed", level, "manifest", P["level"])

ch = d[d.section == "choice"]
cells = ch[ch.kind == "cell"].set_index("cell")
qB = float(ch[ch.kind == "q_B"]["value"].iloc[0])
sup = d[(d.section == "supply") & d.year.notna()]
print("\n== stage B")
for c, r in cells.iterrows():
    Lh = (r.L_long + r.L_short) / 2
    by = json.loads(r.by_year)
    hb = ch[(ch.cell == c) & (ch.kind == "halves_by_year")].set_index("year")
    w = sup[sup.cell == c].set_index("year")["in_state_offers"]
    Lw = sum(by[str(int(y))] * w[y] for y in w.index) / w.sum()
    Llong_w = sum(hb.loc[y, "L_long"] * w[y] for y in w.index) / w.sum()
    Lshort_w = sum(hb.loc[y, "L_short"] * w[y] for y in w.index) / w.sum()
    yr_half = {int(y): (hb.loc[y, "L_long"] + hb.loc[y, "L_short"]) / 2 - by[str(int(y))] for y in hb.index}
    t = r.L / r.SE
    print(f"{c}: L {r.L:.6f} (halves' mean {Lh:.6f}; by-year weighted by in-state offers {Lw:.6f}); "
          f"L_long w {Llong_w:.6f} vs {r.L_long:.6f}; L_short w {Lshort_w:.6f} vs {r.L_short:.6f}; "
          f"max |by-year L - halves mean| {max(abs(v) for v in yr_half.values()):.2e}; "
          f"t = L/SE {t:.4f} vs q_B {qB:.4f}: above {t > qB}")
# q_B plausibility: a 95th percentile of the max of m >= 1 standardised (approx normal) draws lies between
print("q_B bounds for 3 cells under normality: perfectly correlated", norm.ppf(0.95), "independent",
      norm.ppf(0.95 ** (1 / 3)))

print("\n== eligibility (10.3), from the CSV's other sections")
res = d[d.section == "resolution"]
wait = d[(d.section == "wait") & (d.design == "design")].set_index("cell")
lc = d[d.section == "level_control"]
k0 = lc[lc.check == "K0"]
a10 = lc[lc.check == "A10"]
DEC = {"s1": "window", "s2": "window", "u3": "block5"}
dropped = set(ch[ch.kind == "dropped"].cell)


def cp(x, n, a=0.05):
    lo = 0.0 if x == 0 else beta.ppf(a / 2, x, n - x + 1)
    hi = 1.0 if x == n else beta.ppf(1 - a / 2, x + 1, n - x)
    return lo, hi


k0lax, a10lax = {}, {}
for _, r in k0.iterrows():
    lo, hi = cp(int(r.rejections), int(r.replications))
    k0lax[(r.cell, r.form)] = lo > level
    assert abs(lo - r.ci_lo) < 1e-7 and abs(hi - r.ci_hi) < 1e-7, (r.cell, r.form, lo, hi, r.ci_lo, r.ci_hi)
    assert abs(r.rejections / r.replications - r.rate) < 1e-12
    assert abs(r.rate / level - r.ratio) < 1e-3, (r.rate / level, r.ratio)
print("K0: CP intervals, rates and ratios re-derived; lax anywhere:", any(k0lax.values()))
for _, r in a10.iterrows():
    lo, hi = cp(int(r.rejections), int(r.selections))
    assert abs(lo - r.ci_lo) < 1e-7 and abs(hi - r.ci_hi) < 1e-7, (r["class"], r.share, r.level, lo, hi)
    a10lax[(r["class"], r.share, r.level)] = lo > r.level
    assert bool(r.lax) == (lo > r.level)
print("A10: CP intervals re-derived for", len(a10), "rows; lax anywhere:", any(a10lax.values()))
for c in cells.index:
    rc = res[res.cell == c].set_index("scope")["unresolved_3r"]
    worst = max(rc[s] for s in rc.index if s != "overall")
    k2 = rc["overall"] <= 0.05 and worst <= 0.05
    k1 = (sup[sup.cell == c]["sessions_in_state"] >= 21).all()
    k5 = wait.loc[c, "fallback_share"] <= 0.5
    k0ok = not k0lax[(c, "c1")] and not k0lax[(c, "c2")]
    a10ok = not any(v for (cl, s, l), v in a10lax.items() if cl == DEC[c])
    r = cells.loc[c]
    conds = {"K2 worst<=4%": worst <= 0.04, "long>0": r.L_long > 0, "short>0": r.L_short > 0,
             "close>0": r.L_close > 0, "K1": k1, "K2": k2, "K5": k5, "K0": k0ok, "A10": a10ok,
             "not dropped": c not in dropped}
    elig = all(conds.values())
    print(f"{c}: worst-year unresolved {worst:.4f}; failing {[k for k, v in conds.items() if not v]}; "
          f"eligible re-derived {elig}, reported {r.eligible}")

print("\n== Kill B: eligible cells above q_B:",
      [c for c in cells.index if str(cells.loc[c, "eligible"]) == "True" and cells.loc[c, "L"] / cells.loc[c, "SE"] > qB],
      "; any cell above q_B:", [c for c in cells.index if cells.loc[c, "L"] / cells.loc[c, "SE"] > qB])

print("\n== V_B (7.4 / 10.4), mean_dv from A9's lambda_bar and u_c, then against the vendored value map")
pw = d[(d.section == "power") & d.cell.notna()].set_index("cell")
mdv_impl = {c: 4 * 500 / (pw.loc[c, "lambda_bar"] * pw.loc[c, "u_c"]) for c in pw.index}
print("mean_dv implied by lambda_bar:", mdv_impl)
vm = ROOT / "vendor" / "stage2" / "results" / "u_value_map.csv"
vman = json.loads(Path(str(vm) + ".manifest.json").read_text(encoding="utf-8"))
print("value map sha256 matches its manifest:", hashlib.sha256(vm.read_bytes()).hexdigest() == vman["sha256"])
rows = [r for r in csv.DictReader(open(vm, encoding="utf-8")) if r["section"] == "place_values" and r["base"] == "p16"
        and r["state"] == "c_funded_opening" and r["measure"] == "mean_dv"]
mdv = float(rows[0]["value"]); print("value map rows", len(rows), "mean_dv(c)", mdv)
for c, r in cells.iterrows():
    u = pw.loc[c, "u_c"]
    vlow = u * mdv * (r.D_B - qB * r.SE_D_B) / 4
    vpt = u * mdv * r.D_B / 4
    print(f"{c}: V_B lower re-derived {vlow:.4f} reported {r.V_B_lower:.4f}; V_B point {vpt:.2f}; "
          f"D_B/SE_D_B {r.D_B / r.SE_D_B:.3f}; screen MDL>3*lambda_bar {pw.loc[c,'mdl'] > 3*pw.loc[c,'lambda_bar']}"
          f" (ratio {pw.loc[c,'mdl']/pw.loc[c,'lambda_bar']:.2f})")
vb = d[(d.section == "wait")].set_index(["cell", "design"])
op = d[d.section == "openings"]
print("start-years implied by openings/u_c:", {c: vb.loc[(c, "design"), "openings"] / pw.loc[c, "u_c"] for c in pw.index})

print("\n== the kind shares (10.5)")
for c in cells.index:
    k = ch[(ch.cell == c) & ch.kind.isin(list("stfb"))].set_index("kind")
    print(c, "in-state shares sum", round(k.in_state_share.sum(), 12), "excess sum", f"{k.excess_over_strata.sum():.2e}",
          "flatten share = K2 overall", abs(k.loc["f", "in_state_share"] - res[(res.cell == c) & (res.scope == "overall")].unresolved_3r.iloc[0]) < 1e-12)

print("\n== A2 / A7 consistency")
for c in cells.index:
    for des in ("design", "twin0", "twin1"):
        g = op[(op.cell == c) & (op.design == des)]
        n = g[g.group == "all"]["count"].sum()
        wk = g[g.group == "wait"].copy(); wk["k"] = wk.key.astype(int)
        fb = g[(g.group == "share") & (g.key == "fallback")]
        ok = {grp: g[g.group == grp]["count"].sum() == n for grp in ("mark", "hour", "day_kind", "wait")}
        print(c, des, "sums", ok, "wait>=5 == fallbacks", wk[wk.k >= 5]["count"].sum() == fb["count"].iloc[0],
              "fallback share", abs(fb["count"].iloc[0] / n - vb.loc[(c, des), "fallback_share"]) < 1e-12,
              "openings", n == vb.loc[(c, des), "openings"])
st = d[(d.section == "states") & (d.kind == "share_in_state")]
pop = {}
for _, r in st.iterrows():
    n = sup[(sup.cell == r.cell) & (sup.year == r.year)]["in_state_offers"].iloc[0]
    pop.setdefault(int(r.year), []).append(n / r.share)
print("population offers per year implied by each cell (should agree):", {y: [round(v, 3) for v in vs] for y, vs in pop.items()})
for c in cells.index:
    g = sup[(sup.cell == c)]
    by = d[(d.section == "supply") & (d.cell == c) & d.by.notna()]
    print(c, "in-state offers by year", g.in_state_offers.sum(), "by hour", by[by.by == "hour"].in_state_offers.sum(),
          "by day kind", by[by.by == "day_kind"].in_state_offers.sum())

print("\n== u3's forecast hash (canonical JSON in the manifest)")
for name, js, sh in [("final", P["forecast_json"], P["forecast_sha256"])] + [
        (y, v["json"], v["sha256"]) for y, v in P["forecast_folds"].items()]:
    print(name, hashlib.sha256(js.encode("utf-8")).hexdigest() == sh)
fj = json.loads(P["forecast_json"])
print("coefficients", sum(len(v["beta"]) for v in fj.values()))
fs = d[(d.section == "states") & (d.kind == "forecast")]
for _, r in fs.iterrows():
    print(r.band, json.loads(r.beta) == fj[r.band]["beta"])
fo = d[(d.section == "states") & (d.kind == "fold")]
for _, r in fo.iterrows():
    print("fold", int(r.year), r.sha256 == P["forecast_folds"][str(int(r.year))]["sha256"], r.json == P["forecast_folds"][str(int(r.year))]["json"])

print("\n== a*'s (b): the vendored S1/S3 lifts (11 item 3 (b)), read as data")
b = lc[lc.check == "A10_consequence_b"]
for _, r in b.iterrows():
    f = ROOT / "vendor" / "stage2" / "results" / r.file
    vr = [x for x in csv.DictReader(open(f, encoding="utf-8")) if x.get("section") == "lift"]
    keys = list(vr[0].keys())
    hits = [x for x in vr if r.rule in x.values() and any(abs(float(x[k]) - 3.0) < 1e-9 for k in keys
            if k in ("R", "r", "rr", "target_r") and x[k] not in ("", None))]
    if not pd.isna(r.latency):
        hits = [x for x in hits if any(k in x and x[k] not in ("", None) and abs(float(x[k]) - r.latency) < 1e-9
                                       for k in ("latency", "lat"))]
    print(r.file, r.rule, r.latency, "reported", r.abs_mean_lift, "found", [abs(float(x["mean_lift"])) for x in hits], keys)

print("\n== the licence: numeric magnitudes")
num = d.select_dtypes("number")
for c in num.columns:
    v = num[c].dropna().abs()
    if len(v):
        print(f"{c:35s} min {v.min():.4g} max {v.max():.4g} non-integer {(v % 1 != 0).sum()}")
