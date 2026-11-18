import math, subprocess
import pandas as pd, numpy as np
pd.set_option("display.width",250)
ROOT = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended"
UB = pd.read_csv(ROOT + r"\vendor\stage2\results\u_budget.csv", dtype=str, keep_default_na=False)
print(UB[UB.section.isin(["judged","choice"])][["section","cell","arm","role","block","measure","value","n","reference","reference_value"]].head(12).to_string())
B = pd.read_csv(ROOT + r"\results\user_beside.csv", dtype=str, keep_default_na=False)
S = pd.read_csv(ROOT + r"\results\user_beside_starts.csv", dtype={"exact_runs_differing": str, "start_date": str})
# exact-run counts implied by the manifest's convention
one = S[(S.design=="p14")&(S.arm=="verdict")&(S.response=="off")]
print("starts with >= 21 sessions", int((one.observed>=21).sum()), "| index multiple of 21 with >= 21 sessions", int(((one.start_day%21==0)&(one.observed>=21)).sum()))
# S5c rounding bound
S["year"] = S.start_date.str[:4].astype(int)
for a in ("verdict","point"):
    t = S[(S.design=="p15")&(S.arm==a)&(S.response=="forfeit_25")&(S.observed>=126)&(S.year>=2024)]
    x = t.net_month_6.to_numpy(float); n=len(x); k=math.ceil(n/4)
    top = np.sort(x)[::-1][:k].sum(); tot = x.sum(); r = top/tot
    bound = r*((k*0.005)/abs(top) + (n*0.005)/abs(tot))
    rep = float(B[(B.design=="p15")&(B.arm==a)&(B.response=="forfeit_25")&(B.block=="judged")&(B.measure=="S5c")].value.iloc[0])
    print(a, "mine", r, "reported", rep, "difference", abs(r-rep), "cent-rounding bound", bound)
d = subprocess.run(["git","-C",ROOT,"diff","--numstat","results/read_ledger.jsonl"],capture_output=True,text=True).stdout
print("ledger numstat:", d.strip())
# share of identity-like 'off' rows at the verdict arm
