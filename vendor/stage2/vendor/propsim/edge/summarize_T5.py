"""Write T5_RESULTS.md from the result CSVs (no hand-copied numbers)."""
import os, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); rd = lambda f: pd.read_csv(os.path.join(HERE, f))
C, V = rd("results_combine_edge.csv"), rd("results_value_of_edge.csv")
Bf = pd.concat([rd("results_payout_buffer_exploratory.csv"), rd("results_payout_buffer_extension.csv")], ignore_index=True)
Bf["prof"] = Bf.R.map("{:g}".format) + ":1 $" + Bf.risk.map("{:.0f}".format)
C["prof"] = C.R.map("{:g}".format) + ":1 $" + C.risk.map("{:.0f}".format)
val = open(os.path.join(HERE, "validation_T5.txt")).read().strip()
md = lambda df: df.to_markdown()
out = ["# T5 — Value of a demonstrated edge within the conduct constraints", "",
       "Pre-registration: `PREREG_T5.md`. Scripts: `combine_exact.py`, `value_of_edge.py` (pre-registered); "
       "`xfa_small_risk_exploratory.py`, `payout_buffer_exploratory.py` and the buffer extension (exploratory, D-44/D-45). "
       "Edge e = expected P&L per trade as a fraction of $ risked, **after costs**. e = 0 rows are reference only (D-34).", "",
       "## Validation (pre-registered V1–V3)", "", "```", val, "```", "",
       "## 1. Combine pass probability — exact chain (validated against Monte Carlo)", "",
       md(C.pivot(index="prof", columns="edge", values="p_pass").round(3)), "",
       "Admissible profiles (D-36) are all rows except 1:1 $1500 (reference, not admissible).", ""]
for path in ["standard", "consistency"]:
    a = V[(V.path == path) & V.admissible & ~V.exploratory]
    b = a.loc[a.groupby("edge").ev_per_attempt.idxmax()].set_index("edge")
    out += [f"## 2{'a' if path == 'standard' else 'b'}. Best pre-registered admissible pair by EV per attempt — {path} path, take-the-maximum payouts (A5), 1-year funded horizon", "",
            md(b[["combine_profile", "xfa_profile", "p_pass", "xfa_cash_1y", "ev_per_attempt", "ev_structural", "ev_from_edge", "edge_share_of_ev", "failed_combines_per_year"]].round(3)), ""]
out += ["`ev_structural` is the value present at zero edge — the contract asymmetry the firm prohibits exploiting (D-34). "
        "`edge_share_of_ev` is the share that comes from the edge itself. `failed_combines_per_year` makes the churn visible "
        "for one account slot run continuously.", "",
        "## 3. Funded account: payout policy is first-order at positive edge (exploratory, D-45)", "",
        "Realised cash per year over a two-year horizon, standard path, net-positive rule on. Balance left in the account at the horizon is **not** counted (conservative).", "",
        md(Bf.pivot_table(index=["prof", "keep_balance"], columns="edge", values="cash_per_year").round(0)), ""]
best = Bf[Bf.edge > 0].loc[Bf[Bf.edge > 0].groupby("edge").cash_per_year.idxmax()].set_index("edge")
base = Bf[(Bf.keep_balance == 0) & (Bf.edge > 0)].groupby("edge").cash_per_year.max()
best["take_max_best_profile"] = base
out += ["### Best funded policy found per edge", "", md(best[["prof", "keep_balance", "cash_per_year", "p_alive_2y", "unrealised_2y", "take_max_best_profile"]].round(2)), "",
        "## 4. Value per Combine attempt with the best funded policy found", ""]
rows = []
for e, r in best.iterrows():
    cc = C[(C.edge == e) & (C.R == 1.5) & (C.risk == 500.0)].iloc[0] if e in C.edge.values else None
    xfa2y = 2 * r.cash_per_year
    for prof, crow in C[(C.edge == e) & (C.prof != "1:1 $1500")].groupby("prof"):
        crow = crow.iloc[0]; ev = crow.p_pass * (xfa2y - 149.0) - crow.mean_sub
        rows.append(dict(edge=e, combine_profile=prof, p_pass=crow.p_pass, funded_policy=f"{r.prof}, keep ${r.keep_balance:,.0f}", funded_cash_2y=xfa2y, ev_per_attempt=ev))
Q = pd.DataFrame(rows); Qb = Q.loc[Q.groupby("edge").ev_per_attempt.idxmax()].set_index("edge")
out += [md(Qb.round(3)), "",
        "## Caveats", "",
        "- Funded values use a two-year horizon and count only realised cash; larger buffers leave more unrealised balance, so they are understated.",
        "- The buffer and small-risk results are exploratory (chosen after seeing the pre-registered results); their grids are coarse and one optimum (1.5:1 $1,000) is still rising at the largest buffer tested.",
        "- One trade per day; fixed risk; no contract-size (scaling plan) limits; drift convention for edge; exact-at-stop fills. A real edge must survive realistic fills (Prohibited Trading Strategies: no reliance on SIM stop fills).",
        "- Edge is per trade after costs. Commissions and slippage are the difference between a gross and a net edge."]
open(os.path.join(HERE, "T5_RESULTS.md"), "w").write("\n".join(out) + "\n")
print("\n".join(out[-40:]))
