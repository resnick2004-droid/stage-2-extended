import numpy as np, pandas as pd
ROOT = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended"
B = pd.read_csv(ROOT + r"\results\user_beside.csv", dtype=str, keep_default_na=False)
S = pd.read_csv(ROOT + r"\results\user_beside_starts.csv", dtype={"exact_runs_differing": str, "start_date": str})
U = pd.read_csv(ROOT + r"\vendor\stage2\results\user_journey.csv", dtype=str, keep_default_na=False)
days = sorted(S.start_date.unique()); N = len(days); pos = {d: i for i, d in enumerate(days)}
left = S.start_date.map(lambda d: N - pos[d])
print("development sessions", N, "first", days[0], "last", days[-1])
print("observed == min(252, sessions from the start to 2026-07-16 inclusive):", bool((S.observed == np.minimum(252, left)).all()))
print("observed > sessions left:", int((S.observed > left).sum()))
for c in ("first_pass","first_payout","break_even_day","response_day"):
    x = S[c].to_numpy(float); ok = np.isfinite(x)
    print(c, "beyond observed:", int((x[ok] > S.observed.to_numpy()[ok]).sum()))
# identity labels
I = B[(B.section=="identity") & (B.stat=="holds")]
I = I.assign(named=I.measure.str.split(":").str[0])
lab = I[I.arm!=""]
print("holds rows", len(I), "with arm", len(lab), "response column values", lab.response.value_counts().to_dict())
print("holds rows whose response column differs from the response named in the text:", int((lab.response != lab.named).sum()))
# P ordering under limits
E = B[B.section=="extra"].assign(value=lambda z: pd.to_numeric(z.value, errors="coerce"))
pv = E.pivot_table(index=["design","arm","response","block"], columns="measure", values="value", aggfunc="first")
print("P_2000 <= P_2500 <= P everywhere:", bool(((pv.P_bankroll_2000 <= pv.P_bankroll_2500+1e-12) & (pv.P_bankroll_2500 <= pv.P+1e-12)).all()))
# per-start internal consistency
y = S[S.observed>=252]
print("12*payouts_per_month integer:", bool(np.allclose(12*y.payouts_per_month, np.round(12*y.payouts_per_month))),
      "| 12*share_months_positive integer:", bool(np.allclose(12*y.share_months_positive, np.round(12*y.share_months_positive))),
      "| count in 12 months <= payouts:", bool((np.round(12*y.payouts_per_month) <= y.payouts).all()))
ls = y.largest_month_share.dropna()
print("largest_month_share in [1/12, 1]:", bool(((ls >= 1/12-1e-12) & (ls <= 1)).all()))
print("fell_back only with a break-even:", bool((S.fell_back.notna() <= S.break_even_day.notna()).all()))
print("deepest fall >= 0:", bool((S.deepest_fall_after_break_even.dropna() >= 0).all()))
print("off rows: no denial, no forfeiture, no response day:", bool((S[S.response=="off"].payouts_denied==0).all()),
      bool(S[S.response=="off"].cash_forfeited.fillna(0).eq(0).all()), bool(S[S.response=="off"].response_day.isna().all()))
print("denial rows: cash_forfeited zero/blank:", bool(S[S.response.str.startswith("denial")].cash_forfeited.fillna(0).eq(0).all()))
# U1 metric rows with the duplicate keys resolved (blank year)
keys = {"S3a": "first_payout:share_by@21", "S4a": "periodic:share_positive@126", "S4b": "periodic:share_positive@252"}
for d in ("p14","p15","p16"):
    for a in ("verdict","point"):
        for k,key in keys.items():
            u = U[(U.config==d)&(U.arm==a)&(U.key==key)]
            r = B[(B.design==d)&(B.arm==a)&(B.response=="off")&(B.block=="all")&(B.section=="scorecard")&(B.measure==k)]
            vals = set(zip(u.section, u.value, u.n))
            ok = any(abs(float(v)-float(r.value.iloc[0]))<=1e-12 and int(float(n))==int(r.n.iloc[0]) for _,v,n in vals)
            if not ok: print("U1 DIFF", d, a, k, vals, r.value.iloc[0], r.n.iloc[0])
print("U1 duplicate-key rows checked")
# U1's P from its month rows vs ours (P on the 63-session starts)
print(B[(B.section=="scorecard")&(B.measure=="P")&(B.response=="off")&(B.block=="all")][["design","arm","value","n"]].to_string())
