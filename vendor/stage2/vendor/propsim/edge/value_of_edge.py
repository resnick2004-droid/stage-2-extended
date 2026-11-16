"""T5 — value of a demonstrated edge within the conduct constraints (PREREG_T5.md).
Outputs: results_combine_edge.csv, results_xfa_edge.csv, results_value_of_edge.csv, validation_T5.txt"""
import sys, os, time, itertools
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from propsim import Rules, Policy, simulate_combine, simulate_xfa
from combine_exact import combine_exact

ADMISSIBLE = [(R, r) for R in (1.5, 2.0, 3.0) for r in (500.0, 750.0, 1000.0)]
REFERENCE = [(1.0, 1500.0)]
EDGES = [0.0, 0.02, 0.05, 0.10, 0.15, 0.20]
PATHS = ["standard", "consistency"]
N_C, N_X, H = 200_000, 50_000, 252
log = []
def say(s): print(s, flush=True); log.append(s)

def combine_stage():
    rows = []
    for i, ((R, r), e) in enumerate(itertools.product(ADMISSIBLE + REFERENCE, EDGES)):
        ex = combine_exact(R, r, e)
        mc = simulate_combine(Rules(), Policy(rr=R, risk=r), e, N_C, np.random.default_rng(7000 + i), max_days=5000)
        p = mc["passed"].mean(); d = mc["days"]
        rows.append(dict(R=R, risk=r, edge=e, admissible=(R, r) in ADMISSIBLE,
                         p_pass=ex["p_pass"], mean_days=ex["mean_days"], mean_sub=ex["mean_sub"], unresolved=ex["unresolved"],
                         mc_p_pass=p, mc_p_se=np.sqrt(p * (1 - p) / N_C), mc_days=d.mean(), mc_days_se=d.std() / np.sqrt(N_C),
                         mc_sub=mc["sub_fees"].mean(), mc_unresolved=mc["unresolved"].mean()))
    df = pd.DataFrame(rows)
    df["z_p"] = (df.mc_p_pass - df.p_pass) / df.mc_p_se
    df["z_days"] = (df.mc_days - df.mean_days) / df.mc_days_se
    return df

def xfa_stage():
    rows = []; rules = Rules(payout_fee=0.0, require_profit_since_payout=True)
    for i, ((R, r), path, e) in enumerate(itertools.product(ADMISSIBLE + REFERENCE, PATHS, EDGES)):
        x = simulate_xfa(rules, Policy(rr=R, risk=r, payout_path=path), e, N_X, np.random.default_rng(9000 + i), horizon_days=H)
        fp = x["first_payout_day"]; got = fp >= 0
        rows.append(dict(R=R, risk=r, path=path, edge=e, admissible=(R, r) in ADMISSIBLE,
                         cash=x["cash"].mean(), cash_se=x["cash"].std() / np.sqrt(N_X), gross=x["gross_paid"].mean(),
                         gross_se=x["gross_paid"].std() / np.sqrt(N_X),
                         T=(x["B"] + x["gross_paid"]).mean(), T_se=(x["B"] + x["gross_paid"]).std() / np.sqrt(N_X),
                         p_payout=got.mean(), days_to_first_payout=(np.median(fp[got]) + 1) if got.any() else np.nan,
                         payouts=x["n_payouts"].mean(), p_closed=x["closed"].mean(), days_alive=x["days"].mean(),
                         unrealised=np.where(x["closed"], 0.0, x["B"]).mean()))
    return pd.DataFrame(rows)

def compose(C, X):
    """Compose every (Combine profile, XFA profile, path, edge). Churn and edge attribution are reported beside value,
    because a per-year rate also rewards cycling through failed attempts (the prohibited pattern at e = 0, D-34)."""
    out = []
    for (_, c), (_, x) in itertools.product(C.iterrows(), X.iterrows()):
        if c.edge != x.edge: continue
        ev = c.p_pass * (x.cash - 149.0) - c.mean_sub
        L = c.mean_days + c.p_pass * x.days_alive
        out.append(dict(edge=c.edge, path=x.path, combine_profile=f"{c.R:g}:1 ${c.risk:.0f}", xfa_profile=f"{x.R:g}:1 ${x.risk:.0f}",
                        admissible=bool(c.admissible and x.admissible), exploratory=bool(x.get("exploratory", False)),
                        max_position_pct=100.0 * max(c.risk, x.risk) / 2000.0,
                        p_pass=c.p_pass, xfa_cash_1y=x.cash, xfa_days_alive=x.days_alive, ev_per_attempt=ev, cycle_days=L,
                        value_per_slot_year=252.0 * ev / L, combine_attempts_per_year=252.0 / L,
                        failed_combines_per_year=252.0 * (1 - c.p_pass) / L,
                        days_to_first_payout=c.mean_days + x.days_to_first_payout, p_payout_per_attempt=c.p_pass * x.p_payout))
    V = pd.DataFrame(out)
    base = V[V.edge == 0].set_index(["path", "combine_profile", "xfa_profile"])
    idx = pd.MultiIndex.from_frame(V[["path", "combine_profile", "xfa_profile"]])
    V["ev_structural"] = base.ev_per_attempt.reindex(idx).values          # value present at zero edge (the prohibited mechanism)
    V["ev_from_edge"] = V.ev_per_attempt - V.ev_structural
    V["edge_share_of_ev"] = V.ev_from_edge / V.ev_per_attempt
    return V

def recompose():
    C = pd.read_csv(os.path.join(HERE, "results_combine_edge.csv"))
    X = pd.read_csv(os.path.join(HERE, "results_xfa_edge.csv"))
    xp = os.path.join(HERE, "results_xfa_edge_exploratory.csv")
    X["exploratory"] = False
    if os.path.exists(xp): X = pd.concat([X, pd.read_csv(xp)], ignore_index=True)
    X["exploratory"] = X["exploratory"].fillna(False).astype(bool)
    V = compose(C, X); V.to_csv(os.path.join(HERE, "results_value_of_edge.csv"), index=False); return V

if __name__ == "__main__" and "--recompose" in sys.argv:
    V = recompose(); print(f"recomposed {len(V)} pairs"); sys.exit(0)

if __name__ == "__main__":
    t0 = time.time()
    C = combine_stage(); C.to_csv(os.path.join(HERE, "results_combine_edge.csv"), index=False); say(f"combine stage done {time.time()-t0:.0f}s")
    X = xfa_stage(); X.to_csv(os.path.join(HERE, "results_xfa_edge.csv"), index=False); say(f"xfa stage done {time.time()-t0:.0f}s")
    # ---- V1
    z = pd.concat([C.z_p, C.z_days]).abs()
    say(f"V1 exact vs MC: {len(z)} comparisons, {int((z > 3).sum())} beyond 3 SE, max |z| {z.max():.2f} -> "
        + ("PASS" if (z > 3).sum() <= 2 and z.max() <= 4 else "FAIL"))
    # ---- V2
    ref = C[(C.R == 1.0) & (C.risk == 1500.0) & (C.edge == 0)].p_pass.iloc[0]
    g = pd.read_csv(os.path.join(os.path.dirname(HERE), "results_grid_edge0.csv"))
    g1 = g[g.day_rule == "1/day"]
    zz = []
    for _, row in C[C.edge == 0].iterrows():
        m = g1[(g1.rr == row.R) & (g1.risk == row.risk)]
        if len(m): zz.append((m.c_p_pass.iloc[0] - row.p_pass) / m.c_p_pass_se.iloc[0])
    say(f"V2 chain 1:1 $1,500 at e=0 minus 16/49 = {ref - 16/49:.2e} ({'PASS' if abs(ref - 16/49) < 1e-9 else 'FAIL'}); "
        f"grid reproduction: {len(zz)} cells, max |z| {np.max(np.abs(zz)):.2f} -> {'PASS' if np.max(np.abs(zz)) <= 3 else 'FAIL'}")
    # ---- V3
    x0 = X[X.edge == 0]
    b1 = (x0.gross <= 2000 + 3 * x0.gross_se).all(); b2 = (x0["T"] <= 3 * x0.T_se).all()
    mono_fail = []
    for (R, r, path), grp in X.groupby(["R", "risk", "path"]):
        grp = grp.sort_values("edge")
        for a, b in zip(grp.itertuples(), list(grp.itertuples())[1:]):
            if b.cash < a.cash - 3 * np.hypot(a.cash_se, b.cash_se): mono_fail.append((R, r, path, a.edge, b.edge))
    say(f"V3 e=0 gross <= 2000: {'PASS' if b1 else 'FAIL'}; e=0 E[B+Q] <= 0: {'PASS' if b2 else 'FAIL'} "
        f"(max z {(x0['T'] / x0.T_se).max():+.2f}); monotone in edge: {'PASS' if not mono_fail else 'FAIL ' + str(mono_fail)}")
    V = compose(C, X); V.to_csv(os.path.join(HERE, "results_value_of_edge.csv"), index=False)
    say(f"composed {len(V)} pairs; total {time.time()-t0:.0f}s")
    open(os.path.join(HERE, "validation_T5.txt"), "w").write("\n".join(log) + "\n")
