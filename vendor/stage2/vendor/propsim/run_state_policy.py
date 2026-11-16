"""Reproduce the state-dependent policy results (Finding 6).

Combine policies and repeated all-ins use the exact seeds of the stored runs and reproduce them bit-for-bit.
The XFA policy tables were first run inline in an earlier session without recorded seeds; this script
reruns every row (N = 20,000) and checks it against the stored value in standard errors.
Usage: python run_state_policy.py [--verify-only]
"""
import re, sys, numpy as np, pandas as pd
from propsim import Rules
from statepolicy import run_combine, run_xfa, static, xfa_build_then_harvest, xfa_stop_after_payout, combine_fill_the_gap

R = Rules()

# ---------------- Combine (results_state_policy_combine.csv; seed 3, N = 30,000 per policy) ----------------
def lottery_then_fill(rr1, r1, rr2, r2max):
    fill = combine_fill_the_gap(rr2, r2max)
    def act(s):
        rr, risk = fill(s); d1 = (s["day"] == 0)
        return np.where(d1, float(rr1), rr), np.where(d1 & (s["slot"] < 1), float(r1), np.where(d1, 0.0, risk))
    return act

COMBINE = [("static 1:1 $1500 1/day", static(1, 1500)), ("static 0.5:1 $1000 3/day", static(0.5, 1000, 3)),
           ("fill-the-gap 1:1 max $1650", combine_fill_the_gap(1, 1650)), ("fill-the-gap 2:1 max $825", combine_fill_the_gap(2, 825)),
           ("fill-the-gap 0.5:1 max $2000", combine_fill_the_gap(0.5, 2000)), ("day-1 0.825:1 $2000 -> fill 1:1", lottery_then_fill(0.825, 2000, 1, 2000)),
           ("day-1 3:1 $2000 -> fill 1:1", lottery_then_fill(3, 2000, 1, 2000)), ("day-1 0.5:1 $2000 -> fill 1:1", lottery_then_fill(0.5, 2000, 1, 2000))]

def run_combine_table(n=30000):
    rows = []
    for name, act in COMBINE:
        r = run_combine(R, act, n, np.random.default_rng(3)); p = r["passed"].mean()
        rows.append(dict(policy=name, p_pass=p, se=np.sqrt(p * (1 - p) / n), mean_days=r["days"].mean(), sub=r["sub_fees"].mean()))
    return pd.DataFrame(rows)

# ---------------- k consecutive all-ins (results_state_policy_xfa_kallin.csv; seed 7, N = 40,000) ----------------
def allin_k_then_harvest(rr, k, r2=150):
    def act(s):
        d1 = s["day"] == 0; allin = d1 & (s["slot"] < k)
        return np.where(allin, float(rr), 1.0), np.where(allin, s["room"], np.where(d1, 0.0, float(r2)))
    return act

def run_kallin_table(n=40000):
    rows = []
    for rr in [3, 5]:
        for k in [1, 2, 3]:
            r = run_xfa(R, allin_k_then_harvest(rr, k), n, np.random.default_rng(7), 250, "standard")
            rows.append(dict(rr=rr, allins=k, gross=r["gross"].mean(), net=r["cash"].mean(), se=r["cash"].std() / np.sqrt(n),
                             p_payout=(r["first_payout_day"] >= 0).mean(), bound=2000 * (1 - (1 / (1 + rr)) ** k)))
    return pd.DataFrame(rows)

# ---------------- XFA policy tables: name -> policy ----------------
def parse(name):
    """Map a stored policy label to (policy, horizon)."""
    horizon = 500 if "500-day horizon" in name else 250
    stop = "stop after payout" in name
    tpd = 3 if "x3/day" in name else 1
    m = re.match(r"static ([\d.]+):1 \$(\d+) 1/day", name)
    if m: pol = static(float(m[1]), float(m[2]))
    else:
        m = re.match(r"(?:build|day-1 bet) ([\d.]+):1 \$(\d+) -> harvest ([\d.]+):1 \$(\d+)", name)
        if not m: raise ValueError(name)
        t = re.search(r"@B>=(\d+)", name)
        thr = float(t[1]) if t else (1.0 if name.startswith("day-1") else 2000.0)   # day-1 bets harvest from B > 0; builds default to 2,000
        pol = xfa_build_then_harvest(float(m[1]), float(m[2]), float(m[3]), float(m[4]), thr, harvest_tpd=tpd)
    if stop: pol = xfa_stop_after_payout(pol)
    return pol, horizon

def verify_xfa(stored_file, path_col=True, n=20000, seed=2026):
    st = pd.read_csv(stored_file); out = []
    for _, row in st.iterrows():
        path = row["path"] if path_col else "standard"
        pol, h = parse(row["policy"])
        r = run_xfa(R, pol, n, np.random.default_rng(seed), h, path)
        cash, se = r["cash"].mean(), r["cash"].std() / np.sqrt(n)
        se_st = row["se"] if not pd.isna(row.get("se", np.nan)) else se
        out.append(dict(policy=row["policy"], path=path, stored=row["cash"], rerun=cash, z=(cash - row["cash"]) / np.hypot(se, se_st)))
    return pd.DataFrame(out)

if __name__ == "__main__":
    pd.set_option("display.width", 200); fmt = lambda v: f"{v:.3f}"
    comb = run_combine_table(); stored = pd.read_csv("results_state_policy_combine.csv")
    print("Combine: max |rerun - stored| P(pass) =", float(np.max(np.abs(comb.p_pass.values - stored.p_pass.values))))
    kal = run_kallin_table(); stored = pd.read_csv("results_state_policy_xfa_kallin.csv")
    print("k all-ins: max |rerun - stored| net =", float(np.max(np.abs(kal.net.values - stored.net.values))))
    if "--verify-only" not in sys.argv:
        comb.to_csv("results_state_policy_combine.csv", index=False); kal.to_csv("results_state_policy_xfa_kallin.csv", index=False)
    v = pd.concat([verify_xfa("results_state_policy_xfa.csv"), verify_xfa("results_state_policy_xfa_allin.csv", path_col=False)])
    v.to_csv("verify_state_policy_xfa.csv", index=False)
    print(v.to_string(index=False, float_format=fmt))
    print(f"XFA rows: {len(v)}; |z| <= 3 in {int((v.z.abs() <= 3).sum())}; max |z| = {v.z.abs().max():.2f}")
