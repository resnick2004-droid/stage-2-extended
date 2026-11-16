import sys
import pandas as pd

R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_colwidth", 60)

cols = ["section", "shift", "enforcement_p", "rtp", "settlement", "mean_r_used", "median_log_growth",
        "pf_growth_on_base_p50", "pf_required_p90", "pf_break_even_denial_p50", "mean_payouts_per_path",
        "mean_payout_gross", "share_paths_rtp_placed", "share_payouts_exposed", "mean_combine_purchases",
        "share_accounts_ever_paid", "mean_same_day_multi_breach_days", "is_gate_row", "pf_net_p50", "pf_net_p10",
        "ruin_probability", "mean_accounts_funded", "share_trades_skipped_busy", "one_at_a_time", "cross_account_rule",
        "seat_frees", "total_accounts", "accounts", "combines", "budget_k", "twin"]
for f in sys.argv[1:]:
    df = pd.read_csv(f"{R}\\{f}", low_memory=False)
    keep = df[df["section"].isin(["gate", "placement_on", "twin", "gf15b_twin", "unstrict_beside", "check_years",
                                   "gate_at_ledger_n", "p13_reference", "d501_reference"])]
    c = [x for x in cols if x in df.columns]
    print("=====", f)
    print(keep[c].T.to_string())
    v = df[df["section"] == "verdict"]
    vc = [x for x in df.columns if v[x].notna().any()]
    print("--- verdict")
    print(v[vc].T.to_string())
