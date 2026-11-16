import sys
import pandas as pd

R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 60)
pd.set_option("display.max_colwidth", 200)
f = sys.argv[1]
secs = sys.argv[2].split(",")
df = pd.read_csv(f"{R}\\{f}", low_memory=False)
for s in secs:
    d = df[df["section"] == s]
    d = d[[c for c in d.columns if d[c].notna().any()]]
    print("=== section", s, d.shape)
    if len(sys.argv) > 3 and sys.argv[3] == "T":
        print(d.T.to_string())
    else:
        print(d.to_string(index=False))
