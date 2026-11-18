"""Independent re-derivation of results/user_beside.csv from results/user_beside_starts.csv (and the off rows against
vendor/stage2/results/user_journey.csv and u_budget.csv). numpy/pandas only; imports nothing from extended/ or vendor/."""
import math, sys, json
import numpy as np, pandas as pd

ROOT = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended"
B = pd.read_csv(ROOT + r"\results\user_beside.csv", dtype=str, keep_default_na=False)
S = pd.read_csv(ROOT + r"\results\user_beside_starts.csv", dtype={"exact_runs_differing": str, "start_date": str})
OUT = []

def num(x):
    return float(x) if x not in ("", None) else float("nan")

def rep(d, a, r, sec, blk, meas, stat):
    x = B[(B.design == d) & (B.arm == a) & (B.response == r) & (B.section == sec) & (B.block == blk)
          & (B.measure == meas) & (B.stat == stat)]
    if len(x) != 1:
        return None, None
    return num(x.value.iloc[0]), int(float(x.n.iloc[0]))

def q(v, p):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return float(np.percentile(v, p)) if len(v) else float("nan")

def days_q(first, w, p):
    f = np.asarray(first, float)
    v = np.where(np.isfinite(f) & (f <= w), f, 1e9)
    if not len(v):
        return float("nan")
    x = float(np.percentile(v, p))
    return x if x <= w else float("nan")

def cvar(x, a=0.10):
    v = np.sort(x[np.isfinite(x)])
    k = max(1, math.ceil(a * len(v) - 1e-12))
    return float(v[:k].mean())

def neff(x, L=63):
    v = x[np.isfinite(x)]; n = len(v); d = v - v.mean(); g0 = d @ d / n
    lrv = g0 + sum(2 * (1 - k / (L + 1)) * (d[:-k] @ d[k:]) / n for k in range(1, min(L, n - 1) + 1))
    return n * g0 / lrv

def conc(x):
    x = x[np.isfinite(x)]; t = x.sum()
    if not t > 0:
        return float("nan")
    k = math.ceil(len(x) / 4)
    return float(np.sort(x)[::-1][:k].sum() / t)

results = []  # (d,a,r,section,block,measure,stat, reported, mine, n_rep, n_mine)

def chk(d, a, r, sec, blk, meas, stat, mine, nmine, tol):
    v, n = rep(d, a, r, sec, blk, meas, stat)
    if v is None:
        results.append((d, a, r, sec, blk, meas, stat, None, mine, None, nmine, False, "row missing"))
        return
    both_nan = (not np.isfinite(v)) and (not np.isfinite(mine))
    ok = both_nan or (np.isfinite(v) and np.isfinite(mine) and abs(v - mine) <= tol(v))
    okn = (n == nmine)
    results.append((d, a, r, sec, blk, meas, stat, v, mine, n, nmine, ok and okn, ""))

abs_ = lambda t: (lambda v: t)
rel_ = lambda t: (lambda v: max(t, t * abs(v)))
CENT = abs_(0.0051)  # values in the per-start file are rounded to the cent
SHARE = abs_(1e-12)

S["year"] = S.start_date.str[:4].astype(int)
groups = S.groupby(["design", "arm", "response"], sort=False)
for (d, a, r), t in groups:
    t = t.sort_values("start_day")
    for blk in ("all", "judged"):
        jb = (t.year >= 2024) if blk == "judged" else pd.Series(True, index=t.index)
        def el(h):
            return t[(t.observed >= h) & jb]
        # ---- scorecard / extra: P
        e = el(63)
        nets = e[["net_month_1", "net_month_2", "net_month_3"]].to_numpy(float)
        ahead = nets > 0
        n = len(e)
        P = ahead.sum() / (3 * n)
        chk(d, a, r, "scorecard", blk, "P", "value", P, n, SHARE)
        chk(d, a, r, "extra", blk, "P", "value", P, n, SHARE)
        for i in range(3):
            chk(d, a, r, "extra", blk, f"share_ahead_month_{i+1}", "value", ahead[:, i].mean(), n, SHARE)
            chk(d, a, r, "extra", blk, f"mean_net_month_{i+1}", "value", nets[:, i].mean(), n, CENT)
        # months_ahead column itself
        ma = e.months_ahead.to_numpy(float)
        if not np.array_equal(ma, ahead.sum(axis=1).astype(float)):
            results.append((d, a, r, "starts", blk, "months_ahead", "column", None, None, None, None, False,
                            "months_ahead column differs from the count of positive nets"))
        chk(d, a, r, "extra", blk, "cvar10_net_month_3", "value", cvar(nets[:, 2]), n, CENT)
        sp = e.spent_before_first_payout.to_numpy(float)
        for L in (2000, 2500):
            ah = ahead & (np.where(np.isfinite(sp), sp, np.inf) <= L)[:, None]
            chk(d, a, r, "extra", blk, f"P_bankroll_{L}", "value", ah.sum() / (3 * n), n, SHARE)
            fs = sp[np.isfinite(sp)]
            chk(d, a, r, "extra", blk, f"share_spent_over_{L}", "value", float((fs > L).mean()), len(fs), SHARE)
        chk(d, a, r, "extra", blk, "n_eff_bartlett", "value", neff(ahead.sum(axis=1) / 3.0), n, rel_(1e-9))
        chk(d, a, r, "extra", blk, "n_nonoverlapping", "value", n / 63.0, n, SHARE)
        # ---- scorecard: the rest re-derivable from the per-start file
        e126 = el(126)
        fp = e126.first_payout.to_numpy(float)
        paid = np.isfinite(fp) & (fp <= 126)
        chk(d, a, r, "scorecard", blk, "S1", "value", q(e126.spent_before_first_payout.to_numpy(float)[paid], 90),
            int(paid.sum()), abs_(0.006))
        e21 = el(21)
        f21 = e21.first_payout.to_numpy(float)
        chk(d, a, r, "scorecard", blk, "S3a", "value", float((np.isfinite(f21) & (f21 <= 21)).mean()), len(e21), SHARE)
        chk(d, a, r, "scorecard", blk, "S3b", "value", days_q(fp, 126, 90), len(e126), abs_(1e-9))
        chk(d, a, r, "scorecard", blk, "S4a", "value", float((e126.net_month_6.to_numpy(float) > 0).mean()),
            len(e126), SHARE)
        e252 = el(252)
        chk(d, a, r, "scorecard", blk, "S4b", "value", float((e252.net_month_12.to_numpy(float) > 0).mean()),
            len(e252), SHARE)
        chk(d, a, r, "scorecard", blk, "S5a", "value", q(nets[:, 2], 10), n, abs_(0.006))
        chk(d, a, r, "scorecard", blk, "S5c", "value", conc(e126.net_month_6.to_numpy(float)), len(e126), abs_(1e-5))
        # ---- path section
        for ev, spc in (("first_pass", "spent_before_first_pass"), ("first_payout", "spent_before_first_payout")):
            f = e126[ev].to_numpy(float)
            for p in (10, 50, 90):
                chk(d, a, r, "path", blk, f"{ev}_days", f"p{p}", days_q(f, 126, p), len(e126), abs_(1e-9))
            hit = np.isfinite(f) & (f <= 126)
            chk(d, a, r, "path", blk, f"{ev}_days", "share_by_126", float(hit.mean()), len(e126), SHARE)
            v = e126[spc].to_numpy(float)[hit]
            for p in (10, 50, 90):
                chk(d, a, r, "path", blk, spc, f"p{p}", q(v, p), int(np.isfinite(v).sum()), abs_(0.006))
        be = e252.break_even_day.to_numpy(float)
        for p in (10, 50, 90):
            chk(d, a, r, "path", blk, "break_even_days", f"p{p}", days_q(be, 252, p), len(e252), abs_(1e-9))
        chk(d, a, r, "path", blk, "break_even_days", "share_by_252", float((np.isfinite(be) & (be <= 252)).mean()),
            len(e252), SHARE)
        for m in (1, 2, 3, 6, 12):
            em = el(21 * m); x = em.break_even_day.to_numpy(float)
            chk(d, a, r, "path", blk, "break_even", f"share_by_month_{m}",
                float((np.isfinite(x) & (x <= 21 * m)).mean()), len(em), SHARE)
        hitb = np.isfinite(be)
        fb = e252.fell_back.to_numpy(float)[hitb]
        chk(d, a, r, "path", blk, "break_even", "share_fell_back", float(fb.mean()) if len(fb) else float("nan"),
            len(fb), SHARE)
        df = e252.deepest_fall_after_break_even.to_numpy(float)[hitb]
        for p in (10, 50, 90):
            chk(d, a, r, "path", blk, "deepest_fall_after_break_even", f"p{p}", q(df, p),
                int(np.isfinite(df).sum()), abs_(0.006))
        for c in ("share_months_positive", "longest_months_without_payout", "sd_monthly_net", "payouts_per_month",
                  "payout_cash_per_month", "largest_month_share"):
            x = e252[c].to_numpy(float)
            tol = abs_(0.006) if c in ("sd_monthly_net", "payout_cash_per_month") else abs_(1e-9)
            for p in (10, 50, 90):
                chk(d, a, r, "path", blk, c, f"p{p}", q(x, p), int(np.isfinite(x).sum()), tol)
            if c in ("share_months_positive", "payouts_per_month", "payout_cash_per_month"):
                chk(d, a, r, "path", blk, c, "mean", float(np.nanmean(x)) if np.isfinite(x).any() else float("nan"),
                    int(np.isfinite(x).sum()), tol)
        # ---- response section
        for m in (1, 3, 12):
            em = el(21 * m); x = em.response_day.to_numpy(float)
            chk(d, a, r, "response", blk, "acted", f"share_by_month_{m}",
                float((np.isfinite(x) & (x <= 21 * m)).mean()), len(em), SHARE)
        rd = e252.response_day.to_numpy(float)
        for p in (10, 50, 90):
            chk(d, a, r, "response", blk, "response_day", f"p{p}", days_q(rd, 252, p), len(e252), abs_(1e-9))
        chk(d, a, r, "response", blk, "response_day", "share_by_252", float((np.isfinite(rd) & (rd <= 252)).mean()),
            len(e252), SHARE)
        e1 = el(1)
        for c, tol in (("payouts_denied", SHARE), ("cash_forfeited", CENT)):
            x = e1[c].to_numpy(float)
            chk(d, a, r, "response", blk, c, "mean", float(np.nanmean(x)) if np.isfinite(x).any() else float("nan"),
                int(np.isfinite(x).sum()), tol)

R = pd.DataFrame(results, columns=["design", "arm", "response", "section", "block", "measure", "stat", "reported",
                                   "mine", "n_rep", "n_mine", "agrees", "note"])
R.to_csv(sys.argv[1], index=False)
print("checks", len(R), "agree", int(R.agrees.sum()), "disagree", int((~R.agrees).sum()))
bad = R[~R.agrees]
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
print(bad.groupby(["section", "measure", "stat"]).size().to_string())
print(bad.head(60).to_string())
# which rows of the headline file did I not touch?
touched = set(zip(R.design, R.arm, R.response, R.section, R.block, R.measure, R.stat))
H = B[B.section.isin(["scorecard", "extra", "path", "response"])]
untouched = H[[k not in touched for k in zip(H.design, H.arm, H.response, H.section, H.block, H.measure, H.stat)]]
print("headline rows not re-derived:", len(untouched))
print(untouched.groupby(["section", "measure", "stat"]).size().to_string())
