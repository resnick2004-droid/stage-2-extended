import json, pandas as pd, numpy as np
P="c:/Users/resni/AppData/Local/stage2-extended-resume/v1_validation_p14_f7eda0d02e31_500.jsonl"
ROOT="c:/Users/resni/OneDrive/Desktop/Stage 2 - Extended"
L={x["_label"]:x["row"] for x in map(json.loads, open(P))}
print(len(L), list(L)[:3])
R=pd.read_csv(ROOT+"/vendor/stage2/results/a3_brk30_cb20_gate.csv", float_precision="round_trip", low_memory=False)
z=np.isclose(R.enforcement_p.astype(float),0)
ref={"P14 registered":{"bound":R[(R.section=="gate_at_ledger_n")&(R["shift"]=="lower_bound")&z].iloc[0],"point":R[(R.section=="gate")&(R["shift"]=="point")&z].iloc[0]},
     "P14 registered at 0.05":{"bound":R[(R.section=="gate")&(R["shift"]=="lower_bound")&z].iloc[0],"point":R[(R.section=="gate")&(R["shift"]=="point")&z].iloc[0]}}
IC=["mean_r_used","pf_growth_on_base_p50","pf_required_p50","pf_required_p90","pf_required_p99","median_log_growth","mean_final_cash","median_final_cash","mean_max_drawdown","p90_max_drawdown","mean_combine_purchases"]
for lab,arms in ref.items():
    for arm,r in arms.items():
        res=L[lab][arm]
        out=[(c, res.get(c), r[c]) for c in IC if c in res]
        miss=[c for c in IC if c not in res]
        bad=[(c,a,b) for c,a,b in out if not np.isclose(float(a),float(b),rtol=0,atol=0)]
        print(lab,arm,"compared",len(out),"missing",miss,"bad",bad)
# CSV rows vs resume
d=pd.read_csv(ROOT+"/results/p14_validation.csv")
BOUND="verdict (0.05/370)"
def lab_of(r):
    s=r.section
    if s=="a1": return None if r.scheme.startswith("independent") else f"P14 a1 mean_block {int(r.mean_block)}"
    if s=="c1": return f"P14 c1 {r.scheme} realisation {int(r.realisation)}"
    if s=="slip": return None if r.scheme=="base" else f"P14 slip {r.scheme}"
    if s=="b2_curve":
        if int(r.step)==0: return None
        return f"P14 b2 {r.scheme} step {int(r.step)}"
bad=0;n=0
for _,r in d[d.section.isin(["a1","c1","slip","b2_curve"])].iterrows():
    lab=lab_of(r)
    if lab is None: continue
    arm="bound" if r.arm==BOUND else "point"
    res=L[lab][arm]; n+=1
    for c in ["pf_growth_on_base_p50","pf_required_p90","pf_required_p50","v1_share_below_start","mean_max_drawdown","mean_combine_purchases"]:
        if not np.isclose(float(res[c]),float(r[c]),rtol=1e-12): bad+=1; print(lab,arm,c,res[c],r[c])
print("csv rows checked against resume",n,"bad",bad)
# B2 beside measures
b=d[d.section=="b2_curve"][["scheme","step","pf_growth_on_base_p50","pf_required_p90","pf_required_p99","v1_share_below_start","mean_max_drawdown","v1_payout_drought_p90","v1_payouts_per_path_p50","v1_net_p10","median_days_to_first_payout","mean_combine_purchases"]]
pd.set_option("display.width",250)
print(b.to_string())
s=d[d.section=="slip"][["arm","scheme","pf_required_p99","v1_payout_drought_p90","v1_payouts_per_path_p50","v1_net_p10","median_days_to_first_payout","mean_combine_purchases"]]
print(s.to_string())
c=d[d.section=="c1"][["arm","scheme","realisation","v1_share_below_start","mean_max_drawdown","v1_payout_drought_p90","v1_payouts_per_path_p50","median_days_to_first_payout"]]
print(c.to_string())
# A1 control two-sided SE
a=d[d.section=="a1"]
for arm in a.arm.unique():
    g=a[a.arm==arm]; r0=g[g.scheme.str.startswith("independent")].iloc[0]
    for _,r in g.iterrows():
        if r.scheme.startswith("independent"): continue
        print(arm, r.scheme, "growth diff / sqrt(se0^2+se^2) = %.2f"%(r.diff_pf_growth_on_base_p50/np.hypot(r0.growth_se,r.growth_se)),
              "req90 = %.2f"%(r.diff_pf_required_p90/np.hypot(r0.required_p90_se,r.required_p90_se)))
