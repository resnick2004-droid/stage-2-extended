import csv
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

R = Path(r"C:/Users/resni/OneDrive/Desktop/Stage 2 - Extended/results")
L = pd.read_csv(R / "calibration_lift.csv", low_memory=False)
P = pd.read_csv(R / "calibration_p.csv", low_memory=False)
T = pd.read_csv(R / "calibration_two_sample.csv", low_memory=False)
W = pd.read_csv(R / "calibration_power.csv", low_memory=False)
B = pd.read_csv(R / "bm63c_table.csv", low_memory=False)
lev = lambda k: 0.05 / (k * (k + 1))  # noqa: E731
KS = [11, 12, 13, 14, 15]

# bm63c table
B["t8_mine"] = [stats.t.ppf(1 - a, 8) for a in B["level"]]
print("bm63c t8 max abs diff", float((B["t8_mine"] - B["t8"]).abs().max()),
      "ratio max abs diff", float((B["critical"] / B["t8"] - B["ratio_to_t8"]).abs().max()))
b = B.sort_values("level")
print("bm63c critical non-increasing in level:", bool(np.all(np.diff(b["critical"].to_numpy()) <= 0)))
print("bm63c k-levels:", [(int(r.k) if pd.notna(r.k) else None, abs(lev(int(r.k)) - r.level) < 1e-15 if pd.notna(r.k) else None)
                          for r in B.itertuples()])
calib = set(P[(P["null"].str.startswith("real:")) | (P["null"].str.startswith("syn:") & (P["null"] != "syn:path_edge"))]["null"])
print("calibration-null set size", len(calib), "argmax nulls in it:", all(x in calib for x in B["argmax_null"]),
      "argmax set:", sorted(set(B["argmax_null"])))
print(B[["level", "k", "critical", "t8", "ratio_to_t8", "argmax_null"]].to_string(index=False))

# the bootstrap's level
lb = L[L["section"] == "boot"].copy()
lb["above"] = lb["ci_lo"] > lb["level"]
g = lb[lb["k"].isin(KS)]
print("cbb21: nulls with CI wholly above nominal by k:", g.groupby("k")["above"].sum().to_dict(),
      "point above by k:", (g["rate"] > g["level"]).groupby(g["k"]).sum().to_dict())
print(g[g["above"]][["null", "k", "rejections", "reps", "ratio", "ci_lo", "level"]].to_string())

# cons's power cost against t21w (lift; real thinned coin and persist1 nulls)
wl = W[W["part"] == "lift"]
rat = []
for base in ("coin", "persist1"):
    for v in ("win1", "net3"):
        for n in (200, 500, 1000, 2000, 5000):
            g2 = wl[wl["null"] == f"real:thin{n}:{v}:{base}"]
            for k in (11, 15):
                c = float(g2[(g2["method"] == "cons") & (g2["k"] == k)]["mdl80"].iloc[0])
                t = float(g2[(g2["method"] == "t21w") & (g2["k"] == k)]["mdl80"].iloc[0])
                rat.append(c / t)
print("cons mdl80 / t21w mdl80 on the 40 real thinned coin/persist1 cells: min %.4f median %.4f max %.4f" %
      (min(rat), float(np.median(rat)), max(rat)))

# drop rule: k=15 >= k=11 for cons in selection power; the four classes at both k
ws = W[(W["part"] == "two_sample") & (W["form"] == "placebo-selection") & (W["method"] == "cons")]
pv = ws.pivot_table(index=["df_rule", "null"], columns="k", values="difference80", aggfunc="first", dropna=False)
a, c = pv[11].to_numpy(), pv[15].to_numpy()
print("selection cons: k=15 difference80 >= k=11 (empty = infinite): violations",
      int(np.sum((np.isnan(a) & ~np.isnan(c)) | (~np.isnan(a) & ~np.isnan(c) & (c < a - 1e-12)))), "of", len(pv))
for model in ("window", "block21", "block5"):
    for k in (11, 15):
        s = ws[(ws["df_rule"] == "treated") & (ws["model"] == model) & (ws["value"] == "net3") & (ws["share"] == 0.25)
               & (ws["k"] == k)]
        print(f"  treated {model} net3 0.25 cons k={k}: rows {len(s)} difference80 "
              f"{'EMPTY' if s['difference80'].isna().all() else 'not empty'}")
print("raw k field values in calibration_power.csv:", sorted({r["k"] for r in csv.DictReader(open(R / 'calibration_power.csv', newline=''))}))
print("raw share field values (two_sample rows):", sorted({r["share"] for r in csv.DictReader(open(R / 'calibration_power.csv', newline='')) if r["part"] == "two_sample"}))

# the pin's worst rows with their counts and CSV line numbers
STRESS = ("syn:cluster_ar5", "syn:regime03", "syn:regime10", "syn:skew")
def worst_rows(df, mask, label):
    for k in KS:
        g = df[mask & (df["k"] == k)]
        i = g.index[int(np.argmax(g["ratio"].to_numpy()))]
        r = g.loc[i]
        print(f"  {label} k={k}: line {i + 2}, {r['null']}, {int(r['rejections'])}/{int(r['reps'])}, ratio {r['ratio']:.4f}, "
              f"ci [{r['ci_lo']:.3e}, {r['ci_hi']:.3e}] vs level {r['level']:.3e}")
c = L[(L["section"] == "size") & (L["method"] == "cons")]
print("one-sample cons worst rows:")
worst_rows(c, c["null"].str.startswith("real:"), "real")
worst_rows(c, c["null"].str.startswith("syn:") & ~c["null"].str.startswith(STRESS), "realistic")
worst_rows(c, c["null"].str.startswith(STRESS), "stress (beside)")
t = T[(T["df_rule"] == "treated") & (T["method"] == "cons")]
print("treated two-sample cons worst rows:")
worst_rows(t, t["form"] == "placebo-selection", "placebo-selection")
worst_rows(t, t["form"] == "two-sample (C1')", "C1'")
st = c[c["null"].str.startswith(STRESS) & c["k"].isin(KS)]
print("stress nulls with cons point rate above nominal:", sorted(set(st[st["rate"] > st["level"]]["null"])),
      "CI wholly above:", sorted(set(st[st["ci_lo"] > st["level"]]["null"])))
bm = P[(P["method"] == "bm63c") & P["k"].isin(KS) & (P["null"] != "syn:path_edge")]
print("bm63c point above nominal (real/realistic):", bm[bm["rate"] > bm["level"]][["null", "k", "rejections", "reps", "ratio", "ci_lo", "level"]].to_string())

# null name sets for the note
lsz = L[L["section"] == "size"]
real = sorted(set(lsz[lsz["null"].str.startswith("real:")]["null"]))
print("real streams", sorted({x.split(":")[1] for x in real}), "values", sorted({x.split(":")[2] for x in real}),
      "sides", sorted({x.split(":")[3] for x in real}))
syn = sorted(set(lsz[lsz["null"].str.startswith("syn:")]["null"]))
print("synthetic sizes", sorted({int(x.split(':')[2]) for x in syn}))
ps = T[(T["form"] == "placebo-selection") & (T["df_rule"] == "treated")]
print("selection models x shares x values:", ps.groupby("model")["null"].nunique().to_dict())
c1 = T[(T["form"] == "two-sample (C1')") & (T["df_rule"] == "treated")]
print("C1' nulls by side model:", c1.groupby("model")["null"].nunique().to_dict(), "fills", sorted(c1["level_fills"].unique()))
# C1' identical under both rules?
a = T[(T["form"] == "two-sample (C1')") & (T["df_rule"] == "treated")].set_index(["null", "method", "level"])["rejections"]
b2 = T[(T["form"] == "two-sample (C1')") & (T["df_rule"] == "all")].set_index(["null", "method", "level"])["rejections"]
print("C1' rejections identical under treated and all:", bool((a.sort_index() == b2.sort_index()).all()))
# P part: d621 reps; judged starts not in file
print("P d621 reps:", sorted(P[P['method'] == 'd621']['reps'].unique()))
