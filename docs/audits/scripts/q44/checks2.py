import math
import numpy as np, pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400); pd.set_option("display.max_columns", 40)
ROOT = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended"
B = pd.read_csv(ROOT + r"\results\user_beside.csv", dtype=str, keep_default_na=False)
S = pd.read_csv(ROOT + r"\results\user_beside_starts.csv", dtype={"exact_runs_differing": str, "start_date": str})
U = pd.read_csv(ROOT + r"\vendor\stage2\results\user_journey.csv", dtype=str, keep_default_na=False)
S["year"] = S.start_date.str[:4].astype(int)

print("== 1. S5c misses: the month-6 net total and its rounding sensitivity")
for a in ("verdict", "point"):
    t = S[(S.design == "p15") & (S.arm == a) & (S.response == "forfeit_25") & (S.observed >= 126) & (S.year >= 2024)]
    x = t.net_month_6.to_numpy(float)
    k = math.ceil(len(x) / 4)
    print(a, "n", len(x), "total", round(x.sum(), 2), "top-quarter sum", round(np.sort(x)[::-1][:k].sum(), 2),
          "max rounding error of total", round(len(x) * 0.005, 2))

print("== 2. shares in [0,1] in the headline file")
v = pd.to_numeric(B.value, errors="coerce")
sh = B.stat.str.startswith("share") | B.measure.str.startswith("share") | B.measure.isin(
    ["P", "S3a", "S4a", "S4b", "P_bankroll_2000", "P_bankroll_2500"])
bad = B[sh & np.isfinite(v) & ((v < 0) | (v > 1))]
print("share rows", int(sh.sum()), "outside [0,1]", len(bad))
print("S5c above 1:", B[(B.measure == "S5c") & (v > 1)][["design", "arm", "response", "block", "value", "n"]].to_string())
print("S5c blank:", int(((B.measure == "S5c") & ~np.isfinite(v)).sum()))

print("== 3. the ladder: P non-increasing as denial / forfeiture rises")
P = B[(B.section == "scorecard") & (B.measure == "P")].copy()
P["v"] = P.value.astype(float)
viol = []
for (d, a, blk), g in P.groupby(["design", "arm", "block"]):
    m = dict(zip(g.response, g.v))
    for lad in (["off", "denial_10", "denial_25", "denial_50"], ["off", "forfeit_10", "forfeit_25", "forfeit_50"]):
        seq = [m[x] for x in lad]
        ok = all(seq[i] >= seq[i + 1] for i in range(3))
        if not ok:
            viol.append((d, a, blk, lad[1][:6], seq))
    # forfeiture at least as bad as plain denial at each level
    for p in (10, 25, 50):
        if m[f"forfeit_{p}"] > m[f"denial_{p}"]:
            viol.append((d, a, blk, f"forfeit>denial {p}", (m[f"forfeit_{p}"], m[f"denial_{p}"])))
print("ladder violations", viol)
print(P.pivot_table(index=["design", "arm", "block"], columns="response", values="v")[
    ["off", "denial_10", "denial_25", "denial_50", "forfeit_10", "forfeit_25", "forfeit_50", "rtp", "rtp_w3"]].round(4).to_string())
# per-start: is net_month_3 non-increasing along the denial ladder start by start?
for lad in (["off", "denial_10", "denial_25", "denial_50"], ["off", "forfeit_10", "forfeit_25", "forfeit_50"]):
    for (d, a), g in S[S.response.isin(lad)].groupby(["design", "arm"]):
        w = g.pivot(index="start_day", columns="response", values="net_month_3")[lad].dropna()
        inc = sum(int((w[lad[i + 1]] > w[lad[i]] + 0.005).sum()) for i in range(3))
        w2 = g.pivot(index="start_day", columns="response", values="payouts_denied")[lad]
        dec = sum(int((w2[lad[i + 1]] < w2[lad[i]]).sum()) for i in range(1, 3))
        print(d, a, lad[1][:6], "starts", len(w), "per-start month-3 net rising a rung", inc,
              "| denied count falling a rung", dec)

print("== 4. the off rows against U1's start rows")
cols = ["observed", "first_pass", "spent_before_first_pass", "first_payout", "spent_before_first_payout", "payouts",
        "net_month_1", "net_month_2", "net_month_3", "net_month_6", "net_month_12"]
for d in ("p14", "p15", "p16"):
    for a in ("verdict", "point"):
        mine = S[(S.design == d) & (S.arm == a) & (S.response == "off")].set_index("start_day").sort_index()
        u = U[(U.section == "start") & (U.config == d) & (U.arm == a)].copy()
        u["start_day"] = u.start_day.astype(float).astype(int)
        u = u.set_index("start_day").sort_index()
        same_idx = list(mine.index) == list(u.index)
        same_dates = (mine.start_date.values == u.start_date.values).all() if same_idx else False
        worst = {}
        for c in cols:
            x = mine[c].to_numpy(float); y = pd.to_numeric(u[c], errors="coerce").to_numpy(float)
            nanmis = int((np.isnan(x) != np.isnan(y)).sum())
            diff = np.nanmax(np.abs(x - y)) if np.isfinite(x - y).any() else 0.0
            worst[c] = (nanmis, round(float(diff), 4))
        er = (mine.exact_runs_differing.fillna("") != "").sum()
        print(d, a, "starts", len(mine), "same days", same_idx, "same dates", same_dates, "exact_runs_differing nonblank", int(er))
        print("   ", worst)

print("== 5. S3c and S5b at off re-derived from U1's start rows (fees_month_3, pay_days)")
def rhythm_gap(pays, obs, w=126):
    if obs < w:
        return np.nan
    inw = sorted(int(x) for x in pays.split() if int(x) <= w) if pays else []
    if not inw:
        return np.nan
    mk = inw + [w]
    return float(max(b - a for a, b in zip(mk, mk[1:])))
for d in ("p14", "p15", "p16"):
    for a in ("verdict", "point"):
        u = U[(U.section == "start") & (U.config == d) & (U.arm == a)].copy()
        u["obs"] = u.observed.astype(float)
        u["yr"] = u.start_date.str[:4].astype(int)
        for blk in ("all", "judged"):
            jb = (u.yr >= 2024) if blk == "judged" else True
            e = u[(u.obs >= 63) & jb]
            net = e.net_month_3.astype(float).to_numpy(); fee = e.fees_month_3.astype(float).to_numpy()
            s3c = (net + fee).sum() / fee.sum()
            e126 = u[(u.obs >= 126) & jb]
            g = np.array([rhythm_gap(p, o) for p, o in zip(e126.pay_days, e126.obs)])
            g = g[np.isfinite(g)]
            s5b = float(np.percentile(g, 90))
            r1 = B[(B.design == d) & (B.arm == a) & (B.response == "off") & (B.block == blk) & (B.measure == "S3c")]
            r2 = B[(B.design == d) & (B.arm == a) & (B.response == "off") & (B.block == blk) & (B.measure == "S5b")]
            print(d, a, blk, "S3c rep", r1.value.iloc[0], r1.n.iloc[0], "mine", repr(s3c), len(e),
                  "| S5b rep", r2.value.iloc[0], r2.n.iloc[0], "mine", s5b, len(g),
                  "| agree", abs(float(r1.value.iloc[0]) - s3c) < 1e-12 and abs(float(r2.value.iloc[0]) - s5b) < 1e-9
                  and int(r1.n.iloc[0]) == len(e) and int(r2.n.iloc[0]) == len(g))

print("== 6. the off 'all' scorecard against Stage 2's row to beat (u_budget.csv) and U1's metric rows")
UB = pd.read_csv(ROOT + r"\vendor\stage2\results\u_budget.csv", dtype=str, keep_default_na=False)
rb = UB[(UB.section == "cell") & UB.cell.isin(["p14", "p15", "p16"])]
print(rb[["cell", "arm", "role", "block", "measure", "value", "n"]].head(3).to_string())
for _, x in rb.iterrows():
    arm = x.arm if x.arm else "verdict"
    r = B[(B.design == x.cell) & (B.arm == arm) & (B.response == "off") & (B.block == "all") & (B.section == "scorecard")
          & (B.measure == x.measure)]
    if len(r) != 1:
        print("no row for", x.cell, x.measure); continue
    a_, b_ = float(r.value.iloc[0]), float(x.value)
    ok = (np.isnan(a_) and np.isnan(b_)) or abs(a_ - b_) <= 1e-12 * max(1, abs(b_))
    nok = int(r.n.iloc[0]) == int(float(x.n))
    if not (ok and nok):
        print("DIFF", x.cell, arm, x.measure, x.value, x.n, "vs", r.value.iloc[0], r.n.iloc[0])
print("u_budget row-to-beat rows compared", len(rb), "arms present", rb.arm.unique())
keys = {"S1": "first_payout:spent_before_p90@126", "S3a": "first_payout:share_by@21", "S3b": "first_payout:days_p90@126",
        "S3c": "money_back:payouts_per_fee_dollar_pooled@63", "S4a": "periodic:share_positive@126",
        "S4b": "periodic:share_positive@252", "S5a": "periodic:net_p10@63", "S5b": "consistency:longest_gap_p90@126",
        "S5c": "consistency:concentration@126"}
nd = 0; nc = 0
for d in ("p14", "p15", "p16"):
    for a in ("verdict", "point"):
        for k, key in keys.items():
            u = U[(U.config == d) & (U.arm == a) & (U.key == key)]
            r = B[(B.design == d) & (B.arm == a) & (B.response == "off") & (B.block == "all") & (B.section == "scorecard") & (B.measure == k)]
            if len(u) != 1 or len(r) != 1:
                print("missing", d, a, k, len(u), len(r)); continue
            nc += 1
            if not (abs(float(u.value.iloc[0]) - float(r.value.iloc[0])) <= 1e-12 * max(1, abs(float(u.value.iloc[0])))
                    and int(float(u.n.iloc[0])) == int(r.n.iloc[0])):
                nd += 1; print("U1 DIFF", d, a, k, u.value.iloc[0], u.n.iloc[0], r.value.iloc[0], r.n.iloc[0])
print("U1 metric rows compared", nc, "differing", nd)

print("== 7. dates and windows")
print("start_date min/max", S.start_date.min(), S.start_date.max())
print("observed max", S.observed.max(), "starts per reading", S.groupby(["design", "arm", "response"]).size().unique())
last = S[S.start_date == S.start_date.max()]
print("last start's observed", last.observed.unique())
# a start's horizon cannot run past 2026-07-16: sessions left after a start date = count of later start days
days = sorted(S.start_date.unique())
pos = {dd: i for i, dd in enumerate(days)}
over = S[S.observed > S.start_date.map(lambda dd: len(days) - 1 - pos[dd])]
print("starts observed beyond the last development session", len(over))

print("== 8. the identity rows")
I = B[B.section == "identity"]
print(I.groupby(["design", "arm", "response", "stat"]).size().head(20).to_string())
print("holds values", I[I.stat == "holds"].value.value_counts().to_dict(), "count values",
      I[I.stat == "count"].value.value_counts().to_dict())
print(I[I.stat == "count"][["design", "arm", "measure", "value", "n", "note"]].head(8).to_string())

print("== 9. the columns: anything that could be a price level")
num = S.select_dtypes("number")
print(num.describe().T[["min", "max"]].to_string())
