import sys
import pandas as pd
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
for f in sys.argv[1:]:
    df = pd.read_csv(f"{R}\{f}", low_memory=False)
    d = df[df.section == "ftp"]
    c = ["shift", "ftp_label", "share_paths_ftp_placed", "ftp_first_placed_day_p50", "mean_ftp_placements",
         "mean_ftp_funded_closed", "mean_ftp_payouts_denied", "growth_on_required", "growth_change_from_off", "required_p90",
         "mean_payouts_per_path"]
    print("=====", f)
    print(d[[x for x in c if x in d.columns]].round(3).to_string(index=False))
