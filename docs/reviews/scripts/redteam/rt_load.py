"""Red team: load U1 start rows (verdict arm) for p14/p15/p16 and save a compact parquet-free CSV.
Also print the unique sections/configs/arms, and the 'paired' rows for a bootstrap identity check."""
import sys
import pandas as pd

SRC = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results\user_journey.csv"
OUT = r"C:\Users\resni\AppData\Local\Temp\claude\197752aa8b2362c7\9862c1b3-c57d-4498-a2d7-44492c7a25e6\scratchpad\redteam"

cols = ["section", "config", "arm", "start_day", "start_date", "observed", "pay_days", "payouts",
        "first_payout", "spent_before_first_payout",
        "net_month_1", "net_month_2", "net_month_3", "net_month_6", "net_month_12",
        "fees_month_1", "fees_month_2", "fees_month_3",
        "group", "measure", "at_days", "value", "n", "reference", "reference_value", "difference", "lo", "hi",
        "alpha", "block", "draws", "seed", "key", "year"]
df = pd.read_csv(SRC, usecols=cols, low_memory=False)
print(df["section"].value_counts())
st = df[df["section"] == "start"]
print(st.groupby(["config", "arm"]).size())
st.to_csv(OUT + r"\starts.csv", index=False)
pr = df[df["section"] == "paired"]
print(pr.shape)
print(pr[["config", "arm", "reference", "group", "measure", "at_days", "year", "value", "reference_value",
          "difference", "lo", "hi", "alpha", "block", "draws", "seed", "n"]].head(40).to_string())
pr.to_csv(OUT + r"\paired.csv", index=False)
