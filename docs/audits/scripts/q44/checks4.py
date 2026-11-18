import pandas as pd, numpy as np
pd.set_option("display.width",250)
B = pd.read_csv(r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\results\user_beside.csv", dtype=str, keep_default_na=False)
x = B[(B.section=="response")&(B.measure=="acted")&(B.stat=="share_by_month_12")&(B.block=="all")&(B.arm=="verdict")]
t = x.pivot(index="response", columns="design", values="value").astype(float)
P = B[(B.section=="scorecard")&(B.measure=="P")&(B.block=="all")&(B.arm=="verdict")].pivot(index="response", columns="design", values="value").astype(float)
print(pd.concat({"acted_by_m12": t, "P_minus_off": P - P.loc["off"]}, axis=1).round(4).to_string())
S = pd.read_csv(r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\results\user_beside_starts.csv", usecols=["design","arm","response","net_month_3","observed"])
# responses whose per-start month-3 nets equal off's on every start
for (d,a),g in S.groupby(["design","arm"]):
    off = g[g.response=="off"].net_month_3.to_numpy()
    same = [r for r,h in g.groupby("response") if r!="off" and np.array_equal(np.nan_to_num(h.net_month_3.to_numpy(), nan=1e18), np.nan_to_num(off, nan=1e18))]
    print(d,a,"responses identical to off at month 3 on every start:", same)
