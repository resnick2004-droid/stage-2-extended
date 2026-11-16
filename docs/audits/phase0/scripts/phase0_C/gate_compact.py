import sys
import pandas as pd

R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

cols = ["section", "shift", "enforcement_p", "rtp", "mean_r_used", "pf_growth_on_base_p50", "pf_required_p90",
        "pf_break_even_denial_p50", "mean_payouts_per_path", "share_paths_rtp_placed", "share_payouts_exposed",
        "mean_combine_purchases", "mean_same_day_multi_breach_days", "mean_max_mll_breaches_21d", "is_gate_row",
        "horizon_days", "paths", "twin"]
vcols = ["prereg", "verdict", "gate_verdict", "ledger_n", "days", "trades", "risk_policy_id", "growth_point",
         "gate_growth_on_base_p50", "growth_bound_denial_10", "growth_bound_denial_25", "growth_bound_denial_50",
         "growth_placement_on", "growth_zero_edge_twin", "growth_fixed_legs_twin", "tier3_pf_break_even_denial_p50",
         "tier3_share_payouts_exposed", "tier3_mean_max_combine_purchases_21d", "tier3_mean_same_day_multi_breach_days",
         "tier3_mean_max_mll_breaches_21d", "ftp_growth_bound_min", "ftp_growth_bound_min_model",
         "strict_rule_cost_bound", "era_flagged", "bounds_read"]
for f in sys.argv[1:]:
    df = pd.read_csv(f"{R}\\{f}", low_memory=False)
    keep = df[df["section"].isin(["gate", "placement_on", "twin", "gate_at_ledger_n"])]
    c = [x for x in cols if x in df.columns]
    print("=====", f)
    print(keep[c].round(4).to_string(index=False))
    v = df[df["section"] == "verdict"]
    print(v[[x for x in vcols if x in df.columns]].T.to_string())
