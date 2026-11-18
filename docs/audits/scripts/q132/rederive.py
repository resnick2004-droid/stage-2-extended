"""Q-132a: the auditor's independent re-derivation of results/breakeven_fidelity_2.csv from its start file.

Reads CSV/JSON files only: the result and its start file with their manifests, Stage 2's registered
vendor/stage2/results/user_journey.csv and the three gate files, rc_reentry_screen.csv, E-188's
results/breakeven_fidelity.csv, the honesty rows of the result itself. Imports NOTHING from extended/, scripts/,
identity/ or vendor/ (numpy, pandas, scipy only). Every definition below is written from the documented meaning
(vendor/stage2/docs/USER_MILESTONES.md, D-620/D-621 as u_select/user_journey docstrings state them; RD-02 9.2;
Q-16's pcons as extended/p_bound.py's docstrings state it), coded here afresh.

Seeds (fixed before the first run of this script, audit-only, never a reading):
  AUDIT_CRIT_SEED = 91320001 -- the audit's own iid-normal null draws for the OBM(126) and flat-top(63/126)
                                critical values of the mdd_P re-derivation;
  AUDIT_FLIP_SEED = 91320002 -- the audit's own block sign-flip null replications of the mdd_P re-derivation.
They are deliberately not the runner's (Q-16's fixed-b seed and the reading's mdd_P seed, read from their declaring modules' text): agreement within Monte Carlo error is the check.

    python docs/audits/scripts/q132/rederive.py > docs/audits/scripts/q132/rederive_output.txt
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
RES = ROOT / "results"
VR = ROOT / "vendor" / "stage2" / "results"
AUDIT_CRIT_SEED = 91320001
AUDIT_FLIP_SEED = 91320002
MONTH = 21
JUDGED_FIRST = "2024-01-02"
WINDOW_END = "2026-07-16"
DESIGNS = ("p14", "p15", "p16")
RULES = ("stage2", "stop_first", "delay5", "both")
CORR = ("stop_first", "delay5", "both")
ARMS = ("verdict", "point")
BLOCKS = ("all", "judged")
BEYOND = 1e9
TOL_REL = 1e-9

problems: list[str] = []


def say(*a):
    print(*a, flush=True)


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def same(a, b, tol=TOL_REL):
    a, b = float(a), float(b)
    if math.isnan(a) and math.isnan(b):
        return True
    if math.isnan(a) or math.isnan(b):
        return False
    return abs(a - b) <= tol * max(1.0, abs(b))


# ================================================================== 1. manifests
say("## 1. manifests and hashes")
man = json.load(open(RES / "breakeven_fidelity_2.csv.manifest.json"))
sman = json.load(open(RES / "breakeven_fidelity_2_starts.csv.manifest.json"))
for f, m in (("breakeven_fidelity_2.csv", man), ("breakeven_fidelity_2_starts.csv", sman)):
    h = sha(RES / f)
    nrows = sum(1 for _ in open(RES / f, encoding="utf-8")) - 1
    say(f, "sha256 matches manifest:", h == m["sha256"], "| rows", nrows, "manifest", m["rows"],
        "| commit", m["git_commit"], "dirty", m["git_dirty"], "| exploratory", m["exploratory"], "| prereg_id",
        m["prereg_id"], "| seed", m["seed"], "| variant_count", m["variant_count"], "| timestamp", m["timestamp"])
    if h != m["sha256"] or nrows != m["rows"]:
        problems.append(f"{f}: hash or rows differ from its manifest")
say("summary manifest names the start file's sha256:", man["parameters"]["start_file"]["sha256"] == sman["sha256"])
for f, h in man["parameters"]["references"].items():
    mine = sha(VR / f)
    say("reference", f, "hash equals manifest:", mine == h)
    if mine != h:
        problems.append(f"reference {f} hash differs")

# ================================================================== 2. load
summ = pd.read_csv(RES / "breakeven_fidelity_2.csv", keep_default_na=False, na_values=[""], low_memory=False)
S = pd.read_csv(RES / "breakeven_fidelity_2_starts.csv", dtype=str, keep_default_na=False, low_memory=False)
say("\n## 2. the start file")
say("columns equal manifest:", list(S.columns) == sman["columns"], "| columns equal summary manifest's list:",
    list(S.columns) == sman["parameters"]["columns"])
say("rows by (design, rules, arm):", S.groupby(["design", "rules", "arm"]).size().unique().tolist(), "groups",
    S.groupby(["design", "rules", "arm"]).ngroups)
say("alt non-empty:", int((S["alt"] != "").sum()), "| exact_runs_differing non-empty:",
    int((S["exact_runs_differing"] != "").sum()))
ALT_EMPTY = bool((S["alt"] == "").all() and (S["exact_runs_differing"] == "").all())

NUM = [c for c in S.columns if c not in ("design", "rules", "arm", "start_date", "pass_days", "funded_days",
                                          "pay_days", "pay_cash", "exact_runs_differing", "alt")]
for c in NUM:   # Python's float(): round-trip exact on the file's text (pandas' fast parser is not, to the last ulp)
    S[c] = S[c].map(lambda x: float(x) if x != "" else np.nan).astype(float)
S["start_day"] = S["start_day"].astype(int)
S["observed"] = S["observed"].astype(int)


def ints(s):
    return [int(float(x)) for x in s.split()] if s.strip() else []


def floats(s):
    return [float(x) for x in s.split()] if s.strip() else []


S["_pay_days"] = S["pay_days"].map(ints)
S["_pay_cash"] = S["pay_cash"].map(floats)
S["_pass_days"] = S["pass_days"].map(ints)
S["_funded_days"] = S["funded_days"].map(ints)
S["year"] = S["start_date"].str[:4].astype(int)

# window: dates, observed, sessions read
say("start dates:", S["start_date"].min(), "to", S["start_date"].max(), "| any after", WINDOW_END, ":",
    bool((S["start_date"] > WINDOW_END).any()))
cal = S[["start_day", "start_date"]].drop_duplicates().sort_values("start_day")
say("one date per start_day across all groups:", cal["start_day"].is_unique, "| start days", int(cal["start_day"].min()),
    "to", int(cal["start_day"].max()), "| calendar sessions", len(cal))
last_idx = int(cal["start_day"].max())
# close k of a start is session start_day + k - 1 (close 1 = the start date's own session; day 0 = purchase evening)
reach = S["start_day"] + S["observed"] - 1
say("latest session index read by any start (start_day + observed - 1):", int(reach.max()), "| last calendar index",
    last_idx, "| observed = min(252, sessions left) on every row:",
    bool((S["observed"] == np.minimum(252, last_idx + 1 - S["start_day"])).all()))
if int(reach.max()) > last_idx or (S["start_date"] > WINDOW_END).any():
    problems.append("a start reads past the development window")

# ================================================================== 3. record identities on every row
say("\n## 3. per-row record identities (every design, rule set, arm, start)")
bad_fee = bad_mono = bad_first = bad_cnt = bad_order = 0
max_fee_err = 0.0
pd_list = S["_pay_days"].tolist()
pc_list = S["_pay_cash"].tolist()
ps_list = S["_pass_days"].tolist()
fd_list = S["_funded_days"].tolist()
obs = S["observed"].to_numpy()
nets = S[[f"net_month_{k}" for k in range(1, 13)]].to_numpy(float)
fees = S[[f"fees_month_{k}" for k in range(1, 13)]].to_numpy(float)
fp = S["first_payout"].to_numpy(float)
fpc = S["first_payout_cash"].to_numpy(float)
fps = S["first_pass"].to_numpy(float)
ffd = S["first_funded"].to_numpy(float)
npay = S["payouts"].to_numpy(float)
for i in range(len(S)):
    d, c = pd_list[i], pc_list[i]
    if len(d) != len(c) or len(d) != int(npay[i]):
        bad_cnt += 1
    if d != sorted(d) or any(x > obs[i] or x < 0 for x in d) or any(x > obs[i] for x in ps_list[i]):
        bad_order += 1
    # first events
    ok = (math.isnan(fp[i]) if not d else fp[i] == d[0]) and (math.isnan(fpc[i]) if not c else fpc[i] == c[0]) and \
         (math.isnan(fps[i]) if not ps_list[i] else fps[i] == ps_list[i][0]) and \
         (math.isnan(ffd[i]) if not fd_list[i] else ffd[i] == fd_list[i][0])
    if not ok:
        bad_first += 1
    darr, carr = np.asarray(d, float), np.asarray(c, float)
    prev = -np.inf
    for k in range(1, 13):
        if MONTH * k <= obs[i]:
            got = float(carr[darr <= MONTH * k].sum())
            err = abs((got - nets[i, k - 1]) - fees[i, k - 1])
            max_fee_err = max(max_fee_err, err)
            if err > 1e-5:
                bad_fee += 1
            if fees[i, k - 1] < prev - 1e-9 or fees[i, k - 1] < 0:
                bad_mono += 1
            prev = fees[i, k - 1]
        elif not (math.isnan(nets[i, k - 1]) and math.isnan(fees[i, k - 1])):
            bad_fee += 1
say("net = payouts received less fees at every observed month end: violations", bad_fee,
    "| largest |received - net - fees|", f"{max_fee_err:.3g}")
say("fees non-negative and never falling month to month: violations", bad_mono)
say("payouts = len(pay_days) = len(pay_cash): violations", bad_cnt, "| event days ordered and within observed:",
    "violations", bad_order)
say("first_payout/first_payout_cash/first_pass/first_funded = first listed event: violations", bad_first)
for nm, v in (("fee identity", bad_fee), ("fees monotone", bad_mono), ("payout count", bad_cnt),
              ("event order", bad_order), ("first events", bad_first)):
    if v:
        problems.append(f"{nm}: {v} violations")

# months ahead and p_months_ahead
ma = np.where(np.isfinite(nets[:, :3]).all(axis=1) & (obs >= 63), (nets[:, :3] > 0).sum(axis=1).astype(float), np.nan)
d1 = ~((np.isnan(ma) & np.isnan(S["p_months_ahead"].to_numpy())) | (ma == S["p_months_ahead"].to_numpy()))
d2 = ~((np.isnan(ma) & np.isnan(S["months_ahead"].to_numpy())) | (ma == S["months_ahead"].to_numpy()))
say("p_months_ahead re-made from net_month_1..3 (starts with 63 sessions): differing rows", int(d1.sum()),
    "| months_ahead column: differing rows", int(d2.sum()))
if d1.sum() or d2.sum():
    problems.append("months ahead columns differ from the nets")
S["_ma"] = ma

# evenness re-made from nets and payouts (starts with 252 sessions)
ev_bad = {k: 0 for k in ("share_months_positive", "longest_months_without_payout", "sd_monthly_net",
                         "payouts_per_month", "payout_cash_per_month", "largest_month_share")}
ev_cols = {k: S[k].to_numpy(float) for k in ev_bad}
for i in range(len(S)):
    if obs[i] < 252:
        for k in ev_bad:
            if not math.isnan(ev_cols[k][i]):
                ev_bad[k] += 1
        continue
    ch = np.diff(np.concatenate([[0.0], nets[i]]))
    cnt = np.zeros(12)
    cash = np.zeros(12)
    for dd, cc in zip(pd_list[i], pc_list[i]):
        m = (dd - 1) // MONTH + 1
        if 1 <= m <= 12:
            cnt[m - 1] += 1
            cash[m - 1] += cc
    run = best = 0
    for x in cnt:
        run = run + 1 if x == 0 else 0
        best = max(best, run)
    tot = cash.sum()
    mine = {"share_months_positive": float((ch > 0).mean()), "longest_months_without_payout": float(best),
            "sd_monthly_net": float(ch.std(ddof=1)), "payouts_per_month": float(cnt.sum() / 12),
            "payout_cash_per_month": float(tot / 12), "largest_month_share": float(cash.max() / tot) if tot > 0 else np.nan}
    for k in ev_bad:
        if not same(mine[k], ev_cols[k][i], 1e-9):
            ev_bad[k] += 1
say("evenness columns re-made from nets and payouts (252-session starts; blank otherwise): differing rows", ev_bad)
if any(ev_bad.values()):
    problems.append(f"evenness columns differ: {ev_bad}")

# daily-path columns: one-directional bounds from month ends (the daily closes are not in the file)
be = S["break_even_day"].to_numpy(float)
fb = S["fell_back"].to_numpy(float)
dfall = S["deepest_fall_after_break_even"].to_numpy(float)
b1 = b2 = b3 = b4 = 0
for i in range(len(S)):
    for k in range(1, 13):
        if MONTH * k <= obs[i] and nets[i, k - 1] >= -1e-6 and not (np.isfinite(be[i]) and be[i] <= MONTH * k):
            b1 += 1
            break
    if np.isfinite(be[i]):
        if any(MONTH * k > be[i] and MONTH * k <= obs[i] and nets[i, k - 1] < -1e-6 for k in range(1, 13)) and fb[i] != 1:
            b2 += 1
        if not dfall[i] >= 0:
            b3 += 1
    elif not (math.isnan(fb[i]) and math.isnan(dfall[i])):
        b4 += 1
say("break_even_day <= every month end whose net is >= 0: violations", b1, "| fell_back = 1 where a later month end is",
    "below zero: violations", b2, "| deepest fall >= 0: violations", b3, "| blanks without break-even: violations", b4)
if b1 + b2 + b3 + b4:
    problems.append("daily-path bounds violated")
# spent before first payout >= -net at month ends before the payout
sp = S["spent_before_first_payout"].to_numpy(float)
spp = S["spent_before_first_pass"].to_numpy(float)
b5 = 0
for i in range(len(S)):
    for k in range(1, 13):
        dk = MONTH * k
        if dk <= obs[i] and np.isfinite(fp[i]) and dk < fp[i] and not sp[i] >= -nets[i, k - 1] - 1e-6:
            b5 += 1
            break
say("spent_before_first_payout >= the cash below the start at every month end before it: violations", b5,
    "| spent columns negative:", int(((sp < 0) | (spp < 0)).sum()))
if b5:
    problems.append("spent bound violated")

# ================================================================== 4. registered start rows
say("\n## 4. stage2 start rows against Stage 2's registered user_journey.csv (section start)")
U = pd.read_csv(VR / "user_journey.csv", dtype=str, keep_default_na=False, low_memory=False)
U = U[U["section"] == "start"]
cmp_cols = ["start_day", "start_date", "observed", "pass_days", "funded_days", "pay_days", "payouts", "first_pass",
            "first_funded", "first_payout", "first_payout_cash", "spent_before_first_pass", "spent_before_first_payout",
            *[f"net_month_{k}" for k in range(1, 13)], *[f"fees_month_{k}" for k in range(1, 13)], "net_30",
            "exact_runs_differing"]
raw = pd.read_csv(RES / "breakeven_fidelity_2_starts.csv", dtype=str, keep_default_na=False, low_memory=False)
for d in DESIGNS:
    for a in ARMS:
        mine = raw[(raw.design == d) & (raw.rules == "stage2") & (raw.arm == a)].copy()
        reg = U[(U.config == d) & (U.arm == a)].copy()
        mine["_k"] = mine.start_day.astype(int)
        reg["_k"] = reg.start_day.astype(float).astype(int)
        mine, reg = mine.set_index("_k").sort_index(), reg.set_index("_k").sort_index()
        nd = {}
        maxerr = 0.0
        if list(mine.index) != list(reg.index):
            nd["index"] = 1
        for c in cmp_cols:
            if c in ("start_date", "exact_runs_differing"):
                diff = (mine[c].str.strip() != reg[c].str.strip()).sum()
            elif c in ("pass_days", "funded_days", "pay_days"):
                diff = sum(ints(x) != ints(y) for x, y in zip(mine[c], reg[c]))
            else:
                x = pd.to_numeric(mine[c].replace("", np.nan)).to_numpy(float)
                y = pd.to_numeric(reg[c].replace("", np.nan)).to_numpy(float)
                both = np.isnan(x) & np.isnan(y)
                e = np.where(both, 0.0, np.abs(x - y))
                e = np.where(np.isnan(e), np.inf, e)
                maxerr = max(maxerr, float(e.max()))
                diff = int((e > 1e-6).sum())
            if diff:
                nd[c] = int(diff)
        say(f"{d} {a}: starts {len(mine)} vs registered {len(reg)}; columns differing beyond 1e-6: {nd or 'none'};",
            f"largest money difference {maxerr:.3g}")
        if nd:
            problems.append(f"{d} {a} stage2 starts differ from user_journey.csv: {nd}")

# ================================================================== 5. scorecard, extra, path re-made
say("\n## 5. scorecard, extra and path rows re-made from the start file")


def q(x, p):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return (float(np.percentile(x, p)) if len(x) else np.nan), len(x)


def days_q(first, window, p):
    f = np.asarray(first, float)
    if not len(f):
        return np.nan
    v = np.where(np.isfinite(f) & (f <= window), f, BEYOND)
    x = float(np.percentile(v, p))
    return x if x <= window else np.nan


def blk(t, b, h):
    m = t["observed"].to_numpy() >= h
    if b == "judged":
        m &= t["year"].to_numpy() >= 2024
    return t[m]


def gap(pdays, w):
    ins = sorted(x for x in pdays if x <= w)
    if not ins:
        return np.nan
    marks = ins + [w]
    return float(max(b_ - a_ for a_, b_ in zip(marks, marks[1:])))


def conc(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if not len(x) or not x.sum() > 0:
        return np.nan
    k = math.ceil(len(x) / 4)
    return float(np.sort(x)[::-1][:k].sum() / x.sum())


def nef(x, lag=63):
    v = np.asarray(x, float)
    v = v[np.isfinite(v)]
    n = len(v)
    if n < 2:
        return np.nan
    d = v - v.mean()
    g0 = d @ d / n
    if g0 <= 0:
        return np.nan
    lrv = g0
    for k in range(1, min(lag, n - 1) + 1):
        lrv += 2 * (1 - k / (lag + 1)) * (d[:-k] @ d[k:]) / n
    return float(n * g0 / lrv) if lrv > 0 else np.nan


def card(t, b):
    out = {}
    s = blk(t, b, 63)
    n3 = s[[f"net_month_{m}" for m in (1, 2, 3)]].to_numpy(float)
    ok = np.isfinite(n3).all(axis=1)
    out["P"] = ((n3[ok] > 0).sum() / (3 * ok.sum()) if ok.sum() else np.nan, int(ok.sum()))
    s126 = blk(t, b, 126)
    f = s126["first_payout"].to_numpy(float)
    hit = np.isfinite(f) & (f <= 126)
    out["S1"] = (q(s126["spent_before_first_payout"].to_numpy(float)[hit], 90)[0], int(hit.sum()))
    s21 = blk(t, b, 21)
    f21 = s21["first_payout"].to_numpy(float)
    out["S3a"] = (float((np.isfinite(f21) & (f21 <= 21)).mean()) if len(s21) else np.nan, len(s21))
    out["S3b"] = (days_q(f, 126, 90), len(s126))
    n3_ = s["net_month_3"].to_numpy(float)
    f3 = s["fees_month_3"].to_numpy(float)
    ok3 = np.isfinite(n3_) & np.isfinite(f3)
    out["S3c"] = (float((n3_[ok3] + f3[ok3]).sum() / f3[ok3].sum()) if ok3.any() and f3[ok3].sum() > 0 else np.nan,
                  int(ok3.sum()))
    x6 = s126["net_month_6"].to_numpy(float)
    x6 = x6[np.isfinite(x6)]
    out["S4a"] = (float((x6 > 0).mean()) if len(x6) else np.nan, len(x6))
    s252 = blk(t, b, 252)
    x12 = s252["net_month_12"].to_numpy(float)
    x12 = x12[np.isfinite(x12)]
    out["S4b"] = (float((x12 > 0).mean()) if len(x12) else np.nan, len(x12))
    out["S5a"] = q(n3_[np.isfinite(n3_)], 10)
    g = np.array([gap(p, 126) for p in s126["_pay_days"]], float)
    out["S5b"] = q(g, 90)
    out["S5c"] = (conc(x6), len(x6))
    return out


def extra(t, b):
    out = {}
    s = blk(t, b, 63)
    n3 = s[[f"net_month_{m}" for m in (1, 2, 3)]].to_numpy(float)
    ok = np.isfinite(n3).all(axis=1)
    n = int(ok.sum())
    a = n3[ok] > 0
    for i, m in enumerate((1, 2, 3)):
        out[f"share_ahead_month_{m}"] = (float(a[:, i].mean()), n)
    out["P"] = (float(a.sum() / (3 * n)), n)
    for i, m in enumerate((1, 2, 3)):
        x = n3[:, i]
        out[f"mean_net_month_{m}"] = (float(np.nanmean(x)), int(np.isfinite(x).sum()))
    x = np.sort(n3[:, 2][np.isfinite(n3[:, 2])])
    k = max(1, math.ceil(0.10 * len(x) - 1e-12))
    out["cvar10_net_month_3"] = (float(x[:k].mean()), len(x))
    spent = s["spent_before_first_payout"].to_numpy(float)
    for lim in (2000, 2500):
        sp_ = np.where(np.isfinite(spent), spent, np.inf)[ok]
        aa = a & (sp_[:, None] <= lim)
        out[f"P_bankroll_{lim}"] = (float(aa.sum() / (3 * n)), n)
        fs = spent[np.isfinite(spent)]
        out[f"share_spent_over_{lim}"] = (float((fs > lim).mean()), len(fs))
    out["n_eff_bartlett"] = (nef(a.sum(axis=1) / 3.0), n)
    out["n_nonoverlapping"] = (n / 63.0, n)
    return out


def path(t, b):
    out = {}
    e = blk(t, b, 126)
    for ev, spn in (("first_pass", "spent_before_first_pass"), ("first_payout", "spent_before_first_payout")):
        f = e[ev].to_numpy(float)
        for p in (10, 50, 90):
            out[(f"{ev}_days", f"p{p}")] = (days_q(f, 126, p), len(f))
        hit = np.isfinite(f) & (f <= 126)
        out[(f"{ev}_days", "share_by_126")] = (float(hit.mean()) if len(f) else np.nan, len(f))
        for p in (10, 50, 90):
            out[(spn, f"p{p}")] = q(e[spn].to_numpy(float)[hit], p)
    e2 = blk(t, b, 252)
    bev = e2["break_even_day"].to_numpy(float)
    for p in (10, 50, 90):
        out[("break_even_days", f"p{p}")] = (days_q(bev, 252, p), len(bev))
    out[("break_even_days", "share_by_252")] = (float((np.isfinite(bev) & (bev <= 252)).mean()) if len(bev) else np.nan,
                                                len(bev))
    for m in (1, 2, 3, 6, 12):
        em = blk(t, b, MONTH * m)
        x = em["break_even_day"].to_numpy(float)
        out[("break_even", f"share_by_month_{m}")] = (float((np.isfinite(x) & (x <= MONTH * m)).mean())
                                                     if len(x) else np.nan, len(x))
    hit = np.isfinite(bev)
    fbv = e2["fell_back"].to_numpy(float)[hit]
    out[("break_even", "share_fell_back")] = (float(fbv.mean()) if len(fbv) else np.nan, len(fbv))
    for p in (10, 50, 90):
        out[("deepest_fall_after_break_even", f"p{p}")] = q(e2["deepest_fall_after_break_even"].to_numpy(float)[hit], p)
    for c in ("share_months_positive", "longest_months_without_payout", "sd_monthly_net", "payouts_per_month",
              "payout_cash_per_month", "largest_month_share"):
        x = e2[c].to_numpy(float)
        for p in (10, 50, 90):
            out[(c, f"p{p}")] = q(x, p)
        if c in ("share_months_positive", "payouts_per_month", "payout_cash_per_month"):
            xf = x[np.isfinite(x)]
            out[(c, "mean")] = (float(xf.mean()) if len(xf) else np.nan, len(xf))
    return out


groups = {k: g.sort_values("start_day") for k, g in S.groupby(["design", "rules", "arm"])}
key_cols = ["section", "design", "rules", "arm", "block", "measure", "stat"]
fileval = {}
for r in summ[summ.section.isin(["scorecard", "extra", "path"])].itertuples(index=False):
    fileval[(r.section, r.design, r.rules, r.arm, r.block, r.measure, r.stat)] = (r.value, r.n)
compared = differ = nmis = 0
mine_all = {}
diffs = []
for (d, ru, a), t in groups.items():
    for b in BLOCKS:
        c = card(t, b)
        for m, v in c.items():
            mine_all[("scorecard", d, ru, a, b, m, "value")] = v
        for m, v in extra(t, b).items():
            mine_all[("extra", d, ru, a, b, m, "value")] = v
        for (m, st), v in path(t, b).items():
            mine_all[("path", d, ru, a, b, m, st)] = v
for k, (v, n) in mine_all.items():
    if k not in fileval:
        nmis += 1
        diffs.append(("missing in file", k))
        continue
    fv, fn = fileval[k]
    compared += 1
    if not same(v, fv) or int(n) != int(fn):
        differ += 1
        diffs.append((k, v, n, fv, fn))
extra_keys = [k for k in fileval if k not in mine_all and k[5] != "mdd_P"]
say(f"rows re-made: {len(mine_all)}; compared {compared}; differing (value 1e-9 relative or n) {differ}; "
    f"my rows absent from the file {nmis}; file rows I did not re-make (other than mdd_P) {len(extra_keys)}")
for x in diffs[:20]:
    say("  DIFF", x)
for x in extra_keys[:10]:
    say("  not re-made:", x)
if differ or nmis:
    problems.append(f"{differ} re-made rows differ, {nmis} missing")

# ================================================================== 6. internal checks
say("\n## 6. internal identities over the summary")
sv = {k: v for k, v in fileval.items()}
bad = []
for d in DESIGNS:
    for ru in RULES:
        for a in ARMS:
            for b in BLOCKS:
                g = lambda s, m, st="value": sv.get((s, d, ru, a, b, m, st), (np.nan, -1))  # noqa: E731
                if not same(g("scorecard", "P")[0], g("extra", "P")[0], 1e-12) or g("scorecard", "P")[1] != g("extra", "P")[1]:
                    bad.append((d, ru, a, b, "card P != extra P"))
                m3 = np.mean([g("extra", f"share_ahead_month_{m}")[0] for m in (1, 2, 3)])
                if not same(m3, g("extra", "P")[0], 1e-12):
                    bad.append((d, ru, a, b, "P != mean of shares"))
                lo, hi, p = g("extra", "P_bankroll_2000")[0], g("extra", "P_bankroll_2500")[0], g("extra", "P")[0]
                if not (lo <= hi + 1e-12 <= p + 2e-12):
                    bad.append((d, ru, a, b, "bankroll P not ordered"))
                if not g("extra", "share_spent_over_2000")[0] >= g("extra", "share_spent_over_2500")[0] - 1e-12:
                    bad.append((d, ru, a, b, "spent-over shares not ordered"))
                if not g("extra", "cvar10_net_month_3")[0] <= g("scorecard", "S5a")[0] + 1e-9:
                    bad.append((d, ru, a, b, "CVaR10 above p10"))
                if not same(g("scorecard", "S1")[0], g("path", "spent_before_first_payout", "p90")[0]):
                    bad.append((d, ru, a, b, "S1 != path p90"))
                if not same(g("scorecard", "S3b")[0], g("path", "first_payout_days", "p90")[0]):
                    bad.append((d, ru, a, b, "S3b != path p90"))
say("card P = extra P; P = mean of the three shares; bankroll P ordered; spent-over ordered; CVaR10 <= S5a;",
    "S1 = path p90; S3b = path p90 -- problems:", len(bad), bad[:6])
if bad:
    problems.append(f"internal identities: {bad[:6]}")
# shares in [0, 1]
sh = summ[(summ.stat.astype(str).str.startswith("share") | summ.measure.astype(str).str.startswith("share") |
           summ.measure.isin(["P", "S3a", "S4a", "S4b", "P_bankroll_2000", "P_bankroll_2500"]) |
           summ.stat.isin(["coverage", "miss_above", "miss_below", "rare_coverage"])) &
          ~summ.section.isin(["paired", "trades", "gate"])]
v = sh.value.to_numpy(float)
fin = np.isfinite(v)
say("share rows (scorecard, extra, path, honesty and the paired rare coverage):", len(sh), "| finite", int(fin.sum()),
    "| outside [0, 1]:", int(((v[fin] < -1e-12) | (v[fin] > 1 + 1e-12)).sum()))
pr = summ[(summ.section == "paired") & (summ.stat == "rare_coverage")].value.to_numpy(float)
tr = summ[(summ.section == "trades") & summ.measure.str.startswith("share")].value.to_numpy(float)
gs = summ[(summ.section == "gate") & summ.measure.isin(["share_accounts_ever_paid", "ruin_probability"])].value.to_numpy(float)
say("paired rare_coverage outside [0,1]:", int(((pr < 0) | (pr > 1)).sum()), "| trades shares outside [0,1]:",
    int(((tr < 0) | (tr > 1)).sum()), "| gate shares/probabilities outside [0,1]:", int(((gs < 0) | (gs > 1)).sum()))
# start-file shares
for c in ("share_months_positive", "largest_month_share", "fell_back"):
    x = S[c].to_numpy(float)
    x = x[np.isfinite(x)]
    say(f"start file {c} outside [0,1]:", int(((x < 0) | (x > 1)).sum()))

# ================================================================== 7. gate rows
say("\n## 7. gate rows")
GC = man["parameters"]["gate_cols"]
gf = {"p14": "a3_brk30_cb20_gate.csv", "p15": "rc_s100_all_gate.csv", "p16": "rc_s150_all_gate.csv"}
for d, f in gf.items():
    g = pd.read_csv(VR / f, low_memory=False)
    g = g[(g.section == "gate") & np.isclose(pd.to_numeric(g.enforcement_p, errors="coerce").fillna(-1), 0.0)]
    b1_ = b2_ = 0
    for _, row in g.iterrows():
        for c in GC:
            reg = summ[(summ.section == "gate") & (summ.design == d) & (summ.rules == "registered") &
                       (summ["shift"] == row["shift"]) & (summ.measure == c)].value
            s2 = summ[(summ.section == "gate") & (summ.design == d) & (summ.rules == "stage2") &
                      (summ["shift"] == row["shift"]) & (summ.measure == c)].value
            if len(reg) != 1 or not same(reg.iloc[0], float(row[c]), 1e-12):
                b1_ += 1
            if len(s2) != 1 or not same(s2.iloc[0], float(row[c]), 1e-6):
                b2_ += 1
    say(f"{d} ({f}): 0 % gate rows {len(g)} (shifts {sorted(g['shift'])}, rtp {sorted(set(g.rtp.astype(str)))});",
        f"registered rows != file: {b1_} of {len(g) * len(GC)}; stage2 rows != file (1e-6 rel): {b2_}")
    if b1_ or b2_:
        problems.append(f"{d} gate rows differ from {f}")
gt = summ[summ.section == "gate"].pivot_table(index=["design", "shift", "measure"], columns="rules", values="value",
                                              aggfunc="first")
say("ruin_probability over every gate row: max", float(gt.xs("ruin_probability", level="measure").max().max()))
lbg = gt.xs(("lower_bound", "pf_growth_on_base_p50"), level=("shift", "measure"))
say("pf_growth_on_base_p50 at lower_bound, every design and rule set above zero:", bool((lbg.drop(columns="registered") > 0).all().all()))
say("paths column = 500 on every gate row:", bool((gt.xs("paths", level="measure") == 500).all().all()))
say("gate table (rules as columns), the measures beside growth:")
for m in ("pf_growth_on_base_p50", "pf_required_p90", "ruin_probability", "mean_max_drawdown",
          "median_days_to_first_payout", "mean_r_used"):
    say(gt.xs(m, level="measure").to_string(float_format=lambda x: f"{x:.6g}"))

# ================================================================== 8. trades
say("\n## 8. trades section")
T = summ[summ.section == "trades"].pivot_table(index=["design", "rr", "rules"], columns="measure", values="value",
                                                aggfunc="first")
tb = []
for (d, rr), g in T.groupby(level=["design", "rr"]):
    g = g.droplevel([0, 1])
    n0 = g.loc["stage2", "trades"]
    for ru in RULES:
        r = g.loc[ru]
        s_ = r.share_target + r.share_stop + r.share_breakeven + r.share_flatten
        if abs(s_ - 1) > 1e-9:
            tb.append((d, rr, ru, "shares sum", s_))
        for c in ("share_target", "share_stop", "share_breakeven", "share_flatten"):
            if abs(r[c] * r.trades - round(r[c] * r.trades)) > 1e-6:
                tb.append((d, rr, ru, c, "not a whole count"))
        if r.trades != n0:
            tb.append((d, rr, ru, "trade count differs from stage2"))
    s2 = g.loc["stage2"]
    if s2.changed_kind != 0 or s2.changed_gross != 0:
        tb.append((d, rr, "stage2 changed"))
    sf = g.loc["stop_first"]
    dt = round((s2.share_target - sf.share_target) * n0)
    db = round((sf.share_breakeven - s2.share_breakeven) * n0)
    if not (dt == db == sf.changed_kind) or abs(sf.share_stop - s2.share_stop) > 1e-12 or \
            abs(sf.share_flatten - s2.share_flatten) > 1e-12 or sf.mean_net_r > s2.mean_net_r + 1e-12:
        tb.append((d, rr, "stop_first not targets-to-breakeven only", dt, db, sf.changed_kind))
    for ru in ("delay5", "both"):
        r = g.loc[ru]
        moved = sum(abs(round((r[c] - s2[c]) * n0)) for c in ("share_target", "share_stop", "share_breakeven",
                                                              "share_flatten"))
        if moved > 2 * r.changed_kind + 1e-9:
            tb.append((d, rr, ru, "kind moves exceed changed_kind"))
say("groups (design, R):", T.index.droplevel("rules").nunique(), "| problems:", len(tb), tb[:6])
if tb:
    problems.append(f"trades: {tb[:4]}")
ck = summ[(summ.section == "trades") & (summ.measure == "changed_kind")].pivot_table(index=["design", "rr"],
                                                                                     columns="rules", values="value")
say("changed_kind by design and R (trades whose exit kind differs from stage2's):")
say(ck.to_string(float_format=lambda x: f"{x:.0f}"))
cg = summ[(summ.section == "trades") & (summ.measure == "changed_gross")].pivot_table(index=["design"],
                                                                                      columns="rules", values="value",
                                                                                      aggfunc="sum")
say("changed_gross summed over R:")
say(cg.to_string(float_format=lambda x: f"{x:.0f}"))
# P-15's screen identity, as far as the file can test it
scr = pd.read_csv(VR / "rc_reentry_screen.csv", low_memory=False)
row = scr[(scr.cell == "rc_s100_all")]
say("rc_reentry_screen.csv rc_s100_all rows:", len(row), "| its candidates column:",
    row["candidates"].dropna().tolist()[:3], "| this file's p15 stage2 trades at every R:",
    sorted(set(T.xs(("p15",), level=["design"]).xs("stage2", level="rules")["trades"].tolist())))

# ================================================================== 9. paired rows (RD-02 9.2)
say("\n## 9. paired rows re-made from the start file (RD-02 9.2)")
H = 63
hon = summ[summ.section == "honesty"]


def kept(n, h=H):
    return [(j * h, (j + 1) * h) for j in range(0, n // h, 2)]


def ahead_series(t, b):
    s = blk(t, b, 63)
    s = s[np.isfinite(s["_ma"].to_numpy(float))]
    return dict(zip(s["start_date"], s["_ma"].to_numpy(float) / 3.0))


pv = {}
for r in summ[summ.section == "paired"].itertuples(index=False):
    pv[(r.design, r.rules, r.arm, r.block, r.stat)] = (r.value, r.n, r.note)
pcomp = pdiff = 0
pdl = []
paired_mine = {}
for d in DESIGNS:
    for ru in CORR:
        for a in ARMS:
            for b in BLOCKS:
                x = ahead_series(groups[(d, ru, a)], b)
                y = ahead_series(groups[(d, "stage2", a)], b)
                common = sorted(set(x) & set(y))
                if set(x) != set(y):
                    pdl.append((d, ru, a, b, "starts differ between sides"))
                A = np.array([x[k] for k in common])
                B = np.array([y[k] for k in common])
                D_ = A - B
                mine = {"mean": (float(D_.mean()), len(D_))}
                w = kept(len(D_))
                wm = np.array([D_[i:j].mean() for i, j in w])
                wa = np.array([A[i:j].mean() for i, j in w])
                wb = np.array([B[i:j].mean() for i, j in w])
                if len(D_):
                    mine["n_w"] = (float(len(w)), len(D_))
                    mine["sign_above"] = (float((wa > wb).sum()), len(D_))
                    mine["sign_equal"] = (float((wa == wb).sum()), len(D_))
                    mine["sign_below"] = (float((wa < wb).sum()), len(D_))
                    mine["n_eff"] = (nef(D_, 63), len(D_))
                    if np.any(D_ != 0) and len(w) >= 4 and wm.std(ddof=1) > 0:
                        se = wm.std(ddof=1) / math.sqrt(len(wm))
                        tc = stats.t.ppf(0.95, len(wm) - 1)
                        mine["ci90_low"] = (float(wm.mean() - tc * se), len(D_))
                        mine["ci90_high"] = (float(wm.mean() + tc * se), len(D_))
                        mine["kept_mean"] = (float(wm.mean()), len(D_))
                        mine["mdd"] = (float((stats.t.ppf(0.95, len(wm) - 1) + stats.t.ppf(0.80, len(wm) - 1)) * se),
                                       len(D_))
                        hh = hon[(hon.h == H) & (hon.n_w == len(w)) & (hon.stat == "coverage")]
                        cov = dict(zip(hh.measure, hh.value))
                        mine["interval_label"] = (float(min(cov[k] for k in ("gauss", "ahead", "paired")) < 0.88), len(D_))
                        mine["rare_coverage"] = (min(v_ for k_, v_ in cov.items() if k_.startswith(("lumpy", "persistent"))),
                                                 len(D_))
                # the cards' difference
                cp = sv[("scorecard", d, ru, a, b, "P", "value")][0] - sv[("scorecard", d, "stage2", a, b, "P", "value")][0]
                if not same(mine["mean"][0], cp, 1e-12):
                    pdl.append((d, ru, a, b, "paired mean != cards' difference"))
                paired_mine[(d, ru, a, b)] = mine
                for st, (v_, n_) in mine.items():
                    pcomp += 1
                    fv = pv.get((d, ru, a, b, st))
                    if fv is None or not same(v_, fv[0], 1e-9) or int(n_) != int(fv[1]):
                        pdiff += 1
                        pdl.append((d, ru, a, b, st, v_, fv))
                fstats = {k[4] for k in pv if k[:4] == (d, ru, a, b)} - {"interval"}
                if fstats - set(mine):
                    pdl.append((d, ru, a, b, "file stats I did not make", sorted(fstats - set(mine))))
say(f"paired values compared {pcomp}; differing {pdiff}; problems {len(pdl)}", pdl[:8])
if pdiff or pdl:
    problems.append(f"paired rows: {pdl[:4]}")
iv = summ[(summ.section == "paired") & (summ.stat == "interval")]
say("paired 'interval' rows (no interval, with the reason):", len(iv), iv[["design", "rules", "arm", "block", "note"]].to_string(index=False) if len(iv) else "")
say("honesty settings present (h, n_w):", sorted(set(zip(hon.h.astype(int), hon.n_w.astype(int)))), "| shapes per setting:",
    hon.groupby(["h", "n_w"]).measure.nunique().tolist(), "| n per row:", sorted(set(hon.n.astype(int))))
mc = (hon.pivot_table(index=["h", "n_w", "measure"], columns="stat", values="value"))
say("honesty: coverage + miss_above + miss_below = 1 on every shape:", bool(np.allclose(mc.sum(axis=1), 1.0, atol=1e-12)))
say("\nthe paired P differences (corrected less stage2; ahead-average units), as re-made:")
for (d, ru, a, b), m in paired_mine.items():
    lo = m.get("ci90_low", (np.nan,))[0]
    hi = m.get("ci90_high", (np.nan,))[0]
    say(f"  {d} {ru:10s} {a:7s} {b:6s} mean {m['mean'][0]:+.6f} n {m['mean'][1]} n_w {m.get('n_w', (np.nan,))[0]:.0f} "
        f"signs {m.get('sign_above', (np.nan,))[0]:.0f}/{m.get('sign_equal', (np.nan,))[0]:.0f}/{m.get('sign_below', (np.nan,))[0]:.0f} "
        f"ci90 [{lo:+.6f}, {hi:+.6f}] mdd {m.get('mdd', (np.nan,))[0]:.6f} label {m.get('interval_label', (np.nan,))[0]}")

# ================================================================== 10. mdd_P re-derived by the audit's own Monte Carlo
say("\n## 10. mdd_P: Q-16's pcons, re-coded, with the audit's own seeds")
K = man["parameters"]["mdd_P"]["k"]
LEVEL = 0.05 / (K * (K + 1))
say("manifest k", K, "level", man["parameters"]["mdd_P"]["level"], "= 0.05/(k(k+1)):", same(LEVEL, man["parameters"]["mdd_P"]["level"], 1e-12),
    "| at k = 13 the level would be", 0.05 / (13 * 14))
REPS = 5000
NULL = 200_000


def batch_t(Dm, B):
    n = Dm.shape[0]
    bid = (np.arange(n) * B) // n
    est = Dm.mean(axis=0)
    m = np.stack([Dm[bid == j].mean(axis=0) for j in range(B)])
    se = np.sqrt(((m - est) ** 2).sum(axis=0) / (B - 1)) / math.sqrt(B)
    return est, se


def obm_(Dm, m):
    n = Dm.shape[0]
    C = np.vstack([np.zeros((1, Dm.shape[1])), np.cumsum(Dm, axis=0)])
    Bm = (C[m:] - C[:-m]) / m
    est = C[-1] / n
    var = n * m / ((n - m + 1.0) * (n - m)) * ((Bm - est) ** 2).sum(axis=0)
    return est, np.sqrt(var / n)


def ft_(Dm, flat=63, taper=126):
    n = Dm.shape[0]
    est = Dm.mean(axis=0)
    k = np.arange(1, taper)
    w = np.where(k <= flat, 1.0, (taper - k) / float(taper - flat))
    out = np.empty(Dm.shape[1])
    nf = 1 << int(math.ceil(math.log2(2 * n)))
    for i in range(0, Dm.shape[1], 2000):
        Y = Dm[:, i:i + 2000] - est[i:i + 2000]
        F = np.fft.rfft(Y, n=nf, axis=0)
        g = np.fft.irfft(F * np.conj(F), n=nf, axis=0)[:taper] / n      # autocovariances, divisor n, lags 0..taper-1
        out[i:i + 2000] = g[0] + 2.0 * (w[:, None] * g[1:]).sum(axis=0)
    se = np.where(out > 0, np.sqrt(np.maximum(out, 0) / n), np.nan)
    return est, se


crit_cache = {}


def crit(kind, n):
    if (kind, n) in crit_cache:
        return crit_cache[(kind, n)]
    rng = np.random.default_rng([AUDIT_CRIT_SEED, n, 126 if kind == "obm" else 63])
    ts = []
    for _ in range(NULL // 5000):
        z = rng.standard_normal((n, 5000))
        e, s = obm_(z, 126) if kind == "obm" else ft_(z)
        ts.append(np.where(np.isfinite(s), e / s, -np.inf))
    t_ = np.concatenate(ts)
    c = float(np.quantile(t_, 1 - LEVEL))
    crit_cache[(kind, n)] = c
    return c


def mdd_audit(dser, rng):
    x = np.asarray(dser, float)
    c0 = x - x.mean()
    n = len(x)
    L = 63
    phase = rng.integers(0, L, size=REPS)
    nb = (n + L) // L + 1
    sg = rng.choice(np.array([-1.0, 1.0]), size=(nb, REPS))
    fid = (np.arange(n)[:, None] + phase[None, :]) // L
    Dm = c0[:, None] * np.take_along_axis(sg, fid, axis=0)
    B = n // 63
    e1, s1 = batch_t(Dm, B)
    lo1 = e1 - stats.t.ppf(1 - LEVEL, B - 1) * s1
    e2, s2 = obm_(Dm, 126)
    lo2 = e2 - crit("obm", n) * s2
    e3, s3 = ft_(Dm)
    lo3 = np.where(np.isfinite(s3), e3 - crit("ft", n) * s3, -np.inf)
    md = np.maximum.reduce([np.maximum(-e, -np.where(np.isfinite(lo), lo, -np.inf)) for e, lo in
                            ((e1, lo1), (e2, lo2), (e3, lo3))])
    return float(np.quantile(md, 0.80))


mdd_file = summ[(summ.section == "extra") & (summ.measure == "mdd_P")]
say("mdd_P rows:", len(mdd_file), "| finite:", int(np.isfinite(mdd_file.value).sum()), "| blank by note:",
    mdd_file[~np.isfinite(mdd_file.value)].note.str[:40].value_counts().to_dict())
for d in ("p15", "p16"):
    for ru in RULES:
        for a in ARMS:
            x = ahead_series(groups[(d, ru, a)], "judged")
            y = ahead_series(groups[("p14", ru, a)], "judged")
            common = sorted(set(x) & set(y))
            dd = np.array([x[k] for k in common]) - np.array([y[k] for k in common])
            rng = np.random.default_rng([AUDIT_FLIP_SEED, DESIGNS.index(d), RULES.index(ru), ARMS.index(a)])
            v = mdd_audit(dd, rng)
            fv = mdd_file[(mdd_file.design == d) & (mdd_file.rules == ru) & (mdd_file.arm == a) &
                          (mdd_file.block == "judged")]
            say(f"  {d} {ru:10s} {a:7s}: n {len(dd)} (file {int(fv.n.iloc[0])}); file {fv.value.iloc[0]:.6f}; audit "
                f"{v:.6f}; ratio {v / fv.value.iloc[0]:.4f}; mean diff (P {d} less P-14) {dd.mean():+.6f}")
say("audit critical values (own seed):", {f"{k[0]} n={k[1]}": round(v, 4) for k, v in crit_cache.items()},
    "| bm63 t critical df", 595 // 63 - 1, round(float(stats.t.ppf(1 - LEVEL, 595 // 63 - 1)), 4))

# ================================================================== 10b. mdd_P at the runner's declared seeds, re-coded
say("\n## 10b. mdd_P replicated with the audit's own code at the runner's declared seeds (role: Q-16's fixed-b null")
say("     seed (p_bound.SEED) for the critical values, 400,000 draws; mdd_P's flip seed (breakeven_readings.MDD_SEED) by (design, rule set, arm)")
say("     index, 20,000 replications in batches of 2,000) -- the method re-coded, not the runner's functions called")
import re as _re  # the runner's declared seeds, read as text from their declaring modules (no producing code imported)
_pb = (ROOT / 'extended' / 'p_bound.py').read_text(encoding='utf-8')
_br = (ROOT / 'extended' / 'breakeven_readings.py').read_text(encoding='utf-8')
RUN_CRIT_SEED = int(_re.search(r'^SEED = (\d+)$', _pb, _re.M).group(1))
_lo = int(_re.search(r'^SEED_BLOCK = tuple\(range\((\d+), \d+\)\)$', _br, _re.M).group(1))
assert _re.search(r'^MDD_SEED = SEED_BLOCK\[1\]$', _br, _re.M)
RUN_FLIP_SEED = _lo + 1


def null_t(kind, n, seed):
    rng = np.random.default_rng([seed, n, 126] if kind == "obm" else [seed, n, 63, 126])
    out = []
    for _ in range(40):
        z = rng.standard_normal((n, 10_000))
        if kind == "obm":
            e, s_ = obm_(z, 126)
            out.append(e / s_)
        else:
            e, s_ = ft_(z)
            out.append(np.where(np.isfinite(s_), e / s_, -np.inf))
    return np.sort(np.concatenate(out))


tobm = null_t("obm", 595, RUN_CRIT_SEED)
tft = null_t("ft", 595, RUN_CRIT_SEED)
c_obm, c_ft = float(np.quantile(tobm, 1 - LEVEL)), float(np.quantile(tft, 1 - LEVEL))
del tobm, tft
t2 = null_t("ft", 595, AUDIT_CRIT_SEED + 10)
t3 = null_t("ft", 595, AUDIT_CRIT_SEED + 20)
say("critical values at the runner's seed (400,000 draws): obm", round(c_obm, 4), "ft", round(c_ft, 4),
    "| ft at two audit seeds (400,000 draws each):", round(float(np.quantile(t2, 1 - LEVEL)), 4),
    round(float(np.quantile(t3, 1 - LEVEL)), 4), "| draws beyond the ft quantile:", int((t2 > np.quantile(t2, 1 - LEVEL)).sum()))
del t2, t3


def mdd_exact(dser, rng, reps=20_000, batch=2_000):
    x = np.asarray(dser, float)
    c0 = x - x.mean()
    n, L = len(x), 63
    B = n // 63
    tb = stats.t.ppf(1 - LEVEL, B - 1)
    parts, done, binds = [], 0, np.zeros(3)
    while done < reps:
        r = min(batch, reps - done)
        phase = rng.integers(0, L, size=r)
        nb = (n + L) // L + 1
        sg = rng.choice(np.array([-1.0, 1.0]), size=(nb, r))
        fid = (np.arange(n)[:, None] + phase[None, :]) // L
        Dm = c0[:, None] * np.take_along_axis(sg, fid, axis=0)
        e1, s1 = batch_t(Dm, B)
        e2, s2 = obm_(Dm, 126)
        e3, s3 = ft_(Dm)
        los = [e1 - tb * s1, e2 - c_obm * s2, np.where(np.isfinite(s3), e3 - c_ft * s3, -np.inf)]
        los = [np.where(np.isfinite(l_), l_, -np.inf) for l_ in los]
        lo = np.minimum.reduce(los)
        binds += np.bincount(np.argmin(np.stack(los), axis=0), minlength=3)
        parts.append(np.maximum(-e1, -lo))
        done += r
    return float(np.quantile(np.concatenate(parts), 0.80)), binds / binds.sum()


exact_diff = 0
for d in ("p15", "p16"):
    for ru in RULES:
        for a in ARMS:
            x = ahead_series(groups[(d, ru, a)], "judged")
            y = ahead_series(groups[("p14", ru, a)], "judged")
            common = sorted(set(x) & set(y))
            dd = np.array([x[k] for k in common]) - np.array([y[k] for k in common])
            rng = np.random.default_rng([RUN_FLIP_SEED, DESIGNS.index(d), RULES.index(ru), ARMS.index(a)])
            v, bshare = mdd_exact(dd, rng)
            fv = float(mdd_file[(mdd_file.design == d) & (mdd_file.rules == ru) & (mdd_file.arm == a) &
                                (mdd_file.block == "judged")].value.iloc[0])
            ok_ = same(v, fv, 1e-9)
            exact_diff += 0 if ok_ else 1
            say(f"  {d} {ru:10s} {a:7s}: file {fv:.9f}; replicated {v:.9f}; equal (1e-9): {ok_}; the binding lower "
                f"limit's share bm63/obm126/ft63: {np.round(bshare, 3).tolist()}")
if exact_diff:
    problems.append(f"mdd_P: {exact_diff} rows not replicated at the runner's seeds")

# ================================================================== 11. against E-188's file
say("\n## 11. this file's P-14 and P-16 rows against E-188's results/breakeven_fidelity.csv (same rule sets)")
E = pd.read_csv(RES / "breakeven_fidelity.csv", keep_default_na=False, na_values=[""], low_memory=False)
ek = {}
for r in E.itertuples(index=False):
    ek[(r.section, r.design, r.rules, r.arm if isinstance(r.arm, str) else "", r.shift if isinstance(r.shift, str) else "",
        r.rr if r.rr == r.rr else "", r.block if isinstance(r.block, str) else "", r.measure, r.stat)] = (r.value, r.n)
nk = {}
for r in summ.itertuples(index=False):
    if r.design in ("p14", "p16") and r.section in ("scorecard", "extra", "path", "gate", "trades"):
        nk[(r.section, r.design, r.rules, r.arm if isinstance(r.arm, str) else "", r.shift if isinstance(r.shift, str) else "",
            r.rr if r.rr == r.rr else "", r.block if isinstance(r.block, str) else "", r.measure, r.stat)] = (r.value, r.n)
both = set(ek) & set(nk)
dif = [k for k in both if not same(ek[k][0], nk[k][0], 1e-12) and k[7] != "mdd_P"]
dn = [k for k in both if (ek[k][1] == ek[k][1]) and (nk[k][1] == nk[k][1]) and int(ek[k][1]) != int(nk[k][1])]
say(f"keys in E-188's file (these sections, p14/p16): {len([k for k in ek if k[0] in ('scorecard','extra','path','gate','trades')])};",
    f"common {len(both)}; values differing (excluding mdd_P) {len(dif)}; n differing {len(dn)};",
    f"E-188 keys absent here {len([k for k in ek if k not in nk and k[0] in ('scorecard','extra','path','gate','trades')])}")
by_rules = {}
for k in dif:
    by_rules[k[2]] = by_rules.get(k[2], 0) + 1
say("differing by rule set:", by_rules, dif[:5])
if dif or dn:
    problems.append(f"{len(dif)} values differ from E-188's file")

# ================================================================== 12. Q-45's C5: stop_first rises, start by start
say("\n## 12. Q-45 C5: where stop_first is ahead more months than stage2 (per start, 63-session starts)")
for d in DESIGNS:
    for a in ARMS:
        x = groups[(d, "stop_first", a)].set_index("start_date")["_ma"]
        y = groups[(d, "stage2", a)].set_index("start_date")["_ma"]
        ok = x.notna() & y.notna()
        up = int((x[ok] > y[ok]).sum())
        dn_ = int((x[ok] < y[ok]).sum())
        say(f"  {d} {a}: starts {int(ok.sum())}; more months ahead under stop_first {up}; fewer {dn_}; "
            f"net months {int((x[ok] - y[ok]).sum())}")
        # do the starts differ at all in money?
        xs = groups[(d, "stop_first", a)].set_index("start_date")
        ys = groups[(d, "stage2", a)].set_index("start_date")
        dm = int((~np.isclose(xs["net_month_3"].fillna(-1e18), ys["net_month_3"].fillna(-1e18), rtol=0, atol=1e-9)).sum())
        say(f"      starts whose month-3 net differs at all: {dm}")
for a in ARMS:
    for ru in ("delay5", "both"):
        x = groups[("p15", ru, a)]
        y = groups[("p15", "stage2" if ru == "delay5" else "stop_first", a)]
        dm = int((~np.isclose(x["net_month_3"].fillna(-1e18).to_numpy(), y["net_month_3"].fillna(-1e18).to_numpy(),
                              rtol=0, atol=1e-9)).sum())
        say(f"  p15 {ru} against p15 {'stage2' if ru == 'delay5' else 'stop_first'} ({a}): starts whose month-3 net differs: {dm}")

# ================================================================== 13. held-out years
say("\n## 13. the held-out years (2024-01-02 to 2026-07-16) in this file")
first24 = int(cal[cal.start_date >= JUDGED_FIRST].start_day.min())
say("first held-out session index", first24, "date", cal[cal.start_day == first24].start_date.iloc[0])
one = groups[("p14", "stage2", "verdict")]
in_h = one[one.start_date >= JUDGED_FIRST]
cross = one[(one.start_date < JUDGED_FIRST) & (one.start_day + one.observed - 1 >= first24)]
pure = one[(one.start_day + one.observed - 1 < first24)]
say("per (design, rules, arm), starts dated in the held-out years:", len(in_h), "| earlier starts whose observed sessions",
    "reach into them:", len(cross), "| starts wholly before them:", len(pure), "| total", len(one))
for b in BLOCKS:
    s = blk(one, b, 63)
    say(f"  P's starts on block {b}: {len(s)}, of which touching the held-out years:",
        int((s.start_day + 62 >= first24).sum()))
say("\n## problems found:", len(problems))
for p in problems:
    say(" -", p)

# ================================================================== 14. descriptive reading of the re-made cards
say("\n## 14. the re-made scorecards (equal to the file's, section 5), described")
UNIT = {"P": "share", "S1": "dollars", "S3a": "share", "S3b": "sessions", "S3c": "ratio", "S4a": "share", "S4b": "share",
        "S5a": "dollars", "S5b": "sessions", "S5c": "ratio"}
HIGHER = {"P", "S3a", "S3c", "S4a", "S4b", "S5a"}
for b in BLOCKS:
    for a in ARMS:
        say(f"-- block {b}, arm {a}: P by design (rows) and rule set (columns); the best design per rule set")
        tab = pd.DataFrame({ru: {d: mine_all[("scorecard", d, ru, a, b, "P", "value")][0] for d in DESIGNS} for ru in RULES})
        say(tab.to_string(float_format=lambda x: f"{x:.6f}"))
        say("   best:", {ru: tab[ru].idxmax() for ru in RULES})
say("\nD-621 (3)(ii)'s tolerances applied descriptively, each corrected rule set against stage2 (same design, arm, block):")
say("worse by more than 5 points on a share, or by more than 10 % of |stage2's value| on dollars, sessions, ratios")
for d in DESIGNS:
    for ru in CORR:
        for a in ARMS:
            for b in BLOCKS:
                for m, u in UNIT.items():
                    v = mine_all[("scorecard", d, ru, a, b, m, "value")][0]
                    r0 = mine_all[("scorecard", d, "stage2", a, b, m, "value")][0]
                    if not (np.isfinite(v) and np.isfinite(r0)):
                        continue
                    worse = (r0 - v) if m in HIGHER else (v - r0)
                    tol = 0.05 if u == "share" else 0.10 * abs(r0)
                    if worse > tol + 1e-12:
                        say(f"  {d} {ru} {a} {b} {m}: stage2 {r0:.6g} -> {v:.6g} (worse by {worse:.6g}; tolerance {tol:.6g})")
