"""Red team: within-base Spearman(P, S3c) / (P, S3a) -- is the top-region sign a between-base (Simpson) effect?"""
import pandas as pd
from scipy import stats
SRC = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results\user_drivers.csv"
df = pd.read_csv(SRC, low_memory=False)
dt = df[(df["section"] == "design_table") & (df["arm"] == "verdict") & (df["block"] == "all")]
base = dt.groupby("subject")["base"].first()
w = dt.pivot_table(index=["subject", "family"], columns="measure", values="value", aggfunc="first").reset_index()
w["base"] = w["subject"].map(base)
print(w["base"].value_counts(dropna=False).to_string())
sp = lambda a, b: stats.spearmanr(a, b).statistic
for top in (False, True):
    for b, g in w.groupby("base"):
        g = g[g.P >= 0.60] if top else g
        if len(g) >= 5:
            print(f"{'P>=0.60' if top else 'all    '} base {b}: n {len(g)}  rho(P,S3c) {sp(g.P, g.S3c):+.2f}  rho(P,S3a) {sp(g.P, g.S3a):+.2f}")
# pooled within base (ranks centred within base), top region
t = w[w.P >= 0.60].copy()
for m in ("S3c", "S3a"):
    t["rP"] = t.groupby("base")["P"].rank(); t["rM"] = t.groupby("base")[m].rank()
    t["rP"] -= t.groupby("base")["rP"].transform("mean"); t["rM"] -= t.groupby("base")["rM"].transform("mean")
    print("top, pooled within base", m, round((t.rP * t.rM).sum() / ((t.rP**2).sum() * (t.rM**2).sum()) ** 0.5, 2))
print(t.groupby("base")[["P", "S3c", "S3a"]].mean().round(3).to_string())
# the kill-line claim on these 61
p14 = w[w.subject == "p14"].iloc[0]
lo = w[(w.S3c <= p14.S3c) & (w.subject != "p14")]; hi = w[(w.S3c > p14.S3c)]
print("S3c <= P-14's:", len(lo), "beat P-14 on P:", int((lo.P > p14.P).sum()), "| S3c above:", len(hi), "beat:", int((hi.P > p14.P).sum()))
