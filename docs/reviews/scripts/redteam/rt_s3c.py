"""Red team: Spearman(P, S3c) and (P, S3a) over the design table, with range restriction made explicit, and a
family-cluster bootstrap. Independent of track B's scripts."""
import numpy as np
import pandas as pd
from scipy import stats

SRC = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results\user_drivers.csv"
df = pd.read_csv(SRC, low_memory=False)
dt = df[df["section"] == "design_table"]
print(dt[["arm", "block"]].drop_duplicates().to_string())
dt = dt[(dt["arm"] == "verdict") & (dt["block"] == "all")]
wide = dt.pivot_table(index=["subject", "family"], columns="measure", values="value", aggfunc="first").reset_index()
print(wide.shape, list(wide.columns)[:20])
w = wide.dropna(subset=["P", "S3c"])
print("n designs", len(w))
print(w["family"].value_counts().to_string())


def sp(a, b):
    return stats.spearmanr(a, b).statistic


print("all: S3c", round(sp(w.P, w.S3c), 3), "S3a", round(sp(w.P, w.S3a), 3))
fam_fail = w["family"].isin(["consistency", "plan"])
print("without consistency, plan:", int((~fam_fail).sum()), "S3c", round(sp(w.P[~fam_fail], w.S3c[~fam_fail]), 3),
      "S3a", round(sp(w.P[~fam_fail], w.S3a[~fam_fail]), 3))
for thr in (0.50, 0.55, 0.60):
    t = w[w.P >= thr]
    print(f"P >= {thr}: n {len(t)}  S3c {sp(t.P, t.S3c):+.3f}  S3a {sp(t.P, t.S3a):+.3f}  P range {t.P.min():.3f}-{t.P.max():.3f}")

# range restriction benchmark: a screen that is a noisy monotone function of P with the all-design rho of 0.76.
# What Spearman would it show among the top 22 by P, if it were exactly as good everywhere?
rng = np.random.default_rng(5)
P = w.P.values
res = []
for s in np.linspace(0.01, 0.4, 40):
    vals = []
    for _ in range(400):
        x = P + s * rng.standard_normal(len(P))
        top = P >= 0.60
        vals.append((sp(P, x), sp(P[top], x[top])))
    v = np.array(vals)
    res.append((s, v[:, 0].mean(), v[:, 1].mean(), np.percentile(v[:, 1], 5), np.percentile(v[:, 1], 95)))
for s, a, b, l, h in res:
    if abs(a - 0.765) < 0.04:
        print(f"homogeneous screen with all-design rho {a:.3f}: expected top-22 rho {b:+.3f} (5-95% {l:+.3f} to {h:+.3f})")

# family-cluster bootstrap of the top-22 S3a and S3c correlations
top = w[w.P >= 0.60].reset_index(drop=True)
fams = top["family"].unique()
bs = []
for _ in range(4000):
    pick = rng.choice(fams, len(fams), replace=True)
    t = pd.concat([top[top.family == f] for f in pick])
    if t.P.nunique() > 3:
        bs.append((sp(t.P, t.S3c), sp(t.P, t.S3a)))
bs = np.array(bs)
print("top-22 family bootstrap: S3c 5-95%", np.round(np.nanpercentile(bs[:, 0], [5, 95]), 2),
      "S3a 5-95%", np.round(np.nanpercentile(bs[:, 1], [5, 95]), 2), "families", len(fams))
print(top.sort_values("P", ascending=False)[["subject", "family", "P", "S3c", "S3a"]].to_string())
