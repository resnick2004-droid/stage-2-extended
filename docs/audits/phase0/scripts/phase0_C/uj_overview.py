import sys
import pandas as pd

R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_colwidth", 120)
f = sys.argv[1]
use = sys.argv[2].split(",")
df = pd.read_csv(f"{R}\\{f}", usecols=lambda c: c in use, low_memory=False)
print(df.shape)
grp = [c for c in use if c in df.columns][:int(sys.argv[3])]
print(df.groupby(grp, dropna=False).size().to_string())
